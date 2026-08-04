# Validate every property on every node against the schema.org vocabulary,
# honouring inheritance. Catches exactly the class of error the audit found.
import json, sys, urllib.request, os

VOCAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schemaorg.jsonld')
URL = 'https://schema.org/version/latest/schemaorg-current-https.jsonld'

def load():
    if not os.path.exists(VOCAB):
        urllib.request.urlretrieve(URL, VOCAB)
    return json.load(open(VOCAB))['@graph']

def ids(x):
    if x is None: return []
    if isinstance(x, dict): return [x.get('@id', '')]
    if isinstance(x, list): return [i.get('@id', '') if isinstance(i, dict) else str(i) for i in x]
    return [str(x)]

def build(g):
    parents, props = {}, {}
    for n in g:
        i = n.get('@id', '')
        if not i.startswith('schema:'): continue
        name = i.split(':')[-1]
        if 'rdfs:subClassOf' in n:
            parents[name] = [p.split(':')[-1] for p in ids(n['rdfs:subClassOf'])]
        if 'schema:domainIncludes' in n:
            for d in ids(n['schema:domainIncludes']):
                props.setdefault(d.split(':')[-1], set()).add(name)
    return parents, props

def allowed(t, parents, props, seen=None):
    seen = seen or set()
    if t in seen: return set()
    seen.add(t)
    out = set(props.get(t, ()))
    for p in parents.get(t, ()):
        out |= allowed(p, parents, props, seen)
    return out

GENERIC = {'@id', '@type', '@context', '@graph'}

def check(doc, parents, props):
    bad = []
    def walk(o):
        if isinstance(o, dict):
            t = o.get('@type')
            if isinstance(t, str):
                ok = allowed(t, parents, props)
                for k in o:
                    if k in GENERIC: continue
                    if k not in ok:
                        bad.append((t, k, o.get('@id', '(inline)')))
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(doc)
    return bad

if __name__ == '__main__':
    parents, props = build(load())
    data = json.load(open(sys.argv[1]))
    total = 0
    for page, doc in data.items():
        bad = check(doc, parents, props)
        total += len(bad)
        mark = 'FAIL' if bad else ' ok '
        print(f'  {mark}  {page}')
        for t, k, i in bad:
            print(f'          {t}.{k}  invalid   ({i})')
    print(f'\n{total} invalid propert{"y" if total==1 else "ies"}')
    sys.exit(1 if total else 0)
