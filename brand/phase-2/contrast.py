"""WCAG 2.2 contrast ratios for the Sāntvana concept palette.

Run from the repository root:
    python brand/phase-2/contrast.py

The output is the source of truth for the ratios quoted in colour.md and the
/brand route. It is a calculation, not a substitute for testing the final
rendered colours on the final display.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Colour:
    name: str
    hex: str


PALETTE = {
    "ink": Colour("Ink", "#171614"),
    "paper": Colour("Paper", "#F5F1E8"),
    "ground": Colour("Ground", "#2B2722"),
    "bone": Colour("Bone", "#EAE3D6"),
    "sand": Colour("Sand", "#D9CBB4"),
    "stone": Colour("Stone", "#8C8578"),
    "muted": Colour("Muted", "#6B655B"),
    "clay": Colour("Clay", "#A8452B"),
    "clay_hover": Colour("Clay hover", "#8F3A24"),
    "clay_pressed": Colour("Clay pressed", "#7A301D"),
    "clay_light": Colour("Clay light", "#D98B6F"),
    "moss": Colour("Moss", "#3E4A3A"),
    "moss_hover": Colour("Moss hover", "#323C2F"),
    "moss_light": Colour("Moss light", "#A8B5A0"),
    "slate": Colour("Slate", "#35424C"),
    "ochre": Colour("Ochre", "#946200"),
    "red": Colour("Red", "#A62B22"),
    "green": Colour("Green", "#2F6B4F"),
    "blue": Colour("Blue", "#2E5E7E"),
    "white": Colour("White", "#FFFFFF"),
}


def _channel(value: int) -> float:
    c = value / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_value: str) -> float:
    h = hex_value.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def ratio(a: Colour, b: Colour) -> float:
    la, lb = luminance(a.hex), luminance(b.hex)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def verdict(value: float, *, large: bool = False) -> str:
    threshold = 3.0 if large else 4.5
    return "PASS" if value >= threshold else "FAIL"


PAIRS = [
    ("Body text", "ink", "paper", False),
    ("Secondary text", "muted", "paper", False),
    ("Tertiary / large only", "stone", "paper", True),
    ("Ink on stone", "ink", "stone", False),
    ("Body text on dark", "paper", "ink", False),
    ("Secondary on dark", "sand", "ink", False),
    ("Muted on dark", "moss_light", "ink", False),
    ("Accent on dark", "clay_light", "ink", False),
    ("Clay on ink", "clay", "ink", True),
    ("Primary button label", "paper", "clay", False),
    ("Primary button hover", "paper", "clay_hover", False),
    ("Primary button pressed", "paper", "clay_pressed", False),
    ("Link on paper", "clay", "paper", False),
    ("Focus ring on paper", "clay", "paper", True),
    ("Border strong", "ink", "paper", True),
    ("Border subtle", "stone", "paper", True),
    ("Success text", "green", "paper", False),
    ("Warning text", "ochre", "paper", False),
    ("Error text", "red", "paper", False),
    ("Info text", "blue", "paper", False),
    ("Success fill label", "paper", "green", False),
    ("Warning fill label", "paper", "ochre", False),
    ("Error fill label", "paper", "red", False),
    ("Info fill label", "paper", "blue", False),
    ("Moss on paper", "moss", "paper", False),
    ("Slate on paper", "slate", "paper", False),
    ("Ink on bone", "ink", "bone", False),
    ("Muted on bone", "muted", "bone", False),
    ("Ink on sand", "ink", "sand", False),
    ("Muted on sand", "muted", "sand", False),
    ("Paper on moss", "paper", "moss", False),
    ("Paper on slate", "paper", "slate", False),
    ("Paper on ground", "paper", "ground", False),
]


def main() -> None:
    print("| Pair | Foreground | Background | Ratio | Normal text | Large / UI |")
    print("|---|---|---|---:|---|---|")
    for label, fg, bg, large in PAIRS:
        value = ratio(PALETTE[fg], PALETTE[bg])
        normal = verdict(value)
        large_v = verdict(value, large=True)
        print(
            f"| {label} | {PALETTE[fg].name} `{PALETTE[fg].hex}` | "
            f"{PALETTE[bg].name} `{PALETTE[bg].hex}` | {value:.2f}:1 | "
            f"{normal} | {large_v} |"
        )


if __name__ == "__main__":
    main()
