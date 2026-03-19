import re
from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.forms import ValidationError

from .models import Act, Store, Summary, Supply, Transaction

User = get_user_model()


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
            "notes": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "не обязательно"}
            ),
        }


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
        if price <= 0:
            raise ValidationError("Сумма должна быть положительной")
        if price > 1_000_000:
            raise ValidationError("Сумма не может превышать 1 000 000 ₽")
        return price

    def clean_date(self):
        transaction_date = self.cleaned_data.get("date")
        if not transaction_date:
            raise ValidationError("Укажите дату")
        if transaction_date > date.today():
            raise ValidationError("Дата не может быть в будущем")
        if transaction_date < date(2000, 1, 1):
            raise ValidationError("Дата не может быть раньше 2000 года")
        return transaction_date

    def clean(self):
        cleaned_data = super().clean()
        store = cleaned_data.get("store")
        cleaned_data.get("date")

        if store and not Store.objects.filter(id=store.id).exists():
            raise ValidationError("Выбранный магазин не существует")

        return cleaned_data


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
        supply_id = self.cleaned_data.get("id")
        if not supply_id:
            raise ValidationError("Номер поставки обязателен")

        if not re.match(r"^[A-Z0-9-]+$", supply_id):
            raise ValidationError("ID может содержать только буквы, цифры и дефис")

        if not self.instance.pk:
            if Supply.objects.filter(id=supply_id).exists():
                raise ValidationError("Поставка с таким номером уже существует")

        return supply_id

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is None:
            raise ValidationError("Укажите сумму")
        if price <= 0:
            raise ValidationError("Сумма должна быть положительной")
        if price > 10_000_000:
            raise ValidationError("Слишком большая сумма")
        return price

    def clean_date(self):
        supply_date = self.cleaned_data.get("date")
        if not supply_date:
            raise ValidationError("Укажите дату")
        if supply_date > date.today():
            raise ValidationError("Дата не может быть в будущем")
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

        if start and end:
            if start > end:
                raise ValidationError("Дата начала не может быть позже даты окончания")

            if start < date(2000, 1, 1):
                raise ValidationError("Слишком ранняя дата начала")

            if end > date.today():
                raise ValidationError("Дата окончания не может быть в будущем")

            # Проверка длины периода (например, не больше года)
            if (end - start).days > 365:
                raise ValidationError("Период не может превышать 365 дней")

        return cleaned_data
