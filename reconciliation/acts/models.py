from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Store(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        return self.name


class Supply(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=64,
        verbose_name="ID поставки",
        help_text="Введите уникальный идентификатор поставки",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    store = models.ForeignKey(
        Store, verbose_name="Магазин получатель поставки", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "поставка"
        verbose_name_plural = "Поставки"

    def __str__(self):
        return f"Поставка номер {self.id} от {self.date}"


class Transaction(models.Model):
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата транзакции")
    store = models.ForeignKey(
        Store, verbose_name="Магазин плательщик", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платеж от {self.date}. Плательщик {self.store}"
