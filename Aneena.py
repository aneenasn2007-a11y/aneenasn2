"""
aesthetic_chatgpt.py
Generate an aesthetic image (wallpaper) with gradient, soft blobs, noise, and centered text.

Dependencies:
    pip install pillow numpy

Usage:
    python aesthetic_chatgpt.py
    (Opens and saves 'aesthetic_chatgpt.png' in the current folder.)

Customization:
    - Change SIZE for resolution
    - Adjust COLORS, TEXT, FONT_PATH, or other parameters below
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import numpy as np
import random
import math
import os

# ---------- Config ----------
SIZE = (1920, 1080)            # output image size (width, height)
OUTPUT = "aesthetic_chatgpt.png"
TEXT = "ChatGPT"
FONT_PATH = None               # set to path of a .ttf file for nicer fonts, e.g. "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 160
SEED = 42                      # reproducible output; set to None for random
NUM_BLOBS = 6                  # soft geometric shapes
BLOB_MAX_RADIUS = 600
GRADIENT_COLORS = [(20, 35, 65), (89, 45, 120)]  # dark -> purple (RGB tuples)
ACCENT_COLORS = [(255, 200, 120), (120, 220, 255), (200, 120, 255)]
NOISE_OPACITY = 12             # 0..255, how strong the grain/noise appears
# -----------------------------

if SEED is not None:
    random.seed(SEED)
    np.random.seed(SEED)

W, H = SIZE

def linear_gradient(size, color1, color2, horizontal=False):
    """Make a linear gradient from color1 to color2."""
    base = Image.new('RGB', size, color1)
    top = Image.new('RGB', size, color2)
    mask = Image.new('L', size)
    mask_data = []
    if horizontal:
        for x in range(size[0]):
            a = int(255 * (x / (size[0]-1)))
            mask_data.extend([a] * size[1])
    else:
        for y in range(size[1]):
            a = int(255 * (y / (size[1]-1)))
            mask_data.extend([a] * size[0])
    mask.putdata(mask_data)
    gradient = Image.composite(top, base, mask)
    return gradient

def radial_gradient(size, center, radius, inner_color, outer_color):
    """Simple radial gradient circle as image."""
    img = Image.new("RGBA", size, (0,0,0,0))
    px = img.load()
    cx, cy = center
    for y in range(size[1]):
        for x in range(size[0]):
            d = math.hypot(x - cx, y - cy) / max(radius, 1)
            d = min(max(d, 0.0), 1.0)
            inv = 1.0 - d
            r = int(inner_color[0]*inv + outer_color[0]*d)
            g = int(inner_color[1]*inv + outer_color[1]*d)
            b = int(inner_color[2]*inv + outer_color[2]*d)
            a = int(200 * (inv))  # alpha fades out
            if a > 0:
                px[x,y] = (r,g,b,a)
    return img

def make_soft_blob(size, cx, cy, radius, color):
    """Create a blurred soft blob using several radial gradients and blurs."""
    layer = Image.new("RGBA", size, (0,0,0,0))
    # base radial
    base = radial_gradient(size, (cx, cy), radius, color, (10,10,10))
    layer = Image.alpha_composite(layer, base)
    # add a slightly shifted smaller bright core
    core = radial_gradient(size, (int(cx + random.uniform(-radius*0.1, radius*0.1)),
                                 int(cy + random.uniform(-radius*0.1, radius*0.1))),
                           int(radius*0.6),
                           tuple(min(255, int(c*1.6)) for c in color),
                           (10,10,10))
    layer = Image.alpha_composite(layer, core)
    # heavy blur to soften edges
    layer = layer.filter(ImageFilter.GaussianBlur(radius*0.12))
    return layer

def add_grain(image, opacity=10):
    """Add subtle monochrome noise/grain to the image."""
    arr = np.random.normal(loc=128, scale=20, size=(H, W)).astype(np.uint8)
    noise = Image.fromarray(arr, mode='L').convert('RGBA')
    alpha = Image.new('L', (W,H), opacity)  # global alpha
    noise.putalpha(alpha)
    # convert to a colorized noise (slightly tinted)
    tint = Image.new('RGBA', (W,H), (255,255,255,0))
    noise = Image.composite(noise, tint, noise)
    return Image.alpha_composite(image.convert('RGBA'), noise)

def draw_text_centered(img, text, font_path=None, font_size=140, fill=(255,255,255), shadow=True):
