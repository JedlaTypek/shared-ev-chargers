FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
        curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install uv

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app
COPY . .

# PROD: --frozen zajistí, že se nainstalují přesně verze z uv.lock
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 80

# ZDE JE ZMĚNA: Migrace + Start bez reloadu
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 80"]