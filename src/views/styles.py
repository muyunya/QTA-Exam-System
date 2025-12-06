# -*- coding: utf-8 -*-
"""
现代化样式模块
提供玻璃拟态(Glassmorphism)和其他现代UI效果的样式配置

玻璃拟态设计特点：
1. 半透明背景 + 模糊效果
2. 微妙的边框
3. 柔和的阴影
4. 鲜艳的渐变色
"""

# ============================================================
# 颜色方案配置
# ============================================================

# 暗色主题颜色
DARK_COLORS = {
    # 主色调
    "primary": "#6366F1",           # 靛蓝色 - 主按钮
    "primary_light": "#818CF8",     # 浅靛蓝
    "primary_dark": "#4F46E5",      # 深靛蓝
    
    # 成功/错误/警告
    "success": "#10B981",           # 翠绿色
    "success_light": "#34D399",
    "danger": "#EF4444",            # 红色
    "danger_light": "#F87171",
    "warning": "#F59E0B",           # 琥珀色
    "warning_light": "#FBBF24",
    "info": "#3B82F6",              # 蓝色
    
    # 背景色
    "bg_dark": "#0F172A",           # 最深背景
    "bg_medium": "#1E293B",         # 中等深度背景
    "bg_light": "#334155",          # 浅深色背景
    "bg_card": "rgba(30, 41, 59, 0.8)",  # 卡片背景（半透明）
    
    # 文字颜色
    "text_primary": "#F8FAFC",      # 主要文字
    "text_secondary": "#94A3B8",    # 次要文字
    "text_muted": "#64748B",        # 淡化文字
    
    # 边框
    "border": "#475569",            # 边框颜色
    "border_light": "rgba(255, 255, 255, 0.1)",  # 玻璃边框
    
    # 特效
    "glow_primary": "rgba(99, 102, 241, 0.5)",   # 主色发光
    "glow_success": "rgba(16, 185, 129, 0.5)",   # 成功发光
    "shadow": "rgba(0, 0, 0, 0.3)"               # 阴影
}

# 亮色主题颜色
LIGHT_COLORS = {
    # 主色调
    "primary": "#6366F1",
    "primary_light": "#818CF8",
    "primary_dark": "#4F46E5",
    
    # 成功/错误/警告
    "success": "#10B981",
    "success_light": "#34D399",
    "danger": "#EF4444",
    "danger_light": "#F87171",
    "warning": "#F59E0B",
    "warning_light": "#FBBF24",
    "info": "#3B82F6",
    
    # 背景色
    "bg_dark": "#F1F5F9",
    "bg_medium": "#F8FAFC",
    "bg_light": "#FFFFFF",
    "bg_card": "rgba(255, 255, 255, 0.8)",
    
    # 文字颜色
    "text_primary": "#1E293B",
    "text_secondary": "#475569",
    "text_muted": "#94A3B8",
    
    # 边框
    "border": "#CBD5E1",
    "border_light": "rgba(0, 0, 0, 0.1)",
    
    # 特效
    "glow_primary": "rgba(99, 102, 241, 0.3)",
    "glow_success": "rgba(16, 185, 129, 0.3)",
    "shadow": "rgba(0, 0, 0, 0.1)"
}


# ============================================================
# 渐变色配置
# ============================================================

GRADIENTS = {
    # 主题渐变
    "primary": ("#6366F1", "#8B5CF6"),        # 靛蓝到紫色
    "success": ("#10B981", "#14B8A6"),        # 绿到青色
    "danger": ("#EF4444", "#F97316"),         # 红到橙色
    "warning": ("#F59E0B", "#EAB308"),        # 琥珀渐变
    
    # 特殊渐变
    "purple_pink": ("#8B5CF6", "#EC4899"),    # 紫到粉
    "blue_cyan": ("#3B82F6", "#06B6D4"),      # 蓝到青
    "green_lime": ("#10B981", "#84CC16"),     # 绿到黄绿
    "sunset": ("#F97316", "#F43F5E"),         # 日落色
    
    # 背景渐变
    "dark_bg": ("#0F172A", "#1E293B"),        # 暗色背景渐变
    "light_bg": ("#F8FAFC", "#E2E8F0")        # 亮色背景渐变
}


