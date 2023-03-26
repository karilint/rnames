# Create your tasks here

from celery import shared_task
from .binning import binning_process

@shared_task(bind=True)
def binning(self, scheme_id):
    binning_process(self, scheme_id)
