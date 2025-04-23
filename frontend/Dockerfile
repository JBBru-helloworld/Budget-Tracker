# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Bind CRA to all interfaces
ENV HOST=0.0.0.0
# Enable polling for file-watching inside Docker
ENV CHOKIDAR_USEPOLLING=true
ENV WDS_SOCKET_HOST=0.0.0.0
ENV WDS_SOCKET_PORT=3000
ENV WDS_SOCKET_PATH=/sockjs-node

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]

