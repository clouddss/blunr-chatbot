from PIL import Image, ImageDraw, ImageFont
import os

# Skapa bildmapp om den inte finns
os.makedirs('static/images', exist_ok=True)

def create_avatar(filename, text, bg_color, text_color=(255, 255, 255)):
    """Skapa en enkel avatar-bild"""
    img = Image.new('RGB', (200, 200), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Rita text i mitten
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        font = ImageFont.load_default()
    
    text_width = draw.textlength(text, font=font)
    text_height = 60
    x = (200 - text_width) // 2
    y = (200 - text_height) // 2
    
    draw.text((x, y), text, fill=text_color, font=font)
    
    img.save(f'static/images/{filename}')
    print(f"Skapade {filename}")

# Skapa placeholder-bilder
create_avatar('ai-avatar.png', 'AI', (88, 101, 242))
create_avatar('user-avatar.png', 'U', (67, 181, 129))
create_avatar('avatar.png', 'B', (255, 184, 0), (0, 0, 0))

print("Placeholder-bilder skapade!")