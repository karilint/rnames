from .utils.info import BinningProgressUpdater
from .utils.root_binning_ids import main_binning_fun
from . import models

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

    result = main_binning_fun(time_scale['ts_name'], time_scale, ts_names, relations, structured_names)

    # def time_slices(scheme):
    #     return list(BinningSchemeName.objects.filter(scheme=scheme_id).order_by('order').values_list('structured_name__name__name', flat=True))

    # cols = 

    # try:
    #     result = main_binning_fun(queryset_list, cols, {
    #         'rassm': time_slices('rasmussen'),
    #         'berg': time_slices('bergstrom'),
    #         'webby': time_slices('webby'),
    #         'stages': time_slices('stages'),
    #         'periods': time_slices('periods'),
    #         'epochs': time_slices('epochs'),
    #         'eras': time_slices('eras'),
    #         'eons': time_slices('eons')
    #     }, info)
    # except Exception as e:
    #     info.set_error(str(e))
    #     traceback.print_exc()
    #     return

    # update_progress = info.db_update_progress_updater(
    #     len(result['berg'])
    #     + len(result['webby'])
    #     + len(result['stages'])
    #     + len(result['periods'])
    # )

    # create_objects = []
    # update_objects = []

    # def update(obj, oldest, youngest, ts_count, refs, rule):
    #     obj.oldest = oldest
    #     obj.youngest = youngest
    #     obj.ts_count = ts_count
    #     obj.refs = refs
    #     obj.rule = rule
    #     update_objects.append(obj)

    # def create(name, scheme, oldest, youngest, ts_count, refs, rule):
    #     obj = Binning(name=name, binning_scheme=scheme, oldest=oldest, youngest=youngest, ts_count=ts_count, refs=refs, rule=rule)
    #     create_objects.append(obj)

    # def process_result(df, scheme):
    #     col = SimpleNamespace(**{k: v for v, k in enumerate(df.columns)})

    #     for row in df.values:
    #         name = row[col.name]
    #         data = Binning.objects.filter(name=name, binning_scheme=scheme)
    #         if len(data) == 0:
    #             create(name, scheme_id, row[col.oldest], row[col.youngest], row[col.ts_count], row[col.refs], row[col.rule])
    #         else:
    #             update(data[0], row[col.oldest], row[col.youngest], row[col.ts_count], row[col.refs], row[col.rule])
    #         update_progress.update()

    # process_result(result['berg'], 'x_robinb')
    # process_result(result['webby'], 'x_robinw')
    # process_result(result['stages'], 'x_robins')
    # process_result(result['periods'], 'x_robinp')

    # Binning.objects.bulk_create(create_objects, 100)
    # Binning.objects.bulk_update(update_objects, ['oldest', 'youngest', 'ts_count', 'refs', 'rule'], 100)

    # info.finish_binning()
