from decimal import Decimal
from datetime import date

import pytest
from acts.models import Store, Supply, Transaction
from acts.services import DebtCalculator


@pytest.mark.django_db
def test_calculate_balance_before_filter():
    """Есть сделки до start"""
    store = Store.objects.create(name="Test_store")
    # Давно, должно попасть в начальную стоимость
    supply = Supply.objects.create(
        id="1", price=200, date=date(2026, 1, 1), store=store
    )
    transaction = Transaction.objects.create(
        price=40, date=date(2026, 1, 1), store=store
    )
    # Сегодня, не должно попасть в начальную стоимость
    supply1 = Supply.objects.create(
        id="2", price=100, date=date(2026, 3, 16), store=store
    )
    transaction1 = Transaction.objects.create(
        price=80, date=date(2026, 3, 16), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 16), period_end=date(2026, 3, 16)
    )

    # Сумма которая была раньше
    balance_before = -supply.price + transaction.price

    # Рассчитываем долг
    result = calc.calculate()

    assert 2 == len(result.events)
    assert result.balance_before == balance_before
    assert result.balance_before == -200 + 40

    assert result.balance_after == balance_before - supply1.price + transaction1.price
    assert result.balance_after == -200 + 40 - 100 + 80

    assert result.debt == abs(balance_before - supply1.price + transaction1.price)
    assert result.debt == abs(-200 + 40 - 100 + 80)

    assert result.overpayment == 0
    assert result.total_supply == supply1.price
    assert result.total_supply == 100

    assert result.total_transaction == transaction1.price
    assert result.total_transaction == 80


@pytest.mark.django_db
def test_calculate_balance_before():
    """Нет сделок до start"""
    store = Store.objects.create(name="Test_store")
    supply1 = Supply.objects.create(
        id="1", price=100, date=date(2026, 3, 16), store=store
    )
    transaction1 = Transaction.objects.create(
        price=80, date=date(2026, 3, 16), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 16), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert 2 == len(result.events)
    assert result.balance_before == 0

    assert result.balance_after == -supply1.price + transaction1.price
    assert result.balance_after == -100 + 80

    assert result.debt == abs(-supply1.price + transaction1.price)
    assert result.debt == abs(-100 + 80)

    assert result.overpayment == 0

    assert result.total_supply == supply1.price
    assert result.total_supply == 100

    assert result.total_transaction == 80
    assert result.total_transaction == transaction1.price


@pytest.mark.django_db
def test_calculate_debt_no_period():
    """Нет сделок в периоде"""
    store = Store.objects.create(name="Test_store")
    # Давно, должно попасть в начальную стоимость
    supply = Supply.objects.create(
        id="1", price=100, date=date(2026, 1, 1), store=store
    )
    supply1 = Supply.objects.create(
        id="2", price=200, date=date(2026, 1, 2), store=store
    )
    supply2 = Supply.objects.create(
        id="3", price=300, date=date(2026, 1, 3), store=store
    )

    # Сегодня, нет сделок
    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 16), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert 0 == len(result.events)
    assert result.balance_before == -supply.price - supply1.price - supply2.price
    assert result.balance_before == -600

    assert result.balance_after == -600

    assert result.debt == 600
    assert result.overpayment == 0
    assert result.total_supply == 0
    assert result.total_transaction == 0


@pytest.mark.django_db
def test_calculate_debt_full_period():
    """Все сделки в периоде"""
    store = Store.objects.create(name="Test_store")
    # Давно, должно попасть в начальную стоимость
    supply = Supply.objects.create(
        id="1", price=100, date=date(2026, 1, 1), store=store
    )
    supply1 = Supply.objects.create(
        id="2", price=200, date=date(2026, 1, 2), store=store
    )
    supply2 = Supply.objects.create(
        id="3", price=300, date=date(2026, 1, 3), store=store
    )

    # Сегодня, не должно попасть в начальную стоимость
    transaction1 = Transaction.objects.create(
        price=600, date=date(2026, 2, 16), store=store
    )
    transaction2 = Transaction.objects.create(
        price=900, date=date(2026, 3, 16), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 1, 1), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert 5 == len(result.events)
    assert result.balance_before == 0

    assert (
        result.balance_after
        == -supply.price
        - supply1.price
        - supply2.price
        + transaction1.price
        + transaction2.price
    )
    assert result.balance_after == -600 + 600 + 900

    assert result.debt == 0
    assert result.overpayment == 900

    assert result.total_supply == 600
    #
    assert result.total_supply == supply.price + supply1.price + supply2.price

    assert result.total_transaction == transaction1.price + transaction2.price
    assert result.total_transaction == 900 + 600


@pytest.mark.django_db
def test_calculate_debt():
    """Нет поступлений до start"""
    store = Store.objects.create(name="Test_store")
    # Давно, должно попасть в начальную стоимость
    supply = Supply.objects.create(
        id="1", price=100, date=date(2026, 1, 1), store=store
    )
    supply1 = Supply.objects.create(
        id="2", price=200, date=date(2026, 1, 2), store=store
    )
    supply2 = Supply.objects.create(
        id="3", price=300, date=date(2026, 1, 3), store=store
    )

    # Сегодня, не должно попасть в начальную стоимость
    transaction1 = Transaction.objects.create(
        price=600, date=date(2026, 3, 16), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 16), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert 1 == len(result.events)
    assert result.balance_before == -supply.price - supply1.price - supply2.price
    assert result.balance_before == -600

    assert result.balance_after == -600 + transaction1.price
    assert result.balance_after == -600 + 600

    assert result.debt == 0
    assert result.overpayment == 0
    assert result.total_supply == 0
    assert result.total_transaction == transaction1.price


@pytest.mark.django_db
def test_calculate_orders_events_chronologically():
    """События должны идти по дате, а не по типу операции."""
    store = Store.objects.create(name="Test_store")
    later_supply = Supply.objects.create(
        id="1", price=100, date=date(2026, 3, 16), store=store
    )
    earlier_transaction = Transaction.objects.create(
        price=80, date=date(2026, 3, 15), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 15), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert len(result.events) == 2
    assert result.events[0]["type"] == "transaction"
    assert result.events[0]["event"] == earlier_transaction
    assert result.events[1]["type"] == "supply"
    assert result.events[1]["event"] == later_supply


@pytest.mark.django_db
def test_calculate_keeps_decimal_precision():
    """Суммы должны считаться в Decimal без ошибок округления."""
    store = Store.objects.create(name="Decimal Store")
    Supply.objects.create(id="D-1", price=Decimal("0.10"), date=date(2026, 3, 16), store=store)
    Supply.objects.create(id="D-2", price=Decimal("0.20"), date=date(2026, 3, 16), store=store)
    Transaction.objects.create(
        price=Decimal("0.30"), date=date(2026, 3, 16), store=store
    )

    calc = DebtCalculator(
        store=store, period_start=date(2026, 3, 16), period_end=date(2026, 3, 16)
    )

    result = calc.calculate()

    assert result.total_supply == Decimal("0.30")
    assert result.total_transaction == Decimal("0.30")
    assert result.balance_before == Decimal("0")
    assert result.balance_after == Decimal("0.00")
    assert result.debt == Decimal("0")
    assert result.overpayment == Decimal("0.00")
