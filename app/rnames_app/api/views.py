from rest_framework import viewsets
from rest_framework import permissions

from rnames_app.api import serializers
from rnames_app import models

class LocationViewSet(viewsets.ModelViewSet):
	queryset = models.Location.objects.all()
	serializer_class = serializers.LocationSerializer
	permission_classes = []

class NameViewSet(viewsets.ModelViewSet):
	queryset = models.Name.objects.all()
	serializer_class = serializers.NameSerializer
	permission_classes = []

class QualifierViewSet(viewsets.ModelViewSet):
	queryset = models.Qualifier.objects.all()
	serializer_class = serializers.QualifierSerializer
	permission_classes = []

class QualifierNameViewSet(viewsets.ModelViewSet):
	queryset = models.QualifierName.objects.all()
	serializer_class = serializers.QualifierNameSerializer
	permission_classes = []

class StratigraphicQualifierViewSet(viewsets.ModelViewSet):
	queryset = models.StratigraphicQualifier.objects.all()
	serializer_class = serializers.StratigraphicQualifierSerializer
	permission_classes = []

class StructuredNameViewSet(viewsets.ModelViewSet):
	queryset = models.StructuredName.objects.all()
	serializer_class = serializers.StructuredNameSerializer
	permission_classes = []

class ReferenceViewSet(viewsets.ModelViewSet):
	queryset = models.Reference.objects.all()
	serializer_class = serializers.ReferenceSerializer
	permission_classes = []

class RelationViewSet(viewsets.ModelViewSet):
	queryset = models.Relation.objects.all()
	serializer_class = serializers.RelationSerializer
	permission_classes = []

class TimeSliceViewSet(viewsets.ModelViewSet):
	queryset = models.TimeSlice.objects.all()
	serializer_class = serializers.TimeSliceSerializer
	permission_classes = []

class BinningViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = models.Binning.objects.all()
	serializer_class = serializers.BinningSerializer
	permission_classes = []
