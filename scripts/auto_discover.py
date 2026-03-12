#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动发现历史对话并生成 USER.md

功能:
1. 扫描 OpenClaw 目录寻找历史对话
2. 分析对话提取用户特征
3. 生成临时 USER.md 供用户审核
4. 用户确认后替换正式 USER.md
5. 支持交互式问答完善 USER.md
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoDiscover:
    """自动发现历史对话并生成 USER.md"""
    
    def __init__(self, workspace_path: str = None):
        self.openclaw_root = Path.home() / ".openclaw"
        if workspace_path:
            self.workspace_root = Path(workspace_path)
        else:
            self.workspace_root = Path.home() / ".openclaw" / "workspace"
        self.temp_dir = self.workspace_root / "skills" / "i-am" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 搜索路径
        self.search_paths = [
            self.openclaw_root / "agents" / "main" / "sessions",
            self.workspace_root / "memory",
            self.workspace_root / "memory" / "daily",
            self.workspace_root / "memory" / "daily" / "logs",
        ]
        
    def find_conversation_sources(self) -> List[Path]:
        """寻找所有可能的对话来源"""
        sources = []
        
        # 使用预定义的搜索路径
        for search_path in self.search_paths:
            if not search_path.exists():
                continue
            
            # 查找 JSONL 文件 (OpenClaw sessions)
            sources.extend(search_path.glob("*.jsonl"))
            
            # 查找 Markdown 文件 (memory logs)
            sources.extend(search_path.glob("*.md"))
        
        logger.info(f"找到 {len(sources)} 个对话来源文件")
        return sources
    
    def parse_conversation(self, file_path: Path) -> List[Dict]:
        """解析对话文件"""
        conversations = []
        
        try:
            if file_path.suffix == ".jsonl":
                # JSONL 格式 (OpenClaw sessions)
                # OpenClaw 格式：{"type":"message", "message":{"role":"user", "content":[{"type":"text","text":"..."}]}}
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            msg = json.loads(line)
                            
                            # 跳过非消息类型（thinking, toolCall, custom 等）
                            if msg.get("type") != "message":
                                continue
                            
                            # 获取消息内容
                            message_data = msg.get("message", {})
                            role = message_data.get("role", "")
                            
                            if role in ["user", "assistant"]:
                                # 解析 content 数组，只提取 text 类型
                                content_list = message_data.get("content", [])
                                text_parts = []
                                for item in content_list:
                                    if isinstance(item, dict):
                                        # 只提取 text 类型，过滤 thinking/toolCall 等
                                        if item.get("type") == "text":
                                            text_parts.append(item.get("text", ""))
                                        # 跳过 thinking, tool_call, tool_result 等
                                    elif isinstance(item, str):
                                        text_parts.append(item)
                                
                                text = "".join(text_parts).strip()
                                
                                # 跳过空内容或纯 thinking 内容
                                if not text or text.startswith("{'type': 'thinking'"):
                                    continue
                                
                                conversations.append({
                                    "role": role,
                                    "text": text,
                                    "timestamp": msg.get("timestamp", ""),
                                    "source": str(file_path)
                                })
                        except json.JSONDecodeError:
                            continue
            
            elif file_path.suffix == ".md":
                # Markdown 格式 (memory logs)
                content = file_path.read_text(encoding='utf-8')
                # 简单解析：提取用户对话
                lines = content.split('\n')
                current_role = None
                current_text = []
                
                for line in lines:
                    if line.startswith(('用户:', '我:', 'User:', '章伟伟:')):
                        if current_role and current_text:
                            conversations.append({
                                "role": current_role,
                                "text": " ".join(current_text),
                                "timestamp": "",
                                "source": str(file_path)
                            })
                        current_role = "user"
                        current_text = [line.split(':', 1)[-1].strip()]
                    elif line.startswith(('助手:', 'AI:', '龙傲天:')):
                        if current_role and current_text:
                            conversations.append({
                                "role": current_role,
                                "text": " ".join(current_text),
                                "timestamp": "",
                                "source": str(file_path)
                            })
                        current_role = "assistant"
                        current_text = [line.split(':', 1)[-1].strip()]
                    else:
                        if current_role:
                            current_text.append(line.strip())
                
                # 添加最后一个话轮
                if current_role and current_text:
                    conversations.append({
                        "role": current_role,
                        "text": " ".join(current_text),
                        "timestamp": "",
                        "source": str(file_path)
                    })
        
        except Exception as e:
            logger.error(f"解析文件失败 {file_path}: {e}")
        
        return conversations
    
    def extract_interactive_info(self) -> Dict[str, Any]:
        """交互式询问用户信息（当自动提取不足时）"""
        info = {}
        
        # 检查是否是 TTY 环境
        import sys
        if not sys.stdin.isatty():
            logger.info("非 TTY 环境，跳过交互式问答")
            return info
        
        print("\n🎯 自动发现未找到足够信息，需要您协助完善：\n")
        
        try:
            # 询问姓名
            name = input("1. 您的姓名或昵称：").strip()
            if name:
                info["name"] = name
            
            # 询问称呼
            call_sign = input("2. 希望我怎么称呼您（如：兄弟、老板、老师）：").strip()
            if call_sign:
                info["call_sign"] = call_sign
        except (EOFError, KeyboardInterrupt):
            logger.info("用户中断交互式问答")
        
        # 询问时区
        timezone = input("3. 您所在的时区（如：Asia/Shanghai）：").strip()
        if timezone:
            info["timezone"] = timezone
        
        # 询问职业
        profession = input("4. 您的职业或领域（如：嵌入式开发）：").strip()
        if profession:
            info["profession"] = profession
        
        # 询问沟通风格
        print("\n5. 您偏好的沟通风格：")
        print("   a) 直接了当，少废话")
        print("   b) 详细解释，多举例")
        print("   c) 先给结论，再展开")
        style = input("   请选择 (a/b/c)：").strip().lower()
        if style == 'a':
            info["communication_style"] = "直接了当型"
        elif style == 'b':
            info["communication_style"] = "详细解释型"
        elif style == 'c':
            info["communication_style"] = "结论优先型"
        
        return info
    
    def _is_valid_user_text(self, text: str) -> bool:
        """检查是否是有效的用户文本（过滤 Markdown、代码、AI 回复等）"""
        if not text or len(text) < 5:
            return False
        # 过滤掉 Markdown 格式内容
        if text.startswith(('**', '###', '##', '# ', '|', '```', '- [', '1.', '2.', '3.', '{', '[', '(')):
            return False
        # 过滤掉包含大量 Markdown 符号的内容
        markdown_chars = sum(1 for c in text if c in '*#|`>')
        if markdown_chars > len(text) * 0.15:
            return False
        # 过滤掉 thinking 签名
        if 'thinkingSignature' in text or 'reasoning_content' in text:
            return False
        return True
    
    def extract_user_traits(self, conversations: List[Dict]) -> Dict:
        """从对话中提取用户特征"""
        traits = {
            "name": None,
            "call_sign": None,
            "timezone": None,
            "profession": [],
            "communication_style": [],
            "decision_style": [],
            "preferences": [],
            "context": []
        }
        
        # 关键词匹配（增强版）
        patterns = {
            "name": [
                r"我叫 ([^\s,，.。]+)",
                r"我是 ([^\s,，.。]+)",
                r"name[:\s]+([^\s,，.。]+)",
                r"本人 ([^\s,，.。]+)",
            ],
            "call_sign": [
                r"叫我 ([^\s,，.。]+)",
                r"称呼我？为？ ([^\s,，.。]+)",
                r"call me ([^\s,，.。]+)",
                r"喊我 ([^\s,，.。]+)",
            ],
            "timezone": [
                r"时区 [:\s]+([\w/]+)",
                r"timezone[:\s]+([\w/]+)",
                r"我在 ([^\s]+) 时间",
            ],
            "profession": [
                r"我是 (.+?)(?:开发 | 工程师 | 程序员 | 从业者)",
                r"从事 (.+?)(?:开发 | 工作 | 行业)",
                r"profession[:\s]+(.+)",
                r"做 (.+?) 的",
                r"(.+?) 开发",
            ],
            "communication_style": [
                r"(直接 | 简洁 | 简单).*(?:点 | 些)",
                r"别 (?:整 | 搞 | 弄).*(?:没用的 | 虚的 | 废话)",
                r"(?:喜欢 | 偏好).*(?:直接 | 简洁)",
                r"有话直说 | 少整没用的 | 别绕弯",
                r"详细点 | 展开说 | 多解释",
            ],
            "decision_style": [
                r"先干再说 | 直接整 | 开搞 | 开干",
                r"让我想想 | 考虑下 | 再想想",
                r"行动导向 | 结果导向",
            ]
        }
        
        for conv in conversations:
            text = conv.get("text", "")
            
            # 过滤无效内容（Markdown、AI 回复、thinking 等）
            if not self._is_valid_user_text(text):
                continue
            
            # 只处理用户消息
            if conv.get("role") != "user":
                continue
            
            # 提取姓名
            for pattern in patterns["name"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    traits["name"] = match.group(1).strip()
            
            # 提取称呼
            for pattern in patterns["call_sign"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    traits["call_sign"] = match.group(1).strip()
            
            # 提取时区
            for pattern in patterns["timezone"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    traits["timezone"] = match.group(1).strip()
            
            # 提取职业
            for pattern in patterns["profession"]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    profession = match.group(1).strip()
                    if profession and profession not in traits["profession"]:
                        traits["profession"].append(profession)
            
            # 提取沟通风格
            for pattern in patterns["communication_style"]:
                if re.search(pattern, text, re.IGNORECASE):
                    style = self._normalize_style(pattern)
                    if style and style not in traits["communication_style"]:
                        traits["communication_style"].append(style)
            
            # 提取决策风格
            for pattern in patterns["decision_style"]:
                if re.search(pattern, text, re.IGNORECASE):
                    style = self._normalize_decision_style(pattern)
                    if style and style not in traits["decision_style"]:
                        traits["decision_style"].append(style)
        
        return traits
    
    def _normalize_style(self, pattern: str) -> Optional[str]:
        """标准化沟通风格描述"""
        if any(k in pattern for k in ["直接", "简洁", "简单", "有话直说", "少整没用"]):
            return "偏好直接沟通"
        elif any(k in pattern for k in ["详细", "展开", "多解释"]):
            return "偏好详细解释"
        return None
    
    def _normalize_decision_style(self, pattern: str) -> Optional[str]:
        """标准化决策风格描述"""
        if any(k in pattern for k in ["先干", "直接整", "开搞", "行动"]):
            return "行动导向型"
        elif any(k in pattern for k in ["想想", "考虑", "再想想"]):
            return "谨慎思考型"
        return None
    
    def generate_user_md(self, traits: Dict, interactive_info: Dict = None) -> str:
        """生成 USER.md 内容"""
        # 合并自动提取和交互式输入的信息
        if interactive_info:
            for key, value in interactive_info.items():
                if value and not traits.get(key):
                    traits[key] = value
        
        name = traits.get("name") or "User"
        call_sign = traits.get("call_sign") or name or "User"
        timezone = traits.get("timezone") or "Asia/Shanghai"
        
        # 整理职业信息
        profession_list = traits.get("profession", [])
        if isinstance(profession_list, list):
            profession_str = ", ".join(profession_list) if profession_list else "待补充"
        else:
            profession_str = profession_list
        
        # 整理沟通风格
        style_list = traits.get("communication_style", [])
        style_str = ", ".join(style_list) if style_list else "待提取"
        
        # 整理决策风格
        decision_list = traits.get("decision_style", [])
        decision_str = ", ".join(decision_list) if decision_list else "待提取"
        
        # 构建上下文
        context_items = []
        if profession_list:
            context_items.append(f"{profession_str}从业者")
        if style_list:
            context_items.append(f"沟通风格：{style_str}")
        if decision_list:
            context_items.append(f"决策风格：{decision_str}")
        context_items.append("需要 AI 助手协助开发、运维任务")
        context_items.append("使用 OpenClaw 7x24 小时运行 AI 助手")
        
        context = "\n- ".join(context_items)
        
        return f"""# USER.md - About Your Human

> **Generated by**: i-am Skill (Auto Discovery)
> **Generated at**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
> **Review required**: Yes
> **Version**: v4.0 (i-am enhanced)

---

- **Name:** {name}
- **What to call them:** {call_sign}
- **Pronouns:** 
- **Timezone:** {timezone}
- **Notes:** {profession_str}

## Context

- {context}

---

## 🎯 Core Personality Traits (Extracted by i-am)

| Trait | Value | Saturation | Evidence Count |
|-------|-------|------------|----------------|
| Communication Style | {style_str} | Pending | {len(style_list)} |
| Decision Style | {decision_str} | Pending | {len(decision_list)} |

---

## 🧠 ACT-R Cognitive Model

### Declarative Memory (Facts)
- Name: {name}
- Timezone: {timezone}
- Profession: {profession_str}
- To be filled by i-am Skill

### Procedural Memory (Interaction Preferences)
- To be filled based on conversation analysis

### Goal Hierarchy
- **Short-term**: To be filled
- **Medium-term**: To be filled
- **Long-term**: To be filled

### Utility Learning
| Interaction Pattern | Success Rate | Last Adjustment |
|--------------------|--------------|-----------------|
| To be filled | - | - |

---

*This file was auto-generated by i-am Skill based on conversation analysis.
Please review and edit as needed. After confirmation, move to ~/.openclaw/workspace/USER.md*
"""
    
    def run(self, interactive: bool = False) -> Dict[str, Any]:
        """运行自动发现流程"""
        result = {
            "success": False,
            "found_history": False,
            "conversation_count": 0,
            "traits": {},
            "interactive_info": {},
            "generated_file": None,
            "message": "",
        }
        
        logger.info("🔍 开始扫描历史对话...")
        
        # 1. 寻找对话来源
        sources = self.find_conversation_sources()
        
        # 2. 解析对话
        all_conversations = []
        if sources:
            for source in sources[:10]:  # 最多处理 10 个文件
                conversations = self.parse_conversation(source)
                all_conversations.extend(conversations)
        
        if all_conversations:
            result["found_history"] = True
            result["conversation_count"] = len(all_conversations)
            logger.info(f"解析到 {len(all_conversations)} 条对话")
            
            # 3. 提取用户特征
            traits = self.extract_user_traits(all_conversations)
            result["traits"] = traits
            logger.info(f"提取到用户特征：{traits}")
        else:
            logger.info("未找到历史对话记录")
            traits = {}
        
        # 4. 交互式补充（如果信息不足或用户要求）
        interactive_info = {}
        if interactive or not traits.get("name"):
            interactive_info = self.extract_interactive_info()
            result["interactive_info"] = interactive_info
        
        # 5. 生成 USER.md
        user_md_content = self.generate_user_md(traits, interactive_info if interactive_info else None)
        
        # 6. 保存到 temp 目录
        temp_file = self.temp_dir / "USER.generated.md"
        temp_file.write_text(user_md_content, encoding='utf-8')
        result["generated_file"] = str(temp_file)
        
        logger.info(f"✅ 生成 USER.md: {temp_file}")
        result["success"] = True
        result["message"] = f"已生成 USER.md 到 {temp_file}"
        
        return result
    

def main():
    """主函数"""
    import sys
    
    # 检查是否启用交互模式
    interactive = "--interactive" in sys.argv or "-i" in sys.argv
    
    discover = AutoDiscover()
    
    # 运行自动发现
    result = discover.run(interactive=interactive)
    
    print("\n" + "="*60)
    print("📊 自动发现结果报告")
    print("="*60)
    
    if result["success"]:
        if result["found_history"]:
            print(f"✅ 发现 {result['conversation_count']} 条历史对话")
        else:
            print("⚠️  未找到历史对话记录")
        
        if result["traits"]:
            print(f"\n📋 提取到的用户特征:")
            for key, value in result["traits"].items():
                if value:
                    print(f"   - {key}: {value}")
        
        if result["interactive_info"]:
            print(f"\n💬 交互式补充的信息:")
            for key, value in result["interactive_info"].items():
                if value:
                    print(f"   - {key}: {value}")
        
        print(f"\n📄 已生成：{result['generated_file']}")
        print("\n📝 下一步操作:")
        print(f"   1. 查看生成的文件：cat {result['generated_file']}")
        print(f"   2. 编辑完善（如需要）")
        print(f"   3. 确认后移动：mv {result['generated_file']} ~/.openclaw/workspace/USER.md")
    else:
        print(f"\n❌ 失败：{result['message']}")
    
    print("="*60)


if __name__ == "__main__":
    main()
