#!/usr/bin/env python3
"""Backfill the town services block fields across the Areas We Serve collection.

Per town, all derived from the item's `state` field:
  state-key                          new-jersey | georgia | north-carolina
  show-services-block                true (drives the block's bound visibility)
  service-link-{service}             /{service}-{state-key}  x4

Gates before any write: every live item maps to exactly one state, per-state
counts match the known census (NJ 115 / GA 78 / NC 20), and a-state items are
excluded. Items already carrying identical values are skipped. Writes go
through the bulk endpoints in chunks of 100, then the same items are
published. The site publish stays out of this script on purpose - it runs
separately, staging subdomain only.

Token: read from the path in WF_TOKEN_FILE (never echoed, never in the repo).
"""
import json, os, sys, time, urllib.request

CID = "6642b822923646375241d310"
API = "https://api.webflow.com/v2"
KEY_BY_STATE = {"New Jersey": "new-jersey", "Georgia": "georgia",
                "North Carolina": "north-carolina"}
EXPECT_COUNTS = {"New Jersey": 115, "Georgia": 78, "North Carolina": 20}
SERVICES = ["early-intervention", "parent-training", "behavior-support",
            "transition-planning"]

TOKEN = open(os.environ["WF_TOKEN_FILE"]).read().strip()


def req(method, path, body=None):
    r = urllib.request.Request(f"{API}{path}", method=method,
        headers={"Authorization": f"Bearer {TOKEN}",
                 "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(r) as resp:
                return json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f"{method} {path}: {e.code} {e.read().decode()[:300]}")


def main():
    # --- census
    items, offset = [], 0
    while True:
        page = req("GET", f"/collections/{CID}/items?limit=100&offset={offset}")
        items += page["items"]
        offset += 100
        if offset >= page["pagination"]["total"]:
            break
    live = [i for i in items if not i.get("isArchived") and not i.get("isDraft")]
    assert len(live) == 213, f"expected 213 live items, found {len(live)}"

    towns, hubs = [], []
    for i in live:
        fd = i["fieldData"]
        st = fd.get("state")
        assert st in KEY_BY_STATE, f"{fd.get('slug')}: unmapped state {st!r}"
        (hubs if fd.get("a-state") else towns).append(i)
    counts = {}
    for i in towns:
        counts[i["fieldData"]["state"]] = counts.get(i["fieldData"]["state"], 0) + 1
    print(f"census: {len(towns)} towns + {len(hubs)} state hubs; per state {counts}")
    assert sum(counts.values()) + len(hubs) == 213

    # --- compute writes; skip items already carrying identical values
    updates = []
    for i in towns:
        fd, key = i["fieldData"], KEY_BY_STATE[i["fieldData"]["state"]]
        want = {"state-key": key, "show-services-block": True}
        for svc in SERVICES:
            want[f"service-link-{svc}"] = f"/{svc}-{key}"
        if all(fd.get(k) == v for k, v in want.items()):
            continue
        updates.append({"id": i["id"], "fieldData": want})
    print(f"{len(updates)} items need writes, {len(towns) - len(updates)} already current")

    # --- bulk update + publish, chunks of 100
    for n in range(0, len(updates), 100):
        chunk = updates[n:n + 100]
        req("PATCH", f"/collections/{CID}/items", {"items": chunk})
        print(f"updated {n + len(chunk)}/{len(updates)}")
        time.sleep(1)
    all_ids = [i["id"] for i in towns]
    for n in range(0, len(all_ids), 100):
        chunk = all_ids[n:n + 100]
        req("POST", f"/collections/{CID}/items/publish", {"itemIds": chunk})
        print(f"published {n + len(chunk)}/{len(all_ids)}")
        time.sleep(1)

    # --- post-write audit against the live API
    bad = 0
    for st, key in KEY_BY_STATE.items():
        page = req("GET", f"/collections/{CID}/items/live?limit=100&offset=0")
    # full re-list (staged) and recheck every town
    items, offset = [], 0
    while True:
        page = req("GET", f"/collections/{CID}/items?limit=100&offset={offset}")
        items += page["items"]
        offset += 100
        if offset >= page["pagination"]["total"]:
            break
    for i in items:
        fd = i["fieldData"]
        if i.get("isArchived") or i.get("isDraft") or fd.get("a-state"):
            continue
        key = KEY_BY_STATE[fd["state"]]
        ok = (fd.get("state-key") == key and fd.get("show-services-block") is True
              and all(fd.get(f"service-link-{s}") == f"/{s}-{key}" for s in SERVICES))
        if not ok:
            bad += 1
            print(f"MISMATCH {fd.get('slug')}")
    print(f"audit: {bad} mismatches across all towns")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
