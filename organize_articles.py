#!/usr/bin/env python3
"""整理文章目录结构"""
import os
from pathlib import Path
import shutil

ARTICLES_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles")

# 文章分类
CATEGORIES = {
    "cs": ["cs_article_01", "cs_article_02", "cs_article_03", "cs_article_04", "cs_article_05"],
    "geo": [f"geo_article_{i:02d}" for i in range(7, 81)],
    "manlu": ["manlu_article_01", "manlu_article_02", "manlu_article_03", "manlu_article_04", "manlu_article_05",
              "manlu-family", "manlu-healing", "manlu-team"],
    "philosophy": ["reality", "time", "truth", "beauty", "consciousness", "free_will"],
}

# 创建分类目录
for cat in CATEGORIES:
    cat_dir = ARTICLES_DIR / cat
    cat_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ 创建目录: {cat_dir}")

# 移动文件
moved = []
for cat, prefixes in CATEGORIES.items():
    cat_dir = ARTICLES_DIR / cat
    for f in ARTICLES_DIR.glob("*"):
        if f.is_file() and any(f.name.startswith(p) for p in prefixes):
            dest = cat_dir / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
                moved.append((f.name, cat))
                print(f"  📄 {f.name} → {cat}/")

print(f"\n✅ 移动完成: {len(moved)} 个文件")

# 列出新结构
print("\n📁 新目录结构:")
for cat in sorted(CATEGORIES.keys()):
    cat_dir = ARTICLES_DIR / cat
    files = list(cat_dir.glob("*.html")) + list(cat_dir.glob("*.md"))
    print(f"  {cat}/: {len(files)} 个文件")
