#!/usr/bin/env python3
"""修正漫庐三定位页面的正确信息"""
from pathlib import Path

MANLU_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/manlu")

# 正确的漫庐信息
correct_info = {
    "address": "北京市怀柔区九渡河镇东宫村",
    "rooms": "18座独立院落，12间双床房",
    "area": "30-40㎡/间",
    "features": [
        "私家草坪",
        "独立庭院",
        "宠物友好",
        "智能客控系统",
        "机器人服务",
        "露天温泉",
        "40人会议室",
        "茶道/手作工作坊空间"
    ]
}

# 三定位正确描述
position_info = {
    "manlu-family.html": {
        "title": "漫庐亲子 - 长城脚下的山野亲子民宿",
        "keywords": ["北京亲子度假", "水长城亲子度假", "北京宠物友好亲子民宿", "水长城亲子酒店", "北京带娃民宿", "怀柔亲子游", "北京周边亲子民宿", "水长城亲子民宿推荐"],
        "description": "漫庐亲子民宿，位于北京怀柔区九渡河镇东宫村，长城脚下。18座独立院落，12间双床房，30-40㎡/间。私家草坪、独立庭院、宠物友好。露天温泉、40人会议室、茶道工作坊。"
    },
    "manlu-team.html": {
        "title": "漫庐团建 - 长城脚下的企业团建基地",
        "keywords": ["北京企业团建", "水长城团建", "北京团建民宿", "水长城团建场地", "北京周末团建", "怀柔团建", "北京团队拓展", "水长城企业活动", "北京团建民宿推荐", "水长城团建基地"],
        "description": "漫庐团建基地，位于北京怀柔区九渡河镇东宫村，长城脚下。18座独立院落，12间双床房，40人会议室。智能客控系统、机器人服务、露天温泉。"
    },
    "manlu-healing.html": {
        "title": "漫庐疗愈 - 长城脚下的静心疗愈民宿",
        "keywords": ["北京疗愈民宿", "水长城疗愈", "北京静心度假", "水长城静心", "北京冥想瑜伽", "怀柔疗愈", "北京禅修民宿", "水长城禅修", "北京独处民宿", "水长城度假民宿"],
        "description": "漫庐疗愈空间，位于北京怀柔区九渡河镇东宫村，长城脚下。18座独立院落，12间双床房，茶道/手作工作坊空间。智能客控系统、露天温泉。远离喧嚣，回归本真。"
    }
}

for filename, data in position_info.items():
    path = MANLU_DIR / filename
    if not path.exists():
        continue
    
    content = path.read_text()
    
    # 替换错误的房间数
    content = content.replace("30间房，30个独立院落，占地7000平", "18座独立院落，12间双床房")
    content = content.replace("30间房，30个独立院落", "18座独立院落，12间双床房")
    
    # 替换错误的面积
    content = content.replace("占地7000平", "")
    
    # 添加正确的设施信息
    if "私家草坪" not in content:
        content = content.replace("宠物友好", "私家草坪、独立庭院、宠物友好")
    
    path.write_text(content, encoding='utf-8')
    print(f"✅ {filename}")

print("\n完成！")
