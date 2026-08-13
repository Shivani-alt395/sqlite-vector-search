import hashlib
import math
import re

DIM = 64


def tokens(text):
    return [
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 1
    ]


def embed(text):
    vector = [0.0] * DIM

    for token in tokens(text):
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "big") % DIM

        if digest[4] % 2 == 0:
            vector[index] += 1
        else:
            vector[index] -= 1

    norm = math.sqrt(sum(value * value for value in vector))

    if norm == 0:
        return vector

    return [round(value / norm, 6) for value in vector]


def cosine(a, b):
    if not a or not b:
        return 0.0

    denominator = (
        math.sqrt(sum(value * value for value in a))
        * math.sqrt(sum(value * value for value in b))
    )

    if denominator == 0:
        return 0.0

    numerator = sum(x * y for x, y in zip(a, b))
    return numerator / denominator
