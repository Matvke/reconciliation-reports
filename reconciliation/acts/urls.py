from django.urls import path

from .views import (
    ActCreateView,
    ActDeleteView,
    ActDetailView,
    ActListView,
    ActPrintView,
    ActUpdateView,
    HomePage,
    StoreCreateView,
    StoreDeleteView,
    StoreDetailView,
    StoreListView,
    StoreUpdateView,
    SummaryCreateView,
    SummaryDeleteView,
    SummaryDetailView,
    SummaryListView,
    SummaryPrintView,
    SummaryUpdateView,
    SupplyCreateView,
    SupplyDeleteView,
    SupplyDetailView,
    SupplyListView,
    SupplyUpdateView,
    TransactionCreateView,
    TransactionDeleteView,
    TransactionDetailView,
    TransactionListView,
    TransactionUpdateView,
)

urlpatterns = [
    path("", HomePage.as_view(), name="home"),
    path("act_list", ActListView.as_view(), name="act_list"),
    path("act_detail/<int:pk>/", ActDetailView.as_view(), name="act_detail"),
    path("act_update/<int:pk>/", ActUpdateView.as_view(), name="act_update"),
    path("act_delete/<int:pk>/", ActDeleteView.as_view(), name="act_delete"),
    path("act_create", ActCreateView.as_view(), name="act_create"),
    path("act_print/<int:pk>/", ActPrintView.as_view(), name="act_print"),
    path("stores", StoreListView.as_view(), name="stores"),
    path("store_create", StoreCreateView.as_view(), name="store_create"),
    path("store_update/<int:pk>/", StoreUpdateView.as_view(), name="store_update"),
    path("store/<int:pk>/", StoreDetailView.as_view(), name="store_detail"),
    path("store_delete/<int:pk>/", StoreDeleteView.as_view(), name="store_delete"),
    path("summary_create", SummaryCreateView.as_view(), name="summary_create"),
    path("summary/<int:pk>/", SummaryDetailView.as_view(), name="summary_detail"),
    path(
        "summary_delete/<int:pk>/", SummaryDeleteView.as_view(), name="summary_delete"
    ),
    path(
        "summary_update/<int:pk>/", SummaryUpdateView.as_view(), name="summary_update"
    ),
    path("summary_list", SummaryListView.as_view(), name="summary_list"),
    path("summary/<int:pk>/print/", SummaryPrintView.as_view(), name="summary_print"),
    path("supplies", SupplyListView.as_view(), name="supply_list"),
    path("supply_detail/<int:pk>/", SupplyDetailView.as_view(), name="supply_detail"),
    path("supply_delete/<int:pk>/", SupplyDeleteView.as_view(), name="supply_delete"),
    path("supply_update/<int:pk>/", SupplyUpdateView.as_view(), name="supply_update"),
    path("supply_create", SupplyCreateView.as_view(), name="supply_create"),
    path("transaction_list", TransactionListView.as_view(), name="transaction_list"),
    path(
        "transaction_detail/<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction_detail",
    ),
    path(
        "transaction_delete/<int:pk>/",
        TransactionDeleteView.as_view(),
        name="transaction_delete",
    ),
    path(
        "transaction_update/<int:pk>/",
        TransactionUpdateView.as_view(),
        name="transaction_update",
    ),
    path(
        "transaction_create", TransactionCreateView.as_view(), name="transaction_create"
    ),
]
