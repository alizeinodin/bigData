"""Render Persian text with Pango/Cairo (correct RTL shaping)."""

from __future__ import annotations

import io

import cairo
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

FONT_BOLD = "Vazir Bold"
FONT_REG = "Vazir"


def _render_block(
    text: str,
    width: int,
    font_desc: str,
    color: tuple[float, float, float],
) -> cairo.ImageSurface:
    probe = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, 10)
    pctx = cairo.Context(probe)
    layout = PangoCairo.create_layout(pctx)
    font = Pango.FontDescription(font_desc)
    layout.set_font_description(font)
    layout.set_text(text, -1)
    layout.set_alignment(Pango.Alignment.CENTER)
    layout.set_width(width * Pango.SCALE)
    layout.set_spacing(int(Pango.units_from_double(10)))
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)

    _, logical = layout.get_pixel_extents()
    height = max(logical.height + 28, 80)

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surf)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()

    layout = PangoCairo.create_layout(ctx)
    layout.set_font_description(font)
    layout.set_text(text, -1)
    layout.set_alignment(Pango.Alignment.CENTER)
    layout.set_width(width * Pango.SCALE)
    layout.set_spacing(int(Pango.units_from_double(10)))
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)

    ctx.set_source_rgb(*color)
    ctx.move_to(0, 10)
    PangoCairo.show_layout(ctx, layout)
    return surf


def render_text_png(
    text: str,
    width: int,
    font_size: int,
    bold: bool = False,
    color: tuple[float, float, float] = (1, 1, 1),
) -> bytes:
    family = FONT_BOLD if bold else FONT_REG
    surf = _render_block(text, width, f"{family} {font_size}", color)
    buf = io.BytesIO()
    surf.write_to_png(buf)
    return buf.getvalue()


def paste_text_on_image(
    base_rgba,
    text: str,
    y_center: int,
    font_size: int,
    bold: bool = False,
    color: tuple[float, float, float] = (1, 1, 1),
    x_center: int | None = None,
) -> None:
    from PIL import Image

    png_bytes = render_text_png(text, base_rgba.width, font_size, bold, color)
    overlay = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    cx = base_rgba.width // 2 if x_center is None else x_center
    x = cx - overlay.width // 2
    y = y_center - overlay.height // 2
    base_rgba.alpha_composite(overlay, (x, y))
