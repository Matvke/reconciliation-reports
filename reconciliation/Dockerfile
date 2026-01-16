FROM python:3.14

WORKDIR /app

RUN  pip config set install.timeout 100

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

RUN mkdir -p /app/static

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 reconciliation.wsgi:application"]