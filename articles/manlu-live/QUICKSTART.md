# 漫庐AI直播 - 快速启动指南

## 状态检查

✅ 系统已测试通过
✅ 弹幕触发正常
✅ 代码已部署到GitHub

---

## 启动方式

### 方式1：本地运行（推荐新手）

```bash
# 1. 进入项目目录
cd /mnt/d/Projects/.opencode

# 2. 激活虚拟环境
source /tmp/crawl4ai-env/bin/activate

# 3. 启动直播（测试模式）
python manlu-live-kling.py test
```

### 方式2：Web界面（浏览器访问）

```bash
# 1. 启动Web服务
cd /mnt/d/Projects/.opencode
python -m http.server 8080

# 2. 浏览器访问
http://localhost:8080/articles/manlu-live/free.html
```

### 方式3：正式直播（7x24小时）

```bash
# 需要配置Kling API Key
export KLING_API_KEY="your_api_key_here"

# 启动直播
python manlu-live-kling.py stream
```

---

## 关于"生成中"问题

**原因：** Kling AI API 需要时间生成视频（约10-30秒）

**解决方案：**

1. **检查API Key是否正确**
   ```bash
   echo $KLING_API_KEY
   ```

2. **查看日志**
   ```bash
   tail -f logs/stream.log
   ```

3. **如果一直卡住，可能是：**
   - 网络问题 → 检查网络连接
   - API额度用尽 → 次日重置
   - 模型维护中 → 等待恢复

---

## 免费替代方案

如果Kling AI不可用，使用**纯网页版**（无需API）：

```
https://uskj.github.io/articles/manlu-live/free.html
```

这个版本用Canvas绘制动态场景，完全免费，无需API。

---

## 直播配置建议

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| 预生成数量 | 20个 | 减少等待时间 |
| 自动切换 | 8秒 | 每个场景播放时长 |
| 弹幕冷却 | 5秒 | 防止刷屏 |
| 分辨率 | 720p | 平衡质量和速度 |

---

## 下一步

1. **先测试Web版** → 确认弹幕功能正常
2. **再配置Kling** → 获取API Key
3. **最后正式开播** → 连接OBS或其他推流工具

---

**需要帮助？**
- 查看日志: `tail -f logs/stream.log`
- 重启服务: `bash start-manlu-live.sh`