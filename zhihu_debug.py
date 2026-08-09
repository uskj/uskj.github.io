"""Debug: check Zhihu creator page structure"""
import time, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()

    # Load cookies
    cookie_file = os.path.expanduser("~/.zhihu_cookies.json")
    if os.path.exists(cookie_file):
        import json
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        print(f"Loaded {len(cookies)} cookies")

    # Try the write page directly
    print("Going to zhihu.com/write ...")
    page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
    time.sleep(5)

    print(f"Current URL: {page.url}")
    page.screenshot(path="zhihu_page_debug.png", full_page=True)
    print("Screenshot saved: zhihu_page_debug.png")

    # Print page content summary
    title = page.title()
    print(f"Page title: {title}")

    # Find all input and editable elements
    inputs = page.locator('input').all()
    print(f"\nInputs found: {len(inputs)}")
    for i, inp in enumerate(inputs[:10]):
        try:
            placeholder = inp.get_attribute("placeholder") or ""
            input_type = inp.get_attribute("type") or ""
            print(f"  Input {i}: type={input_type}, placeholder={placeholder[:50]}")
        except:
            pass

    editables = page.locator('[contenteditable="true"]').all()
    print(f"\nContenteditable elements: {len(editables)}")
    for i, ed in enumerate(editables[:5]):
        try:
            tag = ed.evaluate("el => el.tagName")
            cls = ed.get_attribute("class") or ""
            print(f"  Editable {i}: tag={tag}, class={cls[:80]}")
        except:
            pass

    # Check for any buttons
    buttons = page.locator('button').all()
    print(f"\nButtons found: {len(buttons)}")
    for i, btn in enumerate(buttons[:15]):
        try:
            text = btn.inner_text()[:30]
            cls = btn.get_attribute("class") or ""
            print(f"  Button {i}: text='{text}', class={cls[:60]}")
        except:
            pass

    print("\nPress Enter to close browser...")
    input()
    browser.close()
