FROM python:3.11-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies (pdf parsing)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list first (better caching)
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code + storage
COPY . .

# Expose port (Render uses $PORT internally)
EXPOSE 8000

# Start server
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]
