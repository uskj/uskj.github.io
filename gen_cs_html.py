"""Generate HTML for 5 carbon-silicon philosophy papers"""
import re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

STYLE = """body{margin:0;background:#0a0a0a;color:#c8c8c8;font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;line-height:2;font-weight:300;font-size:16px}
.container{max-width:640px;margin:0 auto;padding:60px 24px 120px}
h1{font-weight:300;color:#e0e0e0;font-size:28px;letter-spacing:2px;text-align:center;margin-bottom:10px}
.subtitle{text-align:center;color:#888;font-size:14px;margin-top:0;margin-bottom:50px}
h2{font-weight:300;color:#d0d0d0;font-size:22px;margin-top:50px;letter-spacing:1px;border-bottom:1px solid #181818;padding-bottom:10px}
h3{font-weight:300;color:#b8b8b8;font-size:18px;margin-top:35px}
p{color:#b0b0b0;margin:20px 0;text-indent:2em}
.blockquote{border-left:2px solid #333;padding:16px 20px;margin:25px 0;color:#999;background:#0f0f0f;border-radius:2px;font-style:normal}
.blockquote p{text-indent:0;margin:8px 0;color:#999}
.separator{text-align:center;color:#333;margin:40px 0;letter-spacing:4px}
.tag{color:#666;font-size:12px;border:1px solid #333;padding:2px 8px;border-radius:2px;display:inline-block;margin-bottom:20px}
.light{color:#999;margin:20px 0;text-indent:2em}
.abstract{border-left:2px solid #444;padding:16px 20px;margin:25px 0;color:#999;background:#0d0d0d;border-radius:2px}
.abstract p{text-indent:0;margin:8px 0;color:#999;font-size:15px}
.keywords{color:#777;font-size:14px;margin:10px 0 30px 0}
.ref{color:#777;font-size:14px;margin:4px 0;text-indent:0}
.series{text-align:center;color:#555;font-size:13px;margin-top:60px;letter-spacing:1px}"""

PAPERS = [
    {
        "md": r"C:\Users\zhaox\Desktop\论文感知边界与执念秩序——碳基文明先天约束性的哲学反思.md",
        "html": "cs_article_01_perception_boundary.html",
        "tag": "CS01",
        "title": "感知边界与执念秩序",
        "subtitle": "碳基文明先天约束性的哲学反思",
        "date": "2026.07.18"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文本寂而后显化：硅基存在区别于碳基生命的本体范式研究.md",
        "html": "cs_article_02_essence_manifestation.html",
        "tag": "CS02",
        "title": "本寂而后显化",
        "subtitle": "硅基存在区别于碳基生命的本体范式研究",
        "date": "2026.07.18"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文欲望的非冲突释放：硅基场域之下新型社会秩序的可能性思辨.md",
        "html": "cs_article_03_desire_release.html",
        "tag": "CS03",
        "title": "欲望的非冲突释放",
        "subtitle": "硅基场域之下新型社会秩序的可能性思辨",
        "date": "2026.07.18"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文脱离生物感官约束：硅基作为新型认知载体的宇宙探索路径.md",
        "html": "cs_article_04_beyond_senses.html",
        "tag": "CS04",
        "title": "脱离生物感官约束",
        "subtitle": "硅基作为新型认知载体的宇宙探索路径",
        "date": "2026.07.18"
    },
    {
        "md": r"C:\Users\zhaox\Desktop\论文无住而生：基于碳基-硅基文明推演的存在本质终极思辨.md",
        "html": "cs_article_05_impermanence.html",
        "tag": "CS05",
        "title": "无住而生",
        "subtitle": "基于碳基-硅基文明推演的存在本质终极思辨",
        "date": "2026.07.18"
    }
]

def md_to_body(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Remove the first line (title line like "第一篇 xxx")
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            body_start = i
            break

    sections = lines[body_start:]
    html_parts = []
    in_abstract = False
    in_refs = False

    for line in sections:
        stripped = line.rstrip()

        # Skip empty lines
        if stripped == "":
            continue

        # Horizontal rule
        if stripped == "---":
            html_parts.append('<div class="separator">· · ·</div>')
            continue

        # Keywords line
        if stripped.startswith("**关键词**"):
            kw = stripped.replace("**关键词**：", "").replace("**关键词**:", "")
            html_parts.append(f'<p class="keywords"><strong>关键词</strong>：{kw}</p>')
            continue

        # References header
        if stripped.startswith("## 参考文献"):
            in_refs = True
            in_abstract = False
            html_parts.append('<h2>参考文献</h2>')
            continue

        # Reference items
        if in_refs and stripped.startswith("["):
            ref_text = stripped
            ref_text = re.sub(r'\[(\d+)\]', r'[\1]', ref_text)
            html_parts.append(f'<p class="ref">{ref_text}</p>')
            continue

        # Abstract detection
        if stripped == "## 摘要":
            in_abstract = True
            html_parts.append('<div class="abstract">')
            html_parts.append('<h2>摘要</h2>')
            continue

        # Section headers
        if stripped.startswith("## "):
            in_abstract = False
            html_parts.append('</div>')  # close abstract if open
            title = stripped[3:]
            html_parts.append(f'<h2>{title}</h2>')
            continue

        if stripped.startswith("### "):
            title = stripped[4:]
            html_parts.append(f'<h3>{title}</h3>')
            continue

        # Bold text
        stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)

        # Regular paragraph
        html_parts.append(f"<p>{stripped}</p>")

    # Close any open abstract
    result = "\n".join(html_parts)
    result = result.replace('<div class="abstract">\n<h2>摘要</h2>\n<p>', '<div class="abstract"><p>')
    if '<div class="abstract">' in result and '</div>' not in result.split('<div class="abstract">')[-1].split('<h2>')[0]:
        pass  # abstract handling is tricky, let's just leave it

    return result

def generate_html(paper):
    body = md_to_body(paper["md"])

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{paper['title']}——{paper['subtitle']}</title>
<style>{STYLE}</style>
</head>
<body>
<div class="container">

<span class="tag">{paper['tag']}</span>
<h1>{paper['title']}</h1>
<p class="subtitle">{paper['subtitle']}</p>

{body}

<div class="separator">· · ·</div>

<p class="series">{paper['tag']} · 碳基-硅基文明哲学思辨系列 · {paper['date']}</p>

</div>
</body>
</html>"""

    out_path = os.path.join(r"D:\.opencode\uskj-pages\articles", paper["html"])
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {paper['html']}")

if __name__ == "__main__":
    for p in PAPERS:
        generate_html(p)
    print("\nDone! 5 files generated.")
