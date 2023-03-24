from rest_framework import serializers

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ("id", "question", "answer", "count", "bot")
