import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
    './public/index.html',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#00ff00', // Green for hacker console
        background: '#000000', // Black background
        text: '#00ff00', // Green text
      },
    },
  },
  plugins: [],
};

export default config;