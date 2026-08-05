# Match live embed codes against the corrected embeds built offline, keeping the
# ACTION label (e0/e1/...) rather than the inner query label, so each match maps
# back to a specific element id.
import json, sys, re, glob
path=sys.argv[1]
arr=json.load(open(path)); txt="".join(x["text"] for x in arr)
dec=json.JSONDecoder(); objs=[]; i=0
while i < len(txt):
    try: o,i = dec.raw_decode(txt, i)
    except ValueError: i+=1; continue
    objs.append(o)
def flatten(o):
    if isinstance(o,list):
        for v in o: yield from flatten(v)
    elif isinstance(o,dict):
        yield o
        for v in o.values(): yield from flatten(v)
def codes_under(o):
    out=[]
    def w(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k=="value" and isinstance(v,str) and len(v)>200: out.append(v)
                else: w(v)
        elif isinstance(x,list):
            for v in x: w(v)
    w(o); return out
pairs=[]
for o in objs:
    for d in flatten(o):
        lab=d.get("label")
        if lab and re.fullmatch(r'e\d+', str(lab)):
            cs=codes_under(d)
            if cs: pairs.append((lab, cs[0]))
seen=set(); norm=lambda s: re.sub(r'\s+','',s)
orig={f: norm(open(f).read()) for f in glob.glob('embed*.orig.html')}
for lab,c in pairs:
    if (lab,c) in seen: continue
    seen.add((lab,c))
    n=norm(c); hit=[f for f,v in orig.items() if v==n]
    drift = re.findall(r'#c64d42|#c45045|#f8f6f1|#fdebe2|#eef0f4', c, re.I)
    mark = hit[0].replace('.orig.html','') if hit else ('clean' if not drift else '?? DRIFT, NO MATCH')
    print(f"{lab:>4}  {len(c):>6} B  drift={len(drift):<2} -> {mark}")
