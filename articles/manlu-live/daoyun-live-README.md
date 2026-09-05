# 道云AI数字人直播系统

## 基于 AUTOavantar 技术栈

### 核心技术

| 组件 | 技术 | 功能 |
|------|------|------|
| 文案生成 | DeepSeek/阿里云 | AI自动生成口播稿 |
| 语音克隆 | IndexTTS | 5-10秒录音学声线 |
| 数字人驱动 | HeyGem ONNX | 唇形同步精度高 |
| 视频后期 | 自动拼接 | BGM、字幕、转场 |

---

## 快速开始

### 1. 安装依赖

```bash
cd /mnt/d/Projects/.opencode
pip install aiohttp pillow
```

### 2. 部署AUTOavantar

```bash
# 克隆项目
git clone https://github.com/Eikwang/AUTOavantar.git
cd AUTOavantar

# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn api.main:app --host 0.0.0.0 --port 9010
```

### 3. 配置道云老师

```bash
# 准备素材
# 1. 录制道云老师开场视频（daoyun_teacher.mp4）
# 2. 录制声音样本（5-10秒，daoyun_voice.mp3）

# 移动到项目目录
cp /path/to/daoyun_teacher.mp4 /mnt/d/Projects/.opencode/
cp /path/to/daoyun_voice.mp3 /mnt/d/Projects/.opencode/
```

### 4. 启动直播

```bash
# 演示模式
python3 daoyun-live.py demo

# 正式直播（需要配置API）
export DEEPSEEK_API_KEY="your_key"
python3 daoyun-live.py stream
```

### 5. 访问界面

```
http://localhost:8081
```

---

## 课程库

| 课程 | 关键词 | 时长 |
|------|--------|------|
| 禅修入门 | 禅、修、呼吸、静心、冥想 | 30秒 |
| 丹道养生 | 丹道、养生、气、自然、健康 | 30秒 |
| 书法静心 | 书法、写字、笔墨、静心、艺术 | 30秒 |
| 诗词创作 | 诗词、创作、古诗、文学、文化 | 30秒 |
| 易经风水 | 易经、风水、阴阳、八卦、命理 | 30秒 |

---

## 弹幕互动

发送弹幕关键词即可切换课程：

```
禅 → 禅修入门
丹 → 丹道养生
书 → 书法静心
诗 → 诗词创作
易 → 易经风水
```

---

## 硬件要求

| 配置 | 最低 | 推荐 |
|------|------|------|
| 显卡 | 4GB显存 | 6GB+ |
| CPU | i5-13400F | - |
| 内存 | 32GB | - |
| 硬盘 | 100GB | - |

---

## 效率提升

> 以前一天拍3条，现在一天批量产20-30条

**适用场景：**
- ✅ 电商带货
- ✅ 知识付费
- ✅ 培训课程
- ✅ 本地生活

---

## 局限性

- 情感表达缺少烟火气
- 复杂肢体动作（舞蹈、武术）不现实
- 主要靠素材视频驱动

---

## 文件结构

```
/mnt/d/Projects/.opencode/
├── daoyun-live.py          # 主程序
├── daoyun_teacher.mp4      # 道云老师开场视频
├── daoyun_voice.mp3        # 声音样本
├── logs/                   # 日志目录
│   ├── live.log           # 直播日志
│   └── cost.log           # 费用日志
└── cache/                  # 视频缓存
    ├── chanru_xxx.mp4
    ├── dandao_xxx.mp4
    └── ...
```

---

*基于 AUTOavantar 开源项目*
*道云老师 AI数字人直播系统*