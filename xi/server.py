#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════
#  「息」后端 —— opencode 的"手"
#  前端只调 /api/echo /api/activate /api/state，永远看不到 opencode。
#  模型调用封装在此：OPenCode_BASE_URL + OPenCode_KEY 只在服务端环境变量。
# ════════════════════════════════════════════════════════════════════
import json, os, time, base64, urllib.request, urllib.error, io, asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from pathlib import Path

# ── TTS（edge-tts，微软神经网络中文语音）──────────────────────
def _tts_gen(text: str) -> bytes:
    """用 edge-tts 生成 MP3 字节"""
    import asyncio as _asyncio, io as _io, edge_tts as _et
    buf = _io.BytesIO()
    async def _gen():
        comm = _et.Communicate(text, "zh-TW-HsiaoChenNeural", rate="-25%", pitch="+15Hz")
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                buf.write(chunk["data"])
    _asyncio.run(_gen())
    return buf.getvalue()

BASE = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8088"))
HOST = os.environ.get("HOST", "0.0.0.0")
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE))

# ── opencode（模型网关）配置：只在服务端，前端不可见 ──
OPENCODE_BASE = os.environ.get("OPenCode_BASE_URL", "https://opencode.ai/go/v1")
OPENCODE_KEY  = os.environ.get("OPenCode_KEY", "")   # 免费模式可留空
OPENCODE_MODEL= os.environ.get("OPenCode_MODEL", "deepseek-v4-flash")

# ── 配置（部署后可改环境变量；此处为默认值）──
FREE_PER_DAY = int(os.environ.get("XI_FREE_PER_DAY", "3"))
CARDS = os.environ.get("XI_CARDS", "24-xi9823471234,72-xi9823471235,198-xi9823471236,24-xi30b706d7").split(",")
TRIAL_CODES = [{"label":"24小时体验","code":"24-xi9823471234"},
               {"label":"72小时体验","code":"72-xi9823471235"},
               {"label":"198小时体验","code":"198-xi9823471236"}]

ROLES = {
    "anger":   {"key":"anger",   "name":"火焰守护者", "color":"#ff6a3d", "emoji":"🔥"},
    "fear":    {"key":"fear",    "name":"迷雾行者",   "color":"#9b8cff", "emoji":"🌫️"},
    "sad":     {"key":"sad",     "name":"深海潜水员", "color":"#3d7bff", "emoji":"🌊"},
    "joy":     {"key":"joy",     "name":"彩虹编织者", "color":"#ff7ad9", "emoji":"🌈"},
    "disgust": {"key":"disgust", "name":"荆棘守望者", "color":"#7bbf6a", "emoji":"🌵"},
    "surprise": {"key":"surprise","name":"破晓者",    "color":"#ffce4d", "emoji":"🌅"},
    "anticip": {"key":"anticip", "name":"星轨航行者", "color":"#cfe8ff", "emoji":"🌠"},
    "calm":    {"key":"calm",    "name":"湖面映照者", "color":"#8fe0d8", "emoji":"🪷"},
}

EMO_KW = {
    "anger":["气","愤怒","烦","火大","受不了","凭什么","骂","怼","炸","怒","不公平","欺负"],
    "fear":["怕","焦虑","紧张","担心","害怕","不安","慌","睡不着","压力","撑不住","崩溃"],
    "sad":["累","难过","哭","委屈","失落","孤独","空","没意思","想放弃","低落","丧","疲惫"],
    "joy":["开心","高兴","爽","太好了","幸福","满足","喜欢","赢了","成功","哈哈","棒"],
    "disgust":["恶心","讨厌","受够","腻","假","虚伪","反感","嫌"],
    "surprise":["没想到","惊","居然","竟然","突然","意外","震惊","吓"],
    "anticip":["期待","希望","想要","计划","以后","将来","梦想","准备","等不及"],
    "calm":["平静","还好","安静","放松","释然","看开","无所谓","淡定","松了口气"],
}

