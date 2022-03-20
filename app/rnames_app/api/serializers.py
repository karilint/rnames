from rest_framework import serializers

from rnames_app import models

class LocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Location
		fields = ['id', 'name']
		# fields = ['url', 'id', 'name']
		# extra_kwargs = {
		# 	'url': {'view_name': 'api:location-detail'},
		# }

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
	# qualifier_name_id = serializers.HyperlinkedIdentityField(view_name='api:qualifier-name-detail', lookup_field='id')
	# stratigraphic_qualifier_id = serializers.HyperlinkedIdentityField(view_name='api:stratigraphic-qualifier-detail')

	class Meta:
		model = models.Qualifier
		fields = ['id', 'level', 'qualifier_name_id', 'stratigraphic_qualifier_id']

class StructuredNameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.StructuredName
		fields = ['id', 'location_id', 'name_id', 'qualifier_id', 'reference_id']

class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Reference
		fields = ['id', 'first_author', 'year', 'title', 'doi', 'link']

class RelationSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = models.Relation
		fields = ['id', 'belongs_to', 'name_one_id', 'name_two_id', 'reference_id']

class TimeSliceSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.TimeSlice
		fields = ['id', 'order', 'scheme']

class BinningSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Binning
		fields = ['binning_scheme', 'name', 'oldest', 'youngest', 'ts_count', 'refs', 'rule']
