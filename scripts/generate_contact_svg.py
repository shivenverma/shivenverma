from pathlib import Path
import json, html

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/contact.json"
OUT=ROOT/"assets/contact.svg"
data=json.loads(DATA.read_text(encoding="utf-8"))

GITHUB_PATH='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.39 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .22.15.47.55.39A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z'
EMAIL_PATH='M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z'
ICON_MAP={
"github": f'<path d="{GITHUB_PATH}" fill="currentColor"/>',
"linkedin": '<rect x="1" y="1" width="14" height="14" rx="2.3" fill="currentColor"/><path d="M5.2 4.3a1.15 1.15 0 1 1-2.3 0 1.15 1.15 0 0 1 2.3 0zM3.1 6.3h2.1v5.9H3.1V6.3zm3.6 0h2v.8h.03c.28-.52.98-1.08 2.02-1.08 2.16 0 2.56 1.42 2.56 3.27v2.91h-2.1V9.62c0-.62-.01-1.42-.87-1.42-.87 0-1 .68-1 1.38v2.62h-2.1V6.3z" fill="#0a0e14"/>',
"email": f'<path d="{EMAIL_PATH}" fill="currentColor"/>'
}

W,H=1100,190
BG="#0a0e14"; FRAME="#30363d"; TEXT="#e6edf3"; MUTED="#8b949e"; GREEN="#39d353"
CW,CH=330,86
positions=[(45,62),(385,62),(725,62)]

p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
"""<style>@keyframes reveal{0%{opacity:0;transform:translateY(9px)}100%{opacity:1;transform:translateY(0)}}.card{opacity:0;animation:reveal .65s cubic-bezier(.2,.8,.2,1) both}@media(prefers-reduced-motion:reduce){.card{animation:none;opacity:1;transform:none}}</style>""",
f'<text x="{W/2}" y="27" text-anchor="middle" fill="{TEXT}" font-size="20" font-weight="700">shivenverma@github ~ $ ./connect.sh</text>']

for i,(item,(x,y)) in enumerate(zip(data["links"][:3],positions)):
    d=i*.12
    url=html.escape(item["url"],quote=True)
    icon=ICON_MAP[item["icon"]]
    p += [f'<a href="{url}"><g class="card" style="animation-delay:{d:.2f}s">',
          f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="11" fill="{BG}" stroke="{FRAME}"/>',
          f'<g transform="translate({x+18},{y+25}) scale(1.45)" color="{GREEN}">{icon}</g>',
          f'<text x="{x+53}" y="{y+30}" fill="{TEXT}" font-size="15" font-weight="700">{html.escape(item["name"])}</text>',
          f'<text x="{x+53}" y="{y+55}" fill="{MUTED}" font-size="10">{html.escape(item["label"])}</text>',
          f'<text x="{x+CW-18}" y="{y+34}" text-anchor="end" fill="{MUTED}" font-size="10">OPEN ↗</text>',
          '</g></a>']
p.append('</svg>')
OUT.parent.mkdir(exist_ok=True)
OUT.write_text("".join(p),encoding="utf-8")
print("Wrote",OUT)
