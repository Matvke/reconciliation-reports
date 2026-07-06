FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

FROM base AS builder

COPY requirements_prod.txt .

RUN pip install --upgrade pip && pip install -r requirements_prod.txt

COPY . .

RUN python manage.py collectstatic --noinput --clear

FROM base AS runtime

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "reconciliation.wsgi:application"]

FROM runtime AS migrate

CMD ["python", "manage.py", "migrate", "--noinput"]
