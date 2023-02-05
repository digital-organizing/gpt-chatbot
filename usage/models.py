from django.contrib.auth import get_user_model
from django.db import models


class Organization(models.Model):
    openai_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    users = models.ManyToManyField(get_user_model(), blank=True)

    def __str__(self) -> str:
        return self.name


class OpenAIModel(models.Model):
    name = models.CharField(max_length=200)
    price_per_1k = models.DecimalField(max_digits=6, decimal_places=5)

    def __str__(self) -> str:
        return self.name


class Charge(models.Model):
    organization = models.ForeignKey(Organization, models.CASCADE)
    tokens_used = models.IntegerField()
    model = models.ForeignKey(OpenAIModel, models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.tokens_used} tokens at {self.model}'
