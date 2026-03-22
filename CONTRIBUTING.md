# 🤝 参与贡献

<p align="center">
  <strong>技术部门 (Tech Dept) 欢迎各位开发者 💻</strong><br>
  <sub>无论是修复一个 Bug、优化 UI 还是设计一个新的岗位 Agent，我们都非常感谢您的贡献。</sub>
</p>

---

## 📋 贡献方式

### 🐛 报告 Bug

请通过 [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) 提交 Issue，包含以下内容：
- OpenClaw 版本 (`openclaw --version`)
- Python 版本 (`python3 --version`)
- 操作系统信息
- 详细的复现步骤
- 期望结果 vs 实际现象
- 截图（如果涉及看板 UI）

### 💡 功能建议

请使用 [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) 模板。
我们建议您从“业务价值”和“技术实现”两个角度来描述您的建议。

### 🔧 提交 Pull Request (PR)

```bash
# 1. Fork 本仓库
# 2. 克隆您的 Fork 仓库
git clone https://github.com/<your-username>/edict.git
cd edict

# 3. 创建功能分支
git checkout -b feat/new-feature-name

# 4. 本地开发与测试
# 启动看板服务器验证
python3 dashboard/server.py

# 5. 提交代码
git add .
git commit -m "feat: 描述您的改动"

# 6. 推送并创建 PR
git push origin feat/new-feature-name
```

---

## 🏗️ 开发环境

### 前置要求
- 已安装 [OpenClaw](https://openclaw.ai)
- Python 3.9+
- macOS / Linux

### 本地启动流程

```bash
# 安装
./install.sh

# 启动数据刷新（后台运行）
bash scripts/run_loop.sh &

# 启动看板服务器
python3 dashboard/server.py

# 在浏览器中打开
open http://127.0.0.1:7891
```

---

## 🏗️ 项目结构速览

| 目录/文件 | 说明 | 改动频率 |
|----------|------|--------|
| `dashboard/dashboard.html` | 研发看板前端（单文件，React 驱动） | 🔥 高 |
| `dashboard/server.py` | 后端 API 服务器 | 🔥 高 |
| `agents/*/SOUL.md` | 7 个技术岗位的岗位设定与工作流规范 | 🔶 中 |
| `scripts/kanban_update.py` | 研发看板 CLI + 状态机校验逻辑 | 🔶 中 |
| `scripts/*.py` | 数据同步、自动化巡检等脚本 | 🔶 中 |
| `tests/` | 自动化测试用例 | 🔶 中 |

---

## 📝 Commit 规范

我们采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: ✨ 新功能
- `fix`: 🐛 修复 Bug
- `docs`: 📝 文档更新
- `style`: 🎨 代码格式调整（不影响逻辑）
- `refactor`: ♻️ 代码重构
- `perf`: ⚡ 性能优化
- `test`: ✅ 测试相关
- `chore`: 🔧 琐碎任务或维护

---

## 🎯 欢迎贡献的方向

- 🎨 **研发看板 UI**：支持深色模式、优化响应式布局、增强动画效果。
- 🤖 **岗位 Agent 优化**：优化岗位设定（SOUL.md），提升协作效率。
- 📦 **研发 Skills**：为各岗位设计更强大的专业技能包（如自动化测试、代码分析）。
- 🔗 **工具链集成**：集成 Jira, GitHub, Slack 等第三方工具。

---

## 🙏 行为准则

- 保持专业与友善。
- 尊重多样化的观点与经验。
- 接受并提供建设性的反馈。
- 专注于对系统整体效能最有益的改动。

**我们对任何形式的骚扰行为零容忍。**

---

<p align="center">
  <sub>感谢每一位贡献者，你们是技术部门系统不断进化的基石 ⚔️</sub>
</p>
