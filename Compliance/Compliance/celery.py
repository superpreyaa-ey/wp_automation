
    
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
# from django.conf import settings
# # Set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Compliance.settings')

# app = Celery('Compliance')
# app.conf.enable_utc =False
# app.conf.update(timezone ='Asia/Kolkata')
# app.config_from_object(settings,namespace='CELERY')
# # Using a string here means the worker doesn't have to serialize
# # the configuration object to child processes.
# app.config_from_object('django.conf:settings', namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()

# @app.task(bind= True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
    
    
    
from __future__ import absolute_import , unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Compliance.settings')

app = Celery('Compliance')

app.config_from_object('django.conf:settings',namespace="CELERY")

# app.conf.beat_schedule = {
#     'sendNotification' : {
#         'task':'report.tasks.pending_notification',
#         'schedule': crontab(minute=0, hour=0),
#     }
# }



# Define periodic tasks in the beat_schedule
app.conf.beat_schedule = {
    # 'add-every-30-seconds': {
    #     'task': 'report.tasks.usp_master_cron_report',
    #     'schedule': 30.0,
    #     'args': ()
    # },
    'multiply-at-midnight': {
        'task': 'report.tasks.usp_master_cron_report',
        'schedule': crontab(hour=13, minute=11),
        'args': ()
    },
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
 