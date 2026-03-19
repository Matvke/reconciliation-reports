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
    notes = models.CharField(verbose_name="Заметки", null=True, blank=True)

    class Meta:
        verbose_name = "клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]


class Tag(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default="#007bff")

    class Meta:
        verbose_name = "метка"
        verbose_name_plural = "Метки"

    def __str__(self):
        return self.name


class Supply(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=64,
        verbose_name="ID поставки",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата поставки")
    timestamp = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    store = models.ForeignKey(
        Store,
        verbose_name="Магазин получатель поставки",
        on_delete=models.CASCADE,
        related_name="supply",
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Метки")

    class Meta:
        verbose_name = "поставка"
        verbose_name_plural = "Поставки"
        ordering = ("-date",)

    def __str__(self):
        return f"Поставка {self.store} {self.date}"

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]

    def get_tags_display(self):
        return self.tags.all()


class Transaction(models.Model):
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    date = models.DateField(verbose_name="Дата транзакции")
    timestamp = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    store = models.ForeignKey(
        Store,
        verbose_name="Магазин плательщик",
        on_delete=models.CASCADE,
        related_name="transaction",
    )
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Метки")

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "Платежи"
        ordering = ("-date",)

    def __str__(self):
        return f"Платеж {self.store} {self.date}"

    def get_fields(self):
        return [(field, getattr(self, field.name)) for field in self._meta.fields]

    def get_tags_display(self):
        return self.tags.all()


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
        tz = pytz.timezone("Europe/Samara")
        time = self.date.astimezone(tz)
        return f"Сводка от {time.strftime('%d.%m.%Y %H:%M')}"

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
        tz = pytz.timezone("Europe/Samara")
        time = self.date.astimezone(tz)
        return f"Акт сверки от {time.strftime('%d.%m.%Y %H:%M')} {self.store}"

    class Meta:
        verbose_name = "акт сверки"
        verbose_name_plural = "Акты сверки"
