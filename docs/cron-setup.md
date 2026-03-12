# ⏰ i-am 定时任务配置指南

**版本**: v1.0  
**适用**: macOS / Linux / Windows  
**最后更新**: 2026-03-12

---

## 📋 配置步骤

### 方式一：cron (macOS / Linux)

#### 1. 编辑 crontab
```bash
crontab -e
```

#### 2. 添加定时任务

**每天凌晨 3:00 运行**（推荐）:
```bash
0 3 * * * python3 ~/.openclaw/workspace/skills/i-am/scripts/i_am_batch_runner.py run-once --hours 24 >> ~/.openclaw/workspace/skills/i-am/logs/cron.log 2>&1
```

**每 6 小时运行一次**:
```bash
0 */6 * * * python3 ~/.openclaw/workspace/skills/i-am/scripts/i_am_batch_runner.py run-once --hours 6 >> ~/.openclaw/workspace/skills/i-am/logs/cron.log 2>&1
```

**每周一凌晨 2:00 运行**（周分析）:
```bash
0 2 * * 1 python3 ~/.openclaw/workspace/skills/i-am/scripts/i_am_batch_runner.py run-once --hours 168 >> ~/.openclaw/workspace/skills/i-am/logs/cron.log 2>&1
```

#### 3. 验证配置
```bash
# 查看当前 crontab
crontab -l

# 查看 cron 日志
tail -f ~/.openclaw/workspace/skills/i-am/logs/cron.log
```

---

### 方式二：Windows Task Scheduler

#### 1. 创建批处理脚本

创建 `C:\Users\YourName\openclaw\workspace\skills\i-am\scripts\run-i-am.bat`:

```batch
@echo off
REM i-am 定时任务运行脚本
REM 用于 Windows Task Scheduler

cd /d "%~dp0"

REM 设置 Python 路径（根据实际情况修改）
set PYTHON_PATH=C:\Python39\python.exe

REM 如果 Python 不在 PATH 中，使用完整路径
REM 如果在 PATH 中，可以直接用 python

echo [%date% %time%] 运行 i-am 分析...

%PYTHON_PATH% i_am_batch_runner.py run-once --hours 24 >> logs\cron.log 2>&1

echo [%date% %time%] 运行完成

exit /b 0
```

#### 2. 打开任务计划程序

1. 按 `Win + R`
2. 输入 `taskschd.msc`
3. 按 Enter 打开

#### 3. 创建基本任务

1. 右侧点击 **"创建基本任务..."**
2. 名称：`i-am Analysis`
3. 描述：`OpenClaw i-am Skill 定时分析任务`
4. 点击 **下一步**

#### 4. 配置触发器

**每天运行**:
- 触发器：**每天**
- 开始时间：`03:00:00`
- 每隔：`1` 天

**每 6 小时运行**:
- 触发器：**一次**
- 开始时间：`00:00:00`
- 勾选 **重复任务间隔**：`6 小时`
- 持续时间：`无限期`

#### 5. 配置操作

- 操作：**启动程序**
- 程序/脚本：`C:\Users\YourName\openclaw\workspace\skills\i-am\scripts\run-i-am.bat`
- 起始于：`C:\Users\YourName\openclaw\workspace\skills\i-am\scripts\`

#### 6. 完成配置

- 勾选 **"当点击完成时打开属性对话框"**
- 点击 **完成**

#### 7. 高级配置（重要！）

在属性对话框中：

**常规** 选项卡:
- ✅ 勾选 **不管用户是否登录都要运行**
- ✅ 勾选 **使用最高权限运行**
- 配置：`Windows 10` (或你的系统版本)

**条件** 选项卡:
- ✅ 取消勾选 **只有在计算机使用交流电源时才启动此任务** (笔记本需要)
- ✅ 勾选 **如果任务运行时间超过以下时间，将其停止**: `1 小时`

**设置** 选项卡:
- ✅ 勾选 **如果任务失败，重新启动每隔**: `5 分钟`
- ✅ 尝试重新启动次数：`3`
- ✅ 勾选 **如果运行时间超过以下时间，请停止任务**: `1 小时`

#### 8. 测试任务

1. 右侧找到 `i-am Analysis` 任务
2. 右键点击 → **运行**
3. 查看日志：`skills\i-am\logs\cron.log`

---

### 方式三：systemd (Linux Server)

#### 1. 创建服务文件

`/etc/systemd/system/i-am-analysis.service`:

```ini
[Unit]
Description=OpenClaw i-am Analysis
After=network.target

