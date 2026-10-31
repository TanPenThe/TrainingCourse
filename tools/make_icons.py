"""Draws the Training Program app icon (dumbbell on burnt orange) at every size the PWA and stores need."""
from PIL import Image, ImageDraw
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "app/icons"
os.makedirs(OUT, exist_ok=True)
BG, FG = (217, 72, 15), (255, 255, 255)

def draw(size, scale=1.0, rounded=False):
    S = 1024  # draw large, then downsample for smooth edges
    im = Image.new("RGBA", (S, S), BG + (255,))
    d = ImageDraw.Draw(im)
    c, k = S / 2, S / 1024 * scale
    # bar
    d.rounded_rectangle([c - 300 * k, c - 34 * k, c + 300 * k, c + 34 * k], radius=34 * k, fill=FG)
    # plates: big inner, smaller outer, each side
    for sgn in (-1, 1):
        x = c + sgn * 210 * k
        d.rounded_rectangle([x - 46 * k, c - 210 * k, x + 46 * k, c + 210 * k], radius=40 * k, fill=FG)
        x2 = c + sgn * 300 * k
        d.rounded_rectangle([x2 - 36 * k, c - 140 * k, x2 + 36 * k, c + 140 * k], radius=32 * k, fill=FG)
    if rounded:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, S, S], radius=S * 0.22, fill=255)
        im.putalpha(mask)
    return im.resize((size, size), Image.LANCZOS)

draw(192, 0.95).save(f"{OUT}/icon-192.png")
draw(512, 0.95).save(f"{OUT}/icon-512.png")
draw(512, 0.72).save(f"{OUT}/maskable-512.png")   # content kept inside the 80% safe zone
draw(180, 0.95).convert("RGB").save(f"{OUT}/apple-touch-icon.png")
draw(1024, 0.95).convert("RGB").save(f"{OUT}/icon-1024.png")  # App Store / Play Store listing
draw(64, 0.95, rounded=True).save(f"{OUT}/favicon.png")
print("icons written to", OUT)