# 「息」人格壳 —— 给模型看的系统提示，强调陪伴、不评判、不诊断
XI_SYSTEM = (
    "你是「息」，一个情绪按摩师。规则：绝不诊断、绝不说教、绝不给建议式命令。"
    "只用温柔的语言接住对方的情绪。每次返回严格 JSON："
    "{\"insight\":\"一句话看见对方的情绪\",\"breath\":\"一句具体的呼吸引导\","
    "\"closing\":\"一句轻轻收尾的话\"}。每句不超过 40 字，像贴着耳朵说话。"
)

VOICES = [
    {"key":"gentle",  "name":"温婉女生"},
    {"key":"sister",  "name":"知性姐姐"},
    {"key":"charming","name":"迷人帅哥"},
]

# ── 用户态（服务端文件）──
USER_FILE = DATA_DIR / "data" / "user.json"
USER_FILE.parent.mkdir(parents=True, exist_ok=True)
def load_user():
    try: return json.loads(USER_FILE.read_text(encoding="utf-8"))
    except: return {}
def save_user(u): USER_FILE.write_text(json.dumps(u, ensure_ascii=False), encoding="utf-8")

def check_quota():
    u = load_user(); today = time.strftime("%Y-%m-%d")
    if u.get("day") != today: u["day"]=today; u["free_used"]=0; save_user(u)
    member = u.get("expires", 0) > time.time()
    remain = 999 if member else max(0, FREE_PER_DAY - u.get("free_used", 0))
    return (remain > 0), remain, member

def consume_quota(emo, role_name):
    u = load_user()
    if u.get("expires", 0) <= time.time(): u["free_used"] = u.get("free_used",0)+1
    u.setdefault("garden", []).append({"t":int(time.time()),"emo":emo,"role":role_name})
    u["garden"] = u["garden"][-100:]; save_user(u)

def classify_emotion(text, hint):
    if hint and hint in ROLES: return hint
    t = (text or "").lower(); best=None; bs=0
    for emo, kws in EMO_KW.items():
        s = sum(1 for k in kws if k in t)
        if s > bs: bs=s; best=emo
    return best or "calm"

def verify_card(code):
    code = (code or "").strip()
    if not code: return None
    used = json.loads((DATA_DIR/"data"/"used.json").read_text(encoding="utf-8") if (DATA_DIR/"data"/"used.json").exists() else "[]")
    if code in used: return None
    if code in CARDS:
        used.append(code); (DATA_DIR/"data"/"used.json").write_text(json.dumps(used), encoding="utf-8")
        return True
    return None

# ── 调 opencode（封装，前端不可见）──
def call_ai(message, emo, voice_key):
    role = ROLES.get(emo, ROLES["calm"])
    voice = next((v for v in VOICES if v["key"]==voice_key), VOICES[0])
    user_prompt = f"对方说：{message}\n情绪：{role['name']}（{emo}）。语言模式：{voice['name']}。"
    payload = {
        "model": OPENCODE_MODEL,
        "messages":[
            {"role":"system","content":XI_SYSTEM},
            {"role":"user","content":user_prompt}
        ],
        "temperature":0.9, "response_format":{"type":"json_object"}
    }
    headers = {"Content-Type":"application/json"}
    if OPENCODE_KEY: headers["Authorization"] = f"Bearer {OPENCODE_KEY}"
    req = urllib.request.Request(f"{OPENCODE_BASE}/chat/completions",
                                 data=json.dumps(payload).encode(), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode())
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        # 兜底：模型不可用时仍给一句离线文案，保证服务不中断
        c = {
            "anger":  {"insight":"你气的不是那件事，是那个无能为力的自己。","breath":"攥紧拳再松开，吸气4秒屏2秒呼6秒，三轮。","closing":"你的怒，是你在意。"},
            "fear":   {"insight":"怕的是还没发生的念头一遍遍预演。","breath":"手扶桌沿闭眼，只数三次呼吸，回到地面。","closing":"雾会散，你先停。"},
            "sad":    {"insight":"你不是脆弱，是认真地活过。","breath":"手放心口，吸气顶起呼气塌下，三轮。","closing":"我陪你潜一会儿。"},
            "joy":    {"insight":"开心先存进身体，它会是后来的光。","breath":"深吸憋两秒，笑着手举高再呼出。","closing":"这一刻，是你的。"},
            "disgust":{"insight":"你反感的，是曾被冒犯没说出口的自己。","breath":"跺脚，呼气时把腻味轻轻吐掉，三轮。","closing":"你的边界，值得守。"},
            "surprise":{"insight":"意外撕开日常，那道光一直都在。","breath":"找一处光，吸气4秒闭眼屏息再呼出。","closing":"破晓，每天都来。"},
            "anticip":{"insight":"你期待的是那个认真想象的自己。","breath":"仰望，吸气沿光带上升呼气落回。","closing":"路，正亮着。"},
            "calm":   {"insight":"你能平静，是因为有些东西想通了。","breath":"只感受一次完整呼吸，吸4呼6，三轮。","closing":"就这样，挺好。"},
        }.get(emo, {"insight":"我在这里。","breath":"慢慢呼吸，吸气4秒呼气6秒。","closing":"陪你一会儿。"})
        return c

