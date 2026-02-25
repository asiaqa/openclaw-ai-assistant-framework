# HEARTBEAT.md - 系统事件处理

> **重要**: 本文件记录已生效的任务配置  
> **变更规则**: 任何任务的新增/修改/删除 **必须** 获得用户明确许可后方可执行

---

## 系统事件响应规则

当收到以下系统事件时，执行对应操作：

### run_skill_learning
**触发**: 每小时整点
**操作**: 
```bash
cd ~/.openclaw/workspace && node learn-skill.js >> learn-cron.log 2>&1
```
**说明**: 从SkillsMP搜索并学习一个新技能

### fetch_bilibili_account
**触发**: 每天 09:00
**操作**:
```bash
cd ~/.openclaw/workspace && python3 scripts/bilibili-account-fetch.py
```
**说明**: 获取老鱼B站个人账号数据（粉丝、播放、视频表现）

### fetch_ai_intelligence
**触发**: 每天 09:00
**操作**:
```bash
cd ~/.openclaw/workspace && python3 scripts/ai-intelligence-monitor.py
```
**说明**: 泛AI情报监控（B站全站AI相关内容，不限分区，130关键词搜索）

### generate_daily_report
**触发**: 每天 09:30
**操作**:
```bash
cd ~/.openclaw/workspace && python3 scripts/generate-daily-report.py
```
**说明**: 生成统一每日汇报（包含账号数据、AI情报、技能学习）

### git_backup
**触发**: 每30分钟
**操作**:
```bash
cd ~/.openclaw/workspace && git add . && git commit -m "auto: $(date +%Y-%m-%d-%H:%M) backup" && git push origin main 2>/dev/null || true
```
**说明**: 本地工作区Git备份（自动提交到Git仓库，含所有配置文件、脚本、记忆文件）

---

## 每日汇报时间线

| 时间 | 任务 | 产出 |
|------|------|------|
| 09:00 | B站账号数据获取 | 个人账号报告 |
| 09:00 | 泛AI情报监控 | 全站AI热门（不限分区） |
| 09:30 | 生成统一汇报 | 完整日报 |
| 每小时 | 技能学习 | 新技能 |
| 每30分钟 | Git备份 | 自动备份 |

---

## 汇报内容模块

- **B站账号数据**: 粉丝数、播放量、视频表现（Cookie登录获取）
- **B站全站AI**: AI热门视频Top 10（全站关键词搜索，130关键词）
- **技能学习**: 今日学习的新技能（每小时学习记录）
- **系统状态**: 定时任务运行状态监控

---

## 已取消的任务

> 以下任务曾经存在但已取消，恢复需用户明确许可

| 任务 | 原频率 | 取消原因 | 取消时间 |
|------|--------|----------|----------|
| B站科技区爬取 | 10:00/22:00 | 与全站监控重复 | 2026-02-25 |
| X(Twitter)监控 | 每天4次 | API需付费 | 2026-02-25 |
| 抖音监控 | - | 反爬机制太强 | 2026-02-25 |

---

## 常规Heartbeat检查

如果收到常规 heartbeat（无特定事件），检查：
1. 定时任务状态 - `openclaw cron list`
2. 磁盘空间使用情况
3. 最近的错误日志

如一切正常，回复: HEARTBEAT_OK

---

_更新: 2026-02-25_  
_任务数: 5个运行中 | 变更需授权: ✅_
