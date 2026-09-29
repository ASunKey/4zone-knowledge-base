#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务历史 -> 项目内镜像 备份脚本（跨平台 Windows/Mac 通用）
==========================================================
目的：让项目目录自包含。WorkBuddy 的任务历史 jsonl 存放在
      ~/.workbuddy/projects/<slug>/（固定路径，不随项目走），
      本脚本把该目录【备份镜像】到项目内 .workbuddy/tasks/，
      这样拷贝/同步 MyProject 目录时任务历史随之携带。
      脚本自动从自身位置推导项目根与 slug，Windows/Mac 均可运行。

跨机恢复：在新电脑上，用 migrate_sessions.py 从镜像恢复到
      ~/.workbuddy/projects/<new_slug>/ 并改写内部路径：
        # Windows -> Windows（路径不同）
        python3 .workbuddy/scripts/migrate_sessions.py \
            --src-dir <拷来的MyProject>/.workbuddy/tasks \
            --project "D:\\MyProject" --to "<新路径>" --apply
        # Windows -> Mac
        python3 .workbuddy/scripts/migrate_sessions.py \
            --src-dir <拷来的MyProject>/.workbuddy/tasks \
            --project "D:\\MyProject" \
            --to "/Volumes/Drive/MyProject" \
            --home-old "C:\\Users\\<you>" --home-new "/Users/<you>" --apply
      （若新电脑路径与旧路径相同，直接复制 .workbuddy/tasks 到
        ~/.workbuddy/projects/<slug> 即可，无需改写）

用法：
  python3 backup_tasks.py                # dry-run：预览将备份哪些文件
  python3 backup_tasks.py --apply        # 真正备份（默认增量复制，不覆盖不同内容）
  python3 backup_tasks.py --force        # 连同 --apply：整体覆盖镜像（慎重）
"""

import argparse
import json
import os
import platform
import re
import shutil
import sys
import time


def project_root() -> str:
    """脚本位于 <项目>/.workbuddy/scripts/，向上三级即项目根。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def slugify(path: str) -> str:
    """项目绝对路径 -> WorkBuddy slug（跨平台）：
    D:\\MyProject -> e-MyProject（盘符小写去冒号，段保留原大小写）
    /Volumes/Drive/MyProject -> Volumes-Drive-MyProject"""
    segs = []
    for p in path.replace("\\", "/").split("/"):
        if not p:
            continue
        if len(p) == 2 and p[1] == ":":
            p = p[0].lower()
        segs.append(p)
    return "-".join(segs)


def main():
    ap = argparse.ArgumentParser(description="任务历史 -> 项目内镜像备份（跨平台：Windows/Mac 通用）")
    ap.add_argument("--apply", action="store_true", help="真正复制；不加则 dry-run")
    ap.add_argument("--force", action="store_true", help="覆盖镜像中已存在的不同文件（默认跳过）")
    ap.add_argument("--src", default=None, help="源目录（默认 ~/.workbuddy/projects/<项目slug>，自动推导）")
    ap.add_argument("--dst", default=None, help="镜像目录（默认 <项目>/.workbuddy/tasks）")
    args = ap.parse_args()

    proot = project_root()
    pslug = slugify(proot)
    home = os.path.expanduser("~")
    src = args.src or os.path.join(home, ".workbuddy", "projects", pslug)
    dst = args.dst or os.path.join(proot, ".workbuddy", "tasks")

    print(f"项目根   : {proot}  (slug: {pslug})")
    print(f"源(UserData) : {src}")
    print(f"目标(镜像)   : {dst}")
    print(f"模式: {'apply(复制)' if args.apply else 'dry-run(预览)'}"
          + (" + force(覆盖)" if args.force else ""))

    if not os.path.isdir(src):
        print(f"错误: 源目录不存在 {src}")
        sys.exit(1)

    # 收集源文件清单
    files = []
    for root, _, fns in os.walk(src):
        for fn in fns:
            sp = os.path.join(root, fn)
            rp = os.path.relpath(sp, src)
            files.append((sp, rp))

    copied, skipped, updated = 0, 0, 0
    for sp, rp in sorted(files):
        dp = os.path.join(dst, rp)
        if os.path.exists(dp):
            same = os.path.getsize(sp) == os.path.getsize(dp)
            if same and not args.force:
                skipped += 1
                continue
            updated += 1
        if args.apply:
            os.makedirs(os.path.dirname(dp), exist_ok=True)
            shutil.copy2(sp, dp)
            copied += 1
            print(f"  [copy] {rp}")
        else:
            action = "overwrite" if os.path.exists(dp) else "new"
            print(f"  [{action}] {rp}")

    print()
    print(f"共 {len(files)} 个文件: 新增/更新 {copied + updated}, 跳过 {skipped}")
    if args.apply:
        # 写入 META.json：记录镜像的来源路径/平台，供 migrate_sessions.py 恢复时自动识别
        meta = {
            "project_path": proot,
            "slug": pslug,
            "platform": platform.system(),
            "user_home": home,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        os.makedirs(dst, exist_ok=True)
        with open(os.path.join(dst, "META.json"), "w", encoding="utf-8") as fh:
            json.dump(meta, fh, ensure_ascii=False, indent=2)
        print(f"  [meta] META.json 已写入 (来源: {proot})")
        print(f"备份完成 -> {dst}")
        print("跨机迁移: 拷走项目目录后，在新电脑的项目内直接运行")
        print("  python3 .workbuddy/scripts/migrate_sessions.py --apply")
        print("  脚本会自动识别镜像来源与当前机器路径（也可用 --project/--to 手动指定）。")
    else:
        print("以上为预览。加 --apply 真正备份；加 --force 覆盖已有不同文件。")


if __name__ == "__main__":
    main()
