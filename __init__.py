﻿from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from geosafe.celery_app import app as celery_app  # noqa

default_app_config = 'geosafe.apps.GeoSAFEAppConfig'
