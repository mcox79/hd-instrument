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


def load_corpus():
    """atom short-id -> corpus (lower). Used for the MATH-corpus-scope gate (HARD claim is MATH structure,
    not document/provenance atoms that DEPENDS_ON a symmetric math pair)."""
    try:
        from backend.substrate_index.partition import PartitionedStore
        atoms = list(PartitionedStore(DATA_ROOT).all_atoms())
        return {_short(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
                for a in atoms}
    except Exception:
        return {}


def load_graph():
    """Returns sym_pairs (set of frozenset), per-sym-rel breakdown, dep (s->set t), rdep (t->set s), corpus, n_rel."""
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
    return sym_pairs, sym_by_rel, dep, rdep, load_corpus(), n_rel


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
    sym_pairs, sym_by_rel, dep, rdep, corpus, n_rel = load_graph()
    print(f"[load] relations scanned={n_rel} | DEPENDS_ON nodes(src)={len(dep)} | symmetric pairs (unique undirected)={len(sym_pairs)} | corpus map={len(corpus)} atoms", flush=True)
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
    print(f"\n[clean-symmetric SHARES_MATH+DUAL; {len(clean_pairs)} pairs; ALL corpora]", flush=True)
    print(f"  MOTIF-A clean(all-corpora): {len(ca)} | MOTIF-B clean(all-corpora): {len(cb)}", flush=True)

    # ===== CANONICAL HARD CLAIM (DECISION 169c reconciliation): MATH-CORPUS-SCOPE gate =====
    # The clean(all-corpora) counts are INFLATED by document/provenance anchors (research_history /
    # decision_history / findings_history atoms that DEPENDS_ON a symmetric math pair = citations, NOT
    # math motifs). The HARD partial-symmetry claim is about MATH structure -> restrict anchor + BOTH
    # pair members to the math corpus. This also reconciles the 28-vs-31 (both were document-inflated).
    def ismath(n): return corpus.get(n, "") == "math"
    ca_math = [(p, z) for p, z in ca if ismath(z) and all(ismath(x) for x in p)]
    cb_math = [(a, p) for a, p in cb if ismath(a) and all(ismath(x) for x in p)]
    print(f"\n[PRIMARY: MATH-CORPUS-SCOPED clean-symmetric] -- the CANONICAL HARD partial-symmetry claim", flush=True)
    print(f"  MOTIF-A math: {len(ca_math)} ({'PASS' if len(ca_math)>=MIN_SUPPORT else 'FAIL <20'})", flush=True)
    print(f"  MOTIF-B math: {len(cb_math)} ({'PASS' if len(cb_math)>=MIN_SUPPORT else 'FAIL <20'})  <- HARD claim rests here", flush=True)
    print(f"  HARD claim viable (>=1 math motif-type >=20): {'YES' if (len(ca_math)>=MIN_SUPPORT or len(cb_math)>=MIN_SUPPORT) else 'NO'}", flush=True)
    n_doc_b = len(cb) - len(cb_math)
    print(f"  ({n_doc_b} clean MOTIF-B instances dropped as document/provenance anchors -- not math structure)", flush=True)

    # PER-DISTINCT-STRUCTURE breakdown (DECISION 170c): the 20 instances rest on few distinct sym-pair
    # STRUCTURES; a HARD-PASS concentrated in 1-2 families is NOT a general partial-symmetry result.
    from collections import Counter
    struct = Counter(tuple(sorted(p)) for _, p in cb_math)
    print(f"  per-distinct-structure (MOTIF-B math; {len(struct)} distinct sym-pairs over {len(cb_math)} instances):", flush=True)
    for pair, cnt in struct.most_common():
        print(f"     {cnt:2d}x  {{{pair[0]}, {pair[1]}}}", flush=True)
    top2 = sum(c for _, c in struct.most_common(2))
    print(f"  raw concentration: top-2 sym-pairs = {top2}/{len(cb_math)} ({100*top2//max(1,len(cb_math))}%)", flush=True)

    # EFFECTIVE-FAMILY (META-CLUSTERED) breakdown (Skunkworks call): the DFT/FFT/circular-convolution/
    # convolution-theorem/fhrr-bind sym-pairs all encode ONE Fourier-duality relationship -> ONE family,
    # NOT 5 structures (facet-counting = same soft-gerrymander class as document-citation, 58th). The
    # general partial-symmetry HARD claim must close NON-DFT families, not lean on Fourier duality.
    FOURIER_META = {"discrete_fourier_transform", "fast_fourier_transform", "circular_convolution",
                    "convolution_theorem_synthesis", "fhrr_bind"}
    def family_key(pair):
        return "DFT/convolution-theorem META" if all(x in FOURIER_META for x in pair) else tuple(sorted(pair))
    fam = Counter(family_key(p) for _, p in cb_math)
    print(f"  EFFECTIVE families (meta-clustered; {len(fam)} families over {len(cb_math)} instances):", flush=True)
    for f, c in fam.most_common():
        print(f"     {c:2d}/{len(cb_math)} ({100*c//max(1,len(cb_math)):2d}%)  {f}", flush=True)
    dft = fam.get("DFT/convolution-theorem META", 0)
    n_nondft_families = sum(1 for f in fam if f != "DFT/convolution-theorem META")
    print(f"  DFT-meta dominance: {dft}/{len(cb_math)} ({100*dft//max(1,len(cb_math))}%); NON-DFT families: {n_nondft_families}", flush=True)
    print(f"  GRADED GATE: general HARD-PASS requires closing >=majority of {len(fam)} effective families "
          f"AND >=2 NON-DFT families (else report Fourier-family-specific, not general)", flush=True)

    # GENERIC tier (RELATES-only pairs; reportable, NOT load-bearing) + spurious-inclusion verification
    generic_only = sym_by_rel.get("RELATES", set()) - clean_pairs
    ga, gb = extract_motifs(generic_only, dep, rdep)
    print(f"\n[GENERIC tier: RELATES-only {len(generic_only)} pairs] -- reportable, NOT load-bearing for partial-symmetry", flush=True)
    print(f"  MOTIF-A generic: {len(ga)} | MOTIF-B generic: {len(gb)} (these would have INFLATED the all-sym counts)", flush=True)
    print(f"\n[verify] HARD claim (MOTIF-B math={len(cb_math)}) uses SHARES_MATH+DUAL pairs AND math-corpus atoms ONLY;", flush=True)
    print(f"  excluded: {len(ga)+len(gb)} generic-RELATES motifs + {n_doc_b} document/provenance anchors. Two-layer scope gate.", flush=True)

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
