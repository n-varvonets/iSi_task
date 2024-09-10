from django.db import models
from django.conf import settings

__all__ = (
    "Thread",
    "Message",
)


class Thread(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='threads'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Check that there are no more than two participants in a thread
        """
        if self.participants.count() > 2:
            raise ValueError('Thread cannot have more than two participants.')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Thread between {', '.join([user.email for user in self.participants.all()])}"


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_messages',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.email} in thread {self.thread.id}"
