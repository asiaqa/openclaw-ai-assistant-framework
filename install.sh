#!/bin/bash
# OpenClaw AI助手框架 - 快速安装脚本

echo "🚀 开始安装 OpenClaw AI助手框架..."
echo "=================================================="

# 步骤1：创建目录结构
echo "📁 创建目录结构..."
mkdir -p ~/.openclaw/workspace/{config,scripts,data,memory,skills,logs}
mkdir -p ~/.openclaw/workspace/data/{daily-reports,evolution-reports}
mkdir -p ~/.openclaw/backups
echo "✅ 目录创建完成"

# 步骤2：创建核心文件
echo "📝 创建核心配置文件..."
touch ~/.openclaw/workspace/{IDENTITY.md,USER.md,SOUL.md,MEMORY.md,HEARTBEAT.md,AGENTS.md,TOOLS.md}
echo "✅ 核心文件创建完成"

# 步骤3：安装ClawHub CLI
echo "📦 安装 ClawHub CLI..."
if ! command -v clawhub &> /dev/null; then
    npm install -g clawhub
    echo "✅ ClawHub CLI 安装完成"
else
    echo "✅ ClawHub CLI 已安装"
fi

# 步骤4：安装核心技能
echo "📚 安装核心技能..."
clawhub install python --force
clawhub install writer --force
clawhub install summarize --force
clawhub install image --force
echo "✅ 核心技能安装完成"

# 步骤5：配置定时任务
echo "⏰ 配置定时任务..."
#openclaw cron add --name "heartbeat-check" --cron "*/30 * * * *" --exact --system-event "heartbeat_check" 2>/dev/null || true
openclaw cron add --name "daily-evolution" --cron "0 22 * * *" --exact --system-event "daily_evolution" 2>/dev/null || true
#openclaw cron add --name "model-health-check" --cron "0 */6 * * *" --exact --system-event "model_health_check" 2>/dev/null || true
openclaw cron add --name "smart-backup" --cron "0 * * * *" --exact --system-event "smart_backup_check" 2>/dev/null || true
echo "✅ 定时任务配置完成"

# 步骤6：验证安装
echo "🔍 验证安装..."
echo ""
echo "定时任务列表:"
openclaw cron list
echo ""
echo "✅ 安装完成！"
echo ""
echo "📖 下一步："
echo "1. 编辑 ~/.openclaw/workspace/IDENTITY.md - 设置身份"
echo "2. 编辑 ~/.openclaw/workspace/USER.md - 设置用户信息"
echo "3. 查看完整文档: ~/.openclaw/workspace/docs/openclaw-ai-assistant-framework.md"
echo ""
echo "=================================================="
echo "🎉 OpenClaw AI助手框架安装成功！"
