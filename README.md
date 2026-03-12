# i-am Skill - Continuous User Personality Evolution

> **I am You, You am I** - Real-time conversation monitoring + Grounded Theory + ACT-R to become the AI assistant that knows you best

**[🌏 English](README.md)** | **[🇨🇳 中文](README.zh-CN.md)**

---

**Version**: v2.0 (Gateway Integrated)  
**Theory**: Classical Grounded Theory + ACT-R Cognitive Architecture  
**Goal**: Real-time conversation analysis for continuous USER.md personality model refinement

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Designer-Awei/i-am.git ~/.openclaw/workspace/skills/i-am

# Install dependencies
pip3 install watchdog

# Enable gateway integration
cd ~/.openclaw/workspace/skills/i-am
./scripts/gateway-integration.sh enable
```

### 2. Check Status

```bash
# View running status
./scripts/gateway-integration.sh status

# View real-time logs
tail -f logs/watcher.log

# View statistics
ls -1 data/realtime/codes_*.json | wc -l  # Coding count
ls -1 data/realtime/feedback_*.json | wc -l  # ACT-R feedback count
```

### 3. Configuration

Edit `config/config.yaml`:

```yaml
# Batch processing trigger
realtime_monitor:
  batch_trigger:
    conversation_count: 10    # Trigger grounded theory every 10 user messages
    time_interval_minutes: 60 # Or every 60 minutes

# Daily review (ACT-R)
  daily_review:
    enabled: true
    time: "03:00"             # Daily at 3:00 AM
