"""App configuration."""
import logging
import sys

from django.apps import AppConfig
from django.conf import settings
from pymilvus import MilvusException, connections

logger = logging.getLogger(__name__)


class ChatbotConfig(AppConfig):
    """App configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self) -> None:
        """Connect to milvus."""
        if sys.argv[0].endswith('mypy'):
            return
        try:
            connections.connect(host=settings.MILVUS_HOST)
        except MilvusException as e:
            logger.warning("Couldn't connect to Milvus: {}".format(e))

        return super().ready()
