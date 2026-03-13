---
name: i-am
version: 4.0.1
description: Zero-config personality analysis. All-in-one SKILL.md with embedded code. AI-guided installation and IM-adaptive file sending.
license: MIT
---

# i-am Skill v4.0.1 - AI 指令文档

> **给 OpenClaw AI 的指令**：按照以下流程引导用户完成人格分析

---

## 🎯 触发条件

**场景 1: 首次安装（自动触发）**
- 用户安装此 skill 后，AI 主动询问配置

**场景 2: 用户主动触发**
- "运行 i-am 分析"、"分析我的人格"
- "人格特质"、"USER.md 更新"
- "扎根理论"

---

## 📁 文件结构

```
i-am/
├── SKILL.md              # 本文件（AI 指令）
├── clawhub.yaml          # ClawHub 配置
├── CHANGELOG/            # USER.md 变更历史（用户审核后备份）
│   └── USER-YYYYMMDD-HHMM.md  # 按时间戳备份
└── temp/                 # 临时目录（运行时自动创建）
    ├── USER.md           # 预览文件
    └── last_analysis.json # 时间戳
```

**注意**：
- `temp/` 目录和文件在首次运行时自动创建
- `CHANGELOG/` 目录在第一次用户确认后自动创建

---

## 🔄 完整工作流程（AI 执行指南）

### 阶段 1: 安装配置（首次使用）

**触发时机**：用户安装 skill 后，AI 主动触发

#### AI 检测安装状态

**检查清单**：
1. Cron 任务是否已配置（`~/.openclaw/cron/cron-tasks.json` 包含 `i-am` 任务）
2. 时间戳文件是否存在（`temp/last_analysis.json`）

**决策**：
- 如果都已存在 → AI 回复：`✅ i-am 已配置完成，回复"运行分析"开始分析`
- 如果有缺失 → 进入配置流程

#### AI 主动询问配置（首次安装）

**AI 回复模板**：

```
🧠 i-am Skill 配置向导

请选择自动化模式：

1️⃣ **定时模式**（推荐）
   - 每天自动分析两次（凌晨 2:30 和下午 2:30）
   - 使用 OpenClaw 定时任务系统
   - 无需手动操作

2️⃣ **手动模式**
   - 需要时手动运行分析
   - 无后台定时任务
   - 完全手动控制

请回复数字 1 或 2 选择（默认 1）：
```

#### AI 根据用户回复执行

**用户回复 "1" 或 "定时"**：
1. AI 执行：编辑 `cron-tasks.json`，添加两个定时任务（代码见下方）
2. AI 回复：`✅ 定时模式已配置，每天 2:30 自动运行`

**用户回复 "2" 或 "手动"**：
1. AI 回复：`✅ 手动模式已配置，需要时告诉我"运行 i-am 分析"`

#### AI 创建必要文件夹并备份初始 USER.md

**执行代码**：

```python
from pathlib import Path
from datetime import datetime
import shutil

skill_root = Path.home() / ".openclaw" / "workspace" / "skills" / "i-am"
user_md_path = Path.home() / ".openclaw" / "workspace" / "USER.md"

# 步骤 1: 创建 CHANGELOG 文件夹（用于备份 USER.md 历史版本）
changelog_dir = skill_root / "CHANGELOG"
changelog_dir.mkdir(parents=True, exist_ok=True)
print(f"✅ 已创建文件夹：{changelog_dir}")

# 步骤 2: 创建 temp 文件夹（用于存储临时文件）
temp_dir = skill_root / "temp"
temp_dir.mkdir(parents=True, exist_ok=True)
print(f"✅ 已创建文件夹：{temp_dir}")

# 步骤 3: 备份当前 USER.md（初始版本）
if user_md_path.exists():
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    backup_file = changelog_dir / f"USER-{timestamp}-initial.md"
    shutil.copy2(user_md_path, backup_file)
    print(f"📁 已备份初始 USER.md: {backup_file.name}")
else:
    # 创建空的初始文件
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    backup_file = changelog_dir / f"USER-{timestamp}-initial.md"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write("# USER.md - Initial Backup\n\n(首次安装时的空备份)\n")
    print(f"📁 已创建初始 USER.md 备份：{backup_file.name}")
```

**文件夹说明**：

| 文件夹 | 用途 | 创建时机 |
|--------|------|---------|
| `CHANGELOG/` | 备份 USER.md 历史版本 | 首次安装时创建 |
| `temp/` | 存储临时文件（预览、时间戳） | 首次安装时创建 |

