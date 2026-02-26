# OpenClaw 新手自动化模板库
## 一键部署，开箱即用

---

## 模板1：每小时技能自动学习

### 功能
每小时自动从官方技能库学习一个新技能，并发送通知

### 安装步骤

**1. 创建学习脚本** `learn-skill-auto.py`

```python
#!/usr/bin/env python3
"""
每小时自动学习OpenClaw官方技能
来源: https://github.com/VoltAgent/awesome-openclaw-skills
"""

import requests
import re
import json
import os
import random
import subprocess
from datetime import datetime

# ========== 用户配置区域 ==========
# 修改为你的通知方式
NOTIFICATION_TYPE = "feishu"  # 可选: "feishu", "telegram", "discord", "slack"
NOTIFICATION_TARGET = "your-user-id"  # 你的用户ID
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"  # 修改为你的路径
# ==================================

LOG_FILE = os.path.expanduser('~/.openclaw/workspace/logs/auto-skills.log')
README_URL = 'https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md'
SKILL_LOG = os.path.expanduser('~/.openclaw/workspace/skills-auto-log.json')

def log(msg, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] [{level}] {msg}"
    print(log_msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def fetch_skills():
    try:
        response = requests.get(README_URL, timeout=30, verify=False)
        return response.text if response.status_code == 200 else None
    except Exception as e:
        log(f"获取失败: {e}", 'ERROR')
        return None

def parse_skills(readme):
    skills = []
    pattern = r'^\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)$'
    for line in readme.split('\n'):
        match = re.match(pattern, line)
        if match and 'github.com/openclaw/skills' in match.group(2):
            skills.append({
                'name': match.group(1).strip(),
                'url': match.group(2).strip(),
                'description': match.group(3).strip()[:200],
            })
    return skills

def categorize(name, desc):
    text = (name + ' ' + desc).lower()
    if any(kw in text for kw in ['video', 'image', 'visual']):
        return '🎬 视频/图片'
    elif any(kw in text for kw in ['content', 'twitter', 'social']):
        return '✍️ 内容创作'
    elif any(kw in text for kw in ['auto', 'workflow', 'deploy']):
        return '⚙️ 自动化'
    elif any(kw in text for kw in ['data', 'analy', 'monitor']):
        return '📊 数据分析'
    elif any(kw in text for kw in ['code', 'debug', 'git']):
        return '🔧 开发工具'
    else:
        return '📦 其他'

def get_learned():
    if os.path.exists(SKILL_LOG):
        try:
            with open(SKILL_LOG, 'r') as f:
                return set(d.get('skillLearned', {}).get('name', '') for d in json.load(f))
        except:
            pass
    return set()

def save_skill(skill, category):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'hour': datetime.now().hour,
        'category': category,
        'skillLearned': {
            'name': skill['name'],
            'url': skill['url'],
            'description': skill['description'],
        }
    }
    logs = []
    if os.path.exists(SKILL_LOG):
        with open(SKILL_LOG, 'r') as f:
            logs = json.load(f)
    logs.append(entry)
    with open(SKILL_LOG, 'w') as f:
        json.dump(logs, f, indent=2)
    log(f"已学习: {skill['name']}")

def notify(skill, category):
    try:
        message = f"""🎓 OpenClaw技能学习完成

⏰ 时间: {datetime.now().strftime('%H:%M')}
📂 类别: {category}
📚 技能: {skill['name']}

📝 {skill['description'][:80]}...

💡 安装: npx clawhub@latest install {skill['name']}"""
        
        subprocess.run([
            OPENCLAW_PATH, 'message', 'send',
            '--channel', NOTIFICATION_TYPE,
            '--target', NOTIFICATION_TARGET,
            '--message', message
        ], capture_output=True, timeout=30)
        log("通知已发送")
    except Exception as e:
        log(f"通知失败: {e}", 'WARN')

def main():
    hour = datetime.now().hour
    log("=" * 50)
    log("🎓 开始技能学习")
    
    readme = fetch_skills()
    if not readme:
        return
    
    skills = parse_skills(readme)
    learned = get_learned()
    
    available = [s for s in skills if s['name'] not in learned]
    if not available:
        log("所有技能已学完！", 'WARN')
        return
    
    skill = random.choice(available)
    category = categorize(skill['name'], skill['description'])
    
    save_skill(skill, category)
    notify(skill, category)
    
    log(f"类别: {category}")
    log("=" * 50)

if __name__ == '__main__':
    main()
```

