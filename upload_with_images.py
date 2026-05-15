import os
import json
import base64
import urllib.request
import urllib.parse
from PIL import Image
import io
import re

def compress_image_to_base64(img_path):
    img = Image.open(img_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.thumbnail((800, 800))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def main():
    # Load env vars
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                env_vars[k] = v

    client_id = env_vars.get('BLOGGER_CLIENT_ID')
    client_secret = env_vars.get('BLOGGER_CLIENT_SECRET')
    refresh_token = env_vars.get('BLOGGER_REFRESH_TOKEN')
    blog_id = env_vars.get('BLOG_ID')

    # Get access token
    print("Getting access token...")
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
    with urllib.request.urlopen(req) as response:
        token_data = json.loads(response.read().decode('utf-8'))
    access_token = token_data['access_token']
    
    # Get latest post ID
    print("Fetching latest post ID to update...")
    req_posts = urllib.request.Request(f'https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults=1', headers={'Authorization': f'Bearer {access_token}'})
    with urllib.request.urlopen(req_posts) as response:
        posts_data = json.loads(response.read().decode('utf-8'))
    
    if 'items' not in posts_data or len(posts_data['items']) == 0:
        print("No posts found.")
        return
    post_id = posts_data['items'][0]['id']
    print(f"Latest Post ID: {post_id}")

    # Read markdown
    import datetime
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

    # Update post
    print("Updating post on Blogger...")
    update_data = json.dumps({
        "kind": "blogger#post",
        "blog": {"id": blog_id},
        "id": post_id,
        "title": title,
        "content": html_content
    }).encode('utf-8')
    
    req_update = urllib.request.Request(
        f'https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/{post_id}',
        data=update_data,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        method='PUT'
    )
    
    try:
        with urllib.request.urlopen(req_update) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("Successfully updated! URL:", res_data.get('url'))
    except Exception as e:
        print("Update failed:", e)

if __name__ == '__main__':
    main()
