"""
The signature piece: a terminal boot log for an AI agent that "boots up"
into Ali Haider's profile. Each line types itself in left-to-right via an
animated clip-path wipe (a small cursor block rides the reveal edge), lines
are staggered top-to-bottom, and it ends with a permanently blinking cursor.
No JS, no external CSS -- pure SMIL inside the SVG, so it plays on GitHub.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "boot-agent.svg")

BG = "#0a0d12"
BORDER = "#1c2230"
FG = "#c7cdd6"
DIM = "#5c6472"
OK = "#39d353"       # reuse the heatmap green for status ticks -> visual thread between the two panels
ACCENT = "#ffb454"   # signature amber, carried over from the heatmap accent
CYAN = "#5ad1e6"
FONT = "ui-monospace, 'Cascadia Code', 'SF Mono', Consolas, monospace"

FONT_SIZE = 13
LINE_H = 21
CHAR_W = FONT_SIZE * 0.6
LEFT_PAD = 18
TOP_PAD = 40
WIDTH = 490

# Each line: list of (text, color) spans typed in sequence on that row.
LINES = [
    [("$ ", DIM), ("boot agent_core.sh --operator ali", FG)],
    [("[ok] ", OK), ("kernel  ", DIM), ("agentic-ai-runtime v3", FG)],
    [("[ok] ", OK), ("tools   ", DIM), ("n8n \u00b7 pipedrive \u00b7 gemini \u00b7 langgraph", FG)],
    [("[ok] ", OK), ("memory  ", DIM), ("rag index mounted, vector store online", FG)],
    [("[ok] ", OK), ("agents  ", DIM), ("lead-router, support-bot, booking-agent", FG)],
    [("[ok] ", OK), ("operator", DIM), (" ALI HAIDER", ACCENT)],
    [("[ok] ", OK), ("role    ", DIM), ("AI Automation & Agentic Systems Developer", FG)],
    [(">>> ", CYAN), ("status: ", DIM), ("ONLINE \u2014 accepting new missions_", ACCENT)],
]

TYPE_SPEED = 55  # chars per second
GAP_BETWEEN_LINES = 0.12


def line_text_len(spans):
    return sum(len(t) for t, _ in spans)


def build():
    height = TOP_PAD + len(LINES) * LINE_H + 22
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="14" '
                 f'fill="none" stroke="{BORDER}" stroke-width="1"/>')

    # title bar
    parts.append(f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="26" rx="14" fill="#0d1117"/>')
    parts.append(f'<rect x="0.5" y="14" width="{WIDTH-1}" height="13" fill="#0d1117"/>')
    parts.append(f'<text x="16" y="18" fill="{DIM}" font-size="11">agent_core \u2014 zsh</text>')

    t = 0.0
    for row, spans in enumerate(LINES):
        y = TOP_PAD + row * LINE_H
        full_text = "".join(t for t, _ in spans)
        n_chars = len(full_text)
        dur = max(n_chars / TYPE_SPEED, 0.25)
        begin = t
        end = begin + dur
        clip_id = f"clip{row}"
        full_w = n_chars * CHAR_W + 10

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'<rect x="0" y="{y - 13}" height="{LINE_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{full_w:.1f}" '
            f'begin="{begin:.3f}s" dur="{dur:.3f}s" fill="freeze" calcMode="linear"/>'
            f'</rect>'
        )
        parts.append('</clipPath>')

        # the typed text, revealed by the clip path
        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(f'<text x="{LEFT_PAD}" y="{y}" font-size="{FONT_SIZE}">')
        cx = LEFT_PAD
        for span_text, color in spans:
            esc = (span_text.replace("&", "&amp;").replace("<", "&lt;")
                   .replace(">", "&gt;"))
            parts.append(f'<tspan fill="{color}" xml:space="preserve">{esc}</tspan>')
        parts.append('</text>')
        parts.append('</g>')

        # cursor block riding the reveal edge, disappears once the line is done
        cursor_x0 = LEFT_PAD
        parts.append(
            f'<rect x="0" y="{y - 11}" width="7" height="{FONT_SIZE + 2}" fill="{ACCENT}" opacity="0.85">'
            f'<animate attributeName="x" from="{cursor_x0}" to="{cursor_x0 + full_w:.1f}" '
            f'begin="{begin:.3f}s" dur="{dur:.3f}s" fill="freeze" calcMode="linear"/>'
            f'<animate attributeName="opacity" from="0.85" to="0" '
            f'begin="{end:.3f}s" dur="0.08s" fill="freeze"/>'
            f'</rect>'
        )

        t = end + GAP_BETWEEN_LINES

    # final permanently-blinking cursor after the last line finishes
    last_y = TOP_PAD + (len(LINES) - 1) * LINE_H
    last_text_len = line_text_len(LINES[-1])
    blink_x = LEFT_PAD + last_text_len * CHAR_W + 4
    parts.append(
        f'<rect x="{blink_x:.1f}" y="{last_y - 11}" width="7" height="{FONT_SIZE + 2}" fill="{ACCENT}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;0.001;0.3;0.65;0.95;1" '
        f'begin="{t:.3f}s" dur="1.1s" repeatCount="indefinite"/>'
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
