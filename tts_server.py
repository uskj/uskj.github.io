"""
漫庐 AI 陪伴者 TTS 服务
使用 edge-tts（微软 Edge 神经网络中文语音）
启动后浏览器自动调用，无需配置

用法: python tts_server.py
默认端口: 18090
"""
import asyncio
import base64
import io
import logging
from contextlib import asynccontextmanager

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-10%"


async def generate_audio(text: str) -> bytes:
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    buffer = io.BytesIO()
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])
    return buffer.getvalue()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"✅ TTS 服务已启动 | 语音: {VOICE} | 端口: 18090")
    yield
    logger.info("TTS 服务已停止")


app = FastAPI(title="Manlu TTS", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TTSRequest(BaseModel):
    text: str
    session_id: str = ""


class TTSResponse(BaseModel):
    ok: bool
    data: str = ""
    msg: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "voice": VOICE}


@app.post("/tts", response_model=TTSResponse)
async def tts(req: TTSRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    try:
        mp3_data = await generate_audio(req.text)
        b64 = base64.b64encode(mp3_data).decode()
        return TTSResponse(ok=True, data=b64)
    except Exception as e:
        logger.error(f"TTS 生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=18090, log_level="warning")
