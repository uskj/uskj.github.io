#!/usr/bin/env python3
"""
漫庐AI直播引擎 - 弹幕NLP处理 + 场景切换
基于MiniMax H3知识图谱方法：知识节点依赖 + BKT掌握度估计 + 兴趣重写
"""
import json, re, time, hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque

ROOT = Path(r"C:\Users\zhaox\uskj-pages-windows")
LOG_FILE = ROOT / "manlu-live.log"
STATE_FILE = ROOT / "manlu-live-state.json"

# ===== Scene Knowledge Graph =====
# 基于AlphaSchool的原子化知识节点方法
SCENE_GRAPH = {
    # 节点定义（原子级场景组件）
    "meditation": {
        "name": "禅房静坐",
        "prerequisites": [],  # 无前置依赖
        "keywords": ["禅", "坐", "静", "冥想", "丹道", "修行", "止观", "臣服", "参"],
        "tags": ["禅修", "静心", "丹道"],
        "prompts": {
            "en": "Serene Chinese meditation room at dawn, morning light through bamboo blinds, incense smoke, wooden zafu cushion, single flower in vase, documentary style, 35mm film",
            "cn": "清晨禅房，晨光透过竹帘，香炉青烟袅袅，木质地面的蒲团，花入瓶中的单枝花，纪录片摄影风格，35mm胶片质感"
        },
        "audio": "鸟鸣、风声、远钟、诵经声"
    },
    "calligraphy": {
        "name": "雨夜写字",
        "prerequisites": ["meditation"],  # 需先静心再写字
        "keywords": ["书", "墨", "字", "书法", "写", "笔", "砚", "宣纸"],
        "tags": ["书法", "文化"],
        "prompts": {
            "en": "Night scene in traditional Chinese study, rain on paper window, oil lamp on desk, hand writing with brush on rice paper, warm amber light against cool blue rain",
            "cn": "雨夜中式书房，雨滴划过纸窗，桌上单盏油灯，手握毛笔在宣纸上书写，温暖琥珀色光线对抗冷蓝灰色雨夜"
        },
        "audio": "雨声、笔墨沙沙、远处犬吠"
    },
    "nature": {
        "name": "漫庐山居",
        "prerequisites": [],
        "keywords": ["山", "谷", "林", "野", "自然", "风景", "民宿", "北京"],
        "tags": ["自然", "山野"],
        "prompts": {
            "en": "Aerial view of mountain retreat nestled in bamboo forest, white walls black tiles, stone path winding through garden, morning mist rising, drone photography",
            "cn": "漫庐度假村的航拍视角，隐匿在山林竹林中，白墙黑瓦，石径蜿蜒穿过花园，晨雾升腾，无人机摄影"
        },
        "audio": "鸟鸣、风声、流水、虫鸣"
    },
    "tea": {
        "name": "茶道养生",
        "prerequisites": ["meditation"],
        "keywords": ["茶", "气", "息", "养生", "吐纳", "呼吸", " wellness"],
        "tags": ["茶道", "养生"],
        "prompts": {
            "en": "Traditional Chinese tea ceremony in mountain retreat, steam rising from teapot, wooden tea table, bamboo window frame, soft natural light, macro detail of tea leaves",
            "cn": "山野茶室中的传统茶道，茶壶热气袅袅，木质茶桌，竹制窗框，柔和自然光，茶叶微距细节"
        },
        "audio": "煮水声、倒茶声、鸟鸣"
    },
    "poetry": {
        "name": "吟诗抒怀",
        "prerequisites": ["calligraphy"],
        "keywords": ["诗", "词", "吟", "李白", "杜甫", "王维", "唐诗", "宋词"],
        "tags": ["诗词", "文化"],
        "prompts": {
            "en": "Woman in traditional hanfu standing by window reciting poetry, rain outside, soft melancholic light, medium shot, East Asian aesthetic, 35mm film",
            "cn": "穿传统汉服的女子站在窗前吟诗，窗外细雨，柔和忧郁的光线，中景，东亚美学，35mm胶片质感"
        },
        "audio": "雨声、吟诵声、古琴"
    },
    "bamboo": {
        "name": "竹林听风",
        "prerequisites": ["nature"],
        "keywords": ["竹", "风", "影", "漫步", "幽径", "清幽"],
        "tags": ["自然", "竹林"],
        "prompts": {
            "en": "Walking through dense bamboo forest path, sunlight filtering through green canopy, dappled light on stone steps, gentle breeze making bamboo sway, immersive perspective",
            "cn": "走在茂密竹林小径，阳光透过绿色树冠过滤，斑驳光影在石阶上，微风让竹子摇曳，沉浸视角"
        },
        "audio": "竹叶沙沙、鸟鸣、远处钟声"
    },
    "rain": {
        "name": "山雨欲来",
        "prerequisites": ["nature"],
        "keywords": ["雨", " Storm", "雷", "云", "雾", "山雨"],
        "tags": ["自然", "气象"],
        "prompts": {
            "en": "Mountain valley with dark clouds gathering, rain beginning to fall on stone roofs, mist rolling through bamboo, dramatic lighting, high contrast, cinematic composition",
            "cn": "山谷乌云密布，雨开始落在石屋顶，雾穿过竹林，戏剧性光线，高对比度，电影级构图"
        },
        "audio": "雷声、雨声、风声"
    }
}

