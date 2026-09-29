---
name: four-zone-scaffold
description: 知识库构建模式的权威基础库（总纲）。统一定义「四区模式」——raw（外部来源，不可变）/ reflections（思考沙盒，按指令落盘）/ results（Compile 成稿）/ wiki（概念页）——的目录骨架、根级四件套（AGENTS.md/index.md/log.md/README.md）、OKF frontmatter 规范与 .kb 元数据自包含约定。这是多个实战知识库空间共同演化出的构建模式的总纲，作为以后「通知构建」任何新知识库的统一依据。完全 Agent 无关、系统无关（不依赖任何特定 Agent 或操作系统）。当用户说"用四区模式搭一个知识库/新空间/项目框架""把这个项目初始化成知识库""知识库管理""构建知识库""通知构建""搭 wiki"时使用；也用于把已有三层（raw/wiki/AGENTS.md）项目升级为四区。深入执行细节（多语种采集、榜单/企业/爆款专题子区、confidence 四维判定、Compile 出成品等）见姊妹技能 llm-wiki-okf-bootstrap，本技能是它的总入口与分层顶层。
version: 2.0.0
author: The Four-Zone Knowledge Base Contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [knowledge-base, four-zone, okf, llm-wiki, scaffold]
    category: knowledge
    related_skills: [llm-wiki-okf-bootstrap]
agent_created: true
---

# 知识库构建模式总纲（four-zone-scaffold）

> 本技能是「知识库构建模式」的**权威基础库**。它沉淀自多个实战知识库空间共同演化出的约定，
> 作为以后**通知构建**任何新知识库的统一入口与依据。
>
> 分层关系：
> - **本技能（总纲）**：四区模型 + 目录骨架 + 根级四件套 + 关键约定 → 先读这里，把握全貌与硬性规则。
> - **`llm-wiki-okf-bootstrap`（执行手册）**：多语种采集、专题/聚焦子区、confidence 四维判定、Compile 出成品、踩坑记录 → 需要深入执行时再读。
> - **各项目自有技能**：单个知识库特有的工作流，留在各自项目内，不进本仓库。
>
> **本仓库完全 Agent 无关、系统无关**：核心技能只用「目录 + Markdown + 纯标准库脚本」，
> 可在任何 Agent（Claude Code / Cursor / CodeBuddy / WorkBuddy 等）与任何系统（Windows / macOS / Linux）上使用。

---

## 一、四区模型（先讲清，再动手）

| 区 | 目录 | 内容 | 变更规则 |
|----|------|------|----------|
| 区一 | `raw/` | 外部来源：抓取文章、指南 PDF、电子书、政策原文、年报 | **不可变**（真理来源，LLM 只读） |
| 区二 | `reflections/` | 思考沙盒成稿：讨论稿、推演、审核报告、ADR | **按指令落盘**，不自动写 |
| 区三 | `results/` | 结果文章：Compile 产出、成稿、书稿、报告 | 脚本/收敛产出，交付即定稿 |
| 区四 | `wiki/` | 概念页：主题域交叉引用知识图谱 | LLM 编写维护 |

流转链：`raw/` ──Ingest──▶ `reflections/`（讨论）──Compile──▶ `results/`（成稿）──提炼──▶ `wiki/`（正式知识）

**它解决的核心问题**：区分「别人说的」（raw）、「我们想的」（reflections）、「我们产出的」（results）、「我们确认的」（wiki）。四者混淆是知识库膨胀后失序的主因。

**方法论底座**：
- Karpathy **llm_wiki**：Obsidian=IDE，LLM=程序员，Wiki=代码库；核心操作 = Ingest / Query / Lint。
- Google **OKF**（Open Knowledge Format）：一概念一文件 + YAML frontmatter + 保留文件名 + 宽松一致性。

---

## 一点五、用 Obsidian 承载（推荐，但非强制）

四区模式产出的是**纯 Markdown 文件**，本身与任何软件解耦——你可以用任意编辑器/笔记软件打开。
但最契合的日常承载工具是 **Obsidian**（这也正是 Karpathy llm_wiki 的原生设想）：

