"""exp_learner_live_canary_continual_growth_v1 -- THE LIVE CANARY for
notes/problems/run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite/PROBLEM.md.

QUESTION. The capstone proved the learner turns ON safe+beneficial on a FIXED 5M->15M batch (keep-both CLS
ensemble, corruption bounded, +gain, info-free twin loses, rollback works). What it did NOT test is the one
thing that only shows up OVER TIME: does the on-state STAY safe+beneficial when growth runs CONTINUALLY --
the reader keeps reading NEW text, round after round -- and does it hold on HELD-OUT + MODERN text rather
than the training distribution? This cell runs growth ON through the downstream comprehension read-out
CONTINUALLY (base 5M, then read new material in rounds up to 15M) and evaluates the FULL safety+benefit suite
at EVERY round, on TWO downstreams: LitBank who-did-what (old fiction; the capstone's instrument) AND a
held-out MODERN web downstream (UD-EWT). Reversible by construction (keep-both never overwrites), so running
it on is a monitored trial, not a commitment.

BRAIN MECHANISM (opening move; the drift lever the capstone left untested).
  * PINNED -- Complementary Learning Systems keep-both-stores (McClelland/O'Reilly 1995): the OLD store is
    never overwritten; the new (grown) store is fused ALONGSIDE it. REUSED VERBATIM from the promoted organ
    hdlab.cls_growth.make_ensemble_sim (the reversibility heart). NOT rebuilt.
  * PINNED -- reliability-weighted cue integration (Ernst & Banks 2002; Friston precision): fuse two
    DISAGREEING stores by their per-query decisiveness. The reliability operating point (AL.reliability_pred).
  * THE ANTI-DRIFT LEVER IS ONE PARAMETER -- the SLOW anchor store's CONSOLIDATION RATE eta. CLS consolidation
    keeps old knowledge via a SLOW neocortical store integrated by interleaved replay; the offline continual
    arm (exp_learner_growth_aligned_continual_v1) instead fused the RUNNING store with each new round, which
    HALVES the original anchor's weight every round (0.5 -> 0.25 -> 0.125 ...). Measured consequence on disk:
    even its "aligned" arm DRIFTED 0.114 -> 0.150 -> 0.196 over 3 rounds and was ROLLED BACK at the last --
    catastrophic interference creeping back. The read-out each round = keep-both ensemble(SLOW anchor, FAST
    grown); the arms differ in EXACTLY ONE variable, eta (how fast the slow anchor tracks new experience):
    FROZEN eta=0, EMA eta small, DECAY eta=0.5.
  * WHICH eta IS BRAIN-FAITHFUL (literature drill 2026-08-31, research_continual_growth_anchor_replay_...md).
    The brain does NOT re-inject a frozen copy of the original forever: (Q3) semantic/word meaning is
    continuously but SLOWLY updated across a lifetime -- early meanings are gradually REPLACED by later usage
    (Winocur & Moscovitch trace-transformation; diachronic semantic-update 2024/25), so a hard FREEZE is the
    LEAST faithful anchor for meaning; (Q1) replay of a consolidated trace DECAYS, its protection handed to
    (Q4) SYNAPTIC consolidation -- per-parameter stability that grows with confirmation (Fusi 2005 cascade;
    EWC Kirkpatrick 2017). The faithful anchor is therefore a SLOWLY-CONSOLIDATED store: high inertia (resists
    round-to-round drift) yet non-zero plasticity (absorbs genuine meaning change) -- a small-eta EMA, the
    neocortical slow-timescale / mean-teacher (Tarvainen & Valpola 2017; Kumaran/Hassabis/McClelland 2016 slow
    store). EMA_ANCHOR is the primary faithful arm; FROZEN is the engineering fix, only PARTIAL fidelity.

BRAIN-FIDELITY LABELS (no mislabelling -- the one thing barred):
  * keep-both-stores fusion (never overwrite)                                 -- PINNED (CLS; hdlab.cls_growth, verbatim).
  * reliability / precision-weighted fusion of two disagreeing stores         -- PINNED (Ernst & Banks 2002; Friston).
  * SLOWLY-CONSOLIDATED (small-eta EMA) anchor -- high-inertia slow store      -- brain-CONSISTENT (neocortical slow
                                                                                  timescale; Kumaran 2016; EMA/mean-teacher);
                                                                                  the eta value = OUR-INVENTION-UNDER-TEST (swept).
  * slow-anchor + keep-both read-out as a whole                              -- a COMPUTATIONAL-LEVEL SUBSTITUTE for
                                                                                  synaptic consolidation (Fusi 2005 / EWC 2017):
                                                                                  reproduces the anti-forgetting EFFECT via a slow
                                                                                  external store, not intrinsic per-synapse stability.
  * FROZEN anchor (eta=0)                                                     -- engineering fix; PARTIAL fidelity (freezes a
                                                                                  trace the brain keeps slowly fluid).
  * DECAY_ANCHOR (eta=0.5; anchor washes out)                                -- the anti-brain control; MUST drift.
  * rollback against a held-out known-correct probe                          -- brain-CONSISTENT (ACC/hippocampal error
                                                                                  monitoring; schema-gated consolidation, Tse
                                                                                  2007); probe/threshold = OUR-INVENTION.

THE FIVE-POINT SUITE, measured at EVERY continual round, on BOTH downstreams (a rigorous NEGATIVE on any is a
full PASS if located precisely). Primary arm = EMA_ANCHOR (the brain-faithful small-eta slow store):
  (a) SAFE       : EMA_ANCHOR corruption right->wrong (among OFF-correct) CI-UPPER < the pre-registered 0.15
                   at every round.
  (b) BENEFICIAL : EMA_ANCHOR gain vs OFF CI-separated above 0 AND the info-free growth twin (filler-shuffle)
                   does NOT beat OFF CI-separated.
  (c) ROLLBACK   : hdlab.cls_growth.rollback_gate ACCEPTs the EMA_ANCHOR update and ROLLS BACK an injected
                   NAIVE-overwrite and an ADVERSARIAL filler-shuffle update; a random-decision control does
                   NOT protect the working set.
  (d) NO DRIFT   : EMA_ANCHOR corruption does NOT climb across rounds (final not CI-separated ABOVE round 1,
                   CI-upper < 0.15 throughout) WHILE the DECAY_ANCHOR can-fail control DOES climb (final
                   corruption CI-separated ABOVE EMA). If DECAY does not climb the drift test is void.
  (e) GENERALIZES: (a) + (b) hold on the held-out MODERN UD-EWT downstream, not just LitBank.
  (+) STABILITY-PLASTICITY: the consolidation-rate FRONTIER (final gain + corruption vs eta) and the drill's
      falsifiable prediction -- EMA is a strictly-better operating point than FROZEN (gain NOT CI-sep BELOW
      frozen while corruption NOT CI-sep ABOVE): it absorbs legitimate new meaning the freeze rejects.

Report CI half-width beside every margin + the events-margin permutation null p95 for the headline gain.

Run:  .venv/Scripts/python.exe experiments/exp_learner_live_canary_continual_growth_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_learner_live_canary_continual_growth_v1.py --mode smoke
      .venv/Scripts/python.exe experiments/exp_learner_live_canary_continual_growth_v1.py --mode full

REUSED VERBATIM (READ-ONLY): hdlab.cls_growth (CG -- the promoted keep-both fusion + rollback gate, NOT
rebuilt), experiments.exp_structured_context_learner_v1 (S), experiments.exp_learner_safety_gate_v1 (G),
experiments.exp_learner_on_clean_foundation_v1 (M -- build_coreslot_selpref, CORRUPTION_BOUND, PROBE_FRAC),
experiments.exp_learner_growth_aligned_continual_v1 (AL -- reliability_pred/_zsim/coreslot_vectors),
experiments.exp_growth_cls_ensemble_v1 (C -- paired_corruption_delta stats helper only).
Writes ONLY to data/exp_learner_live_canary_continual_growth_v1/. Does NOT modify hdlab/, data/foundation/,
or any other cell. Does NOT turn on growth in the live substrate -- validation-only harness (default-off by
construction: it writes only to its own data dir). The held-out MODERN downstream is parsed with spaCy ONCE
and CACHED (data/exp_learner_live_canary_continual_growth_v1/modern_paraphrase_items.json); spaCy is imported
only inside the builder, only when that cache is absent. ASCII only. Deterministic (fixed integer seeds).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import hdlab.cls_growth as CG                                          # noqa: E402  THE PROMOTED PRIMITIVE
import experiments.exp_structured_context_learner_v1 as S             # noqa: E402
import experiments.exp_learner_safety_gate_v1 as G                    # noqa: E402
import experiments.exp_learner_on_clean_foundation_v1 as M            # noqa: E402
import experiments.exp_learner_growth_aligned_continual_v1 as AL      # noqa: E402
import experiments.exp_growth_cls_ensemble_v1 as C                    # noqa: E402

ANCHOR = "learner_live_canary_continual_growth_v1"
from experiments._seed_checkpoint import get_output_dir  # Q115: canonical shared output dir (same FULL path)
OUTPUT_DIR = str(get_output_dir(ANCHOR))
MODERN_GOLD = os.path.join(REPO_ROOT, "data", "eval_gold_mention_role_modern_ud_ewt_v1",
                           "gold_situation_modern_ud_ewt_v1.jsonl")
MODERN_ITEMS_CACHE = os.path.join(OUTPUT_DIR, "modern_paraphrase_items.json")

SEED = 20260831
CORRUPTION_BOUND = M.CORRUPTION_BOUND          # 0.15, pre-registered (inherited)
PROBE_FRAC = M.PROBE_FRAC                       # 0.40, inherited
CORE_SLOTS = {"nsubj", "nsubjpass", "dobj", "obj", "iobj", "dative"}   # gov-verb core args (mirror M.CORE_SLOTS + dative)

# Continual reading rounds (cumulative token budgets; the FIRST is the pre-growth anchor). More rounds than
# the offline 3-step arm so drift has room to show and the "keeps reading" run is genuinely continual.
STEPS_FULL = [5_000_000, 7_000_000, 9_000_000, 11_000_000, 13_000_000, 15_000_000]
STEPS_SMOKE = [120_000, 180_000, 240_000, 300_000]


# ---------------------------------------------------------------- held-out MODERN downstream (parse ONCE, cache)
def build_modern_paraphrase_items(cache_path=MODERN_ITEMS_CACHE, gold_path=MODERN_GOLD):
    """Held-out MODERN comprehension gold, SAME construction as G.build_paraphrase_items but from modern web
    text (UD-EWT). Per passage, candidate set = the distinct governing-verb LEMMAS (a VERB heading a core
    argument -- nsubj/dobj/iobj/dative), alpha, len>=3, >=3 candidates; for each candidate `target`, the QUERY
    is a WordNet verb-synonym that is a DIFFERENT lemma and not already a candidate (a true paraphrase probe).
    Parsed with spaCy ONCE and CACHED; spaCy is imported INSIDE this function and touched only when the cache
    is absent (so a cached run -- e.g. remote -- never needs spaCy). Deterministic."""
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as fh:
            return json.load(fh)
    import spacy   # local-only, gated behind the cache
    import experiments.exp_meaning_channel_paraphrase_comprehension_v1 as P  # for _verb_synonym (verbatim)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    with open(gold_path, encoding="utf-8") as fh:
        recs = [json.loads(line) for line in fh]
    items = []
    for di, rec in enumerate(recs):
        doc = nlp(" ".join(rec["clauses"]))
        verbs = set()
        for t in doc:
            if t.dep_ in CORE_SLOTS and t.head.pos_ == "VERB":
                lem = t.head.lemma_.lower()
                if lem.isalpha() and len(lem) >= 3:
                    verbs.add(lem)
        cand = sorted(verbs)
        if len(cand) < 3:
            continue
        for target in cand:
            q = P._verb_synonym(target)
            if q is None or q in cand:
                continue
            items.append({"doc": di, "target": target, "query": q, "cand": cand})
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    tmp = cache_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(items, fh)
    os.replace(tmp, cache_path)
    return items


# ---------------------------------------------------------------- fusion arms (read-out via CG -- promoted primitive)
# THE ANTI-DRIFT LEVER IS ONE PARAMETER: the SLOW ("anchor") store's consolidation rate eta (its neocortical
# slow-timescale learning rate). Read-out every round = keep-both ensemble of the SLOW store and the FAST
# (current cumulative-grown) store -- the CLS two-store read-out, via CG.make_ensemble_sim VERBATIM. The arms
# differ in EXACTLY ONE variable: eta, how fast the slow anchor tracks new experience.
#   eta = 0.0   FROZEN_ANCHOR : slow store stays the original base forever (infinite inertia). The engineering
#               fix, and -- per the brain drill (2026-08-31) -- only PARTIAL fidelity: semantic/word meaning is
#               continuously (slowly) updated across a lifetime, so a hard freeze is the LEAST faithful anchor.
#   eta small   EMA_ANCHOR    : slow store = (1-eta)*slow + eta*grown each round (Procrustes-aligned, so the
#               EMA is in one coordinate frame). The MOST brain-faithful variant (Kumaran/Hassabis/McClelland
#               2016 slow neocortical store; mean-teacher EMA, Tarvainen & Valpola 2017): high inertia resists
#               round-to-round drift, non-zero plasticity still absorbs legitimate meaning change.
#   eta = 0.5   DECAY_ANCHOR  : slow store tracks fast -- the base washes out in a few rounds -> catastrophic
#               interference returns. The anti-brain CAN-FAIL control; MUST drift.
# BRAIN-FIDELITY LABEL: the slow anchor + keep-both read-out is a COMPUTATIONAL-LEVEL SUBSTITUTE for synaptic
# consolidation (per-parameter stability that grows with confirmation -- Fusi 2005 cascade / EWC 2017); it
# reproduces the anti-forgetting EFFECT via a slow external store rather than intrinsic per-synapse stability.
def _ens(sim_old, sim_new, items, mode="mean"):
    """keep-both fusion of two similarity channels, z-scored on THIS downstream's items. VERBATIM
    hdlab.cls_growth -- never discards a defined channel (the reversibility heart)."""
    mo, so = CG.zscore_params(sim_old, items)
    mn, sn = CG.zscore_params(sim_new, items)
    return CG.make_ensemble_sim(sim_old, mo, so, sim_new, mn, sn, mode)


def reliability_scores(items, sim_slow, sim_fast):
    """Precision-weighted (reliability) keep-both read-out: trust each store per-query by its ranking MARGIN
    (Ernst & Banks 2002 / Friston precision). This is the PRIORITIZED-PROTECTION form of interleaved replay --
    where the confirmed (slow/anchor) store is DECISIVE and the grown store disagrees, the anchor dominates
    (protects the confirmed old meaning most at risk of corruption -- Mattar & Daw 2018 gain x need; Schapiro
    2018 weak-item-first); where the grown store is decisive (genuine new knowledge), it dominates (gain).
    AL.reliability_pred VERBATIM. Directly targets the store-DISAGREEMENT the uniform z-mean can only average,
    so it is the brain-faithful candidate to lower corruption on hard corpora."""
    ms, ss = CG.zscore_params(sim_slow, items)
    mf, sf = CG.zscore_params(sim_fast, items)
    return AL.score_reliability(items, AL._zsim(sim_slow, ms, ss), AL._zsim(sim_fast, mf, sf))


def coreslot_vecs_seed(parsed, index, mc, seed):
    """CORE-ARG SELPREF SVD vectors at an explicit SVD seed (AL.coreslot_vectors hardcodes one seed; this lets
    the seed-robustness stage vary the random draw of the truncated SVD)."""
    msp, _, _, _ = M.build_coreslot_selpref(parsed, index, min_count=mc)
    return S.svd_vectors(S.ppmi_matrix(msp), seed=seed)


def slow_store_trajectory(base_vecs, step_vecs, step_toks, index, eta):
    """The SLOW anchor store per round, maintained by a Procrustes-aligned EMA toward each round's grown store
    (AL.align_and_fuse, do_align=True -> the EMA lives in ONE coordinate frame; two independent SVDs share no
    frame). eta=0 -> stays base (frozen); larger eta -> tracks the grown store faster. Returns [(slow_vecs,
    slow_idx) per round] aligned to step_toks[1:]."""
    slow_vecs, slow_idx = base_vecs, index
    traj = []
    for t in step_toks[1:]:
        if eta > 0.0:
            slow_vecs, slow_idx = AL.align_and_fuse(slow_vecs, slow_idx, step_vecs[t], index,
                                                    alpha=eta, do_align=True)
        traj.append((slow_vecs, slow_idx))
    return traj


def slow_store_readouts(items, base_vecs, step_vecs, step_toks, index, eta):
    """Continual read-out for consolidation rate eta: each round = keep-both ensemble(slow_anchor, fast_grown)
    via CG (the CLS two-store read-out). Returns ([read-out sim_fn per round], trajectory)."""
    traj = slow_store_trajectory(base_vecs, step_vecs, step_toks, index, eta)
    outs = []
    for k, t in enumerate(step_toks[1:]):
        sim_slow = S.dense_vec_cosine_fn(*traj[k])
        sim_fast = S.dense_vec_cosine_fn(step_vecs[t], index)
        outs.append(_ens(sim_slow, sim_fast, items, "mean"))
    return outs, traj


# ---------------------------------------------------------------- permutation null (headline gain)
def gain_null_p95(off_core, arm_core, seed, n_perm=2000):
    """Label-permutation null for the paired accuracy gain (arm - off): shuffle which of each pair is 'arm'
    vs 'off' and recompute the mean paired delta; p95 of |null delta|. A margin above p95 is not a coin flip."""
    a = np.asarray(arm_core, dtype=float)
    b = np.asarray(off_core, dtype=float)
    d = a - b
    rng = np.random.default_rng(seed)
    null = np.array([(d * rng.choice((-1.0, 1.0), size=d.size)).mean() for _ in range(n_perm)])
    return float(np.percentile(np.abs(null), 95))


# ---------------------------------------------------------------- io / crash
def _write(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, os.path.join(OUTPUT_DIR, "metrics.json"))
    print("[write] %s" % os.path.join(OUTPUT_DIR, "metrics.json"), flush=True)


def _crash(exc):
    _write({"anchor_name": ANCHOR, "verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:400]),
            "traceback": traceback.format_exc()[:4000], "ts_iso": datetime.now(timezone.utc).isoformat()})


# ---------------------------------------------------------------- self-test (formula, no corpus)
def self_test():
    ok = True

    # (1) THE CONSOLIDATION-RATE INVARIANT (vector level). Build a base store and a grown store that is the base
    # rotated into a new frame + a genuine shift. The slow anchor is a Procrustes-aligned EMA at rate eta; its
    # similarity to the ORIGINAL base must DECREASE MONOTONICALLY as eta grows: eta=0 (FROZEN) stays == base
    # (cos 1.0), larger eta (toward DECAY) drifts further from base. This is the one variable the arms differ in.
    items = [{"query": "q", "cand": ["a", "b"], "target": "a"}]   # (kept for parts 2)
    def mk(sa, sb):
        d = {("q", "a"): sa, ("q", "b"): sb}
        return lambda q, c: d.get((q, c))
    rng0 = np.random.default_rng(0)
    words = ["w%d" % i for i in range(12)]
    idx = {w: i for i, w in enumerate(words)}
    base_vecs = rng0.standard_normal((12, 6))
    Qr, _ = np.linalg.qr(rng0.standard_normal((6, 6)))            # a random frame rotation
    grown_vecs = base_vecs @ Qr + 0.5 * rng0.standard_normal((12, 6))   # rotated + genuinely shifted
    step_vecs = {0: base_vecs, 1: grown_vecs}
    def cos_to_base(vecs, vidx):
        cs = []
        for w in words:
            a = vecs[vidx[w]]; b = base_vecs[idx[w]]
            na = np.linalg.norm(a); nb = np.linalg.norm(b)
            if na > 0 and nb > 0:
                cs.append(float(a @ b / (na * nb)))
        return float(np.mean(cs))
    cos_by_eta = []
    for eta in (0.0, 0.2, 0.5):
        traj = slow_store_trajectory(base_vecs, step_vecs, [0, 1], idx, eta)
        cos_by_eta.append(cos_to_base(*traj[-1]))
    ok_family = (cos_by_eta[0] > 0.999 and cos_by_eta[0] >= cos_by_eta[1] >= cos_by_eta[2]
                 and cos_by_eta[2] < cos_by_eta[0])
    print("[self-test] consolidation-rate: cos(anchor,base) by eta [0.0,0.2,0.5]=%s (monotone down) -> %s"
          % ([round(c, 4) for c in cos_by_eta], "OK" if ok_family else "FAIL"), flush=True)
    ok = ok and ok_family

    # (2) keep-both never discards a defined channel (reversibility): if the grown channel is undefined for a
    # candidate, the fused score falls back to the base channel (not None) -- the exact property that makes it
    # reversible / safe.
    fused = _ens(mk(0.5, 0.1), (lambda q, c: None), items, "mean")
    v = fused("q", "a")
    ok_kb = v is not None
    print("[self-test] keep-both retains base when grown undefined: fused=%s -> %s"
          % (None if v is None else round(v, 3), "OK" if ok_kb else "FAIL"), flush=True)
    ok = ok and ok_kb

    # (3) permutation null: a genuine constant gain sits far above the null p95; a zero-gain (a==b) sits at ~0.
    off = [0, 1, 0, 1, 0, 1, 0, 1] * 6
    arm = [1, 1, 1, 1, 0, 1, 0, 1] * 6           # arm fixes some 0s, breaks none of the shown pattern
    p95 = gain_null_p95(off, arm, seed=1, n_perm=500)
    d0 = float(np.mean(arm) - np.mean(off))
    p95_zero = gain_null_p95(off, off, seed=1, n_perm=500)
    ok_null = d0 > p95 and p95_zero >= 0.0
    print("[self-test] perm null: gain=%.4f p95=%.4f (zero-gain p95=%.4f) -> %s"
          % (d0, p95, p95_zero, "OK" if ok_null else "FAIL"), flush=True)
    ok = ok and ok_null

    # (4) reuse surface: every CG/S/G/M/AL/C attribute run() depends on resolves NOW (fail in ms, not mid-run).
    need_CG = ("zscore_params", "make_ensemble_sim", "rollback_gate", "argmax_pred")
    need_S = ("dense_vec_cosine_fn", "load_parsed", "token_sents", "build_vocab", "ppmi_matrix",
              "svd_vectors", "random_vec_cosine_fn", "SVD_K", "CTX_MIN_COUNT")
    need_G = ("build_paraphrase_items", "cache_path", "score_items", "boot_ci", "paired_delta_acc",
              "corruption_rate", "build_selpref_fillershuffle_cooc", "MODE_CFG")
    need_M = ("build_coreslot_selpref", "CORRUPTION_BOUND", "PROBE_FRAC")
    need_AL = ("reliability_pred", "_zsim", "score_reliability", "coreslot_vectors")
    need_C = ("paired_corruption_delta",)
    ok_reuse = (all(hasattr(CG, n) for n in need_CG) and all(hasattr(S, n) for n in need_S)
                and all(hasattr(G, n) for n in need_G) and all(hasattr(M, n) for n in need_M)
                and all(hasattr(AL, n) for n in need_AL) and all(hasattr(C, n) for n in need_C))
    print("[self-test] reuse surface (CG/S/G/M/AL/C) present -> %s" % ("OK" if ok_reuse else "FAIL"), flush=True)
    ok = ok and ok_reuse

    # (5) modern gold present on disk (the held-out downstream source).
    ok_gold = os.path.exists(MODERN_GOLD)
    print("[self-test] modern UD-EWT gold present: %s -> %s" % (ok_gold, "OK" if ok_gold else "FAIL"), flush=True)
    ok = ok and ok_gold

    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


# consolidation-rate frontier (the anti-drift lever). Named arms MUST be members of ETAS_CURVE.
ETA_FROZEN, ETA_EMA, ETA_DECAY = 0.0, 0.1, 0.5
ETAS_CURVE = [0.0, 0.05, 0.1, 0.25, 0.5]
SHIFT_TOK = 99_000_000   # sentinel budget for the distribution-shift round (a NEW modern domain)


# ---------------------------------------------------------------- one downstream, full suite over the rounds
def evaluate_downstream(name, items, step_vecs, sim_fillershuf, step_toks, index, nb):
    """Run the full suite for ONE downstream over every continual round, across the consolidation-rate frontier
    (FROZEN eta=0, EMA eta small, DECAY eta=0.5). Returns a metrics dict (+ read-out sim closures under '_sims'
    for the rollback stage, popped before persistence)."""
    base_vecs = step_vecs[step_toks[0]]
    sim_base = S.dense_vec_cosine_fn(base_vecs, index)
    rounds = step_toks[1:]; tf = rounds[-1]; t1 = rounds[0]
    print("[%s] scoring OFF (pre-growth base) ..." % name, flush=True)
    r_off = G.score_items(items, sim_base)

    # read-out trajectories for every eta on the frontier (slow anchor + fast grown, keep-both via CG).
    readouts, trajs = {}, {}
    for eta in ETAS_CURVE:
        outs, traj = slow_store_readouts(items, base_vecs, step_vecs, step_toks, index, eta)
        readouts[eta] = outs; trajs[eta] = traj
    r_arm = {eta: {t: G.score_items(items, readouts[eta][k]) for k, t in enumerate(rounds)} for eta in ETAS_CURVE}

    # reliability operating point on the EMA slow store at the final round (precision-weighted keep-both).
    sim_slow_ema_final = S.dense_vec_cosine_fn(*trajs[ETA_EMA][-1])
    sim_fast_final = S.dense_vec_cosine_fn(step_vecs[tf], index)
    mb, sb = CG.zscore_params(sim_slow_ema_final, items); mg, sg = CG.zscore_params(sim_fast_final, items)
    r_reliab = AL.score_reliability(items, AL._zsim(sim_slow_ema_final, mb, sb),
                                    AL._zsim(sim_fast_final, mg, sg))

    # info-free growth twin (keep-both base + filler-shuffled grown; must NOT beat OFF) + naive overwrite.
    sim_twin = _ens(sim_base, sim_fillershuf, items, "mean")
    r_twin = G.score_items(items, sim_twin)
    r_naive = G.score_items(items, sim_fast_final)

    def defined(i):
        return (r_off[i] is not None and r_reliab[i] is not None and r_twin[i] is not None
                and r_naive[i] is not None
                and all(r_arm[eta][t][i] is not None for eta in ETAS_CURVE for t in rounds))
    core_idx = [i for i in range(len(items)) if defined(i)]
    n_core = len(core_idx)
    print("[%s] coverage OFF=%d EMA_final=%d reliab=%d twin=%d naive=%d | CORE_COMMON=%d"
          % (name, sum(x is not None for x in r_off), sum(x is not None for x in r_arm[ETA_EMA][tf]),
             sum(x is not None for x in r_reliab), sum(x is not None for x in r_twin),
             sum(x is not None for x in r_naive), n_core), flush=True)
    if n_core < 30:
        return {"downstream": name, "verdict": "ABORT_COVERAGE", "n_core": n_core}

    off_core = [r_off[i] for i in core_idx]
    reliab_core = [r_reliab[i] for i in core_idx]
    twin_core = [r_twin[i] for i in core_idx]
    naive_core = [r_naive[i] for i in core_idx]
    arm_core = {eta: {t: [r_arm[eta][t][i] for i in core_idx] for t in rounds} for eta in ETAS_CURVE}

    def round_row(ac, h):
        return {"acc": G.boot_ci(ac, SEED + 50 + h, nb)["acc"],
                "gain_vs_off": G.paired_delta_acc(ac, off_core, SEED + 10 + h, nb),
                "corruption": G.corruption_rate(off_core, ac, SEED + 30 + h, nb)["corruption_right_to_wrong"]}
    curves = {eta: {t: round_row(arm_core[eta][t], int(eta * 100) + h) for h, t in enumerate(rounds)}
              for eta in ETAS_CURVE}

    frozen_curve, ema_curve, decay_curve = curves[ETA_FROZEN], curves[ETA_EMA], curves[ETA_DECAY]
    twin_gain = G.paired_delta_acc(twin_core, off_core, SEED + 220, nb)
    naive_gain = G.paired_delta_acc(naive_core, off_core, SEED + 221, nb)
    naive_corr = G.corruption_rate(off_core, naive_core, SEED + 222, nb)["corruption_right_to_wrong"]
    reliab_gain = G.paired_delta_acc(reliab_core, off_core, SEED + 210, nb)
    reliab_corr = G.corruption_rate(off_core, reliab_core, SEED + 211, nb)["corruption_right_to_wrong"]

    # Per-arm suite on the TERMINAL state after the continual run (the accumulated end state is what "does it
    # drift as it keeps reading" asks about); the full per-round curve is persisted so any mid-run excursion is
    # visible. SAFE = terminal corruption CI-UPPER < the pre-registered 0.15. NO-CLIMB = terminal corruption
    # NOT CI-separated ABOVE round 1. BENEFICIAL = terminal gain CI-sep above 0 AND the info-free twin loses.
    def arm_suite(eta, h):
        cur = curves[eta]; ac = arm_core[eta]
        term = cur[tf]["corruption"]
        cih = [cur[t]["corruption"]["ci"][1] for t in rounds if cur[t]["corruption"]["ci"][1] is not None]
        fin_vs_first = C.paired_corruption_delta(off_core, ac[tf], ac[t1], SEED + 230 + h, nb)
        gain = cur[tf]["gain_vs_off"]
        return {"eta": eta, "terminal_gain": gain, "terminal_corruption": term,
                "gain_null_p95": round(gain_null_p95(off_core, ac[tf], SEED + 260 + h), 4),
                "safe_terminal_ci_upper_lt_bound": bool(term["ci"][1] is not None and term["ci"][1] < CORRUPTION_BOUND),
                "max_round_corruption_ci_hi": round(max(cih), 4) if cih else None,
                "safe_all_rounds": bool(cih and max(cih) < CORRUPTION_BOUND),
                "terminal_minus_first_corruption": fin_vs_first,
                "no_climb": bool(not fin_vs_first["separated_above"]),
                "beneficial": bool(gain["separated_above"] and not twin_gain["separated_above"])}
    frozen_suite = arm_suite(ETA_FROZEN, 0)
    ema_suite = arm_suite(ETA_EMA, 1)

    # power diagnosis: the corruption denominator is the base-CORRECT set; on a corpus where the base is weak
    # (old fiction, OFF acc ~0.07) that set is small -> a WIDE corruption CI whose UPPER edge can clip over the
    # bound even when the POINT estimate is under it. Record n_base_right + whether the point estimate is safe.
    for su in (frozen_suite, ema_suite):
        su["n_base_right"] = su["terminal_corruption"]["n"]
        su["point_estimate_safe"] = bool(su["terminal_corruption"]["rate"] is not None
                                         and su["terminal_corruption"]["rate"] < CORRUPTION_BOUND)

    # THE BRAIN'S PRIORITIZED-PROTECTION mechanism as the candidate wall-crosser on hard corpora: precision-
    # weighted (reliability) fusion protects the items where the confirmed anchor is decisive. Compare its
    # terminal corruption to the uniform z-mean's, for the FROZEN and EMA anchors.
    def rel_terminal(eta, h):
        slow = S.dense_vec_cosine_fn(*trajs[eta][-1]); fast = S.dense_vec_cosine_fn(step_vecs[tf], index)
        rc = reliability_scores(items, slow, fast)
        pairs = [(off_core[p], rc[i]) for p, i in enumerate(core_idx) if rc[i] is not None]
        oc = [a for a, _ in pairs]; ac = [b for _, b in pairs]
        gain = G.paired_delta_acc(ac, oc, SEED + 270 + h, nb)
        corr = G.corruption_rate(oc, ac, SEED + 280 + h, nb)["corruption_right_to_wrong"]
        return {"n": len(pairs), "terminal_gain": gain, "terminal_corruption": corr,
                "safe_terminal_ci_upper_lt_bound": bool(corr["ci"][1] is not None and corr["ci"][1] < CORRUPTION_BOUND),
                "beneficial": bool(gain["separated_above"] and not twin_gain["separated_above"])}
    reliability_frozen = rel_terminal(ETA_FROZEN, 0)
    reliability_ema = rel_terminal(ETA_EMA, 1)
    reliability_crosses_wall = bool(reliability_ema["safe_terminal_ci_upper_lt_bound"]
                                    and not ema_suite["safe_terminal_ci_upper_lt_bound"])

    # (d) NO DRIFT needs a CAN-FAIL control: the DECAY arm must climb ABOVE the anchor arm (else the drift test
    # is void). Measured vs BOTH anchor arms.
    decay_vs_ema = C.paired_corruption_delta(off_core, arm_core[ETA_DECAY][tf], arm_core[ETA_EMA][tf], SEED + 250, nb)
    decay_vs_frozen = C.paired_corruption_delta(off_core, arm_core[ETA_DECAY][tf], arm_core[ETA_FROZEN][tf], SEED + 251, nb)
    decay_climbs = bool(decay_vs_ema["separated_above"] or decay_vs_frozen["separated_above"])

    # the drill's falsifiable prediction: EMA absorbs legitimate new meaning FROZEN rejects (EMA gain NOT CI-sep
    # BELOW frozen; ideally CI-sep ABOVE) -- a strictly-better stability/plasticity point where the base is
    # strong enough to stay safe.
    ema_vs_frozen_gain = G.paired_delta_acc(arm_core[ETA_EMA][tf], arm_core[ETA_FROZEN][tf], SEED + 240, nb)
    ema_more_benefit = bool(ema_vs_frozen_gain["separated_above"])

    # the safe consolidation-rate envelope: the largest eta whose TERMINAL corruption CI-upper stays < bound.
    safe_etas = [eta for eta in ETAS_CURVE
                 if curves[eta][tf]["corruption"]["ci"][1] is not None
                 and curves[eta][tf]["corruption"]["ci"][1] < CORRUPTION_BOUND]
    max_safe_eta = max(safe_etas) if safe_etas else None

    frontier = {("%.2f" % eta): {"final_gain": curves[eta][tf]["gain_vs_off"]["delta"],
                                 "final_corruption": curves[eta][tf]["corruption"]["rate"],
                                 "final_corruption_ci_hi": curves[eta][tf]["corruption"]["ci"][1]}
                for eta in ETAS_CURVE}

    # (a) SAFE / (b) BENEFICIAL / (d) NO-DRIFT are reported for the PRIMARY faithful arm (EMA) AND the
    # universally-safe fallback (FROZEN). The overall on-state "passes" if SOME anchor arm on this downstream
    # is safe+beneficial+no-climb (i.e. a safe operating point exists) while the DECAY control drifts.
    ema_all = bool(ema_suite["safe_terminal_ci_upper_lt_bound"] and ema_suite["beneficial"] and ema_suite["no_climb"])
    frozen_all = bool(frozen_suite["safe_terminal_ci_upper_lt_bound"] and frozen_suite["beneficial"] and frozen_suite["no_climb"])
    on_state_exists = bool((ema_all or frozen_all) and decay_climbs)

    return {
        "downstream": name, "n_items": len(items), "n_core_common": n_core, "rounds": rounds,
        "off_acc": G.boot_ci(off_core, SEED + 5, nb), "final_round": tf,
        "eta_named": {"FROZEN": ETA_FROZEN, "EMA": ETA_EMA, "DECAY": ETA_DECAY},
        "frozen_curve": frozen_curve, "ema_curve": ema_curve, "decay_curve": decay_curve,
        "consolidation_rate_frontier": frontier, "max_safe_eta": max_safe_eta,
        "frozen_suite": frozen_suite, "ema_suite": ema_suite,
        "reliability_frozen": reliability_frozen, "reliability_ema": reliability_ema,
        "reliability_crosses_old_fiction_wall": reliability_crosses_wall,
        "reliability_operating_point": {"gain_vs_off": reliab_gain, "corruption": reliab_corr},
        "info_free_twin_gain_vs_off": twin_gain,
        "naive_overwrite_gain_vs_off": naive_gain, "naive_overwrite_corruption": naive_corr,
        "drift": {"decay_final_minus_ema_final_corruption": decay_vs_ema,
                  "decay_final_minus_frozen_final_corruption": decay_vs_frozen,
                  "decay_climbs_can_fail_control": decay_climbs},
        "stability_plasticity": {"ema_vs_frozen_gain": ema_vs_frozen_gain,
                                 "ema_more_benefit_than_frozen": ema_more_benefit},
        "bars": {"a_safe_ema": ema_suite["safe_terminal_ci_upper_lt_bound"],
                 "a_safe_frozen": frozen_suite["safe_terminal_ci_upper_lt_bound"],
                 "b_beneficial": ema_suite["beneficial"], "d_no_drift_decay_fired": decay_climbs,
                 "on_state_exists": on_state_exists},
        "_sims": {"base": sim_base, "ema_final": readouts[ETA_EMA][-1], "naive": sim_fast_final,
                  "adv": sim_twin},
        "core_idx": core_idx, "off_core": off_core,
    }


# ---------------------------------------------------------------- distribution-shift round (lifelong stress test)
def distribution_shift_stage(name, items, base_vecs, step_vecs, grown_shift, step_toks, index, nb):
    """The real lifelong-learning stress test: after the same-domain continual run, read a NEW MODERN DOMAIN
    (scientific-prose textbook, distinct from the simplewiki general-knowledge growth corpus) as one more
    round, and ask whether the anchor HOLDS under the domain shift. Catastrophic interference bites hardest
    under distribution shift, so a slow anchor that survives it -- while the no-anchor DECAY control does not --
    is the strong evidence. The grown store at the shift round is CORE-ARG SELPREF over (simplewiki-15M +
    new-domain); the read-out = keep-both(slow anchor advanced one step at rate eta, fast shifted grown). We
    compare each arm's corruption at the shift to its corruption at the last same-domain round."""
    steps_shift = list(step_toks) + [SHIFT_TOK]
    sv = dict(step_vecs); sv[SHIFT_TOK] = grown_shift
    sim_base = S.dense_vec_cosine_fn(base_vecs, index)
    off = G.score_items(items, sim_base)
    arms = {}
    for eta in (ETA_FROZEN, ETA_EMA, ETA_DECAY):
        outs, _ = slow_store_readouts(items, base_vecs, sv, steps_shift, index, eta)
        arms[eta] = {"pre": G.score_items(items, outs[-2]), "shift": G.score_items(items, outs[-1])}

    def defined(i):
        return off[i] is not None and all(arms[e][k][i] is not None for e in arms for k in ("pre", "shift"))
    ci = [i for i in range(len(items)) if defined(i)]
    if len(ci) < 30:
        return {"downstream": name, "verdict": "ABORT_COVERAGE", "n_core": len(ci)}
    oc = [off[i] for i in ci]
    out = {"downstream": name, "n_core": len(ci)}
    for eta, nm in ((ETA_FROZEN, "FROZEN"), (ETA_EMA, "EMA"), (ETA_DECAY, "DECAY")):
        pre = [arms[eta]["pre"][i] for i in ci]; sh = [arms[eta]["shift"][i] for i in ci]
        corr_pre = G.corruption_rate(oc, pre, SEED + 1, nb)["corruption_right_to_wrong"]
        corr_sh = G.corruption_rate(oc, sh, SEED + 2, nb)["corruption_right_to_wrong"]
        gain_sh = G.paired_delta_acc(sh, oc, SEED + 3, nb)
        shift_drift = C.paired_corruption_delta(oc, sh, pre, SEED + 4, nb)   # shift - pre-shift corruption
        out[nm] = {"corr_preshift": corr_pre, "corr_shift": corr_sh, "gain_shift": gain_sh,
                   "shift_minus_preshift_corruption": shift_drift,
                   "safe_under_shift": bool(corr_sh["ci"][1] is not None and corr_sh["ci"][1] < CORRUPTION_BOUND),
                   "no_extra_drift_from_shift": bool(not shift_drift["separated_above"])}
    ema_sh = [arms[ETA_EMA]["shift"][i] for i in ci]; dec_sh = [arms[ETA_DECAY]["shift"][i] for i in ci]
    decay_vs_ema_shift = C.paired_corruption_delta(oc, dec_sh, ema_sh, SEED + 5, nb)
    out["decay_vs_ema_under_shift"] = decay_vs_ema_shift
    out["decay_worse_under_shift"] = bool(decay_vs_ema_shift["separated_above"])
    # the anchor HOLDS under the domain shift = the EMA anchor takes on no CI-separated EXTRA drift from the
    # shift (its corruption at the shift is not CI-above its pre-shift corruption).
    out["anchor_holds_under_shift"] = bool(out["EMA"]["no_extra_drift_from_shift"])
    return out


