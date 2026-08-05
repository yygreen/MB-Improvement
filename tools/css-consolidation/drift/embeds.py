# Reconstruct each drifted embed's code from the rendered page. Webflow renders an
# HtmlEmbed verbatim inside <div class="w-embed">, so the wrapper's inner HTML is
# the embed's code -- which lets me build the corrected version offline and paste
# it once, instead of reading each embed back through the API first.
import re, glob
NEED={'aba-therapy-in-georgia':[4,5,6],'aba-therapy-in-new-jersey':[4,5],
 'aba-therapy-in-north-carolina':[4,5],'autism-screening-checklist':[2],
 'behavior-support':[2],'early-intervention':[2],
 'financial-aid-resources':[3,5,6,7],'in-home-aba-therapy':[2],
 'insurance-terminology':[4,6,7],'parent-training':[2],'services':[3],
 'skill-development':[2],'transition-planning':[2]}

def wrapper_span(h, s, e):
    """Innermost <div class="...w-embed..."> enclosing [s,e)."""
    best=None
    for m in re.finditer(r'<div class="[^"]*w-embed[^"]*">', h):
        if m.end() > s: continue
        # walk to its matching </div>
        depth=1; i=m.end()
        for t in re.finditer(r'<div\b[^>]*>|</div>', h[m.end():]):
            depth += 1 if t.group(0).startswith('<div') else -1
            if depth==0: i=m.end()+t.start(); break
        if i>=e and (best is None or (m.end()>best[0])): best=(m.end(), i)
    return best

seen={}
for page,idxs in NEED.items():
    h=open(page+'.html').read()
    for m in [x for i,x in enumerate(re.finditer(r'<style[^>]*>(.*?)</style>', h, re.S)) if i in idxs]:
        span=wrapper_span(h, m.start(), m.end())
        if not span: print(f"!! {page}: no w-embed wrapper found"); continue
        code=h[span[0]:span[1]]
        key=re.sub(r'\s+','',code)
        seen.setdefault(key,{'code':code,'pages':[]})['pages'].append(page)

print(f"{len(seen)} distinct embeds carry the drift\n")
for i,(k,v) in enumerate(sorted(seen.items(), key=lambda x:-len(x[1]['pages']))):
    c=v['code']
    hits={t:c.lower().count(t) for t in ['#c64d42','#c45045','#e6e2da','#f8f6f1','#fdebe2','#eef0f4','#ff8c5a'] if t in c.lower()}
    print(f"[{i}] {len(c):>6} B  x{len(v['pages'])} page(s)  {hits}")
    print(f"     {', '.join(sorted(set(v['pages'])))}")
    open(f'embed{i}.orig.html','w').write(c)
