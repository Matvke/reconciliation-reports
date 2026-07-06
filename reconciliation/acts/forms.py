import re
from decimal import Decimal
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ValidationError

from .models import Act, Store, Summary, Supply, Transaction

User = get_user_model()
MIN_ALLOWED_DATE = date(2000, 1, 1)


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "address", "phone_number", "notes"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Обязательно"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Не обязательно",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+7 (XXX) XXX-XX-XX (не обязательно)",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "не обязательно",
                    "rows": 3,
                }
            ),
        }

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise ValidationError("Укажите название")
        return name

    def clean_address(self):
        address = (self.cleaned_data.get("address") or "").strip()
        return address or None

    def clean_phone_number(self):
        phone_number = (self.cleaned_data.get("phone_number") or "").strip()
        if not phone_number:
            return None

        normalized = re.sub(r"[\s()+-]", "", phone_number)
        if not normalized.isdigit() or not 7 <= len(normalized) <= 15:
            raise ValidationError("Введите корректный номер телефона")

        return phone_number

    def clean_notes(self):
        notes = (self.cleaned_data.get("notes") or "").strip()
        return notes or None


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["date", "price", "store", "tags"]
        widgets = {
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "store": forms.Select(
                attrs={
                    "class": "form-control form-select",
                }
            ),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            raise ValidationError("Укажите сумму")
        if price <= Decimal("0"):
            raise ValidationError("Сумма должна быть положительной")
        if price > Decimal("1000000"):
            raise ValidationError("Сумма не может превышать 1 000 000 ₽")
        return price

    def clean_date(self):
        transaction_date = self.cleaned_data.get("date")
        if not transaction_date:
            raise ValidationError("Укажите дату")
        if transaction_date > date.today():
            raise ValidationError("Дата не может быть в будущем")
        if transaction_date < MIN_ALLOWED_DATE:
            raise ValidationError("Дата не может быть раньше 2000 года")
        return transaction_date

    def clean(self):
        return super().clean()


class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ["id", "date", "price", "store", "tags"]
        widgets = {
            "id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Номер поставки"}
            ),
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "class": "form-control",
                },
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "store": forms.Select(
                attrs={
                    "class": "form-control form-select",
                }
            ),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def clean_id(self):
        supply_id = (self.cleaned_data.get("id") or "").strip().upper()
        if not supply_id:
            raise ValidationError("Номер поставки обязателен")

        if not re.match(r"^[A-Z0-9-]+$", supply_id):
            raise ValidationError("ID может содержать только буквы, цифры и дефис")

        queryset = Supply.objects.filter(id=supply_id)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Поставка с таким номером уже существует")

        return supply_id

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            raise ValidationError("Укажите сумму")
        if price <= Decimal("0"):
            raise ValidationError("Сумма должна быть положительной")
        if price > Decimal("10000000"):
            raise ValidationError("Слишком большая сумма")
        return price

    def clean_date(self):
        supply_date = self.cleaned_data.get("date")
        if not supply_date:
            raise ValidationError("Укажите дату")
        if supply_date > date.today():
            raise ValidationError("Дата не может быть в будущем")
        if supply_date < MIN_ALLOWED_DATE:
            raise ValidationError("Дата не может быть раньше 2000 года")
        return supply_date


class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ["stores", "period_start", "period_end"]
        widgets = {
            "period_start": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "period_end": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        stores = cleaned_data.get("stores")
        period_start = cleaned_data.get("period_start")
        period_end = cleaned_data.get("period_end")

        if not stores:
            raise ValidationError("Выберите хотя бы один магазин")

        if period_start and period_end:
            if period_start > period_end:
                raise ValidationError("Дата начала не может быть позже даты окончания")

            if period_start < MIN_ALLOWED_DATE:
                raise ValidationError("Слишком ранняя дата начала")

            if period_end > date.today():
                raise ValidationError("Дата окончания не может быть в будущем")

            if (period_end - period_start).days > 365:
                raise ValidationError("Период не может превышать 365 дней")

        return cleaned_data


class ActForm(forms.ModelForm):
    class Meta:
        model = Act
        fields = ["period_start", "period_end", "store"]
        widgets = {
            "period_start": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "period_end": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "store": forms.Select(
                attrs={
                    "class": "form-control form-select",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("period_start")
        end = cleaned_data.get("period_end")
        store = cleaned_data.get("store")

        if not store:
            raise ValidationError("Выберите магазин")

        if start and end:
            if start > end:
                raise ValidationError("Дата начала не может быть позже даты окончания")

            if start < MIN_ALLOWED_DATE:
                raise ValidationError("Слишком ранняя дата начала")

            if end > date.today():
                raise ValidationError("Дата окончания не может быть в будущем")

            # Проверка длины периода (например, не больше года)
            if (end - start).days > 365:
                raise ValidationError("Период не может превышать 365 дней")

        return cleaned_data
