from pretix.base.models import Event, LogEntry, Order
from pretix.presale.signals import checkout_confirm_messages


def has_consented(order: Order):
    return LogEntry.objects.filter(object_id=order.pk, action_type='pretix.event.order.consent').exists()


def confirmation_messages(event: Event):
    msgs = {}
    responses = checkout_confirm_messages.send(event)
    for receiver, response in responses:
        msgs.update(response)

    return msgs


def should_collect_consent(order: Order):
    return not (
        not order.event.settings.get('pretix_atfconsent_enabled', False)
        or order.status not in [Order.STATUS_PAID, Order.STATUS_PENDING]
        or has_consented(order)
        or not (
            bool(order.positions.filter(item__in=order.event.settings.get('pretix_atfconsent_items', [])))
            if not order.event.settings.get('pretix_atfconsent_all_items', False) else True
        )
        or len(confirmation_messages(order.event)) == 0
    )
