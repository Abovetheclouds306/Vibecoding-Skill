def normalize_percent(value):
    if type(value) is not int:
        raise TypeError("integer required")
    if value < 0 or value > 100:
        raise ValueError("outside 0..100")
    return value
