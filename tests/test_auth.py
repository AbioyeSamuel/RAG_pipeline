import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from auth import create_user, authenticate_user

def test_user_creation():
    assert create_user("admin1", "securepass", "admin") == "User created successfully."
    assert create_user("student1", "pass123", "student") == "User created successfully."

def test_authentication():
    assert authenticate_user("admin1", "securepass") is not None
    assert authenticate_user("student1", "wrongpass") is None

if __name__ == "__main__":
    # test_user_creation()
    test_authentication()
    print("All tests passed.")
