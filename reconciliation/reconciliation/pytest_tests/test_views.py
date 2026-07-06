from datetime import date
from decimal import Decimal

from acts.models import Store
from acts.models import Summary, Supply, Transaction
from django.urls import reverse, reverse_lazy


def test_home_page(admin_client, fill_db):
    """Тест проверки стартовой страницы"""
    url = reverse_lazy("acts:home")
    response = admin_client.get(url)
    context = response.context
    stores = context["stores"]
    assert len(stores) == len(Store.objects.all()) == context["store_count"]
    # Проверка на расчет долга.
    # Долг = стоимость поставки - стоимость поступления
    assert stores[0]["debt"] == 0
    assert stores[1]["debt"] == 1
    assert context["total_debt"] == 1


def test_healthz_endpoint(client):
    response = client.get(reverse("acts:healthz"))

    assert response.status_code == 200
    assert response.content == b"ok"


def test_home_page_cache_is_invalidated_on_write(admin_client, fill_db):
    url = reverse_lazy("acts:home")
    first_response = admin_client.get(url)
    first_total = first_response.context["total_debt"]

    store = Store.objects.first()
    Supply.objects.create(
        id="CACHE-1",
        price=5,
        date=date(2026, 3, 16),
        store=store,
    )

    second_response = admin_client.get(url)
    second_total = second_response.context["total_debt"]

    assert first_total == 1
    assert second_total == 6


def test_store_detail_view_page(admin_client, fill_db):
    url = reverse("acts:store_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert context["debt"] == 0
    assert context["supply_total"] == 100
    assert context["transaction_total"] == 100


def test_summary_view_page(admin_client, fill_db):
    url = reverse("acts:summary_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert len(context["stores"]) == len(Store.objects.all())
    assert context["total_supply"] == 201
    assert context["total_transaction"] == 200
    assert context["total_debt"] == 1


def test_summary_view_page_handles_multiple_rows(admin_client):
    summary_store = Store.objects.create(name="Summary Store")
    summary = Summary.objects.create(
        period_start=date(2026, 1, 1),
        period_end=date(2026, 1, 31),
    )
    summary.stores.add(summary_store)

    Supply.objects.create(
        id="S-1",
        price=100,
        date=date(2026, 1, 10),
        store=summary_store,
    )
    Supply.objects.create(
        id="S-2",
        price=200,
        date=date(2026, 1, 11),
        store=summary_store,
    )
    Transaction.objects.create(
        price=30,
        date=date(2026, 1, 12),
        store=summary_store,
    )
    Transaction.objects.create(
        price=45,
        date=date(2026, 1, 13),
        store=summary_store,
    )

    response = admin_client.get(reverse("acts:summary_detail", args=[summary.pk]))
    context = response.context
    row = context["stores"][0]

    assert row["supply_total"] == 300
    assert row["transaction_total"] == 75
    assert row["debt"] == 225
    assert context["total_supply"] == 300
    assert context["total_transaction"] == 75
    assert context["total_debt"] == 225


def test_summary_view_keeps_decimal_precision(admin_client):
    summary_store = Store.objects.create(name="Decimal Store")
    summary = Summary.objects.create(
        period_start=date(2026, 3, 1),
        period_end=date(2026, 3, 31),
    )
    summary.stores.add(summary_store)

    Supply.objects.create(
        id="D-1",
        price=Decimal("0.10"),
        date=date(2026, 3, 10),
        store=summary_store,
    )
    Supply.objects.create(
        id="D-2",
        price=Decimal("0.20"),
        date=date(2026, 3, 11),
        store=summary_store,
    )
    Transaction.objects.create(
        price=Decimal("0.30"),
        date=date(2026, 3, 12),
        store=summary_store,
    )

    response = admin_client.get(reverse("acts:summary_detail", args=[summary.pk]))
    context = response.context
    row = context["stores"][0]

    assert row["supply_total"] == Decimal("0.30")
    assert row["transaction_total"] == Decimal("0.30")
    assert row["debt"] == Decimal("0.00")
    assert context["total_supply"] == Decimal("0.30")
    assert context["total_transaction"] == Decimal("0.30")
    assert context["total_debt"] == Decimal("0.00")


def test_act_view_page(admin_client, fill_db):
    url = reverse("acts:act_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert context["store"] == Store.objects.first()
    assert context["balance_before"] == 0
    assert context["balance_after"] == 0
    assert context["debt"] == 0
    assert context["total_supply"] == 100
    assert context["total_transaction"] == 100
