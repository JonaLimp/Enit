from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "enit.settings")

app = Celery("enit")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: ["emissions"])


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
