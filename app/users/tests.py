"""
Comprehensive tests for the users app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

from .models import User, UserManager
from .serializers import CustomUserCreateSerializer, CustomUserSerializer

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for custom User model."""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'staff'
        }
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertEqual(user.role, self.user_data['role'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )
        
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.role, 'admin')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_create_user_without_email(self):
        """Test that creating user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123'
            )
    
    def test_user_string_representation(self):
        """Test user string representation."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_user_email_normalization(self):
        """Test that email is normalized."""
        email = 'TEST@EXAMPLE.COM'
        user = User.objects.create_user(
            email=email,
            password='testpass123'
        )
        self.assertEqual(user.email, email.lower())
    
    def test_user_role_properties(self):
        """Test user role property methods."""
        # Test admin user
        admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(admin_user.is_manager)
        self.assertFalse(admin_user.is_staff_user)
        
        # Test manager user
        manager_user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            role='manager'
        )
        self.assertFalse(manager_user.is_admin)
        self.assertTrue(manager_user.is_manager)
        self.assertFalse(manager_user.is_staff_user)
        
        # Test staff user
        staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            role='staff'
        )
        self.assertFalse(staff_user.is_admin)
        self.assertFalse(staff_user.is_manager)
        self.assertTrue(staff_user.is_staff_user)
    
    def test_create_superuser_with_invalid_flags(self):
        """Test that creating superuser with invalid flags raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
        
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )


class UserManagerTest(TestCase):
    """Test cases for custom UserManager."""
    
    def test_create_user_default_role(self):
        """Test that default role is 'staff' for regular users."""
        user = User.objects.create_user(
            email='default@example.com',
            password='testpass123'
        )
        self.assertEqual(user.role, 'staff')
    
    def test_create_superuser_default_role(self):
        """Test that default role is 'admin' for superusers."""
        superuser = User.objects.create_superuser(
            email='super@example.com',
            password='superpass123'
        )
        self.assertEqual(superuser.role, 'admin')


class UserSerializerTest(TestCase):
    """Test cases for user serializers."""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'staff'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_serialization(self):
        """Test user serialization."""
        serializer = CustomUserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], self.user_data['email'])
        self.assertEqual(data['first_name'], self.user_data['first_name'])
        self.assertEqual(data['last_name'], self.user_data['last_name'])
        self.assertEqual(data['role'], self.user_data['role'])
        # Password should not be included in serialized data
        self.assertNotIn('password', data)
    
    def test_user_create_serialization(self):
        """Test user creation serialization."""
        create_data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            're_password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        serializer = CustomUserCreateSerializer(data=create_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.email, create_data['email'])
        self.assertEqual(user.first_name, create_data['first_name'])
        self.assertTrue(user.check_password(create_data['password']))
    
    def test_user_create_password_mismatch(self):
        """Test user creation with password mismatch."""
        create_data = {
            'email': 'mismatch@example.com',
            'password': 'password123',
            're_password': 'different123',
            'first_name': 'Mismatch',
            'last_name': 'User'
        }
        
        serializer = CustomUserCreateSerializer(data=create_data)
        self.assertFalse(serializer.is_valid())
    
    def test_user_create_duplicate_email(self):
        """Test user creation with duplicate email."""
        create_data = {
            'email': self.user_data['email'],  # Same as existing user
            'password': 'newpass123',
            're_password': 'newpass123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        
        serializer = CustomUserCreateSerializer(data=create_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class AuthenticationTest(TestCase):
    """Test cases for authentication functionality."""
    
    def setUp(self):
        self.user_data = {
            'email': 'auth@example.com',
            'password': 'authpass123',
            'first_name': 'Auth',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_authenticate_with_email(self):
        """Test authentication using email."""
        user = authenticate(
            username=self.user_data['email'],  # Django uses 'username' field
            password=self.user_data['password']
        )
        self.assertEqual(user, self.user)
    
    def test_authenticate_with_wrong_password(self):
        """Test authentication with wrong password."""
        user = authenticate(
            username=self.user_data['email'],
            password='wrongpassword'
        )
        self.assertIsNone(user)
    
    def test_authenticate_with_nonexistent_email(self):
        """Test authentication with nonexistent email."""
        user = authenticate(
            username='nonexistent@example.com',
            password='anypassword'
        )
        self.assertIsNone(user)


class JWTAuthenticationAPITest(APITestCase):
    """Test cases for JWT authentication API."""
    
    def setUp(self):
        self.user_data = {
            'email': 'jwt@example.com',
            'password': 'jwtpass123',
            'first_name': 'JWT',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_jwt_token_creation(self):
        """Test JWT token creation (login)."""
        url = reverse('jwt-create')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_jwt_token_creation_invalid_credentials(self):
        """Test JWT token creation with invalid credentials."""
        url = reverse('jwt-create')
        login_data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh."""
        # First get tokens
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('jwt-refresh')
        refresh_data = {'refresh': str(refresh)}
        
        response = self.client.post(url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    def test_jwt_token_verify(self):
        """Test JWT token verification."""
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        url = reverse('jwt-verify')
        verify_data = {'token': str(access_token)}
        
        response = self.client.post(url, verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_jwt_token_verify_invalid(self):
        """Test JWT token verification with invalid token."""
        url = reverse('jwt-verify')
        verify_data = {'token': 'invalid.token.here'}
        
        response = self.client.post(url, verify_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserRegistrationAPITest(APITestCase):
    """Test cases for user registration API."""
    
    def test_user_registration(self):
        """Test user registration via API."""
        url = reverse('user-list')
        registration_data = {
            'email': 'register@example.com',
            'password': 'registerpass123',
            're_password': 'registerpass123',
            'first_name': 'Register',
            'last_name': 'User'
        }
        
        response = self.client.post(url, registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify user was created
        user = User.objects.get(email=registration_data['email'])
        self.assertEqual(user.first_name, registration_data['first_name'])
        self.assertEqual(user.role, 'staff')  # Default role
    
    def test_user_registration_password_mismatch(self):
        """Test user registration with password mismatch."""
        url = reverse('user-list')
        registration_data = {
            'email': 'mismatch@example.com',
            'password': 'password123',
            're_password': 'different123',
            'first_name': 'Mismatch',
            'last_name': 'User'
        }
        
        response = self.client.post(url, registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_email(self):
        """Test user registration with existing email."""
        # Create existing user
        User.objects.create_user(
            email='existing@example.com',
            password='existingpass123'
        )
        
        url = reverse('user-list')
        registration_data = {
            'email': 'existing@example.com',
            'password': 'newpass123',
            're_password': 'newpass123',
            'first_name': 'Duplicate',
            'last_name': 'User'
        }
        
        response = self.client.post(url, registration_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserProfileAPITest(APITestCase):
    """Test cases for user profile API."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='profilepass123',
            first_name='Profile',
            last_name='User',
            role='manager'
        )
        
        # Set up JWT authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_get_current_user(self):
        """Test getting current authenticated user."""
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['role'], self.user.role)
    
    def test_update_user_profile(self):
        """Test updating user profile."""
        url = reverse('user-me')
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, update_data['first_name'])
        self.assertEqual(self.user.last_name, update_data['last_name'])
    
    def test_get_user_profile_unauthenticated(self):
        """Test getting user profile without authentication."""
        self.client.credentials()  # Remove authentication
        
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordManagementTest(APITestCase):
    """Test cases for password management."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='password@example.com',
            password='oldpass123',
            first_name='Password',
            last_name='User'
        )
        
        # Set up JWT authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_change_password(self):
        """Test changing user password."""
        url = reverse('user-set-password')
        password_data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            're_new_password': 'newpass123'
        }
        
        response = self.client.post(url, password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertFalse(self.user.check_password('oldpass123'))
    
    def test_change_password_wrong_current(self):
        """Test changing password with wrong current password."""
        url = reverse('user-set-password')
        password_data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123',
            're_new_password': 'newpass123'
        }
        
        response = self.client.post(url, password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatch(self):
        """Test changing password with password mismatch."""
        url = reverse('user-set-password')
        password_data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            're_new_password': 'different123'
        }
        
        response = self.client.post(url, password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRolePermissionTest(APITestCase):
    """Test cases for user role-based permissions."""
    
    def setUp(self):
        # Create users with different roles
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        self.manager_user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            role='manager'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            role='staff'
        )
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
    
    def test_admin_role_properties(self):
        """Test admin role properties."""
        self.assertTrue(self.admin_user.is_admin)
        self.assertFalse(self.admin_user.is_manager)
        self.assertFalse(self.admin_user.is_staff_user)
    
    def test_manager_role_properties(self):
        """Test manager role properties."""
        self.assertFalse(self.manager_user.is_admin)
        self.assertTrue(self.manager_user.is_manager)
        self.assertFalse(self.manager_user.is_staff_user)
    
    def test_staff_role_properties(self):
        """Test staff role properties."""
        self.assertFalse(self.staff_user.is_admin)
        self.assertFalse(self.staff_user.is_manager)
        self.assertTrue(self.staff_user.is_staff_user)
    
    def test_role_cannot_be_changed_by_regular_user(self):
        """Test that regular users cannot change their role."""
        self._authenticate_user(self.staff_user)
        
        url = reverse('user-me')
        update_data = {'role': 'admin'}
        
        response = self.client.patch(url, update_data, format='json')
        
        # Role change should be ignored or forbidden
        self.staff_user.refresh_from_db()
        self.assertEqual(self.staff_user.role, 'staff')


class UserActivationTest(TestCase):
    """Test cases for user activation."""
    
    def test_user_active_by_default(self):
        """Test that users are active by default."""
        user = User.objects.create_user(
            email='active@example.com',
            password='activepass123'
        )
        self.assertTrue(user.is_active)
    
    def test_inactive_user_cannot_authenticate(self):
        """Test that inactive users cannot authenticate."""
        user = User.objects.create_user(
            email='inactive@example.com',
            password='inactivepass123'
        )
        user.is_active = False
        user.save()
        
        authenticated_user = authenticate(
            username='inactive@example.com',
            password='inactivepass123'
        )
        self.assertIsNone(authenticated_user)


class EmailValidationTest(TestCase):
    """Test cases for email validation."""
    
    def test_valid_email_formats(self):
        """Test various valid email formats."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.com',
            'user+tag@domain.co.uk',
            'firstname.lastname@domain.org'
        ]
        
        for email in valid_emails:
            user = User.objects.create_user(
                email=email,
                password='testpass123'
            )
            self.assertEqual(user.email, email.lower())
    
    def test_email_case_insensitive(self):
        """Test that email comparison is case insensitive."""
        User.objects.create_user(
            email='Test@Example.Com',
            password='testpass123'
        )
        
        # Should not be able to create another user with same email in different case
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                password='testpass123'
            )
