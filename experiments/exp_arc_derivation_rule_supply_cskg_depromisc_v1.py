"""arc_derivation_rule_supply_cskg_depromisc_v1 -- cheap DECISIVE salvage probe on the CSKG rule supply.

ONE VARIABLE = CSKG DE-PROMISCUIFICATION (how the CSKG supply is inducted+filtered to remove the
promiscuous hubs). EVERYTHING ELSE reused UNCHANGED from the parent rule-supply probe
(exp_arc_derivation_rule_supply_cskg_v1, imported as rs; which imports the clean-node gate cn):
  - SAME node-identity: cn.NegAwareEncoder + head-lemma gate + PolarityLexicon merge-gate
  - SAME graph builder cn.build_graph_gated, SAME depth<=3 meet-in-middle gate, SAME cn.eval_arm
  - SAME ~100 ARC-Challenge Qs (same seed permutation), SAME word->node mapping (cos>=tau_unify)
  - SAME thresholds tau_unify=0.85, tau_sim=0.60, depth=3 (NOT tuned to force a band)
  - SAME CSKG load + licensing (rs.load_cskg_licensed) -> the licensed row pool is IDENTICAL.
  - SAME parent induction (rs.induce_subgraph) reused ONLY for the cskg_unfiltered POSITIVE CONTROL.

WHY (parent VET-pending but MEASURED on disk, data/exp_arc_derivation_rule_supply_cskg_v1/metrics.json):
CSKG's licensed rows lifted correct-choice coverage 0.07 (WorldTree) -> 0.56 (CSKG) but with NO
selectivity: typed_gap = 0.0516 (correct 0.56 ~= mean-wrong ~0.51); deg-571 'person'/water/food mega-hubs;
VACUOUS chains (conductor -> table-salt via water->cooking->eat). THE QUESTION: is there a SCIENCE-CAUSAL
CORE hidden under the promiscuous hubs (-> de-hubbing REVEALS real selectivity = SALVAGE) or does CSKG
fundamentally lack science causation between the right concepts (-> NEED_EXTRACTION)?

CRITICAL INDUCTION CONFOUND (parent-VET finding, coordinator 2026-07-25, credited): the parent
rs.induce_subgraph has a DEAD `max_deg_induce` param (never referenced in body) -> NO induction-time
degree cap, AND it ranks candidates by `-relevant_degree` and keeps the top budget -> it ACTIVELY SELECTS
the mega-hubs (guarantees deg-571 'person' survives). So a NAIVE post-hoc hub-cap on that hub-preselected
set is a starved-residue artifact (the induction already discarded the low-degree science nodes before the
cap ran) -- it CANNOT distinguish intrinsic CSKG promiscuity from the induction bias. This cell therefore
implements a REAL de-promiscuification: a DEBIASED induction (`induce_subgraph_capped`) that caps node
degree AT INDUCTION time using the FULL-licensed-CSKG degree AND selects by RELEVANCE or RANDOM (NOT by
degree), so the hub is never manufactured and the low-degree science core is retained within budget.

DE-PROMISCUIFIERS (the ONE variable; each fed to the IDENTICAL gate):
  1. cskg_unfiltered : POSITIVE CONTROL -- parent (degree-ranked) induction; reproduce parent anchor
                       (expect cov ~0.56, typed_gap ~0.052, max_deg ~571) at MATCHED regime. tol 0.10 (Gate D).
  2. worldtree       : ANCHOR (small licensed science-curriculum corpus; expect cov ~0.07).
  3. cskg_hubcap8    : DEBIASED induction, degree cap 8 (full-CSKG degree), RELEVANCE-select (non-degree).
  4. cskg_hubcap3    : DEBIASED induction, degree cap 3, RELEVANCE-select.
  5. cskg_random16   : DEBIASED induction, degree cap 16, RANDOM-within-budget (fully unbiased sample).
  6. cskg_science    : hubcap8 debiased induction + BOTH-endpoint WorldTree-science-vocab filter.
  7. cskg_precise    : hubcap8 debiased induction + tightest relations {CAUSE, REQUIRES, IFTHEN} only
                       (drop loose functional USEDFOR=UsedFor/CapableOf/ReceivesAction, SOURCEOF=MadeOf).
  8. cskg_combined   : hubcap8 debiased induction + precise-relation + science-term (tightest).
  The science-term list = WorldTree tablestore content words (independent science curriculum vocab, NOT
  ARC leakage). Per arm we REPORT max-degree-ACHIEVED so the cap firing is verifiable (must be << 571).

METRICS + PRE-REGISTERED BANDS (a priori; STRAIGHT report; NOT tuned to force SALVAGE). Per arm:
  correct-choice coverage (cov), typed SELECTIVITY GAP (cov - mean-wrong), untyped-null gap (promiscuity
  control), max typed node-degree ACHIEVED (mega-hub watch), n rows kept, n nodes. HONESTY GUARD =
  coverage AND selectivity tracked TOGETHER; a gap raised only by collapsing coverage is NOT salvage.
  Per-arm salvage classifier (classify_salvage):
    SALVAGE        : cov >= 0.30 AND typed_gap >= 0.15 -> de-hubbing REVEALED a masked science-causal
                     signal; a filtered CSKG is a viable cheap supply.
    NEED_EXTRACTION: typed_gap < 0.05 OR cov < 0.15 -> no selectivity survives, OR the filter that killed
                     the promiscuity also killed the coverage = no science-causal core.
    MIDDLE_BAND    : otherwise (cov 0.15-0.30 and/or gap 0.05-0.15) -> report straight.
  OVERALL VERDICT:
    SALVAGE         : ANY de-promiscuifier arm (hubcap/random/science/precise/combined) lands SALVAGE.
    NEED_EXTRACTION : NO arm SALVAGE, AND every arm that MATERIALLY removed promiscuity (max_deg dropped
                      >=30% vs anchor OR rows cut >=30%) stays gap<0.15 -> the promiscuity WAS the only
                      connective tissue; redirect to science-precise rule EXTRACTION (text/curated).
    MIDDLE_BAND     : otherwise -> report straight (no clean salvage, no clean need-extraction).
  Glass-box: surviving correct-choice chains for the best de-promiscuified arm are recorded (science-causal
  real derivation vs single-word bridge?) -- a manual read reported by the agent, not auto-scored.

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic
(fixed seed, numpy default_rng, sorted iteration). Agent-reported VET-PENDING.

Compute architecture: sequential-CPU (JUSTIFIED, same as parent). ONE streaming decompress-scan of
cskg.tsv.gz (~6M lines, ~60-100s) then several cheap dict-based inductions over the licensed pool + the
SAME gate (graph build + BFS over ~100 Qs) per arm. Heavy builds: cskg_unfiltered + cskg_random16 (up to
~6000 fillers each); the hubcap/filter arms are smaller. Est wall ~250-400s -> one 600s foreground call.
No matmul-heavy substrate primitive is swept -> not a GPU-batching candidate. Storage: no_storage.

CELL-TEMPLATE MANDATORY: except SystemExit before except Exception (no bare/BaseException); atomic
tmp+os.replace metrics; start-marker; crash-diagnostic; heartbeat with flush; deterministic seeding
(no salted-hash); positive control (cskg_unfiltered reproduces parent cov 0.56 tol 0.10); self-test
exercises REAL filters + REAL debiased induction (asserts hub excluded + graph max_deg<=cap) + REAL gate
discriminator (correct connects, lure severed); progress_logging: print_flush_true.
"""
from __future__ import annotations

