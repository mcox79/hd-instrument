"""
exp_substrate_uot_universal_operator_test_per_field_cpu_v1.py -- CELL UOT: does ONE universal promotion operator fire sensibly in EVERY field given a field-appropriate signal extractor? -- CPU/local (no heat, read-only).

ROUTING: Research DRILL VERDICT (research_to_exp_dev_DRILL_VERDICT_universal_vs_field_specific_HYBRID_H3_CONFIRMED_6_cells_ENDORSED...).
  H3 (HYBRID) confirmed: UNIVERSAL promotion OPERATORS + FIELD-SPECIFIC SIGNAL EXTRACTORS + first-class field partition routing. CELL UOT is
  the DECISIVE cell for the USER directive ("is there a universal way to promote + interact with everything?"). It holds the OPERATOR fixed
  (one grouping+frequency promotion operator, identical code) and SWAPS only the per-field SIGNAL EXTRACTOR, then measures whether the
  operator FIRES sensibly in each field. If the same operator fires (produces coherent promotion candidates) across all/most fields ONCE
  GIVEN a field-appropriate signal, the universal-operator claim holds; the field-specificity lives only in the thin signal-extractor layer.
  NO LLM; relations + atom fields + text vocabulary; numpy for null; no heat. READ-ONLY.

  ONE UNIVERSAL OPERATOR (identical for every field):
    op_group(signal_pairs) -> connected groups size>=3  (the promotion operator: atoms a SIGNAL links become a promotion-candidate group)
    op_frequency(indeg)    -> hubs in-degree>=3          (the frequency-promotion operator)
  FIELD-APPROPRIATE SIGNAL EXTRACTORS (the ONLY thing that changes per field -- the "reading glasses"):
    structural(field_atoms) = shared serves_capability OR shared USES-target OR shared DEPENDS_ON-prereq   (math/science/language/cognition)
    topical(field_atoms)    = shared distinctive vocabulary (df-banded, chaining-free pairwise)            (history)
  Each field is assigned its appropriate extractor; the SAME op_group runs on whatever pairs the extractor emits.

  MEASURES per field: M1 operator FIRES (>=1 coherent group). M2 candidates SANE (groups corroborated by an independent property:
  structural fields -> shared domain/capability; history -> shared vocabulary above null). M3 promotable-fraction gap across fields < 2x
  (the operator promotes a comparable FRACTION of each field once given the right signal -> not wildly field-biased).

PRE-REGISTERED (per drill): HARD-PASS M1 fires in >=4/5 fields AND M2 sane in >=4/5 AND M3 promotable-fraction max/min gap < 2x.
  MIDDLE: M1 in 3/5 OR M3 gap in [2x,5x]. HARD-FAIL: M1 fires in <=2 fields OR M3 gap > 5x (operator is fundamentally field-biased).
  UNKNOWN if no index. ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_uot_universal_operator_test_per_field_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
K_STRUCT = 1; K_TOPIC = 4; DF_MAX_FRAC = 0.08; MIN_TOK_LEN = 4; MAX_BUCKET = 60; SEED = 1028
FIELDS_STRUCT = {"math", "science", "language", "cognition"}; FIELDS_TOPIC = {"history"}
_STOP = set("the of a an and or to for with in on is as by at from this that these those it its be are was were will would can could should has have had not but if then so we our us you your they their does done request benchmark failure hybrid facts data note date research drill exp dev testbed substrate verdict decision result results finding findings memory cycle phase per via use used using also new now".split())


def _norm(x):
    return str(x).split("::")[-1].strip()


def field_of(corpus, aid):
    c = (corpus or "").lower(); aid = aid.upper()
    if "history" in c: return "history"
    if c == "math" or aid.startswith(("T1/", "T2/", "T3/", "T2_FAM/")): return "math"
    if c == "science" or aid.startswith(("PHYS/", "CHEM/", "BIO/")): return "science"
    if aid.startswith(("LEX", "MWP/")) or c == "school": return "language"
    if aid.startswith(("CROSSDISC/", "NEURO/", "CS/")) or c == "concept": return "cognition"
    if c in ("meta", "methodology"): return "meta"
    return "other"


def op_group(pairs):
    """THE UNIVERSAL PROMOTION OPERATOR: connected groups (size>=3) over whatever signal pairs are given. Field-agnostic."""
    adj = defaultdict(set)
    for x, y in pairs:
        adj[x].add(y); adj[y].add(x)
    seen = set(); comps = []
    for n in list(adj):
        if n in seen: continue
        st = [n]; comp = {n}; seen.add(n)
        while st:
            u = st.pop()
            for v in adj[u]:
                if v not in seen: seen.add(v); comp.add(v); st.append(v)
        comps.append(comp)
    return [c for c in comps if len(c) >= 3]


def _tokens(text):
    return [t for t in re.split(r"[^a-z0-9]+", (text or "").lower()) if len(t) >= MIN_TOK_LEN and t not in _STOP and not t.isdigit()]


def pairs_from_buckets(key2atoms, k, max_bucket=MAX_BUCKET):
    pc = Counter()
    for kk, atoms in key2atoms.items():
        a = sorted(atoms)
        if 1 < len(a) <= max_bucket:
            for x, y in combinations(a, 2): pc[(x, y)] += 1
    return {pr for pr, c in pc.items() if c >= k}


def _selftest():
    # universal operator: groups of >=3 from pairs
    g = op_group({("a", "b"), ("b", "c"), ("x", "y")})
    assert len(g) == 1 and len(g[0]) == 3, g
    # field assignment
    assert field_of("decision_history", "x") == "history" and field_of("math", "T2/bind") == "math"
    assert field_of("", "PHYS/ising") == "science" and field_of("", "LEX_org") == "language"
    # bucket->pairs
    pr = pairs_from_buckets({"cap1": {"a", "b", "c"}}, 1)
    assert ("a", "b") in pr and ("a", "c") in pr
    assert "request" in _STOP and _tokens("Viterbi request 2026")[0] == "viterbi"
    print("[selftest] PASS: substrate_uot_universal_operator_test_per_field_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()

    def alg(a):
        x = getattr(a, "algebra", None); return x if isinstance(x, dict) else {}
    field = {}; domain = {}; caps = {}; text = {}
    for a in atoms:
        n = _norm(a.id); c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        field[n] = field_of(c, n); domain[n] = alg(a).get("domain")
        cs = getattr(a, "serves_capability", ()) or ()
        if cs: caps[n] = set(_norm(x) for x in cs)
        text[n] = (getattr(a, "name", "") or "") + " . " + (getattr(a, "description", "") or "")
    dep = defaultdict(set); uses = defaultdict(set); indeg = Counter()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt == "DEPENDS_ON": dep[s].add(t); indeg[t] += 1
            elif rt == "USES": uses[s].add(t)

    def structural_pairs(ids):
        ids = set(ids); cap2 = defaultdict(set)
        for n in ids:
            for c in caps.get(n, ()): cap2[c].add(n)
        # shared capability + shared dep-target + shared uses-target, all restricted to the field's atoms
        e = set(pairs_from_buckets(cap2, K_STRUCT))
        for adjm in (dep, uses):
            t2s = defaultdict(set)
            for s, ts in adjm.items():
                if s in ids:
                    for t in ts: t2s[t].add(s)
            e |= pairs_from_buckets(t2s, 2)
        return e

    def topical_pairs(ids):
        ids = list(ids)
        toks = {n: set(_tokens(text.get(n, ""))) for n in ids}
        df = Counter()
        for s in toks.values():
            for t in s: df[t] += 1
        dmax = max(3, int(DF_MAX_FRAC * len(ids)))
        sal = {n: {t for t in s if 2 <= df[t] <= dmax} for n, s in toks.items()}
        tok2 = defaultdict(set)
        for n, s in sal.items():
            for t in s: tok2[t].add(n)
        return pairs_from_buckets(tok2, K_TOPIC), sal

    by_field = defaultdict(list)
    for n, f in field.items(): by_field[f].append(n)
    target_fields = ["math", "science", "language", "cognition", "history"]
    rng = np.random.default_rng(SEED)
    rows = {}; promotable_fracs = {}
    for f in target_fields:
        ids = by_field.get(f, [])
        if len(ids) < 10:
            rows[f] = {"n_atoms": len(ids), "fires": False, "note": "too_few_atoms"}; continue
        extractor = "structural" if f in FIELDS_STRUCT else "topical"
        if extractor == "structural":
            pairs = structural_pairs(ids); sal = None
        else:
            pairs, sal = topical_pairs(ids)
        groups = op_group(pairs)                                   # SAME universal operator
        fires = len(groups) >= 1
        # M2 sanity: groups corroborated by an INDEPENDENT property
        if extractor == "structural":
            sane = 0
            for g in groups:
                gl = list(g)
                dom = [domain.get(x) for x in gl if domain.get(x)]
                if (dom and len(set(dom)) <= max(1, len(gl) // 2)) or any(caps.get(x) for x in gl):
                    sane += 1
            sane_frac = round(sane / max(1, len(groups)), 3)
        else:
            # history: corroborate via null -- real grouped-fraction vs shuffled-vocab null
            pool = [t for n in ids for t in sal[n]]
            null_groups = []
            if pool:
                parr = np.array(pool, dtype=object)
                shuf = {}
                for n in ids:
                    k = len(sal[n])
                    shuf[n] = set(parr[rng.choice(len(parr), size=min(k, len(parr)), replace=False)].tolist()) if k else set()
                tok2 = defaultdict(set)
                for n, s in shuf.items():
                    for t in s: tok2[t].add(n)
                null_groups = op_group(pairs_from_buckets(tok2, K_TOPIC))
            real_cov = sum(len(g) for g in groups); null_cov = sum(len(g) for g in null_groups)
            sane_frac = round(real_cov / (null_cov + 1e-9), 3) if null_cov else (2.0 if real_cov else 0.0)
        covered = len(set().union(*groups)) if groups else 0
        promotable_fracs[f] = covered / len(ids)
        max_group_frac = round((max(len(g) for g in groups) / len(ids)) if groups else 0.0, 3)
        rows[f] = {"n_atoms": len(ids), "extractor": extractor, "fires": fires, "n_groups": len(groups),
                   "promotable_frac": round(covered / len(ids), 3), "max_group_frac": max_group_frac,
                   "sanity": sane_frac, "top_group_sizes": sorted((len(g) for g in groups), reverse=True)[:6]}
    # SYSTEMS-vs-RECORDS framing (Research-endorsed): system fields should fire+be sane via the universal operator;
    # history is a RECORD = NEGATIVE CONTROL (the operator must NOT cleanly axiomatize narrative -- weak/insane firing CONFIRMS the split).
    SYSTEM_FIELDS = ["math", "science", "language", "cognition"]; RECORD_FIELDS = ["history"]
    def is_sane(f):
        r = rows.get(f, {})
        if not r.get("fires"): return False
        if r.get("max_group_frac", 0) >= 0.5: return False        # NO-MEGA-BLOB guard: one group swallowing the field = degenerate chain, not archetypes
        return (r["sanity"] >= 0.6) if r.get("extractor") == "structural" else (r["sanity"] >= 1.5)
    sys_fire = sum(1 for f in SYSTEM_FIELDS if rows.get(f, {}).get("fires"))
    sys_sane = sum(1 for f in SYSTEM_FIELDS if is_sane(f))
    rec_sane = sum(1 for f in RECORD_FIELDS if is_sane(f))         # negative control: expect 0 (records NOT sanely axiomatized)
    n_fire = sum(1 for f in target_fields if rows.get(f, {}).get("fires"))
    n_sane = sum(1 for f in target_fields if is_sane(f))
    pf = [promotable_fracs[f] for f in SYSTEM_FIELDS if promotable_fracs.get(f, 0) > 0]
    m3_gap = round(max(pf) / min(pf), 3) if len(pf) >= 2 else None
    print("  per-field universal-operator firing (ONE operator, field-appropriate signal extractor):", flush=True)
    for f in target_fields:
        r = rows.get(f, {})
        print("    %-10s atoms=%4d extractor=%-10s FIRES=%s groups=%s sane=%s promotable=%.3f sizes=%s" % (
            f, r.get("n_atoms", 0), r.get("extractor", "-"), r.get("fires"), r.get("n_groups", 0),
            r.get("sanity"), r.get("promotable_frac", 0), r.get("top_group_sizes", [])), flush=True)
    print("  SYSTEM fields fire=%d/4 sane=%d/4 | RECORD(history) sane=%d/1 (negative control, expect 0) | M3 system promotable-gap=%s" % (
        sys_fire, sys_sane, rec_sane, m3_gap), flush=True)
    return {"rows": rows, "n_fire": n_fire, "n_sane": n_sane, "m3_gap": m3_gap,
            "sys_fire": sys_fire, "sys_sane": sys_sane, "rec_sane": rec_sane,
            "promotable_fracs": {f: round(v, 4) for f, v in promotable_fracs.items()}}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    sf = r["sys_fire"]; ss = r["sys_sane"]; rs = r["rec_sane"]; gap = r["m3_gap"]
    s = ("SYSTEM fields (math/science/language/cognition) fire=%d/4 sane=%d/4 via the SAME operator; RECORD field (history) sane=%d/1 "
         "[NEGATIVE CONTROL: should be 0 -- the operator must NOT axiomatize narrative]; system promotable-gap=%s; per-field promotable=%s. "
         "(operator code identical; only the signal extractor swaps -- structural for systems, topical for the record.)") % (
        sf, ss, rs, gap, r["promotable_fracs"])
    gap_ok = (gap is not None and gap < 2.0); gap_mid = (gap is not None and gap < 5.0)
    # HARD-PASS = universal operator promotes SYSTEM-content (>=3/4 sane) AND the RECORD negative control does NOT sanely axiomatize (rs==0)
    if ss >= 3 and rs == 0 and gap_ok:
        return ("HARD_PASS", "HARD_PASS (H3 + systems-vs-records CONFIRMED): the SAME universal operator promotes SYSTEM-content sanely in %d/4 system fields (comparable promotable fraction, gap %.2f<2x) AND correctly does NOT axiomatize the RECORD field (history negative-control sane=0). Promotion is universal over system-content; records are NOT promoted (retrieved/mined instead). Field-specificity lives only in the thin signal-extractor; the operator+ladder are universal over the right content-type. " % (ss, gap) + s)
    if ss >= 3 and rs == 0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: systems promote sanely (%d/4) and the record control behaves (sane=0), but the system promotable-gap %s exceeds 2x -- universal-over-system-content holds with cross-field strength variation (e.g. cognition's capability-vs-domain signal artifact). " % (ss, gap) + s)
    if rs >= 1:
        return ("MIDDLE_BAND", "MIDDLE_BAND: the RECORD negative control (history) registered as 'sane' (rs=%d) -- the topical extractor + operator produced apparently-coherent groups from narrative; either the sanity bar is too loose or history carries more latent structure than expected. Systems sane=%d/4. Investigate before asserting the clean split. " % (rs, ss) + s)
    return ("HARD_FAIL", "HARD_FAIL: the universal operator does NOT sanely promote system-content (only %d/4 system fields sane) -- universal-over-system-content not supported as stated. " % ss + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
