# Helper function to extract and compare UUIDs safely
import uuid
from unittest.mock import patch


def compare_uuids(response_data, model_data, key):
    """Safely converts response string UUIDs to UUID objects for comparison."""
    response_uuid = uuid.UUID(response_data[key])
    assert response_uuid == getattr(model_data, key)


def create_safe_patch(crud_class, method_name):
    """
    Creates a patch object for a specified CRUD method, ensuring it's called
    with commit=False to prevent persistence during tests.
    """

    # Capture the original method reference (e.g., PartCRUD.create)
    original_method = getattr(crud_class, method_name)

    # Define the safe mock function
    def mock_safe(*args, **kwargs):
        kwargs["commit"] = False
        # Call the captured original method to avoid infinite recursion
        return original_method(*args, **kwargs)

    # Construct the full path string for the patch target
    path = f"{crud_class.__module__}.{crud_class.__name__}.{method_name}"

    # Return the unstarted patch object
    return patch(path, new=mock_safe)
