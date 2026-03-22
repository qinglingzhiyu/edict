# 🚀 快速上手指南

> 从零开始，5 分钟搭建你的技术部门 (Tech Dept) AI 协同系统

---

## 第一步：安装 OpenClaw

技术部门基于 [OpenClaw](https://openclaw.ai) 运行，请先安装：

```bash
# macOS
brew install openclaw

# 或下载安装包
# https://openclaw.ai/download
```

安装完成后初始化：

```bash
openclaw init
```

## 第二步：克隆并安装技术部门系统

```bash
git clone https://github.com/cft0808/edict.git
cd edict
chmod +x install.sh && ./install.sh
```

安装脚本会自动完成：
- ✅ 创建 7 个岗位 Agent Workspace（`~/.openclaw/workspace-*`）
- ✅ 写入各岗位 SOUL.md 人格文件
- ✅ 注册 Agent 及权限矩阵到 `openclaw.json`
- ✅ 配置需求数据清洗规则
- ✅ 构建 React 前端到 `dashboard/dist/`（需 Node.js 18+）
- ✅ 初始化数据目录
- ✅ 执行首次数据同步
- ✅ 重启 Gateway 使配置生效

## 第三步：配置消息渠道

在 OpenClaw 中配置消息渠道（Feishu / Telegram / Signal / QQ），将 `pmo`（PMO）Agent 设为需求入口。PMO 会自动分拣闲聊与指令，研发类消息提炼标题后转发产品经理。

```bash
# 查看当前渠道
openclaw channels list

# 添加飞书渠道（入口设为 PMO）
openclaw channels add --type feishu --agent pmo

# 添加 QQ 渠道（入口设为 PMO）
openclaw channels add --type qq --agent pmo
```

参考 OpenClaw 文档：https://docs.openclaw.ai/channels

## 第四步：启动服务

```bash
# 终端 1：数据刷新循环（每 15 秒同步）
bash scripts/run_loop.sh

# 终端 2：看板服务器
python3 dashboard/server.py

# 打开浏览器
open http://127.0.0.1:7891
```

> 💡 **提示**：`run_loop.sh` 每 15 秒自动同步数据。可用 `&` 后台运行。

> 💡 **看板即开即用**：`server.py` 内嵌 `dashboard/dashboard.html`，无需额外构建。Docker 镜像包含预构建的 React 前端。

## 第五步：发送第一个需求

通过消息渠道发送任务（PMO 会自动识别并转发到产品经理）：

```
请帮我用 Python 写一个文本分类器：
1. 使用 scikit-learn
2. 支持多分类
3. 输出混淆矩阵
4. 写完整的文档
```

## 第六步：观察执行过程

打开看板 http://127.0.0.1:7891

1. **📋 研发看板** — 观察任务在各状态（Backlog, Planning, Designing, Developing, Testing, Released）之间流转
2. **🔭 岗位调度** — 查看各岗位工作分布
3. **📜 项目归档** — 任务完成后自动归档并生成时间线

任务流转路径：
```
需求池 (Backlog) → 产品规划 (Planning) → 设计中 (Designing) → 开发中 (Developing) → 测试联调 (Testing) → 已上线 (Released)
```

---

## 🎯 进阶用法

### 使用需求模板

> 看板 → 📜 模板库 → 选择模板 → 填写参数 → 提需求

预设模板：功能开发 · Bug 修复 · 技术重构 · 代码审查 · API 设计 · 竞品分析 · 数据报告 · 部署方案 · 站会摘要

### 切换岗位模型

> 看板 → ⚙️ 模型配置 → 选择新模型 → 应用更改

约 5 秒后 Gateway 自动重启生效。

### 管理技能

> 看板 → 🛠️ 技能配置 → 查看已安装技能 → 点击添加新技能

### 叫停 / 取消任务

> 在研发看板或任务详情中，点击 **⏸ 叫停** 或 **🚫 取消** 按钮

---

## 💡 进阶功能：公共技能 (Common Skills)

如果你希望为**所有** Agent 添加通用技能（如 `code_review`, `data_analysis` 等），可以将技能存放在 `~/.openclaw/common-skills` 目录下。

系统启动时会自动将该目录下的所有技能合并到每个 Agent 的技能列表中。

### 添加公共技能

```bash
python3 scripts/skill_manager.py add-remote \
  --agent common \
  --name code_review \
  --source https://raw.githubusercontent.com/.../SKILL.md \
  --description "全员通用代码审查技能"
```

---

## 常见问题

### 看板显示「服务器未启动」
```bash
# 确认服务器正在运行
python3 dashboard/server.py
```

### Agent 报错 "No API key found for provider"

这是最常见的问题。系统有多个 Agent，每个都需要 API Key。

```bash
# 方法一：为任意 Agent 配置后重新运行 install.sh（推荐）
openclaw agents add pmo          # 按提示输入 API Key
cd edict && ./install.sh         # 自动同步到所有 Agent

# 方法二：手动复制 auth 文件
MAIN_AUTH=$(find ~/.openclaw/agents -name auth-profiles.json | head -1)
for agent in pmo product ui frontend backend qa ops; do
  mkdir -p ~/.openclaw/agents/$agent/agent
  cp "$MAIN_AUTH" ~/.openclaw/agents/$agent/agent/auth-profiles.json
done
```

### Agent 不响应
```bash
# 检查 Gateway 状态
openclaw gateway status

# 必要时重启
openclaw gateway restart
```

---

## 📚 更多资源

- [🏠 项目首页](https://github.com/cft0808/edict)
- [📖 README](../README.md)
- [🤝 贡献指南](../CONTRIBUTING.md)
- [💬 OpenClaw 文档](https://docs.openclaw.ai)