# Reverse index: keyword -> scene
KEYWORD_INDEX = {}
for scene_key, scene_data in SCENE_GRAPH.items():
    for kw in scene_data["keywords"]:
        KEYWORD_INDEX[kw] = scene_key

# ===== BKT (Bayesian Knowledge Tracking) for audience engagement =====
class AudienceBKT:
    """用贝叶斯知识追踪模拟观众'掌握度'，动态调整场景难度"""
    def __init__(self):
        self.mastery = defaultdict(lambda: 0.5)  # 初始掌握度50%
        self.interaction_history = deque(maxlen=100)

    def update(self, scene_key, success):
        """success=True表示观众积极互动（弹幕触发），False表示冷场"""
        current = self.mastery[scene_key]
        # BKT更新：成功提高掌握度，失败降低
        if success:
            self.mastery[scene_key] = min(1.0, current + 0.15)
        else:
            self.mastery[scene_key] = max(0.1, current - 0.1)
        self.interaction_history.append((scene_key, success, time.time()))

    def get_next_scene(self):
        """基于掌握度选择最佳下一个场景"""
        # 选择掌握度在0.3-0.7之间的场景（最近发展区）
        target_scenes = [
            (k, v) for k, v in self.mastery.items()
            if 0.3 <= v <= 0.7
        ]
        if target_scenes:
            # 选掌握度最接近0.5的
            target_scenes.sort(key=lambda x: abs(x[1] - 0.5))
            return target_scenes[0][0]
        # 默认按优先级返回
        priority = ["nature", "meditation", "bamboo", "tea", "calligraphy", "poetry", "rain"]
        for s in priority:
            if s not in self.mastery or self.mastery[s] < 0.8:
                return s
        return "nature"

    def get_mastery_display(self):
        """返回可视化数据"""
        return {
            k: round(v, 2) for k, v in sorted(
                self.mastery.items(), key=lambda x: -x[1]
            )
        }


# ===== Interest Rewriting (类似AlphaSchool的情境重写) =====
class InterestRewriter:
    """基于弹幕兴趣动态重写场景描述"""
    def __init__(self):
        self.user_interests = defaultdict(lambda: defaultdict(int))
        self.writeups = {
            "meditation": {
                "default": "禅房静坐，听晨钟暮鼓",
                "poetic": "竹影扫阶尘不动，月轮穿沼水无痕",
                "modern": "城市人的心灵避难所",
                "philosophical": "止观臣服参，四法归一"
            },
            "calligraphy": {
                "default": "雨夜写字，墨香静心",
                "poetic": "挥毫落纸如云烟，字里行间见功夫",
                "modern": "放下手机，拿起毛笔的30分钟",
                "philosophical": "字如其人，心正笔正"
            },
            "nature": {
                "default": "漫庐山居，回归自然",
                "poetic": "采菊东篱下，悠然见南山",
                "modern": "长城脚下的7000平米山谷",
                "philosophical": "天人合一，道法自然"
            }
        }

    def rewrite(self, scene_key, danmu_text):
        """根据弹幕文本重写场景描述"""
        if scene_key not in self.writeups:
            return SCENE_GRAPH.get(scene_key, {}).get("prompts", {}).get("cn", scene_key)
        # 检测风格关键词
        if any(kw in danmu_text for kw in ["诗", "词", "古", "雅"]):
            style = "poetic"
        elif any(kw in danmu_text for kw in ["现代", "都市", "打工人", "逃离"]):
            style = "modern"
        elif any(kw in danmu_text for kw in ["道", "佛", "禅", "理", "哲学"]):
            style = "philosophical"
        else:
            style = "default"
        return self.writeups[scene_key].get(style, self.writeups[scene_key]["default"])


