"""fixture 모드의 결정적 가짜 임베딩(EP-C1-LLM-001 · EP-C1-RET-001 시험용).

live 임베딩은 승인 뒤 LLM Adapter가 맡는다.
"""

import hashlib
import math

from c1a15.db.models import EMBEDDING_DIM

FAKE_MODEL = "fake-hash-bigram-v1"


def fake_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """공백 · 기호를 뺀 글자 2-gram을 hash로 차원에 더하고 길이 1로 맞춘다. 같은 글은 항상 같은 벡터."""
    chars = [c for c in text if not c.isspace()]
    vec = [0.0] * dim
    for a, b in zip(chars, chars[1:], strict=False):
        digest = hashlib.blake2b((a + b).encode(), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[index] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec
