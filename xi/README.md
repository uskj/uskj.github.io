# 息 · 情绪按摩

一个随时可用的情绪按摩应用：说一句话或长按叹气，它就接住你的情绪，
给你一句看见、一句呼吸、一句轻轻收尾。手机可装到主屏（PWA），离线也能读。

## 架构

```
[息 前端 · 浏览器 / GitHub Pages]          [息 后端 · server.py]
  index.html / sw.js / manifest.json   →   /api/echo  /api/activate  /api/state
  （PWA，纯静态，可离线）                      │
                                              └─→ opencode 网关（模型之手，密钥只在服务端）
```

- **前端**只调 `/api/echo` 等普通接口，**永远看不到背后的 opencode**。
- **后端 server.py** 封装模型调用：把情绪文本转成「息」风格的洞察，密钥存在环境变量。
- 模型调用失败时有离线兜底文案，服务不中断。

## 铁律

「息」产品本身不直连任何模型——模型调用被封在后端 server（opencode 的"手"），
对用户完全透明为普通 REST 接口。

## 本地预览

```bash
# 后端（调 opencode，需联网）
set OPenCode_BASE_URL=https://opencode.ai/go/v1
python server.py
# 打开 http://localhost:8088

# 或直接双击（纯静态，但那样前端调不到后端，需手动改 API_BASE）
start.bat
```

`index.html` 顶部 `XI_API_BASE = ''` 表示同域调后端。
若前端和后端不同域，改成后端地址，如 `const XI_API_BASE = 'https://xi-backend.onrender.com'`。

## 公网部署

### 后端 → Render（免费层，跑 server.py，连 opencode）

1. 注册 https://render.com （用 GitHub 登录）。
2. New → Blueprint → 选本仓库（仓库根目录已有 `render.yaml`）。
3. 在 `XI_CARDS` 变量填入你的卡密串（格式见 `.env.example`，其余变量已预填）。
4. Create New Resources → 等待部署，拿到域名如 `https://xi-backend.onrender.com`。
5. 免费层会休眠，首次访问需冷启动几秒，正常。

### 前端 → GitHub Pages（静态托管）

1. 仓库已推到 `uskj.github.io`（前端在 `xi/` 子目录）。
2. 改 `index.html` 顶部 `XI_API_BASE` 为 Render 后端域名：
   `const XI_API_BASE = 'https://xi-backend.onrender.com'`
3. 开启 GitHub Pages（main 分支根目录）。
4. 手机访问 `https://uskj.github.io/xi/` → 加到主屏即可离线使用。

## 卡密 / 会员

- 每天免费 3 次呼吸（`XI_FREE_PER_DAY`）。
- 卡密在 `XI_CARDS` 环境变量配置；激活后服务端记 `expires` 时间戳解锁无限。
- GitHub Pages 源码公开，卡密仅作演示门槛，不做真安全校验。

## 文件

- `index.html` — 前端（PWA，零依赖）
- `server.py` — 后端（opencode 之手，配额/卡密/情绪分类/模型调用）
- `sw.js` / `manifest.json` / `icon.svg` — PWA
- `railway.json` / `Procfile` / `requirements.txt` / `render.yaml` — 部署配置
- `config.json` — 参考配置（前端已内置，不必读取）
- `gen_codes.py` — 卡密生成器（部署者本地用）
