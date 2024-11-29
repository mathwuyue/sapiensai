import random

def random_int(min_val: int, max_val: int) -> int:
    """Generate a random integer between min_val and max_val."""
    return random.randint(min_val, max_val)

def random_float(min_val: float, max_val: float) -> float:
    """Generate a random float between min_val and max_val."""
    return round(random.uniform(min_val, max_val), 1)
