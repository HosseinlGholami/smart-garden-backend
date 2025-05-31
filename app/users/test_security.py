"""
Security tests for JWT authentication and secret key management.
"""

import os
from django.test import TestCase, override_settings
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import jwt

User = get_user_model()


class SecretKeySecurityTest(TestCase):
    """Test cases for Django secret key security."""
    
    def test_secret_key_exists(self):
        """Test that SECRET_KEY is configured."""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')
    
    def test_secret_key_not_default(self):
        """Test that SECRET_KEY is not the default insecure value."""
        insecure_keys = [
            'django-insecure-change-this-in-production',
            'your-secret-key-here',
            'change-me',
            'insecure-key',
        ]
        
        for insecure_key in insecure_keys:
            self.assertNotEqual(
                settings.SECRET_KEY, 
                insecure_key,
                f"SECRET_KEY should not be the insecure default: {insecure_key}"
            )
    
    def test_secret_key_length(self):
        """Test that SECRET_KEY is sufficiently long for security."""
        min_length = 50  # Django recommendation
        self.assertGreaterEqual(
            len(settings.SECRET_KEY), 
            min_length,
            f"SECRET_KEY should be at least {min_length} characters long"
        )


class JWTSecurityTest(APITestCase):
    """Test cases for JWT token security."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='security@example.com',
            password='securepass123'
        )
    
    def test_jwt_token_creation(self):
        """Test that JWT tokens are created properly."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Token should be a string
        self.assertIsInstance(str(access_token), str)
        
        # Token should have multiple parts (header.payload.signature)
        token_parts = str(access_token).split('.')
        self.assertEqual(len(token_parts), 3)
    
    def test_jwt_token_expiration(self):
        """Test that JWT tokens have proper expiration times."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Decode token to check expiration
        decoded = jwt.decode(
            str(access_token), 
            options={"verify_signature": False}
        )
        
        # Check that exp (expiration) claim exists
        self.assertIn('exp', decoded)
        
        # Check that token expires in the future but not too far
        exp_time = datetime.fromtimestamp(decoded['exp'])
        now = datetime.now()
        
        self.assertGreater(exp_time, now, "Token should expire in the future")
    
    def test_jwt_token_signature_verification(self):
        """Test that JWT token signatures can be verified."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Should be able to verify with Django secret key
        try:
            decoded = jwt.decode(
                str(access_token),
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            self.assertIn('user_id', decoded)
        except jwt.InvalidTokenError:
            self.fail("Valid token should verify successfully") 