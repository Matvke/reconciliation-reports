from django.urls import reverse_lazy

from .forms import ActForm, StoreForm, SummaryForm, SupplyForm, TransactionForm
from .models import Act, Store, Summary, Supply, Transaction


class StoreFormMixin:
    model = Store
    form_class = StoreForm
    template_name = "base_form.html"
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"item_name": "магазина"})
        return context

    def get_success_url(self):
        return reverse_lazy("acts:store_detail", kwargs={"pk": self.object.pk})


class SupplyFormMixin:
    model = Supply
    form_class = SupplyForm
    context_object_name = "item"
    template_name = "base_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"item_name": "поставки"})
        return context

    def get_success_url(self):
        return reverse_lazy("acts:supply_detail", kwargs={"pk": self.object.pk})


class TransactionFormMixin:
    model = Transaction
    form_class = TransactionForm
    success_url = reverse_lazy("acts:transaction_list")
    context_object_name = "item"
    template_name = "base_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"item_name": "поступления средств"})
        return context

    def get_success_url(self):
        return reverse_lazy("acts:transaction_detail", kwargs={"pk": self.object.pk})


class SummaryFormMixin:
    model = Summary
    form_class = SummaryForm
    context_object_name = "item"
    template_name = "base_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"item_name": "сводки"})
        return context

    def get_success_url(self):
        return reverse_lazy("acts:summary_detail", kwargs={"pk": self.object.pk})


class ActFormMixin:
    model = Act
    form_class = ActForm
    success_url = reverse_lazy("acts:act_list")
    context_object_name = "item"
    template_name = "base_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"item_name": "акта сверки"})
        return context

    def get_success_url(self):
        return reverse_lazy("acts:act_detail", kwargs={"pk": self.object.pk})


class ListMixin:
    context_object_name = "items"
    ordering = "id"
    template_name = "base_list.html"
    paginate_by = 10


class DeleteMixin:
    template_name = "base_confirm_delete.html"
    context_object_name = "item"
