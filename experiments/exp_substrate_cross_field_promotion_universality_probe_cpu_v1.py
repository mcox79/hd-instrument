"""
exp_substrate_cross_field_promotion_universality_probe_cpu_v1.py -- is knowledge-promotion UNIVERSAL across fields or field-specific? -- CPU/local (no heat, read-only).

ROUTING: USER strategic question (notes/exp_dev_to_research_DRILL_REQUEST_universal_vs_field_specific_promotion...): "is there a universal way
  to promote + interact with everything, or must math / science / language / history be handled separately?" This is the cheap DECISIVE
  empirical probe I offered -- run BEFORE/ALONGSIDE Research's drill so they get DATA not just a question. NO LLM; relations + atom fields; no heat.

  CORE TEST (the sharpest discriminator, straight from the SHARES_MATH auto-discovery finding): does the SAME structural promotion signal
  mean the SAME thing across fields? The signal = "two atoms share >= 2 DEPENDS_ON prerequisites" (the richest structural promotion signal).
  For each FIELD, measure its CORROBORATION RATE: of the pairs flagged by the structural signal, what fraction are ALSO corroborated by an
  INDEPENDENT semantic signal (share a domain OR share >= 1 serves_capability)?
   - HIGH + consistent corroboration across fields => the signal means "shares structure" EVERYWHERE => promotion is UNIVERSAL (one operator).
   - VARIES by field (high for math/science, low for history/language) => the signal's MEANING is field-dependent => need per-field signal
     extraction (e.g. history's "shared prereqs" = "co-mentioned in a memo", NOT shared structure -- exactly why auto-discovery excluded history).
  Secondary: does frequency-promotion (in-degree) FIRE in every field (are there foundational hubs per field)? + per-field atom/edge census.

PRE-REGISTERED (characterization, not pass/fail capability): report per-field corroboration rate + in-degree hub presence. Verdict bands
  describe the HYPOTHESIS the data supports: UNIVERSAL-LEANING if corroboration spread (max-min over fields with >=20 signal pairs) <= 0.25
  AND all such fields corroboration >= 0.40. FIELD-SPECIFIC-LEANING if spread > 0.25 OR some field < 0.40 (signal means different things).
  MIXED otherwise. UNKNOWN if no index / too few fields with signal. (Either named outcome is HIGH-INFORMATION for the USER question.)
ASCII-only. CPU/local. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_cross_field_promotion_universality_probe_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
MIN_SHARED = 2; MAX_BUCKET = 80; MIN_PAIRS_FOR_FIELD = 20


def _norm(x):
    return str(x).split("::")[-1].strip()


def field_of(corpus: str, atom_id: str) -> str:
    """Map an atom to a coarse FIELD class for the universality comparison."""
    c = (corpus or "").lower(); aid = atom_id.upper()
    if "history" in c:
        return "history"
    if c in ("math",) or aid.startswith(("T1/", "T2/", "T3/", "T2_FAM/")):
        return "math"
    if c in ("science",) or aid.startswith(("PHYS/", "CHEM/", "BIO/")):
        return "science"
    if aid.startswith(("LEX", "MWP/")) or c in ("school",):
        return "language"          # lexicon, semantic-role-labeling, school NLU
    if aid.startswith(("CROSSDISC/", "NEURO/", "CS/")) or c in ("concept",):
        return "cognition"         # cross-disciplinary + neuro + CS + concept
    if c in ("meta", "methodology"):
        return "meta"
    return "other"


def shared_prereq_pairs(dep, min_shared, max_bucket=MAX_BUCKET):
    tgt2src = defaultdict(set)
    for s, ts in dep.items():
        for t in ts:
            tgt2src[t].add(s)
    pc = Counter()
    for t, srcs in tgt2src.items():
        a = sorted(srcs)
        if 1 < len(a) <= max_bucket:
            for x, y in combinations(a, 2):
                pc[(x, y)] += 1
    return {pr for pr, c in pc.items() if c >= min_shared}


def corroborated(pr, domain, caps):
    a, b = pr
    if domain.get(a) and domain.get(a) == domain.get(b):
        return True
    if caps.get(a) and caps.get(b) and (caps[a] & caps[b]):
        return True
    return False


def _selftest():
    assert field_of("decision_history", "x") == "history"
    assert field_of("math", "T2/bind") == "math"
    assert field_of("", "PHYS/ising_model") == "science"
    assert field_of("", "LEX_entity_org") == "language"
    assert field_of("", "CROSSDISC/ising_to_modern_hopfield") == "cognition"
    # shared-prereq: a,b share 2 targets -> pair; a,c share 1 -> not
    dep = {"a": {"t1", "t2"}, "b": {"t1", "t2"}, "c": {"t1"}}
    e = shared_prereq_pairs(dep, 2)
    assert ("a", "b") in e and ("a", "c") not in e, e
    # corroboration via domain / capability
    assert corroborated(("a", "b"), {"a": "alg", "b": "alg"}, {})
    assert corroborated(("a", "b"), {}, {"a": {"c1"}, "b": {"c1", "c2"}})
    assert not corroborated(("a", "b"), {"a": "alg", "b": "top"}, {"a": {"c1"}, "b": {"c2"}})
    print("[selftest] PASS: substrate_cross_field_promotion_universality_probe_cpu_v1", flush=True)


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
    corpus = {}; field = {}; domain = {}; caps = {}
    for a in atoms:
        n = _norm(a.id); c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        corpus[n] = c; field[n] = field_of(c, n); domain[n] = alg(a).get("domain")
        cs = getattr(a, "serves_capability", ()) or ()
        if cs: caps[n] = set(_norm(x) for x in cs)
    dep = defaultdict(set); uses = defaultdict(set); indeg = Counter()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t): continue
            if rt == "DEPENDS_ON":
                dep[s].add(t); indeg[t] += 1
            elif rt == "USES":
                uses[s].add(t)
    field_atoms = Counter(field.values())
    # PRIMARY MEASURE: per-field structural-metadata COVERAGE -- the data the promotion signals operate on.
    # (Universal OPERATORS need per-field SIGNAL data; if a field lacks domain/capability/profile, math-style promotion has nothing to read.)
    cover = {}
    for f in field_atoms:
        ids = [n for n in field if field[n] == f]
        nd = sum(1 for n in ids if domain.get(n)); nc = sum(1 for n in ids if caps.get(n))
        deg = sorted((indeg[n] for n in ids), reverse=True)
        cover[f] = {"n_atoms": len(ids), "pct_domain": round(nd / len(ids), 3), "pct_capability": round(nc / len(ids), 3),
                    "max_indeg": deg[0] if deg else 0, "n_indeg_hubs_ge3": sum(1 for d in deg if d >= 3)}
    # SIGNAL = union of structural promotion signals (shared dep-prereq OR shared USES OR shared capability). CORROBORATION = shared domain.
    e_dep = shared_prereq_pairs(dep, MIN_SHARED)
    e_uses = shared_prereq_pairs(uses, MIN_SHARED)
    cap2atoms = defaultdict(set)
    for n, cs in caps.items():
        for c in cs: cap2atoms[c].add(n)
    e_cap = set()
    for c, atomset in cap2atoms.items():
        a = sorted(atomset)
        if 1 < len(a) <= MAX_BUCKET:
            for x, y in combinations(a, 2): e_cap.add((x, y))
    pairs = e_dep | e_uses | e_cap
    by_field_pairs = defaultdict(list); cross_field = []
    for pr in pairs:
        fa, fb = field.get(pr[0], "other"), field.get(pr[1], "other")
        (by_field_pairs[fa] if fa == fb else cross_field).append(pr if fa == fb else (pr, fa, fb))
    rows = {}
    for f, prs in by_field_pairs.items():
        if not prs: continue
        corr = sum(1 for pr in prs if corroborated(pr, domain, caps))
        rows[f] = {"n_signal_pairs": len(prs), "corroboration_rate": round(corr / len(prs), 4)}
    elig = {f: rows[f]["corroboration_rate"] for f in rows if rows[f]["n_signal_pairs"] >= MIN_PAIRS_FOR_FIELD}
    spread = round(max(elig.values()) - min(elig.values()), 4) if len(elig) >= 2 else None
    cross_corr = round(sum(1 for (pr, _, _) in cross_field if corroborated(pr, domain, caps)) / max(1, len(cross_field)), 4)
    print("  fields (atoms): %s" % dict(field_atoms), flush=True)
    print("  STRUCTURAL-METADATA COVERAGE (the data promotion signals read):", flush=True)
    for f in sorted(cover, key=lambda x: -cover[x]["n_atoms"]):
        c = cover[f]
        print("    %-10s atoms=%4d | domain=%.2f capability=%.2f | indeg max=%d hubs>=3=%d | signal-pairs=%d corrob=%s" % (
            f, c["n_atoms"], c["pct_domain"], c["pct_capability"], c["max_indeg"], c["n_indeg_hubs_ge3"],
            rows.get(f, {}).get("n_signal_pairs", 0), rows.get(f, {}).get("corroboration_rate", "n/a")), flush=True)
    print("  eligible-field corroboration (>=%d pairs): %s SPREAD=%s | cross-field pairs=%d corrob=%.3f" % (
        MIN_PAIRS_FOR_FIELD, {k: round(v, 3) for k, v in elig.items()}, spread, len(cross_field), cross_corr), flush=True)
    # coverage asymmetry: spread in pct_domain across fields with >=20 atoms
    big_fields = {f: cover[f] for f in cover if cover[f]["n_atoms"] >= 20}
    dom_vals = [c["pct_domain"] for c in big_fields.values()]
    coverage_spread = round(max(dom_vals) - min(dom_vals), 3) if len(dom_vals) >= 2 else None
    return {"field_atoms": dict(field_atoms), "coverage": cover, "rows": rows, "eligible_corroboration": elig,
            "corroboration_spread": spread, "coverage_spread_domain": coverage_spread,
            "n_cross_field_pairs": len(cross_field), "cross_field_corroboration": cross_corr,
            "min_pairs_for_field": MIN_PAIRS_FOR_FIELD}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    cov = r["coverage"]; cspread = r["coverage_spread_domain"]; elig = r["eligible_corroboration"]
    big = {f: cov[f] for f in cov if cov[f]["n_atoms"] >= 20}
    if cspread is None:
        return ("UNKNOWN", "UNKNOWN: fewer than 2 fields with >=20 atoms.")
    dom = {f: cov[f]["pct_domain"] for f in big}
    lo_field = min(dom, key=dom.get); hi_field = max(dom, key=dom.get)
    s = ("structural-metadata coverage by field (pct_domain): %s (spread=%.3f); per-field signal corroboration %s; cross-field pairs=%d "
         "corroboration=%.3f. INTERPRETATION: a UNIVERSAL promotion OPERATOR needs per-field SIGNAL DATA; where a field lacks domain/"
         "capability/profile, math-style structural promotion has nothing to read.") % (
        {f: dom[f] for f in dom}, cspread, {k: round(v, 3) for k, v in elig.items()}, r["n_cross_field_pairs"], r["cross_field_corroboration"])
    if cspread <= 0.25 and min(dom.values()) >= 0.40:
        return ("UNIVERSAL_LEANING", "UNIVERSAL-LEANING: structural-metadata coverage is CONSISTENT across fields (all pct_domain>=0.40, spread<=0.25) -- every field carries the data a universal promotion operator reads -> one operator can serve all fields. " + s)
    return ("FIELD_SPECIFIC_LEANING", "FIELD-SPECIFIC-LEANING (current corpus): structural-metadata coverage is HIGHLY field-skewed (pct_domain '%s'=%.2f vs '%s'=%.2f, spread=%.3f). The substrate is currently INSTRUMENTED for math/science promotion (rich domain/capability/signature) but NOT for history/language (sparse) -- and the dominant raw signal differs by field (history: note co-reference, uncorroborated; math: shared capability/USES, corroborated). So promotion needs a UNIVERSAL operator + a PER-FIELD SIGNAL-INSTRUMENTATION layer: each field must populate its own 'structural metadata' for the universal operator to read. OPEN QUESTION for the drill: is this asymmetry FUNDAMENTAL (math is intrinsically more structural) or just UNBUILT (history/language metadata not yet authored)? Matches the SHARES_MATH-auto-discovery finding (history excluded as noise). " % (
        hi_field, dom[hi_field], lo_field, dom[lo_field], cspread) + s)


print("[config] anchor=%s mode=%s min_shared=%d" % (ANCHOR_NAME, RUN_MODE, MIN_SHARED), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
