

export function AnalysisStepper({ status, progress }: { status: string, progress: number }) {
  const steps = [
    { id: 'pending', label: 'Queued' },
    { id: 'processing', label: 'Inference' },
    { id: 'completed', label: 'Completed' },
  ];

  let currentIdx = steps.findIndex(s => s.id === status);
  if (currentIdx === -1 && status === 'failed') currentIdx = 2; // Show failed at end

  return (
    <div className="w-full bg-surface border border-border rounded-xl p-6">
      <div className="flex justify-between items-center mb-6 relative">
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-1 bg-surface-2 rounded-full z-0 overflow-hidden">
           <div 
              className="h-full bg-primary transition-all duration-500 ease-out shadow-[0_0_10px_rgba(0,212,255,0.8)]"
              style={{ width: `${progress}%` }}
           />
        </div>
        
        {steps.map((step, idx) => {
          const isPast = idx <= currentIdx;
          const isActive = idx === currentIdx;
          
          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center">
              <div 
                className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isPast 
                    ? status === 'failed' ? 'bg-danger text-white' : 'bg-primary text-background shadow-[0_0_12px_rgba(0,212,255,0.6)]' 
                    : 'bg-surface-2 text-text-muted border border-border'
                } ${isActive && status !== 'failed' ? 'animate-pulse' : ''}`}
              >
                {isActive ? '●' : '✓'}
              </div>
              <span className={`text-xs mt-2 font-display uppercase tracking-wider ${isPast ? 'text-text-primary' : 'text-text-muted'}`}>
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
      <div className="text-center font-body text-sm text-text-secondary">
        {status === 'processing' ? `Analyzing content... ${progress}%` : 
         status === 'completed' ? 'Forensic generation complete.' : 
         status === 'failed' ? 'Analysis failed.' : 'Waiting in queue...'}
      </div>
    </div>
  );
}
