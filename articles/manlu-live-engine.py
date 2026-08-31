#!/usr/bin/env python3
"""
漫庐AI直播引擎 v1.0
基于MiniMax H3开源模型的弹幕互动直播系统
"""

import json
import time
import random
import os
from datetime import datetime
from pathlib import Path

# ============ 配置 ============
COURSE_CATALOG = {
    "禅修入门": {"video": "chan_intro.mp4", "audio": "chan_intro.mp3", "duration": 300},
    "丹道养生": {"video": "dandan_intro.mp4", "audio": "dandan_intro.mp3", "duration": 300},
    "书法静心": {"video": "shufa_intro.mp4", "audio": "shufa_intro.mp3", "duration": 300},
    "诗词创作": {"video": "shici_intro.mp4", "audio": "shici_intro.mp3", "duration": 300},
    "易经风水": {"video": "yijing_intro.mp4", "audio": "yijing_intro.mp3", "duration": 300},
}

DANMU_TRIGGERS = {
    # 禅修相关
    "禅": {"action": "show_meditation", "content": "静坐观心，止观双运"},
    "坐": {"action": "show_meditation", "content": "安住当下"},
    "静": {"action": "show_silence", "content": "归根曰静"},
    "心": {"action": "show_heart", "content": "明心见性"},
    
    # 养生相关
    "呼吸": {"action": "show_breathing", "content": "吐纳导引，强身健体"},
    "气": {"action": "show_qi", "content": "气聚丹田"},
    "养": {"action": "show_health", "content": "道家养生智慧"},
    
    # 书法相关
    "字": {"action": "show_calligraphy", "content": "笔墨修行，以字载道"},
    "墨": {"action": "show_ink", "content": "墨香静心"},
    "写": {"action": "show_write", "content": "写字即写心"},
    
    # 诗词相关
    "诗": {"action": "show_poetry", "content": "诗词表达心性"},
    "词": {"action": "show_ci", "content": "格律诗词"},
    "吟": {"action": "show_recite", "content": "吟诗抒情"},
    
    # 环境相关
    "雨": {"action": "play_rain", "content": "听雨"},
    "竹": {"action": "show_bamboo", "content": "竹影清风"},
    "山": {"action": "show_mountain", "content": "山居静坐"},
    "茶": {"action": "show_tea", "content": "茶道静心"},
    
    # 通用互动
    "道": {"action": "show_dao", "content": "道法自然"},
    "福": {"action": "show_blessing", "content": "福气满满"},
    "安": {"action": "show_peace", "content": "平安喜乐"},
}

SCENE_LIBRARY = {
    "meditation": {
        "title": "禅房静坐",
        "description": "晨钟暮鼓，竹影婆娑",
        "prompt": "A serene meditation room in traditional Chinese courtyard, morning light filtering through bamboo, soft incense smoke, wooden floor, zafu cushion, kanzashi vase with single branch, gentle shadows, documentary photography style, 35mm film grain, muted greens and warm wood tones",
        "audio": "birdsong, gentle wind, distant bell"
    },
    "calligraphy": {
        "title": "书房写字",
        "description": "笔墨纸砚，静心书写",
        "prompt": "Traditional Chinese study room, wooden desk with inkstone and rice paper, hand holding brush writing characters, rain outside window, warm lamp light, documentary style, shallow depth of field",
        "audio": "rain sound, brush on paper, quiet room tone"
    },
    "nature": {
        "title": "山林晨景",
        "description": "漫庐山居，云卷云舒",
        "prompt": "Mountain retreat in morning mist, bamboo grove swaying, stone path through garden, traditional Chinese architecture with white walls and black tiles, distant mountain peaks, soft diffused light, documentary photography",
        "audio": "birds, wind in bamboo, flowing water"
    }
}

# ============ 状态管理 ============
class LiveState:
    def __init__(self):
        self.current_scene = None
        self.danmu_history = []
        self.last_trigger = 0
        self.cooldown = 5  # 秒
        
    def can_trigger(self):
        return (time.time() - self.last_trigger) > self.cooldown
    
    def record_trigger(self, danmu, action):
        self.danmu_history.append({
            "time": datetime.now().isoformat(),
            "danmu": danmu,
            "action": action
        })
        self.last_trigger = time.time()
        
    def get_today_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        today_danmus = [d for d in self.danmu_history if d["time"].startswith(today)]
        return {
            "total": len(today_danmus),
            "unique": len(set(d["danmu"] for d in today_danmus)),
            "last": today_danmus[-1] if today_danmus else None
        }

state = LiveState()

# ============ 核心引擎 ============
def parse_danmu(text: str) -> dict | None:
    """解析弹幕，返回触发动作"""
    for keyword, trigger in DANMU_TRIGGERS.items():
        if keyword in text:
            return trigger
    return None

