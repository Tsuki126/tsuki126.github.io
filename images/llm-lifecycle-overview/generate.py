#!/usr/bin/env python3
"""Generate all 6 high-quality SVG diagrams for the LLM Lifecycle blog post.
Precise math, grid-aligned, Stripe Gradient theme. No hand-approximation."""

import math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# ── Design System ──────────────────────────────────────────────
BG1, BG2 = "#f8f9fc", "#f0f2f8"
ACCENT1, ACCENT2 = "#635bff", "#8f6ed5"
CARD_FILL, CARD_STROKE = "#ffffff", "#eef0f6"
TEXT_DARK, TEXT_MUTED = "#1a1f36", "#a3acb9"
GREEN, AMBER, PURPLE, RED = "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"
FONT = "Inter, system-ui, -apple-system, sans-serif"
CARD_RX, CARD_SHADOW = 9, '<filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#1a1f36" flood-opacity="0.05"/></filter>'
ACCENT_SHADOW = '<filter id="as"><feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#635bff" flood-opacity="0.12"/></filter>'
BLUR = '<filter id="b"><feGaussianBlur stdDeviation="50"/></filter>'
GRID = 4  # all coords snap to this

def snap(v): return round(v / GRID) * GRID

def header(f, w, h, title, subtitle):
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">\n')
    f.write(f'<defs><linearGradient id="bg"><stop offset="0%" stop-color="{BG1}"/><stop offset="100%" stop-color="{BG2}"/></linearGradient>')
    f.write(f'<linearGradient id="acc"><stop offset="0%" stop-color="{ACCENT1}"/><stop offset="100%" stop-color="{ACCENT2}"/></linearGradient>')
    f.write(f'{CARD_SHADOW}{ACCENT_SHADOW}{BLUR}')
    # arrow markers
    for name, color in [("ma","#635bff"),("mb","#f59e0b"),("mc","#8b5cf6"),("md","#10b981"),("me","#ef4444")]:
        f.write(f'<marker id="{name}" viewBox="0 0 10 8" refX="10" refY="4" markerWidth="6" markerHeight="5" orient="auto"><path d="M0,0L10,4L0,8Z" fill="{color}"/></marker>')
    f.write('</defs>\n')
    f.write(f'<rect width="{w}" height="{h}" fill="url(#bg)"/>\n')
    # title
    f.write(f'<text x="{w//2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="{TEXT_DARK}" letter-spacing="-0.3">{title}</text>\n')
    tw = len(title) * 12
    f.write(f'<line x1="{w//2-tw//2}" y1="52" x2="{w//2+tw//2}" y2="52" stroke="{ACCENT1}" stroke-width="2.5" stroke-linecap="round"/>\n')
    f.write(f'<text x="{w//2}" y="70" text-anchor="middle" font-size="10" fill="{TEXT_MUTED}">{subtitle}</text>\n')

def footer(f): f.write('</svg>\n')

