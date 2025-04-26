# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package manifests
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Use the same command as in your docker-compose.yml (npm run dev)
CMD ["npm", "run", "dev"]