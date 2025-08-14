"""
Flaky tests based on timeout and timing issues - CORRECTED VERSION
Tests are now tuned to be less aggressive and more realistic.
"""
import pytest
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_variable_processing():
    """Test with variable processing time and a more realistic limit."""
    # Simulate processing that may be slow
    processing_time = random.uniform(0.02, 0.08) # Range ajustado
    time.sleep(processing_time)
    
    # Fails if it takes too long (limit is now more lenient)
    assert processing_time < 0.06, f"Processing took too long: {processing_time:.3f}s"

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_deadline_sensitive():
    """Test with a strict but more achievable deadline."""
    start_time = time.time()
    
    # Simulate variable CPU-intensive work
    iterations = random.randint(2000, 12000) # Range ajustado
    total = 0
    for i in range(iterations):
        total += i ** 0.5
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Fails if deadline is exceeded (limit slightly increased)
    assert duration < 0.04, f"Processing took too long: {duration:.3f}s"

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_async_operation():
    """Test with an asynchronous operation where the wait time is realistic."""
    result = {"completed": False, "data": None}
    
    def async_task():
        # Task can take up to 0.06s
        delay = random.uniform(0.02, 0.06)
        time.sleep(delay)
        result["completed"] = True
        result["data"] = "processed"
    
    thread = threading.Thread(target=async_task)
    thread.start()
    
    # Wait for a time that is longer than the max task delay
    # The flakiness will come from system load, not from a guaranteed timeout.
    thread.join(timeout=0.1) 
    
    assert result["completed"] is True
    assert result["data"] == "processed"

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_thread_pool():
    """Test using thread pool with a more forgiving timeout."""
    def slow_task(task_id):
        # Some tasks are slower (up to 0.05s)
        if task_id % 4 == 0:
            time.sleep(0.05)
        else:
            time.sleep(0.01)
        return task_id * 2
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(slow_task, i) for i in range(6)]
        
        results = []
        for future in futures:
            try:
                # Timeout is now more lenient than the slowest task
                result = future.result(timeout=0.1)
                results.append(result)
            except FutureTimeoutError:
                pytest.fail(f"Task timed out unexpectedly. System might be under heavy load.")
    
    assert len(results) == 6

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_network_simulation():
    """Simulates network operation where timeout is a real possibility but not guaranteed."""
    def simulate_network_call():
        # Latency can go up to 0.08s
        network_delay = random.choice([0.01, 0.02, 0.03, 0.04, 0.08]) # 20% chance of being slow
        time.sleep(network_delay)
        
        # We define a "timeout" in our business logic at 0.06s
        if network_delay > 0.06:
            raise TimeoutError("Network timeout")
        
        return {"status": "success", "latency": network_delay}
    
    try:
        response = simulate_network_call()
        assert response["status"] == "success"
    except TimeoutError:
        pytest.fail("Network call timed out as designed for flaky tests.")

# --- O restante dos testes segue a mesma lógica de ajuste ---
# Os limites de tempo foram revisados para serem desafiadores, mas não impossíveis,
# garantindo que a instabilidade venha de variações de performance e não de um design que força a falha.

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_retry_mechanism():
    """Test that implements retry with a more balanced timeout."""
    max_attempts = 3
    timeout_per_attempt = 0.05 # Aumentado
    
    for attempt in range(max_attempts):
        start_time = time.time()
        try:
            operation_time = random.uniform(0.01, 0.06)
            time.sleep(operation_time)
            
            if random.random() > 0.4: # 60% chance of success
                return # Success
            else:
                raise ValueError("Operation failed")
        except ValueError:
            if time.time() - start_time > timeout_per_attempt:
                pytest.fail(f"Attempt {attempt + 1} timed out")
            if attempt == max_attempts - 1:
                pytest.fail("All retry attempts failed")

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_batch_processing():
    """Test of batch processing with a more realistic time limit."""
    batch_size = random.randint(20, 40)
    items_processed = 0
    start_time = time.time()
    max_processing_time = 0.1 # Aumentado

    for i in range(batch_size):
        time.sleep(random.uniform(0.001, 0.003))
        items_processed += 1
        if time.time() - start_time > max_processing_time:
            break
            
    min_items = int(batch_size * 0.7)
    assert items_processed >= min_items, f"Only processed {items_processed}/{batch_size} items"

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_database_query():
    """Simulates database query with a more realistic timeout."""
    def execute_query(complexity):
        query_time = complexity * random.uniform(0.005, 0.01)
        time.sleep(query_time)
        if query_time > 0.05: # Limite ajustado
            raise TimeoutError("Query timeout")
        return {"rows": complexity * 10, "time": query_time}

    try:
        complexity = random.randint(1, 8)
        result = execute_query(complexity)
        assert result["time"] < 0.05
    except TimeoutError:
        pytest.fail("Database query timed out")

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_file_operations():
    """Test of file operations with a more lenient timeout."""
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        start_time = time.time()
        data_size = random.randint(500, 1500)
        data = "x" * data_size
        
        for chunk in [data[i:i+100] for i in range(0, len(data), 100)]:
            temp_file.write(chunk.encode())
            time.sleep(0.002) # Simulate slightly slower I/O
        temp_file.close()
        
        write_time = time.time() - start_time
        assert write_time < 0.08, f"File write too slow: {write_time:.3f}s" # Limite ajustado
        
        with open(temp_file.name, 'r') as f:
            assert len(f.read()) == data_size
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

@pytest.mark.flaky
@pytest.mark.timeout
def test_timeout_memory_allocation():
    """Test that simulates memory allocation with a more realistic timeout."""
    start_time = time.time()
    data_structures = []
    target_size = random.randint(2000, 6000)
    
    for i in range(target_size):
        if i % 100 == 0:
            time.sleep(0.001)
        data_structures.append([j for j in range(10)])
        if time.time() - start_time > 0.06: # Limite ajustado
            break
            
    min_structures = int(target_size * 0.8)
    assert len(data_structures) >= min_structures
