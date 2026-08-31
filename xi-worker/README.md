# 息 · 后端 Worker（Cloudflare）

把 server.py 改写成 Cloudflare Worker，逻辑等价：/api/state、/api/echo、/api/activate。
情绪分类、配额、卡密、opencode 调用、离线兜底全部一致。状态存 KV（无数据库）。

## 部署（约 5 分钟，需 Cloudflare 账号，可用 GitHub 登录）

1. 注册 https://dash.cloudflare.com （GitHub 登录即可）。
2. 左侧 **Workers & Pages** → **Create** → 选 **Workers** → 命名 `xi-backend`。
3. 创建后进入 Worker，点 **Settings → Variables**：
   - KV 命名空间：新建一个 `XI_KV` 绑定到本 Worker。
   - 环境变量（明文即可）：`OPENCODE_BASE=https://opencode.ai/go/v1`、`OPENCODE_MODEL=deepseek-v4-flash`、
     `XI_FREE_PER_DAY=3`、`XI_CARDS=24-xi9823471234,72-xi9823471235,198-xi9823471236,24-xi30b706d7`。
   - 接真模型：再加 secret `OPENCODE_KEY`（留空则走离线兜底）。
4. 把 `worker.js` 内容粘到 Worker 编辑器（或 `wrangler deploy`，需先填 wrangler.toml 的 KV id）。
5. 部署完成得 `https://xi-backend.<你的子域>.workers.dev`。

## 前端对接

改 `xi/index.html` 顶部 `XI_API_BASE` 为上面的 Worker 地址，推到 GitHub Pages。

## 注意

- 免费 Workers 每日 10 万请求，足够个人用。
- `XI_CARDS` 卡密仅演示门槛，KV 已防复用。
