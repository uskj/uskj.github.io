#!/usr/bin/env python3
"""
道云AI数字人直播系统
基于AUTOavantar技术栈：DeepSeek + IndexTTS + HeyGem ONNX
支持7x24小时不间断直播
"""

import asyncio
import aiohttp
import json
import time
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import base64

# ============ 配置 ============
class Config:
    # AUTOavantar 技术栈
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your_deepseek_key")
    INDEX_TTS_URL = "http://localhost:8001"  # IndexTTS服务地址
    HEYgem_URL = "http://localhost:8002"     # HeyGem服务地址
    
    # 道云老师配置
    TEACHER_NAME = "道云"
    TEACHER_AVATAR = "daoyun_teacher.mp4"  # 道云老师开场视频
    TEACHER_REFERENCE_AUDIO = "daoyun_voice.mp3"  # 道云老师声音样本
    
    # 直播配置
    VIDEO_DURATION = 30  # 每条视频30秒
    AUTO_SWITCH_INTERVAL = 35  # 35秒切换
    COOLDOWN = 5  # 弹幕冷却5秒
    
    # 课程库
    COURSES = {
        "chanru": {
            "title": "禅修入门",
            "category": "禅修",
            "description": "从呼吸开始，认识自己的心",
            "keywords": ["禅", "修", "呼吸", "静心", "冥想"],
            "script_template": "大家好，我是道云。今天我们来学习禅修入门。禅修不是逃避现实，而是直面内心...",
            "bpm": 60  # 背景音乐节奏
        },
        "dandao": {
            "title": "丹道养生",
            "category": "养生",
            "description": "顺应自然，养生的智慧",
            "keywords": ["丹道", "养生", "气", "自然", "健康"],
            "script_template": "各位朋友好，我是道云。今天分享丹道养生的心得。养生不是吃药...",
            "bpm": 70
        },
        "shufa": {
            "title": "书法静心",
            "category": "书法",
            "description": "一笔一画，修心养性",
            "keywords": ["书法", "写字", "笔墨", "静心", "艺术"],
            "script_template": "朋友们好，我是道云。书法不仅是艺术，更是修心的方法...",
            "bpm": 55
        },
        "shici": {
            "title": "诗词创作",
            "category": "诗词",
            "description": "以诗言志，以词抒情",
            "keywords": ["诗词", "创作", "古诗", "文学", "文化"],
            "script_template": "大家好，我是道云。诗词是中华文化的瑰宝，今天我们聊聊如何创作...",
            "bpm": 65
        },
        "yijing": {
            "title": "易经风水",
            "category": "易经",
            "description": "天地人之道，阴阳变化之理",
            "keywords": ["易经", "风水", "阴阳", "八卦", "命理"],
            "script_template": "各位有缘人，我是道云。易经讲天地人三才之道，风水则是环境与人...",
            "bpm": 50
        }
    }
    
    # 弹幕关键词映射
    DANMU_TRIGGERS = {}
    for course_key, course_data in COURSES.items():
        for keyword in course_data["keywords"]:
            DANMU_TRIGGERS[keyword] = course_key


