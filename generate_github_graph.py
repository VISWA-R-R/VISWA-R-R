import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape

USERNAME = "VISWA-R-R"
TOKEN = os.environ["GITHUB_TOKEN"]

today = datetime.now(timezone.utc).date()
start_date = today - timedelta(days=29)

query = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    contributionsCollection(from:$from, to:$to) {
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
        "login": USERNAME,
        "from": f"{start_date}T00:00:00Z",
        "to": f"{today}T23:59:59Z"
    }
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "GitHub-Contribution-Graph"
    },
    method="POST"
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

if "errors" in result:
    raise Exception(result["errors"])

weeks = result["data"]["user"]["contributionsCollection"][
    "contributionCalendar"
]["weeks"]

contributions = {}

for week in weeks:
    for day in week["contributionDays"]:
        contributions[day["date"]] = day["contributionCount"]

dates = []

for i in range(30):
    date = start_date + timedelta(days=i)

    dates.append({
        "date": date,
        "count": contributions.get(str(date), 0)
    })

# ---------------------------------------------------------
# SVG SETTINGS
# ---------------------------------------------------------

WIDTH = 1100
HEIGHT = 430

LEFT = 75
RIGHT = 35
TOP = 65
BOTTOM = 75

GRAPH_WIDTH = WIDTH - LEFT - RIGHT
GRAPH_HEIGHT = HEIGHT - TOP - BOTTOM

counts = [item["count"] for item in dates]

maximum = max(counts) if max(counts) > 0 else 5

# Round Y-axis maximum nicely
if maximum <= 5:
    y_max = 5
elif maximum <= 10:
    y_max = 10
elif maximum <= 20:
    y_max = 20
elif maximum <= 30:
    y_max = 30
elif maximum <= 50:
    y_max = 50
else:
    y_max = ((maximum + 9) // 10) * 10

# ---------------------------------------------------------
# POINTS
# ---------------------------------------------------------

points = []

for i, item in enumerate(dates):

    x = LEFT + (
        i / (len(dates) - 1)
    ) * GRAPH_WIDTH

    y = TOP + GRAPH_HEIGHT - (
        item["count"] / y_max
    ) * GRAPH_HEIGHT

    points.append((x, y))

line_points = " ".join(
    f"{x:.2f},{y:.2f}"
    for x, y in points
)

# ---------------------------------------------------------
# GRID
# ---------------------------------------------------------

grid = []

for i in range(6):

    value = (y_max / 5) * i

    y = TOP + GRAPH_HEIGHT - (
        i / 5
    ) * GRAPH_HEIGHT

    grid.append(
        f'''
        <line
            x1="{LEFT}"
            y1="{y:.2f}"
            x2="{LEFT + GRAPH_WIDTH}"
            y2="{y:.2f}"
            stroke="#40516f"
            stroke-width="1"
            opacity="0.65"
        />

        <text
            x="{LEFT - 15}"
            y="{y + 5:.2f}"
            text-anchor="end"
            fill="#9aa9c7"
            font-size="12"
            font-family="Arial"
        >
            {int(value)}
        </text>
        '''
    )

grid_svg = "\n".join(grid)

# ---------------------------------------------------------
# X AXIS LABELS
# ---------------------------------------------------------

x_labels = []

for i, item in enumerate(dates):

    x = LEFT + (
        i / (len(dates) - 1)
    ) * GRAPH_WIDTH

    day = item["date"].day

    x_labels.append(
        f'''
        <text
            x="{x:.2f}"
            y="{HEIGHT - 38}"
            text-anchor="middle"
            fill="#9aa9c7"
            font-size="11"
            font-family="Arial"
        >
            {day}
        </text>
        '''
    )

x_labels_svg = "\n".join(x_labels)

# ---------------------------------------------------------
# X AXIS
# ---------------------------------------------------------

axis = f'''
<line
    x1="{LEFT}"
    y1="{TOP + GRAPH_HEIGHT}"
    x2="{LEFT + GRAPH_WIDTH}"
    y2="{TOP + GRAPH_HEIGHT}"
    stroke="#6b7fa5"
    stroke-width="2"
/>
'''

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

title = f'''
<text
    x="{WIDTH / 2}"
    y="35"
    text-anchor="middle"
    fill="#58a6ff"
    font-size="20"
    font-weight="bold"
    font-family="Arial"
>
    {escape("Viswa R R's Contribution Graph")}
</text>
'''

# ---------------------------------------------------------
# Y AXIS TITLE
# ---------------------------------------------------------

y_title = f'''
<text
    x="18"
    y="{HEIGHT / 2}"
    transform="rotate(-90 18 {HEIGHT / 2})"
    text-anchor="middle"
    fill="#9aa9c7"
    font-size="13"
    font-family="Arial"
>
    Contributions
</text>
'''

# ---------------------------------------------------------
# X AXIS TITLE
# ---------------------------------------------------------

x_title = f'''
<text
    x="{WIDTH / 2}"
    y="{HEIGHT - 10}"
    text-anchor="middle"
    fill="#9aa9c7"
    font-size="13"
    font-family="Arial"
>
    Days
</text>
'''

# ---------------------------------------------------------
# AREA UNDER LINE
# ---------------------------------------------------------

area_points = (
    f"{LEFT},{TOP + GRAPH_HEIGHT} "
    + line_points
    + f" {LEFT + GRAPH_WIDTH},{TOP + GRAPH_HEIGHT}"
)

area = f'''
<polygon
    points="{area_points}"
    fill="#58a6ff"
    opacity="0.12"
/>
'''

# ---------------------------------------------------------
# LINE
# ---------------------------------------------------------

line = f'''
<polyline
    points="{line_points}"
    fill="none"
    stroke="#e6edf3"
    stroke-width="4"
    stroke-linecap="round"
    stroke-linejoin="round"
/>
'''

# ---------------------------------------------------------
# POINTS
# ---------------------------------------------------------

circles = []

for i, item in enumerate(dates):

    x, y = points[i]

    circles.append(
        f'''
        <circle
            cx="{x:.2f}"
            cy="{y:.2f}"
            r="4"
            fill="#58a6ff"
            stroke="#ffffff"
            stroke-width="2"
        />
        '''
    )

circles_svg = "\n".join(circles)

# ---------------------------------------------------------
# DATE RANGE
# ---------------------------------------------------------

date_range = f'''
<text
    x="{WIDTH - 35}"
    y="35"
    text-anchor="end"
    fill="#8b949e"
    font-size="12"
    font-family="Arial"
>
    {start_date.strftime("%d %b")} - {today.strftime("%d %b %Y")}
</text>
'''

# ---------------------------------------------------------
# SVG
# ---------------------------------------------------------

svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
>

<rect
    width="100%"
    height="100%"
    rx="14"
    fill="#161b22"
/>

{title}

{date_range}

{grid_svg}

{axis}

{area}

{line}

{circles_svg}

{x_labels_svg}

{y_title}

{x_title}

</svg>
'''

with open(
    "github-contribution-graph.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(svg)

print("GitHub contribution graph generated successfully.")
print("Username:", USERNAME)
print("Period:", start_date, "to", today)
print("Total contributions:", sum(counts))
