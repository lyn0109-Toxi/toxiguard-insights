import 'dotenv/config';
import { google } from 'googleapis';

const blogger = google.blogger('v3');
const oauth2Client = new google.auth.OAuth2(
  process.env.BLOGGER_CLIENT_ID,
  process.env.BLOGGER_CLIENT_SECRET
);
oauth2Client.setCredentials({ refresh_token: process.env.BLOGGER_REFRESH_TOKEN });

// 1x1 pixel transparent PNG in base64
const base64Image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
const htmlContent = `<p>Test base64 image:</p><img src="${base64Image}" alt="test" />`;

async function testBase64() {
  try {
    const res = await blogger.posts.insert({
      auth: oauth2Client,
      blogId: process.env.BLOG_ID,
      requestBody: {
        title: "Base64 Image Test",
        content: htmlContent,
      }
    });
    console.log("Success:", res.data.url);
  } catch (err) {
    console.error("Error:", err.message);
  }
}
testBase64();
