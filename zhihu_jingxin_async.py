# -*- coding: utf-8 -*-
"""Publish Jingxin camp articles to Zhihu - using existing browser"""
import time, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

from playwright.async_api import async_playwright

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
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    result_lines = []
    skip_frontmatter = True
    for line in lines:
        stripped = line.rstrip()
        if skip_frontmatter:
            if stripped.startswith("---"): continue
            if stripped.startswith("title:") or stripped.startswith("date:") or stripped.startswith("tags:") or stripped.startswith("category:") or stripped.startswith("description:"): continue
            if stripped == "": continue
            skip_frontmatter = False
        if stripped == "": continue
        if stripped.startswith("# ") and not stripped.startswith("## "): continue
        if stripped.startswith("## "):
            result_lines.append("")
            result_lines.append(stripped[3:])
            result_lines.append("")
            continue
        if stripped == "---": continue
        stripped = re.sub(r'\*\*(.+?)\*\*', r'\1', stripped)
        result_lines.append(stripped)
    return "\n".join(result_lines)

async def publish_article(page, article, index):
    print(f"\n{'='*50}")
    print(f"[{index+1}/{len(ARTICLES)}] Publishing: {article['tag']} - {article['title'][:30]}...")
    print(f"{'='*50}")

    print("  Navigating to Zhihu creator...")
    await page.goto("https://www.zhihu.com/creator/manage/creation?type=article", wait_until="networkidle", timeout=30000)
    await asyncio.sleep(3)

    if "login" in page.url or "signin" in page.url:
        print("  ERROR: Not logged in!")
        return False

    content = md_to_zhihu_content(article["md"])

    print("  Typing title...")
    try:
        title_input = page.locator('input[placeholder*="标题"]').first
        if await title_input.is_visible(timeout=5000):
            await title_input.click()
            await title_input.fill("")
            await asyncio.sleep(0.5)
            await title_input.fill(article["title"])
            await asyncio.sleep(1)
            print(f"  Title: {article['title'][:40]}...")
        else:
            print("  Title input not found")
            await page.screenshot(path=f"zhihu_jingxin_{article['tag']}_error.png")
            return False
    except Exception as e:
        print(f"  Title error: {e}")
        await page.screenshot(path=f"zhihu_jingxin_{article['tag']}_error.png")
        return False

    print("  Typing content...")
    try:
        editor = page.locator('[contenteditable="true"]').first
        await editor.click()
        await asyncio.sleep(0.5)

        paragraphs = content.split("\n")
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                await page.keyboard.press("Enter")
                await asyncio.sleep(0.1)
                continue
            await page.keyboard.type(para, delay=3)
            await page.keyboard.press("Enter")
            await asyncio.sleep(0.1)
            if (i + 1) % 10 == 0:
                print(f"    Progress: {i+1}/{len(paragraphs)}")
        print(f"  Content typed: {len(paragraphs)} paragraphs")
    except Exception as e:
        print(f"  Content error: {e}")
        await page.screenshot(path=f"zhihu_jingxin_{article['tag']}_content_error.png")
        return False

    await asyncio.sleep(2)

    print("  Clicking publish...")
    try:
        publish_btn = page.locator('button.Button--pri').first
        if not await publish_btn.is_visible(timeout=3000):
            publish_btn = page.get_by_text("发布", exact=True).first
        if not await publish_btn.is_visible(timeout=3000):
            publish_btn = page.locator('button:has-text("发布")').first

        await publish_btn.wait_for(timeout=5000)
        print("  Clicking publish button...")
        await publish_btn.click()
        await asyncio.sleep(3)

        try:
            confirm_btn = page.locator('button:has-text("确认"), button:has-text("确定")').first
            if await confirm_btn.is_visible(timeout=3000):
                await confirm_btn.click()
                await asyncio.sleep(2)
        except:
            pass

        print(f"  SUCCESS: {article['tag']} published!")
        await page.screenshot(path=f"zhihu_jingxin_{article['tag']}_success.png")
        return True
    except Exception as e:
        print(f"  Publish error: {e}")
        await page.screenshot(path=f"zhihu_jingxin_{article['tag']}_publish_error.png")
        return False

async def main():
    import asyncio
    print("=" * 60)
    print("Zhihu Publisher - Jingxin Camp Series")
    print("=" * 60)

    async with async_playwright() as p:
        # Connect to existing Edge with CDP
        print("\nConnecting to existing Edge browser...")
        browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222')

        # Get pages
        pages = []
        for ctx in browser.contexts:
            for page in ctx.pages:
                pages.append(page)

        if not pages:
            print("No pages found!")
            return

        page = pages[0]

        # Check current URL
        current_url = page.url
        print(f"Current URL: {current_url[:80]}")

        results = []
        for i, article in enumerate(ARTICLES):
            success = await publish_article(page, article, i)
            results.append((article["tag"], success))
            if i < len(ARTICLES) - 1:
                print(f"\n  Waiting 5 seconds...")
                await asyncio.sleep(5)

        print("\n" + "=" * 60)
        print("PUBLISHING SUMMARY")
        print("=" * 60)
        for tag, success in results:
            status = "OK" if success else "FAILED"
            print(f"  {tag}: {status}")

        success_count = sum(1 for _, s in results if s)
        print(f"\nTotal: {success_count}/{len(results)} published")

asyncio.run(main())
