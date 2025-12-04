"""
Script to create placeholder product images
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Product information
products = {
    1: ("Wireless Earbuds", "#1B5E20"),
    2: ("Bluetooth Speaker", "#1B5E20"),
    3: ("Smart Watch", "#1B5E20"),
    4: ("Fitness Band", "#1B5E20"),
    5: ("Laptop Backpack", "#81C784"),
    6: ("Men's Running Shoes", "#81C784"),
    7: ("Women's Casual Shoes", "#81C784"),
    8: ("Cotton T-Shirt", "#81C784"),
    9: ("Jeans", "#81C784"),
    10: ("DSLR Camera", "#C5D8A4"),
    11: ("USB-C Cable", "#C5D8A4"),
    12: ("Portable Hard Disk", "#C5D8A4"),
    13: ("Oven Toaster Grill", "#FAE9D4"),
    14: ("Mixer Grinder", "#FAE9D4"),
    15: ("Induction Stove", "#FAE9D4"),
    16: ("Pressure Cooker", "#FAE9D4"),
    17: ("Office Chair", "#1B5E20"),
    18: ("Study Table", "#1B5E20"),
    19: ("Bed Mattress", "#81C784"),
    20: ("Table Lamp", "#C5D8A4"),
}

# Create images directory if it doesn't exist
os.makedirs('recommender/static/images', exist_ok=True)

# Create images for each product
for product_id, (product_name, color) in products.items():
    # Create image
    img = Image.new('RGB', (400, 400), color=color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Add product name
    text_bbox = draw.textbbox((0, 0), product_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (400 - text_width) // 2
    draw.text((text_x, 150), product_name, fill='white', font=font)
    
    # Add product ID
    id_text = f"Product #{product_id}"
    id_bbox = draw.textbbox((0, 0), id_text, font=small_font)
    id_width = id_bbox[2] - id_bbox[0]
    id_x = (400 - id_width) // 2
    draw.text((id_x, 250), id_text, fill='white', font=small_font)
    
    # Save image
    img.save(f'recommender/static/images/product_{product_id}.jpg')
    print(f"Created product_{product_id}.jpg")

print("All product images created successfully!")
