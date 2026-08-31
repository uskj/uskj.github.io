#!/usr/bin/env python3
"""修正漫庐三定位页面的房间配置"""
from pathlib import Path

MANLU_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/manlu")

# 正确的房间配置
room_config = "12套1.5x2米标间，8间1.8x2米大床，4间带上下铺亲子房，2套3室一厅"

# 替换所有页面中的错误信息
for f in MANLU_DIR.glob("*.html"):
    if f.name == "index.html":
        continue
    
    content = f.read_text()
    
    # 替换错误的房间数
    content = content.replace("18座独立院落，12间双床房", room_config)
    content = content.replace("30间房，30个独立院落", room_config)
    content = content.replace("30间房，18座独立院落", room_config)
    
    # 确保有占地信息（如果原来有）
    if "占地" not in content:
        content = content.replace(room_config, f"{room_config}，占地7000平")
    
    f.write_text(content, encoding='utf-8')
    print(f"✅ {f.name}")

print("\n完成！")
