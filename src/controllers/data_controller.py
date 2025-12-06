# -*- coding: utf-8 -*-
"""
数据控制器模块
负责管理题库数据和用户进度数据
"""

from typing import List, Dict, Any, Optional
from src.models.question import Question, create_question_from_dict
from src.models.user_data import UserProgress, Statistics
from src.utils.file_handler import (
    load_question_bank,
    save_user_progress,
    load_user_progress,
    get_question_banks,
    save_settings,
    load_settings
)


class DataController:
    """
    数据控制器类
    管理题库加载、用户进度保存等数据操作
    
    属性：
        settings: 应用设置字典
        user_progress: 用户进度对象
        question_banks: 已加载的题库列表
        current_questions: 当前题库的题目列表
        current_bank_meta: 当前题库的元信息
    """
    
    def __init__(self):
        """初始化数据控制器"""
        # 加载应用设置
        self.settings = load_settings()
        
        # 加载用户进度
        self.user_progress = load_user_progress()
        
        # 题库相关
        self.question_banks: List[Dict[str, Any]] = []  # 可用题库列表
        self.current_questions: List[Question] = []      # 当前题目列表
        self.current_bank_meta: Dict[str, Any] = {}      # 当前题库元信息
        
        # 刷新题库列表
        self.refresh_question_banks()
    
    def refresh_question_banks(self):
        """刷新可用题库列表"""
        self.question_banks = get_question_banks()
    
    def load_bank(self, file_path: str) -> bool:
        """
        加载指定题库
        
        参数：
            file_path: 题库文件路径
            
        返回：
            bool: 是否加载成功
        """
        try:
            questions, meta = load_question_bank(file_path)
            self.current_questions = questions
            self.current_bank_meta = meta
            
            # 更新用户进度中的当前题库
            self.user_progress.current_bank = file_path
            
            return True
        except Exception as e:
            print(f"加载题库失败: {e}")
            return False
    
    def get_question(self, index: int) -> Optional[Question]:
        """
        获取指定索引的题目
        
        参数：
            index: 题目索引
            
        返回：
            Question: 题目对象，如果索引无效则返回None
        """
        if 0 <= index < len(self.current_questions):
            return self.current_questions[index]
        return None
    
    def get_total_questions(self) -> int:
        """
        获取当前题库的题目总数
        
        返回：
            int: 题目总数
        """
        return len(self.current_questions)
    
    def get_questions_by_type(self, q_type: str) -> List[Question]:
        """
        获取指定类型的题目
        
        参数：
            q_type: 题目类型
            
        返回：
            List[Question]: 符合条件的题目列表
        """
        return [q for q in self.current_questions if q.type == q_type]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Question]:
        """
        获取指定难度的题目
        
        参数：
            difficulty: 难度等级
            
        返回：
            List[Question]: 符合条件的题目列表
        """
        return [q for q in self.current_questions if q.difficulty == difficulty]
    
    def get_wrong_questions(self) -> List[Question]:
        """
        获取错题列表中对应的题目
        
        返回：
            List[Question]: 错题对应的题目列表
        """
        wrong_ids = [wq.question_id for wq in self.user_progress.wrong_questions
                     if wq.question_bank == self.user_progress.current_bank
                     and not wq.is_mastered]
        return [q for q in self.current_questions if q.id in wrong_ids]
    
    def get_favorite_questions(self) -> List[Question]:
        """
        获取收藏的题目
        
        返回：
            List[Question]: 收藏的题目列表
        """
        return [q for q in self.current_questions 
                if q.id in self.user_progress.favorites]
    
    def save_progress(self):
        """保存用户进度"""
        save_user_progress(self.user_progress)
    
    def record_answer(self, question: Question, is_correct: bool, 
                     user_answer: str, time_spent: float = 0.0):
        """
        记录答题结果
        
        参数：
            question: 题目对象
            is_correct: 是否正确
            user_answer: 用户答案
            time_spent: 答题耗时
        """
        self.user_progress.add_answer_record(
            question_id=question.id,
            is_correct=is_correct,
            user_answer=user_answer,
            question_type=question.type,
            time_spent=time_spent
        )
        
        # 自动保存
        if self.settings.get("auto_save", True):
            self.save_progress()
    
    def toggle_favorite(self, question_id: int) -> bool:
        """
        切换收藏状态
        
        参数：
            question_id: 题目ID
            
        返回：
            bool: 切换后的收藏状态
        """
        result = self.user_progress.toggle_favorite(question_id)
        
        # 自动保存
        if self.settings.get("auto_save", True):
            self.save_progress()
        
        return result
    
    def is_favorite(self, question_id: int) -> bool:
        """
        检查是否已收藏
        
        参数：
            question_id: 题目ID
            
        返回：
            bool: 是否已收藏
        """
        return self.user_progress.is_favorite(question_id)
    
    def get_statistics(self) -> Statistics:
        """
        获取学习统计数据
        
        返回：
            Statistics: 统计对象
        """
        return self.user_progress.statistics
    
    def update_setting(self, key: str, value: Any):
        """
        更新设置
        
        参数：
            key: 设置键名
            value: 设置值
        """
        self.settings[key] = value
        save_settings(self.settings)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        获取设置值
        
        参数：
            key: 设置键名
            default: 默认值
            
        返回：
            Any: 设置值
        """
        return self.settings.get(key, default)
