import urllib.request
import json
import datetime
import os
import html

# ============================================================
# YOUR GITHUB PROFILE
# ============================================================

USERNAME = "VISWA-R-R"

# Your profile repository:
# https://github.com/VISWA-R-R/VISWA-R-R

# ============================================================
# GITHUB CONTRIBUTION API
# ============================================================

API_URL = (
    f"https://github-contributions-api.jogruber.de/v4/"
    f"{USERNAME}?y=last"
)

# This file must exist inside your profile repository
OUTPUT = "assets/github-contribution-graph.svg"

os.makedirs("assets", exist_ok=True)

# ============================================================
# GET GITHUB CONTRIBUTION DATA
# ============================================================

request = urllib.request.Request(
    API_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

except Exception as e:
    raise Exception(
        f"Could not get GitHub contribution data: {e}"
    )

contributions = data.get("contributions", [])

if not contributions:
    raise Exception(
        "No GitHub contribution data found."
    )

# ============================================================
# STORE CONTRIBUTIONS BY DATE
# ============================================================

contribution_map = {}

for item in contributions:

    date = item.get("date")
    count = item.get("count", 0)

    if date:
        contribution_map[date] = int(count)

# ============================================================
# LAST 365 DAYS
# ============================================================

today = datetime.date.today()

start_date = today - datetime.timedelta(days=364)

dates = []
values = []

current = start_date

while current <= today:

    dates.append(current)

    date_string = current.strftime("%Y-%m-%d")

    values.append(
        contribution_map.get(
            date_string,
            0
        )
    )

    current += datetime.timedelta(days=1)

# ============================================================
# GRAPH SIZE
# ============================================================

WIDTH = 1200
HEIGHT = 430

LEFT = 70
RIGHT = 35
TOP = 75
BOTTOM = 65

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM

# ============================================================
# MAXIMUM CONTRIBUTION
# ============================================================

max_value = max(values)

if max_value <= 0:
    max_value = 1

# Add headroom
graph_max = max_value * 1.20

# ============================================================
# CREATE GRAPH POINTS
# ============================================================

points = []

for i, value in enumerate(values):

    x = LEFT + (
        i / (len(values) - 1)
    ) * GRAPH_WIDTH

    y = (
        TOP
        + GRAPH_HEIGHT
        - (
            value / graph_max
        ) * GRAPH_HEIGHT
    )

    points.append(
        (x, y)
    )

# ============================================================
# CREATE SMOOTH WAVE
# ============================================================

path = ""

if points:

    path = (
        f"M {points[0][0]:.2f} "
        f"{points[0][1]:.2f}"
    )

    for i in range(1, len(points)):

        x1, y1 = points[i - 1]
        x2, y2 = points[i]

        midpoint = (
            x1 + x2
        ) / 2

        path += (
            f" C "
            f"{midpoint:.2f} {y1:.2f}, "
            f"{midpoint:.2f} {y2:.2f}, "
            f"{x2:.2f} {y2:.2f}"
        )

# ============================================================
# AREA BELOW WAVE
# ============================================================

bottom_y = TOP + GRAPH_HEIGHT

area_path = path

area_path += (
    f" L {points[-1][0]:.2f} {bottom_y:.2f}"
    f" L {points[0][0]:.2f} {bottom_y:.2f}"
    " Z"
)

# ============================================================
# START SVG
# ============================================================

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" '
    f'height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

# ============================================================
# BACKGROUND
# ============================================================

svg.append(
    '<rect '
    'width="100%" '
    'height="100%" '
    'rx="15" '
    'fill="#0d1117"/>'
)

# ============================================================
# TITLE
# ============================================================

svg.append(
    f'<text '
    f'x="{WIDTH / 2}" '
    'y="35" '
    'text-anchor="middle" '
    'font-family="Arial, sans-serif" '
    'font-size="22" '
    'font-weight="bold" '
    'fill="#58a6ff">'
    f'{html.escape(USERNAME)}\'s Contribution Graph'
    '</text>'
)

# ============================================================
# TOTAL CONTRIBUTIONS
# ============================================================

total = sum(values)

svg.append(
    f'<text '
    f'x="{WIDTH - RIGHT}" '
    'y="35" '
    'text-anchor="end" '
    'font-family="Arial, sans-serif" '
    'font-size="13" '
    'fill="#8b949e">'
    f'{total} contributions'
    '</text>'
)

# ============================================================
# GRID LINES
# ============================================================

GRID_LINES = 5

for i in range(GRID_LINES + 1):

    ratio = i / GRID_LINES

    y = (
        TOP
        + GRAPH_HEIGHT
        - ratio * GRAPH_HEIGHT
    )

    grid_value = round(
        graph_max * ratio
    )

    # Horizontal line
    svg.append(
        f'<line '
        f'x1="{LEFT}" '
        f'y1="{y:.2f}" '
        f'x2="{WIDTH - RIGHT}" '
        f'y2="{y:.2f}" '
        'stroke="#21262d" '
        'stroke-width="1"/>'
    )

    # Y-axis value
    svg.append(
        f'<text '
        f'x="{LEFT - 12}" '
        f'y="{y + 4:.2f}" '
        'text-anchor="end" '
        'font-family="Arial, sans-serif" '
        'font-size="11" '
        'fill="#8b949e">'
        f'{grid_value}'
        '</text>'
    )

# ============================================================
# AREA UNDER GRAPH
# ============================================================

svg.append(
    f'<path '
    f'd="{area_path}" '
    'fill="#58a6ff" '
    'fill-opacity="0.12" '
    'stroke="none"/>'
)

# ============================================================
# MAIN WAVE LINE
# ============================================================

svg.append(
    f'<path '
    f'd="{path}" '
    'fill="none" '
    'stroke="#58a6ff" '
    'stroke-width="4" '
    'stroke-linecap="round" '
    'stroke-linejoin="round"/>'
)

# ============================================================
# CONTRIBUTION POINTS
# ============================================================

for i, (x, y) in enumerate(points):

    value = values[i]

    if value > 0:

        date_text = dates[i].strftime(
            "%d %B %Y"
        )

        svg.append(
            f'<circle '
            f'cx="{x:.2f}" '
            f'cy="{y:.2f}" '
            'r="4" '
            'fill="#ffffff" '
            'stroke="#58a6ff" '
            'stroke-width="2">'
            f'<title>'
            f'{date_text}: '
            f'{value} contributions'
            f'</title>'
            '</circle>'
        )

# ============================================================
# MONTH LABELS
# ============================================================

last_month = None

for i, date in enumerate(dates):

    month = date.strftime("%b")

    if month != last_month:

        x = (
            LEFT
            + (
                i / (len(dates) - 1)
            ) * GRAPH_WIDTH
        )

        svg.append(
            f'<text '
            f'x="{x:.2f}" '
            f'y="{HEIGHT - 25}" '
            'font-family="Arial, sans-serif" '
            'font-size="12" '
            'fill="#8b949e">'
            f'{month}'
            '</text>'
        )

        last_month = month

# ============================================================
# X AXIS
# ============================================================

svg.append(
    f'<line '
    f'x1="{LEFT}" '
    f'y1="{TOP + GRAPH_HEIGHT}" '
    f'x2="{WIDTH - RIGHT}" '
    f'y2="{TOP + GRAPH_HEIGHT}" '
    'stroke="#30363d" '
    'stroke-width="1"/>'
)

# ============================================================
# DAYS LABEL
# ============================================================

svg.append(
    f'<text '
    f'x="{WIDTH / 2}" '
    f'y="{HEIGHT - 5}" '
    'text-anchor="middle" '
    'font-family="Arial, sans-serif" '
    'font-size="12" '
    'fill="#8b949e">'
    'Days'
    '</text>'
)

# ============================================================
# CLOSE SVG
# ============================================================

svg.append("</svg>")

# ============================================================
# SAVE GRAPH
# ============================================================

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(svg)
    )

print(
    "GitHub Contribution Wave Graph updated!"
)

print(
    f"Username: {USERNAME}"
)

print(
    f"Total contributions: {total}"
)

print(
    f"Graph saved to: {OUTPUT}"
)
