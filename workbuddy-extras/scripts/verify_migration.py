#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移结果验证工具（跨平台 Windows/Mac 通用）
============================================
检查 migrate_sessions.py 输出目录中的 jsonl：
  1) 旧路径（--old-prefix 及全部大小写/转义/正斜杠变体）零残留
  2) 新路径（--new-prefix 对应变体）有命中
  3) 每行仍是合法 JSON
  4) 抽查 ai-title 的 cwd 字段

用法：
  # Windows -> Windows 场景
  python3 verify_migration.py --dir <输出目录> \
      --old-prefix "D:\\MyProject" --new-prefix "E:\\MyProject"
  # Windows -> Mac 场景（可多次给 --old-prefix，如项目路径 + 用户目录）
  python3 verify_migration.py --dir <输出目录> \
      --old-prefix "D:\\MyProject" --old-prefix "C:\\Users\\<you>" \
      --new-prefix "/Volumes/Drive/MyProject" --new-prefix "/Users/<you>"
"""

import argparse
import json
import os
import re
import sys


def variants(prefix: str):
    """由路径前缀生成 6 种匹配变体（raw 大写/小写、JSON 转义大写/小写、正斜杠大写/小写）。"""
    win = prefix.replace("/", "\\")
    lower = win.lower() if re.match(r"^[A-Za-z]:", win) else win
    raw_u, raw_l = win, lower
    json_u = raw_u.replace("\\", "\\\\")
    json_l = raw_l.replace("\\", "\\\\")
    slash_u = raw_u.replace("\\", "/")
    slash_l = raw_l.replace("\\", "/")
    return list(dict.fromkeys([raw_u, raw_l, json_u, json_l, slash_u, slash_l]))


def main():
    ap = argparse.ArgumentParser(description="验证 migrate_sessions.py 输出")
    ap.add_argument("--dir", required=True, help="待验证目录（迁移输出）")
    ap.add_argument("--old-prefix", action="append", required=True, help="旧路径前缀（可多次）")
    ap.add_argument("--new-prefix", action="append", required=True, help="新路径前缀（可多次，与 old 对应）")
    args = ap.parse_args()

    if len(args.old_prefix) != len(args.new_prefix):
        print("错误: --old-prefix 与 --new-prefix 数量必须一致")
        sys.exit(1)

    old_all, new_all = [], []
    for op, np_ in zip(args.old_prefix, args.new_prefix):
        old_all += variants(op)
        new_all += variants(np_)
    old_all = list(dict.fromkeys(old_all))
    new_all = list(dict.fromkeys(new_all))

    if not os.path.isdir(args.dir):
        print(f"错误: 目录不存在 {args.dir}")
        sys.exit(1)

    issues = 0
    n_files = 0
    for root, _, files in os.walk(args.dir):
        for fn in sorted(files):
            if not fn.endswith(".jsonl"):
                continue
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8") as fh:
                s = fh.read()
            n_files += 1
            old_n = sum(s.count(o) for o in old_all)
            new_hit = any(n in s for n in new_all)
            bad = 0
            for ln in s.split("\n"):
                if ln.strip():
                    try:
                        json.loads(ln)
                    except Exception:
                        bad += 1
            if old_n or bad or not new_hit:
                issues += 1
                print(f"问题: {os.path.relpath(p, args.dir)} 残留{old_n} 新路径{new_hit} 坏行{bad}")
            else:
                print(f"OK: {os.path.relpath(p, args.dir)}")

    # 抽查 ai-title cwd
    for root, _, files in os.walk(args.dir):
        for fn in sorted(files):
            if not fn.endswith(".jsonl"):
                continue
            p = os.path.join(root, fn)
            with open(p, encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln:
                        continue
                    d = json.loads(ln)
                    if d.get("type") == "ai-title":
                        print(f"ai-title cwd: {repr(d.get('cwd'))}  ({os.path.basename(p)})")
                        break
            break
        break

    print()
    print(f"共检查 {n_files} 个 jsonl，问题文件 {issues} 个。")
    print("注意：对话历史正文中可能残留深层嵌套转义路径（如 4+ 层反斜杠），")
    print("属历史文本内容，不影响任务归属与加载；如全部为 0 则改写彻底。")
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