| Obsidian 能力 | 如何服务四区模式 |
|---------------|------------------|
| **本地文件夹即库** | 直接把 `<项目>/` 作为 vault 打开，无需导入导出，raw/reflections/results/wiki 四区天然呈现 |
| **双链 `[[概念]]`** | 与 OKF「一概念一文件 + 交叉引用」同构；wiki 概念页互相 `[[ ]]` 即形成知识图谱 |
| **图谱视图（Graph View）** | 直观看到四区之间的流转与概念关联，正是「主题域交叉引用知识图谱」的可视化 |
| **frontmatter 原生支持** | 直接读取/编辑 YAML frontmatter（`type`/`confidence`/`status` 等），与 OKF 规范零摩擦 |
| **全文检索 / 反向链接** | 对应 llm_wiki 的 Query；反向链接面板即「谁引用了本页」 |
| **同步** | 文件是纯文本，可用任意同步工具（iCloud/坚果云/Syncthing/Git）跨设备 |

**接入方式**：Obsidian →「打开文件夹作为库」→ 选 `<项目>/` 根目录即可，无需任何配置改动。
raw/ 区建议在 Obsidian 里**只读**（或标记为附件库），reflections/results/wiki 由人 + LLM 共同编辑。

**其他可选承载**（按需）：Logseq（大纲式双链）、Notion / 飞书（在线协作，需迁移，弱化纯文本可移植性）、
Typora / VS Code（纯写作/开发视角）。**核心原则：知识库本体永远是可移植的纯 Markdown，工具只是「看它的镜头」——换了镜头，知识不丢。**

---

## 二、目录骨架（幂等，已存在只报告不删）

```bash
cd <项目根>
mkdir -p raw/{articles,guidelines,ebooks} \
         reflections results \
         wiki scripts/{scrapers,compilers,downloaders,utils} \
         .kb/{memory,skills,scripts}
```

完整骨架：

```
<项目>/
├── AGENTS.md              ← Schema 层（核心！人机共建）
├── index.md               ← 四区总索引（OKF 保留名）
├── log.md                 ← 变更日志（OKF 保留名，append-only）
├── README.md              ← 人类入口
├── okf.yaml               ← OKF 配置（profile: <project>-v1，可选）
├── raw/                   ← 区一：外部来源（不可变）
│   ├── README.md + index.md
│   ├── articles/  guidelines/  ebooks/
├── reflections/           ← 区二：思考沙盒
│   ├── README.md + _template.md + index.md
├── results/               ← 区三：Compile 成稿
│   ├── README.md + _template.md + index.md
├── wiki/                  ← 区四：概念页（LLM 完全拥有）
│   ├── index.md  overview.md
│   ├── domains/<域1..域N>/index.md
│   ├── concepts/  entities/  methods/  metrics/  synthesis/
├── scripts/               ← 零依赖工具（根目录不放 .py）
│   ├── README.md + okf_lint.py + build_index.py + wiki_search.py
│   ├── scrapers/  compilers/  downloaders/  utils/
└── .kb/                   ← 项目级元数据（随项目整体迁移，跨系统安全）
    ├── memory/            ← MEMORY.md（长期）+ YYYY-MM-DD.md（日志）
    ├── skills/            ← 项目专属技能（跨项目通用技能留用户级）
    └── scripts/           ← 项目专属工具脚本
```

> **每个子目录都要有 `index.md`**，否则 lint 会报坏链。

---

## 三、OKF frontmatter 规范（每个 `.md` 都带）

**唯一必填字段是 `type`。** 推荐 `title` / `description` / `resource` / `tags` / `timestamp`。

```yaml
---
type: concept              # 必填，非空
title: "概念名"
description: "单句摘要（用于 index 生成与检索片段）"
resource: https://...      # 底层资产 URI；抽象概念可省
tags: [a, b]
domain: <域slug>            # 本库扩展
sources:                    # 本库扩展：raw 层路径
  - raw/articles/xxx.md
related:                    # 本库扩展：显式 wiki 关联
  - wiki/concepts/yyy.md
confidence: medium          # 本库扩展：high/medium/low —— 证据强度诚实标注
status: seed                # 本库扩展：seed/growing/stable/stale
timestamp: 2026-09-28T11:00:00+08:00
---
```

**保留文件名**：`index.md`、`log.md`（不得作为概念文档）+ `AGENTS.md`、`okf.yaml`（本库约定）。

---

## 四、根级四件套（Schema 层最重要）

