from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ActForm, StoreForm, SummaryForm, SupplyForm, TransactionForm
from .models import Act, Store, Summary, Supply, Transaction

User = get_user_model()


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = "pages/index.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Store.objects.annotate(
            supply_total=Coalesce(
                Sum("supply__price"), Value(0, output_field=DecimalField())
            ),
            transaction_total=Coalesce(
                Sum("transaction__price"), Value(0, output_field=DecimalField())
            ),
        ).annotate(debt=F("supply_total") - F("transaction_total"))
        total_debt = qs.aggregate(
            total=Sum(F("supply_total") - F("transaction_total"))
        )["total"]
        context["stores"] = qs
        context["store_count"] = len(context["stores"])
        context["total_debt"] = total_debt
        return context


class StoreCreateView(LoginRequiredMixin, CreateView):
    model = Store
    form_class = StoreForm

    def get_success_url(self):
        return reverse_lazy("store_detail", kwargs={"pk": self.object.pk})


class StoreDeleteView(LoginRequiredMixin, DeleteView):
    model = Store
    success_url = reverse_lazy("stores")


class StoreUpdateView(LoginRequiredMixin, UpdateView):
    model = Store
    form_class = StoreForm
    success_url = reverse_lazy("stores")

    def get_success_url(self):
        return reverse_lazy("store_detail", kwargs={"pk": self.object.pk})


class StoreDetailView(LoginRequiredMixin, DetailView):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        store_with_stats = (
            Store.objects.filter(pk=self.object.pk)
            .annotate(
                supply_total=Coalesce(
                    Sum("supply__price"), Value(0, output_field=DecimalField())
                ),
                transaction_total=Coalesce(
                    Sum("transaction__price"), Value(0, output_field=DecimalField())
                ),
            )
            .annotate(debt=F("supply_total") - F("transaction_total"))
            .first()
        )

        context.update(
            {
                "debt": store_with_stats.debt,
                "supply_total": store_with_stats.supply_total
                if store_with_stats
                else 0,
                "transaction_total": store_with_stats.transaction_total
                if store_with_stats
                else 0,
            }
        )
        return context


class StoreListView(LoginRequiredMixin, ListView):
    model = Store
    context_object_name = "stores"
    ordering = "id"
    paginate_by = 10


class SupplyListView(LoginRequiredMixin, ListView):
    model = Supply
    ordering = "date"
    context_object_name = "supplies"
    paginate_by = 10


class SupplyDetailView(LoginRequiredMixin, DetailView):
    model = Supply
    context_object_name = "supply"


class SupplyUpdateView(LoginRequiredMixin, UpdateView):
    model = Supply
    form_class = SupplyForm

    success_url = reverse_lazy("supply_list")

    def get_success_url(self):
        return reverse_lazy("supply_detail", kwargs={"pk": self.object.pk})


class SupplyCreateView(LoginRequiredMixin, CreateView):
    model = Supply
    form_class = SupplyForm

    def get_initial(self):
        initial = super().get_initial()
        store_id = self.request.GET.get("store")

        if store_id:
            try:
                store = Store.objects.get(id=store_id)
                initial["store"] = store
            except Store.DoesNotExist:
                pass

        return initial

    def get_success_url(self):
        return reverse_lazy("supply_detail", kwargs={"pk": self.object.id})


class SupplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Supply
    success_url = reverse_lazy("supply_list")


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    ordering = "date"
    context_object_name = "transactions"
    paginate_by = 10


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    context_object_name = "transaction"


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    fields = "__all__"

    success_url = reverse_lazy("transaction_list")

    def get_success_url(self):
        return reverse_lazy("transaction_detail", kwargs={"pk": self.object.pk})


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm

    def get_initial(self):
        initial = super().get_initial()
        store_id = self.request.GET.get("store")

        if store_id:
            try:
                store = Store.objects.get(id=store_id)
                initial["store"] = store
            except Store.DoesNotExist:
                pass

        return initial

    def get_success_url(self):
        return reverse_lazy("transaction_detail", kwargs={"pk": self.object.pk})


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy("transaction_list")
    template_name = "acts/transaction_confirm_delete.html"


class SummaryCreateView(LoginRequiredMixin, CreateView):
    model = Summary
    form_class = SummaryForm
    template_name = "acts/summary_form.html"

    def get_success_url(self):
        return reverse_lazy("summary_detail", kwargs={"pk": self.object.pk})


class SummaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Summary
    fields = "__all__"
    success_url = reverse_lazy("summary_list")

    def get_success_url(self):
        return reverse_lazy("summary_detail", kwargs={"pk": self.object.pk})


class SummaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Summary
    success_url = reverse_lazy("summary_list")


class SummaryListView(LoginRequiredMixin, ListView):
    model = Summary
    context_object_name = "summaries"
    ordering = "id"
    paginate_by = 10


