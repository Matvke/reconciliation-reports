from acts.models import Store
from django.urls import reverse, reverse_lazy


def test_home_page(admin_client, fill_db):
    """Тест проверки стартовой страницы"""
    url = reverse_lazy("acts:home")
    response = admin_client.get(url)
    context = response.context
    stores = list(context["stores"].values("name", "debt"))
    assert len(stores) == len(Store.objects.all()) == context["store_count"]
    # Проверка на расчет долга.
    # Долг = стоимость поставки - стоимость поступления
    assert stores[0].get("debt") == 0
    assert stores[1].get("debt") == 1
    assert context["total_debt"] == 1


def test_store_detail_view_page(admin_client, fill_db):
    url = reverse("acts:store_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert context["debt"] == 0
    assert context["supply_total"] == 100
    assert context["transaction_total"] == 100


def test_summary_view_page(admin_client, fill_db):
    url = reverse("acts:summary_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert len(context["stores"]) == len(Store.objects.all())
    assert context["total_supply"] == 201
    assert context["total_transaction"] == 200
    assert context["total_debt"] == 1


def test_act_view_page(admin_client, fill_db):
    url = reverse("acts:act_detail", args=[1])
    response = admin_client.get(url)
    context = response.context
    assert context["store"] == Store.objects.first()
    assert context["balance_before"] == 0
    assert context["balance_after"] == 0
    assert context["debt"] == 0
    assert context["total_supply"] == 100
    assert context["total_transaction"] == 100