**文件示例**：
```
i-am/
├── SKILL.md
├── clawhub.yaml
├── CHANGELOG/
│   ├── USER-20260313-1950-initial.md  ← 初始备份
│   ├── USER-20260313-2030.md          ← 第一次分析后备份
│   └── USER-20260314-0230.md          ← 定时任务备份
└── temp/
    ├── USER.md                        ← 预览文件（用户未确认）
    └── last_analysis.json             ← 时间戳
```

#### AI 确认安装完成

**AI 回复模板**：

```
✅ i-am Skill 安装完成！

📋 配置摘要:
- 模式：定时模式 / 手动模式
- Cron 任务：已配置 / 未配置
- 下次运行：2026-03-14 02:30 / 手动触发
- 初始备份：CHANGELOG/USER-20260313-1800-initial.md

📊 随时查看人格特质：查看当前对话的 USER.md 文件

需要现在运行一次分析吗？回复"是"或"否"
```

---

### 阶段 2: 运行分析（定时/手动触发）

#### 步骤 1: AI 加载用户语料

**AI 指引**：

```python
import json
from pathlib import Path
from datetime import datetime, timedelta

sessions_path = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
skill_root = Path.home() / ".openclaw" / "workspace" / "skills" / "i-am"
last_analysis_file = skill_root / "temp" / "last_analysis.json"

# 读取上次分析时间
if last_analysis_file.exists():
    with open(last_analysis_file, 'r', encoding='utf-8') as f:
        last_time = datetime.fromisoformat(json.load(f)['timestamp'])
else:
    last_time = datetime.now() - timedelta(hours=24)  # 首次运行加载 24 小时

# 扫描 sessions 提取新消息
messages = []
for session_file in sorted(sessions_path.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
    with open(session_file, 'r', encoding='utf-8') as f:
        for line in f:
            msg = json.loads(line)
            if msg.get('type') != 'message' or msg.get('message', {}).get('role') != 'user':
                continue
            
            msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00')).replace(tzinfo=None)
            if msg_time <= last_time:
                continue
            
            # 提取文本
            text = "".join([item.get('text', '') for item in msg['message']['content'] if isinstance(item, dict) and item.get('type') == 'text']).strip()
            
            # AI 自主判断：过滤系统消息
            if not text or text.startswith('[cron:') or text.startswith('Read HEARTBEAT') or text.startswith('A scheduled'):
                continue
            
            # AI 自主发现：Conversation info 中包含真实用户发言
            # 示例格式：
            # Conversation info (untrusted metadata):
            # ```json
            # {"sender": "UserName", "timestamp": "..."}
            # ```
            # [message_id: xxx] UserName：真实消息内容
            if 'Conversation info' in text:
                # AI 需要：
                # 1. 识别发送者（UserName）
                # 2. 编写正则表达式提取真实内容
                # 3. 验证发送者是当前用户
                # 4. 提取消息内容（长度>10 字）
                import re
                # 示例正则（AI 可根据实际格式调整）：
                match = re.search(r'\[message_id:[^\]]+\]\s*\n?([^:]+):(.+?)(?=\n\n|\Z)', text, re.DOTALL)
                if match:
                    sender = match.group(1).strip()
                    content = match.group(2).strip()
                    # AI 自主判断：发送者是否匹配当前用户
                    if sender in ['章伟伟', 'awei', '用户'] and len(content) > 10:
                        text = content
                    else:
                        continue
                else:
                    # AI 应尝试其他正则或格式
                    continue
            
            messages.append({'text': text, 'timestamp': msg_time})

# 设置上限
if len(messages) > 50:
    messages = messages[-50:]
    print(f"⚠️ 消息过多，只处理最近 50 条")

print(f"✅ 加载到 {len(messages)} 条新消息")
```

**AI 注意事项**：
- ✅ 首次运行时，sessions 目录下可能已有历史对话
- ✅ Conversation info 格式中包含真实用户发言，需要提取
- ✅ 不同 IM 渠道的消息格式可能不同，AI 应自主调整正则
- ✅ 提取后验证发送者是当前用户（不是系统通知）
- ✅ 消息内容应>10 字，避免太短的无意义消息

---

#### 步骤 2: AI 进行扎根理论分析

**核心原则**：不要预定义标签，从语料自然涌现！

**执行代码**：

```python
# 开放性编码：从语料自然涌现标签
open_codes = []
for msg in messages:
    text = msg['text']
    code, category = ai_extract_code_from_text(text)  # AI 自主理解
    if code:
        open_codes.append({"text": text, "code": code, "category": category})

