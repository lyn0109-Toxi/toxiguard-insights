from fpdf import FPDF
from PIL import Image

pdf = FPDF(orientation='L', unit='mm', format='A4')
pdf.set_auto_page_break(auto=False)

images = [
    "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/ai_regulatory_science_1778505653746.png",
    "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/ctd_json_extraction_1778508828782.png",
    "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/shap_xai_explainability_1778508805819.png",
    "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/workflow_automation_1778505693551.png",
    "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/ly_type1_dashboard_1778505675870.png"
]

page_w = 297
page_h = 210

for img_path in images:
    img = Image.open(img_path)
    img_w, img_h = img.size
    aspect = img_w / img_h
    
    # Calculate fit within margins (10mm)
    max_w = page_w - 20
    max_h = page_h - 20
    
    if aspect > (max_w / max_h):
        # Fit to width
        final_w = max_w
        final_h = final_w / aspect
    else:
        # Fit to height
        final_h = max_h
        final_w = final_h * aspect
        
    x_offset = (page_w - final_w) / 2
    y_offset = (page_h - final_h) / 2
    
    pdf.add_page()
    # Add dark background for premium look
    pdf.set_fill_color(15, 23, 42) # Slate 900
    pdf.rect(0, 0, page_w, page_h, 'F')
    
    pdf.image(img_path, x=x_offset, y=y_offset, w=final_w, h=final_h)

output_path = "/Users/leeyoung-nam/Desktop/Antigravity Project/LY_Type1_Platform_Showcase.pdf"
pdf.output(output_path)
print(f"PDF generated at: {output_path}")
