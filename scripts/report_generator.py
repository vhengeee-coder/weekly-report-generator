import argparse
import json
import sys
import os
from datetime import datetime, timezone

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")
REPORTS_FILE = os.path.join(DATA_DIR, "reports.json")

TEMPLATES = {
    "simple": {
        "name": "简洁版",
        "sections": ["summary", "completed_tasks", "next_plan", "issues"]
    },
    "detailed": {
        "name": "详细版",
        "sections": ["summary", "completed_tasks", "ongoing_tasks", "issues", "solutions", "next_plan", "metrics"]
    },
    "okr": {
        "name": "OKR版",
        "sections": ["okr_progress", "key_results", "key_actions", "risks", "next_focus"]
    },
    "kpi": {
        "name": "KPI版",
        "sections": ["kpi_status", "data_comparison", "problem_analysis", "improvements"]
    }
}


def load_reports():
    if not os.path.exists(REPORTS_FILE):
        return {"reports": []}
    with open(REPORTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_reports(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_id(report_type):
    now = datetime.now(timezone.utc)
    return f"report_{now.strftime('%Y%m%d_%H%M%S')}"


def cmd_init(args):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REPORTS_FILE):
        save_reports({"reports": []})
        return {"success": True, "message": "初始化完成"}
    return {"success": True, "message": "数据文件已存在"}


def cmd_generate(args):
    report_type = args.type or "weekly"
    template_name = args.template or "detailed"
    template = TEMPLATES.get(template_name, TEMPLATES["detailed"])

    if args.json:
        try:
            raw_input = json.loads(args.json)
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"JSON解析失败: {str(e)}"}
    else:
        raw_input = {}

    now = datetime.now(timezone.utc)
    start_date = args.start or now.strftime("%Y-%m-%d")
    end_date = args.end or now.strftime("%Y-%m-%d")

    if report_type == "weekly":
        title = f"第{now.isocalendar()[1]}周工作周报"
    elif report_type == "daily":
        title = f"{now.strftime('%m月%d日')}工作日报"
    else:
        title = f"工作报告"

    content = {}
    for section in template["sections"]:
        if raw_input:
            if section == "completed_tasks" and "tasks" in raw_input:
                content[section] = raw_input["tasks"]
            elif section == "ongoing_tasks" and "ongoing" in raw_input:
                content[section] = raw_input["ongoing"]
            elif section == "issues" and "issues" in raw_input:
                content[section] = raw_input["issues"]
            elif section == "next_plan" and "next_plan" in raw_input:
                content[section] = raw_input["next_plan"]
            elif section == "summary" and "summary" in raw_input:
                content[section] = raw_input["summary"]
            else:
                content[section] = raw_input.get(section, [])
        else:
            content[section] = []

    report = {
        "id": generate_id(report_type),
        "type": report_type,
        "title": title,
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "created_at": now.isoformat(),
        "template": template_name,
        "content": content,
        "raw_input": raw_input
    }

    if raw_input:
        data = load_reports()
        data["reports"].append(report)
        save_reports(data)
        return {"success": True, "report": report, "message": "报告已生成并保存"}
    else:
        return {
            "success": True,
            "report": report,
            "template_info": {
                "name": template["name"],
                "sections": template["sections"]
            },
            "message": "请提供工作内容以填充报告模板",
            "interactive_prompt": "请提供以下信息：\n1. 本期完成了哪些工作？\n2. 有什么进行中的工作？\n3. 遇到了什么问题？\n4. 下期有什么计划？"
        }


def cmd_list(args):
    data = load_reports()
    reports = data.get("reports", [])
    report_type = args.type

    if report_type:
        reports = [r for r in reports if r.get("type") == report_type]

    result = []
    for r in reports:
        result.append({
            "id": r["id"],
            "type": r["type"],
            "title": r["title"],
            "date_range": r.get("date_range", {}),
            "created_at": r["created_at"],
            "template": r.get("template", "")
        })

    return {"success": True, "total": len(result), "reports": result}


def cmd_view(args):
    data = load_reports()
    report_id = args.id

    for r in data.get("reports", []):
        if r["id"] == report_id:
            return {"success": True, "report": r}

    return {"success": False, "error": f"报告不存在: {report_id}"}


def cmd_delete(args):
    data = load_reports()
    report_id = args.id
    original_len = len(data["reports"])
    data["reports"] = [r for r in data["reports"] if r["id"] != report_id]

    if len(data["reports"]) < original_len:
        save_reports(data)
        return {"success": True, "message": f"报告已删除: {report_id}"}

    return {"success": False, "error": f"报告不存在: {report_id}"}


