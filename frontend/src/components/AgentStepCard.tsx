import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { Check, AlertCircle, Circle, Loader2 } from 'lucide-react';
import type { AgentStep } from '../types';

interface Props {
  step: AgentStep;
  index: number;
  isReportStep: boolean;
  reportTokens: string;
}

export default function AgentStepCard({ step, index, isReportStep, reportTokens }: Props) {
  const [expanded, setExpanded] = useState(step.status === 'running' || step.status === 'error');

  const isRunning = step.status === 'running';
  const isDone = step.status === 'done';
  const isError = step.status === 'error';
  const isPending = step.status === 'pending';

  if (isRunning && !expanded) setExpanded(true);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className={`
        border border-gray-200 bg-white p-4 mb-4 transition-all duration-200 border-l-4
        ${isRunning ? 'border-l-green-400 animate-subtle-pulse' : ''}
        ${isDone ? 'border-l-green-500' : ''}
        ${isError ? 'border-l-red-400' : ''}
        ${isPending ? 'border-l-gray-200 opacity-50' : ''}
      `}
    >
      {/* Header */}
      <button
        onClick={() => !isPending && setExpanded(!expanded)}
        className="w-full flex items-center gap-3 text-left"
      >
        {/* Status indicator */}
        <div className="shrink-0">
          {isPending && <Circle className="h-4 w-4 text-[#9CA3AF]" strokeWidth={1.5} />}
          {isRunning && <Loader2 className="h-4 w-4 text-green-500 animate-spin-slow" strokeWidth={2} />}
          {isDone && <Check className="h-4 w-4 text-green-500" strokeWidth={2} />}
          {isError && <AlertCircle className="h-4 w-4 text-red-500" strokeWidth={2} />}
        </div>

        <div className="flex-1 min-w-0">
          <span className={`font-medium text-sm ${isPending ? 'text-[#9CA3AF]' : 'text-[#111827]'}`}>{step.step_name}</span>
          {isDone && step.output_summary && (
            <p className="text-xs text-[#6B7280] mt-0.5 truncate">{step.output_summary}</p>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isDone && step.duration_ms > 0 && (
            <span className="text-xs font-mono text-[#9CA3AF]">{(step.duration_ms / 1000).toFixed(1)}s</span>
          )}
        </div>
      </button>

      {/* Body — collapsible log lines */}
      <AnimatePresence>
        {expanded && !isPending && (step.details.length > 0 || (isReportStep && reportTokens)) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-3 pl-7">
              <div className="max-h-32 overflow-y-auto space-y-1">
                {step.details.map((line, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="text-xs text-[#6B7280] font-mono leading-relaxed"
                  >
                    {line}
                  </motion.div>
                ))}
                {isRunning && (
                  <div className="text-xs text-green-500 font-mono animate-subtle-pulse">▌</div>
                )}
              </div>

              {/* Report streaming preview */}
              {isReportStep && reportTokens && (
                <div className="mt-3 p-3 bg-[#F8FAF9] border border-gray-200 max-h-56 overflow-y-auto">
                  <pre className="text-xs text-[#6B7280] whitespace-pre-wrap break-words font-mono leading-relaxed">
                    {reportTokens}
                    {isRunning && <span className="text-green-500 animate-subtle-pulse">▌</span>}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
