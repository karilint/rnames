from rest_framework import viewsets, permissions

from rnames_app.api import serializers
from rnames_app import filters
from rnames_app import models

class LocationViewSet(viewsets.ModelViewSet):
	queryset = models.Location.objects.all()
	serializer_class = serializers.LocationSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.LocationFilter

class NameViewSet(viewsets.ModelViewSet):
	queryset = models.Name.objects.all()
	serializer_class = serializers.NameSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.NameFilter

class QualifierViewSet(viewsets.ModelViewSet):
	queryset = models.Qualifier.objects.all()
	serializer_class = serializers.QualifierSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.QualifierFilter

class QualifierNameViewSet(viewsets.ModelViewSet):
	queryset = models.QualifierName.objects.all()
	serializer_class = serializers.QualifierNameSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.QualifierNameFilter

class StratigraphicQualifierViewSet(viewsets.ModelViewSet):
	queryset = models.StratigraphicQualifier.objects.all()
	serializer_class = serializers.StratigraphicQualifierSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.StratigraphicQualifierFilter

class StructuredNameViewSet(viewsets.ModelViewSet):
	queryset = models.StructuredName.objects.all()
	serializer_class = serializers.StructuredNameSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.StructuredNameFilter

class ReferenceViewSet(viewsets.ModelViewSet):
	queryset = models.Reference.objects.all()
	serializer_class = serializers.ReferenceSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.ReferenceFilter

class RelationViewSet(viewsets.ModelViewSet):
	queryset = models.Relation.objects.all()
	serializer_class = serializers.RelationSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.RelationFilter

class TimeSliceViewSet(viewsets.ModelViewSet):
	queryset = models.TimeSlice.objects.all()
	serializer_class = serializers.TimeSliceSerializer
	permission_classes = [permissions.IsAdminUser]
	filterset_class = filters.TimeSliceFilter

class BinningViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Binning.objects.all()
	serializer_class = serializers.BinningSerializer
	permission_classes = [permissions.IsAdminUser]
