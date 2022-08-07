from django.db import models
from rest_framework_api_key.models import AbstractAPIKey
from django_userforeignkey.models.fields import UserForeignKey
from rnames_app import models as rnames_models

class UserApiKey(AbstractAPIKey):
	user = UserForeignKey(auto_user=True, verbose_name="Associated user", related_name='associated_%(class)s')

class ApiKeyUsed(models.Model):
	api_key = models.ForeignKey(UserApiKey, on_delete=models.CASCADE)
	accessed_on = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

class KeyLocation(ApiKeyUsed):
	location = models.ForeignKey(rnames_models.Location, on_delete=models.CASCADE)

class KeyName(ApiKeyUsed):
	name = models.ForeignKey(rnames_models.Name, on_delete=models.CASCADE)

class KeyQualifier(ApiKeyUsed):
	qualifier = models.ForeignKey(rnames_models.Qualifier, on_delete=models.CASCADE)

class KeyQualifierName(ApiKeyUsed):
	qualifier_name = models.ForeignKey(rnames_models.QualifierName, on_delete=models.CASCADE)

class KeyReference(ApiKeyUsed):
	reference = models.ForeignKey(rnames_models.Reference, on_delete=models.CASCADE)

class KeyRelation(ApiKeyUsed):
	relation = models.ForeignKey(rnames_models.Relation, on_delete=models.CASCADE)

class KeyStratigraphicQualifier(ApiKeyUsed):
	stratigraphic_qualifier = models.ForeignKey(rnames_models.StratigraphicQualifier, on_delete=models.CASCADE)

class KeyTimeSlice(ApiKeyUsed):
	time_slice = models.ForeignKey(rnames_models.TimeSlice, on_delete=models.CASCADE)

class KeyStructuredName(ApiKeyUsed):
	structured_name = models.ForeignKey(rnames_models.StructuredName, on_delete=models.CASCADE)