import os
import sys
import json
import time
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments import exp_arc_derivation_rule_supply_cskg_v1 as rs
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as cn
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc

ANCHOR_NAME = "arc_derivation_rule_supply_cskg_depromisc_v1"
SEED = 20260725

TAU_UNIFY = rs.TAU_UNIFY
TAU_SIM = rs.TAU_SIM
DEPTH = rs.DEPTH
CSKG_PATH = rs.CSKG_PATH
FILLER_BUDGET = rs.FILLER_BUDGET          # 6000
CSKG_MAX_DEG_INDUCE = rs.CSKG_MAX_DEG_INDUCE

# de-promiscuification knobs (a priori; NOT tuned to a band)
HUBCAP8 = 8
HUBCAP3 = 3
RANDOM_CAP = 16                            # cskg_random16: unbiased sample under a loose cap
COMBINED_BASE_K = 8                        # science/precise/combined built on the hubcap8 debiased induction
PRECISE_KEEP = ("CAUSE", "REQUIRES", "IFTHEN")   # drop USEDFOR (UsedFor/CapableOf/ReceivesAction), SOURCEOF (MadeOf)

# salvage bands (a priori)
SALVAGE_COV = 0.30
SALVAGE_GAP = 0.15
NEED_GAP = 0.05
NEED_COV = 0.15

# positive-control reproduction (Gate D)
PARENT_CSKG_COV = 0.56                      # MEASURED @ data/exp_arc_derivation_rule_supply_cskg_v1/metrics.json:per_source_table[cskg].cov
REPRO_TOL = 0.10

# promiscuity-removed thresholds (fraction reduction vs unfiltered anchor)
PROM_REMOVED_MAXDEG_FRAC = 0.30
PROM_REMOVED_ROWS_FRAC = 0.30

DEPROM_ARMS = ("cskg_hubcap8", "cskg_hubcap3", "cskg_random16",
               "cskg_science", "cskg_precise", "cskg_combined")

_T0 = [time.perf_counter()]


