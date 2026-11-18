"""Builds assets/street-cred.svg from the public GitHub API (no third-party card service)."""
import json, os, sys, urllib.request, datetime
from collections import Counter

USER = os.environ.get("GH_USER", "Vishwanath-06")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = os.environ.get("OUT", "assets/street-cred.svg")

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "street-cred"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

try:
    user = get(f"https://api.github.com/users/{USER}")
    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = Counter(r["language"] for r in own if r["language"])
    top = langs.most_common(5)
    total = sum(c for _, c in top) or 1
    created = datetime.datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    days = (datetime.datetime.utcnow() - created).days
    rows = [("REPOS_INSTALLED", user["public_repos"]), ("STARS_EARNED", stars),
            ("FOLLOWERS", user["followers"]), ("DAYS_ON_THE_NET", days)]
    status = "SOURCE: GITHUB API"
except Exception as e:  # rate limit / offline: keep a previous card, else write a pending seed
    if os.path.exists(OUT):
        print("API unavailable, keeping existing card:", e)
        sys.exit(0)
    user = {"public_repos": "--", "followers": "--"}
    stars, top, total = "--", [], 1
    rows = [("REPOS_INSTALLED", "--"), ("STARS_EARNED", "--"), ("FOLLOWERS", "--"), ("DAYS_ON_THE_NET", "--")]
    status = "AWAITING FIRST SYNC"
PAL = ["FCEE0A", "00FFFF", "D92121", "FCEE0A", "00FFFF"]
F = "font-family=\"'Share Tech Mono','Courier New',monospace\""
D = 10

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;")

left = []
for i, (k, v) in enumerate(rows):
    y = 98 + i * 36
    s = .14 + i * .05
    left.append(f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{s:.2f};{s+.03:.2f};.94;1" dur="{D}s" repeatCount="indefinite"/>'
                f'<text x="36" y="{y}" font-size="14" fill="#00FFFF">{k}</text>'
                f'<text x="440" y="{y}" font-size="22" font-weight="700" fill="#FCEE0A" text-anchor="end">{esc(v)}</text>'
                f'<line x1="36" y1="{y+9}" x2="440" y2="{y+9}" stroke="#00FFFF" stroke-opacity=".25"/></g>')
right = []
for i, (name, c) in enumerate(top):
    y = 90 + i * 31
    pct = c / total
    w = max(8, round(pct * 250))
    s = .2 + i * .05
    col = PAL[i]
    right.append(f'<text x="540" y="{y+11}" font-size="13" fill="#{col}">{esc(name)}</text>'
                 f'<rect x="680" y="{y}" width="260" height="14" fill="none" stroke="#{col}" stroke-width="1.2"/>'
                 f'<rect x="683" y="{y+3}" width="0" height="8" fill="#{col}"><animate attributeName="width" values="0;0;{w};{w};0" keyTimes="0;{s:.2f};{s+.2:.2f};.94;1" dur="{D}s" repeatCount="indefinite"/></rect>'
                 f'<text x="956" y="{y+11}" font-size="12" fill="#FCEE0A" text-anchor="end">{round(pct*100)}%</text>')
if not top:
    right.append('<text x="540" y="110" font-size="13" fill="#00FFFF">AWAITING SYNC...</text>')
today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 260" width="1000" height="260" role="img" aria-label="Street cred for {USER}: {user["public_repos"]} repos, {stars} stars, {user["followers"]} followers">
<defs><pattern id="sc" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#00FFFF" opacity="0.06"/></pattern>
<pattern id="hh" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="10" fill="#D92121" opacity="0.25"/></pattern></defs>
<rect width="1000" height="260" fill="#050505"/><rect width="1000" height="260" fill="url(#sc)"/>
<polygon points="18,4 994,4 994,236 972,256 4,256 4,18" fill="none" stroke="#FCEE0A" stroke-width="2" stroke-dasharray="2400" stroke-dashoffset="2400"><animate attributeName="stroke-dashoffset" values="2400;0;0;2400" keyTimes="0;.1;.94;1" dur="{D}s" repeatCount="indefinite"/></polygon>
<g {F}>
<polygon points="14,14 270,14 284,30 284,44 14,44" fill="#FCEE0A"/>
<text x="26" y="35" font-size="15" font-weight="700" fill="#050505">NCPD // BOUNTY BOARD</text>
<polygon points="520,14 740,14 754,30 754,44 520,44" fill="#00FFFF"/>
<text x="532" y="35" font-size="15" font-weight="700" fill="#050505">CHROME_IN_USE</text>
<rect x="860" y="16" width="120" height="26" fill="url(#hh)"/>
<line x1="490" y1="60" x2="490" y2="230" stroke="#FCEE0A" stroke-opacity=".5" stroke-dasharray="4 6"/>
{''.join(left)}
{''.join(right)}
<text x="36" y="246" font-size="11" fill="#D92121">SYNCED {today} // {status}</text>
</g>
<rect x="4" y="4" width="992" height="2" fill="#00FFFF" opacity="0.18"><animate attributeName="y" values="4;250;4" dur="5s" repeatCount="indefinite"/></rect>
</svg>'''
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w").write(svg)
print("wrote", OUT, rows, top)
