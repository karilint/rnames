from .utils.info import BinningProgressUpdater
from .utils.root_binning_ids import main_binning_fun
from . import models
from rnames_api import serializers
import traceback
import json

from django.db import connection
from types import SimpleNamespace

import pandas as pd

def get_flat_df(serializer):
    j = json.loads(json.dumps(serializer.data))
    return pd.json_normalize(j, sep='_')

def get_relations():
    qs = models.Relation.objects.select_related().all()
    ser = serializers.RelationInlineSerializer(qs, many=True)
    return get_flat_df(ser)

def get_structured_names():
    qs = models.StructuredName.objects.select_related().all()
    ser = serializers.StructuredNameInlineSerializer(qs, many=True)
    return get_flat_df(ser)

def get_sequence(scheme_id):
    qs = models.BinningSchemeName.objects.filter(ts_name=scheme_id).order_by('sequence').select_related()
    ser = serializers.BinningSchemeNameInlineSerializer(qs, many=True)
    return get_flat_df(ser)

def process_binning_result(scheme_id, df, info = None):
    scheme = models.TimeScale.objects.get(pk=scheme_id)
    create_objects = []

    print('Processing binning result')

    models.Binning.objects.filter(binning_scheme=scheme_id).delete()

    col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

    for row in df.values:
        obj = models.Binning(refs=row[col.refs], binning_scheme=scheme)
        obj.structured_name_id = structured_name=row[col.name_id]
        obj.youngest_id = youngest=row[col.youngest_id]
        obj.oldest_id = oldest=row[col.oldest_id]

        create_objects.append(obj)

    models.Binning.objects.bulk_create(create_objects, 100)
    # info.finish_binning()

def process_binning_absolute_age_result(scheme_id, df, info = None):
    scheme = models.TimeScale.objects.get(pk=scheme_id)
    create_objects = []

    print('Processing binning result')

    models.BinningAbsoluteAge.objects.filter(binning_scheme=scheme_id).delete()

    col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

    for row in df.values:
        obj = models.BinningAbsoluteAge(refs=row[col.refs], binning_scheme=scheme, oldest_age=row[col.oldest_age],
            youngest_age=row[col.youngest_age], reference_age=row[col.ref_age], age_constraints=row[col.age_constraints])
        obj.structured_name_id = structured_name=row[col.name_id]
        obj.youngest_id = youngest=row[col.youngest_id]
        obj.oldest_id = oldest=row[col.oldest_id]

        create_objects.append(obj)

    models.BinningAbsoluteAge.objects.bulk_create(create_objects, 100)
    # info.finish_binning()

def process_binning_generalised(scheme_id, df):
    scheme = models.TimeScale.objects.get(pk=scheme_id)
    create_objects = []

    print('Processing generalised binning result')

    models.BinningGeneralised.objects.filter(binning_scheme=scheme_id).delete()

    col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

    for row in df.values:
        obj = models.BinningGeneralised(name=row[col.name], oldest=row[col.oldest], youngest=row[col.youngest], binning_scheme=scheme)
        create_objects.append(obj)

    models.BinningGeneralised.objects.bulk_create(create_objects, 100)
    # info.finish_binning()

def binning_process(scheme_id):
    connection.connect()
    # info = BinningProgressUpdater()

    # if not info.start_binning():
    #     return

    print('Binning ' + str(scheme_id))

    pd.set_option('display.max_columns', None)

    relations = get_relations()
    structured_names = get_structured_names()

    time_scale = pd.DataFrame(list(models.TimeScale.objects.filter(pk=scheme_id).values('id', 'ts_name')))
    sequence = get_sequence(scheme_id)

    print('Binning ' + time_scale['ts_name'][0])

    try:
        result = main_binning_fun(time_scale['ts_name'], time_scale, sequence, relations, structured_names)
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

    process_binning_result(scheme_id, result['binning'])
    process_binning_generalised(scheme_id, result['generalised'])
    process_binning_absolute_age_result(scheme_id, result['absolute_ages'])
    print('Binning finished')
