#!/usr/bin/env python3
"""更新漫庐页面：添加宠物友好信息"""
from pathlib import Path

MANLU_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/manlu")

# 更新三个定位页面
pages = {
    "manlu-family.html": "漫庐亲子 - 长城脚下的亲子民宿",
    "manlu-team.html": "漫庐团建 - 企业团队拓展基地",
    "manlu-healing.html": "漫庐疗愈 - 山野静心疗愈空间"
}

for filename, title in pages.items():
    path = MANLU_DIR / filename
    if not path.exists():
        continue
    
    content = path.read_text()
    
    # 在features中添加宠物友好
    if "宠物友好" not in content:
        content = content.replace('"features":', '"features": ["宠物友好", ')
        content = content.replace("'features':", "'features': ['宠物友好', ")
    
    # 在description中添加宠物友好
    if "宠物友好" not in content:
        content = content.replace("适合亲子家庭度假。", "适合亲子家庭度假。宠物友好，欢迎带宠同行。")
        content = content.replace("适合企业团建、团队拓展、会议培训。", "适合企业团建、团队拓展、会议培训。宠物友好。")
        content = content.replace("远离喧嚣，回归本真。", "远离喧嚣，回归本真。宠物友好。")
    
    # 确保底部漫庐出品颜色正确
    content = content.replace('style="color:#8af"', 'style="color:#a08030"')
    content = content.replace('>漫庐出品</p>', '>漫庐出品</p>')
    
    path.write_text(content, encoding='utf-8')
    print(f"✅ {filename}")

print("\n完成！")
