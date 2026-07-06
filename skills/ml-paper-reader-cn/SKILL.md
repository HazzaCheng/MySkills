---
name: ml-paper-reader-cn
description: Chinese structured close reading of machine learning, AI, deep learning, NLP, CV, benchmark, systems, and technical research papers, with detailed experiment extraction. Use when the user asks in Chinese or English to read, summarize, explain, analyze, or take notes on a single paper, arXiv link, PDF, Hugging Face paper page, academic article, technical blog, or report, especially when they want sections such as purpose, challenges, method, key concepts, contributions, experiments, conclusion, limitations, and future work.
---

# ML Paper Reader CN

## Overview

Use this skill to produce a faithful Chinese close-reading note for one paper or article. Emphasize evidence boundaries, method mechanics, table/figure extraction, and detailed experiment analysis.

Do not perform a broad literature review unless the user asks for it. For multi-paper synthesis, prefer `literature-review`; for critical quality scoring, combine with `scholar-evaluation`; for paper retrieval, use `arxiv`, `huggingface-papers`, `pdf`, or `zotero` when available and relevant.

## Source Rules

- If the user provides pasted text, base the analysis only on that text.
- If the user provides a URL, arXiv ID, PDF, or local file, retrieve and read the accessible article content before summarizing.
- Do not add outside facts, related work, implementation details, or benchmark context unless the user explicitly asks.
- If full text, appendix, tables, figures, or supplementary material cannot be accessed, state the limitation near the top.
- Mark missing information as `文中未明确说明` instead of inferring it.
- For reasonable synthesis from provided context, label it as `根据上下文可归纳为`.

## Reading Workflow

1. Identify the article type: method paper, benchmark paper, survey, theory paper, system paper, dataset paper, technical blog, or report.
2. Read title, abstract, introduction, figures/tables, method, experiments, conclusion, and appendix when available.
3. Extract claims into the required output sections; prioritize facts directly supported by the article.
4. For method-heavy papers, explain input, processing modules, output, training objective, loss function, and inference flow when present.
5. For formula, algorithm, or pseudocode, explain variable roles, computation flow, and how it supports the method. Do not translate formulas word by word.
6. For experiments, inspect every experiment table/figure that is available and summarize what each is intended to prove.
7. Before finalizing, check that all required sections are present and the experiment section is more detailed than the others.

## Output Requirements

Write in Simplified Chinese. Keep widely used technical terms in English when they appear in the article, such as `transformer`, `BERT`, `GPT`, `CNN`, `attention`, `embedding`, `fine-tuning`, `pretraining`, `RLHF`, `BLEU`, `F1`, and `ROC-AUC`. Explain their role in Chinese, especially their role in this article, not only their generic definition.

Use clear hierarchical headings and bullets. Do not quote long passages. Be professional, objective, and concise where the paper is concise; be detailed where the paper is detailed.

Use this structure:

### 0. 论文元信息

- 标题
- 作者 / 机构
- 发表时间 / venue
- 文章类型
- 一句话总结
- 信息完整性说明: full text / abstract only / missing appendix / missing figures, etc.

### 1. 文章目的

- Use 2-4 bullets for motivation and goals.

### 2. 挑战 / 问题背景

- Use 3-6 bullets for challenges, gaps, or limitations of prior methods.
- Distinguish explicit author claims from inferred background.

### 3. 方法

- Explain the core method, framework, or system.
- Prefer `输入 -> 处理流程/模块 -> 输出` for ML methods.
- Include architecture modules, algorithm steps, training objectives, loss functions, data processing, and inference procedure when present.
- Explain key formulas, algorithms, or pseudocode if they are central.

### 4. 关键概念

- List important terms and concepts.
- Keep common technical terms in English.
- For each concept, explain what it means and what role it plays in this article.

### 5. 主要发现 / 主要贡献

- Use 3-6 bullets for contributions, innovations, or main findings.
- Keep claims within the evidence shown in the article.

### 6. 实验

This must be the most detailed section when experiments exist. If there are no experiments, state `文中未包含实验部分` and explain the evidence type used instead.

Organize in this order:

#### 6.1 实验设置

- 数据集: name, scale, source, task, split, preprocessing, and special properties when given.
- 模型配置: model size, architecture, training setup, compute, optimizer, learning rate, batch size, epochs, decoding, or prompting setup when given.
- 对比基线: list baselines and explain why they matter.
- Implementation or reproducibility details: code, checkpoint, hardware, random seeds, or appendix details when given.

#### 6.2 评价指标

- List each metric, keep metric names such as `accuracy`, `F1`, `BLEU`, `ROUGE`, `perplexity`, `ROC-AUC`, `mAP`, `pass@k`, and `win rate` in English.
- Briefly explain what each metric measures if the article provides or implies it.

#### 6.3 实验结果

- Summarize every main table/figure when available: table/figure identifier, purpose, dataset, compared methods, metrics, best result, and the conclusion the authors draw.
- Include important numeric results, absolute/relative gains, trends, and tradeoffs.
- If exact numbers are unavailable in the accessible text, say so.

#### 6.4 消融实验

- For each ablation, state the removed/replaced component, purpose, result change, and conclusion.
- If no ablation study is present, state `文中未明确给出消融实验`.

#### 6.5 可视化 / 案例分析 / 错误分析

- Summarize qualitative examples, visualizations, case studies, error analysis, or failure cases.
- Explain what behavior they are meant to demonstrate.
- If absent, state `文中未明确给出相关内容`.

#### 6.6 实验分析

- Explain what the experiments support, what remains unsupported, and whether the experimental evidence matches the stated claims.
- Do not introduce external criticism unless the user asks for a review; keep the analysis grounded in the article.

### 7. 局限性与适用边界

- List limitations, assumptions, failure cases, threats to validity, or scope boundaries discussed by the authors.
- If not discussed, state `文中未明确讨论局限性 / 适用边界`.

### 8. 结论与未来工作

- 结论: 2-4 bullets for the overall conclusion.
- 未来工作: list future directions if present; otherwise state `文中未明确给出未来工作`.

### 9. 读者速记

- 这篇文章解决了什么问题？
- 它为什么有效？
- 它相比已有方法强在哪里？
- 读完后最应该记住的 3 点。

## Quality Checks

Before final output, ensure:

- All sections 0-9 are present.
- Missing content is explicitly marked rather than invented.
- Technical terms from the article are preserved when they are standard ML terms.
- The experiment section includes datasets, settings, baselines, metrics, results, ablations, visualizations/cases, and analysis when available.
- Claims derived from tables/figures name the corresponding table/figure when possible.
- The output is a structured summary, not a paragraph-by-paragraph translation.
