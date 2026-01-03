import pytz
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Store(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")
    address = models.CharField(
        max_length=264, verbose_name="Адрес", null=True, blank=True
    )
    phone_number = models.CharField(
        verbose_name="Номер телефона", null=True, blank=True
    )

    class Meta:
        verbose_name = "магазин"
        verbose_name_plural = "Магазины"

    def __str__(self):
        if self.address:
            return f"Магазин {self.name}. Адрес {self.address}."
        return f"Магазин {self.name}."

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]


class Supply(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=64,
        verbose_name="ID поставки",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата")
    store = models.ForeignKey(
        Store,
        verbose_name="Магазин получатель поставки",
        on_delete=models.CASCADE,
        related_name="supply",
    )

    class Meta:
        verbose_name = "поставка"
        verbose_name_plural = "Поставки"

    def __str__(self):
        return f"Поставка номер {self.id} от {self.date}"

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]


class Transaction(models.Model):
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата транзакции")
    store = models.ForeignKey(
        Store,
        verbose_name="Магазин плательщик",
        on_delete=models.CASCADE,
        related_name="transaction",
    )

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"от {self.date} плательщик {self.store}"

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]


class Summary(models.Model):
    period_start = models.DateField(verbose_name="Дата начала промежутка")
    period_end = models.DateField(verbose_name="Дата конца промежутка")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания сводки")
    stores = models.ManyToManyField(
        Store,
        related_name="summaries",
        verbose_name="Магазины",
    )

    def __str__(self):
        moscow_tz = pytz.timezone("Europe/Moscow")
        moscow_time = self.date.astimezone(moscow_tz)
        return f"от {moscow_time.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "сводка"
        verbose_name_plural = "Сводки"


class Act(models.Model):
    period_start = models.DateField(verbose_name="Дата начала промежутка")
    period_end = models.DateField(verbose_name="Дата конца промежутка")
    date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания акта сверки"
    )
    store = models.ForeignKey(
        Store,
        verbose_name="Магазин",
        on_delete=models.CASCADE,
        related_name="act",
    )

    def __str__(self):
        moscow_tz = pytz.timezone("Europe/Moscow")
        moscow_time = self.date.astimezone(moscow_tz)
        return f"от {moscow_time.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "акт сверки"
        verbose_name_plural = "Акты сверки"
