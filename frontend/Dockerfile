FROM node:20-alpine

WORKDIR /app

# Copy package manifests
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variables for development
ENV VITE_API_URL=http://localhost:8000/api
ENV VITE_FIREBASE_API_KEY=""
ENV VITE_FIREBASE_AUTH_DOMAIN=""
ENV VITE_FIREBASE_PROJECT_ID=""
ENV VITE_FIREBASE_STORAGE_BUCKET=""
ENV VITE_FIREBASE_MESSAGING_SENDER_ID=""
ENV VITE_FIREBASE_APP_ID=""

# Start the development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]