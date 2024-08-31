import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# app.conf.beat_shedule = {
#     'send_notifies_on_mondays': {
#         'task': 'news.tasks.send_notifies',
#         'schedule': crontab(),
#         # 'args': (),
#     }
# }

# celery -A your_project worker --loglevel=info --pool=solo
# celery -A NewsPortal beat --loglevel=info
