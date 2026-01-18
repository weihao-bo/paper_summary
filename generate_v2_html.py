#!/usr/bin/env python3
"""生成 SciDiagram v2.1 可视化 HTML 页面"""

import json
from collections import defaultdict
from pathlib import Path

# 路径配置
DATA_DIR = Path("/Volumes/bwh-ssd-2T/3_Code_Archive/Diagram_latex_code_generator/Data/SciDiagram_v2.1")
JSONL_PATH = DATA_DIR / "SciDiagram.jsonl"
OUTPUT_HTML = Path("/Volumes/bwh-ssd-2T/3_Code_Archive/paper_summary/cleaner_comparison.html")

# OSS 配置
OSS_URL_PREFIX = "https://online-image-2512.oss-cn-beijing.aliyuncs.com/SciDiagram_v2.1"


def compute_stats(data: list[dict]) -> dict:
    """计算统计信息"""
    stats = {
        "total": len(data),
        "status": defaultdict(int),
        "categories": defaultdict(int),
        "sources": defaultdict(int),
        "source_category": defaultdict(lambda: defaultdict(int)),
        "category_source": defaultdict(lambda: defaultdict(int)),
    }

    for item in data:
        status = item.get("status", "unknown")
        category = item.get("category", "unknown")
        source = item.get("source_package", "unknown")

        stats["status"][status] += 1
        stats["categories"][category] += 1
        stats["sources"][source] += 1
        stats["source_category"][source][category] += 1
        stats["category_source"][category][source] += 1

    # Convert defaultdicts to regular dicts for JSON
    stats["status"] = dict(stats["status"])
    stats["categories"] = dict(stats["categories"])
    stats["sources"] = dict(stats["sources"])
    stats["source_category"] = {k: dict(v) for k, v in stats["source_category"].items()}
    stats["category_source"] = {k: dict(v) for k, v in stats["category_source"].items()}

    return stats


