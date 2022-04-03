import json

from rest_framework_api_key.permissions import BaseHasAPIKey
from rnames_api.models import UserApiKey

class KeyParser:
	def get(self, request):
		if request.content_type == 'application/json':
			data = json.loads(request.body)
			return data['api_key']

		return None

class HasUserApiKey(BaseHasAPIKey):
	model = UserApiKey
	key_parser = KeyParser()
