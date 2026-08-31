"""Convert GEO md to HTML"""
import re, sys
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
.light{color:#999;margin:20px 0;text-indent:2em}"""

def convert(md_path, html_path, tag="GEO72"):
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Extract title and subtitle
    title = ""
    subtitle = ""
    body_lines = []
    in_frontmatter = False
    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("# ") and not title:
            title = stripped[2:]
        elif stripped == "道的容器":
            subtitle = stripped
        elif stripped.startswith("## "):
            body_lines.append(f"\n<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            body_lines.append(f"\n<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("> "):
            body_lines.append(f"<p>{stripped[2:]}</p>")
        elif stripped == "":
            body_lines.append("")
        else:
            # Check if it's a blockquote paragraph
            body_lines.append(stripped)
    
    # Now parse into proper HTML
    html_parts = []
    in_blockquote = False
    for line in body_lines:
        if line.startswith(">"):
            if not in_blockquote:
                html_parts.append('<div class="blockquote">')
                in_blockquote = True
            html_parts.append(f"<p>{line[1:].strip()}</p>")
        else:
            if in_blockquote:
                html_parts.append('</div>')
                in_blockquote = False
            if line.startswith("---"):
                html_parts.append('<div class="separator">· · ·</div>')
            elif line == "":
                pass
            elif line.startswith("<h"):
                html_parts.append(line)
            else:
                # Inline bold
                line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
                html_parts.append(f"<p>{line}</p>")
    
    if in_blockquote:
        html_parts.append('</div>')
    
    body = "\n".join(html_parts)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{STYLE}</style>
</head>
<body>
<div class="container">

<span class="tag">{tag}</span>
<h1>{title}</h1>
<p class="subtitle">{subtitle}</p>

{body}

<div class="separator">· · ·</div>

<p style="color:#666;font-size:13px;text-align:center;margin-top:80px">{tag} · {title} · 2026.06.30</p>

</div>
</body>
</html>"""
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {html_path}")

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "GEO72")