class SummaryViewMixin:
    context_object_name = "summary"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stores_list = list(
            Store.objects.annotate(
                supply_total=Coalesce(
                    Sum("supply__price"), Value(0, output_field=DecimalField())
                ),
                transaction_total=Coalesce(
                    Sum("transaction__price"), Value(0, output_field=DecimalField())
                ),
            )
            .annotate(debt=F("supply_total") - F("transaction_total"))
            .values("id", "name", "supply_total", "transaction_total", "debt")
            .order_by("-debt")
        )

        total_supply = sum(store["supply_total"] for store in stores_list)
        total_transaction = sum(store["transaction_total"] for store in stores_list)
        total_debt = sum(store["debt"] for store in stores_list)

        context.update(
            {
                "stores": stores_list,
                "total_supply": total_supply,
                "total_transaction": total_transaction,
                "total_debt": total_debt,
            }
        )
        return context


class SummaryDetailView(
    SummaryViewMixin,
    LoginRequiredMixin,
    DetailView,
):
    model = Summary


class SummaryPrintView(
    SummaryViewMixin,
    LoginRequiredMixin,
    DetailView,
):
    model = Summary
    template_name = "acts/summary_print.html"


class ActCreateView(LoginRequiredMixin, CreateView):
    model = Act
    form_class = ActForm
    template_name = "acts/act_form.html"

    def get_initial(self):
        initial = super().get_initial()
        store_id = self.request.GET.get("store")

        if store_id:
            try:
                store = Store.objects.get(id=store_id)
                initial["store"] = store
            except Store.DoesNotExist:
                pass

        return initial

    def get_success_url(self):
        return reverse_lazy("act_detail", kwargs={"pk": self.object.pk})


class ActUpdateView(LoginRequiredMixin, UpdateView):
    model = Act
    form_class = ActForm
    success_url = reverse_lazy("act_list")

    def get_success_url(self):
        return reverse_lazy("act_detail", kwargs={"pk": self.object.pk})


class ActDeleteView(LoginRequiredMixin, DeleteView):
    model = Act
    success_url = reverse_lazy("act_list")


class ActListView(LoginRequiredMixin, ListView):
    model = Act
    context_object_name = "acts"
    ordering = "id"
    paginate_by = 10


class ActViewMixin:
    model = Act
    template_name = "act_detail.html"
    context_object_name = "act"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        act = self.get_object()

        supplies = Supply.objects.filter(
            store=act.store, date__gte=act.period_start, date__lte=act.period_end
        ).order_by("date")

        transactions = Transaction.objects.filter(
            store=act.store, date__gte=act.period_start, date__lte=act.period_end
        ).order_by("date")

        events = []

        for supply in supplies:
            events.append(
                {
                    "type": "supply",
                    "date": supply.date,
                    "supply_amount": supply.price,
                    "transaction_amount": None,
                    "supply": supply,
                    "transaction": None,
                    "balance": None,
                }
            )

        for transaction in transactions:
            events.append(
                {
                    "type": "transaction",
                    "date": transaction.date,
                    "supply_amount": None,
                    "transaction_amount": transaction.price,
                    "supply": None,
                    "transaction": transaction,
                    "balance": None,
                }
            )

        events.sort(key=lambda x: x["date"])

        balance = 0
        for event in events:
            if event["type"] == "supply":
                balance += event["supply_amount"]
            else:
                balance -= event["transaction_amount"]
            event["balance"] = balance

        total_supply = (
            supplies.aggregate(
                total=Coalesce(Sum("price"), 0, output_field=DecimalField())
            )["total"]
            or 0
        )

        total_transaction = (
            transactions.aggregate(
                total=Coalesce(Sum("price"), 0, output_field=DecimalField())
            )["total"]
            or 0
        )

        supply_before = (
            Supply.objects.filter(store=act.store, date__lt=act.period_start).aggregate(
                total=Coalesce(Sum("price"), 0, output_field=DecimalField())
            )["total"]
            or 0
        )

        transaction_before = (
            Transaction.objects.filter(
                store=act.store, date__lt=act.period_start
            ).aggregate(total=Coalesce(Sum("price"), 0, output_field=DecimalField()))[
                "total"
            ]
            or 0
        )

        balance_before = supply_before - transaction_before

        balance_after = balance_before + total_supply - total_transaction

        debt = max(balance_after, 0)

        overpayment = abs(min(balance_after, 0))

        context.update(
            {
                "events": events,
                "total_supply": total_supply,
                "total_transaction": total_transaction,
                "balance_before": balance_before,
                "balance_after": balance_after,
                "debt": debt,
                "overpayment": overpayment,
                "store": act.store,
            }
        )

        return context


class ActDetailView(ActViewMixin, LoginRequiredMixin, DetailView):
    model = Act
    template_name = "acts/act_detail.html"


class ActPrintView(ActViewMixin, LoginRequiredMixin, DetailView):
    model = Act
    template_name = "acts/act_print.html"
