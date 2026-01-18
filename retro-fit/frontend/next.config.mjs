import { defineConfig } from 'next';

export default defineConfig({
  reactStrictMode: true,
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['your-image-domain.com'], // Replace with your image domain if needed
  },
  env: {
    API_URL: process.env.API_URL, // Example of environment variable
  },
});