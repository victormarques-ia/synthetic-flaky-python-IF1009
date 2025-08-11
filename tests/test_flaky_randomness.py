"""
Flaky tests based on randomness
Different failure probabilities to demonstrate variation
"""
import pytest
import random
import time
import hashlib


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_coin_flip():
    """Test that fails ~50% of the time - like coin flip"""
    assert random.random() > 0.5


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_low_probability():
    """Test that fails ~80% of the time - high instability"""
    assert random.random() > 0.8


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_high_probability():
    """Test that fails ~20% of the time - low instability"""
    assert random.random() > 0.2


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_dice_roll():
    """Dice-based test - fails if not rolling 6"""
    dice = random.randint(1, 6)
    assert dice == 6


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_list_choice():
    """Test based on random list choice"""
    options = ["fail", "fail", "fail", "pass"]
    choice = random.choice(options)
    assert choice == "pass"


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_hash_collision():
    """Test based on hash that may collide"""
    data = str(random.randint(1, 100))
    hash_val = int(hashlib.md5(data.encode()).hexdigest()[:2], 16)
    # Fails if hash ends in multiple of 3
    assert hash_val % 3 != 0


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_gaussian():
    """Test based on Gaussian distribution"""
    value = random.gauss(0, 1)  # mean 0, std 1
    # Fails if value is outside 1 standard deviation
    assert abs(value) < 1.0


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_seed_dependent():
    """Test that depends on current seed"""
    # Uses timestamp as randomness source
    current_ms = int(time.time() * 1000)
    value = current_ms % 10
    assert value < 3  # 30% chance to pass


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_multiple_conditions():
    """Test with multiple random conditions"""
    condition1 = random.random() > 0.3
    condition2 = random.randint(1, 10) <= 7
    condition3 = random.choice([True, False, False])
    
    # Needs at least 2 of 3 conditions to be true
    assert sum([condition1, condition2, condition3]) >= 2


@pytest.mark.flaky
@pytest.mark.randomness
def test_random_shuffled_list():
    """Test based on shuffled list order"""
    items = [1, 2, 3, 4, 5]
    random.shuffle(items)
    # Fails if first element is not less than 3
    assert items[0] < 3