def generate_html():
    """生成 HTML 文件"""
    # 读取数据
    data = []
    with open(JSONL_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            item = json.loads(line.strip())
            # 跳过编译失败的条目（没有图片）
            if not item.get('image'):
                continue
            # 添加图片 URL
            image_name = Path(item['image']).name
            item['image_url'] = f"{OSS_URL_PREFIX}/images/{image_name}"
            data.append(item)

    # 计算统计
    stats = compute_stats(data)

    # 生成 HTML
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


HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SciDiagram v2.1 - 数据可视化</title>
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
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
            margin-bottom: 0.8rem;
        }

        .filter-label {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
            min-width: 280px;
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
        .badge-category { background: rgba(163, 113, 247, 0.2); color: var(--accent-purple); }
        .badge-source { background: rgba(210, 153, 34, 0.2); color: var(--accent-orange); }

        .card-body { padding: 0.8rem; }

        /* Image container */
        .image-container {
            background: #fafafa;
            border-radius: 6px;
            overflow: hidden;
            cursor: pointer;
            padding: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 150px;
        }

        .image-container img {
            max-width: 100%;
            max-height: 250px;
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

        .code-box {
            background: var(--bg-code);
            border-radius: 6px;
            padding: 0.6rem;
            max-height: 300px;
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

        /* Per page selector */
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

        /* No results */
        .no-results { text-align: center; padding: 4rem; color: var(--text-secondary); }
        .no-results .emoji { font-size: 3rem; margin-bottom: 1rem; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }

        /* Summary tables */
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            max-width: 1400px;
            margin: 2rem auto 0;
        }

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
        .summary-table .highlight { color: var(--accent-cyan); font-weight: 600; }
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 SciDiagram v2.1 - 数据可视化</h1>
        <p class="subtitle">清洗后数据统计分析与预览</p>
    </header>

    <section class="stats-section">
        <div class="stats-grid" id="stats-grid"></div>
        <div class="charts-container">
            <div class="chart-card">
                <div class="chart-title">📦 来源分布</div>
                <div class="chart-wrapper"><canvas id="sourceChart"></canvas></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">📁 类别分布</div>
                <div class="chart-wrapper"><canvas id="categoryChart"></canvas></div>
            </div>
        </div>

        <div class="tables-container">
            <div class="chart-card">
                <div class="chart-title">📋 来源详细统计</div>
                <table class="summary-table" id="source-table"></table>
            </div>
            <div class="chart-card">
                <div class="chart-title">📋 类别详细统计</div>
                <table class="summary-table" id="category-table"></table>
            </div>
        </div>
    </section>

    <section class="filter-section">
        <div class="filter-group">
            <div class="filter-label">📦 来源筛选</div>
            <div class="filter-row" id="source-filters"></div>
        </div>
        <div class="filter-group">
            <div class="filter-label">📁 类别筛选</div>
            <div class="filter-row" id="category-filters"></div>
        </div>
        <div class="toolbar">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="搜索 ID、来源文件或代码内容...">
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
        // Data
        const DATA = __DATA_PLACEHOLDER__;
        const STATS = __STATS_PLACEHOLDER__;

        // State
        let filteredData = [...DATA];
        let currentPage = 1;
        let itemsPerPage = 50;
        let currentLayout = 2;
        let activeSources = new Set();
        let activeCategories = new Set();

        // Source colors
        const SOURCE_COLORS = {
            'datikz_v3_train': '#58a6ff',
            'datikz_v3_val': '#79c0ff',
            'tikz_pgf': '#3fb950',
            'pgfplots': '#a371f7',
            'circuitikz': '#d29922',
            'tkz-euclide': '#f778ba',
            'chemfig': '#ff7b72',
            'pst-solides3d': '#8b949e',
            'tikz-network': '#e3b341'
        };

        // Category colors
        const CATEGORY_COLORS = {
            'graph_structures': '#58a6ff',
            'charts': '#3fb950',
            'planar_geometry': '#a371f7',
            'circuit_diagrams': '#d29922',
            'chemical_expressions': '#ff7b72',
            '3d_shapes&geometry': '#f778ba'
        };

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            // Activate all sources and categories by default
            Object.keys(STATS.sources).forEach(s => activeSources.add(s));
            Object.keys(STATS.categories).forEach(c => activeCategories.add(c));

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
                    <div class="stat-label">编译成功</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value orange">${Object.keys(STATS.sources).length}</div>
                    <div class="stat-label">数据来源</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value purple">${Object.keys(STATS.categories).length}</div>
                    <div class="stat-label">图表类别</div>
                </div>
            `;
            document.getElementById('stats-grid').innerHTML = html;
        }

        function renderCharts() {
            // Source pie chart
            const sourceLabels = Object.keys(STATS.sources).sort((a, b) => STATS.sources[b] - STATS.sources[a]);
            const sourceData = sourceLabels.map(s => STATS.sources[s]);
            const sourceColors = sourceLabels.map(s => SOURCE_COLORS[s] || '#6e7681');

            new Chart(document.getElementById('sourceChart'), {
                type: 'doughnut',
                data: {
                    labels: sourceLabels,
                    datasets: [{
                        data: sourceData,
                        backgroundColor: sourceColors,
                        borderColor: '#0d1117',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right', labels: { color: '#e6edf3', font: { size: 11 } } }
                    }
                }
            });

            // Category bar chart
            const categoryLabels = Object.keys(STATS.categories).sort((a, b) => STATS.categories[b] - STATS.categories[a]);
            const categoryData = categoryLabels.map(c => STATS.categories[c]);
            const categoryColors = categoryLabels.map(c => CATEGORY_COLORS[c] || '#6e7681');

            new Chart(document.getElementById('categoryChart'), {
                type: 'bar',
                data: {
                    labels: categoryLabels,
                    datasets: [{
                        label: '数量',
                        data: categoryData,
                        backgroundColor: categoryColors,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
                        y: { ticks: { color: '#8b949e' }, grid: { display: false } }
                    }
                }
            });
        }

        function renderTables() {
            // Source table
            const sources = Object.entries(STATS.sources).sort((a, b) => b[1] - a[1]);
            let sourceHtml = `
                <tr>
                    <th>来源</th>
                    <th>数量</th>
                    <th>占比</th>
                </tr>
            `;
            sources.forEach(([src, count]) => {
                const pct = (count / STATS.total * 100).toFixed(1);
                sourceHtml += `
                    <tr>
                        <td>${src}</td>
                        <td class="highlight">${count.toLocaleString()}</td>
                        <td>${pct}%</td>
                    </tr>
                `;
            });
            document.getElementById('source-table').innerHTML = sourceHtml;

            // Category table
            const categories = Object.entries(STATS.categories).sort((a, b) => b[1] - a[1]);
            let categoryHtml = `
                <tr>
                    <th>类别</th>
                    <th>数量</th>
                    <th>占比</th>
                </tr>
            `;
            categories.forEach(([cat, count]) => {
                const pct = (count / STATS.total * 100).toFixed(1);
                categoryHtml += `
                    <tr>
                        <td>${cat}</td>
                        <td class="highlight">${count.toLocaleString()}</td>
                        <td>${pct}%</td>
                    </tr>
                `;
            });
            document.getElementById('category-table').innerHTML = categoryHtml;
        }

        function renderFilters() {
            // Source filters
            const sourcesSorted = Object.entries(STATS.sources).sort((a, b) => b[1] - a[1]);
            const sourceHtml = sourcesSorted.map(([src, count]) => {
                const active = activeSources.has(src) ? 'active' : '';
                return `<button class="filter-btn source-btn ${active}" data-source="${src}">${src}<span class="count">${count}</span></button>`;
            }).join('');
            document.getElementById('source-filters').innerHTML = sourceHtml;

            // Category filters
            const categoriesSorted = Object.entries(STATS.categories).sort((a, b) => b[1] - a[1]);
            const categoryHtml = categoriesSorted.map(([cat, count]) => {
                const active = activeCategories.has(cat) ? 'active' : '';
                return `<button class="filter-btn ${active}" data-category="${cat}">${cat}<span class="count">${count}</span></button>`;
            }).join('');
            document.getElementById('category-filters').innerHTML = categoryHtml;
        }

        function setupEventListeners() {
            // Source filters
            document.getElementById('source-filters').addEventListener('click', e => {
                if (e.target.classList.contains('filter-btn')) {
                    const source = e.target.dataset.source;
                    if (activeSources.has(source)) {
                        activeSources.delete(source);
                        e.target.classList.remove('active');
                    } else {
                        activeSources.add(source);
                        e.target.classList.add('active');
                    }
                    currentPage = 1;
                    applyFilters();
                }
            });

            // Category filters
            document.getElementById('category-filters').addEventListener('click', e => {
                if (e.target.classList.contains('filter-btn')) {
                    const category = e.target.dataset.category;
                    if (activeCategories.has(category)) {
                        activeCategories.delete(category);
                        e.target.classList.remove('active');
                    } else {
                        activeCategories.add(category);
                        e.target.classList.add('active');
                    }
                    currentPage = 1;
                    applyFilters();
                }
            });

            // Search
            let searchTimeout;
            document.getElementById('search-input').addEventListener('input', e => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    currentPage = 1;
                    applyFilters();
                }, 300);
            });

            // Layout toggle
            document.querySelector('.layout-toggle').addEventListener('click', e => {
                if (e.target.classList.contains('layout-btn')) {
                    document.querySelectorAll('.layout-btn').forEach(btn => btn.classList.remove('active'));
                    e.target.classList.add('active');
                    currentLayout = parseInt(e.target.dataset.cols);
                    const grid = document.getElementById('items-grid');
                    grid.className = `items-grid layout-${currentLayout}`;
                }
            });

            // Per page
            document.getElementById('per-page').addEventListener('change', e => {
                itemsPerPage = parseInt(e.target.value);
                currentPage = 1;
                render();
            });
        }

        function applyFilters() {
            const searchTerm = document.getElementById('search-input').value.toLowerCase();

            filteredData = DATA.filter(item => {
                // Source filter
                if (!activeSources.has(item.source_package)) return false;

                // Category filter
                if (!activeCategories.has(item.category)) return false;

                // Search
                if (searchTerm) {
                    const searchable = `${item.id} ${item.source_file} ${item.source_package} ${item.category} ${item.code}`.toLowerCase();
                    if (!searchable.includes(searchTerm)) return false;
                }

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
            const end = start + itemsPerPage;
            const pageData = filteredData.slice(start, end);

            if (pageData.length === 0) {
                document.getElementById('items-grid').innerHTML = `
                    <div class="no-results">
                        <div class="emoji">🔍</div>
                        <div>没有找到匹配的结果</div>
                    </div>
                `;
                return;
            }

            const html = pageData.map((item, idx) => {
                const cardId = `card-${start + idx}`;
                const codeLen = (item.code || '').length;

                return `
                    <div class="item-card">
                        <div class="card-header">
                            <span class="card-id">${item.id}</span>
                            <div class="card-badges">
                                <span class="badge badge-success">✓</span>
                                <span class="badge badge-source">${item.source_package}</span>
                                <span class="badge badge-category">${item.category}</span>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="image-container" onclick="openModal('${item.image_url}', '${item.id}')">
                                <img src="${item.image_url}" loading="lazy" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><text x=%2250%%22 y=%2250%%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23666%22>无图片</text></svg>'">
                            </div>
                            <div class="code-toggle">
                                <button class="code-toggle-btn" onclick="toggleCode('${cardId}')">📝 查看代码 (${codeLen} 字符)</button>
                                <div class="code-content" id="${cardId}-code">
                                    <div class="code-box">
                                        <pre>${escapeHtml(item.code)}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

            document.getElementById('items-grid').innerHTML = html;
        }

        function toggleCode(cardId) {
            const codeContent = document.getElementById(`${cardId}-code`);
            codeContent.classList.toggle('show');
        }

        function renderPagination() {
            const totalPages = Math.ceil(filteredData.length / itemsPerPage);
            if (totalPages <= 1) {
                document.getElementById('pagination').innerHTML = '';
                return;
            }

            let html = `
                <button class="page-btn" onclick="goToPage(1)" ${currentPage === 1 ? 'disabled' : ''}>首页</button>
                <button class="page-btn" onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>上一页</button>
            `;

            const startPage = Math.max(1, currentPage - 2);
            const endPage = Math.min(totalPages, currentPage + 2);

            if (startPage > 1) html += '<span class="page-info">...</span>';

            for (let i = startPage; i <= endPage; i++) {
                html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
            }

            if (endPage < totalPages) html += '<span class="page-info">...</span>';

            html += `
                <button class="page-btn" onclick="goToPage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>下一页</button>
                <button class="page-btn" onclick="goToPage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>末页</button>
                <span class="page-info">${currentPage} / ${totalPages} 页</span>
            `;

            document.getElementById('pagination').innerHTML = html;
        }

        function goToPage(page) {
            currentPage = page;
            render();
            window.scrollTo({ top: document.querySelector('.filter-section').offsetTop, behavior: 'smooth' });
        }

        function openModal(src, info) {
            document.getElementById('modal-image').src = src;
            document.getElementById('modal-info').textContent = info;
            document.getElementById('image-modal').classList.add('active');
        }

        function closeModal() {
            document.getElementById('image-modal').classList.remove('active');
        }

        document.getElementById('image-modal').addEventListener('click', e => {
            if (e.target === e.currentTarget) closeModal();
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeModal();
        });
    </script>
</body>
</html>
'''


if __name__ == "__main__":
    generate_html()
