export default {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'your-image-domain.com',
      },
    ],
  },
  env: {
    API_URL: process.env.API_URL, // Example of environment variable
  },
};