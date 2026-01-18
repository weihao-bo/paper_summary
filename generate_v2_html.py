#!/usr/bin/env python3
"""
基于 v1 完整数据生成 HTML，并更新清洗后图片为 v2.1 OSS URL
添加来源筛选功能
"""

import json
from collections import defaultdict
from pathlib import Path

# 路径配置
V1_DATA_DIR = Path("/Volumes/bwh-ssd-2T/3_Code_Archive/Diagram_latex_code_generator/Data/SciDiagram_v1")
V1_JSONL = V1_DATA_DIR / "SciDiagram_cleaned.jsonl"
OUTPUT_HTML = Path("/Volumes/bwh-ssd-2T/3_Code_Archive/paper_summary/cleaner_comparison.html")

# OSS 配置 - 清洗后图片使用 v2.1
OSS_V1_PREFIX = "https://online-image-2512.oss-cn-beijing.aliyuncs.com/SciDiagram_v1"
OSS_V21_PREFIX = "https://online-image-2512.oss-cn-beijing.aliyuncs.com/SciDiagram_v2.1"


def compute_stats(data: list[dict]) -> dict:
    """计算统计信息（保留原有逻辑）"""
    stats = {
        "total": len(data),
        "status": defaultdict(int),
        "categories": defaultdict(int),
        "sources": defaultdict(int),
        "category_status": defaultdict(lambda: defaultdict(int)),
        "source_status": defaultdict(lambda: defaultdict(int)),
        "code_stats": {
            "original_avg": 0,
            "cleaned_avg": 0,
            "reduction_percent": 0
        },
        "fallback_analysis": {
            "total": 0,
            "compile_errors": 0,
            "vision_errors": 0
        }
    }

    original_lengths = []
    cleaned_lengths = []

    for item in data:
        status = item.get("status", "unknown")
        category = item.get("category", "unknown")
        source = item.get("source_package", "unknown")

        stats["status"][status] += 1
        stats["categories"][category] += 1
        stats["sources"][source] += 1
        stats["category_status"][category][status] += 1
        stats["source_status"][source][status] += 1

        # Code length stats
        if item.get("original_code"):
            original_lengths.append(len(item["original_code"]))
        if item.get("cleaned_code"):
            cleaned_lengths.append(len(item["cleaned_code"]))

        # Fallback analysis
        if status == "fallback":
            stats["fallback_analysis"]["total"] += 1
            if item.get("vision_reason"):
                stats["fallback_analysis"]["vision_errors"] += 1
            else:
                stats["fallback_analysis"]["compile_errors"] += 1

    # Calculate averages
    if original_lengths:
        stats["code_stats"]["original_avg"] = int(sum(original_lengths) / len(original_lengths))
    if cleaned_lengths:
        stats["code_stats"]["cleaned_avg"] = int(sum(cleaned_lengths) / len(cleaned_lengths))
    if stats["code_stats"]["original_avg"] > 0:
        reduction = (1 - stats["code_stats"]["cleaned_avg"] / stats["code_stats"]["original_avg"]) * 100
        stats["code_stats"]["reduction_percent"] = round(reduction, 1)

    # Convert defaultdicts to regular dicts
    stats["status"] = dict(stats["status"])
    stats["categories"] = dict(stats["categories"])
    stats["sources"] = dict(stats["sources"])
    stats["category_status"] = {k: dict(v) for k, v in stats["category_status"].items()}
    stats["source_status"] = {k: dict(v) for k, v in stats["source_status"].items()}

    return stats


def generate_html():
    """生成 HTML"""
    # 读取 v1 完整数据
    data = []
    with open(V1_JSONL, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line.strip())

            # 处理图片路径
            # 原始图片使用 v1 OSS
            if item.get('original_image'):
                orig_name = Path(item['original_image']).name
                item['original_image_path'] = f"{OSS_V1_PREFIX}/images/{orig_name}"
            else:
                item['original_image_path'] = f"{OSS_V1_PREFIX}/images/{item['id']}.png"

            # 清洗后图片：成功的使用 v2.1，其他使用 v1
            if item.get('image'):
                img_name = Path(item['image']).name  # 大写格式: SciDiagram_XXXX.png
                if item.get('status') == 'success':
                    # 成功清洗的使用 v2.1 的图片 (已统一为大写文件名)
                    item['cleaned_image_path'] = f"{OSS_V21_PREFIX}/images/{img_name}"
                else:
                    # fallback/skipped 保持 v1
                    item['cleaned_image_path'] = f"{OSS_V1_PREFIX}/images_cleaned/{img_name}"

            # fallback 图片使用 v1
            if item.get('status') == 'fallback' and item.get('vision_reason'):
                img_name = Path(item.get('image', '')).name
                item['fallback_image_path'] = f"{OSS_V1_PREFIX}/images_fallback/{img_name}"

            data.append(item)

    # 计算统计
    stats = compute_stats(data)

    # 读取模板并生成 HTML
    data_json = json.dumps(data, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)

    html = HTML_TEMPLATE.replace('__DATA_PLACEHOLDER__', data_json)
    html = html.replace('__STATS_PLACEHOLDER__', stats_json)

    # 写入文件
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 已生成: {OUTPUT_HTML}")
    print(f"  包含 {len(data)} 条记录")
    print(f"  来源: {len(stats['sources'])} 个")
    print(f"  类别: {len(stats['categories'])} 个")
    print(f"  状态: 成功 {stats['status'].get('success', 0)}, 回退 {stats['status'].get('fallback', 0)}, 跳过 {stats['status'].get('skipped', 0)}")


