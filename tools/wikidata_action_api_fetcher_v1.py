"""DECISION 45 Step 2: wikidata Action-API fetcher (SPARQL-free; bypasses WDQS outage). For each validated science Q-class: CirrusSearch haswbstatement:P31=Qclass (paginated) -> entity Q-IDs; wbgetentities (batched) -> P31/P279/P361 claims; emit `Qsubj <Pid> Qobj` triples to facts.jsonl (consumed by substrate_facts_jsonl_to_atoms_v2.py qclass mode). R2: held-out gold concepts skipped by label. Pure-stdlib urllib + json (R1). Polite pacing + identified UA.

Usage:
  python tools/wikidata_action_api_fetcher_v1.py --per-class-cap 150 --output data/external/wikidata_action_api/wikidata_science_slice_v1.jsonl
"""
from __future__ import annotations
import sys, json, argparse, urllib.request, urllib.parse, time
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "hd-instrument-substrate-ingest/0.1 (research; marshall.cox@gmail.com)"}

# Validated whitelist (DECISION 45 step 1; tools/wikidata_qclass_discovery_v1.py). Q-class -> label.
QCLASSES = {
    "Q65943": "theorem", "Q24034552": "mathematical concept", "Q8366": "algorithm",
    "Q319141": "conjecture", "Q11348": "function", "Q1936384": "branch of mathematics",
    "Q246672": "mathematical object", "Q200726": "probability distribution",
    "Q11214": "differential equation", "Q11563": "number", "Q3239681": "scientific theory",
    "Q214070": "physical law", "Q408891": "scientific law", "Q11173": "chemical compound",
}
INSTANCE_PIDS = ("P31", "P279", "P361")
# R2 held-out gold concepts -- DO NOT INGEST (skip by label substring, case-insensitive).
HELDOUT_BLOCK = ("active inference", "free energy principle", "free-energy principle",
                 "predictive coding", "part-of-speech", "part of speech", "pos tagging")


def call(params, retries=3):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def collect_entities(qclass, cap):
    qids, offset = [], 0
    while len(qids) < cap:
        d = call({"action": "query", "list": "search", "srsearch": "haswbstatement:P31=" + qclass,
                  "srnamespace": 0, "srlimit": 50, "sroffset": offset, "format": "json"})
        hits = d.get("query", {}).get("search", [])
        if not hits:
            break
        qids.extend(h["title"] for h in hits)
        offset += len(hits)
        time.sleep(0.3)
        if offset >= 9000:  # CirrusSearch deep-pagination guard
            break
    return qids[:cap]


def fetch_claims(qids):
    """Batched wbgetentities -> {qid: (label, [(pid, obj_qid), ...])}."""
    out = {}
    for i in range(0, len(qids), 50):
        batch = qids[i:i + 50]
        d = call({"action": "wbgetentities", "ids": "|".join(batch), "props": "claims|labels",
                  "languages": "en", "format": "json"})
        for q, ent in d.get("entities", {}).items():
            if "missing" in ent:
                continue
            label = ent.get("labels", {}).get("en", {}).get("value", "")
            triples = []
            for pid in INSTANCE_PIDS:
                for c in ent.get("claims", {}).get(pid, []):
                    dv = c.get("mainsnak", {}).get("datavalue")
                    if dv and dv.get("type") == "wikibase-entityid":
                        triples.append((pid, dv["value"]["id"]))
            out[q] = (label, triples)
        time.sleep(0.3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class-cap", type=int, default=150)
    ap.add_argument("--output", default="data/external/wikidata_action_api/wikidata_science_slice_v1.jsonl")
    args = ap.parse_args()
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    all_qids, class_counts = [], {}
    print("=== collecting entities (cap=%d/class) ===" % args.per_class_cap, flush=True)
    for qc, lab in QCLASSES.items():
        ents = collect_entities(qc, args.per_class_cap)
        class_counts[qc] = len(ents)
        all_qids.extend(ents)
        print("  %-10s %-24s %d entities" % (qc, lab, len(ents)), flush=True)
    uniq = list(dict.fromkeys(all_qids))
    print("  total unique entities: %d" % len(uniq), flush=True)
    print("=== fetching claims ===", flush=True)
    claims = fetch_claims(uniq)
    written, blocked, no_triple = 0, 0, 0
    wl = set(QCLASSES)
    with out.open("w", encoding="utf-8") as f:
        for q, (label, triples) in claims.items():
            if label and any(b in label.lower() for b in HELDOUT_BLOCK):
                blocked += 1; continue  # R2
            kept = [(pid, obj) for pid, obj in triples if obj in wl]
            if not kept:
                no_triple += 1; continue
            for pid, obj in kept:
                f.write(json.dumps({"fact": "%s %s %s" % (q, pid, obj), "label": label}) + "\n")
                written += 1
    print("\n=== FETCH SUMMARY ===", flush=True)
    print("  entities with claims: %d" % len(claims), flush=True)
    print("  R2-blocked (held-out): %d" % blocked, flush=True)
    print("  no whitelisted triple: %d" % no_triple, flush=True)
    print("  facts written: %d -> %s" % (written, out), flush=True)


if __name__ == "__main__":
    main()