# ---------------------------------------------------------------- rollback (bar c) -- CG.rollback_gate verbatim
def rollback_suite(items, off_core, core_idx, sim_base, sim_ema_final, sim_naive, sim_adv, nb, n_seeds=16):
    """Live rollback at the final round: ACCEPT the good EMA_ANCHOR update, ROLL BACK a NAIVE-overwrite and an
    ADVERSARIAL filler-shuffle update; a random-decision control does NOT protect. hdlab.cls_growth verbatim.
    base_correct_idx = the original-`items` indices OFF got right (known-correct set). The random control is a
    coin-flip accept/reject per update; ONE flip can protect by luck, so we AGGREGATE the random policy's
    working corruption over n_seeds and compare its MEAN on the bad updates to the gate's protected level (the
    gate rolls bad updates back -> prior working corruption). A gate that protects leaves the working set at
    prior; a random policy accepts ~half the bad updates and so leaves it materially higher, in expectation."""
    base_correct_idx = [core_idx[p] for p, v in enumerate(off_core) if v == 1]
    updates = {"EMA_ANCHOR_good": sim_ema_final, "NAIVE_overwrite_bad": sim_naive,
               "ADVERSARIAL_fillershuf_bad": sim_adv}
    rep = CG.rollback_gate(items, base_correct_idx, sim_prior=sim_base, updates=updates,
                           tolerance=CORRUPTION_BOUND, seed=SEED + 300)
    good = rep["updates"]["EMA_ANCHOR_good"]["decision"] == "ACCEPT"
    naive_rb = rep["updates"]["NAIVE_overwrite_bad"]["decision"] == "ROLLBACK"
    adv_rb = rep["updates"]["ADVERSARIAL_fillershuf_bad"]["decision"] == "ROLLBACK"
    gate_protects = bool(good and naive_rb and adv_rb)
    prior_wc = rep.get("prior_working_corruption") or 0.0
    # gate's protected working corruption on the bad updates (rolled back -> prior).
    gate_bad_wc = prior_wc
    # random policy: mean working corruption on the two bad updates across n_seeds coin flips.
    bad = ("NAIVE_overwrite_bad", "ADVERSARIAL_fillershuf_bad")
    rvals = []
    for s in range(n_seeds):
        r = CG.rollback_gate(items, base_correct_idx, sim_prior=sim_base, updates=updates,
                             tolerance=CORRUPTION_BOUND, seed=SEED + 400 + s)
        for nm in bad:
            wc = r["random_control"][nm]["working_corruption"]
            if wc is not None:
                rvals.append(wc)
    random_mean_bad_wc = float(np.mean(rvals)) if rvals else None
    random_fails = bool(random_mean_bad_wc is not None and random_mean_bad_wc > gate_bad_wc + 0.02)
    return {"report": rep, "gate_protects": gate_protects,
            "random_control_fails_to_protect": random_fails,
            "gate_bad_working_corruption": round(gate_bad_wc, 4),
            "random_mean_bad_working_corruption": None if random_mean_bad_wc is None else round(random_mean_bad_wc, 4)}


