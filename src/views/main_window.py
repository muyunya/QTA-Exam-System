# -*- coding: utf-8 -*-
"""
主窗口模块
实现刷题软件的主界面，采用现代化玻璃拟态设计风格
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Optional, List
import time

from src.models.question import (
    Question, SingleChoiceQuestion, MultiChoiceQuestion,
    FillBlankQuestion, JudgeQuestion, ShortAnswerQuestion, CodingQuestion
)
from src.controllers.data_controller import DataController
from src.controllers.quiz_controller import QuizController, PracticeMode
from src.views.code_block import CodeBlock
from src.views.stats_view import StatsView
from src.views.ai_chat import AIChatWindow
from src.views.bank_manager import QuestionBankManager
from src.views.exam_mode import ExamMode
from src.utils.file_handler import get_questions_dir


class MainWindow:
    """
    主窗口类
    管理整个应用的主界面
    """
    
    # 主题配置
    THEMES = {
        "dark": "darkly",      # 暗色主题
        "light": "litera"      # 亮色主题
    }
    
    def __init__(self):
        """初始化主窗口"""
        # 创建数据控制器
        self.data_controller = DataController()
        
        # 创建刷题控制器
        self.quiz_controller = QuizController(self.data_controller)
        self.quiz_controller.on_question_change = self._on_question_change
        
        # 获取设置
        self.settings = self.data_controller.settings
        
        # 创建主窗口
        theme = self.settings.get("theme", "darkly")
        self.root = ttkb.Window(themename=theme)
        self.root.title("QTA 刷题软件")
        self.root.geometry(f"{self.settings.get('window_width', 1200)}x{self.settings.get('window_height', 800)}")
        self.root.minsize(800, 600)
        
        # 当前主题状态
        self.is_dark_theme = theme in ["darkly", "superhero", "cyborg", "vapor"]
        
        # AI助手窗口引用
        self.ai_chat_window = None
        
        # 用户答案变量
        self.user_choice_var = tk.StringVar()        # 单选题
        self.user_multi_choices: List[tk.BooleanVar] = []  # 多选题
        self.user_judge_var = tk.BooleanVar()        # 判断题
        self.fill_blank_entries: List[tk.Entry] = [] # 填空题输入框
        
        # 绑定快捷键
        self._bind_shortcuts()
        
        # 构建界面
        self._build_ui()
        
        # 尝试加载上次的题库
        self._load_last_bank()
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        # 数字键选择选项
        self.root.bind("1", lambda e: self._quick_select("A"))
        self.root.bind("2", lambda e: self._quick_select("B"))
        self.root.bind("3", lambda e: self._quick_select("C"))
        self.root.bind("4", lambda e: self._quick_select("D"))
        self.root.bind("5", lambda e: self._quick_select("E"))
        
        # 回车提交
        self.root.bind("<Return>", lambda e: self._submit_answer())
        
        # 左右箭头切换题目
        self.root.bind("<Left>", lambda e: self._prev_question())
        self.root.bind("<Right>", lambda e: self._next_question())
        
        # Ctrl+O 打开题库
        self.root.bind("<Control-o>", lambda e: self._open_question_bank())
        
        # Ctrl+T 切换主题
        self.root.bind("<Control-t>", lambda e: self._toggle_theme())
    
    def _quick_select(self, option: str):
        """快捷键选择选项"""
        self.user_choice_var.set(option)
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # 左侧边栏
        self._build_sidebar()
        
        # 右侧主内容区
        self._build_main_content()
    
    def _build_sidebar(self):
        """构建左侧边栏"""
        # 侧边栏容器
        sidebar = ttk.Frame(self.main_container, width=250)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))
        sidebar.pack_propagate(False)  # 固定宽度
        
        # Logo和标题
        title_frame = ttk.Frame(sidebar)
        title_frame.pack(fill=X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="📚 QTA 刷题软件",
            font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # 题库选择区域
        bank_frame = ttk.LabelFrame(sidebar, text="📁 题库", padding=10)
        bank_frame.pack(fill=X, pady=(0, 10))
        
        # 当前题库标签
        self.current_bank_label = ttk.Label(
            bank_frame,
            text="未选择题库",
            font=("Microsoft YaHei UI", 10),
            wraplength=200
        )
        self.current_bank_label.pack(fill=X, pady=(0, 10))
        
        # 打开题库按钮
        open_btn = ttk.Button(
            bank_frame,
            text="📂 打开题库",
            command=self._open_question_bank,
            bootstyle="primary-outline"
        )
        open_btn.pack(fill=X, pady=(0, 5))
        
        # 题库管理按钮
        manage_btn = ttk.Button(
            bank_frame,
            text="📚 题库管理",
            command=self._open_bank_manager,
            bootstyle="info-outline"
        )
        manage_btn.pack(fill=X)
        
        # 练习模式区域
        mode_frame = ttk.LabelFrame(sidebar, text="🎯 练习模式", padding=10)
        mode_frame.pack(fill=X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="sequential")
        
        modes = [
            ("顺序练习", "sequential"),
            ("随机练习", "random"),
            ("错题练习", "wrong"),
            ("收藏练习", "favorite")
        ]
        
        for text, value in modes:
            rb = ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,
                value=value,
                command=self._on_mode_change
            )
            rb.pack(fill=X, pady=2)
        
        # 考试模式按钮
        ttk.Button(
            mode_frame,
            text="📝 开始考试",
            command=self._start_exam,
            bootstyle="warning"
        ).pack(fill=X, pady=(10, 0))
        
        # 统计信息区域
        stats_frame = ttk.LabelFrame(sidebar, text="📊 学习统计", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))
        
        self.stats_labels = {}
        
        stats_items = [
            ("total", "答题总数: 0"),
            ("correct", "正确数: 0"),
            ("wrong", "错误数: 0"),
            ("accuracy", "正确率: 0%"),
            ("time", "学习时长: 0分钟")
        ]
        
        for key, text in stats_items:
            label = ttk.Label(stats_frame, text=text, font=("Microsoft YaHei UI", 10))
            label.pack(fill=X, pady=2)
            self.stats_labels[key] = label
        
        # 查看详细统计按钮
        detail_stats_btn = ttk.Button(
            stats_frame,
            text="📈 查看详细统计",
            command=self._show_stats_detail,
            bootstyle="info-outline"
        )
        detail_stats_btn.pack(fill=X, pady=(10, 0))
        
        # 主题切换按钮
        theme_frame = ttk.Frame(sidebar)
        theme_frame.pack(fill=X, pady=10)
        
        self.theme_btn = ttk.Button(
            theme_frame,
            text="🌙 夜间模式" if not self.is_dark_theme else "☀️ 日间模式",
            command=self._toggle_theme,
            bootstyle="secondary-outline"
        )
        self.theme_btn.pack(fill=X)
        
        # AI助手按钮
        ai_frame = ttk.Frame(sidebar)
        ai_frame.pack(fill=X, pady=5)
        
        ai_btn = ttk.Button(
            ai_frame,
            text="🤖 AI 答题助手",
            command=self._open_ai_chat,
            bootstyle="success"
        )
        ai_btn.pack(fill=X)
        
        # 更新统计显示
        self._update_stats_display()
    
    def _build_main_content(self):
        """构建右侧主内容区"""
        # 主内容容器
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        # 顶部进度条和收藏按钮
        top_bar = ttk.Frame(self.content_frame)
        top_bar.pack(fill=X, pady=(0, 10))
        
        # 进度显示
        self.progress_label = ttk.Label(
            top_bar,
            text="题目 0/0",
            font=("Microsoft YaHei UI", 12)
        )
        self.progress_label.pack(side=LEFT)
        
        # 收藏按钮
        self.favorite_btn = ttk.Button(
            top_bar,
            text="⭐ 收藏",
            command=self._toggle_favorite,
            bootstyle="warning-outline"
        )
        self.favorite_btn.pack(side=RIGHT)
        
        # 题目类型和难度标签
        self.type_label = ttk.Label(
            top_bar,
            text="",
            font=("Microsoft YaHei UI", 10)
        )
        self.type_label.pack(side=RIGHT, padx=20)
        
        # 题目内容区域（使用Canvas实现滚动）
        self.question_canvas = tk.Canvas(self.content_frame, highlightthickness=0)
        self.question_scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient=VERTICAL,
            command=self.question_canvas.yview
        )
        
        self.question_frame = ttk.Frame(self.question_canvas)
        
        self.question_canvas.configure(yscrollcommand=self.question_scrollbar.set)
        
        self.question_scrollbar.pack(side=RIGHT, fill=Y)
        self.question_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.canvas_window = self.question_canvas.create_window(
            (0, 0),
            window=self.question_frame,
            anchor=NW
        )
        
        # 绑定滚动事件
        self.question_frame.bind("<Configure>", self._on_frame_configure)
        self.question_canvas.bind("<Configure>", self._on_canvas_configure)
        self.question_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # 显示欢迎信息
        self._show_welcome()
    
    def _on_frame_configure(self, event):
        """调整Canvas滚动区域"""
        self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """调整Frame宽度以匹配Canvas"""
        self.question_canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.question_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _show_welcome(self):
        """显示欢迎信息"""
        # 清空内容区
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        welcome_frame = ttk.Frame(self.question_frame)
        welcome_frame.pack(fill=BOTH, expand=True, pady=50)
        
        ttk.Label(
            welcome_frame,
            text="🎉 欢迎使用 QTA 刷题软件！",
            font=("Microsoft YaHei UI", 24, "bold")
        ).pack(pady=20)
        
        ttk.Label(
            welcome_frame,
            text="请点击左侧「打开题库」按钮选择题库文件开始练习",
            font=("Microsoft YaHei UI", 14)
        ).pack(pady=10)
        
        ttk.Label(
            welcome_frame,
            text="快捷键提示：",
            font=("Microsoft YaHei UI", 12, "bold")
        ).pack(pady=(30, 10))
        
        shortcuts = [
            "1-5: 快速选择选项",
            "Enter: 提交答案",
            "←/→: 上一题/下一题",
            "Ctrl+O: 打开题库",
            "Ctrl+T: 切换主题"
        ]
        
        for shortcut in shortcuts:
            ttk.Label(
                welcome_frame,
                text=shortcut,
                font=("Microsoft YaHei UI", 11)
            ).pack(pady=2)
    
    def _open_question_bank(self):
        """打开题库文件选择对话框"""
        file_path = filedialog.askopenfilename(
            title="选择题库文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialdir=str(self.data_controller.get_questions_dir()) if hasattr(self.data_controller, 'get_questions_dir') else "."
        )
        
        if file_path:
            self._load_question_bank(file_path)
    
    def _load_question_bank(self, file_path: str):
        """加载题库"""
        if self.data_controller.load_bank(file_path):
            meta = self.data_controller.current_bank_meta
            self.current_bank_label.configure(
                text=f"{meta.get('name', '未命名题库')}\n共 {self.data_controller.get_total_questions()} 道题"
            )
            
            # 开始练习
            self._on_mode_change()
        else:
            messagebox.showerror("错误", "加载题库失败，请检查文件格式")
    
    def _load_last_bank(self):
        """加载上次使用的题库"""
        last_bank = self.data_controller.user_progress.current_bank
        if last_bank:
            try:
                self._load_question_bank(last_bank)
            except:
                pass  # 静默失败
    
    def _on_mode_change(self):
        """练习模式改变"""
        mode_map = {
            "sequential": PracticeMode.SEQUENTIAL,
            "random": PracticeMode.RANDOM,
            "wrong": PracticeMode.WRONG,
            "favorite": PracticeMode.FAVORITE
        }
        
        mode = mode_map.get(self.mode_var.get(), PracticeMode.SEQUENTIAL)
        self.quiz_controller.set_practice_mode(mode)
        
        if not self.quiz_controller.start_practice():
            # 没有题目
            if mode == PracticeMode.WRONG:
                messagebox.showinfo("提示", "错题本为空")
            elif mode == PracticeMode.FAVORITE:
                messagebox.showinfo("提示", "收藏夹为空")
            else:
                messagebox.showinfo("提示", "题库为空")
    
    def _on_question_change(self, question: Question):
        """题目变化回调"""
        self._display_question(question)
        self._update_progress_display()
        self._update_favorite_button()
    
    def _display_question(self, question: Question):
        """显示题目"""
        # 清空内容区
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        
        # 更新类型和难度标签
        self.type_label.configure(
            text=f"[{question.get_type_display()}] {question.get_difficulty_display()}"
        )
        
        # 题目容器
        q_container = ttk.Frame(self.question_frame)
        q_container.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # 题目标题
        ttk.Label(
            q_container,
            text=question.question,
            font=("Microsoft YaHei UI", 14),
            wraplength=700
        ).pack(fill=X, pady=(0, 20), anchor=W)
        
        # 根据题目类型显示不同的答题界面
        if isinstance(question, SingleChoiceQuestion):
            self._display_single_choice(q_container, question)
        elif isinstance(question, MultiChoiceQuestion):
            self._display_multi_choice(q_container, question)
        elif isinstance(question, FillBlankQuestion):
            self._display_fill_blank(q_container, question)
        elif isinstance(question, JudgeQuestion):
            self._display_judge(q_container, question)
        elif isinstance(question, ShortAnswerQuestion):
            self._display_short_answer(q_container, question)
        elif isinstance(question, CodingQuestion):
            self._display_coding(q_container, question)
        
        # 底部按钮区域
        self._build_button_bar(q_container)
    
    def _display_single_choice(self, container: ttk.Frame, question: SingleChoiceQuestion):
        """显示单选题"""
        self.user_choice_var.set("")  # 清空选择
        
        options_frame = ttk.Frame(container)
        options_frame.pack(fill=X, pady=10)
        
        for i, option in enumerate(question.options):
            # 提取选项字母
            letter = option[0] if option else ""
            
            # 创建卡片式选项框
            option_card = ttk.Frame(options_frame, padding=(15, 12))
            option_card.pack(fill=X, pady=4, padx=5)
            
            # 选项字母标签（圆形背景效果）
            letter_label = ttk.Label(
                option_card,
                text=letter,
                font=("Microsoft YaHei UI", 12, "bold"),
                width=3,
                anchor=CENTER,
                bootstyle="inverse-primary"
            )
            letter_label.pack(side=LEFT, padx=(0, 12))
            
            # 选项内容
            option_text = option[2:].strip() if len(option) > 2 else option
            
            rb = ttk.Radiobutton(
                option_card,
                text=option_text,
                variable=self.user_choice_var,
                value=letter,
                bootstyle="primary-outline-toolbutton"
            )
            rb.pack(side=LEFT, fill=X, expand=True)
    
    def _display_multi_choice(self, container: ttk.Frame, question: MultiChoiceQuestion):
        """显示多选题"""
        self.user_multi_choices.clear()
        
        options_frame = ttk.Frame(container)
        options_frame.pack(fill=X, pady=10)
        
        ttk.Label(
            options_frame,
            text="（多选题，请选择所有正确答案）",
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        ).pack(fill=X, pady=(0, 10))
        
        for option in question.options:
            var = tk.BooleanVar(value=False)
            self.user_multi_choices.append(var)
            
            # 提取选项字母
            letter = option[0] if option else ""
            
            # 创建卡片式选项框
            option_card = ttk.Frame(options_frame, padding=(15, 12))
            option_card.pack(fill=X, pady=4, padx=5)
            
            # 选项字母标签
            letter_label = ttk.Label(
                option_card,
                text=letter,
                font=("Microsoft YaHei UI", 12, "bold"),
                width=3,
                anchor=CENTER,
                bootstyle="inverse-info"
            )
            letter_label.pack(side=LEFT, padx=(0, 12))
            
            # 选项内容
            option_text = option[2:].strip() if len(option) > 2 else option
            
            cb = ttk.Checkbutton(
                option_card,
                text=option_text,
                variable=var,
                bootstyle="info-square-toggle"
            )
            cb.pack(side=LEFT, fill=X, expand=True)
    
    def _display_fill_blank(self, container: ttk.Frame, question: FillBlankQuestion):
        """显示填空题"""
        self.fill_blank_entries.clear()
        
        fill_frame = ttk.Frame(container)
        fill_frame.pack(fill=X, pady=10)
        
        # 计算需要几个输入框
        blank_count = len(question.answer)
        
        for i in range(blank_count):
            frame = ttk.Frame(fill_frame)
            frame.pack(fill=X, pady=5)
            
            ttk.Label(
                frame,
                text=f"第 {i + 1} 空:",
                font=("Microsoft YaHei UI", 11)
            ).pack(side=LEFT, padx=(10, 5))
            
            entry = ttk.Entry(frame, font=("Microsoft YaHei UI", 12), width=40)
            entry.pack(side=LEFT, padx=5)
            self.fill_blank_entries.append(entry)
    
    def _display_judge(self, container: ttk.Frame, question: JudgeQuestion):
        """显示判断题"""
        self.user_judge_var.set(True)  # 默认选择正确
        
        judge_frame = ttk.Frame(container)
        judge_frame.pack(fill=X, pady=20)
        
        ttk.Radiobutton(
            judge_frame,
            text="✓ 正确",
            variable=self.user_judge_var,
            value=True,
            bootstyle="success-toolbutton"
        ).pack(side=LEFT, padx=20)
        
        ttk.Radiobutton(
            judge_frame,
            text="✗ 错误",
            variable=self.user_judge_var,
            value=False,
            bootstyle="danger-toolbutton"
        ).pack(side=LEFT, padx=20)
    
    def _display_short_answer(self, container: ttk.Frame, question: ShortAnswerQuestion):
        """显示简答题"""
        answer_frame = ttk.Frame(container)
        answer_frame.pack(fill=BOTH, expand=True, pady=10)
        
        ttk.Label(
            answer_frame,
            text="请输入你的回答：",
            font=("Microsoft YaHei UI", 11)
        ).pack(fill=X, pady=(0, 5))
        
        self.short_answer_text = tk.Text(
            answer_frame,
            height=8,
            font=("Microsoft YaHei UI", 12),
            wrap=tk.WORD
        )
        self.short_answer_text.pack(fill=X, pady=5, padx=10)
        
        if question.keywords:
            ttk.Label(
                answer_frame,
                text=f"提示关键词：{', '.join(question.keywords)}",
                font=("Microsoft YaHei UI", 10),
                foreground="gray"
            ).pack(fill=X, pady=5)
    
    def _display_coding(self, container: ttk.Frame, question: CodingQuestion):
        """显示编程题"""
        coding_frame = ttk.Frame(container)
        coding_frame.pack(fill=BOTH, expand=True, pady=10)
        
        # 显示代码模板（可编辑）
        ttk.Label(
            coding_frame,
            text="请在下面编写代码：",
            font=("Microsoft YaHei UI", 11)
        ).pack(fill=X, pady=(0, 5))
        
        self.code_editor = CodeBlock(
            coding_frame,
            code=question.code_template,
            language=question.language,
            editable=True,
            height=12
        )
        self.code_editor.pack(fill=BOTH, expand=True, pady=5)
        
        # 测试用例提示
        if question.test_cases:
            ttk.Label(
                coding_frame,
                text=f"共 {len(question.test_cases)} 个测试用例",
                font=("Microsoft YaHei UI", 10),
                foreground="gray"
            ).pack(fill=X, pady=5)
    
    def _build_button_bar(self, container: ttk.Frame):
        """构建底部按钮栏"""
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=X, pady=20)
        
        # 上一题按钮
        ttk.Button(
            btn_frame,
            text="⬅ 上一题",
            command=self._prev_question,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        # 提交按钮
        ttk.Button(
            btn_frame,
            text="✓ 提交答案",
            command=self._submit_answer,
            bootstyle="success"
        ).pack(side=LEFT, padx=20)
        
        # 下一题按钮
        ttk.Button(
            btn_frame,
            text="下一题 ➡",
            command=self._next_question,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        # 查看答案按钮（针对简答题和编程题）
        question = self.quiz_controller.get_current_question()
        if isinstance(question, (ShortAnswerQuestion, CodingQuestion)):
            ttk.Button(
                btn_frame,
                text="👁 查看参考答案",
                command=self._show_answer,
                bootstyle="info-outline"
            ).pack(side=RIGHT, padx=5)
    
    def _prev_question(self):
        """上一题"""
        self.quiz_controller.prev_question()
    
    def _next_question(self):
        """下一题"""
        self.quiz_controller.next_question()
    
    def _submit_answer(self):
        """提交答案"""
        question = self.quiz_controller.get_current_question()
        if not question:
            return
        
        # 获取用户答案
        user_answer = self._get_user_answer(question)
        
        # 检查答案
        is_correct, correct_answer, explanation = self.quiz_controller.check_answer(user_answer)
        
        # 显示结果
        self._show_result(is_correct, correct_answer, explanation)
        
        # 更新统计显示
        self._update_stats_display()
    
    def _get_user_answer(self, question: Question):
        """获取用户答案"""
        if isinstance(question, SingleChoiceQuestion):
            return self.user_choice_var.get()
        
        elif isinstance(question, MultiChoiceQuestion):
            # 获取所有选中的选项
            selected = []
            for i, var in enumerate(self.user_multi_choices):
                if var.get():
                    # 提取选项字母
                    letter = question.options[i][0] if question.options[i] else ""
                    selected.append(letter)
            return selected
        
        elif isinstance(question, FillBlankQuestion):
            return [entry.get() for entry in self.fill_blank_entries]
        
        elif isinstance(question, JudgeQuestion):
            return self.user_judge_var.get()
        
        elif isinstance(question, ShortAnswerQuestion):
            return self.short_answer_text.get("1.0", tk.END).strip()
        
        elif isinstance(question, CodingQuestion):
            return self.code_editor.get_code()
        
        return ""
    
    def _show_result(self, is_correct: bool, correct_answer: str, explanation: str):
        """显示答题结果"""
        # 创建结果对话框
        result_window = ttkb.Toplevel(self.root)
        result_window.title("答题结果")
        result_window.geometry("500x400")
        result_window.transient(self.root)
        result_window.grab_set()
        
        # 结果图标和文字
        result_frame = ttk.Frame(result_window, padding=20)
        result_frame.pack(fill=BOTH, expand=True)
        
        if is_correct:
            icon_text = "✅"
            result_text = "回答正确！"
            style = "success"
        else:
            icon_text = "❌"
            result_text = "回答错误"
            style = "danger"
        
        ttk.Label(
            result_frame,
            text=icon_text,
            font=("Segoe UI Emoji", 48)
        ).pack(pady=10)
        
        ttk.Label(
            result_frame,
            text=result_text,
            font=("Microsoft YaHei UI", 18, "bold"),
            bootstyle=style
        ).pack(pady=5)
        
        # 正确答案
        if not is_correct and correct_answer:
            ttk.Label(
                result_frame,
                text=f"正确答案：{correct_answer}",
                font=("Microsoft YaHei UI", 12)
            ).pack(pady=10)
        
        # 解析
        if explanation:
            ttk.Separator(result_frame).pack(fill=X, pady=10)
            
            ttk.Label(
                result_frame,
                text="💡 解析：",
                font=("Microsoft YaHei UI", 11, "bold")
            ).pack(fill=X)
            
            explanation_text = tk.Text(
                result_frame,
                height=6,
                font=("Microsoft YaHei UI", 11),
                wrap=tk.WORD,
                relief=tk.FLAT
            )
            explanation_text.pack(fill=BOTH, expand=True, pady=5)
            explanation_text.insert("1.0", explanation)
            explanation_text.configure(state=tk.DISABLED)
        
        # 关闭按钮
        ttk.Button(
            result_frame,
            text="确定",
            command=result_window.destroy,
            bootstyle="primary"
        ).pack(pady=10)
    
    def _show_answer(self):
        """显示参考答案"""
        question = self.quiz_controller.get_current_question()
        if not question:
            return
        
        answer_window = ttkb.Toplevel(self.root)
        answer_window.title("参考答案")
        answer_window.geometry("600x500")
        answer_window.transient(self.root)
        
        frame = ttk.Frame(answer_window, padding=20)
        frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="📝 参考答案",
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack(pady=(0, 10))
        
        if isinstance(question, ShortAnswerQuestion):
            text = tk.Text(frame, height=15, font=("Microsoft YaHei UI", 12), wrap=tk.WORD)
            text.pack(fill=BOTH, expand=True)
            text.insert("1.0", question.answer)
            text.configure(state=tk.DISABLED)
        
        elif isinstance(question, CodingQuestion):
            code_block = CodeBlock(
                frame,
                code=question.answer_code,
                language=question.language,
                editable=False,
                height=15
            )
            code_block.pack(fill=BOTH, expand=True)
        
        ttk.Button(
            frame,
            text="关闭",
            command=answer_window.destroy,
            bootstyle="secondary"
        ).pack(pady=10)
    
    def _toggle_favorite(self):
        """切换收藏状态"""
        is_favorite = self.quiz_controller.toggle_favorite()
        self._update_favorite_button()
        
        if is_favorite:
            messagebox.showinfo("收藏", "已添加到收藏夹")
        else:
            messagebox.showinfo("收藏", "已从收藏夹移除")
    
    def _update_favorite_button(self):
        """更新收藏按钮状态"""
        if self.quiz_controller.is_current_favorite():
            self.favorite_btn.configure(text="★ 已收藏", bootstyle="warning")
        else:
            self.favorite_btn.configure(text="☆ 收藏", bootstyle="warning-outline")
    
    def _update_progress_display(self):
        """更新进度显示"""
        current, total = self.quiz_controller.get_progress()
        self.progress_label.configure(text=f"题目 {current}/{total}")
    
    def _update_stats_display(self):
        """更新统计显示"""
        stats = self.data_controller.get_statistics()
        
        self.stats_labels["total"].configure(text=f"答题总数: {stats.total_questions}")
        self.stats_labels["correct"].configure(text=f"正确数: {stats.correct_count}")
        self.stats_labels["wrong"].configure(text=f"错误数: {stats.wrong_count}")
        self.stats_labels["accuracy"].configure(text=f"正确率: {stats.accuracy:.1f}%")
        self.stats_labels["time"].configure(text=f"学习时长: {stats.total_time_display}")
    
    def _show_stats_detail(self):
        """显示详细统计视图"""
        stats = self.data_controller.get_statistics()
        StatsView(self.root, stats, self.is_dark_theme)
    
    def _toggle_theme(self):
        """切换主题"""
        if self.is_dark_theme:
            self.root.style.theme_use("litera")
            self.is_dark_theme = False
            self.theme_btn.configure(text="🌙 夜间模式")
            self.data_controller.update_setting("theme", "litera")
        else:
            self.root.style.theme_use("darkly")
            self.is_dark_theme = True
            self.theme_btn.configure(text="☀️ 日间模式")
            self.data_controller.update_setting("theme", "darkly")
    
    def _open_ai_chat(self):
        """打开AI聊天窗口"""
        # 获取API密钥
        api_key = self.settings.get("ai_api_key", "")
        
        if not api_key:
            messagebox.showwarning("提示", "请先在config/settings.json中配置AI API密钥")
            return
        
        # 如果窗口已存在且有效，聚焦到它
        if self.ai_chat_window and self.ai_chat_window.winfo_exists():
            self.ai_chat_window.lift()
            self.ai_chat_window.focus_force()
            # 更新当前题目到AI窗口
            question = self.quiz_controller.get_current_question()
            if question:
                self.ai_chat_window.set_current_question(question)
        else:
            # 创建新的AI聊天窗口
            self.ai_chat_window = AIChatWindow(
                self.root,
                api_key,
                self.is_dark_theme
            )
            # 设置当前题目
            question = self.quiz_controller.get_current_question()
            if question:
                self.ai_chat_window.set_current_question(question)
    
    def _open_bank_manager(self):
        """打开题库管理器"""
        # 使用file_handler的get_questions_dir函数获取题库目录
        questions_dir = get_questions_dir()
        
        def on_select_bank(bank_path):
            """题库选择回调"""
            self._load_question_bank(bank_path)
        
        # 创建题库管理窗口
        manager = QuestionBankManager(
            self.root,
            str(questions_dir),
            on_select_bank
        )
        manager.grab_set()
    
    def _start_exam(self):
        """开始考试模式"""
        # 检查是否加载了题库
        if not self.data_controller.current_questions:
            messagebox.showwarning("提示", "请先打开一个题库")
            return
        
        total_questions = len(self.data_controller.current_questions)
        
        # 创建题目数量选择对话框
        dialog = ttkb.Toplevel(self.root)
        dialog.title("📝 开始考试")
        dialog.geometry("350x260")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text="请选择考试题目数量",
            font=("Microsoft YaHei UI", 14, "bold")
        ).pack(pady=(0, 20))
        
        ttk.Label(
            main_frame,
            text=f"当前题库共 {total_questions} 题",
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        ).pack()
        
        # 题目数量选择
        count_frame = ttk.Frame(main_frame)
        count_frame.pack(pady=15)
        
        ttk.Label(count_frame, text="题目数量:", font=("Microsoft YaHei UI", 11)).pack(side=LEFT)
        
        count_var = tk.StringVar(value=str(min(10, total_questions)))
        count_spinbox = ttk.Spinbox(
            count_frame,
            from_=1,
            to=total_questions,
            textvariable=count_var,
            width=10,
            font=("Microsoft YaHei UI", 11)
        )
        count_spinbox.pack(side=LEFT, padx=10)
        
        def start():
            try:
                count = int(count_var.get())
                if count < 1 or count > total_questions:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("错误", f"请输入1-{total_questions}之间的数字")
                return
            
            dialog.destroy()
            
            # 启动考试模式
            exam = ExamMode(
                self.root,
                self.data_controller.current_questions,
                question_count=count
            )
            exam.grab_set()
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="开始考试",
            command=start,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="取消",
            command=dialog.destroy,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
    
    def run(self):
        """运行主窗口"""
        self.root.mainloop()
