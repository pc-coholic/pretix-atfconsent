from pretix.base.email import BaseMailTextPlaceholder
from pretix.multidomain.urlreverse import build_absolute_uri


class ATFConsentMailTextPlaceholder(BaseMailTextPlaceholder):
    identifier = 'atfconsent_link'
    required_context = ['order']

    def render(self, context):
        order = context['order']

        return build_absolute_uri(
            order.event,
            'plugins:pretix_atfconsent:order.consent', kwargs={
                'order': order.code,
                'secret': order.secret,
            }
        )

    def render_sample(self, event):
        return build_absolute_uri(
            event,
            'plugins:pretix_atfconsent:order.consent', kwargs={
                'order': 'F8VVL',
                'secret': '6zzjnumtsx136ddy',
            }
        )