# ---------------------------------------------------------------------------
# atomic metrics / start-marker / crash diag / heartbeat
# ---------------------------------------------------------------------------
def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    try:
        with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# DEBIASED induction: cap degree AT induction (full-CSKG degree) + non-degree selection.
# This is the load-bearing fix for the parent induction's hub-manufacturing bug.
# ---------------------------------------------------------------------------
def induce_subgraph_capped(cskg_rows, seed_words, filler_budget, deg_cap, select_mode, rng):
    """Query-conditioned induction that EXCLUDES mega-hubs at induction time.
    cskg_rows: FULL licensed pool [(gen_rel, a, b)]. deg = full-pool undirected label degree.
    Keep only labels with full-degree <= deg_cap (hub NEVER enters the budget), among nodes incident to a
    seed-incident edge, selected by RELEVANCE (non-degree) or RANDOM (fully unbiased). Deterministic.
    Returns (rows[{relation,arg0,arg1}], stat). Every kept node has full-degree <= deg_cap, so the kept
    subgraph's PRE-MERGE label degree is <= deg_cap (post node-merge may inflate modestly; REPORTED)."""
    seed_words = set(seed_words)

    def label_tokens(lab):
        return set(arc._content_words(lab, min_len=4))

    full_deg = {}
    all_labels = set()
    for (_, a, b) in cskg_rows:
        full_deg[a] = full_deg.get(a, 0) + 1
        full_deg[b] = full_deg.get(b, 0) + 1
        all_labels.add(a); all_labels.add(b)

    seed_relevance = {}
    for lab in all_labels:
        toks = label_tokens(lab)
        if not toks:
            continue
        m = toks & seed_words
        if m:
            seed_relevance[lab] = len(m) / len(toks)
    seed_nodes = set(seed_relevance)

    # candidate = nodes incident to a seed-incident edge, EXCLUDING any node over the degree cap.
    cand = set()
    incident = set()   # all nodes incident to a seed-incident edge (before the cap)
    for (_, a, b) in cskg_rows:
        if a in seed_nodes or b in seed_nodes:
            incident.add(a); incident.add(b)
            if full_deg[a] <= deg_cap:
                cand.add(a)
            if full_deg[b] <= deg_cap:
                cand.add(b)
    n_excluded_hub = sum(1 for n in incident if full_deg[n] > deg_cap)  # over-cap hubs removed at induction
    cand = sorted(cand)  # deterministic base order

    if select_mode == "relevance":
        cand.sort(key=lambda n: (-seed_relevance.get(n, 0.0), n))   # NON-degree selection
    elif select_mode == "random":
        perm = rng.permutation(len(cand))
        cand = [cand[int(i)] for i in perm]                          # fully unbiased sample
    else:
        raise ValueError(f"unknown select_mode {select_mode!r}")

    keep = set(cand[:filler_budget])
    kept = []
    for (gen, a, b) in cskg_rows:
        if a in keep and b in keep:
            kept.append({"relation": gen, "arg0": a, "arg1": b})
    n_frontier = len([n for n in keep if n not in seed_nodes])
    stat = {"deg_cap": deg_cap, "select_mode": select_mode, "n_all_labels": len(all_labels),
            "n_seed_nodes": len(seed_nodes), "n_candidate_nodes": len(cand),
            "n_kept_nodes": len(keep), "n_kept_seeds": len(keep) - n_frontier,
            "n_kept_frontier": n_frontier, "n_kept_rows": len(kept),
            "n_excluded_over_cap_seeds": n_excluded_hub, "filler_budget": filler_budget,
            "kept_max_full_degree": max((full_deg[n] for n in keep), default=0)}
    return kept, stat


# ---------------------------------------------------------------------------
# edge filters (science-term / precise-relation) on an induced row set
# ---------------------------------------------------------------------------
def _make_is_science(sci_vocab):
    def is_sci(lab):
        return bool(set(arc._content_words(lab, min_len=4)) & sci_vocab)
    return is_sci


def filter_science_terms(rows, sci_vocab):
    is_sci = _make_is_science(sci_vocab)
    return [r for r in rows if is_sci(r["arg0"]) and is_sci(r["arg1"])]


def filter_precise_relation(rows, keep=PRECISE_KEEP):
    keep = set(keep)
    return [r for r in rows if r["relation"] in keep]


def build_worldtree_science_vocab(wt_rows):
    """Independent science-curriculum vocabulary = content words of WorldTree licensed rows (NOT ARC)."""
    vocab = set()
    for r in wt_rows:
        for lab in (r["arg0"], r["arg1"]):
            for w in arc._content_words(lab, min_len=4):
                vocab.add(w)
    return vocab


