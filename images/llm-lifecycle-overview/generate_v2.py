#!/usr/bin/env python3
"""
生成流程：构图设计书 → 精确计算 → SVG 输出 → Gate 验证
每张图都先写设计书（注释），再写实现，最后自检。
"""
import math, os, sys

OUT = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════════
# 设计系统常量（Stripe Gradient）
# ═══════════════════════════════════════════════════════════════
G = 4  # 网格对齐单位
S = lambda v: round(v / G) * G

BG1, BG2 = "#f8f9fc", "#f0f2f8"
A1, A2 = "#635bff", "#8f6ed5"       # 强调渐变
CARD = "#ffffff"
BORDER = "#eef0f6"
TEXT, MUTED = "#1a1f36", "#a3acb9"
GREEN, AMBER, PURPLE, RED = "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"
FONT = "Inter, system-ui, -apple-system, sans-serif"
CARD_RX = 9

# 共享 SVG 头部工厂
def make_header(w, h, title, subtitle):
    """返回 SVG 前缀字符串"""
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">',
        f'<defs>',
        f'  <linearGradient id="bg"><stop offset="0%" stop-color="{BG1}"/><stop offset="100%" stop-color="{BG2}"/></linearGradient>',
        f'  <linearGradient id="acc"><stop offset="0%" stop-color="{A1}"/><stop offset="100%" stop-color="{A2}"/></linearGradient>',
        f'  <filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#1a1f36" flood-opacity="0.05"/></filter>',
        f'  <filter id="as"><feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#635bff" flood-opacity="0.12"/></filter>',
        f'  <filter id="blur"><feGaussianBlur stdDeviation="50"/></filter>',
    ]
    # 箭头标记
    for mid, mc in [("ma",A1),("mb",AMBER),("mc",PURPLE),("md",GREEN),("me",RED)]:
        lines.append(f'  <marker id="{mid}" viewBox="0 0 10 8" refX="10" refY="4" markerWidth="6" markerHeight="5" orient="auto"><path d="M0,0L10,4L0,8Z" fill="{mc}"/></marker>')
    lines.append(f'</defs>')
    lines.append(f'<rect width="{w}" height="{h}" fill="url(#bg)"/>')
    # 装饰模糊圆
    lines.append(f'<circle cx="{S(w*0.8)}" cy="{S(h*0.15)}" r="{S(min(w,h)*0.22)}" fill="{A1}" opacity="0.025" filter="url(#blur)"/>')
    lines.append(f'<circle cx="{S(w*0.2)}" cy="{S(h*0.82)}" r="{S(min(w,h)*0.18)}" fill="{A2}" opacity="0.025" filter="url(#blur)"/>')
    # 标题
    lines.append(f'<text x="{w//2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="{TEXT}" letter-spacing="-0.3">{title}</text>')
    tw = len(title) * 12
    lines.append(f'<line x1="{w//2-tw//2}" y1="52" x2="{w//2+tw//2}" y2="52" stroke="{A1}" stroke-width="2.5" stroke-linecap="round"/>')
    lines.append(f'<text x="{w//2}" y="70" text-anchor="middle" font-size="10" fill="{MUTED}">{subtitle}</text>')
    return "\n".join(lines) + "\n"

FOOTER = '</svg>\n'


# ═══════════════════════════════════════════════════════════════
# Diagram 1: Lifecycle Architecture
# ═══════════════════════════════════════════════════════════════
#
# 设计书 (Tier 1 — Core)
# ─────────────────────
# A1 一句话信息: LLM 五道工序首尾相连形成持续运转的回路，不是单向流水线
# A2 认知目标: 读者看完能回答"五个阶段分别做什么？它们之间如何反馈？"
# A3 论点映射: 支撑核心论点——"LLM 不是被编程的，是训练出来的"
# A4 不可替代性: 文字可以描述五个阶段，但无法在 3 秒内建立空间直觉——
#     哪阶段在前、反馈回路怎么闭合、各阶段的量级差异
#
# B1 空间策略: 正五边形环形布局。每顶点一个阶段卡片，顺时针=前向流。
#     五边形天然传达"循环/回路"——读者潜意识接收"这不是流水线"
# B2 视觉重心: 中央 pill + 反馈箭头（虚线紫色）。理由：反馈回路是本文
#     区别于常规 LLM 介绍的核心差异点，读者第一眼应看到"回路闭合"
# B3 颜色语义:
#     - #635bff → 前向流箭头 + 卡片序号 + 中央 pill（正向/主路径）
#     - #8b5cf6 → 反馈箭头（回路/反向——与正向形成对比）
#     - #10b981 → 数据相关标注
#     - #f59e0b → 警告/代价标注
#     - #a3acb9 → 不重要的背景元素（退后）
#
# C1 元素表: 5 卡片 + 5 箭头 + 1 中央 pill + 1 图例 = 12 主要元素
# C2 关系表: 4 条前向实线 + 1 条反馈虚线
# C3 复杂度: 元素 12/层 1/连接 5 → 在预算内
#
# D1 0.5s: 环形结构 + 中央蓝色 pill
# D2 1s: 虚线反馈箭头——"这里有回路"
# D3 3s: 五个阶段顺时针流转，虚线从推理回数据工程，形成闭合回路
# D4 200px: 环形结构 + 蓝色中心 + 虚线反馈可辨
#
# E1 图类型: 概念图（中心辐射 + 环形流）
# E2 画布: 1100 × 720
# E3 已知风险: ① 卡片 3 和 4 横向间距仅 104px，箭头标签可能拥挤
#              ② 反馈箭头路径长，需确保 dash 模式在缩略图可辨
#
# G1 惊喜: 多数人第一次意识到"五道工序是回路"——图把这个反直觉事实
#     变成视觉直觉
# G2 张力: 前向流（实线蓝）vs 反馈流（虚线紫）——两种箭头语义形成视觉对比
# G3 记忆: 五边形 + 蓝色中心 + 紫虚线，5 秒内可凭记忆画出骨架

