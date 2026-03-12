# i-am Skill Work Flow

## Complete Work Flow

### Phase 1: Installation
```bash
git clone https://github.com/Designer-Awei/i-am.git ~/.openclaw/workspace/skills/i-am
python scripts/i_am_daemon.py start
```

### Phase 2: Conversation Acquisition
- Source 1: OpenClaw Session History (auto)
- Source 2: Real-time Message Hook (optional)
- Source 3: Manual Import

### Phase 3: Real-time Processing
Daemon runs every minute:
1. Load new conversations (last 1 hour)
2. Open coding for each user message
3. Save to session_YYYYMMDD.json
4. Update label_library.json

### Phase 4: Batch Processing Trigger
Trigger conditions (any):
- 5 pending conversations
- 12 hours since last processing
- Manual trigger

### Phase 5: Batch Processing Execution
1. Load all pending sessions
2. Open coding (extract labels)
3. Axial coding (cluster labels)
4. Selective coding (generate core traits)
5. ACT-R utility learning
6. Merge updates
7. Update USER.md with backup
8. Mark conversations as processed

### Phase 6: USER.md Update
- Core personality traits table
- ACT-R cognitive model
- Auto-increment version

---

## ⚠️ Edge Cases

### Case 1: USER.md Not Exists
**Solution**: Auto-create initial USER.md with placeholder structure.

### Case 2: AGENTS.md Not Reading USER.md
**Solution**: Manually add to AGENTS.md:
```markdown
3. Read `USER.md` — this is who you're helping
```

### Case 3: Sessions Path Not Exists
**Solution**: Use manual recording:
```bash
python scripts/conversation_recorder.py record -u "message"
```

### Case 4: Daemon Not Running
**Solution**: 
```bash
python scripts/i_am_daemon.py start
# Or manual trigger
python scripts/i_am.py update
```

### Case 5: No Pending Conversations
**Solution**: Wait for new conversations or manually record.

---

## 📊 Monitoring

```bash
# View logs
tail -f logs/daemon.log

# View statistics
python scripts/conversation_recorder.py stats

# View change log
cat user_md_sync/change_log.md
```

---

*Work Flow: i-am v1.0.0 | 2026-03-12*
