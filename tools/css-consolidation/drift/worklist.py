import re, glob
from collections import defaultdict
DRIFT = {
 '#c64d42':'#b34a40',   # third button-hover red -> --cta-hover
 '#c45045':'#b34a40',   # fourth button-hover red -> --cta-hover
 '#e6e2da':'#e5e5e5',   # third rule tone -> --border
 '#f8f6f1':'#f9f6f1',   # one unit off --warm
 '#fdebe2':'#fef0eb',   # -> --accent-light
 '#eef0f4':'#e8f6f6',   # -> --teal-light
}
HOLD = {'#ff8c5a'}      # visible change, held for a separate decision
rows=defaultdict(lambda: defaultdict(int))
for f in sorted(glob.glob('*.html')):
    page=f[:-5]
    html=open(f).read()
    blocks=[(i,b) for i,b in enumerate(re.findall(r'<style[^>]*>(.*?)</style>', html, re.S))
            if re.search(r'\.(mm|mb)-', b)]
    for i,b in blocks:
        css=re.sub(r'/\*[\s\S]*?\*/',' ',b)
        for t in list(DRIFT)+list(HOLD):
            n=css.lower().count(t)
            if n: rows[page][(i,t)]=n
tot=0; held=0
for page in sorted(rows):
    parts=[]
    for (i,t),n in sorted(rows[page].items()):
        tag='HOLD' if t in HOLD else DRIFT[t]
        parts.append(f"block{i}:{t}x{n}->{tag}")
        if t in HOLD: held+=n
        else: tot+=n
    print(f"{page:32} {' | '.join(parts)}")
print(f"\nto change: {tot} occurrence(s);  held: {held} (#ff8c5a)")
print(f"pages needing an edit: {sum(1 for p in rows if any(t not in HOLD for _,t in rows[p]))}")