- **`AGENTS.md`**：项目身份 / 四区架构与各区职责 / wiki 目录结构 / OKF frontmatter 规范 / 核心操作（四区流转 + Ingest/Query/Lint）/ 命名与链接惯例 / index.md 与 log.md 格式约定 / 工具说明 / 共同演化清单。**必含第 7 节「约定与偏好」**（涉台港澳表述、文件命名、confidence 诚实标注、reflections 不自动落盘等硬规则固化于此）。
- **`index.md`**：四区总索引，含四区结构图 + 各区入口链接 + 最后更新行。带 `type: Index`。
- **`log.md`**：变更日志，仅追加。格式 `## [YYYY-MM-DD] 操作类型 | 描述`，操作类型限 `ingest|query|lint|build|refactor`。
- **`README.md`**：项目说明，含四区表格（区/目录/内容/**变更规则**）+ 快速导航 + 内容规模 + 相关链接。

---

## 五、各区 README 与模板（约定载体，别省）

- `raw/README.md`：**不可变**声明 + 子目录职责（外部来源才进这里，AI 产出不进 raw）。
- `reflections/README.md`：三阶段工作流（口头讨论不落盘 → 用户指令才落盘 → 阶段性汇聚）+ 文件命名 + 单篇模板。**必须写明「不主动写文件，只在用户下令时写」**。
- `reflections/_template.md`：`type: Reflection Note` / title / topic / date / status(draft|discussion|converged)。
- `results/README.md` + `results/_template.md`：`type: Result Article` + 摘要/正文/结论/晋升记录（含 `promoted_to`）。
- `wiki/index.md`：总索引，每行 `- [标题](相对路径) — 一句话描述`；每主题域一个 `index.md`。
- `scripts/README.md`：分类表 + 「根目录不放 .py」+ 运行方式约定。

---

## 六、`.kb/` 元数据自包含

项目级元数据统一放在 `.kb/` 目录内（`memory` / `skills` / `scripts`），**随项目整体迁移，不依赖全局环境、不绑定任何特定 Agent**：

| 目录 | 用途 |
|------|------|
| `.kb/memory/` | `MEMORY.md`（长期项目约定）+ `YYYY-MM-DD.md`（当日日志，append-only） |
| `.kb/skills/` | 项目专属技能（跨项目通用的技能应放用户级目录，而非塞进单个项目） |
| `.kb/scripts/` | 项目专属工具脚本 |

> 设计原则：**知识库应该自包含、可整目录拷贝迁移**。任何依赖「用户数据目录」「全局配置」的机制都会破坏可移植性——若某 Agent 有额外的会话/历史存储机制，请用「镜像备份」的思路把它同步进 `.kb/`，而不是反过来让知识库依赖它。

---

## 七、关键约定（硬性，决定了能不能长期用下去）

1. **`raw/` 不可变** —— AI 产出一律不进 raw；`raw/reflections/`、`raw/book/`、编译产出目录都是**错位**的典型。
2. **`reflections/` 不自动落盘** —— 讨论归讨论，只在人明确下令时才写。
3. **每个 `.md` 都带 OKF frontmatter**，`type` 必填 —— 检索/聚合/跨库迁移的基础。
4. **文件命名 kebab-case 英文（ASCII slug）** —— 跨平台（Windows↔macOS↔Linux）同步安全，避免 NFC/NFD 冲突；标题正文照常用中文。
5. **交叉引用用包根绝对路径** `[文本](/wiki/entities/example-entity.md)` —— 文件移动后仍稳定。
6. **双源并列原则** —— 数据冲突时**不合并、不取平均**，两处都写并标注口径差异。
7. **`confidence` 诚实标注** —— 不确定标 `low/medium`，并在「争议与不确定性」小节说明**缺什么**。
8. **脚本路径用 `Path(__file__).resolve().parents[2]`** —— 不依赖 cwd，也不依赖特定 shell。
9. **删除/移动前先写 `rename_map_*.csv` 回滚映射** —— 任何批量操作都能撤销。
10. **`.kb/` 随项目整体迁移** —— 不依赖全局环境；任何外部存储机制用「镜像」思路同步进项目，而非反向依赖。
11. **涉台港澳表述强制规范** —— 统一「中国台湾」「中国香港」「中国澳门」，绝不表述为独立国家；历史文献名原样保留；主权相关以国家立场为准。**必须固化进 AGENTS.md 第 7 节**。
12. **跨系统路径一律用 `pathlib` 处理，不写死盘符/分隔符** —— 脚本在 Windows / macOS / Linux 都能跑。

---

## 八、执行步骤（一句话触发后的完整流程）

1. **采集项目参数**（缺则合理假设并说明，不卡住）：项目名 / 根路径 / 一句话定位 / 主语言 / 主题域（4-12 个）/ 多语言 / 采集平台。
2. **建目录**（幂等）。
3. **写根级四件套**（AGENTS.md 最重要）。
4. **写各区 README + 模板**。
5. **建 `.kb/` 自包含元数据**（memory / skills / scripts）。
6. **（可选）建定时备份自动化** —— 把「镜像外部会话历史到项目内」这一步设为定时任务（具体调度方式随 Agent/系统而定，不写死）。
7. **校验并汇报**：目录树完整性 / frontmatter 合规 / 相对链接可解析 / **以汇总表汇报**（项目名/路径/四区文件数/根级文件/脚本数/待办）。

---

## 九、从三层升级为四区（迁移已有项目）

1. `mkdir reflections results`
2. 归位：`raw/reflections/` → `reflections/`；`raw/` 下编译产出目录 → `results/`
3. 全库替换引用路径（wiki 相对链接 + 脚本 `OUT`/`DIR` 常量）
4. 生成回滚映射 CSV 存 `.kb/memory/rename_map_YYYYMMDD.csv`
5. 根级新增 `index.md` / `log.md` / `README.md`，改写 `AGENTS.md` 为四区
6. 追加 `log.md` 一条 `refactor | 四区模式重构`

**风险控制**：先 dry-run 列出将移动的文件与将修改的引用，确认后再执行。

---

## 十、深入执行时（转姊妹技能）

以下主题属于**执行层**，本总纲只给入口，详细步骤与踩坑记录见 `llm-wiki-okf-bootstrap`：

| 主题 | 何时触发 |
|------|----------|
| 多语种 raw 采集（双语对照格式） | 用户要求多语言资料 |
| 专题采集区 + 聚焦子区 | 「中国前十名」「同母体 N 城」「历年爆款演化」 |
| 企业/品牌方向下沉采集 | 政策→企业，年报/招股书口径 |
| confidence 四维判定 + 企业财务九项检查表 | 要标注证据强度 |
| Compile 出成品（决策手册式成稿） | 用户要「一份能给人看的报告/手册」 |
| 过程思考落盘（ADR + reasoning） | 要保存推理过程 |

---

## 十一、参考样板（先抄再改，别重新发明）

如果你手头已有遵循四区模式的知识库，可直接作为样板复制骨架。**先 `ls` 参考样板，复制其 `AGENTS.md` 结构与约定，再按新主题改写，不要重新发明。**

常见样板类型（按领域可迁移）：

| 样板类型 | 适合主题 | 可复用的要点 |
|------|------|------|
| 健康 / 医学类 | 慢病、养生、心理健康 | 四区 + 多语种资料 + 双语对照 + 长文/书稿撰写 |
| 行为 / 习惯类 | 戒除、养成、自律 | 四区 + 多主题域横向覆盖 |
| 成长 / 知识类 | 方法论、思维模型 | 四区 + OKF 多域知识体系 |
| 文化 / 人文类 | 地方文化、思想史 | 四区 + 多语种渐进采集 |
| 商业 / 产业类 | 行业研究、产品分析 | 四区 + 专题子区 + confidence 判定 + Compile 出成品 |

---

## 十二、常见坑（血泪教训汇总）

- 删除/移动文件前先写 `rename_map_*.csv` 回滚映射。
- `raw/reflections/` 提升为根级 `reflections/` 后，旧相对链接 `../../raw/reflections/...` 失效，需全库替换。
- 编译脚本移入 `scripts/compilers/` 后 `parents` 层级易错（`parent.parent` → `parents[2]`）。
- 某些 shell 会把 `/tmp` 等路径做特殊解析，临时文件统一放项目目录内，避免跨系统歧义。
- 新建技能/自动化前先查重，避免重复。
- reflections 命名统一 `YYYY-MM-DD-<topic-slug>.md`（不要混用 `reflection-YYYYMMDD-<topic>.md`）。
- `reflections/README.md`、`results/README.md` 缺 OKF frontmatter 的，统一补 `type: Reflection Index` / `type: Results Index`。
- lint 必须剥离代码块再提取链接；目录链接视为有效；`build_index` 不能无条件跳过 `index.md`（域索引页要收录）。

---

*创建于 2026-09-10，2026-09-28 迭代升级为「知识库构建模式总纲」。约定提炼自多个 LLM Wiki 知识库空间（健康 / 行为 / 成长 / 文化 / 商业类）的实证实践。*
