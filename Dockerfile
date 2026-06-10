FROM node:22-alpine AS frontend-builder

WORKDIR /build
COPY demo/package.json demo/package-lock.json* ./
RUN npm ci
COPY demo/ .
RUN npm run build

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.3.3

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

ENV PATH="/root/.local/bin:$PATH"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* README.md ./
COPY src ./src

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY --from=frontend-builder /build/dist demo/dist

EXPOSE 8000

CMD ["uvicorn", "hr_assistant.main:app", "--host", "0.0.0.0", "--port", "8000"]
