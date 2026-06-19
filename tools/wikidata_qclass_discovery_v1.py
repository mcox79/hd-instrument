"""DECISION 45 Step 1b: DISCOVER correct current wikidata Q-class IDs for math/science concepts (the mapper's hand-curated list is 84pct stale). For each concept name: wbsearchentities -> top candidates; then haswbstatement:P31=<Qid> -> instance count + sample labels to confirm it yields real instances. Output a validated Q-class whitelist (Q-IDs with high clean instance counts). Pure-stdlib urllib (Action API; bypasses WDQS outage)."""
from __future__ import annotations
import sys, json, urllib.request, urllib.parse, time
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "hd-instrument-substrate-ingest/0.1 (research; marshall.cox@gmail.com)"}

# Target classes: unambiguous-ish math/science categories likely to have many instances.
CONCEPTS = [
    "theorem", "mathematical theorem", "conjecture", "mathematical object", "mathematical concept",
    "algorithm", "mathematical function", "physical law", "scientific law", "scientific theory",
    "chemical compound", "mathematical structure", "topological space", "Lie group",
    "differential equation", "probability distribution", "matrix decomposition", "graph",
    "vector space", "mathematical group", "field of mathematics", "number",
]


def call(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_entity(name):
    d = call({"action": "wbsearchentities", "search": name, "language": "en", "type": "item",
              "limit": 3, "format": "json"})
    return [(h["id"], h.get("label", ""), h.get("description", "")) for h in d.get("search", [])]


def instance_count(qid):
    d = call({"action": "query", "list": "search", "srsearch": "haswbstatement:P31=" + qid,
              "srnamespace": 0, "srlimit": 4, "format": "json"})
    total = d.get("query", {}).get("searchinfo", {}).get("totalhits", 0)
    titles = [h["title"] for h in d.get("query", {}).get("search", [])]
    return total, titles


def main():
    whitelist = {}
    print("discovering correct Q-class IDs for %d concepts...\n" % len(CONCEPTS), flush=True)
    for name in CONCEPTS:
        try:
            cands = search_entity(name)
        except Exception as e:
            print("  %-26s SEARCH_FAIL %s" % (name, str(e)[:50])); time.sleep(0.4); continue
        if not cands:
            print("  %-26s (no candidate)" % name); time.sleep(0.4); continue
        qid, lab, desc = cands[0]
        time.sleep(0.4)
        try:
            total, sample = instance_count(qid)
        except Exception as e:
            total, sample = -1, []
        print("  %-26s -> %-10s '%s' (%s) | P31-instances=%s sample=%s" % (
            name, qid, lab[:22], desc[:30], total, sample[:3]), flush=True)
        if total and total >= 20:
            whitelist[qid] = {"concept": name, "label": lab, "desc": desc, "instances": total}
        time.sleep(0.5)
    print("\n=== WHITELIST (instances>=20) %d classes ===" % len(whitelist), flush=True)
    for q, m in sorted(whitelist.items(), key=lambda kv: -kv[1]["instances"]):
        print("  %-10s %-22s instances=%d" % (q, m["label"][:22], m["instances"]), flush=True)
    import pathlib
    p = pathlib.Path("data/external/wikidata_action_api/qclass_whitelist_v1.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(whitelist, indent=1), encoding="utf-8")
    print("\nwrote %s (%d classes)" % (p, len(whitelist)), flush=True)


if __name__ == "__main__":
    main()
