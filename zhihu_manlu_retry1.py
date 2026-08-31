"""Retry publishing ONLY article 1 (北京周边有什么值得去的静心度假地？) to Zhihu.
Articles 2 & 3 already published by zhihu_manlu_v1.py - do NOT rerun those."""
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
art = articles[0]  # ONLY first article
print(f"Target: {art['title']} ({len(art['paras'])} paras)")

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

ok = False
try:
    # domcontentloaded instead of networkidle - Zhihu write page has long-lived connections
    page.goto("https://zhuanlan.zhihu.com/write", wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)
    print(f"Page title: {page.title()}")
    print(f"URL: {page.url}")

    # Title - explicit wait up to 45s
    ta = page.locator('textarea[placeholder*="标题"]').first
    ta.wait_for(state="visible", timeout=45000)
    ta.click()
    time.sleep(0.2)
    ta.fill(art["title"])
    time.sleep(0.3)
    print("  Title OK")

    # Content (plain paragraphs: type + Enter)
    ed = page.locator('.public-DraftEditor-content').first
    ed.wait_for(state="visible", timeout=30000)
    ed.click()
    time.sleep(0.3)
    for txt in art["paras"]:
        page.keyboard.type(txt, delay=2)
        page.keyboard.press("Enter")
        time.sleep(0.02)
    print(f"  Content OK: {len(art['paras'])} paras")

    time.sleep(1)
    # Find and click publish
    clicked = False
    for b in page.locator('button').all():
        try:
            if b.inner_text().strip() == "发布":
                b.click()
                print("  Publish clicked")
                clicked = True
                break
        except Exception:
            pass
    if not clicked:
        print("  WARN: publish button not found")

    time.sleep(5)
    url = page.url
    ok = "just_published" in url or "/p/" in url
    print(f"  URL: {url} -> {'OK' if ok else 'CHECK'}")
except Exception as e:
    print(f"  ERROR: {e}")
    try:
        print(f"  final URL: {page.url}")
    except Exception:
        pass

print(f"\n=== RESULT: {'OK' if ok else 'FAIL'} - {art['title']} ===")
browser.close()
pw.stop()
print("Done!")
