import fs from 'fs';
import path from 'path';
import 'dotenv/config';

async function upload() {
  try {
    const clientId = process.env.BLOGGER_CLIENT_ID;
    const clientSecret = process.env.BLOGGER_CLIENT_SECRET;
    const refreshToken = process.env.BLOGGER_REFRESH_TOKEN;
    const blogId = process.env.BLOG_ID;

    console.log("Getting access token...");
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
      console.error("Failed to get access token", tokenData);
      return;
    }
    const accessToken = tokenData.access_token;
    console.log("Got access token.");

    const isoDate = new Date().toISOString().slice(0, 10);
    const filename = `daily_${isoDate}.md`;
    const filePath = path.resolve('blog_posts', 'daily', filename);
    let markdownContent = fs.readFileSync(filePath, 'utf8');

    // Replace images with placeholders because base64 of 3 premium images is too large for Blogger API
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
    markdownContent = markdownContent.replace(imageRegex, (match, alt, imgPath) => {
      return `\n<br/><b>[이미지 삽입 위치: ${alt}]</b><br/>\n`;
    });

    let articleTitle = `Pharma Daily Insights (${isoDate})`;
    const titleMatch = markdownContent.match(/^title:\s*["']?([^"'\n]+)["']?/m);
    if (titleMatch) {
      articleTitle = titleMatch[1];
    }
    
    // Convert basic markdown to HTML for Blogger
    let htmlContent = markdownContent
      .replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" style="max-width:100%; border-radius:8px; margin:20px 0; box-shadow:0 4px 6px rgba(0,0,0,0.1);"/>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/^\* (.*$)/gim, '<ul><li>$1</li></ul>')
      .replace(/<\/ul>\n<ul>/g, '')
      .replace(/\n\n/g, '<p></p>')
      .replace(/---/g, '<hr/>');

    htmlContent = `<div style="font-family: sans-serif; line-height: 1.6; color: #333;">${htmlContent}</div>`;

    console.log(`Posting to Blogger: ${articleTitle}`);
    const postRes = await fetch(`https://www.googleapis.com/blogger/v3/blogs/${blogId}/posts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        kind: 'blogger#post',
        blog: {
          id: blogId
        },
        title: articleTitle,
        content: htmlContent
      })
    });
    
    const postData = await postRes.json();
    if (postData.url) {
      console.log(`Successfully posted! URL: ${postData.url}`);
    } else {
      console.error("Failed to post", postData);
    }
  } catch (err) {
    console.error("Error:", err);
  }
}

upload();
