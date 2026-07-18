"""
Fetch real contribution-calendar data for a GitHub user, no token required.

GitHub serves the calendar as a public HTML fragment at:
    https://github.com/users/<username>/contributions
This is the same fragment the profile page itself renders, so we scrape and
parse it with BeautifulSoup instead of touching the GraphQL API.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "alyhaider096")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    resp = requests.get(URL.replace(USERNAME, username), headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    cells = soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day")

    if not cells:
        cells = soup.select("[data-date]")

    for cell in cells:
        date_str = cell.get("data-date")
        level = cell.get("data-level")
        if date_str is None:
            continue
        try:
            level = int(level) if level is not None else 0
        except ValueError:
            level = 0
        days.append({"date": date_str, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_streaks(days):
    """Return (current_streak, longest_streak, best_day)."""
    longest = current = 0
    running = 0
    best_day = {"date": None, "level": 0}

    for d in days:
        if d["level"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
        if d["level"] > best_day["level"]:
            best_day = {"date": d["date"], "level": d["level"]}

    for d in reversed(days):
        if d["level"] > 0:
            current += 1
        else:
            break

    return current, longest, best_day


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    html = fetch_html(username)
    days = parse_days(html)

    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(id="js-contribution-activity-description")
    total_text = re.sub(r"\s+", " ", heading.get_text()).strip() if heading else ""
    match = re.search(r"([\d,]+)\s+contributions", total_text)
    total_contributions = int(match.group(1).replace(",", "")) if match else sum(1 for d in days if d["level"] > 0)

    current_streak, longest_streak, best_day = compute_streaks(days)

    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {len(days)} days, {total_contributions} total contributions -> {OUT_PATH}")


if __name__ == "__main__":
    main()
