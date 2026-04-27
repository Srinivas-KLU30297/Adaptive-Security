import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Cpu } from 'lucide-react';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Quick UI button export
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', isLoading, children, ...props }, ref) => {
    
    const variants = {
      primary: "bg-red-600 text-zinc-50 border border-red-500/20 shadow-glow-red hover:bg-red-500",
      secondary: "glass text-zinc-50 hover:bg-zinc-900/80",
      danger: "bg-red-600 text-zinc-50 hover:bg-red-700",
      ghost: "bg-transparent text-zinc-500 hover:text-zinc-50 hover:bg-zinc-900/50"
    };

    const sizes = {
      sm: "h-8 px-3 text-xs",
      md: "h-10 px-4 text-sm",
      lg: "h-12 px-6 text-base"
    };

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded uppercase tracking-widest font-display font-bold transition-all disabled:opacity-50 disabled:pointer-events-none",
          variants[variant],
          sizes[size],
          className
        )}
        disabled={isLoading || props.disabled}
        {...props}
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <Cpu className="animate-spin" size={16} />
            <span className="animate-pulse">PROCESSING...</span>
          </div>
        ) : children}
      </button>
    );
  }
);
Button.displayName = "Button";