class CourseContent:
    """课程内容生成器"""
    
    def __init__(self):
        self.cache = {}
    
    async def generate_script(self, course_key: str, topic: str = None) -> str:
        """使用DeepSeek生成课程内容"""
        course = Config.COURSES.get(course_key)
        if not course:
            return "暂无课程内容"
        
        # 检查缓存
        cache_key = f"{course_key}_{topic or 'default'}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 调用DeepSeek生成文案
        prompt = f"""你是道云老师，一位精通禅修、丹道、书法、诗词、易经的传统文化导师。
请为主题"{topic or course['title']}"生成一段30秒的口播文案。
要求：
1. 语言平和、有禅意
2. 结合传统文化智慧
3. 适合直播讲解
4. 字数100-150字

请直接输出文案内容，不要加标题。"""
        
        try:
            script = await self._call_deepseek(prompt)
            self.cache[cache_key] = script
            return script
        except Exception as e:
            print(f"生成文案失败: {e}")
            return course["script_template"]
    
    async def _call_deepseek(self, prompt: str) -> str:
        """调用DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个专业的传统文化讲师道云老师"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                json=payload,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API错误: {resp.status}")


class TTSManager:
    """语音合成管理器（IndexTTS）"""
    
    def __init__(self):
        self.voice_clones = {}
    
    async def clone_voice(self, audio_path: str, voice_id: str) -> bool:
        """克隆声音（5-10秒录音即可）"""
        try:
            # 读取音频文件
            with open(audio_path, 'rb') as f:
                audio_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 调用IndexTTS克隆接口
            payload = {
                "audio": audio_data,
                "voice_id": voice_id,
                "name": Config.TEACHER_NAME
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{Config.INDEX_TTS_URL}/api/clone",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.voice_clones[voice_id] = data.get("voice_uuid")
                        print(f"✓ 声音克隆成功: {voice_id}")
                        return True
                    else:
                        print(f"声音克隆失败: {resp.status}")
                        return False
        except Exception as e:
            print(f"克隆声音错误: {e}")
            return False
    
    async def generate_speech(self, text: str, voice_id: str = None) -> Optional[bytes]:
        """生成语音"""
        if not voice_id:
            voice_id = Config.TEACHER_NAME
        
        try:
            payload = {
                "text": text,
                "voice_id": voice_id,
                "speed": 0.9,  # 稍慢，适合禅修内容
                "pitch": 1.0
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{Config.INDEX_TTS_URL}/api/tts",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        return None
        except Exception as e:
            print(f"语音生成失败: {e}")
            return None


class DigitalHumanManager:
    """数字人驱动管理器（HeyGem ONNX）"""
    
    def __init__(self):
        self.avatar_videos = {}
    
    async def create_avatar(self, avatar_id: str, video_path: str, audio_path: str) -> bool:
        """创建数字人形象"""
        try:
            payload = {
                "avatar_id": avatar_id,
                "video": video_path,
                "audio": audio_path,
                "model": "heygem-onnx"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{Config.HEYgem_URL}/api/avatar/create",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.avatar_videos[avatar_id] = data.get("video_url")
                        print(f"✓ 数字人创建成功: {avatar_id}")
                        return True
                    else:
                        print(f"数字人创建失败: {resp.status}")
                        return False
        except Exception as e:
            print(f"创建数字人错误: {e}")
            return False
    
    async def drive_avatar(self, avatar_id: str, audio_data: bytes) -> Optional[bytes]:
        """驱动数字人（唇形同步）"""
        try:
            # Base64编码音频
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "avatar_id": avatar_id,
                "audio": audio_b64,
                "lip_sync": True,
                "face_enhance": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{Config.HEYgem_URL}/api/avatar/drive",
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        return await resp.read()
                    else:
                        return None
        except Exception as e:
            print(f"驱动数字人失败: {e}")
            return None


class LiveEngine:
    """直播引擎"""
    
    def __init__(self):
        self.content_generator = CourseContent()
        self.tts_manager = TTSManager()
        self.digital_human = DigitalHumanManager()
        
        self.current_course = "chanru"
        self.is_live = False
        self.start_time = None
        self.danmu_count = 0
        self.last_trigger = 0
        self.stats = {
            "videos_generated": 0,
            "total_duration": 0,
            "scripts_generated": 0
        }
    
    async def start(self):
        """启动直播"""
        self.is_live = True
        self.start_time = datetime.now()
        
        print("=" * 60)
        print("道云AI数字人直播系统 v1.0")
        print("基于 AUTOavantar 技术栈")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 初始化
        await self._initialize()
        
        # 开始直播
        await self._main_loop()
    
    async def _initialize(self):
        """初始化"""
        print("\n初始化系统...")
        
        # 克隆声音
        voice_path = f"/mnt/d/Projects/.opencode/daoyun_voice.mp3"
        if os.path.exists(voice_path):
            await self.tts_manager.clone_voice(voice_path, Config.TEACHER_NAME)
        else:
            print("⚠ 未找到声音样本，使用默认声音")
        
        # 创建数字人
        avatar_path = f"/mnt/d/Projects/.opencode/{Config.TEACHER_AVATAR}"
        if os.path.exists(avatar_path):
            await self.digital_human.create_avatar(
                Config.TEACHER_NAME,
                avatar_path,
                voice_path
            )
        else:
            print("⚠ 未找到道云老师视频，使用默认形象")
        
        print("✓ 初始化完成")
    
    async def _main_loop(self):
        """主直播循环"""
        print("\n开始7x24小时直播...")
        
        while self.is_live:
            # 获取下一个课程
            course_key = self._get_next_course()
            course = Config.COURSES.get(course_key, Config.COURSES["chanru"])
            
            print(f"\n▶ 直播课程: {course['title']}")
            
            # 生成文案
            script = await self.content_generator.generate_script(course_key)
            self.stats["scripts_generated"] += 1
            
            # 生成语音
            audio_data = await self.tts_manager.generate_speech(script)
            
            # 驱动数字人
            if audio_data:
                video_data = await self.digital_human.drive_avatar(
                    Config.TEACHER_NAME,
                    audio_data
                )
                
                if video_data:
                    # 保存到缓存
                    cache_path = self._save_video(course_key, video_data)
                    print(f"  ✓ 生成完成: {course['title']}")
                    self.stats["videos_generated"] += 1
                    
                    # 推送到直播平台
                    # TODO: 实现推流逻辑
                    await asyncio.sleep(Config.VIDEO_DURATION)
                else:
                    print(f"  ✗ 数字人驱动失败")
                    await asyncio.sleep(5)
            else:
                print(f"  ✗ 语音生成失败")
                await asyncio.sleep(5)
            
            self.stats["total_duration"] += Config.VIDEO_DURATION
        
        print("\n直播结束")
        self._print_stats()
    
    def _get_next_course(self) -> str:
        """获取下一个课程"""
        keys = list(Config.COURSES.keys())
        # 避免连续重复
        if self.current_course in keys:
            keys = [k for k in keys if k != self.current_course]
        return keys[hash(datetime.now()) % len(keys)]
    
    def _save_video(self, course_key: str, video_data: bytes) -> Optional[Path]:
        """保存视频"""
        cache_dir = Path("/tmp/manlu_daoyun_cache")
        cache_dir.mkdir(exist_ok=True)
        
        video_hash = hashlib.md5(video_data).hexdigest()[:8]
        video_path = cache_dir / f"{course_key}_{video_hash}.mp4"
        
        with open(video_path, 'wb') as f:
            f.write(video_data)
        
        return video_path
    
    def process_danmu(self, text: str) -> Dict:
        """处理弹幕"""
        now = time.time()
        
        if now - self.last_trigger < Config.COOLDOWN:
            remaining = int(Config.COOLDOWN - (now - self.last_trigger))
            return {"status": "cooldown", "remaining": remaining}
        
        # 匹配课程
        for keyword, course_key in Config.DANMU_TRIGGERS.items():
            if keyword in text:
                self.last_trigger = now
                self.danmu_count += 1
                self.current_course = course_key
                return {
                    "status": "triggered",
                    "course": course_key,
                    "title": Config.COURSES[course_key]["title"]
                }
        
        # 未匹配，随机课程
        courses = list(Config.COURSES.keys())
        random_course = courses[hash(text) % len(courses)]
        self.last_trigger = now
        self.danmu_count += 1
        self.current_course = random_course
        return {
            "status": "random",
            "course": random_course,
            "title": Config.COURSES[random_course]["title"],
            "danmu": text
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        return {
            **self.stats,
            "elapsed": int(elapsed),
            "danmu_count": self.danmu_count,
            "uptime": self._format_duration(elapsed)
        }
    
    def stop(self):
        """停止直播"""
        self.is_live = False
        self._print_stats()
    
    def _print_stats(self):
        """打印统计"""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("直播统计")
        print("=" * 60)
        print(f"运行时长: {stats['uptime']}")
        print(f"生成视频: {stats['videos_generated']} 个")
        print(f"生成文案: {stats['scripts_generated']} 篇")
        print(f"弹幕触发: {stats['danmu_count']} 次")
        print("=" * 60)
    
    def _format_duration(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"


# ============ Web界面 ============
async def create_web_interface():
    """创建Web界面"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/" or self.path == "/index.html":
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                
                html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>道云AI数字人直播</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'PingFang SC', sans-serif; background: #0a0a0a; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .logo { font-size: 28px; color: #7a9a7a; letter-spacing: 6px; }
        .live-badge { display: flex; align-items: center; gap: 10px; padding: 10px 20px; background: rgba(255,59,48,0.2); border-radius: 25px; }
        .live-dot { width: 10px; height: 10px; background: #ff3b30; border-radius: 50%; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .main { display: grid; grid-template-columns: 1fr 350px; gap: 20px; margin-top: 20px; }
        .video-section { background: rgba(255,255,255,0.05); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .video-container { aspect-ratio: 16/9; background: #000; position: relative; }
        video { width: 100%; height: 100%; object-fit: cover; }
        .video-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 30px 20px; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); }
        .scene-title { font-size: 32px; font-weight: 300; letter-spacing: 6px; }
        .scene-desc { font-size: 14px; color: rgba(255,255,255,0.7); margin-top: 8px; }
        .controls { display: flex; gap: 10px; padding: 15px; background: rgba(0,0,0,0.3); }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #7a9a7a; color: #fff; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .stats { display: flex; gap: 20px; padding: 15px; background: rgba(0,0,0,0.3); }
        .stat-item { text-align: center; flex: 1; }
        .stat-value { font-size: 28px; color: #7a9a7a; }
        .stat-label { font-size: 12px; color: rgba(255,255,255,0.5); }
        .panel { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px; }
        .panel-title { font-size: 14px; color: #7a9a7a; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        textarea { width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; color: #fff; min-height: 80px; }
        .tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .tag { padding: 6px 14px; background: rgba(122,154,122,0.2); border: 1px solid rgba(122,154,122,0.4); border-radius: 16px; font-size: 13px; cursor: pointer; }
        .log-list { max-height: 150px; overflow-y: auto; font-size: 12px; color: rgba(255,255,255,0.5); }
        .log-item { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">道云<span style="color:#fff;font-weight:300;">AI直播</span></div>
            <div class="live-badge"><div class="live-dot"></div><span>7x24小时直播中</span></div>
        </header>
        <div class="main">
            <div class="video-section">
                <div class="video-container">
                    <video id="videoPlayer" autoplay loop muted></video>
                    <div class="video-overlay">
                        <div class="scene-title" id="sceneTitle">禅修入门</div>
                        <div class="scene-desc" id="sceneDesc">从呼吸开始，认识自己的心</div>
                    </div>
                </div>
                <div class="controls">
                    <button class="btn btn-primary">▶ 自动播放</button>
                    <button class="btn btn-secondary">⏸ 暂停</button>
                    <button class="btn btn-secondary">🔄 刷新</button>
                    <button class="btn btn-secondary">📷 截图</button>
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
                    <div class="panel-title">💬 发送弹幕</div>
                    <textarea id="danmuInput" placeholder="输入弹幕触发课程..."></textarea>
                    <div class="tags">
                        <span class="tag" onclick="send('禅')">禅修入门</span>
                        <span class="tag" onclick="send('丹')">丹道养生</span>
                        <span class="tag" onclick="send('书')">书法静心</span>
                        <span class="tag" onclick="send('诗')">诗词创作</span>
                        <span class="tag" onclick="send('易')">易经风水</span>
                    </div>
                </div>
                <div class="panel">
                    <div class="panel-title">📋 系统日志</div>
                    <div class="log-list" id="logList">
                        <div class="log-item">[系统] 道云AI直播已启动</div>
                        <div class="log-item">[系统] 基于AUTOavantar技术</div>
                        <div class="log-item">[系统] 7x24小时自动运行</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        let danmuCount = 0;
        function send(text) {
            document.getElementById('danmuInput').value = text;
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
        document.getElementById('danmuInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter') send(e.target.value);
        });
        let seconds = 0;
        setInterval(() => {
            seconds++;
            const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
            const secs = (seconds % 60).toString().padStart(2, '0');
            document.getElementById('uptime').textContent = mins + ':' + secs;
        }, 1000);
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
    
    server = HTTPServer(('0.0.0.0', 8081), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print("道云AI直播Web界面已启动: http://localhost:8081")
    return server


# ============ 主入口 ============
async def main():
    """主函数"""
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "stream"
    
    if mode == "stream":
        # 直播模式
        engine = LiveEngine()
        await engine.start()
    elif mode == "web":
        # Web界面模式
        await create_web_interface()
        while True:
            await asyncio.sleep(3600)
    elif mode == "test":
        # 测试模式
        print("测试道云AI直播系统:")
        engine = LiveEngine()
        for danmu in ["禅修好", "想学丹道", "书法教学", "易经讲解"]:
            result = engine.process_danmu(danmu)
            print(f"  {danmu} → {result}")
    elif mode == "demo":
        # 演示模式
        print("=" * 60)
        print("道云AI数字人直播系统 - 演示模式")
        print("基于 AUTOavantar 技术栈")
        print("=" * 60)
        print("\n请先配置以下服务：")
        print("  1. DeepSeek API Key")
        print("  2. IndexTTS 服务 (localhost:8001)")
        print("  3. HeyGem 服务 (localhost:8002)")
        print("\n当前模式：仅启动Web界面")
        await create_web_interface()
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())