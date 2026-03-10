# Paper Summary

论文架构总结合集 - 用交互式网页可视化展示论文/代码仓库的架构设计。

## 在线查看

所有页面通过 GitHub Pages 部署，访问地址：
**https://weihao-bo.github.io/paper_summary/**

## 论文索引

| 论文名称 | 会议/期刊 | 原论文 | 代码仓库 | 在线页面 |
|---------|---------|--------|---------|---------|
| LoCoMo | ACL 2024 | [arXiv](https://arxiv.org/abs/2402.17753) | [snap-research/locomo](https://github.com/snap-research/locomo) | [查看](https://weihao-bo.github.io/paper_summary/2024_locomo.html) |
| Engineering/CAD Diagrams Survey | 自整理 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_cad_survey.html) |
| Circuit Eval Benchmark Viewer | Gemini 3 Pro 测试 | - | - | [查看](https://weihao-bo.github.io/paper_summary/structure_benchmark_test_gemini3pro.html) |
| SVG 图像理解局限性分析 | Gemini 分析 2025 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_svg_limitations.html) |
| TikZ 代码 vs 图像推理 | Gemini 分析 2025 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_tikz_reasoning.html) |
| Gemini 3 Pro 能力与目标分析 | Gemini 分析 2025 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_gemini3_pro_goals.html) |
| S1-MMAlign 数据集样例展示 | arXiv 2025 | [arXiv](https://arxiv.org/abs/2601.00264) | [HuggingFace](https://huggingface.co/datasets/ScienceOne-AI/S1-MMAlign) | [查看](https://weihao-bo.github.io/paper_summary/2025_s1_mmalign.html) |
| Diagram with LaTeX 数据集 | 自整理 2025 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_diagram_with_latex_dataset.html) |
| AI 前沿峰会专家观点总结 | 会议总结 2026 | [微信公众号](https://mp.weixin.qq.com/s/bfTbsnItuyr_k-w3XlejOg) | - | [查看](https://weihao-bo.github.io/paper_summary/2026_ai_summit.html) |
| LaTeX Pipeline 可视化 | 工具 2025 | - | - | [查看](https://weihao-bo.github.io/paper_summary/2025_latex_pipeline.html) |
| Video Agent Tool Pool & Trajectories | 工具 2025 | - | [weihao-bo/video_agent_tool_pool](https://github.com/weihao-bo/video_agent_tool_pool) | [查看](https://weihao-bo.github.io/paper_summary/video_agent_tool_pool.html) |

## 文件结构

```
paper_summary/
├── README.md           # 本文件
├── CLAUDE.md           # 项目规范
├── index.html          # 首页（可选）
└── {year}_{paper_id}.html  # 论文架构页面
```

## 文件命名规范

- 格式：`{year}_{paper_id}.html`
- 示例：`2024_locomo.html`, `2023_msc.html`

## 部署说明

本仓库使用 GitHub Pages 从 `main` 分支根目录部署。添加新页面后会自动部署。
