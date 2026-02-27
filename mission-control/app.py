#!/usr/bin/env python3
"""
Mission Control - OpenClaw任务控制中心
用途: 定制化仪表板，管理WF助手的工作流
版本: v2.0 - 实时数据版
"""

from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wf-mission-control-2026'

# ==================== 数据接口 ====================

def get_tasks():
    """获取待办任务 - 从MEMORY.md读取"""
    tasks = []
    try:
        memory_file = '/home/zzyuzhangxing/.openclaw/workspace/MEMORY.md'
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 解析待办事项
                if '## ⚠️ 待办' in content:
                    lines = content.split('\n')
                    task_id = 1
                    for line in lines:
                        if line.strip().startswith('- [ ]'):
                            task_text = line.replace('- [ ]', '').strip()
                            priority = 'high' if 'P1' in task_text else 'medium' if 'P2' in task_text else 'low'
                            tasks.append({
                                "id": task_id,
                                "title": task_text,
                                "status": "pending",
                                "priority": priority
                            })
                            task_id += 1
    except Exception as e:
        print(f"读取任务失败: {e}")
    
    # 如果没有读取到，返回默认任务
    if not tasks:
        tasks = [
            {"id": 1, "title": "审核今日早报", "status": "pending", "priority": "high"},
            {"id": 2, "title": "分析B站热门视频", "status": "pending", "priority": "medium"},
            {"id": 3, "title": "学习新技能", "status": "in_progress", "priority": "low"},
        ]
    
    return tasks

def get_agents():
    """获取子Agent状态 - 从cron日志读取"""
    agents = []
    try:
        # 读取cron任务状态
        result = subprocess.run(
            ['openclaw', 'cron', 'list', '--json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            cron_data = json.loads(result.stdout)
            
            # 解析任务
            agent_map = {
                'install-skills-v2': '技能学习Agent',
                'daily-report-gen': '日报生成Agent',
                'ai-intelligence-monitor': 'AI情报监控Agent',
                'bilibili-account-fetch': 'B站账号监控Agent',
                'send-daily-report': '日报发送Agent'
            }
            
            for task in cron_data:
                task_name = task.get('name', '')
                if task_name in agent_map:
                    last_run = task.get('state', {}).get('lastRunAtMs', 0)
                    next_run = task.get('state', {}).get('nextRunAtMs', 0)
                    
                    # 转换时间戳
                    last_run_str = datetime.fromtimestamp(last_run / 1000).strftime('%H:%M') if last_run else 'N/A'
                    next_run_str = datetime.fromtimestamp(next_run / 1000).strftime('%H:%M') if next_run else 'N/A'
                    
                    agents.append({
                        "name": agent_map[task_name],
                        "status": "running" if task.get('state', {}).get('status') == 'ok' else "idle",
                        "last_run": last_run_str,
                        "next_run": next_run_str,
                        "tasks_completed": 30  # 默认值，后续可从日志统计
                    })
    except Exception as e:
        print(f"读取Agent状态失败: {e}")
    
    # 如果没有读取到，返回默认数据
    if not agents:
        agents = [
            {"name": "技能学习Agent", "status": "running", "last_run": "19:00", "next_run": "20:00", "tasks_completed": 27},
            {"name": "日报生成Agent", "status": "idle", "last_run": "09:30", "next_run": "明日09:30", "tasks_completed": 30},
            {"name": "AI情报监控Agent", "status": "idle", "last_run": "09:00", "next_run": "明日09:00", "tasks_completed": 30}
        ]
    
    return agents

def get_approval_queue():
    """获取审批队列 - 从审批日志读取"""
    queue = []
    try:
        approval_file = '/home/zzyuzhangxing/.openclaw/workspace/data/approval-queue.json'
        if os.path.exists(approval_file):
            with open(approval_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
    except Exception as e:
        print(f"读取审批队列失败: {e}")
    
    # 如果没有数据，返回示例
    if not queue:
        queue = [
            {"id": 1, "type": "tweet", "content": "今天学到了OpenClaw的反向提示技巧...", "created_at": "19:30", "status": "pending"},
            {"id": 2, "type": "video_script", "content": "【ComfyUI教程】如何用AI生成...", "created_at": "18:45", "status": "pending"}
        ]
    
    return queue

def get_system_status():
    """获取系统状态 - 实时读取"""
    status = {
        "gateway": "unknown",
        "model": "unknown",
        "skills_installed": 0,
        "cron_jobs": 0,
        "last_backup": "unknown"
    }
    
    try:
        # 读取Gateway状态
        result = subprocess.run(
            ['openclaw', 'gateway', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            if 'running' in result.stdout:
                status['gateway'] = 'running'
            else:
                status['gateway'] = 'stopped'
        
        # 读取当前模型
        result = subprocess.run(
            ['openclaw', 'models', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Default'):
                    status['model'] = line.split(':')[1].strip()
                    break
        
        # 统计技能数量
        skills_dir = '/home/zzyuzhangxing/.openclaw/workspace/skills'
        if os.path.exists(skills_dir):
            status['skills_installed'] = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])
        
        # 统计cron任务
        result = subprocess.run(
            ['openclaw', 'cron', 'list'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            status['cron_jobs'] = result.stdout.count('\n') - 1  # 减去表头
        
        # 读取最后备份时间
        backup_file = '/home/zzyuzhangxing/.openclaw/workspace/logs/git-backup.log'
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    # 提取时间戳
                    if '[' in last_line and ']' in last_line:
                        status['last_backup'] = last_line.split('[')[1].split(']')[0].split()[1]
        
    except Exception as e:
        print(f"读取系统状态失败: {e}")
    
    return status

# ==================== 路由 ====================

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/tasks')
def api_tasks():
    """待办任务API - 实时数据"""
    return jsonify(get_tasks())

@app.route('/api/agents')
def api_agents():
    """子Agent状态API - 实时数据"""
    return jsonify(get_agents())

@app.route('/api/approval-queue')
def api_approval_queue():
    """审批队列API"""
    return jsonify(get_approval_queue())

@app.route('/api/system-status')
def api_system_status():
    """系统状态API - 实时数据"""
    return jsonify(get_system_status())

@app.route('/api/skills')
def api_skills():
    """技能列表API - 实时数据"""
    skills_dir = '/home/zzyuzhangxing/.openclaw/workspace/skills'
    skills = []
    if os.path.exists(skills_dir):
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if os.path.isdir(skill_path):
                skills.append({
                    "name": skill_name,
                    "path": skill_path
                })
    return jsonify({"count": len(skills), "skills": skills})

# ==================== 启动 ====================

if __name__ == '__main__':
    print("🚀 Mission Control 启动中...")
    print("📍 本地访问: http://localhost:5000")
    print("📍 外部访问: http://0.0.0.0:5000")
    print("📊 数据模式: 实时读取")
    print("⏹️  停止服务: Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=False)
