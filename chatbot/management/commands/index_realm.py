"""Index texts from a realm into the milvus database."""
import argparse
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from chatbot.services import index_realm


class Command(BaseCommand):
    """Command to index texts."""

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments."""
        parser.add_argument('realm', type=str)
        parser.add_argument('--batch_size',
                            type=int,
                            default=10_000,
                            required=False)
        parser.add_argument('--monitor', action=argparse.BooleanOptionalAction)

    def handle(self, *args: Any, **options: Any) -> None:
        """Start indexing the realm."""
        if options['monitor']:
            index_realm(options['realm'], 1, True)
        else:
            index_realm(
                options['realm'],
                options['batch_size'],
            )
