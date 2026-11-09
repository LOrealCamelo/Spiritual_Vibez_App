# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
# Optional enterprise CA bundle for builds behind a TLS proxy. Normal Render
# builds need no secret and use the base image's verified public trust store.
RUN --mount=type=secret,id=build_ca \
    if [ -f /run/secrets/build_ca ]; then export PIP_CERT=/run/secrets/build_ca; fi; \
    python -m pip install --no-cache-dir -r backend/requirements.txt

# The filtered context includes backend, frontend and mobile/assets/tarot.
# Keep them in one layer, including the deck FastAPI mounts at startup.
COPY . .

EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port \"${PORT:-8000}\""]
