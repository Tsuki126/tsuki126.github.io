# 三对话写作流水线 · 使用指南

## 前置准备

```bash
# 1. 获取 DeepSeek API Key
#    在 https://platform.deepseek.com/ 注册获取

# 2. 设置环境变量（建议写入 ~/.zshrc）
export DEEPSEEK_API_KEY="sk-xxx"

# 3. 脚本已就位
#    ~/.claude/skills/blog/outline-template.md  — 大纲模板
#    <project>/generate_from_outline.py          — DeepSeek 生成脚本
```

## 标准流程

### 对话 1：Claude 生成大纲

```
提示词示例：
/blog new deep-dive "MCP 协议安全分析"
——然后用 outline-template.md 输出大纲
```

输出：`outline.md`（含 thesis、章节规格、配图规划、引用来源）

**→ 你确认大纲，可以要求修改**

### 对话 2：DeepSeek 生成初稿

在 CLI 中执行：

```bash
! python generate_from_outline.py content/blog/my-article/outline.md
```

或指定输出路径：
```bash
! python generate_from_outline.py outline.md -o content/blog/raw-article.md
```

输出：`raw_article.md`（含 frontmatter 和正文，配图位置用 `<INSERT_DIAGRAM: 图名>` 占位）

**→ 此时可以 /clear 重启对话**

### 对话 3：Claude 审核 + 润色 + 补图

```
提示词示例：
读取 content/blog/raw_article.md
审核：事实准确性、论证强度、信息密度
润色：按 Stripe 博客风格，短段落，论点先行
补图：对每个 <INSERT_DIAGRAM: 图名> 生成 SVG
```

输出：`content/blog/{slug}.md` + `static/images/{slug}/*.svg`

## 关键设计

| 要素 | 说明 |
|:---|:---|
| outline.md | 核心质量关口。不确认就不往下走 |
| spec 信息 | 每节的 purpose/evidence/tone 都写入 outline，减少 DeepSeek 的随机偏差 |
| RAW 格式 | 纯 Markdown，含 <INSERT_DIAGRAM> 占位，Claude 据此补图 |
| 模型分工 | DeepSeek 负责初稿多样性，Claude 负责审核 + 配图 + 润色 |
