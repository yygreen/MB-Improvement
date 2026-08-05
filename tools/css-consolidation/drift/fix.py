import re, glob, os
SUBS={'#c64d42':'#b34a40','#c45045':'#b34a40','#f8f6f1':'#f9f6f1',
      '#fdebe2':'#fef0eb','#eef0f4':'#e8f6f6'}
tot=0; out=[]
for f in sorted(glob.glob('embed*.orig.html'), key=lambda x:int(re.findall(r'\d+',x)[0])):
    i=int(re.findall(r'\d+',f)[0]); c=open(f).read(); o=c; n=0
    for a,b in SUBS.items():
        k=len(re.findall(a,o,re.I)); n+=k
        o=re.sub(a,b,o,flags=re.I)
    if not n: continue
    assert len(o)==len(c), f"length changed on embed{i}"
    open(f'embed{i}.fixed.html','w').write(o)
    out.append((i,len(c),n)); tot+=n
for i,sz,n in sorted(out, key=lambda x:x[1]):
    print(f"embed{i:<3} {sz:>6} B   {n} substitution(s)")
print(f"\n{len(out)} embeds, {tot} substitutions, {sum(s for _,s,_ in out)} B to re-emit")