**2. 配置定时任务**
```bash
# 编辑crontab
crontab -e

# 添加（每小时执行）
0 * * * * cd ~/.openclaw/workspace && python3 learn-skill-auto.py >> ~/.openclaw/workspace/logs/cron.log 2>&1
```

**3. 修改配置**
- 第16行: 修改 `NOTIFICATION_TARGET` 为你的用户ID
- 第17行: 修改 `OPENCLAW_PATH` 为你的openclaw路径（运行 `which openclaw` 查看）

---

## 模板2：每日自动备份工作区

### 功能
每天自动备份工作区到Git仓库

### 安装步骤

**1. 创建备份脚本** `auto-backup.py`

```python
#!/usr/bin/env python3
"""每日自动Git备份工作区"""

import subprocess
import os
from datetime import datetime

WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
NOTIFICATION_TYPE = "feishu"  # 修改为你的通知方式
NOTIFICATION_TARGET = "your-user-id"  # 修改为你的用户ID
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

def run(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode == 0, result.stdout, result.stderr

def main():
    os.chdir(WORKSPACE)
    
    # Git操作
    run("git add -A")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    success, out, err = run(f'git commit -m "auto: daily backup @ {timestamp}"')
    
    if success:
        run("git push origin main")
        message = f"""📦 每日备份完成

⏰ 时间: {timestamp}
✅ Git提交成功
📤 已推送到远程仓库

变更文件已自动备份！"""
    else:
        message = f"""📦 每日备份

⏰ 时间: {timestamp}
ℹ️ 无变更需要提交

工作区已是最新状态"""
    
    # 发送通知
    subprocess.run([
        OPENCLAW_PATH, 'message', 'send',
        '--channel', NOTIFICATION_TYPE,
        '--target', NOTIFICATION_TARGET,
        '--message', message
    ], capture_output=True)

if __name__ == '__main__':
    main()
```

**2. 配置定时任务**
```bash
crontab -e

# 每天23:30执行备份
30 23 * * * cd ~/.openclaw/workspace && python3 auto-backup.py
```

---

## 模板3：定时提醒系统

### 功能
定时发送提醒消息（喝水、休息、会议等）

### 安装步骤

**1. 创建提醒脚本** `reminder.py`

```python
#!/usr/bin/env python3
"""定时提醒系统"""

import subprocess
import sys
from datetime import datetime

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

REMINDERS = {
    "water": {
        "icon": "💧",
        "title": "喝水提醒",
        "message": "该喝水了！保持身体水分充足~"
    },
    "break": {
        "icon": "☕",
        "title": "休息提醒", 
        "message": "久坐提醒！起来活动5分钟吧~"
    },
    "stand": {
        "icon": "🧘",
        "title": "站立提醒",
        "message": "站立办公15分钟，保护脊椎健康！"
    },
    "eyes": {
        "icon": "👀",
        "title": "护眼提醒",
        "message": "眼睛累了！看看远处，做做眼保健操~"
    }
}

def send(reminder_key):
    r = REMINDERS.get(reminder_key)
    if not r:
        print(f"未知提醒类型: {reminder_key}")
        print(f"可用类型: {', '.join(REMINDERS.keys())}")
        return
    
    message = f"""{r['icon']} {r['title']}

{r['message']}

⏰ {datetime.now().strftime('%H:%M')}"""
    
    subprocess.run([
        OPENCLAW_PATH, 'message', 'send',
        '--channel', NOTIFICATION_TYPE,
        '--target', NOTIFICATION_TARGET,
        '--message', message
    ])
    print(f"已发送: {r['title']}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 reminder.py [类型]")
        print(f"类型: {', '.join(REMINDERS.keys())}")
        sys.exit(1)
    
    send(sys.argv[1])
```

