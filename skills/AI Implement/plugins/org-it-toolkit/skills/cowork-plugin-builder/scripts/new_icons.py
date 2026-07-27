#!/usr/bin/env python3
"""
Generate placeholder `color.png` (192x192) and `outline.png` (32x32) for a
Cowork plugin package.

Both icons are required at the plugin root by the manifest. This writes valid
PNGs using only the standard library - no Pillow needed.

  color.png    solid accent colour, opaque, 192x192
  outline.png  white glyph on transparency, 32x32

Usage
-----
    python3 new_icons.py --plugin-dir <folder> [--accent "#0078D4"]
"""

from __future__ import annotations

import argparse
import pathlib
import struct
import sys
import zlib


def write_png(path: pathlib.Path, width: int, height: int, pixels: bytes) -> None:
    """pixels must be RGBA, row-major, width*height*4 bytes."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)  # filter type 0 (None) for each scanline
        raw.extend(pixels[y * stride:(y + 1) * stride])

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def parse_hex(colour: str) -> tuple[int, int, int]:
    c = colour.lstrip("#")
    if len(c) != 6:
        sys.exit(f"ERROR: accent colour must be #RRGGBB, got: {colour}")
    try:
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except ValueError:
        sys.exit(f"ERROR: accent colour is not valid hex: {colour}")


def make_color_icon(path: pathlib.Path, accent: str, size: int = 192) -> None:
    r, g, b = parse_hex(accent)
    px = bytearray()
    cx = cy = size / 2
    radius = size * 0.34
    for y in range(size):
        for x in range(size):
            # simple filled circle so the icon does not look like a flat square
            inside = (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
            if inside:
                px += bytes((255, 255, 255, 255))
            else:
                px += bytes((r, g, b, 255))
    write_png(path, size, size, bytes(px))


def make_outline_icon(path: pathlib.Path, size: int = 32) -> None:
    px = bytearray()
    cx = cy = size / 2
    outer = size * 0.42
    inner = size * 0.28
    for y in range(size):
        for x in range(size):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            ring = inner ** 2 <= d2 <= outer ** 2
            px += bytes((255, 255, 255, 255)) if ring else bytes((0, 0, 0, 0))
    write_png(path, size, size, bytes(px))


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate placeholder plugin icons.")
    ap.add_argument("--plugin-dir", required=True, help="Path to the plugin folder")
    ap.add_argument("--accent", default="#0078D4", help="Accent colour, #RRGGBB")
    args = ap.parse_args()

    plugin_dir = pathlib.Path(args.plugin_dir).expanduser().resolve()
    if not plugin_dir.is_dir():
        sys.exit(f"ERROR: not a directory: {plugin_dir}")

    color_path = plugin_dir / "color.png"
    outline_path = plugin_dir / "outline.png"

    make_color_icon(color_path, args.accent)
    make_outline_icon(outline_path)

    print(f"wrote {color_path}  (192x192, accent {args.accent})")
    print(f"wrote {outline_path}  (32x32, white on transparent)")
    print("Replace these with real branded icons before shipping to a customer.")


if __name__ == "__main__":
    main()
