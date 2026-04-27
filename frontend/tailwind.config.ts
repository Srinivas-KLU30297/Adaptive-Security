/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        background: '#09090b', // zinc-950
        surface: 'rgba(9, 9, 11, 0.7)',
        'surface-2': '#18181b', // zinc-900
        border: 'rgba(255,255,255,0.1)',
        primary: {
          DEFAULT: '#dc2626', // red-600
          dark: '#b91c1c'     // red-700
        },
        secondary: '#059669', // emerald bg
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#dc2626',
        'text-primary': '#fafafa', // zinc-50
        'text-secondary': '#a1a1aa', // zinc-400
        'text-muted': '#71717a', // zinc-500
      },
      fontFamily: {
        display: ['JetBrains Mono', 'monospace'],
        body: ['JetBrains Mono', 'monospace'],
        ui: ['JetBrains Mono', 'monospace'],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
