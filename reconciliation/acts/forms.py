from django import forms

from .models import ReconiliationAct, Supply, Transaction


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
        }


class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ["date", "price", "store"]
        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }


class ReconiliationActForm(forms.ModelForm):
    class Meta:
        model = ReconiliationAct
        fields = "__all__"
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
