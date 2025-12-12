# CLAUDE.md

本文件为 Claude Code 提供项目规范和指导。

## 项目概述

这是一个论文架构总结的静态网站仓库，通过 GitHub Pages 部署。每个 HTML 文件对应一篇论文/代码仓库的架构可视化。

## 添加新论文的流程

### 1. 创建 HTML 文件

- **命名格式**：`{year}_{paper_id}.html`
  - `year`: 论文发表年份（4 位数字）
  - `paper_id`: 论文简称（小写，下划线分隔）
  - 示例：`2024_locomo.html`, `2023_multi_session_chat.html`

### 2. HTML 文件规范

每个 HTML 文件应包含：
- 论文标题和会议信息
- 代码仓库架构可视化
- 核心模块说明
- 数据流程图
- 关键代码片段解释

推荐的 HTML 结构：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{论文名称} 代码仓库架构详解</title>
    <!-- 内联样式，保持文件独立 -->
</head>
<body>
    <header>
        <h1>{论文名称} 代码仓库架构详解</h1>
        <p class="subtitle">{会议} {年份}</p>
    </header>
    <!-- 内容区域 -->
</body>
</html>
```

### 3. 更新 README.md

添加新页面后，**必须**在 README.md 的论文索引表格中添加一行：

```markdown
| 论文名称 | 会议/期刊 | 原论文 | 代码仓库 | 在线页面 |
|---------|---------|--------|---------|---------|
| {论文名称} | {会议} {年份} | [arXiv]({论文链接}) | [{repo}]({仓库链接}) | [查看](https://weihao-bo.github.io/paper_summary/{文件名}) |
```

### 4. 提交规范

提交信息格式：
```
Add: {论文名称} ({会议} {年份})

- 添加论文架构总结页面
- 更新 README 索引
```

## 部署说明

- 使用 GitHub Pages 从 `main` 分支根目录部署
- 推送到 `main` 分支后自动部署
- 部署地址：`https://weihao-bo.github.io/paper_summary/`

## 样式规范

- 所有 CSS 内联在 HTML 文件中，保持每个文件独立可用
- 推荐使用的配色方案：
  - 主色：`#4F46E5` (紫蓝色)
  - 次色：`#10B981` (绿色)
  - 警告：`#F59E0B` (橙色)
  - 背景：`#F9FAFB` (浅灰)
- 支持响应式设计，适配移动端

## 常用命令

```bash
# 本地预览（需要 Python）
cd /Users/bwh/Documents/Code/paper_summary
python -m http.server 8000
# 然后访问 http://localhost:8000

# 提交并推送
git add .
git commit -m "Add: {论文名称}"
git push origin main
```
