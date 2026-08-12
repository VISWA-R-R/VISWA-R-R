import os
import json
import urllib.request

USERNAME = "VISWA-R-R"
OUTPUT_FILE = "assets/github-streak.svg"

TOKEN = os.environ.get("GH_TOKEN")

if not TOKEN:
    raise RuntimeError("GH_TOKEN secret is missing.")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
          }
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": QUERY,
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
        "User-Agent": "github-streak-generator"
    },
    method="POST"
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

if "errors" in result:
    raise RuntimeError(json.dumps(result["errors"], indent=2))

calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

days = []

for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days.append({
            "date": day["date"],
            "count": day["contributionCount"]
        })

days.sort(key=lambda x: x["date"])

# Current streak
current_streak = 0

for day in reversed(days):
    if day["count"] > 0:
        current_streak += 1
    else:
        break

# Longest streak
longest_streak = 0
running = 0

for day in days:
    if day["count"] > 0:
        running += 1
        longest_streak = max(longest_streak, running)
    else:
        running = 0

total_contributions = calendar["totalContributions"]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="700"
height="230"
viewBox="0 0 700 230">

<rect
x="5"
y="5"
width="690"
height="220"
rx="18"
fill="#0d1117"
stroke="#30363d"
stroke-width="2"/>

<text
x="350"
y="45"
text-anchor="middle"
font-family="Arial"
font-size="25"
font-weight="bold"
fill="#ffffff">
GitHub Contribution Streak
</text>

<rect x="35" y="70" width="195" height="115" rx="14" fill="#21262d"/>
<rect x="252" y="70" width="195" height="115" rx="14" fill="#21262d"/>
<rect x="469" y="70" width="195" height="115" rx="14" fill="#21262d"/>

<text x="132" y="105"
text-anchor="middle"
font-family="Arial"
font-size="17"
fill="#8b949e">
Current Streak
</text>

<text x="132" y="145"
text-anchor="middle"
font-family="Arial"
font-size="34"
font-weight="bold"
fill="#58a6ff">
{current_streak}
</text>

<text x="132" y="170"
text-anchor="middle"
font-family="Arial"
font-size="14"
fill="#8b949e">
days
</text>

<text x="349" y="105"
text-anchor="middle"
font-family="Arial"
font-size="17"
fill="#8b949e">
Longest Streak
</text>

<text x="349" y="145"
text-anchor="middle"
font-family="Arial"
font-size="34"
font-weight="bold"
fill="#a371f7">
{longest_streak}
</text>

<text x="349" y="170"
text-anchor="middle"
font-family="Arial"
font-size="14"
fill="#8b949e">
days
</text>

<text x="566" y="105"
text-anchor="middle"
font-family="Arial"
font-size="17"
fill="#8b949e">
Contributions
</text>

<text x="566" y="145"
text-anchor="middle"
font-family="Arial"
font-size="34"
font-weight="bold"
fill="#3fb950">
{total_contributions}
</text>

<text x="566" y="170"
text-anchor="middle"
font-family="Arial"
font-size="14"
fill="#8b949e">
past year
</text>

<text x="350" y="210"
text-anchor="middle"
font-family="Arial"
font-size="12"
fill="#6e7681">
Updated automatically by GitHub Actions
</text>

</svg>
'''

os.makedirs("assets", exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(svg)

print("GitHub streak SVG generated successfully.")
print("Current streak:", current_streak)
print("Longest streak:", longest_streak)
print("Total contributions:", total_contributions)
