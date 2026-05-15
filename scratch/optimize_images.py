from PIL import Image
import os

def optimize_image(input_path, output_path, max_width=800):
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return False
    
    with Image.open(input_path) as img:
        # Calculate aspect ratio
        width_percent = (max_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(width_percent)))
        
        # Resize
        img = img.resize((max_width, hsize), Image.Resampling.LANCZOS)
        
        # Convert to RGB before saving as JPEG
        rgb_img = img.convert('RGB')
        rgb_img.save(output_path, "JPEG", quality=85, optimize=True)
        print(f"Optimized: {output_path}")
        return True

if __name__ == "__main__":
    brain_dir = "/Users/leeyoung-nam/.gemini/antigravity/brain/1136e33a-d9b6-4526-9231-15cd55cf8546/"
    
    # Optimize Screenshot
    optimize_image(
        os.path.join(brain_dir, "media__1778295785166.png"),
        os.path.join(brain_dir, "screenshot_optimized.jpg")
    )
    
    # Optimize Concept Art
    optimize_image(
        os.path.join(brain_dir, "irrational_human_choice_concept_1778295738747.png"),
        os.path.join(brain_dir, "concept_optimized.jpg")
    )
