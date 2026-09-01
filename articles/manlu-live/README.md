# 漫庐AI直播 - 使用指南

## 快速开始

### 方式一：本地运行（推荐）
```bash
# 1. 创建虚拟环境
cd /mnt/d/Projects/.opencode/uskj-pages/articles/manlu-live/
python3 -m http.server 8080

# 2. 浏览器访问
http://localhost:8080/index.html
```

### 方式二：GitHub Pages
```bash
# 已部署到: https://uskj.github.io/articles/manlu-live/
# 直接访问即可使用
```

---

## 功能说明

### 弹幕互动
1. 在左侧输入框输入弹幕
2. 点击"发送"或按Enter键
3. 系统识别关键词并切换对应场景

**支持关键词：**
| 关键词 | 触发场景 |
|--------|----------|
| 禅/坐/静/心 | 禅房静坐 |
| 书/墨/字/写 | 书房写字 |
| 雨 | 雨夜听声 |
| 竹 | 竹林听风 |
| 山 | 漫庐山居 |
| 茶 | 茶道静心 |

### 场景切换
- 点击右侧"手动切换场景"按钮
- 或在弹幕输入"关键词+任意内容"

### 自动播放
- 点击"自动播放"按钮
- 每10秒随机切换场景

### 截图功能
- 点击"截图"按钮
- 自动保存当前画面为PNG

---

## 技术架构

```
前端界面 (index.html)
    ↓
弹幕输入 → 关键词匹配 → 场景切换 → Canvas渲染
    ↓
系统日志 → 统计面板 → 成本计算
```

---

## 与后端对接

如需对接真实AI视频生成：

```javascript
// 修改 sendDanmu 函数
async function sendDanmu() {
    const text = document.getElementById('danmuInput').value;
    
    // 调用Seedance API
    const response = await fetch('https://api.seedance.tv/generate', {
        method: 'POST',
        headers: {'Authorization': 'Bearer YOUR_API_KEY'},
        body: JSON.stringify({
            prompt: getScenePrompt(text),
            duration: 5
        })
    });
    
    const videoUrl = await response.json().then(d => d.url);
    // 播放视频...
}
```

---

## 成本估算

| 项目 | 单价 | 日耗 | 月耗 |
|------|------|------|------|
| Seedance API | ¥0.02/5秒 | ¥5 | ¥150 |
| 服务器 | 免费 | - | 免费 |
| **总计** | - | **¥5** | **¥150** |

---

**船长AI视界出品**