```

---

## 📊 Core Features

### 1. Real-time Conversation Monitoring

**Intercept OpenClaw conversations via file watcher**:

```
User Message → Feishu → OpenClaw Gateway
                        ↓
                 sessions/*.jsonl (incremental write)
                        ↓ (watchdog monitor)
                 i_am_watcher detects change
                        ↓
                 Extract user messages only (AI replies excluded from batch)
```

**Key Design**:
- ✅ **User messages only** - Avoid AI reply contamination in grounded theory
- ✅ **AI replies as context** - Help ACT-R understand user reactions
- ✅ **Incremental reading** - Only process new messages, no re-analysis

### 2. Grounded Theory Engine

**Automatically extract personality traits from user conversations**:

```
User: "Brother, be direct, cut the crap"
  ↓
Open Coding → ["prefer direct communication", "dislike formalities"]
  ↓
Axial Coding → [Communication Style: Direct Type]
  ↓
Selective Coding → Update USER.md, 92% saturation
```

**Batch Processing**:
- **Trigger**: Every 10 user messages OR every 60 minutes
- **Data Source**: User messages only (pure, no noise)
- **Output**: Core personality traits + saturation scores

### 3. ACT-R Implicit Feedback

**Infer user satisfaction from conversations**:

| User Says | AI Reply | Inference | Rule Adjustment |
|-----------|----------|-----------|----------------|
| "Awesome" | Plan A | Positive | Strength +10% |
| "Wrong" | Plan B | Negative | Strength -15% |
| "Continue" | Plan C | Positive | Strength +15% |

**Daily Review**:
- **Time**: 3:00 AM daily
- **Scope**: Past 24 hours conversations
- **Output**: ACT-R rule strength updates

### 4. Automatic Batch Processing

**No manual intervention needed**:

- Every 10 user messages → Trigger full grounded theory workflow
- Every 60 minutes → Force trigger (even if <10 messages)
- Daily 3:00 AM → ACT-R deep review

**Daemon**:
- File watcher runs in background
- Auto-detect new conversations
- Real-time open coding + ACT-R feedback
- Auto batch processing when threshold reached

---

## 🎯 Usage Scenarios

### Scenario 1: Real-time Personality Analysis

**For**: Users who want AI to understand them quickly

**Config**:
```yaml
batch_trigger:
  conversation_count: 5   # Trigger every 5 messages
  time_interval_minutes: 30
```

**Effect**: AI masters your communication style after a few conversations

### Scenario 2: Deep Self-Exploration

**For**: Users who want to reflect on themselves through conversations

**Config**:
```yaml
batch_trigger:
  conversation_count: 20  # Accumulate more data
  time_interval_minutes: 120

daily_review:
  enabled: true
  time: "03:00"
```

**Effect**: Daily deep personality analysis report

### Scenario 3: Team Collaboration Analysis

**For**: Analyzing team member communication styles

**Config**:
```yaml
# Multi-user support (future feature)
multi_user:
  enabled: true
  users:
    - open_id: "ou_xxx"
      name: "Zhang San"
    - open_id: "ou_yyy"
      name: "Li Si"
```

---

## 📁 Directory Structure

```
i-am/
├── SKILL.md                          # Skill entry
├── README.md                         # English documentation
├── README.zh-CN.md                   # Chinese documentation
├── WORK_FLOW.md                      # Work flow
├── config/
│   └── config.yaml                   # Configuration
├── scripts/
│   ├── i_am_watcher.py               # 🔥 Real-time watcher (NEW)
│   ├── i_am_batch_runner.py          # 🔥 Batch runner (NEW)
│   ├── gateway-integration.sh        # 🔥 Gateway integration (NEW)
│   ├── open_coding.py                # Open coding
│   ├── actr_feedback.py              # ACT-R feedback
│   ├── user_md_sync.py               # USER.md sync
│   └── conversation_recorder.py      # Conversation recorder
├── grounding_theory/                 # Grounded theory data
├── actr/                             # ACT-R data
├── data/
│   ├── realtime/                     # 🔥 Real-time data (NEW)
│   │   ├── codes_*.json             # Open coding results
│   │   ├── feedback_*.json          # ACT-R feedback results
│   │   └── batch_*.json             # Batch processing data
│   └── batch_runs/                   # Batch run results
├── user_md_sync/
│   ├── backup/                       # USER.md backups
│   └── change_log.md                 # Change log
└── logs/
    └── watcher.log                   # 🔥 Watcher logs (NEW)
```

---

## 🔧 Gateway Integration

### Enable Monitoring

```bash
cd ~/.openclaw/workspace/skills/i-am
./scripts/gateway-integration.sh enable
```

**Output**:
```
✅ i-am real-time monitoring enabled!

📊 Configuration:
   PID: 45798
   Batch: Grounded theory every 10 user messages
   Daily review: 3:00 AM (ACT-R)

📄 Log file:
   logs/watcher.log
```

### Check Status

```bash
./scripts/gateway-integration.sh status
```

**Output**:
```
✅ Running (PID: 45798)

📈 Statistics:
   Open coding: 15 times
   ACT-R feedback: 15 times
```

### Disable Monitoring

```bash
./scripts/gateway-integration.sh disable
```

---

## 🛠️ Troubleshooting

### Problem 1: Watcher Not Started

**Check**:
```bash
./scripts/gateway-integration.sh status
```

**Solution**:
```bash
./scripts/gateway-integration.sh enable
```

### Problem 2: No Coding Results

**Check logs**:
```bash
tail -f logs/watcher.log | grep "Open Coding"
```

**Possible causes**:
- All messages are system messages (filtered out)
- Watcher not started correctly

### Problem 3: Batch Processing Not Triggered

**Check**:
```bash
grep "Batch" logs/watcher.log
```

**Manual trigger**:
```bash
python3 scripts/i_am_batch_runner.py test --hours 1
```

---

## 📊 Performance Metrics

### Latency

| Stage | Latency | Description |
|-------|---------|-------------|
| Message write → Detect | <100ms | File system watch |
| Detect → Open coding | <500ms | Pattern matching |
| Detect → ACT-R feedback | <500ms | Pattern matching |
| Threshold → Batch processing | <2s | Full workflow |

### Resource Usage

| Metric | Value | Description |
|--------|-------|-------------|
| CPU | <1% | Background monitoring |
| Memory | ~50MB | Python process |
| Disk IO | Low | Incremental reading |
| Network | None | Local execution |

---

## 📝 FAQ

### Q: Do I need to restart the gateway after installation?

**A: No!**

i-am runs as an independent monitor:
- ✅ Monitors sessions directory via file watcher
- ✅ Does not modify OpenClaw gateway code
- ✅ Does not depend on gateway plugin system
- ✅ Enable/disable anytime, no gateway impact

### Q: Why use user messages only for grounded theory?

**A: Avoid AI reply contamination**

- Grounded theory's core is inductive reasoning from **user's natural expressions**
- AI replies are "generated", not "user's true thoughts"
- Mixing AI replies distorts coding results

### Q: Does ACT-R feedback need AI replies?

**A: Yes, but only as context**

- ACT-R needs to analyze "user's reaction to AI reply"
- Example: User says "Wrong, different approach" → Negative feedback
- But AI reply itself is NOT added to grounded theory batch

### Q: What time is the daily review?

**A: Default 3:00 AM (configurable)**

```yaml
daily_review:
  time: "03:00"  # Change to other time
```

### Q: Does it support Windows?

**A: Yes!**

- watchdog library is cross-platform (macOS/Windows/Linux)
- Batch processing scripts are in Python
- Daily review uses system scheduler (cron/Task Scheduler)

---

## 📞 Support

**GitHub Issues**: https://github.com/Designer-Awei/i-am/issues  
**Author**: Dragon Aotian  
**License**: MIT

---

## 📝 Changelog

### v2.0 (2026-03-12) - Gateway Integrated

**New**:
- ✅ Real-time watcher (i_am_watcher.py)
- ✅ Batch runner (i_am_batch_runner.py)
- ✅ Gateway integration script (gateway-integration.sh)
- ✅ User messages only for grounded theory (avoid AI noise)
- ✅ AI replies as ACT-R context
- ✅ Auto batch processing every 10 user messages
- ✅ Daily 3:00 AM ACT-R deep review

**Optimized**:
- ✅ Incremental sessions reading (no re-analysis)
- ✅ Separate storage for coding and feedback results
- ✅ Complete logging system (watcher.log)

### v1.0 (2026-03-12) - Initial Release

- ✅ Grounded Theory engine (open/axial/selective coding)
- ✅ ACT-R cognitive architecture (implicit feedback/rule update)
- ✅ Active verification mechanism
- ✅ User manual and documentation

---

*Release: i-am Skill v2.0 | 2026-03-12*  
*Gateway Integrated · Real-time Monitoring · Pure Data*
