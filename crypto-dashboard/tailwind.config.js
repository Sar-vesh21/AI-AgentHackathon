/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#10B981', // emerald-500
          600: '#059669', // emerald-600
          700: '#047857', // emerald-700
        },
        background: {
          dark: '#000000',
          light: '#1F2937',
        },
        surface: {
          dark: '#111827',
          DEFAULT: '#1F2937',
          light: '#374151',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
} 