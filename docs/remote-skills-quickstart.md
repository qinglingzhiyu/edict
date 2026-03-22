# 远程 Skills 快速入门

## 5 分钟体验

### 1. 启动服务器

```bash
# 确保你在项目根目录
python3 dashboard/server.py
# 输出: 技术部门研发看板启动 → http://127.0.0.1:7891
```

### 2. 添加官方 Skill（CLI）

```bash
# 为产品经理添加代码审查 skill
python3 scripts/skill_manager.py add-remote \
  --agent product \
  --name code_review \
  --source https://raw.githubusercontent.com/openclaw-ai/skills-hub/main/code_review/SKILL.md \
  --description "代码审查能力"

# 输出:
# ⏳ 正在从 https://raw.githubusercontent.com/... 下载...
# ✅ 技能 code_review 已添加到 product
```

### 3. 列出所有远程 Skills

```bash
python3 scripts/skill_manager.py list-remote

# 输出:
# 📋 共 1 个远程 skills：
# 
# Agent       | Skill 名称           | 描述                           | 添加时间
# ------------|----------------------|--------------------------------|----------
# product     | code_review          | 代码审查能力                   | 2026-03-02
```

---

## 常见操作

### 一键导入官方库中的所有 skills

```bash
python3 scripts/skill_manager.py import-official-hub \
  --agents product,ui,frontend,backend,qa,ops
```

这会自动为每个岗位添加对应的专业技能。

### 更新某个 Skill 到最新版本

```bash
python3 scripts/skill_manager.py update-remote \
  --agent product \
  --name code_review
```

### 移除某个 Skill

```bash
python3 scripts/skill_manager.py remove-remote \
  --agent product \
  --name code_review
```

---

## 看板 UI 操作

### 在看板中添加 Remote Skill

1. 打开 http://localhost:7891
2. 进入 🛠️ **技能配置** 面板
3. 点击 **➕ 添加远程 Skill** 按钮
4. 填写表单（如 Agent 选择 `product`，Skill 名称填 `code_review`）
5. 点击 **导入** 按钮

---

## 更多信息

- 📚 [完整指南](remote-skills-guide.md)
- 🏛️ [架构文档](task-dispatch-architecture.md)
- 🤝 [项目贡献](../CONTRIBUTING.md)
