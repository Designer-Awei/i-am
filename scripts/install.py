#!/usr/bin/env python3
"""
i-am Skill Installer

Asks user to choose automation mode:
1. Scheduled (Default) - Auto analysis twice daily (2:30 AM & 2:30 PM)
2. Manual - Run analysis on-demand
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

def print_banner():
    print("="*60)
    print("🧠 i-am Skill Installer / 安装程序")
    print("="*60)
    print()

def ask_mode():
    print("Choose automation mode / 选择自动化模式:")
    print()
    print("  1) Scheduled Mode (Default, Recommended) / 定时模式（默认，推荐）")
    print("     - Automatic analysis twice daily (2:30 AM & 2:30 PM)")
    print("       每天自动分析两次（凌晨 2:30 和下午 2:30）")
    print("     - Uses OpenClaw cron system")
    print("       使用 OpenClaw 定时任务系统")
    print("     - ACT-R + Grounded Theory in one run")
    print("       ACT-R + 扎根理论合并执行")
    print()
    print("  2) Manual Mode / 手动模式")
    print("     - Run analysis when you want updates")
    print("       需要时手动运行分析")
    print("     - No background processes")
    print("       无后台进程")
    print("     - Full control")
    print("       完全控制")
    print()
    
    while True:
        choice = input("Enter choice [1/2] (default: 1): ").strip()
        if not choice:
            return 1  # Default to scheduled mode
        try:
            mode = int(choice)
            if mode in [1, 2]:
                return mode
        except:
            pass
        print("Invalid choice / 无效选择。Please enter 1 or 2 / 请输入 1 或 2。")

def setup_scheduled_mode():
    """Configure OpenClaw cron tasks for twice daily analysis (2:30 AM & 2:30 PM)"""
    print("\n⚙️  Setting up scheduled mode (twice daily at 2:30 AM & 2:30 PM)...")
    print("   配置定时模式（每天凌晨 2:30 和下午 2:30 各执行一次）...")
    
    cron_tasks_path = Path.home() / ".openclaw" / "cron" / "cron-tasks.json"
    
    # Load existing tasks
    if cron_tasks_path.exists():
        with open(cron_tasks_path, 'r', encoding='utf-8') as f:
            cron_data = json.load(f)
    else:
        cron_data = {"jobs": []}
    
    # Check if i-am tasks already exist
    task_ids = ["i-am-morning-analysis", "i-am-afternoon-analysis"]
    existing = [job for job in cron_data.get("jobs", []) if job.get("id") in task_ids]
    
    if existing:
        print(f"  ℹ️  Scheduled tasks already exist, skipping...")
        print(f"  ℹ️  定时任务已存在，跳过配置...")
        return
    
    # Add morning task (2:30 AM)
    morning_task = {
        "id": "i-am-morning-analysis",
        "name": "i-am Morning Personality Analysis",
        "description": "Analyze OpenClaw sessions and update USER.md daily at 2:30 AM using ACT-R + Grounded Theory",
        "enabled": True,
        "createdAtMs": int(datetime.now().timestamp() * 1000),
        "updatedAtMs": int(datetime.now().timestamp() * 1000),
        "schedule": {
            "kind": "cron",
            "expr": "30 2 * * *",  # Daily at 2:30 AM
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "main",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "Run i-am morning analysis: cd ~/.openclaw/workspace/skills/i-am && python3 scripts/i_am_daily_analysis.py && echo 'Morning analysis complete, USER.md updated'"
        },
        "state": {
            "nextRunAtMs": int(datetime.now().timestamp() * 1000) + 24 * 3600 * 1000
        }
    }
    
    # Add afternoon task (2:30 PM)
    afternoon_task = {
        "id": "i-am-afternoon-analysis",
        "name": "i-am Afternoon Personality Analysis",
        "description": "Analyze OpenClaw sessions and update USER.md daily at 2:30 PM using ACT-R + Grounded Theory",
        "enabled": True,
        "createdAtMs": int(datetime.now().timestamp() * 1000),
        "updatedAtMs": int(datetime.now().timestamp() * 1000),
        "schedule": {
            "kind": "cron",
            "expr": "30 14 * * *",  # Daily at 2:30 PM
            "tz": "Asia/Shanghai"
        },
        "sessionTarget": "main",
        "wakeMode": "now",
        "payload": {
            "kind": "agentTurn",
            "message": "Run i-am afternoon analysis: cd ~/.openclaw/workspace/skills/i-am && python3 scripts/i_am_daily_analysis.py && echo 'Afternoon analysis complete, USER.md updated'"
        },
        "state": {
            "nextRunAtMs": int(datetime.now().timestamp() * 1000) + 12 * 3600 * 1000
        }
    }
    
    cron_data["jobs"].append(morning_task)
    cron_data["jobs"].append(afternoon_task)
    
    # Save
    with open(cron_tasks_path, 'w', encoding='utf-8') as f:
        json.dump(cron_data, f, ensure_ascii=False, indent=4)
    
    print(f"  ✅ Scheduled tasks added to cron-tasks.json")
    print(f"  ✅ 定时任务已添加到 cron-tasks.json")
    print(f"  📅 Morning run: daily at 2:30 AM / 凌晨 2:30 执行")
    print(f"  📅 Afternoon run: daily at 2:30 PM / 下午 2:30 执行")

def print_usage(mode):
    print("\n" + "="*60)
    print("✅ Installation Complete! / 安装完成！")
    print("="*60)
    print()
    
    if mode == 1:
        print("📋 Usage (Scheduled Mode) / 使用说明（定时模式）:")
        print()
        print("  Analysis runs automatically twice daily:")
        print("  分析每天自动执行两次:")
        print("    - 2:30 AM (morning) / 凌晨 2:30")
        print("    - 2:30 PM (afternoon) / 下午 2:30")
        print()
        print("  Check next run / 查看下次执行:")
        print("    cat ~/.openclaw/cron/cron-tasks.json | grep -A 10 \"i-am\"")
        print()
        print("  Manual analysis anytime / 随时手动分析:")
        print("    python3 scripts/i_am_daily_analysis.py")
        print()
    elif mode == 2:
        print("📋 Usage (Manual Mode) / 使用说明（手动模式）:")
        print()
        print("  Run analysis when needed / 需要时运行分析:")
        print("    python3 scripts/i_am_daily_analysis.py")
        print()
        print("  Discover from history / 从历史发现:")
        print("    python3 scripts/auto_discover.py")
        print()
    
    print("📊 Check USER.md anytime / 随时查看 USER.md:")
    print("  cat ~/.openclaw/workspace/USER.md")
    print()

def main():
    print_banner()
    
    # Ask user for mode
    mode = ask_mode()
    
    mode_names = {1: "Scheduled / 定时", 2: "Manual / 手动"}
    print(f"\n✅ Selected: {mode_names[mode]} Mode / 已选择：{mode_names[mode]} 模式")
    
    # Setup based on mode
    if mode == 1:
        setup_scheduled_mode()
    
    # Print usage
    print_usage(mode)

if __name__ == "__main__":
    main()
