from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from typing import Any, Optional
from django.http import HttpRequest
from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer
from django.db.models import Count, Q, QuerySet


__all__ = (
    "ThreadViewSet",
    "MessageViewSet",
)


class ThreadViewSet(viewsets.ModelViewSet):
    """
    ThreadViewSet handles CRUD operations for the Thread model, including:

    - `create`: Checks if a thread with the same participants exists. If found, returns the existing thread, otherwise creates a new one.
    - `destroy`: Deletes a specific thread.
    - `user_threads`: Returns a list of threads for the current authenticated user.
    - `messages`: Retrieves all messages from a specific thread.

    Key methods:
    - `_get_existing_thread`: Finds a thread with exactly two matching participants.
    - Custom validation in `create`: Ensures two unique participants per thread.
    """
    # todo:
    #  - add schema

    serializer_class = ThreadSerializer
    queryset = Thread.objects.all()
    permission_classes = [IsAuthenticated]

    def _get_existing_thread(self, participants: list[int]) -> QuerySet:
        """
        Find a thread with exactly two participants matching the provided IDs.

        Annotates each thread with:
        - participant_count: Total participants in the thread.
        - matching_participants: Number of participants matching the provided list.

        Filters threads where:
        - Exactly 2 participants.
        - Both match the provided IDs.

        ### Example:

        | Thread ID | Participants | participant_count | matching_participants |
        |-----------|--------------|-------------------|-----------------------|
        | 1         | [1, 2]       | 2                 | 1                     |
        | 2         | [2, 3]       | 2                 | 2                     |
        | 3         | [1, 3]       | 2                 | 1                     |
        |-----------|--------------|-------------------|-----------------------|
        """
        return Thread.objects.prefetch_related('participants').annotate(
            participant_count=Count('participants'),  # Count the number of participants in each thread
            matching_participants=Count('participants', filter=Q(participants__in=participants))
            # Count matching participants
        ).filter(
            participant_count=2,  # Only threads with exactly 2 participants
            matching_participants=2  # Both participants must match
        )

    def create(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """
        Override the create method to check if a thread with the same participants already exists.
        If it exists, return the existing thread. Otherwise, create a new thread.
        """
        participants = request.data.get('participants', [])

        # 1.a. ensure that exactly two participants are provided
        if len(participants) != 2:
            return Response({"error": "A thread must have exactly two participants."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 1.b. ensure that both participant IDs are unique (no duplicates)
        if participants[0] == participants[1]:
            return Response({"error": "The same participant cannot be added twice."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 2.find if a thread with the same participants already exists
        participants = list(map(int, participants))
        existing_thread = self._get_existing_thread(participants)
        if existing_thread.exists():
            serializer = self.get_serializer(existing_thread.first())
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 3. if no matching thread exists, create a new thread
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        thread = self.get_object()
        thread.delete()
        return Response({'status': 'Thread deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def user_threads(self, request: HttpRequest) -> Response:
        """
        Returns a paginated list of threads for the current user.
        """
        user = request.user
        threads = Thread.objects.filter(participants=user)
        page = self.paginate_queryset(threads)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(threads, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def messages(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        """
        Custom action to retrieve a paginated list of messages for a specific thread.
        """
        thread = self.get_object()
        messages = thread.messages.select_related('sender').all()
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    MessageViewSet handles CRUD operations for the Message model, including:

    - `unread`: Returns the count of unread messages for the current authenticated user.
    - `mark_as_read`: Marks a specific message as read.
        """
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def unread(self, request: HttpRequest) -> Response:
        """
        Custom action to return the count of unread messages for the current user.
        """
        user = request.user
        unread_messages = Message.objects.filter(is_read=False, thread__participants__in=[user])
        return Response({"unread_count": unread_messages.count()})

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request: HttpRequest, pk: Optional[int] = None) -> Response:
        """
        Custom action to mark a specific message as read based on its primary key (pk).
        """
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response({'status': 'message marked as read'})
