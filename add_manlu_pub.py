#!/usr/bin/env python3
"""给所有文章底部添加漫庐出品链接"""
from pathlib import Path
import re

ARTICLES_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles")
MANLU_PUB = '<p style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a1a1a; color: #8af; font-size: 13px;">🏡 <a href="/articles/manlu-geo/" style="color: #8af;">漫庐出品</a> · 长城脚下的山野民宿</p>'

# 找到所有HTML文件
html_files = list(ARTICLES_DIR.rglob("*.html"))
print(f"找到 {len(html_files)} 个HTML文件")

updated = 0
for f in html_files:
    content = f.read_text()
    if "漫庐出品" in content:
        continue
    # 在footer或body结束前添加
    if '</body>' in content:
        content = content.replace('</body>', f'{MANLU_PUB}\n</body>')
        f.write_text(content)
        updated += 1
        print(f"  ✅ {f.name}")
    else:
        print(f"  ⚠️  {f.name} 无</body>标签")

print(f"\n更新完成: {updated} 个文件")
