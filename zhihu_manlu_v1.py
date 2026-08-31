"""Publish 3 Manlu healing articles to Zhihu - from manlu_zhihu_3.md"""
import time, sys, re, os, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

SRC = r"C:\Users\zhaox\AppData\Local\Temp\opencode\manlu_zhihu_3.md"


def parse_sections(md_path):
    """Split by '---' lines; each section: '# 漫庐疗愈 - 知乎回答N' + '**问题：...**' + body"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    sections = re.split(r"\n---+\n", text)
    out = []
    for sec in sections:
        lines = [l.rstrip() for l in sec.split("\n")]
        title = None
        body = []
        for s in lines:
            if s == "" or s == "---":
                continue
            m = re.match(r"^\*\*问题[：:]\s*(.+?)\s*\*\*$", s)
            if m:
                title = m.group(1).strip()
                continue
            if s.startswith("# "):
                continue
            body.append(re.sub(r"\*\*(.+?)\*\*", r"\1", s))
        if title and body:
            out.append({"title": title, "paras": body})
    return out


print("Parsing sections...")
articles = parse_sections(SRC)
print(f"Found {len(articles)} articles")
for a in articles:
    print(f"  - {a['title']} ({len(a['paras'])} paras)")

print("Starting...")
pw = sync_playwright().start()
browser = pw.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
ctx = browser.new_context(viewport={"width": 1280, "height": 900})
page = ctx.new_page()

cf = os.path.expanduser("~/.zhihu_cookies.json")
if os.path.exists(cf):
    with open(cf, "r") as f:
        ctx.add_cookies(json.load(f))
    print("Cookies loaded")

results = []
for idx, art in enumerate(articles):
    print(f"\n--- [{idx+1}/{len(articles)}] {art['title'][:20]}... ---")
    try:
        page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
        time.sleep(4)

        # Title
        ta = page.locator('textarea[placeholder*="标题"]').first
        ta.click()
        time.sleep(0.2)
        ta.fill(art["title"])
        time.sleep(0.3)
        print("  Title OK")

        # Content (plain paragraphs: type + Enter)
        ed = page.locator('.public-DraftEditor-content').first
        ed.click()
        time.sleep(0.3)
        for txt in art["paras"]:
            page.keyboard.type(txt, delay=2)
            page.keyboard.press("Enter")
            time.sleep(0.02)
        print(f"  Content OK: {len(art['paras'])} paras")

        time.sleep(1)
        # Find and click publish
        for b in page.locator('button').all():
            try:
                if b.inner_text().strip() == "发布":
                    b.click()
                    print("  Publish clicked")
                    break
            except Exception:
                pass

        time.sleep(4)
        url = page.url
        ok = "just_published" in url or "/p/" in url
        print(f"  URL: {url} -> {'OK' if ok else 'CHECK'}")
        results.append((art["title"], ok))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append((art["title"], False))

    if idx < len(articles) - 1:
        time.sleep(5)

print("\n=== RESULTS ===")
for t, o in results:
    print(f"  {'OK' if o else 'FAIL'}: {t}")
print(f"Total: {sum(1 for _, o in results if o)}/{len(articles)}")

browser.close()
pw.stop()
print("Done!")
