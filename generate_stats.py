# generate_stats.py
#
# FULLY AUTOMATIC:
# - Real GitHub contribution data
# - Current month wave graph
# - Current streak
# - Longest streak
# - Total contributions
# - Automatically updated by GitHub Actions
#
# NO streak-stats.vercel.app
# NO github-readme-activity-graph.vercel.app
# NO external image service
#
# Username: VISWA-R-R

import urllib.request
import json
import datetime
import os
import html

USERNAME = "VISWA-R-R"

GRAPH_FILE = "assets/contribution-wave.svg"
STREAK_FILE = "assets/github-streak.svg"

TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    raise Exception("GITHUB_TOKEN is missing.")

os.makedirs("assets", exist_ok=True)


# ============================================================
# GITHUB GRAPHQL API
# ============================================================

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": query,
    "variables": {
        "login": USERNAME
    }
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "VISWA-R-R-GitHub-Stats"
    },
    method="POST"
)

with urllib.request.urlopen(request, timeout=30) as response:
    result = json.loads(response.read().decode("utf-8"))


# ============================================================
# CHECK API RESPONSE
# ============================================================

if "errors" in result:
    raise Exception(
        "GitHub API Error: "
        + json.dumps(result["errors"])
    )

user = result.get("data", {}).get("user")

if not user:
    raise Exception(
        f"GitHub user '{USERNAME}' was not found."
    )

calendar = (
    user["contributionsCollection"]
    ["contributionCalendar"]
)

all_days = []

for week in calendar["weeks"]:
    for day in week["contributionDays"]:

        all_days.append({
            "date": datetime.date.fromisoformat(day["date"]),
            "count": day["contributionCount"]
        })


# ============================================================
# SORT DATA
# ============================================================

all_days.sort(key=lambda x: x["date"])

contribution_map = {
    item["date"]: item["count"]
    for item in all_days
}


# ============================================================
# CURRENT MONTH
# ============================================================

today = datetime.date.today()

first_day = today.replace(day=1)

if today.month == 12:
    next_month = datetime.date(
        today.year + 1,
        1,
        1
    )
else:
    next_month = datetime.date(
        today.year,
        today.month + 1,
        1
    )

last_day = next_month - datetime.timedelta(days=1)

month_days = []

current = first_day

while current <= today:

    month_days.append({
        "date": current,
        "count": contribution_map.get(
            current,
            0
        )
    })

    current += datetime.timedelta(days=1)


# ============================================================
# STREAK CALCULATION
# ============================================================

# Current streak
#
# If today has no contribution, check yesterday.
# This prevents the streak from incorrectly becoming zero
# before the day is over.

current_streak = 0

check_date = today

if contribution_map.get(today, 0) == 0:
    check_date = today - datetime.timedelta(days=1)

while contribution_map.get(check_date, 0) > 0:

    current_streak += 1

    check_date -= datetime.timedelta(days=1)


# ============================================================
# LONGEST STREAK
# ============================================================

longest_streak = 0
running_streak = 0

for item in all_days:

    if item["count"] > 0:

        running_streak += 1

        if running_streak > longest_streak:
            longest_streak = running_streak

    else:
        running_streak = 0


# ============================================================
# TOTAL CONTRIBUTIONS
# ============================================================

total_contributions = calendar["totalContributions"]

month_total = sum(
    item["count"]
    for item in month_days
)


# ============================================================
# CREATE MONTHLY WAVE GRAPH
# ============================================================

WIDTH = 1100
HEIGHT = 430

LEFT = 65
RIGHT = 35
TOP = 85
BOTTOM = 70

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM

values = [
    item["count"]
    for item in month_days
]

if not values:
    values = [0]

maximum = max(values)

if maximum <= 0:
    maximum = 1

graph_max = max(5, maximum + 2)


# ============================================================
# GRAPH POINTS
# ============================================================

points = []

for i, value in enumerate(values):

    if len(values) == 1:
        x = LEFT
    else:
        x = (
            LEFT
            + (i / (len(values) - 1))
            * GRAPH_WIDTH
        )

    y = (
        TOP
        + GRAPH_HEIGHT
        - (value / graph_max)
        * GRAPH_HEIGHT
    )

    points.append((x, y))


# ============================================================
# SMOOTH WAVE
# ============================================================

path = (
    f"M {points[0][0]:.2f} "
    f"{points[0][1]:.2f}"
)

for i in range(1, len(points)):

    x1, y1 = points[i - 1]
    x2, y2 = points[i]

    middle = (x1 + x2) / 2

    path += (
        f" C {middle:.2f} {y1:.2f},"
        f" {middle:.2f} {y2:.2f},"
        f" {x2:.2f} {y2:.2f}"
    )


# ============================================================
# GRAPH AREA
# ============================================================

bottom = TOP + GRAPH_HEIGHT

area_path = (
    path
    + f" L {points[-1][0]:.2f} {bottom}"
    + f" L {points[0][0]:.2f} {bottom}"
    + " Z"
)


# ============================================================
# SVG GRAPH
# ============================================================

svg = []

