---
name: i-am
version: 2.0.2
description: Twice-daily personality analysis skill. Uses ACT-R + Grounded Theory to analyze OpenClaw sessions and auto-update USER.md. Runs at 2:30 AM & 2:30 PM via OpenClaw cron.
license: MIT
---

# i-am Skill - Twice-Daily Personality Analysis

> **I am You, You am I** - Automated twice-daily personality analysis using ACT-R + Grounded Theory

**[🌏 English](README.md)** | **[🇨🇳 中文](README.zh-CN.md)**

---

## ⚠️ Security Notes

**File Access**:
- Read: `~/.openclaw/agents/main/sessions/*.jsonl` (conversation history)
- Write: `~/.openclaw/workspace/USER.md` (user personality model)
- Write: `data/daily_runs/` (analysis results)

**Network**: No external network calls. All data stays local.

**Privacy**: Sessions contain conversation history. Review code before running.

**Automation**: Default runs twice daily at 2:30 AM & 2:30 PM via OpenClaw cron.

---

## 🚀 Quick Start

### Installation

```bash
# Clone to skills directory
git clone https://github.com/Designer-Awei/i-am.git ~/.openclaw/workspace/skills/i-am
cd ~/.openclaw/workspace/skills/i-am

# Install Python dependencies
pip3 install watchdog

# Run installer (asks for mode, default: scheduled)
python3 scripts/install.py
```

**Installer will ask / 安装程序会询问**:
1. Scheduled Mode (Default) / 定时模式（默认） - Auto twice daily at 2:30 AM & 2:30 PM
2. Manual Mode / 手动模式 - Run when needed

---

## 🎯 What This Skill Does

**i-am** performs twice-daily personality analysis:

1. **Load New Sessions** - Only sessions since last analysis
2. **ACT-R Feedback** - Analyze user satisfaction patterns
3. **Grounded Theory** - Extract personality traits (Open/Axial/Selective Coding)
4. **Update USER.md** - Merge insights into personality model

**Schedule**: Twice daily at 2:30 AM & 2:30 PM (configurable)

**When to use**:
- You want AI to understand your communication style
- You need personality-based AI responses
- You want automated twice-daily analysis

---

## 📊 How It Works

### Daily Flow (Scheduled Mode)

```
2:30 AM → OpenClaw cron triggers i-am (morning)
    ↓
Load sessions since yesterday's PM analysis
    ↓
Run ACT-R + Grounded Theory
    ↓
Update USER.md
    ↓
Save timestamp

2:30 PM → OpenClaw cron triggers i-am (afternoon)
    ↓
Load sessions since morning analysis
    ↓
Run ACT-R + Grounded Theory
    ↓
Update USER.md
    ↓
Save timestamp
```

### Analysis Process

```
Sessions (since last run)
    ↓
ACT-R Analysis:
  - Positive feedback: X
  - Negative feedback: Y
  - Neutral: Z
    ↓
Grounded Theory:
  - Open Coding: extract labels
  - Axial Coding: cluster categories
  - Selective Coding: core traits
    ↓
USER.md Update:
  - Communication Style
  - Decision Style
  - Technical Focus
  - ACT-R rule adjustments
```

---

## 🔧 Installation Modes

### Mode 1: Scheduled (Default, Recommended)

**What happens**: OpenClaw cron runs analysis twice daily at 2:30 AM & 2:30 PM

**Configuration**:
- Added to: `~/.openclaw/cron/cron-tasks.json`
- Schedule 1: `30 2 * * *` (2:30 AM)
- Schedule 2: `30 14 * * *` (2:30 PM)
- Timezone: Asia/Shanghai

**Usage**:
```bash
# Analysis runs automatically twice daily
# Check config: cat ~/.openclaw/cron/cron-tasks.json | grep -A 10 "i-am"

# Manual analysis anytime
python3 scripts/i_am_daily_analysis.py
```

**Pros**:
- ✅ Fully automated
- ✅ Runs twice daily without forgetting
- ✅ Uses OpenClaw's built-in cron
- ✅ No background daemon

**Cons**:
- ⚠️ Fixed schedule (2:30 AM & 2:30 PM daily)

---

### Mode 2: Manual

**What happens**: Analysis runs only when you execute the command

**Usage**:
```bash
python3 scripts/i_am_daily_analysis.py
```

**Pros**:
- ✅ Full control
- ✅ No automation
- ✅ Run when you want

**Cons**:
- ⚠️ Must remember to run
- ⚠️ No automatic updates

---

## 📁 Directory Structure

```
i-am/
├── SKILL.md                          # Skill entry
├── README.md                         # English docs
├── README.zh-CN.md                   # Chinese docs
├── clawhub.yaml                      # ClawHub config
├── scripts/
│   ├── install.py                    # Installer (asks for mode)
│   ├── i_am_daily_analysis.py        # Main analysis (ACT-R + Grounded Theory)
│   ├── auto_discover.py              # History discovery
│   ├── open_coding.py                # Open coding engine
│   ├── actr_feedback.py              # ACT-R feedback engine
│   └── user_md_sync.py               # USER.md sync engine
├── config/
│   └── config.yaml                   # Analysis config
├── data/
│   └── daily_runs/                   # Daily analysis results
├── grounding_theory/                 # Grounded theory data
├── actr/                             # ACT-R data
└── user_md_sync/
    └── change_log.md                 # USER.md change log
```

---

## 🔍 Usage Examples

### Check Analysis Results

```bash
# Check USER.md
cat ~/.openclaw/workspace/USER.md

# Check latest analysis results
ls -lt data/daily_runs/
cat data/daily_runs/analysis_*.json | tail -50
```

### Manual Analysis

```bash
# Run daily analysis manually
python3 scripts/i_am_daily_analysis.py

# Discover from full history (one-time)
python3 scripts/auto_discover.py
```

### Check Cron Config

```bash
# View scheduled tasks
cat ~/.openclaw/cron/cron-tasks.json | grep -A 15 "i-am"
```

---

## 🛠️ Troubleshooting

### No traits extracted

**Cause**: Sessions contain mostly system messages

**Solution**: Wait for more user conversations, analysis will run at next scheduled time

### USER.md not updated

**Check**:
```bash
# Verify file exists
ls -la ~/.openclaw/workspace/USER.md

# Check permissions
cat ~/.openclaw/workspace/USER.md
```

### Scheduled mode not running

**Check cron config**:
```bash
cat ~/.openclaw/cron/cron-tasks.json | grep -A 15 "i-am"
```

**Re-run installer**:
```bash
python3 scripts/install.py
# Choose mode 1 (Scheduled)
```

### Analysis fails

**Check logs**:
```bash
cat data/daily_runs/analysis_*.json
```

**Run manually to debug**:
```bash
python3 scripts/i_am_daily_analysis.py
```

---

## 📝 Changelog

### v2.0.2 (2026-03-12)
- Twice-daily analysis (2:30 AM & 2:30 PM)
- Default: scheduled mode (twice daily)
- ACT-R + Grounded Theory merged
- Incremental analysis (only new sessions)
- Interactive installer with bilingual prompts

### v2.0.1 (2026-03-12)
- Universal sender extraction
- Support any IM platform via OpenClaw

### v2.0.0 (2026-03-12)
- Session-based personality analysis
- Grounded Theory extraction
- ACT-R cognitive architecture
- Auto USER.md updates

---

*Documentation: i-am Skill v2.0.2 | 2026-03-12*
