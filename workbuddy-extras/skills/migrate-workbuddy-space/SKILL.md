---
name: migrate-workbuddy-space
description: 把 WorkBuddy 某空间的对话任务历史跨机/跨路径迁移。当用户问"把项目目录拷到另一台电脑后怎么保留任务历史/任务不见了/迁移空间"时使用。核心：任务 jsonl 不在项目目录里，需拷 ~/.workbuddy/projects/<slug>/ 并改写内部路径（JSON 转义大小写 + 文本大写），否则任务被判为不属于该空间而隐藏。
version: 1.0.0
author: The Four-Zone Knowledge Base Contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [workbuddy, migration, task-history]
    category: workbuddy-extras
agent_created: true
---

# WorkBuddy 空间任务历史迁移（migrate-workbuddy-space）

## 何时用
- 用户把项目目录（如 `D:\WorkBuddy\MyProject`）复制到另一台电脑，问"任务历史怎么保留 / 任务不见了 / 项目能否正常运行"。
- 跨机（Windows↔Mac）或跨路径（C:→D: 等）迁移 WorkBuddy 空间。

## 核心事实（必须先讲给用户）
1. **项目目录 ≠ 任务历史**。项目目录（AGENTS.md/raw/wiki/.workbuddy）是纯文件，复制即可正常运行，**skills/memory/scripts 全随目录走**（这正是把元数据收进 `.workbuddy/` 的价值）。
2. **任务 jsonl 在用户数据目录**：`~/.workbuddy/projects/<slug>/`（Windows 即 `C:\Users\<you>\.workbuddy\projects\`）。slug 规则（实测）：盘符转小写去冒号 + 其余路径段保留原大小写，段间用 `-`。如 `D:\WorkBuddy\MyProject` → `e-MyProject`；`/Volumes/Drive/Work` → `Volumes-Drive-Work`。
3. **归属判定**：sessions 表 cwd + jsonl 内部路径。jsonl 内路径有 3 种关键变体，全部要改写：
   - `ai-title` 事件 `"cwd":"d:\\WorkBuddy\\MyProject"`（**小写盘符 + JSON 转义双反斜杠**）
   - user_info 文本 `Workspace Folder: D:\WorkBuddy\MyProject`（**大写盘符 + raw 单反斜杠**）
   - `file-history-snapshot` 的 trackedFiles 绝对路径
4. **路径相同则零改写**：新电脑若项目路径与旧机器完全一致（如都是 `D:\WorkBuddy\MyProject`），直接拷 jsonl 目录即可，无需改任何内容。

## 操作步骤（路径不同场景）
1. 拷贝项目目录到新电脑（`.workbuddy/scripts/` 下脚本随之到达，Windows/Mac 通用）。
2. 把旧机器 `~/.workbuddy/projects/<old_slug>/` 整个目录拷到新电脑任意临时目录（含 subagents 子目录）。
3. 运行（dry-run 先预览）：
   ```
   # Windows -> Windows（路径不同）
   python3 migrate_sessions.py --src-dir "X:\tmp\sessions" --project "D:\WorkBuddy\MyProject" --to "E:\MyProject"
   python3 migrate_sessions.py --src-dir "X:\tmp\sessions" --project "D:\WorkBuddy\MyProject" --to "E:\MyProject" --apply
   # Windows -> Mac（Mac 上项目如 /Volumes/Drive/MyProject；建议同时改写用户目录）
   python3 migrate_sessions.py --src-dir "/tmp/sessions" --project "D:\WorkBuddy\MyProject" \
       --to "/Volumes/Drive/MyProject" --home-old "C:\\Users\\<you>" --home-new "/Users/<you>" --apply
   ```
   （默认输出到 `~/.workbuddy/projects/<new_slug>/`，写前自动备份 *.bak；slug 由新路径自动推导，POSIX 路径如 `/Volumes/Drive/MyProject` → `Volumes-Drive-Work-MyProject`）
4. 验证：`python3 verify_migration.py --dir <输出目录> --old-prefix <旧路径> --new-prefix <新路径>`
   （可多次给 --old/--new-prefix；Windows→Mac 建议两对：项目路径 + 用户目录）
5. **完全退出 WorkBuddy 再重启**（Windows 托盘退出 + 任务管理器；Mac 上 Cmd+Q 后确认进程退出），否则不重新扫描 projects 目录。

## 踩过的坑（必读）
- **MSYS 路径转换**：git bash 会把 `D:\WorkBuddy\MyProject` 参数转成 `E:/MyProject`，导致只替换正斜杠变体、漏掉 JSON 转义双反斜杠（实测 444 vs 3347 处）。`forms()` 按盘符判定 Windows/POSIX：Windows 路径归一化反斜杠后推导 raw/json/slash 三变体；POSIX 路径（`/` 开头）无反斜杠、三变体相同。匹配一律 `re.IGNORECASE`。
- **大小写双写**：小写盘符的 `cwd` 字段 + 大写盘符的文本，两者都要替换，只改一个任务仍会隐藏。
- **Mac 场景**：`--to` 用 POSIX 路径（如 `/Volumes/Drive/MyProject`）；建议加 `--home-old C:\Users\<you> --home-new /Users/<you>` 一并改写用户目录引用（SOUL.md、.workbuddy、binaries 等路径）。
- **slug 大小写**：新电脑上若任务不显示，优先怀疑 slug 目录名大小写（盘符小写去冒号，其余段保留原大小写，勿全小写）。
- **深层嵌套转义**：对话历史正文里可能有 4+ 层反斜杠的路径（嵌套 JSON 快照、调试文本），属历史内容，不影响任务归属与加载；无需强求清零。
- 替换后用 `json.loads` 逐行校验，防止改写破坏 JSON 结构。

## 相关脚本位置
- `.workbuddy/scripts/migrate_sessions.py` — 迁移/恢复（dry-run 默认，--apply 写）
- `.workbuddy/scripts/verify_migration.py` — 迁移后验证
- `.workbuddy/scripts/backup_tasks.py` — UserData 任务历史 → 项目内 `.workbuddy/tasks/` 镜像（配合 automation 每日自动同步，保证项目目录自包含可移植）

## 镜像方案（推荐日常使用，避免每次手动迁移）
1. 任务 jsonl 固定存 UserData，**项目内不会被自动扫描**——所以用镜像 + 恢复实现"自动可移植"：
   - 备份：`backup_tasks.py --apply`（或依赖 automation 每日同步）→ `.workbuddy/tasks/`
   - 恢复：`migrate_sessions.py --src-dir <MyProject>/.workbuddy/tasks --project D:\WorkBuddy\MyProject --to <新路径> --apply`
   - 若新电脑路径与旧路径相同：直接把 `.workbuddy/tasks/` 复制为 `~/.workbuddy/projects/<slug>` 即可，零改写
2. 进阶（未采用）：`mklink /J` 把 UserData slug 目录链接到 `.workbuddy/tasks/`，数据真在项目内、拷目录即全带走；需完全退出 WorkBuddy 后建链接。
