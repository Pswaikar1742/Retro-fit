# Use Node.js LTS
FROM node:20-alpine

WORKDIR /app

# Install dependencies based on package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Start
CMD ["npm", "start"]

EXPOSE 3000
