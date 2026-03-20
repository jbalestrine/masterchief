"""
Generate required Roku channel icon/splash PNGs.
Run: python make_images.py
Requires: Pillow  (pip install Pillow)
"""
from PIL import Image, ImageDraw, ImageFont
import os

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

BG      = (13, 17, 23)       # #0D1117
GREEN   = (35, 134, 54)      # #238636
TEXT    = (230, 237, 243)    # #E6EDF3

def make_icon(path, w, h):
    img = Image.new("RGBA", (w, h), BG)
    draw = ImageDraw.Draw(img)
    # rounded rect fill
    margin = 10
    draw.rounded_rectangle([margin, margin, w - margin, h - margin],
                            radius=16, fill=GREEN)
    # "MC" text centred
    font_size = max(16, h // 3)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    txt = "MC"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, (h - th) // 2), txt, fill=TEXT, font=font)
    img.save(path)
    print(f"  Created {path}")

def make_splash(path, w, h):
    img = Image.new("RGBA", (w, h), BG)
    draw = ImageDraw.Draw(img)
    try:
        font_big  = ImageFont.truetype("arial.ttf", 72)
        font_sub  = ImageFont.truetype("arial.ttf", 32)
    except Exception:
        font_big = font_sub = ImageFont.load_default()

    title = "MasterChief DevOps"
    sub   = "Your DevOps Platform"

    bbox = draw.textbbox((0, 0), title, font=font_big)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((w - tw) // 2, h // 2 - th - 20), title, fill=TEXT,  font=font_big)

    bbox2 = draw.textbbox((0, 0), sub, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((w - tw2) // 2, h // 2 + 20), sub, fill=(139, 148, 158), font=font_sub)

    img.save(path)
    print(f"  Created {path}")

print("Generating Roku channel images...")
make_icon(  os.path.join(IMAGES_DIR, "icon_focus_hd.png"),  336, 210)
make_icon(  os.path.join(IMAGES_DIR, "icon_side_hd.png"),   108, 69)
make_splash(os.path.join(IMAGES_DIR, "splash_hd.png"),      1280, 720)
print("Done. Images written to roku/images/")
