import os
import requests
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from nd.redis_client import RedisClient

User = get_user_model()


class SSOAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the user based on the SSO token provided in the Authorization header.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None  # No authentication credentials provided

        token = auth_header.split("Bearer ")[1].strip()
        if not token:
            return None

        # Try retrieving user data from Redis cache first
        redis_client = RedisClient()
        cache_key = f"sso_token_{token}"
        user_data = redis_client.get_dict(cache_key)

        if not user_data:
            # Verify the token with the SSO server
            sso_verify_url = f'{os.environ.get("SSO_URL")}/api/users/me/'
            response = requests.get(
                sso_verify_url, headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise AuthenticationFailed("SSO token is invalid or expired.")
            user_data = response.json()

        # Get or update the user information
        try:
            user = User.objects.get(username=user_data["preferred_username"])
            update_fields = []

            first_name = user_data["name"].split(" ")[0]
            if user.first_name != first_name:
                user.first_name = first_name
                update_fields.append("first_name")

            last_name = user_data["name"].split(" ")[1]
            if user.last_name != last_name:
                user.last_name = last_name
                update_fields.append("last_name")

            if user.access_level != user_data["access_level"]:
                user.access_level = user_data["access_level"]
                update_fields.append("access_level")

            if update_fields:
                user.save(update_fields=update_fields)

        except User.DoesNotExist:
            try:
                user = User.objects.create(
                    username=user_data["preferred_username"],
                    email=user_data["email"],
                    first_name=user_data["name"].split(" ")[0],
                    last_name=user_data["name"].split(" ")[1],
                    access_level=user_data["access_level"],
                )
            except Exception:
                raise AuthenticationFailed("Error creating user.")

        return (user, None)

    def authenticate_header(self, request):
        return "Bearer"
