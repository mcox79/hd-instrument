"""
exp_substrate_shares_math_auto_discovery_structural_signals_cpu_v1.py -- auto-discover SHARES_MATH candidate edges from INDEPENDENT structural signals -- CPU/local (no heat, read-only).

ROUTING: Research design (research_to_testbed_exp_dev_SHARES_MATH_auto_discovery_cell_DESIGN_independent_structural_signals_unblocks_KP_P3...).
  Substrate has 0 SHARES_MATH edges -> KP P3 (bisimulation promotion), Pi/Sigma id-type, CHTV-2 alpha-equivalence are all GATED. This cell
  AUTO-DISCOVERS candidate SHARES_MATH edges (atoms that share underlying mathematics) from structural signals ORTHOGONAL to bge/codebook
  geometry -> preserves P3's independence (P4 used composite_hrr cosine; this uses relations + algebra-dict fields, NOT geometry). READ-ONLY:
  emits a scored candidate edge list for Testbed review+ingest (meta::RULE_authoring_substrate_queries_first). NO LLM; numpy-free; no heat.

  VERIFY-BEFORE-BUILD (GREP-FIRST per memory rule): Research's design referenced fields ABSENT in the current schema -- algebra_dict.axioms (0),
  science_algebra_category (0), atom.equivalences (0). I adapted the 5 signals to the ACTUAL populated structural fields (flagged to Research):
   S1 algebra-profile match     : shared (domain, operation_type, signature_input_type, signature_output_type, complexity_class) sub-tuple.
   S2 shared DEPENDS_ON prereqs : >= MIN_SHARED common DEPENDS_ON targets (richest signal; 2220 edges).
   S3 serves_capability overlap : >= 1 shared capability (caps are specific PP-### ids -> 1 is meaningful).
   S4 SPECIALIZES/INSTANCE_OF   : shared parent class (A SPECIALIZES X & B INSTANCE_OF X, or symmetric).
   S5 shared USES targets       : >= MIN_SHARED common USES targets.
  PRECISION GUARD (probe finding): the shared-prereq signal over the FULL corpus picks up *_history narrative atoms that co-reference notes
  (a 136-atom noise blob). We RESTRICT candidate atoms to STRUCTURED/math corpora (exclude *_history) so SHARES_MATH means shared MATH.

PRE-REGISTERED: a candidate edge needs a STRONG single signal (S2>=2 shared prereqs, OR S5>=2 shared USES, OR S4 parent cycle, OR S3 shared
  capability) OR (S1 algebra-profile match AND any weak corroboration). Then connected components of candidate edges = SHARES_MATH groups.
  HARD-PASS >= 10 components of size >= 3 (directly sufficient to unblock P3 HARD-PASS) AND >= 90pct of grouped atoms are math-corpora.
  MIDDLE 3-9 components size>=3. HARD-FAIL < 3 (structural signals too sparse to seed SHARES_MATH). UNKNOWN if no index.
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
ANCHOR_NAME = "substrate_shares_math_auto_discovery_structural_signals_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
MIN_SHARED = 2; MAX_BUCKET = 60; SIG_FIELDS = ("domain", "operation_type", "signature_input_type", "signature_output_type", "complexity_class")


def _norm(x):
    return str(x).split("::")[-1].strip()


def _is_math_corpus(c: str) -> bool:
    c = (c or "").lower()
    return bool(c) and ("history" not in c)        # exclude *_history narrative; keep math/science/concept/school/meta/cross-disc/etc.


def components(edges):
    adj = defaultdict(set)
    for x, y in edges:
        adj[x].add(y); adj[y].add(x)
    seen = set(); comps = []
    for n in list(adj):
        if n in seen:
            continue
        stack = [n]; comp = {n}; seen.add(n)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); comp.add(v); stack.append(v)
        comps.append(sorted(comp))
    return comps


def pairs_from_buckets(key2atoms, min_shared_is_bucket=True, max_bucket=MAX_BUCKET):
    """If min_shared_is_bucket: atoms sharing the SAME key are pairwise candidates (S1/S3/S4). Returns Counter of pairs."""
    pc = Counter()
    for k, atomset in key2atoms.items():
        a = sorted(atomset)
        if 1 < len(a) <= max_bucket:
            for x, y in combinations(a, 2):
                pc[(x, y)] += 1
    return pc


def shared_target_pairs(adjmap, min_shared, max_bucket=MAX_BUCKET):
    """Atoms sharing >= min_shared common targets (S2 DEPENDS_ON, S5 USES). Invert target->sources, count co-occurrence."""
    tgt2src = defaultdict(set)
    for s, ts in adjmap.items():
        for t in ts:
            tgt2src[t].add(s)
    pc = Counter()
    for t, srcs in tgt2src.items():
        a = sorted(srcs)
        if 1 < len(a) <= max_bucket:
            for x, y in combinations(a, 2):
                pc[(x, y)] += 1
    return {pr for pr, c in pc.items() if c >= min_shared}


def _selftest():
    # components
    cs = components({("a", "b"), ("b", "c"), ("x", "y")})
    assert sorted(len(c) for c in cs) == [2, 3], cs
    # shared_target_pairs: a,b share targets t1,t2 (>=2) -> edge; a,c share only t1 -> no edge
    adjm = {"a": {"t1", "t2"}, "b": {"t1", "t2"}, "c": {"t1"}}
    e = shared_target_pairs(adjm, 2)
    assert ("a", "b") in e and ("a", "c") not in e, e
    # bucket pairs: same key -> pair
    pc = pairs_from_buckets({"k": {"a", "b", "c"}, "j": {"d"}})
    assert pc[("a", "b")] == 1 and ("d", "x") not in pc
    # math-corpus filter excludes history
    assert _is_math_corpus("math") and _is_math_corpus("CROSSDISC") and not _is_math_corpus("decision_history") and not _is_math_corpus("")
    print("[selftest] PASS: substrate_shares_math_auto_discovery_structural_signals_cpu_v1", flush=True)


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
    corpus = {_norm(a.id): str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower() for a in atoms}
    math_ids = {n for n, c in corpus.items() if _is_math_corpus(c)}
    sigprofile = {}; caps = {}
    for a in atoms:
        n = _norm(a.id)
        if n not in math_ids:
            continue
        al = alg(a)
        prof = tuple(al.get(f) for f in SIG_FIELDS)
        if sum(1 for v in prof if v) >= 3:                 # need >=3 populated subfields to be a meaningful profile
            sigprofile[n] = prof
        cs = getattr(a, "serves_capability", ()) or ()
        if cs:
            caps[n] = set(_norm(c) for c in cs)
    # relation adjacency (restricted to math atoms on the SOURCE side)
    dep = defaultdict(set); uses = defaultdict(set); spec = defaultdict(set); inst = defaultdict(set)
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            rt = (r.get("rel_type", "") or "").upper(); s = _norm(r.get("src_id", "")); t = _norm(r.get("tgt_id", ""))
            if not (s and t and s != t and s in math_ids): continue
            if rt == "DEPENDS_ON": dep[s].add(t)
            elif rt == "USES": uses[s].add(t)
            elif rt == "SPECIALIZES": spec[s].add(t)
            elif rt == "INSTANCE_OF": inst[s].add(t)
    # signals
    e_dep = shared_target_pairs(dep, MIN_SHARED)
    e_uses = shared_target_pairs(uses, MIN_SHARED)
    cap2atoms = defaultdict(set)
    for n, cs in caps.items():
        for c in cs: cap2atoms[c].add(n)
    e_cap = {pr for pr in pairs_from_buckets(cap2atoms)}
    prof2atoms = defaultdict(set)
    for n, p in sigprofile.items(): prof2atoms[p].add(n)
    e_prof = {pr for pr in pairs_from_buckets(prof2atoms)}
    # S4 specialize/instance shared parent
    e_si = set()
    parent2spec = defaultdict(set); parent2inst = defaultdict(set)
    for n, ts in spec.items():
        for t in ts: parent2spec[t].add(n)
    for n, ts in inst.items():
        for t in ts: parent2inst[t].add(n)
    for parent in set(parent2spec) | set(parent2inst):
        grp = sorted(parent2spec[parent] | parent2inst[parent])
        if 1 < len(grp) <= MAX_BUCKET:
            for x, y in combinations(grp, 2): e_si.add((x, y))
    # aggregate: STRONG single signal OR (profile AND any weak corroboration)
    strong = e_dep | e_uses | e_cap | e_si
    edges = set(strong)
    for pr in e_prof:
        if pr in strong or pr in e_cap:
            edges.add(pr)                                  # profile match counts when corroborated
    # provenance per edge
    def prov(pr):
        p = []
        if pr in e_dep: p.append("dep>=2")
        if pr in e_uses: p.append("uses>=2")
        if pr in e_cap: p.append("cap")
        if pr in e_si: p.append("spec/inst")
        if pr in e_prof: p.append("algprofile")
        return p
    comps = components(edges)
    big = [c for c in comps if len(c) >= 3]
    big.sort(key=len, reverse=True)
    grouped_atoms = [a for c in big for a in c]
    math_frac = round(sum(1 for a in grouped_atoms if a in math_ids) / max(1, len(grouped_atoms)), 4)
    sig_counter = Counter()
    for pr in edges:
        for s in prov(pr): sig_counter[s] += 1
    print("  math atoms=%d | candidate edges=%d (signals: %s)" % (len(math_ids), len(edges), dict(sig_counter)), flush=True)
    print("  SHARES_MATH groups (components size>=3): %d | sizes=%s | math-fraction=%.3f" % (
        len(big), [len(c) for c in big[:14]], math_frac), flush=True)
    out_groups = []
    for c in big[:40]:
        # representative shared signal: most common provenance among intra-group edges
        intra = [pr for pr in edges if pr[0] in set(c) and pr[1] in set(c)]
        pc = Counter(s for pr in intra for s in prov(pr))
        out_groups.append({"size": len(c), "members": c[:14], "dominant_signal": pc.most_common(1)[0][0] if pc else "?"})
        print("    GROUP size=%2d via=%s :: %s" % (len(c), out_groups[-1]["dominant_signal"], c[:6]), flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    edge_list = [{"a": x, "b": y, "signals": prov((x, y))} for (x, y) in sorted(edges)]
    (bf / "shares_math_auto_discovery_candidates.json").write_text(json.dumps(
        {"candidate_edges": edge_list, "groups": out_groups, "n_math_atoms": len(math_ids),
         "signal_counts": dict(sig_counter), "min_shared": MIN_SHARED}, indent=2), encoding="utf-8")
    return {"n_math_atoms": len(math_ids), "n_edges": len(edges), "n_groups_ge3": len(big),
            "group_sizes": [len(c) for c in big], "math_fraction": math_frac, "signal_counts": dict(sig_counter),
            "groups": out_groups[:20]}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    n = r["n_groups_ge3"]; mf = r["math_fraction"]
    s = ("%d candidate SHARES_MATH edges over %d math atoms (signals %s) -> %d connected groups size>=3 (sizes %s), math-fraction=%.3f; "
         "saved bench_reports/shares_math_auto_discovery_candidates.json (READ-ONLY -- Testbed reviews+ingests as SHARES_MATH edges, then KP P3 runs)") % (
        r["n_edges"], r["n_math_atoms"], r["signal_counts"], n, r["group_sizes"][:14], mf)
    if n >= 10 and mf >= 0.90:
        return ("HARD_PASS", "HARD_PASS: structural auto-discovery seeds %d>=10 SHARES_MATH groups (size>=3, %.0f%% math) from signals ORTHOGONAL to codebook geometry -- directly sufficient to unblock KP P3 as an INDEPENDENT 3rd mechanism (-> aggregate KP 3-of-5). " % (n, mf * 100) + s)
    if n >= 3:
        return ("MIDDLE_BAND", "MIDDLE_BAND: %d SHARES_MATH groups (3-9, math-fraction %.3f) -- enough to RUN P3 (it will produce >=3 bisimulation classes, bisim-refinement may split the larger groups toward 10) but below the >=10 HARD-PASS; structural signals partially seed SHARES_MATH at the current corpus. " % (n, mf) + s)
    return ("HARD_FAIL", "HARD_FAIL: only %d SHARES_MATH groups -- structural signals too sparse to seed SHARES_MATH bisimulation at the current corpus. " % n + s)


print("[config] anchor=%s mode=%s min_shared=%d sig_fields=%s" % (ANCHOR_NAME, RUN_MODE, MIN_SHARED, SIG_FIELDS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
