#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
USER.md 同步引擎

负责将扎根理论和 ACT-R 的分析结果合并到 USER.md
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class UserMDSyncEngine:
    """USER.md 同步引擎"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        # 修复：先转 Path 再 expanduser
        user_md_path_str = self.config["user_md_sync"]["user_md_path"]
        self.user_md_path = Path(user_md_path_str).expanduser() if isinstance(user_md_path_str, str) else user_md_path_str.expanduser()
        
        backup_config = self.config["user_md_sync"].get("backup", {})
        if "backup_dir" in backup_config:
            backup_dir_str = backup_config["backup_dir"]
            self.backup_dir = Path(backup_dir_str).expanduser() if isinstance(backup_dir_str, str) else backup_dir_str.expanduser()
        else:
            self.backup_dir = Path(__file__).parent.parent / "user_md_sync" / "backup"
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        import yaml
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_backup(self) -> Optional[str]:
        """创建 USER.md 备份"""
        if not self.config["user_md_sync"]["backup_enabled"]:
            return None
        
        if not self.user_md_path.exists():
            return None
        
        # 确保备份目录存在
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"USER_{timestamp}.md"
        backup_path = self.backup_dir / backup_filename
        
        # 复制文件
        shutil.copy2(self.user_md_path, backup_path)
        
        # 清理过期备份
        self._cleanup_old_backups()
        
        return str(backup_path)
    
    def _cleanup_old_backups(self):
        """清理过期备份"""
        retention_days = self.config["user_md_sync"]["backup_retention_days"]
        cutoff = datetime.now().timestamp() - (retention_days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("USER_*.md"):
            if backup_file.stat().st_mtime < cutoff:
                backup_file.unlink()
    
    def merge_updates(self, grounding_updates: Dict, actr_updates: Dict) -> Dict[str, Any]:
        """
        合并更新建议
        
        Args:
            grounding_updates: 扎根理论的更新建议
            actr_updates: ACT-R 的更新建议
            
        Returns:
            合并后的更新内容
        """
        merged = {
            "core_traits": [],
            "actr_model": {},
            "changes": [],
            "conflicts": []
        }
        
        # 策略：扎根理论优先
        conflict_resolution = self.config["user_md_sync"]["merge_strategy"]["conflict_resolution"]
        
        # 处理核心特质（来自扎根理论）
        if grounding_updates.get("core_traits"):
            merged["core_traits"] = grounding_updates["core_traits"]
            merged["changes"].append({
                "section": "核心人格特质",
                "action": "update",
                "source": "grounding_theory"
            })
        
        # 处理 ACT-R 模型
        if actr_updates.get("production_rules"):
            merged["actr_model"]["production_rules"] = actr_updates["production_rules"]
            merged["changes"].append({
                "section": "ACT-R 认知模型",
                "action": "update",
                "source": "actr"
            })
        
        if actr_updates.get("utility_changes"):
            merged["actr_model"]["utility_changes"] = actr_updates["utility_changes"]
            merged["changes"].append({
                "section": "效用学习",
                "action": "update",
                "source": "actr"
            })
        
        # 检测冲突
        if grounding_updates.get("traits") and actr_updates.get("traits"):
            for gt_trait in grounding_updates["traits"]:
                for actr_trait in actr_updates["traits"]:
                    if gt_trait.get("name") == actr_trait.get("name"):
                        if gt_trait.get("value") != actr_trait.get("value"):
                            merged["conflicts"].append({
                                "trait": gt_trait["name"],
                                "grounding_value": gt_trait["value"],
                                "actr_value": actr_trait["value"],
                                "resolution": "grounding_priority" if conflict_resolution == "grounding_priority" else "manual"
                            })
        
        return merged
    
    def update_user_md(self, merged_updates: Dict) -> Dict[str, Any]:
        """
        更新 USER.md
        
        Args:
            merged_updates: 合并后的更新内容
            
        Returns:
            更新摘要
        """
        update_summary = {
            "success": False,
            "backup": None,
            "changes": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 创建备份
        backup_path = self.create_backup()
        if backup_path:
            update_summary["backup"] = backup_path
        
        # 读取现有内容
        if not self.user_md_path.exists():
            # 创建新文件
            content = self._create_initial_user_md()
        else:
            with open(self.user_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        # 更新内容
        new_content = self._apply_updates(content, merged_updates)
        
        # 写入文件
        with open(self.user_md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        update_summary["success"] = True
        update_summary["changes"] = merged_updates.get("changes", [])
        
        # 记录变更日志
        self._log_changes(merged_updates)
        
        return update_summary
    
    def _create_initial_user_md(self, user_info: dict = None) -> str:
        """
        创建初始 USER.md（参考 OpenClaw 官方格式）
        
        Args:
            user_info: 用户提供的信息（可选）
                - name: 姓名/称呼
                - timezone: 时区
                - notes: 备注信息
        """
        name = user_info.get("name", "User") if user_info else "User"
        call_sign = user_info.get("call_sign", name) if user_info else "User"
        timezone = user_info.get("timezone", "UTC") if user_info else "UTC"
        notes = user_info.get("notes", "To be filled") if user_info else "To be filled"
        
        return """# USER.md - About Your Human

