from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('HourX Info', {'fields': ('time_balance', 'bio', 'profile_picture')}),
    )

admin.site.register(User, CustomUserAdmin)