# ---------------------------------------------------------------------------
# per-arm salvage classifier (a priori)
# ---------------------------------------------------------------------------
def classify_salvage(cov, typed_gap):
    if cov >= SALVAGE_COV and typed_gap >= SALVAGE_GAP:
        return "SALVAGE"
    if typed_gap < NEED_GAP or cov < NEED_COV:
        return "NEED_EXTRACTION"
    return "MIDDLE_BAND"


# ---------------------------------------------------------------------------
# self-test (REAL code paths: debiased induction cap + filters + REAL gate discriminator)
# ---------------------------------------------------------------------------
def _self_test():
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    print("[self-test] salvage classifier reachability ...", flush=True)
    assert classify_salvage(0.40, 0.20) == "SALVAGE"
    assert classify_salvage(0.10, 0.30) == "NEED_EXTRACTION"     # coverage collapse -> NOT salvage
    assert classify_salvage(0.56, 0.03) == "NEED_EXTRACTION"     # no selectivity survives
    assert classify_salvage(0.25, 0.10) == "MIDDLE_BAND"
    assert classify_salvage(0.35, 0.14) == "MIDDLE_BAND"         # cov ok but gap under bar
    print("[self-test] salvage classifier OK", flush=True)

    # synthetic FULL pool: rain->flood->erosion is a science chain; 'person' is a deg-5 hub.
    rows = [
        ("CAUSE", "rain", "flood"),
        ("CAUSE", "flood", "erosion"),
        ("USEDFOR", "person", "flood"),
        ("USEDFOR", "person", "erosion"),
        ("USEDFOR", "person", "salt"),
        ("USEDFOR", "person", "cooking"),
        ("USEDFOR", "person", "walking"),
        ("SOURCEOF", "cooking", "salt"),
    ]
    rng = np.random.default_rng(SEED)
    seed_words = {"rain", "erosion", "salt"}
    # DEBIASED cap K=3: 'person' has full-degree 5 -> MUST be excluded; rain/flood/erosion retained.
    kept, st = induce_subgraph_capped(rows, seed_words, filler_budget=100, deg_cap=3,
                                      select_mode="relevance", rng=rng)
    kept_labels = {r["arg0"] for r in kept} | {r["arg1"] for r in kept}
    assert "person" not in kept_labels, f"debiased cap kept the hub: {kept_labels}"
    assert st["n_excluded_over_cap_seeds"] >= 1, "hub was not counted as excluded-over-cap"
    # kept subgraph label degree must be <= cap
    deg = {}
    for r in kept:
        deg[r["arg0"]] = deg.get(r["arg0"], 0) + 1
        deg[r["arg1"]] = deg.get(r["arg1"], 0) + 1
    assert max(deg.values(), default=0) <= 3, f"debiased induction max label-degree > cap: {deg}"
    print(f"[self-test] debiased induction OK (hub excluded at induction; max label-deg<=cap): {st}",
          flush=True)

    # random-select mode is deterministic under a fixed rng + never keeps an over-cap node
    keptR, stR = induce_subgraph_capped(rows, seed_words, filler_budget=100, deg_cap=3,
                                        select_mode="random", rng=np.random.default_rng(SEED))
    labR = {r["arg0"] for r in keptR} | {r["arg1"] for r in keptR}
    assert "person" not in labR, f"random-select kept the hub: {labR}"
    print("[self-test] random-select induction OK (hub excluded)", flush=True)

    # edge filters
    krows = [{"relation": g, "arg0": a, "arg1": b} for (g, a, b) in rows]
    pr = filter_precise_relation(krows)
    assert all(r["relation"] in PRECISE_KEEP for r in pr) and len(pr) == 2, f"precise wrong: {pr}"
    st_rows = filter_science_terms(krows, {"rain", "flood", "erosion"})
    st_labels = {r["arg0"] for r in st_rows} | {r["arg1"] for r in st_rows}
    assert st_labels <= {"rain", "flood", "erosion"}, f"science filter leaked: {st_labels}"
    print("[self-test] edge filters OK (precise keeps CAUSE/REQUIRES/IFTHEN; science both-endpoint)",
          flush=True)

    # REAL gate discriminator CAN fire + CAN fail on the DEBIASED induced rows
    wn = _load_wordnet()
    pol = PolarityLexicon()
    base = cn._FakeBase()
    enc = cn.NegAwareEncoder(base, seed=SEED)
    g = cn.build_graph_gated(kept, enc.encode_batch, tau_unify=0.99, tau_sim=0.5, wn=wn, pol_lex=pol,
                             use_head_gate=True, use_pol_gate=True)

    def nodes_of(word):
        m = g["map_words"](gate._l2_rows(enc.encode_batch([word])))
        return set().union(*m) if m else set()

    rain_n, erosion_n, salt_n = nodes_of("rain"), nodes_of("erosion"), nodes_of("salt")
    assert rain_n and erosion_n, "planted words must map to nodes after debiased induction"
    assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, erosion_n, DEPTH, min_len=1) is True, \
        "debiased correct chain rain->flood->erosion MUST connect (gate can fire)"
    if salt_n:
        assert gate.meet_connected(g["fwd"], g["bwd"], rain_n, salt_n, DEPTH, min_len=1) is False, \
            "lure rain->salt MUST NOT connect once the person hub is excluded (gate can fail)"
    # graph max degree << 571 (the cap actually fired end-to-end)
    assert g["max_typed_node_degree"] <= 3 * 3, \
        f"debiased graph max degree {g['max_typed_node_degree']} not near cap"
    print("[self-test] REAL-gate discriminator OK on debiased rows (correct connects, lure severed)",
          flush=True)
    print("[self-test] ALL PASS", flush=True)


