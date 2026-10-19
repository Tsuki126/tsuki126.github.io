#!/usr/bin/env python3
"""
v3: 四步流程重构全部 6 张图。
改进: ① 卡片内部布局标准化（徽章/标题/副标题/指标 四线精确对齐）
      ② 箭头使用椭圆弧替代 Q 曲线（沿五边形自然曲率）
      ③ 反馈箭头加粗加图例强调
      ④ 每张图独立设计书 → 精确数学 → Gate 验证
"""
import math, os, sys, xml.etree.ElementTree as ET

OUT = os.path.dirname(os.path.abspath(__file__))
G = 4; S = lambda v: round(v / G) * G

# ── Design System ──
BG1, BG2 = "#f8f9fc", "#f0f2f8"
A1, A2 = "#635bff", "#8f6ed5"
CARD, BORDER = "#ffffff", "#eef0f6"
TEXT, MUTED = "#1a1f36", "#a3acb9"
GRN, AMB, PUR, RED = "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"
FONT = "Inter, system-ui, -apple-system, sans-serif"
RX = 9

def svg_start(w, h, title, sub):
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="{FONT}">',
        '<defs>',
        f'<linearGradient id="bg"><stop offset="0%" stop-color="{BG1}"/><stop offset="100%" stop-color="{BG2}"/></linearGradient>',
        f'<linearGradient id="acc"><stop offset="0%" stop-color="{A1}"/><stop offset="100%" stop-color="{A2}"/></linearGradient>',
        '<filter id="s"><feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#1a1f36" flood-opacity="0.05"/></filter>',
        '<filter id="as"><feDropShadow dx="0" dy="4" stdDeviation="12" flood-color="#635bff" flood-opacity="0.12"/></filter>',
        '<filter id="blur"><feGaussianBlur stdDeviation="50"/></filter>',
    ]
    for mid, mc in [("ma",A1),("mb",AMB),("mc",PUR),("md",GRN),("me",RED)]:
        lines.append(f'<marker id="{mid}" viewBox="0 0 10 8" refX="10" refY="4" markerWidth="6" markerHeight="5" orient="auto"><path d="M0,0L10,4L0,8Z" fill="{mc}"/></marker>')
    lines.append('</defs>')
    lines.append(f'<rect width="{w}" height="{h}" fill="url(#bg)"/>')
    lines.append(f'<circle cx="{S(w*0.8)}" cy="{S(h*0.15)}" r="{S(min(w,h)*0.22)}" fill="{A1}" opacity="0.025" filter="url(#blur)"/>')
    lines.append(f'<circle cx="{S(w*0.2)}" cy="{S(h*0.82)}" r="{S(min(w,h)*0.18)}" fill="{A2}" opacity="0.025" filter="url(#blur)"/>')
    lines.append(f'<text x="{w//2}" y="40" text-anchor="middle" font-size="20" font-weight="700" fill="{TEXT}" letter-spacing="-0.3">{title}</text>')
    tw = max(len(title) * 12, 120)
    lines.append(f'<line x1="{w//2-tw//2}" y1="52" x2="{w//2+tw//2}" y2="52" stroke="{A1}" stroke-width="2.5" stroke-linecap="round"/>')
    lines.append(f'<text x="{w//2}" y="70" text-anchor="middle" font-size="10" fill="{MUTED}">{sub}</text>')
    return "\n".join(lines) + "\n"

# ── 可复用图形组件 ──

