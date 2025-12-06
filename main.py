# -*- coding: utf-8 -*-
"""
QTA 刷题软件 - 主程序入口

这是程序的入口文件，运行此文件启动刷题软件。
使用方法：python main.py

功能特点：
1. 支持多种题型：单选题、多选题、填空题、判断题、简答题、编程题
2. 代码语法高亮显示
3. 编程题实时运行验证
4. 错题本和收藏功能
5. 学习统计
6. 日间/夜间主题切换
7. 快捷键支持

作者：QTA
版本：1.0.0
"""

import sys
import os

# 将项目根目录添加到Python路径
# 这样可以正确导入src包下的模块
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """
    主函数
    创建并运行主窗口
    """
    try:
        # 导入主窗口类
        from src.views.main_window import MainWindow
        
        # 创建主窗口实例
        app = MainWindow()
        
        # 运行主循环
        app.run()
        
    except ImportError as e:
        # 导入错误，可能是依赖未安装
        print("=" * 50)
        print("错误：缺少必要的依赖包")
        print("=" * 50)
        print(f"详细信息：{e}")
        print()
        print("请运行以下命令安装依赖：")
        print("  pip install ttkbootstrap pygments")
        print()
        input("按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        # 其他错误
        print("=" * 50)
        print("程序运行出错")
        print("=" * 50)
        print(f"错误类型：{type(e).__name__}")
        print(f"错误信息：{e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        input("按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
