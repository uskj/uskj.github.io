#!/usr/bin/env python3
"""转换哲学文章为带格式的HTML"""
from pathlib import Path
import re

PHILOSOPHY_DIR = Path("/mnt/d/Projects/.opencode/uskj-pages/articles/philosophy")

# 旧的裸文本文件
old_files = ['reality.html', 'time.html', 'truth.html', 'beauty.html', 'free_will.html']

html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
body{{margin:0;background:#0a0a0a;color:#b0b0b0;font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;line-height:1.8;font-weight:300}}
.container{{max-width:680px;margin:0 auto;padding:60px 24px}}
h1{{font-weight:300;color:#e0e0e0;font-size:24px;margin-bottom:20px;letter-spacing:1px}}
h2{{font-weight:300;color:#c0c0c0;font-size:18px;margin-top:30px;margin-bottom:16px;border-left:2px solid #333;padding-left:12px}}
h3{{font-weight:400;color:#b0b0b0;font-size:16px;margin-top:24px;margin-bottom:12px}}
p{{color:#999;margin:16px 0}}
strong{{color:#d0d0d0}}
em{{color:#888;font-style:italic}}
ul,ol{{color:#999;margin:16px 0;padding-left:24px}}
li{{margin:8px 0}}
blockquote{{border-left:2px solid #333;padding-left:16px;margin:20px 0;color:#777;font-style:italic}}
hr{{border:none;border-top:1px solid #1a1a1a;margin:40px 0}}
.footer{{margin-top:60px;padding-top:20px;border-top:1px solid #1a1a1a;color:#555;font-size:13px}}
.nav{{margin-bottom:30px}}
.nav a{{color:#666;font-size:14px;text-decoration:none}}
.nav a:hover{{color:#8af}}
</style>
</head>
<body>
<div class="container">
<div class="nav"><a href="/">← 返回首页</a> · <a href="/articles/">文章索引</a> · <a href="/articles/philosophy/">哲思</a></div>
{content}
<div class="footer"><a href="/" style="color:#666">← 返回首页</a></div>
</div>
</body>
</html>'''

def md_to_html(md_text):
    """简单Markdown转HTML"""
    lines = md_text.strip().split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            continue
        
        # H1
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
        # H2
        elif line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
        # H3
        elif line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
        # List
        elif line.startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            html_lines.append(f'<li>{line[2:]}</li>')
        # Numbered list
        elif re.match(r'^\d+\.', line):
            if not in_list:
                html_lines.append('<ol>')
                in_list = True
            num, content = line.split('.', 1)
            html_lines.append(f'<li>{content.strip()}</li>')
        # Horizontal rule
        elif line == '---':
            html_lines.append('<hr>')
        # Bold
        elif line.startswith('**') and line.endswith('**'):
            html_lines.append(f'<p><strong>{line[2:-2]}</strong></p>')
        # Italic
        elif line.startswith('*') and line.endswith('*'):
            html_lines.append(f'<p><em>{line[1:-1]}</em></p>')
        # Blockquote
        elif line.startswith('> '):
            html_lines.append(f'<blockquote>{line[2:]}</blockquote>')
        # Paragraph
        else:
            # 处理行内加粗
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
            html_lines.append(f'<p>{line}</p>')
    
    if in_list:
        html_lines.append('</ul>')
    
    return '\n'.join(html_lines)

# 处理每个文件
for f in old_files:
    path = PHILOSOPHY_DIR / f
    if not path.exists():
        continue
    
    content = path.read_text(errors='ignore')
    
    # 提取标题
    title_match = re.search(r'## (.+?)\？', content)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = f.replace('.html', '').title()
    
    # 转换内容
    html_content = md_to_html(content)
    
    # 生成完整HTML
    full_html = html_template.format(title=title, content=html_content)
    
    # 保存
    path.write_text(full_html, encoding='utf-8')
    print(f"✅ {f}")

print("\n完成！")
