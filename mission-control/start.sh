#!/bin/bash
# Mission Control 启动脚本

cd /home/zzyuzhangxing/.openclaw/workspace/mission-control

echo "🚀 启动 Mission Control..."
echo "📍 访问地址: http://localhost:5000"
echo "⏹️  停止服务: Ctrl+C"
echo ""

python3 app.py
