import urllib.request, ssl, re, csv
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
B = "https://www.mastermindbehavior.com"
sm = urllib.request.urlopen(f"{B}/sitemap.xml", context=ctx).read().decode()
posts = sorted(set(re.findall(r"<loc>https://www\.mastermindbehavior\.com(/post/[^<]+)</loc>", sm)))
SIGNALS = {
 "new-jersey": ["New Jersey", "NJEIS", "PerformCare", "NJ FamilyCare", "Lakewood"],
 "georgia": ["Georgia", "Ava's Law", "Babies Can't Wait", "Katie Beckett", "DBHDD", "Macon"],
 "north-carolina": ["North Carolina", "NC Medicaid", "LME/MCO", "CDSA", "RB-BHT"],
}
SVC = ["early-intervention", "parent-training", "behavior-support", "transition-planning"]
rows = []
for path in posts:
    try:
        p = urllib.request.urlopen(B + path, context=ctx).read().decode()
    except Exception:
        continue
    # scope to the article rich text only: first w-richtext block to the footer
    m = re.search(r'class="[^"]*w-richtext[^"]*"', p)
    if not m: continue
    end = p.find('<footer')
    if end == -1: end = p.rfind('class="footer')
    art = p[m.start():end]
    generic = {s: len(re.findall(f'href="[^"]*/{s}"', art)) for s in SVC}
    statelinks = sum(len(re.findall(f'href="[^"]*/{s}-(?:new-jersey|georgia|north-carolina)"', art)) for s in SVC)
    sig = {k: sum(art.count(t) for t in ts) for k, ts in SIGNALS.items()}
    best = max(sig, key=sig.get)
    rows.append({"post": path, "generic_links": sum(generic.values()),
                 **{f"g_{s}": generic[s] for s in SVC}, "state_links": statelinks,
                 "sig_nj": sig["new-jersey"], "sig_ga": sig["georgia"], "sig_nc": sig["north-carolina"],
                 "best_state": best if sig[best] >= 3 else ""})
with open("blog-link-audit.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
cand = [r for r in rows if r["best_state"] and r["state_links"] == 0]
strong = [r for r in cand if max(r["sig_nj"], r["sig_ga"], r["sig_nc"]) >= 5]
print(f"{len(rows)} posts; {len(cand)} candidates (article-scoped signal >=3, no state link)")
print("by state:", {s: sum(1 for r in cand if r['best_state'] == s) for s in SIGNALS})
print(f"strong (signal >=5): {len(strong)}")
for r in sorted(strong, key=lambda r: -max(r['sig_nj'], r['sig_ga'], r['sig_nc']))[:15]:
    print(" ", r["post"], r["best_state"], f"nj{r['sig_nj']}/ga{r['sig_ga']}/nc{r['sig_nc']}", f"generic:{r['generic_links']}")
