from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

class LinkedInPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(26, 54, 93)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, 'ToxiGuard AI | The Human Judgment Premium Report', align='C')

def create_linkedin_carousel():
    pdf = LinkedInPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Page 1: Title & Graphic ---
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 24)
    pdf.ln(10)
    pdf.multi_cell(0, 15, "The Human Judgment Premium", align='C')
    
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(100)
    pdf.ln(5)
    pdf.multi_cell(0, 10, "Why Ethical Cognition is the New Strategic Currency", align='C')
    
    # Add Image
    img_path = "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/human_judgment_premium_concept_1778293735284.png"
    if os.path.exists(img_path):
        pdf.image(img_path, x=25, y=70, w=160)
    
    # --- Page 2: Insights ---
    pdf.add_page()
    pdf.set_text_color(26, 54, 93)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 15, "Insights from WSJ Future of Everything", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(45, 55, 72)
    
    insights = [
        "- THE COGNITIVE DIVIDE: Leaders warn of a gap between automated efficiency and human-centric judgment.",
        "- BEYOND PATTERNS: AI lacks the causal and ethical reasoning required for high-stakes regulatory decisions.",
        "- HUMAN-IN-THE-LOOP: Regulatory acceptance depends on human validators bridging data with ethics.",
        "- VALUE-BASED OUTCOMES: In an AI-Native era, ethical judgment is the highest premium."
    ]
    
    for line in insights:
        pdf.multi_cell(0, 10, line)
        pdf.ln(2)
    
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(26, 54, 93)
    pdf.multi_cell(0, 10, "ToxiGuard AI: Empowering the Final Decision.", align='C')

    output_path = "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/LinkedIn_Human_Judgment_Premium.pdf"
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    try:
        result = create_linkedin_carousel()
        print(f"PDF Created: {result}")
    except Exception as e:
        print(f"Error: {e}")
