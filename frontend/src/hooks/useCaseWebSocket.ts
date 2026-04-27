import { useState, useCallback } from 'react';

// This hook now drives an animated progress bar for any analysis,
// using real data from the API response rather than simulated events.
export function useCaseWebSocket(caseId?: string) {
  const [status, setStatus] = useState<string>('pending');
  const [progress, setProgress] = useState<number>(0);
  const [events, setEvents] = useState<any[]>([]);

  // Expose a function to trigger completion with real data
  const completeWithData = useCallback((data: any) => {
    // Animate progress from current position to 100%
    setStatus('processing');
    setProgress(30);
    
    const steps = [50, 70, 90, 100];
    let i = 0;
    const interval = setInterval(() => {
      setProgress(steps[i]);
      i++;
      if (i >= steps.length) {
        clearInterval(interval);
        setStatus('completed');
        setEvents([data]);
      }
    }, 400);
  }, []);

  const reset = useCallback(() => {
    setStatus('pending');
    setProgress(0);
    setEvents([]);
  }, []);

  const latestEvent = events.length > 0 ? events[events.length - 1] : null;

  return { status, progress, events, latestEvent, completeWithData, reset };
}
