import { useState, useEffect, useCallback, useRef } from 'react';
import type { AgentStep, AnalysisResult } from '../types';

const INITIAL_STEPS: AgentStep[] = [
  { step_id: 'ocr_agent', step_name: 'OCR & Portfolio Parse', status: 'pending', icon: '📸', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
  { step_id: 'data_agent', step_name: 'Market Data Fetch', status: 'pending', icon: '📊', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
  { step_id: 'news_agent', step_name: 'News & Sentiment', status: 'pending', icon: '📰', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
  { step_id: 'technical_agent', step_name: 'Technical Analysis', status: 'pending', icon: '📈', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
  { step_id: 'macro_agent', step_name: 'Macro Context', status: 'pending', icon: '🌍', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
  { step_id: 'report_agent', step_name: 'Report Synthesis', status: 'pending', icon: '🧠', input_summary: '', output_summary: '', details: [], data: null, duration_ms: 0 },
];

export function useAgentStream(sessionId: string | null) {
  const [steps, setSteps] = useState<AgentStep[]>(INITIAL_STEPS);
  const [isComplete, setIsComplete] = useState(false);
  const [isError, setIsError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [reportTokens, setReportTokens] = useState('');
  const esRef = useRef<EventSource | null>(null);

  const reset = useCallback(() => {
    setSteps(INITIAL_STEPS.map(s => ({ ...s })));
    setIsComplete(false);
    setIsError(false);
    setErrorMessage('');
    setResult(null);
    setReportTokens('');
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    reset();
    const es = new EventSource(`/api/stream-analysis?session_id=${sessionId}`);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data);

        if (event.type === 'STEP_UPDATE') {
          setSteps(prev => {
            const idx = prev.findIndex(s => s.step_id === event.step_id);
            if (idx >= 0) {
              const updated = [...prev];
              updated[idx] = { ...updated[idx], ...event };
              return updated;
            }
            return prev;
          });
        } else if (event.type === 'REPORT_TOKEN') {
          setReportTokens(prev => prev + event.token);
        } else if (event.type === 'COMPLETE') {
          setResult(event.payload);
          setIsComplete(true);
          es.close();
        } else if (event.type === 'ERROR') {
          setIsError(true);
          setErrorMessage(event.message || 'Unknown error');
          es.close();
        }
      } catch {
        // Ignore parse errors for heartbeats etc.
      }
    };

    es.onerror = () => {
      setIsError(true);
      setErrorMessage('Connection to server lost');
      es.close();
    };

    return () => {
      es.close();
    };
  }, [sessionId, reset]);

  const currentStepIndex = steps.findIndex(s => s.status === 'running');
  const completedSteps = steps.filter(s => s.status === 'done').length;
  const progress = isComplete ? 100 : Math.round((completedSteps / steps.length) * 100);

  return {
    steps,
    isComplete,
    isError,
    errorMessage,
    result,
    reportTokens,
    currentStepIndex,
    completedSteps,
    progress,
    reset,
  };
}
