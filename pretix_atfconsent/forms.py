from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, gettext_noop  # NoQA
from django_scopes.forms import SafeModelChoiceField
from i18nfield.forms import I18nFormField, I18nTextarea
from pretix.base.forms import SettingsForm
from pretix.base.models import Item, CheckinList
from pretix.control.forms.widgets import Select2


class ATFConsentSettingsForm(SettingsForm):
    pretix_atfconsent_enabled = forms.BooleanField(
        label=_('Enable ATF Consent Collection'),
        required=False
    )

    pretix_atfconsent_explanation = I18nFormField(
        label=_('Long Consent Collection Explanation'),
        help_text=_("This text will be shown on the consent collection page. It should explain to the customer, why "
                    "the consents are collected after the fact, what happens if they do not provide the requested "
                    "consent and until they have time to provide their consent."),
        required=True,
        widget=I18nTextarea,
    )

    pretix_atfconsent_short_explanation = I18nFormField(
        label=_('Short Consent Collection Explanation'),
        help_text=_("This text will be shown on the order page next to a link to the consent page."),
        required=True,
        widget=I18nTextarea,
    )

    pretix_atfconsent_all_items = forms.BooleanField(
        label=_("All products (including newly created ones)"),
        required=False
    )

    pretix_atfconsent_items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.none(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                'class': 'scrolling-multiple-choice',
                'data-inverse-dependency': '#id_pretix_atfconsent_all_items',
            }
        ),
        label=_('Limit to products'),
        initial=None,
        required=False
    )

    pretix_atfconsent_checkinlist = SafeModelChoiceField(
        label=_('Track given consents on Check-In list'),
        queryset=CheckinList.objects.none(),
        required=False,
        disabled=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = kwargs.pop('obj')

        self.fields['pretix_atfconsent_items'].queryset = Item.objects.filter(event=self.event)
        self.fields['pretix_atfconsent_checkinlist'].queryset = self.event.checkin_lists.all()
        self.fields['pretix_atfconsent_checkinlist'].widget = Select2(
            attrs={
                'data-model-select2': 'generic',
                'data-select2-url': reverse('control:event.orders.checkinlists.select2', kwargs={
                    'event': self.event.slug,
                    'organizer': self.event.organizer.slug,
                }),
                'data-placeholder': _('Send to customers checked in on list'),
            }
        )
        self.fields['pretix_atfconsent_checkinlist'].widget.choices = self.fields['pretix_atfconsent_checkinlist'].choices

    def clean(self):
        data = super().clean()

        for k, v in self.fields.items():
            if isinstance(v, forms.ModelMultipleChoiceField):
                if k in data:
                    answstr = [o.pk for o in data[k]]
                    data[k] = answstr

        return data
