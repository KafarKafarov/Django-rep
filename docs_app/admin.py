from django.contrib import admin
from .models import Docs, UserToDocs, Price, Cart

admin.site.register(Docs)
admin.site.register(UserToDocs)
admin.site.register(Price)
admin.site.register(Cart)