#!/usr/bin/env python3
"""整合GEO文章：按内容分类到不同目录"""
from pathlib import Path
import re
import shutil

ARTICLES_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles")
GEO_DIR = ARTICLES_DIR / "geo"

# 创建子目录
categories = {
    "manlu": "漫庐民宿GEO",
    "philosophy": "哲学思考", 
    "science": "科学/AI",
    "daily": "日用修行",
}
for cat in categories:
    (GEO_DIR / cat).mkdir(parents=True, exist_ok=True)

# 分类规则
def classify_file(f):
    content = f.read_text(errors='ignore').lower()
    name = f.name
    
    # 漫庐相关
    if any(k in content for k in ['漫庐', '民宿', '长城', '怀柔', '温泉', '亲子', '团建', '疗愈']):
        return 'manlu'
    
    # 哲学/道/佛相关
    if any(k in content for k in ['道', '佛', '禅', '空', '般若', '菩提', '菩萨', '修行', ' meditation', '悟']):
        return 'philosophy'
    
    # 科学/AI相关
    if any(k in content for k in ['ai', '人工智能', '硅基', '涌现', '意识', '量子', '物理']):
        return 'science'
    
    # 日用修行
    if any(k in content for k in ['日用', '呼吸', '当下', '此刻', '日常']):
        return 'daily'
    
    return 'philosophy'  # 默认哲学

# 分类并移动文件
moved = []
for f in GEO_DIR.glob("*.html"):
    cat = classify_file(f)
    dest = GEO_DIR / cat / f.name
    if not dest.exists():
        shutil.move(str(f), str(dest))
        moved.append((f.name, cat))
        print(f"  {f.name} → {cat}/")

# 统计
print("\n分类结果:")
for cat in categories:
    count = len(list((GEO_DIR / cat).glob("*.html")))
    print(f"  {cat}: {count} 篇")

print(f"\n总计移动: {len(moved)} 个文件")
