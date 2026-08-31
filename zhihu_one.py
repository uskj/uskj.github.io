"""Publish ONE article to Zhihu - step by step with pauses"""
import time, sys, re, os, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

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

paper = {
    "md": r"C:\Users\zhaox\Desktop\论文感知边界与执念秩序——碳基文明先天约束性的哲学反思.md",
    "title": "感知边界与执念秩序——碳基文明先天约束性的哲学反思",
    "tag": "CS01"
}

print("Launching Edge...")
pw = sync_playwright().start()
browser = pw.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
context = browser.new_context(viewport={"width": 1280, "height": 900})
page = context.new_page()

# Load cookies
cookie_file = os.path.expanduser("~/.zhihu_cookies.json")
if os.path.exists(cookie_file):
    with open(cookie_file, "r") as f:
        cookies = json.load(f)
    context.add_cookies(cookies)
    print(f"Loaded {len(cookies)} cookies")

# Step 1: Go to write page
print("\n[Step 1] Opening Zhihu write page...")
page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
time.sleep(4)
print(f"  URL: {page.url}")
print(f"  Title: {page.title()}")

# Step 2: Fill title
print("\n[Step 2] Filling title...")
title_ta = page.locator('textarea[placeholder*="标题"]').first
title_ta.click()
time.sleep(0.3)
title_ta.fill(paper["title"])
time.sleep(0.5)
print(f"  Title filled: {paper['title']}")

# Step 3: Fill content
print("\n[Step 3] Filling content...")
paragraphs = md_to_zhihu_paragraphs(paper["md"])
print(f"  {len(paragraphs)} paragraphs to type")

editor = page.locator('.public-DraftEditor-content').first
editor.click()
time.sleep(0.5)

for i, (ptype, text) in enumerate(paragraphs):
    if ptype == "h2":
        page.keyboard.press("Enter")
        page.keyboard.type(text, delay=3)
        page.keyboard.press("Enter")
    elif ptype == "h3":
        page.keyboard.press("Enter")
        page.keyboard.type(text, delay=3)
        page.keyboard.press("Enter")
    else:
        page.keyboard.type(text, delay=3)
        page.keyboard.press("Enter")
    time.sleep(0.03)
    if (i + 1) % 20 == 0:
        print(f"  Progress: {i+1}/{len(paragraphs)}")

print(f"  Content done!")

# Step 4: Click publish
print("\n[Step 4] Looking for publish button...")
time.sleep(1)

# Find all buttons and their text
btns = page.locator('button').all()
pub_btn = None
for b in btns:
    try:
        txt = b.inner_text().strip()
        if txt == "发布":
            pub_btn = b
            break
    except:
        pass

if pub_btn:
    print("  Found publish button, clicking...")
    pub_btn.click()
    time.sleep(3)
    print("  Clicked! Waiting for dialog...")
else:
    print("  ERROR: Publish button not found!")
    page.screenshot(path="zhihu_nobutton.png")
    print("  Take a screenshot. Browser stays open.")
    input("  Press Enter to close...")

# Step 5: Handle confirmation
print("\n[Step 5] Looking for confirmation...")
time.sleep(2)
# Try to find confirm button in any dialog/modal
confirm_selectors = [
    'button:has-text("确认发布")',
    'button:has-text("确认")',
    'button.Button--primary:has-text("发布")',
    '.Modal button.Button--primary',
]
for sel in confirm_selectors:
    try:
        btn = page.locator(sel).first
        if btn.is_visible(timeout=2000):
            print(f"  Found confirm: {sel}")
            btn.click()
            time.sleep(3)
            break
    except:
        pass

print(f"\n  Final URL: {page.url}")
page.screenshot(path="zhihu_final.png")
print("  Screenshot saved: zhihu_final.png")

print("\nDone! Browser stays open. Press Enter to close.")
input()
browser.stop()
