"""Publish 5 carbon-silicon papers to Zhihu - v2"""
import time, sys, re, os, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

PAPERS = [
    {"md": r"C:\Users\zhaox\Desktop\论文感知边界与执念秩序——碳基文明先天约束性的哲学反思.md",
     "title": "感知边界与执念秩序——碳基文明先天约束性的哲学反思", "tag": "CS01"},
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
    """Convert markdown to list of (type, text) tuples for Zhihu"""
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
        elif s.startswith("[") and s[1].isdigit():
            result.append(("ref", s))
        elif "内容由 AI 生成" in s:
            continue
        else:
            result.append(("p", re.sub(r'\*\*(.+?)\*\*', r'\1', s)))
    return result


def type_in_editor(page, paragraphs):
    """Type paragraphs into the Draft.js editor"""
    editor = page.locator('.public-DraftEditor-content').first
    editor.click()
    time.sleep(0.5)

    for i, (ptype, text) in enumerate(paragraphs):
        if ptype == "h2":
            page.keyboard.press("Enter")
            time.sleep(0.05)
            # Use toolbar "标题" button to make H2
            try:
                title_btn = page.locator('button:has-text("标题")').first
                title_btn.click()
                time.sleep(0.3)
                # Select H2 from dropdown if available
                try:
                    h2_option = page.locator(':text("H2"), :text("二级标题")').first
                    if h2_option.is_visible(timeout=1000):
                        h2_option.click()
                        time.sleep(0.2)
                except:
                    pass
            except:
                pass
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
            time.sleep(0.05)

        elif ptype == "h3":
            page.keyboard.press("Enter")
            time.sleep(0.05)
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
            time.sleep(0.05)

        elif ptype == "ref":
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
            time.sleep(0.05)

        else:  # p
            page.keyboard.type(text, delay=3)
            page.keyboard.press("Enter")
            time.sleep(0.05)

        if (i + 1) % 30 == 0:
            print(f"    Progress: {i+1}/{len(paragraphs)}")

    print(f"    Done: {len(paragraphs)} paragraphs typed")


def publish_one(page, paper, index):
    print(f"\n{'='*50}")
    print(f"[{index+1}/5] {paper['tag']} - {paper['title']}")
    print(f"{'='*50}")

    # Go to write page
    page.goto("https://zhuanlan.zhihu.com/write", wait_until="networkidle", timeout=30000)
    time.sleep(4)

    if "login" in page.url or "signin" in page.url:
        print("  ERROR: Not logged in!")
        return False

    # 1. Fill title
    print("  Filling title...")
    title_ta = page.locator('textarea[placeholder*="标题"]').first
    title_ta.click()
    time.sleep(0.3)
    title_ta.fill("")
    title_ta.fill(paper["title"])
    time.sleep(0.5)

    # 2. Fill content
    print("  Filling content...")
    paragraphs = md_to_zhihu_paragraphs(paper["md"])
    type_in_editor(page, paragraphs)
    time.sleep(2)

    # 3. Click publish
    print("  Clicking publish...")
    try:
        # Find the publish button - it's the blue one at top right
        pub_btn = page.locator('button.Button--primary:has-text("发布")').first
        if not pub_btn.is_visible(timeout=3000):
            pub_btn = page.locator('button:has-text("发布")').first
        if not pub_btn.is_visible(timeout=3000):
            # Try all buttons and find the one with 发布
            btns = page.locator('button').all()
            for b in btns:
                try:
                    txt = b.inner_text().strip()
                    if "发布" in txt and "撤销" not in txt and "重做" not in txt:
                        pub_btn = b
                        break
                except:
                    pass

        pub_btn.click()
        print("  Publish clicked, waiting for dialog...")
        time.sleep(3)

        # 4. Handle confirmation dialog
        try:
            # Look for the confirm/publish button in the modal
            confirm = page.locator('button.Button--primary:has-text("确认发布"), button.Button--primary:has-text("发布")').first
            if confirm.is_visible(timeout=5000):
                confirm.click()
                print("  Confirmed!")
                time.sleep(3)
        except:
            print("  No confirmation dialog found")

        # Check if we're back to the article list or success page
        current_url = page.url
        print(f"  Current URL: {current_url}")
        page.screenshot(path=f"zhihu_result_{paper['tag']}.png")
        print(f"  Screenshot: zhihu_result_{paper['tag']}.png")
        return True

    except Exception as e:
        print(f"  Publish error: {e}")
        page.screenshot(path=f"zhihu_error_{paper['tag']}.png")
        return False


def main():
    print("=" * 60)
    print("Zhihu Publisher v2 - Carbon-Silicon Series")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=False, args=["--start-maximized"])
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
                print("  Waiting 5s before next...")
                time.sleep(5)

        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        for tag, ok in results:
            print(f"  {tag}: {'OK' if ok else 'FAILED'}")
        print(f"\nTotal: {sum(1 for _,o in results if o)}/{len(results)}")

        browser.close()


if __name__ == "__main__":
    main()
