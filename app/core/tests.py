"""
Tests for core Django functionality including migrations and setup.
"""

from django.test import TestCase
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
import io
import sys


class DatabaseMigrationTest(TestCase):
    """Test cases for database migrations and setup."""
    
    def test_migrations_complete(self):
        """Test that all migrations have been applied."""
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        # If there are pending migrations, the plan will not be empty
        self.assertEqual(
            len(plan), 0, 
            f"There are {len(plan)} pending migrations: {[migration.name for migration in plan]}"
        )
    
    def test_database_tables_exist(self):
        """Test that all expected database tables exist."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
        
        # Check for essential Django tables
        # Note: We use custom user model, so auth_user doesn't exist
        expected_tables = [
            'users_user',  # Our custom user table instead of auth_user
            'django_migrations',
            'django_content_type',
            'auth_group',  # Django auth groups still exist
            'auth_permission',  # Django permissions still exist
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Expected table '{table}' not found in database")
    
    def test_custom_models_tables_exist(self):
        """Test that custom app model tables exist."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
        
        # Check for our custom app tables
        expected_custom_tables = [
            'users_user',
            'garden_garden',
            'garden_valve',
            'garden_schedule',
            'garden_systemlog',
        ]
        
        for table in expected_custom_tables:
            self.assertIn(table, tables, f"Custom table '{table}' not found in database")
    
    def test_makemigrations_no_changes(self):
        """Test that makemigrations finds no pending changes."""
        # Capture output
        out = io.StringIO()
        try:
            call_command('makemigrations', '--dry-run', '--check', stdout=out)
            output = out.getvalue()
            # If there are no changes, the command should succeed
            self.assertIn('No changes detected', output)
        except SystemExit as e:
            # makemigrations exits with code 1 if changes are detected
            if e.code == 1:
                self.fail("There are pending model changes that need migrations")
    
    def test_migrate_command_runs(self):
        """Test that migrate command runs without errors."""
        # This should complete without errors
        try:
            call_command('migrate', verbosity=0)
        except Exception as e:
            self.fail(f"Migration command failed: {e}")


class DatabaseIndexTest(TestCase):
    """Test cases for database indexes and performance."""
    
    def test_user_email_index(self):
        """Test that user email field has proper indexing."""
        with connection.cursor() as cursor:
            cursor.execute("SHOW INDEX FROM users_user WHERE Column_name = 'email'")
            indexes = cursor.fetchall()
            self.assertTrue(len(indexes) > 0, "Email field should have an index")
    
    def test_garden_indexes(self):
        """Test that garden models have proper indexing."""
        with connection.cursor() as cursor:
            # Check valve garden_id foreign key index
            cursor.execute("SHOW INDEX FROM garden_valve WHERE Column_name = 'garden_id'")
            indexes = cursor.fetchall()
            self.assertTrue(len(indexes) > 0, "Valve garden_id should have an index")


class DatabaseConstraintTest(TestCase):
    """Test cases for database constraints and validations."""
    
    def test_user_email_unique_constraint(self):
        """Test that user email has unique constraint."""
        from django.contrib.auth import get_user_model
        from django.db import IntegrityError
        
        User = get_user_model()
        
        # Create first user
        User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Try to create second user with same email
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                password='testpass456'
            )
    
    def test_garden_valve_unique_constraint(self):
        """Test that garden-valve number combination is unique."""
        from garden.models import Garden, Valve
        from django.db import IntegrityError
        
        garden = Garden.objects.create(name="Test Garden")
        
        # Create first valve
        Valve.objects.create(garden=garden, number=1, status='off')
        
        # Try to create second valve with same number in same garden
        with self.assertRaises(IntegrityError):
            Valve.objects.create(garden=garden, number=1, status='off') 