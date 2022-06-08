from .utils.pbdb_import import pbdb_import
from . import models
from django.db import connection
import pandas as pd

def paleobiology_database_import():
	connection.connect()
	country_codes_df = pd.DataFrame(list(models.CountryCode.objects.all().values('iso3166_1_alpha_2', 'official_name_en' ,'region_name')))
	country_codes_df.rename(inplace=True, columns={'iso3166_1_alpha_2': 'ISO3166-1-Alpha-2', 'region_name': 'Region Name'})
	print(country_codes_df)
	data = pbdb_import(country_codes_df)
	print(data['relations'])
	print(data['references'])
	print(data['structured_names'])