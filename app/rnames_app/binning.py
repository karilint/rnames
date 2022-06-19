from .utils.info import BinningProgressUpdater
from .utils.root_binning_ids import main_binning_fun
from . import models
import traceback

from django.db import connection
from types import SimpleNamespace

import pandas as pd

def get_table_as_df(db_columns, model):
    queryset_list = list(model.objects.select_related().values_list(*db_columns))
    df = pd.DataFrame(queryset_list)
    columns = []

    for col in db_columns:
        columns.append(col.replace('__', '_'))

    df.columns = columns
    return df

def get_relations_df():
    db_columns = [
        'id',
        'reference__id',
        'reference__title',
        'reference__year',


        'name_one__id',
        'name_one__location__name',
        'name_one__name__name',
        'name_one__qualifier__level',
        'name_one__qualifier__qualifier_name__name',
        'name_one__qualifier__stratigraphic_qualifier__name',
        'name_one__remarks',

        'name_two__id',
        'name_two__location__name',
        'name_two__name__name',
        'name_two__qualifier__level',
        'name_two__qualifier__qualifier_name__name',
        'name_two__qualifier__stratigraphic_qualifier__name',
        'name_two__remarks',
    ]

    return get_table_as_df(db_columns, models.Relation)

def get_structured_names_df():
    db_columns = [
        'id',

        'name__name',
        'location__name',

        'qualifier__qualifier_name__name',
        'qualifier__stratigraphic_qualifier__name',
        'qualifier__level',

        'reference__id',
        'reference__first_author',
        'reference__year',
        'reference__title',
    ]

    return get_table_as_df(db_columns, models.StructuredName)

def process_results(scheme_id, result, info = None):
    scheme = models.TimeScale.objects.get(pk=scheme_id)
    create_objects = []

    models.Binning.objects.filter(binning_scheme=scheme_id).delete()

    def process_result(df):
        col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

        for row in df.values:
            obj = models.Binning(name=row[col.name], binning_scheme=scheme, oldest_name=row[col.oldest_name], youngest_name=row[col.youngest_name], ts_count=row[col.ts_count], refs=row[col.refs], rule=row[col.rule])
            create_objects.append(obj)

    # todo
    result['binning']['rule'] = '-1'
    result['generalised']['rule'] = '-1'
    result['absolute_ages']['rule'] = '-1'

    result['binning']['ts_count'] = 0
    result['generalised']['ts_count'] = 0
    result['absolute_ages']['ts_count'] = 0

    result['generalised']['refs'] = ''
    result['generalised'].rename(inplace=True, columns={'oldest': 'oldest_name', 'youngest': 'youngest_name'})

    ########

    print('Processing binning')
    process_result(result['binning'])
    print('Processing generalised')
    process_result(result['generalised'])
    print('Processing absolute_ages')
    process_result(result['absolute_ages'])

    models.Binning.objects.bulk_create(create_objects, 100)
    print('Binning finished')
    # info.finish_binning()


def binning_process(scheme_id):
    connection.connect()
    # info = BinningProgressUpdater()

    # if not info.start_binning():
    #     return

    pd.set_option('display.max_columns', None)

    relations = get_relations_df()
    print(relations)

    structured_names = get_structured_names_df()
    print(structured_names)

    time_scale = pd.DataFrame(list(models.TimeScale.objects.filter(pk=scheme_id).values('id', 'ts_name')))
    ts_names = pd.DataFrame(list(models.BinningSchemeName.objects.filter(ts_name=scheme_id).order_by('sequence').values('id', 'ts_name', 'structured_name', 'sequence')))

    try:
        result = main_binning_fun(time_scale['ts_name'], time_scale, ts_names, relations, structured_names)
    except:
        traceback.print_exc()
        return

    # print(result['binning'].columns)
    # Index(['name_id', 'name', 'qualifier_name', 'oldest_id', 'oldest_name', 'youngest_id', 'youngest_name', 'refs', 'binning_scheme'], dtype='object')
    print(result['binning'])

    # print(result['generalised'].columns)
    # Index(['name', 'oldest', 'youngest', 'binning_scheme'], dtype='object')
    print(result['generalised'])

    # print(result['absolute_ages'].columns)
    # Index(['name_id', 'name', 'qualifier_name', 'oldest_id', 'oldest_name', 'youngest_id', 'youngest_name', 'refs', 'binning_scheme', 'oldest_age', 'youngest_age', 'ref_age', 'age_constraints'], dtype='object')
    print(result['absolute_ages'])

    process_results(scheme_id, result);
