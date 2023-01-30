"""Clear index."""
from django.core.management.base import BaseCommand

from chatbot.collections import drop_collection
from chatbot.models import Realm, Text


class Command(BaseCommand):
    """Command to index texts."""

    def add_arguments(self, parser):
        """Add arguments."""
        parser.add_argument('realm', type=str)

    def handle(self, *args, **options):
        """Start indexing the realm."""
        drop_collection(options['realm'])
        Text.objects.filter(realm=Realm.objects.get(slug=options['realm'])).update(indexed=False)
