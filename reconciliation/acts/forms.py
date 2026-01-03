from django import forms
from django.contrib.auth import get_user_model

from .models import Act, Store, Summary, Supply, Transaction

User = get_user_model()


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "address", "phone_number"]
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
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["date", "price", "store"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
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
        }


class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ["id", "date", "price", "store"]
        widgets = {
            "id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Номер поставки"}
            ),
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
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
        }


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
