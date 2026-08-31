# 漫庐AI直播 - 预生成场景视频提示词库

## 禅修场景 (Meditation)

### M01: 禅房晨景
**English Prompt:**
A serene Chinese meditation room at dawn, morning light filtering through bamboo blinds, incense smoke curling from bronze censer, wooden floor with zafu cushion, single branch in kanzashi vase, soft shadows, documentary photography style, 35mm film grain, muted greens and warm wood tones, quiet dignity.

**中文提示词:**
清晨禅房，晨光透过竹帘，香炉青烟袅袅，木质地面的蒲团，花入瓶中的单枝花，柔和阴影，纪录片摄影风格，35mm胶片颗粒感，低饱和度的青绿色调和温暖木色，安静的尊严。

---

### M02: 竹影禅坐
**English Prompt:**
Close-up of hands in meditation mudra, sitting on woven mat, bamboo shadows dancing on white wall, morning light soft and diffused, shallow depth of field, focus on hands and shadows, documentary style, 50mm lens feel.

**中文提示词:**
特写禅坐手势，坐在编织垫上，竹影在白墙上摇曳，晨光柔和散射，浅景深，焦点在手和影子，纪录片风格，50mm镜头质感。

---

### M03: 远钟暮鼓
**English Prompt:**
Wide shot of temple courtyard at dusk, ancient bell tower silhouetted against purple sky, stone path wet from rain, bamboo grove swaying, single monk walking slowly, atmospheric perspective, cinematic color grading, teal and orange tones.

**中文提示词:**
黄昏寺庙庭院全景，古钟楼剪影映衬紫罗兰色天空，石板路雨后湿润，竹林摇曳，僧人缓慢行走，大气的透视感，电影级调色，青色和橙色色调。

---

## 书法场景 (Calligraphy)

### C01: 雨夜写字
**English Prompt:**
Night scene in traditional Chinese study, rain streaks on paper window, single oil lamp on desk, hand holding brush writing on rice paper, ink stone and water cup nearby, warm amber light against cool blue rain darkness, shallow depth of field, 35mm film look.

**中文提示词:**
雨夜中式书房，雨滴划过纸窗，桌上单盏油灯，手握毛笔在宣纸上书写，砚台和水盂在旁边，温暖琥珀色光线对抗冷蓝灰色雨夜，浅景深，35mm胶片质感。

---

### C02: 墨香静心
**English Prompt:**
Close-up of calligraphy brush touching rice paper, ink spreading slowly, hand steady and focused, wooden desk surface visible, soft window light from side, macro detail, shallow depth of field, documentary photography style.

**中文提示词:**
特写毛笔触碰宣纸，墨汁缓慢晕染，手稳而专注，可见木质桌面，侧面柔和窗光，微距细节，浅景深，纪录片摄影风格。

---

### C03: 字如其人
**English Prompt:**
Medium shot of elderly master guiding young student's hand holding brush, both focused, traditional study background with scrolls and books, warm natural light, intergenerational connection, documentary style.

**中文提示词:**
中景老者引导年轻学生握笔的手，两人专注，传统书房背景有卷轴和书籍，温暖自然光，代际连接，纪录片风格。

---

## 自然场景 (Nature)

### N01: 漫庐山居
**English Prompt:**
Aerial view of Manlu retreat nestled in mountains, white walls and black tiles, bamboo grove surrounding, stone path winding through garden, morning mist rising, soft diffused light, drone photography, 24mm wide angle.

**中文提示词:**
漫庐度假村的航拍视角，隐匿在山林中，白墙黑瓦，竹林环绕，石径蜿蜒穿过花园，晨雾升腾，柔和散射光，无人机摄影，24mm广角。

---

### N02: 竹林听风
**English Prompt:**
Walking through bamboo forest path, sunlight filtering through dense green canopy, dappled light on stone steps, gentle breeze making bamboo sway, immersive perspective, 35mm film grain, nature documentary style.

**中文提示词:**
走在竹林小径，阳光透过茂密绿色树冠过滤，斑驳光影在石阶上，微风让竹子摇曳，沉浸视角，35mm胶片颗粒，自然纪录片风格。

---

### N03: 山雨欲来
**English Prompt:**
Mountain valley with dark clouds gathering, rain beginning to fall on stone roofs, mist rolling through bamboo, dramatic lighting, high contrast, cinematic composition, 50mm lens.

**中文提示词:**
山谷乌云密布，雨开始落在石屋顶，雾穿过竹林，戏剧性光线，高对比度，电影级构图，50mm镜头。

---

## 诗词场景 (Poetry)

### P01: 吟诗抒怀
**English Prompt:**
Woman in traditional hanfu standing by window, reciting poetry, rain outside, soft melancholic light, medium shot, shallow depth of field, East Asian aesthetic, 35mm film look.

**中文提示词:**
穿传统汉服的女子站在窗前吟诗，窗外下雨，柔和忧郁的光线，中景，浅景深，东亚美学，35mm胶片质感。

---

### P02: 格律之美
**English Prompt:**
Close-up of ancient poetry book open on wooden table, ink characters clear, single candle flame flickering, warm amber light, macro detail of paper texture, shallow depth of field.

**中文提示词:**
古诗集特写打开在木桌上，墨字清晰，单支蜡烛火焰摇曳，温暖琥珀色光线，纸张纹理微距细节，浅景深。

---

## 使用建议

### 批量生成策略

```bash
# 按场景类型批量生成
python batch_generate.py --scene meditation --count 10
python batch_generate.py --scene calligraphy --count 8
python batch_generate.py --scene nature --count 12
```

### 场景轮换逻辑

- 白天（6:00-18:00）：自然场景优先
- 傍晚（18:00-21:00）：禅修场景优先
- 夜晚（21:00-6:00）：书法场景优先

### 弹幕触发优先级

1. 精准匹配（5秒冷却）
2. 模糊匹配（10秒冷却）
3. 无匹配→随机场景（30秒冷却）

---

**船长AI视界出品**