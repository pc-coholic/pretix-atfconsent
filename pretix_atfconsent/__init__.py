from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = '1.0.0'


class PluginApp(PluginConfig):
    name = 'pretix_atfconsent'
    verbose_name = 'After the fact Consent Collector'

    class PretixPluginMeta:
        name = gettext_lazy('After the Fact Consent Collector')
        author = 'Martin Gross'
        description = gettext_lazy('A pretix plugin to collect consent from users after they have already placed their order')
        visible = True
        version = __version__
        category = 'FEATURE'
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_atfconsent.PluginApp'
