from .utils.pbdb_import import pbdb_import
from .utils.macrostrat_import import macrostrat_import
from . import models
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
import pandas as pd
import numpy as np
import re
import datetime

def create_references(references_map, references_df):
	for index, row in references_df.iterrows():
		doi = ''

		if isinstance(row['doi'], str):
			doi = row['doi']

		ref = models.Reference.objects.filter(title=row['title'], year=row['year'])

		if ref.exists():
			reference = ref[0]
		else:
			reference = models.Reference(
				first_author=row['first_author'],
				year=row['year'],
				title=row['title'],
				doi=doi,
			)
			reference.full_clean()
			reference.save()
			print('Created reference ' + str(reference))

		references_map[row['id']] = reference

def create_structured_name_components(relations_df, cache):
	create_names = []
	create_locations = []

	for index, row in relations_df.iterrows():
		name_1 = models.Name(name=row['Name_one'])
		name_1.clean_fields()
		name_1.clean()
		create_names.append(name_1)

		name_2 = models.Name(name=row['Name_two'])
		name_2.clean_fields()
		name_2.clean()
		create_names.append(name_2)

		row['Name_one'] = name_1.name
		row['Name_two'] = name_2.name

		location_1 = models.Location(name=row['Location_one'])
		location_1.clean_fields()
		location_1.clean()
		create_locations.append(location_1)

		location_2 = models.Location(name=row['Location_two'])
		location_2.clean_fields()
		location_2.clean()
		create_locations.append(location_2)

		row['Location_one'] = location_1.name
		row['Location_two'] = location_2.name

	models.Name.objects.bulk_create(create_names, ignore_conflicts=True)
	models.Location.objects.bulk_create(create_locations, ignore_conflicts=True)

	for name in models.Name.objects.all():
		cache['name'][name.name] = name

	for location in models.Location.objects.all():
		cache['location'][location.name] = location

	for qualifier in models.Qualifier.objects.all().select_related():
		cache['qualifier'][qualifier.qualifier_name.name] = qualifier

	for structured_name in models.StructuredName.objects.all().select_related():
		key = (structured_name.name.name, structured_name.location.name, structured_name.qualifier.qualifier_name.name)
		cache['structured_name'][key] = structured_name

def get_structured_name(name_str, location_str, qualifier_name_str, remarks_str, cache):
	# Bulk create can't be used for structured names since the unique_together constraint is for
	# name, location, qualifier AND reference. A structured name should only have a reference
	# if its usage is "unusual", so there is no reference added to the structured name and the
	# unique_together constraint doesn't catch duplicates with reference=null
	key = (name_str, location_str, qualifier_name_str)

	if key in cache['structured_name']:
		return cache['structured_name'][key]

	try:
		structured_name = models.StructuredName.objects.get(
			name__name=name_str,
			location__name=location_str,
			qualifier__qualifier_name__name=qualifier_name_str
		)
		cache['structured_name'][key] = structured_name
		return structured_name
	except ObjectDoesNotExist:
		pass

	try:
		name = cache['name'][name_str]
	except:
		name = models.Name.objects.get(name=name_str)

	try:
		location = cache['location'][location_str]
	except:
		location = models.Location.objects.get(name=location_str)

	qualifier = cache['qualifier'][qualifier_name_str]

	structured_name = models.StructuredName(name=name, location=location, qualifier=qualifier, remarks=remarks_str)
	structured_name.save()
	print('Created structured name ' + str(structured_name))
	cache['structured_name'][key] = structured_name
	return structured_name

def create_relations(references_map, relations_df, cache):
	create_relations = []
	row_count = str(relations_df.shape[0])
	i = 0
	for index, row in relations_df.iterrows():
		print('Relations row ' + str(i) + '/' + row_count)
		i = i + 1
		name_one = get_structured_name(
			name_str=row['Name_one'],
			location_str=row['Location_one'],
			qualifier_name_str=row['Qualifier_one'],
			remarks_str=row['Name_one_remarks'],
			cache=cache
		)

		name_two = get_structured_name(
			name_str=row['Name_two'],
			location_str=row['Location_two'],
			qualifier_name_str=row['Qualifier_two'],
			remarks_str=row['Name_two_remarks'],
			cache=cache
		)

		if row['Relation'] == 'belongs to':
			belongs_to = 1
		else:
			belongs_to = 0

		if not isinstance(row['Reference'], list):
			row['Reference'] = [row['Reference']]

		for ref_id in row['Reference']:
			reference = references_map[ref_id]
			create_relations.append(models.Relation(
				name_one=name_one,
				name_two=name_two,
				belongs_to=belongs_to,
				reference=reference
			))

	models.Relation.objects.bulk_create(create_relations, ignore_conflicts=True)

def pbdb_reference():
	year = datetime.datetime.now().date().year
	title = 'Paleobiology Database'
	return models.Reference.objects.get_or_create(year=year,title=title,)[0]

def macrostrat_reference():
	year = datetime.datetime.now().date().year
	title = 'Macrostrat Database'
	return models.Reference.objects.get_or_create(year=year,title=title,)[0]

def import_data(data, references_map):
	cache = {}
	cache['name'] = {}
	cache['location'] = {}
	cache['qualifier'] = {}
	cache['structured_name'] = {}

	print('Creating structured name components')
	create_structured_name_components(data['relations'], cache)
	print('Finished creating structured name components')

	print('Creating references')
	create_references(references_map, data['references'])
	print('Finished creating references')

	print('Creating relations')
	create_relations(references_map, data['relations'], cache)
	print('Finished creating relations')

	print('Finished importing data')

def paleobiology_database_import():
	print('Starting pbdb import')

	connection.connect()
	country_codes_df = pd.DataFrame(list(models.CountryCode.objects.all().values('iso3166_1_alpha_2', 'official_name_en' ,'region_name')))
	country_codes_df.rename(inplace=True, columns={'iso3166_1_alpha_2': 'ISO3166-1-Alpha-2', 'region_name': 'Region Name'})
	data = pbdb_import(country_codes_df)

	references_map = {}
	references_map['PBDB'] = pbdb_reference()
	import_data(data, references_map);

def macrostrat_database_import():
	print('Starting macrostrat import')

	connection.connect()
	snames = models.StructuredName.objects.all().select_related('name', 'location', 'qualifier', 'reference',
		'qualifier__qualifier_name').values('id', 'name__name', 'qualifier__qualifier_name__name',
			'location__name', 'reference__first_author', 'reference__year','reference__id')

	structured_names_df = pd.DataFrame(snames)

	structured_names_df.rename(columns={
		'name__name': 'name_name',
		'qualifier__qualifier_name__name': 'qualifier_qualifier_name_name',
		'location__name': 'location_name',
		'reference__first_author': 'reference_first_author',
		'reference__year': 'reference_year',
		'reference__id': 'reference_id'
	}, inplace=True)

	data = macrostrat_import(structured_names_df)
	data['references'] = pd.DataFrame()
	data['relations']['Reference'] = 'MSDB'

	references_map = {'MSDB': macrostrat_reference()}
	import_data(data, references_map);
