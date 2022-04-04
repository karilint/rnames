from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin
from rnames_api.models import UserApiKey

@admin.register(UserApiKey)
class UserApiKeyModelAdmin(APIKeyModelAdmin):
	list_display = [*APIKeyModelAdmin.list_display, "user"]
	search_fields = [*APIKeyModelAdmin.search_fields, "user"]