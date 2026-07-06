from datetime import date
from decimal import Decimal

import pytest
from acts.forms import ActForm, StoreForm, SummaryForm, SupplyForm, TransactionForm
from acts.models import Store, Supply


@pytest.mark.django_db
def test_store_form_strips_and_validates_phone():
    form = StoreForm(
        data={
            "name": "  Продукты  ",
            "address": "  Самара, Ленина 1  ",
            "phone_number": " +7 (912) 345-67-89 ",
            "notes": "  Важно  ",
        }
    )

    assert form.is_valid()
    assert form.cleaned_data["name"] == "Продукты"
    assert form.cleaned_data["address"] == "Самара, Ленина 1"
    assert form.cleaned_data["phone_number"] == "+7 (912) 345-67-89"
    assert form.cleaned_data["notes"] == "Важно"


@pytest.mark.django_db
def test_store_form_rejects_invalid_phone():
    form = StoreForm(
        data={
            "name": "Shop",
            "address": "",
            "phone_number": "12-34",
            "notes": "",
        }
    )

    assert not form.is_valid()
    assert "Введите корректный номер телефона" in form.errors["phone_number"][0]


@pytest.mark.django_db
def test_supply_form_normalizes_identifier_and_rejects_duplicates():
    store = Store.objects.create(name="Shop")
    Supply.objects.create(id="AB-1", price=Decimal("10.00"), date=date(2026, 3, 16), store=store)

    form = SupplyForm(
        data={
            "id": "  ab-2  ",
            "date": date(2026, 3, 16),
            "price": Decimal("12.34"),
            "store": store.pk,
            "tags": [],
        }
    )

    assert form.is_valid()
    assert form.cleaned_data["id"] == "AB-2"

    duplicate = SupplyForm(
        data={
            "id": "ab-1",
            "date": date(2026, 3, 16),
            "price": Decimal("12.34"),
            "store": store.pk,
            "tags": [],
        }
    )

    assert not duplicate.is_valid()
    assert "Поставка с таким номером уже существует" in duplicate.errors["id"][0]


@pytest.mark.django_db
def test_transaction_and_summary_forms_validate_periods():
    store = Store.objects.create(name="Shop")

    transaction_form = TransactionForm(
        data={
            "date": date(2026, 3, 16),
            "price": Decimal("1.00"),
            "store": store.pk,
            "tags": [],
        }
    )
    assert transaction_form.is_valid()

    invalid_summary = SummaryForm(
        data={
            "stores": [],
            "period_start": date(2026, 3, 17),
            "period_end": date(2026, 3, 16),
        }
    )
    assert not invalid_summary.is_valid()
    assert "Выберите хотя бы один магазин" in invalid_summary.non_field_errors()[0]

    valid_summary = SummaryForm(
        data={
            "stores": [store.pk],
            "period_start": date(2026, 3, 1),
            "period_end": date(2026, 3, 16),
        }
    )
    assert valid_summary.is_valid()

    invalid_act = ActForm(
        data={
            "period_start": date(2026, 3, 17),
            "period_end": date(2026, 3, 16),
            "store": store.pk,
        }
    )
    assert not invalid_act.is_valid()
    assert "Дата начала не может быть позже даты окончания" in invalid_act.non_field_errors()[0]
