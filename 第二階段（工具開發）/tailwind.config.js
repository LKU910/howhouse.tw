/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./deploy/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Noto Sans TC"', 'sans-serif'],
        serif: ['"Noto Serif TC"', 'serif'],
      },
      colors: {
        stone: {
          50: '#FAFAFA',
          100: '#F4F4F4',
          200: '#E5E5E5',
          800: '#2A2A2A',
          900: '#121212',
        },
        architect: {
          bronze: '#B8956A',
          terracotta: '#9C4A38',
          slate: '#4A5D6A',
        }
      }
    }
  },
  plugins: [],
}
