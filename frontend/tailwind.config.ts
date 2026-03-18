/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sw: {
          navy: '#0D2137',
          blue: '#2E75B6',
          green: '#22C55E',
          orange: '#F59E0B',
          red: '#EF4444',
          bg: '#F7F8FA',
          surface: '#FFFFFF',
          border: '#E2E8F0',
          text: '#0D2137',
          'text-mid': '#64748B',
          'text-sub': '#94A3B8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        card: '10px',
        input: '6px',
      },
      boxShadow: {
        card: '0 1px 6px rgba(13,33,55,0.05)',
      },
    },
  },
  plugins: [],
}
