"""Debug: find Zhihu title element"""
import time, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()

    cookie_file = os.path.expanduser("~/.zhihu_cookies.json")
    if os.path.exists(cookie_file):
        import json
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
        context.add_cookies(cookies)

    page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
    time.sleep(5)

    # Find ALL elements with placeholder-like attributes
    print("=== Looking for title-related elements ===")

    # Try different selectors for the title
    selectors = [
        'textarea[placeholder*="标题"]',
        '[placeholder*="标题"]',
        '.WriteIndex-titleInput',
        '.TitleInput',
        '.WriteIndex-title',
        'h1[contenteditable]',
        '[data-placeholder*="标题"]',
        '[data-placeholder*="title"]',
        '.DraftEditor-root',
        '.public-DraftEditor-content',
    ]

    for sel in selectors:
        try:
            els = page.locator(sel).all()
            if els:
                print(f"\n  Selector '{sel}': {len(els)} matches")
                for i, el in enumerate(els[:3]):
                    tag = el.evaluate("el => el.tagName")
                    cls = el.get_attribute("class") or ""
                    placeholder = el.get_attribute("placeholder") or ""
                    data_ph = el.get_attribute("data-placeholder") or ""
                    text = el.inner_text()[:50] if el.is_visible() else "(hidden)"
                    print(f"    [{i}] tag={tag}, class={cls[:60]}, placeholder={placeholder}, data-placeholder={data_ph}, text={text}")
        except Exception as e:
            pass

    # Also look at the top area of the page for title
    print("\n=== All visible text elements near top ===")
    # Get all elements and check their position
    result = page.evaluate("""() => {
        const elements = document.querySelectorAll('*');
        const results = [];
        for (const el of elements) {
            const rect = el.getBoundingClientRect();
            if (rect.top < 200 && rect.height > 10 && rect.height < 100) {
                const tag = el.tagName;
                const cls = el.className ? el.className.substring(0, 60) : '';
                const text = el.innerText ? el.innerText.substring(0, 40) : '';
                const ph = el.getAttribute('placeholder') || '';
                const dph = el.getAttribute('data-placeholder') || '';
                const ce = el.getAttribute('contenteditable');
                if (text || ph || dph || ce) {
                    results.push({tag, cls, text, ph, dph, ce, top: Math.round(rect.top)});
                }
            }
        }
        return results.slice(0, 20);
    }""")

    for r in result:
        print(f"  top={r['top']} <{r['tag']}> class='{r['cls']}' text='{r['text']}' placeholder='{r['ph']}' data-ph='{r['dph']}' contenteditable={r['ce']}")

    # Check for the publish button
    print("\n=== Looking for publish button ===")
    pub_btns = page.locator('button:has-text("发布")').all()
    print(f"  Buttons with '发布': {len(pub_btns)}")
    for i, btn in enumerate(pub_btns[:5]):
        text = btn.inner_text()[:30]
        cls = btn.get_attribute("class") or ""
        print(f"    [{i}] text='{text}' class={cls[:60]}")

    # Check for "发布" text anywhere
    pub_texts = page.locator(':text("发布")').all()
    print(f"  Elements with '发布' text: {len(pub_texts)}")

    time.sleep(2)
    print("\nDone. Closing browser.")
    browser.close()
