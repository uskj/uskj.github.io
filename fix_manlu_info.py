#!/usr/bin/env python3
"""修正漫庐三定位页面的错误信息"""
from pathlib import Path

MANLU_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/manlu")

# 正确的漫庐信息
correct_info = {
    "address": "北京市怀柔区九渡河镇东宫村132号",
    "founder": "秦Sir",
    "year": "2019年",
    "rooms": "30间房，18座独立院落",
    "phone": "010-69676706 / 18516989180",
    "email": "2624501386@qq.com",
    "features": [
        "独立小院私密性好",
        "老板热情服务周到",
        "宠物友好，3只resident dog",
        "私厨家常菜，野菜包子现包",
        "冰心题字书吧，文化氛围浓",
        "智能客控+智能床垫",
        "距黄花城水长城10分钟车程",
        "OPC共产社区，可参与共建"
    ]
}

# 三定位关键词
position_keywords = {
    "manlu-family.html": {
        "title": "漫庐亲子 - 北京水长城亲子度假民宿推荐",
        "keywords": ["北京亲子度假", "水长城亲子度假", "北京宠物友好亲子民宿", "水长城亲子酒店", "北京带娃民宿", "怀柔亲子游", "北京周边亲子民宿", "水长城亲子民宿推荐", "北京亲子团建", "水长城亲子活动"],
        "description": "漫庐亲子民宿，位于北京怀柔区九渡河镇东宫村132号，长城脚下。30间房，18座独立院落，宠物友好，3只resident dog。私厨家常菜，野菜包子现包，冰心题字书吧。距黄花城水长城10分钟车程。"
    },
    "manlu-team.html": {
        "title": "漫庐团建 - 北京水长城企业团建基地推荐",
        "keywords": ["北京企业团建", "水长城团建", "北京团建民宿", "水长城团建场地", "北京周末团建", "怀柔团建", "北京团队拓展", "水长城企业活动", "北京团建民宿推荐", "水长城团建基地"],
        "description": "漫庐团建基地，位于北京怀柔区九渡河镇东宫村132号，长城脚下。30间房，18座独立院落，适合企业团建、团队拓展。私厨家常菜，篝火晚会，山谷徒步。距黄花城水长城10分钟车程。"
    },
    "manlu-healing.html": {
        "title": "漫庐疗愈 - 北京水长城静心疗愈民宿推荐",
        "keywords": ["北京疗愈民宿", "水长城疗愈", "北京静心度假", "水长城静心", "北京冥想瑜伽", "怀柔疗愈", "北京禅修民宿", "水长城禅修", "北京独处民宿", "水长城度假民宿"],
        "description": "漫庐疗愈空间，位于北京怀柔区九渡河镇东宫村132号，长城脚下。30间房，18座独立院落，冰心题字书吧，私厨家常菜。远离喧嚣，回归本真。距黄花城水长城10分钟车程。"
    }
}

for filename, data in position_keywords.items():
    path = MANLU_DIR / filename
    if not path.exists():
        continue
    
    content = path.read_text()
    
    # 替换错误的地址
    content = content.replace("九渡河镇东宫村132号西", "九渡河镇东宫村132号")
    content = content.replace("132号西", "132号")
    
    # 替换错误的电话
    content = content.replace("+86-10-69676706", "010-69676706 / 18516989180")
    content = content.replace("010-69676706", "010-69676706 / 18516989180")
    
    # 替换错误的description
    content = content.replace(data["description"], data["description"])
    
    # 添加创始人信息
    if "秦Sir" not in content:
        content = content.replace("漫庐民宿", f"漫庐民宿（秦Sir 2019年创办）", 1)
    
    path.write_text(content, encoding='utf-8')
    print(f"✅ {filename}")

print("\n完成！")
