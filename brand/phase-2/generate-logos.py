"""Generate the Sāntvana concept logo suite as outlined SVG.

The wordmarks are shaped with HarfBuzz and converted to SVG paths with
fontTools, so the files do not depend on a viewer having the brand fonts.

Run from the repository root:
    python brand/phase-2/generate-logos.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "public" / "fonts"
OUT = Path(__file__).resolve().parent / "logos"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#171614"
PAPER = "#F5F1E8"

ARCHIVO = FONTS / "Archivo-Variable.ttf"
NOTO_SANS_DEVA = FONTS / "NotoSansDevanagari-Variable.ttf"


@dataclass
class ShapedText:
    """A shaped run of text in font units, ready to place in an SVG."""

    paths: list[str]
    width_units: float
    bbox_units: tuple[float, float, float, float]
    upem: int

    def at(self, x: float, baseline: float, size: float) -> str:
        scale = size / self.upem
        return (
            f'<g transform="translate({x:.2f} {baseline:.2f}) '
            f'scale({scale:.6f} {-scale:.6f})">'
            + "".join(self.paths)
            + "</g>"
        )

    def width(self, size: float) -> float:
        return self.width_units * size / self.upem

    def bbox(self, x: float, baseline: float, size: float) -> tuple[float, float, float, float]:
        scale = size / self.upem
        x0, y0, x1, y1 = self.bbox_units
        return (x + x0 * scale, baseline - y1 * scale, x + x1 * scale, baseline - y0 * scale)


def shape_text(
    font_path: Path,
    text: str,
    *,
    weight: int = 600,
    width: int = 100,
    tracking_em: float = 0.0,
) -> ShapedText:
    """Shape text with HarfBuzz and return SVG paths in font units."""
    blob = hb.Blob.from_file_path(str(font_path))
    face = hb.Face(blob)
    hb_font = hb.Font(face)
    hb_font.set_variations({"wght": weight, "wdth": width})

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf)

    tt = TTFont(str(font_path))
    glyph_set = tt.getGlyphSet()
    upem = tt["head"].unitsPerEm
    tracking = tracking_em * upem

    paths: list[str] = []
    pen_x = 0.0
    pen_y = 0.0
    bounds: list[float] | None = None

    for index, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        glyph_name = tt.getGlyphOrder()[info.codepoint]
        x = pen_x + pos.x_offset
        y = pen_y + pos.y_offset

        svg_pen = SVGPathPen(glyph_set)
        bounds_pen = BoundsPen(glyph_set)
        glyph_set[glyph_name].draw(TransformPen(svg_pen, (1, 0, 0, 1, x, y)))
        glyph_set[glyph_name].draw(TransformPen(bounds_pen, (1, 0, 0, 1, x, y)))

        d = svg_pen.getCommands()
        if d:
            paths.append(f'<path d="{d}"/>')

        if bounds_pen.bounds is not None:
            b = bounds_pen.bounds
            if bounds is None:
                bounds = list(b)
            else:
                bounds[0] = min(bounds[0], b[0])
                bounds[1] = min(bounds[1], b[1])
                bounds[2] = max(bounds[2], b[2])
                bounds[3] = max(bounds[3], b[3])

        pen_x += pos.x_advance
        pen_y += pos.y_advance
        if index < len(buf.glyph_infos) - 1:
            pen_x += tracking

    if bounds is None:
        bounds = [0.0, 0.0, 0.0, 0.0]

    return ShapedText(paths, pen_x, tuple(bounds), upem)  # type: ignore[arg-type]


def svg_document(
    viewbox: str,
    body: str,
    *,
    title: str,
    desc: str,
    width: str | None = None,
    height: str | None = None,
) -> str:
    size_attrs = ""
    if width:
        size_attrs += f' width="{width}"'
    if height:
        size_attrs += f' height="{height}"'
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"{size_attrs} role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  {body}
</svg>
'''


def symbol_svg(fill: str, bar: str) -> str:
    body = f'''<g fill="{fill}">
    <rect x="2" y="2" width="60" height="60" rx="16"/>
    <g fill="{bar}">
      <rect x="15" y="18" width="34" height="7" rx="3.5"/>
      <rect x="17" y="29" width="34" height="7" rx="3.5"/>
      <rect x="15" y="40" width="34" height="7" rx="3.5"/>
    </g>
  </g>'''
    return svg_document(
        "0 0 64 64",
        body,
        title="Sāntvana ground mark",
        desc="A rounded square containing three staggered tread bars. Concept mark; not for print.",
        width="64",
        height="64",
    )


def monogram_svg(fill: str, letter: str) -> str:
    s = shape_text(ARCHIVO, "S", weight=700, tracking_em=0)
    size = 46
    w = s.width(size)
    x0, y0, x1, y1 = s.bbox(0, 0, size)
    x = (64 - w) / 2 - x0
    baseline = (64 - (y1 - y0)) / 2 - y0
    body = f'''<g fill="{fill}">
    <rect x="2" y="2" width="60" height="60" rx="16"/>
    <g fill="{letter}">{s.at(x, baseline, size)}</g>
  </g>'''
    return svg_document(
        "0 0 64 64",
        body,
        title="Sāntvana S monogram",
        desc="A rounded square containing an S monogram for use below 20 px. Concept mark; not for print.",
        width="64",
        height="64",
    )


def wordmark_latin_svg(fill: str) -> str:
    text = shape_text(ARCHIVO, "Sāntvana", weight=600, tracking_em=-0.018)
    size = 120
    w = text.width(size)
    x0, y0, x1, y1 = text.bbox(0, 0, size)
    pad_x = 24
    pad_y = 22
    baseline = pad_y - y0
    vb_w = w + pad_x * 2
    vb_h = (y1 - y0) + pad_y * 2
    body = f'<g fill="{fill}">{text.at(pad_x - x0, baseline, size)}</g>'
    return svg_document(
        f"0 0 {vb_w:.0f} {vb_h:.0f}",
        body,
        title="Sāntvana Latin wordmark",
        desc="The Latin wordmark Sāntvana with a macron on the first a. Concept wordmark; not for print.",
    )


def wordmark_deva_svg(fill: str) -> str:
    text = shape_text(NOTO_SANS_DEVA, "सांत्वना", weight=600)
    size = 120
    w = text.width(size)
    x0, y0, x1, y1 = text.bbox(0, 0, size)
    pad_x = 24
    pad_y = 24
    baseline = pad_y - y0
    vb_w = w + pad_x * 2
    vb_h = (y1 - y0) + pad_y * 2
    body = f'<g fill="{fill}">{text.at(pad_x - x0, baseline, size)}</g>'
    return svg_document(
        f"0 0 {vb_w:.0f} {vb_h:.0f}",
        body,
        title="Sāntvana Devanagari wordmark",
        desc="The Devanagari wordmark सांत्वना in the selected anusvara form. Concept wordmark; not for print.",
    )


def horizontal_svg(fill: str, reverse: bool = False) -> str:
    latin = shape_text(ARCHIVO, "Sāntvana", weight=600, tracking_em=-0.018)
    deva = shape_text(NOTO_SANS_DEVA, "सांत्वना", weight=600)

    latin_size = 104
    deva_size = 66
    latin_w = latin.width(latin_size)
    deva_w = deva.width(deva_size)

    text_x = 208
    latin_baseline = 160
    deva_baseline = 232
    latin_bbox = latin.bbox(text_x, latin_baseline, latin_size)
    deva_bbox = deva.bbox(text_x, deva_baseline, deva_size)

    symbol_x = 40
    symbol_y = 100
    symbol_size = 120
    symbol_center_y = symbol_y + symbol_size / 2
    text_center_y = (latin_bbox[1] + deva_bbox[3]) / 2
    symbol_y += text_center_y - symbol_center_y

    vb_w = max(text_x + latin_w, text_x + deva_w) + 40
    vb_h = 320

    mark_fill = PAPER if reverse else INK
    bar_fill = INK if reverse else PAPER

    body = f'''<g fill="{fill}">
    <g transform="translate({symbol_x} {symbol_y}) scale({symbol_size / 64:.4f})">
      <rect x="2" y="2" width="60" height="60" rx="16" fill="{mark_fill}"/>
      <g fill="{bar_fill}">
        <rect x="15" y="18" width="34" height="7" rx="3.5"/>
        <rect x="17" y="29" width="34" height="7" rx="3.5"/>
        <rect x="15" y="40" width="34" height="7" rx="3.5"/>
      </g>
    </g>
    {latin.at(text_x, latin_baseline, latin_size)}
    {deva.at(text_x, deva_baseline, deva_size)}
  </g>'''

    return svg_document(
        f"0 0 {vb_w:.0f} {vb_h}",
        body,
        title="Sāntvana horizontal bilingual lockup",
        desc="Horizontal concept lockup: ground mark, Latin wordmark Sāntvana and Devanagari wordmark सांत्वना. Not for print.",
    )


def stacked_svg(fill: str, reverse: bool = False) -> str:
    latin = shape_text(ARCHIVO, "Sāntvana", weight=600, tracking_em=-0.018)
    deva = shape_text(NOTO_SANS_DEVA, "सांत्वना", weight=600)

    latin_size = 92
    deva_size = 58
    latin_w = latin.width(latin_size)
    deva_w = deva.width(deva_size)

    vb_w = 600
    symbol_size = 128
    symbol_x = (vb_w - symbol_size) / 2
    symbol_y = 40

    latin_baseline = 272
    deva_baseline = 354
    latin_x = (vb_w - latin_w) / 2
    deva_x = (vb_w - deva_w) / 2

    mark_fill = PAPER if reverse else INK
    bar_fill = INK if reverse else PAPER

    body = f'''<g fill="{fill}">
    <g transform="translate({symbol_x:.2f} {symbol_y}) scale({symbol_size / 64:.4f})">
      <rect x="2" y="2" width="60" height="60" rx="16" fill="{mark_fill}"/>
      <g fill="{bar_fill}">
        <rect x="15" y="18" width="34" height="7" rx="3.5"/>
        <rect x="17" y="29" width="34" height="7" rx="3.5"/>
        <rect x="15" y="40" width="34" height="7" rx="3.5"/>
      </g>
    </g>
    {latin.at(latin_x, latin_baseline, latin_size)}
    {deva.at(deva_x, deva_baseline, deva_size)}
  </g>'''

    return svg_document(
        "0 0 600 420",
        body,
        title="Sāntvana stacked bilingual lockup",
        desc="Stacked concept lockup: ground mark above the Latin wordmark Sāntvana, with the Devanagari wordmark सांत्वना below. Not for print.",
    )


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    files = {
        "santvana-horizontal.svg": horizontal_svg(INK),
        "santvana-horizontal-reverse.svg": horizontal_svg(PAPER, reverse=True),
        "santvana-stacked.svg": stacked_svg(INK),
        "santvana-stacked-reverse.svg": stacked_svg(PAPER, reverse=True),
        "santvana-wordmark-latin.svg": wordmark_latin_svg(INK),
        "santvana-wordmark-devanagari.svg": wordmark_deva_svg(INK),
        "santvana-symbol.svg": symbol_svg(INK, PAPER),
        "santvana-symbol-reverse.svg": symbol_svg(PAPER, INK),
        "santvana-monogram.svg": monogram_svg(INK, PAPER),
        "santvana-monogram-reverse.svg": monogram_svg(PAPER, INK),
    }
    for name, content in files.items():
        write(OUT / name, content)


if __name__ == "__main__":
    main()
