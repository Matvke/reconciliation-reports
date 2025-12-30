from django.contrib import admin

from .models import ReconiliationAct, Store, Supply, Transaction

admin.site.register((Supply, Transaction, Store, ReconiliationAct))
