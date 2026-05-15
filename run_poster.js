import { postDailyBlog } from './src/blog_poster.js';

console.log("Starting forced blog post...");
postDailyBlog().then(() => {
  console.log("Forced blog post finished.");
  process.exit(0);
}).catch(e => {
  console.error("Error:", e);
  process.exit(1);
});
