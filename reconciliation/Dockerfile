FROM python:3.14-slim

WORKDIR /app

RUN pip config set install.timeout 100

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

RUN python manage.py collectstatic --noinput --clear

CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 reconciliation.wsgi:application"]