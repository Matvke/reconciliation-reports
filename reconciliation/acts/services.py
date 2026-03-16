from dataclasses import dataclass
from typing import Any, Dict, List

from django.db.models import Sum


@dataclass
class ReconciliationResult:
    events: List[Dict[str, Any]]
    balance_before: float
    balance_after: float
    total_supply: float
    total_transaction: float
    debt: float
    overpayment: float


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
            or 0
        )
        transactions_sum_before = (
            self.store.transaction.filter(date__lt=self.period_start).aggregate(
                total=Sum("price")
            )["total"]
            or 0
        )

        return -supplies_sum_before + transactions_sum_before

    def _get_supplies(self):
        return self.store.supply.filter(
            date__gte=self.period_start, date__lte=self.period_end
        )

    def _get_transactions(self):
        return self.store.transaction.filter(
            date__gte=self.period_start, date__lte=self.period_end
        )

    def calculate(self):
        supplies = self._get_supplies()
        transactions = self._get_transactions()
        balance_before = self._calculate_balance_before()

        events = []
        balance = balance_before
        total_supply = 0
        total_transaction = 0

        events = []
        for supply in supplies:
            balance -= supply.price
            total_supply += supply.price
            events.append(
                {
                    "type": "supply",
                    "event": supply,
                    "price": supply.price,
                    "balance": balance,
                    "date": supply.date,
                }
            )

        for transaction in transactions:
            balance += transaction.price
            total_transaction += transaction.price
            events.append(
                {
                    "type": "transaction",
                    "event": transaction,
                    "price": transaction.price,
                    "balance": balance,
                    "date": transaction.date,
                }
            )

        return ReconciliationResult(
            events=events,
            balance_before=balance_before,
            balance_after=balance,
            total_supply=total_supply,
            total_transaction=total_transaction,
            debt=abs(min(balance, 0)),
            overpayment=max(balance, 0),
        )
