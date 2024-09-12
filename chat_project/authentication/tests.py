import os

import pytest
from rest_framework.test import APIClient
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture(scope='function')
def load_test_data(db, django_db_setup):
    """
    Fixture to load test data from a JSON file before each test.
    It determines the absolute path to the 'db_dump.json' fixture file
    based on the current project's structure.
    """
    fixture_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fixtures', 'db_dump.json')

    # Check if the fixture file exists
    if not os.path.exists(fixture_path):
        print(f"File {fixture_path} not found!")
        raise FileNotFoundError(f"Fixture at {fixture_path} not found!")
    else:
        print(f"File {fixture_path} found, loading data...")

    call_command('loaddata', fixture_path)

@pytest.mark.django_db
def test_successful_registration():
    """
    Registration test #1: Successful registration of a new user.
    Checks that a new user can register and that JWT tokens (access, refresh) are returned.
    """
    client = APIClient()
    data = {
        "email": "uniqueuser@example.com",  # unique email
        "password": "complexpassword123",
        "username": "uniqueuser",  # unique username
        "first_name": "New",
        "last_name": "User"
    }

    response = client.post("/api/auth/register/", data)

    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert User.objects.filter(email="uniqueuser@example.com").exists()

@pytest.mark.django_db
def test_registration_with_existing_email(load_test_data):
    """
    Registration test #2: Registration with an already registered email.
    Checks that registration fails when using an existing email.
    """
    client = APIClient()
    data = {
        "email": "testlogin@example.com",  # Email that is already in the fixture
        "password": "password123",
        "username": "testlogin_unique1"
    }

    response = client.post("/api/auth/register/", data)
    assert response.status_code == 400
    assert "already taken" in str(response.data)

@pytest.mark.django_db
def test_successful_login(load_test_data):
    """
    Authentication test #1: Successful login with valid credentials.
    Checks that a user can log in and JWT tokens (access, refresh) are returned.
    """
    client = APIClient()
    data = {
        "email": "testlogin@example.com",  # User data from fixture
        "password": "password123"
    }

    response = client.post("/api/auth/token/", data)

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
