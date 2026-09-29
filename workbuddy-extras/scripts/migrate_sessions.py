#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WorkBuddy 空间任务历史 跨机迁移脚本（通用版）
============================================
背景：WorkBuddy 的对话任务历史（*.jsonl）【不在项目目录里】，
      而是存放在 ~/.workbuddy/projects/<slug>/（Windows 即 C:\\Users\\<you>\\.workbuddy\\projects\\）。
      slug = 项目绝对路径小写转连字符，例如 D:\\MyProject -> e-MyProject。
      任务归属靠 jsonl 内部的路径字段判定：
        - ai-title 事件的 "cwd":"d:\\MyProject"（结构化字段，小写盘符，JSON 转义）
        - 对话正文 user_info 的 "Workspace Folder: D:\\MyProject"（文本，大写盘符）
        - file-history-snapshot 事件里的 trackedFiles 绝对路径
      因此跨机迁移时，若新机器上项目路径与旧机器不同，必须改写 jsonl 内的旧路径，
      否则任务会被判定为"不属于该空间"而隐藏（大小写/转义两处都要改，缺一不可）。

本脚本做什么：
  1) 读取旧 jsonl 目录（默认 ~/.workbuddy/projects/<old_slug>，可 --src-dir 指定）
  2) 把每个 .jsonl（含 subagents 子目录）中的旧项目路径
     （JSON 转义小写/大写、普通文本、正斜杠形式）全部替换为新项目路径
  3) 输出到 ~/.workbuddy/projects/<new_slug>/（自动按新路径重命名 slug，可 --out-dir 覆盖）
  4) 默认 dry-run 只报告，加 --apply 才写（写前自动备份已有文件为 *.bak）

用法（在【新电脑】上运行；两种方式任选）：
  ★ 自动模式（推荐）：把项目目录拷到新电脑后，直接在项目内运行，无需任何路径参数——
     脚本自动：源=项目内 .workbuddy/tasks 镜像；旧路径=镜像 META.json 记录；
     目标=脚本所在项目根（自动适应当前机器路径）；跨平台时自动改写用户目录。
     python3 .workbuddy/scripts/migrate_sessions.py            # dry-run 预览
     python3 .workbuddy/scripts/migrate_sessions.py --apply    # 正式迁移
  ★ 手动模式（可覆盖任何自动判定）：
     # Windows -> Windows（路径不同）
     python3 migrate_sessions.py --src-dir "X:\\tmp\\sessions" --project "D:\\MyProject" --to "E:\\MyProject"
     # Windows -> Mac（示例：Mac 上项目位于外接卷 /Volumes/Drive/MyProject）
     python3 migrate_sessions.py --src-dir "/tmp/sessions" --project "D:\\MyProject" --to "/Volumes/Drive/MyProject" \
         --home-old "C:\\Users\\<you>" --home-new "/Users/<you>"
  迁移后：完全退出 WorkBuddy（Windows 托盘退出+任务管理器；Mac Cmd+Q 并确认进程退出）再重启。

参数：
  --project  旧项目绝对路径（默认从镜像 META.json 自动读取）
  --to       新项目绝对路径（默认=脚本所在项目根，自动适应当前机器；即"只认 MyProject 文件夹，父路径自动适配"）
  --src-dir  旧 jsonl 目录（默认 <项目>/.workbuddy/tasks 镜像）
  --out-dir  输出目录（默认 ~/.workbuddy/projects/<new_slug>）
  --home-old / --home-new  旧/新机器用户目录（跨平台迁移自动用当前用户目录，也可手动覆盖）
  --apply    真正写入；不加则仅 dry-run 报告
