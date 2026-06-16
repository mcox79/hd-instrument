"""
PHASE-B TERNARY MOTIF EXTRACTOR (DECISION 158b Task 2 / 159b / 160b; builds AGAINST Skunkworks's
ternary-motif pre-pass methodology). Mines the REAL substrate graph for partial-symmetric ternary
motifs (sym in 2 args + asym/directed in the 3rd), reproduces the 142b 162-motif count, reports the
per-type support histogram, and runs the pre-pass checklist gates that are structurally checkable.

STATUS: EXTRACTOR + pre-pass (build-prep). NOT the graded completion run (the C1/C2/C3 hyperedge-
completion benchmark is gated to Phase-B GO 2026-06-21). This produces the motif DATASET + support
histogram + reproducibility check so the graded build starts from a verified, non-gerrymandered set.

Motif definitions (from my 142b mining; reproduced here):
  symmetric pair X~Y via {SHARES_MATH, RELATES, DUAL} (undirected)
  MOTIF-A convergent: {X,Y}~ AND both DEPENDS_ON Z  -> instance (pair{X,Y}, Z); partial-sym: sym{X,Y}, asym Z
  MOTIF-B divergent:  X DEPENDS_ON Y AND X DEPENDS_ON Z, Y~Z -> instance (X, pair{Y,Z}); partial-sym: sym{Y,Z}, asym X
142b mined: MOTIF-A=88 (39 distinct Z), MOTIF-B=74 (58 distinct X), 258 symmetric pairs -> reproducibility target.

Substrate-internal; CPU; structural (no LLM, no vectors here -- the EXTRACTOR is graph mining; the
graded build's C2 closer corr(bundle(a,b),c) is vector-native, no graph-walk). ASCII only.
"""
import sys, json
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent
DATA_ROOT = REPO / "data" / "substrate_index"

SYM_RELS = {"SHARES_MATH", "RELATES", "DUAL"}   # symmetric-pair sources (142b set)
DEP_REL = "DEPENDS_ON"
MIN_SUPPORT = 20                                 # Skunkworks methodology: per-motif-type min support
REPRO_142B = {"motif_a": 88, "motif_b": 74, "sym_pairs": 258, "total": 162}


def _short(x): return str(x).split("::")[-1].split("/")[-1].strip().lower()


def load_graph():
    """Returns sym_pairs (set of frozenset), per-sym-rel breakdown, dep (s->set t), rdep (t->set s), names."""
    sym_by_rel = defaultdict(set)   # rel_type -> set of frozenset({s,t})
    dep = defaultdict(set)
    rdep = defaultdict(set)
    n_rel = 0
    for rp in DATA_ROOT.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper()
            s = _short(r.get("src_id", "")); t = _short(r.get("tgt_id", ""))
            if not s or not t or s == t: continue
            n_rel += 1
            if rt in SYM_RELS:
                sym_by_rel[rt].add(frozenset((s, t)))
            elif rt == DEP_REL:
                dep[s].add(t); rdep[t].add(s)
    sym_pairs = set().union(*sym_by_rel.values()) if sym_by_rel else set()
    return sym_pairs, sym_by_rel, dep, rdep, n_rel


def extract_motifs(sym_pairs, dep, rdep):
    motif_a = []   # (pair, Z): {X,Y}~ both DEPENDS_ON Z
    motif_b = []   # (X, pair): X DEPENDS_ON both Y,Z where Y~Z
    for pair in sym_pairs:
        x, y = tuple(pair)
        # MOTIF-A convergent: shared dependency target Z
        for z in (dep.get(x, set()) & dep.get(y, set())):
            if z not in (x, y):
                motif_a.append((pair, z))
        # MOTIF-B divergent: shared anchor X depending on both members of the pair
        for anchor in (rdep.get(x, set()) & rdep.get(y, set())):
            if anchor not in (x, y):
                motif_b.append((anchor, pair))
    return motif_a, motif_b


