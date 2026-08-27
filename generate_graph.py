import urllib.request
import json
import datetime
import os
import html

USERNAME = "VISWA-R-R"
API_URL = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
OUTPUT = "assets/github-contribution-graph.svg"

os.makedirs("assets", exist_ok=True)

# ============================================================
# GET GITHUB CONTRIBUTIONS
# ============================================================

request = urllib.request.Request(
    API_URL,
    headers={"User-Agent": "GitHub-Wave-Graph"}
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.loads(response.read().decode("utf-8"))

contributions = data.get("contributions", [])

if not contributions:
    raise Exception("Unable to get GitHub contribution data.")

contribution_map = {
    item["date"]: item.get("count", 0)
    for item in contributions
    if item.get("date")
}

# ============================================================
# CURRENT MONTH ONLY
# ============================================================

today = datetime.date.today()

start_date = today.replace(day=1)

dates = []
values = []

current = start_date

while current <= today:
    dates.append(current)
    values.append(
        contribution_map.get(
            current.strftime("%Y-%m-%d"),
            0
        )
    )
    current += datetime.timedelta(days=1)

# ============================================================
# GRAPH SETTINGS
# ============================================================

WIDTH = 1000
HEIGHT = 420

LEFT = 65
RIGHT = 30
TOP = 75
BOTTOM = 65

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM

max_value = max(values) if values else 1

if max_value == 0:
    max_value = 1

# ============================================================
# CREATE WAVE POINTS
# ============================================================

points = []

for i, value in enumerate(values):

    if len(values) == 1:
        x = LEFT
    else:
        x = LEFT + (
            i / (len(values) - 1)
        ) * GRAPH_WIDTH

    y = TOP + GRAPH_HEIGHT - (
        value / max_value
    ) * GRAPH_HEIGHT

    points.append((x, y))

# ============================================================
# SMOOTH WAVE
# ============================================================

path = f"M {points[0][0]:.2f} {points[0][1]:.2f}"

for i in range(1, len(points)):

    x1, y1 = points[i - 1]
    x2, y2 = points[i]

    midpoint = (x1 + x2) / 2

    path += (
        f" C {midpoint:.2f} {y1:.2f}, "
        f"{midpoint:.2f} {y2:.2f}, "
        f"{x2:.2f} {y2:.2f}"
    )

# ============================================================
# AREA UNDER GRAPH
# ============================================================

bottom_y = TOP + GRAPH_HEIGHT

area_path = (
    path
    + f" L {points[-1][0]:.2f} {bottom_y}"
    + f" L {points[0][0]:.2f} {bottom_y}"
    + " Z"
)

# ============================================================
# SVG
# ============================================================

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

# Background
svg.append(
    '<rect width="100%" height="100%" '
    'rx="15" fill="#0d1117"/>'
)

# ============================================================
# TITLE
# ============================================================

month_name = today.strftime("%B %Y")

svg.append(
    f'<text x="{WIDTH / 2}" y="38" '
    'text-anchor="middle" '
    'font-family="Arial, sans-serif" '
    'font-size="24" '
    'font-weight="bold" '
    'fill="#58a6ff">'
    f'{html.escape(USERNAME)}\'s Contribution Graph'
    '</text>'
)

svg.append(
    f'<text x="{WIDTH - RIGHT}" y="38" '
    'text-anchor="end" '
    'font-family="Arial, sans-serif" '
    'font-size="14" '
    'fill="#8b949e">'
    f'{month_name}'
    '</text>'
)

# ============================================================
# GRID LINES
# ============================================================

grid_lines = 5

for i in range(grid_lines + 1):

    y = TOP + GRAPH_HEIGHT - (
        i / grid_lines
    ) * GRAPH_HEIGHT

    value = round(
        max_value * i / grid_lines
    )

    svg.append(
        f'<line x1="{LEFT}" y1="{y:.2f}" '
        f'x2="{WIDTH - RIGHT}" y2="{y:.2f}" '
        'stroke="#21262d" '
        'stroke-width="1"/>'
    )

    svg.append(
        f'<text x="{LEFT - 12}" y="{y + 4:.2f}" '
        'text-anchor="end" '
        'font-family="Arial, sans-serif" '
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
# WAVE LINE
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

for i, (x, y) in enumerate(points):

    count = values[i]

    svg.append(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" '
        'r="5" '
        'fill="#ffffff" '
        'stroke="#58a6ff" '
        'stroke-width="2">'
        f'<title>'
        f'{dates[i].strftime("%d %B %Y")}: '
        f'{count} contributions'
        f'</title>'
        '</circle>'
    )

# ============================================================
# DATE LABELS
# ============================================================

for i, date in enumerate(dates):

    # Show every 3 days to keep it clean
    if date.day == 1 or date.day % 3 == 0:

        x = points[i][0]

        svg.append(
            f'<text x="{x:.2f}" '
            f'y="{HEIGHT - 28}" '
            'text-anchor="middle" '
            'font-family="Arial, sans-serif" '
            'font-size="11" '
            'fill="#8b949e">'
            f'{date.day}'
            '</text>'
        )

# ============================================================
# TOTAL
# ============================================================

total = sum(values)

svg.append(
    f'<text x="{WIDTH - RIGHT}" '
    f'y="{HEIGHT - 28}" '
    'text-anchor="end" '
    'font-family="Arial, sans-serif" '
    'font-size="13" '
    'fill="#8b949e">'
    f'Total: {total}'
    '</text>'
)

svg.append("</svg>")

# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT,
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))

print(
    f"{month_name} contribution graph updated successfully!"
)
print(f"Total contributions this month: {total}")
