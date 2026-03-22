# 远程 Skills 资源管理指南

## 概述

技术部门协作系统 (Tech Dept) 现已支持从网上连接和增补 skills 资源，无需手动复制文件。支持从以下来源获取：

- **GitHub 仓库** (raw.githubusercontent.com)
- **任何 HTTPS URL** (需返回有效的 skill 文件)
- **本地文件路径**
- **内置仓库** (官方 skills 库)

---

## 功能架构

### 1. API 端点

#### `POST /api/add-remote-skill`

从远程 URL 或本地路径为指定 Agent 添加 skill。

**请求体：**
```json
{
  "agentId": "product",
  "skillName": "code_review",
  "sourceUrl": "https://raw.githubusercontent.com/org/skills-repo/main/code_review/SKILL.md",
  "description": "代码审查专项技能"
}
```

**参数说明：**
- `agentId` (string, 必需): 目标 Agent ID (如 product, frontend, backend 等)
- `skillName` (string, 必需): skill 的内部名称 (仅允许字母/数字/下划线/汉字)
- `sourceUrl` (string, 必需): 远程 URL 或本地文件路径
- `description` (string, 可选): skill 的中文描述

---

## CLI 命令

### 添加远程 Skill

```bash
python3 scripts/skill_manager.py add-remote \
  --agent product \
  --name code_review \
  --source https://raw.githubusercontent.com/org/skills-repo/main/code_review/SKILL.md \
  --description "代码审查专项技能"
```

### 列出远程 Skills

```bash
python3 scripts/skill_manager.py list-remote
```

---

## 官方 Skills 库

### OpenClaw Skills Hub

> **官方 skills 库地址**: https://github.com/openclaw-ai/skills-hub

可用 skills 列表：

| Skill 名称 | 描述 | 适用 Agent |
|-----------|------|----------|
| `code_review` | 代码审查（支持 Python/JS/Go） | backend / qa |
| `api_design` | API 设计审查 | backend / product |
| `security_audit` | 安全审计 | qa |
| `data_analysis` | 数据分析 | backend |
| `doc_generation` | 文档生成 | frontend / product |
| `test_framework` | 测试框架设计 | qa / ops |

**一键导入官方 skills**

```bash
python3 scripts/skill_manager.py import-official-hub \
  --agents product,ui,frontend,backend,qa,ops
```

---

## 看板 UI 操作

### 快捷添加 Skill

1. 打开看板 → 🛠️ **技能配置** 面板
2. 点击 **➕ 添加远程 Skill** 按钮
3. 填写表单并点击 **确认**

---

## 安全考虑

远程 skills 在沙箱中执行（由 OpenClaw runtime 提供），无法访问敏感配置文件，只能访问分配的 workspace 目录。

---

## 故障排查

**Q: 下载失败，提示 "Connection timeout"**
A: 检查网络连接和 URL 有效性。中国大陆访问 GitHub 可能需要配置代理。

**Q: 如何创建自己的 skills 库？**
A: 参考 [OpenClaw Skills Hub](https://github.com/openclaw-ai/skills-hub) 的结构创建自己的仓库，然后通过 URL 导入即可。

---

<p align="center">
  <sub>用 <strong>开放</strong> 的生态，赋能 <strong>流程化</strong> 的 AI 协作</sub>
</p>