def export_markdown(report):
    lines = []
    lines.append(f"# {report['title']}\n")
    dr = report.get("date_range", {})
    if dr:
        lines.append(f"**日期范围**: {dr.get('start', '')} ~ {dr.get('end', '')}\n")
    lines.append(f"**生成时间**: {report['created_at']}\n")

    content = report.get("content", {})
    section_titles = {
        "summary": "工作概述",
        "completed_tasks": "完成事项",
        "ongoing_tasks": "进行中事项",
        "issues": "问题与风险",
        "solutions": "解决方案",
        "next_plan": "下期计划",
        "metrics": "数据指标",
        "okr_progress": "OKR目标进度",
        "key_results": "关键结果",
        "key_actions": "关键行动",
        "risks": "风险与阻碍",
        "next_focus": "下期重点",
        "kpi_status": "KPI指标完成情况",
        "data_comparison": "数据对比分析",
        "problem_analysis": "问题分析",
        "improvements": "改进措施"
    }

    for section, title in section_titles.items():
        if section in content:
            lines.append(f"\n## {title}\n")
            items = content[section]
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        status = item.get("status", "")
                        progress = item.get("progress", "")
                        text = item.get("content", str(item))
                        line = f"- {text}"
                        if status:
                            line += f" [{status}]"
                        if progress:
                            line += f" (进度: {progress}%)"
                        lines.append(line)
                    else:
                        lines.append(f"- {item}")
            elif isinstance(items, str):
                lines.append(items)

    return "\n".join(lines)


def export_html(report):
    md = export_markdown(report)
    html_body = md.replace("\n", "<br>\n")
    html_body = html_body.replace("# ", "<h1>").replace("\n<h1>", "</h1>\n<h1>")
    html_body = html_body.replace("## ", "<h2>").replace("\n<h2>", "</h2>\n<h2>")
    html_body = html_body.replace("- ", "<li>").replace("\n<li>", "</li>\n<li>")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{report['title']}</title>
<style>body{{font-family:sans-serif;max-width:800px;margin:0 auto;padding:20px}}
h1{{color:#333}}h2{{color:#555;border-bottom:1px solid #eee;padding-bottom:5px}}
li{{margin:5px 0}}</style></head>
<body>{html_body}</body></html>"""


def cmd_export(args):
    data = load_reports()
    report_id = args.id
    fmt = args.format or "markdown"

    for r in data.get("reports", []):
        if r["id"] == report_id:
            if fmt == "markdown":
                content = export_markdown(r)
            elif fmt == "html":
                content = export_html(r)
            elif fmt == "text":
                content = export_markdown(r).replace("# ", "").replace("## ", "").replace("- ", "  • ")
            else:
                return {"success": False, "error": f"不支持的格式: {fmt}"}
            return {"success": True, "format": fmt, "content": content, "report_id": report_id}

    return {"success": False, "error": f"报告不存在: {report_id}"}


def cmd_template_list(args):
    result = []
    for key, val in TEMPLATES.items():
        result.append({
            "id": key,
            "name": val["name"],
            "sections": val["sections"]
        })
    return {"success": True, "templates": result}


def cmd_template_view(args):
    name = args.name
    if name in TEMPLATES:
        return {"success": True, "template": {"id": name, **TEMPLATES[name]}}
    return {"success": False, "error": f"模板不存在: {name}", "available": list(TEMPLATES.keys())}


def main():
    parser = argparse.ArgumentParser(description="周报/日报自动生成器")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")

    gen_p = subparsers.add_parser("generate")
    gen_p.add_argument("--type", choices=["weekly", "daily", "monthly"], default="weekly")
    gen_p.add_argument("--json", default=None)
    gen_p.add_argument("--template", choices=list(TEMPLATES.keys()), default="detailed")
    gen_p.add_argument("--start", default=None)
    gen_p.add_argument("--end", default=None)

    list_p = subparsers.add_parser("list")
    list_p.add_argument("--type", choices=["weekly", "daily", "monthly"], default=None)

    view_p = subparsers.add_parser("view")
    view_p.add_argument("--id", required=True)

    del_p = subparsers.add_parser("delete")
    del_p.add_argument("--id", required=True)

    exp_p = subparsers.add_parser("export")
    exp_p.add_argument("--id", required=True)
    exp_p.add_argument("--format", choices=["markdown", "html", "text"], default="markdown")

    tpl_p = subparsers.add_parser("template")
    tpl_sub = tpl_p.add_subparsers(dest="action")
    tpl_sub.add_parser("list")
    tpl_view = tpl_sub.add_parser("view")
    tpl_view.add_argument("--name", required=True)

    args = parser.parse_args()

    try:
        if args.command == "init":
            result = cmd_init(args)
        elif args.command == "generate":
            result = cmd_generate(args)
        elif args.command == "list":
            result = cmd_list(args)
        elif args.command == "view":
            result = cmd_view(args)
        elif args.command == "delete":
            result = cmd_delete(args)
        elif args.command == "export":
            result = cmd_export(args)
        elif args.command == "template":
            action = getattr(args, "action", None)
            if action == "list":
                result = cmd_template_list(args)
            elif action == "view":
                result = cmd_template_view(args)
            else:
                result = {"success": False, "error": "请指定模板操作: list / view"}
        else:
            parser.print_help()
            return

        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