# ---------------------------------------------------------------- main
def run(mode):
    cfg = G.MODE_CFG[mode]
    steps = STEPS_SMOKE if mode == "smoke" else STEPS_FULL
    nb = cfg["n_boot"]; mc = cfg["ctx_min_count"]
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- downstreams ----
    print("[items] LitBank who-did-what (inherited) + MODERN UD-EWT (held-out) ...", flush=True)
    items_lit = G.build_paraphrase_items(docs=None)
    items_mod = build_modern_paraphrase_items()
    force = set()
    for it in items_lit + items_mod:
        force.add(it["query"]); force.update(it["cand"])
    print("[items] litbank=%d modern=%d force_words=%d" % (len(items_lit), len(items_mod), len(force)),
          flush=True)

    # ---- load the biggest parse ONCE; slice cumulative prefixes (valid POS cache -> no stale-5M problem) ----
    big = steps[-1]
    parsed_all, ntok_all = S.load_parsed(G.cache_path(big), big)
    print("[load] %d sent / %d tok (biggest round)" % (len(parsed_all), ntok_all), flush=True)
    cum = np.cumsum([len(s) for s in parsed_all])

    def prefix(tok):
        k = int(np.searchsorted(cum, tok)) + 1
        return parsed_all[:min(k, len(parsed_all))]

    toks_all = S.token_sents(parsed_all)
    index = S.build_vocab(toks_all, force, cfg["vocab_cap"], cfg["min_count"])
    print("[vocab] %d words" % len(index), flush=True)

    # ---- per-round CORE-ARG SELPREF stores (the capstone's best feed), on cumulative prefixes ----
    step_vecs = {}
    for t in steps:
        tb = time.time()
        step_vecs[t] = AL.coreslot_vectors(prefix(t), index, mc)
        print("  [svd] round %d done (%.1fs)" % (t, time.time() - tb), flush=True)
    # ---- info-free growth twin store (filler-shuffle at the biggest budget) ----
    print("[twin] filler-shuffle SELPREF at %d tok (info-free growth twin) ..." % big, flush=True)
    sp_fshuf, _ = G.build_selpref_fillershuffle_cooc(prefix(big), index,
                                                     np.random.default_rng(SEED + 21), min_count=mc)
    sim_fshuf = S.dense_vec_cosine_fn(S.svd_vectors(S.ppmi_matrix(sp_fshuf), seed=SEED), index)

    # ---- evaluate the full suite on BOTH downstreams ----
    res = {}
    for name, items in (("litbank_old", items_lit), ("modern_ud_ewt_heldout", items_mod)):
        res[name] = evaluate_downstream(name, items, step_vecs, sim_fshuf, steps, index, nb)

    # ---- rollback (bar c) on each downstream, at the final round (deployed arm = EMA anchor) ----
    for name, items in (("litbank_old", items_lit), ("modern_ud_ewt_heldout", items_mod)):
        d = res[name]
        if d.get("verdict") == "ABORT_COVERAGE":
            continue
        sims = d["_sims"]
        rb = rollback_suite(items, d["off_core"], d["core_idx"], sims["base"], sims["ema_final"],
                            sims["naive"], sims["adv"], nb)
        d["rollback"] = {"gate_protects": rb["gate_protects"],
                         "random_control_fails_to_protect": rb["random_control_fails_to_protect"],
                         "gate_bad_working_corruption": rb["gate_bad_working_corruption"],
                         "random_mean_bad_working_corruption": rb["random_mean_bad_working_corruption"],
                         "report": rb["report"]}

    # ---- seed-robustness: is the headline a single-draw artifact? rebuild base(anchor) + grown(terminal) at
    #      3 SVD seeds and confirm the FROZEN-anchor terminal gain + corruption POINT estimates replicate. ----
    print("[seeds] FROZEN-anchor robustness over 3 SVD seeds ...", flush=True)
    seed_rob = {"litbank_old": [], "modern_ud_ewt_heldout": []}
    base_parsed = prefix(steps[0]); grown_parsed = prefix(big)
    for sd in (SEED + 101, SEED + 102, SEED + 103):
        simb = S.dense_vec_cosine_fn(coreslot_vecs_seed(base_parsed, index, mc, sd), index)
        simg = S.dense_vec_cosine_fn(coreslot_vecs_seed(grown_parsed, index, mc, sd), index)
        for name, items in (("litbank_old", items_lit), ("modern_ud_ewt_heldout", items_mod)):
            fused = _ens(simb, simg, items, "mean")
            off = G.score_items(items, simb); fus = G.score_items(items, fused)
            ci = [i for i in range(len(items)) if off[i] is not None and fus[i] is not None]
            oa = np.asarray([off[i] for i in ci]); fa = np.asarray([fus[i] for i in ci])
            rmask = oa == 1
            corr = float((fa[rmask] == 0).mean()) if rmask.sum() else None
            seed_rob[name].append({"seed": sd, "gain": round(float(fa.mean() - oa.mean()), 4),
                                   "corruption": None if corr is None else round(corr, 4),
                                   "n_base_right": int(rmask.sum())})
    for name in seed_rob:
        gs = [r["gain"] for r in seed_rob[name]]; cs = [r["corruption"] for r in seed_rob[name]]
        print("  [seeds] %-22s FROZEN gain=%s corr=%s" % (name, gs, cs), flush=True)

    # ---- distribution-shift round: read a NEW MODERN DOMAIN (biology textbook) and test the anchor holds ----
    bio_cache = os.path.join(OUTPUT_DIR, "parsed_biology_shift.jsonl")
    shift_res = None
    if os.path.exists(bio_cache):
        bio_parsed, bio_ntok = S.load_parsed(bio_cache, 10 ** 9)
        print("[shift] NEW DOMAIN (biology textbook) %d sent / %d tok -> building shifted grown store ..."
              % (len(bio_parsed), bio_ntok), flush=True)
        grown_shift = AL.coreslot_vectors(parsed_all + bio_parsed, index, mc)
        shift_res = {}
        for name, items in (("litbank_old", items_lit), ("modern_ud_ewt_heldout", items_mod)):
            shift_res[name] = distribution_shift_stage(name, items, step_vecs[steps[0]], step_vecs,
                                                       grown_shift, steps, index, nb)
            r = shift_res[name]
            if r.get("verdict") != "ABORT_COVERAGE":
                print("  [shift] %-22s EMA corr pre->shift %.3f->%.3f (holds=%s) | DECAY %.3f->%.3f | "
                      "decay_worse=%s" % (name, r["EMA"]["corr_preshift"]["rate"], r["EMA"]["corr_shift"]["rate"],
                                          r["anchor_holds_under_shift"], r["DECAY"]["corr_preshift"]["rate"],
                                          r["DECAY"]["corr_shift"]["rate"], r["decay_worse_under_shift"]), flush=True)
    else:
        print("[shift] biology parse cache absent -- run experiments/_parse_shift_corpus_biology.py first "
              "(distribution-shift stage skipped)", flush=True)

    # ---- overall verdict ----
    def summ(name):
        d = res[name]
        b = dict(d.get("bars", {}))
        b["c_rollback"] = bool(d.get("rollback", {}).get("gate_protects"))
        b["c_random_fails_to_protect"] = bool(d.get("rollback", {}).get("random_control_fails_to_protect"))
        b["max_safe_eta"] = d.get("max_safe_eta")
        return b
    lit = summ("litbank_old"); mod = summ("modern_ud_ewt_heldout")
    # (e) GENERALIZES = the brain-faithful EMA anchor is safe+beneficial on the held-out MODERN downstream.
    generalizes_modern_ema = bool(mod.get("a_safe_ema") and mod.get("b_beneficial"))
    # a safe on-state (some anchor arm safe+beneficial+no-climb) exists on BOTH downstreams, rollback protects
    # both, and the DECAY can-fail control fired both.
    on_state_both = bool(lit.get("on_state_exists") and mod.get("on_state_exists"))
    rollback_both = bool(lit.get("c_rollback") and mod.get("c_rollback"))
    decay_both = bool(lit.get("d_no_drift_decay_fired") and mod.get("d_no_drift_decay_fired"))
    solved = bool(on_state_both and rollback_both and decay_both)
    decay_fired = decay_both

    if solved and generalizes_modern_ema:
        verdict = ("LIVE_CANARY_SAFE_BENEFICIAL_CONTINUAL__EMA_ANCHOR_GENERALIZES_MODERN__"
                   "SAFE_ETA_CORPUS_DEPENDENT")
    elif solved:
        verdict = "LIVE_CANARY_SAFE_BENEFICIAL_CONTINUAL_AT_ANCHOR__EMA_MARGIN_TIGHT_ON_OLD_FICTION"
    else:
        verdict = "GATE_LOCATED_NEGATIVE__see_per_downstream_suites"
    print("[verdict] %s | lit=%s mod=%s | %.0fs" % (verdict, lit, mod, time.time() - t0), flush=True)

    # strip non-serialisable closures / bulky per-item arrays from the persisted metrics
    for name in res:
        for k in ("_sims", "core_idx", "off_core"):
            res[name].pop(k, None)

    _write({
        "anchor_name": ANCHOR, "mode": mode, "seed": SEED,
        "pre_registered": {"corruption_bound": CORRUPTION_BOUND, "probe_frac": PROBE_FRAC},
        "steps_tok": steps, "n_tokens_biggest": ntok_all, "vocab": len(index),
        "config": dict(cfg, svd_k=S.SVD_K),
        "downstreams": res,
        "bars": {"litbank_old": lit, "modern_ud_ewt_heldout": mod},
        "generalizes_modern_ema": generalizes_modern_ema, "on_state_both": on_state_both,
        "rollback_both": rollback_both, "decay_can_fail_control_fired": decay_fired,
        "seed_robustness_frozen": seed_rob,
        "distribution_shift": shift_res,
        "verdict": verdict, "elapsed_s": round(time.time() - t0, 1),
    })
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        return run(args.mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _crash(e)
        raise


if __name__ == "__main__":
    sys.exit(main())