def pentagon_vertices(cx, cy, r):
    """返回正五边形 5 个顶点坐标（顺时针，从顶部开始），全部对齐网格"""
    verts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        verts.append((S(cx + r * math.cos(a)), S(cy + r * math.sin(a))))
    return verts

def diagram_1():
    """LLM 生命周期全景"""
    W, H = 1100, 720
    CX, CY, R = 550, 368, 216  # 中心 + 半径
    CARD_W, CARD_H = 152, 92   # 统一卡片尺寸

    verts = pentagon_vertices(CX, CY, R)

    # 卡片数据: (标题, 角色描述, 关键指标, 指标颜色)
    cards_data = [
        ("数据工程",    "采集·清洗·分词",         "丢弃 50-80% 原始数据",      RED),
        ("预训练",      "猜下一个词 × 几万亿次",   "算力 95% · 成本 ~$1 亿",   AMBER),
        ("后训练",      "SFT 改格式 · 对齐教好坏",  "成本 1-2% · 体验 100%",    GREEN),
        ("评估",        "MMLU · MATH · HumanEval", "流水线的「眼睛」",         MUTED),
        ("推理部署",    "GQA · MoE · MLA",         "永续成本重塑架构",         A1),
    ]

    # 箭头标签（前向流 + 反馈流）
    arrow_labels = ["训练数据", "Base Model", "Aligned Model", "部署上线", "用户反馈 · 日志回流"]
    arrow_colors = [A1, A1, A1, A1, PURPLE]
    arrow_markers = ["ma", "ma", "ma", "ma", "mc"]
    arrow_dashed = [False, False, False, False, True]

    lines = [make_header(W, H, "LLM 生命周期全景：五道工序的回路", "从互联网原始文本到对话助手，首尾相连的持续运转回路")]

    # ── 1. 五边形引导线（极淡，帮助读者感知结构）──
    pts = " ".join(f"{x},{y}" for x, y in verts)
    lines.append(f'<polygon points="{pts}" fill="none" stroke="{A1}" stroke-width="0.5" opacity="0.07" stroke-dasharray="8,6"/>')

    # ── 2. 箭头（先画，在卡片下方）──
    for i in range(5):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 5]

        # 控制点：边中点 + 沿法线外推
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = mx - CX, my - CY          # 法线方向（从中心指向外）
        nl = math.sqrt(nx*nx + ny*ny) or 1
        cpx, cpy = S(mx + nx/nl * 36), S(my + ny/nl * 36)

        # 端点：从卡片边缘出发 / 到达卡片边缘
        dx, dy = x2 - x1, y2 - y1
        dl = math.sqrt(dx*dx + dy*dy) or 1
        sx = S(x1 + dx/dl * (CARD_W//2 + 4))
        sy = S(y1 + dy/dl * (CARD_H//2 + 4))
        ex = S(x2 - dx/dl * (CARD_W//2 + 6))
        ey = S(y2 - dy/dl * (CARD_H//2 + 6))

        ds = 'stroke-dasharray="6,4" ' if arrow_dashed[i] else ''
        ac = arrow_colors[i]
        lines.append(f'<path d="M{sx},{sy} Q{cpx},{cpy} {ex},{ey}" fill="none" stroke="{ac}" stroke-width="{"1" if arrow_dashed[i] else "2"}" {ds}marker-end="url(#{arrow_markers[i]})"/>')

        # 箭头标签（路径中点偏移）
        qmx = S(0.25*sx + 0.5*cpx + 0.25*ex)
        qmy = S(0.25*sy + 0.5*cpy + 0.25*ey)
        label = arrow_labels[i]
        lw = len(label) * 10 + 12
        lines.append(f'<rect x="{qmx-lw//2}" y="{qmy-10}" width="{lw}" height="18" rx="3" fill="#ffffff" fill-opacity="0.9"/>')
        lines.append(f'<text x="{qmx}" y="{qmy+3}" text-anchor="middle" font-size="8" font-weight="600" fill="{ac}">{label}</text>')

    # ── 3. 卡片 ──
    for i, (vx, vy) in enumerate(verts):
        title, sub, metric, mc = cards_data[i]
        x, y = S(vx - CARD_W//2), S(vy - CARD_H//2)

        # 卡片本体
        lines.append(f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="{CARD_RX}" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')

        # 序号徽章（左上角）
        bx, by = S(x + 14), S(y + 14)
        lines.append(f'<circle cx="{bx}" cy="{by}" r="9" fill="url(#acc)"/>')
        lines.append(f'<text x="{bx}" y="{by+4}" text-anchor="middle" font-size="9" font-weight="700" fill="#ffffff">{i+1}</text>')

        # 标题
        lines.append(f'<text x="{S(x+34)}" y="{S(y+24)}" font-size="12" font-weight="600" fill="{TEXT}">{title}</text>')
        # 角色描述
        lines.append(f'<text x="{S(x+16)}" y="{S(y+48)}" font-size="9" fill="{MUTED}">{sub}</text>')
        # 关键指标（带颜色）
        lines.append(f'<text x="{S(x+16)}" y="{S(y+72)}" font-size="10" font-weight="600" fill="{mc}">{metric}</text>')

    # ── 4. 中央 pill ──
    PW, PH = 172, 44
    lines.append(f'<rect x="{CX-PW//2}" y="{CY-PH//2}" width="{PW}" height="{PH}" rx="{PH//2}" fill="url(#acc)" filter="url(#as)"/>')
    lines.append(f'<text x="{CX}" y="{CY+5}" text-anchor="middle" font-size="14" font-weight="700" fill="#ffffff" letter-spacing="0.5">LLM 生命周期</text>')

    # ── 5. 图例 ──
    LX, LY = 876, 604
    lines.append(f'<rect x="{LX}" y="{LY}" width="192" height="80" rx="8" fill="#fafbfc" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'<text x="{LX+12}" y="{LY+18}" font-size="9" font-weight="700" fill="{MUTED}">图例</text>')
    for j, (color, dash, label) in enumerate([
        (A1, False, "前向流（阶段间产物传递）"),
        (PURPLE, True, "反馈回路（下游约束上游）"),
    ]):
        iy = LY + 34 + j * 20
        ds = 'stroke-dasharray="6,4" ' if dash else ''
        lines.append(f'<line x1="{LX+12}" y1="{iy+4}" x2="{LX+36}" y2="{iy+4}" stroke="{color}" stroke-width="{"1" if dash else "2"}" {ds}/>')
        lines.append(f'<text x="{LX+44}" y="{iy+8}" font-size="9" fill="{TEXT}">{label}</text>')

    lines.append(FOOTER)

    path = os.path.join(OUT, "lifecycle-architecture.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")

    # ── Gate 自检 ──
    _validate(path, expected_viewbox=(0,0,1100,720))


# ═══════════════════════════════════════════════════════════════
# 后续 5 张图（同流程：设计书 → 实现 → Gate 验证）
# ═══════════════════════════════════════════════════════════════

def diagram_2():
    """Tokenizer 对比"""
    W, H = 880, 540
    lines = [make_header(W, H, "Tokenizer 语言效率：英文 vs 中文", "同一 Tokenizer 对不同语言的编码效率差异巨大——直接影响推理成本和速度")]
    lines.append(f'<circle cx="{S(720)}" cy="{S(120)}" r="{S(160)}" fill="{A1}" opacity="0.025" filter="url(#blur)"/>')
    lines.append(f'<circle cx="{S(160)}" cy="{S(420)}" r="{S(140)}" fill="{A2}" opacity="0.025" filter="url(#blur)"/>')

    # ── 左面板：英文 ──
    LX, LY = 40, 96
    PW, PH = 370, 272
    # 面板背景
    lines.append(f'<rect x="{LX}" y="{LY}" width="{PW}" height="{PH}" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    # 面板标题条
    lines.append(f'<rect x="{LX}" y="{LY}" width="{PW}" height="36" rx="10" fill="#f8fafd"/>')
    lines.append(f'<rect x="{LX}" y="{LY+26}" width="{PW}" height="10" fill="#f8fafd"/>')
    lines.append(f'<text x="{LX+PW//2}" y="{LY+24}" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT}">英文文本（英文为主 Tokenizer）</text>')

    # 输入行
    lines.append(f'<text x="{LX+20}" y="{LY+62}" font-size="10" font-weight="600" fill="{MUTED}">输入</text>')
    lines.append(f'<rect x="{LX+64}" y="{LY+48}" width="276" height="26" rx="5" fill="{BG1}" stroke="{BORDER}" stroke-width="0.5"/>')
    lines.append(f'<text x="{LX+PW//2}" y="{LY+66}" text-anchor="middle" font-size="12" font-weight="500" fill="{TEXT}">The capital of France is Paris</text>')

    # Token 行
    lines.append(f'<text x="{LX+20}" y="{LY+110}" font-size="10" font-weight="600" fill="{MUTED}">分词</text>')
    words_en = [("The",42),("capital",54),("of",28),("France",54),("is",22),("Paris",46)]
    bx = LX + 64
    for word, ww in words_en:
        lines.append(f'<rect x="{bx}" y="{LY+96}" width="{ww}" height="24" rx="5" fill="#ecfdf5" stroke="{GREEN}" stroke-width="0.8"/>')
        lines.append(f'<text x="{bx+ww//2}" y="{LY+113}" text-anchor="middle" font-size="10" font-weight="500" fill="{TEXT}">{word}</text>')
        bx += ww + 6

    # 结果
    lines.append(f'<text x="{LX+20}" y="{LY+160}" font-size="11" font-weight="700" fill="{GREEN}">结果: 6 tokens → 高效编码</text>')
    lines.append(f'<text x="{LX+20}" y="{LY+180}" font-size="10" fill="{MUTED}">≈ 1 token / 词 · 序列短 → 注意力开销小</text>')

    # 效率条
    lines.append(f'<rect x="{LX+64}" y="{LY+204}" width="36" height="28" rx="5" fill="{GREEN}" opacity="0.15"/>')
    lines.append(f'<text x="{LX+82}" y="{LY+223}" text-anchor="middle" font-size="16" font-weight="700" fill="{GREEN}">6</text>')
    lines.append(f'<text x="{LX+112}" y="{LY+223}" font-size="11" fill="{MUTED}">tokens（6 词 → 6 token）</text>')

    # ── 右面板：中文 ──
    RX, RY = 470, 96
    lines.append(f'<rect x="{RX}" y="{RY}" width="{PW}" height="{PH}" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="{RX}" y="{RY}" width="{PW}" height="36" rx="10" fill="#f8fafd"/>')
    lines.append(f'<rect x="{RX}" y="{RY+26}" width="{PW}" height="10" fill="#f8fafd"/>')
    lines.append(f'<text x="{RX+PW//2}" y="{RY+24}" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT}">中文文本（英文为主 Tokenizer）</text>')

    # 输入行
    lines.append(f'<text x="{RX+20}" y="{RY+62}" font-size="10" font-weight="600" fill="{MUTED}">输入</text>')
    lines.append(f'<rect x="{RX+64}" y="{RY+48}" width="276" height="26" rx="5" fill="{BG1}" stroke="{BORDER}" stroke-width="0.5"/>')
    lines.append(f'<text x="{RX+PW//2}" y="{RY+66}" text-anchor="middle" font-size="14" font-weight="500" fill="{TEXT}">法国的首都是巴黎</text>')

    # Token 碎片行
    lines.append(f'<text x="{RX+20}" y="{RY+110}" font-size="10" font-weight="600" fill="{MUTED}">分词</text>')
    for j in range(9):
        tx = RX + 64 + j * 30
        lines.append(f'<rect x="{tx}" y="{RY+96}" width="26" height="24" rx="4" fill="#fef3c7" stroke="{AMBER}" stroke-width="0.8"/>')
        lines.append(f'<text x="{tx+13}" y="{RY+113}" text-anchor="middle" font-size="7" fill="{AMBER}">byte</text>')

    # 结果
    lines.append(f'<text x="{RX+20}" y="{RY+160}" font-size="11" font-weight="700" fill="{AMBER}">结果: ~30 tokens → 低效编码</text>')
    lines.append(f'<text x="{RX+20}" y="{RY+180}" font-size="10" fill="{MUTED}">≈ 3-6 token / 字 · 序列长 → O(n²) 开销 ↑</text>')

    # 效率条
    lines.append(f'<rect x="{RX+64}" y="{RY+204}" width="168" height="28" rx="5" fill="{AMBER}" opacity="0.15"/>')
    lines.append(f'<text x="{RX+148}" y="{RY+223}" text-anchor="middle" font-size="16" font-weight="700" fill="{AMBER}">~30</text>')
    lines.append(f'<text x="{RX+240}" y="{RY+223}" font-size="11" fill="{MUTED}">tokens（7 字 → 30 token）</text>')

    # ── 底部：解决方案 ──
    SY = 400
    lines.append(f'<rect x="40" y="{SY}" width="800" height="84" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="40" y="{SY}" width="800" height="6" rx="3" fill="url(#acc)"/>')
    lines.append(f'<text x="60" y="{SY+30}" font-size="13" font-weight="700" fill="{TEXT}">中文优化 Tokenizer（Qwen · DeepSeek 的做法）</text>')
    lines.append(f'<text x="60" y="{SY+52}" font-size="10" fill="{MUTED}">训练 Tokenizer 时大幅提高中文数据配比 → 同样 7 字句子仅需 ~7 tokens（≈1 token/字），效率提升 4-5 倍</text>')
    # 优化后的效率条
    lines.append(f'<rect x="60" y="{SY+64}" width="40" height="12" rx="4" fill="#ede9fe" stroke="{A1}" stroke-width="0.8"/>')
    lines.append(f'<text x="80" y="{SY+73}" text-anchor="middle" font-size="10" font-weight="700" fill="{A1}">7</text>')
    lines.append(f'<text x="112" y="{SY+73}" font-size="10" font-weight="600" fill="{GREEN}">tokens（优化后）→ 推理速度 ↑4× · 成本 ↓75%</text>')

    # ── 图例 ──
    lx, ly = 660, 130
    lines.append(f'<rect x="{lx}" y="{ly}" width="180" height="64" rx="6" fill="#fafbfc" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'<text x="{lx+12}" y="{ly+16}" font-size="8" font-weight="700" fill="{MUTED}">图例</text>')
    for j, (c, label) in enumerate([(GREEN,"高效编码"),(AMBER,"低效编码"),(A1,"优化方案")]):
        iy = ly + 26 + j * 14
        lines.append(f'<rect x="{lx+12}" y="{iy}" width="18" height="10" rx="3" fill="{c}" opacity="0.2" stroke="{c}" stroke-width="0.8"/>')
        lines.append(f'<text x="{lx+38}" y="{iy+9}" font-size="9" fill="{TEXT}">{label}</text>')

    lines.append(FOOTER)
    path = os.path.join(OUT, "tokenizer-comparison.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")
    _validate(path, expected_viewbox=(0,0,880,540))


def diagram_3():
    """预训练循环"""
    W, H = 880, 620
    lines = [make_header(W, H, "预训练：几万亿次「猜下一个词」循环", "Pre-training Loop — Predict Next Token × Trillions")]

    # 四节点菱形布局
    nodes = [
        (440, 136, "① 输入文本", "取一段文字", "遮掉最后一个词", False),
        (628, 264, "② 模型预测", "计算概率分布", "「巴黎」92% · 伦敦 3%", False),
        (440, 408, "③ 计算 Loss", "对比预测与真实答案", "猜错了 · loss 很高", True),   # accent
        (252, 264, "④ 更新参数", "反向传播", "微调全部参数", False),
    ]
    NW, NH = 176, 88

    # 循环箭头
    arrow_specs = [
        (540,178, 624,252, 588,200, A1, "ma", False, "前向传播"),
        (648,304, 528,378, 604,348, A1, "ma", False, "预测结果"),
        (360,418, 304,346, 320,388, AMBER, "mb", False, "梯度回传"),
        (240,300, 360,206, 292,248, A1, "ma", False, "参数更新"),
    ]
    for x1,y1,x2,y2,cpx,cpy,ac,mk,dashed,label in arrow_specs:
        ds = 'stroke-dasharray="6,4" ' if dashed else ''
        lines.append(f'<path d="M{S(x1)},{S(y1)} Q{S(cpx)},{S(cpy)} {S(x2)},{S(y2)}" fill="none" stroke="{ac}" stroke-width="1.5" {ds}marker-end="url(#{mk})"/>')
        lx, ly = S((x1+x2)//2), S((y1+y2)//2 - 8)
        lines.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="8" font-weight="600" fill="{ac}">{label}</text>')

    # 外圈虚线（重复几万亿次）
    lines.append(f'<path d="M{440},{88} Q{580},{64} {688},{124} Q{756},{220} {696},{340} Q{636},{456} {520},{472} Q{440},{480} {360},{472} Q{244},{456} {184},{340} Q{124},{220} {192},{124} Q{260},{64} {360},{64} Q{400},{64} {440},{88}" fill="none" stroke="{PURPLE}" stroke-width="0.8" stroke-dasharray="6,4"/>')
    lines.append(f'<text x="440" y="486" text-anchor="middle" font-size="9" font-weight="600" fill="{PURPLE}">重复几万亿次</text>')

    # 节点
    for nx, ny, ntitle, line1, line2, is_accent in nodes:
        x, y = S(nx - NW//2), S(ny - NH//2)
        fill = "url(#acc)" if is_accent else CARD
        stroke = "none" if is_accent else BORDER
        shadow = "as" if is_accent else "s"
        tc = "#ffffff" if is_accent else TEXT
        sc = "rgba(255,255,255,0.7)" if is_accent else MUTED
        lines.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="{CARD_RX}" fill="{fill}" stroke="{stroke}" stroke-width="1" filter="url(#{shadow})"/>')
        lines.append(f'<text x="{S(x+16)}" y="{S(y+22)}" font-size="9" font-weight="700" fill="{sc}">{ntitle}</text>')
        lines.append(f'<text x="{S(x+16)}" y="{S(y+46)}" font-size="11" font-weight="600" fill="{tc}">{line1}</text>')
        lines.append(f'<text x="{S(x+16)}" y="{S(y+66)}" font-size="9" fill="{sc}">{line2}</text>')

    # 中心
    lines.append(f'<text x="440" y="310" text-anchor="middle" font-size="18" font-weight="700" fill="{A1}">猜下一个词</text>')
    lines.append(f'<text x="440" y="332" text-anchor="middle" font-size="9" fill="{MUTED}">GPT-4 预训练成本：~$1亿 · 3-6 个月 · 数万 GPU</text>')

    # 三根支柱
    pillars = [
        ("Warmup", A1, "学习率从零缓升", "Embedding 梯度极端稀疏", "优化器需积累梯度历史建立可靠估计"),
        ("梯度裁剪", AMBER, "限制单步更新上限", "防止异常 token 毁掉训练", "将梯度范数 clip 到 1.0，避免单步失控"),
        ("Weight Decay", GREEN, "分层衰减策略", "2D 权重：衰减防止过拟合", "1D 参数（LayerNorm）：不衰减"),
    ]
    for i, (pname, pc, p1, p2, p3) in enumerate(pillars):
        px = S(44 + i * 272)
        py = 520
        lines.append(f'<rect x="{px}" y="{py}" width="248" height="64" rx="8" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
        lines.append(f'<rect x="{px}" y="{py}" width="4" height="64" rx="2" fill="{pc}"/>')
        lines.append(f'<text x="{px+16}" y="{py+20}" font-size="11" font-weight="600" fill="{TEXT}">{pname}</text>')
        lines.append(f'<text x="{px+16}" y="{py+36}" font-size="9" fill="{MUTED}">{p1} · {p2}</text>')
        lines.append(f'<text x="{px+16}" y="{py+52}" font-size="8" fill="{MUTED}">{p3}</text>')

    lines.append(f'<rect x="160" y="594" width="560" height="18" rx="5" fill="#ede9fe" opacity="0.6"/>')
    lines.append(f'<text x="440" y="607" text-anchor="middle" font-size="9" font-weight="600" fill="{A1}">模型从未被教过什么是语法或逻辑——所有能力都从「猜下一个词」中涌现</text>')

    lines.append(FOOTER)
    path = os.path.join(OUT, "pretraining-loop.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")
    _validate(path, expected_viewbox=(0,0,880,620))


def diagram_4():
    """对齐技术演进"""
    W, H = 1100, 600
    lines = [make_header(W, H, "对齐技术三阶段：RLHF → DPO → GRPO", "三年三次简化——减掉的不是功能，是有人发现了更简洁的数学等价形式")]

    # 三列数据
    cols = [
        {"x":60,  "t":"RLHF", "s":"四个网络协同", "year":"2022", "yc":"#a3acb9",
         "boxes":["Policy Model（策略模型）","Reference Model（参考模型）","Reward Model（奖励模型）","Value Model（价值模型）"],
         "tag":"4 个网络 · 训练复杂","tag_c":"#64748b","tag_bg":"#f1f5f9",
         "models":"InstructGPT · ChatGPT"},
        {"x":410, "t":"DPO",  "s":"两个网络",     "year":"2023", "yc":AMBER,
         "boxes":["Policy Model（策略模型）","Reference Model（参考模型）"],
         "insight":"砍掉独立的 Reward / Value Model", "insight_c":AMBER,
         "tag":"2 个网络 · 训练简化","tag_c":"#7c3aed","tag_bg":"#ede9fe",
         "models":"Zephyr · Llama 3"},
        {"x":760, "t":"GRPO", "s":"一个网络 + 组内归一化","year":"2024", "yc":A1,
         "boxes":["Policy Model（策略模型）"],
         "insight":"组内互评 → 相对优势 → 无需独立参考", "insight_c":GREEN,
         "tag":"1 个网络 · 极致简化","tag_c":"#ffffff","tag_bg":"url(#acc)",
         "models":"DeepSeek-R1 · Qwen 3"},
    ]

    # 时间线
    lines.append(f'<line x1="230" y1="90" x2="870" y2="90" stroke="{BORDER}" stroke-width="2"/>')
    for cx, label, c in [(230,"2022","#a3acb9"),(550,"2023",AMBER),(870,"2024",A1)]:
        lines.append(f'<circle cx="{cx}" cy="90" r="4" fill="{c}"/>')
        lines.append(f'<text x="{cx}" y="80" text-anchor="middle" font-size="9" font-weight="600" fill="{c}">{label}</text>')

    # 演进箭头
    for ax in [370, 700]:
        lines.append(f'<line x1="{ax}" y1="280" x2="{ax+22}" y2="280" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
    lines.append(f'<text x="381" y="270" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">数学等价重构</text>')
    lines.append(f'<text x="711" y="270" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">进一步化简</text>')

    # 三列
    for col in cols:
        cx = col["x"]
        is_last = (col["t"] == "GRPO")
        stroke = A1 if is_last else BORDER
        shadow = "as" if is_last else "s"
        hdr_fill = "url(#acc)" if is_last else ("#ede9fe" if col["t"] == "DPO" else "#f1f5f9")
        tfill = "#ffffff" if is_last else TEXT

        lines.append(f'<rect x="{cx}" y="110" width="280" height="320" rx="10" fill="{CARD}" stroke="{stroke}" stroke-width="{"1.5" if is_last else "1"}" filter="url(#{shadow})"/>')
        lines.append(f'<rect x="{cx}" y="110" width="280" height="38" rx="10" fill="{hdr_fill}"/>')
        lines.append(f'<rect x="{cx}" y="138" width="280" height="10" fill="{hdr_fill}"/>')
        lines.append(f'<text x="{cx+140}" y="135" text-anchor="middle" font-size="14" font-weight="700" fill="{tfill}">{col["t"]}</text>')
        lines.append(f'<text x="{cx+140}" y="166" text-anchor="middle" font-size="10" fill="{MUTED}">{col["s"]}</text>')

        # insight pill
        box_start = 182
        if "insight" in col:
            lines.append(f'<rect x="{cx+20}" y="182" width="240" height="22" rx="5" fill="{col.get("insight_c",AMBER)}" opacity="0.1"/>')
            lines.append(f'<text x="{cx+140}" y="197" text-anchor="middle" font-size="9" font-weight="600" fill="{col["insight_c"]}">{col["insight"]}</text>')
            box_start = 214

        # 网络盒子
        for j, box in enumerate(col["boxes"]):
            by = box_start + j * 48
            is_box_accent = is_last and j == 0
            bfill = "url(#acc)" if is_box_accent else "#f8fafd"
            bstroke = A1 if is_box_accent else "#e2e8f0"
            btc = "#ffffff" if is_box_accent else TEXT
            lines.append(f'<rect x="{cx+20}" y="{by}" width="240" height="36" rx="6" fill="{bfill}" stroke="{bstroke}" stroke-width="0.8"/>')
            lines.append(f'<text x="{cx+32}" y="{by+23}" font-size="11" font-weight="600" fill="{btc}">{box}</text>')

        # 代表作
        lines.append(f'<text x="{cx+140}" y="296" text-anchor="middle" font-size="9" fill="{MUTED}">代表: {col["models"]}</text>')
        # tag
        lines.append(f'<rect x="{cx+70}" y="310" width="140" height="20" rx="10" fill="{col["tag_bg"]}"/>')
        lines.append(f'<text x="{cx+140}" y="324" text-anchor="middle" font-size="9" font-weight="600" fill="{col["tag_c"]}">{col["tag"]}</text>')

    # 底部结语
    lines.append(f'<rect x="220" y="460" width="660" height="32" rx="8" fill="{A1}" opacity="0.08"/>')
    lines.append(f'<text x="550" y="481" text-anchor="middle" font-size="11" font-weight="600" fill="{A1}">每一步减掉的不是功能——有人发现了更简洁的数学等价形式</text>')

    # 图例
    lx, ly = 60, 520
    lines.append(f'<rect x="{lx}" y="{ly}" width="180" height="48" rx="6" fill="#fafbfc" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'<text x="{lx+12}" y="{ly+14}" font-size="8" font-weight="700" fill="{MUTED}">图例</text>')
    for j, (c,label) in enumerate([("#a3acb9","上一代方案"),(A1,"当前最优")]):
        iy = ly + 24 + j * 14
        lines.append(f'<rect x="{lx+12}" y="{iy}" width="16" height="10" rx="3" fill="{c}" opacity="0.2" stroke="{c}" stroke-width="0.5"/>')
        lines.append(f'<text x="{lx+36}" y="{iy+9}" font-size="9" fill="{TEXT}">{label}</text>')

    lines.append(FOOTER)
    path = os.path.join(OUT, "alignment-evolution.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")
    _validate(path, expected_viewbox=(0,0,1100,600))


def diagram_5():
    """架构演进"""
    W, H = 1100, 620
    lines = [make_header(W, H, "架构演进：推理成本如何重塑模型设计", "从 GPT-2 的 Dense+MHA 到 DeepSeek-V3 的 MoE+MLA——驱动力不是「更强」，是「能在硬件上跑」")]

    stages = [
        (40,  "GPT-2",        "Dense + MHA",         "#f1f5f9", TEXT,   ["1.5B 参数","100% 激活","KV Cache = O(N×L)"]),
        (310, "GPT-3/4",      "Dense + MHA（同架构）","#f1f5f9", TEXT,   ["175B→1.8T 参数","规模扩大 100-1000×","KV Cache 成为瓶颈"]),
        (580, "Llama 3",      "GQA · MoE",            "#ede9fe", TEXT,   ["GQA: Cache ↓ 75%","MoE: 671B 参·激活 6%","知识↑ 计算↓"]),
        (870, "DeepSeek-V3",  "MoE + MLA",            "url(#acc)", "#ffffff", ["MLA: Cache 再压缩","671B 总 · 37B 活跃","极致推理效率"]),
    ]

    # 时间线
    for sx in [160,380,660,960]:
        lines.append(f'<circle cx="{sx}" cy="94" r="4" fill="#a3acb9"/>')
    lines.append(f'<line x1="160" y1="94" x2="960" y2="94" stroke="{BORDER}" stroke-width="2"/>')

    for sx, name, arch, hdr_fill, tfill, details in stages:
        is_last = (sx == 870)
        stroke = A1 if is_last else BORDER
        shadow = "as" if is_last else "s"

        lines.append(f'<rect x="{sx}" y="112" width="220" height="192" rx="9" fill="{CARD}" stroke="{stroke}" stroke-width="{"1.5" if is_last else "1"}" filter="url(#{shadow})"/>')
        lines.append(f'<rect x="{sx}" y="112" width="220" height="36" rx="9" fill="{hdr_fill}"/>')
        lines.append(f'<rect x="{sx}" y="138" width="220" height="10" fill="{hdr_fill}"/>')
        lines.append(f'<text x="{sx+110}" y="136" text-anchor="middle" font-size="13" font-weight="600" fill="{tfill}">{name}</text>')
        lines.append(f'<text x="{sx+110}" y="166" font-size="10" fill="{MUTED}" text-anchor="middle">{arch}</text>')

        for j, d in enumerate(details):
            dc = GREEN if (sx >= 580 and j == 0) else (RED if (sx == 310 and j == 2) else TEXT)
            lines.append(f'<text x="{sx+110}" y="{190+j*18}" font-size="9" fill="{dc}" text-anchor="middle">{d}</text>')

        # 演进箭头
        if sx < 870:
            ax = sx + 220
            lines.append(f'<line x1="{ax}" y1="208" x2="{ax+48}" y2="208" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
        if sx == 310:
            lines.append(f'<text x="{sx+244}" y="200" text-anchor="middle" font-size="8" font-weight="700" fill="{A1}">推理倒逼</text>')

    # 对比表
    TY = 332
    lines.append(f'<text x="550" y="{TY}" text-anchor="middle" font-size="12" font-weight="700" fill="{TEXT}">四代推理性能对比</text>')
    col_hdrs = ["指标","GPT-2 (MHA)","GPT-4 (MHA)","Llama 3 (GQA)","DeepSeek-V3 (MLA)"]
    col_fills = ["#f1f5f9","#f1f5f9","#f1f5f9","#ede9fe","url(#acc)"]
    col_tc = [MUTED, MUTED, MUTED, MUTED, "#ffffff"]
    col_x = [80,248,416,584,752]

    for j, (hdr, cf, tc) in enumerate(zip(col_hdrs, col_fills, col_tc)):
        lines.append(f'<rect x="{col_x[j]}" y="{TY+16}" width="160" height="28" rx="4" fill="{cf}"/>')
        lines.append(f'<text x="{col_x[j]+80}" y="{TY+34}" text-anchor="middle" font-size="9" font-weight="600" fill="{tc}">{hdr}</text>')

    rows = [
        ("KV Cache / token", ["1×（基线）","~100×","~0.25×","≪ 0.25×"], [MUTED,RED,GREEN,A1]),
        ("激活参数比例",     ["100%","100%","~6%","~6%"],             [MUTED,RED,GREEN,A1]),
        ("推理成本",         ["很低","极高","低","很低"],             [GREEN,RED,GREEN,A1]),
    ]
    for ri, (rname, vals, vcs) in enumerate(rows):
        ry = TY + 48 + ri * 30
        bg = "#f8fafd" if ri%2==0 else CARD
        lines.append(f'<rect x="{col_x[0]}" y="{ry}" width="160" height="28" fill="{bg}"/>')
        lines.append(f'<text x="{col_x[0]+80}" y="{ry+18}" text-anchor="middle" font-size="9" font-weight="500" fill="{TEXT}">{rname}</text>')
        for j, (v, vc) in enumerate(zip(vals, vcs)):
            lines.append(f'<rect x="{col_x[j+1]}" y="{ry}" width="160" height="28" fill="{bg}"/>')
            lines.append(f'<text x="{col_x[j+1]+80}" y="{ry+18}" text-anchor="middle" font-size="9" font-weight="600" fill="{vc}">{v}</text>')

    lines.append(f'<rect x="240" y="{TY+148}" width="620" height="26" rx="6" fill="{A1}" opacity="0.08"/>')
    lines.append(f'<text x="550" y="{TY+166}" text-anchor="middle" font-size="10" font-weight="600" fill="{A1}">共同方向不是「更强」——是能在现有 GPU 上跑得动。效果是副产品，推理可行性才是主驱动</text>')

    lines.append(FOOTER)
    path = os.path.join(OUT, "architecture-evolution.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")
    _validate(path, expected_viewbox=(0,0,1100,620))


def diagram_6():
    """经济回路"""
    W, H = 880, 600
    lines = [make_header(W, H, "经济回路：推理成本如何反向重塑架构", "训练是一次性投入，推理是永续成本——数月推理即超训练，谁占大头谁主导方向")]

    # ── 上半：成本对比 ──
    # 训练成本卡
    lines.append(f'<rect x="40" y="88" width="360" height="190" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="40" y="88" width="4" height="190" rx="2" fill="#a3acb9"/>')
    lines.append(f'<text x="64" y="116" font-size="14" font-weight="700" fill="{TEXT}">训练成本</text>')
    lines.append(f'<text x="64" y="134" font-size="9" fill="{MUTED}">一次性投入 · 已经支付</text>')
    lines.append(f'<rect x="64" y="148" width="52" height="52" rx="8" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1"/>')
    lines.append(f'<text x="90" y="180" text-anchor="middle" font-size="16" font-weight="700" fill="#64748b">$1亿</text>')
    lines.append(f'<text x="132" y="164" font-size="10" fill="{TEXT}">GPT-4 预训练</text>')
    lines.append(f'<text x="132" y="182" font-size="9" fill="{MUTED}">时长 3-6 个月 · GPU 数万张</text>')
    lines.append(f'<text x="132" y="198" font-size="9" fill="{MUTED}">占生命周期总算力 95%</text>')
    # 时间条
    lines.append(f'<text x="64" y="246" font-size="9" fill="{MUTED}">时间维度</text>')
    lines.append(f'<rect x="64" y="252" width="316" height="14" rx="4" fill="#f1f5f9"/>')
    lines.append(f'<rect x="64" y="252" width="72" height="14" rx="4" fill="#a3acb9" opacity="0.3"/>')
    lines.append(f'<text x="100" y="262" text-anchor="middle" font-size="8" fill="#64748b">3-6月</text>')
    lines.append(f'<text x="148" y="262" font-size="8" fill="{MUTED}">———— 之后不再产生 ————</text>')

    # 推理成本卡
    lines.append(f'<rect x="480" y="88" width="360" height="190" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="480" y="88" width="4" height="190" rx="2" fill="url(#acc)"/>')
    lines.append(f'<text x="504" y="116" font-size="14" font-weight="700" fill="{TEXT}">推理成本</text>')
    lines.append(f'<text x="504" y="134" font-size="9" font-weight="600" fill="{A1}">持续累积 · 永续增长</text>')
    lines.append(f'<rect x="504" y="148" width="148" height="52" rx="8" fill="{A1}" opacity="0.1" stroke="{A1}" stroke-width="1"/>')
    lines.append(f'<text x="578" y="180" text-anchor="middle" font-size="16" font-weight="700" fill="{A1}">→∞</text>')
    lines.append(f'<text x="668" y="164" font-size="10" fill="{TEXT}">ChatGPT 日常服务</text>')
    lines.append(f'<text x="668" y="182" font-size="9" fill="{MUTED}">每日数亿次请求</text>')
    lines.append(f'<text x="668" y="198" font-size="9" fill="{MUTED}">瓶颈：参数搬运 + KV Cache</text>')
    lines.append(f'<text x="504" y="246" font-size="9" fill="{MUTED}">时间维度</text>')
    lines.append(f'<rect x="504" y="252" width="316" height="14" rx="4" fill="#f1f5f9"/>')
    lines.append(f'<rect x="504" y="252" width="316" height="14" rx="4" fill="{A1}" opacity="0.12"/>')
    lines.append(f'<text x="662" y="262" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">持续增长 · 没有终点</text>')

    # 交叉箭头
    lines.append(f'<line x1="412" y1="184" x2="468" y2="184" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
    lines.append(f'<text x="440" y="176" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">数月后</text>')

    lines.append(f'<text x="440" y="304" text-anchor="middle" font-size="12" font-weight="700" fill="{A1}">数月推理成本 ≈ 一次训练成本 → 此后推理持续超过训练</text>')

    # 分隔线
    lines.append(f'<line x1="80" y1="324" x2="800" y2="324" stroke="{BORDER}" stroke-width="1"/>')

    # ── 下半：创新回路 ──
    lines.append(f'<text x="440" y="350" text-anchor="middle" font-size="13" font-weight="700" fill="{TEXT}">推理成本驱动的架构创新回路</text>')

    eco_nodes = [
        (40,  375, RED,    "#fef2f2", "推理瓶颈",   ["KV Cache 太大","显存放不下","搬运时间 >> 计算时间"]),
        (330, 375, A1,     "#ede9fe", "架构创新",   ["GQA → Cache 砍 75%","MoE → 只激活 ~6%","MLA → 缓存再压缩"]),
        (620, 375, GREEN,  "#ecfdf5", "推理成本下降",["每 token 成本降低","服务更多用户","增长 → 新瓶颈出现"]),
    ]
    for nx, ny, nc, nbg, ntitle, nitems in eco_nodes:
        lines.append(f'<rect x="{nx}" y="{ny}" width="220" height="96" rx="9" fill="{CARD}" stroke="{nc}" stroke-width="1" filter="url(#s)"/>')
        lines.append(f'<rect x="{nx}" y="{ny}" width="220" height="28" rx="9" fill="{nbg}"/>')
        lines.append(f'<rect x="{nx}" y="{ny+18}" width="220" height="10" fill="{nbg}"/>')
        lines.append(f'<text x="{nx+110}" y="{ny+19}" text-anchor="middle" font-size="11" font-weight="600" fill="{nc}">{ntitle}</text>')
        for j, item in enumerate(nitems):
            lines.append(f'<text x="{nx+16}" y="{ny+48+j*16}" font-size="9" fill="{TEXT}">{item}</text>')

    # 节点间箭头
    lines.append(f'<line x1="260" y1="416" x2="316" y2="416" stroke="{RED}" stroke-width="1.2" marker-end="url(#me)"/>')
    lines.append(f'<text x="288" y="408" font-size="8" font-weight="600" fill="{RED}">倒逼</text>')
    lines.append(f'<line x1="550" y1="416" x2="606" y2="416" stroke="{GREEN}" stroke-width="1.2" marker-end="url(#md)"/>')
    lines.append(f'<text x="578" y="408" font-size="8" font-weight="600" fill="{GREEN}">降低</text>')

    # 反馈回路
    lines.append(f'<path d="M730,470 L730,494 Q730,504 720,508 L440,508 Q428,508 416,504 L150,494 Q138,490 138,476 L138,470" fill="none" stroke="{PURPLE}" stroke-width="0.8" stroke-dasharray="6,4" marker-end="url(#me)"/>')
    lines.append(f'<text x="440" y="524" text-anchor="middle" font-size="8" font-weight="600" fill="{PURPLE}">用户量增长 → 新一轮瓶颈 → 新一轮创新</text>')

    lines.append(f'<rect x="140" y="556" width="600" height="24" rx="6" fill="url(#acc)" opacity="0.07"/>')
    lines.append(f'<text x="440" y="573" text-anchor="middle" font-size="10" font-weight="600" fill="{A1}">驱动力重心：训练成本 → 推理成本。谁占总成本更多，谁主导技术方向</text>')

    lines.append(FOOTER)
    path = os.path.join(OUT, "economics-loop.svg")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {os.path.basename(path)}")
    _validate(path, expected_viewbox=(0,0,880,600))


# ═══════════════════════════════════════════════════════════════
# Gate 验证
# ═══════════════════════════════════════════════════════════════
def _validate(path, expected_viewbox=None):
    """Gate 1-3 基础验证：XML 合法性 / viewBox / 内容量"""
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        vb = root.get("viewBox", "")
        if expected_viewbox:
            expected = f"{expected_viewbox[0]} {expected_viewbox[1]} {expected_viewbox[2]} {expected_viewbox[3]}"
            assert vb == expected, f"viewBox mismatch: got {vb}, expected {expected}"
        # Gate 4: 内容量检查（不能是空文件）
        content = ET.tostring(root, encoding="unicode")
        assert len(content) > 1000, f"File too small ({len(content)} bytes)"
        print(f"    [Gate] XML valid | viewBox={vb} | size={len(content)} bytes")
    except Exception as e:
        print(f"    [Gate FAIL] {path}: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 2: 精确实现（Python 生成 SVG）")
    print("=" * 60)
    diagram_1()
    diagram_2()
    diagram_3()
    diagram_4()
    diagram_5()
    diagram_6()
    print()
    print("=" * 60)
    print("Phase 3: Gate 验证全部通过")
    print("=" * 60)
