# -*- coding: utf-8 -*-
"""
AI服务模块
调用硅基流动(SiliconFlow) API实现AI答题助手功能

硅基流动API兼容OpenAI格式，使用REST API调用
"""

import requests
import json
from typing import Optional, List, Dict, Generator
from dataclasses import dataclass


@dataclass
class AIConfig:
    """
    AI服务配置类
    
    属性：
        api_key: API密钥
        base_url: API基础URL
        model: 使用的模型名称
        max_tokens: 最大生成token数
        temperature: 温度参数（0-2，越高越随机）
    """
    api_key: str = ""
    base_url: str = "https://api.siliconflow.cn/v1"
    model: str = "Qwen/Qwen2.5-7B-Instruct"  # 默认使用通义千问模型
    max_tokens: int = 1024
    temperature: float = 0.7


class AIService:
    """
    AI服务类
    提供与硅基流动API交互的功能
    """
    
    # 系统提示词 - 定义AI助手的角色和行为
    SYSTEM_PROMPT = """你是一个专业的编程学习助手，专门帮助用户理解和解答编程相关的题目。

你的任务是：
1. 帮助用户理解题目的含义
2. 提供解题思路和提示，但不直接给出完整答案
3. 解释相关的编程概念
4. 如果用户坚持要答案，可以给出详细解释

回答时请：
- 使用简洁清晰的中文
- 对于代码，使用markdown代码块格式
- 循序渐进地引导用户思考
- 鼓励用户自己尝试"""
    
    def __init__(self, config: AIConfig):
        """
        初始化AI服务
        
        参数：
            config: AI配置对象
        """
        self.config = config
        self.conversation_history: List[Dict[str, str]] = []
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def set_question_context(self, question_text: str, question_type: str, 
                            options: Optional[List[str]] = None):
        """
        设置当前题目上下文
        这会在对话开始时告诉AI当前正在做什么题
        
        参数：
            question_text: 题目内容
            question_type: 题目类型
            options: 选项列表（如果有）
        """
        # 清空之前的对话
        self.clear_history()
        
        # 构建题目上下文
        context = f"当前题目类型：{question_type}\n\n题目内容：\n{question_text}"
        
        if options:
            context += "\n\n选项：\n" + "\n".join(options)
        
        # 添加到对话历史
        self.conversation_history.append({
            "role": "user",
            "content": f"我正在做一道编程题，请帮我分析一下这道题：\n\n{context}"
        })
    
    def chat(self, user_message: str) -> str:
        """
        发送消息并获取AI回复
        
        参数：
            user_message: 用户消息
            
        返回：
            str: AI的回复
        """
        # 添加用户消息到历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # 构建请求
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建消息列表，包含系统提示
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.conversation_history
            
            data = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "stream": False
            }
            
            # 发送请求
            response = requests.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API请求失败: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = f"API错误: {error_data['error'].get('message', '未知错误')}"
                except:
                    pass
                return error_msg
            
            # 解析响应
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # 添加AI回复到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试"
        except requests.exceptions.ConnectionError:
            return "网络连接失败，请检查网络"
        except Exception as e:
            return f"发生错误: {str(e)}"
    
    def get_hint(self, question_text: str, question_type: str,
                options: Optional[List[str]] = None) -> str:
        """
        获取题目提示（快捷方法）
        自动设置上下文并请求提示
        
        参数：
            question_text: 题目内容
            question_type: 题目类型
            options: 选项列表
            
        返回：
            str: AI给出的提示
        """
        self.set_question_context(question_text, question_type, options)
        return self.chat("请给我一些解题提示，帮助我理解这道题，但不要直接告诉我答案。")
    
    def explain_answer(self, question_text: str, correct_answer: str,
                      explanation: str = "") -> str:
        """
        解释答案（答题后使用）
        
        参数：
            question_text: 题目内容
            correct_answer: 正确答案
            explanation: 原有的解析
            
        返回：
            str: AI的详细解释
        """
        prompt = f"""请帮我详细解释这道题：

题目：{question_text}

正确答案：{correct_answer}

{f'原解析：{explanation}' if explanation else ''}

请用通俗易懂的方式解释为什么这个答案是正确的，以及相关的知识点。"""
        
        self.clear_history()
        return self.chat(prompt)


def create_ai_service(api_key: str) -> AIService:
    """
    创建AI服务实例的便捷函数
    
    参数：
        api_key: API密钥
        
    返回：
        AIService: AI服务实例
    """
    config = AIConfig(api_key=api_key)
    return AIService(config)
