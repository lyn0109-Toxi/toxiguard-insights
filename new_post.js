/**
 * new_post.js
 * Blogger에 새 포스트를 생성합니다.
 * daily_2026-05-12.md를 HTML로 변환하여 새 게시글로 발행합니다.
 */
import fs from 'fs';
import path from 'path';
import 'dotenv/config';

// ── Markdown → HTML 변환 ──────────────────────────────────────────────────
function markdownToHtml(md) {
  let html = md;

  // frontmatter 제거 (--- ... --- 블록)
  html = html.replace(/^---[\s\S]*?---\n/, '');

  // HALO 인포그래픽 이미지 경로 → base64 또는 제거 (외부 접근 불가 로컬 경로)
  const HALO_IMG_PATH = '/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/fda_halo_infographic_1778556157107.png';
  if (fs.existsSync(HALO_IMG_PATH)) {
    const base64 = fs.readFileSync(HALO_IMG_PATH, 'base64');
    html = html.replace(
      /!\[FDA HALO Platform Architecture Infographic\]\([^)]+\)/,
      `<img src="data:image/png;base64,${base64}" alt="FDA HALO Platform Architecture" style="max-width:100%;border-radius:12px;margin:24px 0;box-shadow:0 4px 20px rgba(0,0,0,0.15);"/>`
    );
  }

  // 나머지 이미지 제거 (로컬 경로는 Blogger에서 표시 불가)
  html = html.replace(/!\[[^\]]*\]\([^)]+\)\n?/g, '');

  // 표 (Markdown Table → HTML table)
  html = html.replace(/^\|(.+)\|$/gm, (line) => {
    const cells = line.split('|').filter((c, i, arr) => i !== 0 && i !== arr.length - 1);
    return '<tr>' + cells.map(c => `<td style="padding:8px 12px;border:1px solid #e2e8f0;">${c.trim()}</td>`).join('') + '</tr>';
  });
  // 구분선 제거 (|---|---|)
  html = html.replace(/<tr>(<td[^>]*>\s*[-:]+\s*<\/td>)+<\/tr>\n?/g, '');
  // 첫번째 행을 thead로
  html = html.replace(/<tr>(<td[^>]*>Feature.*?<\/td>)/, (match) => {
    return match.replace(/<td/g, '<th style="background:#0f172a;color:#38bdf8;padding:8px 12px;font-weight:600;"').replace(/<\/td>/g, '</th>');
  });
  html = html.replace(/(<tr>(<t[hd][^>]*>.*?<\/t[hd]>)+<\/tr>\n?)+/gs, (tableContent) => {
    return `<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:0.9em;">${tableContent}</table>`;
  });

  // Headings
  html = html.replace(/^# (.+)$/gm, '<h1 style="font-size:2em;font-weight:900;color:#0f172a;margin:0 0 16px;">$1</h1>');
  html = html.replace(/^## (.+)$/gm, '<h2 style="font-size:1.4em;font-weight:700;color:#0f172a;border-left:4px solid #38bdf8;padding-left:12px;margin:32px 0 12px;">$1</h2>');
  html = html.replace(/^### (.+)$/gm, '<h3 style="font-size:1.1em;font-weight:600;color:#1e293b;margin:24px 0 8px;">$1</h3>');

  // Blockquote (Jeremy Walsh 인용)
  html = html.replace(/^> (.+)$/gm, '<blockquote style="background:#0f172a;border-left:4px solid #38bdf8;padding:16px 20px;margin:20px 0;border-radius:0 8px 8px 0;font-style:italic;color:#e2e8f0;">$1</blockquote>');

  // Bold / Italic
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Inline links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:#0ea5e9;text-decoration:underline;">$1</a>');

  // References 섹션: 🔗로 시작하는 줄을 링크 블록으로
  html = html.replace(/^🔗 (https?:\/\/\S+)/gm, '<a href="$1" target="_blank" style="display:block;color:#0ea5e9;word-break:break-all;font-size:0.85em;margin:4px 0;">🔗 $1</a>');

  // Bullet list
  html = html.replace(/^[-*] (.+)$/gm, '<li style="margin:6px 0;">$1</li>');
  html = html.replace(/(<li[^>]*>.*<\/li>\n?)+/gs, (items) => `<ul style="padding-left:20px;margin:12px 0;">${items}</ul>`);

  // Numbered list
  html = html.replace(/^\d+\. (.+)$/gm, '<li style="margin:6px 0;">$1</li>');

  // HR
  html = html.replace(/^---$/gm, '<hr style="border:none;border-top:1px solid #e2e8f0;margin:32px 0;"/>');

  // Paragraph breaks
  html = html.replace(/\n\n+/g, '</p><p style="margin:0 0 16px;line-height:1.8;">');

  // Wrap in container
  html = `<div style="font-family:'Segoe UI',sans-serif;line-height:1.8;color:#1e293b;max-width:760px;margin:0 auto;"><p style="margin:0 0 16px;line-height:1.8;">${html}</p></div>`;

  return html;
}

// ── 메인 업로드 함수 ──────────────────────────────────────────────────────
async function publishNewPost() {
  try {
    const clientId     = process.env.BLOGGER_CLIENT_ID;
    const clientSecret = process.env.BLOGGER_CLIENT_SECRET;
    const refreshToken = process.env.BLOGGER_REFRESH_TOKEN;
    const blogId       = process.env.BLOG_ID;

    // 1. Access Token 발급
    console.log('🔑 Getting access token...');
    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: clientId,
        client_secret: clientSecret,
        refresh_token: refreshToken,
        grant_type: 'refresh_token'
      })
    });
    const tokenData = await tokenRes.json();
    if (!tokenData.access_token) {
      console.error('❌ Failed to get access token:', tokenData);
      return;
    }
    const accessToken = tokenData.access_token;
    console.log('✅ Got access token.');

    // 2. Markdown 파일 읽기
    const filePath = path.resolve('blog_posts', 'daily', 'daily_2026-05-12.md');
    const markdown  = fs.readFileSync(filePath, 'utf8');

    // 3. 제목 추출
    const titleMatch = markdown.match(/^title:\s*["']?([^"'\n]+)["']?/m);
    const articleTitle = titleMatch ? titleMatch[1] : 'FDA HALO & Elsa 4.0 Analysis';
    console.log(`📝 Title: ${articleTitle}`);

    // 4. Markdown → HTML 변환
    const htmlContent = markdownToHtml(markdown);
    console.log(`✅ HTML converted (${htmlContent.length} chars).`);

    // 5. 새 포스트 생성 (POST)
    console.log('🚀 Publishing new post to Blogger...');
    const postRes = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        kind: 'blogger#post',
        blog: { id: blogId },
        title: articleTitle,
        content: htmlContent,
        labels: ['FDA', 'Regulatory Science', 'AI', 'Elsa', 'HALO', 'Drug Development']
      })
    });

    const postData = await postRes.json();
    if (postData.url) {
      console.log(`\n🎉 Successfully published!`);
      console.log(`📎 URL: ${postData.url}`);
    } else {
      console.error('❌ Failed to publish:', JSON.stringify(postData, null, 2));
    }
  } catch (err) {
    console.error('❌ Error:', err);
  }
}

publishNewPost();