# ===== Main Engine =====
class ManluLiveEngine:
    def __init__(self):
        self.bkt = AudienceBKT()
        self.rewriter = InterestRewriter()
        self.current_scene = None
        self.danmu_count = 0
        self.scene_switches = 0
        self.start_time = None
        self.log_file = LOG_FILE

    def process_danmu(self, user: str, text: str) -> dict:
        """处理一条弹幕，返回场景触发结果"""
        self.danmu_count += 1
        result = {
            "user": user,
            "text": text,
            "matched_scene": None,
            "action": "none",
            "timestamp": datetime.now().isoformat()
        }

        # 1. 关键词匹配
        matched_scene = None
        for kw in text:
            if kw in KEYWORD_INDEX:
                matched_scene = KEYWORD_INDEX[kw]
                break

        # 2. 模糊匹配（成语/短语）
        if not matched_scene:
            for pattern, scene in [
                (r"静心", "meditation"), (r"冥想", "meditation"),
                (r"写字", "calligraphy"), (r"书法", "calligraphy"),
                (r"山林", "nature"), (r"民宿", "nature"),
                (r"喝茶", "tea"), (r"品茶", "tea"),
                (r"吟诗", "poetry"), (r"唐诗", "poetry"),
                (r"竹林", "bamboo"), (r"听风", "bamboo"),
                (r"下雨", "rain"), (r"山雨", "rain"),
            ]:
                if re.search(pattern, text):
                    matched_scene = scene
                    break

        if matched_scene:
            result["matched_scene"] = matched_scene
            result["action"] = "scene_trigger"
            self.scene_switches += 1
            # BKT更新：成功匹配=积极互动
            self.bkt.update(matched_scene, True)
            # 兴趣重写
            rewritten_desc = self.rewriter.rewrite(matched_scene, text)
            result["rewritten_desc"] = rewritten_desc

            # 记录日志
            self._log(f"DANMU: [{user}] '{text}' -> {matched_scene} ({rewritten_desc})")
        else:
            # 未匹配→随机推荐场景
            recommended = self.bkt.get_next_scene()
            result["action"] = "recommend"
            result["recommended_scene"] = recommended
            self.bkt.update(recommended, False)  # 冷场反馈
            self._log(f"DANMU: [{user}] '{text}' -> recommend {recommended}")

        return result

    def get_dashboard_state(self) -> dict:
        """返回仪表盘所需的全部状态数据"""
        return {
            "is_live": bool(self.start_time),
            "elapsed_seconds": int(time.time() - self.start_time) if self.start_time else 0,
            "danmu_count": self.danmu_count,
            "scene_switches": self.scene_switches,
            "current_scene": self.current_scene,
            "mastery": self.bkt.get_mastery_display(),
            "next_scene": self.bkt.get_next_scene(),
            "steps": self._get_current_step()
        }

    def _get_current_step(self) -> int:
        """根据直播时长计算当前阶段"""
        if not self.start_time:
            return 1
        elapsed = time.time() - self.start_time
        step_duration = 3600 / 6  # 60分钟分6阶段
        return min(6, int(elapsed / step_duration) + 1)

    def _log(self, message: str):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line)

    def save_state(self):
        """保存当前状态到文件"""
        state = self.get_dashboard_state()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_state(self):
        """从文件恢复状态"""
        if STATE_FILE.exists():
            with open(STATE_FILE, encoding="utf-8") as f:
                state = json.load(f)
            self.danmu_count = state.get("danmu_count", 0)
            self.scene_switches = state.get("scene_switches", 0)
            return True
        return False


if __name__ == "__main__":
    engine = ManluLiveEngine()

    # 测试弹幕处理
    test_danmus = [
        ("观众A", "好静啊，想打坐"),
        ("观众B", "我喜欢书法，能写个字吗"),
        ("观众C", "山里空气真好"),
        ("观众D", "喝茶喝茶"),
        ("观众E", "唐诗三百首"),
        ("观众F", "竹林好美"),
        ("观众G", "下雨了"),
        ("观众H", "漫庐在哪里"),
        ("观众I", "想逃离城市"),
        ("观众J", "道法自然"),
    ]

    print("=== 漫庐AI直播引擎测试 ===\n")
    for user, text in test_danmus:
        result = engine.process_danmu(user, text)
        action = result["action"]
        if action == "scene_trigger":
            print(f"[{user}] {text!r} -> [{result['matched_scene']}] ({result.get('rewritten_desc', '')})")
        elif action == "recommend":
            print(f"[{user}] {text!r} -> recommend {result['recommended_scene']}")

    print(f"\n--- 仪表盘状态 ---")
    state = engine.get_dashboard_state()
    print(json.dumps(state, ensure_ascii=False, indent=2))

    print(f"\n--- 观众掌握度分布 ---")
    print(json.dumps(engine.bkt.get_mastery_display(), ensure_ascii=False, indent=2))

    engine.save_state()
    print(f"\n日志已保存到: {LOG_FILE}")
