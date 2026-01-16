import datetime

import pytest
from acts.models import Act, Store, Summary, Supply, Transaction
from django.urls import get_resolver

resolver = get_resolver()


@pytest.fixture
def url_names():
    """Все urls из приложений"""
    app_names = [
        "acts",
    ]
    names = []
    for pattern in resolver.url_patterns:
        if pattern.app_name in app_names:
            for url in pattern.url_patterns:
                names.append(f"{pattern.app_name}:{url.name}")
    return names


def create_test_stores():
    Store.objects.create(name="Test Store1")
    Store.objects.create(name="Test Store 2")


def create_test_supplies():
    Supply.objects.create(
        id="100", price=100, date=datetime.date.today(), store=Store.objects.first()
    )
    Supply.objects.create(
        id="101", price=101, date=datetime.date.today(), store=Store.objects.last()
    )


def create_test_transactions():
    Transaction.objects.create(
        price=100, date=datetime.date.today(), store=Store.objects.first()
    )
    Transaction.objects.create(
        price=100, date=datetime.date.today(), store=Store.objects.last()
    )


def create_test_summaries():
    store1 = Store.objects.first()
    store2 = Store.objects.last()
    Summary.objects.create(
        period_start=datetime.date(year=2020, month=1, day=1),
        period_end=datetime.date.today(),
    )
    Summary.objects.first().stores.add(store1, store2)
    Summary.objects.create(
        period_start=datetime.date(year=2020, month=1, day=1),
        period_end=datetime.date.today(),
    )
    Summary.objects.last().stores.add(store2)


def create_test_acts():
    Act.objects.create(
        period_start=datetime.date(year=2020, month=1, day=1),
        period_end=datetime.date.today(),
        store=Store.objects.first(),
    )
    Act.objects.create(
        period_start=datetime.date(year=2020, month=1, day=1),
        period_end=datetime.date.today(),
        store=Store.objects.last(),
    )


@pytest.fixture
def fill_db(db):
    create_test_stores()
    create_test_supplies()
    create_test_transactions()
    create_test_summaries()
    create_test_acts()
