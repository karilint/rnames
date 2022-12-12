from rnames_api.permissions import get_api_key
from simple_history.models import HistoricalRecords

def add_history_api_key(sender, **kwargs):
    history_instance = kwargs['history_instance']
    history_instance.api_key = get_api_key(HistoricalRecords.context.request)
