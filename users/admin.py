from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Додаткові поля', {'fields': ('department',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'department', 'is_staff')
