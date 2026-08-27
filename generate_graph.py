# generate_graph.py
# THIS VERSION SHOWS ONLY THE CURRENT MONTH.
# Example: August 2026 -> only August 1 to August 27/31.

import urllib.request
import json
import datetime
import os
import html

USERNAME = "VISWA-R-R"
OUTPUT = "assets/github-contribution-graph.svg"

os.makedirs("assets", exist_ok=True)

# ------------------------------------------------------------
# GET GITHUB DATA
# ------------------------------------------------------------

url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"

request = urllib.request.Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.loads(response.read().decode("utf-8"))

contributions = data.get("contributions", [])

if not contributions:
    raise Exception("GitHub contribution data could not be loaded.")

# ------------------------------------------------------------
# SAVE CONTRIBUTIONS
# ------------------------------------------------------------

contribution_map = {}

for item in contributions:
    contribution_map[item["date"]] = item.get("count", 0)

# ------------------------------------------------------------
# CURRENT MONTH ONLY
# ------------------------------------------------------------

today = datetime.date.today()

first_day = today.replace(day=1)

# Last day of current month
if today.month == 12:
    next_month = datetime.date(today.year + 1, 1, 1)
else:
    next_month = datetime.date(today.year, today.month + 1, 1)

last_day = next_month - datetime.timedelta(days=1)

# IMPORTANT:
# Only dates from the CURRENT MONTH are added.
dates = []
values = []

current = first_day

while current <= min(today, last_day):

    date_string = current.strftime("%Y-%m-%d")

    dates.append(current)

    values.append(
        contribution_map.get(date_string, 0)
    )

    current += datetime.timedelta(days=1)

# ------------------------------------------------------------
# GRAPH SIZE
# ------------------------------------------------------------

WIDTH = 1100
HEIGHT = 430

LEFT = 65
RIGHT = 35
TOP = 80
BOTTOM = 70

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM

# ------------------------------------------------------------
# MAX VALUE
# ------------------------------------------------------------

maximum = max(values) if values else 1

if maximum <= 0:
    maximum = 1

# Give graph some headroom
graph_max = max(5, maximum + 2)

# ------------------------------------------------------------
# CREATE POINTS
# ------------------------------------------------------------

points = []

for i, value in enumerate(values):

    if len(values) == 1:
        x = LEFT
    else:
        x = LEFT + (
            i / (len(values) - 1)
        ) * GRAPH_WIDTH

    y = (
        TOP
        + GRAPH_HEIGHT
        - (value / graph_max) * GRAPH_HEIGHT
    )

    points.append((x, y))

# ------------------------------------------------------------
# CREATE WAVE
# ------------------------------------------------------------

path = ""

if points:

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

# ------------------------------------------------------------
# AREA
# ------------------------------------------------------------

bottom = TOP + GRAPH_HEIGHT

area_path = (
    path
    + f" L {points[-1][0]:.2f} {bottom}"
    + f" L {points[0][0]:.2f} {bottom}"
    + " Z"
)

# ------------------------------------------------------------
# SVG
# ------------------------------------------------------------

svg = []

svg.append(
    '<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

# Background
svg.append(
    '<rect width="100%" height="100%" '
    'rx="15" fill="#0d1117"/>'
)

# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------

month_name = today.strftime("%B %Y")

svg.append(
    f'<text x="{WIDTH / 2}" y="38" '
    'text-anchor="middle" '
    'font-family="Arial,sans-serif" '
    'font-size="24" '
    'font-weight="bold" '
    'fill="#58a6ff">'
    f'{USERNAME} Contribution Graph'
    '</text>'
)

svg.append(
    f'<text x="{WIDTH - RIGHT}" y="38" '
    'text-anchor="end" '
    'font-family="Arial,sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    f'{month_name}'
    '</text>'
)

# ------------------------------------------------------------
# GRID
# ------------------------------------------------------------

for i in range(6):

    y = (
        TOP
        + GRAPH_HEIGHT
        - (i / 5) * GRAPH_HEIGHT
    )

    value = round(
        graph_max * i / 5
    )

    svg.append(
        f'<line x1="{LEFT}" y1="{y:.2f}" '
        f'x2="{WIDTH - RIGHT}" y2="{y:.2f}" '
        'stroke="#21262d" stroke-width="1"/>'
    )

    svg.append(
        f'<text x="{LEFT - 12}" y="{y + 4:.2f}" '
        'text-anchor="end" '
        'font-family="Arial,sans-serif" '
        'font-size="11" '
        'fill="#8b949e">'
        f'{value}'
        '</text>'
    )

# ------------------------------------------------------------
# AREA
# ------------------------------------------------------------

svg.append(
    f'<path d="{area_path}" '
    'fill="#58a6ff" '
    'fill-opacity="0.12"/>'
)

# ------------------------------------------------------------
# WAVE LINE
# ------------------------------------------------------------

svg.append(
    f'<path d="{path}" '
    'fill="none" '
    'stroke="#58a6ff" '
    'stroke-width="4" '
    'stroke-linecap="round" '
    'stroke-linejoin="round"/>'
)

# ------------------------------------------------------------
# POINTS
# ------------------------------------------------------------

for i, point in enumerate(points):

    x, y = point
    count = values[i]

    svg.append(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" '
        'fill="#ffffff" '
        'stroke="#58a6ff" '
        'stroke-width="2">'
        f'<title>'
        f'{dates[i].strftime("%d %B %Y")} - '
        f'{count} contributions'
        f'</title>'
        '</circle>'
    )

# ------------------------------------------------------------
# DAY NUMBERS
# ------------------------------------------------------------

for i, date in enumerate(dates):

    # Show 1, 5, 10, 15, 20, 25, etc.
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

# ------------------------------------------------------------
# TOTAL
# ------------------------------------------------------------

total = sum(values)

svg.append(
    f'<text x="{LEFT}" y="{HEIGHT - 30}" '
    'font-family="Arial,sans-serif" '
    'font-size="13" '
    'fill="#8b949e">'
    f'Total this month: {total}'
    '</text>'
)

svg.append("</svg>")

# ------------------------------------------------------------
# WRITE FILE
# ------------------------------------------------------------

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))

print("======================================")
print("MONTHLY GRAPH UPDATED")
print("======================================")
print(f"User: {USERNAME}")
print(f"Month: {month_name}")
print(f"Days displayed: {len(dates)}")
print(f"Contributions: {total}")
print(f"File: {OUTPUT}")
print("======================================")
