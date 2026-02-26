#!/bin/bash
# Git auto-backup script

cd /home/zzyuzhangxing/.openclaw/workspace || exit 1

git add .
git commit -m "auto: $(date +%Y-%m-%d-%H:%M) backup"
git push origin main 2>/dev/null || true