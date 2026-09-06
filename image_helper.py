# -*- coding: utf-8 -*-
"""
Slaydlar uchun oddiy dekorativ rasm (gradient + matn) generatori.
Internetga ulanish talab qilinmaydi - hammasi Pillow bilan chiziladi.
"""

import os
import hashlib
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "generated_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Har xil mavzular uchun turli rang palitralari
PALETTES = [
    ((79, 70, 229), (236, 72, 153)),   # indigo -> pink
    ((16, 185, 129), (59, 130, 246)),  # green -> blue
    ((245, 158, 11), (239, 68, 68)),   # amber -> red
    ((6, 182, 212), (99, 102, 241)),   # cyan -> indigo
    ((236, 72, 153), (251, 146, 60)),  # pink -> orange
]


def _pick_palette(seed_text: str):
    h = int(hashlib.md5(seed_text.encode("utf-8")).hexdigest(), 16)
    return PALETTES[h % len(PALETTES)]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def generate_slide_image(text: str, width=1280, height=720) -> str:
    """Berilgan matn asosida gradient fon + katta harf/ikon chizadi.
    Qaytaradi: yaratilgan rasm fayl yo'li (PNG)
    """
    color1, color2 = _pick_palette(text)
    img = Image.new("RGB", (width, height), color1)
    draw = ImageDraw.Draw(img)

    # Diagonal gradient
    for y in range(height):
        t = y / height
        row_color = _lerp(color1, color2, t)
        draw.line([(0, y), (width, y)], fill=row_color)

    # Markazga yarim shaffof oq doira (RGBA overlay orqali)
    circle_radius = 140
    cx, cy = width // 2, height // 2

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse(
        [cx - circle_radius, cy - circle_radius, cx + circle_radius, cy + circle_radius],
        fill=(255, 255, 255, 70),
        outline=(255, 255, 255, 200),
        width=4,
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Birinchi harfni doira ustiga to'q rangda chizish (kontrast uchun)
    letter = (text.strip()[:1] or "?").upper()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 160)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), letter, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    text_color = _lerp(color1, color2, 0.5)
    # Kontrastni oshirish uchun rangni to'qlashtiramiz
    text_color = tuple(max(0, c - 60) for c in text_color)
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), letter, fill=text_color, font=font)

    safe_name = "".join(c for c in text if c.isalnum())[:20] or "slide"
    path = os.path.join(OUTPUT_DIR, f"{safe_name}_{abs(hash(text)) % 10000}.png")
    img.save(path)
    return path
