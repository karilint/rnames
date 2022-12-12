from django.db import models
from rest_framework_api_key.models import AbstractAPIKey
from django_userforeignkey.models.fields import UserForeignKey
from rnames_app import models as rnames_models

class UserApiKey(AbstractAPIKey):
	user = UserForeignKey(auto_user=True, verbose_name="Associated user", related_name='associated_%(class)s')
