import sqlite3
import bcrypt # Note: If bcrypt is not available, this script will fail. 
              # Production environments should handle this dependency.

DATABASE_FILE = 'users.db'

def create_user(username, password, agent_settings=None):
    """Creates a new user with a hashed password."""
    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, agent_settings) VALUES (?, ?, ?)",
                (username, password_hash, agent_settings)
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    except Exception as e:
        print(f"An error occurred in create_user: {e}")
        return False

def get_user_by_username(username):
    """Retrieves a user by their username."""
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, agent_settings FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            if user_row:
                # Return as a dictionary for easier access to columns
                return {
                    "id": user_row[0],
                    "username": user_row[1],
                    "password_hash": user_row[2],
                    "agent_settings": user_row[3]
                }
            return None
    except Exception as e:
        print(f"An error occurred in get_user_by_username: {e}")
        return None

def verify_password(username, password):
    """Verifies a user's password."""
    user = get_user_by_username(username)
    if user and user.get("password_hash"):
        stored_password_hash = user["password_hash"].encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), stored_password_hash)
    return False

def update_agent_settings(username, agent_settings):
    """Updates the agent_settings for a given username."""
    try:
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET agent_settings = ? WHERE username = ?",
                (agent_settings, username)
            )
            conn.commit()
            return cursor.rowcount > 0 # Returns True if a row was updated
    except Exception as e:
        print(f"An error occurred in update_agent_settings: {e}")
        return False

def get_agent_settings(username):
    """Retrieves the agent_settings for a given username."""
    user = get_user_by_username(username)
    if user:
        return user.get("agent_settings")
    return None

if __name__ == '__main__':
    # Basic testing (requires database_setup.py to be run first)
    # 1. Ensure database_setup.py has been run to create users.db and the users table.
    print("Running basic tests for user_service.py...")

    # Test create_user
    print("\nTesting user creation...")
    if create_user("testuser1", "password123", '{"theme": "dark"}'):
        print("User 'testuser1' created successfully.")
    else:
        print("Failed to create 'testuser1' (might already exist).")

    if create_user("testuser2", "securepass", '{"notifications": "on"}'):
        print("User 'testuser2' created successfully.")
    else:
        print("Failed to create 'testuser2' (might already exist).")
    
    # Test duplicate user creation
    print("\nTesting duplicate user creation...")
    if not create_user("testuser1", "newpassword"):
        print("Correctly prevented duplicate username 'testuser1'.")
    else:
        print("Error: Allowed duplicate username 'testuser1'.")

    # Test get_user_by_username
    print("\nTesting user retrieval...")
    user1 = get_user_by_username("testuser1")
    if user1:
        print(f"Retrieved user 'testuser1': {user1['username']}, Settings: {user1['agent_settings']}")
    else:
        print("Failed to retrieve 'testuser1'.")

    non_existent_user = get_user_by_username("nouser")
    if non_existent_user is None:
        print("Correctly returned None for non-existent user 'nouser'.")
    else:
        print("Error: Retrieved data for non-existent user 'nouser'.")

    # Test password verification
    print("\nTesting password verification...")
    if verify_password("testuser1", "password123"):
        print("Password for 'testuser1' verified successfully.")
    else:
        print("Password verification failed for 'testuser1' (correct password).")

    if not verify_password("testuser1", "wrongpassword"):
        print("Correctly failed password verification for 'testuser1' (wrong password).")
    else:
        print("Error: Verified incorrect password for 'testuser1'.")

    if not verify_password("nouser", "anypassword"):
        print("Correctly failed password verification for non-existent user 'nouser'.")
    else:
        print("Error: Verified password for non-existent user 'nouser'.")
        
    # Test update_agent_settings
    print("\nTesting agent settings update...")
    if update_agent_settings("testuser1", '{"theme": "light", "language": "en"}'):
        print("Agent settings for 'testuser1' updated successfully.")
        updated_user1 = get_user_by_username("testuser1")
        print(f"Updated settings for 'testuser1': {updated_user1['agent_settings']}")
    else:
        print("Failed to update agent settings for 'testuser1'.")

    if not update_agent_settings("nouser", '{"mode": "expert"}'):
        print("Correctly failed to update settings for non-existent user 'nouser'.")
    else:
        print("Error: Updated settings for non-existent user 'nouser'.")

    # Test get_agent_settings
    print("\nTesting agent settings retrieval...")
    settings1 = get_agent_settings("testuser1")
    if settings1:
        print(f"Retrieved agent settings for 'testuser1': {settings1}")
    else:
        print("Failed to retrieve agent settings for 'testuser1'.")

    settings_nouser = get_agent_settings("nouser")
    if settings_nouser is None:
        print("Correctly returned None for agent settings of non-existent user 'nouser'.")
    else:
        print("Error: Retrieved agent settings for non-existent user 'nouser'.")

    print("\nBasic tests completed.")
    print("Remember to run demo/ui/service/server/database_setup.py first if the database is not yet created.")
    print("Also, ensure bcrypt is installed (`pip install bcrypt`).")
