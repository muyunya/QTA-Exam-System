import PyInstaller.__main__
import os
import shutil

# 清理旧的构建文件
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# 准备临时构建目录（用于存放干净的数据文件）
if os.path.exists('build_temp'):
    shutil.rmtree('build_temp')
os.makedirs('build_temp/data/questions')
os.makedirs('build_temp/config')

# 复制题库文件（排除用户进度）
src_questions = 'data/questions'
dst_questions = 'build_temp/data/questions'
if os.path.exists(src_questions):
    for f in os.listdir(src_questions):
        if f.endswith('.json'):
            shutil.copy2(os.path.join(src_questions, f), dst_questions)

# 复制默认配置（排除settings.json，或者创建一个默认的）
# 这里我们不复制现有的settings.json，让程序生成默认的
# 或者如果有一个 default_settings.json 可以复制

# PyInstaller 参数
params = [
    'main.py',                      # 主程序入口
    '--name=QTA刷题软件',            # 生成的可执行文件名
    '--windowed',                   # 不显示控制台窗口 (GUI应用)
    '--onefile',                    # 打包成单个文件
    '--icon=NONE',                  # 暂时不使用图标
    '--clean',                      # 清理临时文件
    
    # 包含数据文件 (源路径;目标路径)
    '--add-data=build_temp/data;data',
    '--add-data=build_temp/config;config',
    '--add-data=src;src',
    
    # 收集 ttkbootstrap 的数据文件
    '--collect-all=ttkbootstrap',
    
    # 强制添加隐藏导入
    '--hidden-import=ttkbootstrap',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
]

try:
    print("开始打包...")
    PyInstaller.__main__.run(params)
    print("打包完成！可执行文件位于 dist/ 目录")
finally:
    # 清理临时目录
    if os.path.exists('build_temp'):
        shutil.rmtree('build_temp')
