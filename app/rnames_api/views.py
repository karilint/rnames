from rest_framework import viewsets, permissions

from rnames_app import filters, models

from rnames_api import serializers
from rnames_api.permissions import HasUserApiKey

class ApiViewSet(viewsets.ModelViewSet):
	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			permission_classes = []
		else:
			permission_classes = [permissions.IsAdminUser | HasUserApiKey]
		
		return [permission() for permission in permission_classes]

class LocationViewSet(ApiViewSet):
	queryset = models.Location.objects.all()
	serializer_class = serializers.LocationSerializer
	filterset_class = filters.LocationFilter

class NameViewSet(ApiViewSet):
	queryset = models.Name.objects.all()
	serializer_class = serializers.NameSerializer
	filterset_class = filters.NameFilter

class QualifierViewSet(ApiViewSet):
	queryset = models.Qualifier.objects.all()
	serializer_class = serializers.QualifierSerializer
	filterset_class = filters.QualifierFilter

class QualifierNameViewSet(ApiViewSet):
	queryset = models.QualifierName.objects.all()
	serializer_class = serializers.QualifierNameSerializer
	filterset_class = filters.QualifierNameFilter

class StratigraphicQualifierViewSet(ApiViewSet):
	queryset = models.StratigraphicQualifier.objects.all()
	serializer_class = serializers.StratigraphicQualifierSerializer
	filterset_class = filters.StratigraphicQualifierFilter

class StructuredNameViewSet(ApiViewSet):
	queryset = models.StructuredName.objects.all()
	serializer_class = serializers.StructuredNameSerializer
	filterset_class = filters.StructuredNameFilter

class ReferenceViewSet(ApiViewSet):
	queryset = models.Reference.objects.all()
	serializer_class = serializers.ReferenceSerializer
	filterset_class = filters.ReferenceFilter

class RelationViewSet(ApiViewSet):
	queryset = models.Relation.objects.all()
	serializer_class = serializers.RelationSerializer
	filterset_class = filters.RelationFilter

class TimeSliceViewSet(ApiViewSet):
	queryset = models.TimeSlice.objects.all()
	serializer_class = serializers.TimeSliceSerializer
	filterset_class = filters.TimeSliceFilter

class BinningViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Binning.objects.all()
	serializer_class = serializers.BinningSerializer