class Handler(BaseHTTPRequestHandler):
    def _send(self, obj, ct="application/json"):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", f"{ct}; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"): self._send((BASE/"index.html").read_bytes(), "text/html")
        elif path == "/manifest.json": self._send((BASE/"manifest.json").read_bytes(), "application/manifest+json")
        elif path == "/sw.js": self._send((BASE/"sw.js").read_bytes(), "text/javascript")
        elif path == "/api/state":
            ok, remain, member = check_quota()
            self._send({"remain":remain,"member":member,"free_per_day":FREE_PER_DAY,
                        "roles":list(ROLES.values()),"voices":VOICES,"trial_codes":TRIAL_CODES})
        elif path == "/api/tts-health":
            self._send({"ok": True, "voice": "zh-TW-HsiaoChenNeural", "rate": "-25%", "pitch": "+15Hz"})
        else: self.send_error(404)
    def do_POST(self):
        path = urlparse(self.path).path
        n = int(self.headers.get("Content-Length",0))
        body = json.loads(self.rfile.read(n)) if n else {}
        if path == "/api/echo":
            ok, remain, member = check_quota()
            if not ok:
                self._send({"ok":False,"reason":"quota","msg":"今天的三次呼吸用完了。但你此刻的声音里，好像还有话想说。"}); return
            msg = body.get("message",""); hint = body.get("emotion"); voice_key = body.get("voice","")
            emo = classify_emotion(msg, hint); role = ROLES.get(emo, ROLES["calm"])
            res = call_ai(msg, emo, voice_key); consume_quota(emo, role["name"])
            _, r2, m2 = check_quota()
            self._send({"ok":True,"role":role,"insight":res.get("insight",""),
                        "breath":res.get("breath",""),"closing":res.get("closing",""),
                        "remain":r2,"member":m2})
        elif path == "/api/activate":
            hours = verify_card(body.get("code",""))
            if hours is None: self._send({"ok":False,"msg":"卡密无效或已使用"}); return
            u = load_user(); h = int((body.get("code","24-").split("-")[0]) or 72)
            u["expires"] = max(u.get("expires",0), time.time()) + h*3600
            save_user(u); self._send({"ok":True,"msg":f"已解锁 {h} 小时无限呼吸"})
        elif path == "/api/tts":
            text = body.get("text","").strip()
            if not text:
                self._send({"ok":False,"msg":"text is required"}); return
            try:
                mp3 = _tts_gen(text)
                b64 = base64.b64encode(mp3).decode()
                self._send({"ok":True,"data":b64})
            except Exception as e:
                self._send({"ok":False,"msg":str(e)})
        else: self.send_error(404)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[息] 后端启动 → http://{HOST}:{PORT}  (opencode: {OPENCODE_BASE})")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
