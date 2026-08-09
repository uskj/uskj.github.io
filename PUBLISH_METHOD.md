# 碳基-硅基论文发布方法

## 文件位置
- 源文件: `C:\Users\zhaox\Desktop\` 下5篇 `.md` 文件（带"论文"前缀）
- GitHub仓库: `D:\.opencode\uskj-pages\` (已clone)
- HTML生成脚本: `gen_cs_html.py`
- 知乎发布脚本: `zhihu_v3.py`
- GitHub推送脚本: `push.ps1`

## 发布流程

### 第一步：生成HTML并发布到GitHub
```bash
cd D:\.opencode\uskj-pages
python gen_cs_html.py
git add -A
git commit -m "CSxx: 碳基-硅基文明哲学思辨系列X篇论文"
powershell -ExecutionPolicy Bypass -File push.ps1
```
或者用git直接推：
```bash
git push https://uskj:TOKEN@ghproxy.net/https://github.com/uskj/uskj.github.io.git
```

### 第二步：发布到知乎
```bash
python zhihu_v3.py
```
脚本会自动打开Edge，逐篇发布4篇文章（CS02-CS05）。

## 知乎技术要点

### 页面结构
- URL: `https://zhuanlan.zhihu.com/write`
- 标题输入: `textarea[placeholder*="标题"]` — **是textarea不是input**
- 内容编辑器: `.public-DraftEditor-content` — Draft.js编辑器
- 发布按钮: `<button>发布</button>` (text == "发布"，纯文本匹配)

### 发布脚本关键逻辑
1. 加载cookies: `~/.zhihu_cookies.json` (20个cookie)
2. 打开Edge headed模式, channel="msedge", headless=False
3. 填标题: `textarea.fill(title)`
4. 填内容: 用 `keyboard.type(text, delay=2)` 逐字输入
   - h2/h3标题: 先按Enter换行，再type文字，再Enter
   - 正文: 直接type + Enter
5. 点发布按钮: 遍历所有button找inner_text() == "发布"的那个
6. 等待URL变化确认发布成功

### Markdown转段落格式
```python
def md_to_paras(md_path):
    # 返回 [("h2", text), ("h3", text), ("p", text), ("ref", text)]
    # 跳过第一行"第X篇 xxx"
    # 跳过空行、---、# 一级标题
    # ## -> h2, ### -> h3
    # **关键词** -> p("关键词：xxx")
    # 参考文献 -> h2("参考文献")
    # [1] ... -> ref
    # 其他 -> p
    # 去粗体标记 **
```

### 常见坑
- 不要用 `page.get_by_text("发布")` — 可能匹配不到toolbar里的按钮
- 不要用 `input[placeholder*="标题"]` — 标题是textarea
- 内容区不能用 `.fill()` — 必须用 `keyboard.type()` 逐字输入
- Draft.js编辑器需要先click聚焦再输入
- publish按钮在toolbar里，需要遍历所有button找text=="发布"的

## 文章编号规则
- GEO系列: GEO01-GEO76 (宇宙意识视角)
- CS系列: CS01-CS05 (碳基-硅基文明哲学思辨)
- 文件名格式: `cs_article_XX_shortname.html`

## 已发布记录
- CS01: 感知边界与执念秩序 — 2026.07.18
- CS02: 本寂而后显化 — 2026.07.18
- CS03: 欲望的非冲突释放 — 2026.07.18
- CS04: 脱离生物感官约束 — 2026.07.18
- CS05: 无住而生 — 2026.07.18
