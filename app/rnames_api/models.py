from django.db import models
from rest_framework_api_key.models import AbstractAPIKey
from django_userforeignkey.models.fields import UserForeignKey

class UserApiKey(AbstractAPIKey):
    user = UserForeignKey(auto_user=True, verbose_name="Associated user", related_name='associated_%(class)s')

class ApiKeyHistoricalModel(models.Model):
    api_key = models.ForeignKey(UserApiKey, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        abstract = True
