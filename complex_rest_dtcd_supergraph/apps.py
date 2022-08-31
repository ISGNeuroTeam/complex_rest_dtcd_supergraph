"""
Configuration for this Django application / plugin.

https://docs.djangoproject.com/en/4.0/ref/applications/#configuring-applications
"""

from django.apps import AppConfig

from .settings import PLUGIN_NAME


class SupergraphConfig(AppConfig):
    default = True
    name = PLUGIN_NAME
    label = "supergraph"
    verbose_name = "DTCD Supergraph plugin"

    def ready(self) -> None:
        # https://docs.djangoproject.com/en/4.0/ref/applications/#django.apps.AppConfig.ready

        # register checks
        # https://docs.djangoproject.com/en/4.0/topics/checks/#registering-and-labeling-checks
        from . import checks
