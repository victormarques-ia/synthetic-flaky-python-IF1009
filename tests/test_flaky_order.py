"""
Flaky tests based on state pollution between test executions
Tests fail when global state gets polluted by previous test runs
"""
import pytest
import os
import random
from pathlib import Path


# This state persists within the same process across test runs
# ISOLATION (--forked): Each test runs in new process → state always clean
# RETRIES (--reruns): Same process reused → pollution accumulates
global_pollution = {
    "leaked_connections": [],
    "stale_cache": {},
    "error_count": 0,
    "temp_files": [],
    "env_vars_set": [],
    "run_count": 0
}

def pollute_state():
    """Simulates state pollution that accumulates over test runs"""
    global_pollution["run_count"] += 1
    global_pollution["leaked_connections"].append(f"conn_{global_pollution['run_count']}")
    global_pollution["stale_cache"][f"key_{global_pollution['run_count']}"] = "stale_value"
    global_pollution["error_count"] += 1
    global_pollution["temp_files"].append(f"/tmp/leaked_{global_pollution['run_count']}.tmp")
    
    # Set environment variable that persists in same process
    env_var = f"LEAKED_VAR_{global_pollution['run_count']}"
    os.environ[env_var] = "polluted"
    global_pollution["env_vars_set"].append(env_var)

@pytest.mark.flaky
@pytest.mark.order
def test_clean_application_start():
    """
    Test expects clean application state.
    ISOLATION: Always clean (new process) → ~100% success
    RETRIES: Pollution accumulates → low success rate
    """
    
    # This test ALWAYS pollutes state at the end, simulating cleanup failure
    pollute_state()
    
    # Test fails if there's ANY pollution from previous runs
    assert len(global_pollution["leaked_connections"]) <= 1, f"Found leaked connections: {global_pollution['leaked_connections']}"
    assert len(global_pollution["stale_cache"]) <= 1, f"Found stale cache: {global_pollution['stale_cache']}"
    assert global_pollution["error_count"] <= 1, f"Error count too high: {global_pollution['error_count']}"


@pytest.mark.flaky
@pytest.mark.order
def test_database_connection_pool():
    
    # Always add pollution
    pollute_state()
    
    # Fail if too many leaked connections (indicates pollution from previous runs)
    assert len(global_pollution["leaked_connections"]) <= 1, f"Connection pool polluted: {global_pollution['leaked_connections']}"


@pytest.mark.flaky  
@pytest.mark.order
def test_cache_invalidation():
    
    # Always add pollution
    pollute_state()
    
    # Fail if cache has accumulated too many stale entries
    assert len(global_pollution["stale_cache"]) <= 1, f"Cache polluted: {global_pollution['stale_cache']}"


@pytest.mark.flaky
@pytest.mark.order
def test_error_counter_reset():
    
    # Always add pollution
    pollute_state()
    
    # Fail if error count is too high (indicates accumulation from previous runs)
    assert global_pollution["error_count"] <= 1, f"Error count too high: {global_pollution['error_count']}"


@pytest.mark.flaky
@pytest.mark.order  
def test_temp_file_cleanup():
    
    # Always add pollution
    pollute_state()
    
    # Fail if too many temp files (indicates cleanup failure from previous runs)
    assert len(global_pollution["temp_files"]) <= 1, f"Temp files not cleaned: {global_pollution['temp_files']}"


@pytest.mark.flaky
@pytest.mark.order
def test_environment_variables():

    # Always add pollution  
    pollute_state()
    
    # Fail if too many leaked environment variables
    assert len(global_pollution["env_vars_set"]) <= 1, f"Environment polluted: {global_pollution['env_vars_set']}"


@pytest.mark.flaky
@pytest.mark.order
def test_process_state_isolation():

    # Always add pollution
    pollute_state()
    
    # Fail if this is not the first or second run in the same process
    # (indicates we're in a retry scenario with accumulated state)
    assert global_pollution["run_count"] <= 1, f"Process has been reused too many times: {global_pollution['run_count']}"


@pytest.mark.flaky
@pytest.mark.order
def test_configuration_pollution():

    # Always add pollution
    pollute_state()
    
    # Check for environment variable pollution 
    leaked_vars = [var for var in os.environ.keys() if var.startswith("LEAKED_VAR_")]
    assert len(leaked_vars) <= 1, f"Found leaked environment variables: {leaked_vars}"


@pytest.mark.flaky
@pytest.mark.order  
def test_memory_state_accumulation():
    
    # Always add pollution
    pollute_state()
    
    # Calculate total pollution level
    total_pollution = (
        len(global_pollution["leaked_connections"]) +
        len(global_pollution["stale_cache"]) + 
        global_pollution["error_count"] +
        len(global_pollution["temp_files"])
    )
    
    # Fail if total pollution is too high (indicates accumulation)
    assert total_pollution <= 4, f"Total pollution level too high: {total_pollution}"