**2. 配置定时任务**
```bash
crontab -e

# 每小时喝水提醒
0 * * * * cd ~/.openclaw/workspace && python3 reminder.py water

# 每2小时休息提醒  
0 */2 * * * cd ~/.openclaw/workspace && python3 reminder.py break

# 每天11:00站立提醒
0 11 * * * cd ~/.openclaw/workspace && python3 reminder.py stand

# 每小时护眼提醒
30 * * * * cd ~/.openclaw/workspace && python3 reminder.py eyes
```

---

## 模板4：文件自动整理

### 功能
自动整理下载文件夹，按类型分类

### 安装步骤

**1. 创建整理脚本** `auto-organize.py`

```python
#!/usr/bin/env python3
"""自动整理下载文件夹"""

import os
import shutil
from datetime import datetime
from pathlib import Path

# ========== 用户配置 ==========
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
ORGANIZE_DIR = os.path.expanduser("~/Downloads/Organized")
# ==============================

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Scripts": [".py", ".js", ".sh", ".bash", ".zsh"]
}

def organize():
    moved = 0
    for filename in os.listdir(DOWNLOAD_DIR):
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        
        ext = Path(filename).suffix.lower()
        
        for folder, extensions in FILE_TYPES.items():
            if ext in extensions:
                dest_folder = os.path.join(ORGANIZE_DIR, folder)
                os.makedirs(dest_folder, exist_ok=True)
                
                dest_path = os.path.join(dest_folder, filename)
                shutil.move(filepath, dest_path)
                print(f"Moved: {filename} -> {folder}/")
                moved += 1
                break
    
    return moved

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 开始整理...")
    count = organize()
    print(f"整理完成: {count} 个文件")

if __name__ == '__main__':
    main()
```

**2. 配置定时任务**
```bash
crontab -e

# 每天凌晨3点整理下载文件夹
0 3 * * * python3 ~/.openclaw/workspace/auto-organize.py
```

---

## 模板5：系统监控日报

### 功能
每天发送系统状态报告（磁盘、内存、CPU）

### 安装步骤

**1. 创建监控脚本** `system-monitor.py`

```python
#!/usr/bin/env python3
"""系统监控日报"""

import subprocess
import psutil
from datetime import datetime

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

def get_system_info():
    # 磁盘使用
    disk = psutil.disk_usage('/')
    disk_used = disk.used / (1024**3)  # GB
    disk_total = disk.total / (1024**3)
    disk_percent = disk.percent
    
    # 内存使用
    mem = psutil.virtual_memory()
    mem_used = mem.used / (1024**3)
    mem_total = mem.total / (1024**3)
    mem_percent = mem.percent
    
    # CPU使用
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return {
        'disk_used': round(disk_used, 1),
        'disk_total': round(disk_total, 1),
        'disk_percent': disk_percent,
        'mem_used': round(mem_used, 1),
        'mem_total': round(mem_total, 1),
        'mem_percent': mem_percent,
        'cpu_percent': cpu_percent
    }

def main():
    info = get_system_info()
    
    # 状态图标
    disk_icon = "🔴" if info['disk_percent'] > 90 else "🟡" if info['disk_percent'] > 70 else "🟢"
    mem_icon = "🔴" if info['mem_percent'] > 90 else "🟡" if info['mem_percent'] > 70 else "🟢"
    cpu_icon = "🔴" if info['cpu_percent'] > 80 else "🟡" if info['cpu_percent'] > 50 else "🟢"
    
    message = f"""📊 系统状态日报

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}

💾 磁盘使用:
   {disk_icon} {info['disk_used']}GB / {info['disk_total']}GB ({info['disk_percent']}%)

🧠 内存使用:
   {mem_icon} {info['mem_used']}GB / {info['mem_total']}GB ({info['mem_percent']}%)

⚡ CPU使用:
   {cpu_icon} {info['cpu_percent']}%

{'⚠️ 注意: 磁盘空间不足！' if info['disk_percent'] > 90 else '✅ 系统状态正常'}"""
    
    subprocess.run([
        OPENCLAW_PATH, 'message', 'send',
        '--channel', NOTIFICATION_TYPE,
        '--target', NOTIFICATION_TARGET,
        '--message', message
    ], capture_output=True)
    
    print("系统监控报告已发送")

if __name__ == '__main__':
    main()
```

