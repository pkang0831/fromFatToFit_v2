import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#8B4513',
          light: '#A0522D',
          dark: '#654321',
        },
        secondary: {
          DEFAULT: '#D2691E',
          light: '#DEB887',
        },
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        surfaceAlt: 'var(--color-surface-alt)',
        text: {
          DEFAULT: 'var(--color-text)',
          secondary: 'var(--color-text-secondary)',
          light: 'var(--color-text-light)',
          onPrimary: '#FFFFFF',
        },
        accent: {
          DEFAULT: '#DEB887',
          alt: '#D2B48C',
        },
        premium: {
          DEFAULT: '#FFD700',
          dark: '#DAA520',
        },
        border: {
          DEFAULT: 'var(--color-border)',
          light: 'var(--color-border-light)',
        },
        success: '#8BC34A',
        warning: '#FFA726',
        error: '#D32F2F',
        info: '#29B6F6',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
      },
      boxShadow: {
        sm: '0 1px 2px 0 rgba(62, 39, 35, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(62, 39, 35, 0.1), 0 1px 2px 0 rgba(62, 39, 35, 0.06)',
        md: '0 4px 6px -1px rgba(62, 39, 35, 0.1), 0 2px 4px -1px rgba(62, 39, 35, 0.06)',
        lg: '0 10px 15px -3px rgba(62, 39, 35, 0.1), 0 4px 6px -2px rgba(62, 39, 35, 0.05)',
        xl: '0 20px 25px -5px rgba(62, 39, 35, 0.1), 0 10px 10px -5px rgba(62, 39, 35, 0.04)',
      },
    },
  },
  plugins: [],
}

export default config
