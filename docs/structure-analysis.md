# i-am Skill v2.0.2 文件结构分析与优化建议

## 📁 当前文件结构

```
i-am/
├── 📄 根目录文件 (5 个)
│   ├── SKILL.md                    # Skill 入口定义
│   ├── README.md                   # 英文文档
│   ├── README.zh-CN.md             # 中文文档
│   ├── WORK_FLOW.md                # 工作流程 (待更新)
│   └── clawhub.yaml                # ClawHub 配置
│
├── 📜 scripts/ (6 个脚本)
│   ├── install.py                  # 安装脚本 (询问模式)
│   ├── i_am_daily_analysis.py      # 每日分析主脚本 ⭐
│   ├── auto_discover.py            # 历史发现
│   ├── open_coding.py              # 开放性编码引擎
│   ├── actr_feedback.py            # ACT-R 反馈引擎
│   └── user_md_sync.py             # USER.md 同步引擎
│
├── ⚙️ config/ (1 个配置)
│   └── config.yaml                 # 分析配置
│
├── 📚 docs/ (5 个文档)
│   ├── architecture.md             # 架构文档
│   ├── cleanup-report.md           # 清理报告 (临时)
│   ├── cron-setup.md               # 定时任务配置
│   ├── gateway-integration.md      # 网关集成 (过时)
│   ├── middleware-design.md        # 中间件设计 (过时)
│   └── release-test-report.md      # 测试报告 (临时)
│
├── 🧠 grounding_theory/ (2 个文件)
│   ├── README.md
│   └── open_coding/
│       └── label_library.json      # 标签库
│
├── 🧠 actr/ (2 个文件)
│   ├── README.md
│   └── procedural_memory/
│       └── production_rules.json   # 产生式规则
│
└── 📝 user_md_sync/ (1 个文件)
    └── change_log.md               # 变更日志
```

---

## ✅ 优点分析

| 方面 | 评分 | 说明 |
|------|------|------|
| **核心功能集中度** | ⭐⭐⭐⭐⭐ | 主脚本只有 1 个 (i_am_daily_analysis.py) |
| **引擎模块化** | ⭐⭐⭐⭐⭐ | open_coding/actr_feedback/user_md_sync 分离 |
| **文档完整性** | ⭐⭐⭐⭐ | 有架构、配置、定时任务文档 |
| **配置集中化** | ⭐⭐⭐⭐⭐ | 所有配置在 config.yaml |
| **数据分离** | ⭐⭐⭐⭐ | 运行时数据在 data/目录 |

---

## ⚠️ 优化空间

### 1. 删除过时文档 (优先级：高)

**问题**: docs/ 包含过时文档
- `gateway-integration.md` - 网关集成已删除
- `middleware-design.md` - 中间件设计已弃用
- `cleanup-report.md` - 临时清理报告
- `release-test-report.md` - 临时测试报告

**建议**:
```bash
# 删除过时文档
rm docs/gateway-integration.md
rm docs/middleware-design.md
rm docs/cleanup-report.md
rm docs/release-test-report.md
```

**优化后**: docs/ 保留 2 个核心文档
- `architecture.md` - 架构说明
- `cron-setup.md` - 定时任务配置

---

### 2. 简化引擎目录 (优先级：中)

**问题**: grounding_theory/ 和 actr/ 目录结构过深

**当前**:
```
grounding_theory/
├── README.md
└── open_coding/
    └── label_library.json

actr/
├── README.md
└── procedural_memory/
    └── production_rules.json
```

**建议简化**:
```
data/
├── labels/
│   └── label_library.json      # 标签库
└── rules/
    └── production_rules.json   # 产生式规则
```

**好处**:
- 减少 2 层目录深度
- 统一数据存放位置
- README.md 内容可合并到主文档

---

### 3. 合并 user_md_sync/ (优先级：低)

**问题**: user_md_sync/ 只有 1 个文件

**当前**:
```
user_md_sync/
└── change_log.md
```

**建议**: 合并到根目录或 data/
```
# 方案 A: 移到根目录
USER_CHANGE_LOG.md

# 方案 B: 移到 data/
data/
└── change_log.md
```

---

### 4. WORK_FLOW.md 更新 (优先级：高)

**问题**: WORK_FLOW.md 还是旧版内容

