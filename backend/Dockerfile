# backend/Dockerfile
FROM python:3.11-slim

# 1. Set working directory
WORKDIR /app

# 2. Install system dependencies (if your requirements need them)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy only requirements for better caching
COPY requirements.txt ./

# 4. Upgrade pip and install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY . .

# 6. Create uploads directory with proper permissions
RUN mkdir -p uploads \
    && chown -R root:root uploads

# 7. Ensure output is logged to console immediately
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 8. Expose application port
EXPOSE 8000

# 9. Run the Uvicorn server with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