# ---------------------------------------------------------------------------
# main run
# ---------------------------------------------------------------------------
def run(output_dir, n_sample, seed, cskg_max_lines, filler_budget):
    os.makedirs(output_dir, exist_ok=True)
    run_mode = "smoke" if cskg_max_lines else "full"
    _write_start_marker(output_dir, run_mode)
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _heartbeat(output_dir, "start", {"n_sample": n_sample, "cskg_max_lines": cskg_max_lines,
                                     "filler_budget": filler_budget, "tau_unify": TAU_UNIFY})

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    base_enc = SemanticHDEncoder()
    neg_enc = cn.NegAwareEncoder(base_enc, seed=seed)
    wn = base_enc._wn
    pol = PolarityLexicon()
    _heartbeat(output_dir, "encoder_ready")

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(all_q))[:n_sample]
    questions = [all_q[int(i)] for i in sorted(idx.tolist())]
    seed_words = set()
    for q in questions:
        for w in arc._content_words(q["stem"], min_len=4):
            seed_words.add(w)
        for ch in q["choices"]:
            for w in arc._content_words(ch, min_len=4):
                seed_words.add(w)
    _heartbeat(output_dir, "questions_loaded", {"n_total": len(all_q), "n_sample": len(questions),
                                                "n_seed_words": len(seed_words)})

    wt_rows, wt_per_rel = rs.worldtree_rows()
    sci_vocab = build_worldtree_science_vocab(wt_rows)
    _heartbeat(output_dir, "worldtree_loaded", {"n_rows": len(wt_rows), "n_sci_vocab": len(sci_vocab)})

    cskg_lic, n_scanned, cskg_per_rel = rs.load_cskg_licensed(CSKG_PATH, max_lines=cskg_max_lines)
    _heartbeat(output_dir, "cskg_loaded", {"n_licensed_rows": len(cskg_lic), "n_scanned": n_scanned})

    # induction 1: parent degree-ranked induction (positive control -> reproduce parent cov 0.56)
    cskg_parent, induce_parent = rs.induce_subgraph(cskg_lic, seed_words, filler_budget,
                                                    CSKG_MAX_DEG_INDUCE)
    _heartbeat(output_dir, "induce_parent", induce_parent)

    # inductions 2-4: DEBIASED (degree cap at induction + non-degree selection)
    kept8, ind8 = induce_subgraph_capped(cskg_lic, seed_words, filler_budget, HUBCAP8,
                                         "relevance", np.random.default_rng(seed + 1))
    _heartbeat(output_dir, "induce_hubcap8", ind8)
    kept3, ind3 = induce_subgraph_capped(cskg_lic, seed_words, filler_budget, HUBCAP3,
                                         "relevance", np.random.default_rng(seed + 2))
    _heartbeat(output_dir, "induce_hubcap3", ind3)
    keptR, indR = induce_subgraph_capped(cskg_lic, seed_words, filler_budget, RANDOM_CAP,
                                         "random", np.random.default_rng(seed + 3))
    _heartbeat(output_dir, "induce_random16", indR)

    # semantic filters on the hubcap8 debiased induction
    sci_rows = filter_science_terms(kept8, sci_vocab)
    prec_rows = filter_precise_relation(kept8)
    comb_rows = filter_science_terms(filter_precise_relation(kept8), sci_vocab)

    arm_rows = {
        "cskg_unfiltered": cskg_parent,
        "cskg_hubcap8": kept8,
        "cskg_hubcap3": kept3,
        "cskg_random16": keptR,
        "cskg_science": sci_rows,
        "cskg_precise": prec_rows,
        "cskg_combined": comb_rows,
    }
    arm_induction = {
        "cskg_unfiltered": induce_parent, "cskg_hubcap8": ind8, "cskg_hubcap3": ind3,
        "cskg_random16": indR,
        "cskg_science": {"base": "hubcap8", "filter": "science_terms", "n_rows": len(sci_rows)},
        "cskg_precise": {"base": "hubcap8", "filter": "precise_relation", "n_rows": len(prec_rows)},
        "cskg_combined": {"base": "hubcap8", "filter": "precise+science", "n_rows": len(comb_rows)},
    }
    for name, rws in arm_rows.items():
        _heartbeat(output_dir, f"{name}_rows", {"n_rows": len(rws)})

    per = {}

    def _eval(name, rws):
        _heartbeat(output_dir, f"{name}_eval_start", {"n_rows": len(rws)})
        res = rs.eval_source(rws, neg_enc, wn, pol, questions, output_dir, name)
        if res is None:
            per[name] = {"arm": name, "n_rows": len(rws), "empty": True,
                         "typed_correct_coverage": 0.0, "typed_selectivity_gap": 0.0,
                         "untyped_selectivity_gap": 0.0, "untyped_correct_coverage": 0.0,
                         "salvage_band": "NEED_EXTRACTION",
                         "note": "filter/induction emptied the row set -> coverage collapse (NOT salvage)"}
            _heartbeat(output_dir, f"{name}_done_empty", {"n_rows": len(rws)})
            return
        cov = res["typed_correct_coverage"]
        tgap = res["typed_selectivity_gap"]
        res["arm"] = name
        res["n_rows"] = len(rws)
        res["salvage_band"] = classify_salvage(cov, tgap)
        per[name] = res
        _heartbeat(output_dir, f"{name}_done",
                   {"band": res["salvage_band"], "cov": cov, "typed_gap": tgap,
                    "untyped_gap": res["untyped_selectivity_gap"],
                    "max_deg": res["graph"]["max_typed_node_degree"], "n_rows": len(rws)})

    _eval("worldtree", wt_rows)
    for name in ("cskg_unfiltered", "cskg_hubcap8", "cskg_hubcap3", "cskg_random16",
                 "cskg_science", "cskg_precise", "cskg_combined"):
        _eval(name, arm_rows[name])

    anchor = per["cskg_unfiltered"]
    anchor_cov = anchor["typed_correct_coverage"]
    anchor_gap = anchor["typed_selectivity_gap"]
    anchor_maxdeg = anchor.get("graph", {}).get("max_typed_node_degree", 0)
    anchor_nrows = anchor["n_rows"]
    repro_dev = abs(anchor_cov - PARENT_CSKG_COV)
    repro_ok = bool(repro_dev <= REPRO_TOL)  # tolerance not asserted at smoke (reduced regime)

    salvage_hits = [a for a in DEPROM_ARMS
                    if per.get(a) and per[a].get("salvage_band") == "SALVAGE"]

    def _prom_removed(arm):
        r = per.get(arm)
        if not r or r.get("empty"):
            return True
        md = r.get("graph", {}).get("max_typed_node_degree", anchor_maxdeg)
        nr = r.get("n_rows", anchor_nrows)
        maxdeg_drop = (anchor_maxdeg - md) / anchor_maxdeg if anchor_maxdeg else 0.0
        rows_drop = (anchor_nrows - nr) / anchor_nrows if anchor_nrows else 0.0
        return bool(maxdeg_drop >= PROM_REMOVED_MAXDEG_FRAC or rows_drop >= PROM_REMOVED_ROWS_FRAC)

    prom_removed_arms = [a for a in DEPROM_ARMS if _prom_removed(a)]
    need_extraction = (len(salvage_hits) == 0 and len(prom_removed_arms) > 0 and
                       all(per.get(a, {}).get("salvage_band") in ("NEED_EXTRACTION", "MIDDLE_BAND")
                           and per.get(a, {}).get("typed_selectivity_gap", 0.0) < SALVAGE_GAP
                           for a in prom_removed_arms))

    if salvage_hits:
        verdict = "SALVAGE"
    elif need_extraction:
        verdict = "NEED_EXTRACTION"
    else:
        verdict = "MIDDLE_BAND"

    ranked = [a for a in DEPROM_ARMS
              if per.get(a) and per[a].get("typed_correct_coverage", 0.0) >= NEED_COV]
    best_arm = max(ranked, key=lambda a: per[a]["typed_selectivity_gap"]) if ranked else None
    best_chains = per.get(best_arm, {}).get("example_chains", []) if best_arm else []

    table = []
    for name in ("worldtree", "cskg_unfiltered", "cskg_hubcap8", "cskg_hubcap3", "cskg_random16",
                 "cskg_science", "cskg_precise", "cskg_combined"):
        r = per.get(name)
        if r is None:
            continue
        table.append({
            "arm": name, "salvage_band": r.get("salvage_band", "NA"),
            "n_rows": r.get("n_rows", 0),
            "cov": r.get("typed_correct_coverage", 0.0),
            "typed_gap": r.get("typed_selectivity_gap", 0.0),
            "untyped_cov": r.get("untyped_correct_coverage", 0.0),
            "untyped_gap": r.get("untyped_selectivity_gap", 0.0),
            "gap_beats_untyped": r.get("typed_gap_beats_untyped", None),
            "max_deg_achieved": r.get("graph", {}).get("max_typed_node_degree", None),
            "hub": r.get("graph", {}).get("max_degree_node_label", None),
            "n_nodes": r.get("graph", {}).get("n_nodes", None),
            "prom_removed": _prom_removed(name) if name in DEPROM_ARMS else None,
        })

    summary = (f"CSKG DE-PROMISCUIFY(debiased-induction) | verdict={verdict} | anchor(unfiltered) "
               f"cov={anchor_cov:.3f} gap={anchor_gap:+.4f} maxdeg={anchor_maxdeg} (parent cov "
               f"{PARENT_CSKG_COV}, repro_dev={repro_dev:.3f} ok={repro_ok}) | best_deprom={best_arm} "
               f"gap={per.get(best_arm, {}).get('typed_selectivity_gap', 0.0):+.4f} "
               f"cov={per.get(best_arm, {}).get('typed_correct_coverage', 0.0):.3f} "
               f"maxdeg={per.get(best_arm, {}).get('graph', {}).get('max_typed_node_degree', 'NA')} | "
               f"salvage_hits={salvage_hits}")

    vmsg_map = {
        "SALVAGE": ("SALVAGE: a de-promiscuified arm (debiased hub-capped induction / science / precise) "
                    "yielded typed selectivity gap >= 0.15 while keeping correct coverage >= 0.30 with "
                    "max-degree << 571 -> removing the (partly induction-manufactured) hub REVEALED a "
                    "real science-causal signal; a filtered CSKG is a viable cheap supply. Scale it."),
        "NEED_EXTRACTION": ("NEED_EXTRACTION: even with a DEBIASED induction that excludes the mega-hubs at "
                            "induction time (max-degree << 571, non-degree selection so the hub is not "
                            "re-manufactured), every promiscuity-removing arm keeps typed gap <0.15 with "
                            "cov<0.30 (or coverage collapses) -> there is NO science-causal core; CSKG's "
                            "connectivity WAS the vacuous hub bridges. Redirect to science-precise rule "
                            "EXTRACTION (text/curated causal rules), NOT off-the-shelf commonsense KBs."),
        "MIDDLE_BAND": ("MIDDLE_BAND: debiased de-promiscuification moved coverage/selectivity partway but "
                        "no arm cleared SALVAGE (cov>=0.30 AND gap>=0.15) and the promiscuity-removed arms "
                        "did not cleanly collapse -> report straight; no clean salvage or need-extraction."),
    }
    vmsg = vmsg_map.get(verdict, f"verdict = {verdict}")

    metrics = {
        "verdict": "GATE_MEASURED",
        "salvage_verdict": verdict,
        "summary": summary,
        "verdict_msg": vmsg,
        "anchor_name": ANCHOR_NAME,
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "run_mode": run_mode,
        "best_deprom_arm": best_arm,
        "salvage_hits": salvage_hits,
        "prom_removed_arms": prom_removed_arms,
        "positive_control": {
            "arm": "cskg_unfiltered", "measured_cov": round(anchor_cov, 4),
            "measured_typed_gap": round(anchor_gap, 4), "measured_max_deg": anchor_maxdeg,
            "parent_cov": PARENT_CSKG_COV, "repro_dev": round(repro_dev, 4),
            "repro_tol": REPRO_TOL, "repro_ok": repro_ok,
            "note": "parent degree-ranked induction; reproduces parent CSKG anchor at matched regime",
        },
        "induction_confound_addressed": (
            "parent rs.induce_subgraph has a DEAD max_deg_induce param + ranks candidates by "
            "-relevant_degree (top-budget) -> actively selects mega-hubs. This cell's cskg_hubcap*/random "
            "arms use induce_subgraph_capped: full-CSKG degree cap AT induction + relevance/random "
            "(non-degree) selection so the hub is never manufactured. max_deg_achieved reported per arm."),
        "config": {"n_sample": len(questions), "tau_unify": TAU_UNIFY, "tau_sim": TAU_SIM,
                   "depth": DEPTH, "seed": seed, "filler_budget": filler_budget,
                   "cskg_max_lines": cskg_max_lines, "hubcap8": HUBCAP8, "hubcap3": HUBCAP3,
                   "random_cap": RANDOM_CAP, "precise_keep": list(PRECISE_KEEP),
                   "combined_base_k": COMBINED_BASE_K, "n_science_vocab": len(sci_vocab),
                   "one_variable": ("cskg_de_promiscuification (parent-induction anchor vs debiased "
                                    "hub-capped/random inductions +/- science/precise edge filters); "
                                    "node-identity/gate/Qs/depth/thresholds IDENTICAL to parent")},
        "per_arm_table": table,
        "per_arm": per,
        "arm_induction": arm_induction,
        "best_deprom_chains_glassbox": best_chains,
        "cskg_load": {"path": os.path.relpath(CSKG_PATH, _REPO), "n_scanned": n_scanned,
                      "n_licensed_rows": len(cskg_lic),
                      "induction_caveat": ("CSKG query-conditioned subgraph-induced around sampled ARC "
                                           "vocab -> coverage is an UPPER BOUND (generous). A "
                                           "NEED_EXTRACTION verdict under generous induction is DECISIVE.")},
        "bands_preregistered": {
            "SALVAGE": f"cov >= {SALVAGE_COV} AND typed_gap >= {SALVAGE_GAP}",
            "NEED_EXTRACTION_per_arm": f"typed_gap < {NEED_GAP} OR cov < {NEED_COV}",
            "MIDDLE_BAND": "otherwise",
            "OVERALL_SALVAGE": "ANY deprom arm SALVAGE",
            "OVERALL_NEED_EXTRACTION": (f"no arm SALVAGE AND every arm that removed promiscuity "
                                        f"(max_deg drop >= {PROM_REMOVED_MAXDEG_FRAC} OR rows drop "
                                        f">= {PROM_REMOVED_ROWS_FRAC} vs anchor) stays gap<{SALVAGE_GAP}"),
            "HONEST_GUARD": ("coverage AND selectivity tracked together; cov>=0.30 required for SALVAGE so "
                             "a gap raised only by collapsing coverage is excluded by construction. "
                             "max_deg_achieved reported per arm to verify the hub cap actually fired."),
        },
        "parent_ref": {"cell": "arc_derivation_rule_supply_cskg_v1 (ba2d1b174)",
                       "cskg_cov_on_disk": PARENT_CSKG_COV, "cskg_typed_gap_on_disk": 0.0516,
                       "cskg_max_deg_on_disk": 571, "worldtree_cov_on_disk": 0.07,
                       "parent_headline": "MIDDLE_BAND (PROMISCUOUS: cov up, no selectivity)"},
        "notes": ("ONE-VARIABLE ablation: CSKG de-promiscuification (induction-debias + edge filter). "
                  "Node-identity (NegAwareEncoder + head-gate + polarity merge-gate), gate "
                  "(build_graph_gated + meet_connected), Qs, depth, thresholds IDENTICAL to parent. "
                  "Debiased induction addresses the parent induction's hub-manufacturing bug (dead "
                  "max_deg_induce + degree-ranked selection). Science-vocab = WorldTree content words "
                  "(independent; NOT ARC leakage). STRAIGHT report; NOT tuned to force SALVAGE. "
                  "NEED_EXTRACTION is the expected + fully reportable outcome."),
        "REQUIRED_FIELDS": ["verdict", "salvage_verdict", "best_deprom_arm", "salvage_hits",
                            "per_arm_table", "per_arm", "positive_control",
                            "induction_confound_addressed", "cskg_load"],
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)

    print("\n===== CSKG DE-PROMISCUIFICATION SALVAGE PROBE (debiased induction) =====", flush=True)
    print(summary, flush=True)
    print(f"VERDICT = {verdict} :: {vmsg}", flush=True)
    print("per-arm table (max_deg_achieved verifies the cap fired):", flush=True)
    for row in table:
        print(f"  {row['arm']:>16} band={str(row['salvage_band']):<16} rows={row['n_rows']:>7} "
              f"cov={row['cov']:.3f} typed_gap={row['typed_gap']:+.4f} "
              f"untyped_gap={row['untyped_gap']:+.4f} max_deg={row['max_deg_achieved']} "
              f"hub={row['hub']} prom_removed={row['prom_removed']}", flush=True)
    if best_arm:
        print(f"\nGLASS-BOX best de-promiscuified arm = {best_arm} "
              f"({len(best_chains)} surviving correct chains):", flush=True)
        for ch in best_chains:
            print(f"  Q[{ch.get('qid')}] {ch.get('stem', '')[:90]!r} -> "
                  f"{ch.get('correct_choice', '')[:60]!r} :: chain={ch.get('chain')}", flush=True)
    return metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=100, help="ARC-Challenge sample size")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--filler-budget", type=int, default=FILLER_BUDGET)
    ap.add_argument("--cskg-max-lines", type=int, default=0,
                    help="cap CSKG lines scanned (>0 = partial; smoke uses a cap)")
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    if args.mode == "smoke":
        n_sample = 12
        cskg_max_lines = args.cskg_max_lines or 400000
        filler_budget = min(args.filler_budget, 1500)
    else:
        n_sample = args.n
        cskg_max_lines = args.cskg_max_lines  # 0 = full scan
        filler_budget = args.filler_budget

    output_dir = args.out
    try:
        run(output_dir, n_sample, args.seed, cskg_max_lines, filler_budget)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print(f"[CRASH] {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
