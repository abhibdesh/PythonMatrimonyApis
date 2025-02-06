from celery.schedules import crontab
from main import celery

celery.conf.beat_schedule = {
    'clear_inactive_sessions_every_30_min': {
        'task': 'app.clear_inactive_sessions',
        'schedule': crontab(minute='*/2'),  # Runs every 30 minutes
    },
}
