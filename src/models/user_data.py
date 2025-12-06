# -*- coding: utf-8 -*-
"""
用户数据模型模块
用于存储用户的答题进度、错题记录和学习统计数据
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class AnswerRecord:
    """
    单次答题记录
    
    属性说明：
        question_id: 题目ID
        is_correct: 是否答对
        user_answer: 用户的答案
        answer_time: 答题时间（ISO格式字符串）
        time_spent: 答题耗时（秒）
    """
    question_id: int              # 题目ID
    is_correct: bool              # 是否正确
    user_answer: str              # 用户答案（统一转为字符串存储）
    answer_time: str = ""         # 答题时间
    time_spent: float = 0.0       # 耗时（秒）
    
    def to_dict(self) -> dict:
        """
        转换为字典，用于JSON序列化
        
        返回：
            dict: 包含所有属性的字典
        """
        return {
            "question_id": self.question_id,
            "is_correct": self.is_correct,
            "user_answer": self.user_answer,
            "answer_time": self.answer_time,
            "time_spent": self.time_spent
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AnswerRecord":
        """
        从字典创建对象
        
        参数：
            data: 包含答题记录数据的字典
            
        返回：
            AnswerRecord: 答题记录对象
        """
        return cls(
            question_id=data.get("question_id", 0),
            is_correct=data.get("is_correct", False),
            user_answer=data.get("user_answer", ""),
            answer_time=data.get("answer_time", ""),
            time_spent=data.get("time_spent", 0.0)
        )


@dataclass
class WrongQuestion:
    """
    错题记录
    
    属性说明：
        question_id: 题目ID
        question_bank: 题库文件名（用于定位题目来源）
        wrong_count: 做错次数
        last_wrong_time: 最后一次做错的时间
        is_mastered: 是否已掌握（用户可标记）
    """
    question_id: int                # 题目ID
    question_bank: str = ""         # 题库名称
    wrong_count: int = 1            # 错误次数
    last_wrong_time: str = ""       # 最后错误时间
    is_mastered: bool = False       # 是否已掌握
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "question_id": self.question_id,
            "question_bank": self.question_bank,
            "wrong_count": self.wrong_count,
            "last_wrong_time": self.last_wrong_time,
            "is_mastered": self.is_mastered
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WrongQuestion":
        """从字典创建对象"""
        return cls(
            question_id=data.get("question_id", 0),
            question_bank=data.get("question_bank", ""),
            wrong_count=data.get("wrong_count", 1),
            last_wrong_time=data.get("last_wrong_time", ""),
            is_mastered=data.get("is_mastered", False)
        )


@dataclass
class Statistics:
    """
    学习统计数据
    
    属性说明：
        total_questions: 总答题数
        correct_count: 正确数
        wrong_count: 错误数
        total_time: 总学习时长（秒）
        daily_stats: 每日统计，格式 {"2024-01-01": {"correct": 10, "wrong": 5}}
        type_stats: 按题型统计，格式 {"single_choice": {"correct": 5, "wrong": 2}}
    """
    total_questions: int = 0                              # 总答题数
    correct_count: int = 0                                # 正确数
    wrong_count: int = 0                                  # 错误数
    total_time: float = 0.0                               # 总时长（秒）
    daily_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)  # 每日统计
    type_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)   # 题型统计
    
    @property
    def accuracy(self) -> float:
        """
        计算正确率
        
        返回：
            float: 正确率（0-100的百分比）
        """
        if self.total_questions == 0:
            return 0.0
        return (self.correct_count / self.total_questions) * 100
    
    @property
    def total_time_display(self) -> str:
        """
        获取格式化的学习时长显示
        
        返回：
            str: 格式化的时长字符串，如 "2小时30分钟"
        """
        hours = int(self.total_time // 3600)
        minutes = int((self.total_time % 3600) // 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟"
        elif minutes > 0:
            return f"{minutes}分钟"
        else:
            return f"{int(self.total_time)}秒"
    
    def update(self, is_correct: bool, question_type: str, time_spent: float):
        """
        更新统计数据
        
        参数：
            is_correct: 本次答题是否正确
            question_type: 题目类型
            time_spent: 答题耗时（秒）
        """
        # 更新总计
        self.total_questions += 1
        self.total_time += time_spent
        
        if is_correct:
            self.correct_count += 1
        else:
            self.wrong_count += 1
        
        # 更新每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = {"correct": 0, "wrong": 0}
        
        if is_correct:
            self.daily_stats[today]["correct"] += 1
        else:
            self.daily_stats[today]["wrong"] += 1
        
        # 更新题型统计
        if question_type not in self.type_stats:
            self.type_stats[question_type] = {"correct": 0, "wrong": 0}
        
        if is_correct:
            self.type_stats[question_type]["correct"] += 1
        else:
            self.type_stats[question_type]["wrong"] += 1
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "wrong_count": self.wrong_count,
            "total_time": self.total_time,
            "daily_stats": self.daily_stats,
            "type_stats": self.type_stats
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Statistics":
        """从字典创建对象"""
        return cls(
            total_questions=data.get("total_questions", 0),
            correct_count=data.get("correct_count", 0),
            wrong_count=data.get("wrong_count", 0),
            total_time=data.get("total_time", 0.0),
            daily_stats=data.get("daily_stats", {}),
            type_stats=data.get("type_stats", {})
        )


@dataclass
class UserProgress:
    """
    用户进度数据
    整合所有用户相关的数据
    
    属性说明：
        current_bank: 当前题库名称
        current_index: 当前题目索引
        answer_records: 答题记录列表
        wrong_questions: 错题列表
        favorites: 收藏的题目ID列表
        statistics: 学习统计
    """
    current_bank: str = ""                                        # 当前题库
    current_index: int = 0                                        # 当前索引
    answer_records: List[AnswerRecord] = field(default_factory=list)  # 答题记录
    wrong_questions: List[WrongQuestion] = field(default_factory=list)  # 错题本
    favorites: List[int] = field(default_factory=list)            # 收藏列表
    statistics: Statistics = field(default_factory=Statistics)    # 统计数据
    
    def add_answer_record(self, question_id: int, is_correct: bool, 
                         user_answer: str, question_type: str,
                         time_spent: float = 0.0):
        """
        添加答题记录
        
        参数：
            question_id: 题目ID
            is_correct: 是否正确
            user_answer: 用户答案
            question_type: 题目类型
            time_spent: 答题耗时
        """
        # 创建答题记录
        record = AnswerRecord(
            question_id=question_id,
            is_correct=is_correct,
            user_answer=str(user_answer),
            answer_time=datetime.now().isoformat(),
            time_spent=time_spent
        )
        self.answer_records.append(record)
        
        # 更新统计
        self.statistics.update(is_correct, question_type, time_spent)
        
        # 如果答错，添加到错题本
        if not is_correct:
            self.add_wrong_question(question_id, self.current_bank)
    
    def add_wrong_question(self, question_id: int, question_bank: str):
        """
        添加错题
        如果已存在则增加错误次数
        
        参数：
            question_id: 题目ID
            question_bank: 题库名称
        """
        # 查找是否已存在
        for wq in self.wrong_questions:
            if wq.question_id == question_id and wq.question_bank == question_bank:
                wq.wrong_count += 1
                wq.last_wrong_time = datetime.now().isoformat()
                wq.is_mastered = False  # 又做错了，取消已掌握标记
                return
        
        # 不存在则新建
        self.wrong_questions.append(WrongQuestion(
            question_id=question_id,
            question_bank=question_bank,
            wrong_count=1,
            last_wrong_time=datetime.now().isoformat()
        ))
    
    def toggle_favorite(self, question_id: int) -> bool:
        """
        切换收藏状态
        
        参数：
            question_id: 题目ID
            
        返回：
            bool: 切换后的收藏状态（True表示已收藏）
        """
        if question_id in self.favorites:
            self.favorites.remove(question_id)
            return False
        else:
            self.favorites.append(question_id)
            return True
    
    def is_favorite(self, question_id: int) -> bool:
        """
        检查是否已收藏
        
        参数：
            question_id: 题目ID
            
        返回：
            bool: 是否已收藏
        """
        return question_id in self.favorites
    
    def to_dict(self) -> dict:
        """转换为字典，用于JSON保存"""
        return {
            "current_bank": self.current_bank,
            "current_index": self.current_index,
            "answer_records": [r.to_dict() for r in self.answer_records],
            "wrong_questions": [w.to_dict() for w in self.wrong_questions],
            "favorites": self.favorites,
            "statistics": self.statistics.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProgress":
        """从字典创建对象"""
        progress = cls(
            current_bank=data.get("current_bank", ""),
            current_index=data.get("current_index", 0),
            favorites=data.get("favorites", [])
        )
        
        # 加载答题记录
        for record_data in data.get("answer_records", []):
            progress.answer_records.append(AnswerRecord.from_dict(record_data))
        
        # 加载错题本
        for wrong_data in data.get("wrong_questions", []):
            progress.wrong_questions.append(WrongQuestion.from_dict(wrong_data))
        
        # 加载统计数据
        if "statistics" in data:
            progress.statistics = Statistics.from_dict(data["statistics"])
        
        return progress
