"""
Flaky tests based on external dependencies
Simulation of APIs, databases, file system, network
"""
import pytest
import time
import random
import os
from unittest.mock import patch


class MockExternalAPI:
    """Simulates unstable external API"""
    
    @staticmethod
    def get_user_data(user_id):
        """Simulates API call that may fail"""
        # 30% chance of network failure
        if random.random() < 0.3:
            raise ConnectionError("Network timeout")
        
        # Variable latency
        time.sleep(random.uniform(0.01, 0.05))
        
        return {"id": user_id, "name": f"User{user_id}", "active": True}
    
    @staticmethod
    def post_data(data):
        """Simulates POST that may fail"""
        # 25% chance of server error
        if random.random() < 0.25:
            raise Exception("Server Error 500")
        
        return {"status": "created", "id": random.randint(1000, 9999)}


class MockDatabase:
    """Simulates unstable database"""
    
    @staticmethod
    def connect():
        """Simulates connection that may fail"""
        # 20% chance of connection failure
        if random.random() < 0.2:
            raise ConnectionError("Database connection failed")
        
        time.sleep(random.uniform(0.01, 0.03))
        return True
    
    @staticmethod
    def query(sql):
        """Simulates query that may timeout"""
        # 15% chance of timeout
        if random.random() < 0.15:
            time.sleep(2)  # Simulate timeout
            raise TimeoutError("Query timeout")
        
        return [{"id": 1, "data": "test"}]


@pytest.mark.flaky
@pytest.mark.external
def test_external_api_user_fetch():
    """Test that depends on external API to fetch user"""
    try:
        user_data = MockExternalAPI.get_user_data(123)
        assert user_data["id"] == 123
        assert "name" in user_data
        assert user_data["active"] is True
    except ConnectionError:
        pytest.fail("API call failed due to network issues")


@pytest.mark.flaky
@pytest.mark.external
def test_external_api_post_data():
    """Test that sends data to external API"""
    payload = {"name": "Test User", "email": "test@example.com"}
    
    try:
        response = MockExternalAPI.post_data(payload)
        assert response["status"] == "created"
        assert "id" in response
    except Exception as e:
        pytest.fail(f"API POST failed: {e}")


@pytest.mark.flaky
@pytest.mark.external
def test_external_database_connection():
    """Test that depends on database connection"""
    try:
        connected = MockDatabase.connect()
        assert connected is True
    except ConnectionError:
        pytest.fail("Database connection failed")


@pytest.mark.flaky
@pytest.mark.external
def test_external_database_query():
    """Test that executes database query"""
    try:
        # First connect
        MockDatabase.connect()
        
        # Then execute query
        results = MockDatabase.query("SELECT * FROM users")
        assert len(results) > 0
        assert "id" in results[0]
        
    except (ConnectionError, TimeoutError) as e:
        pytest.fail(f"Database operation failed: {e}")


@pytest.mark.flaky
@pytest.mark.external
def test_external_file_system():
    """Test that depends on file system"""
    test_file = "/tmp/test_external_file.txt"
    
    try:
        # Simulate occasional I/O failure
        if random.random() < 0.2:
            raise OSError("Disk full")
        
        # Write file
        with open(test_file, 'w') as f:
            f.write("test data")
        
        # Read file
        with open(test_file, 'r') as f:
            content = f.read()
        
        assert content == "test data"
        
    except OSError:
        pytest.fail("File system operation failed")
    finally:
        # Clean up file
        if os.path.exists(test_file):
            os.remove(test_file)


@pytest.mark.flaky
@pytest.mark.external
def test_external_network_latency():
    """Test sensitive to network latency"""
    start_time = time.time()
    
    try:
        # Simulate network call with variable latency
        network_delay = random.uniform(0.01, 0.08)
        time.sleep(network_delay)
        
        # Simulate 10% network failure
        if random.random() < 0.1:
            raise ConnectionError("Network unreachable")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Fail if latency is too high
        assert total_time < 0.06, f"Network too slow: {total_time:.3f}s"
        
    except ConnectionError:
        pytest.fail("Network connection failed")


@pytest.mark.flaky
@pytest.mark.external
def test_external_environment_variable():
    """Test that depends on environment variable"""
    # Simulate variable that may not be defined
    api_key = os.environ.get("EXTERNAL_API_KEY")
    
    if not api_key:
        # Simulate 40% chance of variable not being defined
        if random.random() < 0.4:
            pytest.fail("EXTERNAL_API_KEY environment variable not set")
        else:
            # Temporarily define to simulate inconsistent environment
            os.environ["EXTERNAL_API_KEY"] = "temp_key_123"
            api_key = os.environ["EXTERNAL_API_KEY"]
    
    assert len(api_key) > 5
    assert api_key.startswith(("test_", "prod_", "temp_"))


@pytest.mark.flaky
@pytest.mark.external
def test_external_third_party_service():
    """Test that depends on third-party service"""
    def call_external_service():
        # Simulate call to external service
        service_status = random.choice([
            "available", "available", "available",  # 60% available
            "slow", "slow",                         # 40% slow
            "down"                                  # 20% down
        ])
        
        if service_status == "down":
            raise ConnectionError("Service unavailable")
        elif service_status == "slow":
            time.sleep(0.1)  # Simulate slowness
            return {"status": "ok", "delay": True}
        else:
            return {"status": "ok", "delay": False}
    
    try:
        response = call_external_service()
        assert response["status"] == "ok"
        
        # If there was a delay, it may fail in some cases
        if response.get("delay"):
            # 30% chance of failure when there is delay
            if random.random() < 0.3:
                pytest.fail("Service too slow")
        
    except ConnectionError:
        pytest.fail("External service is down")


@pytest.mark.flaky
@pytest.mark.external
def test_external_cache_dependency():
    """Test that depends on external cache"""
    cache_key = "test_key_123"
    
    # Simulate cache that may be inconsistent
    cache_available = random.random() > 0.2  # 80% available
    cache_hit = random.random() > 0.3 if cache_available else False  # 70% hit rate
    
    if not cache_available:
        pytest.fail("Cache service unavailable")
    
    if cache_hit:
        # Cache hit - data available
        cached_data = {"user_id": 123, "cached_at": time.time()}
        assert cached_data["user_id"] == 123
    else:
        # Cache miss - need to fetch data (may be slow)
        time.sleep(random.uniform(0.02, 0.06))
        fresh_data = {"user_id": 123, "fetched_at": time.time()}
        assert fresh_data["user_id"] == 123
