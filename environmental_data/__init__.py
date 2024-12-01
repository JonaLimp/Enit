from __future__ import absolute_import, unicode_literals

# This ensures the Celery app is always imported when Django starts,
# and that shared_task will use this app.
from enit.celery import app as celery_app

__all__ = ("celery_app",)
