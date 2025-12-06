# -*- coding: utf-8 -*-
"""
统计视图模块
显示用户学习统计的详细信息
包含图表展示和数据分析
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Dict, List
from datetime import datetime, timedelta

from src.models.user_data import Statistics
from src.views.styles import (
    get_colors, get_font, QUESTION_TYPE_COLORS, DIFFICULTY_COLORS
)


class StatsView(ttkb.Toplevel):
    """
    统计视图窗口
    显示详细的学习统计数据
    """
    
    def __init__(self, parent, statistics: Statistics, is_dark: bool = True):
        """
        初始化统计视图
        
        参数：
            parent: 父窗口
            statistics: 统计数据对象
            is_dark: 是否暗色主题
        """
        super().__init__(parent)
        
        self.statistics = statistics
        self.is_dark = is_dark
        self.colors = get_colors(is_dark)
        
        # 窗口设置
        self.title("📊 学习统计")
        self.geometry("800x600")
        self.transient(parent)
        
        # 构建界面
        self._build_ui()
    
    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        ttk.Label(
            main_frame,
            text="📊 学习统计报告",
            font=get_font("cn_primary", "2xl", bold=True)
        ).pack(pady=(0, 20))
        
        # 概览卡片区域
        self._build_overview_cards(main_frame)
        
        # 详细统计区域
        detail_frame = ttk.Frame(main_frame)
        detail_frame.pack(fill=BOTH, expand=True, pady=20)
        
        # 左侧 - 题型统计
        left_frame = ttk.LabelFrame(detail_frame, text="📝 题型分布", padding=10)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self._build_type_stats(left_frame)
        
        # 右侧 - 近期记录
        right_frame = ttk.LabelFrame(detail_frame, text="📅 近7天记录", padding=10)
        right_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))
        self._build_daily_stats(right_frame)
        
        # 关闭按钮
        ttk.Button(
            main_frame,
            text="关闭",
            command=self.destroy,
            bootstyle="secondary-outline"
        ).pack(pady=10)
    
    def _build_overview_cards(self, parent):
        """构建概览卡片"""
        cards_frame = ttk.Frame(parent)
        cards_frame.pack(fill=X, pady=10)
        
        # 统计数据
        stats_data = [
            {
                "icon": "📚",
                "label": "答题总数",
                "value": str(self.statistics.total_questions),
                "color": "info"
            },
            {
                "icon": "✅",
                "label": "正确数",
                "value": str(self.statistics.correct_count),
                "color": "success"
            },
            {
                "icon": "❌",
                "label": "错误数",
                "value": str(self.statistics.wrong_count),
                "color": "danger"
            },
            {
                "icon": "🎯",
                "label": "正确率",
                "value": f"{self.statistics.accuracy:.1f}%",
                "color": "warning"
            },
            {
                "icon": "⏱️",
                "label": "学习时长",
                "value": self.statistics.total_time_display,
                "color": "primary"
            }
        ]
        
        for i, data in enumerate(stats_data):
            card = ttk.Frame(cards_frame)
            card.pack(side=LEFT, fill=X, expand=True, padx=5)
            
            # 图标
            ttk.Label(
                card,
                text=data["icon"],
                font=("Segoe UI Emoji", 24)
            ).pack()
            
            # 数值
            ttk.Label(
                card,
                text=data["value"],
                font=get_font("cn_primary", "xl", bold=True),
                bootstyle=data["color"]
            ).pack()
            
            # 标签
            ttk.Label(
                card,
                text=data["label"],
                font=get_font("cn_primary", "sm")
            ).pack()
    
    def _build_type_stats(self, parent):
        """构建题型统计"""
        type_stats = self.statistics.type_stats
        
        if not type_stats:
            ttk.Label(
                parent,
                text="暂无数据",
                font=get_font("cn_primary", "md")
            ).pack(pady=20)
            return
        
        # 题型名称映射
        type_names = {
            "single_choice": "单选题",
            "multi_choice": "多选题",
            "fill_blank": "填空题",
            "judge": "判断题",
            "short_answer": "简答题",
            "coding": "编程题"
        }
        
        for q_type, stats in type_stats.items():
            row = ttk.Frame(parent)
            row.pack(fill=X, pady=5)
            
            # 题型名称
            type_name = type_names.get(q_type, q_type)
            ttk.Label(
                row,
                text=type_name,
                font=get_font("cn_primary", "sm"),
                width=10
            ).pack(side=LEFT)
            
            # 进度条
            total = stats.get("correct", 0) + stats.get("wrong", 0)
            correct = stats.get("correct", 0)
            accuracy = (correct / total * 100) if total > 0 else 0
            
            progress = ttk.Progressbar(
                row,
                value=accuracy,
                maximum=100,
                length=150,
                bootstyle="success-striped"
            )
            progress.pack(side=LEFT, padx=10)
            
            # 数值
            ttk.Label(
                row,
                text=f"{correct}/{total} ({accuracy:.0f}%)",
                font=get_font("cn_primary", "sm")
            ).pack(side=LEFT)
    
    def _build_daily_stats(self, parent):
        """构建每日统计"""
        daily_stats = self.statistics.daily_stats
        
        if not daily_stats:
            ttk.Label(
                parent,
                text="暂无数据",
                font=get_font("cn_primary", "md")
            ).pack(pady=20)
            return
        
        # 获取最近7天的数据
        today = datetime.now()
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            day_name = date.strftime("%m/%d")
            
            row = ttk.Frame(parent)
            row.pack(fill=X, pady=3)
            
            # 日期
            ttk.Label(
                row,
                text=day_name,
                font=get_font("cn_primary", "sm"),
                width=8
            ).pack(side=LEFT)
            
            if date_str in daily_stats:
                stats = daily_stats[date_str]
                correct = stats.get("correct", 0)
                wrong = stats.get("wrong", 0)
                total = correct + wrong
                
                # 正确数（绿色）
                ttk.Label(
                    row,
                    text=f"✅ {correct}",
                    font=get_font("cn_primary", "sm"),
                    bootstyle="success"
                ).pack(side=LEFT, padx=10)
                
                # 错误数（红色）
                ttk.Label(
                    row,
                    text=f"❌ {wrong}",
                    font=get_font("cn_primary", "sm"),
                    bootstyle="danger"
                ).pack(side=LEFT)
            else:
                ttk.Label(
                    row,
                    text="- 无记录 -",
                    font=get_font("cn_primary", "sm"),
                    foreground="gray"
                ).pack(side=LEFT, padx=10)


class ProgressRing(tk.Canvas):
    """
    环形进度条组件
    用于显示正确率等百分比数据
    """
    
    def __init__(self, parent, size=100, thickness=10, 
                 value=0, max_value=100,
                 bg_color="#334155", fg_color="#10B981",
                 **kwargs):
        """
        初始化环形进度条
        
        参数：
            parent: 父组件
            size: 尺寸
            thickness: 环的粗细
            value: 当前值
            max_value: 最大值
            bg_color: 背景环颜色
            fg_color: 前景环颜色
        """
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, **kwargs)
        
        self.size = size
        self.thickness = thickness
        self.value = value
        self.max_value = max_value
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        self._draw()
    
    def _draw(self):
        """绘制环形进度条"""
        self.delete("all")
        
        # 计算座标
        pad = self.thickness / 2
        x0 = y0 = pad
        x1 = y1 = self.size - pad
        
        # 绘制背景环
        self.create_arc(
            x0, y0, x1, y1,
            start=90, extent=-360,
            style=tk.ARC,
            outline=self.bg_color,
            width=self.thickness
        )
        
        # 计算进度角度
        if self.max_value > 0:
            extent = -360 * (self.value / self.max_value)
        else:
            extent = 0
        
        # 绘制进度环
        self.create_arc(
            x0, y0, x1, y1,
            start=90, extent=extent,
            style=tk.ARC,
            outline=self.fg_color,
            width=self.thickness
        )
        
        # 显示百分比文字
        percentage = (self.value / self.max_value * 100) if self.max_value > 0 else 0
        self.create_text(
            self.size / 2, self.size / 2,
            text=f"{percentage:.0f}%",
            font=("Microsoft YaHei UI", 14, "bold"),
            fill=self.fg_color
        )
    
    def set_value(self, value: float):
        """
        设置进度值
        
        参数：
            value: 新的值
        """
        self.value = min(value, self.max_value)
        self._draw()
