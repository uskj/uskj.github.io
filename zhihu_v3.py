"""Publish 4 remaining articles - non-interactive, auto-close"""
import time, sys, re, os, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PAPERS = [
    {"md": r"D:\Projects\papers\论文本寂而后显化：硅基存在区别于碳基生命的本体范式研究.md",
       "title": "本寂而后显化：硅基存在区别于碳基生命的本体范式研究", "tag": "CS02"},
    {"md": r"D:\Projects\papers\论文欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨.md",
       "title": "欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨", "tag": "CS03"},
    {"md": r"D:\Projects\papers\论文脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径.md",
       "title": "脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径", "tag": "CS04"},
    {"md": r"D:\Projects\papers\论文无住而生：基于碳基-硅基文明推演的存在本质终极思辨.md",
       "title": "无住而生：基于碳基‑硅基文明推演的存在本质终极思辨", "tag": "CS05"},
]

def md_to_paras(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    result = []
    skip = True
    for line in text.split("\n"):
        s = line.rstrip()
        if skip and s.startswith("论文"):
            skip = False
            continue
        if s == "" or s == "---" or s.startswith("# ") and not s.startswith("## "):
            continue
        if s.startswith("## "):
            result.append(("h2", re.sub(r'\*\*(.+?)\*\*', r'\1', s[3:])))
        elif s.startswith("### "):
            result.append(("h3", re.sub(r'\*\*(.+?)\*\*', r'\1', s[4:])))
        elif s.startswith("**閸忔娊鏁拠?*"):
            result.append(("p", "閸忔娊鏁拠宥忕窗" + s.split("閿?,1)[-1].split(":",1)[-1]))
        elif s.startswith("## 閸欏倽鈧啯鏋冮悮?):
            result.append(("h2", "閸欏倽鈧啯鏋冮悮?))
        elif s.startswith("[") and len(s)>1 and s[1].isdigit():
            result.append(("ref", s))
        elif "AI 閻㈢喐鍨? in s:
            continue
        else:
            result.append(("p", re.sub(r'\*\*(.+?)\*\*', r'\1', s)))
    return result

print("Starting...")
pw = sync_playwright().start()
browser = pw.chromium.launch(channel="chrome", headless=False, args=['--disable-blink-features=AutomationControlled', '--start-maximized'], extra_http_headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "zh-CN,zh;q=0.9", "Referer": "https://www.zhihu.com/"})
ctx = browser.new_context(viewport={"width":1280,"height":900})
page = ctx.new_page()

cf = os.path.expanduser("~/.zhihu_cookies.json")
if os.path.exists(cf):
    with open(cf,"r") as f: ctx.add_cookies(json.load(f))
    print("Cookies loaded")

results = []
for idx, paper in enumerate(PAPERS):
    print(f"\n--- [{idx+1}/4] {paper['tag']} ---")
    try:
        page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
        time.sleep(4)

        # Title
        ta = page.locator('textarea[placeholder*="閺嶅洭顣?]').first
        ta.click()
        time.sleep(0.2)
        ta.fill(paper["title"])
        time.sleep(0.3)
        print(f"  Title OK")

        # Content
        paras = md_to_paras(paper["md"])
        ed = page.locator('.public-DraftEditor-content').first
        ed.click()
        time.sleep(0.3)
        for i,(pt,txt) in enumerate(paras):
            if pt in ("h2","h3"):
                page.keyboard.press("Enter")
                page.keyboard.type(txt, delay=2)
                page.keyboard.press("Enter")
            else:
                page.keyboard.type(txt, delay=2)
                page.keyboard.press("Enter")
            time.sleep(0.02)
        print(f"  Content OK: {len(paras)} paras")

        time.sleep(1)
        # Find and click publish
        for b in page.locator('button').all():
            try:
                if b.inner_text().strip() == "閸欐垵绔?:
                    b.click()
                    print("  Publish clicked")
                    break
            except: pass

        time.sleep(4)
        url = page.url
        ok = "just_published" in url or "/p/" in url
        print(f"  URL: {url} -> {'OK' if ok else 'CHECK'}")
        results.append((paper["tag"], ok))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append((paper["tag"], False))

    if idx < len(PAPERS)-1:
        time.sleep(5)

print("\n=== RESULTS ===")
for t,o in results:
    print(f"  {t}: {'OK' if o else 'FAIL'}")
print(f"Total: {sum(1 for _,o in results if o)}/4")

browser.close()
pw.stop()
print("Done!")
