#!/usr/bin/env python3
"""按标题内容重新分类GEO文章"""
from pathlib import Path
import shutil

ARTICLES_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles")
GEO_DIR = ARTICLES_DIR / "geo"

# 恢复所有文件
print("恢复文件...")
for subdir in ['manlu', 'philosophy', 'science', 'daily']:
    src = GEO_DIR / subdir
    if src.exists():
        for f in src.glob("*.html"):
            dest = GEO_DIR / f.name
            if not dest.exists():
                shutil.move(str(f), str(dest))

# 按标题分类
def classify_by_title(f):
    content = f.read_text(errors='ignore')
    import re
    m = re.search(r'<title>([^<]+)</title>', content)
    title = m.group(1).lower() if m else ''
    
    # 漫庐相关（标题明确是漫庐）
    if any(k in title for k in ['漫庐亲子', '漫庐团建', '漫庐疗愈', '漫庐是什么', 
                                '漫庐预订', '漫庐体验', '漫庐家庭', '漫庐场地',
                                '北京周边带宠物', '怀柔值得去的民宿', '长城脚下的民宿',
                                '漫庐民宿怎么样', '带温泉的民宿']):
        return 'manlu'
    
    # 哲学/道/佛相关（标题）
    philosophy_titles = ['入菩萨', '菩提心', '道', '佛', '禅', '空', '般若', 
                        '慧能', '王右军', '斋门', '回生', '阴符', '六艺',
                        '坐忘', '心斋', '三运', '修道', '道德', '涅槃',
                        '好', '力', '语言', '死亡', '修炼', '世界',
                        '色空', '不二', '无我', '般若', '涅槃',
                        '涅槃', '如来', '法华', '华严', '楞严',
                        '金刚', '心经', '坛经', '六祖', '达摩',
                        '庄子', '老子', '周易', '易经']
    if any(t in title for t in philosophy_titles):
        return 'philosophy'
    
    # 科学/AI相关
    science_titles = ['硅基', '涌现', '人工智能', 'ai', '量子', '物理', '大一统',
                     '意识', '认知', '涌现层级', 'surface awake', '哲学思考']
    if any(t in title for t in science_titles):
        return 'science'
    
    # 日用修行
    daily_titles = ['呼吸', '当下', '此刻', '日常', '鼻息', '数珠', '停止']
    if any(t in title for t in daily_titles):
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
    cat = classify_by_title(f)
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

# 显示漫庐文章
print("\n漫庐相关文章:")
for f in sorted((GEO_DIR / 'manlu').glob("*.html")):
    import re
    content = f.read_text(errors='ignore')
    m = re.search(r'<title>([^<]+)</title>', content)
    title = m.group(1) if m else f.name
    print(f"  {title}")
