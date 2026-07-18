"""
Render data/contributions.json into an animated SVG heatmap:
53 weeks x 7 days of rounded boxes, revealed column-by-column with a short
per-box stagger, then frozen (no infinite looping).
"""
import json
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#0d1117", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 34
TOP_PAD = 34
MONTH_LABEL_H = 18
FONT = "ui-monospace, 'Cascadia Code', 'SF Mono', Consolas, monospace"
BG = "#0a0d12"
FG = "#8b96a5"
ACCENT = "#ffb454"


def level_color(level: int) -> str:
    level = max(0, min(level, 4))
    return PALETTE[level]


def build_week_columns(days):
    """Group days into GitHub-style Sunday-start weeks, oldest -> newest."""
    by_date = {d["date"]: d["level"] for d in days}
    if not days:
        return []

    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()

    # Walk back from the most recent Saturday to build full weeks.
    end = last_date
    while end.weekday() != 5:  # Saturday = 5
        end += timedelta(days=1)
    start = end - timedelta(weeks=52, days=6)
    while start.weekday() != 6:  # Sunday = 6
        start += timedelta(days=1)

    weeks = []
    cursor = start
    while cursor <= end:
        week = []
        for _ in range(7):
            key = cursor.isoformat()
            level = by_date.get(key, 0) if cursor >= first_date else None
            week.append({"date": key, "level": level})
            cursor += timedelta(days=1)
        weeks.append(week)
    return weeks


def month_label_positions(weeks):
    labels = []
    seen_months = set()
    for i, week in enumerate(weeks):
        for day in week:
            if day["level"] is None:
                continue
            d = datetime.strptime(day["date"], "%Y-%m-%d").date()
            key = (d.year, d.month)
            if d.day <= 7 and key not in seen_months:
                seen_months.add(key)
                labels.append((i, d.strftime("%b")))
            break
    return labels


def render(payload):
    weeks = build_week_columns(payload["days"])
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * CELL + 16
    height = TOP_PAD + 7 * CELL + 46

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">'
    )
    parts.append(f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>')

    # subtle border
    parts.append(f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="14" '
                  f'fill="none" stroke="#1c2230" stroke-width="1"/>')

    # header line: fake shell prompt
    parts.append(
        f'<text x="16" y="20" fill="{ACCENT}" font-size="12">'
        f'<tspan fill="#5c6472">$</tspan> ./contributions.sh --user {payload["username"]}</text>'
    )

    # month labels
    for week_idx, label in month_label_positions(weeks):
        x = LEFT_PAD + week_idx * CELL
        parts.append(f'<text x="{x}" y="{TOP_PAD - 8}" fill="{FG}" font-size="9">{label}</text>')

    # day-of-week labels (Mon / Wed / Fri)
    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in dow_labels.items():
        y = TOP_PAD + row * CELL + BOX - 2
        parts.append(f'<text x="4" y="{y}" fill="{FG}" font-size="9">{label}</text>')

    # boxes, diagonal stagger: delay grows with (week_idx + row_idx)
    total_diag = n_weeks + 7
    max_delay = 1.6  # seconds for the whole reveal
    box_index = 0
    for week_idx, week in enumerate(weeks):
        x = LEFT_PAD + week_idx * CELL
        for row_idx, day in enumerate(week):
            if day["level"] is None:
                continue
            y = TOP_PAD + row_idx * CELL
            delay = (week_idx + row_idx) / total_diag * max_delay
            color = level_color(day["level"])
            title = f'{day["date"]}: level {day["level"]}'
            parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2.5" ry="2.5" '
                f'fill="{color}" opacity="0">'
                f'<title>{title}</title>'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="scale" '
                f'from="0.4" to="1" begin="{delay:.3f}s" dur="0.35s" '
                f'additive="sum" fill="freeze" '
                f'/>'
                f'</rect>'
            )
            box_index += 1

    # legend: Less -> More
    legend_y = height - 26
    legend_x = width - 16 - (5 * (BOX + 4)) - 62
    parts.append(f'<text x="{legend_x}" y="{legend_y + BOX - 2}" fill="{FG}" font-size="9">Less</text>')
    for i, color in enumerate(PALETTE):
        lx = legend_x + 30 + i * (BOX + 4)
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2.5" fill="{color}"/>')
    parts.append(
        f'<text x="{legend_x + 30 + 5 * (BOX + 4) + 6}" y="{legend_y + BOX - 2}" '
        f'fill="{FG}" font-size="9">More</text>'
    )

    # stats footer
    stats = (
        f'{payload["total_contributions"]:,} contributions in the last year  '
        f'\u00b7  current streak {payload["current_streak"]}d  '
        f'\u00b7  longest streak {payload["longest_streak"]}d'
    )
    parts.append(f'<text x="16" y="{height - 8}" fill="{ACCENT}" font-size="10">{stats}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    with open(DATA_PATH) as f:
        payload = json.load(f)
    svg = render(payload)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
