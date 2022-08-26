"""
Helper script creates the initial Root node with UID from settings.

TODO Deprecate this command when fron-end team switches to explicit
root management.
"""

from django.core.management.base import BaseCommand

from ...models import Root
from ... import settings


class Command(BaseCommand):
    help = "Create the default Root node"

    def handle(self, *args, **options):
        uid = settings.DEFAULT_ROOT_UUID.hex  # must be hex - see Root
        root = Root.nodes.get_or_none(uid=uid)

        if root is None:
            root = Root(uid=uid, **settings.DEFAULT_ROOT_DATA).save()
            self.stdout.write(
                self.style.SUCCESS("Successfully created root node: %s" % root)
            )
        else:
            self.stdout.write(
                self.style.WARNING("Default root with uid '%s' already exists." % uid)
            )
