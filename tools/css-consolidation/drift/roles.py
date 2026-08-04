import re, glob
from collections import defaultdict
TARGETS=['#c64d42','#c45045','#e6e2da','#ff8c5a','#f8f6f1','#002833','#34abc7','#fdebe2','#eef0f4','#f7f6f5','#fbf9f9']
seen=defaultdict(set)
for f in sorted(glob.glob('*.html')):
    html=open(f).read()
    blocks=[b for b in re.findall(r'<style[^>]*>(.*?)</style>', html, re.S) if re.search(r'\.(mm|mb)-', b)]
    css=re.sub(r'/\*[\s\S]*?\*/',' ','\n'.join(blocks))
    # split into rules so we can name the selector each literal sits in
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        sel, body = m.group(1).strip().replace('\n',' '), m.group(2)
        for t in TARGETS:
            if t in body.lower():
                for decl in body.split(';'):
                    if t in decl.lower():
                        s = re.sub(r'\s+',' ',sel)[:52]
                        seen[t].add((s, re.sub(r'\s+',' ',decl).strip()[:60]))
NEAR={'#c64d42':'--cta #db5b4f / --cta-hover #b34a40','#c45045':'--cta-hover #b34a40',
 '#e6e2da':'--border #e5e5e5 / --warm-dark #f0ebe3','#ff8c5a':'--accent #e8734a',
 '#f8f6f1':'--warm #f9f6f1','#002833':'(nothing close)','#34abc7':'--teal #3ba5a8',
 '#fdebe2':'--accent-light #fef0eb','#eef0f4':'--teal-light #e8f6f6',
 '#f7f6f5':'(deliberate: --surface-alt)','#fbf9f9':'(deliberate: --warm-alt)'}
for t in TARGETS:
    if t in seen:
        print(f"\n{t}  ->  nearest dominant: {NEAR[t]}")
        for s,d in sorted(seen[t])[:4]:
            print(f"    {s}\n        {d}")
        if len(seen[t])>4: print(f"    ... {len(seen[t])-4} more site(s)")