**2. 安装依赖**
```bash
pip3 install psutil
```

**3. 配置定时任务**
```bash
crontab -e

# 每天早上9点发送系统报告
0 9 * * * python3 ~/.openclaw/workspace/system-monitor.py
```

---

## 快速部署命令

一键部署所有模板：

```bash
# 1. 创建工作目录
mkdir -p ~/.openclaw/workspace/logs

# 2. 复制上述脚本（保存为对应文件）
# learn-skill-auto.py
# auto-backup.py
# reminder.py
# auto-organize.py
# system-monitor.py

# 3. 安装依赖
pip3 install psutil requests

# 4. 获取openclaw路径
which openclaw
# 修改脚本中的 OPENCLAW_PATH

# 5. 配置定时任务
crontab -e
# 添加上述所有定时任务

# 6. 测试
python3 ~/.openclaw/workspace/learn-skill-auto.py
```

---

## 注意事项

1. **修改配置**：每个脚本顶部的 `NOTIFICATION_TYPE`、`NOTIFICATION_TARGET`、`OPENCLAW_PATH` 必须修改为你自己的

2. **获取用户ID**：运行 `openclaw message send --channel feishu --target @me --message "test"` 查看你的ID

3. **日志查看**：所有脚本日志保存在 `~/.openclaw/workspace/logs/` 目录

4. **测试运行**：首次部署后，手动运行脚本测试，确认通知能收到

---

*模板库版本: 1.0*  
*适用: OpenClaw新手自动化入门*

---

# 扩展模板（新增4个）

## 模板6：RSS订阅自动汇总

### 功能
每天自动抓取RSS订阅源，汇总热门文章发送

### 安装步骤

**1. 创建RSS脚本** `rss-daily.py`

```python
#!/usr/bin/env python3
"""RSS订阅每日汇总"""

import feedparser
import subprocess
from datetime import datetime

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

# ========== RSS源配置 ==========
RSS_FEEDS = [
    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
    {"name": "量子位", "url": "https://www.qbitai.com/rss"},
    {"name": "GitHub Trending", "url": "https://github.com/trending/rss"},
]
# ==============================

def fetch_feed(feed_info):
    try:
        feed = feedparser.parse(feed_info['url'])
        entries = feed.entries[:3]  # 取前3条
        return [
            {"title": e.title, "link": e.link, "feed": feed_info['name']}
            for e in entries
        ]
    except:
        return []

def main():
    all_articles = []
    for feed in RSS_FEEDS:
        articles = fetch_feed(feed)
        all_articles.extend(articles)
    
    if not all_articles:
        return
    
    # 构建消息
    lines = [f"📰 RSS每日精选 ({datetime.now().strftime('%m-%d')})", ""]
    for i, a in enumerate(all_articles[:10], 1):  # 最多10条
        lines.append(f"{i}. [{a['feed']}] {a['title']}")
        lines.append(f"   {a['link']}")
        lines.append("")
    
    message = "\n".join(lines)
    
    subprocess.run([
        OPENCLAW_PATH, 'message', 'send',
        '--channel', NOTIFICATION_TYPE,
        '--target', NOTIFICATION_TARGET,
        '--message', message
    ], capture_output=True)
    
    print(f"已发送 {len(all_articles)} 篇文章")

if __name__ == '__main__':
    main()
```

**2. 安装依赖**
```bash
pip3 install feedparser
```

**3. 配置定时任务**
```bash
crontab -e

# 每天早上8:30发送RSS汇总
30 8 * * * python3 ~/.openclaw/workspace/rss-daily.py
```

---

## 模板7：网站可用性监控

