# ProbWin AI - production Dockerfile
# Multi-stage build: deps wheel cache + slim runtime image

FROM python:3.12-slim AS builder

WORKDIR /build

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip wheel --wheel-dir /wheels -r requirements.txt


FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Kopiuj wheele z builder stage
COPY --from=builder /wheels /wheels
COPY requirements.txt ./
RUN pip install --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels

# Kopiuj kod aplikacji
COPY backend/ ./backend/
COPY scripts/ ./scripts/

# Persistent volume mount points (Fly.io / Railway montuja tu dyski)
RUN mkdir -p /data /app/reports
ENV DATABASE_PATH=/data/probwin.sqlite \
    ELO_CACHE_PATH=/data/elo_cache.json

EXPOSE 8000

# Healthcheck (Docker, Railway, Fly.io wszystkie respektuja)
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)" || exit 1

# $PORT jest ustawiany przez Railway/Heroku, $API_HOST przez fly.io
# Default 8000 jesli zadne nie ustawione
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
