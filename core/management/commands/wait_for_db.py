import logging
import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

logger = logging.getLogger('shoppero')


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        logger.info('Waiting for database...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                logger.error('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
