import { AlertTriangle, ShieldCheck, HelpCircle, Flame } from 'lucide-react';
import { clsx } from 'clsx';

export function RiskBadge({ level }: { level?: string }) {
  if (!level) return null;
  
  const levels: Record<string, { color: string, icon: any, label: string }> = {
    low: { color: "text-success border-success bg-success/10 shadow-[0_0_8px_rgba(16,185,129,0.4)]", icon: ShieldCheck, label: "LOW RISK" },
    medium: { color: "text-warning border-warning bg-warning/10 shadow-[0_0_8px_rgba(245,158,11,0.4)]", icon: HelpCircle, label: "MEDIUM RISK" },
    high: { color: "text-danger border-danger bg-danger/10 shadow-[0_0_8px_rgba(239,68,68,0.4)]", icon: AlertTriangle, label: "HIGH RISK" },
    critical: { color: "text-[#ff0055] border-[#ff0055] bg-[#ff0055]/10 shadow-[0_0_12px_rgba(255,0,85,0.6)] animate-pulse", icon: Flame, label: "CRITICAL THREAT" },
  };

  const config = levels[level.toLowerCase()] || levels.low;
  const Icon = config.icon;

  return (
    <div className={clsx("inline-flex items-center gap-2 px-3 py-1 rounded-full border border-b font-display text-xs tracking-wider", config.color)}>
      <Icon size={14} />
      <span>{config.label}</span>
    </div>
  );
}