### 功能
监控指定网站是否可访问，宕机时立即告警

### 安装步骤

**1. 创建监控脚本** `website-monitor.py`

```python
#!/usr/bin/env python3
"""网站可用性监控"""

import requests
import subprocess
import os
from datetime import datetime

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

# ========== 监控配置 ==========
WEBSITES = [
    {"name": "我的博客", "url": "https://example.com", "expected": 200},
    {"name": "API服务", "url": "https://api.example.com/health", "expected": 200},
]
CHECK_INTERVAL = 5  # 分钟
STATUS_FILE = "/tmp/website-status.json"
# ==============================

def check_website(site):
    try:
        response = requests.get(site['url'], timeout=10)
        return response.status_code == site['expected']
    except:
        return False

def load_previous_status():
    if os.path.exists(STATUS_FILE):
        try:
            import json
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_status(status):
    import json
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)

def main():
    previous = load_previous_status()
    current = {}
    alerts = []
    
    for site in WEBSITES:
        is_up = check_website(site)
        current[site['name']] = is_up
        
        # 状态变化才告警
        prev = previous.get(site['name'], True)
        if prev and not is_up:
            alerts.append(f"🔴 {site['name']} 宕机！")
        elif not prev and is_up:
            alerts.append(f"🟢 {site['name']} 恢复！")
    
    save_status(current)
    
    if alerts:
        message = f"""⚠️ 网站监控告警

{'\n'.join(alerts)}

⏰ {datetime.now().strftime('%H:%M')}"""
        
        subprocess.run([
            OPENCLAW_PATH, 'message', 'send',
            '--channel', NOTIFICATION_TYPE,
            '--target', NOTIFICATION_TARGET,
            '--message', message
        ], capture_output=True)
        print(f"发送告警: {len(alerts)} 条")
    else:
        print("所有网站正常")

if __name__ == '__main__':
    main()
```

**2. 配置定时任务**
```bash
crontab -e

# 每5分钟检查一次
*/5 * * * * python3 ~/.openclaw/workspace/website-monitor.py
```

---

## 模板8：天气早报

### 功能
每天早上发送当日天气预报和穿衣建议

### 安装步骤

**1. 创建天气脚本** `weather-morning.py`

```python
#!/usr/bin/env python3
"""每日天气早报"""

import requests
import subprocess
from datetime import datetime

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

# ========== 城市配置 ==========
CITY = "上海"  # 修改为你的城市
CITY_CODE = "101020100"  # 城市代码，从天气网站获取
# ==============================

def get_weather():
    try:
        # 使用和风天气API（需要申请key）
        # url = f"https://devapi.qweather.com/v7/weather/3d?location={CITY_CODE}&key=YOUR_KEY"
        # 或使用免费接口
        url = f"http://t.weather.itboy.net/api/weather/city/{CITY_CODE}"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 200:
            today = data['data']['forecast'][0]
            return {
                'city': data['cityInfo']['city'],
                'temp_high': today['high'].replace('高温 ', ''),
                'temp_low': today['low'].replace('低温 ', ''),
                'weather': today['type'],
                'notice': today['notice']
            }
    except:
        pass
    return None

def get_advice(temp_high, weather):
    temp = int(temp_high.replace('℃', ''))
    if temp >= 30:
        return "☀️ 天气炎热，注意防晒！"
    elif temp >= 20:
        return "🌤️ 天气舒适，适合外出~"
    elif temp >= 10:
        return "🌥️ 有点凉，记得带外套~"
    else:
        return "❄️ 天气寒冷，注意保暖！"

def main():
    weather = get_weather()
    if not weather:
        print("获取天气失败")
        return
    
    advice = get_advice(weather['temp_high'], weather['weather'])
    
    message = f"""🌤️ 早安！今日天气预报

📍 {weather['city']}
🌡️ {weather['temp_low']} ~ {weather['temp_high']}
☁️ {weather['weather']}

💡 {weather['notice']}

{advice}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
    
    subprocess.run([
        OPENCLAW_PATH, 'message', 'send',
        '--channel', NOTIFICATION_TYPE,
        '--target', NOTIFICATION_TARGET,
        '--message', message
    ], capture_output=True)
    
    print("天气早报已发送")

if __name__ == '__main__':
    main()
```

