"""Pydantic 数据模型：API 契约定义，前后端共享的类型基础。"""

from enum import StrEnum


class EducationLevel(StrEnum):
    """学历层级（对应分学历差异化策略）。"""

    JUNIOR_HIGH = "初中及以下"
    SENIOR_HIGH = "高中/中专"
    COLLEGE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士及以上"


class IndustryType(StrEnum):
    """宁夏重点产业 + 通用产业。"""

    NEW_ENERGY = "新能源"
    WINE = "葡萄酒"
    AGRICULTURE = "枸杞/滩羊及特色农业"
    COMPUTING = "算力与数据"
    TOURISM = "文旅"
    GENERAL = "通用"


class PositionType(StrEnum):
    """岗位类型（题库/面试维度）。"""

    TECHNICAL = "技术类"
    SALES = "销售/市场类"
    OPERATION = "运营类"
    SERVICE = "服务类"
    MANUFACTURING = "生产/工程类"
    GENERAL = "通用"
