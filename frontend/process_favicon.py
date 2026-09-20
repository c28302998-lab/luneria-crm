from PIL import Image
import numpy as np
import sys

def remove_black_background(input_path, output_path):
    try:
        img = Image.open(input_path).convert("RGBA")
        data = np.array(img)
        
        # Black background is usually close to [0,0,0]
        # We can create a mask for pixels that are very dark
        r, g, b, a = data.T
        
        # Define a threshold for "black"
        threshold = 30
        black_areas = (r < threshold) & (g < threshold) & (b < threshold)
        
        # Set alpha to 0 for black areas
        data[..., 3][black_areas.T] = 0
        
        # Alternatively, we can use a circular mask if the logo is a perfect circle
        h, w = data.shape[:2]
        center = (h//2, w//2)
        radius = min(h, w)//2
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        
        # Create a strict circular mask
        circular_mask = dist_from_center > radius
        data[..., 3][circular_mask] = 0
        
        out_img = Image.fromarray(data)
        out_img.save(output_path, "PNG")
        print(f"Saved {output_path}")
    except Exception as e:
        print(f"Error: {e}")

remove_black_background("src/app/icon.jpg", "src/app/icon.png")
remove_black_background("public/logo.jpg", "public/logo.png")
