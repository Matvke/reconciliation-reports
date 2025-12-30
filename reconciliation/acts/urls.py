from django.urls import path

from .views import (
    HomePage,
    ReconciliationActDetailView,
    ReconciliationActPrintView,
    ReconiliationActCreateView,
    ReconiliationActDeleteView,
    ReconiliationActListView,
    ReconiliationActUpdateView,
    StoreCreateView,
    StoreDeleteView,
    StoreDetailView,
    StoreListView,
    StoreUpdateView,
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
    path("stores", StoreListView.as_view(), name="stores"),
    path("store_create", StoreCreateView.as_view(), name="store_create"),
    path("store_update/<int:pk>/", StoreUpdateView.as_view(), name="store_update"),
    path("store/<int:pk>/", StoreDetailView.as_view(), name="store_detail"),
    path("store_delete/<int:pk>/", StoreDeleteView.as_view(), name="store_delete"),
    path("act_create", ReconiliationActCreateView.as_view(), name="act_create"),
    path("act/<int:pk>/", ReconciliationActDetailView.as_view(), name="act_detail"),
    path(
        "act_delete/<int:pk>/", ReconiliationActDeleteView.as_view(), name="act_delete"
    ),
    path(
        "act_update/<int:pk>/", ReconiliationActUpdateView.as_view(), name="act_update"
    ),
    path("act_list", ReconiliationActListView.as_view(), name="act_list"),
    path("act/<int:pk>/print/", ReconciliationActPrintView.as_view(), name="act_print"),
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
