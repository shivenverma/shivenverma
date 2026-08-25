from pathlib import Path
import json,html

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"data/contact.json").read_text(encoding="utf-8"))
out=ROOT/"assets/contact.svg"

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
    p += [
      f'<a href="{url}"><g class="card" style="animation-delay:{d:.2f}s">',
      f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="11" fill="{BG}" stroke="{FRAME}"/>',
      f'<text x="{x+18}" y="{y+34}" fill="{GREEN}" font-size="17" font-weight="700">{html.escape(item["icon"])}</text>',
      f'<text x="{x+53}" y="{y+30}" fill="{TEXT}" font-size="15" font-weight="700">{html.escape(item["name"])}</text>',
      f'<text x="{x+53}" y="{y+55}" fill="{MUTED}" font-size="10">{html.escape(item["label"])}</text>',
      f'<text x="{x+CW-18}" y="{y+34}" text-anchor="end" fill="{MUTED}" font-size="10">OPEN ↗</text>',
      '</g></a>'
    ]
p.append('</svg>')
out.parent.mkdir(exist_ok=True)
out.write_text("".join(p),encoding="utf-8")
print("Wrote",out)
