"""
Flaky tests based on race conditions - CORRECTED VERSION
Each test now uses a fixture to ensure state isolation.
"""
import pytest
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor

# ### FIXTURES TO PROVIDE ISOLATED STATE ###

@pytest.fixture
def shared_counter():
    """Provides a clean counter dictionary for each test."""
    return {"value": 0}

@pytest.fixture
def shared_list():
    """Provides a clean list for each test."""
    return []

@pytest.fixture
def shared_flag():
    """Provides a clean flag dictionary for each test."""
    return {"ready": False}

# ### REFACTORED TESTS ###

@pytest.mark.flaky
@pytest.mark.race
def test_race_counter_increment(shared_counter): # Fixture is passed as an argument
    """Classic race condition - counter increment"""
    # No need to reset the counter, the fixture handles it.
    
    def increment():
        for _ in range(10):
            current = shared_counter["value"]
            time.sleep(0.001)
            shared_counter["value"] = current + 1
    
    t1 = threading.Thread(target=increment)
    t2 = threading.Thread(target=increment)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # This assertion will still be flaky (the goal), but the test is now independent.
    assert shared_counter["value"] == 20


@pytest.mark.flaky
@pytest.mark.race
def test_race_list_append(shared_list): # Fixture is passed as an argument
    """Race condition in list operations"""
    # No need for shared_list.clear()
    
    def add_items():
        for i in range(5):
            # Although list.append is thread-safe in CPython, the sleep
            # can still create interleaving, which is what we want to test.
            shared_list.append(i)
            time.sleep(0.001)
    
    threads = [threading.Thread(target=add_items) for _ in range(3)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert len(shared_list) == 15
    assert sorted(shared_list) == sorted([0, 1, 2, 3, 4] * 3)


@pytest.mark.flaky
@pytest.mark.race
def test_race_flag_timing(shared_flag): # Fixture is passed as an argument
    """Race condition with synchronization flag"""
    # No need to reset the flag
    
    def set_flag():
        time.sleep(random.uniform(0.01, 0.03))
        shared_flag["ready"] = True
    
    def check_flag():
        time.sleep(0.02)
        return shared_flag["ready"]
    
    setter = threading.Thread(target=set_flag)
    setter.start()
    
    result = check_flag()
    setter.join()
    
    assert result is True

# Note: This test was already safe as it used a local variable 'results'.
# No changes were needed, but it's good practice to be explicit.
@pytest.mark.flaky
@pytest.mark.race
def test_race_thread_pool():
    """Race condition using thread pool"""
    results = []
    
    def worker(task_id):
        time.sleep(random.uniform(0.001, 0.02))
        results.append(task_id)
        return task_id
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        for future in futures:
            future.result()
            
    assert len(results) == 10
    assert sorted(results) == list(range(10))

@pytest.mark.flaky
@pytest.mark.race
def test_race_file_write():
    """Simulated race condition in file writing"""
    import tempfile
    import os
    
    # tempfile is created and cleaned up within the test, so it's already isolated.
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    try:
        def write_data(data):
            time.sleep(random.uniform(0.001, 0.01))
            with open(temp_file.name, 'w') as f:
                f.write(data)
        
        def read_data():
            time.sleep(0.005)
            try:
                with open(temp_file.name, 'r') as f:
                    return f.read()
            except (FileNotFoundError, OSError):
                return ""

        writer = threading.Thread(target=write_data, args=("test_data",))
        writer.start()
        
        content = read_data()
        writer.join()
        
        assert content == "test_data"
    finally:
        # Ensure cleanup
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass

# Note: This test was also safe because it used local variables.
@pytest.mark.flaky
@pytest.mark.race
def test_race_producer_consumer():
    """Standard producer-consumer race condition"""
    queue = []
    consumed = []
    
    def producer():
        for i in range(5):
            time.sleep(0.001)
            queue.append(i)
    
    def consumer():
        consumed_count = 0
        while consumed_count < 5:
            if queue:
                item = queue.pop(0)
                consumed.append(item)
                consumed_count += 1
            time.sleep(0.001)

    prod_thread = threading.Thread(target=producer)
    cons_thread = threading.Thread(target=consumer)
    
    prod_thread.start()
    cons_thread.start()
    
    prod_thread.join(timeout=1)
    cons_thread.join(timeout=1)
    
    assert len(consumed) == 5

# This test also used a local variable, so it was safe.
@pytest.mark.flaky
@pytest.mark.race
def test_race_double_checked_locking():
    """Simulation of double-checked locking anti-pattern"""
    singleton = {"instance": None}
    
    def get_instance():
        if singleton["instance"] is None:
            time.sleep(0.001)
            singleton["instance"] = "initialized"
        return singleton["instance"]
        
    results = []
    def worker():
        instance = get_instance()
        results.append(instance)
    
    threads = [threading.Thread(target=worker) for _ in range(5)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert all(r == "initialized" for r in results)
    # This assertion is tricky. A race condition could create multiple instances.
    # To make it flaky, we check if more than one unique object was created.
    # However, with string instances, this is less obvious.
    # The main point is the test is now isolated.
