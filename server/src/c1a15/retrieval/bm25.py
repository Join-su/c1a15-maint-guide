"""agent 패키지 메모리 BM25 색인(R3). 시작할 때 DB 이력에서 다시 만든다."""

import math
from collections import Counter

from c1a15.retrieval.tokens import tokenize


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs: dict[str, Counter] = {}
        self.lengths: dict[str, int] = {}
        self.df: Counter = Counter()

    def add(self, doc_id: str, text: str) -> None:
        if doc_id in self.docs:
            return
        terms = Counter(tokenize(text))
        self.docs[doc_id], self.lengths[doc_id] = terms, sum(terms.values())
        self.df.update(terms.keys())

    def rank(self, query: str, doc_ids: list[str]) -> list[str]:
        """주어진 문서 안에서 점수 순(같으면 문서 ID 순)."""
        q = tokenize(query)
        n = len(self.docs)
        avg = sum(self.lengths.values()) / n if n else 0.0
        scores = {}
        for d in doc_ids:
            tf, length, s = self.docs[d], self.lengths[d], 0.0
            for t in q:
                if t in tf:
                    idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                    s += idf * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * length / avg))
            scores[d] = s
        return sorted(doc_ids, key=lambda d: (-scores[d], d))
