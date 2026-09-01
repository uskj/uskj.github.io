# 漫庐AI直播 - 免费版

## 访问地址

**本地测试：** http://localhost:8080/articles/manlu-live/free.html
**线上访问：** https://uskj.github.io/articles/manlu-live/free.html

---

## 功能说明

| 功能 | 状态 |
|------|------|
| 弹幕互动 | ✅ 正常 |
| 场景切换 | ✅ 6个场景 |
| 自动播放 | ✅ 10秒切换 |
| 截图保存 | ✅ 下载PNG |
| 实时统计 | ✅ 弹幕/时长/费用 |

---

## 弹幕关键词

```
禅/坐/静/心 → 禅房静坐
书/墨/字/写 → 书房写字
雨 → 雨夜听声
竹 → 竹林听风
山 → 漫庐山居
茶 → 茶道静心
```

---

## 启动方式

```bash
# 1. 进入项目目录
cd /mnt/d/Projects/.opencode/uskj-pages

# 2. 启动Web服务
python3 -m http.server 8080

# 3. 浏览器访问
http://localhost:8080/articles/manlu-live/free.html
```

---

## 7x24小时运行

```bash
# 后台运行
nohup python3 -m http.server 8080 > /dev/null 2>&1 &

# 查看日志
tail -f /dev/null

# 停止服务
pkill -f "http.server 8080"
```

---

**免费方案无需API，完全离线可用。**