import json

from rest_framework_api_key.permissions import BaseHasAPIKey
from rnames_api.models import UserApiKey

class HasUserApiKey(BaseHasAPIKey):
	model = UserApiKey
