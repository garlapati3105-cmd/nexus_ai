import os
import multiprocessing

# Bind TCP port
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Worker counts (standard formula: 2x CPU cores + 1)
workers = int(os.getenv("WEB_CONCURRENCY", "4"))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout guidelines
timeout = int(os.getenv("TIMEOUT", "120"))
keepalive = 5

# Logging logs levels
loglevel = os.getenv("LOG_LEVEL", "info")
errorlog = "-"
accesslog = "-"
