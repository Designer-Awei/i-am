# i-am Skill 架构设计文档

**版本**: v1.0  
**最后更新**: 2026-03-11

---

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                          │
│                                                                  │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐            │
│  │  用户消息   │ →  │  i-am Hook  │ →  │  AI 回复    │            │
│  └────────────┘    └────────────┘    └────────────┘            │
│                          ↓                                       │
│                   ┌──────────────┐                              │
│                   │  对话记录器   │                              │
│                   └──────────────┘                              │
│                          ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    i-am 后台处理                          │   │
│  │                                                           │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │   │
│  │  │ 开放性编码   │ →  │ ACT-R 反馈   │ →  │ 对话缓存    │  │   │
│  │  └─────────────┘    └─────────────┘    └─────────────┘  │   │
│  │                                           ↓                │   │
│  │  ┌─────────────────────────────────────────────┐          │   │
│  │  │           批次处理触发器                     │          │   │
│  │  │  - 每 10 次对话                               │          │   │
│  │  │  - 或每 24 小时                               │          │   │
│  │  │  - 或用户手动触发                            │          │   │
│  │  └─────────────────────────────────────────────┘          │   │
│  │                                           ↓                │   │
│  │  ┌─────────────┐    ┌─────────────┐                       │   │
│  │  │ 主轴编码     │ →  │ USER.md 同步  │                       │   │
│  │  └─────────────┘    └─────────────┘                       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 数据存储结构

### 1. 对话记录存储

**位置**: `~/.openclaw/workspace/skills/i-am/data/conversations/`

**文件命名**: `conv_YYYYMMDD_HHMMSS.json`

**格式**:
```json
{
  "session_id": "20260311_225300",
  "timestamp": "2026-03-11T22:53:00+08:00",
  "user_message": "兄弟，直接点",
  "ai_prediction": {
    "style": "直接",
    "action": "省略客套话"
  },
  "ai_response": "行，你说。",
  "user_feedback": "好的，就这样",
  "inferred_feedback": {
    "type": "positive",
    "strength": 0.1,
    "signals": ["好的", "就这样"]
  },
  "processed": false,
  "open_coding": null
}
```

### 2. 编码结果存储

**位置**: `grounding_theory/open_coding/session_YYYYMMDD.json`

**格式**:
```json
{
  "session_id": "20260311",
  "timestamp": "2026-03-11T23:00:00+08:00",
  "conversation_ids": ["20260311_225300", "20260311_225500"],
  "codes": [
    {
      "text": "兄弟，直接点",
      "label": "偏好直接沟通",
      "category": "沟通风格"
    }
  ],
  "statistics": {
    "total_codes": 5,
    "categories": {
      "沟通风格": 3,
      "决策风格": 2
    }
  }
}
```

### 3. 核心人格模型

**位置**: `grounding_theory/selective_coding/core_model.json`

**格式**:
```json
{
  "version": "v1.0",
  "last_updated": "2026-03-11T23:00:00+08:00",
  "core_traits": [
    {
      "name": "沟通风格",
      "value": "直截了当型",
      "saturation": 0.92,
      "evidence_count": 23
    }
  ],
  "history": [
    {
      "version": "v0.9",
      "updated": "2026-03-10T23:00:00+08:00",
      "changes": ["新增特质：决策风格"]
    }
  ]
}
```

### 4. ACT-R 产生式规则

**位置**: `actr/procedural_memory/production_rules.json`

**格式**:
```json
{
  "productions": [
    {
      "name": "回复风格选择",
      "condition": "IF 用户=章伟伟 AND 场景=日常对话",
      "action": "THEN 使用直接语气",
      "strength": 0.95,
      "success_rate": 0.98,
      "last_verified": "2026-03-11T22:53:00+08:00"
    }
  ]
}
```

---

## 🔄 工作流程

### 模式 1: 实时 Hook 模式（推荐）

**触发时机**: 每次用户消息

**流程**:
```
1. 用户发送消息
   ↓
2. i-am Hook 拦截（作为 OpenClaw 中间件）
   ↓
3. 记录对话到 data/conversations/
   ↓
4. 实时开放性编码（提取标签）
   ↓
5. 更新 ACT-R 隐式反馈
   ↓
6. AI 生成回复（使用最新的人格模型）
   ↓
7. 等待用户反馈（下一条消息）
   ↓
8. 回到步骤 3
```

**批次处理触发条件**（任一满足即触发）:
- 累积 10 次未处理对话
- 距离上次处理超过 24 小时
- 用户手动触发命令

### 模式 2: 间歇式批次处理

**触发时机**: 用户手动执行命令

**流程**:
```
1. 用户执行：python scripts/i_am.py update
   ↓
2. 读取所有未处理的对话记录
   ↓
3. 批量开放性编码
   ↓
4. 主轴编码（聚类）
   ↓
5. 选择性编码（更新核心模型）
   ↓
6. ACT-R 效用学习
   ↓
7. 合并更新 USER.md
   ↓
8. 标记对话为已处理
```

