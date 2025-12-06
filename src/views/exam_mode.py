# -*- coding: utf-8 -*-
"""
考试模式模块
提供模拟考试功能，支持批量答题后统一提交
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from src.models.question import (
    Question, SingleChoiceQuestion, MultiChoiceQuestion,
    FillBlankQuestion, JudgeQuestion
)


@dataclass
class ExamAnswer:
    """考试答案记录"""
    question_id: int
    question_index: int
    user_answer: Any = None
    is_answered: bool = False


class ExamMode(ttkb.Toplevel):
    """
    考试模式窗口
    支持批量答题后统一提交检查
    """
    
    def __init__(self, parent, questions: List[Question], 
                 question_count: int = 10, on_finish=None):
        """
        初始化考试模式
        
        参数：
            parent: 父窗口
            questions: 题目列表
            question_count: 考试题目数量
            on_finish: 考试结束回调
        """
        super().__init__(parent)
        
        self.all_questions = questions
        self.question_count = min(question_count, len(questions))
        self.on_finish = on_finish
        
        # 选取题目
        self.exam_questions = self.all_questions[:self.question_count]
        
        # 答案记录
        self.answers: Dict[int, ExamAnswer] = {}
        for i, q in enumerate(self.exam_questions):
            self.answers[i] = ExamAnswer(
                question_id=q.id,
                question_index=i
            )
        
        # 当前题目索引
        self.current_index = 0
        
        # 用户选择变量
        self.user_choice_var = tk.StringVar()
        self.user_multi_choices: List[tk.BooleanVar] = []
        self.fill_blank_entries: List[ttk.Entry] = []
        self.judge_var = tk.BooleanVar()
        
        # 窗口设置
        self.title("📝 考试模式")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        # 构建界面
        self._build_ui()
        
        # 显示第一题
        self._show_question(0)
        
        # 阻止关闭窗口时直接退出
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 顶部信息栏
        self._build_header(main_frame)
        
        # 中间内容区
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # 左侧答题卡
        self._build_answer_card(content_frame)
        
        # 右侧题目区
        self._build_question_area(content_frame)
        
        # 底部按钮栏
        self._build_footer(main_frame)
    
    def _build_header(self, parent):
        """构建顶部信息栏"""
        header = ttk.Frame(parent)
        header.pack(fill=X, pady=(0, 10))
        
        ttk.Label(
            header,
            text="📝 考试模式",
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack(side=LEFT)
        
        # 进度显示
        self.progress_label = ttk.Label(
            header,
            text=f"进度：0/{self.question_count}",
            font=("Microsoft YaHei UI", 12)
        )
        self.progress_label.pack(side=RIGHT, padx=20)
    
    def _build_answer_card(self, parent):
        """构建答题卡"""
        card_frame = ttk.LabelFrame(parent, text="📋 答题卡", padding=10)
        card_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        # 答题卡说明
        ttk.Label(
            card_frame,
            text="点击跳转，绿色=已答",
            font=("Microsoft YaHei UI", 9),
            foreground="gray"
        ).pack(pady=(0, 10))
        
        # 答题卡按钮容器
        buttons_frame = ttk.Frame(card_frame)
        buttons_frame.pack(fill=BOTH, expand=True)
        
        self.card_buttons: List[ttk.Button] = []
        
        # 每行5个按钮
        cols = 5
        for i in range(self.question_count):
            row = i // cols
            col = i % cols
            
            btn = ttk.Button(
                buttons_frame,
                text=str(i + 1),
                width=4,
                command=lambda idx=i: self._goto_question(idx),
                bootstyle="secondary-outline"
            )
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.card_buttons.append(btn)
    
    def _build_question_area(self, parent):
        """构建题目区域"""
        question_frame = ttk.LabelFrame(parent, text="题目", padding=15)
        question_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 题目编号
        self.question_num_label = ttk.Label(
            question_frame,
            text="第 1 题",
            font=("Microsoft YaHei UI", 14, "bold")
        )
        self.question_num_label.pack(anchor=W, pady=(0, 10))
        
        # 题目内容
        self.question_text = tk.Text(
            question_frame,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 12),
            height=5,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bg=self.cget("background")
        )
        self.question_text.pack(fill=X, pady=(0, 15))
        
        # 选项容器
        self.options_container = ttk.Frame(question_frame)
        self.options_container.pack(fill=BOTH, expand=True)
        
        # 导航按钮
        nav_frame = ttk.Frame(question_frame)
        nav_frame.pack(fill=X, pady=(20, 0))
        
        ttk.Button(
            nav_frame,
            text="⬅ 上一题",
            command=self._prev_question,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            nav_frame,
            text="下一题 ➡",
            command=self._next_question,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        # 保存并下一题按钮
        ttk.Button(
            nav_frame,
            text="💾 保存并下一题",
            command=self._save_and_next,
            bootstyle="info"
        ).pack(side=RIGHT, padx=5)
    
    def _build_footer(self, parent):
        """构建底部按钮栏"""
        footer = ttk.Frame(parent)
        footer.pack(fill=X, pady=(10, 0))
        
        # 交卷按钮
        ttk.Button(
            footer,
            text="📤 交卷",
            command=self._submit_exam,
            bootstyle="success"
        ).pack(side=RIGHT, padx=5)
        
        # 退出按钮
        ttk.Button(
            footer,
            text="退出考试",
            command=self._on_close,
            bootstyle="danger-outline"
        ).pack(side=RIGHT, padx=5)
    
    def _show_question(self, index: int):
        """显示指定题目"""
        if index < 0 or index >= self.question_count:
            return
        
        # 保存当前答案
        if self.current_index != index:
            self._save_current_answer(silent=True)
        
        self.current_index = index
        question = self.exam_questions[index]
        
        # 更新题目编号
        self.question_num_label.config(text=f"第 {index + 1} 题 ({self._get_type_name(question.type)})")
        
        # 更新题目内容
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", question.question)
        self.question_text.config(state=tk.DISABLED)
        
        # 清空选项容器
        for widget in self.options_container.winfo_children():
            widget.destroy()
        
        # 根据题型显示选项
        if isinstance(question, SingleChoiceQuestion):
            self._show_single_choice(question)
        elif isinstance(question, MultiChoiceQuestion):
            self._show_multi_choice(question)
        elif isinstance(question, JudgeQuestion):
            self._show_judge(question)
        elif isinstance(question, FillBlankQuestion):
            self._show_fill_blank(question)
        
        # 恢复已保存的答案
        self._restore_answer(index)
        
        # 更新答题卡高亮
        self._update_card_highlight()
    
    def _get_type_name(self, q_type: str) -> str:
        """获取题型名称"""
        type_names = {
            "single_choice": "单选题",
            "multi_choice": "多选题",
            "fill_blank": "填空题",
            "judge": "判断题"
        }
        return type_names.get(q_type, q_type)
    
    def _show_single_choice(self, question: SingleChoiceQuestion):
        """显示单选题"""
        self.user_choice_var.set("")
        
        for option in question.options:
            letter = option[0] if option else ""
            option_text = option[2:].strip() if len(option) > 2 else option
            
            option_card = ttk.Frame(self.options_container, padding=(15, 10))
            option_card.pack(fill=X, pady=3)
            
            ttk.Label(
                option_card,
                text=letter,
                font=("Microsoft YaHei UI", 12, "bold"),
                width=3,
                anchor=CENTER,
                bootstyle="inverse-primary"
            ).pack(side=LEFT, padx=(0, 12))
            
            rb = ttk.Radiobutton(
                option_card,
                text=option_text,
                variable=self.user_choice_var,
                value=letter,
                bootstyle="primary-outline-toolbutton"
            )
            rb.pack(side=LEFT, fill=X, expand=True)
    
    def _show_multi_choice(self, question: MultiChoiceQuestion):
        """显示多选题"""
        self.user_multi_choices.clear()
        
        ttk.Label(
            self.options_container,
            text="（多选题，请选择所有正确答案）",
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        ).pack(fill=X, pady=(0, 10))
        
        for option in question.options:
            var = tk.BooleanVar(value=False)
            self.user_multi_choices.append(var)
            
            letter = option[0] if option else ""
            option_text = option[2:].strip() if len(option) > 2 else option
            
            option_card = ttk.Frame(self.options_container, padding=(15, 10))
            option_card.pack(fill=X, pady=3)
            
            ttk.Label(
                option_card,
                text=letter,
                font=("Microsoft YaHei UI", 12, "bold"),
                width=3,
                anchor=CENTER,
                bootstyle="inverse-info"
            ).pack(side=LEFT, padx=(0, 12))
            
            cb = ttk.Checkbutton(
                option_card,
                text=option_text,
                variable=var,
                bootstyle="info-square-toggle"
            )
            cb.pack(side=LEFT, fill=X, expand=True)
    
    def _show_judge(self, question: JudgeQuestion):
        """显示判断题"""
        self.judge_var.set(False)
        
        for text, value in [("✓ 正确", True), ("✗ 错误", False)]:
            option_card = ttk.Frame(self.options_container, padding=(15, 10))
            option_card.pack(fill=X, pady=3)
            
            rb = ttk.Radiobutton(
                option_card,
                text=text,
                variable=self.judge_var,
                value=value,
                bootstyle="primary-outline-toolbutton"
            )
            rb.pack(fill=X)
    
    def _show_fill_blank(self, question: FillBlankQuestion):
        """显示填空题"""
        self.fill_blank_entries.clear()
        
        # 计算空格数量
        blank_count = question.question.count("___") or 1
        
        ttk.Label(
            self.options_container,
            text=f"请填写 {blank_count} 个空",
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        ).pack(fill=X, pady=(0, 10))
        
        for i in range(blank_count):
            frame = ttk.Frame(self.options_container)
            frame.pack(fill=X, pady=5)
            
            ttk.Label(
                frame,
                text=f"空 {i + 1}:",
                font=("Microsoft YaHei UI", 11)
            ).pack(side=LEFT, padx=(0, 10))
            
            entry = ttk.Entry(frame, font=("Microsoft YaHei UI", 11))
            entry.pack(side=LEFT, fill=X, expand=True)
            self.fill_blank_entries.append(entry)
    
    def _get_current_answer(self) -> Any:
        """获取当前题目的答案"""
        question = self.exam_questions[self.current_index]
        
        if isinstance(question, SingleChoiceQuestion):
            return self.user_choice_var.get()
        elif isinstance(question, MultiChoiceQuestion):
            selected = []
            for i, var in enumerate(self.user_multi_choices):
                if var.get():
                    letter = question.options[i][0]
                    selected.append(letter)
            return selected
        elif isinstance(question, JudgeQuestion):
            return self.judge_var.get()
        elif isinstance(question, FillBlankQuestion):
            return [entry.get() for entry in self.fill_blank_entries]
        
        return None
    
    def _save_current_answer(self, silent: bool = False):
        """保存当前题目答案"""
        answer = self._get_current_answer()
        
        # 检查是否已作答
        is_answered = False
        if isinstance(answer, str):
            is_answered = bool(answer)
        elif isinstance(answer, list):
            is_answered = any(answer)
        elif isinstance(answer, bool):
            is_answered = True
        
        self.answers[self.current_index].user_answer = answer
        self.answers[self.current_index].is_answered = is_answered
        
        # 更新答题卡和进度
        self._update_card_highlight()
        self._update_progress()
        
        # 已移除弹窗提示
    
    def _restore_answer(self, index: int):
        """恢复已保存的答案"""
        answer_record = self.answers.get(index)
        if not answer_record or not answer_record.is_answered:
            return
        
        question = self.exam_questions[index]
        answer = answer_record.user_answer
        
        if isinstance(question, SingleChoiceQuestion) and isinstance(answer, str):
            self.user_choice_var.set(answer)
        elif isinstance(question, MultiChoiceQuestion) and isinstance(answer, list):
            for i, var in enumerate(self.user_multi_choices):
                letter = question.options[i][0] if i < len(question.options) else ""
                var.set(letter in answer)
        elif isinstance(question, JudgeQuestion) and isinstance(answer, bool):
            self.judge_var.set(answer)
        elif isinstance(question, FillBlankQuestion) and isinstance(answer, list):
            for i, entry in enumerate(self.fill_blank_entries):
                if i < len(answer):
                    entry.delete(0, tk.END)
                    entry.insert(0, answer[i])
    
    def _update_card_highlight(self):
        """更新答题卡高亮"""
        for i, btn in enumerate(self.card_buttons):
            if self.answers[i].is_answered:
                btn.configure(bootstyle="success")
            elif i == self.current_index:
                btn.configure(bootstyle="primary")
            else:
                btn.configure(bootstyle="secondary-outline")
    
    def _update_progress(self):
        """更新进度显示"""
        answered = sum(1 for a in self.answers.values() if a.is_answered)
        self.progress_label.config(text=f"进度：{answered}/{self.question_count}")
    
    def _goto_question(self, index: int):
        """跳转到指定题目"""
        self._show_question(index)
    
    def _prev_question(self):
        """上一题"""
        if self.current_index > 0:
            self._show_question(self.current_index - 1)
    
    def _next_question(self):
        """下一题"""
        if self.current_index < self.question_count - 1:
            self._show_question(self.current_index + 1)
    
    def _save_and_next(self):
        """保存当前答案并跳到下一题"""
        self._save_current_answer(silent=True)
        
        if self.current_index < self.question_count - 1:
            self._show_question(self.current_index + 1)
    
    def _submit_exam(self):
        """交卷"""
        # 保存当前答案
        self._save_current_answer(silent=True)
        
        # 检查未答题数
        unanswered = [i + 1 for i, a in self.answers.items() if not a.is_answered]
        
        if unanswered:
            msg = f"还有 {len(unanswered)} 题未作答：\n{', '.join(map(str, unanswered[:10]))}"
            if len(unanswered) > 10:
                msg += f"...等 {len(unanswered)} 题"
            msg += "\n\n确定要交卷吗？"
            
            if not messagebox.askyesno("确认交卷", msg, parent=self):
                return
        else:
            if not messagebox.askyesno("确认交卷", "已完成所有题目，确定要交卷吗？", parent=self):
                return
        
        # 计算成绩
        results = self._calculate_results()
        
        # 显示结果
        self._show_results(results)
    
    def _calculate_results(self) -> Dict:
        """计算考试结果"""
        correct_count = 0
        wrong_count = 0
        details = []
        
        for i, question in enumerate(self.exam_questions):
            answer_record = self.answers[i]
            user_answer = answer_record.user_answer
            
            # 判断正误
            is_correct = question.check_answer(user_answer)
            
            if is_correct:
                correct_count += 1
            else:
                wrong_count += 1
            
            details.append({
                "index": i,
                "question": question,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "correct_answer": question.answer,
                "explanation": getattr(question, 'explanation', '')
            })
        
        return {
            "total": self.question_count,
            "correct": correct_count,
            "wrong": wrong_count,
            "score": correct_count / self.question_count * 100 if self.question_count > 0 else 0,
            "details": details
        }
    
    def _show_results(self, results: Dict):
        """显示考试结果"""
        # 创建结果窗口
        result_window = ExamResultView(self, results)
        result_window.grab_set()
        self.wait_window(result_window)
        
        # 结果窗口关闭后，关闭考试窗口
        if self.on_finish:
            self.on_finish(results)
        self.destroy()
    
    def _on_close(self):
        """关闭窗口"""
        if messagebox.askyesno("确认退出", "确定要退出考试吗？\n未提交的答案将不会保存。", parent=self):
            self.destroy()


class ExamResultView(ttkb.Toplevel):
    """考试结果展示窗口"""
    
    def __init__(self, parent, results: Dict):
        super().__init__(parent)
        
        self.results = results
        
        self.title("📊 考试结果")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        self._build_ui()
    
    def _build_ui(self):
        """构建界面"""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 成绩概览
        self._build_summary(main_frame)
        
        # 详细结果
        self._build_details(main_frame)
        
        # 关闭按钮
        ttk.Button(
            main_frame,
            text="关闭",
            command=self.destroy,
            bootstyle="primary"
        ).pack(pady=10)
    
    def _build_summary(self, parent):
        """构建成绩概览"""
        summary_frame = ttk.Frame(parent)
        summary_frame.pack(fill=X, pady=(0, 20))
        
        # 分数显示
        score = self.results["score"]
        score_color = "success" if score >= 60 else "danger"
        
        ttk.Label(
            summary_frame,
            text=f"🎯 得分：{score:.1f}分",
            font=("Microsoft YaHei UI", 24, "bold"),
            bootstyle=score_color
        ).pack()
        
        # 统计
        stats_text = f"正确：{self.results['correct']} 题  |  错误：{self.results['wrong']} 题  |  总计：{self.results['total']} 题"
        ttk.Label(
            summary_frame,
            text=stats_text,
            font=("Microsoft YaHei UI", 12)
        ).pack(pady=10)
    
    def _build_details(self, parent):
        """构建详细结果"""
        details_frame = ttk.LabelFrame(parent, text="📝 答题详情", padding=10)
        details_frame.pack(fill=BOTH, expand=True)
        
        # 创建带滚动条的列表
        canvas = tk.Canvas(details_frame)
        scrollbar = ttk.Scrollbar(details_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 阻止滚轮事件传播
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        canvas.bind("<MouseWheel>", on_mousewheel)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 显示每道题的结果
        for detail in self.results["details"]:
            self._add_detail_item(scrollable_frame, detail)
    
    def _add_detail_item(self, parent, detail: Dict):
        """添加详情项"""
        question = detail["question"]
        is_correct = detail["is_correct"]
        
        # 题目容器
        item_frame = ttk.Frame(parent, padding=10)
        item_frame.pack(fill=X, pady=5, padx=5)
        
        # 题号和状态
        status = "✅" if is_correct else "❌"
        header = ttk.Frame(item_frame)
        header.pack(fill=X)
        
        ttk.Label(
            header,
            text=f"{status} 第 {detail['index'] + 1} 题",
            font=("Microsoft YaHei UI", 11, "bold"),
            bootstyle="success" if is_correct else "danger"
        ).pack(side=LEFT)
        
        # 题目内容（简略）
        question_preview = question.question[:50] + "..." if len(question.question) > 50 else question.question
        ttk.Label(
            item_frame,
            text=question_preview,
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        ).pack(fill=X, pady=2)
        
        # 如果答错，显示正确答案和解析
        if not is_correct:
            answer_frame = ttk.Frame(item_frame)
            answer_frame.pack(fill=X, pady=5)
            
            # 用户答案
            user_ans = detail["user_answer"]
            if isinstance(user_ans, list):
                user_ans = ", ".join(str(a) for a in user_ans)
            ttk.Label(
                answer_frame,
                text=f"你的答案：{user_ans or '未作答'}",
                font=("Microsoft YaHei UI", 10),
                bootstyle="danger"
            ).pack(anchor=W)
            
            # 正确答案
            correct_ans = detail["correct_answer"]
            if isinstance(correct_ans, list):
                correct_ans = ", ".join(str(a) for a in correct_ans)
            ttk.Label(
                answer_frame,
                text=f"正确答案：{correct_ans}",
                font=("Microsoft YaHei UI", 10),
                bootstyle="success"
            ).pack(anchor=W)
            
            # 解析
            if detail["explanation"]:
                ttk.Label(
                    answer_frame,
                    text=f"解析：{detail['explanation']}",
                    font=("Microsoft YaHei UI", 10),
                    foreground="gray",
                    wraplength=600
                ).pack(anchor=W, pady=(5, 0))
        
        # 分隔线
        ttk.Separator(item_frame).pack(fill=X, pady=(10, 0))