# 主轴编码：聚类
axial_clusters = {}
for code in open_codes:
    cat = code['category']
    if cat not in axial_clusters:
        axial_clusters[cat] = {}
    axial_clusters[cat][code['code']] = axial_clusters[cat].get(code['code'], 0) + 1

# 选择性编码：提取核心特质（含范畴新增规则）
core_traits = {}

# 规则 1: 初次运行建议生成 3-5 个特质（太少不全面，太多不聚焦）
# 规则 2: 每个范畴至少有 2 个编码或总频次>=消息数的 10% 才保留
# 规则 3: 最多保留 7 个特质（按频次排序，取前 7 个）

for cat, labels in axial_clusters.items():
    total_count = sum(labels.values())
    
    # 判断是否新增/保留这个范畴
    if len(labels) < 2 and total_count < len(messages) * 0.1:
        # 范畴太小，跳过
        continue
    
    top_label, count = max(labels.items(), key=lambda x: x[1])
    
    # 初始饱和度计算：0.5 + (频次/总消息数)*0.5
    # 示例：4 条消息中有 2 条提到 → 饱和度 = 0.5 + (2/4)*0.5 = 0.75
    saturation = min(0.95, 0.5 + (count / max(len(messages), 1)) * 0.5)
    
    # 初次运行饱和度修正（避免单次分析饱和度过高）
    if cat not in historical_traits:
        saturation = min(saturation, 0.7)  # 初次最高 0.7
    
    # 置信度更新规则（不新增文件，内存计算）
    confidence = saturation
    if cat in historical_traits:  # 有历史记录
        old_value = historical_traits[cat].get('value', '')
        old_confidence = historical_traits[cat].get('confidence', 0.5)
        
        if top_label == old_value:
            # 一致：提升置信度
            confidence = min(0.95, old_confidence + 0.05)
        else:
            # 冲突：新说法权重更高
            confidence = max(0.6, saturation)  # 新特质至少 0.6
    
    core_traits[cat] = {
        "value": top_label,
        "saturation": saturation,
        "confidence": confidence,
        "level": "core" if confidence >= 0.7 else "secondary",
        "change": f"+{int((confidence-saturation)*100)}%" if confidence > saturation else f"{int((confidence-saturation)*100)}%"
    }

# 按频次排序，最多保留 7 个特质
core_traits = dict(sorted(core_traits.items(), 
                          key=lambda x: sum(axial_clusters[x[0]].values()), 
                          reverse=True)[:7])
```

**范畴新增规则**（AI 必须遵守）：

| 规则 | 说明 | 示例 |
|------|------|------|
| **最小频次** | 范畴总频次 >= 消息数×10% | 20 条消息 → 至少 2 条提到 |
| **最小多样性** | 范畴内至少 2 个不同编码 | "决策风格" 有"行动导向"+"谨慎思考" |
| **初次上限** | 初次运行最多 5 个特质 | 避免太多不聚焦 |
| **历史上限** | 有历史记录最多 7 个特质 | 保持稳定性 |
| **初次饱和度** | 初次分析饱和度最高 0.7 | 避免单次分析过高 |
| **历史饱和度** | 有历史记录按实际计算 | 可超过 0.7 |

**示例**：
```
输入：20 条用户消息
开放性编码：提取 35 个编码
主轴编码：聚类为 8 个范畴

选择性编码（应用规则）：
1. 决策风格：总频次 8 (40%) ✅ 保留
2. 沟通风格：总频次 6 (30%) ✅ 保留
3. 技术取向：总频次 5 (25%) ✅ 保留
4. 方法论：总频次 4 (20%) ✅ 保留
5. 情感表达：总频次 3 (15%) ✅ 保留
6. 学习风格：总频次 2 (10%) ✅ 保留（刚好达标）
7. 工作习惯：总频次 1 (5%)  ❌ 跳过（<10%）
8. 社交偏好：总频次 1 (5%)  ❌ 跳过（<10%）

