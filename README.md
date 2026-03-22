<h1 align="center">💻 技术部门 · Edict (Tech Dept)</h1>

<p align="center">
  <strong>基于现代互联网技术部门工作流的 AI 多 Agent 协作系统。<br>
  从需求池到上线，全生命周期自动化管理。</strong>
</p>

<p align="center">
  <sub>7 个核心 AI 岗位（PMO、产品、UI、前端、后端、测试、运维）构成的协作闭环：<br>需求分拣、产品规划、界面设计、并行开发、质量保证、自动化部署。<br>
  比普通 Agent 框架多一层<b>严格的阶段审核</b>，比传统看板多一个<b>实时执行大脑</b>。</sub>
</p>

<p align="center">
  <a href="#-快速体验">🚀 快速体验</a> ·
  <a href="#-岗位架构">🏛️ 岗位架构</a> ·
  <a href="#-功能全景">📋 研发看板</a> ·
  <a href="tech_dept_prd.md">📚 详细 PRD</a> ·
  <a href="CONTRIBUTING.md">参与贡献</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Required-blue?style=flat-square" alt="OpenClaw">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Agents-7_Specialized-8B5CF6?style=flat-square" alt="Agents">
  <img src="https://img.shields.io/badge/Workflow-Agile-F59E0B?style=flat-square" alt="Agile Workflow">
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat-square&logo=react&logoColor=white" alt="React">
</p>

---

## 🎬 核心理念

传统的 Multi-Agent 协作往往缺乏结构化的流程和质量控制。**技术部门 (Tech Dept)** 引入了现代互联网公司的成熟工作流：

```
需求方 → PMO (需求池) → 产品经理 (规划) → UI 设计师 (设计) → 研发 (开发) → 测试 (验证) → 运维 (发布)
```

这不仅是角色名称的改变，更是**职责的分权与制衡**：

| 特性 | 传统 AI 协作 | **技术部门 (Tech Dept)** |
|---|:---:|:---:|
| **流程控制** | 自由讨论，容易偏离 | **严格的阶段流转校验** |
| **质量关卡** | 无审核，产出质量参差不齐 | **测试工程师专职验收，不合格打回** |
| **透明度** | 过程黑盒，仅见结果 | **实时看板展现每个岗位的思考过程** |
| **并行效率** | 串行执行为主 | **支持前后端并行开发与联调** |
| **任务追溯** | 散落在对话记录中 | **完整的项目执行日志与归档** |

---

## ✨ 功能全景

### 🏛️ 7 大核心技术岗位
- **PMO**：需求入口，负责项目建档与全局进度监控。
- **产品经理**：需求分析，输出 PRD 并拆解子任务。
- **UI 设计师**：视觉设计，输出界面稿与交互规范。
- **前端/后端工程师**：工程实现，支持接口对接与联调。
- **测试工程师**：质量把控，执行测试并反馈 Bug。
- **运维工程师**：环境部署，负责最终的生产上线。

### 📋 研发看板 (Dashboard)
- **Kanban 看板**：按 Backlog, Planning, Designing, Developing, Testing, ReadyForRelease 展示。
- **调度监控**：实时查看各岗位活跃度、Token 消耗与健康状态。
- **项目详情**：查看完整的任务流转记录，支持暂停、取消、恢复操作。
- **模板库**：预设“功能开发”、“Bug 修复”、“技术重构”等常用任务模板。
- **模型热切换**：看板内一键切换每个岗位使用的 LLM（Claude/GPT/DeepSeek 等）。

---

## 🚀 快速体验

### 前置条件
- 已安装 [OpenClaw](https://openclaw.ai)
- Python 3.9+
- macOS / Linux

### 安装与启动

```bash
# 1. 克隆并安装
git clone https://github.com/cft0808/edict.git
cd edict
chmod +x install.sh && ./install.sh

# 2. 启动数据刷新循环（后台）
bash scripts/run_loop.sh &

# 3. 启动看板服务器
python3 dashboard/server.py
```
打开浏览器访问：[http://127.0.0.1:7891](http://127.0.0.1:7891)

---

## 🏛️ 协作流程

```
                           ┌───────────────────────────────────┐
                           │          👑 需求方（用户）           │
                           └─────────────────┬─────────────────┘
                                             │ 提需求
                           ┌─────────────────▼─────────────────┐
                           │          📅 PMO (pmo)             │
                           │    分拣、建档、指派产品经理          │
                           └─────────────────┬─────────────────┘
                                             │ 派发
                           ┌─────────────────▼─────────────────┐
                           │          📋 产品经理 (product)      │
                           │      需求分析 -> PRD -> 任务拆解    │
                           └─────────────────┬─────────────────┘
                                             │ 提交设计/开发
                           ┌─────────────────▼─────────────────┐
                           │          🎨 UI 设计师 (ui)         │
                           │       视觉设计稿 -> 交互规范         │
                           └─────────────────┬─────────────────┘
                                             │ 设计完成
               ┌─────────────────────────────┴─────────────────────────────┐
               │                                                           │
     ┌─────────▼─────────┐                                       ┌─────────▼─────────┐
     │   💻 前端开发 (fe)  │                                       │   ⚙️ 后端开发 (be)  │
     │     页面逻辑实现    │ <─────────── API 联调 ───────────>   │    业务逻辑/数据库   │
     └─────────┬─────────┘                                       └─────────┬─────────┘
               │                                                           │
               └─────────────────────────────┬─────────────────────────────┘
                                             │ 提测
                           ┌─────────────────▼─────────────────┐
                           │          ⚖️ 测试工程师 (qa)        │
                           │       功能验证 -> Bug 反馈 -> 验收   │
                           └─────────────────┬─────────────────┘
                                             │ 验收通过
                           ┌─────────────────▼─────────────────┐
                           │          🚀 运维工程师 (ops)       │
                           │       环境部署 -> 发布上线 -> 汇报   │
                           └───────────────────────────────────┘
```

---

## 📄 License

[MIT](LICENSE) · 由 [OpenClaw](https://openclaw.ai) 社区构建
