# -*- coding: utf-8 -*-
"""
题目数据模型模块
定义各种题型的数据结构类

题型说明：
- single_choice: 单选题
- multi_choice: 多选题  
- fill_blank: 填空题
- judge: 判断题
- short_answer: 简答题
- coding: 编程题
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union, Any
from enum import Enum


class QuestionType(Enum):
    """
    题目类型枚举
    用于标识不同类型的题目
    """
    SINGLE_CHOICE = "single_choice"   # 单选题
    MULTI_CHOICE = "multi_choice"     # 多选题
    FILL_BLANK = "fill_blank"         # 填空题
    JUDGE = "judge"                   # 判断题
    SHORT_ANSWER = "short_answer"     # 简答题
    CODING = "coding"                 # 编程题


class Difficulty(Enum):
    """
    题目难度枚举
    """
    EASY = "easy"       # 简单
    MEDIUM = "medium"   # 中等
    HARD = "hard"       # 困难


@dataclass
class Question:
    """
    题目基类
    所有题型的公共属性都定义在这里
    
    属性说明：
        id: 题目唯一标识符
        type: 题目类型（使用QuestionType枚举值的字符串形式）
        question: 题目内容/题干
        difficulty: 难度等级
        tags: 标签列表，用于分类
        explanation: 答案解析
    """
    id: int                                    # 题目ID
    type: str                                  # 题目类型
    question: str                              # 题目内容
    difficulty: str = "medium"                 # 难度：easy/medium/hard
    tags: List[str] = field(default_factory=list)  # 标签列表
    explanation: str = ""                      # 答案解析
    
    def check_answer(self, user_answer: Any) -> bool:
        """
        检查答案是否正确
        默认返回False，子类需重写此方法
        """
        return False
    
    def get_type_display(self) -> str:
        """
        获取题目类型的中文显示名称
        
        返回：
            str: 题目类型的中文名称
        """
        type_names = {
            "single_choice": "单选题",
            "multi_choice": "多选题",
            "fill_blank": "填空题",
            "judge": "判断题",
            "short_answer": "简答题",
            "coding": "编程题"
        }
        return type_names.get(self.type, "未知题型")
    
    def get_difficulty_display(self) -> str:
        """
        获取难度的中文显示名称
        
        返回：
            str: 难度的中文名称
        """
        difficulty_names = {
            "easy": "简单",
            "medium": "中等",
            "hard": "困难"
        }
        return difficulty_names.get(self.difficulty, "未知")


@dataclass
class SingleChoiceQuestion(Question):
    """
    单选题类
    继承自Question基类，添加选项和答案属性
    
    属性说明：
        options: 选项列表，如["A. 选项1", "B. 选项2", ...]
        answer: 正确答案，如"A"
    """
    options: List[str] = field(default_factory=list)  # 选项列表
    answer: str = ""                                   # 正确答案（单个字母）
    
    def check_answer(self, user_answer: str) -> bool:
        """
        检查用户答案是否正确
        
        参数：
            user_answer: 用户选择的答案
            
        返回：
            bool: 答案是否正确
        """
        # 统一转为大写比较，忽略大小写差异
        return user_answer.upper().strip() == self.answer.upper().strip()


@dataclass
class MultiChoiceQuestion(Question):
    """
    多选题类
    与单选题类似，但答案是一个列表
    
    属性说明：
        options: 选项列表
        answer: 正确答案列表，如["A", "B", "D"]
    """
    options: List[str] = field(default_factory=list)  # 选项列表
    answer: List[str] = field(default_factory=list)   # 正确答案列表
    
    def check_answer(self, user_answer: List[str]) -> bool:
        """
        检查用户答案是否正确
        多选题需要完全匹配才算正确
        
        参数：
            user_answer: 用户选择的答案列表
            
        返回：
            bool: 答案是否正确
        """
        # 将两个列表都转为大写并排序后比较
        user_set = set(a.upper().strip() for a in user_answer)
        correct_set = set(a.upper().strip() for a in self.answer)
        return user_set == correct_set


@dataclass
class FillBlankQuestion(Question):
    """
    填空题类
    支持单个或多个填空
    
    属性说明：
        answer: 答案列表，每个元素对应一个空的答案
               如果某个空有多个可接受答案，可以用字符串形式："答案1|答案2"
    """
    answer: List[str] = field(default_factory=list)  # 答案列表
    
    def check_answer(self, user_answers: List[str]) -> bool:
        """
        检查用户答案是否正确
        
        参数：
            user_answers: 用户填写的答案列表
            
        返回：
            bool: 答案是否正确
        """
        # 答案数量必须一致
        if len(user_answers) != len(self.answer):
            return False
        
        # 逐个检查每个空的答案
        for user_ans, correct_ans in zip(user_answers, self.answer):
            # 支持多个可接受答案，用|分隔
            acceptable_answers = [a.strip().lower() for a in correct_ans.split("|")]
            if user_ans.strip().lower() not in acceptable_answers:
                return False
        
        return True


@dataclass
class JudgeQuestion(Question):
    """
    判断题类
    答案只有对（True）或错（False）
    
    属性说明：
        answer: 正确答案，True表示对，False表示错
    """
    answer: bool = True  # 正确答案
    
    def check_answer(self, user_answer: bool) -> bool:
        """
        检查用户答案是否正确
        
        参数：
            user_answer: 用户的判断
            
        返回：
            bool: 答案是否正确
        """
        return user_answer == self.answer


@dataclass
class ShortAnswerQuestion(Question):
    """
    简答题类
    用户输入文字作答，与参考答案对比
    
    属性说明：
        answer: 参考答案文本
        keywords: 关键词列表，用于简单的答案匹配检查
    """
    answer: str = ""                                   # 参考答案
    keywords: List[str] = field(default_factory=list)  # 关键词列表
    
    def check_keywords(self, user_answer: str) -> tuple:
        """
        检查用户答案中包含了多少关键词
        简答题不做严格判断，返回匹配的关键词数量和总数
        
        参数：
            user_answer: 用户的回答
            
        返回：
            tuple: (匹配的关键词数量, 关键词总数, 匹配的关键词列表)
        """
        user_answer_lower = user_answer.lower()
        matched = [kw for kw in self.keywords if kw.lower() in user_answer_lower]
        return (len(matched), len(self.keywords), matched)

    def check_answer(self, user_answer: str) -> bool:
        """
        检查简答题答案
        如果提供了参考答案，则进行简单比对；否则返回False（需人工阅卷）
        """
        if not user_answer:
            return False
        # 简单比对：如果包含关键词或与参考答案相似
        if self.keywords:
            matched_count, _, _ = self.check_keywords(user_answer)
            return matched_count > 0
        return user_answer.strip() == self.answer.strip()


@dataclass
class TestCase:
    """
    编程题测试用例
    
    属性说明：
        input: 输入数据（字符串形式）
        expected_output: 期望的输出结果
    """
    input: str = ""           # 输入
    expected_output: str = "" # 期望输出


@dataclass
class CodingQuestion(Question):
    """
    编程题类
    支持代码编写和运行验证
    
    属性说明：
        code_template: 代码模板，用户在此基础上编写代码
        test_cases: 测试用例列表
        answer_code: 参考答案代码
        language: 编程语言，默认为python
    """
    code_template: str = ""                              # 代码模板
    test_cases: List[dict] = field(default_factory=list) # 测试用例
    answer_code: str = ""                                # 参考答案代码
    language: str = "python"                             # 编程语言
    
    def check_answer(self, user_answer: str) -> bool:
        """
        检查编程题答案
        目前仅检查是否非空，实际应运行测试用例
        """
        return bool(user_answer and user_answer.strip())
    
    def get_test_cases(self) -> List[TestCase]:
        """
        获取测试用例对象列表
        
        返回：
            List[TestCase]: 测试用例列表
        """
        return [
            TestCase(
                input=tc.get("input", ""),
                expected_output=tc.get("expected_output", "")
            )
            for tc in self.test_cases
        ]


def create_question_from_dict(data: dict) -> Question:
    """
    工厂函数：根据字典数据创建对应类型的题目对象
    
    这个函数会根据字典中的type字段，自动创建对应类型的题目对象。
    这样在加载JSON题库时可以方便地转换数据。
    
    参数：
        data: 包含题目数据的字典
        
    返回：
        Question: 对应类型的题目对象
        
    示例：
        >>> data = {"id": 1, "type": "single_choice", "question": "...", ...}
        >>> question = create_question_from_dict(data)
        >>> isinstance(question, SingleChoiceQuestion)
        True
    """
    # 获取题目类型
    q_type = data.get("type", "")
    
    # 提取公共字段
    common_fields = {
        "id": data.get("id", 0),
        "type": q_type,
        "question": data.get("question", ""),
        "difficulty": data.get("difficulty", "medium"),
        "tags": data.get("tags", []),
        "explanation": data.get("explanation", "")
    }
    
    # 根据类型创建对应的题目对象
    if q_type == "single_choice":
        return SingleChoiceQuestion(
            **common_fields,
            options=data.get("options", []),
            answer=data.get("answer", "")
        )
    
    elif q_type == "multi_choice":
        return MultiChoiceQuestion(
            **common_fields,
            options=data.get("options", []),
            answer=data.get("answer", [])
        )
    
    elif q_type == "fill_blank":
        return FillBlankQuestion(
            **common_fields,
            answer=data.get("answer", [])
        )
    
    elif q_type == "judge":
        return JudgeQuestion(
            **common_fields,
            answer=data.get("answer", True)
        )
    
    elif q_type == "short_answer":
        return ShortAnswerQuestion(
            **common_fields,
            answer=data.get("answer", ""),
            keywords=data.get("keywords", [])
        )
    
    elif q_type == "coding":
        return CodingQuestion(
            **common_fields,
            code_template=data.get("code_template", ""),
            test_cases=data.get("test_cases", []),
            answer_code=data.get("answer_code", ""),
            language=data.get("language", "python")
        )
    
    else:
        # 未知类型，返回基类对象
        return Question(**common_fields)
