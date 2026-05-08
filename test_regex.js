import fs from 'fs';
import path from 'path';

let markdown = `Here is an image: ![Chart](/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/lung_cancer_pipeline_chart_1777746137449.png)`;

// Replace local images with base64
const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
markdown = markdown.replace(imageRegex, (match, alt, imgPath) => {
  if (fs.existsSync(imgPath)) {
    const ext = path.extname(imgPath).substring(1) || 'png';
    const base64 = fs.readFileSync(imgPath, 'base64');
    return `![${alt}](data:image/${ext};base64,${base64})`;
  }
  return match;
});

console.log(markdown.substring(0, 150) + "...");