svg.append(
    '<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

svg.append(
    '<rect width="100%" height="100%" '
    'rx="16" fill="#0d1117"/>'
)


# Title

month_name = today.strftime("%B %Y")

svg.append(
    f'<text x="{WIDTH / 2}" y="38" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="24" '
    'font-weight="bold" '
    'fill="#58a6ff">'
    f"{USERNAME}'s Contribution Graph"
    '</text>'
)

svg.append(
    f'<text x="{WIDTH - RIGHT}" y="38" '
    'text-anchor="end" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    f'{html.escape(month_name)}'
    '</text>'
)


# ============================================================
# GRID
# ============================================================

for i in range(6):

    y = (
        TOP
        + GRAPH_HEIGHT
        - (i / 5)
        * GRAPH_HEIGHT
    )

    value = round(
        graph_max * i / 5
    )

    svg.append(
        f'<line x1="{LEFT}" y1="{y:.2f}" '
        f'x2="{WIDTH - RIGHT}" y2="{y:.2f}" '
        'stroke="#21262d" '
        'stroke-width="1"/>'
    )

    svg.append(
        f'<text x="{LEFT - 12}" '
        f'y="{y + 4:.2f}" '
        'text-anchor="end" '
        'font-family="Arial,sans-serif" '
        'font-size="11" '
        'fill="#8b949e">'
        f'{value}'
        '</text>'
    )


# ============================================================
# AREA
# ============================================================

svg.append(
    f'<path d="{area_path}" '
    'fill="#58a6ff" '
    'fill-opacity="0.12"/>'
)


# ============================================================
# WAVE
# ============================================================

svg.append(
    f'<path d="{path}" '
    'fill="none" '
    'stroke="#58a6ff" '
    'stroke-width="4" '
    'stroke-linecap="round" '
    'stroke-linejoin="round"/>'
)


# ============================================================
# POINTS
# ============================================================

for i, point in enumerate(points):

    x, y = point

    count = values[i]

    date_text = month_days[i]["date"].strftime(
        "%d %B %Y"
    )

    svg.append(
        f'<circle cx="{x:.2f}" '
        f'cy="{y:.2f}" '
        'r="5" '
        'fill="#ffffff" '
        'stroke="#58a6ff" '
        'stroke-width="2">'
        f'<title>{date_text}: '
        f'{count} contributions</title>'
        '</circle>'
    )


# ============================================================
# DATE LABELS
# ============================================================

for i, item in enumerate(month_days):

    date = item["date"]

    if date.day == 1 or date.day % 5 == 0:

        x = points[i][0]

        svg.append(
            f'<text x="{x:.2f}" '
            f'y="{HEIGHT - 30}" '
            'text-anchor="middle" '
            'font-family="Arial,sans-serif" '
            'font-size="12" '
            'fill="#8b949e">'
            f'{date.day}'
            '</text>'
        )


# ============================================================
# MONTH TOTAL
# ============================================================

svg.append(
    f'<text x="{LEFT}" '
    f'y="{HEIGHT - 30}" '
    'font-family="Arial,sans-serif" '
    'font-size="13" '
    'fill="#8b949e">'
    f'This month: {month_total} contributions'
    '</text>'
)

svg.append("</svg>")


with open(
    GRAPH_FILE,
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))


# ============================================================
# CREATE STREAK CARD
# ============================================================

STREAK_WIDTH = 850
STREAK_HEIGHT = 250

streak_svg = []

streak_svg.append(
    '<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{STREAK_WIDTH}" '
    f'height="{STREAK_HEIGHT}" '
    f'viewBox="0 0 {STREAK_WIDTH} {STREAK_HEIGHT}">'
)

streak_svg.append(
    '<rect width="100%" height="100%" '
    'rx="18" fill="#0d1117"/>'
)


# Title

streak_svg.append(
    f'<text x="{STREAK_WIDTH / 2}" y="42" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="23" '
    'font-weight="bold" '
    'fill="#58a6ff">'
    'GitHub Contribution Streak'
    '</text>'
)


# ============================================================
# CURRENT STREAK
# ============================================================

streak_svg.append(
    '<text x="215" y="95" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="48" '
    'font-weight="bold" '
    'fill="#ffffff">'
    f'{current_streak}'
    '</text>'
)

streak_svg.append(
    '<text x="215" y="125" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    'CURRENT STREAK'
    '</text>'
)


# ============================================================
# LONGEST STREAK
# ============================================================

streak_svg.append(
    '<text x="425" y="95" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="48" '
    'font-weight="bold" '
    'fill="#ffffff">'
    f'{longest_streak}'
    '</text>'
)

streak_svg.append(
    '<text x="425" y="125" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    'LONGEST STREAK'
    '</text>'
)


# ============================================================
# TOTAL
# ============================================================

streak_svg.append(
    '<text x="635" y="95" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="48" '
    'font-weight="bold" '
    'fill="#ffffff">'
    f'{total_contributions}'
    '</text>'
)

streak_svg.append(
    '<text x="635" y="125" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    'TOTAL CONTRIBUTIONS'
    '</text>'
)


# ============================================================
# BOTTOM TEXT
# ============================================================

streak_svg.append(
    '<text x="425" y="190" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#58a6ff">'
    f'{html.escape(USERNAME)} • Automatically Updated'
    '</text>'
)

streak_svg.append("</svg>")


with open(
    STREAK_FILE,
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(streak_svg))


# ============================================================
# FINISHED
# ============================================================

print("========================================")
print("GITHUB STATS UPDATED SUCCESSFULLY")
print("========================================")
print(f"Username              : {USERNAME}")
print(f"Current streak        : {current_streak}")
print(f"Longest streak        : {longest_streak}")
print(f"Total contributions   : {total_contributions}")
print(f"This month             : {month_total}")
print(f"Wave graph             : {GRAPH_FILE}")
print(f"Streak card            : {STREAK_FILE}")
print("========================================")
