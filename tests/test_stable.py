"""
Stable tests - always pass
Serve as baseline for comparison
"""
import pytest
import time
import math


@pytest.mark.stable
def test_stable_arithmetic():
    """Basic arithmetic test"""
    assert 2 + 2 == 4
    assert 10 * 5 == 50


@pytest.mark.stable
def test_stable_string_operations():
    """Deterministic string operations"""
    text = "hello world"
    assert text.upper() == "HELLO WORLD"
    assert len(text) == 11


@pytest.mark.stable
def test_stable_list_operations():
    """Deterministic list operations"""
    numbers = [1, 2, 3, 4, 5]
    assert sum(numbers) == 15
    assert len(numbers) == 5
    assert max(numbers) == 5


@pytest.mark.stable
def test_stable_dict_operations():
    """Deterministic dictionary operations"""
    data = {"a": 1, "b": 2, "c": 3}
    assert len(data) == 3
    assert data["a"] == 1
    assert "b" in data


@pytest.mark.stable
def test_stable_math_operations():
    """Deterministic math operations"""
    assert math.sqrt(16) == 4.0
    assert math.pow(2, 3) == 8.0
    assert abs(-5) == 5


@pytest.mark.stable
def test_stable_boolean_logic():
    """Deterministic boolean logic"""
    assert True and True
    assert not (False and True)
    assert True or False


@pytest.mark.stable
def test_stable_type_checking():
    """Deterministic type checking"""
    assert isinstance(42, int)
    assert isinstance("hello", str)
    assert isinstance([1, 2, 3], list)


@pytest.mark.stable
def test_stable_range_operations():
    """Deterministic range operations"""
    result = list(range(5))
    assert result == [0, 1, 2, 3, 4]
    assert len(result) == 5


@pytest.mark.stable
def test_stable_set_operations():
    """Deterministic set operations"""
    set1 = {1, 2, 3}
    set2 = {3, 4, 5}
    intersection = set1 & set2
    assert intersection == {3}


@pytest.mark.stable
def test_stable_string_formatting():
    """Deterministic string formatting"""
    name = "Python"
    version = 3.10
    result = f"Language: {name} {version}"
    assert result == "Language: Python 3.1"


@pytest.mark.stable
def test_stable_list_comprehension():
    """Deterministic list comprehension"""
    squares = [x**2 for x in range(5)]
    assert squares == [0, 1, 4, 9, 16]


@pytest.mark.stable
def test_stable_exception_handling():
    """Deterministic exception handling"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0


@pytest.mark.stable
def test_stable_file_path_operations():
    """Deterministic path operations"""
    from pathlib import Path
    path = Path("test/file.txt")
    assert path.suffix == ".txt"
    assert path.stem == "file"


@pytest.mark.stable
def test_stable_datetime_parsing():
    """Deterministic datetime parsing"""
    from datetime import datetime
    dt = datetime(2025, 1, 1, 12, 0, 0)
    assert dt.year == 2025
    assert dt.month == 1


@pytest.mark.stable
def test_stable_json_operations():
    """Deterministic JSON operations"""
    import json
    data = {"key": "value", "number": 42}
    json_str = json.dumps(data, sort_keys=True)
    parsed = json.loads(json_str)
    assert parsed["key"] == "value"
    assert parsed["number"] == 42