**建议**: 更新为新架构
```markdown
# i-am Work Flow v2.0.2

## 每日流程
2:30 AM → i_am_daily_analysis.py 运行
  ↓
加载上次分析后的新 sessions
  ↓
ACT-R 隐式反馈分析
  ↓
扎根理论（开放→主轴→选择性编码）
  ↓
询问用户确认（首次/7 天后）
  ↓
更新 USER.md
  ↓
保存时间戳

2:30 PM → 重复以上流程
```

---

### 5. 添加 requirements.txt (优先级：中)

**问题**: 依赖只在文档中提到

**建议**: 添加 requirements.txt
```txt
# i-am Skill Dependencies
watchdog>=3.0.0
```

**好处**:
- 一键安装依赖
- 版本明确
- 符合 Python 项目规范

---

## 🎯 优化后文件结构

```
i-am/
├── 📄 根目录 (7 个文件)
│   ├── SKILL.md                    # Skill 入口
│   ├── README.md                   # 英文文档
│   ├── README.zh-CN.md             # 中文文档
│   ├── WORK_FLOW.md                # 工作流程 ⭐更新
│   ├── clawhub.yaml                # ClawHub 配置
│   ├── requirements.txt            # Python 依赖 ⭐新增
│   └── USER_CHANGE_LOG.md          # 变更日志 ⭐移动
│
├── 📜 scripts/ (6 个脚本)
│   ├── install.py                  # 安装脚本
│   ├── i_am_daily_analysis.py      # 每日分析 ⭐
│   ├── auto_discover.py            # 历史发现
│   ├── open_coding.py              # 开放性编码
│   ├── actr_feedback.py            # ACT-R 反馈
│   └── user_md_sync.py             # USER.md 同步
│
├── ⚙️ config/ (1 个配置)
│   └── config.yaml                 # 分析配置
│
├── 📚 docs/ (2 个文档) ⭐精简
│   ├── architecture.md             # 架构文档
│   └── cron-setup.md               # 定时任务配置
│
├── 📊 data/ (运行时生成) ⭐统一
│   ├── daily_runs/                 # 每日分析结果
│   ├── labels/                     # 标签库 ⭐移动
│   └── rules/                      # 产生式规则 ⭐移动
│
└── temp/ (临时文件)
    └── test_results.json           # 测试结果
```

---

## 📊 优化对比

| 指标 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| 根目录文件 | 5 个 | 7 个 | +2 (requirements.txt, change_log) |
| docs/文件 | 6 个 | 2 个 | -4 (删除过时) |
| 数据目录 | 分散 | 统一 data/ | 集中管理 |
| 目录层级 | 最深 4 层 | 最深 3 层 | 简化 1 层 |
| 总文件数 | 23 个 | 21 个 | -2 (精简) |

---

## 🔧 优化步骤

### 步骤 1: 删除过时文档
```bash
cd i-am
rm docs/gateway-integration.md
rm docs/middleware-design.md
rm docs/cleanup-report.md
rm docs/release-test-report.md
```

### 步骤 2: 添加 requirements.txt
```bash
cat > requirements.txt << 'EOF'
# i-am Skill Dependencies
watchdog>=3.0.0
EOF
```

### 步骤 3: 移动变更日志
```bash
mv user_md_sync/change_log.md USER_CHANGE_LOG.md
rmdir user_md_sync
```

### 步骤 4: 更新 WORK_FLOW.md
```bash
# 更新为新架构文档
```

### 步骤 5: 简化数据目录 (可选)
```bash
# 移动标签库和规则到 data/
mkdir -p data/labels data/rules
mv grounding_theory/open_coding/label_library.json data/labels/
mv actr/procedural_memory/production_rules.json data/rules/
```

---

## ✅ 最终建议

### 立即优化 (高优先级)
1. ✅ 删除过时文档 (4 个)
2. ✅ 添加 requirements.txt
3. ✅ 更新 WORK_FLOW.md

### 后续优化 (中优先级)
4. 移动 change_log 到根目录
5. 简化 grounding_theory/ 和 actr/ 目录

### 可选优化 (低优先级)
6. 统一数据到 data/ 目录

---

*分析时间：2026-03-12*
*版本：i-am Skill v2.0.2*
