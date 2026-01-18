# reconciliation-reports

Reconciliation Reports is a small web application for small business accounting. It provides supply and transaction tracking, summaries and report generation.

## Contents
- [Installation](#Installation)
- [Stack](#Stack)
- [Purpose](#Purpose)
- [Environment Variables](#Environment)

## Installation
1. Clone the repository 
`(https://github.com/Matvke/reconciliation-reports.git)`
2. Navigate to the project directory
`cd reconciliation-reports/reconciliation`
3. Install requirements
`pip install -r requirements.txt`
4. Set up the database migrations
`python manage.py makemigrations`
`python manage.py migrate`
5. Run the application locally
`python manage.py runserver`

## Environment Variables
1. `DATA_DIR=/app/data` The mounted S3 bucket directory where SQLite files are stored.
2. `SECRET_KEY=your_secret_key` Django secret key for cryptographic signing.
3. `ALLOWED_HOSTS=acts-service.internal.containers.cloud.ru` Cloud.ru internal host for internal routing. 
4. `CSRF_TRUSTED_ORIGINS=https://<your_container_app>.containerapps.ru` Cloud.ru public address for CSRF protection.

## Tests
1. Navigate to the project directory
`cd reconciliation-reports/reconciliation`
2. Run tests
`pytest`

## Stack
1. Python 3.11
2. Django 6.0
3. SQLite3 
4. Pytest 9

## Purpose
This application was developed for a small business. A key requirement was reducing the operating expenses.

The goal was achieved by using cloud.ru **Container Apps** (an analog of **AWS App Runner**) and SQLite database stored in mounted S3 bucket.
This setup is a good compromise, since the service is used by a small number of people. 

It costs about 1$ per month, which satisfies the customer.