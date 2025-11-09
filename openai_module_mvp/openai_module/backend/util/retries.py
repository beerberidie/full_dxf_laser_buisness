import random
def backoff(attempt: int, base: float=0.2, cap: float=8.0) -> float:
    return min(cap, base * (2 ** attempt)) + random.random() * 0.1
