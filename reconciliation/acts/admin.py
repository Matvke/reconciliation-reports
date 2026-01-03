from django.contrib import admin

from .models import Act, Store, Summary, Supply, Transaction

admin.site.register((Supply, Transaction, Store, Summary, Act))
