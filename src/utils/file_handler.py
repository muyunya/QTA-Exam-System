# -*- coding: utf-8 -*-
"""
文件处理工具模块
负责JSON题库加载、用户数据保存和读取等文件操作
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

# 导入数据模型
from src.models.question import Question, create_question_from_dict
from src.models.user_data import UserProgress


import sys
import shutil

def get_base_path() -> Path:
    """
    获取应用基础路径
    如果是打包环境，返回可执行文件所在目录
    如果是开发环境，返回项目根目录
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent

def get_resource_path(relative_path: str) -> Path:
    """
    获取资源文件路径（用于读取打包在exe内的文件）
    """
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.parent.parent
    return base_path / relative_path

def get_data_dir() -> Path:
    """
    获取数据目录路径
    优先使用用户目录下的data文件夹（可读写）
    """
    data_dir = get_base_path() / "data"
    
    # 如果数据目录不存在，且是打包环境，尝试从资源目录复制默认数据
    if not data_dir.exists() and getattr(sys, 'frozen', False):
        try:
            default_data = get_resource_path("data")
            if default_data.exists():
                shutil.copytree(default_data, data_dir)
        except Exception as e:
            print(f"复制默认数据失败: {e}")
            
    data_dir.mkdir(exist_ok=True)
    return data_dir

def get_questions_dir() -> Path:
    """
    获取题库文件目录路径
    """
    questions_dir = get_data_dir() / "questions"
    questions_dir.mkdir(exist_ok=True)
    return questions_dir

def get_config_dir() -> Path:
    """
    获取配置文件目录路径
    """
    config_dir = get_base_path() / "config"
    
    # 如果配置目录不存在，且是打包环境，尝试从资源目录复制
    if not config_dir.exists() and getattr(sys, 'frozen', False):
        try:
            default_config = get_resource_path("config")
            if default_config.exists():
                shutil.copytree(default_config, config_dir)
        except Exception as e:
            print(f"复制默认配置失败: {e}")
            
    config_dir.mkdir(exist_ok=True)
    return config_dir


def load_question_bank(file_path: str) -> tuple:
    """
    加载题库文件
    
    参数：
        file_path: 题库JSON文件路径（可以是绝对路径或相对于questions目录的相对路径）
        
    返回：
        tuple: (题目列表, 题库元信息字典)
        
    示例：
        >>> questions, meta = load_question_bank("sample.json")
        >>> print(meta["name"])
        "Python基础题库"
    """
    # 处理路径
    path = Path(file_path)
    
    # 如果不是绝对路径，则相对于questions目录
    if not path.is_absolute():
        path = get_questions_dir() / path
    
    # 检查文件是否存在
    if not path.exists():
        raise FileNotFoundError(f"题库文件不存在: {path}")
    
    # 读取JSON文件
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"题库文件格式错误: {e}")
    
    # 提取元信息
    meta = data.get("meta", {
        "name": path.stem,  # 使用文件名作为默认名称
        "version": "1.0",
        "author": "未知",
        "description": ""
    })
    
    # 将题目数据转换为题目对象
    questions = []
    for q_data in data.get("questions", []):
        try:
            question = create_question_from_dict(q_data)
            questions.append(question)
        except Exception as e:
            # 如果某道题解析失败，打印警告但继续处理其他题目
            print(f"警告: 解析题目 {q_data.get('id', '未知')} 失败: {e}")
    
    return questions, meta


def get_question_banks() -> List[Dict[str, Any]]:
    """
    获取所有可用的题库列表
    
    返回：
        List[Dict]: 题库信息列表，每个元素包含 {
            "file_name": 文件名,
            "file_path": 完整路径,
            "name": 题库名称,
            "question_count": 题目数量,
            "description": 描述
        }
    """
    questions_dir = get_questions_dir()
    banks = []
    
    # 遍历questions目录下的所有JSON文件
    for json_file in questions_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            meta = data.get("meta", {})
            questions = data.get("questions", [])
            
            banks.append({
                "file_name": json_file.name,
                "file_path": str(json_file),
                "name": meta.get("name", json_file.stem),
                "question_count": len(questions),
                "description": meta.get("description", "")
            })
        except Exception as e:
            # 如果某个文件读取失败，跳过
            print(f"警告: 读取题库 {json_file.name} 失败: {e}")
    
    return banks


def save_user_progress(progress: UserProgress, file_name: str = "user_progress.json"):
    """
    保存用户进度数据
    
    参数：
        progress: UserProgress对象
        file_name: 保存的文件名，默认为user_progress.json
    """
    file_path = get_data_dir() / file_name
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(progress.to_dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存用户进度失败: {e}")
        raise


def load_user_progress(file_name: str = "user_progress.json") -> UserProgress:
    """
    加载用户进度数据
    如果文件不存在，返回一个新的空UserProgress对象
    
    参数：
        file_name: 文件名，默认为user_progress.json
        
    返回：
        UserProgress: 用户进度对象
    """
    file_path = get_data_dir() / file_name
    
    # 如果文件不存在，返回新的空对象
    if not file_path.exists():
        return UserProgress()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return UserProgress.from_dict(data)
    except Exception as e:
        print(f"加载用户进度失败: {e}")
        # 如果加载失败，返回新的空对象
        return UserProgress()


def save_settings(settings: dict, file_name: str = "settings.json"):
    """
    保存应用设置
    
    参数：
        settings: 设置字典
        file_name: 文件名
    """
    file_path = get_config_dir() / file_name
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存设置失败: {e}")
        raise


def load_settings(file_name: str = "settings.json") -> dict:
    """
    加载应用设置
    如果文件不存在，返回默认设置
    
    参数：
        file_name: 文件名
        
    返回：
        dict: 设置字典
    """
    file_path = get_config_dir() / file_name
    
    # 默认设置
    default_settings = {
        "theme": "darkly",           # 默认暗色主题
        "font_size": 14,             # 默认字体大小
        "window_width": 1200,        # 窗口宽度
        "window_height": 800,        # 窗口高度
        "auto_save": True,           # 自动保存进度
        "show_explanation": True,    # 显示答案解析
        "code_font": "Consolas",     # 代码字体
        "code_font_size": 12,        # 代码字体大小
        "ai_api_key": "",            # AI API密钥（硅基流动）
        "ai_model": "Qwen/Qwen2.5-7B-Instruct" # 默认AI模型
    }
    
    if not file_path.exists():
        # 文件不存在，保存默认设置并返回
        save_settings(default_settings, file_name)
        return default_settings
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        
        # 合并默认设置（确保新增的设置项有默认值）
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        return settings
    except Exception as e:
        print(f"加载设置失败: {e}")
        return default_settings
