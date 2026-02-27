#!/bin/bash
# 智能备份脚本 - 基于24h或10K变化触发
# 功能：备份配置文件和记忆文件，7天轮换

BACKUP_BASE="/home/zzyuzhangxing/.openclaw/backups"
WORKSPACE="/home/zzyuzhangxing/.openclaw/workspace"
DAY_OF_WEEK=$(date +%A)  # Monday, Tuesday, etc.
BACKUP_DIR="$BACKUP_BASE/$DAY_OF_WEEK"
LOG_FILE="/home/zzyuzhangxing/.openclaw/workspace/logs/backup.log"

# 需要备份的文件列表
BACKUP_FILES=(
    "MEMORY.md"
    "USER.md"
    "IDENTITY.md"
    "SOUL.md"
    "AGENTS.md"
    "HEARTBEAT.md"
    "TOOLS.md"
    "openclaw.json"
    "skills-learning-log.json"
    "mission-control/ITERATION_PLAN.md"
)

# 创建备份目录
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname $LOG_FILE)"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查是否需要备份
need_backup() {
    local file=$1
    local backup_file="$BACKUP_DIR/$(basename $file)"
    
    # 如果备份不存在，需要备份
    if [ ! -f "$backup_file" ]; then
        log "📥 需要备份: $file (备份不存在)"
        return 0
    fi
    
    # 检查时间差异（超过24小时）
    local last_backup=$(stat -c %Y "$backup_file" 2>/dev/null || echo 0)
    local now=$(date +%s)
    local time_diff=$((now - last_backup))
    
    if [ $time_diff -gt 86400 ]; then
        log "⏰ 需要备份: $file (超过24小时)"
        return 0
    fi
    
    # 检查大小差异（超过10K）
    local original_size=$(stat -c %s "$WORKSPACE/$file" 2>/dev/null || echo 0)
    local backup_size=$(stat -c %s "$backup_file" 2>/dev/null || echo 0)
    local size_diff=$((original_size - backup_size))
    
    if [ $size_diff -lt 0 ]; then
        size_diff=$((-size_diff))
    fi
    
    if [ $size_diff -gt 10240 ]; then
        log "📊 需要备份: $file (大小变化超过10K)"
        return 0
    fi
    
    return 1
}

# 执行备份
backup_file() {
    local file=$1
    local source="$WORKSPACE/$file"
    local dest="$BACKUP_DIR/$(basename $file)"
    
    if [ -f "$source" ]; then
        cp "$source" "$dest"
        log "✅ 已备份: $file"
    else
        log "⚠️  文件不存在: $file"
    fi
}

# 主备份流程
log "="
log "🔄 开始智能备份检查"
log "="

backup_count=0

for file in "${BACKUP_FILES[@]}"; do
    if need_backup "$file"; then
        backup_file "$file"
        backup_count=$((backup_count + 1))
    fi
done

log "📊 本次备份: $backup_count 个文件"
log "="

# 同步到iCloud（如果配置了）
ICLOUD_DIR="/home/zzyuzhangxing/iCloudDrive/OpenClaw-Backup"
if [ -d "$ICLOUD_DIR" ]; then
    rsync -av "$BACKUP_BASE/" "$ICLOUD_DIR/" >> "$LOG_FILE" 2>&1
    log "☁️  已同步到iCloud"
fi

echo "备份完成: $backup_count 个文件"
