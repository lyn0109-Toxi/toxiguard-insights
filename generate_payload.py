import os
import json
import base64
from PIL import Image
import io
import re
import datetime

def compress_image_to_base64(img_path):
    img = Image.open(img_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def main():
    iso_date = datetime.datetime.now().strftime("%Y-%m-%d")
    md_path = os.path.join('blog_posts', 'daily', f'daily_{iso_date}.md')
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Get title
    title_match = re.search(r'^title:\s*["\']?([^"\'\n]+)["\']?', md_text, re.MULTILINE)
    title = title_match.group(1) if title_match else f"Pharma Daily Insights ({iso_date})"

    # Embed images
    def replace_image(match):
        alt = match.group(1)
        img_path = match.group(2)
        if os.path.exists(img_path):
            print(f"Compressing {img_path}...")
            b64 = compress_image_to_base64(img_path)
            return f'<img src="data:image/jpeg;base64,{b64}" alt="{alt}" style="max-width:100%; border-radius:8px; margin:20px 0; box-shadow:0 4px 6px rgba(0,0,0,0.1);"/>'
        return match.group(0)

    html_content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, md_text)
    
    # Basic MD to HTML
    html_content = re.sub(r'^### (.*)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^\> (.*)$', r'<blockquote>\1</blockquote>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
    html_content = re.sub(r'^\* (.*)$', r'<ul><li>\1</li></ul>', html_content, flags=re.MULTILINE)
    html_content = html_content.replace('</ul>\n<ul>', '')
    html_content = html_content.replace('\n\n', '<p></p>')
    html_content = html_content.replace('---', '<hr/>')
    
    html_content = f'<div style="font-family: sans-serif; line-height: 1.6; color: #333;">{html_content}</div>'

    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                env_vars[k] = v
    blog_id = env_vars.get('BLOG_ID')

    payload = {
        "kind": "blogger#post",
        "blog": {"id": blog_id},
        "title": title,
        "content": html_content
    }

    with open('payload.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f)
    
    print("Payload written to payload.json")

if __name__ == '__main__':
    main()
