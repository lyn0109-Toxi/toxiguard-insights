/**
 * fix_title.js
 * 방금 게시된 포스트의 제목을 올바르게 수정합니다.
 */
import 'dotenv/config';

const CORRECT_TITLE = "FDA's Internal AI Just Got a Major Upgrade: What Elsa 4.0 and HALO Mean for the Pharmaceutical Industry";
const POST_URL = "https://toxiguardai.blogspot.com/2026/05/fda.html";

async function fixTitle() {
  const clientId     = process.env.BLOGGER_CLIENT_ID;
  const clientSecret = process.env.BLOGGER_CLIENT_SECRET;
  const refreshToken = process.env.BLOGGER_REFRESH_TOKEN;
  const blogId       = process.env.BLOG_ID;

  // 1. Access Token
  const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: clientId, client_secret: clientSecret, refresh_token: refreshToken, grant_type: 'refresh_token' })
  });
  const { access_token } = await tokenRes.json();

  // 2. 최신 포스트 찾기
  const listRes = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts?maxResults=1`, {
    headers: { Authorization: `Bearer ${access_token}` }
  });
  const listData = await listRes.json();
  const post = listData.items[0];
  console.log(`Found: "${post.title}" (ID: ${post.id})`);

  // 3. 제목 수정 (PATCH)
  const patchRes = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts/${post.id}`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${access_token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: CORRECT_TITLE })
  });
  const patchData = await patchRes.json();
  if (patchData.title) {
    console.log(`✅ Title fixed: "${patchData.title}"`);
    console.log(`📎 URL: ${patchData.url}`);
  } else {
    console.error('❌ Failed:', patchData);
  }
}

fixTitle();
