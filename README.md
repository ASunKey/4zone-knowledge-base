# Four-Zone Knowledge Base（四区模式知识库）

> 一套把零散资料变成**可持续增长的结构化知识库**的 AI 技能包（Skills）。
> 沉淀自多个真实知识库空间的长期实践，跨 Agent 通用（WorkBuddy / Claude Code / Cursor / CodeBuddy 等）。

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 这是什么

「四区模式」是一种用 AI 长期维护知识库的组织方法。它把知识库拆成四个职责清晰的目录，解决"资料、思考、产出、结论混在一起"导致知识库膨胀后失序的问题。

| 区 | 目录 | 放什么 | 变更规则 |
|----|------|--------|----------|
| 区一 | `raw/` | 外部来源：抓取文章、指南 PDF、电子书、政策原文、年报 | **不可变**，是"真理来源" |
| 区二 | `reflections/` | 思考沙盒成稿：讨论稿、推演、审核报告 | **按指令落盘**，AI 不自动写 |
| 区三 | `results/` | 结果文章：编译产出、成稿、书稿、报告 | 脚本 / 收敛产出 |
| 区四 | `wiki/` | 概念页：主题域交叉引用的知识图谱 | AI 编写维护 |

流转链：

```
外部来源 ──摄取──▶ raw/（区一）
                     │ 讨论（不落盘）
                     ▼
              reflections/（区二）──按指令落盘
                     │ Compile / 汇聚
                     ▼
              results/（区三）──成稿
                     │ 提炼稳定
                     ▼
              wiki/（区四）──正式知识
```

**它解决的核心问题**：区分「别人说的」（raw）、「我们想的」（reflections）、「我们产出的」（results）、「我们确认的」（wiki）。

**方法论底座**：
- **Karpathy llm_wiki** —— Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库；核心操作 = Ingest / Query / Lint。
- **Google OKF（Open Knowledge Format）** —— 一概念一文件 + YAML frontmatter + 保留文件名 + 宽松一致性。

---

## 仓库结构

```
four-zone-knowledge-base/
├── README.md                                  ← 本文件
├── LICENSE                                    ← MIT 许可
├── skills/                                    ← 核心技能包（Agent/系统无关）
│   ├── four-zone-scaffold/                    ← 【总纲】四区模式权威基础库
│   │   └── SKILL.md
│   └── llm-wiki-okf-bootstrap/                ← 【执行手册】多语种采集/专题子区/confidence/Compile
│       └── SKILL.md
└── workbuddy-extras/                          ← WorkBuddy 专用可选扩展（非 WorkBuddy 用户可忽略）
    ├── README.md
    ├── skills/migrate-workbuddy-space/        ← 空间跨机/跨路径迁移
    └── scripts/
        ├── backup_tasks.py                    ← 任务历史 → 项目内镜像
        ├── migrate_sessions.py                ← 跨机迁移 + 路径改写
        └── verify_migration.py                ← 迁移后校验
```

### 核心技能的分层关系

| 技能 | 层级 | 何时用 |
|------|------|--------|
| `four-zone-scaffold` | **总纲** | 搭任何新知识库、升级已有项目、把握全貌与硬性规则 |
| `llm-wiki-okf-bootstrap` | 执行手册 | 深入执行：多语种采集、榜单/企业/爆款专题、confidence 判定、Compile 出成品 |

> 两个核心技能**完全 Agent 无关、系统无关**：只用「目录 + Markdown + 纯标准库脚本」，
> 可在任何 Agent（Claude Code / Cursor / CodeBuddy / WorkBuddy 等）与任何系统（Windows / macOS / Linux）上使用。
>
> `workbuddy-extras/` 是**可选扩展**，仅服务 WorkBuddy / CodeBuddy 用户的空间迁移场景，与核心方法相互独立。

---

## 快速开始

### 1. 安装技能

把 `skills/` 下你需要的技能目录，复制到你的 Agent 的技能目录：

| Agent | 用户级技能目录（全局可用） | 项目级技能目录 |
|-------|---------------------------|----------------|
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **Cursor** | `~/.cursor/skills/`（或 `.cursor/rules`） | `.cursor/skills/` |
| **WorkBuddy / CodeBuddy** | `~/.workbuddy/skills/` | `<项目>/.workbuddy/skills/` |
| **Hermes** | `~/.hermes/skills/<category>/` | 项目内任意位置 |
| **其他（通用）** | 任意目录，加到 Agent 的技能搜索路径 | `<项目>/skills/` |

> **最小安装**：只需要 `four-zone-scaffold` 一个技能即可搭出完整框架。
> 需要深入执行多语种采集、专题研究、出成品时，再加 `llm-wiki-okf-bootstrap`。
>
> 这两个核心技能**与具体 Agent 无关**——只要你的 Agent 支持「目录 + SKILL.md（YAML frontmatter）」的技能格式即可。
> 若你的 Agent 不叫上述名字，把技能目录放到它识别技能的位置即可，无需任何改动。
>
> 技能 frontmatter 已包含 Hermes 的 `metadata.hermes`（tags/category/related_skills）与 `version`/`platforms` 字段，
> 因此也支持 Hermes 的渐进式披露（先看摘要、命中才加载全文）与按平台筛选。

### 2. 触发搭建

装好后，对 Agent 说一句：

```
用四区模式给这个项目搭一个知识库框架
```

