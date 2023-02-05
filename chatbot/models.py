"""Models for the application."""
from django.contrib.auth import get_user_model
from django.db import models


class Realm(models.Model):
    """Collects texts and configuration about generating embeddings."""

    openai_key = models.CharField(max_length=200)
    openai_org = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    embedding_model = models.CharField(max_length=100, default="text-embedding-ada-002")
    embedding_dim = models.IntegerField(default=1536)

    users = models.ManyToManyField(get_user_model())

    def __str__(self) -> str:
        """Represent as a string."""
        return self.slug


class Chatbot(models.Model):
    """Configuration for a chatbot."""

    openai_key = models.CharField(max_length=200)
    openai_org = models.CharField(max_length=200, blank=True)

    prompt_template = models.TextField()

    model = models.CharField(max_length=200, default='text-davinci-003')
    model_max_tokens = models.IntegerField(default=4096)

    max_tokens = models.IntegerField(default=720)
    temperature = models.FloatField(default=0.9)
    presence_penality = models.FloatField(default=0)
    frequency_penality = models.FloatField(default=0)

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    realm = models.ForeignKey(Realm, models.CASCADE)

    users = models.ManyToManyField(get_user_model())

    public = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Represent as a string."""
        return self.slug


class Text(models.Model):
    """Text snippet from a website or pdf."""

    realm = models.ForeignKey(Realm, models.CASCADE)

    content = models.TextField()
    url = models.CharField(max_length=2048, blank=True)
    page = models.IntegerField(default=0)

    internal = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    indexed = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Represent as a string."""
        return self.content

    class Meta:
        verbose_name = 'Text'


class Question(models.Model):
    """A question that was asked."""

    created_at = models.DateTimeField(auto_now_add=True)
    question = models.TextField()
    answer = models.TextField()
    context = models.ManyToManyField(Text, blank=True)

    prompt = models.TextField(blank=True)

    bot = models.ForeignKey(Chatbot, models.CASCADE)
    user = models.ForeignKey(get_user_model(), models.SET_NULL, blank=True, null=True)

    def __str__(self) -> str:
        """Represent as a string."""
        return self.question
