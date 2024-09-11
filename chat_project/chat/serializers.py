from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Thread

__all__ = (
    "ThreadSerializer",
    "MessageSerializer",
)


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'

    def validate(self, attrs):
        participants = attrs.get('participants', [])
        if len(participants) > 2:
            raise serializers.ValidationError('Thread cannot have more than two participants.')
        return attrs

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])

        # m2m
        thread = Thread.objects.create(**validated_data)
        thread.participants.set(participants)

        return thread


class MessageSerializer(serializers.ModelSerializer):
    thread = serializers.IntegerField()

    class Meta:
        model = Message
        fields = '__all__'

    def validate_thread(self, value):
        """
        Validate that the thread with the given ID exists.
        """
        if not Thread.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Thread with id {value} does not exist.")
        return value

    def validate_sender(self, value):
        """
        Validate that the sender with the given ID exists.
        """
        User = get_user_model()
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(f"Sender with id {value.id} does not exist.")
        return value

