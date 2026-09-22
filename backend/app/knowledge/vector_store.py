"""内存向量库：开发期零依赖实现，预留 Qdrant/pgvector 升级路径。"""

import math
from dataclasses import dataclass


@dataclass(slots=True)
class _Entry:
    doc_id: str
    vector: list[float]
    payload: dict


class InMemoryVectorStore:
    """纯 Python 余弦相似度检索（千级规模足够）。"""

    def __init__(self) -> None:
        self._entries: list[_Entry] = []

    def add(self, doc_id: str, vector: list[float], payload: dict) -> None:
        self._entries = [e for e in self._entries if e.doc_id != doc_id]
        self._entries.append(_Entry(doc_id=doc_id, vector=vector, payload=payload))

    def search(self, vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict]]:
        scored = [(e.doc_id, self._cosine(vector, e.vector), e.payload) for e in self._entries]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._entries)

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
