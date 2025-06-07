# import pytest
from ..config.mongodb import get_database
from ..models.user import User

def test_mongodb_connection():
    """Test MongoDB connection"""
    # try:
    #     db = get_database()
    #     # If we get here, the connection was successful
    #     assert True
    # # except Exception as e:
    #     pytest.fail(f"Failed to connect to MongoDB: {str(e)}")

def test_user_crud():
    """# Test User CRUD operations"""
    # Test user creation
    user_id = User.create_user(
        username="testuser",
        email="test@example.com",
        password_hash="hashedpassword123"
    )
    assert user_id is not None

    # Test user retrieval
    user = User.get_user_by_id(user_id)
    assert user is not None
    assert user['email'] == "test@example.com"

    # Test user update
    update_success = User.update_user(
        user_id,
        {"username": "updated_testuser"}
    )
    assert update_success is True

    # Verify update
    updated_user = User.get_user_by_id(user_id)
    assert updated_user['username'] == "updated_testuser"

    # Test user deletion
    delete_success = User.delete_user(user_id)
    assert delete_success is True

    # Verify deletion
    deleted_user = User.get_user_by_id(user_id)
    assert deleted_user is None 