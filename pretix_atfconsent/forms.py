from django import forms
from django.utils.translation import gettext_lazy as _, gettext_noop  # NoQA
from i18nfield.forms import I18nFormField, I18nTextarea
from pretix.base.forms import SettingsForm


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
