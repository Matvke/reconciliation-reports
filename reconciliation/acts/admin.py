from django.contrib import admin

from .models import Act, Store, Summary, Supply, Tag, Transaction

admin.site.register((Supply, Transaction, Store, Summary, Act, Tag))
