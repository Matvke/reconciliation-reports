from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import DecimalField, OuterRef, Prefetch, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
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
from .services import DebtCalculator

User = get_user_model()

cached_view = method_decorator(cache_page(300), name="dispatch")
cookie_vary_view = method_decorator(vary_on_cookie, name="dispatch")


class HealthCheckView(TemplateView):
    def get(self, request, *args, **kwargs):
        return HttpResponse("ok", content_type="text/plain")


@cached_view
@cookie_vary_view
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
        )

        stores = []
        for store in qs:
            supply_total = store.supply_total or Decimal("0")
            transaction_total = store.transaction_total or Decimal("0")
            stores.append(
                {
                    "pk": store.id,
                    "id": store.id,
                    "name": store.name,
                    "supply_total": supply_total,
                    "transaction_total": transaction_total,
                    "debt": supply_total - transaction_total,
                }
            )

        context["stores"] = stores
        context["store_count"] = len(stores)
        context["total_debt"] = sum((store["debt"] for store in stores), Decimal("0"))
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


@cached_view
@cookie_vary_view
class StoreDetailView(LoginRequiredMixin, DetailView):
    model = Store

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "supply",
                    queryset=Supply.objects.order_by("-date", "-timestamp", "-pk").prefetch_related(
                        "tags"
                    ),
                ),
                Prefetch(
                    "transaction",
                    queryset=Transaction.objects.order_by(
                        "-date", "-timestamp", "-pk"
                    ).prefetch_related("tags"),
                ),
                Prefetch("summaries", queryset=Summary.objects.order_by("-date")),
            )
        )

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
                "supplies": list(self.object.supply.all()),
                "transactions": list(self.object.transaction.all()),
                "summaries": list(self.object.summaries.all()),
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
                "title": self.model._meta.verbose_name_plural,
                "create_url_name": "acts:store_create",
                "create_text": "Создать клиента",
                "detail_url_name": "acts:store_detail",
                "update_url_name": "acts:store_update",
                "delete_url_name": "acts:store_delete",
            }
        )
        return context


@cached_view
@cookie_vary_view
class SupplyListView(LoginRequiredMixin, ListMixin, ListView):
    model = Supply
    ordering = "-date"

    def get_queryset(self):
        return super().get_queryset().select_related("store")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.model._meta.verbose_name_plural,
                "create_url_name": "acts:supply_create",
                "create_text": "Создать поставку",
                "detail_url_name": "acts:supply_detail",
                "update_url_name": "acts:supply_update",
                "delete_url_name": "acts:supply_delete",
            }
        )
        return context


@cached_view
@cookie_vary_view
class SupplyDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = Supply
    context_object_name = "supply"

    def get_queryset(self):
        return super().get_queryset().select_related("store").prefetch_related("tags")


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


@cached_view
@cookie_vary_view
class TransactionListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Transaction
    ordering = "-date"

    def get_queryset(self):
        return super().get_queryset().select_related("store")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.model._meta.verbose_name_plural,
                "create_url_name": "acts:transaction_create",
                "create_text": "Создать платеж",
                "detail_url_name": "acts:transaction_detail",
                "update_url_name": "acts:transaction_update",
                "delete_url_name": "acts:transaction_delete",
            }
        )
        return context


@cached_view
@cookie_vary_view
class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    context_object_name = "transaction"

    def get_queryset(self):
        return super().get_queryset().select_related("store").prefetch_related(
            "tags"
        )


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


@cached_view
@cookie_vary_view
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
                "title": self.model._meta.verbose_name_plural,
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

        summary = self.object
        supply_subquery = (
            Supply.objects.filter(store=OuterRef("pk"))
            .values("store")
            .annotate(total=Sum("price"))
            .values("total")
        )
        transaction_subquery = (
            Transaction.objects.filter(store=OuterRef("pk"))
            .values("store")
            .annotate(total=Sum("price"))
            .values("total")
        )

        summaries = list(
            summary.stores.annotate(
                supply_total=Coalesce(
                    Subquery(supply_subquery), Value(0, output_field=DecimalField())
                ),
                transaction_total=Coalesce(
                    Subquery(transaction_subquery),
                    Value(0, output_field=DecimalField()),
                ),
            ).values("id", "name", "supply_total", "transaction_total")
        )

        summaries = [
            {
                "pk": store["id"],
                "id": store["id"],
                "name": store["name"],
                "supply_total": store["supply_total"] or Decimal("0"),
                "transaction_total": store["transaction_total"] or Decimal("0"),
                "debt": (store["supply_total"] or Decimal("0"))
                - (store["transaction_total"] or Decimal("0")),
            }
            for store in summaries
        ]
        summaries.sort(key=lambda item: (-item["debt"], item["name"]))

        total_supply = sum((store["supply_total"] for store in summaries), Decimal("0"))
        total_transaction = sum(
            (store["transaction_total"] for store in summaries), Decimal("0")
        )
        total_debt = sum((store["debt"] for store in summaries), Decimal("0"))

        context.update(
            {
                "stores": summaries,
                "total_supply": total_supply,
                "total_transaction": total_transaction,
                "total_debt": total_debt,
            }
        )
        return context


@cached_view
@cookie_vary_view
class SummaryDetailView(
    SummaryViewMixin,
    LoginRequiredMixin,
    DetailView,
):
    model = Summary


@cached_view
@cookie_vary_view
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


@cached_view
@cookie_vary_view
class ActListView(
    LoginRequiredMixin,
    ListMixin,
    ListView,
):
    model = Act
    ordering = "-date"

    def get_queryset(self):
        return super().get_queryset().select_related("store")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.model._meta.verbose_name_plural,
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
    template_name = "acts/act_detail.html"
    context_object_name = "act"

    def get_queryset(self):
        return super().get_queryset().select_related("store")

    def get_context_data(self, **kwargs):
        act = getattr(self, "object", None) or self.get_object()
        calculator = DebtCalculator(act.store, act.period_start, act.period_end)
        context = super().get_context_data(**kwargs)
        result = calculator.calculate()
        context.update(
            {
                "store": act.store,
                "events": result.events,
                "total_supply": result.total_supply,
                "total_transaction": result.total_transaction,
                "balance_before": result.balance_before,
                "balance_after": result.balance_after,
                "debt": result.debt,
                "overpayment": result.overpayment,
            }
        )
        return context


@cached_view
@cookie_vary_view
class ActDetailView(ActViewMixin, LoginRequiredMixin, DetailView):
    model = Act
    template_name = "acts/act_detail.html"


@cached_view
@cookie_vary_view
class ActPrintView(ActViewMixin, LoginRequiredMixin, DetailView):
    model = Act
    template_name = "acts/act_print.html"