Agent 会自动加载技能里的完整流程，建好目录、写出全部规范文档，并给你一份校验汇报。

### 3. 搭建后的目录长什么样

```
<你的项目>/
├── AGENTS.md              ← Schema 层：架构与操作规范（最重要）
├── index.md               ← 四区总索引
├── log.md                 ← 变更日志（仅追加）
├── README.md              ← 项目说明
├── okf.yaml               ← OKF 配置（可选）
├── raw/                   ← 区一：外部来源（不可变）
├── reflections/           ← 区二：思考沙盒
├── results/               ← 区三：结果文章
├── wiki/                  ← 区四：概念页
├── scripts/               ← 工具脚本
└── .kb/                   ← 项目级元数据（跨系统安全，随项目迁移）
```

---

## 用什么工具承载（Obsidian 推荐，但不锁定）

四区模式产出的是**纯 Markdown 文件**，本身与软件无关。日常最契合的承载工具是 **Obsidian**（也是 Karpathy llm_wiki 的原生设想）：

| Obsidian 能力 | 服务四区模式 |
|---------------|--------------|
| 本地文件夹即库 | 直接把项目根目录当 vault 打开，四区天然呈现 |
| 双链 `[[概念]]` | 与 OKF「一概念一文件 + 交叉引用」同构，形成知识图谱 |
| 图谱视图 | 直观看到四区流转与概念关联 |
| frontmatter 原生支持 | 直接读写 `type`/`confidence`/`status` 等 YAML |
| 全文检索 / 反向链接 | 对应 llm_wiki 的 Query |

**接入**：Obsidian → 打开文件夹作为库 → 选项目根目录，零配置。

其他可选：Logseq（大纲式双链）、Notion / 飞书（在线协作但弱化可移植性）、Typora / VS Code（纯读写）。

> **核心原则：知识库本体永远是可移植的纯 Markdown，工具只是「看它的镜头」——换了镜头，知识不丢。**

---

## 关键约定（决定了它能不能长期用下去）

1. **`raw/` 不可变** —— AI 产出一律不进 raw，它是"事实"层。
2. **`reflections/` 不自动落盘** —— 只在人明确下令时才写文件，避免闲聊污染知识库。
3. **每个 `.md` 都带 OKF frontmatter**，`type` 字段必填。
4. **文件命名用 kebab-case 英文（ASCII slug）** —— 跨平台同步安全；标题正文照常用中文。
5. **交叉引用用包根绝对路径** —— 文件移动后仍稳定。
6. **双源并列原则** —— 数据冲突时不合并、不取平均，两处都写并标注口径差异。
7. **`confidence` 诚实标注** —— 不确定就标 `low/medium`，宁可保守也不假装确定。
8. **删除 / 移动前先写回滚映射 CSV** —— 任何批量操作都能撤销。

---

## 关于 WorkBuddy 扩展（`workbuddy-extras/`）

仓库根部的两个核心技能**与系统、Agent 无关**。唯一与特定产品绑定的部分被单独拆到 `workbuddy-extras/`：

| 内容 | 作用 | 谁需要 |
|------|------|--------|
| `skills/migrate-workbuddy-space/` | 迁移 WorkBuddy 空间时保留任务历史 | 仅 WorkBuddy / CodeBuddy 用户 |
| `scripts/backup_tasks.py` 等三件套 | 任务历史镜像 / 跨机迁移 / 校验 | 仅 WorkBuddy / CodeBuddy 用户 |

> **如果你不用 WorkBuddy / CodeBuddy，直接忽略 `workbuddy-extras/` 即可**，核心方法不受任何影响。
> 详见 [`workbuddy-extras/README.md`](workbuddy-extras/README.md)。

---

## 从三层升级为四区（已有项目）

如果你已有 `raw/ + wiki/ + AGENTS.md` 的三层项目，技能会自动走"升级"流程：

1. 建 `reflections/` 和 `results/` 两个新目录
2. 把错位的 `raw/reflections/` 归位到根级 `reflections/`，编译产出归位到 `results/`
3. 全库替换引用路径，生成回滚映射 CSV
4. 新增 `index.md` / `log.md` / `README.md`，改写 `AGENTS.md` 为四区

**风险控制**：先 dry-run 列出将移动的文件与将修改的引用，确认后再执行。

---

## 常见问题

**Q：`results/` 和 `wiki/` 有什么区别？**
`results/` 是产出物（编译出的文章、书稿、报告），`wiki/` 是提炼后的稳定知识（概念页）。前者可以粗糙、可以带争议，后者要求收敛、可对外。

**Q：必须四个区都用吗？**
不必。最小可用是 `raw/` + `wiki/`。但目录先建好，避免后面迁移。

**Q：主题域要设几个？**
4-12 个为宜。太少说明领域没拆开，太多说明颗粒度太细。

**Q：能用于非知识库项目吗？**
四区模型是为"资料 → 知识"转化设计的。纯软件项目用标准代码目录结构更合适。

**Q：中文项目名会有问题吗？**
目录名建议用英文（跨平台同步更稳），标题和正文尽管用中文。

---

## 延伸阅读

- Karpathy, *llm_wiki* 方法论 —— Obsidian 是 IDE，LLM 是程序员，Wiki 是代码库
- Google Cloud, *Open Knowledge Format (OKF)* —— 一概念一文件 + YAML frontmatter

---

## 许可证

[MIT License](LICENSE) — 可自由使用、修改、分发。
