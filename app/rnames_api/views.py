from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from rnames_app import filters, models

from rnames_api import serializers, models as api_models
from rnames_api.permissions import HasUserApiKey, get_api_key

class ApiViewSet(viewsets.ModelViewSet):
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			permission_classes = []
		else:
			permission_classes = [permissions.IsAdminUser | HasUserApiKey]
		
		return [permission() for permission in permission_classes]

	def create(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid():
			serializer.save()

			if not (request.user != None and request.user.is_staff): # Api request using IsAdminUser permission
				api_key = get_api_key(request)
				self.log_access(api_key, serializer.instance)

			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	class Meta:
		abstract = True

class LocationViewSet(ApiViewSet):
	queryset = models.Location.objects.is_active()
	serializer_class = serializers.LocationSerializer
	filterset_class = filters.LocationFilter
	def log_access(self, api_key, instance):
		api_models.KeyLocation(location=instance, api_key=api_key).save()

class NameViewSet(ApiViewSet):
	queryset = models.Name.objects.is_active()
	serializer_class = serializers.NameSerializer
	filterset_class = filters.NameFilter

	def log_access(self, api_key, instance):
		api_models.KeyName(name=instance, api_key=api_key).save()

class QualifierViewSet(ApiViewSet):
	queryset = models.Qualifier.objects.is_active()
	serializer_class = serializers.QualifierSerializer
	filterset_class = filters.QualifierFilter

	def log_access(self, api_key, instance):
		api_models.KeyQualifier(qualifier=instance, api_key=api_key).save()

class QualifierNameViewSet(ApiViewSet):
	queryset = models.QualifierName.objects.is_active()
	serializer_class = serializers.QualifierNameSerializer
	filterset_class = filters.QualifierNameFilter

	def log_access(self, api_key, instance):
		api_models.KeyQualifierName(qualifier_name=instance, api_key=api_key).save()

class StratigraphicQualifierViewSet(ApiViewSet):
	queryset = models.StratigraphicQualifier.objects.is_active()
	serializer_class = serializers.StratigraphicQualifierSerializer
	filterset_class = filters.StratigraphicQualifierFilter

	def log_access(self, api_key, instance):
		api_models.KeyStratigraphicQualifier(stratigraphic_qualifier=instance, api_key=api_key).save()

class StructuredNameViewSet(ApiViewSet):
	queryset = models.StructuredName.objects.is_active()
	serializer_class = serializers.StructuredNameSerializer
	filterset_class = filters.StructuredNameFilter

	def log_access(self, api_key, instance):
		api_models.KeyStructuredName(structured_name=instance, api_key=api_key).save()

class ReferenceViewSet(ApiViewSet):
	queryset = models.Reference.objects.is_active()
	serializer_class = serializers.ReferenceSerializer
	filterset_class = filters.ReferenceFilter

	def log_access(self, api_key, instance):
		api_models.KeyReference(reference=instance, api_key=api_key).save()

class RelationViewSet(ApiViewSet):
	queryset = models.Relation.objects.is_active()
	serializer_class = serializers.RelationSerializer
	filterset_class = filters.RelationFilter

	def log_access(self, api_key, instance):
		api_models.KeyRelation(relation=instance, api_key=api_key).save()

class TimeSliceViewSet(ApiViewSet):
	queryset = models.TimeSlice.objects.is_active()
	serializer_class = serializers.TimeSliceSerializer
	filterset_class = filters.TimeSliceFilter

	def log_access(self, api_key, instance):
		api_models.KeyTimeSlice(time_slice=instance, api_key=api_key).save()

class BinningViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Binning.objects.all()
	serializer_class = serializers.BinningSerializer
