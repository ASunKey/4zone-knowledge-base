# WorkBuddy 扩展（可选）

> ⚠️ 本目录是**可选的 WorkBuddy / CodeBuddy 专用扩展**，与仓库核心的 `four-zone-scaffold` + `llm-wiki-okf-bootstrap` 完全独立。
>
> **如果你不用 WorkBuddy / CodeBuddy，可以直接忽略整个 `workbuddy-extras/` 目录**——核心知识库构建方法不依赖它。

## 为什么单独放这里

四区模式知识库的**核心方法**（`skills/four-zone-scaffold` + `skills/llm-wiki-okf-bootstrap`）是**完全 Agent 无关、系统无关**的，任何 Agent、任何系统都能用。

但其中有一部分工作流是 **WorkBuddy / CodeBuddy 特有的**——即「迁移空间时保留对话任务历史」，它依赖 WorkBuddy 把对话历史（`*.jsonl`）存放在用户数据目录（`~/.workbuddy/projects/<slug>/`）这一机制。这部分对非 WorkBuddy 用户毫无意义，故拆分到此目录。

## 内容

```
workbuddy-extras/
├── skills/migrate-workbuddy-space/   ← 技能：WorkBuddy 空间跨机/跨路径迁移（含踩坑记录）
└── scripts/
    ├── backup_tasks.py               ← 任务历史 → 项目内镜像备份
    ├── migrate_sessions.py           ← 镜像 → 新机，改写 jsonl 内路径并重命名 slug
    └── verify_migration.py           ← 迁移后验证
```

三个脚本是**纯标准库、零依赖**的，可独立复用；但它们服务的对象是 WorkBuddy 的会话历史存储，非 WorkBuddy 用户无需关注。

## 使用前提

- 仅适用于 **WorkBuddy / CodeBuddy** 用户；
- 涉及 `~/.workbuddy/projects/<slug>/` 这一 WorkBuddy 私有数据目录；
- 迁移操作前请先备份，脚本默认 dry-run，加 `--apply` 才真正写入。

> 其他 Agent（Claude Code、Cursor 等）用户：请直接使用仓库根 `skills/` 下的两个核心技能，忽略本目录。