# HTML 模板 - 基于原模板添加来源筛选
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LaTeX Code Cleaner - 数据可视化 (v2.1)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e14;
            --bg-secondary: #0d1117;
            --bg-tertiary: #161b22;
            --bg-code: #1a1f29;
            --border-color: #30363d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --text-muted: #6e7681;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-purple: #a371f7;
            --accent-orange: #d29922;
            --accent-pink: #f778ba;
            --accent-cyan: #79c0ff;
            --accent-red: #ff7b72;
            --accent-yellow: #e3b341;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            padding: 2rem;
            text-align: center;
            border-bottom: 1px solid var(--border-color);
        }

        .header h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
        .header .subtitle { color: rgba(255,255,255,0.85); font-size: 0.95rem; }

        /* Statistics Section */
        .stats-section {
            padding: 2rem;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 1.5rem;
            max-width: 1400px;
            margin: 0 auto 2rem;
        }

        .stat-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }

        .stat-value {
            font-family: 'Fira Code', monospace;
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        .stat-value.green { color: var(--accent-green); }
        .stat-value.yellow { color: var(--accent-yellow); }
        .stat-value.red { color: var(--accent-red); }
        .stat-value.purple { color: var(--accent-purple); }
        .stat-value.orange { color: var(--accent-orange); }

        .stat-label { font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem; }

        /* Charts */
        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .chart-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
        }

        .chart-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }

        .chart-wrapper {
            position: relative;
            height: 300px;
        }

        /* Tables container */
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            max-width: 1400px;
            margin: 2rem auto 0;
        }

        /* Filters */
        .filter-section {
            padding: 1rem 2rem;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .filter-group {
            margin-bottom: 0.6rem;
        }

        .filter-label {
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: center;
        }

        .filter-row {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .filter-btn {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 0.4rem 0.8rem;
            color: var(--text-primary);
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .filter-btn:hover { border-color: var(--accent-blue); }
        .filter-btn.active { border-color: var(--accent-green); background: rgba(63, 185, 80, 0.15); }
        .filter-btn.source-btn.active { border-color: var(--accent-orange); background: rgba(210, 153, 34, 0.15); }
        .filter-btn .count { font-family: 'Fira Code', monospace; font-size: 0.7rem; color: var(--accent-cyan); margin-left: 0.3rem; }

        .toolbar {
            display: flex;
            gap: 1rem;
            align-items: center;
            justify-content: center;
            margin-top: 0.5rem;
        }

        .search-box {
            position: relative;
            min-width: 250px;
        }

        .search-box input {
            width: 100%;
            padding: 0.5rem 1rem 0.5rem 2.5rem;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
        }

        .search-box input:focus { border-color: var(--accent-blue); }
        .search-box::before { content: '🔍'; position: absolute; left: 0.8rem; top: 50%; transform: translateY(-50%); font-size: 0.85rem; }

        .result-count { color: var(--text-secondary); font-size: 0.85rem; }

        /* Layout toggle */
        .layout-toggle {
            display: flex;
            gap: 0.3rem;
            background: var(--bg-secondary);
            padding: 0.3rem;
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }

        .layout-btn {
            padding: 0.3rem 0.6rem;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            border-radius: 6px;
            font-size: 1rem;
        }

        .layout-btn.active { background: var(--accent-blue); color: white; }

        /* Main Content */
        .main-content {
            padding: 1.5rem;
            max-width: 1800px;
            margin: 0 auto;
        }

        /* Grid layout */
        .items-grid {
            display: grid;
            gap: 1.5rem;
        }

        .items-grid.layout-1 { grid-template-columns: 1fr; }
        .items-grid.layout-2 { grid-template-columns: repeat(2, 1fr); }
        .items-grid.layout-3 { grid-template-columns: repeat(3, 1fr); }
        .items-grid.layout-4 { grid-template-columns: repeat(4, 1fr); }

        @media (max-width: 1400px) { .items-grid.layout-4 { grid-template-columns: repeat(3, 1fr); } }
        @media (max-width: 1100px) { .items-grid.layout-4, .items-grid.layout-3 { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 768px) { .items-grid.layout-4, .items-grid.layout-3, .items-grid.layout-2 { grid-template-columns: 1fr; } }

        /* Item Card */
        .item-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .item-card:hover { border-color: var(--accent-blue); }

        .card-header {
            padding: 0.6rem 0.8rem;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.3rem;
        }

        .card-id { font-family: 'Fira Code', monospace; font-size: 0.8rem; color: var(--accent-cyan); }

        .card-badges { display: flex; gap: 0.3rem; flex-wrap: wrap; }

        .badge {
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 500;
        }

        .badge-success { background: rgba(63, 185, 80, 0.2); color: var(--accent-green); }
        .badge-fallback { background: rgba(210, 153, 34, 0.2); color: var(--accent-yellow); }
        .badge-skipped { background: rgba(139, 148, 158, 0.2); color: var(--text-secondary); }
        .badge-category { background: rgba(163, 113, 247, 0.2); color: var(--accent-purple); }
        .badge-source { background: rgba(210, 153, 34, 0.2); color: var(--accent-orange); }
        .badge-compile-error { background: rgba(255, 123, 114, 0.2); color: var(--accent-red); }
        .badge-vision-error { background: rgba(255, 123, 114, 0.2); color: var(--accent-pink); }

        .card-body { padding: 0.8rem; }

        /* Image comparison */
        .image-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }

        .image-comparison.three-col {
            grid-template-columns: 1fr 1fr 1fr;
        }

        .image-box {
            background: #fafafa;
            border-radius: 6px;
            overflow: hidden;
            cursor: pointer;
        }

        .image-label {
            background: var(--bg-tertiary);
            padding: 0.3rem 0.5rem;
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-align: center;
        }

        .image-label.original { border-left: 3px solid var(--accent-red); }
        .image-label.cleaned { border-left: 3px solid var(--accent-green); }
        .image-label.fallback { border-left: 3px solid var(--accent-yellow); }

        .image-container {
            padding: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 120px;
        }

        .image-container img {
            max-width: 100%;
            max-height: 200px;
            object-fit: contain;
        }

        /* Code toggle */
        .code-toggle {
            margin-top: 0.5rem;
        }

        .code-toggle-btn {
            width: 100%;
            padding: 0.4rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            cursor: pointer;
        }

        .code-toggle-btn:hover { border-color: var(--accent-blue); }

        .code-content {
            display: none;
            margin-top: 0.5rem;
        }

        .code-content.show { display: block; }

        .code-tabs {
            display: flex;
            gap: 0.3rem;
            margin-bottom: 0.5rem;
        }

        .code-tab {
            padding: 0.3rem 0.6rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 0.7rem;
            color: var(--text-secondary);
            cursor: pointer;
        }

        .code-tab.active { background: var(--accent-blue); color: white; border-color: var(--accent-blue); }

        .code-box {
            background: var(--bg-code);
            border-radius: 6px;
            padding: 0.6rem;
            max-height: 250px;
            overflow: auto;
        }

        .code-box pre {
            font-family: 'Fira Code', monospace;
            font-size: 0.7rem;
            line-height: 1.4;
            white-space: pre-wrap;
            word-break: break-word;
            color: var(--text-primary);
        }

        /* Error info */
        .error-info {
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
        }

        .error-info.compile {
            background: rgba(255, 123, 114, 0.1);
            border: 1px solid rgba(255, 123, 114, 0.3);
            color: var(--accent-red);
        }

        .error-info.vision {
            background: rgba(247, 120, 186, 0.1);
            border: 1px solid rgba(247, 120, 186, 0.3);
            color: var(--accent-pink);
        }

        .error-title { font-weight: 600; margin-bottom: 0.3rem; }
        .error-text { color: var(--text-secondary); white-space: pre-wrap; word-break: break-word; max-height: 100px; overflow: auto; }

        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 0.4rem;
            padding: 1.5rem;
            flex-wrap: wrap;
        }

        .page-btn {
            padding: 0.4rem 0.7rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.85rem;
            cursor: pointer;
            min-width: 36px;
            text-align: center;
        }

        .page-btn:hover:not(:disabled) { background: var(--accent-blue); border-color: var(--accent-blue); }
        .page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .page-btn.active { background: var(--accent-green); border-color: var(--accent-green); }
        .page-info { color: var(--text-secondary); font-size: 0.85rem; padding: 0 0.5rem; }

        .per-page-select {
            padding: 0.4rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 0.85rem;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.95);
            cursor: zoom-out;
        }

        .modal.active { display: flex; align-items: center; justify-content: center; }
        .modal-content { max-width: 95%; max-height: 95%; object-fit: contain; }
        .modal-close { position: absolute; top: 20px; right: 30px; color: white; font-size: 2rem; cursor: pointer; }
        .modal-info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); color: white; background: rgba(0,0,0,0.7); padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; }

        .no-results { text-align: center; padding: 4rem; color: var(--text-secondary); }
        .no-results .emoji { font-size: 3rem; margin-bottom: 1rem; }

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

        .summary-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }

        .summary-table th, .summary-table td {
            padding: 0.6rem;
            border: 1px solid var(--border-color);
            text-align: center;
        }

        .summary-table th {
            background: var(--bg-tertiary);
            color: var(--text-primary);
        }

        .summary-table td { color: var(--text-secondary); }
        .summary-table .rate-high { color: var(--accent-green); font-weight: 600; }
        .summary-table .rate-mid { color: var(--accent-yellow); font-weight: 600; }
        .summary-table .rate-low { color: var(--accent-red); font-weight: 600; }
        .summary-table .highlight { color: var(--accent-cyan); font-weight: 600; }
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 LaTeX Code Cleaner - 数据可视化</h1>
        <p class="subtitle">清洗结果统计分析与对比查看 (v2.1 图片)</p>
    </header>

    <section class="stats-section">
        <div class="stats-grid" id="stats-grid"></div>
        <div class="charts-container">
            <div class="chart-card">
                <div class="chart-title">📈 状态分布</div>
                <div class="chart-wrapper"><canvas id="statusChart"></canvas></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📊 各类别清洗成功率</div>
                <div class="chart-wrapper"><canvas id="categoryChart"></canvas></div>
            </div>
        </div>
        <div class="charts-container" style="margin-top: 2rem;">
            <div class="chart-card">
                <div class="chart-title">📦 来源分布</div>
                <div class="chart-wrapper"><canvas id="sourceChart"></canvas></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📦 各来源清洗成功率</div>
                <div class="chart-wrapper"><canvas id="sourceRateChart"></canvas></div>
            </div>
        </div>

        <div class="tables-container">
            <div class="chart-card">
                <div class="chart-title">📋 各类别详细统计</div>
                <table class="summary-table" id="category-table"></table>
            </div>
            <div class="chart-card">
                <div class="chart-title">📋 各来源详细统计</div>
                <table class="summary-table" id="source-table"></table>
            </div>
        </div>
    </section>

    <section class="filter-section">
        <div class="filter-group">
            <div class="filter-label">状态筛选</div>
            <div class="filter-row" id="status-filters"></div>
        </div>
        <div class="filter-group">
            <div class="filter-label">来源筛选</div>
            <div class="filter-row" id="source-filters"></div>
        </div>
        <div class="filter-group">
            <div class="filter-label">类别筛选</div>
            <div class="filter-row" id="category-filters"></div>
        </div>
        <div class="toolbar">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="搜索 ID、来源或代码内容...">
            </div>
            <div class="layout-toggle">
                <button class="layout-btn" data-cols="1" title="单列">📄</button>
                <button class="layout-btn active" data-cols="2" title="双列">📑</button>
                <button class="layout-btn" data-cols="3" title="三列">📚</button>
                <button class="layout-btn" data-cols="4" title="四列">📰</button>
            </div>
            <select class="per-page-select" id="per-page">
                <option value="20">20 条/页</option>
                <option value="50" selected>50 条/页</option>
                <option value="100">100 条/页</option>
                <option value="200">200 条/页</option>
            </select>
            <span class="result-count" id="result-count"></span>
        </div>
    </section>

    <div class="main-content">
        <div class="items-grid layout-2" id="items-grid"></div>
    </div>

    <div class="pagination" id="pagination"></div>

    <div class="modal" id="image-modal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img class="modal-content" id="modal-image">
        <div class="modal-info" id="modal-info"></div>
    </div>

    <script>
        const DATA = __DATA_PLACEHOLDER__;
        const STATS = __STATS_PLACEHOLDER__;

        let filteredData = [...DATA];
        let currentPage = 1;
        let itemsPerPage = 50;
        let currentLayout = 2;
        let activeStatuses = new Set(['success', 'fallback', 'skipped']);
        let activeCategories = new Set();
        let activeSources = new Set();

        document.addEventListener('DOMContentLoaded', () => {
            Object.keys(STATS.categories).forEach(c => activeCategories.add(c));
            Object.keys(STATS.sources).forEach(s => activeSources.add(s));

            renderStats();
            renderCharts();
            renderTables();
            renderFilters();
            applyFilters();
            setupEventListeners();
        });

        function renderStats() {
            const html = `
                <div class="stat-card">
                    <div class="stat-value">${STATS.total.toLocaleString()}</div>
                    <div class="stat-label">总条目</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value green">${(STATS.status.success || 0).toLocaleString()}</div>
                    <div class="stat-label">成功清洗</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value yellow">${(STATS.status.fallback || 0).toLocaleString()}</div>
                    <div class="stat-label">回退原始</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(STATS.status.skipped || 0).toLocaleString()}</div>
                    <div class="stat-label">跳过</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value purple">${STATS.code_stats.reduction_percent}%</div>
                    <div class="stat-label">代码缩减率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value red">${STATS.fallback_analysis.compile_errors.toLocaleString()}</div>
                    <div class="stat-label">编译错误</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" style="color: var(--accent-pink)">${STATS.fallback_analysis.vision_errors.toLocaleString()}</div>
                    <div class="stat-label">视觉不一致</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value orange">${Object.keys(STATS.sources).length}</div>
                    <div class="stat-label">数据来源</div>
                </div>
            `;
            document.getElementById('stats-grid').innerHTML = html;
        }

        function renderCharts() {
            // Status pie chart
            new Chart(document.getElementById('statusChart'), {
                type: 'doughnut',
                data: {
                    labels: ['成功', '回退', '跳过'],
                    datasets: [{
                        data: [STATS.status.success || 0, STATS.status.fallback || 0, STATS.status.skipped || 0],
                        backgroundColor: ['#3fb950', '#d29922', '#6e7681'],
                        borderColor: '#0d1117',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom', labels: { color: '#e6edf3' } } }
                }
            });

            // Category success rate
            const categories = Object.keys(STATS.category_status).filter(c => {
                const s = STATS.category_status[c];
                return (s.success || 0) + (s.fallback || 0) > 0;
            }).sort((a, b) => {
                const rA = (STATS.category_status[a].success || 0) / ((STATS.category_status[a].success || 0) + (STATS.category_status[a].fallback || 0));
                const rB = (STATS.category_status[b].success || 0) / ((STATS.category_status[b].success || 0) + (STATS.category_status[b].fallback || 0));
                return rB - rA;
            });
            const catRates = categories.map(c => {
                const s = STATS.category_status[c];
                return ((s.success || 0) / ((s.success || 0) + (s.fallback || 0)) * 100).toFixed(1);
            });

            new Chart(document.getElementById('categoryChart'), {
                type: 'bar',
                data: {
                    labels: categories,
                    datasets: [{ label: '成功率 (%)', data: catRates, backgroundColor: catRates.map(r => r >= 70 ? '#3fb950' : r >= 40 ? '#d29922' : '#ff7b72'), borderRadius: 4 }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: { x: { max: 100, ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }, y: { ticks: { color: '#8b949e' }, grid: { display: false } } }
                }
            });

            // Source pie chart
            const srcLabels = Object.keys(STATS.sources).sort((a, b) => STATS.sources[b] - STATS.sources[a]);
            const srcData = srcLabels.map(s => STATS.sources[s]);
            const srcColors = ['#58a6ff', '#3fb950', '#a371f7', '#d29922', '#f778ba', '#ff7b72', '#79c0ff', '#e3b341', '#8b949e'];

            new Chart(document.getElementById('sourceChart'), {
                type: 'doughnut',
                data: {
                    labels: srcLabels,
                    datasets: [{ data: srcData, backgroundColor: srcColors.slice(0, srcLabels.length), borderColor: '#0d1117', borderWidth: 2 }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'right', labels: { color: '#e6edf3', font: { size: 11 } } } }
                }
            });

            // Source success rate
            const sources = Object.keys(STATS.source_status).filter(s => {
                const st = STATS.source_status[s];
                return (st.success || 0) + (st.fallback || 0) > 0;
            }).sort((a, b) => {
                const rA = (STATS.source_status[a].success || 0) / ((STATS.source_status[a].success || 0) + (STATS.source_status[a].fallback || 0));
                const rB = (STATS.source_status[b].success || 0) / ((STATS.source_status[b].success || 0) + (STATS.source_status[b].fallback || 0));
                return rB - rA;
            });
            const srcRates = sources.map(s => {
                const st = STATS.source_status[s];
                return ((st.success || 0) / ((st.success || 0) + (st.fallback || 0)) * 100).toFixed(1);
            });

            new Chart(document.getElementById('sourceRateChart'), {
                type: 'bar',
                data: {
                    labels: sources,
                    datasets: [{ label: '成功率 (%)', data: srcRates, backgroundColor: srcRates.map(r => r >= 70 ? '#3fb950' : r >= 40 ? '#d29922' : '#ff7b72'), borderRadius: 4 }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                    plugins: { legend: { display: false } },
                    scales: { x: { max: 100, ticks: { color: '#8b949e' }, grid: { color: '#30363d' } }, y: { ticks: { color: '#8b949e' }, grid: { display: false } } }
                }
            });
        }

        function renderTables() {
            // Category table
            const cats = Object.keys(STATS.category_status).sort((a, b) => {
                const tA = Object.values(STATS.category_status[a]).reduce((s, v) => s + v, 0);
                const tB = Object.values(STATS.category_status[b]).reduce((s, v) => s + v, 0);
                return tB - tA;
            });
            let catHtml = '<tr><th>类别</th><th>总数</th><th>成功</th><th>回退</th><th>跳过</th><th>清洗率</th></tr>';
            cats.forEach(cat => {
                const s = STATS.category_status[cat];
                const total = Object.values(s).reduce((a, v) => a + v, 0);
                const success = s.success || 0, fallback = s.fallback || 0, skipped = s.skipped || 0;
                const processed = success + fallback;
                const rate = processed > 0 ? (success / processed * 100).toFixed(1) : '-';
                const rateClass = rate === '-' ? '' : rate >= 70 ? 'rate-high' : rate >= 40 ? 'rate-mid' : 'rate-low';
                catHtml += `<tr><td>${cat}</td><td>${total}</td><td>${success || '-'}</td><td>${fallback || '-'}</td><td>${skipped || '-'}</td><td class="${rateClass}">${rate}${rate !== '-' ? '%' : ''}</td></tr>`;
            });
            document.getElementById('category-table').innerHTML = catHtml;

            // Source table
            const srcs = Object.keys(STATS.source_status).sort((a, b) => {
                const tA = Object.values(STATS.source_status[a]).reduce((s, v) => s + v, 0);
                const tB = Object.values(STATS.source_status[b]).reduce((s, v) => s + v, 0);
                return tB - tA;
            });
            let srcHtml = '<tr><th>来源</th><th>总数</th><th>成功</th><th>回退</th><th>跳过</th><th>清洗率</th></tr>';
            srcs.forEach(src => {
                const s = STATS.source_status[src];
                const total = Object.values(s).reduce((a, v) => a + v, 0);
                const success = s.success || 0, fallback = s.fallback || 0, skipped = s.skipped || 0;
                const processed = success + fallback;
                const rate = processed > 0 ? (success / processed * 100).toFixed(1) : '-';
                const rateClass = rate === '-' ? '' : rate >= 70 ? 'rate-high' : rate >= 40 ? 'rate-mid' : 'rate-low';
                srcHtml += `<tr><td>${src}</td><td class="highlight">${total}</td><td>${success || '-'}</td><td>${fallback || '-'}</td><td>${skipped || '-'}</td><td class="${rateClass}">${rate}${rate !== '-' ? '%' : ''}</td></tr>`;
            });
            document.getElementById('source-table').innerHTML = srcHtml;
        }

        function renderFilters() {
            const statusNames = { success: '成功', fallback: '回退', skipped: '跳过' };
            document.getElementById('status-filters').innerHTML = Object.entries(STATS.status).map(([st, cnt]) =>
                `<button class="filter-btn ${activeStatuses.has(st) ? 'active' : ''}" data-status="${st}">${statusNames[st]}<span class="count">${cnt}</span></button>`
            ).join('');

            document.getElementById('source-filters').innerHTML = Object.entries(STATS.sources)
                .sort((a, b) => b[1] - a[1])
                .map(([src, cnt]) => `<button class="filter-btn source-btn ${activeSources.has(src) ? 'active' : ''}" data-source="${src}">${src}<span class="count">${cnt}</span></button>`)
                .join('');

            document.getElementById('category-filters').innerHTML = Object.entries(STATS.categories)
                .filter(([c]) => c && c !== 'unknown')
                .sort((a, b) => b[1] - a[1])
                .map(([cat, cnt]) => `<button class="filter-btn ${activeCategories.has(cat) ? 'active' : ''}" data-category="${cat}">${cat}<span class="count">${cnt}</span></button>`)
                .join('');
        }

        function setupEventListeners() {
            document.getElementById('status-filters').addEventListener('click', e => {
                if (e.target.classList.contains('filter-btn')) {
                    const st = e.target.dataset.status;
                    activeStatuses.has(st) ? (activeStatuses.delete(st), e.target.classList.remove('active')) : (activeStatuses.add(st), e.target.classList.add('active'));
                    currentPage = 1; applyFilters();
                }
            });

            document.getElementById('source-filters').addEventListener('click', e => {
                if (e.target.classList.contains('filter-btn')) {
                    const src = e.target.dataset.source;
                    activeSources.has(src) ? (activeSources.delete(src), e.target.classList.remove('active')) : (activeSources.add(src), e.target.classList.add('active'));
                    currentPage = 1; applyFilters();
                }
            });

            document.getElementById('category-filters').addEventListener('click', e => {
                if (e.target.classList.contains('filter-btn')) {
                    const cat = e.target.dataset.category;
                    activeCategories.has(cat) ? (activeCategories.delete(cat), e.target.classList.remove('active')) : (activeCategories.add(cat), e.target.classList.add('active'));
                    currentPage = 1; applyFilters();
                }
            });

            let searchTimeout;
            document.getElementById('search-input').addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => { currentPage = 1; applyFilters(); }, 300);
            });

            document.querySelector('.layout-toggle').addEventListener('click', e => {
                if (e.target.classList.contains('layout-btn')) {
                    document.querySelectorAll('.layout-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    currentLayout = parseInt(e.target.dataset.cols);
                    document.getElementById('items-grid').className = `items-grid layout-${currentLayout}`;
                }
            });

            document.getElementById('per-page').addEventListener('change', e => {
                itemsPerPage = parseInt(e.target.value);
                currentPage = 1; render();
            });
        }

        function applyFilters() {
            const term = document.getElementById('search-input').value.toLowerCase();
            filteredData = DATA.filter(item => {
                if (!activeStatuses.has(item.status)) return false;
                if (item.source_package && !activeSources.has(item.source_package)) return false;
                if (item.category && !activeCategories.has(item.category)) return false;
                if (term && !`${item.id} ${item.source_file} ${item.source_package} ${item.original_code}`.toLowerCase().includes(term)) return false;
                return true;
            });
            render();
        }

        function render() {
            renderItems();
            renderPagination();
            document.getElementById('result-count').textContent = `共 ${filteredData.length} 条结果`;
        }

        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function renderItems() {
            const start = (currentPage - 1) * itemsPerPage;
            const pageData = filteredData.slice(start, start + itemsPerPage);

            if (pageData.length === 0) {
                document.getElementById('items-grid').innerHTML = '<div class="no-results"><div class="emoji">🔍</div><div>没有找到匹配的结果</div></div>';
                return;
            }

            const html = pageData.map((item, idx) => {
                const statusClass = `badge-${item.status}`;
                const statusText = { success: '成功', fallback: '回退', skipped: '跳过' }[item.status];
                const isVisionError = item.status === 'fallback' && item.vision_reason && !item.compile_error;
                const isCompileError = item.status === 'fallback' && item.compile_error;

                const originalImage = item.original_image_path;
                const cleanedImage = item.cleaned_image_path;
                const fallbackImage = item.fallback_image_path;

                const origLen = (item.original_code || '').length;
                const cleanedLen = (item.cleaned_code || '').length;
                const reduction = origLen > 0 && cleanedLen > 0 ? Math.round((1 - cleanedLen / origLen) * 100) : 0;

                let errorBadge = isCompileError ? '<span class="badge badge-compile-error">编译错误</span>' :
                                 isVisionError ? '<span class="badge badge-vision-error">视觉不一致</span>' : '';

                let imageGrid = '';
                const imgErr = "this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23666%22>无图片</text></svg>'";

                if (item.status === 'skipped') {
                    imageGrid = `<div class="image-comparison"><div class="image-box" onclick="openModal('${originalImage}', '原始图片')"><div class="image-label original">原始图片</div><div class="image-container"><img src="${originalImage}" loading="lazy" onerror="${imgErr}"></div></div></div>`;
                } else if (isVisionError && fallbackImage) {
                    imageGrid = `<div class="image-comparison three-col">
                        <div class="image-box" onclick="openModal('${originalImage}', '原始图片')"><div class="image-label original">原始图片</div><div class="image-container"><img src="${originalImage}" loading="lazy" onerror="${imgErr}"></div></div>
                        <div class="image-box" onclick="openModal('${fallbackImage}', 'LLM 渲染')"><div class="image-label fallback">LLM 渲染</div><div class="image-container"><img src="${fallbackImage}" loading="lazy" onerror="${imgErr}"></div></div>
                        <div class="image-box" onclick="openModal('${cleanedImage}', '最终输出')"><div class="image-label cleaned">最终输出</div><div class="image-container"><img src="${cleanedImage}" loading="lazy" onerror="${imgErr}"></div></div>
                    </div>`;
                } else {
                    imageGrid = `<div class="image-comparison">
                        <div class="image-box" onclick="openModal('${originalImage}', '原始图片')"><div class="image-label original">原始图片</div><div class="image-container"><img src="${originalImage}" loading="lazy" onerror="${imgErr}"></div></div>
                        <div class="image-box" onclick="openModal('${cleanedImage}', '${item.status === 'success' ? '清洗后' : '最终输出'}')"><div class="image-label cleaned">${item.status === 'success' ? '清洗后' : '最终输出'}</div><div class="image-container"><img src="${cleanedImage}" loading="lazy" onerror="${imgErr}"></div></div>
                    </div>`;
                }

                let errorInfo = isCompileError ? `<div class="error-info compile"><div class="error-title">❌ 编译错误</div><div class="error-text">${escapeHtml(item.compile_error)}</div></div>` :
                                isVisionError ? `<div class="error-info vision"><div class="error-title">👁️ 视觉检查失败</div><div class="error-text">${escapeHtml(item.vision_reason)}</div></div>` : '';

                const cardId = `card-${start + idx}`;

                return `<div class="item-card">
                    <div class="card-header">
                        <span class="card-id">${item.id}</span>
                        <div class="card-badges">
                            <span class="badge ${statusClass}">${statusText}</span>
                            ${item.source_package ? `<span class="badge badge-source">${item.source_package}</span>` : ''}
                            ${item.category ? `<span class="badge badge-category">${item.category}</span>` : ''}
                            ${item.status === 'success' && reduction > 0 ? `<span class="badge" style="background: rgba(163,113,247,0.2); color: var(--accent-purple);">-${reduction}%</span>` : ''}
                            ${errorBadge}
                        </div>
                    </div>
                    <div class="card-body">
                        ${imageGrid}
                        ${errorInfo}
                        <div class="code-toggle">
                            <button class="code-toggle-btn" onclick="toggleCode('${cardId}')">📝 查看代码 (原始 ${origLen} → ${cleanedLen || origLen} 字符)</button>
                            <div class="code-content" id="${cardId}-code">
                                <div class="code-tabs">
                                    <button class="code-tab active" onclick="showCodeTab('${cardId}', 'original')">原始代码</button>
                                    ${item.cleaned_code ? `<button class="code-tab" onclick="showCodeTab('${cardId}', 'cleaned')">清洗后代码</button>` : ''}
                                </div>
                                <div class="code-box" id="${cardId}-original"><pre>${escapeHtml(item.original_code)}</pre></div>
                                ${item.cleaned_code ? `<div class="code-box" id="${cardId}-cleaned" style="display:none;"><pre>${escapeHtml(item.cleaned_code)}</pre></div>` : ''}
                            </div>
                        </div>
                    </div>
                </div>`;
            }).join('');

            document.getElementById('items-grid').innerHTML = html;
        }

        function toggleCode(cardId) { document.getElementById(`${cardId}-code`).classList.toggle('show'); }

        function showCodeTab(cardId, tab) {
            const orig = document.getElementById(`${cardId}-original`);
            const clean = document.getElementById(`${cardId}-cleaned`);
            const tabs = document.querySelectorAll(`#${cardId}-code .code-tab`);
            tabs.forEach(t => t.classList.remove('active'));
            if (tab === 'original') { orig.style.display = 'block'; if (clean) clean.style.display = 'none'; tabs[0].classList.add('active'); }
            else { orig.style.display = 'none'; if (clean) clean.style.display = 'block'; if (tabs[1]) tabs[1].classList.add('active'); }
        }

        function renderPagination() {
            const totalPages = Math.ceil(filteredData.length / itemsPerPage);
            if (totalPages <= 1) { document.getElementById('pagination').innerHTML = ''; return; }
            let html = `<button class="page-btn" onclick="goToPage(1)" ${currentPage === 1 ? 'disabled' : ''}>首页</button>
                <button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>上一页</button>`;
            const start = Math.max(1, currentPage - 2), end = Math.min(totalPages, currentPage + 2);
            if (start > 1) html += '<span class="page-info">...</span>';
            for (let i = start; i <= end; i++) html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
            if (end < totalPages) html += '<span class="page-info">...</span>';
            html += `<button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>下一页</button>
                <button class="page-btn" onclick="goToPage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>末页</button>
                <span class="page-info">${currentPage} / ${totalPages} 页</span>`;
            document.getElementById('pagination').innerHTML = html;
        }

        function goToPage(page) { currentPage = page; render(); window.scrollTo({ top: document.querySelector('.filter-section').offsetTop, behavior: 'smooth' }); }
        function openModal(src, info) { document.getElementById('modal-image').src = src; document.getElementById('modal-info').textContent = info; document.getElementById('image-modal').classList.add('active'); }
        function closeModal() { document.getElementById('image-modal').classList.remove('active'); }
        document.getElementById('image-modal').addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    </script>
</body>
</html>
'''


if __name__ == "__main__":
    generate_html()
