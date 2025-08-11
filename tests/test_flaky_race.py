"""
Flaky tests based on race conditions
Concurrency and timing issues
"""
import pytest
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor


# Shared state to demonstrate race conditions
shared_counter = {"value": 0}
shared_list = []
shared_flag = {"ready": False}


@pytest.mark.flaky
@pytest.mark.race
def test_race_counter_increment():
    """Classic race condition - counter increment"""
    shared_counter["value"] = 0
    
    def increment():
        for _ in range(10):
            current = shared_counter["value"]
            time.sleep(0.001)  # Simulates processing
            shared_counter["value"] = current + 1
    
    # Two threads incrementing simultaneously
    t1 = threading.Thread(target=increment)
    t2 = threading.Thread(target=increment)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    # We expect 20, but due to race condition it might be less
    assert shared_counter["value"] == 20


@pytest.mark.flaky
@pytest.mark.race
def test_race_list_append():
    """Race condition in list operations"""
    shared_list.clear()
    
    def add_items():
        for i in range(5):
            shared_list.append(i)
            time.sleep(0.001)
    
    # Multiple threads adding items
    threads = [threading.Thread(target=add_items) for _ in range(3)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # We expect 15 items, but order may vary
    assert len(shared_list) == 15
    assert sorted(shared_list) == sorted([0, 1, 2, 3, 4] * 3)


@pytest.mark.flaky
@pytest.mark.race
def test_race_flag_timing():
    """Race condition with synchronization flag"""
    shared_flag["ready"] = False
    
    def set_flag():
        time.sleep(random.uniform(0.01, 0.03))
        shared_flag["ready"] = True
    
    def check_flag():
        time.sleep(0.02)  # Critical timing
        return shared_flag["ready"]
    
    setter = threading.Thread(target=set_flag)
    setter.start()
    
    # May fail depending on timing
    result = check_flag()
    setter.join()
    
    assert result is True


@pytest.mark.flaky
@pytest.mark.race
def test_race_thread_pool():
    """Race condition using thread pool"""
    results = []
    
    def worker(task_id):
        # Simulates variable work
        time.sleep(random.uniform(0.001, 0.02))
        results.append(task_id)
        return task_id
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        for future in futures:
            future.result()
    
    # Order may vary due to concurrency
    assert len(results) == 10
    assert sorted(results) == list(range(10))


@pytest.mark.flaky
@pytest.mark.race
def test_race_file_write():
    """Simulated race condition in file writing"""
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    
    def write_data(data):
        time.sleep(random.uniform(0.001, 0.01))
        with open(temp_file.name, 'w') as f:
            f.write(data)
    
    def read_data():
        time.sleep(0.005)  # Critical timing
        try:
            with open(temp_file.name, 'r') as f:
                return f.read()
        except (FileNotFoundError, OSError):
            return ""
    
    # Thread that writes
    writer = threading.Thread(target=write_data, args=("test_data",))
    writer.start()
    
    # Tries to read before write completes
    content = read_data()
    writer.join()
    
    # Clean temporary file
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass
    
    assert content == "test_data"


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
        while len(consumed) < 5:
            if queue:
                item = queue.pop(0)
                consumed.append(item)
            time.sleep(0.001)
    
    prod_thread = threading.Thread(target=producer)
    cons_thread = threading.Thread(target=consumer)
    
    prod_thread.start()
    cons_thread.start()
    
    # Timeout to avoid deadlock
    prod_thread.join(timeout=1)
    cons_thread.join(timeout=1)
    
    assert len(consumed) == 5


@pytest.mark.flaky
@pytest.mark.race
def test_race_double_checked_locking():
    """Simulation of double-checked locking anti-pattern"""
    singleton = {"instance": None}
    
    def get_instance():
        if singleton["instance"] is None:
            time.sleep(0.001)  # Simulates initialization
            singleton["instance"] = "initialized"
        return singleton["instance"]
    
    # Multiple threads trying to get instance
    results = []
    
    def worker():
        instance = get_instance()
        results.append(instance)
    
    threads = [threading.Thread(target=worker) for _ in range(5)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All should have the same instance
    assert all(r == "initialized" for r in results)
    assert len(set(results)) == 1
