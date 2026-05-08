import cron from 'node-cron';
import { postDailyBlog } from './src/blog_poster.js';

console.log(`[${new Date().toISOString()}] Starting cron scheduler for Blogger Auto-Poster...`);
console.log('The daily blog post job is scheduled to run every day at 08:00 AM local time.');

// Schedule: 0 8 * * * (Minute 0, Hour 8, Every day)
cron.schedule('0 8 * * *', () => {
  console.log(`[${new Date().toISOString()}] Cron trigger: Running daily blog post...`);
  postDailyBlog();
});
