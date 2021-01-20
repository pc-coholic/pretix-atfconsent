from django_scopes import scopes_disabled
from pretix.base.models import Event
from pretix.celery_app import app


@app.task
@scopes_disabled()
def consent_to_checkin(event):
    event = Event.objects.get(pk=event)
    pass
