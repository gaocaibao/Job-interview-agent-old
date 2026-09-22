"""知识层基础类型。"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(slots=True)
class KnowledgeNode:
    """知识网络节点：岗位-技能-知识点，携带引用来源。"""

    id: str
    industry: str
    position: str
    skill: str
    content: str
    source_ref: str = ""
    tags: list[str] = field(default_factory=list)

    def searchable_text(self) -> str:
        return " ".join([self.skill, self.content, *self.tags])


@dataclass(slots=True)
class SearchHit:
    node: KnowledgeNode
    score: float
    matched_by: str  # keyword / vector / hybrid


class Retriever(Protocol):
    async def search(
        self, query: str, industry: str | None = None, top_k: int = 5
    ) -> list[SearchHit]: ...
