# Build React once; serve the website and FastAPI from a single cloud service.
FROM node:22-alpine AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=production \
    CAMPUSMATE_DATASET=jscoe \
    CAMPUSMATE_SEED=1
WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ ./backend/
COPY scripts/serve_cloud.py ./scripts/serve_cloud.py
COPY --from=frontend /build/frontend/dist ./frontend/dist
EXPOSE 10000
CMD ["python", "scripts/serve_cloud.py"]
