# OpenClaw AI Assistant Framework

一个专业、高效、自主成长的AI助手框架，专为AI自媒体博主设计。

## ⚠️ 重要安全提示

**警告：** 仓库历史中存在危险的 `cleanup-github.sh` 脚本（已在最新版本删除）。

**请勿运行历史版本中的 `cleanup-github.sh`！**
- 该脚本包含强制删除命令，会删除您的个人文件
- 仅适用于原作者清理自己的仓库
- 如果您已经运行了该脚本，请立即停止并恢复您的数据

**安全使用建议：**
- 使用最新版本的代码
- 不要运行任何包含 `git rm -rf` 或 `rm -rf` 的脚本
- Fork后请先检查所有脚本的安全性

## ✨ 特性

### 🚀 核心能力
- **7步深度使用法**：智能备份、模型池、会话识别、上下文压缩、任务铁律、陌生任务处理、自我进化
- **24小时定向学习**：根据时段自动学习相关技能（视觉创作 + 自媒体运营）
- **AI自我成长**：Skill深度学习、经验总结、知识整合、创造新能力
- **3层记忆体系**：工作记忆、短期记忆、长期记忆
- **10个定时任务**：自动维护、学习、进化、报告

### 📊 模型池体系
- 高速池：zai/glm-4.7（快速响应）
- 智能池：zai/glm-5（复杂推理）
- 文本池：zai/glm-5（长文本）
- 视觉池：zai/glm-4.6v（图片/视频）

### 🎯 24小时学习规则
- 前12小时（00:00-12:00）：视觉创作时段
  - 00:00-04:00：图像生成、提示词工程
  - 04:00-08:00：视频制作、剪辑工具
  - 08:00-12:00：视觉优化、设计工具
- 后12小时（12:00-24:00）：自媒体运营时段
  - 12:00-16:00：内容创作、文案写作
  - 16:00-20:00：社交媒体、互动运营
  - 20:00-24:00：数据分析、自动化营销

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/Work-Fisher/openclaw-ai-assistant-framework.git
cd openclaw-ai-assistant-framework
chmod +x install.sh
./install.sh
```

### 2. 配置模型池

编辑 `config/model-pools.json` 配置模型池：
```json
{
  "version": 2,
  "pools": {
    "fast": {
      "primary": "zai/glm-4.7",
      "fallback": "zai/glm-4.7"
    },
    "smart": {
      "primary": "zai/glm-5",
      "fallback": "zai/glm-5"
    },
    "text": {
      "primary": "zai/glm-5",
      "fallback": "zai/glm-4.7"
    },
    "vision": {
      "primary": "zai/glm-4.6v",
      "fallback": "zai/glm-4.6v"
    }
  }
}
```

### 3. 配置24小时学习计划

编辑 `config/skill-learning-schedule.json`：
```json
{
  "hourly_rotation": {
    "00-04": ["image", "prompt", "ai-art", "generation"],
    "04-08": ["video", "editing", "production", "creative"],
    "08-12": ["design", "graphics", "photo", "visual"],
    "12-16": ["content", "writing", "copywriting", "blog"],
    "16-20": ["social", "twitter", "weibo", "engagement"],
    "20-24": ["analytics", "automation", "seo", "marketing"]
  }
}
```

### 4. 启动定时任务

```bash
# Heartbeat检查（每30分钟）
openclaw cron add --name "heartbeat-notify" --cron "*/30 * * * *" --session isolated ...

# 技能学习（每小时）
openclaw cron add --name "install-skills-infinite" --cron "0 * * * *" --session isolated ...

# 每日进化报告（每天22:00）
openclaw cron add --name "daily-evolution" --cron "0 22 * * *" --session main ...

# 每日成长报告（每天09:00）
openclaw cron add --name "daily-growth-report" --cron "0 9 * * *" --session isolated ...
```

## 📚 文档

### 核心文档
- [完整框架文档](docs/openclaw-ai-assistant-framework.md) - OpenClaw 7步深度使用法
- [AI自我成长计划](docs/ai-self-evolution-plan.md) - 6大成长维度
- [Skill深度学习](docs/skill-deep-learning.md) - 知识提取与整合
- [上下文压缩机制](docs/context-compression-mechanism.md) - 框架固化
- [每日成长报告](docs/daily-growth-report-mechanism.md) - 成长可视化

### 配置文档
- [模型池配置](config/model-pools.md) - 4层模型池体系
- [会话路由](config/session-routing.md) - 自动选择模型池
- [任务铁律](config/task-iron-law.md) - 5轮尝试机制
- [24小时学习计划](config/skill-learning-schedule.json) - 定向学习

## 🔧 核心脚本

### 学习相关
- `learn-skill-infinite.js` - 24小时定向学习脚本
- `scripts/extract-skill-knowledge.py` - Skill知识提取

### 维护相关
- `scripts/heartbeat-check.py` - 心跳检查与反思
- `scripts/daily-evolution.py` - 每日进化报告
- `scripts/smart-backup.sh` - 智能备份（7天轮换）
- `scripts/model-health-check.py` - 模型池健康检查

## 📊 架构

### 三层记忆体系
- **L1 工作记忆**：当前会话临时记忆
- **L2 短期记忆**：每日记忆文件（memory/YYYY-MM-DD.md）
- **L3 长期记忆**：永久记忆文件（MEMORY.md）

### 定时任务体系（10个）
1. **heartbeat-notify** - 每30分钟（记忆维护）
2. **smart-backup** - 每小时（智能备份）
3. **model-health-check** - 每6小时（模型健康）
4. **install-skills-infinite** - 每小时（技能学习）
5. **daily-evolution** - 每天22:00（进化报告）
6. **daily-growth-report** - 每天09:00（成长报告）
7. **daily-report-gen** - 每天09:30（日报生成）
8. **mission-control-weekly** - 每周一20:00（迭代）

## 🚀 版本历史

### v3.0 (2026-02-28) - 自我成长版
- ✅ 24小时定向学习系统
- ✅ AI自我成长机制
- ✅ Skill深度学习机制
- ✅ 经验总结机制
- ✅ 知识整合机制
- ✅ 每日成长报告

### v2.0 (2026-02-27) - 框架固化版
- ✅ 7步深度使用框架
- ✅ 4层模型池体系
- ✅ 3层记忆体系
- ✅ 11个定时任务
- ✅ Heartbeat记忆维护

## 🎯 目标

### 短期（1个月）
- 技能总数达到100个
- 知识点达到200个
- 创造5个新能力

### 中期（3个月）
- 完全自主成长
- 创造10个新能力
- 成为专家级助手

### 长期（6个月）
- 持续优化进化
- 创造独特方法
- 成为不可或缺的助手

## 📄 许可

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**创建时间**：2026-02-27
**当前版本**：v3.0（自我成长版）
**维护者**：Work-Fisher
