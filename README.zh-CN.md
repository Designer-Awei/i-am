# i-am Skill - 用户人格模型持续进化

> **我即用户，用户即我** - 通过实时对话监控 + 扎根理论 + ACT-R，成为最懂你的 AI 助手

**[🌏 English](README.md)** | **[🇨🇳 中文](README.zh-CN.md)**

---

**版本**: v2.0 (网关集成版)  
**理论**: 经典扎根理论 + ACT-R 认知架构  
**目标**: 实时分析用户对话，持续完善 USER.md 人格模型

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/Designer-Awei/i-am.git ~/.openclaw/workspace/skills/i-am

# 安装依赖
pip3 install watchdog

# 启用网关集成
cd ~/.openclaw/workspace/skills/i-am
./scripts/gateway-integration.sh enable
```

### 2. 查看状态

```bash
# 查看运行状态
./scripts/gateway-integration.sh status

# 查看实时日志
tail -f logs/watcher.log

# 查看统计数据
ls -1 data/realtime/codes_*.json | wc -l  # 编码次数
ls -1 data/realtime/feedback_*.json | wc -l  # ACT-R 反馈次数
```

### 3. 配置

编辑 `config/config.yaml`:

```yaml
# 批次处理触发条件
realtime_monitor:
  batch_trigger:
    conversation_count: 10    # 每 10 条用户消息触发扎根理论
    time_interval_minutes: 60 # 或每 60 分钟触发

# 每日复盘 (ACT-R)
  daily_review:
    enabled: true
    time: "03:00"             # 每天凌晨 3:00
