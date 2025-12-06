# QTA 刷题软件

一个基于Python开发的现代化刷题训练软件，支持多种题型，具有代码高亮和实时运行功能。

## ✨ 功能特点

- 📝 **多种题型支持**
  - 单选题、多选题
  - 填空题
  - 判断题
  - 简答题
  - 编程题（支持Python代码实时运行验证）

- 🎨 **现代化界面**
  - 简洁美观的UI设计
  - 日间/夜间主题切换
  - 代码语法高亮

- 📊 **学习追踪**
  - 答题正确率统计
  - 学习时长记录
  - 错题本功能
  - 收藏夹功能

- ⌨️ **快捷键支持**
  - `1-5`: 快速选择选项
  - `Enter`: 提交答案
  - `←/→`: 切换题目
  - `Ctrl+O`: 打开题库
  - `Ctrl+T`: 切换主题

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Windows / macOS / Linux

### 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install ttkbootstrap pygments
```

### 运行程序

```bash
python main.py
```

## 📚 题库格式

题库使用JSON格式，示例结构如下：

```json
{
    "meta": {
        "name": "题库名称",
        "version": "1.0",
        "author": "作者",
        "description": "描述"
    },
    "questions": [
        {
            "id": 1,
            "type": "single_choice",
            "difficulty": "easy",
            "tags": ["标签1", "标签2"],
            "question": "题目内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "answer": "A",
            "explanation": "答案解析"
        }
    ]
}
```

### 支持的题目类型

| 类型 | type值 | 说明 |
|------|--------|------|
| 单选题 | `single_choice` | answer为单个字母 |
| 多选题 | `multi_choice` | answer为字母数组 |
| 填空题 | `fill_blank` | answer为答案数组 |
| 判断题 | `judge` | answer为true/false |
| 简答题 | `short_answer` | answer为参考答案文本 |
| 编程题 | `coding` | 包含code_template和test_cases |

详细格式说明请参考 `docs/题库格式说明.md`

## 📁 项目结构

```
QTA/
├── main.py              # 主程序入口
├── requirements.txt     # 依赖包列表
├── config/              # 配置文件
├── data/
│   ├── questions/       # 题库文件
│   └── user_progress.json
└── src/
    ├── models/          # 数据模型
    ├── views/           # 界面组件
    ├── controllers/     # 控制器
    └── utils/           # 工具函数
```

## 🎯 使用说明

1. 启动程序后，点击「打开题库」选择JSON题库文件
2. 选择练习模式（顺序/随机/错题/收藏）
3. 开始答题，提交答案后会显示结果和解析
4. 使用快捷键可以更高效地答题

## 📝 开发说明

如需自定义或扩展功能，请参考各模块的文档注释。

## 📄 许可证

MIT License
