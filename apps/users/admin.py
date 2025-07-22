from django.contrib import admin

from apps.users.models import Address, Profile

# Register your models here.
admin.site.register(Profile)
admin.site.register(Address)