# IMPORT LIBRARY TO CONNECT WITH RABBITMQ
from __future__ import absolute_import
import os
from celery import Celery
from celery.signals import setup_logging
from event_consumer.handlers import AMQPRetryConsumerStep

from trinity.settings import LOGGING
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trinity.settings')

# CREATE APP CELERY
app = Celery('trinity')
app.steps['consumer'].add(AMQPRetryConsumerStep)

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# CREATE TASKS
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@setup_logging.connect()
def configure_logging(sender=None, **kwargs):
    import logging.config
    logging.config.dictConfig(LOGGING)