#!/usr/bin/env python3
"""
generate_hero_image.py

Compose a hero + services layout image for the TECH SOLUTIONS repo.
Usage:
    python generate_hero_image.py --src assets/reception.png --out preview/tech_reception_web_preview.png

The script includes robust font fallbacks and will create the output directory if needed.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import argparse
import sys

# Known font candidates to try if the explicit ones are missing
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

_font_cache = {}


def get_resample_filter():
    try:
        return Image.Resampling.LANCZOS  # type: ignore[attr-defined]
    except Exception:
        return Image.LANCZOS


def load_truetype(path: str, size: int):
    key = (path, size)
    if key in _font_cache:
        return _font_cache[key]
    try:
        f = ImageFont.truetype(path, size)
        _font_cache[key] = f
        return f
    except Exception:
        return None


def find_font(preferred_path: str | None, bold: bool, size: int):
    if preferred_path:
        tt = load_truetype(preferred_path, size)
        if tt:
            return tt

    candidates = FONT_CANDIDATES[:]
    if bold:
        bold_pref = [p for p in candidates if "Bold" in p or "bold" in p]
        other_pref = [p for p in candidates if p not in bold_pref]
        candidates = bold_pref + other_pref

    for p in candidates:
        tt = load_truetype(p, size)
        if tt:
            return tt

    return ImageFont.load_default()


def F(size: int, b: bool=False, regular_path: str|None=None, bold_path: str|None=None):
    return find_font(bold_path if b else regular_path, b, size)


def compose_image(src_path: Path, out_path: Path, W=1440, regular_font_path=None, bold_font_path=None):
    if not src_path.exists():
        raise FileNotFoundError(f"Source image not found: {src_path}")

    src = Image.open(src_path).convert("RGB")
    scale = W / src.width
    new_h = int(src.height * scale)
    resample = get_resample_filter()
    hero = src.resize((W, new_h), resample)

    H = 250 + hero.height + 720
    canvas = Image.new("RGB", (W, H), "#050811")
    d = ImageDraw.Draw(canvas)

    d.rectangle((0,0,W,82), fill="#070c16")
    d.text((70,28), "TECH ", font=F(25, True, regular_font_path, bold_font_path), fill="white")
    d.text((155,28), "SOLUTIONS", font=F(25, True, regular_font_path, bold_font_path), fill="#38a9ff")
    for i, t in enumerate(["Services", "Reception", "Contact"]):
        d.text((1050+i*105,31), t, font=F(16, False, regular_font_path, bold_font_path), fill="#cbd6e8")

    d.text((70,120), "NEXT-GENERATION TECHNOLOGY", font=F(14, True, regular_font_path, bold_font_path), fill="#45b4ff")
    d.text((70,155), "Build the", font=F(62, True, regular_font_path, bold_font_path), fill="white")
    d.text((70,225), "future.", font=F(62, True, regular_font_path, bold_font_path), fill="#54bdff")
    d.text((70,305), "A premium digital home for a modern", font=F(20, False, regular_font_path, bold_font_path), fill="#9eabc0")
    d.text((70,335), "technology company.", font=F(20, False, regular_font_path, bold_font_path), fill="#9eabc0")

    iy = 405
    canvas.paste(hero, (0, iy))

    sy = iy + hero.height
    d.rectangle((0,sy,W,H), fill="#07101e")
    d.text((70, sy+55), "WHAT WE DO", font=F(14, True, regular_font_path, bold_font_path), fill="#45b4ff")
    d.text((70, sy+88), "Technology, designed beautifully.", font=F(40, True, regular_font_path, bold_font_path), fill="white")

    cards = [
        ("Web Development","Fast, responsive websites"),
        ("App Development","Modern scalable applications"),
        ("Cloud Solutions","Reliable digital infrastructure"),
        ("AI & Automation","Intelligent workflows"),
        ("Cyber Security","Security-minded products"),
        ("Digital Strategy","Clear technology direction"),
    ]
    x0, y0 = 70, sy+170
    cw, ch, gap = 400, 125, 30
    for idx,(title,desc) in enumerate(cards):
        col, row = idx%3, idx//3
        x = x0 + col*(cw+gap)
        y = y0 + row*(ch+25)
        try:
            d.rounded_rectangle((x,y,x+cw,y+ch), radius=18, fill="#101b2b", outline="#1e344d", width=2)
        except AttributeError:
            d.rectangle((x,y,x+cw,y+ch), fill="#101b2b", outline="#1e344d", width=2)
        d.text((x+24,y+22), title, font=F(19, True, regular_font_path, bold_font_path), fill="white")
        d.text((x+24,y+60), desc, font=F(14, False, regular_font_path, bold_font_path), fill="#8795ab")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=92)
    return out_path


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Compose TECH SOLUTIONS hero image")
    p.add_argument("--src", "-s", required=True, help="Path to source hero image (reception.png)")
    p.add_argument("--out", "-o", default="preview/tech_reception_web_preview.png", help="Output path")
    p.add_argument("--width", "-W", type=int, default=1440, help="Target canvas width")
    p.add_argument("--regular-font", help="Path to regular font .ttf")
    p.add_argument("--bold-font", help="Path to bold font .ttf")
    return p.parse_args()


def main():
    args = parse_args()
    src_path = Path(args.src)
    out_path = Path(args.out)
    try:
        out = compose_image(src_path, out_path, W=args.width, regular_font_path=args.regular_font, bold_font_path=args.bold_font)
        print(f"Saved preview to: {out}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print("Unhandled error composing image:", e, file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    main()
