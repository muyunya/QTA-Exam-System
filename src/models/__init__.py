# -*- coding: utf-8 -*-
"""
数据模型包
包含题目模型和用户数据模型
"""

# 从子模块导出主要类，方便外部直接导入
from .question import (
    Question,
    SingleChoiceQuestion,
    MultiChoiceQuestion,
    FillBlankQuestion,
    JudgeQuestion,
    ShortAnswerQuestion,
    CodingQuestion,
    create_question_from_dict
)

from .user_data import UserProgress, Statistics
