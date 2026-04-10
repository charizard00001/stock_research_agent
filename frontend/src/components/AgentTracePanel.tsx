import AgentStepCard from './AgentStepCard';
import type { AgentStep } from '../types';

interface Props {
  steps: AgentStep[];
  completedSteps: number;
  progress: number;
  reportTokens: string;
  isComplete: boolean;
  isError: boolean;
  errorMessage: string;
}

export default function AgentTracePanel({
  steps,
  completedSteps,
  progress,
  reportTokens,
  isComplete,
  isError,
  errorMessage,
}: Props) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mb-8">
        <h2 className="text-lg font-bold text-[#111827] tracking-[-0.01em]">
          Analysis Progress
        </h2>
        <p className="text-sm text-[#6B7280] mt-1">
          {isComplete ? 'Analysis complete' : isError ? 'Analysis encountered an error' : 'Analyzing your portfolio...'}
        </p>
      </div>

      {/* Progress bar */}
      <div className="mb-6 space-y-2">
        <div className="flex items-center justify-between text-xs text-[#6B7280]">
          <span>{isComplete ? 'Complete' : isError ? 'Error' : completedSteps > 0 ? `Step ${completedSteps} of ${steps.length}` : `0 of ${steps.length}`}</span>
          <span className="font-mono">{progress}%</span>
        </div>
        <div className="h-1 bg-gray-100 overflow-hidden">
          <div
            className="h-full transition-all duration-500 ease-out"
            style={{
              width: `${progress}%`,
              background: isError ? '#EF4444' : isComplete ? '#22C55E' : '#4ADE80',
            }}
          />
        </div>
      </div>

      {/* Steps */}
      <div>
        {steps.map((step, i) => (
          <AgentStepCard
            key={step.step_id}
            step={step}
            index={i}
            isReportStep={step.step_id === 'report_agent'}
            reportTokens={reportTokens}
          />
        ))}
      </div>

      {isError && (
        <div className="mt-4 p-4 border border-red-200 bg-red-50">
          <p className="text-sm text-red-600">{errorMessage}</p>
        </div>
      )}
    </div>
  );
}
