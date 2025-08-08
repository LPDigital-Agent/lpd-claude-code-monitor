import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('FLASK_PORT', '5002')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "lpd-neurocenter-backend"

# Server mechanics
daemon = False
pidfile = ".pids/neurocenter_backend_gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for local development)
# keyfile = None
# certfile = None
