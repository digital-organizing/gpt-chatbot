"""Import texts into database."""
import json
from typing import Any, List

from django.core.management.base import BaseCommand, CommandParser

from chatbot.models import Realm, Text

BATCH_SIZE = 1024


class Command(BaseCommand):
    """Command to import texts into the db."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a new command."""
        super().__init__(*args, **kwargs)
        self.batch: List[Text] = []

    help = "Import texts into database"

    def _process_line(self, line: str) -> None:
        data = json.loads(line)

        self.batch.append(
            Text(
                realm=self.realm,
                content=data['text'],
                url=data['url'],
                page=data['page'],
            ))

        if len(self.batch) > BATCH_SIZE:
            self._create_db()

    def _create_db(self) -> None:
        Text.objects.bulk_create(self.batch)
        self.batch = []

    def add_arguments(self, parser: CommandParser) -> None:
        """Add arguments to the command."""
        parser.add_argument('realm', type=str)
        parser.add_argument('path', type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command."""
        self.realm = Realm.objects.get(slug=options['realm'])
        self.batch = []
        path: str = options.get('path', '')

        with open(path) as f:
            for line in f:
                self._process_line(line)
            self._create_db()
