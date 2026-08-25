#!/usr/bin/env python3
"""
Render a GitHub contribution heatmap that closely matches the visual
proportions of Avi Vashishta's profile:

- no enclosing terminal/card border around the heatmap
- centered terminal prompt above
- large GitHub-like cells
- month labels across the top
- Mon/Wed/Fri labels on the left
- contribution total below
- slower one-shot reveal animation

Input:
    data/contributions.json

Output:
    assets/contrib-heatmap.svg
"""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "assets" / "contrib-heatmap.svg"

# Match the visual scale of the reference.
CELL = 15
GAP = 4
STEP = CELL + GAP

PAD_LEFT = 44
PAD_RIGHT = 28
LABEL_W = 28

TITLE_H = 34
MONTH_H = 22
GRID_TOP = TITLE_H + MONTH_H
GRID_H = 7 * STEP - GAP
FOOTER_H = 48
BOTTOM_PAD = 10

TEXT = "#e6edf3"
MUTED = "#8b949e"

PALETTE = [
    "#161b22",  # 0
    "#0e4429",  # 1
    "#006d32",  # 2
    "#26a641",  # 3
    "#39d353",  # 4
]

# Slower than the first version.
CELL_DURATION = 0.65
COL_DELAY = 0.045
ROW_DELAY = 0.08


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    return 4


def build_grid(days: list[dict]) -> list[list[tuple | None]]:
    first = dt.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7

    columns: list[list[tuple | None]] = []
    col: list[tuple | None] = [None] * lead

    for day in days:
        date = dt.date.fromisoformat(day["date"])
        weekday = (date.weekday() + 1) % 7

        while len(col) < weekday:
            col.append(None)

        col.append((day["date"], day["count"], level_for(day["count"])))

        if len(col) == 7:
            columns.append(col)
            col = []

    if col:
        col.extend([None] * (7 - len(col)))
        columns.append(col)

    return columns


def render(data: dict) -> str:
    grid = build_grid(data["days"])
    weeks = len(grid)

    grid_width = weeks * STEP - GAP
    width = PAD_LEFT + LABEL_W + grid_width + PAD_RIGHT
    height = GRID_TOP + GRID_H + FOOTER_H + BOTTOM_PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
        """<style>
        @keyframes heatReveal {
          0%   { opacity: 0; transform: translateY(-8px); }
          100% { opacity: 1; transform: translateY(0); }
        }

        .heat-cell {
          opacity: 0;
          transform-box: fill-box;
          transform-origin: center;
          animation-name: heatReveal;
          animation-duration: .65s;
          animation-timing-function: cubic-bezier(.2,.8,.2,1);
          animation-fill-mode: forwards;
        }

        @media (prefers-reduced-motion: reduce) {
          .heat-cell {
            animation: none;
            opacity: 1;
            transform: none;
          }
        }
        </style>""",
        f'<text x="{width/2}" y="25" text-anchor="middle" '
        f'fill="{TEXT}" font-size="20" font-weight="700">'
        f'<tspan fill="{TEXT}">{html.escape(data["username"])}</tspan>'
        f'<tspan fill="{TEXT}">@github ~ $ ./contributions.sh</tspan>'
        f'</text>',
    ]

    grid_left = PAD_LEFT + LABEL_W

    # Month labels.
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = dt.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                x = grid_left + ci * STEP
                parts.append(
                    f'<text x="{x}" y="{TITLE_H + 13}" '
                    f'fill="{MUTED}" font-size="12">{date.strftime("%b")}</text>'
                )
            break

    # GitHub-style weekday labels.
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = GRID_TOP + row * STEP + 11
        parts.append(
            f'<text x="{PAD_LEFT}" y="{y}" fill="{MUTED}" font-size="11">{label}</text>'
        )

    for ci, column in enumerate(grid):
        x = grid_left + ci * STEP

        for ri, cell in enumerate(column):
            if cell is None:
                continue

            date_str, count, level = cell
            y = GRID_TOP + ri * STEP
            delay = ci * COL_DELAY + ri * ROW_DELAY

            plural = "" if count == 1 else "s"
            tooltip = html.escape(
                f"{date_str}: {count} contribution{plural}"
            )

            parts.append(
                f'<rect class="heat-cell" x="{x}" y="{y}" '
                f'width="{CELL}" height="{CELL}" rx="3" '
                f'fill="{PALETTE[level]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>{tooltip}</title>'
                f'</rect>'
            )

    # Total, matching Avi's cleaner footer rather than our first verbose stats block.
    total_y = GRID_TOP + GRID_H + 28
    total = html.escape(f'{data["total_contributions"]:,}')
    parts.append(
        f'<text x="{grid_left}" y="{total_y}" fill="{TEXT}" '
        f'font-size="16" font-weight="700">'
        f'{total}<tspan dx="7" font-weight="400">contributions in the last year</tspan>'
        f'</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    if not IN_PATH.exists():
        raise FileNotFoundError(
            f"{IN_PATH} is missing. Run fetch_contributions.py first."
        )

    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(data), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
