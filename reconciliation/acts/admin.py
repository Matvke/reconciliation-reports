from django.contrib import admin

from .models import ReconciliationAct, Store, Supply, Transaction

admin.site.register((Supply, Transaction, Store, ReconciliationAct))