```

---

## 📊 核心功能

### 1. 实时对话监控

**通过文件监控器实时拦截 OpenClaw 对话**:

```
用户消息 → 飞书 → OpenClaw 网关
                   ↓
            sessions/*.jsonl (增量写入)
                   ↓ (watchdog 监控)
            i_am_watcher 检测到变化
                   ↓
            只提取用户消息（AI 回复不加入 batch）
```

**关键设计**:
- ✅ **只分析用户消息** - 避免 AI 回复污染扎根理论
- ✅ **AI 回复作为上下文** - 帮助 ACT-R 理解用户反应
- ✅ **增量读取** - 只处理新增消息，不重复分析

### 2. 扎根理论引擎

**自动从用户对话中提取人格特质**:

```
用户："兄弟，直接点，别整没用的"
  ↓
开放性编码 → ["偏好直接沟通", "厌恶客套"]
  ↓
主轴编码 → 【沟通风格：直截了当型】
  ↓
选择性编码 → 更新 USER.md，饱和度 92%
```

**批次处理**:
- **触发条件**: 每 10 条用户消息 或 每 60 分钟
- **数据源**: 只使用用户消息（纯净无噪声）
- **输出**: 核心人格特质 + 饱和度评分

### 3. ACT-R 隐式反馈

**从对话中推断用户满意度**:

| 用户说 | AI 回复 | 推断 | 规则调整 |
|--------|--------|------|---------|
| "牛逼" | 方案 A | 正面 | 强度 +10% |
| "不对" | 方案 B | 负面 | 强度 -15% |
| "继续" | 方案 C | 正面 | 强度 +15% |

**每日复盘**:
- **时间**: 每天凌晨 3:00
- **范围**: 过去 24 小时对话
- **输出**: ACT-R 规则强度更新

### 4. 自动批次处理

**无需手动干预**:

- 每 10 条用户消息 → 触发扎根理论完整流程
- 每 60 分钟 → 强制触发（即使不足 10 条）
- 每天 3:00 → ACT-R 深度复盘

**守护进程**:
- 文件监控器后台运行
- 自动检测新对话
- 实时开放性编码 + ACT-R 反馈
- 达到阈值自动批次处理

---

## 🎯 使用场景

### 场景 1: 实时人格分析

**适合**: 希望 AI 快速了解自己的用户

**配置**:
```yaml
batch_trigger:
  conversation_count: 5   # 每 5 条消息触发
  time_interval_minutes: 30
```

**效果**: AI 在几次对话后就能掌握你的沟通风格

### 场景 2: 深度自我探索

**适合**: 希望通过对话反思自己的用户

**配置**:
```yaml
batch_trigger:
  conversation_count: 20  # 累积更多数据
  time_interval_minutes: 120

daily_review:
  enabled: true
  time: "03:00"
```

**效果**: 每天生成深度人格分析报告

### 场景 3: 团队协作分析

**适合**: 分析团队成员沟通风格

**配置**:
```yaml
# 多用户支持（未来功能）
multi_user:
  enabled: true
  users:
    - open_id: "ou_xxx"
      name: "张三"
    - open_id: "ou_yyy"
      name: "李四"
```

---

## 📁 目录结构

```
i-am/
├── SKILL.md                          # Skill 入口
├── README.md                         # 英文文档
├── README.zh-CN.md                   # 中文文档
├── WORK_FLOW.md                      # 工作流程
├── config/
│   └── config.yaml                   # 配置文件
├── scripts/
│   ├── i_am_watcher.py               # 🔥 实时监控器（新增）
│   ├── i_am_batch_runner.py          # 🔥 批次运行器（新增）
│   ├── gateway-integration.sh        # 🔥 网关集成脚本（新增）
│   ├── open_coding.py                # 开放性编码
│   ├── actr_feedback.py              # ACT-R 反馈
│   ├── user_md_sync.py               # USER.md 同步
│   └── conversation_recorder.py      # 对话记录器
├── grounding_theory/                 # 扎根理论数据
├── actr/                             # ACT-R 数据
├── data/
│   ├── realtime/                     # 🔥 实时数据（新增）
│   │   ├── codes_*.json             # 开放性编码结果
│   │   ├── feedback_*.json          # ACT-R 反馈结果
│   │   └── batch_*.json             # 批次处理数据
│   └── batch_runs/                   # 批次运行结果
├── user_md_sync/
│   ├── backup/                       # USER.md 备份
│   └── change_log.md                 # 变更日志
└── logs/
    └── watcher.log                   # 🔥 监控器日志（新增）
```

---

## 🔧 网关集成

### 启用监控

```bash
cd ~/.openclaw/workspace/skills/i-am
./scripts/gateway-integration.sh enable
```

**输出**:
```
✅ i-am 实时监控已启用！

📊 配置信息:
   PID: 45798
   批次处理：每 10 条用户消息触发扎根理论
   每日复盘：凌晨 3:00 (ACT-R)

📄 日志文件:
   logs/watcher.log
```

### 查看状态

```bash
./scripts/gateway-integration.sh status
```

**输出**:
```
✅ 运行中 (PID: 45798)

📈 统计数据:
   开放性编码：15 次
   ACT-R 反馈：15 次
```

### 禁用监控

```bash
./scripts/gateway-integration.sh disable
```

---

## 🛠️ 故障排查

### 问题 1: 监控器未启动

**检查**:
```bash
./scripts/gateway-integration.sh status
```

**解决**:
```bash
./scripts/gateway-integration.sh enable
```

### 问题 2: 没有编码结果

**检查日志**:
```bash
tail -f logs/watcher.log | grep "开放性编码"
```

**可能原因**:
- 对话都是系统消息（被过滤）
- 监控器未正确启动

### 问题 3: 批次处理未触发

**检查**:
```bash
grep "批次处理" logs/watcher.log
```

**手动触发**:
```bash
python3 scripts/i_am_batch_runner.py test --hours 1
```

---

## 📊 性能指标

### 延迟

| 阶段 | 延迟 | 说明 |
|------|------|------|
| 消息写入 → 检测到 | <100ms | 文件系统监控 |
| 检测到 → 开放性编码 | <500ms | 规则匹配 |
| 检测到 → ACT-R 反馈 | <500ms | 模式匹配 |
| 达到阈值 → 批次处理 | <2s | 完整工作流 |

### 资源占用

| 指标 | 值 | 说明 |
|------|-----|------|
| CPU | <1% | 后台监控 |
| 内存 | ~50MB | Python 进程 |
| 磁盘 IO | 低 | 增量读取 |
| 网络 | 无 | 本地运行 |

---

## 📝 常见问题

### Q: 安装后需要重启网关吗？

**A: 不需要！**

i-am 作为独立监控器运行：
- ✅ 通过文件监控 sessions 目录
- ✅ 不修改 OpenClaw 网关代码
- ✅ 不依赖网关插件系统
- ✅ 随时启用/禁用，不影响网关

### Q: 为什么只用用户消息做扎根理论？

**A: 避免 AI 回复污染数据**

- 扎根理论的核心是从**用户自然表达**中归纳特质
- AI 回复是"生成的"，不是"用户的真实想法"
- 混入 AI 回复会导致编码结果失真

### Q: ACT-R 反馈需要 AI 回复吗？

**A: 需要，但只作为上下文**

- ACT-R 需要分析"用户对 AI 回复的反应"
- 例如：用户说"不对，换个方案" → 负面反馈
- 但 AI 回复本身不加入扎根理论 batch

### Q: 每日复盘几点执行？

**A: 默认凌晨 3:00（可配置）**

```yaml
daily_review:
  time: "03:00"  # 修改为其他时间
```

### Q: 支持 Windows 吗？

**A: 支持！**

- watchdog 库跨平台（macOS/Windows/Linux）
- 批次处理脚本用 Python 编写
- 每日复盘用系统定时任务（cron/Task Scheduler）

---

## 📞 支持

**GitHub Issues**: https://github.com/Designer-Awei/i-am/issues  
**作者**: 龙傲天  
**许可**: MIT

---

## 📝 更新日志

### v2.0 (2026-03-12) - 网关集成版

**新增**:
- ✅ 实时监控器（i_am_watcher.py）
- ✅ 批次运行器（i_am_batch_runner.py）
- ✅ 网关集成脚本（gateway-integration.sh）
- ✅ 只使用用户消息进行扎根理论（避免 AI 噪声）
- ✅ AI 回复作为 ACT-R 上下文
- ✅ 每 10 条用户消息自动触发批次处理
- ✅ 每日凌晨 3:00 ACT-R 深度复盘

**优化**:
- ✅ 增量读取 sessions 文件（不重复分析）
- ✅ 分开存储编码结果和反馈结果
- ✅ 完善日志系统（watcher.log）

### v1.0 (2026-03-12) - 初始版本

- ✅ 扎根理论引擎（开放性/主轴/选择性编码）
- ✅ ACT-R 认知架构（隐式反馈/规则更新）
- ✅ 主动验证机制
- ✅ 用户手册和文档

---

*发布：i-am Skill v2.0 | 2026-03-12*  
*网关集成 · 实时监控 · 纯净数据*
