/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#09090B',
        surface: '#111113',
        border: '#1F1F23',
        accent: '#6366F1',
        green: '#22C55E',
        amber: '#F59E0B',
        red: '#EF4444',
        blue: '#3B82F6',
        text: '#FAFAFA',
        subtext: '#A1A1AA',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
