// ══════════════════════════════════════════════════════════════
// 「息」后端 —— Cloudflare Worker（opencode 的"手"）
//   前端只调 /api/echo /api/activate /api/state，永远看不到 opencode。
//   模型调用封装在此：OPENCODE_*/XI_* 只在 Worker 环境变量。
//   KV(XI_KV) 存用户配额与卡密已用状态。
// ══════════════════════════════════════════════════════════════

const ROLES = {
  anger:   {key:"anger",   name:"火焰守护者", color:"#ff6a3d", emoji:"🔥"},
  fear:    {key:"fear",    name:"迷雾行者",   color:"#9b8cff", emoji:"🌫️"},
  sad:     {key:"sad",     name:"深海潜水员", color:"#3d7bff", emoji:"🌊"},
  joy:     {key:"joy",     name:"彩虹编织者", color:"#ff7ad9", emoji:"🌈"},
  disgust: {key:"disgust", name:"荆棘守望者", color:"#7bbf6a", emoji:"🌿"},
  surprise:{key:"surprise",name:"破晓者",    color:"#ffce4d", emoji:"🌅"},
  anticip: {key:"anticip", name:"星轨航行者", color:"#cfe8ff", emoji:"🌠"},
  calm:    {key:"calm",    name:"湖面映照者", color:"#8fe0d8", emoji:"🪷"},
};
const EMO_KW = {
  anger:["气","愤怒","烦","火大","受不了","凭什么","骂","炸","怒","不公平","欺负"],
  fear:["怕","焦虑","紧张","担心","害怕","不安","慌","睡不着","压力","撑不住","崩溃"],
  sad:["累","难过","哭","委屈","失落","孤独","空","没意思","想放弃","低落","丧","疲惫"],
  joy:["开心","高兴","爽","太好了","幸福","满足","喜欢","赢了","成功","哈哈","棒"],
  disgust:["恶心","讨厌","受够","腻","假","虚伪","反感","嫌"],
  surprise:["没想到","惊","居然","竟然","突然","意外","震惊","吓"],
  anticip:["期待","希望","想要","计划","以后","将来","梦想","准备","等不及"],
  calm:["平静","还好","安静","放松","释然","看开","无所谓","淡定","松了口气"],
};
const XI_SYSTEM = (
  "你是「息」，一个情绪按摩师。规则：绝不诊断、绝不说教、绝不给建议式命令。"
  "只用温柔的语言接住对方的情绪。每次返回严格 JSON："
  "{\"insight\":\"一句话看见对方的情绪\",\"breath\":\"一句具体的呼吸引导\","
  "\"closing\":\"一句轻轻收尾的话\"}。每句不超过 40 字，像贴着耳朵说话。"
);
const VOICES = [
  {key:"gentle",  name:"温婉女生"},
  {key:"sister",  name:"知性姐姐"},
  {key:"charming",name:"迷人帅哥"},
];
const TRIAL_CODES = [
  {label:"24小时体验",code:"24-xi9823471234"},
  {label:"72小时体验",code:"72-xi9823471235"},
  {label:"198小时体验",code:"198-xi9823471236"},
];
const FALLBACK = {
  anger:  {insight:"你气的不是那件事，是那个无能为力的自己。",breath:"攥紧拳再松开，吸气4秒屏2秒呼6秒，三轮。",closing:"你的怒，是你在意。"},
  fear:   {insight:"怕的是还没发生的念头一遍遍预演。",breath:"手扶桌沿闭眼，只数三次呼吸，回到地面。",closing:"雾会散，你先停。"},
  sad:    {insight:"你不是脆弱，是认真地活过。",breath:"手放心口，吸气顶起呼气塌下，三轮。",closing:"我陪你潜一会儿。"},
  joy:    {insight:"开心先存进身体，它会是后来的光。",breath:"深吸憋两秒，笑着手举高再呼出。",closing:"这一刻，是你的。"},
  disgust:{insight:"你反感的，是曾被冒犯没说出口的自己。",breath:"跺脚，呼气时把腻味轻轻吐掉，三轮。",closing:"你的边界，值得守。"},
  surprise:{insight:"意外撕开日常，那道光一直都在。",breath:"找一处光，吸气4秒闭眼屏息再呼出。",closing:"破晓，每天都来。"},
  anticip:{insight:"你期待的是那个认真想象的自己。",breath:"仰望，吸气沿光带上升呼气落回。",closing:"路，正亮着。"},
  calm:   {insight:"你能平静，是因为有些东西想通了。",breath:"只感受一次完整呼吸，吸4呼6，三轮。",closing:"就这样，挺好。"},
};

const OPENCODE_KEY = typeof OPENCODE_KEY_SECRET !== "undefined" ? OPENCODE_KEY_SECRET : (typeof OPENCODE_KEY !== "undefined" ? OPENCODE_KEY : "");

