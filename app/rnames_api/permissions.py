import json

from rest_framework_api_key.permissions import BaseHasAPIKey
from rnames_api.models import UserApiKey

class HasUserApiKey(BaseHasAPIKey):
	model = UserApiKey

def get_api_key(request):
	if not api_key_header() in request.headers:
		return None

	key = request.META["HTTP_AUTHORIZATION"].split()[1]
	return UserApiKey.objects.get_from_key(key)

def revoke_existing_keys(user):
	existing_keys = UserApiKey.objects.filter(user=user, revoked=False)

	for key in existing_keys:
		key.revoked = True

	UserApiKey.objects.bulk_update(existing_keys, ['revoked'], len(existing_keys))

def revoke_user_api_key(user, prefix):
	existing_keys = UserApiKey.objects.filter(user=user, prefix=prefix, revoked=False)

	for key in existing_keys:
		key.revoked = True

	UserApiKey.objects.bulk_update(existing_keys, ['revoked'], len(existing_keys))

def generate_api_key(request):
	api_key, key = UserApiKey.objects.create_key(name='key',user=request.user)
	return key

def list_api_keys(request):
	return UserApiKey.objects.filter(user=request.user).order_by('-created')

def api_key_header():
	return 'Authorization'