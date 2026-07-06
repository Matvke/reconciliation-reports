from decimal import Decimal
from heapq import merge
from dataclasses import dataclass
from typing import Any, Dict, List

from django.db.models import Sum


@dataclass
class ReconciliationResult:
    events: List[Dict[str, Any]]
    balance_before: Decimal
    balance_after: Decimal
    total_supply: Decimal
    total_transaction: Decimal
    debt: Decimal
    overpayment: Decimal


class DebtCalculator:
    def __init__(self, store, period_start, period_end):
        self.store = store
        self.period_start = period_start
        self.period_end = period_end

    def _calculate_balance_before(self):
        supplies_sum_before = (
            self.store.supply.filter(date__lt=self.period_start).aggregate(
                total=Sum("price")
            )["total"]
            or Decimal("0")
        )
        transactions_sum_before = (
            self.store.transaction.filter(date__lt=self.period_start).aggregate(
                total=Sum("price")
            )["total"]
            or Decimal("0")
        )

        return -supplies_sum_before + transactions_sum_before

    def _get_supplies(self):
        return (
            self.store.supply.filter(date__gte=self.period_start, date__lte=self.period_end)
            .only("id", "price", "date", "timestamp")
            .order_by("date", "timestamp", "pk")
        )

    def _get_transactions(self):
        return (
            self.store.transaction.filter(
                date__gte=self.period_start, date__lte=self.period_end
            )
            .only("id", "price", "date", "timestamp")
            .order_by("date", "timestamp", "pk")
        )

    def _event_stream(self, queryset, event_type, type_order):
        for item in queryset:
            yield (
                item.date,
                item.timestamp,
                type_order,
                item.pk,
                {
                    "type": event_type,
                    "event": item,
                    "price": item.price,
                    "date": item.date,
                },
            )

    def calculate(self):
        if self.period_start > self.period_end:
            raise ValueError("period_start cannot be after period_end")

        balance_before = self._calculate_balance_before()

        supplies = self._get_supplies()
        transactions = self._get_transactions()
        events = []
        balance = balance_before
        total_supply = Decimal("0")
        total_transaction = Decimal("0")

        for _, _, _, _, event in merge(
            self._event_stream(supplies, "supply", 0),
            self._event_stream(transactions, "transaction", 1),
        ):
            if event["type"] == "supply":
                balance -= event["price"]
                total_supply += event["price"]
            else:
                balance += event["price"]
                total_transaction += event["price"]
            event["balance"] = balance
            events.append(event)

        return ReconciliationResult(
            events=events,
            balance_before=balance_before,
            balance_after=balance,
            total_supply=total_supply,
            total_transaction=total_transaction,
            debt=abs(min(balance, 0)),
            overpayment=max(balance, 0),
        )
