import { useState, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { AnimatePresence, motion } from 'framer-motion';
import UploadScreen from './components/UploadScreen';
import AgentTracePanel from './components/AgentTracePanel';
import ReportDashboard from './components/ReportDashboard';
import { useAgentStream } from './hooks/useAgentStream';

type Phase = 'upload' | 'analyzing' | 'report';

export default function App() {
  const [phase, setPhase] = useState<Phase>('upload');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const { steps, isComplete, isError, errorMessage, result, reportTokens, progress, reset } = useAgentStream(sessionId);

  const handleSessionStart = useCallback((sid: string) => {
    setSessionId(sid);
    setPhase('analyzing');
  }, []);

  const handleRestart = useCallback(() => {
    setPhase('upload');
    setSessionId(null);
    reset();
  }, [reset]);

  // Transition to report once complete
  if (phase === 'analyzing' && isComplete && result) {
    // Use a micro-delay so the last step card can show "done"
    setTimeout(() => setPhase('report'), 800);
  }

  if (phase === 'analyzing' && isError) {
    toast.error(errorMessage || 'Analysis failed');
  }

  return (
    <div className="min-h-screen bg-white text-[#111827] flex flex-col">
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#FFFFFF', color: '#111827', border: '1px solid #E5E7EB', fontSize: '14px' },
        }}
      />

      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-green-200 bg-white px-6 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <span className="text-[15px] font-semibold tracking-[-0.01em] text-[#111827]">
            Equilyze
          </span>
          {phase !== 'upload' && (
            <button
              onClick={handleRestart}
              className="text-sm text-[#6B7280] hover:text-[#111827] transition-colors px-4 py-2 hover:bg-[#F8FAF9]"
            >
              New Analysis
            </button>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center px-6 py-8">
        <AnimatePresence mode="wait">
          {phase === 'upload' && (
            <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full flex items-center justify-center min-h-[calc(100vh-64px)]">
              <UploadScreen onSessionStart={handleSessionStart} />
            </motion.div>
          )}

          {phase === 'analyzing' && (
            <motion.div key="analyzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full max-w-2xl mx-auto">
              <AgentTracePanel
                steps={steps}
                completedSteps={steps.filter(s => s.status === 'done').length}
                progress={progress}
                reportTokens={reportTokens}
                isComplete={isComplete}
                isError={isError}
                errorMessage={errorMessage}
              />
            </motion.div>
          )}

          {phase === 'report' && result && sessionId && (
            <motion.div key="report" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="w-full max-w-3xl mx-auto">
              <ReportDashboard result={result} sessionId={sessionId} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