def generate_scene_prompt(action: str) -> dict:
    """根据动作生成场景提示词"""
    scene_map = {
        "show_meditation": "meditation",
        "show_silence": "meditation",
        "show_heart": "meditation",
        "show_breathing": "nature",
        "show_qi": "nature",
        "show_health": "nature",
        "show_calligraphy": "calligraphy",
        "show_ink": "calligraphy",
        "show_write": "calligraphy",
        "show_poetry": "nature",
        "show_ci": "nature",
        "show_recite": "nature",
        "play_rain": "calligraphy",
        "show_bamboo": "nature",
        "show_mountain": "nature",
        "show_tea": "nature",
        "show_dao": "meditation",
        "show_blessing": "nature",
        "show_peace": "meditation",
    }
    scene_key = scene_map.get(action, "nature")
    return SCENE_LIBRARY.get(scene_key, SCENE_LIBRARY["nature"])

def simulate_generation(prompt: str) -> dict:
    """模拟视频生成（实际使用时替换为真实API调用）"""
    return {
        "status": "success",
        "prompt": prompt,
        "duration": random.randint(3, 5),
        "cost": round(random.uniform(0.01, 0.05), 2),
        "scene": random.choice(["meditation", "calligraphy", "nature"])
    }

def process_danmu(text: str) -> dict:
    """处理单条弹幕"""
    trigger = parse_danmu(text)
    if not trigger:
        return {"status": "ignored", "reason": "no_match"}
    
    if not state.can_trigger():
        return {"status": "cooldown", "reason": "too_soon"}
    
    state.record_trigger(text, trigger["action"])
    
    # 生成场景
    scene = generate_scene_prompt(trigger["action"])
    
    # 模拟生成（实际使用时调用Seedance/Kling API）
    result = simulate_generation(scene["prompt"])
    
    return {
        "status": "success",
        "danmu": text,
        "trigger": trigger,
        "scene": scene,
        "generation": result
    }

def get_broadcast_schedule() -> list:
    """获取直播课表"""
    now = datetime.now()
    hour = now.hour
    
    schedule = [
        {"time": "08:00", "course": "禅修入门", "status": "scheduled"},
        {"time": "10:00", "course": "丹道养生", "status": "scheduled"},
        {"time": "14:00", "course": "书法静心", "status": "scheduled"},
        {"time": "16:00", "course": "诗词创作", "status": "scheduled"},
        {"time": "20:00", "course": "易经风水", "status": "scheduled"},
    ]
    
    # 标记当前时段
    for item in schedule:
        item_time = int(item["time"].split(":")[0])
        if hour >= item_time and hour < item_time + 2:
            item["status"] = "live"
        elif hour < item_time:
            item["status"] = "upcoming"
        else:
            item["status"] = "ended"
    
    return schedule

def generate_stream_ready_content() -> dict:
    """生成可直接推流的 content"""
    today = datetime.now()
    stats = state.get_today_stats()
    schedule = get_broadcast_schedule()
    
    return {
        "timestamp": today.isoformat(),
        "stats": stats,
        "schedule": schedule,
        "next_course": next((s for s in schedule if s["status"] == "upcoming"), None),
        "current_status": "online"
    }

# ============ 主循环 ============
def run_live_loop():
    """主直播循环"""
    print("=" * 50)
    print("漫庐AI直播引擎 v1.0")
    print(f"启动时间: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # 每日重置统计
    last_date = None
    
    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        
        # 检查是否新的一天
        if last_date != today_str:
            state.danmu_history.clear()
            last_date = today_str
            print(f"\n[{now}] 新的一天，统计已重置")
        
        # 生成直播状态
        stream_data = generate_stream_ready_content()
        
        # 输出状态（实际使用时推送到直播平台）
        if now.minute % 5 == 0:  # 每5分钟报告一次
            print(f"\n[{now}] 直播状态:")
            print(f"  今日弹幕: {stream_data['stats']['total']}")
            print(f"  当前课程: {stream_data['next_course']['course'] if stream_data['next_course'] else '自由模式'}")
            print(f"  状态: {stream_data['current_status']}")
        
        time.sleep(60)  # 每分钟检查一次

# ============ 测试模式 ============
def test_mode():
    """测试弹幕处理"""
    test_danmus = [
        "禅修真舒服",
        "想学打坐",
        "听雨声真好",
        "竹子好美",
        "静心写字",
        "道法自然",
        "这个不好",
        "随机内容"
    ]
    
    print("\n=== 测试弹幕处理 ===\n")
    for danmu in test_danmus:
        result = process_danmu(danmu)
        print(f"弹幕: {danmu}")
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
        time.sleep(0.5)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mode()
    else:
        run_live_loop()