[Service]
Type=oneshot
User=your_username
WorkingDirectory=/home/your_username/.openclaw/workspace/skills/i-am/scripts
ExecStart=/usr/bin/python3 /home/your_username/.openclaw/workspace/skills/i-am/scripts/i_am_batch_runner.py run-once --hours 24
StandardOutput=append:/var/log/i-am-analysis.log
StandardError=append:/var/log/i-am-analysis.log

[Install]
WantedBy=multi-user.target
```

#### 2. 创建定时器文件

`/etc/systemd/system/i-am-analysis.timer`:

```ini
[Unit]
Description=Run i-am Analysis Daily
Requires=i-am-analysis.service

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

#### 3. 启用并启动

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启用定时器
sudo systemctl enable i-am-analysis.timer

# 启动定时器
sudo systemctl start i-am-analysis.timer

# 查看状态
systemctl status i-am-analysis.timer

# 查看日志
journalctl -u i-am-analysis.service
```

---

## 🧪 测试命令

### 测试运行
```bash
# macOS / Linux
cd ~/.openclaw/workspace/skills/i-am/scripts
python3 i_am_batch_runner.py test --hours 24

# Windows
cd C:\Users\YourName\openclaw\workspace\skills\i-am\scripts
python i_am_batch_runner.py test --hours 24
```

### 手动运行一次
```bash
# macOS / Linux
python3 i_am_batch_runner.py run-once --hours 24

# Windows
python i_am_batch_runner.py run-once --hours 24
```

---

## 📊 日志查看

### 日志位置
- **macOS / Linux**: `~/.openclaw/workspace/skills/i-am/logs/cron.log`
- **Windows**: `skills\i-am\logs\cron.log`

### 运行结果位置
- **macOS / Linux**: `~/.openclaw/workspace/skills/i-am/data/batch_runs/`
- **Windows**: `skills\i-am\data\batch_runs\`

### 查看最新结果
```bash
# macOS / Linux
cd ~/.openclaw/workspace/skills/i-am/data/batch_runs
ls -lt | head -5
cat run_result_YYYYMMDD_HHMM.json

# Windows PowerShell
cd skills\i-am\data\batch_runs
dir | Select-Object -First 5
Get-Content run_result_YYYYMMDD_HHMM.json
```

---

## ⚠️ 注意事项

### 1. Python 路径

**macOS / Linux**:
```bash
# 查找 Python3 路径
which python3
# 通常：/usr/bin/python3 或 /opt/homebrew/bin/python3
```

**Windows**:
```cmd
REM 查找 Python 路径
where python
REM 通常：C:\Python39\python.exe 或 C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe
```

### 2. 权限问题

**macOS / Linux**:
```bash
# 确保脚本可执行
chmod +x ~/.openclaw/workspace/skills/i-am/scripts/i_am_batch_runner.py
```

**Windows**:
- 确保以管理员权限创建任务
- 确保任务属性勾选"使用最高权限运行"

### 3. 时区问题

确保定时任务的时区与你的时区一致：
- **中国**: Asia/Shanghai (UTC+8)
- **美国东部**: America/New_York (UTC-5/UTC-4)

### 4. 日志轮转

防止日志文件过大，建议配置日志轮转：

**macOS / Linux** (`/etc/logrotate.d/i-am`):
```
~/.openclaw/workspace/skills/i-am/logs/cron.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 📋 推荐配置

### 个人用户（对话较少）
- **频率**: 每天凌晨 3:00
- **分析范围**: 最近 24 小时
- **命令**: `run-once --hours 24`

### 高频用户（对话频繁）
- **频率**: 每 6 小时
- **分析范围**: 最近 6 小时
- **命令**: `run-once --hours 6`

### 周分析（深度分析）
- **频率**: 每周一凌晨 2:00
- **分析范围**: 最近 168 小时（7 天）
- **命令**: `run-once --hours 168`

---

## 🔍 故障排查

### 问题 1: 任务不运行

**检查**:
```bash
# macOS / Linux
crontab -l
grep cron /var/log/system.log

# Windows
# 打开任务计划程序 → 查看任务历史
```

### 问题 2: Python 找不到

**解决**:
```bash
# 使用完整路径
which python3
# 替换 crontab 中的 python3 为完整路径
```

### 问题 3: 权限错误

**解决**:
```bash
# macOS / Linux
chmod +x ~/.openclaw/workspace/skills/i-am/scripts/*.py

# Windows
# 以管理员身份运行任务计划程序
```

### 问题 4: 没有分析结果

**检查**:
```bash
# 查看日志
tail -f ~/.openclaw/workspace/skills/i-am/logs/cron.log

# 手动运行测试
python3 i_am_batch_runner.py test --hours 24
```

---

*配置指南 v1.0 | 2026-03-12*
