from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from rnames_app import filters, models

from rnames_api import serializers, models as api_models
from rnames_api.permissions import HasUserApiKey, get_api_key

from rnames_api.paginators import Paginator

class ApiViewSet(viewsets.ModelViewSet):
	pagination_class = Paginator

	@method_decorator(cache_page(60*60))
	def list(self, request, format=None):
		qs = self.get_queryset()
		qs = self.filter_queryset(qs)
		page = self.paginate_queryset(qs)
		serializer = self.get_serializer(page, many=True)
		return self.get_paginated_response(serializer.data)

	def get_permissions(self):
		if self.action in ['list', 'retrieve']:
			permission_classes = []
		else:
			permission_classes = [permissions.IsAdminUser | HasUserApiKey]
		
		return [permission() for permission in permission_classes]

	class Meta:
		abstract = True

class LocationViewSet(ApiViewSet):
	queryset = models.Location.objects.all()
	serializer_class = serializers.LocationSerializer
	filterset_class = filters.LocationFilter

class NameViewSet(ApiViewSet):
	queryset = models.Name.objects.all()
	serializer_class = serializers.NameSerializer
	filterset_class = filters.NameFilter

class QualifierViewSet(ApiViewSet):
	filterset_class = filters.QualifierFilter

	def get_queryset(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return models.Qualifier.objects.prefetch_related('qualifier_name', 'stratigraphic_qualifier')

		return models.Qualifier.objects.all()

	def get_serializer_class(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return serializers.QualifierInlineSerializer
		return serializers.QualifierSerializer

class QualifierNameViewSet(ApiViewSet):
	queryset = models.QualifierName.objects.all()
	serializer_class = serializers.QualifierNameSerializer
	filterset_class = filters.QualifierNameFilter

class StratigraphicQualifierViewSet(ApiViewSet):
	queryset = models.StratigraphicQualifier.objects.all()
	serializer_class = serializers.StratigraphicQualifierSerializer
	filterset_class = filters.StratigraphicQualifierFilter

class StructuredNameViewSet(ApiViewSet):
	filterset_class = filters.StructuredNameFilter

	def get_queryset(self):

		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return models.StructuredName.objects.all().select_related()

		return models.StructuredName.objects.all()

	def get_serializer_class(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return serializers.StructuredNameInlineSerializer
		return serializers.StructuredNameSerializer

class ReferenceViewSet(ApiViewSet):
	queryset = models.Reference.objects.all()
	serializer_class = serializers.ReferenceSerializer
	filterset_class = filters.ReferenceFilter

class RelationViewSet(ApiViewSet):
	filterset_class = filters.RelationFilter

	def get_queryset(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return models.Relation.objects.all().select_related()

		return models.Relation.objects.all()

	def get_serializer_class(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return serializers.RelationInlineSerializer
		return serializers.RelationSerializer

class BinningViewSet(viewsets.ReadOnlyModelViewSet):
	filterset_class = filters.BinningFilter
	queryset = models.Binning.objects.all()
	serializer_class = serializers.BinningSerializer

class AbsoluteAgeValueViewSet(ApiViewSet):
	filterset_class = filters.AbsoluteAgeValueFilter
	queryset = models.AbsoluteAgeValue.objects.all()
	serializer_class = serializers.AbsoluteAgeValueSerializer

class TimeScaleViewSet(ApiViewSet):
	queryset = models.TimeScale.objects.all()
	serializer_class = serializers.TimeScaleSerializer

	def log_access(self, api_key, instance):
		pass

class BinningSchemeNameViewSet(ApiViewSet):
	def get_queryset(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return models.BinningSchemeName.objects.all().select_related()

		return models.BinningSchemeName.objects.all()

	def get_serializer_class(self):
		if self.request.method == 'GET' and 'inline' in self.request.query_params:
			return serializers.BinningSchemeNameInlineSerializer
		return serializers.BinningSchemeNameSerializer
