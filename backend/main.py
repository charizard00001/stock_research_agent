import os
import json
import uuid
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from backend.agents.pipeline import run_pipeline
from backend.agents.chat_agent import build_chat_system_prompt
from backend.utils.pdf_export import generate_pdf
from backend.llm_client import chat as llm_chat

app = FastAPI(title="Portfolio Research Agent")

allowed_origins = ["http://localhost:5173", "http://localhost:3000"]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage (in-memory for local dev)
queues: dict[str, asyncio.Queue] = {}
session_data: dict[str, dict] = {}
session_images: dict[str, bytes] = {}
session_chat_history: dict[str, list[dict]] = {}
session_models: dict[str, str] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), model: str = Form(None)):
    session_id = str(uuid.uuid4())
    image_bytes = await file.read()

    if not image_bytes:
        return {"error": "No file uploaded"}, 400

    if model:
        session_models[session_id] = model

    session_images[session_id] = image_bytes
    queues[session_id] = asyncio.Queue()

    asyncio.create_task(run_pipeline(session_id, image_bytes, queues, model=model))

    return {"session_id": session_id}


@app.get("/api/stream-analysis")
async def stream_analysis(session_id: str, request: Request):
    if session_id not in queues:
        return {"error": "Invalid session ID"}, 404

    async def event_generator():
        queue = queues[session_id]
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=120)
                try:
                    data = json.dumps(event, default=str)
                except (TypeError, ValueError) as ser_err:
                    data = json.dumps({"type": "ERROR", "message": f"Serialization error: {ser_err}"})
                yield {"data": data}

                if event.get("type") in ("COMPLETE", "ERROR"):
                    # Store final data for PDF export
                    if event.get("type") == "COMPLETE":
                        session_data[session_id] = event.get("payload", {})
                    break
            except asyncio.TimeoutError:
                yield {"data": json.dumps({"type": "HEARTBEAT"})}

    return EventSourceResponse(event_generator())


@app.get("/api/export-pdf")
async def export_pdf(session_id: str):
    data = session_data.get(session_id)
    if not data:
        return Response(content="No report data found", status_code=404)

    report = data.get("report", {})
    portfolio = data.get("portfolio", {})
    pdf_bytes = generate_pdf(report, portfolio)

    return Response(
        content=bytes(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=portfolio_report_{session_id[:8]}.pdf"},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest, request: Request):
    data = session_data.get(body.session_id)
    if not data:
        return Response(
            content=json.dumps({"error": "No report data found for this session"}),
            status_code=404,
            media_type="application/json",
        )

    # Build system prompt from portfolio data
    system_prompt = build_chat_system_prompt(data)

    # Init or get chat history for this session
    if body.session_id not in session_chat_history:
        session_chat_history[body.session_id] = []

    history = session_chat_history[body.session_id]
    history.append({"role": "user", "content": body.message})

    async def stream_generator():
        full_response = ""
        try:
            chat_model = session_models.get(body.session_id)
            response = llm_chat(
                messages=history,
                system=system_prompt,
                stream=True,
                model=chat_model,
            )
            for chunk in response:
                if await request.is_disconnected():
                    break
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    full_response += delta.content
                    yield {"data": json.dumps({"type": "token", "token": delta.content})}

            # Save assistant response to history
            history.append({"role": "assistant", "content": full_response})
            yield {"data": json.dumps({"type": "done"})}
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}

    return EventSourceResponse(stream_generator())
