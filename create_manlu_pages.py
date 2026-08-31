#!/usr/bin/env python3
"""创建漫庐三定位页面"""
from pathlib import Path

MANLU_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/manlu")

templates = {
    "manlu-family.html": {
        "title": "漫庐亲子 - 长城脚下的亲子民宿",
        "subtitle": "亲子度假 · 宠物友好 · 星空露营",
        "features": ["露天温泉", "篮球场", "台球室", "烧烤区", "星空露台", "宠物友好", "厨房", "儿童游乐区"],
        "description": "漫庐亲子民宿位于北京怀柔区九渡河镇东宫村，长城脚下。7000平超大场地，30间带院子客房，适合亲子家庭度假。宠物友好，有露天温泉、KTV、烧烤、篮球场等丰富设施。"
    },
    "manlu-team.html": {
        "title": "漫庐团建 - 企业团队拓展基地",
        "subtitle": "团队拓展 · 会议培训 · 团建活动",
        "features": ["50+会议室", "KTV", "烧烤", "篮球场", "徒步路线", "篝火晚会", "团队游戏"],
        "description": "漫庐团建基地位于北京怀柔长城脚下，7000平场地，30间客房，50+会议室。适合企业团建、团队拓展、会议培训。周边有徒步路线、KTV、烧烤、篝火晚会等丰富活动。"
    },
    "manlu-healing.html": {
        "title": "漫庐疗愈 - 山野静心疗愈空间",
        "subtitle": "静心疗愈 · 茶道工作坊 · 冥想瑜伽",
        "features": ["茶道工作坊", "冥想空间", "星空露台", "山野徒步", "温泉理疗", "书吧"],
        "description": "漫庐疗愈空间位于北京怀柔长城脚下，山野静心之地。茶道工作坊、冥想瑜伽、星空露台、山野徒步。远离喧嚣，回归本真。"
    }
}

for filename, data in templates.items():
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data['title']} | 漫庐民宿</title>
<meta name="description" content="{data['description']}">
<style>
body{{margin:0;background:#0a0a0a;color:#b0b0b0;font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;line-height:1.8;font-weight:300}}
.container{{max-width:680px;margin:0 auto;padding:60px 24px}}
h1{{font-weight:300;color:#e0e0e0;font-size:28px;letter-spacing:2px;margin-bottom:8px}}
.subtitle{{color:#888;font-size:14px;margin-bottom:40px}}
h2{{font-weight:400;color:#c0c0c0;font-size:18px;margin-top:40px;margin-bottom:20px}}
p{{color:#999;margin:16px 0}}
.features{{list-style:none;padding:0;margin:20px 0}}
.features li{{padding:8px 0;border-bottom:1px solid #181818;color:#888}}
.features li:before{{content:"✦ ";color:#c9a84c}}
.footer{{margin-top:60px;padding-top:20px;border-top:1px solid #1a1a1a;color:#555;font-size:13px}}
.nav{{margin-bottom:30px}}
.nav a{{color:#666;font-size:14px;text-decoration:none}}
.nav a:hover{{color:#8af}}
.cta{{display:inline-block;margin-top:30px;padding:12px 24px;background:#c9a84c;color:#0a0a0a;text-decoration:none;border-radius:4px;font-weight:400}}
.cta:hover{{background:#b89840}}
</style>
</head>
<body>
<div class="container">
<div class="nav"><a href="/">← 返回首页</a> · <a href="/articles/">文章索引</a> · <a href="/articles/manlu/">漫庐民宿</a></div>

<h1>{data['title']}</h1>
<p class="subtitle">{data['subtitle']}</p>

<p>{data['description']}</p>

<h2>核心设施</h2>
<ul class="features">
{chr(10).join(f'<li>{f}</li>' for f in data['features'])}
</ul>

<h2>预订方式</h2>
<p>电话预订：请联系漫庐管家</p>
<p>微信预订：搜索"漫庐民宿"</p>
<a class="cta" href="/articles/manlu/manlu_article_05_booking.html">查看预订指南</a>

<div class="footer">
<p style="color:#a08030">漫庐出品</p>
<p><a href="/" style="color:#666">← 返回首页</a></p>
</div>
</div>
</body>
</html>'''
    (MANLU_DIR / filename).write_text(html, encoding='utf-8')
    print(f"✅ {filename}")
