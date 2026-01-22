# Use Node.js LTS
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
# Use npm install instead of ci because package-lock.json might not exist yet
RUN npm install

# Copy source
COPY . .

# Build
RUN npm run build

# Start
CMD ["npm", "start"]

EXPOSE 3000