输出：6 个核心特质（<7 个，符合规则）
```

**置信度规则**（AI 必须遵守）：

| 场景 | 置信度计算 |
|------|-----------|
| 首次分析 | `置信度 = 饱和度` |
| 与历史一致 | `新置信度 = 旧置信度 + 0.05` |
| 与历史冲突 | `新置信度 = max(0.6, 饱和度)`（新说法权重高） |
| 用户确认 | `置信度 +0.10`（最高 0.95） |

**AI 注意**：
- ❌ 不要预定义标签
- ✅ 置信度低于 0.5 的特质标注为"待验证"
- ✅ 新旧冲突时，优先采用新说法（用户可能改变了）
- ✅ 输出时必须显示饱和度变化（如 `+5%`、`-12%`）

---

#### 步骤 3: AI 生成预览文件

**执行代码**：

```python
from pathlib import Path

user_md_path = Path.home() / ".openclaw" / "workspace" / "USER.md"

# 读取当前 USER.md
if user_md_path.exists():
    with open(user_md_path, 'r', encoding='utf-8') as f:
        old_content = f.read()
else:
    old_content = "# USER.md - About Your Human\n\n## Context\n\n"

# 移除旧的人格特质部分
if "## 🧠 人格特质" in old_content:
    content = old_content.split("## 🧠 人格特质")[0]
else:
    content = old_content

# 生成新的人格特质
dynamic = "\n## 🧠 人格特质 (i-am 动态分析)\n\n"
for trait, data in core_traits.items():
    emoji = {"core": "🔴", "secondary": "🟡", "emerging": "🟢"}.get(data.get('level'), '🟢')
    dynamic += f"- {emoji} **{trait}**: {data['value']} (饱和度：{data['saturation']:.0%})\n"

# 保存到 temp/USER.md（预览文件，用户未确认）
temp_dir = skill_root / "temp"
temp_dir.mkdir(parents=True, exist_ok=True)
preview_file = temp_dir / "USER.md"

with open(preview_file, 'w', encoding='utf-8') as f:
    f.write(content.rstrip() + "\n" + dynamic + "\n")

print(f"✅ 预览已保存到：{preview_file}")
```

**注意**：
- ✅ 预览文件存在 `temp/USER.md`
- ❌ **此时不备份到 CHANGELOG/**
- ⏳ 等待用户确认

---

#### 步骤 4: AI 根据 IM 渠道发送预览文件

**AI 自主决策流程**：

1. **检测当前 IM 渠道**
   - 读取 inbound context 的 `channel` 字段
   - 可用值：`feishu`、`telegram`、`discord`、`whatsapp`、`signal` 等

2. **评估文件发送能力**
   - 检查该 IM 是否支持文件发送
   - 检查是否有已安装的 file-sender skill
   - 检查 IM 原生 API 是否支持

3. **选择最佳发送方式**（优先级从高到低）：
   - 优先：使用已安装的 file-sender skill（如 feishu-send-file）
   - 次优：使用 IM 原生文件发送功能
   - 降级：发送文字预览（前 1000 字）

4. **发送文件并请求确认**

**AI 回复模板**：

```
📋 USER.md 更新预览

检测到以下人格特质：

🔴 **沟通风格**: 直接高效
   饱和度：75% (+5%)  ← 显示变化
   置信度：80%

🔴 **决策风格**: 行动导向
   饱和度：68% (不变)
   置信度：73%

🟡 **技术取向**: 实用主义
   饱和度：52% (-10%)  ← 与历史冲突
   置信度：60%

📄 预览文件已发送（temp/USER.md）
📁 当前 USER.md 已备份到：CHANGELOG/USER-20260313-1730.md

🤖 请审核预览内容，确认是否更新 USER.md？
回复"确认"、"推送"、"是"或"ok"确认更新
回复"取消"、"否"或"不更新"取消
```

---

#### 步骤 5: AI 根据用户确认执行

**用户回复包含"确认"、"推送"、"是"、"ok"**：

```python
from datetime import datetime

# 读取预览文件
preview_file = skill_root / "temp" / "USER.md"
with open(preview_file, 'r', encoding='utf-8') as f:
    new_content = f.read()