---

## ⚙️ 配置选项

### 工作模式配置

```yaml
# config/config.yaml

mode:
  # 实时 Hook 模式
  realtime_hook:
    enabled: true           # 是否启用实时拦截
    log_all: true           # 记录所有对话
    skip_patterns:          # 跳过的对话类型
      - "heartbeat"
      - "system_command"
  
  # 批次处理
  batch_processing:
    enabled: true
    trigger:
      conversation_count: 10   # 累积多少次对话
      time_interval_hours: 24  # 或多少小时
      manual_only: false       # 仅手动触发
```

### 对话来源配置

```yaml
data_sources:
  # OpenClaw 会话历史
  openclaw_sessions:
    enabled: true
    path: "~/.openclaw/agents/main/sessions/"
    format: "jsonl"
  
  # 直接消息拦截
  message_hook:
    enabled: true
    channel: "feishu"  # 或 "all"
  
  # 手动导入
  manual_import:
    enabled: true
    directory: "data/imports/"
```

---

## 📊 性能优化

### 1. 增量处理

- 只处理未处理的对话
- 使用文件锁避免并发冲突
- 异步处理，不阻塞主流程

### 2. 缓存策略

- 标签库缓存在内存
- 产生式规则缓存（避免重复加载）
- 对话记录分批加载

### 3. 存储优化

- 对话记录按天分文件
- 超过 30 天的记录压缩归档
- 编码结果索引化

---

## 🔧 与 OpenClaw 集成

### 方案 A: OpenClaw Hook（推荐）

在 OpenClaw 的消息处理流程中插入 Hook：

```python
# ~/.openclaw/plugins/i_am_hook.py

from openclaw.hooks import MessageHook
from i_am.scripts.iam_skill import IAMSkill

class IAMMessageHook(MessageHook):
    def __init__(self):
        self.skill = IAMSkill()
    
    def on_message_received(self, message):
        # 记录对话
        self.skill.record_conversation(message)
        
        # 实时编码
        self.skill.process_realtime(message)
    
    def on_response_sent(self, response):
        # 记录 AI 预测
        self.skill.record_prediction(response)
```

### 方案 B: 独立进程（简单）

作为独立进程运行，定期扫描 OpenClaw 日志：

```bash
# 后台运行
python scripts/i_am_daemon.py &

# 或作为 systemd 服务
[Unit]
Description=i-am Skill Daemon
After=openclaw.service

[Service]
ExecStart=/usr/bin/python3 /path/to/i_am/scripts/i_am_daemon.py
Restart=always
```

---

## 📝 使用示例

### 实时模式

```bash
# 1. 启用 Hook
python scripts/i_am.py hook enable

# 2. 查看状态
python scripts/i_am.py status

# 输出:
# Mode: Realtime Hook (enabled)
# Pending conversations: 5
# Last batch processing: 2 hours ago
```

### 批次模式

```bash
# 1. 手动触发批次处理
python scripts/i_am.py update --sessions 20260311

# 2. 导出模型
python scripts/i_am.py export --output ~/Desktop/user_model.json

# 3. 查看变更日志
cat user_md_sync/change_log.md
```

### 查看对话记录

```bash
# 列出所有对话记录
ls -la data/conversations/

# 查看特定对话
cat data/conversations/conv_20260311_225300.json

# 统计未处理对话
python scripts/i_am.py stats
```

---

## 🎯 推荐配置

**对于间歇式对话用户**（如你）:

```yaml
mode:
  realtime_hook:
    enabled: false        # 不启用实时拦截
  batch_processing:
    enabled: true
    trigger:
      conversation_count: 5    # 累积 5 次就处理
      time_interval_hours: 12  # 或 12 小时
      manual_only: false
```

**理由**:
- 你不会连续对话，实时模式浪费资源
- 批次处理效率高，每次处理有足够数据
- 12 小时间隔保证每天至少处理 2 次

---

## ❓ 回答你的问题

### Q1: 当前是按批次读取对话记录吗？

**A**: 是的，当前设计是批次处理。但我正在改造成**实时 Hook + 批次处理混合模式**。

### Q2: 对话从哪里获取？怎么存储？

**A**: 
- **来源**: 当前需要手动传入 → 改造后从 OpenClaw 会话历史自动获取
- **存储**: `data/conversations/conv_YYYYMMDD_HHMMSS.json`

### Q3: i-am 的工作方式？

**A**: 
- **当前**: 间歇式批次处理（手动触发）
- **目标**: 实时 Hook（始终在线）+ 批次处理（后台运行）

---

## 🚀 下一步

1. **创建对话记录器** - 自动从 OpenClaw 获取会话
2. **实现 Hook 集成** - 作为 OpenClaw 插件
3. **配置 Daemon 进程** - 后台持续运行
4. **完善 USER.md 同步** - 自动备份 + 变更追踪

---

*文档版本：1.0*  
*最后更新：2026-03-11 22:53*
