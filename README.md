# i-am Skill v4.0.9

> **I am You, You am I** - Zero-config personality analysis using Grounded Theory

**[🇨🇳 中文版](README.zh-CN.md)** | **[🌏 English](README.md)**

---

## ⚡ Quick Start

```bash
# After installing this skill, AI will automatically guide you through configuration
# No manual setup required
```

**Schedule**: Twice daily at 2:30 AM & 2:30 PM (via OpenClaw cron)

---

## 🎯 What It Does

**i-am** analyzes your conversation history and updates USER.md with personality traits:

1. **Load Messages** - Extract user messages since last analysis
2. **Grounded Theory** - AI extracts traits from semantics (no predefined labels)
3. **Confidence Tracking** - Track trait confidence over time
4. **Update USER.md** - Merge insights into personality model

**Output Example**:
```markdown
## 🧠 Personality Traits (i-am Dynamic Analysis)

- 🔴 **Communication Style**: Direct & Efficient (Saturation: 75%, +5%)
- 🔴 **Decision Style**: Action-Oriented (Saturation: 68%, unchanged)
- 🟡 **Technical Orientation**: Pragmatism (Saturation: 52%, -10%)
```

---

## 📁 File Structure

```
i-am/
├── SKILL.md                          # Core AI instructions
├── clawhub.yaml                      # ClawHub config
├── README.md                         # This file (English)
├── README.zh-CN.md                   # Chinese version
├── .gitignore                        # Git ignore rules
└── CHANGELOG/                        # USER.md backup history (auto-created)
    └── USER-YYYYMMDD-HHMM.md         # Timestamped backups
```

---

## 🔄 How It Works

### Configuration Flow (First Install)

```
User installs skill
    ↓
AI detects new installation
    ↓
AI asks: Choose automation mode (1 Scheduled / 2 Manual)
    ↓
User replies: 1
    ↓
AI configures cron tasks
    ↓
AI creates folders (CHANGELOG/, temp/)
    ↓
AI backs up initial USER.md
    ↓
✅ Configuration complete!
```

### Analysis Flow (Scheduled/Manual)

```
OpenClaw Cron (2:30 AM/PM) or User triggers "Run i-am analysis"
    ↓
AI loads new messages since last analysis (max 50)
    ↓
AI performs Grounded Theory analysis:
  1. Open Coding: Extract codes from each message
  2. Axial Coding: Cluster codes into categories
  3. Selective Coding: Extract core traits with saturation
    ↓
AI generates preview (temp/USER.md)
    ↓
AI sends preview file to user for review
    ↓
User confirms or cancels
    ↓
If confirmed: Update USER.md + backup to CHANGELOG/
If cancelled: Delete temp/USER.md
```

---

## 🎓 Grounded Theory Method

**Core Principle**: No predefined labels, traits emerge from data!

### Three Coding Stages

| Stage | Input | Output |
|-------|-------|--------|
| **Open Coding** | User messages | Codes + Categories |
| **Axial Coding** | Open codes | Category clusters |
| **Selective Coding** | Axial clusters | Core traits + Saturation |

### Saturation Calculation

```
Saturation = 0.5 + (frequency / total_messages) * 0.5
```

### Confidence Update Rules

| Scenario | Confidence Calculation |
|----------|----------------------|
| First analysis | `confidence = saturation` |
| Consistent with history | `new = old + 0.05` |
| Conflict with history | `new = max(0.6, saturation)` (new statement weighted higher) |
| User confirms | `confidence + 0.10` (max 0.95) |

---

## ⚙️ Configuration

### Cron Schedule

Automatically configured during installation:
- **Morning**: 2:30 AM daily
- **Afternoon**: 2:30 PM daily

### Parameters

```yaml
analysis:
  min_messages: 5             # Skip if fewer than 5 messages
  max_messages: 50            # Process only last 50 messages
  
saturation:
  core: 0.7                   # Core trait threshold (🔴)
  secondary: 0.5              # Secondary trait threshold (🟡)
  emerging: 0.3               # Emerging trait threshold (🟢)
```

---

## 📊 Usage Examples

### Example 1: First Configuration

```
User: [installs i-am skill]

AI: 🧠 i-am Skill Configuration Wizard
    
    Choose automation mode:
    
    1️⃣ Scheduled Mode (Recommended)
       - Auto analysis twice daily (2:30 AM & 2:30 PM)
    
    2️⃣ Manual Mode
       - Run analysis on-demand
    
    Reply 1 or 2 (default 1):

User: 1

AI: ✅ Scheduled mode configured!
    
    📋 Configuration Summary:
    - Mode: Scheduled
    - Cron tasks: Configured (2:30 AM & 2:30 PM)
    - Next run: 2026-03-14 02:30
    - Folders: CHANGELOG/ ✅, temp/ ✅
    - Initial backup: CHANGELOG/USER-20260313-2000-initial.md
    
    Reply "Run i-am analysis" to start analysis
```

### Example 2: Run Analysis

```
User: Run i-am analysis

AI: 📊 Loading user messages...
    ✅ Loaded 15 new messages
    
    🧠 Starting Grounded Theory analysis...
    ✅ Extracted 4 core traits
    
    📋 USER.md Update Preview
    
    🔴 **Communication Style**: Direct & Efficient
       Saturation: 75% (+5%)
       Confidence: 80%
    
    🔴 **Decision Style**: Action-Oriented
       Saturation: 68% (unchanged)
       Confidence: 73%
    
    🟡 **Technical Orientation**: Pragmatism
       Saturation: 52% (-10%)
       Confidence: 60%
    
    📄 Preview file sent (temp/USER.md)
    📁 Backup: CHANGELOG/USER-20260313-2000.md
    
    🤖 Please review and confirm update?
    Reply "confirm", "push", "yes", or "ok" to confirm
    Reply "cancel", "no" to cancel
```

---

## 🔒 Security

- ✅ All data processed locally, no network transmission
- ✅ No external API keys required (uses current session model)
- ✅ User confirmation required before updating USER.md
- ✅ Preview file for user review
- ✅ Automatic backup to CHANGELOG/ before updates

---

## 📝 Changelog

### v4.0.9 (2026-03-13)
- ✅ Added .gitignore to ignore .DS_Store
- ✅ Added folder creation guide in installation
- ✅ Simplified confidence rules (3 scenarios)
- ✅ Removed ACT-R integration
- ✅ Added saturation change display (+5%, -10%)

### v4.0.0
- ✅ Minimalist architecture (SKILL.md + clawhub.yaml only)
- ✅ All code embedded in SKILL.md
- ✅ IM-adaptive file sending
- ✅ Zero-config installation

---

*i-am Skill v4.0.9 | 2026-03-13*
