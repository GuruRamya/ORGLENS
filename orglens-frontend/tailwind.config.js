export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Sohne', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        body: ['Inter Var', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        maroon: {
          50: '#f9f5f5',
          100: '#f0e6e6',
          200: '#d9bfbf',
          300: '#c29999',
          400: '#a85959',
          500: '#8B3A3A',
          600: '#7a3333',
          700: '#5f2828',
          800: '#4a1f1f',
          900: '#3a1818',
        },
        neutral: {
          25: '#fafafa',
          50: '#f5f5f5',
          100: '#eeeeee',
          150: '#e8e8e8',
          200: '#e0e0e0',
          300: '#c9c9c9',
          400: '#b0b0b0',
          500: '#808080',
          600: '#666666',
          700: '#4f4f4f',
          800: '#333333',
          900: '#1a1a1a',
          950: '#0f0f0f',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'fade-up': 'fadeUp 0.6s ease forwards',
        'fade-in': 'fadeIn 0.4s ease forwards',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
      },
      boxShadow: {
        'neo-sm': '4px 4px 12px rgba(0, 0, 0, 0.08), -4px -4px 12px rgba(255, 255, 255, 0.8)',
        'neo-md': '6px 6px 16px rgba(0, 0, 0, 0.1), -6px -6px 16px rgba(255, 255, 255, 0.9)',
        'neo-lg': '8px 8px 20px rgba(0, 0, 0, 0.12), -8px -8px 20px rgba(255, 255, 255, 0.95)',
        'neo-inset': 'inset 2px 2px 5px rgba(0, 0, 0, 0.06), inset -2px -2px 5px rgba(255, 255, 255, 0.7)',
      },
      backdropBlur: {
        'xl': '20px',
      },
      scale: {
        '102': '1.02',
      },
    },
  },
  plugins: [],
}