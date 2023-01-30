"""Index texts from a realm into the milvus database."""
from django.core.management.base import BaseCommand

from chatbot.services import index_realm


class Command(BaseCommand):
    """Command to index texts."""

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument('realm', type=str)

    def handle(self, *args, **options):
        """Start indexing the realm."""
        index_realm(options['realm'])
