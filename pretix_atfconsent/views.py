import json
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _  # NoQA
from pretix.base.models import Event, LogEntry, Order
from pretix.control.views.event import (
    EventSettingsFormView, EventSettingsViewMixin,
)
from pretix.presale.views.order import OrderModify

from pretix_atfconsent.forms import ATFConsentSettingsForm
from pretix_atfconsent.helpers import (
    confirmation_messages, should_collect_consent,
)


class OrderConsent(OrderModify):
    template_name = "pretix_atfconsent/presale/order_atfconsent.html"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.kwargs = kwargs
        if not self.order:
            raise Http404(_('Unknown order code or not authorized to access this order.'))
        if not should_collect_consent(self.order):
            messages.success(request, _('At this point, you do not need to consent to anything.'))
            return redirect(self.get_order_url())
        return super(OrderModify, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['confirm_messages'] = confirmation_messages(self.order.event)
        return ctx


class OrderConsentDo(OrderModify):
    def post(self, request, *args, **kwargs):
        confirm_messages = confirmation_messages(self.order.event)
        if confirm_messages:
            for key, msg in confirm_messages.items():
                if request.POST.get('confirm_{}'.format(key)) != 'yes':
                    msg = str(_('You need to check all checkboxes on the bottom of the page.'))
                    messages.error(request, msg)
                    return redirect(reverse('plugins:pretix_atfconsent:order.consent', kwargs={
                        'organizer': request.organizer.slug,
                        'event': request.event.slug,
                        'order': self.order.code,
                        'secret': self.order.secret
                    }))

            meta_info = self.order.meta_info_data
            meta_info.update({
                'confirm_messages': [
                    str(m) for m in confirm_messages.values()
                ]
            })
            self.order.meta_info = json.dumps(meta_info)
            self.order.save()

            for msg in meta_info.get('confirm_messages', []):
                self.order.log_action('pretix.event.order.consent', data={'msg': msg})

            messages.success(request, _("Thank you for providing your consent and updating your order."))
        else:
            messages.error(request, _("Something went wrong. Please try again later."))

        return redirect(self.get_order_url())


class ATFConsentSettings(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = ATFConsentSettingsForm
    template_name = 'pretix_atfconsent/control/settings.html'
    permission = 'can_change_settings'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        all_orders = Order.objects.filter(
            event=self.request.event,
            status__in=[Order.STATUS_PENDING, Order.STATUS_PAID]
        )
        ctx['total_orders'] = all_orders.count()
        ctx['given_consents'] = LogEntry.objects.filter(
            event=self.request.event,
            object_id__in=all_orders.values('pk'),
            action_type='pretix.event.order.consent'
        ).order_by('object_id').values_list('object_id', flat=True).distinct().count()
        ctx['pending_consents'] = ctx['total_orders'] - ctx['given_consents']
        return ctx

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_atfconsent:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug
        })
