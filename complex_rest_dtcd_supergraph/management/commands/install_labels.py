"""
Helper script to re-install Neo4j constraints and indexes from current
models.
"""

# See 'install_labels' command in https://github.com/neo4j-contrib/django-neomodel
from django import setup as setup_django
from django.core.management.base import BaseCommand

from neomodel import install_all_labels, remove_all_labels


class Command(BaseCommand):
    help = "Install constraints and indexes for Neo4j database."

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Remove old constrains and indexes before installation",
        )

    def handle(self, *args, **options):
        setup_django()

        # (optional) remove old constrains and indexes
        if options["reset"]:
            try:
                remove_all_labels(stdout=self.stdout)
            except Exception:
                pass

        # install new constrains and indexes from models
        install_all_labels(stdout=self.stdout)
