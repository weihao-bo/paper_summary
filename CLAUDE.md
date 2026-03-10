# CLAUDE.md

本文件为 AI 编程助手（如 Claude Code、Gemini 等）提供项目规范和指导。**所有提交必须严格遵循以下规范。**

## 项目概述

这是一个**交互式可视化页面合集**的静态网站仓库，通过 GitHub Pages 部署。内容涵盖论文架构解读、数据集浏览、评测结果展示、分析报告及工具流程可视化等。

- **部署地址**：`https://weihao-bo.github.io/paper_summary/`
- **部署方式**：GitHub Pages，从 `main` 分支根目录自动部署

## 页面分类

本仓库的页面按功能分为以下六类：

| 分类 | 说明 | 示例 |
|------|------|------|
| 📄 论文解读 | 论文/代码仓库的架构可视化 | `2024_locomo.html` |
| 📊 数据集展示 | 数据集的交互式浏览与统计 | `SciDiagram.html` |
| 📈 评测结果 | 模型/工具的评测结果展示 | `scidiagram_eval_standard.html` |
| 🔬 分析报告 | 技术分析、对比、局限性研究 | `de_vs_d2c_analysis.html` |
| 🛠️ 工具/流程 | 工具链、工作流的可视化 | `mcp_trace_analysis.html` |
| 📝 会议总结 | 会议/峰会的观点总结 | `2026_ai_summit.html` |

---

## 文件命名规范

### 推荐格式

```
{year}_{topic_id}.html
```

- `year`：内容相关年份（4 位数字）
- `topic_id`：主题简称（**全小写，下划线分隔**）
- 示例：`2024_locomo.html`、`2025_cad_survey.html`、`2026_ai_summit.html`

### 已知不规范文件（历史遗留，暂不重命名）

以下文件因历史原因未遵循命名规范，为避免破坏已分享的 GitHub Pages 链接，暂时保留原名：

- `SciDiagram.html`、`SciDiagram_Task.html`、`SciDiagram_Task_MINI.html`
- `Artificial_Analysis_Intelligence.html`
- `cleaner_comparison.html`、`fallback_analysis.html`
- `scidiagram_eval_standard.html`、`scidiagram_eval_strict.html`
- `scidiagram_reevaluated_visualization.html`、`scidiagram_workflow.html`
- `latex_eval_statistics.html`、`latex_local_eval.html`
- `mcp_trace_analysis.html`、`de_vs_d2c_analysis.html`
- `video_agent_tool_pool.html`

**⚠️ 新增页面必须遵循推荐命名格式，不得再使用不规范命名。**

---

## 添加新页面的流程

每次添加新页面时，必须完成以下**所有步骤**，缺一不可：

### 1. 创建 HTML 文件

- 按照 `{year}_{topic_id}.html` 命名规范创建文件
- 所有 CSS 内联在 HTML 中，保持文件独立可用（无外部依赖）

### 2. HTML 文件结构要求

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{页面标题}</title>
    <!-- 内联样式 -->
</head>
<body>
    <header>
        <h1>{页面标题}</h1>
        <p class="subtitle">{分类} · {年份}</p>
    </header>
    <!-- 内容区域 -->
</body>
</html>
```

### 3. 更新 README.md（⚠️ 必须）

在 README.md **对应分类**的表格中添加一行：

```markdown
| {页面名称} | {简要功能描述} | [查看](https://weihao-bo.github.io/paper_summary/{文件名}) |
```

### 4. 提交并推送

确保 HTML 文件和更新后的 README.md 在同一次提交中。

---

## 提交规范

### 提交信息格式

**新增页面**：
```
Add: {页面名称}
```

**更新页面**：
```
Update: {页面名称}（{变更说明}）
```

**修复问题**：
```
Fix: {问题简述}
```

**回退操作**：
```
Revert: {回退说明}
```

### 提交检查清单

每次提交前，确认以下事项：

- [ ] HTML 文件命名遵循 `{year}_{topic_id}.html` 格式
- [ ] HTML 文件中包含正确的 `<title>` 标签
- [ ] CSS 全部内联，无外部依赖
- [ ] 新增页面已在 README.md 对应分类的表格中添加记录
- [ ] 提交信息遵循上述格式规范

---

## 样式规范

- 所有 CSS 内联在 HTML 文件中，保持每个文件独立可用
- 推荐配色方案：
  - 主色：`#4F46E5`（紫蓝色）
  - 次色：`#10B981`（绿色）
  - 警告：`#F59E0B`（橙色）
  - 背景：`#F9FAFB`（浅灰）
- 支持响应式设计，适配移动端

## 常用命令

```bash
# 本地预览
cd /Users/boweihao/Documents/paper_summary
python -m http.server 8000
# 访问 http://localhost:8000

# 提交并推送
git add .
git commit -m "Add: {页面名称}"
git push origin main
```
