#!/usr/bin/env python3
"""
Fetch the public GitHub contribution calendar for one profile.

No GitHub token is required. The page is the same public contribution
endpoint GitHub uses for the profile calendar.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "contributions.json"

USERNAME = os.getenv("GH_PROFILE_USER", "shivenverma")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days() -> list[dict]:
    response = requests.get(
        URL,
        headers={"User-Agent": "shivenverma-profile-readme/1.0"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")

    if not cells:
        raise RuntimeError(
            "GitHub contribution cells were not found. "
            "GitHub may have changed its calendar markup."
        )

    days: list[dict] = []

    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        cell_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
        text = tooltip.get_text(" ", strip=True) if tooltip else ""

        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            match = re.match(r"(\d+)", text)
            count = int(match.group(1)) if match else 0

        days.append({"date": date, "count": count})

    if not days:
        raise RuntimeError("No contribution days were parsed.")

    days.sort(key=lambda item: item["date"])
    return days


def current_streak(days: list[dict]) -> int:
    index = len(days) - 1

    # Today may still be in progress, so do not break yesterday's streak
    # just because today's count is currently zero.
    if days[index]["count"] == 0:
        index -= 1

    streak = 0
    while index >= 0 and days[index]["count"] > 0:
        streak += 1
        index -= 1

    return streak


def longest_streak(days: list[dict]) -> int:
    best = run = 0
    for day in days:
        if day["count"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def build_data(days: list[dict]) -> dict:
    total = sum(item["count"] for item in days)
    active_days = sum(item["count"] > 0 for item in days)

    best_day = max(days, key=lambda item: item["count"])

    monthly: dict[str, int] = {}
    for item in days:
        month = item["date"][:7]
        monthly[month] = monthly.get(month, 0) + item["count"]

    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "range": {
            "start": days[0]["date"],
            "end": days[-1]["date"],
        },
        "total_contributions": total,
        "active_days": active_days,
        "current_streak": current_streak(days),
        "longest_streak": longest_streak(days),
        "best_day": best_day,
        "monthly": [
            {"month": month, "total": total}
            for month, total in sorted(monthly.items())
        ],
        "days": days,
    }


def main() -> None:
    days = fetch_days()
    data = build_data(days)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")

    print(
        f"{USERNAME}: {data['total_contributions']} contributions | "
        f"current streak {data['current_streak']} | "
        f"longest streak {data['longest_streak']}"
    )


if __name__ == "__main__":
    main()
