#!/usr/bin/env python3
"""
从官方 awesome-openclaw-skills 学习
来源: https://github.com/VoltAgent/awesome-openclaw-skills
"""

import requests
import re
import json
import os
import random
from datetime import datetime

LOG_FILE = '/home/zzyuzhangxing/.openclaw/workspace/logs/openclaw_official_skills.log'
README_URL = 'https://raw.githubusercontent.com/VoltAgent/awesome-openclaw-skills/main/README.md'

def log(msg, level='INFO'):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] [{level}] {msg}"
    print(log_msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except:
        pass

def fetch_official_skills():
    """从官方仓库获取技能列表"""
    try:
        log("📥 获取官方技能列表...")
        response = requests.get(README_URL, timeout=30, verify=False)
        if response.status_code == 200:
            return response.text
        else:
            log(f"⚠️ HTTP {response.status_code}", 'WARN')
            return None
    except Exception as e:
        log(f"❌ 获取失败: {e}", 'ERROR')
        return None

def parse_skills(readme):
    """解析README中的技能列表"""
    skills = []
    
    # 匹配技能链接格式
    # - [skill-name](url) - description
    pattern = r'^\s*-\s*\[([^\]]+)\]\(([^)]+)\)\s*-\s*(.+)$'
    
    for line in readme.split('\n'):
        match = re.match(pattern, line)
        if match:
            name = match.group(1).strip()
            url = match.group(2).strip()
            desc = match.group(3).strip()
            
            # 过滤掉非技能链接（如安全工具等）
            if 'github.com/openclaw/skills' in url and name not in ['Snyk Skill Security Scanner', 'Agent Trust Hub']:
                skills.append({
                    'name': name,
                    'url': url,
                    'description': desc[:200],
                    'source': 'awesome-openclaw-skills'
                })
    
    return skills

def categorize_skill(name, desc):
    """根据名称和描述分类技能"""
    text = (name + ' ' + desc).lower()
    
    # 视频/图片
    if any(kw in text for kw in ['video', 'image', 'avatar', 'diagram', 'draw', 'visual']):
        return '🎬 视频/图片'
    
    # 内容创作
    elif any(kw in text for kw in ['content', 'twitter', 'social', 'post', 'marketing', 'message']):
        return '✍️ 内容创作'
    
    # 自动化
    elif any(kw in text for kw in ['auto', 'bot', 'workflow', 'orchestrat', 'deploy', 'ci/cd', 'schedule']):
        return '⚙️ 自动化'
    
    # 数据分析
    elif any(kw in text for kw in ['data', 'analy', 'monitor', 'log', 'metric', 'report']):
        return '📊 数据分析'
    
    # 开发工具
    elif any(kw in text for kw in ['code', 'debug', 'docker', 'git', 'github', 'cursor', 'ide', 'agent', 'coding']):
        return '🔧 开发工具'
    
    # 沟通协作
    elif any(kw in text for kw in ['slack', 'discord', 'telegram', 'email', 'communication', 'team']):
        return '💬 沟通协作'
    
    # 金融/其他
    else:
        return '📦 其他'

def get_learned_skills():
    """获取已学习的技能"""
    log_path = '/home/zzyuzhangxing/.openclaw/workspace/skills-learning-log.json'
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as f:
                logs = json.load(f)
            learned = set()
            for log_entry in logs:
                skill_name = log_entry.get('skillLearned', {}).get('name', '')
                if skill_name and skill_name not in ['搜索中', '未找到新技能']:
                    learned.add(skill_name)
            return learned
        except:
            pass
    return set()

def select_skill_by_hour(hour, skills, learned):
    """根据当前小时选择技能类别"""
    # 偶数小时: 创作类 (视频/图片 + 内容创作)
    # 奇数小时: 技术类 (自动化 + 数据分析 + 开发工具)
    
    if hour % 2 == 0:
        target_categories = ['🎬 视频/图片', '✍️ 内容创作']
    else:
        target_categories = ['⚙️ 自动化', '📊 数据分析', '🔧 开发工具']
    
    # 先尝试从目标类别中选择
    available = [s for s in skills 
                 if categorize_skill(s['name'], s['description']) in target_categories 
                 and s['name'] not in learned]
    
    # 如果目标类别没有，从全部未学习的选
    if not available:
        available = [s for s in skills if s['name'] not in learned]
    
    if not available:
        return None
    
    # 随机选择
    return random.choice(available)

def save_skill(skill, category):
    """保存技能学习记录"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'hour': datetime.now().hour,
        'category': category,
        'skillLearned': {
            'name': skill['name'],
            'url': skill['url'],
            'description': skill['description'],
            'source': skill['source']
        },
        'details': f"""# {skill['name']}

## 类别
{category}

## 描述
{skill['description']}

## 来源
官方技能库: https://github.com/VoltAgent/awesome-openclaw-skills

## 安装方式
```bash
npx clawhub@latest install {skill['name']}
```

或者直接复制技能文件夹到:
- Global: `~/.openclaw/skills/`
- Workspace: `<project>/skills/`

## 官方链接
{skill['url']}
"""
    }
    
    log_path = '/home/zzyuzhangxing/.openclaw/workspace/skills-learning-log.json'
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            logs = json.load(f)
    logs.append(log_entry)
    
    with open(log_path, 'w') as f:
        json.dump(logs, f, indent=2)
    
    log(f"  → 已记录技能: {skill['name']}")

def send_notification(skill, category):
    """发送飞书通知"""
    try:
        import subprocess
        message = f"""🎓 官方OpenClaw技能学习完成

⏰ 时间: {datetime.now().strftime('%H:%M')}
📂 类别: {category}
📚 技能: {skill['name']}

📝 简介: {skill['description'][:80]}...

🔗 来源: 官方 awesome-openclaw-skills
💡 安装: npx clawhub@latest install {skill['name']}

这是来自官方2868技能库的专业技能！"""
        
        # 使用完整路径调用openclaw（cron环境可能找不到PATH）
        openclaw_path = '/home/zzyuzhangxing/.npm-global/bin/openclaw'
        subprocess.run([
            openclaw_path, 'message', 'send',
            '--channel', 'feishu',
            '--target', 'ou_f17427a7518faa014659589d89db4d8b',
            '--message', message
        ], capture_output=True, timeout=30)
        log("  → 已发送飞书通知")
    except Exception as e:
        log(f"  ⚠️ 通知发送失败: {e}", 'WARN')

def main():
    """主函数"""
    now = datetime.now()
    hour = now.hour
    
    log("=" * 60)
    log("🎓 官方OpenClaw技能学习")
    log("=" * 60)
    log(f"⏰ 当前时间: {now.strftime('%H:%M')}")
    
    # 获取官方技能列表
    readme = fetch_official_skills()
    if not readme:
        log("❌ 无法获取官方技能列表", 'ERROR')
        return 1
    
    # 解析技能
    skills = parse_skills(readme)
    log(f"📚 官方技能库: {len(skills)} 个技能")
    
    if not skills:
        log("⚠️ 未解析到技能", 'WARN')
        return 1
    
    # 获取已学习技能
    learned = get_learned_skills()
    log(f"✅ 已学习: {len(learned)} 个")
    log(f"📖 待学习: {len(skills) - len(learned)} 个")
    
    # 根据小时选择技能
    skill = select_skill_by_hour(hour, skills, learned)
    
    if not skill:
        log("⚠️ 所有技能都已学习完毕！", 'WARN')
        log("等待技能库更新...")
        return 0
    
    # 分类
    category = categorize_skill(skill['name'], skill['description'])
    
    # 保存记录
    save_skill(skill, category)
    
    # 显示结果
    log("")
    log("=" * 60)
    log("🎉 技能学习完成")
    log("=" * 60)
    log(f"📚 技能: {skill['name']}")
    log(f"📂 类别: {category}")
    log(f"📝 描述: {skill['description'][:100]}...")
    log(f"🔗 来源: 官方 awesome-openclaw-skills")
    log("")
    log("💡 安装命令:")
    log(f"   npx clawhub@latest install {skill['name']}")
    log("")
    log("📚 这是来自官方2868技能库的专业技能！")
    log("=" * 60)
    
    # 发送通知
    send_notification(skill, category)
    
    log("\n✅ 完成！")
    return 0

if __name__ == '__main__':
    import sys
    # 禁用SSL警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sys.exit(main())
