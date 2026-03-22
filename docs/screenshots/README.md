# 📸 截图说明

看板截图用于 README 和文档展示。请启动看板后按以下顺序截图并放置到本目录。

## 截图清单

| 文件名 | 内容 | 对应面板 |
|--------|------|---------|
| `01-kanban-main.png` | 研发看板总览 | 📋 研发看板 |
| `02-monitor.png` | 岗位调度监控 | 🔭 岗位调度 |
| `03-task-detail.png` | 任务流转详情 | 📋 详情弹窗 |
| `04-model-config.png` | 模型配置面板 | ⚙️ 模型配置 |
| `05-skills-config.png` | 技能配置面板 | 🛠️ 技能配置 |
| `06-official-overview.png` | 效能总览 | 👥 效能统计 |
| `07-sessions.png` | 实时会话记录 | 💬 会话流 |
| `08-memorials.png` | 项目归档 | 📜 项目归档 |
| `09-templates.png` | 需求模板库 | 📜 模板库 |
| `10-morning-briefing.png` | 天下要闻 | 📰 每日简报 |
| `11-ceremony.png` | 启动开场动画 | 开场动画 |

## 自动截图

```bash
# 确保看板服务器正在运行
python3 dashboard/server.py &

# 自动截取全部截图
python3 scripts/take_screenshots.py
```

## 建议

- 使用 **1920×1080** 分辨率
- 确保看板有足够的数据（至少 5+ 任务）
- 深色主题截图效果最佳
