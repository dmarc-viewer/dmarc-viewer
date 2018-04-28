"""
<Program Name>
    loadviews.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    April, 2018

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Simple django management command to load JSON formatted fixture file
    containing analysis views into db.

<Usage>
    ```
    python manage.py loadviews [<path to fixture>]
    ```
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from website import serializer

logger = logging.getLogger(__name__)

DEFAULT_FIXTURE_PATH = "demo/views.json"

class Command(BaseCommand):
    help = "Load analysis views from JSON fixture file into db"

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="?", type=str,
                default=DEFAULT_FIXTURE_PATH, help="Path to JSON fixture file"
                " containing analysis views")

    def handle(self, *args, **options):
        logging.info("Loading views from '{}'"
                .format(options["path"]))
        serializer.import_views_from_json(options["path"])

