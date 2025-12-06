# -*- coding: utf-8 -*-
"""
代码运行器模块
用于执行Python代码并验证测试用例
注意：出于安全考虑，目前仅支持Python代码

安全措施：
1. 限制代码执行时间
2. 限制可用的内置函数
3. 捕获所有异常
"""

import sys
import io
import traceback
from typing import List, Tuple, Optional
from contextlib import redirect_stdout, redirect_stderr
import threading
import queue


# 代码执行超时时间（秒）
EXECUTION_TIMEOUT = 5


def run_python_code(code: str, input_data: str = "") -> Tuple[bool, str, str]:
    """
    执行Python代码
    
    参数：
        code: 要执行的Python代码
        input_data: 输入数据（会被设置为stdin）
        
    返回：
        Tuple[bool, str, str]: (是否成功, 标准输出, 错误信息)
        
    示例：
        >>> success, output, error = run_python_code("print(1 + 1)")
        >>> print(success, output)
        True 2
    """
    # 用于存储执行结果
    result_queue = queue.Queue()
    
    def execute():
        """在单独的线程中执行代码"""
        # 重定向标准输入输出
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            # 设置输入
            sys.stdin = io.StringIO(input_data)
            
            # 捕获输出
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # 创建受限的全局命名空间
            # 移除一些危险的内置函数
            safe_builtins = dict(__builtins__) if isinstance(__builtins__, dict) else dict(vars(__builtins__))
            
            # 移除危险函数
            dangerous_functions = [
                'eval', 'exec', 'compile', 'open', '__import__',
                'globals', 'locals', 'vars', 'dir',
                'getattr', 'setattr', 'delattr', 'hasattr',
                'exit', 'quit'
            ]
            for func in dangerous_functions:
                safe_builtins.pop(func, None)
            
            # 执行代码
            exec_globals = {"__builtins__": safe_builtins}
            exec(code, exec_globals)
            
            # 获取输出
            output = stdout_capture.getvalue()
            error = stderr_capture.getvalue()
            
            result_queue.put((True, output.strip(), error.strip()))
            
        except Exception as e:
            # 获取详细的错误信息
            error_msg = traceback.format_exc()
            result_queue.put((False, "", error_msg))
            
        finally:
            # 恢复标准输入输出
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    # 在线程中执行代码
    thread = threading.Thread(target=execute)
    thread.daemon = True
    thread.start()
    
    # 等待执行完成（设置超时）
    thread.join(timeout=EXECUTION_TIMEOUT)
    
    if thread.is_alive():
        # 超时
        return (False, "", f"代码执行超时（超过{EXECUTION_TIMEOUT}秒）")
    
    # 获取结果
    try:
        return result_queue.get_nowait()
    except queue.Empty:
        return (False, "", "执行异常：无法获取结果")


def validate_test_cases(code: str, test_cases: List[dict]) -> Tuple[bool, List[dict]]:
    """
    使用测试用例验证代码
    
    参数：
        code: 用户编写的代码
        test_cases: 测试用例列表，每个测试用例格式为:
                   {"input": "输入数据", "expected_output": "期望输出"}
        
    返回：
        Tuple[bool, List[dict]]: (是否全部通过, 测试结果列表)
        
        测试结果列表中每个元素格式：
        {
            "passed": bool,           # 是否通过
            "input": str,             # 输入
            "expected_output": str,   # 期望输出
            "actual_output": str,     # 实际输出
            "error": str              # 错误信息（如果有）
        }
        
    示例：
        >>> code = "n = int(input())\\nprint(sum(range(1, n+1)))"
        >>> test_cases = [{"input": "5", "expected_output": "15"}]
        >>> all_passed, results = validate_test_cases(code, test_cases)
    """
    results = []
    all_passed = True
    
    for tc in test_cases:
        input_data = tc.get("input", "")
        expected = tc.get("expected_output", "").strip()
        
        # 执行代码
        success, output, error = run_python_code(code, input_data)
        
        # 比较输出
        actual = output.strip()
        passed = success and (actual == expected)
        
        if not passed:
            all_passed = False
        
        results.append({
            "passed": passed,
            "input": input_data,
            "expected_output": expected,
            "actual_output": actual,
            "error": error if not success else ""
        })
    
    return (all_passed, results)


def run_code_with_function(code: str, function_name: str, 
                           test_cases: List[dict]) -> Tuple[bool, List[dict]]:
    """
    运行代码并调用指定函数进行测试
    适用于编程题中要求编写特定函数的情况
    
    参数：
        code: 用户编写的代码（包含函数定义）
        function_name: 要测试的函数名
        test_cases: 测试用例列表，每个测试用例格式为:
                   {"input": "函数参数", "expected_output": "期望返回值"}
        
    返回：
        Tuple[bool, List[dict]]: (是否全部通过, 测试结果列表)
    """
    results = []
    all_passed = True
    
    for tc in test_cases:
        input_data = tc.get("input", "")
        expected = tc.get("expected_output", "").strip()
        
        # 构建测试代码
        test_code = f"""
{code}

# 调用函数并打印结果
result = {function_name}({input_data})
print(result)
"""
        
        # 执行代码
        success, output, error = run_python_code(test_code)
        
        # 比较输出
        actual = output.strip()
        passed = success and (actual == expected)
        
        if not passed:
            all_passed = False
        
        results.append({
            "passed": passed,
            "input": f"{function_name}({input_data})",
            "expected_output": expected,
            "actual_output": actual,
            "error": error if not success else ""
        })
    
    return (all_passed, results)
