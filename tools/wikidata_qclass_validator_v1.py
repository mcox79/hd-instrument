"""DECISION 45 Step 1: validate the mapper's hand-curated MATH/SCIENCE Q-class IDs against CURRENT wikidata labels (they are stale -- e.g. Q12483 returns population stats). Batched wbgetentities (Action API; bypasses WDQS outage). Pure-stdlib urllib. Outputs a table + a refreshed VALID set + flags.

For each Q-ID: fetch current English label; compare (token overlap) to the mapper's expected label; classify VALID (overlap) / STALE (no overlap) / MISSING. The VALID set becomes the fetch whitelist.
"""
from __future__ import annotations
import sys, json, urllib.request, urllib.parse, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "hd-instrument-substrate-ingest/0.1 (research; marshall.cox@gmail.com)"}

# Q-ID -> mapper's expected label (from substrate_facts_jsonl_to_atoms_v2.py comments)
EXPECTED = {
    "Q11862829": "mathematical object", "Q12483": "theorem", "Q121594": "mathematical statement",
    "Q4373292": "mathematical theorem", "Q839863": "mathematical formula", "Q12482": "axiom",
    "Q179467": "function mathematics", "Q11567": "number", "Q12503": "integer",
    "Q44559": "variable mathematics", "Q5862903": "mathematical operation", "Q1369832": "mathematical structure",
    "Q190556": "mathematical proof", "Q190099": "equation", "Q11473": "graph mathematics",
    "Q44424": "algorithm", "Q4485003": "mathematical concept", "Q1379457": "mathematical notation",
    "Q11023": "vector space", "Q188524": "group mathematics", "Q161205": "field mathematics",
    "Q161228": "ring mathematics", "Q190008": "category mathematics", "Q170978": "topological space",
    "Q207936": "set mathematics", "Q207342": "measure mathematics", "Q207316": "metric space",
    "Q207223": "probability space", "Q11471": "physics or math constant", "Q186290": "matrix",
    "Q133250": "linear algebra", "Q41217": "geometric figure", "Q133038": "calculus",
    "Q43287": "logic", "Q23404": "algorithmic procedure", "Q1144549": "mathematical method",
    "Q1191515": "mathematical theory", "Q9081": "knowledge",
    "Q2329": "chemistry", "Q420": "biology", "Q11862": "quantum mechanics", "Q377903": "scientific theory",
    "Q12136": "disease", "Q7239": "organism", "Q8054": "protein", "Q7187": "gene",
    "Q40348": "algorithm", "Q19064": "method process", "Q1183543": "scientific concept",
    "Q11422": "physical law", "Q188211": "physical phenomenon", "Q1207505": "quantity",
    "Q482798": "quantum theory", "Q11402": "general relativity", "Q333": "general",
}

STOP = {"mathematics", "or", "process", "general", "a", "the", "of"}


def call(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_labels(qids):
    out = {}
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        d = call({"action": "wbgetentities", "ids": "|".join(batch), "props": "labels|descriptions",
                  "languages": "en", "format": "json"})
        for q, ent in d.get("entities", {}).items():
            lab = ent.get("labels", {}).get("en", {}).get("value", "")
            desc = ent.get("descriptions", {}).get("en", {}).get("value", "")
            out[q] = (lab, desc)
        time.sleep(0.3)
    return out


def overlaps(expected, current):
    e = {w for w in expected.lower().replace("(", " ").replace(")", " ").split() if w not in STOP}
    c = set(current.lower().replace("(", " ").replace(")", " ").split())
    return bool(e & c)


def main():
    qids = list(EXPECTED.keys())
    print("validating %d Q-class IDs against current wikidata labels...\n" % len(qids), flush=True)
    labels = fetch_labels(qids)
    valid, stale, missing = [], [], []
    print("  %-11s %-26s %-26s %s" % ("Q-ID", "mapper-expected", "current-label", "verdict"), flush=True)
    for q in qids:
        exp = EXPECTED[q]
        if q not in labels:
            missing.append(q); print("  %-11s %-26s %-26s MISSING" % (q, exp[:25], "?")); continue
        cur, desc = labels[q]
        ok = overlaps(exp, cur) or overlaps(exp, desc)
        (valid if ok else stale).append(q)
        print("  %-11s %-26s %-26s %s" % (q, exp[:25], cur[:25], "VALID" if ok else "STALE"), flush=True)
    print("\n=== SUMMARY ===", flush=True)
    print("VALID (%d): %s" % (len(valid), valid), flush=True)
    print("STALE (%d): %s" % (len(stale), stale), flush=True)
    print("MISSING (%d): %s" % (len(missing), missing), flush=True)
    # write refreshed valid set
    out = {"valid": valid, "stale": {q: (EXPECTED[q], labels.get(q, ("?", ""))[0]) for q in stale},
           "missing": missing, "valid_with_labels": {q: labels[q][0] for q in valid}}
    import pathlib
    p = pathlib.Path("data/external/wikidata_action_api/qclass_validation_v1.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\nwrote %s" % p, flush=True)


if __name__ == "__main__":
    main()