"""

import argparse
import json
import os
import platform
import re
import shutil
import sys


def slugify(path: str) -> str:
    """项目绝对路径 -> slug。实测规则（依现有 projects 目录名）：
    D:\\MyProject      -> e-MyProject      （盘符转小写去冒号，其余段保留原大小写）
    /Volumes/Drive/Work -> Volumes-Drive-Work （POSIX 无盘符，段保留原大小写）"""
    s = path.replace("\\", "/")
    segs = []
    for p in s.split("/"):
        if not p:
            continue
        if len(p) == 2 and p[1] == ":":
            p = p[0].lower()  # 盘符 "D:" -> "d"
        segs.append(p)
    return "-".join(segs)


def forms(path: str):
    """返回路径的三种结构形式，用于在 jsonl 中匹配：
       raw / json 转义 / 正斜杠。
    - Windows 路径（含盘符，如 D:\\MyProject 或 E:/MyProject）：
      raw = D:\\...，json = D:\\\\...，slash = D:/...
    - POSIX 路径（/ 开头，如 /Volumes/Drive/MyProject）：
      无反斜杠，三种形式相同 = 路径本身。
    注意：参数可能被 shell（git bash MSYS 路径转换）改成正斜杠，
    Windows 判定以盘符为准。"""
    if re.match(r"^[A-Za-z]:", path):
        raw = path.replace("/", "\\")
        json_esc = raw.replace("\\", "\\\\")
        slash = raw.replace("\\", "/")
    else:
        raw = json_esc = slash = path
    return raw, json_esc, slash


def replace_in_line(line: str, old_f, new_f) -> tuple:
    """对单行做大小写不敏感替换（用函数替换避免反斜杠被 re.sub 解释）。
    返回 (新行, 替换次数)。"""
    pat = re.compile(re.escape(old_f), re.IGNORECASE)
    count = [0]

    def _repl(m):
        count[0] += 1
        return new_f

    return pat.sub(_repl, line), count[0]


def process_file(src_path: str, dst_path: str, pairs, dry_run: bool):
    """处理单个 jsonl：逐行替换，校验每行仍是合法 JSON，统计次数。"""
    total = 0
    with open(src_path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    out_lines = []
    for line in lines:
        if not line.strip():
            out_lines.append(line)
            continue
        n = 0
        for old_f, new_f in pairs:
            line, c = replace_in_line(line, old_f, new_f)
            n += c
        # 校验：替换后该行仍是合法 JSON（JSON 转义形式下重新解析）
        try:
            json.loads(line)
        except Exception as e:
            print(f"  ! 警告: {os.path.basename(src_path)} 某行替换后 JSON 解析失败: {e}")
            print(f"    -> {line[:160]}")
        total += n
        out_lines.append(line)

    rel = os.path.basename(src_path)
    if dry_run:
        if total:
            print(f"  [dry-run] {os.path.basename(src_path)}: {total} 处路径将被替换 -> {dst_path}")
    else:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        if os.path.exists(dst_path):
            shutil.copy2(dst_path, dst_path + ".bak")
        with open(dst_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(out_lines))
        print(f"  [ok] {os.path.basename(src_path)}: 替换 {total} 处 -> {dst_path}")
    return total


def main():
    ap = argparse.ArgumentParser(description="WorkBuddy 空间任务历史跨机迁移：改写 jsonl 内项目路径并重命名 slug")
    ap.add_argument("--project", default=None, help="旧项目绝对路径（默认从镜像 META.json 自动读取）")
    ap.add_argument("--to", default=None, help="新项目绝对路径（默认=脚本所在项目根，自动适应当前机器）")
    ap.add_argument("--src-dir", default=None, help="旧 jsonl 目录（默认 <项目>/.workbuddy/tasks 镜像）")
    ap.add_argument("--out-dir", default=None, help="输出目录（默认 ~/.workbuddy/projects/<new_slug>）")
    ap.add_argument("--home-old", default=None, help="旧机器用户目录（默认从 META 读取）")
    ap.add_argument("--home-new", default=None, help="新机器用户目录（跨平台迁移自动用当前用户目录）")
    ap.add_argument("--apply", action="store_true", help="真正写入；不加则 dry-run")
    args = ap.parse_args()

    home = os.path.expanduser("~")
    proot = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_src = os.path.join(proot, ".workbuddy", "tasks")

    # 1) 确定源目录
    src_dir = args.src_dir
    if src_dir is None and os.path.isdir(default_src):
        src_dir = default_src
        print(f"[自动] 源目录 = 项目内镜像 {src_dir}")

    # 2) 读取镜像 META（记录来源路径/平台）
    meta = {}
    if src_dir and os.path.exists(os.path.join(src_dir, "META.json")):
        try:
            with open(os.path.join(src_dir, "META.json"), encoding="utf-8") as fh:
                meta = json.load(fh)
            print(f"[自动] 从镜像 META 读取来源: {meta.get('project_path')} (平台 {meta.get('platform')})")
        except Exception as e:
            print(f"  ! 警告: META.json 读取失败: {e}")

    # 3) 确定新旧项目路径
    old_project = args.project or meta.get("project_path")
    new_project = args.to or proot
    if new_project == proot and args.to is None:
        print(f"[自动] 目标路径 = 当前项目根 {new_project}")
    if not old_project:
        print("错误: 无法确定旧项目路径。请用 --project 指定，或确保源目录含镜像 META.json。")
        sys.exit(1)

    old_slug = slugify(old_project)
    new_slug = slugify(new_project)
    if src_dir is None:
        src_dir = os.path.join(home, ".workbuddy", "projects", old_slug)
    out_dir = args.out_dir or os.path.join(home, ".workbuddy", "projects", new_slug)

    # 4) 用户目录：跨平台迁移自动采用当前用户目录
    home_old = args.home_old or meta.get("user_home")
    home_new = args.home_new
    src_platform = meta.get("platform", "")
    if home_old and home_new is None and platform.system() != src_platform and src_platform:
        home_new = home
        print(f"[自动] 跨平台迁移（{src_platform} -> {platform.system()}），用户目录 {home_old} -> {home_new}")

    print(f"旧项目: {old_project}  (slug: {old_slug})")
    print(f"新项目: {new_project}  (slug: {new_slug})")
    print(f"源目录: {src_dir}")
    print(f"目标目录: {out_dir}")
    print(f"模式: {'apply(写入, 自动备份 .bak)' if args.apply else 'dry-run(仅预览)'}")
    print()

    if not os.path.isdir(src_dir):
        print(f"错误: 源目录不存在: {src_dir}")
        print("跨机场景请用 --src-dir 指向拷来的旧 jsonl 目录（或放到项目内 .workbuddy/tasks 镜像）。")
        sys.exit(1)

    # 替换对：项目路径三变体（分别大小写不敏感）
    same_project = os.path.normcase(os.path.normpath(old_project)) == os.path.normcase(os.path.normpath(new_project))
    pairs = []
    if same_project:
        print("新旧项目路径相同 -> 无需改写路径，直接复制任务文件。")
    else:
        old_raw, old_json, old_slash = forms(old_project)
        new_raw, new_json, new_slash = forms(new_project)
        pairs = [
            (old_json, new_json),
            (old_raw, new_raw),
            (old_slash, new_slash),
        ]
    # 可选：用户目录改写（跨机迁移时处理 C:\Users\<you> -> /Users/<you> 等）
    if home_old and home_new:
        ho_raw, ho_json, ho_slash = forms(home_old)
        hn_raw, hn_json, hn_slash = forms(home_new)
        pairs += [
            (ho_json, hn_json),
            (ho_raw, hn_raw),
            (ho_slash, hn_slash),
        ]
        print(f"用户目录改写: {home_old} -> {home_new}")

    total_all = 0
    n_files = 0
    for root, dirs, files in os.walk(src_dir):
        dirs.sort()
        for fn in sorted(files):
            if not fn.endswith(".jsonl"):
                continue
            src_path = os.path.join(root, fn)
            rel_path = os.path.relpath(src_path, src_dir)
            dst_path = os.path.join(out_dir, rel_path)
            n = process_file(src_path, dst_path, pairs, args.apply is False)
            total_all += n
            n_files += 1

    print()
    print(f"共处理 {n_files} 个 jsonl，累计 {total_all} 处路径替换。")
    if not args.apply:
        print("以上为预览。确认无误后加 --apply 真正迁移。")
    else:
        print("迁移完成。请【完全退出 WorkBuddy 再重启】（托盘退出+任务管理器清进程），")
        print("重启后新空间即显示迁移过来的任务。")
        print("若任务未显示：多为 slug 大小写或路径改写遗漏，可检查 jsonl 内是否仍含旧路径。")


if __name__ == "__main__":
    main()
