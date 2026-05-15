import fs from 'fs';
import path from 'path';
import 'dotenv/config';

const CORRECT_TITLE = "FDA's Internal AI Just Got a Major Upgrade: What Elsa 4.0 and HALO Mean for the Pharmaceutical Industry";
const POST_ID = "9072991312052643084";

function markdownToHtml(md) {
  let html = md.replace(/^---[\s\S]*?---\n/, '');

  // HALO 인포그래픽 base64 삽입
  const imgPath = '/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/fda_halo_infographic_1778556157107.png';
  if (fs.existsSync(imgPath)) {
    const b64 = fs.readFileSync(imgPath, 'base64');
    html = html.replace(/!\[[^\]]*\]\([^)]*fda_halo_infographic[^)]*\)/, `<img src="data:image/png;base64,${b64}" alt="FDA HALO Architecture" style="max-width:100%;border-radius:12px;margin:24px 0;box-shadow:0 4px 20px rgba(0,0,0,0.15);"/>`);
  }
  // 나머지 이미지 제거
  html = html.replace(/!\[[^\]]*\]\([^)]+\)\n?/g, '');

  // Markdown Table → HTML
  html = html.replace(/(\|.+\|\n)+/g, (block) => {
    const rows = block.trim().split('\n').filter(r => !r.match(/^\|[-| :]+\|$/));
    const [header, ...body] = rows;
    const thCells = header.split('|').filter((c,i,a)=>i>0&&i<a.length-1)
      .map(c=>`<th style="background:#0f172a;color:#38bdf8;padding:10px 14px;font-weight:600;text-align:left;">${c.trim()}</th>`).join('');
    const bodyRows = body.map(r => {
      const cells = r.split('|').filter((c,i,a)=>i>0&&i<a.length-1)
        .map(c=>`<td style="padding:9px 14px;border-bottom:1px solid #f1f5f9;">${c.trim()}</td>`).join('');
      return `<tr>${cells}</tr>`;
    }).join('');
    return `<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:0.9em;"><thead><tr>${thCells}</tr></thead><tbody>${bodyRows}</tbody></table>`;
  });

  html = html.replace(/^# (.+)$/gm, '<h1 style="font-family:Georgia,serif;font-size:2em;font-weight:900;color:#0f172a;margin:0 0 20px;line-height:1.25;">$1</h1>');
  html = html.replace(/^## (.+)$/gm, '<h2 style="font-size:1.35em;font-weight:700;color:#0f172a;border-left:4px solid #38bdf8;padding-left:14px;margin:36px 0 14px;">$1</h2>');
  html = html.replace(/^### (.+)$/gm, '<h3 style="font-size:1.05em;font-weight:600;color:#1e293b;margin:24px 0 8px;">$1</h3>');
  html = html.replace(/^> (.+)$/gm, '<blockquote style="background:#0f172a;border-left:4px solid #38bdf8;padding:16px 20px;margin:20px 0;border-radius:0 8px 8px 0;font-style:italic;color:#e2e8f0;">$1</blockquote>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0ea5e9;">$1</a>');
  html = html.replace(/^🔗 (https?:\/\/\S+)/gm, '<a href="$1" target="_blank" style="display:block;color:#0ea5e9;word-break:break-all;font-size:0.85em;margin:4px 0;">🔗 $1</a>');
  html = html.replace(/^[-*] (.+)$/gm, '<li style="margin:7px 0;line-height:1.7;">$1</li>');
  html = html.replace(/(<li[^>]*>[\s\S]*?<\/li>\n?)+/g, m => `<ul style="padding-left:22px;margin:14px 0;">${m}</ul>`);
  html = html.replace(/^---$/gm, '<hr style="border:none;border-top:1px solid #e2e8f0;margin:36px 0;"/>');
  html = html.replace(/\n\n+/g, '</p><p style="margin:0 0 18px;line-height:1.85;color:#334155;">');
  html = `<div style="font-family:'Segoe UI',Arial,sans-serif;line-height:1.85;color:#334155;max-width:780px;margin:0 auto;"><p style="margin:0 0 18px;line-height:1.85;">${html}</p></div>`;
  return html;
}

async function updatePost() {
  const clientId     = process.env.BLOGGER_CLIENT_ID;
  const clientSecret = process.env.BLOGGER_CLIENT_SECRET;
  const refreshToken = process.env.BLOGGER_REFRESH_TOKEN;
  const blogId       = process.env.BLOG_ID;

  console.log('🔑 Getting access token...');
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: clientId, client_secret: clientSecret, refresh_token: refreshToken, grant_type: 'refresh_token' })
  });
  const { access_token } = await tokenRes.json();
  console.log('✅ Got access token.');

  const md = fs.readFileSync(path.resolve('blog_posts', 'daily', 'daily_2026-05-12.md'), 'utf8');
  const htmlContent = markdownToHtml(md);
  console.log(`✅ HTML ready (${htmlContent.length} chars).`);

  console.log('🚀 Updating existing post...');
  const res = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts/${POST_ID}`, {
    method: 'PUT',
    headers: { Authorization: `Bearer ${access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      kind: 'blogger#post', blog: { id: blogId }, id: POST_ID,
      title: CORRECT_TITLE, content: htmlContent,
      labels: ['FDA', 'Regulatory Science', 'AI', 'Elsa', 'HALO', 'Drug Development']
    })
  });
  const data = await res.json();
  if (data.url) { console.log(`\n🎉 Successfully updated!\n📎 URL: ${data.url}`); }
  else { console.error('❌ Failed:', JSON.stringify(data, null, 2)); }
}

updatePost();
