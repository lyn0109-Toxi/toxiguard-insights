import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function createPdf() {
  const pdfDoc = await PDFDocument.create();
  
  const images = [
    'compressed_images/1.jpg',
    'compressed_images/2.jpg',
    'compressed_images/3.jpg',
    'compressed_images/4.jpg',
    'compressed_images/5.jpg'
  ];

  for (const imgPath of images) {
    if (fs.existsSync(imgPath)) {
      const imgBytes = fs.readFileSync(imgPath);
      const img = await pdfDoc.embedJpg(imgBytes);
      const { width, height } = img.scale(1);
      
      const page = pdfDoc.addPage([width, height]);
      page.drawImage(img, {
        x: 0,
        y: 0,
        width: width,
        height: height
      });
    }
  }

  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync('LY_Type1_Platform_Showcase.pdf', pdfBytes);
  console.log("PDF created successfully!");
}

createPdf().catch(console.error);