**2. 配置定时任务**
```bash
crontab -e

# 每天早上7:30发送天气
30 7 * * * python3 ~/.openclaw/workspace/weather-morning.py
```

---

## 模板9：待办事项截止提醒

### 功能
读取待办列表，临近截止自动提醒

### 安装步骤

**1. 创建待办脚本** `todo-reminder.py`

```python
#!/usr/bin/env python3
"""待办事项截止提醒"""

import subprocess
import os
from datetime import datetime, timedelta
import json

NOTIFICATION_TYPE = "feishu"
NOTIFICATION_TARGET = "your-user-id"
OPENCLAW_PATH = "/home/username/.npm-global/bin/openclaw"

TODO_FILE = os.path.expanduser("~/.openclaw/workspace/todo-list.json")

def load_todos():
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def check_deadlines():
    todos = load_todos()
    now = datetime.now()
    alerts = []
    
    for todo in todos:
        if todo.get('done'):
            continue
        
        deadline_str = todo.get('deadline')
        if not deadline_str:
            continue
        
        deadline = datetime.fromisoformat(deadline_str)
        days_left = (deadline - now).days
        
        if days_left < 0:
            alerts.append(f"🔴 逾期: {todo['title']} (已逾期{abs(days_left)}天)")
        elif days_left == 0:
            alerts.append(f"🟠 今天截止: {todo['title']}")
        elif days_left <= 2:
            alerts.append(f"🟡 即将截止: {todo['title']} (还剩{days_left}天)")
    
    return alerts

def main():
    alerts = check_deadlines()
    
    if alerts:
        message = f"""⏰ 待办事项提醒

{'\n'.join(alerts)}

📋 共 {len(alerts)} 项待办需要关注

⏰ {datetime.now().strftime('%m-%d %H:%M')}"""
        
        subprocess.run([
            OPENCLAW_PATH, 'message', 'send',
            '--channel', NOTIFICATION_TYPE,
            '--target', NOTIFICATION_TARGET,
            '--message', message
        ], capture_output=True)
        print(f"发送提醒: {len(alerts)} 项")
    else:
        print("无待办需要提醒")

if __name__ == '__main__':
    main()
```

**2. 创建待办文件示例** `todo-list.json`

```json
[
  {
    "title": "完成周报",
    "deadline": "2026-02-28T18:00:00",
    "done": false
  },
  {
    "title": "预订机票",
    "deadline": "2026-03-01T12:00:00",
    "done": false
  }
]
```

**3. 配置定时任务**
```bash
crontab -e

# 每天9:00、15:00、18:00检查待办
0 9,15,18 * * * python3 ~/.openclaw/workspace/todo-reminder.py
```

---

## 完整模板清单（9个）

| 编号 | 模板 | 功能 | 频率 |
|------|------|------|------|
| 1 | 技能学习 | 每小时自动学新技能 | 每小时 |
| 2 | Git备份 | 自动备份工作区 | 每天23:30 |
| 3 | 定时提醒 | 喝水/休息/护眼 | 自定义 |
| 4 | 文件整理 | 自动分类下载文件 | 每天3:00 |
| 5 | 系统监控 | 磁盘/内存/CPU报告 | 每天9:00 |
| 6 | **RSS汇总** | 抓取订阅源推送 | 每天8:30 |
| 7 | **网站监控** | 网站宕机告警 | 每5分钟 |
| 8 | **天气早报** | 天气预报+建议 | 每天7:30 |
| 9 | **待办提醒** | 截止日提醒 | 每天3次 |

---

## 依赖安装总清单

```bash
# 一键安装所有依赖
pip3 install psutil requests feedparser

# 或者分开安装
pip3 install psutil      # 系统监控
pip3 install requests    # HTTP请求
pip3 install feedparser  # RSS解析
```

---

*模板库版本: 2.0 | 新增4个实用模板*