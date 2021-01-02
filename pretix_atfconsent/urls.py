from django.conf.urls import url

from pretix_atfconsent.views import (
    ATFConsentSettings, OrderConsent, OrderConsentDo,
)

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/atfconsent/$',
        ATFConsentSettings.as_view(), name='settings'),
]

event_patterns = [
    url(r'^order/(?P<order>[^/]+)/(?P<secret>[A-Za-z0-9]+)/consent/$',
        OrderConsent.as_view(), name='order.consent'),
    url(r'^order/(?P<order>[^/]+)/(?P<secret>[A-Za-z0-9]+)/consent/do$',
        OrderConsentDo.as_view(), name='order.consent.do'),
]