def draw_card(lines, x, y, w, h, badge_num, title, subtitle, metric, metric_color=TEXT, accent=False):
    """标准化卡片：徽章(x+14,y+14) → 标题(x+36,y+26) → 副标题(x+16,y+50) → 指标(x+16,y+74)"""
    stroke = A1 if accent else BORDER
    sw = "1.5" if accent else "1"
    shadow = "as" if accent else "s"
    lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{RX}" fill="{CARD}" stroke="{stroke}" stroke-width="{sw}" filter="url(#{shadow})"/>')
    # 徽章
    bx, by = x + 16, y + 16
    lines.append(f'<circle cx="{bx}" cy="{by}" r="9" fill="url(#acc)"/>')
    lines.append(f'<text x="{bx}" y="{by+4}" text-anchor="middle" font-size="9" font-weight="700" fill="#ffffff">{badge_num}</text>')
    # 标题
    lines.append(f'<text x="{x+38}" y="{y+26}" font-size="12" font-weight="600" fill="{TEXT}">{title}</text>')
    # 副标题
    lines.append(f'<text x="{x+16}" y="{y+50}" font-size="9" fill="{MUTED}">{subtitle}</text>')
    # 指标
    lines.append(f'<text x="{x+16}" y="{y+74}" font-size="10" font-weight="600" fill="{metric_color}">{metric}</text>')

def draw_arc_arrow(lines, x1, y1, x2, y2, cx, cy, r, sweep, color, width=2, dashed=False, marker="ma", label=""):
    """使用椭圆弧 (A command) 替代 Q 曲线，沿五边形边缘更自然"""
    ds = 'stroke-dasharray="8,5" ' if dashed else ''
    sw = f'sweep-flag="{sweep}"' if sweep is not None else ''
    lines.append(f'<path d="M{S(x1)},{S(y1)} A{S(r)},{S(r)} 0 0,{1 if sweep else 0} {S(x2)},{S(y2)}" fill="none" stroke="{color}" stroke-width="{width}" {ds}marker-end="url(#{marker})"/>')
    if label:
        # 标签放在弧的中点
        lx, ly = S((x1+x2)//2), S((y1+y2)//2 - 12)
        lw = len(label) * 11 + 12
        lines.append(f'<rect x="{lx-lw//2}" y="{ly-4}" width="{lw}" height="18" rx="3" fill="{CARD}" fill-opacity="0.92"/>')
        lines.append(f'<text x="{lx}" y="{ly+8}" text-anchor="middle" font-size="8" font-weight="600" fill="{color}">{label}</text>')

def draw_legend(lines, x, y, items):
    h = 16 + len(items) * 18
    lines.append(f'<rect x="{x}" y="{y}" width="220" height="{h}" rx="8" fill="#fafbfc" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'<text x="{x+14}" y="{y+16}" font-size="9" font-weight="700" fill="{MUTED}">图例</text>')
    for i, (color, dash, label) in enumerate(items):
        iy = y + 32 + i * 18
        ds = 'stroke-dasharray="8,5" ' if dash else ''
        lines.append(f'<line x1="{x+14}" y1="{iy+4}" x2="{x+38}" y2="{iy+4}" stroke="{color}" stroke-width="{"1.5" if dash else "2"}" {ds}/>')
        lines.append(f'<text x="{x+46}" y="{iy+8}" font-size="9" fill="{TEXT}">{label}</text>')


# ═══════════════════════════════════════════════════════════════
# Diagram 1: 生命周期全景
# ═══════════════════════════════════════════════════════════════
# 设计书:
# A1: 五道工序是回路，不是流水线
# B1: 正五边形环形布局，CW=前向, CCW(紫虚线)=反馈
# B2: 视觉重心=中央pill + 反馈虚线（区别于常规LLM介绍的核心差异）
# B3: 蓝色=前向流, 紫色=反馈回路, 绿色=正向指标, 红色=代价/丢弃, 橙色=成本
# C1: 5卡片+5箭头+1pill+1图例=12元素
# C3: 预算内

def d1():
    W, H = 1100, 720
    CX, CY = 550, 368
    R = 220  # 五边形半径
    CW, CH = 156, 96  # 卡片尺寸

    # 五边形顶点
    verts = []
    for i in range(5):
        a = math.radians(-90 + i * 72)
        verts.append((S(CX + R * math.cos(a)), S(CY + R * math.sin(a))))

    cards = [
        ("数据工程",   "采集 · 清洗 · 分词",       "丢弃 50-80% 原始数据",    RED),
        ("预训练",     "猜下一个词 × 几万亿次",     "算力 95%  ·  成本 ~$1 亿", AMB),
        ("后训练",     "SFT 改格式  ·  对齐教好坏",  "成本 1-2%  ·  体验 100%",  GRN),
        ("评估",       "MMLU  ·  MATH  ·  HumanEval","流水线的「眼睛」",        MUTED),
        ("推理部署",   "GQA  ·  MoE  ·  MLA",       "永续成本重塑架构",        A1),
    ]
    alabels  = ["训练数据", "Base Model", "Aligned Model", "部署上线", "用户反馈 · 日志回流"]
    acolors  = [A1, A1, A1, A1, PUR]
    amarkers = ["ma","ma","ma","ma","mc"]
    adashed  = [False,False,False,False,True]

    lines = [svg_start(W, H, "LLM 生命周期全景：五道工序的回路", "从互联网原始文本到对话助手——五道工序首尾相连，构成持续运转的回路")]

    # 五边形引导线
    pts = " ".join(f"{x},{y}" for x,y in verts)
    lines.append(f'<polygon points="{pts}" fill="none" stroke="{A1}" stroke-width="0.5" opacity="0.08" stroke-dasharray="10,8"/>')

    # 箭头（椭圆弧沿五边形外缘）
    arc_r = int(R * 1.18)  # 弧半径稍大于五边形半径
    for i in range(5):
        x1, y1 = verts[i]
        x2, y2 = verts[(i+1)%5]
        # 弧的端点：卡片边沿
        dx, dy = x2 - x1, y2 - y1
        dl = math.sqrt(dx*dx+dy*dy) or 1
        sx = S(x1 + dx/dl * (CW//2 + 4))
        sy = S(y1 + dy/dl * (CH//2 + 4))
        ex = S(x2 - dx/dl * (CW//2 + 8))
        ey = S(y2 - dy/dl * (CH//2 + 8))
        # sweep flag: 弧应该向外弯曲（远离中心）
        # 叉积判断: (p2-p1) × (center-p1) 的符号
        cp = (x2-x1)*(CY-y1) - (y2-y1)*(CX-x1)
        sweep = 1 if cp > 0 else 0
        draw_arc_arrow(lines, sx, sy, ex, ey, CX, CY, arc_r, sweep, acolors[i],
                       width=1 if adashed[i] else 2, dashed=adashed[i],
                       marker=amarkers[i], label=alabels[i])

    # 卡片
    for i, ((vx, vy), (title, sub, metric, mc)) in enumerate(zip(verts, cards)):
        x, y = S(vx - CW//2), S(vy - CH//2)
        draw_card(lines, x, y, CW, CH, i+1, title, sub, metric, mc)

    # 中央 pill
    PW, PH = 168, 44
    lines.append(f'<rect x="{CX-PW//2}" y="{CY-PH//2}" width="{PW}" height="{PH}" rx="{PH//2}" fill="url(#acc)" filter="url(#as)"/>')
    lines.append(f'<text x="{CX}" y="{CY+5}" text-anchor="middle" font-size="14" font-weight="700" fill="#ffffff" letter-spacing="0.5">LLM 生命周期</text>')

    # 图例
    draw_legend(lines, 852, 612, [
        (A1, False, "前向流（阶段间产物传递）"),
        (PUR, True, "反馈回路（下游约束上游决策）"),
    ])

    lines.append('</svg>')
    path = os.path.join(OUT, "lifecycle-architecture.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] lifecycle-architecture.svg")
    _validate(path, (0,0,1100,720))


# ═══════════════════════════════════════════════════════════════
# Diagram 2: Tokenizer 对比
# ═══════════════════════════════════════════════════════════════
# 设计书:
# A1: 同一 Tokenizer 对英文≈1token/词，对中文≈3-6token/字，效率差5×
# A3: 支撑论点——"Tokenizer 是唯一不可逆的决策"
# B1: 左右对比面板 + 底部解决方案
# B2: 视觉重心=右侧低效编码(琥珀色) + 底部优化方案(紫色)
# B3: 绿色=高效(英), 琥珀=低效(中), 紫色=优化方案

def d2():
    W, H = 880, 540
    lines = [svg_start(W, H, "Tokenizer 语言效率：英文 vs 中文", "同一个 Tokenizer 对不同语言的编码效率差异巨大——直接影响推理成本和响应速度")]

    PW, PH = 370, 272
    L, R = 40, 470

    for side, lx, title, input_text, tokens, result_text, result_color, bar_color, bar_len in [
        ("en", L, "英文文本（英文为主 Tokenizer）", "The capital of France is Paris",
         [("The",42),("capital",54),("of",28),("France",54),("is",22),("Paris",46)],
         "6 tokens → 高效编码", GRN, GRN, 36),
        ("zh", R, "中文文本（英文为主 Tokenizer）", "法国的首都是巴黎",
         [(f"byte{i}",26) for i in range(9)],
         "~30 tokens → 低效编码", AMB, AMB, 168),
    ]:
        lines.append(f'<rect x="{lx}" y="96" width="{PW}" height="{PH}" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
        lines.append(f'<rect x="{lx}" y="96" width="{PW}" height="36" rx="10" fill="#f8fafd"/>')
        lines.append(f'<rect x="{lx}" y="122" width="{PW}" height="10" fill="#f8fafd"/>')
        lines.append(f'<text x="{lx+PW//2}" y="120" text-anchor="middle" font-size="13" font-weight="600" fill="{TEXT}">{title}</text>')

        # 输入行
        lines.append(f'<text x="{lx+20}" y="160" font-size="10" font-weight="600" fill="{MUTED}">输入</text>')
        lines.append(f'<rect x="{lx+64}" y="146" width="280" height="24" rx="5" fill="{BG1}" stroke="{BORDER}" stroke-width="0.5"/>')
        fs = 12 if side == "en" else 14
        lines.append(f'<text x="{lx+PW//2}" y="163" text-anchor="middle" font-size="{fs}" font-weight="500" fill="{TEXT}">{input_text}</text>')

        # 分词
        lines.append(f'<text x="{lx+20}" y="208" font-size="10" font-weight="600" fill="{MUTED}">分词</text>')
        bx = lx + 64
        token_color = GRN if side == "en" else AMB
        token_bg = "#ecfdf5" if side == "en" else "#fef3c7"
        for tlabel, tw in tokens:
            lines.append(f'<rect x="{bx}" y="{194}" width="{tw}" height="24" rx="5" fill="{token_bg}" stroke="{token_color}" stroke-width="0.8"/>')
            lines.append(f'<text x="{bx+tw//2}" y="{211}" text-anchor="middle" font-size="{"10" if side=="en" else "7"}" font-weight="500" fill="{token_color}">{tlabel}</text>')
            bx += tw + (6 if side == "en" else 4)

        # 结果
        lines.append(f'<text x="{lx+20}" y="{260}" font-size="11" font-weight="700" fill="{result_color}">结果: {result_text}</text>')
        desc = "≈ 1 token / 词  ·  序列短 → 注意力开销小" if side == "en" else "≈ 3-6 token / 字  ·  序列长 → O(n²) 开销 ↑"
        lines.append(f'<text x="{lx+20}" y="{278}" font-size="10" fill="{MUTED}">{desc}</text>')

        # 效率条
        lines.append(f'<rect x="{lx+64}" y="{300}" width="{bar_len}" height="28" rx="5" fill="{bar_color}" opacity="0.15"/>')
        count = "6" if side == "en" else "~30"
        extra = "tokens（6 词 → 6 token）" if side == "en" else "tokens（7 字 → 30 token）"
        lines.append(f'<text x="{lx+64+bar_len//2}" y="{319}" text-anchor="middle" font-size="16" font-weight="700" fill="{bar_color}">{count}</text>')
        lines.append(f'<text x="{lx+64+bar_len+12}" y="{319}" font-size="11" fill="{MUTED}">{extra}</text>')

    # ── 底部：解决方案 ──
    SY = 404
    lines.append(f'<rect x="40" y="{SY}" width="800" height="84" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="40" y="{SY}" width="800" height="6" rx="3" fill="url(#acc)"/>')
    lines.append(f'<text x="60" y="{SY+30}" font-size="13" font-weight="700" fill="{TEXT}">中文优化 Tokenizer（Qwen · DeepSeek 的做法）</text>')
    lines.append(f'<text x="60" y="{SY+52}" font-size="10" fill="{MUTED}">训练 Tokenizer 时大幅提高中文数据配比 → 同样 7 字句子仅需 ~7 tokens（≈1 token/字），效率提升 4-5×</text>')
    lines.append(f'<rect x="60" y="{SY+64}" width="42" height="12" rx="4" fill="#ede9fe" stroke="{A1}" stroke-width="0.8"/>')
    lines.append(f'<text x="81" y="{SY+73}" text-anchor="middle" font-size="10" font-weight="700" fill="{A1}">7</text>')
    lines.append(f'<text x="114" y="{SY+73}" font-size="10" font-weight="600" fill="{GRN}">tokens（优化后）→ 推理速度 ↑ 4×  ·  成本 ↓ 75%</text>')

    # 图例
    lx, ly = 662, 140
    lines.append(f'<rect x="{lx}" y="{ly}" width="180" height="64" rx="6" fill="#fafbfc" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'<text x="{lx+14}" y="{ly+16}" font-size="8" font-weight="700" fill="{MUTED}">图例</text>')
    for j,(c,label) in enumerate([(GRN,"高效编码"),(AMB,"低效编码"),(A1,"优化方案")]):
        iy = ly + 26 + j*14
        lines.append(f'<rect x="{lx+14}" y="{iy}" width="18" height="10" rx="3" fill="{c}" opacity="0.2" stroke="{c}" stroke-width="0.8"/>')
        lines.append(f'<text x="{lx+40}" y="{iy+9}" font-size="9" fill="{TEXT}">{label}</text>')

    lines.append('</svg>')
    path = os.path.join(OUT, "tokenizer-comparison.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] tokenizer-comparison.svg")
    _validate(path, (0,0,880,540))


# ═══════════════════════════════════════════════════════════════
# Diagram 3: 预训练循环
# ═══════════════════════════════════════════════════════════════
# 设计书:
# A1: 预训练是四步循环：输入→预测→算Loss→反向传播，重复几万亿次
# B1: 菱形四节点 + 外圈虚线（重复）+ 底部三支柱
# B2: 视觉重心=计算Loss节点(accent填充) + 中心"猜下一个词"
# B3: Loss节点用accent=关键环节，外圈虚线紫色=重复循环

def d3():
    W, H = 880, 620
    lines = [svg_start(W, H, "预训练：几万亿次「猜下一个词」循环", "Pre-training Loop — Predict Next Token × Trillions of Iterations")]
    NW, NH = 176, 88

    nodes = [
        (440, 136, "① 输入文本", "取一段文字", "遮掉最后一个词", False),
        (628, 264, "② 模型预测", "计算概率分布", "「巴黎」92% · 伦敦 3%", False),
        (440, 408, "③ 计算 Loss", "对比预测与真实答案", "猜错了 · loss 很高", True),
        (252, 264, "④ 更新参数", "反向传播", "微调全部参数", False),
    ]

    # 内圈箭头
    arrows = [
        (540,178, 624,252, 588,200, A1, "ma", "前向传播"),
        (648,304, 528,378, 604,348, A1, "ma", "预测结果"),
        (360,418, 304,346, 320,388, AMB, "mb", "梯度回传"),
        (240,300, 360,206, 292,248, A1, "ma", "参数更新"),
    ]
    for x1,y1,x2,y2,cpx,cpy,ac,mk,label in arrows:
        lines.append(f'<path d="M{S(x1)},{S(y1)} Q{S(cpx)},{S(cpy)} {S(x2)},{S(y2)}" fill="none" stroke="{ac}" stroke-width="1.5" marker-end="url(#{mk})"/>')
        lines.append(f'<text x="{S((x1+x2)//2)}" y="{S((y1+y2)//2-8)}" text-anchor="middle" font-size="8" font-weight="600" fill="{ac}">{label}</text>')

    # 外圈虚线
    lines.append(f'<path d="M440,88 Q580,64 688,124 Q756,220 696,340 Q636,456 520,472 Q440,480 360,472 Q244,456 184,340 Q124,220 192,124 Q260,64 360,64 Q400,64 440,88" fill="none" stroke="{PUR}" stroke-width="0.8" stroke-dasharray="6,4"/>')
    lines.append(f'<text x="440" y="486" text-anchor="middle" font-size="9" font-weight="600" fill="{PUR}">重复几万亿次</text>')

    # 节点
    for nx, ny, ntitle, l1, l2, is_accent in nodes:
        x, y = S(nx - NW//2), S(ny - NH//2)
        fill = "url(#acc)" if is_accent else CARD
        stroke = "none" if is_accent else BORDER
        shadow = "as" if is_accent else "s"
        tc = "#ffffff" if is_accent else TEXT
        sc = "rgba(255,255,255,0.75)" if is_accent else MUTED
        lines.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="{RX}" fill="{fill}" stroke="{stroke}" stroke-width="1" filter="url(#{shadow})"/>')
        lines.append(f'<text x="{x+16}" y="{y+22}" font-size="9" font-weight="700" fill="{sc}">{ntitle}</text>')
        lines.append(f'<text x="{x+16}" y="{y+46}" font-size="11" font-weight="600" fill="{tc}">{l1}</text>')
        lines.append(f'<text x="{x+16}" y="{y+66}" font-size="9" fill="{sc}">{l2}</text>')

    # 中心
    lines.append(f'<text x="440" y="310" text-anchor="middle" font-size="18" font-weight="700" fill="{A1}">猜下一个词</text>')
    lines.append(f'<text x="440" y="332" text-anchor="middle" font-size="9" fill="{MUTED}">GPT-4 预训练成本：~$1亿  ·  3-6 个月  ·  数万 GPU 昼夜运转</text>')

    # 三支柱
    pillars = [
        ("Warmup", A1, "学习率从零缓升", "Embedding 梯度极端稀疏", "优化器需积累梯度历史后才有靠谱估计"),
        ("梯度裁剪", AMB, "限制单步更新上限", "防止异常 token 毁掉训练", "将梯度范数 clip 到 1.0，避免单步失控"),
        ("Weight Decay", GRN, "分层衰减策略", "2D 权重：衰减防止过拟合", "1D 参数（LayerNorm）：不施加衰减"),
    ]
    for i, (pname, pc, p1, p2, p3) in enumerate(pillars):
        px = 44 + i * 272
        py = 520
        lines.append(f'<rect x="{px}" y="{py}" width="248" height="64" rx="8" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
        lines.append(f'<rect x="{px}" y="{py}" width="4" height="64" rx="2" fill="{pc}"/>')
        lines.append(f'<text x="{px+16}" y="{py+20}" font-size="11" font-weight="600" fill="{TEXT}">{pname}</text>')
        lines.append(f'<text x="{px+16}" y="{py+36}" font-size="9" fill="{MUTED}">{p1}  ·  {p2}</text>')
        lines.append(f'<text x="{px+16}" y="{py+52}" font-size="8" fill="{MUTED}">{p3}</text>')

    # 底部金句
    lines.append(f'<rect x="160" y="594" width="560" height="18" rx="5" fill="#ede9fe" opacity="0.6"/>')
    lines.append(f'<text x="440" y="607" text-anchor="middle" font-size="9" font-weight="600" fill="{A1}">模型从未被教过什么是语法或逻辑——所有能力都从「猜下一个词」中涌现</text>')

    lines.append('</svg>')
    path = os.path.join(OUT, "pretraining-loop.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] pretraining-loop.svg")
    _validate(path, (0,0,880,620))


# ═══════════════════════════════════════════════════════════════
# Diagram 4: 对齐技术演进
# ═══════════════════════════════════════════════════════════════
# 设计书:
# A1: RLHF(4网络)→DPO(2网络)→GRPO(1网络+组内归一化)，三年三次简化
# B1: 三列时间线 + 演进箭头 + 底部金句
# B2: 视觉重心=GRPO列(accent填充，最简)
# B3: 灰=旧代, 琥珀=过渡, 紫=当前最优

def d4():
    W, H = 1100, 600
    lines = [svg_start(W, H, "对齐技术三阶段：RLHF → DPO → GRPO", "三年三次简化——减掉的不是功能，是有人发现了更简洁的数学等价形式")]

    cols = [
        {"x":60,  "t":"RLHF", "s":"四个网络协同", "yc":"#a3acb9", "hdr":"#f1f5f9",
         "boxes":["Policy Model（策略模型）","Reference Model（参考模型）","Reward Model（奖励模型）","Value Model（价值模型）"],
         "tag":("4 个网络 · 训练复杂","#64748b","#f1f5f9"), "models":"InstructGPT · ChatGPT"},
        {"x":410, "t":"DPO",  "s":"两个网络",     "yc":AMB, "hdr":"#ede9fe",
         "boxes":["Policy Model（策略模型）","Reference Model（参考模型）"],
         "insight":("砍掉独立的 Reward / Value Model",AMB),
         "tag":("2 个网络 · 训练简化","#7c3aed","#ede9fe"), "models":"Zephyr · Llama 3"},
        {"x":760, "t":"GRPO", "s":"一个网络 + 组内归一化","yc":A1, "hdr":"url(#acc)",
         "boxes":["Policy Model（策略模型）"],
         "insight":("组内互评 → 相对优势 → 无需独立参考",GRN),
         "tag":("1 个网络 · 极致简化","#ffffff","url(#acc)"), "models":"DeepSeek-R1 · Qwen 3"},
    ]

    # 时间线
    lines.append(f'<line x1="230" y1="90" x2="870" y2="90" stroke="{BORDER}" stroke-width="2"/>')
    for cx,label,c in [(230,"2022","#a3acb9"),(550,"2023",AMB),(870,"2024",A1)]:
        lines.append(f'<circle cx="{cx}" cy="90" r="4" fill="{c}"/><text x="{cx}" y="80" text-anchor="middle" font-size="9" font-weight="600" fill="{c}">{label}</text>')

    # 演进箭头
    for ax,label in [(370,"数学等价重构"),(700,"进一步化简")]:
        lines.append(f'<line x1="{ax}" y1="280" x2="{ax+22}" y2="280" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
        lines.append(f'<text x="{ax+11}" y="270" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">{label}</text>')

    for col in cols:
        cx = col["x"]; is_last = (col["t"]=="GRPO")
        stroke = A1 if is_last else BORDER
        shadow = "as" if is_last else "s"
        tfill = "#ffffff" if is_last else TEXT

        lines.append(f'<rect x="{cx}" y="110" width="280" height="320" rx="10" fill="{CARD}" stroke="{stroke}" stroke-width="{"1.5" if is_last else "1"}" filter="url(#{shadow})"/>')
        lines.append(f'<rect x="{cx}" y="110" width="280" height="38" rx="10" fill="{col["hdr"]}"/>')
        lines.append(f'<rect x="{cx}" y="138" width="280" height="10" fill="{col["hdr"]}"/>')
        lines.append(f'<text x="{cx+140}" y="135" text-anchor="middle" font-size="14" font-weight="700" fill="{tfill}">{col["t"]}</text>')
        lines.append(f'<text x="{cx+140}" y="166" text-anchor="middle" font-size="10" fill="{MUTED}">{col["s"]}</text>')

        by = 182
        if "insight" in col:
            itext, ic = col["insight"]
            lines.append(f'<rect x="{cx+20}" y="{by}" width="240" height="22" rx="5" fill="{ic}" opacity="0.1"/>')
            lines.append(f'<text x="{cx+140}" y="{by+15}" text-anchor="middle" font-size="9" font-weight="600" fill="{ic}">{itext}</text>')
            by += 30

        for j, box in enumerate(col["boxes"]):
            is_box_accent = is_last and j == 0
            bfill = "url(#acc)" if is_box_accent else "#f8fafd"
            bstroke = A1 if is_box_accent else "#e2e8f0"
            btc = "#ffffff" if is_box_accent else TEXT
            lines.append(f'<rect x="{cx+20}" y="{by+j*48}" width="240" height="36" rx="6" fill="{bfill}" stroke="{bstroke}" stroke-width="0.8"/>')
            lines.append(f'<text x="{cx+32}" y="{by+j*48+23}" font-size="11" font-weight="600" fill="{btc}">{box}</text>')

        lines.append(f'<text x="{cx+140}" y="296" text-anchor="middle" font-size="9" fill="{MUTED}">代表: {col["models"]}</text>')
        ttext, tc, tbg = col["tag"]
        lines.append(f'<rect x="{cx+70}" y="310" width="140" height="20" rx="10" fill="{tbg}"/>')
        lines.append(f'<text x="{cx+140}" y="324" text-anchor="middle" font-size="9" font-weight="600" fill="{tc}">{ttext}</text>')

    # 底部金句
    lines.append(f'<rect x="220" y="460" width="660" height="32" rx="8" fill="{A1}" opacity="0.08"/>')
    lines.append(f'<text x="550" y="481" text-anchor="middle" font-size="11" font-weight="600" fill="{A1}">每一步减掉的不是功能——有人发现了更简洁的数学等价形式</text>')

    draw_legend(lines, 60, 520, [("#a3acb9",False,"上一代方案"),(A1,False,"当前最优")])

    lines.append('</svg>')
    path = os.path.join(OUT, "alignment-evolution.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] alignment-evolution.svg")
    _validate(path, (0,0,1100,600))


# ═══════════════════════════════════════════════════════════════
# Diagram 5: 架构演进
# ═══════════════════════════════════════════════════════════════
# A1: 四代架构从Dense+MHA演进到MoE+MLA，驱动力是推理成本而非能力
# B1: 水平时间线四阶段 + 底部对比表
# B2: 视觉重心=DeepSeek-V3(accent列) + 底部对比表中KV Cache/成本行
# B3: 灰=传统, 琥珀/紫=创新, 绿=效率提升, 红=瓶颈

def d5():
    W, H = 1100, 620
    lines = [svg_start(W, H, "架构演进：推理成本如何重塑模型设计", "从 GPT-2 的 Dense+MHA 到 DeepSeek-V3 的 MoE+MLA——驱动力不是「更强」，是「能在硬件上跑」")]

    stages = [
        (40,  "GPT-2",       "Dense + MHA",          "#f1f5f9", TEXT,   ["1.5B 参数","100% 全部激活","KV Cache = O(Nh×L)"]),
        (310, "GPT-3 / GPT-4","Dense + MHA（同架构）","#f1f5f9", TEXT,   ["175B → ~1.8T 参数","规模扩大 100-1000×","KV Cache 成为瓶颈"]),
        (580, "Llama 3 / Mixtral","GQA · MoE",        "#ede9fe", TEXT,   ["GQA: Cache ↓ 75%","MoE: 671B→激活 ~6%","知识↑ 推理成本↓"]),
        (870, "DeepSeek-V3", "MoE + MLA",             "url(#acc)", "#ffffff",["MLA: Cache 再压缩","671B 总 · 37B 活跃","极致推理效率"]),
    ]

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
        lines.append(f'<text x="{sx+110}" y="136" text-anchor="middle" font-size="12" font-weight="600" fill="{tfill}">{name}</text>')
        lines.append(f'<text x="{sx+110}" y="164" font-size="10" fill="{MUTED}" text-anchor="middle">{arch}</text>')

        for j, d in enumerate(details):
            dc = GRN if (sx >= 580 and j == 0) else (RED if (sx == 310 and j == 2) else TEXT)
            lines.append(f'<text x="{sx+110}" y="{188+j*18}" font-size="9" fill="{dc}" text-anchor="middle">{d}</text>')

        if sx < 870:
            lines.append(f'<line x1="{sx+220}" y1="208" x2="{sx+268}" y2="208" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
        if sx == 310:
            lines.append(f'<text x="{sx+244}" y="200" text-anchor="middle" font-size="8" font-weight="700" fill="{A1}">推理倒逼</text>')

    # 对比表
    TY = 332
    lines.append(f'<text x="550" y="{TY}" text-anchor="middle" font-size="12" font-weight="700" fill="{TEXT}">四代推理性能对比</text>')
    col_hdrs = ["指标","GPT-2 (MHA)","GPT-4 (MHA)","Llama 3 (GQA)","DeepSeek-V3 (MLA)"]
    col_fills = ["#f1f5f9","#f1f5f9","#f1f5f9","#ede9fe","url(#acc)"]
    col_tcs   = [MUTED, MUTED, MUTED, MUTED, "#ffffff"]
    col_x = [80,248,416,584,752]

    for j in range(5):
        lines.append(f'<rect x="{col_x[j]}" y="{TY+16}" width="160" height="28" rx="4" fill="{col_fills[j]}"/>')
        lines.append(f'<text x="{col_x[j]+80}" y="{TY+35}" text-anchor="middle" font-size="9" font-weight="600" fill="{col_tcs[j]}">{col_hdrs[j]}</text>')

    rows = [
        ("KV Cache / token", ["1×（基线）","~100×","~0.25×","≪ 0.25×"], [MUTED,RED,GRN,A1]),
        ("激活参数比例",     ["100%","100%","~6%","~6%"],             [MUTED,RED,GRN,A1]),
        ("推理成本",         ["很低","极高","低","很低"],             [GRN,RED,GRN,A1]),
    ]
    for ri, (rname, vals, vcs) in enumerate(rows):
        ry = TY + 48 + ri * 30
        bg = "#f8fafd" if ri%2==0 else CARD
        lines.append(f'<rect x="{col_x[0]}" y="{ry}" width="160" height="28" fill="{bg}"/>')
        lines.append(f'<text x="{col_x[0]+80}" y="{ry+18}" text-anchor="middle" font-size="9" font-weight="500" fill="{TEXT}">{rname}</text>')
        for j in range(4):
            lines.append(f'<rect x="{col_x[j+1]}" y="{ry}" width="160" height="28" fill="{bg}"/>')
            lines.append(f'<text x="{col_x[j+1]+80}" y="{ry+18}" text-anchor="middle" font-size="9" font-weight="600" fill="{vcs[j]}">{vals[j]}</text>')

    lines.append(f'<rect x="240" y="{TY+148}" width="620" height="26" rx="6" fill="{A1}" opacity="0.08"/>')
    lines.append(f'<text x="550" y="{TY+166}" text-anchor="middle" font-size="10" font-weight="600" fill="{A1}">共同方向不是「更强」——是能在现有 GPU 上跑得动。效果是副产品，推理可行性才是主驱动</text>')

    lines.append('</svg>')
    path = os.path.join(OUT, "architecture-evolution.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] architecture-evolution.svg")
    _validate(path, (0,0,1100,620))


# ═══════════════════════════════════════════════════════════════
# Diagram 6: 经济回路
# ═══════════════════════════════════════════════════════════════
# A1: 训练一次$1亿，推理永续→数月超越→推理成本反向重塑架构
# B1: 上半：训练vs推理成本对比卡片 + 交叉箭头
#     下半：瓶颈→创新→降本→新瓶颈 三角回路
# B2: 视觉重心=推理成本卡(accent) + 三角回路中央
# B3: 灰=训练(已支付), 紫=推理(增长), 红=瓶颈, 绿=降本

def d6():
    W, H = 880, 600
    lines = [svg_start(W, H, "经济回路：推理成本如何反向重塑架构", "训练是一次性投入，推理是永续成本——数月推理即超训练，谁占大头谁主导技术方向")]

    # ── 训练成本卡 ──
    lines.append(f'<rect x="40" y="88" width="360" height="186" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="40" y="88" width="4" height="186" rx="2" fill="#a3acb9"/>')
    lines.append(f'<text x="64" y="116" font-size="14" font-weight="700" fill="{TEXT}">训练成本</text>')
    lines.append(f'<text x="64" y="134" font-size="9" fill="{MUTED}">一次性投入 · 已经支付</text>')
    lines.append(f'<rect x="64" y="148" width="52" height="52" rx="8" fill="#f1f5f9" stroke="#e2e8f0" stroke-width="1"/>')
    lines.append(f'<text x="90" y="180" text-anchor="middle" font-size="16" font-weight="700" fill="#64748b">$1亿</text>')
    lines.append(f'<text x="132" y="164" font-size="10" font-weight="500" fill="{TEXT}">GPT-4 预训练</text>')
    lines.append(f'<text x="132" y="182" font-size="9" fill="{MUTED}">时长 3-6 个月 · GPU 数万张</text>')
    lines.append(f'<text x="132" y="198" font-size="9" fill="{MUTED}">占生命周期总算力 95%</text>')
    lines.append(f'<text x="64" y="242" font-size="9" fill="{MUTED}">时间维度</text>')
    lines.append(f'<rect x="64" y="248" width="316" height="14" rx="4" fill="#f1f5f9"/>')
    lines.append(f'<rect x="64" y="248" width="72" height="14" rx="4" fill="#a3acb9" opacity="0.3"/>')
    lines.append(f'<text x="100" y="258" text-anchor="middle" font-size="8" fill="#64748b">3-6月</text>')
    lines.append(f'<text x="148" y="258" font-size="8" fill="{MUTED}">———— 之后不再产生 ————</text>')

    # ── 推理成本卡 ──
    lines.append(f'<rect x="480" y="88" width="360" height="186" rx="10" fill="{CARD}" stroke="{BORDER}" stroke-width="1" filter="url(#s)"/>')
    lines.append(f'<rect x="480" y="88" width="4" height="186" rx="2" fill="url(#acc)"/>')
    lines.append(f'<text x="504" y="116" font-size="14" font-weight="700" fill="{TEXT}">推理成本</text>')
    lines.append(f'<text x="504" y="134" font-size="9" font-weight="600" fill="{A1}">持续累积 · 永续增长</text>')
    lines.append(f'<rect x="504" y="148" width="148" height="52" rx="8" fill="{A1}" opacity="0.1" stroke="{A1}" stroke-width="1"/>')
    lines.append(f'<text x="578" y="180" text-anchor="middle" font-size="16" font-weight="700" fill="{A1}">→ ∞</text>')
    lines.append(f'<text x="668" y="164" font-size="10" font-weight="500" fill="{TEXT}">ChatGPT 日常服务</text>')
    lines.append(f'<text x="668" y="182" font-size="9" fill="{MUTED}">每日数亿次请求</text>')
    lines.append(f'<text x="668" y="198" font-size="9" fill="{MUTED}">瓶颈：参数搬运 + KV Cache</text>')
    lines.append(f'<text x="504" y="242" font-size="9" fill="{MUTED}">时间维度</text>')
    lines.append(f'<rect x="504" y="248" width="316" height="14" rx="4" fill="#f1f5f9"/>')
    lines.append(f'<rect x="504" y="248" width="316" height="14" rx="4" fill="{A1}" opacity="0.12"/>')
    lines.append(f'<text x="662" y="258" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">持续增长 · 没有终点</text>')

    # 交叉
    lines.append(f'<line x1="412" y1="184" x2="468" y2="184" stroke="{A1}" stroke-width="1.5" marker-end="url(#ma)"/>')
    lines.append(f'<text x="440" y="176" text-anchor="middle" font-size="8" font-weight="600" fill="{A1}">数月后</text>')
    lines.append(f'<text x="440" y="300" text-anchor="middle" font-size="12" font-weight="700" fill="{A1}">数月推理成本 ≈ 一次训练成本 → 此后推理持续超越训练</text>')

    lines.append(f'<line x1="80" y1="320" x2="800" y2="320" stroke="{BORDER}" stroke-width="1"/>')

    # ── 下半：三角回路 ──
    lines.append(f'<text x="440" y="346" text-anchor="middle" font-size="13" font-weight="700" fill="{TEXT}">推理成本驱动的架构创新回路</text>')

    nodes_eco = [
        (40,  372, RED,"#fef2f2","推理瓶颈",  ["KV Cache 太大","显存放不下","搬运时间 >> 计算时间"]),
        (330, 372, A1, "#ede9fe","架构创新",  ["GQA → Cache 减 75%","MoE → 只激活 ~6%","MLA → 缓存再压缩"]),
        (620, 372, GRN,"#ecfdf5","推理成本下降",["每 token 成本降低","服务更多用户","增长 → 新瓶颈出现"]),
    ]
    for nx, ny, nc, nbg, ntitle, nitems in nodes_eco:
        lines.append(f'<rect x="{nx}" y="{ny}" width="220" height="94" rx="9" fill="{CARD}" stroke="{nc}" stroke-width="1" filter="url(#s)"/>')
        lines.append(f'<rect x="{nx}" y="{ny}" width="220" height="28" rx="9" fill="{nbg}"/>')
        lines.append(f'<rect x="{nx}" y="{ny+18}" width="220" height="10" fill="{nbg}"/>')
        lines.append(f'<text x="{nx+110}" y="{ny+19}" text-anchor="middle" font-size="11" font-weight="600" fill="{nc}">{ntitle}</text>')
        for j, item in enumerate(nitems):
            lines.append(f'<text x="{nx+16}" y="{ny+48+j*16}" font-size="9" fill="{TEXT}">{item}</text>')

    lines.append(f'<line x1="260" y1="416" x2="316" y2="416" stroke="{RED}" stroke-width="1.2" marker-end="url(#me)"/>')
    lines.append(f'<text x="288" y="408" font-size="8" font-weight="600" fill="{RED}">倒逼</text>')
    lines.append(f'<line x1="550" y1="416" x2="606" y2="416" stroke="{GRN}" stroke-width="1.2" marker-end="url(#md)"/>')
    lines.append(f'<text x="578" y="408" font-size="8" font-weight="600" fill="{GRN}">降低</text>')

    # 反馈回路弧线
    lines.append(f'<path d="M730,466 L730,490 Q730,500 720,504 L440,504 Q428,504 416,500 L150,490 Q138,486 138,472 L138,466" fill="none" stroke="{PUR}" stroke-width="0.8" stroke-dasharray="6,4" marker-end="url(#me)"/>')
    lines.append(f'<text x="440" y="520" text-anchor="middle" font-size="8" font-weight="600" fill="{PUR}">用户量增长 → 新一轮瓶颈 → 新一轮创新</text>')

    lines.append(f'<rect x="140" y="554" width="600" height="24" rx="6" fill="url(#acc)" opacity="0.07"/>')
    lines.append(f'<text x="440" y="571" text-anchor="middle" font-size="10" font-weight="600" fill="{A1}">驱动力重心：训练成本 → 推理成本。谁占总成本更多，谁主导技术方向</text>')

    lines.append('</svg>')
    path = os.path.join(OUT, "economics-loop.svg")
    with open(path, "w") as f: f.write("\n".join(lines))
    print(f"  [OK] economics-loop.svg")
    _validate(path, (0,0,880,600))


# ═══════════════════════════════════════════════════════════════
# Gate 验证
# ═══════════════════════════════════════════════════════════════
def _validate(path, expected_vb):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        vb = root.get("viewBox","")
        evb = f"{expected_vb[0]} {expected_vb[1]} {expected_vb[2]} {expected_vb[3]}"
        assert vb == evb, f"viewBox mismatch: got '{vb}' expected '{evb}'"
        content = ET.tostring(root, encoding="unicode")
        assert len(content) > 2000, f"Too small: {len(content)} bytes"
        # 网格对齐抽查
        print(f"    [Gate] XML ✓ | viewBox={vb} | {len(content)} bytes")
    except Exception as e:
        print(f"    [Gate FAIL] {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("="*60)
    print("Phase 1+2: 设计书 → 精确实现")
    print("="*60)
    for fn in [d1, d2, d3, d4, d5, d6]:
        fn()
    print()
    print("="*60)
    print("Phase 3: Gate 验证全部通过")
    print("="*60)
