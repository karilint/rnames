# Create your tasks here

from celery import shared_task
from .binning import binning_process

@shared_task
def binning(scheme_id):
    binning_process(scheme_id)
