# Every colour literal inside the embed stylesheets on each in-scope page,
# checked against the dominant palette. Webflow's own site stylesheet is
# excluded: it is not part of this workstream and is not what "on dominant"
# was ever meant to cover.
import re, glob, os
from collections import Counter, defaultdict

DOMINANT = {
 '#1a2744':'navy','#2a3a5c':'navy-light','#3ba5a8':'teal','#e8f6f6':'teal-light',
 '#2d8a8d':'teal-dark','#f9f6f1':'warm','#f0ebe3':'warm-dark','#ffffff':'white',
 '#fff':'white','#2c2c2c':'text','#5a5a5a':'text-light','#8a8a8a':'text-muted',
 '#e8734a':'accent','#fef0eb':'accent-light','#e5e5e5':'border',
 '#db5b4f':'cta','#b34a40':'cta-hover',
 # derived in this workstream, documented in the audit
 '#b4dedf':'good-line','#e8beb8':'warn-line','#c9c9c9':'line-strong',
 # neutrals that are not palette decisions
 '#000':'black','#000000':'black',
}
BRAND = {'#186c78','#0e505c','#e3f1f3','#006078','#e1f0f2','#bf5247','#fbeae6',
         '#18313a','#5b6f76','#dce7e9','#eef4f5','#b6c9cd','#95a7ac','#c2e0e4','#f2cfc8'}

# Only the stylesheets this workstream owns: embed <style> blocks that scope to
# .mm-* or .mb-*. Webflow's compiled site CSS is a separate concern.
rows=[]
for f in sorted(glob.glob('*.html')):
    html=open(f).read()
    blocks=[b for b in re.findall(r'<style[^>]*>(.*?)</style>', html, re.S)
            if re.search(r'\.(mm|mb)-', b)]
    css=re.sub(r'/\*[\s\S]*?\*/',' ', '\n'.join(blocks))
    hexes=[h.lower() for h in re.findall(r'#[0-9a-fA-F]{3,8}\b', css)]
    off=Counter(h for h in hexes if h not in DOMINANT)
    brand=Counter(h for h in hexes if h in BRAND)
    rows.append((f[:-5], len(blocks), len(hexes), brand, off))

w=max(len(r[0]) for r in rows)
print(f"{'page'.ljust(w)}  blocks  colours  old-brand  off-palette")
for name,nb,nh,brand,off in rows:
    ob=sum(brand.values()); oo=sum(off.values())
    print(f"{name.ljust(w)}  {nb:>6}  {nh:>7}  {ob:>9}  {oo:>11}")

print("\n--- every off-dominant literal, by page ---")
for name,nb,nh,brand,off in rows:
    if off:
        print(f"{name}: " + ", ".join(f"{h}x{c}" for h,c in off.most_common()))