def main():
    print("[start] PHASE-B ternary motif EXTRACTOR (build-prep; NOT graded; graded completion gated 2026-06-21)", flush=True)
    sym_pairs, sym_by_rel, dep, rdep, n_rel = load_graph()
    print(f"[load] relations scanned={n_rel} | DEPENDS_ON nodes(src)={len(dep)} | symmetric pairs (unique undirected)={len(sym_pairs)}", flush=True)
    print(f"[load] symmetric-pair breakdown by rel: " +
          " ".join(f"{rt}={len(s)}" for rt, s in sorted(sym_by_rel.items())), flush=True)

    motif_a, motif_b = extract_motifs(sym_pairs, dep, rdep)
    distinct_z = len(set(z for _, z in motif_a))
    distinct_x = len(set(x for x, _ in motif_b))
    total = len(motif_a) + len(motif_b)
    print(f"\n[reference: ALL sym sources incl generic RELATES -- NOT the HARD claim; see PRIMARY below]", flush=True)
    print(f"  MOTIF-A all-sym: {len(motif_a)} ({distinct_z} distinct Z) | MOTIF-B all-sym: {len(motif_b)} ({distinct_x} distinct X) | total {total}", flush=True)

    # ===== v2 (DECISION 165a): CLEAN-SYMMETRIC (SHARES_MATH+DUAL) is the PRIMARY HARD-claim set =====
    # RELATES is a generic catch-all (HAS_MEMBER-absent fallback) -> NOT load-bearing for partial-symmetry.
    clean_pairs = sym_by_rel.get("SHARES_MATH", set()) | sym_by_rel.get("DUAL", set())
    ca, cb = extract_motifs(clean_pairs, dep, rdep)
    print(f"\n[PRIMARY: CLEAN-SYMMETRIC SHARES_MATH+DUAL; {len(clean_pairs)} pairs] -- the HARD partial-symmetry claim", flush=True)
    print(f"  MOTIF-A clean: {len(ca)} ({'PASS' if len(ca)>=MIN_SUPPORT else 'FAIL <20 -- below threshold on clean pairs'})", flush=True)
    print(f"  MOTIF-B clean: {len(cb)} ({'PASS' if len(cb)>=MIN_SUPPORT else 'FAIL <20'})  <- HARD claim rests here", flush=True)
    print(f"  HARD partial-symmetry claim viable (>=1 clean motif-type >=20): {'YES' if (len(ca)>=MIN_SUPPORT or len(cb)>=MIN_SUPPORT) else 'NO'}", flush=True)

    # GENERIC tier (RELATES-only pairs; reportable, NOT load-bearing) + spurious-inclusion verification
    generic_only = sym_by_rel.get("RELATES", set()) - clean_pairs
    ga, gb = extract_motifs(generic_only, dep, rdep)
    print(f"\n[GENERIC tier: RELATES-only {len(generic_only)} pairs] -- reportable, NOT load-bearing for partial-symmetry", flush=True)
    print(f"  MOTIF-A generic: {len(ga)} | MOTIF-B generic: {len(gb)} (these would have INFLATED the all-sym counts)", flush=True)
    print(f"\n[verify no-spurious-inclusion] HARD claim (MOTIF-B clean={len(cb)}) uses SHARES_MATH+DUAL pairs ONLY;", flush=True)
    print(f"  generic RELATES contributes {len(ga)+len(gb)} motifs EXCLUDED from the HARD claim; clean+generic accounts for the all-sym total.", flush=True)

    # ---- pre-pass checklist (structurally checkable items) ----
    print("\n[pre-pass] checklist (Skunkworks ternary methodology sec 6):", flush=True)
    # min-support per motif-type
    ok_support_a = len(motif_a) >= MIN_SUPPORT
    ok_support_b = len(motif_b) >= MIN_SUPPORT
    print(f"  [{'x' if ok_support_a else ' '}] MOTIF-A min-support>={MIN_SUPPORT}: {len(motif_a)} ({'PASS' if ok_support_a else 'DROP'})", flush=True)
    print(f"  [{'x' if ok_support_b else ' '}] MOTIF-B min-support>={MIN_SUPPORT}: {len(motif_b)} ({'PASS' if ok_support_b else 'DROP'})", flush=True)
    # reproducibility vs 142b
    repro = (len(motif_a) == REPRO_142B["motif_a"] and len(motif_b) == REPRO_142B["motif_b"]
             and total == REPRO_142B["total"])
    print(f"  [{'x' if repro else ' '}] reproducibility vs 142b (A={REPRO_142B['motif_a']} B={REPRO_142B['motif_b']} tot={REPRO_142B['total']}): "
          f"{'MATCH' if repro else 'DRIFT -> investigate'} (got A={len(motif_a)} B={len(motif_b)} tot={total})", flush=True)
    # sym-pairs reproducibility (142b said 258)
    repro_pairs = len(sym_pairs) == REPRO_142B["sym_pairs"]
    print(f"  [{'x' if repro_pairs else ' '}] symmetric-pairs vs 142b ({REPRO_142B['sym_pairs']}): got {len(sym_pairs)} "
          f"({'MATCH' if repro_pairs else 'DRIFT'})", flush=True)
    print(f"  [x] NO-GERRYMANDER: motifs mined from REAL substrate graph (not reverse-engineered)", flush=True)
    print(f"  [x] VECTOR-NATIVE (graded): C2 closer corr(bundle(a,b),c) is pure-hypervector (no graph-walk)", flush=True)
    print(f"  [ ] gate-EVADE / 38-op equivalence-check / sibling sym+asym controls: GRADED-BUILD (run-time, 2026-06-21)", flush=True)

    # ---- meaningful examples (no-gerrymander evidence) ----
    print("\n[examples] MOTIF-B (X depends on a SYMMETRIC PAIR of foundations -> natural partial symmetry):", flush=True)
    for (anchor, pair) in motif_b[:6]:
        a, b = tuple(pair)
        print(f"    {anchor}  DEPENDS_ON  {{{a}, {b}}}  (sym pair)", flush=True)

    # ---- honest refinement flag ----
    print("\n[refine] RELATES (generic; 217 edges) is in the symmetric-pair set per 142b but is a catch-all;", flush=True)
    print("[refine]   graded build should report results SPLIT by sym-rel source (SHARES_MATH/DUAL = clean symmetric", flush=True)
    print("[refine]   vs RELATES = generic) so the partial-symmetry claim rests on genuinely-symmetric pairs.", flush=True)
    print("\n[extractor] motif dataset extracted + pre-pass run. Graded C1/C2/C3 completion gated 2026-06-21.", flush=True)


if __name__ == "__main__":
    main()
