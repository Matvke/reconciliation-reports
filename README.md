# reconciliation-reports

Reconciliation Reports is a small web application for small business accounting. It provides supply and transaction tracking, summaries and report generation.

## Contents
- [Installation](#installation)
- [Stack](#stack)
- [Purpose](#purpose)
- [Environment Variables](#environment-variables)
- [Tests](#tests)

## Installation
1. Clone the repository 
`git clone https://github.com/Matvke/reconciliation-reports.git`
2. Navigate to the project directory
`cd reconciliation-reports/reconciliation`
3. Create venv and install requirements
`python -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
4. Set up the database migrations
`python manage.py migrate`
5. Create superuser
`python manage.py createsuperuser`
6. Run the application locally
`python manage.py runserver`

## Environment Variables
1. `DATA_DIR=/app/data` The mounted S3 bucket directory.
2. `SECRET_KEY=your_secret_key` Django secret key for cryptographic signing.
3. `ALLOWED_HOSTS=`
4. `CSRF_TRUSTED_ORIGINS=` 

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
This application was developed for a small business to track supplies, transactions and generate reconciliation reports.