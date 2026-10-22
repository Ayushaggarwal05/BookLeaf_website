/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F4F7F5',
          100: '#E5EDE7',
          200: '#C7DBCB',
          300: '#9FBFA5',
          400: '#6E9E78',
          500: '#4D7C5F',
          600: '#386047',
          700: '#2C4C38',
          800: '#223C2C',
          900: '#1B3124',
          950: '#0E1C14',
        },
        cream: {
          50: '#FDFBF7',
          100: '#FAF8F3',
          200: '#F3EFE6',
          300: '#E8E2D5',
          400: '#D5CDBE',
        },
        paper: '#FDFBF7',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Georgia', 'Cambria', '"Times New Roman"', 'serif'],
      },
      boxShadow: {
        soft: '0 2px 10px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02)',
        card: '0 4px 20px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [],
}
