# generate_graph.py

import urllib.request
import json
import datetime
import os
import html

USERNAME = "VISWA-R-R"

API_URL = (
    f"https://github-contributions-api.jogruber.de/v4/"
    f"{USERNAME}?y=last"
)

OUTPUT = "assets/github-contribution-graph.svg"

os.makedirs("assets", exist_ok=True)

# --------------------------------------------------
# Get GitHub contribution data
# --------------------------------------------------

request = urllib.request.Request(
    API_URL,
    headers={
        "User-Agent": "GitHub-Contribution-Graph"
    }
)

with urllib.request.urlopen(request, timeout=30) as response:
    data = json.loads(response.read().decode("utf-8"))

contributions = data.get("contributions", [])

if not contributions:
    raise Exception("Could not retrieve GitHub contribution data.")

# --------------------------------------------------
# Convert API data into date -> contribution count
# --------------------------------------------------

contribution_map = {}

for item in contributions:
    date = item.get("date")
    count = item.get("count", 0)

    if date:
        contribution_map[date] = count

# --------------------------------------------------
# Create last 365 days
# --------------------------------------------------

today = datetime.date.today()
start_date = today - datetime.timedelta(days=364)

dates = []

current = start_date

while current <= today:
    dates.append(current)
    current += datetime.timedelta(days=1)

# --------------------------------------------------
# GitHub-style contribution levels
# --------------------------------------------------

def get_level(count):
    if count == 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 5:
        return 2
    elif count <= 9:
        return 3
    else:
        return 4

# --------------------------------------------------
# SVG configuration
# --------------------------------------------------

CELL = 13
GAP = 3
STEP = CELL + GAP

LEFT = 45
TOP = 45

# Find Sunday before start date
first_date = dates[0]
first_sunday = first_date - datetime.timedelta(
    days=(first_date.weekday() + 1) % 7
)

last_date = dates[-1]
last_sunday = last_date - datetime.timedelta(
    days=(last_date.weekday() + 1) % 7
)

weeks = ((last_sunday - first_sunday).days // 7) + 1

WIDTH = LEFT + weeks * STEP + 20
HEIGHT = TOP + 7 * STEP + 40

# --------------------------------------------------
# Colors
# --------------------------------------------------

colors = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353"
}

# --------------------------------------------------
# Start SVG
# --------------------------------------------------

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{WIDTH}" height="{HEIGHT}" '
    f'viewBox="0 0 {WIDTH} {HEIGHT}">'
)

svg.append(
    '<rect width="100%" height="100%" fill="#0d1117" rx="10"/>'
)

# --------------------------------------------------
# Title
# --------------------------------------------------

svg.append(
    '<text x="20" y="25" '
    'font-family="Arial, sans-serif" '
    'font-size="15" font-weight="bold" '
    'fill="#58a6ff">'
    f'{html.escape(USERNAME)} Contribution Graph'
    '</text>'
)

# --------------------------------------------------
# Day labels
# --------------------------------------------------

day_labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri"
}

for row, label in day_labels.items():
    y = TOP + row * STEP + 10

    svg.append(
        f'<text x="5" y="{y}" '
        'font-family="Arial, sans-serif" '
        'font-size="9" fill="#8b949e">'
        f'{label}</text>'
    )

# --------------------------------------------------
# Draw contribution cells
# --------------------------------------------------

date = first_sunday

while date <= last_date:

    week = (date - first_sunday).days // 7
    row = (date - first_sunday).days % 7

    count = contribution_map.get(
        date.strftime("%Y-%m-%d"),
        0
    )

    level = get_level(count)

    x = LEFT + week * STEP
    y = TOP + row * STEP

    safe_date = html.escape(date.strftime("%Y-%m-%d"))

    svg.append(
        f'<rect x="{x}" y="{y}" '
        f'width="{CELL}" height="{CELL}" '
        f'rx="2" '
        f'fill="{colors[level]}">'
        f'<title>{safe_date}: {count} contributions</title>'
        f'</rect>'
    )

    date += datetime.timedelta(days=1)

# --------------------------------------------------
# Legend
# --------------------------------------------------

legend_y = HEIGHT - 25

svg.append(
    f'<text x="{LEFT}" y="{legend_y + 10}" '
    'font-family="Arial, sans-serif" '
    'font-size="9" fill="#8b949e">'
    'Less'
    '</text>'
)

for i in range(5):

    x = LEFT + 30 + i * 18

    svg.append(
        f'<rect x="{x}" y="{legend_y}" '
        f'width="12" height="12" rx="2" '
        f'fill="{colors[i]}"/>'
    )

svg.append(
    f'<text x="{LEFT + 125}" y="{legend_y + 10}" '
    'font-family="Arial, sans-serif" '
    'font-size="9" fill="#8b949e">'
    'More'
    '</text>'
)

# --------------------------------------------------
# Close SVG
# --------------------------------------------------

svg.append("</svg>")

# --------------------------------------------------
# Save
# --------------------------------------------------

with open(OUTPUT, "w", encoding="utf-8") as file:
    file.write("\n".join(svg))

print("Contribution graph updated successfully.")
print(f"Output: {OUTPUT}")
