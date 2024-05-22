import numpy as np
from typing import List

def serialize(vector: List[float]) -> bytes:
    return np.asarray(vector).astype(np.float32).tobytes()
