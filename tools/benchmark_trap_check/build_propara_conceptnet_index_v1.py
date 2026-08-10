"""One-time preprocessing: scan the full ConceptNet 5.7.0 assertions dump ONCE and extract a
compact ProPara-SCOPED English edge index for the co-participation bridging probe.

Rationale (same pattern as run_fastcoref_propara_v1.py): querying the 498MB gz per participant-verb
pair is infeasible; instead we build, in one pass, a term -> [(relation, other_term, weight)] map
restricted to (a) English<->English edges where at least one endpoint is a ProPara vocabulary term
(participant tokens + sentence content tokens across dev+test) and (b) a co-participation-relevant
relation set. The bridging cell reads the small JSON, NOT the gz.

Invoke:  python tools/benchmark_trap_check/build_propara_conceptnet_index_v1.py
Output:  data/benchmark_trap_check/propara_conceptnet_index_v1.json
         {"_meta": {...}, "edges": {term: [[rel, other_term, weight], ...], ...}}
NO gold used (only the surface text vocabulary; ConceptNet is a real external KB).
"""
import gzip
import json
import os
import re
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara")
CN_GZ = os.path.join(REPO_ROOT, "data", "conceptnet", "conceptnet-assertions-5.7.0.csv.gz")
OUT = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_conceptnet_index_v1.json")

# co-participation-relevant relations (a participant linked to a process/other-entity)
KEEP_RELS = {
    "PartOf", "MadeOf", "HasA", "UsedFor", "ReceivesAction", "HasSubevent", "HasFirstSubevent",
    "HasLastSubevent", "Causes", "CausesDesire", "HasPrerequisite", "CapableOf", "IsA",
    "RelatedTo", "Synonym", "FormOf", "DerivedFrom", "SimilarTo", "HasProperty", "AtLocation",
}
_WORD = re.compile(r"[a-z]+")


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8").read().strip().split("\n")]


def _toks(s):
    return {t for t in _WORD.findall(s.lower()) if len(t) > 2}


def _singularize(t):
    if t.endswith("ies") and len(t) > 4:
        return t[:-3] + "y"
    if t.endswith("es") and len(t) > 4:
        return t[:-2]
    if t.endswith("s") and len(t) > 3:
        return t[:-1]
    return t


def build_vocab():
    vocab = set()
    for split in ("dev", "test"):
        for p in load_jsonl(os.path.join(DATA_DIR, f"grids.v1.{split}.json")):
            for part in p["participants"]:
                for t in _toks(part):
                    vocab.add(t); vocab.add(_singularize(t))
            for s in p["sentence_texts"]:
                for t in _toks(s):
                    vocab.add(t); vocab.add(_singularize(t))
    return vocab


def _cn_term(uri):
    # /c/en/sound_wave/n -> "sound wave" ; return None if not English
    parts = uri.split("/")
    if len(parts) < 4 or parts[1] != "c" or parts[2] != "en":
        return None
    return parts[3].replace("_", " ")


def main():
    vocab = build_vocab()
    print(f"[vocab] {len(vocab)} ProPara terms", flush=True)
    edges = {}
    n_lines = 0
    n_kept = 0
    t0 = time.time()
    with gzip.open(CN_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            n_lines += 1
            if n_lines % 2_000_000 == 0:
                print(f"[scan] {n_lines/1e6:.0f}M lines, {n_kept} edges kept, {time.time()-t0:.0f}s", flush=True)
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            rel = parts[1].split("/")[2] if parts[1].startswith("/r/") else None
            if rel not in KEEP_RELS:
                continue
            start = _cn_term(parts[2])
            end = _cn_term(parts[3])
            if start is None or end is None:
                continue
            start_toks = _toks(start)
            end_toks = _toks(end)
            # keep iff some endpoint token is ProPara vocab (the OTHER endpoint is the co-participant hint)
            start_hit = bool(start_toks & vocab)
            end_hit = bool(end_toks & vocab)
            if not (start_hit or end_hit):
                continue
            weight = 1.0
            try:
                meta = json.loads(parts[4]) if len(parts) > 4 else {}
                weight = float(meta.get("weight", 1.0))
            except Exception:
                weight = 1.0
            # index BOTH directions on the single-word head tokens so lookup by a participant/entity token works
            for a_toks, b in ((start_toks, end), (end_toks, start)):
                for at in (a_toks & vocab):
                    edges.setdefault(at, []).append([rel, b, round(weight, 3)])
            n_kept += 1
    # dedupe + cap per term (keep highest-weight)
    for term in list(edges.keys()):
        seen = {}
        for rel, other, w in edges[term]:
            key = (rel, other)
            if key not in seen or w > seen[key][2]:
                seen[key] = [rel, other, w]
        edges[term] = sorted(seen.values(), key=lambda e: -e[2])[:200]
    out = {"_meta": {"source": "conceptnet-assertions-5.7.0", "relations": sorted(KEEP_RELS),
                     "n_vocab_terms": len(vocab), "n_terms_with_edges": len(edges),
                     "n_edges_scanned_kept": n_kept, "n_lines": n_lines},
           "edges": edges}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"[done] {len(edges)} terms indexed, {n_kept} raw edges kept, {time.time()-t0:.0f}s -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
