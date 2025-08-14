"""
Flaky tests based on execution order dependencies
Tests that depend on state left by other tests
"""
import pytest
import os
import tempfile
import random
from pathlib import Path


# Global state shared between tests
global_state = {
    "initialized": False,
    "counter": 0,
    "data": None,
    "temp_file": None
}

@pytest.mark.flaky
@pytest.mark.order
def test_order_01_initialize():
    """Test that initializes global state - must run first"""
    global_state["initialized"] = True
    global_state["counter"] = 0
    global_state["data"] = {"users": [], "settings": {}}
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
    temp_file.write("initial_data")
    temp_file.close()
    global_state["temp_file"] = temp_file.name
    
    assert global_state["initialized"] is True


@pytest.mark.flaky
@pytest.mark.order
def test_order_02_use_state():
    """Test that depends on initialized state"""
    # Fails if test_order_01_initialize did not run first
    assert global_state["initialized"] is True
    assert global_state["data"] is not None
    
    # Modify state
    global_state["counter"] += 1
    global_state["data"]["users"].append("user1")
    
    assert global_state["counter"] == 1
    assert len(global_state["data"]["users"]) == 1


@pytest.mark.flaky
@pytest.mark.order
def test_order_03_modify_state():
    """Test that modifies existing state"""
    # Depends on previous tests
    assert global_state["counter"] == 1
    assert "user1" in global_state["data"]["users"]
    
    # Add more data
    global_state["counter"] += 1
    global_state["data"]["users"].append("user2")
    global_state["data"]["settings"]["theme"] = "dark"
    
    assert global_state["counter"] == 2


@pytest.mark.flaky
@pytest.mark.order
def test_order_04_verify_final_state():
    """Test that verifies final state"""
    # Depends on all previous tests
    assert global_state["counter"] == 2
    assert len(global_state["data"]["users"]) == 2
    assert global_state["data"]["settings"]["theme"] == "dark"
    
    # Clean up temporary file
    if global_state["temp_file"] and os.path.exists(global_state["temp_file"]):
        os.unlink(global_state["temp_file"])


@pytest.mark.flaky
@pytest.mark.order
def test_order_file_dependency_1():
    """Creates file that will be used by another test"""
    config_file = Path("test_config.txt")
    config_file.write_text("database_url=localhost:5432\napi_key=test123")
    assert config_file.exists()


@pytest.mark.flaky
@pytest.mark.order
def test_order_file_dependency_2():
    """Reads file created by previous test"""
    config_file = Path("test_config.txt")
    # Fails if file was not created by previous test
    content = config_file.read_text()
    assert "database_url" in content
    assert "api_key" in content
    
    # Modify file
    content += "\ndebug=true"
    config_file.write_text(content)


@pytest.mark.flaky
@pytest.mark.order
def test_order_file_dependency_3():
    """Verifies modifications to the file"""
    config_file = Path("test_config.txt")
    content = config_file.read_text()
    assert "debug=true" in content
    
    # Clean up file
    if config_file.exists():
        config_file.unlink()


# Database dependency simulation
database_state = {"tables": set(), "records": []}


@pytest.mark.flaky
@pytest.mark.order
def test_order_db_create_table():
    """Simulates table creation in database"""
    database_state["tables"].add("users")
    database_state["records"].clear()
    assert "users" in database_state["tables"]


@pytest.mark.flaky
@pytest.mark.order
def test_order_db_insert_data():
    """Simulates data insertion - depends on table existing"""
    # Fails if table was not created
    assert "users" in database_state["tables"]
    
    database_state["records"].append({"id": 1, "name": "John"})
    database_state["records"].append({"id": 2, "name": "Jane"})
    
    assert len(database_state["records"]) == 2


@pytest.mark.flaky
@pytest.mark.order
def test_order_db_query_data():
    """Simulates data query - depends on data being inserted"""
    # Fails if data was not inserted
    assert len(database_state["records"]) == 2
    
    # Search by ID
    john = next((r for r in database_state["records"] if r["id"] == 1), None)
    assert john is not None
    assert john["name"] == "John"


@pytest.mark.flaky
@pytest.mark.order
def test_order_db_update_data():
    """Simulates data update - depends on previous query"""
    # Modify existing record
    for record in database_state["records"]:
        if record["id"] == 1:
            record["name"] = "John Doe"
            break
    
    # Verify modification
    john = next((r for r in database_state["records"] if r["id"] == 1), None)
    assert john["name"] == "John Doe"


# Environment variable dependency
@pytest.mark.flaky
@pytest.mark.order
def test_order_env_setup():
    """Define environment variable for other tests"""
    os.environ["TEST_MODE"] = "integration"
    os.environ["API_BASE_URL"] = "http://test.example.com"
    assert os.environ.get("TEST_MODE") == "integration"


@pytest.mark.flaky
@pytest.mark.order
def test_order_env_usage():
    """Uses environment variables defined previously"""
    # Fails if variables were not defined
    test_mode = os.environ.get("TEST_MODE")
    api_url = os.environ.get("API_BASE_URL")
    
    assert test_mode == "integration"
    assert api_url == "http://test.example.com"
    
    # Clean up variables
    del os.environ["TEST_MODE"]
    del os.environ["API_BASE_URL"]
