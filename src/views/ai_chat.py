# -*- coding: utf-8 -*-
"""
AI聊天窗口模块
提供与AI助手对话的界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import threading
from typing import Optional, Callable

from src.utils.ai_service import AIService, AIConfig, create_ai_service
from src.models.question import Question


class AIChatWindow(ttkb.Toplevel):
    """
    AI聊天窗口类
    提供与AI助手对话的界面
    """
    
    # 可用模型列表（硅基流动支持的模型）
    # 格式: (显示名称, 模型ID, 是否免费)
    AVAILABLE_MODELS = [
        # 免费模型
        ("Qwen3-8B (免费/推理)", "Qwen/Qwen3-8B"),
        ("Qwen2.5-7B (免费)", "Qwen/Qwen2.5-7B-Instruct"),
        ("Qwen2.5-Coder-7B (免费)", "Qwen/Qwen2.5-Coder-7B-Instruct"),
        ("DeepSeek-R1-7B (免费/推理)", "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"),
        ("DeepSeek-R1-8B (免费)", "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"),
        ("GLM-4-9B (免费)", "THUDM/glm-4-9b-chat"),
        ("GLM-4-9B-0414 (免费)", "THUDM/GLM-4-9B-0414"),
        ("GLM-Z1-9B (免费/推理)", "THUDM/GLM-Z1-9B-0414"),
        ("InternLM2.5-7B (免费)", "internlm/internlm2_5-7b-chat"),
        # 付费模型
        ("Qwen2.5-VL-7B (视觉)", "Pro/Qwen/Qwen2.5-VL-7B-Instruct"),
        ("GLM-4.1V-9B (视觉/推理)", "Pro/THUDM/GLM-4.1V-9B-Thinking"),
    ]
    
    def __init__(self, parent, api_key: str, is_dark: bool = True):
        """
        初始化AI聊天窗口
        
        参数：
            parent: 父窗口
            api_key: API密钥
            is_dark: 是否暗色主题
        """
        super().__init__(parent)
        
        self.api_key = api_key
        self.is_dark = is_dark
        self.ai_service: Optional[AIService] = None
        self.current_question: Optional[Question] = None
        self.is_loading = False
        
        # 窗口设置
        self.title("🤖 AI 答题助手")
        self.geometry("500x600")
        self.minsize(400, 500)
        
        # 尝试创建AI服务
        self._init_ai_service()
        
        # 构建界面
        self._build_ui()
    
    def _init_ai_service(self):
        """初始化AI服务"""
        if self.api_key:
            self.ai_service = create_ai_service(self.api_key)
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 顶部标题栏
        self._build_header(main_frame)
        
        # 底部：快捷按钮区域（先pack，确保始终可见）
        self._build_quick_buttons(main_frame)
        
        # 底部：输入区域（先pack，确保始终可见）
        self._build_input_area(main_frame)
        
        # 中间：聊天消息区域（最后pack，填充剩余空间）
        self._build_chat_area(main_frame)
    
    def _build_header(self, parent):
        """构建顶部标题栏"""
        header = ttk.Frame(parent)
        header.pack(fill=X, pady=(0, 10))
        
        # 标题
        ttk.Label(
            header,
            text="🤖 AI 答题助手",
            font=("Microsoft YaHei UI", 14, "bold")
        ).pack(side=LEFT)
        
        # 清空对话按钮
        ttk.Button(
            header,
            text="🗑️ 清空",
            command=self._clear_chat,
            bootstyle="secondary-outline"
        ).pack(side=RIGHT)
        
        # 当前题目状态
        self.question_status = ttk.Label(
            header,
            text="未加载题目",
            font=("Microsoft YaHei UI", 10),
            foreground="gray"
        )
        self.question_status.pack(side=RIGHT, padx=10)
        
        # 模型选择区域
        model_frame = ttk.Frame(parent)
        model_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Label(
            model_frame,
            text="模型:",
            font=("Microsoft YaHei UI", 10)
        ).pack(side=LEFT)
        
        # 模型选择下拉框
        self.model_var = tk.StringVar()
        model_names = [m[0] for m in self.AVAILABLE_MODELS]
        
        self.model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=model_names,
            state="readonly",
            width=20
        )
        self.model_combo.pack(side=LEFT, padx=5)
        self.model_combo.current(0)  # 默认选择第一个
        self.model_combo.bind("<<ComboboxSelected>>", self._on_model_change)
    
    def _build_chat_area(self, parent):
        """构建聊天消息区域"""
        # 聊天框容器
        chat_container = ttk.Frame(parent)
        chat_container.pack(fill=BOTH, expand=True, pady=5)
        
        # 聊天消息显示区域
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 11),
            state=tk.DISABLED,
            height=20
        )
        self.chat_display.pack(fill=BOTH, expand=True)
        
        # 阻止滚轮事件传播到父窗口
        def on_mousewheel(event):
            self.chat_display.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"  # 阻止事件传播
        
        self.chat_display.bind("<MouseWheel>", on_mousewheel)
        
        # 配置文本标签样式
        self.chat_display.tag_configure(
            "user",
            foreground="#3B82F6",
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.chat_display.tag_configure(
            "assistant",
            foreground="#10B981",
            font=("Microsoft YaHei UI", 11, "bold")
        )
        self.chat_display.tag_configure(
            "system",
            foreground="gray",
            font=("Microsoft YaHei UI", 10, "italic")
        )
        
        # 添加欢迎消息
        self._add_system_message("欢迎使用AI答题助手！我可以帮你理解题目、提供解题思路。")
    
    def _build_input_area(self, parent):
        """构建输入区域"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=X, pady=10)
        
        # 输入框
        self.input_text = ttk.Entry(
            input_frame,
            font=("Microsoft YaHei UI", 12)
        )
        self.input_text.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        # 绑定回车发送
        self.input_text.bind("<Return>", lambda e: self._send_message())
        
        # 发送按钮
        self.send_btn = ttk.Button(
            input_frame,
            text="发送",
            command=self._send_message,
            bootstyle="primary"
        )
        self.send_btn.pack(side=RIGHT)
    
    def _build_quick_buttons(self, parent):
        """构建快捷按钮区域"""
        quick_frame = ttk.LabelFrame(parent, text="💡 快捷操作", padding=5)
        quick_frame.pack(fill=X, pady=(5, 0))
        
        buttons = [
            ("📝 获取提示", self._get_hint),
            ("🔍 分析题目", self._analyze_question),
            ("💬 解释答案", self._explain_answer),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                quick_frame,
                text=text,
                command=command,
                bootstyle="info-outline"
            )
            btn.pack(side=LEFT, padx=5, pady=5)
    
    def _add_message(self, sender: str, message: str, tag: str = ""):
        """
        添加消息到聊天区域
        
        参数：
            sender: 发送者名称
            message: 消息内容
            tag: 文本标签
        """
        self.chat_display.config(state=tk.NORMAL)
        
        # 添加发送者
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        
        # 添加消息内容
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # 滚动到底部
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _add_system_message(self, message: str):
        """添加系统消息"""
        self._add_message("💡 系统", message, "system")
    
    def _add_user_message(self, message: str):
        """添加用户消息"""
        self._add_message("👤 你", message, "user")
    
    def _add_ai_message(self, message: str):
        """添加AI消息"""
        self._add_message("🤖 AI", message, "assistant")
    
    def _clear_chat(self):
        """清空聊天记录"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        if self.ai_service:
            self.ai_service.clear_history()
        
        self._add_system_message("对话已清空，可以开始新的对话。")
    
    def _on_model_change(self, event=None):
        """模型选择变化"""
        if not self.ai_service:
            return
        
        # 获取选中的模型
        selected_name = self.model_var.get()
        for name, model_id in self.AVAILABLE_MODELS:
            if name == selected_name:
                self.ai_service.config.model = model_id
                self._add_system_message(f"已切换到模型: {name}")
                break
    
    def _send_message(self):
        """发送消息"""
        message = self.input_text.get().strip()
        if not message:
            return
        
        if self.is_loading:
            return
        
        if not self.ai_service:
            self._add_system_message("AI服务未初始化，请检查API密钥配置。")
            return
        
        # 清空输入框
        self.input_text.delete(0, tk.END)
        
        # 显示用户消息
        self._add_user_message(message)
        
        # 禁用发送按钮
        self._set_loading(True)
        
        # 在后台线程发送请求
        def do_request():
            try:
                response = self.ai_service.chat(message)
                # 在主线程更新UI
                self.after(0, lambda: self._on_response(response))
            except Exception as e:
                error_msg = f"请求失败: {str(e)}"
                self.after(0, lambda: self._on_response(error_msg))
        
        thread = threading.Thread(target=do_request)
        thread.daemon = True
        thread.start()
    
    def _on_response(self, response: str):
        """收到AI响应的回调"""
        self._add_ai_message(response)
        self._set_loading(False)
    
    def _set_loading(self, loading: bool):
        """设置加载状态"""
        self.is_loading = loading
        if loading:
            self.send_btn.config(text="⏳ 思考中...", state=tk.DISABLED)
            self._add_system_message("AI正在思考，请稍候...")
        else:
            self.send_btn.config(text="发送", state=tk.NORMAL)
    
    def set_current_question(self, question: Question):
        """
        设置当前题目
        
        参数：
            question: 题目对象
        """
        self.current_question = question
        self.question_status.config(
            text=f"当前: {question.get_type_display()}",
            foreground="green"
        )
        
        # 清空之前的对话，为新题目准备
        if self.ai_service:
            self.ai_service.clear_history()
        
        self._add_system_message(f"已加载题目: {question.question[:50]}...")
    
    def _get_hint(self):
        """获取题目提示"""
        if not self.current_question:
            self._add_system_message("请先在主界面选择一道题目。")
            return
        
        if not self.ai_service:
            self._add_system_message("AI服务未初始化。")
            return
        
        if self.is_loading:
            return
        
        self._set_loading(True)
        
        def do_request():
            # 获取选项（如果有）
            options = None
            if hasattr(self.current_question, 'options'):
                options = self.current_question.options
            
            response = self.ai_service.get_hint(
                self.current_question.question,
                self.current_question.get_type_display(),
                options
            )
            self.after(0, lambda: self._on_response(response))
        
        thread = threading.Thread(target=do_request)
        thread.daemon = True
        thread.start()
    
    def _analyze_question(self):
        """分析当前题目"""
        if not self.current_question:
            self._add_system_message("请先在主界面选择一道题目。")
            return
        
        self._add_user_message("请帮我分析一下这道题目的考点和解题方向。")
        
        if self.ai_service and not self.is_loading:
            self._set_loading(True)
            
            def do_request():
                # 设置题目上下文
                options = None
                if hasattr(self.current_question, 'options'):
                    options = self.current_question.options
                
                self.ai_service.set_question_context(
                    self.current_question.question,
                    self.current_question.get_type_display(),
                    options
                )
                
                response = self.ai_service.chat(
                    "请分析这道题的考点、知识点，以及解题的思路方向。"
                )
                self.after(0, lambda: self._on_response(response))
            
            thread = threading.Thread(target=do_request)
            thread.daemon = True
            thread.start()
    
    def _explain_answer(self):
        """解释答案"""
        if not self.current_question:
            self._add_system_message("请先在主界面选择一道题目。")
            return
        
        self._add_user_message("请告诉我这道题的正确答案并详细解释。")
        
        if self.ai_service and not self.is_loading:
            self._set_loading(True)
            
            def do_request():
                # 获取答案
                answer = ""
                if hasattr(self.current_question, 'answer'):
                    answer = str(self.current_question.answer)
                
                explanation = self.current_question.explanation
                
                response = self.ai_service.explain_answer(
                    self.current_question.question,
                    answer,
                    explanation
                )
                self.after(0, lambda: self._on_response(response))
            
            thread = threading.Thread(target=do_request)
            thread.daemon = True
            thread.start()
