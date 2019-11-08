import numpy as np

def binary_deserializer(data: str, dtype=np.float32):
    return np.fromstring(data, dtype=dtype)