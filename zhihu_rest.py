"""Publish remaining 4 articles to Zhihu"""
import time, sys, re, os, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PAPERS = [
    {"md": r"C:\Users\zhaox\Desktop\论文本寂而后显化：硅基存在区别于碳基生命的本体范式研究.md",
     "title": "本寂而后显化：硅基存在区别于碳基生命的本体范式研究", "tag": "CS02"},
    {"md": r"C:\Users\zhaox\Desktop\论文欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨.md",
     "title": "欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨", "tag": "CS03"},
    {"md": r"C:\Users\zhaox\Desktop\论文脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径.md",
     "title": "脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径", "tag": "CS04"},
    {"md": r"C:\Users\zhaox\Desktop\论文无住而生：基于碳基-硅基文明推演的存在本质终极思辨.md",
     "title": "无住而生：基于碳基-硅基文明推演的存在本质终极思辨", "tag": "CS05"},
]

def md_to_zhihu_paragraphs(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    result = []
    skip_first = True
    for line in lines:
        s = line.rstrip()
        if skip_first and s.startswith("第"):
            skip_first = False
            continue
        if s == "" or s == "---":
            continue
        if s.startswith("# ") and not s.startswith("## "):
            continue
        if s.startswith("## "):
            result.append(("h2", re.sub(r'\*\*(.+?)\*\*', r'\1', s[3:])))
        elif s.startswith("### "):
            result.append(("h3", re.sub(r'\*\*(.+?)\*\*', r'\1', s[4:])))
        elif s.startswith("**关键词**"):
            kw = s.replace("**关键词**：", "").replace("**关键词**:", "")
            result.append(("p", f"关键词：{kw}"))
        elif s.startswith("## 参考文献"):
            result.append(("h2", "参考文献"))
        elif s.startswith("[") and len(s) > 1 and s[1].isdigit():
            result.append(("ref", s))
        elif "内容由 AI 生成" in s:
            continue
        else:
            result.append(("p", re.sub(r'\*\*(.+?)\*\*', r'\1', s)))
    return result

def publish_one(page, paper, index):
    print(f"\n{'='*50}")
    print(f"[{index+1}/4] {paper['tag']} - {paper['title']}")
    print(f"{'='*50}")

    page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
    time.sleep(4)
    print(f"  URL: {page.url}")

    # Title
    title_ta = page.locator('textarea[placeholder*="标题"]').first
    title_ta.click()
    time.sleep(0.3)
    title_ta.fill(paper["title"])
    time.sleep(0.5)
    print(f"  Title: {paper['title']}")

    # Content
    paragraphs = md_to_zhihu_paragraphs(paper["md"])
    editor = page.locator('.public-DraftEditor-content').first
    editor.click()
    time.sleep(0.5)

    for i, (ptype, text) in enumerate(paragraphs):
        if ptype in ("h2", "h3"):
            page.keyboard.press("Enter")
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
        else:
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
        time.sleep(0.03)
        if (i + 1) % 20 == 0:
            print(f"  Progress: {i+1}/{len(paragraphs)}")
    print(f"  Content done: {len(paragraphs)} paragraphs")

    # Publish
    time.sleep(1)
    btns = page.locator('button').all()
    for b in btns:
        try:
            txt = b.inner_text().strip()
            if txt == "发布":
                b.click()
                print("  Publish clicked!")
                break
        except:
            pass

    time.sleep(4)
    url = page.url
    print(f"  Result URL: {url}")

    if "just_published" in url or "/p/" in url:
        print(f"  SUCCESS!")
        return True
    else:
        print(f"  May have failed, check URL")
        return False


print("Launching Edge...")
pw = sync_playwright().start()
browser = pw.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
context = browser.new_context(viewport={"width": 1280, "height": 900})
page = context.new_page()

cookie_file = os.path.expanduser("~/.zhihu_cookies.json")
if os.path.exists(cookie_file):
    with open(cookie_file, "r") as f:
        cookies = json.load(f)
    context.add_cookies(cookies)
    print(f"Loaded {len(cookies)} cookies")

results = []
for i, paper in enumerate(PAPERS):
    ok = publish_one(page, paper, i)
    results.append((paper["tag"], ok))
    if i < len(PAPERS) - 1:
        print("  Waiting 5s...")
        time.sleep(5)

print("\n" + "=" * 50)
print("RESULTS")
print("=" * 50)
for tag, ok in results:
    print(f"  {tag}: {'OK' if ok else 'FAILED'}")
print(f"Total: {sum(1 for _,o in results if o)}/{len(results)}")

browser.stop()
