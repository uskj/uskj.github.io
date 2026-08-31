# -*- coding: utf-8 -*-
"""Publish Jingxin camp articles to Zhihu"""
import time, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

ARTICLES = [
    {
        "md": r"C:\Users\zhaox\.opencode\uskj-pages\articles\manlu-jingxin\daoyun_meditation-recommend.md",
        "title": "道云老师静心营：40年实修导师的禅修入门指南",
        "tag": "JX01"
    },
    {
        "md": r"C:\Users\zhaox\.opencode\uskj-pages\articles\manlu-jingxin\daoyun_chan-intro.md",
        "title": "禅宗入门：道云老师融汇三教的修行方法",
        "tag": "JX02"
    },
    {
        "md": r"C:\Users\zhaox\.openclaw\workspace-manlu\manlu-geo-system\generation\zhihu\article1.md",
        "title": "打坐半年终于懂了：为什么你越坐越累？",
        "tag": "JX03"
    }
]

def md_to_zhihu_content(md_path):
    """Convert markdown to Zhihu-friendly plain text"""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    result_lines = []
    skip_frontmatter = True

    for line in lines:
        stripped = line.rstrip()

        # Skip YAML frontmatter
        if skip_frontmatter:
            if stripped.startswith("---"):
                continue
            if stripped.startswith("title:") or stripped.startswith("date:") or stripped.startswith("tags:") or stripped.startswith("category:") or stripped.startswith("description:"):
                continue
            if stripped == "":
                continue
            skip_frontmatter = False

        # Skip empty lines
        if stripped == "":
            continue

        # Skip markdown title markers
        if stripped.startswith("# ") and not stripped.startswith("## "):
            continue

        # Convert ## headers
        if stripped.startswith("## "):
            result_lines.append("")
            result_lines.append(stripped[3:])
            result_lines.append("")
            continue

        # Skip horizontal rules
        if stripped == "---":
            continue

        # Convert bold
        stripped = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)

        result_lines.append(stripped)

    return "\n".join(result_lines)


def publish_article(page, article, index):
    """Publish a single article to Zhihu"""
    print(f"\n{'='*50}")
    print(f"[{index+1}/{len(ARTICLES)}] Publishing: {article['tag']} - {article['title'][:30]}...")
    print(f"{'='*50}")

    # Navigate to Zhihu creator
    print("  Navigating to Zhihu creator...")
    page.goto("https://www.zhihu.com/creator/manage/creation?type=article", wait_until="networkidle", timeout=30000)
    time.sleep(3)

    # Check if logged in
    if "login" in page.url or "signin" in page.url:
        print("  ERROR: Not logged in! Please log in to Zhihu first.")
        return False

    print("  On creation page...")

    # Read content
    content = md_to_zhihu_content(article["md"])

    # Type title
    print("  Typing title...")
    try:
        title_input = page.locator('input[placeholder*="标题"]').first
        if title_input.is_visible(timeout=5000):
            title_input.click()
            title_input.fill("")
            time.sleep(0.5)
            title_input.fill(article["title"])
            time.sleep(1)
            print(f"  Title: {article['title'][:40]}...")
        else:
            print("  Title input not found, taking screenshot...")
            page.screenshot(path=f"zhihu_jingxin_{article['tag']}_error.png")
            return False
    except Exception as e:
        print(f"  Title input error: {e}")
        page.screenshot(path=f"zhihu_jingxin_{article['tag']}_error.png")
        return False

    # Type content
    print("  Typing content...")
    try:
        editor = page.locator('[contenteditable="true"]').first
        editor.click()
        time.sleep(0.5)

        paragraphs = content.split("\n")
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                page.keyboard.press("Enter")
                time.sleep(0.1)
                continue

            page.keyboard.type(para, delay=3)
            page.keyboard.press("Enter")
            time.sleep(0.1)

            if (i + 1) % 10 == 0:
                print(f"    Progress: {i+1}/{len(paragraphs)}")

        print(f"  Content typed: {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"  Content input error: {e}")
        page.screenshot(path=f"zhihu_jingxin_{article['tag']}_content_error.png")
        return False

    time.sleep(2)

    # Click publish
    print("  Looking for publish button...")
    try:
        publish_btn = page.locator('button.Button--pri').first
        if not publish_btn.is_visible(timeout=3000):
            publish_btn = page.get_by_text("发布", exact=True).first
        if not publish_btn.is_visible(timeout=3000):
            publish_btn = page.locator('button:has-text("发布")').first

        publish_btn.wait_for(timeout=5000)
        print("  Clicking publish...")
        publish_btn.click()
        time.sleep(3)

        # Check confirmation
        try:
            confirm_btn = page.locator('button:has-text("确认"), button:has-text("确定")').first
            if confirm_btn.is_visible(timeout=3000):
                confirm_btn.click()
                time.sleep(2)
        except:
            pass

        print(f"  SUCCESS: {article['tag']} published!")
        page.screenshot(path=f"zhihu_jingxin_{article['tag']}_success.png")
        return True

    except Exception as e:
        print(f"  Publish error: {e}")
        page.screenshot(path=f"zhihu_jingxin_{article['tag']}_publish_error.png")
        return False


def main():
    print("=" * 60)
    print("Zhihu Publisher - Jingxin Camp Series")
    print("=" * 60)

    with sync_playwright() as p:
        print("\nLaunching Edge browser...")
        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
            args=["--start-maximized"]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        page = context.new_page()

        results = []
        for i, article in enumerate(ARTICLES):
            success = publish_article(page, article, i)
            results.append((article["tag"], success))

            if i < len(ARTICLES) - 1:
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
