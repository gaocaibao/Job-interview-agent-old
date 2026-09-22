"""混合检索器：关键词（可用）+ 向量（配置 Embedding 后启用）+ 引用溯源。"""

import re

from app.knowledge.base import KnowledgeNode, SearchHit

_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HybridRetriever:
    def __init__(self, nodes: list[KnowledgeNode] | None = None):
        self._nodes: dict[str, KnowledgeNode] = {}
        for n in nodes or []:
            self.add(n)

    def add(self, node: KnowledgeNode) -> None:
        self._nodes[node.id] = node

    @property
    def size(self) -> int:
        return len(self._nodes)

    def keyword_search(
        self, query: str, industry: str | None = None, top_k: int = 5
    ) -> list[SearchHit]:
        q_tokens = set(tokenize(query))
        hits: list[SearchHit] = []
        for node in self._nodes.values():
            if industry and node.industry != industry:
                continue
            n_tokens = set(tokenize(node.searchable_text()))
            if not q_tokens or not n_tokens:
                continue
            overlap = q_tokens & n_tokens
            score = len(overlap) / len(q_tokens)
            if score > 0:
                hits.append(SearchHit(node=node, score=round(score, 4), matched_by="keyword"))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]

    async def search(
        self, query: str, industry: str | None = None, top_k: int = 5
    ) -> list[SearchHit]:
        """异步接口，保持与向量检索升级后的兼容。"""
        return self.keyword_search(query, industry, top_k)
