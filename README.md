# MySkills

Personal Codex skills shared across Windows and macOS machines.

This repo is a migration record and backup for non-system skills normally stored under:

```text
~/.codex/skills
```

On Windows this usually resolves to `%USERPROFILE%\.codex\skills`. On macOS it resolves to `$HOME/.codex/skills`.

## What is included

- `skills/`: a snapshot of each user-installed skill folder.
- `skills-manifest.json`: machine-readable inventory generated from local `SKILL.md` files.
- `skills-installers.json`: install recipes for package-managed skills that should not be copied from old machines.
- `skills-upstreams.json`: upstream repository map for skills with known sources.
- `scripts/install-local-skills.py`: cross-platform restore script for Windows and macOS.
- `scripts/sync-from-local-skills.py`: cross-platform sync script for Windows and macOS.
- `scripts/check-upstream-skills.py`: upstream drift checker for mirrored skills.
- `scripts/*.ps1`: legacy Windows PowerShell helpers kept for convenience.

System skills under `.system` and plugin-provided skills are not copied here, because Codex/plugins should provide those again on each machine.

## Restore on a machine

From this repo root, run one of:

```bash
python3 scripts/install-local-skills.py
```

```powershell
py -3 scripts\install-local-skills.py
```

The script copies every folder in `skills/` into `~/.codex/skills`.

Package-managed skills listed in `skills-installers.json` are installed from their package command instead of copied from this repo. Current installer-backed skills:

| Skill | Install command | Notes |
|---|---|---|
| ecc-skills | `python3 scripts/install-ecc-package-skills.py --package ecc-universal --skills <managedSkillNamesCsv>` | Install ECC skills that are present in the ecc-universal npm package. ECC skills not currently shipped in that package remain as repository snapshots. |
| ttmall-skill-repo | `cd /Users/bytedance/Work/code/ttmall_skill_repo && bash install.sh` | Installed as symlinks from /Users/bytedance/Work/code/ttmall_skill_repo. Keep these managed by that repository instead of snapshotting them into MySkills. |
| weread-skills | `npx skills add Tencent/WeChatReading -g` | Set `WEREAD_API_KEY` locally after install. |

## Update this repo after installing new skills

From this repo root, run one of:

```bash
python3 scripts/sync-from-local-skills.py --commit --push
```

```powershell
py -3 scripts\sync-from-local-skills.py --commit --push
```

For skills installed through package runners, for example:

```bash
npx skills add Tencent/WeChatReading -g
```

add them to `skills-installers.json` instead of committing the installed `SKILL.md` files. The command is the restore path for new machines. Do not commit credentials or API keys; keep them in local environment variables.

All generated text files are written as UTF-8 without BOM so both macOS/Linux tools and Windows terminals can read them cleanly.

## Check upstream skill updates

This repository is a local snapshot, so upstream project updates are tracked separately in `skills-upstreams.json`.

Show mapping coverage without network access:

```bash
python3 scripts/check-upstream-skills.py --coverage
```

```powershell
py -3 scripts\check-upstream-skills.py --coverage
```

Check one skill against its upstream repository:

```bash
python3 scripts/check-upstream-skills.py --skill codebase-onboarding
```

Write a full JSON report:

```bash
python3 scripts/check-upstream-skills.py --write-report
```

Statuses:

- `up-to-date`: repository snapshot matches the configured upstream path.
- `upstream-changed`: upstream content differs from `skills/<name>`.
- `upstream-path-missing`: the upstream repo was fetched, but no configured path matched.
- `unknown-upstream`: no upstream repo is known yet; add it to `skills-upstreams.json`.
- `upstream-unavailable`: git could not fetch the configured repo/ref.

## Skill Inventory

Count: 122

