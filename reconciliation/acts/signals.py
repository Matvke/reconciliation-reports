from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_delete, post_save

from .models import Act, Store, Summary, Supply, Tag, Transaction


def clear_app_cache(*args, **kwargs):
    cache.clear()


def clear_app_cache_on_m2m_change(sender, action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        cache.clear()


for model in (Act, Store, Summary, Supply, Tag, Transaction):
    post_save.connect(clear_app_cache, sender=model, weak=False)
    post_delete.connect(clear_app_cache, sender=model, weak=False)

for through_model in (
    Supply.tags.through,
    Transaction.tags.through,
    Summary.stores.through,
):
    m2m_changed.connect(
        clear_app_cache_on_m2m_change,
        sender=through_model,
        weak=False,
    )