def decor_circles(f, circles):
    for cx, cy, r, c in circles:
        f.write(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" opacity="0.025" filter="url(#b)"/>\n')

def card(f, x, y, w=140, h=88, accent=False, badge=None):
    stroke = f'{ACCENT1}' if accent else CARD_STROKE
    sw = '1.5' if accent else '1'
    shadow = 'as' if accent else 's'
    f.write(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{CARD_RX}" fill="{CARD_FILL}" stroke="{stroke}" stroke-width="{sw}" filter="url(#{shadow})"/>\n')
    if badge:
        cx, cy = snap(x + 18), snap(y + 18)
        f.write(f'<circle cx="{cx}" cy="{cy}" r="9" fill="url(#acc)"/>\n')
        f.write(f'<text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="9" fill="#ffffff" font-weight="700">{badge}</text>\n')
    return x + 16, y + 12  # text anchor

def card_text(f, ax, ay, title, sub, note, badge=False):
    tx = snap(ax + (24 if badge else 0))
    f.write(f'<text x="{tx}" y="{ay}" font-size="12" font-weight="600" fill="{TEXT_DARK}">{title}</text>\n')
    f.write(f'<text x="{ax}" y="{ay+22}" font-size="9" fill="{TEXT_MUTED}">{sub}</text>\n')
    f.write(f'<text x="{ax}" y="{ay+42}" font-size="8" fill="{TEXT_MUTED}">{note}</text>\n')

def curved_arrow(f, x1, y1, x2, y2, cx, cy, color, width=1.5, dashed=False, marker="ma", label=None, lx=None, ly=None):
    ds = 'stroke-dasharray="6,4" ' if dashed else ''
    f.write(f'<path d="M{snap(x1)},{snap(y1)} Q{snap(cx)},{snap(cy)} {snap(x2)},{snap(y2)}" fill="none" stroke="{color}" stroke-width="{width}" {ds}marker-end="url(#{marker})"/>\n')
    if label:
        lx = lx or snap((x1 + x2) // 2)
        ly = ly or snap((y1 + y2) // 2)
        f.write(f'<rect x="{lx-32}" y="{ly-10}" width="64" height="18" rx="3" fill="#ffffff" fill-opacity="0.88"/>\n')
        f.write(f'<text x="{lx}" y="{ly+3}" text-anchor="middle" font-size="8" fill="{color}" font-weight="600">{label}</text>\n')

def pill(f, cx, cy, w, h, text, accent=True):
    fill = 'url(#acc)' if accent else CARD_FILL
    f.write(f'<rect x="{cx-w//2}" y="{cy-h//2}" width="{w}" height="{h}" rx="{h//2}" fill="{fill}" filter="url(#as)"/>\n')
    f.write(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="14" fill="#ffffff" font-weight="700">{text}</text>\n')

def insight_bar(f, w, y, text):
    f.write(f'<rect x="{(1100-w)//2}" y="{y}" width="{w}" height="32" rx="6" fill="#ede9fe" opacity="0.7"/>\n')
    f.write(f'<text x="550" y="{y+21}" text-anchor="middle" font-size="10" fill="{ACCENT1}" font-weight="600">{text}</text>\n')

def legend(f, x, y, items):
    h = 16 + len(items) * 16
    f.write(f'<rect x="{x}" y="{y}" width="180" height="{h}" rx="8" fill="#fafbfc" stroke="{CARD_STROKE}" stroke-width="1"/>\n')
    f.write(f'<text x="{x+12}" y="{y+16}" font-size="9" fill="{TEXT_MUTED}" font-weight="700">图例</text>\n')
    for i, (color, dash, label) in enumerate(items):
        iy = y + 30 + i * 16
        ds = f'stroke-dasharray="6,4" ' if dash else ''
        f.write(f'<line x1="{x+12}" y1="{iy+4}" x2="{x+40}" y2="{iy+4}" stroke="{color}" stroke-width="1.5" {ds}/>\n')
        f.write(f'<text x="{x+48}" y="{iy+8}" font-size="9" fill="{TEXT_DARK}">{label}</text>\n')


# ═══════════════════════════════════════════════════════════════
# Diagram 1: Lifecycle Architecture (pentagon loop)
# ═══════════════════════════════════════════════════════════════
def diagram_1():
    w, h = 1100, 720
    cx, cy, r = 550, 370, 210
    # pentagon vertices (clockwise from top), angles start at -90°
    verts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        verts.append((snap(cx + r * math.cos(a)), snap(cy + r * math.sin(a))))
    # card data
    cards = [
        ("数据工程", "采集 · 清洗 · 分词", "50-80% 原始数据被丢弃"),
        ("预训练", "猜下一个词 × 几万亿次", "算力 95% · 约 $1 亿"),
        ("后训练", "SFT + 对齐", "1-2% 成本 · 100% 体验差异"),
        ("评估", "MMLU · MATH · HumanEval", "每个阶段的「眼睛」"),
        ("推理部署", "GQA · MoE · MLA", "永续成本重塑架构"),
    ]
    arrow_labels = ["训练数据", "Base Model", "Aligned Model", "部署", "用户反馈 · 日志回流"]
    # arrow colors: 4 solid + 1 dashed
    arrow_colors = [ACCENT1, ACCENT1, ACCENT1, ACCENT1, PURPLE]
    arrow_dashed = [False, False, False, False, True]
    arrow_markers = ["ma", "ma", "ma", "ma", "mc"]

    with open(os.path.join(OUT, "lifecycle-architecture.svg"), "w") as f:
        header(f, w, h, "LLM 生命周期全景：五道工序的回路", "从互联网原始文本到对话助手，首尾相连的持续运转回路")
        decor_circles(f, [(880, 140, 200, ACCENT1), (220, 560, 180, ACCENT2), (550, 380, 160, ACCENT1)])

        # faint pentagon guide
        pts = " ".join(f"{vx},{vy}" for vx, vy in verts)
        f.write(f'<polygon points="{pts}" fill="none" stroke="{ACCENT1}" stroke-width="0.5" opacity="0.08" stroke-dasharray="8,6"/>\n')

        # arrows
        for i in range(5):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % 5]
            # control point: midpoint pushed outward
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            vx, vy = mx - cx, my - cy
            vl = math.sqrt(vx*vx + vy*vy) or 1
            push = 30
            cpx, cpy = snap(mx + vx / vl * push), snap(my + vy / vl * push)
            # adjust endpoints to card edges
            dx, dy = x2 - x1, y2 - y1
            dl = math.sqrt(dx*dx + dy*dy) or 1
            # start from card edge
            sx = snap(x1 + dx / dl * 70)
            sy = snap(y1 + dy / dl * 55)
            # end near next card edge
            ex = snap(x2 - dx / dl * 70)
            ey = snap(y2 - dy / dl * 55)
            curved_arrow(f, sx, sy, ex, ey, cpx, cpy, arrow_colors[i], dashed=arrow_dashed[i], marker=arrow_markers[i], label=arrow_labels[i])

        # cards
        for i, (title, sub, note) in enumerate(cards):
            vx, vy = verts[i]
            cx_card, cy_card = vx, vy
            x, y = snap(cx_card - 70), snap(cy_card - 44)
            ax, ay = card(f, x, y, badge=i+1)
            card_text(f, ax, ay, title, sub, note, badge=True)

        # center pill
        pill(f, cx, cy, 152, 44, "LLM 生命周期")

        legend(f, 888, 600, [
            (ACCENT1, False, "主数据流"),
            (PURPLE, True, "反馈回路"),
            (GREEN, False, "数据流转"),
        ])
        footer(f)

# ═══════════════════════════════════════════════════════════════
# Diagram 2: Tokenizer Comparison
# ═══════════════════════════════════════════════════════════════
def diagram_2():
    w, h = 880, 540
    with open(os.path.join(OUT, "tokenizer-comparison.svg"), "w") as f:
        header(f, w, h, "Tokenizer 语言效率：英文 vs 中文", "同一个 Tokenizer 对不同语言的编码效率差异巨大——直接影响推理成本和速度")
        decor_circles(f, [(720, 120, 160, ACCENT1), (160, 420, 140, ACCENT2)])

        # Left panel: English
        f.write(f'<rect x="40" y="100" width="370" height="260" rx="10" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
        f.write(f'<rect x="40" y="100" width="370" height="36" rx="10" fill="#f8fafd"/>\n')
        f.write(f'<rect x="40" y="126" width="370" height="10" fill="#f8fafd"/>\n')
        f.write(f'<text x="225" y="124" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT_DARK}">英文文本 · Token 化</text>\n')
        f.write(f'<text x="60" y="164" font-size="11" fill="{TEXT_MUTED}" font-weight="600">输入</text>\n')
        f.write(f'<rect x="110" y="150" width="280" height="26" rx="5" fill="{BG1}" stroke="{CARD_STROKE}" stroke-width="0.5"/>\n')
        f.write(f'<text x="250" y="168" text-anchor="middle" font-size="12" font-weight="500" fill="{TEXT_DARK}">The capital of France is Paris</text>\n')
        f.write(f'<text x="60" y="210" font-size="11" fill="{TEXT_MUTED}" font-weight="600">分词</text>\n')
        words = ["The", "capital", "of", "France", "is", "Paris"]
        for j, word in enumerate(words):
            bx = snap(110 + j * 48)
            f.write(f'<rect x="{bx}" y="196" width="42" height="24" rx="5" fill="#ecfdf5" stroke="{GREEN}" stroke-width="0.8"/>\n')
            f.write(f'<text x="{bx+21}" y="213" text-anchor="middle" font-size="10" font-weight="500" fill="{TEXT_DARK}">{word}</text>\n')
        f.write(f'<text x="60" y="256" font-size="11" font-weight="700" fill="{GREEN}">结果: 6 tokens</text>\n')
        f.write(f'<text x="60" y="274" font-size="10" fill="{TEXT_MUTED}">≈ 1 token / 词 — 高效编码</text>\n')
        f.write(f'<rect x="110" y="300" width="36" height="28" rx="5" fill="{GREEN}" opacity="0.15"/>\n')
        f.write(f'<text x="128" y="319" text-anchor="middle" font-size="16" font-weight="700" fill="{GREEN}">6</text>\n')
        f.write(f'<text x="158" y="319" font-size="11" fill="{TEXT_MUTED}">tokens</text>\n')

        # Right panel: Chinese
        f.write(f'<rect x="470" y="100" width="370" height="260" rx="10" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
        f.write(f'<rect x="470" y="100" width="370" height="36" rx="10" fill="#f8fafd"/>\n')
        f.write(f'<rect x="470" y="126" width="370" height="10" fill="#f8fafd"/>\n')
        f.write(f'<text x="655" y="124" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT_DARK}">中文文本 · Token 化（英文为主 Tokenizer）</text>\n')
        f.write(f'<text x="490" y="164" font-size="11" fill="{TEXT_MUTED}" font-weight="600">输入</text>\n')
        f.write(f'<rect x="540" y="150" width="280" height="26" rx="5" fill="{BG1}" stroke="{CARD_STROKE}" stroke-width="0.5"/>\n')
        f.write(f'<text x="680" y="168" text-anchor="middle" font-size="14" font-weight="500" fill="{TEXT_DARK}">法国的首都是巴黎</text>\n')
        f.write(f'<text x="490" y="210" font-size="11" fill="{TEXT_MUTED}" font-weight="600">分词</text>\n')
        for j in range(8):
            bx = snap(540 + j * 28)
            f.write(f'<rect x="{bx}" y="196" width="24" height="24" rx="4" fill="#fef3c7" stroke="{AMBER}" stroke-width="0.8"/>\n')
            f.write(f'<text x="{bx+12}" y="213" text-anchor="middle" font-size="8" fill="{AMBER}">···</text>\n')
        f.write(f'<text x="490" y="256" font-size="11" font-weight="700" fill="{AMBER}">结果: ~30 tokens</text>\n')
        f.write(f'<text x="490" y="274" font-size="10" fill="{TEXT_MUTED}">≈ 3-6 token / 字 — 低效编码</text>\n')
        f.write(f'<rect x="540" y="300" width="150" height="28" rx="5" fill="{AMBER}" opacity="0.15"/>\n')
        f.write(f'<text x="615" y="319" text-anchor="middle" font-size="16" font-weight="700" fill="{AMBER}">~30</text>\n')
        f.write(f'<text x="700" y="319" font-size="11" fill="{TEXT_MUTED}">tokens</text>\n')

        # Bottom: Solution
        f.write(f'<rect x="40" y="390" width="800" height="76" rx="10" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
        f.write(f'<rect x="40" y="390" width="800" height="6" rx="3" fill="url(#acc)"/>\n')
        f.write(f'<text x="60" y="420" font-size="12" font-weight="700" fill="{TEXT_DARK}">中文优化 Tokenizer（Qwen · DeepSeek 的做法）</text>\n')
        f.write(f'<text x="60" y="438" font-size="10" fill="{TEXT_MUTED}">训练 Tokenizer 时大幅提高中文数据配比 → 同样的句子 ~7 tokens（≈1 token/字），效率提升 4-5×</text>\n')
        f.write(f'<rect x="60" y="448" width="36" height="14" rx="4" fill="#ede9fe" stroke="{ACCENT1}" stroke-width="0.8"/>\n')
        f.write(f'<text x="78" y="459" text-anchor="middle" font-size="11" font-weight="700" fill="{ACCENT1}">7</text>\n')
        f.write(f'<text x="110" y="459" font-size="10" font-weight="600" fill="{GREEN}">tokens（优化后）</text>\n')

        legend(f, 660, 130, [
            (GREEN, False, "高效编码 ~1 token"),
            (AMBER, False, "低效编码 3-6 token"),
            (ACCENT1, False, "优化方案"),
        ])
        footer(f)

# ═══════════════════════════════════════════════════════════════
# Diagram 3: Pre-training Loop
# ═══════════════════════════════════════════════════════════════
def diagram_3():
    w, h = 880, 620
    # Diamond loop: 4 nodes at top/right/bottom/left
    nodes = [
        (440, 140, "① 输入文本", "取一段文字，遮掉最后一个词", '"法国的首都是 [MASK]"'),
        (620, 260, "② 模型预测", "计算每个可能词的概率分布", "巴黎 92% · 伦敦 3% · 其他 3%"),
        (440, 400, "③ 计算 Loss", "对比预测与真实答案", "猜错了 · loss 很高"),
        (260, 260, "④ 更新参数", "反向传播 · 微调全部参数", "每步幅度微小到可忽略"),
    ]
    accent_node = 2  # index of node 3 (0-based)

    with open(os.path.join(OUT, "pretraining-loop.svg"), "w") as f:
        header(f, w, h, "预训练：几万亿次「猜下一个词」循环", "Pre-training Loop — Predict Next Token")
        decor_circles(f, [(720, 120, 150, ACCENT1), (160, 500, 130, ACCENT2)])

        # loop arrows (drawn first)
        arrow_specs = [
            (540, 186, 620, 244, 592, 200, ACCENT1, "ma", "前向传播"),
            (644, 310, 520, 370, 600, 352, ACCENT1, "ma", "预测结果"),
            (360, 410, 300, 346, 320, 388, AMBER, "mb", "梯度回传"),
            (236, 300, 360, 216, 292, 252, ACCENT1, "ma", "参数更新"),
        ]
        for x1, y1, x2, y2, cpx, cpy, color, marker, label in arrow_specs:
            curved_arrow(f, x1, y1, x2, y2, cpx, cpy, color, marker=marker, label=label)

        # dashed outer loop
        f.write(f'<path d="M{snap(440)},{snap(90)} Q{snap(560)},{snap(60)} {snap(680)},{snap(120)} Q{snap(750)},{snap(240)} {snap(680)},{snap(340)} Q{snap(620)},{snap(440)} {snap(520)},{snap(460)} Q{snap(440)},{snap(468)} {snap(360)},{snap(460)} Q{snap(260)},{snap(440)} {snap(200)},{snap(340)} Q{snap(130)},{snap(240)} {snap(200)},{snap(120)} Q{snap(240)},{snap(60)} {snap(360)},{snap(60)} Q{snap(400)},{snap(60)} {snap(440)},{snap(90)}" fill="none" stroke="{PURPLE}" stroke-width="0.8" stroke-dasharray="6,4"/>\n')
        f.write(f'<text x="440" y="478" text-anchor="middle" font-size="9" font-weight="600" fill="{PURPLE}">重复几万亿次</text>\n')

        # nodes
        for i, (nx, ny, ntitle, nsub, nnote) in enumerate(nodes):
            is_accent = (i == accent_node)
            x, y = snap(nx - 88), snap(ny - 44)
            ax, ay = card(f, x, y, w=176, h=88, accent=is_accent)
            fill = "#ffffff" if not is_accent else ACCENT1
            tfill = TEXT_DARK if not is_accent else "#ffffff"
            sf1 = "#a3acb9" if not is_accent else "rgba(255,255,255,0.7)"
            sf2 = "#a3acb9" if not is_accent else "rgba(255,255,255,0.7)"
            f.write(f'<text x="{ax}" y="{ay+2}" font-size="9" font-weight="700" fill="{sf1}">{ntitle}</text>\n')
            f.write(f'<text x="{ax}" y="{ay+22}" font-size="11" font-weight="600" fill="{tfill}">{nsub}</text>\n')
            f.write(f'<text x="{ax}" y="{ay+42}" font-size="9" fill="{sf2}">{nnote}</text>\n')

        # center stats
        f.write(f'<text x="440" y="310" text-anchor="middle" font-size="18" font-weight="700" fill="{ACCENT1}">猜下一个词</text>\n')
        f.write(f'<text x="440" y="332" text-anchor="middle" font-size="9" fill="{TEXT_MUTED}">GPT-4 预训练: ~$1亿 · 3-6 个月 · 数万 GPU</text>\n')

        # Three pillars
        pillars = [
            ("Warmup", ACCENT1, "学习率从零缓升", "Embedding 梯度极端稀疏", "优化器需积累梯度历史"),
            ("梯度裁剪", AMBER, "限制每次参数更新的上限", "防止异常 token 毁掉训练", "将梯度范数 clip 到 1.0"),
            ("Weight Decay", GREEN, "分层衰减", "2D 权重衰减，1D 参数不衰减", "矩阵正则化，LayerNorm 豁免"),
        ]
        for i, (pname, pcolor, p1, p2, p3) in enumerate(pillars):
            px = snap(44 + i * 256 + i * 28)
            py = 500
            f.write(f'<rect x="{px}" y="{py}" width="236" height="64" rx="8" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
            f.write(f'<rect x="{px}" y="{py}" width="4" height="64" rx="2" fill="{pcolor}"/>\n')
            f.write(f'<text x="{px+16}" y="{py+20}" font-size="11" font-weight="600" fill="{TEXT_DARK}">{pname}</text>\n')
            f.write(f'<text x="{px+16}" y="{py+36}" font-size="9" fill="{TEXT_MUTED}">{p1}</text>\n')
            f.write(f'<text x="{px+16}" y="{py+50}" font-size="8" fill="{TEXT_MUTED}">{p2} · {p3}</text>\n')

        insight_bar(f, 600, 580, "模型从未被教过什么是语法或逻辑——所有能力都从「猜下一个词」中涌现")
        legend(f, 700, 540, [
            (ACCENT1, False, "前向/参数更新"),
            (AMBER, False, "梯度回传"),
            (PURPLE, True, "循环重复"),
        ])
        footer(f)

# ═══════════════════════════════════════════════════════════════
# Diagram 4: Alignment Evolution
# ═══════════════════════════════════════════════════════════════
def diagram_4():
    w, h = 1100, 600
    cols = [
        {
            "title": "RLHF", "sub": "四个网络协同", "year": "2022", "color": "#a3acb9",
            "boxes": ["Policy Model（策略模型）", "Reference Model（参考模型）", "Reward Model（奖励模型）", "Value Model（价值模型）"],
            "tag": "4 个网络 · 训练复杂", "models": "InstructGPT · ChatGPT",
        },
        {
            "title": "DPO", "sub": "两个网络", "year": "2023", "color": AMBER,
            "boxes": ["Policy Model（策略模型）", "Reference Model（参考模型）"],
            "tag": "2 个网络 · 训练简化", "models": "Zephyr · Llama 3",
            "insight": "砍掉独立的 Reward / Value Model",
        },
        {
            "title": "GRPO", "sub": "一个网络 + 组内归一化", "year": "2024", "color": ACCENT1,
            "boxes": ["Policy Model（策略模型）"],
            "tag": "1 个网络 · 极致简化", "models": "DeepSeek-R1 · Qwen 3",
            "insight": "组内互评 → 无需独立参考模型",
        },
    ]

    with open(os.path.join(OUT, "alignment-evolution.svg"), "w") as f:
        header(f, w, h, "对齐技术三阶段：RLHF → DPO → GRPO", "三年三次简化——减掉的不是功能，是有人发现了更简洁的数学等价形式")
        decor_circles(f, [(900, 120, 160, ACCENT1), (200, 480, 140, ACCENT2)])

        # timeline
        f.write(f'<line x1="230" y1="90" x2="870" y2="90" stroke="{CARD_STROKE}" stroke-width="2"/>\n')
        for cx_t, label, c in [(230, "2022", "#a3acb9"), (550, "2023", AMBER), (870, "2024", ACCENT1)]:
            f.write(f'<circle cx="{cx_t}" cy="90" r="4" fill="{c}"/>\n')
            f.write(f'<text x="{cx_t}" y="82" text-anchor="middle" font-size="9" font-weight="600" fill="{c}">{label}</text>\n')

        # evolution arrows
        f.write(f'<line x1="370" y1="280" x2="392" y2="280" stroke="{ACCENT1}" stroke-width="1.5" marker-end="url(#ma)"/>\n')
        f.write(f'<text x="381" y="270" text-anchor="middle" font-size="8" font-weight="600" fill="{ACCENT1}">数学等价重构</text>\n')
        f.write(f'<line x1="700" y1="280" x2="722" y2="280" stroke="{ACCENT1}" stroke-width="1.5" marker-end="url(#ma)"/>\n')
        f.write(f'<text x="711" y="270" text-anchor="middle" font-size="8" font-weight="600" fill="{ACCENT1}">进一步化简</text>\n')

        # columns
        for i, col in enumerate(cols):
            cx = 60 + i * 350
            is_last = (i == 2)
            stroke = ACCENT1 if is_last else CARD_STROKE
            shadow = "as" if is_last else "s"
            header_fill = "url(#acc)" if is_last else ("#ede9fe" if i == 1 else "#f1f5f9")

            f.write(f'<rect x="{cx}" y="110" width="280" height="320" rx="10" fill="{CARD_FILL}" stroke="{stroke}" stroke-width="{"1.5" if is_last else "1"}" filter="url(#{shadow})"/>\n')
            f.write(f'<rect x="{cx}" y="110" width="280" height="38" rx="10" fill="{header_fill}"/>\n')
            f.write(f'<rect x="{cx}" y="138" width="280" height="10" fill="{header_fill}"/>\n')
            tfill = "#ffffff" if is_last else TEXT_DARK
            f.write(f'<text x="{cx+140}" y="135" text-anchor="middle" font-size="14" font-weight="700" fill="{tfill}">{col["title"]}</text>\n')
            f.write(f'<text x="{cx+140}" y="166" text-anchor="middle" font-size="10" fill="{TEXT_MUTED}">{col["sub"]}</text>\n')

            # insight pill if present
            if "insight" in col:
                ic = GREEN if is_last else AMBER
                ibg = "#ecfdf5" if is_last else "#fef3c7"
                f.write(f'<rect x="{cx+20}" y="182" width="240" height="22" rx="5" fill="{ibg}" opacity="0.6"/>\n')
                f.write(f'<text x="{cx+140}" y="197" text-anchor="middle" font-size="9" font-weight="600" fill="{ic}">{col["insight"]}</text>\n')
                box_start = 216
            else:
                box_start = 192

            # boxes
            n_boxes = len(col["boxes"])
            for j, box_text in enumerate(col["boxes"]):
                by = box_start + j * 48
                box_fill = "url(#acc)" if (is_last and j == 0) else "#f8fafd"
                box_stroke = ACCENT1 if (is_last and j == 0) else "#e2e8f0"
                box_text_color = "#ffffff" if (is_last and j == 0) else TEXT_DARK
                f.write(f'<rect x="{cx+20}" y="{by}" width="240" height="40" rx="6" fill="{box_fill}" stroke="{box_stroke}" stroke-width="0.8"/>\n')
                f.write(f'<text x="{cx+32}" y="{by+22}" font-size="11" font-weight="600" fill="{box_text_color}">{box_text}</text>\n')

            # models
            f.write(f'<text x="{cx+140}" y="{300}" text-anchor="middle" font-size="9" fill="{TEXT_MUTED}">代表模型: {col["models"]}</text>\n')

            # tag
            tag_fill = "url(#acc)" if is_last else ("#ede9fe" if i == 1 else "#f1f5f9")
            tag_color = "#ffffff" if is_last else ("#7c3aed" if i == 1 else "#64748b")
            f.write(f'<rect x="{cx+70}" y="312" width="140" height="20" rx="10" fill="{tag_fill}"/>\n')
            f.write(f'<text x="{cx+140}" y="326" text-anchor="middle" font-size="9" font-weight="600" fill="{tag_color}">{col["tag"]}</text>\n')

        # bottom insight
        f.write(f'<rect x="220" y="460" width="660" height="32" rx="8" fill="{ACCENT1}" opacity="0.08"/>\n')
        f.write(f'<text x="550" y="481" text-anchor="middle" font-size="11" font-weight="600" fill="{ACCENT1}">每一步减掉的不是功能——有人发现了更简洁的数学等价形式</text>\n')

        legend(f, 60, 520, [
            ("#a3acb9", False, "上一代方案"),
            (ACCENT1, False, "当前方案"),
        ])
        footer(f)

# ═══════════════════════════════════════════════════════════════
# Diagram 5: Architecture Evolution
# ═══════════════════════════════════════════════════════════════
def diagram_5():
    w, h = 1100, 620
    stages = [
        ("GPT-2", "Dense + MHA", "2019", "#a3acb9", ["1.5B 参数", "全部参数每次激活", "KV Cache = O(N×L)"]),
        ("GPT-3 / GPT-4", "Dense + MHA（同架构）", "2020-23", "#a3acb9", ["175B → ~1.8T 参数", "规模扩大 100-1000×", "KV Cache 成为瓶颈"]),
        ("Llama 3 / Mixtral", "GQA · MoE", "2024", AMBER, ["GQA: KV Cache ↓75%", "MoE: 671B 参，激活~6%", "知识容量↑ 推理成本↓"]),
        ("DeepSeek-V3", "MoE + MLA", "2024-25", ACCENT1, ["MLA: KV Cache 进一步压缩", "671B 总参 · 37B 活跃", "极致推理效率"]),
    ]
    sw = 220  # stage card width

    with open(os.path.join(OUT, "architecture-evolution.svg"), "w") as f:
        header(f, w, h, "架构演进：推理成本如何重塑模型设计", "从 GPT-2 的 Dense+MHA 到 DeepSeek-V3 的 MoE+MLA——驱动力不是「更强」，是「能在硬件上跑」")
        decor_circles(f, [(900, 120, 150, ACCENT1), (200, 520, 130, ACCENT2)])

        # timeline
        f.write(f'<line x1="160" y1="94" x2="960" y2="94" stroke="{CARD_STROKE}" stroke-width="2"/>\n')
        for sx in [160, 380, 660, 960]:
            f.write(f'<circle cx="{sx}" cy="94" r="4" fill="#a3acb9"/>\n')

        # stage cards
        stage_x = [40, 310, 580, 870]
        for i, (name, arch, year, scolor, details) in enumerate(stages):
            sx = stage_x[i]
            is_last = (i == 3)
            stroke = ACCENT1 if is_last else CARD_STROKE
            sw_stroke = "1.5" if is_last else "1"
            shadow = "as" if is_last else "s"
            header_fill = "url(#acc)" if is_last else ("#ede9fe" if i == 2 else "#f1f5f9")

            f.write(f'<rect x="{sx}" y="112" width="220" height="200" rx="9" fill="{CARD_FILL}" stroke="{stroke}" stroke-width="{sw_stroke}" filter="url(#{shadow})"/>\n')
            f.write(f'<rect x="{sx}" y="112" width="220" height="36" rx="9" fill="{header_fill}"/>\n')
            f.write(f'<rect x="{sx}" y="138" width="220" height="10" fill="{header_fill}"/>\n')
            tfill = "#ffffff" if is_last else TEXT_DARK
            f.write(f'<text x="{sx+110}" y="136" text-anchor="middle" font-size="13" font-weight="600" fill="{tfill}">{name}</text>\n')
            f.write(f'<text x="{sx+110}" y="168" font-size="10" fill="{TEXT_MUTED}" text-anchor="middle">{arch}</text>\n')

            for j, detail in enumerate(details):
                dc = GREEN if (i >= 2 and j == 0) else (RED if (i == 1 and j == 2) else TEXT_DARK)
                f.write(f'<text x="{sx+110}" y="{192+j*18}" font-size="9" fill="{dc}" text-anchor="middle">{detail}</text>\n')

            # evolution arrows between stages
            if i < 3:
                ax = stage_x[i] + 220
                f.write(f'<line x1="{ax}" y1="212" x2="{ax+50}" y2="212" stroke="{ACCENT1}" stroke-width="1.5" marker-end="url(#ma)"/>\n')
                if i == 1:
                    f.write(f'<text x="{ax+25}" y="204" text-anchor="middle" font-size="8" font-weight="700" fill="{ACCENT1}">推理成本倒逼</text>\n')

        # Comparison table
        ty = 340
        f.write(f'<text x="550" y="{ty}" text-anchor="middle" font-size="12" font-weight="700" fill="{TEXT_DARK}">四代推理性能对比</text>\n')
        col_hdrs = ["指标", "GPT-2 (MHA)", "GPT-4 (MHA)", "Llama 3 (GQA)", "DeepSeek-V3 (MLA)"]
        col_colors = ["#f1f5f9", "#f1f5f9", "#f1f5f9", "#ede9fe", "url(#acc)"]
        col_x = [80, 248, 416, 584, 752]

        for j, (hdr, cc) in enumerate(zip(col_hdrs, col_colors)):
            fill = cc if cc.startswith("url") else cc
            tcol = "#ffffff" if j == 4 else TEXT_MUTED
            f.write(f'<rect x="{col_x[j]}" y="{ty+20}" width="160" height="30" rx="4" fill="{fill}"/>\n')
            f.write(f'<text x="{col_x[j]+80}" y="{ty+39}" text-anchor="middle" font-size="10" font-weight="600" fill="{tcol}">{hdr}</text>\n')

        rows = [
            ("KV Cache / token", ["1×（基线）", "~100×", "~0.25×", "≪ 0.25×"], [TEXT_MUTED, RED, GREEN, ACCENT1]),
            ("激活参数比例", ["100%", "100%", "~6%", "~6%"], [TEXT_MUTED, RED, GREEN, ACCENT1]),
            ("推理成本", ["很低", "极高", "低", "很低"], [GREEN, RED, GREEN, ACCENT1]),
        ]
        for ri, (rname, values, colors) in enumerate(rows):
            ry = ty + 54 + ri * 32
            bg = "#f8fafd" if ri % 2 == 0 else CARD_FILL
            f.write(f'<rect x="{col_x[0]}" y="{ry}" width="160" height="30" fill="{bg}"/>\n')
            f.write(f'<text x="{col_x[0]+80}" y="{ry+20}" text-anchor="middle" font-size="10" font-weight="500" fill="{TEXT_DARK}">{rname}</text>\n')
            for j, (val, vc) in enumerate(zip(values, colors)):
                f.write(f'<rect x="{col_x[j+1]}" y="{ry}" width="160" height="30" fill="{bg}"/>\n')
                f.write(f'<text x="{col_x[j+1]+80}" y="{ry+20}" text-anchor="middle" font-size="10" font-weight="600" fill="{vc}">{val}</text>\n')

        insight_bar(f, 640, 492, "共同方向不是「更强」——是能在现有 GPU 上跑得动。效果是副产品，推理可行性才是主驱动。")
        legend(f, 880, 548, [
            ("#a3acb9", False, "传统架构"),
            (ACCENT1, False, "推理优化"),
        ])
        footer(f)

# ═══════════════════════════════════════════════════════════════
# Diagram 6: Economics Loop
# ═══════════════════════════════════════════════════════════════
def diagram_6():
    w, h = 880, 600
    with open(os.path.join(OUT, "economics-loop.svg"), "w") as f:
        header(f, w, h, "经济回路：推理成本如何反向重塑架构", "训练是一次性投入，推理是永续成本——数月推理成本即超训练，谁占大头谁主导方向")
        decor_circles(f, [(720, 120, 150, ACCENT1), (160, 500, 140, ACCENT2)])

        # Top half: cost comparison - two cards side by side
        # Training cost card
        f.write(f'<rect x="40" y="88" width="360" height="190" rx="10" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
        f.write(f'<rect x="40" y="88" width="4" height="190" rx="2" fill="#a3acb9"/>\n')
        f.write(f'<text x="64" y="116" font-size="14" font-weight="700" fill="{TEXT_DARK}">训练成本</text>\n')
        f.write(f'<text x="64" y="134" font-size="9" fill="{TEXT_MUTED}">一次性投入 · 已经支付</text>\n')
        # cost bar
        f.write(f'<rect x="64" y="150" width="48" height="48" rx="8" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1"/>\n')
        f.write(f'<text x="88" y="180" text-anchor="middle" font-size="15" font-weight="700" fill="#64748b">$1亿</text>\n')
        # stats
        f.write(f'<text x="128" y="164" font-size="10" fill="{TEXT_DARK}">GPT-4 预训练</text>\n')
        f.write(f'<text x="128" y="182" font-size="9" fill="{TEXT_MUTED}">时长 3-6 个月 · GPU 数万张</text>\n')
        f.write(f'<text x="128" y="198" font-size="9" fill="{TEXT_MUTED}">占生命周期算力 95%</text>\n')
        # time bar
        f.write(f'<text x="64" y="246" font-size="9" fill="{TEXT_MUTED}">时间维度</text>\n')
        f.write(f'<rect x="64" y="252" width="316" height="14" rx="4" fill="#f1f5f9"/>\n')
        f.write(f'<rect x="64" y="252" width="64" height="14" rx="4" fill="#a3acb9" opacity="0.3"/>\n')
        f.write(f'<text x="96" y="262" text-anchor="middle" font-size="8" fill="#64748b">3-6 月</text>\n')
        f.write(f'<text x="140" y="262" font-size="8" fill="{TEXT_MUTED}">———— 之后不再产生 ————</text>\n')

        # Inference cost card
        f.write(f'<rect x="480" y="88" width="360" height="190" rx="10" fill="{CARD_FILL}" stroke="{CARD_STROKE}" stroke-width="1" filter="url(#s)"/>\n')
        f.write(f'<rect x="480" y="88" width="4" height="190" rx="2" fill="url(#acc)"/>\n')
        f.write(f'<text x="504" y="116" font-size="14" font-weight="700" fill="{TEXT_DARK}">推理成本</text>\n')
        f.write(f'<text x="504" y="134" font-size="9" font-weight="600" fill="{ACCENT1}">持续累积 · 永续增长</text>\n')
        # cost bar (growing)
        f.write(f'<rect x="504" y="150" width="140" height="48" rx="8" fill="{ACCENT1}" opacity="0.1" stroke="{ACCENT1}" stroke-width="1"/>\n')
        f.write(f'<text x="574" y="180" text-anchor="middle" font-size="15" font-weight="700" fill="{ACCENT1}">∞</text>\n')
        # stats
        f.write(f'<text x="660" y="164" font-size="10" fill="{TEXT_DARK}">ChatGPT 日常服务</text>\n')
        f.write(f'<text x="660" y="182" font-size="9" fill="{TEXT_MUTED}">每日数亿次请求</text>\n')
        f.write(f'<text x="660" y="198" font-size="9" fill="{TEXT_MUTED}">瓶颈: 参数搬运 + KV Cache</text>\n')
        # time bar
        f.write(f'<text x="504" y="246" font-size="9" fill="{TEXT_MUTED}">时间维度</text>\n')
        f.write(f'<rect x="504" y="252" width="316" height="14" rx="4" fill="#f1f5f9"/>\n')
        f.write(f'<rect x="504" y="252" width="316" height="14" rx="4" fill="{ACCENT1}" opacity="0.12"/>\n')
        f.write(f'<text x="662" y="262" text-anchor="middle" font-size="8" font-weight="600" fill="{ACCENT1}">持续增长 · 没有终点</text>\n')

        # crossover arrow
        f.write(f'<line x1="412" y1="184" x2="468" y2="184" stroke="{ACCENT1}" stroke-width="1.5" marker-end="url(#ma)"/>\n')
        f.write(f'<text x="440" y="176" text-anchor="middle" font-size="8" font-weight="600" fill="{ACCENT1}">数月后</text>\n')

        f.write(f'<text x="440" y="302" text-anchor="middle" font-size="12" font-weight="700" fill="{ACCENT1}">数月推理成本 ≈ 一次训练成本 → 此后推理持续超训练</text>\n')

        # Divider
        f.write(f'<line x1="80" y1="320" x2="800" y2="320" stroke="{CARD_STROKE}" stroke-width="1"/>\n')
        f.write(f'<text x="440" y="346" text-anchor="middle" font-size="13" font-weight="700" fill="{TEXT_DARK}">推理成本驱动的架构创新回路</text>\n')

        # Three nodes: bottleneck → innovation → cost reduction → (loop)
        nodes_eco = [
            (40, 370, RED, "#fef2f2", "推理瓶颈", ["KV Cache 太大", "显存放不下", "搬运时间 >> 计算时间"]),
            (330, 370, ACCENT1, "#ede9fe", "架构创新", ["GQA → Cache 砍 75%", "MoE → 只激活 ~6%", "MLA → 缓存进一步压缩"]),
            (620, 370, GREEN, "#ecfdf5", "推理成本下降", ["每 token 成本降低", "服务更多用户", "用户量增长 → 新瓶颈"]),
        ]
        for nx, ny, nc, nbg, ntitle, nitems in nodes_eco:
            f.write(f'<rect x="{nx}" y="{ny}" width="220" height="96" rx="9" fill="{CARD_FILL}" stroke="{nc}" stroke-width="1" filter="url(#s)"/>\n')
            f.write(f'<rect x="{nx}" y="{ny}" width="220" height="28" rx="9" fill="{nbg}"/>\n')
            f.write(f'<rect x="{nx}" y="{ny+18}" width="220" height="10" fill="{nbg}"/>\n')
            f.write(f'<text x="{nx+110}" y="{ny+19}" text-anchor="middle" font-size="11" font-weight="600" fill="{nc}">{ntitle}</text>\n')
            for j, item in enumerate(nitems):
                f.write(f'<text x="{nx+16}" y="{ny+48+j*16}" font-size="9" fill="{TEXT_DARK}">{item}</text>\n')

        # Arrows: bottleneck → innovation → cost
        f.write(f'<line x1="260" y1="412" x2="316" y2="412" stroke="{RED}" stroke-width="1.2" marker-end="url(#me)"/>\n')
        f.write(f'<text x="288" y="404" font-size="8" font-weight="600" fill="{RED}">倒逼</text>\n')
        f.write(f'<line x1="550" y1="412" x2="606" y2="412" stroke="{GREEN}" stroke-width="1.2" marker-end="url(#md)"/>\n')
        f.write(f'<text x="578" y="404" font-size="8" font-weight="600" fill="{GREEN}">降低</text>\n')

        # Feedback loop back
        f.write(f'<path d="M730,466 L730,490 Q730,500 720,504 L440,504 Q428,504 416,500 L150,490 Q138,486 138,472 L138,466" fill="none" stroke="{PURPLE}" stroke-width="0.8" stroke-dasharray="6,4" marker-end="url(#me)"/>\n')
        f.write(f'<text x="440" y="520" text-anchor="middle" font-size="8" font-weight="600" fill="{PURPLE}">用户量增长 → 新一轮瓶颈 → 新一轮创新</text>\n')

        f.write(f'<rect x="140" y="550" width="600" height="24" rx="6" fill="url(#acc)" opacity="0.07"/>\n')
        f.write(f'<text x="440" y="567" text-anchor="middle" font-size="10" font-weight="600" fill="{ACCENT1}">驱动力重心：训练成本 → 推理成本。谁占总成本更多，谁主导技术方向。</text>\n')
        footer(f)


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    diagram_1()
    diagram_2()
    diagram_3()
    diagram_4()
    diagram_5()
    diagram_6()
    print("All 6 SVGs generated.")
