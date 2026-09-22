"""知识库摄入流水线：原始资料 → 知识节点。

P0 版本：人工/半自动产出的结构化 JSON 直接入库。
P1 版本：接入大模型辅助提炼（政策文件/企业资料 → 知识点卡片）。
"""

import json
from pathlib import Path

from app.knowledge.base import KnowledgeNode
from app.knowledge.retriever import HybridRetriever


def load_nodes_from_json(path: str | Path) -> list[KnowledgeNode]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [KnowledgeNode(**item) for item in data]


def build_retriever(nodes: list[KnowledgeNode]) -> HybridRetriever:
    return HybridRetriever(nodes)


async def extract_nodes_with_llm(
    raw_text: str, industry: str, source_ref: str, llm_router
) -> list[KnowledgeNode]:
    """用大模型从原始资料提炼知识节点（需已配置 LLM）。"""
    from app.services.llm.base import ChatMessage

    result = await llm_router.chat(
        [
            ChatMessage(
                role="system",
                content=(
                    "你是知识工程师。从给定资料中提炼'岗位-技能-知识点'三元组，"
                    "输出 JSON 数组，每项含 skill（技能点）、content（知识点说明，80字内）、"
                    "tags（关键词列表）。只输出 JSON。"
                ),
            ),
            ChatMessage(role="user", content=raw_text[:8000]),
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(result.content)
    items = data if isinstance(data, list) else data.get("nodes", [])
    return [
        KnowledgeNode(
            id=f"{industry}-{i}",
            industry=industry,
            position="",
            skill=item.get("skill", ""),
            content=item.get("content", ""),
            source_ref=source_ref,
            tags=item.get("tags", []),
        )
        for i, item in enumerate(items)
    ]