# 覆盖写入 USER.md
user_md_path = Path.home() / ".openclaw" / "workspace" / "USER.md"
with open(user_md_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

# 更新时间戳
timestamp_file = skill_root / "temp" / "last_analysis.json"
with open(timestamp_file, 'w', encoding='utf-8') as f:
    json.dump({"timestamp": datetime.now().isoformat()}, f)

# 备份到 CHANGELOG/
changelog_dir = skill_root / "CHANGELOG"
changelog_dir.mkdir(parents=True, exist_ok=True)
backup_file = changelog_dir / f"USER-{datetime.now().strftime('%Y%m%d-%H%M')}.md"
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

# 用户确认后提升置信度
for trait in core_traits.values():
    trait['confidence'] = min(0.95, trait.get('confidence', 0.5) + 0.10)

print("✅ USER.md 已更新")
print(f"📁 已备份到：{backup_file.name}")
```

**AI 回复**：`✅ USER.md 已更新，{len(core_traits)} 个人格特质已写入。备份文件：CHANGELOG/USER-20260313-1805.md`

**用户回复包含"取消"、"否"、"不更新"**：

**AI 回复**：`❌ 已取消，USER.md 保持不变。备份文件已保存：CHANGELOG/USER-20260313-1730.md`

---

## 📊 CHANGELOG 机制

### 备份规则

**时机**：
- 每次分析前：备份当前 USER.md（用户审核前）
- 用户确认后：备份更新后的 USER.md（用户审核后）

**文件名格式**：
```
CHANGELOG/USER-YYYYMMDD-HHMM.md
```

**示例**：
```
CHANGELOG/
├── USER-20260313-1730.md  # 分析前的备份
├── USER-20260313-1735.md  # 用户确认后的备份
└── USER-20260314-0230.md  # 定时任务备份
```

### 用户撤回/检查变更

**查看变更历史**：
```bash
ls -lt skills/i-am/CHANGELOG/
```

**对比变更**：
```bash
# 对比最近两次备份
diff skills/i-am/CHANGELOG/USER-20260313-1730.md \
     skills/i-am/CHANGELOG/USER-20260313-1735.md
```

**撤回更改**：
```bash
# 恢复到之前的版本
cp skills/i-am/CHANGELOG/USER-20260313-1730.md ~/.openclaw/workspace/USER.md
```

---

## 🛠️ 配置参数

```yaml
# AI 可读的配置参数

analysis:
  min_messages: 5             # 最少消息数（不足则跳过）
  max_display: 20             # 最多显示 20 条消息
  
confirmation:
  interval_days: 7            # 每 7 天确认一次
  auto_approve_first: true    # 首次自动批准
  
saturation:
  core: 0.7                   # 核心特质阈值（>=0.7 为🔴）
  secondary: 0.5              # 次要特质阈值（0.5-0.7 为🟡）
  emerging: 0.3               # 涌现特质阈值（<0.5 为🟢）
```

---

## 📊 使用示例（AI 参考）

### 示例 1: 首次配置（用户安装 skill 后）

```
用户：[安装 i-am skill]

AI: （检测到新安装，主动触发配置流程）
    
    🧠 i-am Skill 配置向导
    
    请选择自动化模式：
    
    1️⃣ 定时模式（推荐）- 每天自动分析两次
    2️⃣ 手动模式 - 需要时手动运行
    
    请回复数字 1 或 2 选择：

用户：1

AI: （编辑 cron-tasks.json，添加定时任务）
    
    ✅ 定时模式已配置！
    
    📋 配置摘要:
    - 模式：定时模式
    - Cron 任务：已配置（2:30 AM & 2:30 PM）
    - 下次运行：2026-03-14 02:30
    
    回复"运行 i-am 分析"开始分析
```

### 示例 2: 运行分析（IM 自适应）

```
用户：运行 i-am 分析

AI: （执行步骤 1-4）
    
    📊 正在加载用户语料...
    ✅ 加载到 15 条新消息
    
    🧠 开始扎根理论分析...
    ✅ 提取到 4 个核心特质
    
    （检测当前渠道：feishu）
    （选择：使用 feishu-send-file skill 发送文件）
    
    📄 [发送文件：temp/USER.md]
    
    📋 USER.md 更新预览
    
    🔴 **沟通风格**: 直接高效 (75%)
    🔴 **决策风格**: 行动导向 (68%)
    🟡 **技术取向**: 实用主义 (52%)
    
    📁 当前 USER.md 已备份到：CHANGELOG/USER-20260313-1730.md
    
    🤖 预览文件已发送，请审核！
    
    确认是否更新 USER.md？
```

---

## 🔒 安全说明

**AI 必须遵守**：
- ✅ 所有数据本地处理，无网络传输
- ✅ 不需要额外 API key（使用当前会话模型）
- ✅ 用户确认后才更新 USER.md
- ✅ 预览文件供用户审核
- ✅ 每次变更自动备份到 CHANGELOG/

---

