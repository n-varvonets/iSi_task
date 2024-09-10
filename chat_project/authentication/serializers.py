from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'password', 'username']

    def create(self, validated_data):
        User = get_user_model()
        username = validated_data.get('username', f"{validated_data.get('first_name', '')} {validated_data.get('last_name', '')}".strip())

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=username,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user
