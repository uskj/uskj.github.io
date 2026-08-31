const BASE_URL = "speech.platform.bing.com/consumer/speech/synthesize/readaloud";
const TRUSTED_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4";
const WSS_URL = `wss://${BASE_URL}/edge/v1?TrustedClientToken=${TRUSTED_TOKEN}`;
const VOICES_URL = `https://${BASE_URL}/voices/list?trustedclienttoken=${TRUSTED_TOKEN}`;

const CHROMIUM_VERSION = "143.0.3650.75";
const CHROMIUM_MAJOR = CHROMIUM_VERSION.split(".")[0];

const BASE_HEADERS = {
  "User-Agent": `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/${CHROMIUM_MAJOR}.0.0.0 Safari/537.36 Edg/${CHROMIUM_MAJOR}.0.0.0`,
  "Accept-Encoding": "gzip, deflate, br",
  "Accept-Language": "en-US,en;q=0.9",
};

const WSS_HEADERS = {
  "Pragma": "no-cache",
  "Cache-Control": "no-cache",
  "Origin": "chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold",
  "Sec-WebSocket-Version": "13",
  ...BASE_HEADERS,
};

async function getVoices() {
  const res = await fetch(VOICES_URL);
  return res.json();
}

async function synthesize(text, voice = "zh-CN-XiaoxiaoNeural", rate = "-20%", pitch = "+0Hz") {
  const ws = new WebSocket(WSS_URL, ["Guaja"], { headers: WSS_HEADERS });

  return new Promise((resolve, reject) => {
    let audioChunks = [];
    let metadata = {};

    ws.onopen = () => {
      const timestamp = new Date().toISOString();
      const configLine = `Paths:Synthesize.Speech\r\nHost:${BASE_URL}\r\nX-Timestamp:${timestamp}\r\n\r\n`;
      ws.send(configLine);
    };

    ws.onmessage = (event) => {
      const data = event.data;
      if (typeof data === "string") {
        const lines = data.split(/\r?\n/);
        for (const line of lines) {
          if (line.startsWith("Status:") || line.startsWith("X-") || line.includes("RequestId")) {
            const idx = line.indexOf(":");
            if (idx > 0) {
              const key = line.substring(0, idx).trim();
              const val = line.substring(idx + 1).trim();
              if (key && val) metadata[key] = val;
            }
          }
        }
      } else if (data instanceof ArrayBuffer) {
        audioChunks.push(data);
      } else if (data instanceof Blob) {
        data.arrayBuffer().then(buf => audioChunks.push(buf)).catch(reject);
        return;
      }
    };

    ws.onerror = (err) => reject(new Error("WebSocket error: " + (err.message || "unknown")));

    const timeout = setTimeout(() => {
      ws.close();
      reject(new Error("TTS timeout after 90s"));
    }, 90000);

    ws.onclose = (event) => {
      clearTimeout(timeout);
      if (event.code === 1000 && audioChunks.length > 0) {
        const totalLen = audioChunks.reduce((sum, chunk) => sum + chunk.byteLength, 0);
        const merged = new Uint8Array(totalLen);
        let offset = 0;
        for (const chunk of audioChunks) {
          merged.set(new Uint8Array(chunk), offset);
          offset += chunk.byteLength;
        }
        resolve({ audio: merged.buffer, metadata });
      } else {
        reject(new Error(`No audio received or connection closed (code: ${event.code})`));
      }
    };
  });
}

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get("Origin") || "*";
    const corsHeaders = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Access-Control-Max-Age": "86400",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders });
    }

    try {
      const url = new URL(request.url);

      if (request.method === "GET" && url.pathname === "/api/voices") {
        const voices = await getVoices();
        return new Response(JSON.stringify(voices), {
          headers: { "Content-Type": "application/json", ...corsHeaders },
        });
      }

      if (request.method === "POST" && url.pathname === "/api/tts") {
        const { text, voice = "zh-CN-XiaoxiaoNeural", rate = "-20%", pitch = "+0Hz" } = await request.json();
        if (!text || !text.trim()) {
          return new Response(JSON.stringify({ ok: false, msg: "text is required" }), {
            status: 400, headers: { "Content-Type": "application/json", ...corsHeaders },
          });
        }

        const result = await synthesize(text.trim(), voice, rate, pitch);
        const base64Audio = btoa(Array.from(new Uint8Array(result.audio)).map(b => String.fromCharCode(b)).join(""));
        return new Response(JSON.stringify({ ok: true, data: base64Audio }), {
          headers: { "Content-Type": "application/json", ...corsHeaders },
        });
      }

      return new Response("Not Found", { status: 404, headers: { ...corsHeaders } });
    } catch (err) {
      return new Response(JSON.stringify({ ok: false, msg: err.message }), {
        status: 500, headers: { "Content-Type": "application/json", ...corsHeaders },
      });
    }
  },
};
