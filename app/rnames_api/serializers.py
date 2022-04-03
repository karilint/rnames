from rest_framework import serializers

from rnames_app import models

class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Location
		fields = ['id', 'name']

class NameSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Name
		fields = ['id', 'name']

class QualifierNameSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.QualifierName
		fields = ['id', 'name']

class StratigraphicQualifierSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.StratigraphicQualifier
		fields = ['id', 'name']

class QualifierSerializer(serializers.HyperlinkedModelSerializer):
	qualifier_name = serializers.HyperlinkedRelatedField(view_name='api-qualifier-name-detail', queryset=models.Qualifier.objects.all())
	stratigraphic_qualifier = serializers.HyperlinkedRelatedField(view_name='api-stratigraphic-qualifier-detail', queryset=models.StratigraphicQualifier.objects.all())

	class Meta:
		model = models.Qualifier
		fields = ['id', 'level', 'qualifier_name', 'stratigraphic_qualifier']

class StructuredNameSerializer(serializers.HyperlinkedModelSerializer):
	location = serializers.HyperlinkedRelatedField(view_name='api-location-detail', queryset=models.Location.objects.all())
	name = serializers.HyperlinkedRelatedField(view_name='api-name-detail', queryset=models.Name.objects.all())
	qualifier = serializers.HyperlinkedRelatedField(view_name='api-qualifier-detail', queryset=models.Qualifier.objects.all())
	reference = serializers.HyperlinkedRelatedField(view_name='api-reference-detail', queryset=models.Reference.objects.all())

	class Meta:
		model = models.StructuredName
		fields = ['id', 'location', 'name', 'qualifier', 'reference', 'remarks']

class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Reference
		fields = ['id', 'first_author', 'year', 'title', 'doi', 'link']

class RelationSerializer(serializers.HyperlinkedModelSerializer):
	name_one = serializers.HyperlinkedRelatedField(view_name='api-structured-name-detail', queryset=models.StructuredName.objects.all())
	name_two = serializers.HyperlinkedRelatedField(view_name='api-structured-name-detail', queryset=models.StructuredName.objects.all())
	reference = serializers.HyperlinkedRelatedField(view_name='api-reference-detail', queryset=models.Reference.objects.all())

	class Meta:
		model = models.Relation
		fields = ['id', 'belongs_to', 'name_one', 'name_two', 'reference']

class TimeSliceSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.TimeSlice
		fields = ['id', 'order', 'scheme']

class BinningSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Binning
		fields = ['binning_scheme', 'name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']