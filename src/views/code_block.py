# -*- coding: utf-8 -*-
"""
代码高亮展示组件模块
使用Pygments实现代码语法高亮
支持多种编程语言
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import get_formatter_by_name
from pygments.styles import get_style_by_name
from typing import Optional
import re


class CodeBlock(tk.Frame):
    """
    代码展示组件
    提供语法高亮的代码显示功能
    
    功能：
    - 支持多种编程语言的语法高亮
    - 显示行号
    - 代码复制功能
    - 支持编辑模式（用于编程题）
    """
    
    # 语言到Pygments lexer名称的映射
    LANGUAGE_MAP = {
        "python": "python",
        "py": "python",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "c++": "cpp",
        "javascript": "javascript",
        "js": "javascript",
        "html": "html",
        "css": "css",
        "sql": "sql",
        "json": "json",
        "xml": "xml",
        "bash": "bash",
        "shell": "bash"
    }
    
    # 语法高亮的颜色配置（适配暗色主题）
    # 这些颜色是根据Monokai风格定制的
    SYNTAX_COLORS = {
        "keyword": "#F92672",      # 关键字 - 粉红色
        "name": "#F8F8F2",         # 名称 - 白色
        "function": "#A6E22E",     # 函数名 - 绿色
        "class": "#66D9EF",        # 类名 - 青色
        "string": "#E6DB74",       # 字符串 - 黄色
        "number": "#AE81FF",       # 数字 - 紫色
        "comment": "#75715E",      # 注释 - 灰色
        "operator": "#F92672",     # 运算符 - 粉红色
        "decorator": "#F92672",    # 装饰器 - 粉红色
        "builtin": "#66D9EF",      # 内置函数 - 青色
        "background": "#272822",   # 背景色 - 深灰
        "text": "#F8F8F2",         # 默认文字 - 白色
        "line_number": "#75715E",  # 行号颜色 - 灰色
        "line_number_bg": "#2D2D2D"  # 行号背景色
    }
    
    def __init__(self, parent, code: str = "", language: str = "python",
                 editable: bool = False, height: int = 15, 
                 show_line_numbers: bool = True,
                 font_family: str = "Consolas", font_size: int = 16,
                 **kwargs):
        """
        初始化代码展示组件
        
        参数：
            parent: 父组件
            code: 要显示的代码
            language: 编程语言
            editable: 是否可编辑
            height: 显示高度（行数）
            show_line_numbers: 是否显示行号
            font_family: 字体名称
            font_size: 字体大小
        """
        super().__init__(parent, **kwargs)
        
        # 保存配置
        self.language = language.lower()
        self.editable = editable
        self.show_line_numbers = show_line_numbers
        self.font_family = font_family
        self.font_size = font_size
        
        # 配置样式
        self.configure(bg=self.SYNTAX_COLORS["background"])
        
        # 创建顶部工具栏
        self._create_toolbar()
        
        # 创建代码显示区域
        self._create_code_area(height)
        
        # 设置初始代码
        if code:
            self.set_code(code)
    
    def _create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = tk.Frame(self, bg=self.SYNTAX_COLORS["background"])
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # 语言标签
        lang_label = tk.Label(
            toolbar,
            text=self.language.upper(),
            fg=self.SYNTAX_COLORS["comment"],
            bg=self.SYNTAX_COLORS["background"],
            font=(self.font_family, self.font_size - 2)
        )
        lang_label.pack(side=tk.LEFT)
        
        # 复制按钮
        copy_btn = tk.Button(
            toolbar,
            text="📋 复制",
            command=self._copy_code,
            fg=self.SYNTAX_COLORS["text"],
            bg="#3D3D3D",
            activebackground="#4D4D4D",
            activeforeground=self.SYNTAX_COLORS["text"],
            relief=tk.FLAT,
            font=(self.font_family, self.font_size - 2),
            cursor="hand2"
        )
        copy_btn.pack(side=tk.RIGHT, padx=5)
    
    def _create_code_area(self, height: int):
        """创建代码显示区域"""
        # 容器Frame
        container = tk.Frame(self, bg=self.SYNTAX_COLORS["background"])
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 行号显示区域（如果启用）
        if self.show_line_numbers:
            self.line_numbers = tk.Text(
                container,
                width=4,
                height=height,
                bg=self.SYNTAX_COLORS["line_number_bg"],
                fg=self.SYNTAX_COLORS["line_number"],
                font=(self.font_family, self.font_size),
                state=tk.DISABLED,
                borderwidth=0,
                highlightthickness=0,
                padx=5,
                pady=5
            )
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # 代码文本区域
        self.code_text = tk.Text(
            container,
            height=height,
            bg=self.SYNTAX_COLORS["background"],
            fg=self.SYNTAX_COLORS["text"],
            font=(self.font_family, self.font_size),
            insertbackground=self.SYNTAX_COLORS["text"],  # 光标颜色
            selectbackground="#49483E",  # 选中背景色
            selectforeground=self.SYNTAX_COLORS["text"],
            borderwidth=0,
            highlightthickness=0,
            padx=10,
            pady=5,
            wrap=tk.NONE,  # 不自动换行
            undo=True  # 启用撤销功能
        )
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 如果不可编辑，禁用输入
        if not self.editable:
            self.code_text.config(state=tk.DISABLED)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(container, orient=tk.VERTICAL,
                                     command=self._on_scroll_y)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                     command=self.code_text.xview)
        scrollbar_x.pack(fill=tk.X)
        
        self.code_text.config(yscrollcommand=scrollbar_y.set,
                              xscrollcommand=scrollbar_x.set)
        
        # 绑定行号同步滚动
        if self.show_line_numbers:
            self.line_numbers.config(yscrollcommand=scrollbar_y.set)
        
        # 绑定内容变化事件（用于可编辑模式）
        if self.editable:
            self.code_text.bind("<KeyRelease>", self._on_content_change)
            self.code_text.bind("<Tab>", self._handle_tab)
        
        # 配置语法高亮的标签
        self._configure_tags()
    
    def _configure_tags(self):
        """配置语法高亮所需的文本标签"""
        self.code_text.tag_configure("keyword", foreground=self.SYNTAX_COLORS["keyword"])
        self.code_text.tag_configure("name", foreground=self.SYNTAX_COLORS["name"])
        self.code_text.tag_configure("function", foreground=self.SYNTAX_COLORS["function"])
        self.code_text.tag_configure("class", foreground=self.SYNTAX_COLORS["class"])
        self.code_text.tag_configure("string", foreground=self.SYNTAX_COLORS["string"])
        self.code_text.tag_configure("number", foreground=self.SYNTAX_COLORS["number"])
        self.code_text.tag_configure("comment", foreground=self.SYNTAX_COLORS["comment"])
        self.code_text.tag_configure("operator", foreground=self.SYNTAX_COLORS["operator"])
        self.code_text.tag_configure("decorator", foreground=self.SYNTAX_COLORS["decorator"])
        self.code_text.tag_configure("builtin", foreground=self.SYNTAX_COLORS["builtin"])
    
    def _on_scroll_y(self, *args):
        """处理垂直滚动，同步行号"""
        self.code_text.yview(*args)
        if self.show_line_numbers:
            self.line_numbers.yview(*args)
    
    def _handle_tab(self, event):
        """处理Tab键，插入4个空格而不是制表符"""
        self.code_text.insert(tk.INSERT, "    ")
        return "break"  # 阻止默认的Tab行为
    
    def _on_content_change(self, event=None):
        """内容变化时更新行号和语法高亮"""
        self._update_line_numbers()
        self._apply_syntax_highlighting()
    
    def _update_line_numbers(self):
        """更新行号显示"""
        if not self.show_line_numbers:
            return
        
        # 获取总行数
        content = self.code_text.get("1.0", tk.END)
        lines = content.count("\n")
        
        # 生成行号文本
        line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))
        
        # 更新行号显示
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)
    
    def _apply_syntax_highlighting(self):
        """应用语法高亮"""
        # 获取代码内容
        code = self.code_text.get("1.0", tk.END)
        
        # 清除所有现有标签
        for tag in ["keyword", "name", "function", "class", "string",
                    "number", "comment", "operator", "decorator", "builtin"]:
            self.code_text.tag_remove(tag, "1.0", tk.END)
        
        # 根据语言应用简单的正则高亮
        # 这里使用简化的规则，实际项目中可以使用Pygments进行更精确的高亮
        self._highlight_python(code)
    
    def _highlight_python(self, code: str):
        """为Python代码应用语法高亮"""
        # Python关键字
        keywords = [
            "and", "as", "assert", "async", "await", "break", "class",
            "continue", "def", "del", "elif", "else", "except", "False",
            "finally", "for", "from", "global", "if", "import", "in",
            "is", "lambda", "None", "nonlocal", "not", "or", "pass",
            "raise", "return", "True", "try", "while", "with", "yield"
        ]
        
        # Python内置函数
        builtins = [
            "abs", "all", "any", "bin", "bool", "bytes", "callable",
            "chr", "classmethod", "compile", "complex", "dict", "dir",
            "divmod", "enumerate", "eval", "exec", "filter", "float",
            "format", "frozenset", "getattr", "globals", "hasattr",
            "hash", "help", "hex", "id", "input", "int", "isinstance",
            "issubclass", "iter", "len", "list", "locals", "map", "max",
            "min", "next", "object", "oct", "open", "ord", "pow", "print",
            "property", "range", "repr", "reversed", "round", "set",
            "setattr", "slice", "sorted", "staticmethod", "str", "sum",
            "super", "tuple", "type", "vars", "zip"
        ]
        
        lines = code.split("\n")
        
        for line_num, line in enumerate(lines, start=1):
            # 高亮注释
            comment_match = re.search(r"#.*$", line)
            if comment_match:
                start = f"{line_num}.{comment_match.start()}"
                end = f"{line_num}.{comment_match.end()}"
                self.code_text.tag_add("comment", start, end)
            
            # 高亮字符串（简化处理）
            for match in re.finditer(r'(["\'])(?:(?!\1)[^\\]|\\.)*\1', line):
                # 检查是否在注释中
                if comment_match and match.start() >= comment_match.start():
                    continue
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.code_text.tag_add("string", start, end)
            
            # 高亮数字
            for match in re.finditer(r"\b\d+\.?\d*\b", line):
                if comment_match and match.start() >= comment_match.start():
                    continue
                start = f"{line_num}.{match.start()}"
                end = f"{line_num}.{match.end()}"
                self.code_text.tag_add("number", start, end)
            
            # 高亮关键字
            for keyword in keywords:
                pattern = rf"\b{keyword}\b"
                for match in re.finditer(pattern, line):
                    if comment_match and match.start() >= comment_match.start():
                        continue
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self.code_text.tag_add("keyword", start, end)
            
            # 高亮内置函数
            for builtin in builtins:
                pattern = rf"\b{builtin}\b(?=\()"
                for match in re.finditer(pattern, line):
                    if comment_match and match.start() >= comment_match.start():
                        continue
                    start = f"{line_num}.{match.start()}"
                    end = f"{line_num}.{match.end()}"
                    self.code_text.tag_add("builtin", start, end)
            
            # 高亮函数定义
            func_match = re.search(r"def\s+(\w+)", line)
            if func_match:
                start = f"{line_num}.{func_match.start(1)}"
                end = f"{line_num}.{func_match.end(1)}"
                self.code_text.tag_add("function", start, end)
            
            # 高亮类定义
            class_match = re.search(r"class\s+(\w+)", line)
            if class_match:
                start = f"{line_num}.{class_match.start(1)}"
                end = f"{line_num}.{class_match.end(1)}"
                self.code_text.tag_add("class", start, end)
            
            # 高亮装饰器
            decorator_match = re.search(r"(@\w+)", line)
            if decorator_match:
                start = f"{line_num}.{decorator_match.start()}"
                end = f"{line_num}.{decorator_match.end()}"
                self.code_text.tag_add("decorator", start, end)
    
    def set_code(self, code: str):
        """
        设置代码内容
        
        参数：
            code: 要显示的代码
        """
        # 如果是禁用状态，先启用
        was_disabled = self.code_text.cget("state") == tk.DISABLED
        if was_disabled:
            self.code_text.config(state=tk.NORMAL)
        
        # 清除并插入新代码
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", code)
        
        # 更新行号和语法高亮
        self._update_line_numbers()
        self._apply_syntax_highlighting()
        
        # 恢复禁用状态
        if was_disabled:
            self.code_text.config(state=tk.DISABLED)
    
    def get_code(self) -> str:
        """
        获取当前代码内容
        
        返回：
            str: 当前的代码文本
        """
        return self.code_text.get("1.0", tk.END).rstrip()
    
    def _copy_code(self):
        """复制代码到剪贴板"""
        code = self.get_code()
        self.clipboard_clear()
        self.clipboard_append(code)
        
        # 可以在这里添加复制成功的提示
        # 但为了简单起见，暂时不添加
    
    def set_editable(self, editable: bool):
        """
        设置是否可编辑
        
        参数：
            editable: 是否可编辑
        """
        self.editable = editable
        if editable:
            self.code_text.config(state=tk.NORMAL)
        else:
            self.code_text.config(state=tk.DISABLED)
    
    def clear(self):
        """清除代码内容"""
        self.set_code("")
