"""
Neofetch-style info panel: a small hand-drawn "agent network" glyph on the
left (three nodes + edges, standing in for a distro logo) and key/value rows
on the right. Rows fade + slide up on a short stagger, then hold -- calmer
than the boot log next to it, since the boot log is the one bold move.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

BG = "#0a0d12"
BORDER = "#1c2230"
FG = "#c7cdd6"
DIM = "#5c6472"
KEY = "#5ad1e6"
ACCENT = "#ffb454"
OK = "#39d353"
FONT = "ui-monospace, 'Cascadia Code', 'SF Mono', Consolas, monospace"

WIDTH = 490
FONT_SIZE = 12.5
ROW_H = 19
LEFT_COL_W = 118
PAD_TOP = 30
PAD_LEFT = 20

ROWS = [
    ("os", "Agentic AI Runtime"),
    ("host", "Agenryx Labs (founder)"),
    ("kernel", "Python 3.11 \u00b7 FastAPI"),
    ("shell", "n8n \u00d7 LangChain \u00d7 OpenAI"),
    ("now", "Building AI agents, RAG systems & workflow automation"),
    ("focus", "RAG \u00b7 AI chatbots \u00b7 CRM automation \u00b7 SaaS MVPs"),
    ("stack", "OpenAI \u00b7 Supabase \u00b7 Next.js \u00b7 Flutter"),
    ("mail", "aly.haider069@gmail.com"),
    ("linked", "/in/ali-haider-300aab245"),
    ("social", "@aly.movs"),
]

PALETTE_STRIP = ["#0d1117", "#39d353", "#5ad1e6", "#ffb454", "#c7cdd6", "#e8e2d6"]


def glyph_svg(cx, cy, scale=1.0):
    """Three-node agent-network glyph: a small triangle of connected agents."""
    p1 = (cx, cy - 34 * scale)
    p2 = (cx - 30 * scale, cy + 20 * scale)
    p3 = (cx + 30 * scale, cy + 20 * scale)
    r = 7 * scale
    lines = []
    for a, b in [(p1, p2), (p2, p3), (p3, p1)]:
        lines.append(
            f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
            f'stroke="{DIM}" stroke-width="1.4"/>'
        )
    dots_colors = [ACCENT, KEY, OK]
    for (x, y), c in zip([p1, p2, p3], dots_colors):
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{BG}" stroke="{c}" stroke-width="1.6"/>')
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*0.4:.1f}" fill="{c}"/>')
    return "\n".join(lines)


def build():
    height = PAD_TOP + len(ROWS) * ROW_H + 54
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="14" '
                 f'fill="none" stroke="{BORDER}" stroke-width="1"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="26" rx="14" fill="#0d1117"/>')
    parts.append(f'<rect x="0.5" y="14" width="{WIDTH-1}" height="13" fill="#0d1117"/>')
    parts.append(f'<text x="16" y="18" fill="{DIM}" font-size="11">ali@github</text>')

    parts.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.5s" fill="freeze"/>')
    parts.append(glyph_svg(cx=62, cy=PAD_TOP + 46, scale=0.85))
    parts.append('</g>')
    parts.append(f'<text x="20" y="{PAD_TOP + 88}" fill="{DIM}" font-size="10">ali@github</text>')
    parts.append(f'<line x1="20" y1="{PAD_TOP + 96}" x2="104" y2="{PAD_TOP + 96}" stroke="{BORDER}" stroke-width="1"/>')

    text_left = PAD_LEFT + LEFT_COL_W
    stagger = 0.06
    for i, (key, val) in enumerate(ROWS):
        y = PAD_TOP + i * ROW_H + 10
        delay = 0.15 + i * stagger
        esc_val = val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        parts.append(
            f'<g opacity="0" transform="translate(0,6)">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 6" to="0 0" begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
            f'<text x="{text_left}" y="{y}" font-size="{FONT_SIZE}">'
            f'<tspan fill="{KEY}">{key}</tspan><tspan fill="{DIM}">:</tspan> '
            f'<tspan fill="{FG}">{esc_val}</tspan>'
            f'</text>'
            f'</g>'
        )

    strip_y = height - 26
    for i, c in enumerate(PALETTE_STRIP):
        x = PAD_LEFT + i * 16
        delay = 0.15 + len(ROWS) * stagger + 0.1
        parts.append(
            f'<rect x="{x}" y="{strip_y}" width="13" height="13" rx="3" fill="{c}" '
            f'stroke="{BORDER}" stroke-width="0.6" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay + i*0.03:.3f}s" dur="0.3s" fill="freeze"/>'
            f'</rect>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build()
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
