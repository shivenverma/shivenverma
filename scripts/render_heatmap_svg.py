#!/usr/bin/env python3
"""
Render data/contributions.json into a GitHub-style animated SVG.

The animation is one-shot: cells slide in once when the SVG is loaded,
then remain in their final state.
"""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "assets" / "contrib-heatmap.svg"

# Tuned to match the dark terminal aesthetic of the hero.
PALETTE = [
    "#161b22",  # 0
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
    "#69f0a0",  # 5
]

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 24
LABEL_W = 34
TITLE_H = 30
MONTH_H = 22
FOOTER_H = 70

COL_DELAY = 0.018
ROW_DELAY = 0.045
CELL_DURATION = 0.42


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days: list[dict]) -> list[list[tuple | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    # GitHub's display is Sunday -> Saturday.
    lead = (first.weekday() + 1) % 7

    grid: list[list[tuple | None]] = []
    column: list[tuple | None] = [None] * lead

    for day in days:
        date = dt.date.fromisoformat(day["date"])
        weekday = (date.weekday() + 1) % 7

        while len(column) < weekday:
            column.append(None)

        column.append(
            (
                day["date"],
                day["count"],
                level_for(day["count"]),
            )
        )

        if len(column) == 7:
            grid.append(column)
            column = []

    if column:
        column.extend([None] * (7 - len(column)))
        grid.append(column)

    return grid


def render(data: dict) -> str:
    days = data["days"]
    grid = build_grid(days)

    n_cols = len(grid)
    grid_w = n_cols * STEP
    grid_h = 7 * STEP

    width = PAD + LABEL_W + grid_w + PAD
    height = TITLE_H + MONTH_H + grid_h + FOOTER_H + PAD

    css = f"""
    @keyframes heatmapCell {{
      0%   {{ opacity: 0; transform: translateY(-7px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
    .heat-cell {{
      opacity: 0;
      animation: heatmapCell {CELL_DURATION:.2f}s cubic-bezier(.2,.8,.2,1) both;
    }}
    """.strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
        f"<style>{css}</style>",
        f'<rect width="{width}" height="{height}" rx="14" fill="{BG}"/>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="14" '
        f'fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLE_H}" x2="{width}" y2="{TITLE_H}" stroke="{FRAME}"/>',
    ]

    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(
            f'<circle cx="{PAD + i * 16}" cy="{TITLE_H / 2}" r="5" fill="{color}"/>'
        )

    username = html.escape(data["username"])
    parts.append(
        f'<text x="{width / 2}" y="{TITLE_H / 2 + 4}" text-anchor="middle" '
        f'fill="{MUTED}" font-size="11">'
        f'{username}@github: ~$ ./contributions.sh</text>'
    )

    grid_top = TITLE_H + MONTH_H
    grid_left = PAD + LABEL_W

    # Month labels only on the first visible day of each month.
    seen: set[tuple[int, int]] = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = dt.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen and date.day <= 7:
                seen.add(key)
                x = grid_left + ci * STEP
                parts.append(
                    f'<text x="{x}" y="{TITLE_H + 15}" fill="{MUTED}" '
                    f'font-size="10">{date.strftime("%b")}</text>'
                )
            break

    for row_index, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + row_index * STEP + 10
        parts.append(
            f'<text x="{PAD}" y="{y}" fill="{MUTED}" font-size="9">{label}</text>'
        )

    for col_index, column in enumerate(grid):
        gx = grid_left + col_index * STEP

        for row_index, cell in enumerate(column):
            if cell is None:
                continue

            date_string, count, level = cell
            gy = grid_top + row_index * STEP
            delay = col_index * COL_DELAY + row_index * ROW_DELAY
            plural = "" if count == 1 else "s"
            title = html.escape(
                f"{date_string}: {count} contribution{plural}"
            )

            parts.append(
                f'<rect class="heat-cell" x="{gx}" y="{gy}" width="{CELL}" '
                f'height="{CELL}" rx="3" fill="{PALETTE[level]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f"<title>{title}</title></rect>"
            )

    # Legend.
    legend_y = grid_top + grid_h + 8
    legend_x = width - PAD - 170

    parts.append(
        f'<text x="{legend_x}" y="{legend_y + 10}" fill="{MUTED}" '
        f'font-size="10" text-anchor="end">Less</text>'
    )

    lx = legend_x + 10
    for color in PALETTE:
        parts.append(
            f'<rect x="{lx}" y="{legend_y}" width="11" height="11" rx="2.5" fill="{color}"/>'
        )
        lx += 14

    parts.append(
        f'<text x="{lx + 3}" y="{legend_y + 10}" fill="{MUTED}" '
        f'font-size="10">More</text>'
    )

    sep_y = legend_y + 25
    parts.append(
        f'<line x1="0" y1="{sep_y}" x2="{width}" y2="{sep_y}" stroke="{FRAME}"/>'
    )

    total = data["total_contributions"]
    current = data["current_streak"]
    longest = data["longest_streak"]
    best = data["best_day"]
    start = data["range"]["start"]
    end = data["range"]["end"]

    y1 = sep_y + 22
    y2 = y1 + 20

    parts.append(
        f'<text x="{PAD}" y="{y1}" fill="#39d353" font-size="13">'
        f'<tspan font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>'
    )
    parts.append(
        f'<text x="{width-PAD}" y="{y1}" text-anchor="end" fill="{MUTED}" '
        f'font-size="11">{start} → {end}</text>'
    )

    parts.append(
        f'<text x="{PAD}" y="{y2}" fill="{MUTED}" font-size="12">'
        f'current streak <tspan fill="#22d3ee" font-weight="700">{current} days</tspan>'
        f'<tspan fill="{MUTED}"> · longest </tspan>'
        f'<tspan fill="#22d3ee" font-weight="700">{longest} days</tspan></text>'
    )
    parts.append(
        f'<text x="{width-PAD}" y="{y2}" text-anchor="end" fill="{MUTED}" '
        f'font-size="11">best day <tspan fill="#f2cc60" font-weight="700">'
        f'{best["count"]}</tspan> on {html.escape(best["date"])}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    if not IN_PATH.exists():
        raise FileNotFoundError(
            f"{IN_PATH} not found. Run fetch_contributions.py first."
        )

    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(data), encoding="utf-8")

    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
