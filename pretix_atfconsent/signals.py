from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _, gettext_noop
from django_scopes import scopes_disabled
from i18nfield.strings import LazyI18nString
from pretix.base.models import Event, Order
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import register_mail_placeholders, periodic_task
from pretix.control.signals import nav_event_settings
from pretix.presale.signals import order_info_top

from pretix_atfconsent.helpers import should_collect_consent
from pretix_atfconsent.tasks import consent_to_checkin


@receiver(nav_event_settings, dispatch_uid="atfconsent_nav_event_settings")
def nav_event_settings(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(request.organizer, request.event, 'can_change_event_settings', request=request):
        return []
    return [{
        'label': _('Consent Collection (ATF)'),
        'url': reverse('plugins:pretix_atfconsent:settings', kwargs={
            'event': request.event.slug,
            'organizer': request.organizer.slug,
        }),
        'active': (url.namespace == 'plugins:pretix_atfconsent' and url.url_name == 'settings'),
        'icon': 'check',
    }]


@receiver(order_info_top, dispatch_uid="atfconsent_order_info_top")
def order_info_top(sender: Event, request, order: Order, **kwargs):
    if not should_collect_consent(order):
        return

    template = get_template('pretix_atfconsent/presale/order_info_top.html')
    ctx = {
        'order': order,
        'event': sender,
    }
    return template.render(ctx, request=request)


@receiver(register_mail_placeholders, dispatch_uid="atfconsent_register_mail_placeholders")
def register_mail_renderers(sender, **kwargs):
    from .email import ATFConsentMailTextPlaceholder
    return [ATFConsentMailTextPlaceholder()]


@receiver(periodic_task, dispatch_uid='atfconsent_periodic_task')
@scopes_disabled()
def periodic_task(sender, **kwargs):
    Event_SettingsStore = get_model('pretixbase', 'Event_SettingsStore') # NoQA
    events = list(Event.objects.filter(
        id__in=Event_SettingsStore.objects.filter(
            key='pretix_atfconsent_checkinlist',
            value__isNull=False
        ).values_list('object_id', flat=True),
        plugins__contains='pretix_atfconsent',
    ).values_list('pk', flat=True))

    for eventpk in events:
        consent_to_checkin.apply(args=(eventpk,))


settings_hierarkey.add_default('pretix_atfconsent_enabled', False, bool)
settings_hierarkey.add_default('pretix_atfconsent_explanation', LazyI18nString.from_gettext(
    gettext_noop(
        "Due to the evolving nature of our event, the following information was not yet available at the time "
        "when you registered for this event.\r\n"
        "\r\n"
        "Please take a moment of your time to read through the provided information and confirm that you agree "
        "with the posted information.\r\n"
        "\r\n"
        "Should you not agree with the conditions outlined, we will unfortunately have to cancel your. In this case "
        "you will be provided with a full refund.\r\n"
        "\r\n"
        "If you would like to actively dispute the conditions below and not wait for us to cancel your order due to "
        "non-agreement of the conditions outlined below, feel free to contact us directly at any time."
    )), LazyI18nString)
settings_hierarkey.add_default('pretix_atfconsent_short_explanation', LazyI18nString.from_gettext(
    gettext_noop(
        "Due to the evolving nature of our event, some information was not yet available at the time "
        "when you registered for this event.\r\n"
        "\r\n"
        "Please click the button, take a moment of your time to read through the provided information and confirm "
        "that you agree with the posted information.\r\n"
        "\r\n"
        "Please do this as soon as possible, as we will have to cancel orders of participants that do not actively "
        "provide their consent.\r\n"
    )), LazyI18nString)
settings_hierarkey.add_default('pretix_atfconsent_all_items', True, bool)
settings_hierarkey.add_default('pretix_atfconsent_items', [], list)
