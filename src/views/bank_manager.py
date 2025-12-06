# -*- coding: utf-8 -*-
"""
题库管理模块
提供题库列表展示、创建和编辑功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from src.models.question import (
    Question, SingleChoiceQuestion, MultiChoiceQuestion,
    FillBlankQuestion, JudgeQuestion, ShortAnswerQuestion, CodingQuestion
)


class QuestionBankManager(ttkb.Toplevel):
    """
    题库管理窗口
    提供题库列表展示和管理功能
    """
    
    def __init__(self, parent, questions_dir: str, on_select_bank=None):
        """
        初始化题库管理器
        
        参数：
            parent: 父窗口
            questions_dir: 题库目录路径
            on_select_bank: 选择题库后的回调函数
        """
        super().__init__(parent)
        
        self.questions_dir = Path(questions_dir)
        self.on_select_bank = on_select_bank
        self.banks: List[Dict] = []
        
        # 窗口设置
        self.title("📚 题库管理")
        self.geometry("800x600")
        self.minsize(700, 500)
        
        # 构建界面
        self._build_ui()
        
        # 扫描题库
        self._scan_banks()
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 顶部工具栏
        self._build_toolbar(main_frame)
        
        # 题库列表
        self._build_bank_list(main_frame)
        
        # 底部操作栏
        self._build_bottom_bar(main_frame)
    
    def _build_toolbar(self, parent):
        """构建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=X, pady=(0, 10))
        
        # 标题
        ttk.Label(
            toolbar,
            text="📚 题库管理",
            font=("Microsoft YaHei UI", 16, "bold")
        ).pack(side=LEFT)
        
        # 刷新按钮
        ttk.Button(
            toolbar,
            text="🔄 刷新",
            command=self._scan_banks,
            bootstyle="secondary-outline"
        ).pack(side=RIGHT, padx=5)
        
        # 新建题库按钮
        ttk.Button(
            toolbar,
            text="➕ 新建题库",
            command=self._create_new_bank,
            bootstyle="success"
        ).pack(side=RIGHT, padx=5)
    
    def _build_bank_list(self, parent):
        """构建题库列表"""
        # 列表容器
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=BOTH, expand=True)
        
        # 创建Treeview
        columns = ("name", "questions", "author", "modified")
        self.bank_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # 设置列标题
        self.bank_tree.heading("name", text="题库名称")
        self.bank_tree.heading("questions", text="题目数量")
        self.bank_tree.heading("author", text="作者")
        self.bank_tree.heading("modified", text="修改时间")
        
        # 设置列宽
        self.bank_tree.column("name", width=250)
        self.bank_tree.column("questions", width=100, anchor=CENTER)
        self.bank_tree.column("author", width=150)
        self.bank_tree.column("modified", width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.bank_tree.yview)
        self.bank_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.bank_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 双击事件
        self.bank_tree.bind("<Double-1>", self._on_bank_double_click)
        
        # 阻止滚轮事件传播到父窗口
        def on_mousewheel(event):
            self.bank_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        self.bank_tree.bind("<MouseWheel>", on_mousewheel)
    
    def _build_bottom_bar(self, parent):
        """构建底部操作栏"""
        bottom = ttk.Frame(parent)
        bottom.pack(fill=X, pady=(10, 0))
        
        # 选择按钮
        ttk.Button(
            bottom,
            text="✓ 选择此题库",
            command=self._select_bank,
            bootstyle="primary"
        ).pack(side=LEFT, padx=5)
        
        # 编辑按钮
        ttk.Button(
            bottom,
            text="✏️ 编辑题库",
            command=self._edit_bank,
            bootstyle="info-outline"
        ).pack(side=LEFT, padx=5)
        
        # 删除按钮
        ttk.Button(
            bottom,
            text="🗑️ 删除",
            command=self._delete_bank,
            bootstyle="danger-outline"
        ).pack(side=RIGHT, padx=5)
        
        # 题库目录标签
        ttk.Label(
            bottom,
            text=f"📁 {self.questions_dir}",
            font=("Microsoft YaHei UI", 9),
            foreground="gray"
        ).pack(side=RIGHT, padx=20)
    
    def _scan_banks(self):
        """扫描题库目录"""
        # 清空列表
        for item in self.bank_tree.get_children():
            self.bank_tree.delete(item)
        
        self.banks = []
        
        # 确保目录存在
        if not self.questions_dir.exists():
            self.questions_dir.mkdir(parents=True)
            return
        
        # 扫描JSON文件
        for file_path in self.questions_dir.glob("*.json"):
            try:
                bank_info = self._load_bank_info(file_path)
                if bank_info:
                    self.banks.append(bank_info)
                    
                    # 添加到列表
                    self.bank_tree.insert("", "end", values=(
                        bank_info["name"],
                        bank_info["question_count"],
                        bank_info["author"],
                        bank_info["modified"]
                    ), tags=(str(file_path),))
                    
            except Exception as e:
                print(f"加载题库失败 {file_path}: {e}")
    
    def _load_bank_info(self, file_path: Path) -> Optional[Dict]:
        """
        加载题库基本信息
        
        参数：
            file_path: 题库文件路径
            
        返回：
            dict: 题库信息，加载失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证格式
            if "questions" not in data:
                return None
            
            meta = data.get("meta", {})
            
            # 获取修改时间
            mtime = os.path.getmtime(file_path)
            modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            
            return {
                "path": str(file_path),
                "name": meta.get("name", file_path.stem),
                "author": meta.get("author", "未知"),
                "description": meta.get("description", ""),
                "question_count": len(data.get("questions", [])),
                "modified": modified
            }
            
        except (json.JSONDecodeError, KeyError):
            return None
    
    def _get_selected_bank(self) -> Optional[Dict]:
        """获取当前选中的题库"""
        selection = self.bank_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        tags = self.bank_tree.item(item, "tags")
        
        if tags:
            path = tags[0]
            for bank in self.banks:
                if bank["path"] == path:
                    return bank
        
        return None
    
    def _on_bank_double_click(self, event):
        """双击题库"""
        self._select_bank()
    
    def _select_bank(self):
        """选择题库"""
        bank = self._get_selected_bank()
        if not bank:
            messagebox.showwarning("提示", "请先选择一个题库")
            return
        
        if self.on_select_bank:
            self.on_select_bank(bank["path"])
        
        self.destroy()
    
    def _create_new_bank(self):
        """创建新题库"""
        # 打开题库编辑器
        editor = QuestionBankEditor(self, self.questions_dir)
        editor.grab_set()
        self.wait_window(editor)
        
        # 刷新列表
        self._scan_banks()
    
    def _edit_bank(self):
        """编辑题库"""
        bank = self._get_selected_bank()
        if not bank:
            messagebox.showwarning("提示", "请先选择一个题库")
            return
        
        # 打开题库编辑器
        editor = QuestionBankEditor(self, self.questions_dir, bank["path"])
        editor.grab_set()
        self.wait_window(editor)
        
        # 刷新列表
        self._scan_banks()
    
    def _delete_bank(self):
        """删除题库"""
        bank = self._get_selected_bank()
        if not bank:
            messagebox.showwarning("提示", "请先选择一个题库")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除题库「{bank['name']}」吗？\n此操作不可恢复！"):
            try:
                os.remove(bank["path"])
                self._scan_banks()
                messagebox.showinfo("成功", "题库已删除")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败：{e}")


class QuestionBankEditor(ttkb.Toplevel):
    """
    题库编辑器
    用于创建和编辑题库
    """
    
    # 题目类型
    QUESTION_TYPES = [
        ("单选题", "single_choice"),
        ("多选题", "multi_choice"),
        ("填空题", "fill_blank"),
        ("判断题", "judge"),
        ("简答题", "short_answer"),
        ("编程题", "coding"),
    ]
    
    def __init__(self, parent, questions_dir: Path, bank_path: str = None):
        """
        初始化题库编辑器
        
        参数：
            parent: 父窗口
            questions_dir: 题库目录
            bank_path: 编辑的题库路径（新建时为None）
        """
        super().__init__(parent)
        
        self.questions_dir = questions_dir
        self.bank_path = bank_path
        self.is_new = bank_path is None
        
        # 题库数据
        self.meta = {"name": "", "author": "", "description": "", "version": "1.0"}
        self.questions: List[Dict] = []
        
        # 窗口设置
        self.title("✏️ 新建题库" if self.is_new else "✏️ 编辑题库")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # 加载现有数据
        if not self.is_new:
            self._load_bank()
        
        # 构建界面
        self._build_ui()
    
    def _load_bank(self):
        """加载题库数据"""
        try:
            with open(self.bank_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.meta = data.get("meta", self.meta)
            self.questions = data.get("questions", [])
            
        except Exception as e:
            messagebox.showerror("错误", f"加载题库失败：{e}")
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 顶部元数据区域
        self._build_meta_area(main_frame)
        
        # 中间题目列表和编辑区域
        middle = ttk.Frame(main_frame)
        middle.pack(fill=BOTH, expand=True, pady=10)
        
        # 左侧题目列表
        self._build_question_list(middle)
        
        # 右侧题目编辑区
        self._build_question_editor(middle)
        
        # 底部保存按钮
        self._build_save_bar(main_frame)
        
        # 刷新题目列表（在所有UI组件创建完成后）
        self._refresh_question_list()
    
    def _build_meta_area(self, parent):
        """构建元数据区域"""
        meta_frame = ttk.LabelFrame(parent, text="📋 题库信息", padding=10)
        meta_frame.pack(fill=X, pady=(0, 10))
        
        # 题库名称
        row1 = ttk.Frame(meta_frame)
        row1.pack(fill=X, pady=2)
        
        ttk.Label(row1, text="名称:", width=8).pack(side=LEFT)
        self.name_entry = ttk.Entry(row1, width=30)
        self.name_entry.pack(side=LEFT, padx=5)
        self.name_entry.insert(0, self.meta.get("name", ""))
        
        ttk.Label(row1, text="作者:", width=8).pack(side=LEFT, padx=(20, 0))
        self.author_entry = ttk.Entry(row1, width=20)
        self.author_entry.pack(side=LEFT, padx=5)
        self.author_entry.insert(0, self.meta.get("author", ""))
        
        # 描述
        row2 = ttk.Frame(meta_frame)
        row2.pack(fill=X, pady=2)
        
        ttk.Label(row2, text="描述:", width=8).pack(side=LEFT)
        self.desc_entry = ttk.Entry(row2, width=70)
        self.desc_entry.pack(side=LEFT, padx=5, fill=X, expand=True)
        self.desc_entry.insert(0, self.meta.get("description", ""))
    
    def _build_question_list(self, parent):
        """构建题目列表"""
        left_frame = ttk.LabelFrame(parent, text="📝 题目列表", padding=5)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        # 工具栏
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=X, pady=(0, 5))
        
        ttk.Button(
            toolbar,
            text="➕ 添加题目",
            command=self._add_question,
            bootstyle="success-outline"
        ).pack(side=LEFT, padx=2)
        
        ttk.Button(
            toolbar,
            text="🗑️ 删除",
            command=self._delete_question,
            bootstyle="danger-outline"
        ).pack(side=LEFT, padx=2)
        
        # 题目列表
        columns = ("id", "type", "preview")
        self.question_tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15
        )
        
        self.question_tree.heading("id", text="ID")
        self.question_tree.heading("type", text="类型")
        self.question_tree.heading("preview", text="题目预览")
        
        self.question_tree.column("id", width=40)
        self.question_tree.column("type", width=70)
        self.question_tree.column("preview", width=200)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=VERTICAL, command=self.question_tree.yview)
        self.question_tree.configure(yscrollcommand=scrollbar.set)
        
        self.question_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 绑定选择事件
        self.question_tree.bind("<<TreeviewSelect>>", self._on_question_select)
        
        # 阻止滚轮事件传播到父窗口
        def on_mousewheel(event):
            self.question_tree.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        self.question_tree.bind("<MouseWheel>", on_mousewheel)
    
    def _build_question_editor(self, parent):
        """构建题目编辑区"""
        right_frame = ttk.LabelFrame(parent, text="✏️ 编辑题目", padding=10)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        
        # 题目类型
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(fill=X, pady=5)
        
        ttk.Label(type_frame, text="类型:").pack(side=LEFT)
        self.type_var = tk.StringVar(value="single_choice")
        self.type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=[t[0] for t in self.QUESTION_TYPES],
            state="readonly",
            width=15
        )
        self.type_combo.pack(side=LEFT, padx=5)
        self.type_combo.current(0)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)
        
        # 难度
        ttk.Label(type_frame, text="难度:").pack(side=LEFT, padx=(20, 0))
        self.diff_var = tk.StringVar(value="easy")
        diff_combo = ttk.Combobox(
            type_frame,
            textvariable=self.diff_var,
            values=["easy", "medium", "hard"],
            state="readonly",
            width=10
        )
        diff_combo.pack(side=LEFT, padx=5)
        diff_combo.current(0)
        
        # 题目内容
        ttk.Label(right_frame, text="题目内容:").pack(anchor=W, pady=(10, 2))
        self.question_text = tk.Text(right_frame, height=4, wrap=tk.WORD)
        self.question_text.pack(fill=X, pady=2)
        
        # 选项区域（单选/多选）
        self.options_frame = ttk.LabelFrame(right_frame, text="选项", padding=5)
        self.options_frame.pack(fill=X, pady=5)
        
        self.option_entries = []
        for i in range(4):
            frame = ttk.Frame(self.options_frame)
            frame.pack(fill=X, pady=1)
            ttk.Label(frame, text=f"{chr(65+i)}.", width=3).pack(side=LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=LEFT, fill=X, expand=True, padx=2)
            self.option_entries.append(entry)
        
        # 答案
        answer_frame = ttk.Frame(right_frame)
        answer_frame.pack(fill=X, pady=5)
        
        ttk.Label(answer_frame, text="答案:").pack(side=LEFT)
        self.answer_entry = ttk.Entry(answer_frame, width=30)
        self.answer_entry.pack(side=LEFT, padx=5)
        
        ttk.Label(answer_frame, text="(单选填A/B/C/D，多选填AB/ABC等)", foreground="gray").pack(side=LEFT)
        
        # 解析
        ttk.Label(right_frame, text="解析:").pack(anchor=W, pady=(10, 2))
        self.explanation_text = tk.Text(right_frame, height=3, wrap=tk.WORD)
        self.explanation_text.pack(fill=X, pady=2)
        
        # 保存当前题目按钮
        ttk.Button(
            right_frame,
            text="💾 保存此题",
            command=self._save_current_question,
            bootstyle="primary"
        ).pack(pady=10)
        
        # 当前编辑的题目索引
        self.current_question_index = -1
    
    def _build_save_bar(self, parent):
        """构建保存栏"""
        save_frame = ttk.Frame(parent)
        save_frame.pack(fill=X, pady=(10, 0))
        
        ttk.Button(
            save_frame,
            text="💾 保存题库",
            command=self._save_bank,
            bootstyle="success"
        ).pack(side=LEFT, padx=5)
        
        ttk.Button(
            save_frame,
            text="取消",
            command=self.destroy,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=5)
        
        # 题目统计
        self.stats_label = ttk.Label(
            save_frame,
            text=f"共 {len(self.questions)} 道题目",
            font=("Microsoft YaHei UI", 10)
        )
        self.stats_label.pack(side=RIGHT, padx=10)
    
    def _refresh_question_list(self):
        """刷新题目列表"""
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        
        type_names = {t[1]: t[0] for t in self.QUESTION_TYPES}
        
        for i, q in enumerate(self.questions):
            q_type = type_names.get(q.get("type", ""), q.get("type", ""))
            preview = q.get("question", "")[:30] + "..." if len(q.get("question", "")) > 30 else q.get("question", "")
            
            self.question_tree.insert("", "end", values=(
                q.get("id", i + 1),
                q_type,
                preview
            ))
        
        self.stats_label.configure(text=f"共 {len(self.questions)} 道题目")
    
    def _on_question_select(self, event):
        """选择题目"""
        selection = self.question_tree.selection()
        if not selection:
            return
        
        # 获取索引
        item = selection[0]
        index = self.question_tree.index(item)
        
        if 0 <= index < len(self.questions):
            self._load_question_to_editor(index)
    
    def _load_question_to_editor(self, index: int):
        """加载题目到编辑器"""
        # 检查UI组件是否已创建
        if not hasattr(self, 'type_combo'):
            return
            
        self.current_question_index = index
        q = self.questions[index]
        
        # 设置类型
        type_names = {t[1]: t[0] for t in self.QUESTION_TYPES}
        q_type = q.get("type", "single_choice")
        if q_type in type_names:
            self.type_combo.set(type_names[q_type])
        
        # 设置难度
        self.diff_var.set(q.get("difficulty", "easy"))
        
        # 设置题目内容
        self.question_text.delete("1.0", tk.END)
        self.question_text.insert("1.0", q.get("question", ""))
        
        # 设置选项
        options = q.get("options", [])
        for i, entry in enumerate(self.option_entries):
            entry.delete(0, tk.END)
            if i < len(options):
                entry.insert(0, options[i])
        
        # 设置答案
        self.answer_entry.delete(0, tk.END)
        answer = q.get("answer", "")
        if isinstance(answer, list):
            self.answer_entry.insert(0, "".join(answer))
        elif isinstance(answer, bool):
            self.answer_entry.insert(0, "true" if answer else "false")
        else:
            self.answer_entry.insert(0, str(answer))
        
        # 设置解析
        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.insert("1.0", q.get("explanation", ""))
    
    def _on_type_change(self, event=None):
        """题目类型变化"""
        # 可以根据类型显示/隐藏不同的输入区域
        pass
    
    def _add_question(self):
        """添加新题目"""
        new_id = len(self.questions) + 1
        new_question = {
            "id": new_id,
            "type": "single_choice",
            "question": "新题目",
            "options": ["A. ", "B. ", "C. ", "D. "],
            "answer": "A",
            "difficulty": "easy",
            "explanation": ""
        }
        
        self.questions.append(new_question)
        self._refresh_question_list()
        
        # 选中新题目
        children = self.question_tree.get_children()
        if children:
            self.question_tree.selection_set(children[-1])
            self._load_question_to_editor(len(self.questions) - 1)
    
    def _delete_question(self):
        """删除题目"""
        if self.current_question_index < 0:
            messagebox.showwarning("提示", "请先选择一道题目")
            return
        
        if messagebox.askyesno("确认", "确定删除此题目吗？"):
            del self.questions[self.current_question_index]
            self.current_question_index = -1
            self._refresh_question_list()
    
    def _save_current_question(self):
        """保存当前编辑的题目"""
        if self.current_question_index < 0:
            messagebox.showwarning("提示", "请先选择或添加一道题目")
            return
        
        # 获取类型
        type_map = {t[0]: t[1] for t in self.QUESTION_TYPES}
        q_type = type_map.get(self.type_combo.get(), "single_choice")
        
        # 构建题目数据
        question = {
            "id": self.current_question_index + 1,
            "type": q_type,
            "question": self.question_text.get("1.0", tk.END).strip(),
            "difficulty": self.diff_var.get(),
            "explanation": self.explanation_text.get("1.0", tk.END).strip()
        }
        
        # 根据类型处理选项和答案
        if q_type in ["single_choice", "multi_choice"]:
            options = []
            for entry in self.option_entries:
                opt = entry.get().strip()
                if opt:
                    options.append(opt)
            question["options"] = options
            
            answer = self.answer_entry.get().strip().upper()
            if q_type == "multi_choice":
                question["answer"] = list(answer)
            else:
                question["answer"] = answer
        
        elif q_type == "judge":
            answer = self.answer_entry.get().strip().lower()
            question["answer"] = answer in ["true", "1", "正确", "对"]
        
        elif q_type == "fill_blank":
            answer = self.answer_entry.get().strip()
            question["answer"] = [a.strip() for a in answer.split("|")]
        
        else:
            question["answer"] = self.answer_entry.get().strip()
        
        # 更新题目
        self.questions[self.current_question_index] = question
        self._refresh_question_list()
        
        messagebox.showinfo("成功", "题目已保存")
    
    def _save_bank(self):
        """保存题库"""
        # 获取元数据
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入题库名称")
            return
        
        self.meta["name"] = name
        self.meta["author"] = self.author_entry.get().strip()
        self.meta["description"] = self.desc_entry.get().strip()
        
        # 构建数据
        data = {
            "meta": self.meta,
            "questions": self.questions
        }
        
        # 确定保存路径
        if self.is_new:
            # 新建：用名称作为文件名
            filename = f"{name}.json"
            save_path = self.questions_dir / filename
        else:
            save_path = Path(self.bank_path)
        
        # 保存
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"题库已保存到：{save_path}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")
