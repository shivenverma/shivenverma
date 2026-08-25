from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[1]
d=json.loads((R/"data/roadmap.json").read_text())
W,H=1100,500
BG="#0a0e14"; FRAME="#30363d"; TEXT="#e6edf3"; MUTED="#8b949e"; GREEN="#39d353"; YELLOW="#d29922"; TRACK="#21262d"
CW,CH=480,72; LX,RX=45,575; TOP,RH=72,82; BW,BH=205,8
def sc(s): return GREEN if s=="ACTIVE" else YELLOW if s=="BUILDING" else MUTED
p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace">',
"""<style>@keyframes r{0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}}@keyframes f{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}.row{opacity:0;animation:r .65s cubic-bezier(.2,.8,.2,1) both}.bar{transform-box:fill-box;transform-origin:left center;animation:f .9s cubic-bezier(.2,.8,.2,1) both}@media(prefers-reduced-motion:reduce){.row,.bar{animation:none;opacity:1;transform:none}}</style>""",
f'<text x="{W/2}" y="27" text-anchor="middle" fill="{TEXT}" font-size="20" font-weight="700">shivenverma@github ~ $ ./roadmap.sh</text>',
f'<text x="{LX}" y="57" fill="{TEXT}" font-size="11" font-weight="700">CURRENTLY BUILDING</text>']
items=d["current"]
for i,item in enumerate(items):
    col=0 if i<4 else 1; r=i if i<4 else i-4; x=LX if col==0 else RX; y=TOP+r*RH; delay=i*.1; lev=max(1,min(5,int(item["level"]))); frac=lev/5; status=item["status"].upper()
    p += [f'<g class="row" style="animation-delay:{delay:.2f}s">',
          f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="10" fill="{BG}" stroke="{FRAME}"/>',
          f'<text x="{x+16}" y="{y+24}" fill="{TEXT}" font-size="15" font-weight="700">{html.escape(item["icon"])}  {html.escape(item["name"])}</text>',
          f'<text x="{x+CW-16}" y="{y+24}" text-anchor="end" fill="{sc(status)}" font-size="9" font-weight="700">{status}</text>',
          f'<text x="{x+16}" y="{y+44}" fill="{MUTED}" font-size="10">{html.escape(item["description"])}</text>',
          f'<rect x="{x+16}" y="{y+57}" width="{BW}" height="{BH}" rx="4" fill="{TRACK}"/>',
          f'<rect class="bar" x="{x+16}" y="{y+57}" width="{BW*frac:.1f}" height="{BH}" rx="4" fill="{GREEN}" style="animation-delay:{delay+.18:.2f}s"/>',
          f'<text x="{x+16+BW+10}" y="{y+65}" fill="{MUTED}" font-size="9">{lev}/5</text></g>']
uy=TOP+4*RH+20
p.append(f'<text x="{LX}" y="{uy}" fill="{TEXT}" font-size="11" font-weight="700">UP NEXT</text>')
for i,item in enumerate(d["up_next"][:4]):
    col=i%2; row=i//2; x=LX+col*530; y=uy+15+row*48; delay=.9+i*.12
    p += [f'<g class="row" style="animation-delay:{delay:.2f}s">',
          f'<rect x="{x}" y="{y}" width="500" height="38" rx="9" fill="{BG}" stroke="{FRAME}"/>',
          f'<text x="{x+14}" y="{y+24}" fill="{TEXT}" font-size="12">{html.escape(item["icon"])}  {html.escape(item["name"])}</text>',
          f'<text x="{x+180}" y="{y+24}" fill="{MUTED}" font-size="9">{html.escape(item["description"])}</text></g>']
p += [f'<text x="{LX}" y="{H-14}" fill="{MUTED}" font-size="9">Level 5 = actively building · Level 1 = just starting · edit data/roadmap.json to update</text></svg>']
(R/"assets").mkdir(exist_ok=True)
(R/"assets/roadmap.svg").write_text("".join(p),encoding="utf-8")
print("Wrote assets/roadmap.svg")
