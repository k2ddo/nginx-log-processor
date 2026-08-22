from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import LogEntry

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ["date", "ip_address", "http_method", "request_uri", "response_code"]
    list_filter = ["http_method", "response_code"]
    list_filter_submit = True
    search_fields = ["ip_address", "user", "request_uri"]
    date_hierarchy = "date"
    readonly_fields = [
        "date",
        "ip_address",
        "user",
        "http_method",
        "request_uri",
        "response_code",
        "response_size",
    ]

    def has_add_permission(self, request) -> bool:
        return False
