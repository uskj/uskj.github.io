#!/usr/bin/env python3
"""
漫庐AI直播 - Kling AI 集成版
支持7x24小时不间断直播，预生成+实时触发
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# ============ 配置 ============
class Config:
    # Kling AI API（免费版）
    KLING_API_KEY = os.getenv("KLING_API_KEY", "your_api_key_here")
    KLING_API_URL = "https://api.klingai.com/v1/videos/generations"
    
    # 直播配置
    STREAM_DURATION = 5  # 每个视频5秒
    AUTO_SWITCH_INTERVAL = 8  # 8秒自动切换
    COOLDOWN = 5  # 弹幕冷却5秒
    
    # 本地缓存
    CACHE_DIR = Path("/tmp/manlu_cache")
    CACHE_DIR.mkdir(exist_ok=True)
    
    # 场景库
    SCENES = {
        "nature": {
            "title": "漫庐山居",
            "desc": "云卷云舒，竹影清风",
            "prompt": "A serene Chinese mountain retreat at dawn, morning mist rising through bamboo grove, traditional white-walled black-tiled architecture, stone path winding through garden, distant mountain peaks, soft diffused natural light, cinematic quality, 35mm film grain, documentary photography style, muted greens and warm wood tones",
            "keywords": ["山", "林", "自然", "云"]
        },
        "meditation": {
            "title": "禅房静坐",
            "desc": "晨钟暮鼓，竹影婆娑",
            "prompt": "A serene meditation room in traditional Chinese courtyard, morning light filtering through bamboo blinds, incense smoke curling from bronze censer, wooden floor with zafu cushion, single branch in kanzashi vase, soft shadows, documentary photography style, 35mm film grain, muted greens and warm wood tones",
            "keywords": ["禅", "坐", "静", "心", "佛"]
        },
        "calligraphy": {
            "title": "书房写字",
            "desc": "笔墨纸砚，静心书写",
            "prompt": "Traditional Chinese study room interior, wooden desk with inkstone and rice paper, hand holding brush writing calligraphy characters, warm oil lamp light, rain outside paper window, close-up shot, shallow depth of field, cinematic lighting, 35mm film look",
            "keywords": ["书", "墨", "字", "写", "笔"]
        },
        "rain": {
            "title": "雨夜听声",
            "desc": "窗前听雨，墨香静心",
            "prompt": "Night scene in traditional Chinese study, rain streaks down paper window, single oil lamp providing warm amber glow, desk with open book and calligraphy tools, melancholic atmosphere, soft focus, cinematic color grading, teal and orange tones, 35mm film grain",
            "keywords": ["雨", "夜", "听"]
        },
        "bamboo": {
            "title": "竹林听风",
            "desc": "竹影摇曳，清风徐来",
            "prompt": "Walking through dense bamboo forest path, sunlight filtering through green canopy creating dappled patterns on stone steps, gentle breeze making bamboo sway, immersive perspective, nature documentary style, 35mm film grain, vibrant greens",
            "keywords": ["竹", "林", "风"]
        },
        "tea": {
            "title": "茶道静心",
            "desc": "煮茶听雨，禅意人生",
            "prompt": "Traditional Chinese tea ceremony setting, wooden table with ceramic teapot and teacups, steam rising from hot water, warm natural light from window, slow motion detail shots, documentary style, 35mm film look, earth tones",
            "keywords": ["茶", "道"]
        }
    }
    
    # 弹幕关键词映射
    DANMU_TRIGGERS = {}
    for scene_key, scene_data in SCENES.items():
        for keyword in scene_data["keywords"]:
            DANMU_TRIGGERS[keyword] = scene_key


class KlingClient:
    """Kling AI API客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = Config.KLING_API_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def generate_video(
        self, 
        prompt: str, 
        duration: int = 5,
        model: str = "kling-v1"
    ) -> Optional[Dict]:
        """生成视频"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "duration": duration,
                "resolution": "720p"
            }
            
            async with self.session.post(self.base_url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "success": True,
                        "video_url": data.get("video_url"),
                        "task_id": data.get("task_id"),
                        "prompt": prompt[:50]
                    }
                else:
                    print(f"API错误: {resp.status}")
                    return None
                    
        except Exception as e:
            print(f"生成失败: {e}")
            return None
    
    async def check_status(self, task_id: str) -> Optional[Dict]:
        """检查生成状态"""
        try:
            url = f"{self.base_url}/{task_id}"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                return None
        except:
            return None


class SceneManager:
    """场景管理器"""
    
    def __init__(self):
        self.current_scene = "nature"
        self.video_queue: List[str] = []
        self.generated_videos: Dict[str, str] = {}  # scene_key -> video_path
    
    def get_next_scene(self, force: bool = False) -> str:
        """获取下一个场景"""
        if force or not self.video_queue:
            scenes = list(Config.SCENES.keys())
            # 随机但避免连续重复
            if len(self.video_queue) > 0 and self.video_queue[-1] in scenes:
                scenes.remove(self.video_queue[-1])
            next_scene = scenes[hash(datetime.now()) % len(scenes)]
            self.video_queue.append(next_scene)
        return self.video_queue.pop(0)
    
    def get_scene_data(self, scene_key: str) -> Dict:
        """获取场景数据"""
        return Config.SCENES.get(scene_key, Config.SCENES["nature"])
    
    def trigger_by_danmu(self, text: str) -> Optional[str]:
        """根据弹幕触发场景"""
        for keyword, scene_key in Config.DANMU_TRIGGERS.items():
            if keyword in text:
                self.current_scene = scene_key
                return scene_key
        return None


class LiveStream:
    """直播流管理器"""
    
    def __init__(self):
        self.scene_manager = SceneManager()
        self.kling_client: Optional[KlingClient] = None
        self.is_live = False
        self.start_time = None
        self.danmu_count = 0
        self.last_trigger = 0
        self.stats = {
            "videos_generated": 0,
            "total_duration": 0,
            "cost": 0.0
        }
    
    async def start(self):
        """启动直播"""
        self.is_live = True
        self.start_time = datetime.now()
        
        print("=" * 50)
        print("漫庐AI直播系统启动")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 预生成首批场景
        await self._prefetch_scenes(count=10)
        
        # 开始直播循环
        await self._main_loop()
    
    async def _prefetch_scenes(self, count: int):
        """预生成场景视频"""
        print(f"\n预生成 {count} 个场景视频...")
        
        async with KlingClient(Config.KLING_API_KEY) as client:
            for i in range(count):
                scene_key = self.scene_manager.get_next_scene(force=True)
                scene_data = self.scene_manager.get_scene_data(scene_key)
                
                print(f"[{i+1}/{count}] 生成: {scene_data['title']}...")
                
                result = await client.generate_video(
                    prompt=scene_data["prompt"],
                    duration=Config.STREAM_DURATION
                )
                
                if result and result.get("video_url"):
                    self.scene_manager.generated_videos[scene_key] = result["video_url"]
                    self.stats["videos_generated"] += 1
                    print(f"  ✓ 已缓存")
                else:
                    print(f"  ✗ 失败，跳过")
                
                await asyncio.sleep(1)  # 避免API限流
    
    async def _main_loop(self):
        """主直播循环"""
        print("\n开始直播循环...")
        
        while self.is_live:
            # 获取下一个场景
            scene_key = self.scene_manager.get_next_scene()
            scene_data = self.scene_manager.get_scene_data(scene_key)
            
            # 检查是否有缓存视频
            video_url = self.scene_manager.generated_videos.get(scene_key)
            
            if not video_url:
                # 实时生成（降级）
                print(f"\n实时生成: {scene_data['title']}")
                video_url = await self._generate_on_demand(scene_key)
            
            if video_url:
                print(f"▶ 播放: {scene_data['title']}")
                # TODO: 推送到直播平台
                # 这里应该是推流代码
                await asyncio.sleep(Config.STREAM_DURATION)
            
            # 自动统计
            self.stats["total_duration"] += Config.STREAM_DURATION
        
        print(f"\n直播结束，统计: {self.stats}")
    
    async def _generate_on_demand(self, scene_key: str) -> Optional[str]:
        """按需生成视频"""
        scene_data = self.scene_manager.get_scene_data(scene_key)
        
        async with KlingClient(Config.KLING_API_KEY) as client:
            result = await client.generate_video(
                prompt=scene_data["prompt"],
                duration=Config.STREAM_DURATION
            )
            
            if result and result.get("video_url"):
                self.scene_manager.generated_videos[scene_key] = result["video_url"]
                self.stats["videos_generated"] += 1
                return result["video_url"]
        
        return None
    
    def process_danmu(self, text: str) -> Dict:
        """处理弹幕"""
        now = time.time()
        
        if now - self.last_trigger < Config.COOLDOWN:
            return {"status": "cooldown", "remaining": int(Config.COOLDOWN - (now - self.last_trigger))}
        
        scene_key = self.scene_manager.trigger_by_danmu(text)
        
        if scene_key:
            self.last_trigger = now
            self.danmu_count += 1
            return {
                "status": "triggered",
                "scene": scene_key,
                "title": self.scene_manager.get_scene_data(scene_key)["title"]
            }
        
        return {"status": "ignored"}
    
    def get_stats(self) -> Dict:
        """获取直播统计"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            **self.stats,
            "elapsed": int(elapsed),
            "danmu_count": self.danmu_count,
            "cache_size": len(self.scene_manager.generated_videos),
            "uptime": self._format_duration(elapsed)
        }
    
    def _format_duration(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def stop(self):
        """停止直播"""
        self.is_live = False
        self._print_stats()
    
    def _print_stats(self):
        """打印统计"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("直播统计")
        print("=" * 50)
        print(f"运行时长: {stats['uptime']}")
        print(f"生成视频: {stats['videos_generated']} 个")
        print(f"弹幕触发: {stats['danmu_count']} 次")
        print(f"缓存场景: {stats['cache_size']} 个")
        print(f"预估费用: ¥{stats['cost']:.2f}")


# ============ Web界面 ============
async def create_web_interface():
    """创建Web界面（简化版）"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>漫庐AI直播</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'PingFang SC', sans-serif; background: #0a0a0a; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .logo { font-size: 24px; color: #7a9a7a; letter-spacing: 4px; }
        .live-badge { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: rgba(255,59,48,0.2); border-radius: 20px; }
        .live-dot { width: 8px; height: 8px; background: #ff3b30; border-radius: 50%; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .main { display: grid; grid-template-columns: 1fr 300px; gap: 20px; margin-top: 20px; }
        .video-section { background: rgba(255,255,255,0.05); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .video-container { aspect-ratio: 16/9; background: #000; display: flex; align-items: center; justify-content: center; }
        .video-placeholder { text-align: center; color: rgba(255,255,255,0.5); }
        .video-title { font-size: 28px; margin-bottom: 10px; }
        .video-desc { font-size: 14px; }
        .controls { display: flex; gap: 10px; padding: 15px; background: rgba(0,0,0,0.3); }
        .btn { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #7a9a7a; color: #fff; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .stats { display: flex; gap: 20px; padding: 15px; background: rgba(0,0,0,0.3); }
        .stat-item { text-align: center; }
        .stat-value { font-size: 24px; color: #7a9a7a; }
        .stat-label { font-size: 12px; color: rgba(255,255,255,0.5); }
        .panel { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px; }
        .panel-title { font-size: 14px; color: #7a9a7a; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        textarea { width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: #fff; min-height: 80px; }
        .tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .tag { padding: 4px 12px; background: rgba(122,154,122,0.2); border: 1px solid rgba(122,154,122,0.4); border-radius: 12px; font-size: 12px; cursor: pointer; }
        .log-list { max-height: 150px; overflow-y: auto; font-size: 12px; color: rgba(255,255,255,0.5); }
        .log-item { padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">漫庐AI直播</div>
            <div class="live-badge"><div class="live-dot"></div><span>直播中</span></div>
        </header>
        <div class="main">
            <div class="video-section">
                <div class="video-container">
                    <div class="video-placeholder">
                        <div class="video-title" id="sceneTitle">漫庐山居</div>
                        <div class="video-desc" id="sceneDesc">云卷云舒，竹影清风</div>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn btn-primary">▶ 自动播放</button>
                    <button class="btn btn-secondary">⏸ 暂停</button>
                    <button class="btn btn-secondary">🔄 刷新</button>
                </div>
                <div class="stats">
                    <div class="stat-item"><div class="stat-value" id="danmuCount">0</div><div class="stat-label">弹幕</div></div>
                    <div class="stat-item"><div class="stat-value" id="videoCount">0</div><div class="stat-label">视频</div></div>
                    <div class="stat-item"><div class="stat-value" id="uptime">00:00</div><div class="stat-label">时长</div></div>
                    <div class="stat-item"><div class="stat-value">¥0</div><div class="stat-label">费用</div></div>
                </div>
            </div>
            <div>
                <div class="panel">
                    <div class="panel-title">发送弹幕</div>
                    <textarea id="danmuInput" placeholder="输入弹幕触发场景..."></textarea>
                    <div class="tags">
                        <span class="tag" onclick="send('禅')">禅</span>
                        <span class="tag" onclick="send('坐')">坐</span>
                        <span class="tag" onclick="send('静')">静</span>
                        <span class="tag" onclick="send('雨')">雨</span>
                        <span class="tag" onclick="send('竹')">竹</span>
                        <span class="tag" onclick="send('山')">山</span>
                        <span class="tag" onclick="send('茶')">茶</span>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-title">系统日志</div>
                    <div class="log-list" id="logList">
                        <div class="log-item">[系统] 直播已启动</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let danmuCount = 0;
        function send(text) {
            document.getElementById('danmuInput').value = text;
            // 实际应该发送到后端API
            danmuCount++;
            document.getElementById('danmuCount').textContent = danmuCount;
            addLog('弹幕: ' + text);
        }
        function addLog(msg) {
            const list = document.getElementById('logList');
            const item = document.createElement('div');
            item.className = 'log-item';
            item.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
            list.insertBefore(item, list.firstChild);
        }
        // 键盘事件
        document.getElementById('danmuInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') send(e.target.value);
        });
    </script>
</body>
</html>
                """
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_error(404)
        
        def do_POST(self):
            if self.path == "/api/danmu":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            else:
                self.send_error(404)
    
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print("Web界面已启动: http://localhost:8080")
    return server


# ============ 主入口 ============
async def main():
    """主函数"""
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "stream"
    
    if mode == "stream":
        # 直播模式
        stream = LiveStream()
        await stream.start()
    elif mode == "web":
        # Web界面模式
        await create_web_interface()
        # 保持运行
        while True:
            await asyncio.sleep(3600)
    elif mode == "test":
        # 测试模式
        print("测试弹幕触发:")
        stream = LiveStream()
        for danmu in ["禅修真舒服", "想听雨声", "竹子好美", "随机内容"]:
            result = stream.process_danmu(danmu)
            print(f"  {danmu} → {result}")


if __name__ == "__main__":
    asyncio.run(main())