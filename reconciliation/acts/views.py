from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, F, OuterRef, Subquery, Sum, Value
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

from .base_views import (
    ActFormMixin,
    DeleteMixin,
    ListMixin,
    StoreFormMixin,
    SummaryFormMixin,
    SupplyFormMixin,
    TransactionFormMixin,
)
from .models import Act, Store, Summary, Supply, Transaction

User = get_user_model()


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = "pages/index.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supply_sub = (
            Supply.objects.filter(store=OuterRef("pk"))
            .values("store")
            .annotate(total=Sum("price"))
            .values("total")
        )

        transaction_sub = (
            Transaction.objects.filter(store=OuterRef("pk"))
            .values("store")
            .annotate(total=Sum("price"))
            .values("total")
        )

        qs = Store.objects.annotate(
            supply_total=Coalesce(
                Subquery(supply_sub), Value(0, output_field=DecimalField())
            ),
            transaction_total=Coalesce(
                Subquery(transaction_sub), Value(0, output_field=DecimalField())
            ),
        ).annotate(debt=F("supply_total") - F("transaction_total"))

        context["stores"] = qs
        context["store_count"] = len(context["stores"])
        context["total_debt"] = qs.aggregate(total=Sum("debt"))["total"] or 0
        return context


class StoreCreateView(
    LoginRequiredMixin,
    StoreFormMixin,
    CreateView,
):
    pass


class StoreUpdateView(
    LoginRequiredMixin,
    StoreFormMixin,
    UpdateView,
):
    pass


class StoreDeleteView(
    LoginRequiredMixin,
    DeleteMixin,
    DeleteView,
):
    model = Store
    success_url = reverse_lazy("acts:store_list")


class StoreDetailView(LoginRequiredMixin, DetailView):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transaction_total = Transaction.objects.filter(store=self.object).aggregate(
            total=Coalesce(Sum("price"), Value(0, output_field=DecimalField()))
        )["total"]

        supply_total = Supply.objects.filter(store=self.object).aggregate(
            total=Coalesce(Sum("price"), Value(0, output_field=DecimalField()))
        )["total"]

        debt = supply_total - transaction_total
        context.update(
            {
                "debt": debt,
                "transaction_total": transaction_total,
                "supply_total": supply_total,
            }
        )
        return context


class StoreListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Store

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Магазины",
                "create_url_name": "acts:store_create",
                "create_text": "Создать магазин",
                "detail_url_name": "acts:store_detail",
                "update_url_name": "acts:store_update",
                "delete_url_name": "acts:store_delete",
            }
        )
        return context


class SupplyListView(LoginRequiredMixin, ListMixin, ListView):
    model = Supply
    ordering = "date"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Поставки",
                "create_url_name": "acts:supply_create",
                "create_text": "Создать поставку",
                "detail_url_name": "acts:supply_detail",
                "update_url_name": "acts:supply_update",
                "delete_url_name": "acts:supply_delete",
            }
        )
        return context


class SupplyDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = Supply
    context_object_name = "supply"


class SupplyUpdateView(
    LoginRequiredMixin,
    SupplyFormMixin,
    UpdateView,
):
    pass


class SupplyCreateView(
    LoginRequiredMixin,
    SupplyFormMixin,
    CreateView,
):
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


class SupplyDeleteView(
    LoginRequiredMixin,
    DeleteMixin,
    DeleteView,
):
    model = Supply
    success_url = reverse_lazy("acts:supply_list")


class TransactionListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Transaction
    ordering = "date"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Поступления средств",
                "create_url_name": "acts:transaction_create",
                "create_text": "Создать поступление",
                "detail_url_name": "acts:transaction_detail",
                "update_url_name": "acts:transaction_update",
                "delete_url_name": "acts:transaction_delete",
            }
        )
        return context


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    context_object_name = "transaction"


class TransactionUpdateView(
    LoginRequiredMixin,
    TransactionFormMixin,
    UpdateView,
):
    pass


class TransactionCreateView(
    LoginRequiredMixin,
    TransactionFormMixin,
    CreateView,
):
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


class TransactionDeleteView(
    LoginRequiredMixin,
    DeleteMixin,
    DeleteView,
):
    model = Transaction
    success_url = reverse_lazy("acts:transaction_list")


class SummaryCreateView(
    LoginRequiredMixin,
    SummaryFormMixin,
    CreateView,
):
    pass


class SummaryUpdateView(
    LoginRequiredMixin,
    SummaryFormMixin,
    UpdateView,
):
    pass


class SummaryDeleteView(
    LoginRequiredMixin,
    DeleteMixin,
    DeleteView,
):
    model = Summary
    success_url = reverse_lazy("acts:summary_list")
    template_name = "base_confirm_delete.html"


class SummaryListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Summary

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Сводки",
                "create_url_name": "acts:summary_create",
                "create_text": "Создать сводку",
                "detail_url_name": "acts:summary_detail",
                "update_url_name": "acts:summary_update",
                "delete_url_name": "acts:summary_delete",
            }
        )
        return context


class SummaryViewMixin:
    context_object_name = "summary"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        store_list = Summary.objects.get(pk=self.object.id).stores
        summaries = list(
            store_list.annotate(
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

        total_supply = sum(store["supply_total"] for store in summaries)
        total_transaction = sum(store["transaction_total"] for store in summaries)
        total_debt = sum(store["debt"] for store in summaries)

        context.update(
            {
                "stores": summaries,
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


class ActCreateView(
    LoginRequiredMixin,
    ActFormMixin,
    CreateView,
):
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


class ActUpdateView(
    LoginRequiredMixin,
    ActFormMixin,
    UpdateView,
):
    pass


class ActDeleteView(
    LoginRequiredMixin,
    DeleteMixin,
    DeleteView,
):
    model = Act
    success_url = reverse_lazy("acts:act_list")


class ActListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Act

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": "Акты сверки",
                "create_url_name": "acts:act_create",
                "create_text": "Создать акт сверки",
                "detail_url_name": "acts:act_detail",
                "update_url_name": "acts:act_update",
                "delete_url_name": "acts:act_delete",
            }
        )
        return context


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
        balance = balance_before
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
