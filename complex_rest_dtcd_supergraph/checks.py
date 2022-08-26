"""
Custom checks for this plugin.

See https://docs.djangoproject.com/en/4.0/topics/checks/#module-django.core.checks
for details.
"""

from django.core.checks import Warning, register, Tags

from . import settings
from .models import Root


# TODO deprecate this check when fron-end team switches to explicit
# root management
@register(Tags.database, Tags.models)
def check_default_root_exists(app_configs, **kwargs):
    # stop if this plugin is not included in apps to check
    if app_configs is not None and settings.PLUGIN_NAME not in app_configs:
        return []

    errors = []

    # if default root does not exist, issue a warning
    root = Root.nodes.get_or_none(uid=settings.DEFAULT_ROOT_UUID.hex)

    if root is None:
        errors.append(
            Warning(
                "Default Root node does not exist.",
                hint="You can create it with 'create_default_root_node' command.",
            )
        )
    return errors