function classifyEmotion(text, hint) {
  if (hint && ROLES[hint]) return hint;
  const t = (text || "").toLowerCase();
  let best = null, bs = 0;
  for (const [emo, kws] of Object.entries(EMO_KW)) {
    let s = 0; for (const k of kws) if (t.includes(k)) s++;
    if (s > bs) { bs = s; best = emo; }
  }
  return best || "calm";
}

async function loadUser() {
  const v = await XI_KV.get("user");
  try { return v ? JSON.parse(v) : {}; } catch { return {}; }
}
async function saveUser(u) { await XI_KV.put("user", JSON.stringify(u)); }

async function checkQuota() {
  let u = await loadUser();
  const today = new Date().toISOString().slice(0,10);
  if (u.day !== today) { u.day = today; u.free_used = 0; await saveUser(u); }
  const member = (u.expires || 0) > Date.now();
  const remain = member ? 999 : Math.max(0, (XI_FREE_PER_DAY) - (u.free_used || 0));
  return { ok: remain > 0, remain, member };
}
async function consumeQuota(emo, roleName) {
  let u = await loadUser();
  if ((u.expires || 0) <= Date.now()) u.free_used = (u.free_used || 0) + 1;
  u.garden = u.garden || [];
  u.garden.push({ t: Math.floor(Date.now()/1000), emo, role: roleName });
  u.garden = u.garden.slice(-100);
  await saveUser(u);
}

async function verifyCard(code) {
  code = (code || "").trim();
  if (!code) return null;
  const used = JSON.parse(await XI_KV.get("used") || "[]");
  if (used.includes(code)) return null;
  const CARDS = (XI_CARDS || "").split(",");
  if (CARDS.includes(code)) {
    used.push(code); await XI_KV.put("used", JSON.stringify(used));
    return true;
  }
  return null;
}

async function callAI(message, emo, voiceKey) {
  const role = ROLES[emo] || ROLES.calm;
  const voice = VOICES.find(v => v.key === voiceKey) || VOICES[0];
  const userPrompt = `对方说：${message}\n情绪：${role.name}（${emo}）。语言模式：${voice.name}。`;
  const payload = {
    model: OPENCODE_MODEL,
    messages: [
      { role: "system", content: XI_SYSTEM },
      { role: "user", content: userPrompt }
    ],
    temperature: 0.9, response_format: { type: "json_object" }
  };
  const headers = { "Content-Type": "application/json" };
  if (OPENCODE_KEY) headers["Authorization"] = `Bearer ${OPENCODE_KEY}`;
  try {
    const r = await fetch(`${OPENCODE_BASE}/chat/completions`, {
      method: "POST", headers, body: JSON.stringify(payload)
    });
    const data = await r.json();
    return JSON.parse(data.choices[0].message.content);
  } catch (e) {
    return FALLBACK[emo] || { insight:"我在这里。", breath:"慢慢呼吸，吸气4秒呼气6秒。", closing:"陪你一会儿。" };
  }
}

function json(obj) {
  return new Response(JSON.stringify(obj), {
    headers: { "Content-Type":"application/json; charset=utf-8", "Cache-Control":"no-store", "Access-Control-Allow-Origin":"*" }
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname;

    if (path === "/api/state") {
      const q = await checkQuota();
      return json({ remain:q.remain, member:q.member, free_per_day:XI_FREE_PER_DAY,
                   roles:Object.values(ROLES), voices:VOICES, trial_codes:TRIAL_CODES });
    }

    if (path === "/api/echo" && request.method === "POST") {
      const q = await checkQuota();
      if (!q.ok) return json({ ok:false, reason:"quota", msg:"今天的三次呼吸用完了。但你此刻的声音里，好像还有话想说。" });
      let body; try { body = await request.json(); } catch { body = {}; }
      const msg = body.message || "";
      const emo = classifyEmotion(msg, body.emotion);
      const role = ROLES[emo] || ROLES.calm;
      const res = await callAI(msg, emo, body.voice || "");
      await consumeQuota(emo, role.name);
      const q2 = await checkQuota();
      return json({ ok:true, role, insight:res.insight||"", breath:res.breath||"", closing:res.closing||"",
                   remain:q2.remain, member:q2.member });
    }

    if (path === "/api/activate" && request.method === "POST") {
      let body; try { body = await request.json(); } catch { body = {}; }
      const ok = await verifyCard(body.code || "");
      if (!ok) return json({ ok:false, msg:"卡密无效或已使用" });
      let u = await loadUser();
      const h = parseInt((body.code || "24-").split("-")[0]) || 72;
      u.expires = Math.max(u.expires || 0, Date.now()) + h * 3600 * 1000;
      await saveUser(u);
      return json({ ok:true, msg:`已解锁 ${h} 小时无限呼吸` });
    }

    return new Response("Not Found", { status: 404 });
  }
};