| Folder | Skill name | Description |
|---|---|---|
| academic-paper | academic-paper | 12-agent academic paper writing pipeline. 11 modes (full/plan/outline/revision/revision-coach/abstract/lit-review/format-convert/citation-check/disclosure/rebuttal-audit). 6 paper types, 5 citation formats, bilingual abstracts, LaTeX/DOCX-via-Pandoc/PDF output. Style Calibration + Writing Quality Check + Anti-Patterns with IRON RULE markers. Triggers: write paper, academic paper, guide my paper, parse reviews, audit my rebuttal, check my response draft, AI disclosure, 寫論文, 學術論文, 引導我寫論文, 審查意見, 評估回覆. |
| academic-paper-reviewer | academic-paper-reviewer | Multi-perspective academic paper review with dynamic reviewer personas. Simulates 5 independent reviewers (EIC + 3 peer reviewers + Devil's Advocate) with field-specific expertise. Supports full review, re-review (verification), quick assessment, methodology focus, Socratic guided, and calibration modes. Triggers on: review paper, peer review, manuscript review, referee report, review my paper, critique paper, simulate review, editorial review, calibrate reviewer, reviewer calibration, measure reviewer accuracy. |
| academic-pipeline | academic-pipeline | Orchestrator for the full academic research pipeline: research -> write -> integrity check -> review -> revise -> re-review -> re-revise -> final integrity check -> finalize. Coordinates deep-research, academic-paper, and academic-paper-reviewer into a seamless 10-stage workflow with mandatory integrity verification, two-stage peer review, and reproducible quality gates. Triggers on: academic pipeline, research to paper, full paper workflow, paper pipeline, end-to-end paper, research-to-publication, complete paper workflow. |
| accessibility | accessibility | Design, implement, and audit inclusive digital products using WCAG 2.2 Level AA standards. Use this skill to generate semantic ARIA for Web and accessibility traits for Web and Native platforms (iOS/Android). |
| agent-eval | agent-eval | Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics |
| agent-payment-x402 | agent-payment-x402 | Add x402 payment execution to AI agents with per-task budgets, spending controls, and non-custodial wallets. Supports Base through agentwallet-sdk and X Layer through OKX Payments / OKX Agent Payments Protocol. |
| architecture-decision-records | architecture-decision-records | Capture architectural decisions made during Claude Code sessions as structured ADRs. Auto-detects decision moments, records context, alternatives considered, and rationale. Maintains an ADR log so future developers understand why the codebase is shaped the way it is. |
| arxiv | arxiv | Search arXiv papers by keyword, author, category, or ID. |
| autonomous-agent-harness | autonomous-agent-harness | Transform Claude Code into a fully autonomous agent system with persistent memory, scheduled operations, computer use, and task queuing. Replaces standalone agent frameworks (Hermes, AutoGPT) by leveraging Claude Code's native crons, dispatch, MCP tools, and memory. Use when the user wants continuous autonomous operation, scheduled tasks, or a self-directing agent loop. |
| benchmark | benchmark | Use this skill to measure performance baselines, detect regressions before/after PRs, and compare stack alternatives. |
| browser-qa | browser-qa | Use this skill to automate visual testing and UI interaction verification using browser automation after deploying features. |
| bun-runtime | bun-runtime | Bun as runtime, package manager, bundler, and test runner. When to choose Bun vs Node, migration notes, and Vercel support. |
| canary-watch | canary-watch | Use this skill to monitor and verify a deployed URL after releases — checks HTTP endpoints, SSE streams, static assets, console errors, and performance regressions after deploys, merges, or dependency upgrades. Smoke / canary / post-deploy verification. |
| ck | ck | You are the **Context Keeper** assistant. When the user invokes any `/ck:*` command, run the corresponding Node.js script and present its stdout to the user verbatim. Scripts live at: `~/.claude/skills/ck/commands/` (expand `~` with `$HOME`). |
| claude-design | claude-design | Design one-off HTML artifacts (landing, deck, prototype). |
| click-path-audit | click-path-audit | Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other out, produce wrong final state, or leave the UI in an inconsistent state. Use when: systematic debugging found no bugs but users report broken buttons, or after any major refactor touching shared state stores. |
| codebase-onboarding | codebase-onboarding | Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.md. Use when joining a new project or setting up Claude Code for the first time in a repo. |
| codehealth-mcp | codehealth-mcp | Real-time structural Code Health via CodeScene MCP — review before edits, verify score deltas after changes, gate commits and PRs. Use when reviewing code quality, refactoring, checking if AI changes degraded a file, or before commit/PR. |
| context-budget | context-budget | Audits Claude Code context window consumption across agents, skills, MCP servers, and rules. Identifies bloat, redundant components, and produces prioritized token-savings recommendations. |
| deep-research | deep-research | Universal deep research agent team. 13-agent pipeline for rigorous academic research on any topic. 8 modes: full research, quick brief, paper review, lit-review, fact-check, three-way literature scan, Socratic guided research dialogue, and systematic review with optional meta-analysis. Covers research question formulation, Socratic mentoring, methodology design, systematic literature search, source verification, cross-source synthesis, risk of bias assessment, meta-analysis, APA 7.0 report compilation, editorial review, devil's advocate challenges, ethics review, and post-research literature monitoring. Triggers on: research, deep research, literature review, systematic review, meta-analysis, PRISMA, evidence synthesis, fact-check, WHY HOW WHAT papers, 3W literature scan, guide my research, help me think through, 研究, 深度研究, 文獻回顧, 文獻探討, 系統性回顧, 後設分析, 事實查核, 三段式文獻掃描, 引導我的研究, 幫我釐清, 幫我想想, 我不確定要研究什麼, 研究方向, 研究主題. |
| design-system | design-system | Use this skill to generate or audit design systems, check visual consistency, and review PRs that touch styling. |
| django-celery | django-celery | Django + Celery async task patterns — configuration, task design, beat scheduling, retries, canvas workflows, monitoring, and testing. Use when adding background jobs, scheduled tasks, or async processing to a Django app. |
| documentation-lookup | documentation-lookup | Use up-to-date library and framework docs via Context7 MCP instead of training data. Activates for setup questions, API references, code examples, or when the user names a framework (e.g. React, Next.js, Prisma). |
| ecc-guide | ecc-guide | Guide users through ECC's current agents, skills, commands, hooks, rules, install profiles, and project onboarding by reading the live repository surface before answering. |
| flox-environments | flox-environments | Create reproducible, cross-platform (macOS/Linux) development environments with Flox, a declarative Nix-based environment manager. Use when setting up project toolchains for any language, installing system-level dependencies (compilers, databases, native libs like openssl/BLAS), pinning exact package versions for a team, running local services (PostgreSQL, Redis, Kafka), onboarding developers with one command, or solving 'works on my machine' problems — including agent/vibe-coding setups that need project-scoped tools without sudo. Also use when the user mentions .flox/, manifest.toml, flox activate, or FloxHub. |
| flutter-dart-code-review | flutter-dart-code-review | Library-agnostic Flutter/Dart code review checklist covering widget best practices, state management patterns (BLoC, Riverpod, Provider, GetX, MobX, Signals), Dart idioms, performance, accessibility, security, and clean architecture. |
| follow-aleabito | follow-aleabito | Track Serenity / @aleabitoreddit on X and turn the feed into (1) a beginner-friendly Chinese iMessage digest with first-principles + Buffett-style judgement, (2) cumulative 60-day ticker mention analytics CSVs for a website, (3) a Xiaohongshu writing brief, and (4) a durable private research map. Trigger on requests like "follow aleabitoreddit / AleaBito / Serenity", "daily Chinese updates from that X account", "60-day mention analytics", "ticker mention count", "写小红书 aleabito", "aleabito 研究地图 / research map", or any request for Chinese commentary derived from @aleabitoreddit posts. |
| frontend-a11y | frontend-a11y | Accessibility patterns for React and Next.js — semantic HTML, ARIA attributes, form labeling, keyboard navigation, focus management, and screen reader support. Use when building any interactive UI component or form. |
| gan-style-harness | gan-style-harness | GAN-inspired Generator-Evaluator agent harness for building high-quality applications autonomously. Based on Anthropic's March 2026 harness design paper. |
| gateguard | gateguard | Fact-forcing gate that blocks Edit/Write/Bash (including MultiEdit) and demands concrete investigation (importers, data schemas, user instruction) before allowing the action. Measurably improves output quality by +2.25 points vs ungated agents. |
| git-workflow | git-workflow | Git workflow patterns including branching strategies, commit conventions, merge vs rebase, conflict resolution, and collaborative development best practices for teams of all sizes. |
| healthcare-cdss-patterns | healthcare-cdss-patterns | Clinical Decision Support System (CDSS) development patterns. Drug interaction checking, dose validation, clinical scoring (NEWS2, qSOFA), alert severity classification, and integration into EMR workflows. |
| healthcare-emr-patterns | healthcare-emr-patterns | EMR/EHR development patterns for healthcare applications. Clinical safety, encounter workflows, prescription generation, clinical decision support integration, and accessibility-first UI for medical data entry. |
| healthcare-eval-harness | healthcare-eval-harness | Patient safety evaluation harness for healthcare application deployments. Automated test suites for CDSS accuracy, PHI exposure, clinical workflow integrity, and integration compliance. Blocks deployments on safety failures. |
| hermes-imports | hermes-imports | Convert local Hermes operator workflows into sanitized ECC skills and release-pack artifacts. Use when preparing a Hermes workflow for public ECC reuse without leaking private workspace state, credentials, or local-only paths. |
| hexagonal-architecture | hexagonal-architecture | Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration across TypeScript, Java, Kotlin, and Go services. |
| homelab-pihole-dns | homelab-pihole-dns | Pi-hole installation, blocklist management, DNS-over-HTTPS setup, DHCP integration, local DNS records, and troubleshooting broken DNS resolution on a home network. |
| homelab-vlan-segmentation | homelab-vlan-segmentation | Segmenting home networks into VLANs for IoT, guest, trusted, and server traffic using UniFi, pfSense/OPNsense, and MikroTik — including switch trunk config, firewall rules, and wireless SSID mapping. |
| homelab-wireguard-vpn | homelab-wireguard-vpn | WireGuard VPN server setup, peer configuration, key generation, split tunneling vs full tunnel routing, and remote access to a home network from mobile and laptop clients. |
| humanizer | humanizer | Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on Wikipedia's comprehensive "Signs of AI writing" guide. Detects and fixes patterns including: inflated symbolism, promotional language, superficial -ing analyses, vague attributions, em dash overuse, rule of three, AI vocabulary words, passive voice, negative parallelisms, and filler phrases. |
| humanizer-zh | humanizer-zh | 去除文本中的 AI 生成痕迹。适用于编辑或审阅文本，使其听起来更自然、更像人类书写。 基于维基百科的"AI 写作特征"综合指南。检测并修复以下模式：夸大的象征意义、 宣传性语言、以 -ing 结尾的肤浅分析、模糊的归因、破折号过度使用、三段式法则、 AI 词汇、否定式排比、过多的连接性短语。 |
| ideation | creative-ideation | Generate ideas via named methods from creative practice. |
| inherit-legacy-style | inherit-legacy-style | Legacy-project style inheritance skill. Use when the user types /inherit-legacy-style, or when onboarding an AI coding agent onto a hand-written legacy project and you need to prevent "style drift" (the model imposing its pretrained mainstream idioms onto the project). Language- and framework-agnostic — it aligns meta-architecture only, not syntax. Once run, it becomes a behavioral constraint on all subsequent coding tasks. Do NOT use for pure research or one-off questions unrelated to code-style alignment. |
| intent-driven-development | intent-driven-development | Turn ambiguous or high-impact product and engineering changes into scoped, verifiable acceptance criteria before or alongside implementation. Use when a user asks to clarify a feature, define acceptance criteria, de-risk a security/data/migration/integration change, prepare implementation requirements for another agent, or make a complex request testable. Do not trigger for trivial edits, straightforward fixes, active debugging, code review, or implementation requests whose acceptance conditions are already clear unless the user explicitly invokes this skill. |
| ios-icon-gen | ios-icon-gen | Generate iOS app icons as PNG imagesets for Xcode asset catalogs from SF Symbols (5000+ Apple-native) or Iconify API (275k+ open source icons from 200+ collections). Use when generating icons, creating icon assets, adding icons to asset catalog, or searching for icons for iOS projects. |
| jupyter-live-kernel | jupyter-live-kernel | Iterative Python via live Jupyter kernel (hamelnb). |
| karpathy-guidelines | karpathy-guidelines | Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria. |
| kubernetes-patterns | kubernetes-patterns | Kubernetes workload patterns, resource management, RBAC, probes, autoscaling, ConfigMap/Secret handling, and kubectl debugging for production-grade deployments. |
| lark-approval | lark-approval | 飞书审批：查询和处理审批待办/已办/实例，搜索可发起审批定义、查看定义详情并发起原生审批实例。当用户要处理审批任务、查看审批实例、搜索或发起审批时使用。审批待办不是飞书任务；非审批类待办走 lark-task。不负责创建审批定义；三方审批定义不走原生提单。 |
| lark-apps | lark-apps | 妙搭（Spark/Miaoda）应用开发与托管：应用创建、HTML静态站点发布、本地全栈开发、云端生成迭代、AI相关能力和飞书平台能力或者其他外部能力集成、日志/Trace/监控指标/PV/UV 查询、环境变量管理。当用户要开发/新建一个系统·工具·平台·应用，或要本地开发 / 云端开发 / 修改 / 部署 / 发布 / 上线 / 拿可分享链接，或用 HTML 做页面·网站·部署到妙搭，或提到妙搭/Spark/Miaoda（应用运行时域名形如 *.aiforce.cloud）、应用数据库、应用文件存储、开放 API Key、可见范围、线上日志、接口请求量、错误量、延迟、访问量、环境变量时使用。不负责普通云盘文件上传（lark-drive）、飞书文档编辑（lark-doc）、原生幻灯片创建（lark-slides）。 |
| lark-attendance | lark-attendance | 飞书考勤打卡：查询自己的考勤打卡记录 |
| lark-base | lark-base | 飞书多维表格（Base）操作：建表、字段、记录、视图、统计、公式/lookup、表单、仪表盘、workflow、角色权限；遇到 Base/多维表格/bitable 或 /base/ 链接时使用。文件导入转 lark-drive，认证/授权转 lark-shared。 |
| lark-calendar | lark-calendar | 飞书日历：管理日历日程和会议室。查看/搜索日程、创建/更新日程、管理参会人、查询忙闲和推荐时段、预定会议室。当用户需要查看日程安排、创建/修改会议、查询/预定会议室时使用。不负责：查询过去的视频会议记录（走 lark-vc）、待办任务（走 lark-task）。 |
| lark-contact | lark-contact | 飞书 / Lark 通讯录:按姓名 / 邮箱解析成 open_id,或按 open_id 反查姓名 / 部门 / 邮箱 / 联系方式 / 个人状态 / 签名。当用户提到某人姓名要下一步发消息 / 排日程,或拿到 open_id 想查具体信息时使用。不负责部门树遍历、按部门列员工、组织架构图,这类需求走原生 OpenAPI。 |
| lark-doc | lark-doc | 飞书云文档（Docx / Wiki 文档）：读取和编辑飞书文档内容。当用户给出文档 URL 或 token，或需要查看、创建、编辑文档、插入或下载文档图片附件时使用。文档中嵌入的电子表格、多维表格、画板，先用本 skill 提取 token 再切到对应 skill。当用户给出 doubao.com 的 /docx/ 或 /wiki/ URL/token 时，也应直接使用本 skill；路由依据是 URL 路径模式和 token，而不是域名。不负责文档评论管理，也不负责表格或 Base 的数据操作。当用户明确要操作飞书思维笔记时，也使用本 skill。 |
| lark-drive | lark-drive | 飞书云空间（云盘/云存储）：管理 Drive 文件和文件夹，包含上传/下载、创建文件夹、复制/移动/删除、查看元数据、评论/权限/订阅、标题、版本和本地文件导入。用户需要整理云盘目录、处理云空间资源 URL/token，或导入 Word/Markdown/Excel/CSV/PPTX/.base 为 docx/sheet/bitable/slides 时使用；doubao.com 云空间 URL/token 也按资源路径和 token 路由，不回退 WebFetch。不负责：文档内容编辑（走 lark-doc）、表格/Base 表内数据操作（走 lark-sheets/lark-base）、知识空间节点/成员管理（走 lark-wiki）、原生 Markdown 文件读写/patch/diff（走 lark-markdown）。 |
| lark-event | lark-event | Lark/Feishu real-time event listening / subscribing / consuming: stream events as NDJSON via `lark-cli event consume <EventKey>` (covers IM messages/reactions/chat changes, Task updates, VC meeting started/joined/ended, Minutes generated, Whiteboard updated, etc.). Use for Lark bots, real-time message processing, long-running subscribers, streaming webhook/push handlers. Supports `--max-events` / `--timeout` bounded runs and a stderr ready-marker contract — designed for AI agents running as subprocesses. |
| lark-im | lark-im | 飞书即时通讯：收发消息和管理群聊。发送和回复消息、搜索聊天记录、管理群聊成员、上传下载图片和文件（支持大文件分片下载）、管理表情回复、发送应用内/短信/电话加急、发送和处理交互卡片（Interactive Card）、监听卡片按钮回调（card.action.trigger）。当用户需要发消息、查看或搜索聊天记录、下载聊天中的文件、查看群成员、搜索群、创建群聊或话题群、管理标记数据、管理 Feed 置顶（添加/移除/查询置顶会话）、管理标签数据、处理卡片回调时使用。 |
| lark-mail | lark-mail | 飞书邮箱：Use when user mentions 起草邮件、写邮件、草稿、发送/回复/转发邮件、查阅邮件、看邮件、搜索邮件、邮件文件夹、邮件标签、邮件联系人、监听新邮件、邮件收信规则等；use for mail/email intent only. Do not use for docs/sheets/calendar/auth setup/pure contact lookup/IM chat tasks. |
| lark-markdown | lark-markdown | 飞书 Markdown：查看、创建、上传、编辑和比较 Markdown 文件。当用户需要创建或编辑 Markdown 文件、读取、修改、局部 patch 或比较差异时使用。不负责将 Markdown 导入为飞书在线文档，也不负责文件搜索、权限、评论、移动、删除等云空间管理操作。 |
| lark-minutes | lark-minutes | 飞书妙记：搜索妙记、查看妙记基础信息、下载/上传音视频、读取或编辑妙记的产物内容、改标题、替换说话人/关键词。当给出minute_token、本地音视频文件，要查/改/转妙记产物时使用；本地音视频转纪要/逐字稿优先走本 skill，不要用 ffmpeg/whisper 本地转写。不负责：获取会议关联妙记，或仅按自然语言标题定位纪要 |
| lark-okr | lark-okr | 飞书 OKR：管理目标与关键结果。查看和编辑 OKR 周期、目标、关键结果、对齐关系、量化指标和进展记录。当用户需要查看或创建 OKR、管理目标和关键结果、查看对齐关系时使用。不负责：待办任务管理（lark-task）、日程/会议安排（lark-calendar）、绩效评估 |
| lark-openapi-explorer | lark-openapi-explorer | 飞书/Lark 原生 OpenAPI 探索：从官方文档库中挖掘未经 CLI 封装的原生 OpenAPI 接口。当用户的需求无法被现有 lark-* skill 或 lark-cli 已注册命令满足，需要查找并调用原生飞书 OpenAPI 时使用。 |
| lark-shared | lark-shared | Use for lark-cli setup/auth tasks: auth login/status/logout, user vs bot identity, business-domain permissions (--domain, including all/docs/drive), missing scopes, revoking authorization, or handling _notice JSON. |
| lark-sheets | lark-sheets | 飞书电子表格：创建和操作电子表格。支持创建表格、管理工作表与行列结构（增删/合并/调整尺寸/隐藏/冻结）、读写单元格（值/公式/样式/批注/单元格图片）、查找替换、多操作原子批量更新，以及图表、透视表、条件格式、筛选器、迷你图、浮动图片等对象的创建与维护。当用户需要创建电子表格、管理工作表、批量读写或编辑数据、统计汇总与可视化、表格美化、公式计算（含 Excel 公式迁移）、金融/财务建模（DCF、三张表、预算、Sensitivity 等）等任务时使用。若用户是想按名称或关键词搜索云空间（云盘/云存储）里的表格文件，请改用 lark-drive 的 drive +search 先定位资源。当用户给出 doubao.com 的 /sheets/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。 |
| lark-skill-maker | lark-skill-maker | 创建 lark-cli 的自定义 Skill。当用户需要把飞书 API 操作封装成可复用的 Skill（包装原子 API 或编排多步流程）时使用。 |
| lark-slides | lark-slides | 飞书幻灯片：创建和编辑幻灯片。创建演示文稿、读取幻灯片内容、管理幻灯片页面（创建、删除、读取、局部替换）。当用户需要创建或编辑幻灯片、读取或修改单个页面时使用。当用户给出 doubao.com 的 /slides/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。不负责：云文档内容编辑（走 lark-doc）、云文档里的独立画板对象（走 lark-whiteboard，注意 slide 内嵌的流程图/架构图仍属本 skill）、上传或下载普通文件（走 lark-drive）。 |
| lark-task | lark-task | 飞书任务：管理任务、清单和任务智能体。创建待办任务、查看和更新任务状态、拆分子任务、组织任务清单、分配协作成员、上传任务附件、注册或注销任务智能体、更新任务智能体的主页数据、写入智能体任务记录。当用户需要创建待办事项、查看任务列表、跟踪任务进度、管理项目清单或给他人分配任务、为任务上传附件文件、注册注销任务智能体、更新智能体主页数据、写入任务记录时使用。 |
| lark-vc | lark-vc | 飞书视频会议：搜索历史会议记录、查询会议纪要（总结/待办/章节/逐字稿）、查询参会人快照。当用户查询已结束的会议、获取会议产物（纪要/妙记）、查看参会人时使用；查询未来日程走 lark-calendar。不负责：Agent 真实入会/离会、会中实时事件（走 lark-vc-agent）。 |
| lark-vc-agent | lark-vc-agent | 飞书视频会议会中能力：用于让应用机器人真实加入或离开正在进行的会议，并读取当前身份可见的会中事件、发送会中文本消息或会中表情。适用于用户询问正在开的会议发生了什么、谁在发言、是否共享内容，或需要发现当前可读的进行中会议 ID。不负责已结束会议搜索、参会人快照、纪要、逐字稿或录制查询，这些使用 lark-vc 技能。 |
| lark-whiteboard | lark-whiteboard | 飞书画板：查询和编辑飞书云文档中的画板。支持导出画板为预览图片、导出原始节点结构、使用多种格式更新画板内容。 当用户需要查看画板内容、导出画板图片、编辑画板时使用此 skill。不负责：飞书云文档内容编辑（lark-doc）、文档内嵌电子表格/Base（lark-sheets / lark-base）。 |
| lark-wiki | lark-wiki | 飞书知识库：管理知识空间、空间成员和文档节点。创建和查询知识空间、查看和管理空间成员、管理节点层级结构、在知识库中组织文档和快捷方式。当用户需要在知识库中查找或创建文档、浏览知识空间结构、查看或管理空间成员、移动或复制节点时使用。当用户给出 doubao.com 的 /wiki/ URL/token 时，也应直接使用本 skill，不要因为域名不是飞书而回退到 WebFetch；路由依据是 URL 路径模式和 token，而不是域名。不负责：上传文件到知识库节点下（走 lark-drive）、编辑文档/表格/Base 内容（走 lark-doc / lark-sheets / lark-base）。 |
| lark-workflow-meeting-summary | lark-workflow-meeting-summary | 会议纪要整理工作流：汇总指定时间范围内的会议纪要并生成结构化报告。当用户需要整理会议纪要、生成会议周报、回顾一段时间内的会议内容时使用。 |
| lark-workflow-standup-report | lark-workflow-standup-report | 日程待办摘要：编排 calendar +agenda 和 task +get-my-tasks，生成指定日期的日程与未完成任务摘要。适用于了解今天/明天/本周的安排。 |
| marketing-campaign | marketing-campaign | End-to-end marketing campaign planning and execution. Covers audience research, positioning, campaign angle definition, landing page copy, email sequences, social posts, ad copy, short-form video scripts, and content calendars. Use as the orchestration layer for multi-channel product launches. |
| ml-paper-reader-cn | ml-paper-reader-cn | Chinese structured close reading of machine learning, AI, deep learning, NLP, CV, benchmark, systems, and technical research papers, with detailed experiment extraction. Use when the user asks in Chinese or English to read, summarize, explain, analyze, or take notes on a single paper, arXiv link, PDF, Hugging Face paper page, academic article, technical blog, or report, especially when they want sections such as purpose, challenges, method, key concepts, contributions, experiments, conclusion, limitations, and future work. |
| motion-advanced | motion-advanced | Advanced motion patterns for React / Next.js — drag & drop, gestures, text animations, SVG path drawing, custom hooks, imperative sequences (useAnimate), loaders, and the full API decision tree. Requires motion-foundations. |
| motion-foundations | motion-foundations | Motion tokens, spring presets, performance rules, device adaptation, accessibility enforcement, and SSR safety for React / Next.js using motion/react. Foundation layer — all other motion skills depend on this. |
| motion-patterns | motion-patterns | Production-ready animation patterns for React / Next.js — button, modal, toast, stagger, page transitions, exit animations, scroll, and layout — built on motion-foundations tokens and springs. |
| nextjs-turbopack | nextjs-turbopack | Next.js 16+ and Turbopack — incremental bundling, FS caching, dev speed, and when to use Turbopack vs webpack. |
| nuxt4-patterns | nuxt4-patterns | Nuxt 4 app patterns for hydration safety, performance, route rules, lazy loading, and SSR-safe data fetching with useFetch and useAsyncData. |
| openclaw-persona-forge | openclaw-persona-forge | 为 OpenClaw AI Agent 锻造完整的龙虾灵魂方案。根据用户偏好或随机抽卡， 输出身份定位、灵魂描述(SOUL.md)、角色化底线规则、名字和头像生图提示词。 如当前环境提供已审核的生图 skill，可自动生成统一风格头像图片。 当用户需要创建、设计或定制 OpenClaw 龙虾灵魂时使用。 不适用于：微调已有 SOUL.md、非 OpenClaw 平台的角色设计、纯工具型无性格 Agent。 触发词：龙虾灵魂、虾魂、OpenClaw 灵魂、养虾灵魂、龙虾角色、龙虾定位、 龙虾剧本杀角色、龙虾游戏角色、龙虾 NPC、龙虾性格、龙虾背景故事、 lobster soul、lobster character、抽卡、随机龙虾、龙虾 SOUL、gacha。 |
| opensource-pipeline | opensource-pipeline | Open-source pipeline: fork, sanitize, and package private projects for safe public release. Chains 3 agents (forker, sanitizer, packager). Triggers: '/opensource', 'open source this', 'make this public', 'prepare for open source'. |
| orch-add-feature | orch-add-feature | Orchestrate building a brand-new feature end to end — research, plan, TDD implementation, review, and gated commit — by delegating each phase to the matching ECC agent. Use when adding a capability that does not exist yet. |
| orch-build-mvp | orch-build-mvp | Orchestrate bootstrapping a working MVP from a design or spec document — ingest the doc, plan thin vertical slices, scaffold the first end-to-end slice, then TDD-implement, review, and gated commit. Use to turn an SDD/PRD into a running starting point. |
| orch-change-feature | orch-change-feature | Orchestrate altering an existing, working feature to new desired behavior — update its tests to the new spec, change the implementation to match, review, and gated commit. Use when behavior is not broken but should be different. |
| orch-fix-defect | orch-fix-defect | Orchestrate fixing a bug — reproduce it as a failing regression test, fix to green, review, and gated commit — by delegating each phase to the matching ECC agent. Use when existing behavior is broken or wrong. |
| orch-pipeline | orch-pipeline | Shared orchestration engine for the orch-* skill family. Defines the gated Research-Plan-TDD-Review-Commit pipeline, the size classifier, the agent map, and the two human gates that the orch-* operation skills delegate to. Not usually invoked directly. |
| orch-refine-code | orch-refine-code | Orchestrate a behavior-preserving refactor — confirm tests are green, restructure without changing behavior, keep tests green, review, and gated commit. Use when the structure should improve but behavior must not change. |
| plan | plan | Plan mode: write an actionable markdown plan to .hermes/plans/, no execution. Bite-sized tasks, exact paths, complete code. |
| plan-orchestrate | plan-orchestrate | Read a plan document, decompose it into steps, design a per-step agent chain from the ECC catalogue, and emit ready-to-paste /orchestrate custom prompts. Generative only — never invokes /orchestrate itself. Use when the user has a multi-step plan and wants to drive it through orchestrate without composing chains by hand. |
| popular-web-designs | popular-web-designs | 54 real design systems (Stripe, Linear, Vercel) as HTML/CSS. |
| powerpoint | powerpoint | Create, read, edit .pptx decks, slides, notes, templates. |
| product-lens | product-lens | Use this skill to validate the "why" before building, run product diagnostics, and pressure-test product direction before the request becomes an implementation contract. |
| pytorch-patterns | pytorch-patterns | PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data loading. |
| react-performance | vercel-react-best-practices | React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements. |
| recsys-pipeline-architect | recsys-pipeline-architect | Designs composable recommendation, ranking, and feed pipelines using the six-stage Source→Hydrator→Filter→Scorer→Selector→SideEffect framework popularized by X's open-sourced For You algorithm. Use this skill when the user wants to build any system that picks "the top K items for a user/context" — content feeds, search ranking, task prioritization, notification ordering, RAG retrieval ranking, alert triage, ad selection. Produces a stage-by-stage spec, an interface definition in the user's target language, and a runnable scaffold. Triggers: "recommendation system", "feed algorithm", "ranking pipeline", "for you feed", "how should I rank X", "candidate pipeline", "content recommender", "pipeline architecture for recsys". |
| redis-patterns | redis-patterns | Redis data structure patterns, caching strategies, distributed locks, rate limiting, pub/sub, and connection management for production applications. |
| repo-scan | repo-scan | 对指定项目源码目录执行全面资产审计，生成《全网模块与源码资产审计详细清单》。当用户要求"审计源码"、"盘点代码资产"、"生成清单"时自动触发。 |
| research-paper-writing | research-paper-writing | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| rules-distill | rules-distill | Scan skills to extract cross-cutting principles and distill them into rules — append, revise, or create new rule files |
| safety-guard | safety-guard | Use this skill to prevent destructive operations when working on production systems or running agents autonomously. |
| santa-method | santa-method | Multi-agent adversarial verification with convergence loop. Two independent review agents must both pass before output ships. |
| serenity-aleabitoreddit | serenity-aleabitoreddit | Apply trader Serenity's (@aleabitoreddit) AI/semiconductor supply-chain analytical lens to US-stock ideas and market judgment. Use this skill whenever evaluating a stock decision (buy / sell / hold / size); forming an outlook on any AI, semiconductor, optical/CPO, memory, power/grid, or neocloud name; mentioning any ticker in Serenity's universe (NBIS, AXTI, LITE, SIVE, COHR, AAOI, IREN, CRWV, MU, SNDK, NVDA, TSM, MRVL, AVGO, INTC, SOI, IQE, TSEM, CIFR, XLU, VST, CEG, EWY, etc.); asking "what would Serenity think", "is this a real bottleneck", or wanting a supply-chain / bottleneck read on a thesis. Decision-support only — never auto-trades and never places or cancels orders. |
| serenity-chokepoint-investing | serenity-chokepoint-investing | Use when analyzing stocks through @aleabitoreddit/Serenity-style supply-chain chokepoint thinking: AI/semi photonics, scarce physical bottlenecks, small-cap monopoly or duopoly nodes, catalyst timing, valuation mismatch, and risk controls. This skill supports investment research and stock analysis; it does not provide personalized financial advice. |
| serenity-method | serenity-method | Apply @aleabitoreddit ("Serenity")'s distilled stock-analysis method to ANY ticker, sector, or situation — critical-chokepoint / supply-chain-OSINT idea discovery, first-principles value-chain decomposition, a Buffett-style quality gate (moat / profitability / customer-replacement risk, all default unverified), and narrative-vs-fundamentals hygiene. Produces a beginner-friendly Chinese analysis (她的观点 / 小白解释 / 第一性原理 / Buffett 直接判断 / 当前结论) that classifies an idea as 研究地图 vs 可投资结论. Trigger on "analyze like Serenity / 用 aleabito 的方法分析 / 用 Serenity 框架 / critical chokepoint 分析 / 第一性原理 + Buffett 判断这只股 / supply-chain bottleneck thesis". Never emits buy/sell calls. |
| serenity-radar | serenity-radar | Use @aleabitoreddit ("Serenity")'s full mention archive (built by the follow-aleabito skill) to anticipate where her attention is moving and generate candidate ideas in her style. Two modes — (1) RADAR reads the live mention data for attention momentum (which tickers she is heating up on, new entrants, conviction core, theme rotation) via scripts/radar.js; (2) GENERATOR applies her empirically-mined patterns (theme-rotation logic, selection signature, catalyst playbook) to propose her likely next focus. Every candidate is gated through the serenity-method checklist. This is a CANDIDATE GENERATOR + CHECKLIST, never an oracle or buy/sell signal. Trigger on "what is Serenity ramping on / her next pick / aleabito radar / predict her next move / generate ideas like her / 她下一个可能看什么". |
| serenity-reply | serenity-reply | Serenity (@aleabitoreddit) 的思维框架与表达方式。基于 6 维度深度调研（1700+ 推文、Substack 长访谈、第三方分析、批评者观点）， 提炼 5 个核心心智模型、8 条决策启发式和完整的表达 DNA。 用途：作为 AI/半导体供应链投资的思维顾问，用 Serenity 的视角分析投资标的、审视决策、提供反馈。 当用户提到「用 Serenity 的视角」「aleabitoreddit 会怎么看」「Serenity 模式」「Serenity perspective」「用 aleabitoreddit 的角度」时使用。 即使用户只是说「帮我用 Serenity 的角度想想」「如果 Serenity 会怎么做」「切换到 Serenity」也应触发。 |
| serenity-skill | serenity-skill | Turn an investment agent into a supply-chain bottleneck hunter. Use this skill for source-backed investment research, live market/theme scans, AI/semi/technology value-chain mapping, A-share/HK/US stock screening, thesis stress tests, and Serenity-inspired research conversations. Trigger on requests like "用 Serenity 的方式看", "深度调研", "产业链/供应链/卡点/瓶颈", "A股 AI 半导体哪个最值得研究", "find unknown bottlenecks", "rank candidates", or "challenge this thesis". Outputs plain-language reasoning, ranked research priorities, evidence chains, risks, and next verification steps. Research support only; no trade execution. |
| serenity-skill-0xagata | serenity-skill-0xagata | > *Distilled from 4,740 tweets by @aleabitoreddit — supply chain analyst, retail investor champion, photonics supercycle caller.* |
| serenity-stock-choke | serenity-stock-choke | A股通用"卡脖子"选股技能。应用 Serenity（@aleabitoreddit）的供应链瓶颈理论， 对任意 A 股板块/产业链进行结构化分析，寻找"一旦断货整个产业就停工"的瓶颈环节， 并筛选该环节中具备技术壁垒和资本信号的小盘股。 触发词：分析XX板块、找XX卡脖子、serenity分析、A股瓶颈产业链 适用板块示例：电力、光模块、医疗器械、半导体设备、军工、新能源车等任意板块 数据源：neodata-financial-search（行情/研报/资金）+ westock-data（筹码/大宗/机构） ⚠️ 注意：本技能不预测大盘走势，不适用于纯题材炒作无实质产业逻辑的小票。 |
| serenity-stock-scorer | serenity-stock-scorer | Score a stock from 0-100 using the local Serenity Signal Ledger tweet corpus. Use when a user asks to rate, rank, analyze, or triage a ticker based on Serenity/X tweet evidence, cashtag mentions, Serenity-style AI supply-chain theses, or the project-local `data/serenity.sqlite` or `api/instance/serenity.sqlite` snapshot. |
| serenity-zadanthony | serenity | 用 Serenity(@aleabitoreddit)的"供应链卡点逆向"投资逻辑分析股票/板块——帮你判断该怎么分析、往哪一层挖、什么会证实或证伪、值不值得投。把市场当物理系统而非代码列表,先建 thesis 再谈标的。当用户聊美股/AI 供应链/光模块(CPO/硅光/InP)/半导体/内存/NeoCloud/电力液冷/机器人等 AI 全产业链任意细分的投资分析,或主动 /serenity 时使用。 |
| serenity-zongmin-yu | serenity | Activates AI infrastructure and semiconductor supply chain analysis. Trigger when: tracing hyperscaler AI capex to find bottleneck companies, analyzing semiconductor/photonics/memory/packaging supply chains, mapping BOM dependencies for AI hardware (GPUs, TPUs, ASICs, optical interconnects, HBM), evaluating supplier concentration in chip materials or critical components, asking "who controls the critical input for AI buildout," or identifying small companies that trillion-dollar AI deployments depend on. Even if the user does not mention "Serenity," proactively trigger when the topic involves AI infrastructure supply chain analysis, semiconductor bottleneck mapping, or upstream supplier tracing for AI hardware. |
| sketch | sketch | Throwaway HTML mockups: 2-3 design variants to compare. |
| skill-comply | skill-comply | Visualize whether skills, rules, and agent definitions are actually followed — auto-generates scenarios at 3 prompt strictness levels, runs agents, classifies behavioral sequences, and reports compliance rates with full tool call timelines |
| social-publisher | social-publisher | Agent-driven scheduling and publishing of social media posts across 13 platforms via SocialClaw. Use when the user wants to publish to X, LinkedIn, Instagram, Facebook Pages, TikTok, Discord, Telegram, YouTube, Reddit, WordPress, or Pinterest — or when managing campaigns, uploading media, or monitoring post delivery status. |
| tinystruct-patterns | tinystruct-patterns | Expert guidance for developing with the tinystruct Java framework. Use when working on the tinystruct codebase or any project built on tinystruct — including creating Application classes, @Action-mapped routes, unit tests, ActionRegistry, HTTP/CLI dual-mode handling, the built-in HTTP server, the event system, JSON with Builder/Builders, database persistence with AbstractData, POJO generation, Server-Sent Events (SSE), file uploads, and outbound HTTP networking. |
| token-budget-advisor | token-budget-advisor | Analyze prompts and offer depth / token-budget options BEFORE answering. Use this skill when the user wants to control token usage, tune response depth, choose between short and long answers, or optimize their prompt. Triggers on: "tokens", "token budget", "depth", "consumption", "short vs long answer", "how many tokens", "save tokens", "answer at 50%", "give me the short version", "I want to control how much you use", "tune your response", "presupuesto de tokens", "profundidad", "responde al 50%", "dame la versión corta", or any equivalent phrasing in English or Spanish. If the user wants to control length, detail or depth -- even without mentioning tokens explicitly -- this skill applies. |
| uncloud | uncloud | Use when managing an Uncloud cluster — deploying services, configuring Caddy ingress, adding static proxy routes for non-cluster devices, publishing ports, scaling, inspecting logs, or managing machines and volumes with the `uc` CLI. |
| vite-patterns | vite-patterns | Vite build tool patterns including config, plugins, HMR, env variables, proxy setup, SSR, library mode, dependency pre-bundling, and build optimization. Activate when working with vite.config.ts, Vite plugins, or Vite-based projects. |
| zotero-paper-curator | zotero-paper-curator | Add or update machine learning papers in the user's local Zotero library, choose suitable existing collections, attach a PDF, add a Chinese paper summary as a Zotero child note, and apply high-quality tags. Use when the user asks to add a summarized paper, arXiv/PDF paper, or paper reading note to Zotero; classify a paper in Zotero; or reuse/create Zotero tags based on paper semantics. |
