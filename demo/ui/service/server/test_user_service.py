import unittest
import sqlite3
import os
import bcrypt
from unittest.mock import patch

# Functions to be tested from user_service.py
# Assuming the test script is in the same directory as user_service.py for direct import,
# or that the python path is set up correctly for demo.ui.service.server.user_service
# For robust testing, we'll use the full path for patching.
from demo.ui.service.server.user_service import (
    create_user,
    get_user_by_username,
    verify_password,
    update_agent_settings,
    get_agent_settings
)

# The actual path used by user_service.py for its constant
USER_SERVICE_DB_FILE_PATH = 'demo.ui.service.server.user_service.DATABASE_FILE'

class TestUserService(unittest.TestCase):

    def setUp(self):
        """Set up a temporary test database and patch DATABASE_FILE."""
        self.test_db_file = 'test_users.db'
        
        # Patch the DATABASE_FILE constant in user_service.py
        self.patcher = patch(USER_SERVICE_DB_FILE_PATH, self.test_db_file)
        self.mock_db_file = self.patcher.start() # Start patching

        # Create the users table in the test database
        conn = None
        try:
            conn = sqlite3.connect(self.test_db_file)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    agent_settings TEXT
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            # self.fail(f"Failed to set up test database table: {e}") # Fail test if setup fails
            raise RuntimeError(f"Failed to set up test database table: {e}")
        finally:
            if conn:
                conn.close()

    def tearDown(self):
        """Stop the patcher and remove the test database file."""
        self.patcher.stop() # Stop patching
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)

    def test_create_user(self):
        """Test user creation with various scenarios."""
        # Successful creation with agent settings
        self.assertTrue(create_user("testuser1", "password123", '{"theme": "dark"}'))
        
        user = get_user_by_username("testuser1")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "testuser1")
        self.assertEqual(user["agent_settings"], '{"theme": "dark"}')
        
        # Verify password hash
        self.assertNotEqual(user["password_hash"], "password123")
        self.assertTrue(bcrypt.checkpw("password123".encode('utf-8'), user["password_hash"].encode('utf-8')))

        # Successful creation without agent settings (should default to None or be empty)
        self.assertTrue(create_user("testuser2", "password456"))
        user2 = get_user_by_username("testuser2")
        self.assertIsNotNone(user2)
        self.assertIsNone(user2["agent_settings"]) # Assuming it defaults to None if not provided

        # Test creating a user with an existing username
        self.assertFalse(create_user("testuser1", "anotherpassword"))

    def test_get_user_by_username(self):
        """Test retrieving users."""
        create_user("getuser", "password", '{"setting": "value"}')
        
        user = get_user_by_username("getuser")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "getuser")
        self.assertEqual(user["id"], 1) # Assuming it's the first user
        self.assertEqual(user["agent_settings"], '{"setting": "value"}')

        # Test retrieving a non-existent user
        non_existent_user = get_user_by_username("nouser")
        self.assertIsNone(non_existent_user)

    def test_verify_password(self):
        """Test password verification."""
        create_user("verifyuser", "correctpassword")
        
        # Correct password
        self.assertTrue(verify_password("verifyuser", "correctpassword"))
        # Incorrect password
        self.assertFalse(verify_password("verifyuser", "wrongpassword"))
        # Non-existent user
        self.assertFalse(verify_password("nouser", "anypassword"))

    def test_update_agent_settings(self):
        """Test updating agent settings."""
        create_user("updatesettingsuser", "password123", '{"initial": "true"}')
        
        # Successful update
        new_settings = '{"initial": "false", "new_key": "new_value"}'
        self.assertTrue(update_agent_settings("updatesettingsuser", new_settings))
        
        updated_user = get_user_by_username("updatesettingsuser")
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user["agent_settings"], new_settings)

        # Test updating settings for a non-existent user
        self.assertFalse(update_agent_settings("nouser", '{"theme": "light"}'))

    def test_get_agent_settings(self):
        """Test retrieving agent settings."""
        # User with settings
        create_user("userwithsettings", "password", '{"mode": "expert"}')
        settings = get_agent_settings("userwithsettings")
        self.assertEqual(settings, '{"mode": "expert"}')

        # User without settings (created with None or default)
        create_user("userwithoutsettings", "password") # agent_settings defaults to None
        settings_none = get_agent_settings("userwithoutsettings")
        self.assertIsNone(settings_none)
        
        # Non-existent user
        settings_nouser = get_agent_settings("nouser")
        self.assertIsNone(settings_nouser)

    def test_create_user_bcrypt_failure(self):
        """Test user creation when bcrypt fails."""
        with patch('bcrypt.hashpw', side_effect=Exception("Bcrypt error")):
            self.assertFalse(create_user("bcryptfailuser", "password"))

    def test_get_user_db_error(self):
        """Test get_user_by_username when a database error occurs."""
        # To simulate a DB error, we can try to query after the DB is closed or made inaccessible.
        # This is a bit tricky to do perfectly without more invasive mocking of sqlite3 itself.
        # For now, we'll rely on the other tests covering normal operation.
        # A more advanced test might involve patching 'sqlite3.connect' within the scope of get_user_by_username
        # to raise an error.
        
        # Example of how one might do this (more complex):
        create_user("dbuser", "password")
        with patch(f'{USER_SERVICE_DB_FILE_PATH.rsplit(".", 1)[0]}.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Simulated DB connection error")
            user = get_user_by_username("dbuser")
            self.assertIsNone(user) # Expect None due to the error handling in get_user_by_username

if __name__ == '__main__':
    unittest.main(verbosity=2)
