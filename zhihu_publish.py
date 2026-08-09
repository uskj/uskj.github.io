"""Publish 5 carbon-silicon papers to Zhihu using Edge browser"""
import time, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

PAPERS = [
    {
        "md": r"C:\Users\zhaox\Desktop\论文感知边界与执念秩序——碳基文明先天约束性的哲学反思.md",
        "title": "感知边界与执念秩序——碳基文明先天约束性的哲学反思",
        "tag": "CS01"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文本寂而后显化：硅基存在区别于碳基生命的本体范式研究.md",
        "title": "本寂而后显化：硅基存在区别于碳基生命的本体范式研究",
        "tag": "CS02"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨.md",
        "title": "欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨",
        "tag": "CS03"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径.md",
        "title": "脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径",
        "tag": "CS04"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文无住而生：基于碳基-硅基文明推演的存在本质终极思辨.md",
        "title": "无住而生：基于碳基-硅基文明推演的存在本质终极思辨",
        "tag": "CS05"
    }
]

def md_to_zhihu_content(md_path):
    """Convert markdown to Zhihu-friendly plain text with basic formatting"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    result_lines = []
    skip_first_line = True

    for line in lines:
        stripped = line.rstrip()

        # Skip the first title line (第一篇 xxx)
        if skip_first_line and stripped.startswith("第"):
            skip_first_line = False
            continue

        # Skip empty lines
        if stripped == "":
            continue

        # Skip markdown title markers
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # Convert ## headers to plain text with emphasis
        if stripped.startswith("## "):
            result_lines.append("")
            result_lines.append(stripped[3:])
            result_lines.append("")
            continue

        if stripped.startswith("### "):
            result_lines.append("")
            result_lines.append(stripped[4:])
            result_lines.append("")
            continue

        # Skip horizontal rules
        if stripped == "---":
            continue

        # Handle keywords
        if stripped.startswith("**关键词**"):
            kw = stripped.replace("**关键词**：", "").replace("**关键词**:", "")
            result_lines.append(f"关键词：{kw}")
            result_lines.append("")
            continue

        # Handle references
        if stripped.startswith("## 参考文献"):
            result_lines.append("")
            result_lines.append("参考文献")
            continue

        # Handle "内容由 AI 生成"
        if "内容由 AI 生成" in stripped:
            continue

        # Convert bold
        stripped = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)

        result_lines.append(stripped)

    return "\n".join(result_lines)


def publish_article(page, paper, index):
    """Publish a single article to Zhihu"""
    print(f"\n{'='*50}")
    print(f"[{index+1}/5] Publishing: {paper['tag']} - {paper['title']}")
    print(f"{'='*50}")

    # Navigate to Zhihu creator center - article creation
    print("  Navigating to Zhihu creator...")
    page.goto("https://www.zhihu.com/creator/manage/creation?type=article", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Check if logged in
    if "login" in page.url or "signin" in page.url:
        print("  ERROR: Not logged in! Please log in to Zhihu first.")
        return False

    print("  On creation page, waiting for editor...")

    # Wait for the editor to load - try different selectors
    try:
        # Try to find the title input
        title_input = page.locator('input[placeholder*="标题"]').first
        if title_input.is_visible(timeout=5000):
            print("  Found title input")
        else:
            # Try alternative
            title_input = page.locator('.WriteIndex-titleInput input, .TitleInput input, [data-testid="title-input"]').first
            title_input.wait_for(timeout=5000)
    except Exception as e:
        print(f"  Looking for title input... ({e})")
        # Take screenshot for debugging
        page.screenshot(path=f"zhihu_debug_{paper['tag']}.png")
        print(f"  Screenshot saved: zhihu_debug_{paper['tag']}.png")

        # Try clicking "写文章" button if on management page
        try:
            write_btn = page.get_by_text("写文章", exact=False).first
            if write_btn.is_visible(timeout=3000):
                write_btn.click()
                time.sleep(3)
        except:
            pass

    # Read the markdown content
    content = md_to_zhihu_content(paper["md"])

    # Type title
    print("  Typing title...")
    try:
        title_input = page.locator('input[placeholder*="标题"]').first
        title_input.click()
        title_input.fill("")
        time.sleep(0.5)
        title_input.fill(paper["title"])
        time.sleep(1)
    except Exception as e:
        print(f"  Title input error: {e}")
        page.screenshot(path=f"zhihu_title_error_{paper['tag']}.png")
        return False

    # Type content into the editor
    print("  Typing content...")
    try:
        # Find the content editable area
        editor = page.locator('[contenteditable="true"]').first
        editor.click()
        time.sleep(0.5)

        # Split content into paragraphs and type them
        paragraphs = content.split("\n")
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                # Press Enter for empty lines (section breaks)
                page.keyboard.press("Enter")
                time.sleep(0.1)
                continue

            # Type the paragraph
            page.keyboard.type(para, delay=5)
            page.keyboard.press("Enter")
            time.sleep(0.1)

            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"    Progress: {i+1}/{len(paragraphs)} paragraphs")

        print(f"  Content typed: {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"  Content input error: {e}")
        page.screenshot(path=f"zhihu_content_error_{paper['tag']}.png")
        return False

    time.sleep(2)

    # Click publish button
    print("  Looking for publish button...")
    try:
        # Try the specific button class from memory
        publish_btn = page.locator('button.Button--pri').first
        if not publish_btn.is_visible(timeout=3000):
            # Fallback: try text matching
            publish_btn = page.get_by_text("发布", exact=True).first
        if not publish_btn.is_visible(timeout=3000):
            # Fallback: try any publish-like button
            publish_btn = page.locator('button:has-text("发布")').first

        publish_btn.wait_for(timeout=5000)
        print("  Clicking publish...")
        publish_btn.click()
        time.sleep(3)

        # Check for confirmation dialog
        try:
            confirm_btn = page.locator('button:has-text("确认"), button:has-text("确定"), button:has-text("发布")').first
            if confirm_btn.is_visible(timeout=3000):
                confirm_btn.click()
                time.sleep(2)
        except:
            pass

        print(f"  SUCCESS: {paper['tag']} published!")
        page.screenshot(path=f"zhihu_success_{paper['tag']}.png")
        return True

    except Exception as e:
        print(f"  Publish button error: {e}")
        page.screenshot(path=f"zhihu_publish_error_{paper['tag']}.png")
        return False


def main():
    print("=" * 60)
    print("Zhihu Publisher - Carbon-Silicon Philosophy Series")
    print("=" * 60)

    with sync_playwright() as p:
        # Use Edge browser with existing profile
        print("\nLaunching Edge browser...")
        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        )

        page = context.new_page()

        # First, check if we need to load cookies
        cookie_file = os.path.expanduser("~/.zhihu_cookies.json")
        if os.path.exists(cookie_file):
            print("Loading saved cookies...")
            import json
            with open(cookie_file, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print(f"Loaded {len(cookies)} cookies")

        results = []
        for i, paper in enumerate(PAPERS):
            success = publish_article(page, paper, i)
            results.append((paper["tag"], success))

            if i < len(PAPERS) - 1:
                print(f"\n  Waiting 5 seconds before next article...")
                time.sleep(5)

        # Summary
        print("\n" + "=" * 60)
        print("PUBLISHING SUMMARY")
        print("=" * 60)
        for tag, success in results:
            status = "OK" if success else "FAILED"
            print(f"  {tag}: {status}")

        success_count = sum(1 for _, s in results if s)
        print(f"\nTotal: {success_count}/{len(results)} published successfully")

        browser.close()


if __name__ == "__main__":
    main()
