# -*- coding: utf-8 -*-
"""
刷题控制器模块
负责刷题流程的控制，包括题目切换、答案验证、模式切换等
"""

import random
from typing import List, Optional, Callable, Any
from enum import Enum

from src.models.question import (
    Question, SingleChoiceQuestion, MultiChoiceQuestion,
    FillBlankQuestion, JudgeQuestion, ShortAnswerQuestion, CodingQuestion
)
from src.controllers.data_controller import DataController
from src.utils.code_runner import validate_test_cases, run_code_with_function


class PracticeMode(Enum):
    """
    练习模式枚举
    """
    SEQUENTIAL = "sequential"   # 顺序练习
    RANDOM = "random"           # 随机练习
    WRONG = "wrong"             # 错题练习
    FAVORITE = "favorite"       # 收藏练习


class QuizController:
    """
    刷题控制器类
    控制刷题的整体流程
    
    属性：
        data_controller: 数据控制器
        practice_mode: 当前练习模式
        current_index: 当前题目索引
        question_list: 当前练习的题目列表
        on_question_change: 题目变化回调函数
        start_time: 当前题目开始时间
    """
    
    def __init__(self, data_controller: DataController):
        """
        初始化刷题控制器
        
        参数：
            data_controller: 数据控制器实例
        """
        self.data_controller = data_controller
        self.practice_mode = PracticeMode.SEQUENTIAL
        self.current_index = 0
        self.question_list: List[Question] = []
        
        # 回调函数
        self.on_question_change: Optional[Callable[[Question], None]] = None
        
        # 答题计时
        self.start_time: float = 0.0
    
    def set_practice_mode(self, mode: PracticeMode):
        """
        设置练习模式
        
        参数：
            mode: 练习模式
        """
        self.practice_mode = mode
        self._prepare_question_list()
        self.current_index = 0
    
    def _prepare_question_list(self):
        """根据练习模式准备题目列表"""
        if self.practice_mode == PracticeMode.SEQUENTIAL:
            # 顺序练习：使用全部题目
            self.question_list = self.data_controller.current_questions.copy()
        
        elif self.practice_mode == PracticeMode.RANDOM:
            # 随机练习：打乱题目顺序
            self.question_list = self.data_controller.current_questions.copy()
            random.shuffle(self.question_list)
        
        elif self.practice_mode == PracticeMode.WRONG:
            # 错题练习：只包含错题
            self.question_list = self.data_controller.get_wrong_questions()
        
        elif self.practice_mode == PracticeMode.FAVORITE:
            # 收藏练习：只包含收藏的题目
            self.question_list = self.data_controller.get_favorite_questions()
    
    def start_practice(self) -> bool:
        """
        开始练习
        
        返回：
            bool: 是否成功开始（题库是否有题目）
        """
        self._prepare_question_list()
        self.current_index = 0
        
        if len(self.question_list) == 0:
            return False
        
        # 触发题目变化
        self._notify_question_change()
        return True
    
    def get_current_question(self) -> Optional[Question]:
        """
        获取当前题目
        
        返回：
            Question: 当前题目，如果没有则返回None
        """
        if 0 <= self.current_index < len(self.question_list):
            return self.question_list[self.current_index]
        return None
    
    def next_question(self) -> Optional[Question]:
        """
        切换到下一题
        
        返回：
            Question: 下一题，如果已是最后一题则返回None
        """
        if self.current_index < len(self.question_list) - 1:
            self.current_index += 1
            self._notify_question_change()
            return self.get_current_question()
        return None
    
    def prev_question(self) -> Optional[Question]:
        """
        切换到上一题
        
        返回：
            Question: 上一题，如果已是第一题则返回None
        """
        if self.current_index > 0:
            self.current_index -= 1
            self._notify_question_change()
            return self.get_current_question()
        return None
    
    def goto_question(self, index: int) -> Optional[Question]:
        """
        跳转到指定题目
        
        参数：
            index: 题目索引
            
        返回：
            Question: 指定的题目，如果索引无效则返回None
        """
        if 0 <= index < len(self.question_list):
            self.current_index = index
            self._notify_question_change()
            return self.get_current_question()
        return None
    
    def get_progress(self) -> tuple:
        """
        获取当前进度
        
        返回：
            tuple: (当前索引+1, 总题数)
        """
        return (self.current_index + 1, len(self.question_list))
    
    def _notify_question_change(self):
        """通知题目变化"""
        import time
        self.start_time = time.time()
        
        if self.on_question_change:
            question = self.get_current_question()
            if question:
                self.on_question_change(question)
    
    def check_answer(self, user_answer: Any) -> tuple:
        """
        检查答案
        
        参数：
            user_answer: 用户的答案
            
        返回：
            tuple: (是否正确, 正确答案, 解析)
        """
        import time
        time_spent = time.time() - self.start_time
        
        question = self.get_current_question()
        if not question:
            return (False, "", "")
        
        is_correct = False
        correct_answer = ""
        explanation = question.explanation
        
        # 根据题目类型检查答案
        if isinstance(question, SingleChoiceQuestion):
            is_correct = question.check_answer(user_answer)
            correct_answer = question.answer
        
        elif isinstance(question, MultiChoiceQuestion):
            is_correct = question.check_answer(user_answer)
            correct_answer = ", ".join(question.answer)
        
        elif isinstance(question, FillBlankQuestion):
            is_correct = question.check_answer(user_answer)
            correct_answer = " / ".join(question.answer)
        
        elif isinstance(question, JudgeQuestion):
            is_correct = question.check_answer(user_answer)
            correct_answer = "正确" if question.answer else "错误"
        
        elif isinstance(question, ShortAnswerQuestion):
            # 简答题不做严格判断，返回关键词匹配情况
            matched, total, keywords = question.check_keywords(user_answer)
            is_correct = matched >= total // 2  # 匹配一半以上关键词算对
            correct_answer = question.answer
            explanation = f"关键词匹配: {matched}/{total}\n参考答案: {question.answer}"
        
        elif isinstance(question, CodingQuestion):
            # 编程题通过测试用例验证
            is_correct, correct_answer = self._check_coding_answer(question, user_answer)
        
        # 记录答题结果
        self.data_controller.record_answer(
            question=question,
            is_correct=is_correct,
            user_answer=str(user_answer),
            time_spent=time_spent
        )
        
        return (is_correct, correct_answer, explanation)
    
    def _check_coding_answer(self, question: CodingQuestion, user_code: str) -> tuple:
        """
        检查编程题答案
        
        参数：
            question: 编程题对象
            user_code: 用户代码
            
        返回：
            tuple: (是否全部通过, 测试结果说明)
        """
        # 尝试从代码模板中提取函数名
        import re
        func_match = re.search(r"def\s+(\w+)", question.code_template)
        
        if func_match:
            func_name = func_match.group(1)
            all_passed, results = run_code_with_function(
                user_code, func_name, question.test_cases
            )
        else:
            all_passed, results = validate_test_cases(user_code, question.test_cases)
        
        # 生成测试结果说明
        result_lines = []
        for i, r in enumerate(results, 1):
            status = "✅ 通过" if r["passed"] else "❌ 失败"
            result_lines.append(f"测试用例 {i}: {status}")
            if not r["passed"]:
                result_lines.append(f"  输入: {r['input']}")
                result_lines.append(f"  期望输出: {r['expected_output']}")
                result_lines.append(f"  实际输出: {r['actual_output']}")
                if r["error"]:
                    result_lines.append(f"  错误: {r['error']}")
        
        return (all_passed, "\n".join(result_lines))
    
    def toggle_favorite(self) -> bool:
        """
        切换当前题目的收藏状态
        
        返回：
            bool: 切换后的收藏状态
        """
        question = self.get_current_question()
        if question:
            return self.data_controller.toggle_favorite(question.id)
        return False
    
    def is_current_favorite(self) -> bool:
        """
        检查当前题目是否已收藏
        
        返回：
            bool: 是否已收藏
        """
        question = self.get_current_question()
        if question:
            return self.data_controller.is_favorite(question.id)
        return False
