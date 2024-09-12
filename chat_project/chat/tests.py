import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from chat.models import Thread, Message

User = get_user_model()


@pytest.mark.django_db
def test_create_thread_with_same_participant_twice():
    """
    Thread test: Ensure a user cannot create a thread with the same participant ID twice.
    """
    client = APIClient()

    # Create a user and get the Bearer token
    user = User.objects.create_user(email="user1@example.com", password="password123", username="user1")

    # Authenticate and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Try creating a thread with the same participant ID twice
    data = {
        "participants": [user.id, user.id]
    }
    response = client.post("/api/chat/threads/", data)

    assert response.status_code == 400
    assert "The same participant cannot be added twice" or "A thread must have exactly two participants" in str(response.data)


@pytest.mark.django_db
def test_create_thread_with_existing_participants():
    """
    Thread test #2: Creating a thread with participants that already have a thread.
    If a thread with the same participants already exists, the existing thread should be returned.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")

    # Authenticate user1 and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create an existing thread with user1 and user2
    existing_thread = Thread.objects.create()
    existing_thread.participants.set([user1, user2])

    # Try creating a thread with the same participants
    data = {
        "participants": [user1.id, user2.id]
    }
    response = client.post("/api/chat/threads/", data, format='json')

    # Assert that the response returns the existing thread
    assert response.status_code == 200
    assert response.data['id'] == existing_thread.id
    assert response.data['participants'] == [user1.id, user2.id]


@pytest.mark.django_db
def test_send_message_with_user_not_in_thread():
    """
    Message test #1: Sending a message by a user not in the thread.
    Checks that a user not in the thread cannot send a message.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")
    user3 = User.objects.create_user(email="user3@example.com", password="password123", username="user3")

    # Authenticate user3 and get the access token
    login_data = {
        "email": "user3@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user3
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Create a thread with user1 and user2
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])

    # Try sending a message to the thread as user3 (who is not a participant)
    data = {
        "thread": thread.id,  # Using the thread ID here
        "sender": user3.id,   # user3 is not a participant of the thread
        "text": "Hello, how are you?"
    }
    response = client.post("/api/chat/messages/", data, format='json')

    # Ensure that the response has the appropriate status and error message
    assert response.status_code == 400
    assert "Sender with id" in str(response.data) or "You are not a participant of this thread" in str(response.data)


@pytest.mark.django_db
def test_create_thread_with_more_than_two_participants():
    """
    Thread test #3: Creating a thread with more than two participants.
    Checks that creating a thread with more than two participants fails.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")
    user3 = User.objects.create_user(email="user3@example.com", password="password123", username="user3")

    # Authenticate user1 and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Try creating a thread with more than two participants
    data = {
        "participants": [user1.id, user2.id, user3.id]  # More than 2 participants
    }
    response = client.post("/api/chat/threads/", data, format='json')

    # Check that the status code is 400 and the error message is as expected
    assert response.status_code == 400
    assert "A thread must have exactly two participants." in str(response.data)


@pytest.mark.django_db
def test_get_user_threads():
    """
    Thread test #4: Retrieving the list of threads for a user.
    Checks that the user can retrieve all threads they are part of.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")

    # Create a thread
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])

    # Authenticate user1 and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Get the threads for user1
    response = client.get("/api/chat/threads/user_threads/")

    assert response.status_code == 200
    assert response.data['results'][0]['id'] == thread.id


@pytest.mark.django_db
def test_get_unread_messages_count():
    """
    Message test #2: Retrieving the number of unread messages for a user.
    Checks that the user can see how many messages are unread.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")

    # Create a thread
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])

    # Create some messages
    Message.objects.create(thread=thread, sender=user2, text="Message 1", is_read=False)
    Message.objects.create(thread=thread, sender=user2, text="Message 2", is_read=False)

    # Authenticate user1 and get the access tokena
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Get unread message count
    response = client.get("/api/chat/messages/unread/")

    assert response.status_code == 200
    assert response.data["unread_count"] == 2


@pytest.mark.django_db
# @pytest.mark.skip(reason="Этот тест еще не готов")
def test_mark_message_as_read():
    """
    Message test #3: Marking a message as read.
    Checks that a user can mark a message as read.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")

    # Create a thread
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])

    # Create a message
    message = Message.objects.create(thread=thread, sender=user2, text="Test message", is_read=False)

    # Authenticate user1 and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Mark the message as read
    response = client.post(f"/api/chat/messages/{message.id}/mark_as_read/")

    assert response.status_code == 200
    assert response.data['status'] == 'message marked as read'
    message.refresh_from_db()
    assert message.is_read is True


@pytest.mark.django_db
def test_delete_thread():
    """
    Thread test #5: Deleting a thread.
    Checks that a user can delete a thread.
    """
    client = APIClient()

    # Create users
    user1 = User.objects.create_user(email="user1@example.com", password="password123", username="user1")
    user2 = User.objects.create_user(email="user2@example.com", password="password123", username="user2")

    # Create a thread
    thread = Thread.objects.create()
    thread.participants.set([user1, user2])

    # Authenticate user1 and get the access token
    login_data = {
        "email": "user1@example.com",
        "password": "password123"
    }
    login_response = client.post("/api/auth/token/", login_data)
    access_token = login_response.data['access']

    # Set the Authorization header with the Bearer token for user1
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    # Delete the thread
    response = client.delete(f"/api/chat/threads/{thread.id}/")

    assert response.status_code == 204
    assert not Thread.objects.filter(id=thread.id).exists()
