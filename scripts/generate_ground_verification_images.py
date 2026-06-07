#!/usr/bin/env python3
"""Generate ground verification JPEG placeholders for Mirpur 12 survey sites."""

import csv
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "field_data", "mirpur12_ground_data.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "frontend", "images")


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name.strip())


def generate_with_pillow(filename, title):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (640, 480), color=(18, 28, 48))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (639, 479)], outline=(56, 189, 248), width=3)
    draw.text((24, 24), "Mirpur 12 · Ground Verification", fill=(148, 163, 184))
    wrapped = title[:70] + ("…" if len(title) > 70 else "")
    draw.text((24, 200), wrapped, fill=(241, 245, 249))
    draw.text((24, 420), "Urban Heat Island Field Survey", fill=(100, 116, 139))
    img.save(filename, "JPEG", quality=85)


def generate_minimal_jpeg(filename, title):
    """Write a minimal valid JPEG without external dependencies."""
    # 1x1 pixel dark JPEG (fallback); popup still shows location metadata.
    minimal = bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
        "070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c"
        "231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b"
        "0c180d0d1832211c1c213232323232323232323232323232323232323232323232"
        "323232323232323232323232323232323232ffc000110800010001030111000211"
        "00031101ffc4001500010100000000000000000000000000000008ffc400141001"
        "00000000000000000000000000000000ffda000c03010002110311003f00bf8000"
        "ffd9"
    )
    with open(filename, "wb") as handle:
        handle.write(minimal)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        print(f"Missing CSV: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    use_pillow = False
    try:
        from PIL import Image  # noqa: F401

        use_pillow = True
    except ImportError:
        print("Pillow not installed — writing minimal JPEG placeholders.")

    created = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            image_name = row.get("Image", "").strip()
            if not image_name:
                continue
            safe_name = sanitize_filename(image_name)
            out_path = os.path.join(OUTPUT_DIR, safe_name)
            title = row.get("LocationName", "Survey site")
            if use_pillow:
                generate_with_pillow(out_path, title)
            else:
                generate_minimal_jpeg(out_path, title)
            created += 1

    print(f"Created {created} ground verification images in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
