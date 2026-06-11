---
name: weekly-report-generator
description: 自动生成周报/日报工具。根据用户提供的工作记录、任务完成情况、遇到的问题等信息，智能生成结构化的周报或日报。支持多种报告模板和格式。当用户需要写周报、日报、工作总结时触发。
---

# 周报/日报自动生成器

## 概述

本skill帮助用户自动生成结构化的周报或日报。用户只需提供工作内容、任务完成情况等原始信息，系统会智能整理并生成专业的报告文档。

**核心能力：**
- 支持周报、日报、月报等多种报告类型
- 多种报告模板可选（简洁版、详细版、OKR版、KPI版等）
- 智能提取关键信息和亮点
- 自动生成下周/明日工作计划建议
- 支持导出Markdown、HTML、纯文本格式
- 历史报告存储与查询

---

## 快速命令参考

所有操作通过 `scripts/report_generator.py` 脚本执行。

### 初始化
```bash
python scripts/report_generator.py init
```

### 生成报告
```bash
# 生成周报（交互式）
python scripts/report_generator.py generate --type weekly

# 生成日报
python scripts/report_generator.py generate --type daily

# 使用JSON数据生成
python scripts/report_generator.py generate --type weekly --json '{"tasks":[...],"issues":[...]}'

# 指定模板
python scripts/report_generator.py generate --type weekly --template detailed

# 指定日期范围
python scripts/report_generator.py generate --type weekly --start 2024-01-01 --end 2024-01-07
```

### 报告管理
```bash
# 列出历史报告
python scripts/report_generator.py list --type weekly

# 查看报告详情
python scripts/report_generator.py view --id report_xxx

# 删除报告
python scripts/report_generator.py delete --id report_xxx

# 导出报告
python scripts/report_generator.py export --id report_xxx --format markdown
```

### 模板管理
```bash
# 列出可用模板
python scripts/report_generator.py template list

# 查看模板详情
python scripts/report_generator.py template view --name simple
```

---

## 数据存储结构

```
data/
├── reports.json          # 报告存储文件
└── templates/            # 自定义模板目录
    └── custom_template.json
```

### reports.json 格式

```json
{
  "reports": [
    {
      "id": "report_20240107_weekly",
      "type": "weekly",
      "title": "第1周工作周报",
      "date_range": {
        "start": "2024-01-01",
        "end": "2024-01-07"
      },
      "created_at": "2024-01-07T18:00:00Z",
      "template": "detailed",
      "content": {
        "summary": "本周工作概述...",
        "completed_tasks": [...],
        "ongoing_tasks": [...],
        "issues": [...],
        "next_week_plan": [...]
      },
      "raw_input": {...}
    }
  ]
}
```

---

## 报告模板说明

### 1. 简洁版 (simple)
适用于快速汇报，包含：
- 本周完成事项
- 下周计划
- 需要协调的问题

### 2. 详细版 (detailed)
适用于正式汇报，包含：
- 工作概述
- 详细完成事项（含进度、成果）
- 进行中事项
- 遇到的问题及解决方案
- 下周详细计划
- 数据指标（如有）

### 3. OKR版 (okr)
适用于OKR管理，包含：
- OKR目标进度
- 关键结果完成情况
- 本周关键行动
- 风险与阻碍
- 下周重点

### 4. KPI版 (kpi)
适用于KPI考核，包含：
- KPI指标完成情况
- 数据对比分析
- 问题分析
- 改进措施

---

## 工作流程

### 流程一：交互式生成报告

```
用户: 帮我生成本周周报
AI: 📝 好的，让我帮您生成本周周报。
    请告诉我本周完成了哪些工作？（可以逐条描述）

用户: 1. 完成了用户登录模块的开发和测试
     2. 修复了3个线上bug
     3. 参加了2次技术评审会议

AI: 收到！请问有什么进行中但未完成的工作吗？

用户: 正在开发支付模块，进度60%

AI: 了解。本周有遇到什么问题或困难吗？

用户: 支付接口文档不完整，需要和第三方沟通

AI: 好的。请问下周有什么工作计划？

用户: 继续完成支付模块，开始订单模块设计

AI: ✅ 周报生成完成！

    📊 **第X周工作周报**
    
    ## 工作概述
    本周主要完成了用户登录模块的开发测试工作，修复了多个线上问题，
    并持续推进支付模块开发。
    
    ## 完成事项
    1. ✅ 完成用户登录模块开发和测试
    2. ✅ 修复3个线上bug
    3. ✅ 参加2次技术评审会议
    
    ## 进行中事项
    - 🔄 支付模块开发（进度60%）
    
    ## 问题与风险
    - ⚠️ 支付接口文档不完整，需与第三方沟通
    
    ## 下周计划
    1. 继续完成支付模块开发
    2. 开始订单模块设计
    
    ---
    是否需要保存此报告？(是/否)
```

### 流程二：快速生成（JSON输入）

```bash
python scripts/report_generator.py generate --type weekly --json '{
  "tasks": [
    {"content": "完成登录模块开发", "status": "completed", "progress": 100},
    {"content": "修复线上bug", "status": "completed", "count": 3}
  ],
  "ongoing": [
    {"content": "支付模块开发", "progress": 60}
  ],
  "issues": [
    {"content": "支付接口文档不完整", "impact": "medium"}
  ],
  "next_plan": [
    "继续完成支付模块",
    "开始订单模块设计"
  ]
}'
```

---

## 意图识别

| 意图 | 触发关键词 | 映射命令 |
|------|-----------|---------|
| 生成周报 | "写周报"、"生成周报"、"本周工作总结"、"帮我写周报" | `generate --type weekly` |
| 生成日报 | "写日报"、"生成日报"、"今天工作总结"、"日报" | `generate --type daily` |
| 查看历史 | "历史周报"、"之前的报告"、"上周周报" | `list` |
| 修改报告 | "修改周报"、"编辑报告" | `edit` |

---

## 错误处理

```
# 无工作内容
用户: 帮我写周报
AI: 📝 请提供本周的工作内容，我会帮您整理成周报。
    您可以告诉我：
    - 完成了哪些任务？
    - 有什么进行中的工作？
    - 遇到了什么问题？

# 日期格式错误
用户: 生成2024年1月的周报
AI: ⚠️ 请提供具体的日期范围。
    示例：生成2024-01-01到2024-01-07的周报
```

---

## 依赖

- Python >= 3.8
- 无需额外第三方库

## 许可证

MIT License
