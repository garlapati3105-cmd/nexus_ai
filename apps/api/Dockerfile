FROM python:3.11-slim

# Set environment system configurations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set workspace directories
WORKDIR /app

# Install system utilities and standard packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Expose FastAPI operational port
EXPOSE 8000

# Start server using uvicorn directly with dynamic port binding
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
