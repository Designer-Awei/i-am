#!/usr/bin/env python3
"""
i-am Daily Analysis

Combines ACT-R feedback + Grounded Theory in one run:
1. Load sessions since last analysis
2. Run ACT-R implicit feedback analysis
3. Run Grounded Theory (Open/Axial/Selective Coding)
4. Generate USER.md preview
5. Ask for confirmation (first run only, then weekly)
6. Update USER.md if confirmed
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import re

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from open_coding import OpenCodingExtractor
from actr_feedback import ImplicitFeedbackInferencer
from user_md_sync import UserMDSyncEngine

class IamDailyAnalysis:
    """Daily personality analysis combining ACT-R + Grounded Theory"""
    
    def __init__(self):
        self.open_coding = OpenCodingExtractor()
        self.actr = ImplicitFeedbackInferencer()
        self.sync = UserMDSyncEngine()
        
        self.sessions_path = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
        self.data_dir = Path(__file__).parent.parent / "data" / "daily_runs"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load last analysis timestamp
        self.last_analysis_file = self.data_dir / "last_analysis.json"
        self.last_analysis_time = self._load_last_analysis_time()
        
        # Confirmation tracking
        self.confirmation_file = self.data_dir / "confirmation.json"
        self.confirmation_status = self._load_confirmation_status()
    
    def _load_last_analysis_time(self):
        """Load timestamp of last analysis"""
        if self.last_analysis_file.exists():
            with open(self.last_analysis_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return datetime.fromisoformat(data['timestamp'])
        # Default: analyze last 12 hours if no previous analysis
        return datetime.now() - timedelta(hours=12)
    
    def _save_last_analysis_time(self):
        """Save current analysis timestamp"""
        with open(self.last_analysis_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
    
    def _load_confirmation_status(self):
        """Load user confirmation status"""
        if self.confirmation_file.exists():
            with open(self.confirmation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        # Default: ask for confirmation on first run
        return {
            'last_confirmed': None,
            'auto_approve_until': None,
            'total_confirmations': 0
        }
    
    def _save_confirmation_status(self):
        """Save confirmation status"""
        with open(self.confirmation_file, 'w', encoding='utf-8') as f:
            json.dump(self.confirmation_status, f, indent=2, ensure_ascii=False)
    
    def _should_ask_confirmation(self):
        """Determine if we should ask for user confirmation"""
        # First run: always ask
        if not self.confirmation_status['last_confirmed']:
            return True
        
        # Check if auto-approve period is still valid
        if self.confirmation_status['auto_approve_until']:
            auto_until = datetime.fromisoformat(self.confirmation_status['auto_approve_until'])
            if datetime.now() < auto_until:
                return False  # Still in auto-approve period
        
        # Weekly confirmation (every 7 days)
        last_confirmed = datetime.fromisoformat(self.confirmation_status['last_confirmed'])
        days_since_confirmation = (datetime.now() - last_confirmed).days
        
        return days_since_confirmation >= 7
    
    def _ask_confirmation(self, core_traits, actr_stats):
        """Ask user for confirmation to update USER.md"""
        import sys
        
        # Check if running in TTY environment
        if not sys.stdin.isatty():
            print("\nℹ️  Non-TTY environment, auto-approving / 非 TTY 环境，自动批准...")
            return 'approve'
        
        print("\n" + "="*60)
        print("📋 USER.md Update Preview / USER.md 更新预览")
        print("="*60)
        
        print("\n🎯 Core Traits Detected / 检测到的核心特质:")
        for trait, data in core_traits.items():
            print(f"   - {trait}: {data['value']} (saturation: {data['saturation']:.0%})")
        
        print(f"\n🧠 ACT-R Feedback / ACT-R 反馈:")
        print(f"   Positive / 正面：{actr_stats['positive']}")
        print(f"   Negative / 负面：{actr_stats['negative']}")
        print(f"   Neutral / 中性：{actr_stats['neutral']}")
        
        print("\n" + "-"*60)
        print("Choose action / 选择操作:")
        print()
        print("  1) Approve and Update / 批准并更新 (default) / 默认")
        print("     - Update USER.md with new insights")
        print("       用新洞察更新 USER.md")
        print("     - Auto-approve next 7 days")
        print("       未来 7 天自动批准")
        print()
        print("  2) Review Manually / 手动审阅")
        print("     - Save preview for manual review")
        print("       保存预览供手动审阅")
        print("     - Don't update USER.md yet")
        print("       暂不更新 USER.md")
        print()
        print("  3) Always Auto-Approve / 总是自动批准")
        print("     - Skip confirmation for 30 days")
        print("       30 天内跳过确认")
        print("     - Auto-update USER.md")
        print("       自动更新 USER.md")
        print()
        
        while True:
            choice = input("Enter choice [1/2/3] (default: 1): ").strip()
            if not choice:
                return 'approve'  # Default to approve
            if choice.lower() in ['1', 'approve', '批准']:
                return 'approve'
            elif choice.lower() in ['2', 'review', '审阅']:
                return 'review'
            elif choice.lower() in ['3', 'always', '总是']:
                return 'always_approve'
            print("Invalid choice / 无效选择。Please enter 1, 2, or 3 / 请输入 1、2 或 3。")
    
    def _save_preview(self, core_traits, actr_stats):
        """Save preview for manual review"""
        preview_file = self.data_dir / f"preview_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(preview_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'core_traits': core_traits,
                'actr_feedback': actr_stats,
                'status': 'pending_review'
            }, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Preview saved / 预览已保存：{preview_file}")
        print(f"   Review and manually update USER.md when ready")
        print(f"   审阅后手动更新 USER.md")
    
    def load_sessions_since_last_analysis(self):
        """Load user messages since last analysis"""
        print(f"📊 Loading sessions since / 加载会话从 {self.last_analysis_time.strftime('%Y-%m-%d %H:%M')}...")
        
        user_messages = []
        
        if not self.sessions_path.exists():
            print(f"   ⚠️  Sessions directory not found / 会话目录不存在：{self.sessions_path}")
            return user_messages
        
        for session_file in self.sessions_path.glob("*.jsonl"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            msg = json.loads(line)
                            if msg.get("type") != "message":
                                continue
                            
                            message_data = msg.get("message", {})
                            if message_data.get("role") != "user":
                                continue
                            
                            # Get timestamp
                            msg_timestamp = msg.get("timestamp", "")
                            if msg_timestamp:
                                try:
                                    msg_dt = datetime.fromisoformat(msg_timestamp.replace('Z', '+00:00'))
                                    msg_dt = msg_dt.replace(tzinfo=None)
                                except:
                                    msg_dt = datetime.now()
                            else:
                                msg_dt = datetime.now()
                            
                            # Only load messages since last analysis
                            if msg_dt <= self.last_analysis_time:
                                continue
                            
                            # Extract text
                            content_list = message_data.get("content", [])
                            text_parts = []
                            for item in content_list:
                                if isinstance(item, dict) and item.get("type") == "text":
                                    text_parts.append(item.get("text", ""))
                            
                            text = "".join(text_parts).strip()
                            
                            # Filter system messages
                            if not text or text.startswith("[cron:") or text.startswith("Read HEARTBEAT"):
                                continue
                            
                            # Extract real content from IM metadata
                            if text.startswith("Conversation info") or text.startswith("[Queued messages"):
                                match = re.search(r'\][\n\s]*([^\n]+?)：(.+)$', text, re.DOTALL)
                                if match:
                                    text = match.group(2).strip()
                                else:
                                    lines = text.split('\n')
                                    for line in reversed(lines):
                                        line = line.strip()
                                        if line and not line.startswith(('```', '---', '===', '[', '{')):
                                            if ':' in line and len(line) < 50:
                                                continue
                                            text = line
                                            break
                                    else:
                                        continue
                            
                            user_messages.append({
                                "text": text,
                                "timestamp": msg_dt,
                                "session": session_file.name
                            })
                            
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"   ⚠️  Error reading / 读取错误 {session_file.name}: {e}")
        
        print(f"   ✅ Loaded / 加载 {len(user_messages)} user messages / 用户消息")
        return user_messages
    
    def run_actr_analysis(self, messages):
        """Run ACT-R implicit feedback analysis"""
        print("\n🧠 Running ACT-R implicit feedback analysis / 运行 ACT-R 隐式反馈分析...")
        
        feedback_stats = {"positive": 0, "negative": 0, "neutral": 0}
        
        for msg in messages:
            result = self.actr.infer_feedback(msg["text"])
            feedback_type = result.get("type", "neutral")
            feedback_stats[feedback_type] += 1
        
        print(f"   ✅ Analyzed / 分析了 {len(messages)} messages / 消息")
        print(f"      Positive / 正面：{feedback_stats['positive']}")
        print(f"      Negative / 负面：{feedback_stats['negative']}")
        print(f"      Neutral / 中性：{feedback_stats['neutral']}")
        
        return feedback_stats
    
    def run_grounded_theory(self, messages):
        """Run Grounded Theory analysis (Open/Axial/Selective Coding)"""
        print("\n🏷️  Running Grounded Theory analysis / 运行扎根理论分析...")
        
        # Open Coding: extract labels from each message
        open_codes = []
        for msg in messages:
            codes = self.open_coding.extract_codes(msg["text"])
            if codes:
                open_codes.extend(codes)
        
        print(f"   ✅ Open Coding / 开放性编码：extracted / 提取 {len(open_codes)} codes / 编码")
        
        if not open_codes:
            print(f"   ℹ️  No codes extracted (messages may be task-oriented) / 未提取到编码（消息可能是任务型的）")
            return {}
        
        # Axial Coding: cluster labels into categories
        category_stats = {}
        for code in open_codes:
            for label_info in code.get("labels", []):
                category = label_info.get("category", "unknown")
                label = label_info.get("label", "unknown")
                
                if category not in category_stats:
                    category_stats[category] = {}
                if label not in category_stats[category]:
                    category_stats[category][label] = 0
                category_stats[category][label] += 1
        
        print(f"   ✅ Axial Coding / 主轴编码：clustered / 聚类为 {len(category_stats)} categories / 类别")
        
        # Selective Coding: generate core traits
        core_traits = {}
        for category, labels in category_stats.items():
            sorted_labels = sorted(labels.items(), key=lambda x: x[1], reverse=True)
            if sorted_labels:
                top_label, count = sorted_labels[0]
                core_traits[category] = {
                    "value": top_label,
                    "count": count,
                    "saturation": min(0.95, 0.5 + (count * 0.05)),
                    "all_labels": dict(sorted_labels)
                }
        
        print(f"   ✅ Selective Coding / 选择性编码：generated / 生成 {len(core_traits)} core traits / 核心特质")
        
        return core_traits
    
    def update_user_md(self, actr_stats, core_traits):
        """Update USER.md with merged insights"""
        print("\n📄 Updating USER.md / 更新 USER.md...")
        
        # Save analysis results
        result_file = self.data_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "since": self.last_analysis_time.isoformat(),
                "actr_feedback": actr_stats,
                "core_traits": core_traits
            }, f, ensure_ascii=False, indent=2)
        
        # Update USER.md via sync engine
        try:
            # Create user info dict for sync
            user_info = {}
            if core_traits:
                for trait, data in core_traits.items():
                    user_info[trait.lower().replace(' ', '_')] = data['value']
            
            # Sync (this will backup and update USER.md)
            self.sync.update_user_md(user_info)
            
            print(f"   ✅ USER.md updated / 已更新")
            print(f"   📄 Results saved / 结果已保存：{result_file}")
            
        except Exception as e:
            print(f"   ⚠️  USER.md sync failed / 同步失败：{e}")
    
    def run(self):
        """Run complete daily analysis"""
        print("="*60)
        print("🧠 i-am Daily Analysis / 每日分析")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. Load sessions since last analysis
        messages = self.load_sessions_since_last_analysis()
        
        if not messages:
            print("\n⚠️  No new messages since last analysis / 上次分析后无新消息，skipping / 跳过...")
            self._save_last_analysis_time()
            return
        
        # 2. Run ACT-R analysis
        actr_stats = self.run_actr_analysis(messages)
        
        # 3. Run Grounded Theory
        core_traits = self.run_grounded_theory(messages)
        
        # 4. Check if confirmation is needed
        if self._should_ask_confirmation():
            # Ask user for confirmation
            action = self._ask_confirmation(core_traits, actr_stats)
            
            if action == 'approve':
                # Update USER.md
                self.update_user_md(actr_stats, core_traits)
                
                # Update confirmation status
                self.confirmation_status['last_confirmed'] = datetime.now().isoformat()
                self.confirmation_status['total_confirmations'] += 1
                self._save_confirmation_status()
                
            elif action == 'review':
                # Save preview for manual review
                self._save_preview(core_traits, actr_stats)
                
            elif action == 'always_approve':
                # Update USER.md and set auto-approve for 30 days
                self.update_user_md(actr_stats, core_traits)
                
                self.confirmation_status['last_confirmed'] = datetime.now().isoformat()
                self.confirmation_status['auto_approve_until'] = (datetime.now() + timedelta(days=30)).isoformat()
                self.confirmation_status['total_confirmations'] += 1
                self._save_confirmation_status()
        else:
            # Auto-approve (within 7-day period)
            print("\nℹ️  Auto-approved (within 7-day confirmation period) / 自动批准（7 天确认期内）")
            self.update_user_md(actr_stats, core_traits)
        
        # 5. Save timestamp
        self._save_last_analysis_time()
        
        print("\n" + "="*60)
        print("✅ Daily Analysis Complete / 每日分析完成！")
        print("="*60)

def main():
    analysis = IamDailyAnalysis()
    analysis.run()

if __name__ == "__main__":
    main()
