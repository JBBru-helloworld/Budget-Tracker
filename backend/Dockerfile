# backend/Dockerfile
FROM python:3.11-slim

# 1. Set working directory
WORKDIR /app

# 2. Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
       libjpeg-dev \
       zlib1g-dev \
       libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy only requirements for better caching
COPY requirements.txt ./

# 4. Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Create necessary directories with proper permissions
RUN mkdir -p uploads static/avatars \
    && chown -R root:root uploads static/avatars

# 7. Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# 8. Expose application port
EXPOSE 8000

# 9. Run the Uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
