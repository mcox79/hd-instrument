# Stage 2 FETCH: select the item-edit subsample (all reverted item-edits + a
# fixed random accepted sample) and cache each involved entity's current claims
# + sitelinks. Separated from analysis so the (network) fetch runs once and the
# analysis can iterate cheaply. ASCII-only. No queue/GPU/atoms.
#
# Triple per edit is parsed from the wikibase edit COMMENT (structured
# "[[Property:Pxxx]]: [[Qyyy]]"), so no per-revision content fetch is needed.

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "exp_wdvc_realdata_capability"))
RAW_PATH = os.path.join(OUT_DIR, "sample_raw.jsonl")
SAMPLE_PATH = os.path.join(OUT_DIR, "stage2_sample.jsonl")
CLAIMS_PATH = os.path.join(OUT_DIR, "entity_claims.jsonl")

API = "https://www.wikidata.org/w/api.php"
UA = "hd-instrument-research/1.0 (research use; contact marshall.cox@gmail.com)"
N_NEG = 3000
SEED = 12345  # fixed integer seed (NOT hash()) per PROT-023

PROP_RE = re.compile(r"\[\[Property:(P\d+)\]\]")
ITEM_RE = re.compile(r"\]\]:\s*\[\[(Q\d+)\]\]")


def api_get(params, retries=4):
    params = dict(params)
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # NOT BaseException
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("API failed after retries: %r" % last)


def parse_item_edit(r):
    """Return (head, prop, target) if this is an item-valued edit on a Q-entity, else None."""
    if not r["title"].startswith("Q"):
        return None
    c = r.get("comment") or ""
    p = PROP_RE.search(c)
    t = ITEM_RE.search(c)
    if not (p and t):
        return None
    return (r["title"], p.group(1), t.group(1))


def main():
    import random
    rng = random.Random(SEED)
    rows = [json.loads(l) for l in open(RAW_PATH, encoding="utf-8")]
    human = [r for r in rows if not r["bot"]]
    item_edits = []
    for r in human:
        tr = parse_item_edit(r)
        if tr is None:
            continue
        r = dict(r)
        r["head"], r["prop"], r["target"] = tr
        item_edits.append(r)
    pos = [r for r in item_edits if r["reverted"]]
    neg = [r for r in item_edits if not r["reverted"]]
    rng.shuffle(neg)
    neg = neg[:N_NEG]
    sample = pos + neg
    rng.shuffle(sample)
    with open(SAMPLE_PATH, "w", encoding="utf-8") as f:
        for r in sample:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    print("[sample] item-edits total=%d pos=%d neg_kept=%d sample=%d"
          % (len(item_edits), len(pos), len(neg), len(sample)), flush=True)

    # Unique entities to fetch: heads + targets.
    ents = sorted({r["head"] for r in sample} | {r["target"] for r in sample})
    print("[fetch] unique entities to fetch: %d" % len(ents), flush=True)

    done = set()
    if os.path.exists(CLAIMS_PATH):
        for l in open(CLAIMS_PATH, encoding="utf-8"):
            try:
                done.add(json.loads(l)["id"])
            except Exception:
                pass
    todo = [e for e in ents if e not in done]
    print("[fetch] already cached=%d todo=%d" % (len(done), len(todo)), flush=True)

    fout = open(CLAIMS_PATH, "a", encoding="utf-8")
    n_batch = 0
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        d = api_get({"action": "wbgetentities", "ids": "|".join(batch),
                     "props": "claims|sitelinks", "format": "json"})
        ent_map = d.get("entities", {})
        for qid, ent in ent_map.items():
            if "missing" in ent:
                rec = {"id": qid, "missing": True, "triples": [], "n_statements": 0,
                       "n_sitelinks": 0, "refs_by_stmt": {}}
            else:
                triples = []
                refs = {}
                claims = ent.get("claims", {}) or {}
                n_stmt = 0
                for pid, stmts in claims.items():
                    for st in stmts:
                        n_stmt += 1
                        nref = len(st.get("references", []) or [])
                        mainsnak = st.get("mainsnak", {})
                        dv = mainsnak.get("datavalue", {})
                        val = dv.get("value")
                        tgt = None
                        if isinstance(val, dict) and val.get("entity-type") == "item":
                            tgt = "Q%s" % val.get("numeric-id")
                        if tgt:
                            triples.append([pid, tgt])
                            refs["%s|%s" % (pid, tgt)] = nref
                rec = {"id": qid, "missing": False, "triples": triples,
                       "n_statements": n_stmt, "n_sitelinks": len(ent.get("sitelinks", {}) or {}),
                       "refs_by_stmt": refs}
            fout.write(json.dumps(rec, ensure_ascii=True) + "\n")
        fout.flush()
        n_batch += 1
        if n_batch % 10 == 0:
            print("[fetch] batches=%d entities_done~%d" % (n_batch, i + len(batch)), flush=True)
        time.sleep(0.2)
    fout.close()
    print("[done] claims cached to %s" % CLAIMS_PATH, flush=True)


if __name__ == "__main__":
    main()