> **Version**: v4.0 (i-am enhanced)
> **Last Updated**: {date}
> **Update Engine**: Grounded Theory + ACT-R

---

- **Name**: {name}
- **What to call them**: {call_sign}
- **Pronouns**: 
- **Timezone**: {timezone}
- **Notes**: {notes}

## Context

- To be filled
- Uses OpenClaw for AI assistant tasks

---

## 🎯 Core Personality Traits (Extracted by Grounded Theory)

| Trait | Value | Saturation | Evidence Count |
|-------|-------|------------|----------------|
| Communication Style | To be extracted | - | - |
| Decision Style | To be extracted | - | - |

---

## 🧠 ACT-R Cognitive Model

### Declarative Memory (Facts)
- To be filled

### Procedural Memory (Interaction Preferences)
- To be filled

### Goal Hierarchy
- **Short-term**: To be filled
- **Medium-term**: To be filled
- **Long-term**: To be filled

### Utility Learning
| Interaction Pattern | Success Rate | Last Adjustment |
|--------------------|--------------|-----------------|
| To be filled | - | - |

---

*This file is automatically updated by i-am Skill based on conversation analysis.*
""".format(
            date=datetime.now().strftime("%Y-%m-%d"),
            name=name,
            call_sign=call_sign,
            timezone=timezone,
            notes=notes
        )
    
    def _apply_updates(self, content: str, updates: Dict) -> str:
        """应用更新到内容"""
        import re
        
        # 更新核心人格特质表格
        if updates.get("core_traits"):
            traits_table = self._generate_traits_table(updates["core_traits"])
            
            # 查找并替换特质表格部分
            pattern = r'(## 🎯 核心人格特质.*?\n)(\| 特质 \|.*?\n)(.*?)(---)'
            replacement = f'\\1{traits_table}\\4'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 更新 ACT-R 模型部分
        if updates.get("actr_model"):
            actr_content = self._generate_actr_section(updates["actr_model"])
            
            # 查找并替换 ACT-R 部分
            pattern = r'(## 🧠 ACT-R 认知模型.*?\n)(.*?)(---|\Z)'
            replacement = f'## 🧠 ACT-R 认知模型\\n\\n{actr_content}\\n\\n\\3'
            
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 更新版本号
        version_pattern = r'\*\*版本\*\*:\s*v([\d.]+)'
        match = re.search(version_pattern, content)
        if match:
            current_version = match.group(1)
            major, minor, patch = map(int, current_version.split('.'))
            new_version = f"{major}.{minor}.{patch + 1}"
            content = re.sub(version_pattern, f"**版本**: v{new_version}", content, count=1)
        
        # 更新日期
        date_pattern = r'\*\*最后更新\*\*:\s*[\d-]+'
        content = re.sub(date_pattern, f"**最后更新**: {datetime.now().strftime('%Y-%m-%d')}", content)
        
        return content
    
    def _generate_traits_table(self, traits: List[Dict]) -> str:
        """生成特质表格"""
        lines = ["| 特质 | 值 | 饱和度 | 证据数 |", "|------|-----|--------|--------|"]
        
        for trait in traits:
            name = trait.get("name", "未知")
            value = trait.get("value", "未知")
            saturation = trait.get("saturation", 0)
            evidence = trait.get("evidence_count", 0)
            
            lines.append(f"| {name} | {value} | {saturation:.0%} | {evidence} |")
        
        return '\n'.join(lines) + '\n'
    
    def _generate_actr_section(self, actr_model: Dict) -> str:
        """生成 ACT-R 模型部分"""
        lines = []
        
        # 产生式规则
        if "production_rules" in actr_model:
            lines.append("### 程序性记忆（产生式规则）")
            lines.append("")
            lines.append("| 规则 | 强度 | 成功率 | 最后验证 |")
            lines.append("|------|------|--------|---------|")
            
            for rule in actr_model["production_rules"]:
                name = rule.get("name", "未知")
                strength = rule.get("strength", 0)
                success_rate = rule.get("success_rate", 0)
                last_verified = rule.get("last_verified", "未知")
                
                lines.append(f"| {name} | {strength:.2f} | {success_rate:.2f} | {last_verified[:10]} |")
            
            lines.append("")
        
        # 效用变化
        if "utility_changes" in actr_model:
            lines.append("### 效用学习")
            lines.append("")
            lines.append("| 互动模式 | 调整 | 原因 |")
            lines.append("|---------|------|------|")
            
            for change in actr_model["utility_changes"]:
                mode = change.get("mode", "未知")
                adjustment = change.get("adjustment", 0)
                reason = change.get("reason", "")
                
                arrow = "↑" if adjustment > 0 else "↓" if adjustment < 0 else "→"
                lines.append(f"| {mode} | {arrow} {abs(adjustment):.2f} | {reason} |")
        
        return '\n'.join(lines)
    
    def _log_changes(self, updates: Dict):
        """记录变更日志"""
        log_path = Path(__file__).parent.parent / "user_md_sync" / "change_log.md"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"## {timestamp}\n\n"
        
        for change in updates.get("changes", []):
            log_entry += f"- **{change['section']}**: {change['action']} (来源：{change['source']})\n"
        
        if updates.get("conflicts"):
            log_entry += "\n### 冲突\n\n"
            for conflict in updates["conflicts"]:
                log_entry += f"- {conflict['trait']}: 扎根={conflict['grounding_value']}, ACT-R={conflict['actr_value']} → {conflict['resolution']}\n"
        
        log_entry += "\n---\n\n"
        
        # 追加到日志文件
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)


def main():
    """主函数"""
    import sys
    
    engine = UserMDSyncEngine()
    
    # 示例更新
    grounding_updates = {
        "core_traits": [
            {"name": "沟通风格", "value": "直截了当型", "saturation": 0.92, "evidence_count": 23},
            {"name": "决策风格", "value": "行动优先型", "saturation": 0.85, "evidence_count": 18},
        ]
    }
    
    actr_updates = {
        "production_rules": [
            {"name": "回复风格选择", "strength": 0.95, "success_rate": 0.98, "last_verified": datetime.now().isoformat()},
        ],
        "utility_changes": [
            {"mode": "直接给方案", "adjustment": 0.05, "reason": "用户正面反馈"},
        ]
    }
    
    # 合并更新
    merged = engine.merge_updates(grounding_updates, actr_updates)
    
    # 应用更新
    summary = engine.update_user_md(merged)
    
    print("USER.md 更新摘要:")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
