import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eefbf5',
          500: '#179a62',
          900: '#0f5135'
        }
      }
    }
  },
  plugins: []
};

export default config;
