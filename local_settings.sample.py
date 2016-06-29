import os
import djcelery
from kombu import Queue
from celery.schedules import crontab

# App specific
# Geosafe - Celery settings

# Pick the correct broker for relaying commands to InaSAFE Headless
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = BROKER_URL

# Specific celery settings. Can be modified accordingly or leave as default
CELERY_ALWAYS_EAGER = False
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_IGNORE_RESULT = False
CELERY_SEND_EVENTS = True
CELERY_TASK_RESULT_EXPIRES = 24 * 3600
CELERY_DISABLE_RATE_LIMITS = True
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"
CELERY_CREATE_MISSING_QUEUES = True

# Defining Celery queue to avoid clash between tasks. Leave as default
CELERY_QUEUES = [
    Queue('default', routing_key='default'),
    Queue('cleanup', routing_key='cleanup'),
    Queue('update', routing_key='update'),
    Queue('email', routing_key='email'),
    Queue('inasafe-headless', routing_key='inasafe-headless'),
    Queue('geosafe', routing_key='geosafe'),
]

# Schedule for periodic tasks
CELERYBEAT_SCHEDULE = {
    # executes every night at 0:0 AM
    'clean-impact-nightly': {
        'task': 'geosafe.tasks.analysis.clean_impact_result',
        'schedule': crontab(hour='0', minute='0')
    }
}

djcelery.setup_loader()

# base url used to resolve layer files accessed by InaSAFE Headless
GEONODE_BASE_URL = 'http://localhost:8000/'
