#!/usr/bin/env python3
"""重新整合GEO文章分类"""
from pathlib import Path
import shutil

ARTICLES_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles")
GEO_DIR = ARTICLES_DIR / "geo"

# 先恢复所有文件到geo根目录
print("恢复文件到geo目录...")
for subdir in ['manlu', 'philosophy', 'science', 'daily']:
    src = GEO_DIR / subdir
    if src.exists():
        for f in src.glob("*.html"):
            dest = GEO_DIR / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))
        print(f"  恢复 {subdir}/ 完成")

# 新的分类规则
def classify_file(f):
    content = f.read_text(errors='ignore').lower()
    name = f.name
    
    # 漫庐特定内容（民宿、预订、家庭等）
    manlu_keywords = ['漫庐民宿', '漫庐亲子', '漫庐团建', '漫庐疗愈', 
                      '九渡河镇', '东宫村', '长城脚下', '山野高端',
                      '18座院落', '露天温泉', '智能客控']
    if any(k in content for k in manlu_keywords):
        return 'manlu'
    
    # 哲学/道/佛相关
    philosophy_keywords = ['道', '佛', '禅', '空', '般若', '菩提', '菩萨', 
                          '修行', '悟', '寂天', '慧能', '王右军', '斋门',
                          '回生', '阴符', '六艺', '坐忘', '心斋', '三运']
    if any(k in content for k in philosophy_keywords):
        return 'philosophy'
    
    # 科学/AI相关
    science_keywords = ['硅基', '涌现', 'ai', '人工智能', '量子', '物理', 
                       '意识', '认知', '涌现层级', '大一统']
    if any(k in content for k in science_keywords):
        return 'science'
    
    # 日用修行
    daily_keywords = ['日用', '呼吸', '当下', '此刻', '日常', '鼻息', '数珠']
    if any(k in content for k in daily_keywords):
        return 'daily'
    
    return 'philosophy'

# 创建子目录
for cat in ['manlu', 'philosophy', 'science', 'daily']:
    (GEO_DIR / cat).mkdir(parents=True, exist_ok=True)

# 分类并移动
moved = []
for f in list(GEO_DIR.glob("*.html")):
    if f.name == 'index.html':
        continue
    cat = classify_file(f)
    dest = GEO_DIR / cat / f.name
    if not dest.exists():
        shutil.move(str(f), str(dest))
        moved.append((f.name, cat))

# 统计
print("\n分类结果:")
for cat in ['manlu', 'philosophy', 'science', 'daily']:
    count = len(list((GEO_DIR / cat).glob("*.html")))
    print(f"  {cat}: {count} 篇")

print(f"\n总计: {len(moved)} 个文件")
print("\n漫庐相关文章:")
for f in sorted((GEO_DIR / 'manlu').glob("*.html")):
    print(f"  {f.name}")