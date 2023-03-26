from django.apps import AppConfig

class RnamesApiConfig(AppConfig):
    name = 'rnames_api'

    def ready(self):
        from simple_history.signals import (pre_create_historical_record,)
        from rnames_api.signals import add_history_api_key
        pre_create_historical_record.connect(
            add_history_api_key
        )