# ============================================================
# 字体配置
# ============================================================

FONTS = {
    # 中文字体
    "cn_primary": "Microsoft YaHei UI",
    "cn_secondary": "SimHei",
    
    # 英文字体
    "en_primary": "Segoe UI",
    "en_secondary": "Arial",
    
    # 代码字体
    "code": "Consolas",
    "code_alt": "Courier New",
    
    # Emoji字体
    "emoji": "Segoe UI Emoji"
}

# 字体大小
FONT_SIZES = {
    "xs": 10,
    "sm": 12,
    "md": 14,
    "lg": 16,
    "xl": 18,
    "2xl": 24,
    "3xl": 30,
    "4xl": 36
}


# ============================================================
# 间距配置
# ============================================================

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
    "3xl": 64
}


# ============================================================
# 圆角配置
# ============================================================

BORDER_RADIUS = {
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "2xl": 24,
    "full": 9999
}


# ============================================================
# 题型颜色标签
# ============================================================

QUESTION_TYPE_COLORS = {
    "single_choice": {
        "bg": "#3B82F6",      # 蓝色
        "text": "#FFFFFF"
    },
    "multi_choice": {
        "bg": "#8B5CF6",      # 紫色
        "text": "#FFFFFF"
    },
    "fill_blank": {
        "bg": "#10B981",      # 绿色
        "text": "#FFFFFF"
    },
    "judge": {
        "bg": "#F59E0B",      # 琥珀色
        "text": "#FFFFFF"
    },
    "short_answer": {
        "bg": "#EC4899",      # 粉色
        "text": "#FFFFFF"
    },
    "coding": {
        "bg": "#6366F1",      # 靛蓝色
        "text": "#FFFFFF"
    }
}


# ============================================================
# 难度颜色标签
# ============================================================

DIFFICULTY_COLORS = {
    "easy": {
        "bg": "#10B981",      # 绿色
        "text": "#FFFFFF",
        "label": "简单"
    },
    "medium": {
        "bg": "#F59E0B",      # 琥珀色
        "text": "#FFFFFF",
        "label": "中等"
    },
    "hard": {
        "bg": "#EF4444",      # 红色
        "text": "#FFFFFF",
        "label": "困难"
    }
}


# ============================================================
# 动画配置
# ============================================================

ANIMATIONS = {
    "fast": 150,      # 快速动画 ms
    "normal": 300,    # 正常动画 ms
    "slow": 500       # 慢速动画 ms
}


# ============================================================
# 辅助函数
# ============================================================

def get_colors(is_dark: bool = True) -> dict:
    """
    获取当前主题的颜色配置
    
    参数：
        is_dark: 是否为暗色主题
        
    返回：
        dict: 颜色配置字典
    """
    return DARK_COLORS if is_dark else LIGHT_COLORS


def get_font(font_type: str = "cn_primary", size: str = "md", bold: bool = False) -> tuple:
    """
    获取字体配置元组
    
    参数：
        font_type: 字体类型
        size: 字体大小（xs/sm/md/lg/xl/2xl/3xl/4xl）
        bold: 是否粗体
        
    返回：
        tuple: (字体名称, 大小, 样式)
    """
    font_name = FONTS.get(font_type, FONTS["cn_primary"])
    font_size = FONT_SIZES.get(size, FONT_SIZES["md"])
    weight = "bold" if bold else "normal"
    
    return (font_name, font_size, weight)


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """
    将十六进制颜色转换为RGBA格式
    
    参数：
        hex_color: 十六进制颜色值
        alpha: 透明度 (0.0 - 1.0)
        
    返回：
        str: RGBA格式字符串
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return f"rgba({r}, {g}, {b}, {alpha})"
