"""exp_learner_growth_aligned_continual_v1 -- FULL-SOLUTION extension #1 (items 1,2,4) for
notes/problems/turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation.

exp_learner_on_clean_foundation_v1 established: the learner turns ON safe+beneficial via CLS keep-both-stores
(corruption 0.093 CI[0.067,0.124]<0.15, gain +0.054), and DIAGNOSED that the ~9% corruption is
REPRESENTATION-INTRINSIC -- it comes from the grown store rebuilding its SVD coordinate frame, so
random-dropping input edges leaves corruption unchanged (random-drop == noisy == 0.093, the ensemble floor).
This cell tries to CROSS that floor with the brain-faithful fix, proves the safety over CONTINUAL growth, and
reports the recovery-vs-corruption decomposition.

BRAIN MECHANISM (opening move): the batch "refit the whole store then fuse" is NOT how the neocortex grows.
Complementary Learning Systems consolidation is INCREMENTAL and frame-PRESERVING -- new experience is
integrated into the EXISTING representational geometry (slow, interleaved), not by re-deriving a fresh
coordinate frame each time. Two independently truncated SVDs share no coordinate correspondence (unique only
up to an orthogonal rotation of equal singular values), so fusing them mixes two unaligned frames -- exactly
the reorganisation that corrupts. The faithful fix is to ALIGN the grown frame to the pre-growth frame before
fusing (orthogonal Procrustes -- the closed-form best rotation), so growth moves vectors WITHIN one geometry
instead of rotating the whole space. This is the incremental/aligned analogue of online consolidation.

BRAIN-FIDELITY LABELS (no mislabelling -- the one thing barred):
  * CLS keep-both-stores (fuse pre-growth + grown, never overwrite)                  -- PINNED (McClelland/O'Reilly 1995).
  * CLS_RELIABILITY = precision-weighted cue integration (trust each store by its     -- PINNED (Ernst & Banks 2002;
      per-query decisiveness/margin)                                                       Friston precision; the substrate's own convergent-cue reader).
  * CLS_ALIGNED = preserve the existing representational GEOMETRY when integrating     -- brain-CONSISTENT principle (frame preservation =
      new experience (Procrustes = the closed-form frame-alignment)                         anti-catastrophic-forgetting), Procrustes algebra = OUR-INVENTION-UNDER-TEST.
  * ROLLBACK against a held-out known-correct probe = do not consolidate an update     -- brain-CONSISTENT (ACC/hippocampal error-monitoring +
      that raises error on established knowledge                                            schema-gated consolidation, Tse 2007); the probe/threshold = OUR-INVENTION.
  * CLS_UNALIGNED (average two UNALIGNED frames) = the anti-brain control (frame-mixing) -- must LOSE.

ITEM 1 (cross the floor): does any brain-faithful fusion push corruption BELOW the keep-both floor?
  Arms: CLS_ENSEMBLE (v1's z-scored-cosine keep-both -- the incumbent best, frame-safe by construction);
  CLS_RELIABILITY (PINNED precision-weighted cue integration -- the brain's way to fuse DISAGREEING stores,
  the mechanism most likely to cross a disagreement floor); CLS_ALIGNED (frame-preservation via Procrustes);
  CLS_UNALIGNED (the anti-brain control -- average two unaligned SVD frames, must NOT cross the floor).
ITEM 2 (continual): grow in steps 5M->8M->11M->15M (prefixes of the 15M cache, sliced in memory). At each
  step fuse the RUNNING store with the new cumulative store (aligned vs unaligned), measure corruption of the
  ORIGINAL 5M-correct probe + gain at each step + run the rollback gate. Shows whether iterating the fusion
  COMPOUNDS corruption toward the naive 0.26 (unaligned) or stays bounded (aligned) -- the lifetime-learning
  safety claim.
ITEM 4 (decomposition): for every arm report recovery_wrong_to_right alongside corruption_right_to_wrong and
  the RATIO (answers fixed per answer broken) -- "net-beneficial after accounting for forgetting" as one
  decisive number.

FEED: the CORE-ARG extraction (v1's best on-state -- SELPREF restricted to core grammatical roles), so this
builds on the best foundation. Downstream = the SAME LitBank who-did-what verb-paraphrase (G, verbatim).

Run: .venv/Scripts/python.exe experiments/exp_learner_growth_aligned_continual_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_learner_growth_aligned_continual_v1.py --mode smoke
     .venv/Scripts/python.exe experiments/exp_learner_growth_aligned_continual_v1.py --mode full

REUSED VERBATIM (READ-ONLY): exp_structured_context_learner_v1 (S), exp_learner_safety_gate_v1 (G),
exp_growth_cls_ensemble_v1 (C), exp_learner_on_clean_foundation_v1 (M -- build_coreslot_selpref,
rollback_eval, SEED, CORRUPTION_BOUND, PROBE_FRAC). Writes ONLY to data/exp_learner_growth_aligned_continual_v1/.
ASCII only. Deterministic (fixed seeds). Does NOT modify hdlab/ or any other cell.
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
for p in (REPO_ROOT, os.path.join(REPO_ROOT, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_structured_context_learner_v1 as S   # noqa: E402
import experiments.exp_learner_safety_gate_v1 as G          # noqa: E402
import experiments.exp_growth_cls_ensemble_v1 as C          # noqa: E402
import experiments.exp_learner_on_clean_foundation_v1 as M  # noqa: E402

ANCHOR = "learner_growth_aligned_continual_v1"
from experiments._seed_checkpoint import get_output_dir  # Q115: canonical shared output dir (same FULL path)
OUTPUT_DIR = str(get_output_dir(ANCHOR))
SEED = M.SEED
ALPHA = 0.5                       # keep-both convex weight (OUR-INVENTION-UNDER-TEST; 0.5 = equal keep-both)
STEPS_FULL = [5_000_000, 8_000_000, 11_000_000, 15_000_000]
STEPS_SMOKE = [150_000, 220_000, 300_000]


# --------------------------------------------------------------------------- aligned-basis fusion
def procrustes_rotation(src_shared, ref_shared):
    """Closed-form orthogonal Procrustes: R (d x d) minimizing ||src_shared @ R - ref_shared||_F over the
    SHARED rows. R = U @ Vt where U,S,Vt = svd(src_shared.T @ ref_shared). Orthogonal -> norm-preserving."""
    Mmat = src_shared.T @ ref_shared
    U, _s, Vt = np.linalg.svd(Mmat, full_matrices=False)
    return U @ Vt


def _l2norm_rows(V):
    n = np.linalg.norm(V, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return V / n


def align_and_fuse(ref_vecs, ref_idx, new_vecs, new_idx, alpha, do_align):
    """Keep-both-stores in a SHARED FRAME. Align new_vecs to ref_vecs's frame on the shared vocab (Procrustes
    rotation), L2-normalise both, convex-combine per word over the UNION vocab: fused = (1-a)*ref + a*new for
    shared words, ref-only or new(aligned)-only otherwise. Returns (fused_vecs, union_index). do_align=False
    is the control: average the two UNALIGNED frames (no rotation) -- expected to be meaningless."""
    shared = [w for w in ref_idx if w in new_idx]
    if do_align and len(shared) >= 10:
        A = np.asarray([new_vecs[new_idx[w]] for w in shared], dtype=np.float64)
        B = np.asarray([ref_vecs[ref_idx[w]] for w in shared], dtype=np.float64)
        R = procrustes_rotation(A, B)
        new_aligned = new_vecs @ R
    else:
        new_aligned = new_vecs
    ref_n = _l2norm_rows(np.asarray(ref_vecs, dtype=np.float64))
    new_n = _l2norm_rows(np.asarray(new_aligned, dtype=np.float64))
    union = sorted(set(ref_idx) | set(new_idx))
    uidx = {w: i for i, w in enumerate(union)}
    d = ref_n.shape[1]
    fused = np.zeros((len(union), d), dtype=np.float64)
    for w, i in uidx.items():
        inr = w in ref_idx; inn = w in new_idx
        if inr and inn:
            fused[i] = (1.0 - alpha) * ref_n[ref_idx[w]] + alpha * new_n[new_idx[w]]
        elif inr:
            fused[i] = ref_n[ref_idx[w]]
        else:
            fused[i] = new_n[new_idx[w]]
    return fused, uidx


# --------------------------------------------------------------------------- reliability-weighted fusion
# THE PINNED BRAIN MECHANISM for fusing two DISAGREEING memory stores: precision-weighted cue integration
# (Ernst & Banks 2002 multisensory; Friston precision; the substrate's own convergent-cue reader). Each
# store is trusted in proportion to how DECISIVE it is on THIS query (its ranking margin = a precision
# proxy), so where the pre-growth store is confident and the grown store disagrees, the old store dominates
# (protects known answers); where the grown store is decisive (genuine new knowledge), it dominates (gain).
# This directly targets the store-DISAGREEMENT that the frame-safe fixed blend can only average.
def _zsim(sim_fn, mean, std):
    def z(q, c):
        s = sim_fn(q, c)
        return None if s is None else (s - mean) / std
    return z


def reliability_pred(item, z_old, z_new):
    """Per-item precision-weighted keep-both fusion. Weight each store by its ranking MARGIN (top1 - top2
    over the candidates -> decisiveness ~ precision); fuse the z-scored per-candidate similarities by that
    weight; argmax. Falls back to whichever store is defined for a candidate (never discards a live store)."""
    cand = item["cand"]; q = item["query"]
    zo = [z_old(q, c) for c in cand]; zn = [z_new(q, c) for c in cand]
    def margin(zs):
        d = sorted((v for v in zs if v is not None), reverse=True)
        return (d[0] - d[1]) if len(d) >= 2 else (abs(d[0]) if d else 0.0)
    mo, mn = margin(zo), margin(zn)
    tot = mo + mn
    w_old = 0.5 if tot <= 1e-12 else mo / tot
    w_new = 1.0 - w_old
    fused = []
    for a, b in zip(zo, zn):
        if a is None and b is None:
            fused.append(None)
        elif a is None:
            fused.append(b)
        elif b is None:
            fused.append(a)
        else:
            fused.append(w_old * a + w_new * b)
    if all(v is None for v in fused):
        return None
    filled = [v if v is not None else -1e18 for v in fused]
    return cand[int(np.argmax(filled))]


def score_reliability(items, z_old, z_new):
    out = []
    for it in items:
        pred = reliability_pred(it, z_old, z_new)
        out.append(None if pred is None else int(pred == it["target"]))
    return out


def selpref_vectors(parsed, index, min_count):
    M_sp, _ = S.build_selpref_cooc(parsed, index, min_count=min_count)
    return S.svd_vectors(S.ppmi_matrix(M_sp), seed=SEED)


def coreslot_vectors(parsed, index, min_count):
    M_sp, _, _, _ = M.build_coreslot_selpref(parsed, index, min_count=min_count)
    return S.svd_vectors(S.ppmi_matrix(M_sp), seed=SEED)


# --------------------------------------------------------------------------- decomposition (item 4)
def recovery_corruption(base_core, arm_core, seed, n_boot):
    """corruption_right_to_wrong + recovery_wrong_to_right + the fix/break RATIO (answers fixed per answer
    broken). RATIO > 1 => growth fixes more than it breaks (net-beneficial after accounting for forgetting)."""
    rc = G.corruption_rate(base_core, arm_core, seed, n_boot)
    base = np.asarray(base_core, dtype=int); arm = np.asarray(arm_core, dtype=int)
    n_right = int((base == 1).sum()); n_wrong = int((base == 0).sum())
    broke = int(((base == 1) & (arm == 0)).sum())      # right -> wrong
    fixed = int(((base == 0) & (arm == 1)).sum())      # wrong -> right
    ratio = (fixed / broke) if broke else None
    return {"corruption_right_to_wrong": rc["corruption_right_to_wrong"],
            "recovery_wrong_to_right": rc["recovery_wrong_to_right"],
            "n_broke": broke, "n_fixed": fixed, "n_base_right": n_right, "n_base_wrong": n_wrong,
            "fixed_per_broken_ratio": None if ratio is None else round(ratio, 3)}


# --------------------------------------------------------------------------- io / crash
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


# --------------------------------------------------------------------------- self-test
def self_test():
    ok = True

    # (1) Procrustes recovers a known rotation: B = A @ Q for a random orthogonal Q -> recovered R ~= Q, and
    # A @ R ~= B (residual ~0).
    rng = np.random.default_rng(0)
    A = rng.standard_normal((40, 8))
    Qr, _ = np.linalg.qr(rng.standard_normal((8, 8)))    # random orthogonal
    B = A @ Qr
    R = procrustes_rotation(A, B)
    resid = float(np.linalg.norm(A @ R - B))
    ok_p = resid < 1e-6
    print("[self-test] procrustes recovers rotation: residual=%.2e -> %s" % (resid, "OK" if ok_p else "FAIL"),
          flush=True)
    ok = ok and ok_p

    # (2) align_and_fuse: aligning makes a rotated copy fuse COHERENTLY (fused ~ ref direction), while the
    # UNALIGNED average of a rotated copy is INCOHERENT (lower self-similarity to ref). Construct new = ref
    # rotated by Q on shared words; aligned fusion should restore high cosine to ref, unaligned should not.
    words = ["w%d" % i for i in range(30)]
    idx = {w: i for i, w in enumerate(words)}
    ref = rng.standard_normal((30, 8))
    new = ref @ Qr                                        # same meaning, rotated frame
    fa, ua = align_and_fuse(ref, idx, new, idx, alpha=0.5, do_align=True)
    fu, uu = align_and_fuse(ref, idx, new, idx, alpha=0.5, do_align=False)
    refn = _l2norm_rows(ref)
    cos_a = float(np.mean([fa[ua[w]] @ refn[idx[w]] / (np.linalg.norm(fa[ua[w]]) or 1) for w in words]))
    cos_u = float(np.mean([fu[uu[w]] @ refn[idx[w]] / (np.linalg.norm(fu[uu[w]]) or 1) for w in words]))
    ok_f = cos_a > 0.98 and cos_u < cos_a - 0.1
    print("[self-test] aligned fusion coherent (cos_to_ref aligned=%.3f > unaligned=%.3f) -> %s"
          % (cos_a, cos_u, "OK" if ok_f else "FAIL"), flush=True)
    ok = ok and ok_f

    # (3) recovery_corruption decomposition arithmetic: base right {0,1,2,4}, wrong {3}. arm breaks idx1
    # (right->wrong), fixes idx3 (wrong->right). broke=1 fixed=1 ratio=1.0.
    base = [1, 1, 1, 0, 1]; arm = [1, 0, 1, 1, 1]
    d = recovery_corruption(base, arm, seed=1, n_boot=100)
    ok_d = (d["n_broke"] == 1 and d["n_fixed"] == 1 and d["fixed_per_broken_ratio"] == 1.0)
    print("[self-test] decomposition: broke=%d fixed=%d ratio=%s -> %s"
          % (d["n_broke"], d["n_fixed"], d["fixed_per_broken_ratio"], "OK" if ok_d else "FAIL"), flush=True)
    ok = ok and ok_d

    # (4) reliability fusion: when the OLD store is decisive (big margin) and the NEW store disagrees weakly,
    # the fused pick follows the OLD store (protects known answers). Toy: 3 candidates; old picks 'a'
    # decisively (margins large), new picks 'b' weakly -> reliability must keep 'a'.
    zold = {("q", "a"): 3.0, ("q", "b"): -1.0, ("q", "c"): -1.0}   # old: decisive 'a'
    znew = {("q", "a"): 0.0, ("q", "b"): 0.1, ("q", "c"): 0.0}     # new: weak 'b'
    zo = lambda q, c: zold.get((q, c)); zn = lambda q, c: znew.get((q, c))
    pred = reliability_pred({"query": "q", "cand": ["a", "b", "c"], "target": "a"}, zo, zn)
    ok_rel = (pred == "a")
    print("[self-test] reliability keeps the DECISIVE old store's pick over a weak disagreeing new store: "
          "pred=%s -> %s" % (pred, "OK" if ok_rel else "FAIL"), flush=True)
    ok = ok and ok_rel

    # (5) reuse surface
    ok_r = (all(hasattr(S, n) for n in ("build_selpref_cooc", "svd_vectors", "ppmi_matrix",
                                        "dense_vec_cosine_fn", "load_parsed", "token_sents", "build_vocab"))
            and all(hasattr(G, n) for n in ("build_paraphrase_items", "cache_path", "score_items",
                                            "boot_ci", "paired_delta_acc", "corruption_rate", "MODE_CFG"))
            and all(hasattr(M, n) for n in ("build_coreslot_selpref", "rollback_eval", "CORRUPTION_BOUND",
                                            "PROBE_FRAC")))
    print("[self-test] reuse surface present -> %s" % ("OK" if ok_r else "FAIL"), flush=True)
    ok = ok and ok_r

    print("[self-test] " + ("ALL OK" if ok else "FAILED"), flush=True)
    return 0 if ok else 1


# --------------------------------------------------------------------------- main
def run(mode):
    cfg = G.MODE_CFG[mode]
    steps = STEPS_SMOKE if mode == "smoke" else STEPS_FULL
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    nb = cfg["n_boot"]; mc = cfg["ctx_min_count"]

    items = G.build_paraphrase_items(docs=None)
    force = set()
    for it in items:
        force.add(it["query"]); force.update(it["cand"])
    print("[items] n=%d" % len(items), flush=True)

    # Load the largest parse ONCE; slice cumulative prefixes in memory at each token budget.
    big_tok = steps[-1]
    parsed_all, ntok_all = S.load_parsed(G.cache_path(big_tok), big_tok)
    print("[load] %d sent / %d tok (biggest step)" % (len(parsed_all), ntok_all), flush=True)
    cum = np.cumsum([len(s) for s in parsed_all])
    def prefix(tok):
        k = int(np.searchsorted(cum, tok)) + 1
        return parsed_all[:min(k, len(parsed_all))]

    # Vocab: build on the biggest step (superset), reuse for every prefix so vectors share a row space where
    # a word exists at that budget (build_selpref just yields fewer edges at smaller prefixes).
    toks_all = S.token_sents(parsed_all)
    index = S.build_vocab(toks_all, force, cfg["vocab_cap"], cfg["min_count"])
    print("[vocab] %d words" % len(index), flush=True)

    # Per-step CORE-ARG SELPREF vectors (the best feed) on each cumulative prefix.
    step_parsed = {t: prefix(t) for t in steps}
    step_vecs = {}
    for t in steps:
        tb = time.time()
        step_vecs[t] = coreslot_vectors(step_parsed[t], index, mc)
        print("  [svd] step %d done (%.1fs)" % (t, time.time() - tb), flush=True)
    base_tok = steps[0]

    sim_off = S.dense_vec_cosine_fn(step_vecs[base_tok], index)
    off_vecs = step_vecs[base_tok]

    # ---- single-step arms at the biggest budget: ENSEMBLE (v1) vs ALIGNED vs UNALIGNED ----
    big_vecs = step_vecs[big_tok]
    sim_grown = S.dense_vec_cosine_fn(big_vecs, index)
    mb, sb = C.zscore_params(sim_off, items); mg, sg = C.zscore_params(sim_grown, items)
    sim_ens = C.make_ensemble_sim(sim_off, mb, sb, sim_grown, mg, sg, "mean")
    fused_al, uidx_al = align_and_fuse(off_vecs, index, big_vecs, index, ALPHA, do_align=True)
    fused_un, uidx_un = align_and_fuse(off_vecs, index, big_vecs, index, ALPHA, do_align=False)
    sim_aligned = S.dense_vec_cosine_fn(fused_al, uidx_al)
    sim_unaligned = S.dense_vec_cosine_fn(fused_un, uidx_un)
    # CLS_RELIABILITY: the PINNED precision-weighted cue-integration fusion (scored per-item, not a sim_fn)
    z_old = _zsim(sim_off, mb, sb); z_new = _zsim(sim_grown, mg, sg)
    r_reliability = score_reliability(items, z_old, z_new)

    arms = {"OFF": sim_off, "CLS_ENSEMBLE": sim_ens, "CLS_ALIGNED": sim_aligned,
            "CLS_UNALIGNED": sim_unaligned}
    scores = {nm: G.score_items(items, fn) for nm, fn in arms.items()}
    scores["CLS_RELIABILITY"] = r_reliability
    arms["CLS_RELIABILITY"] = None   # placeholder (scored above); not a pairwise sim_fn
    core_idx = [i for i in range(len(items)) if all(scores[nm][i] is not None for nm in arms)]
    n_core = len(core_idx)
    print("[coverage] " + " ".join("%s=%d" % (nm, sum(x is not None for x in scores[nm])) for nm in arms)
          + " | CORE=%d" % n_core, flush=True)
    if n_core < 30:
        _write({"anchor_name": ANCHOR, "mode": mode, "verdict": "ABORT_COVERAGE", "n_core": n_core})
        return 1
    core = {nm: [scores[nm][i] for i in core_idx] for nm in arms}

    grown_arms = ["CLS_ENSEMBLE", "CLS_ALIGNED", "CLS_UNALIGNED", "CLS_RELIABILITY"]
    arm_acc = {nm: G.boot_ci(core[nm], SEED + 1 + h, nb) for h, nm in enumerate(arms)}
    gains = {nm: G.paired_delta_acc(core[nm], core["OFF"], SEED + 20 + h, nb)
             for h, nm in enumerate(grown_arms)}
    decomp = {nm: recovery_corruption(core["OFF"], core[nm], SEED + 40 + h, nb)
              for h, nm in enumerate(grown_arms)}
    # does ALIGNED or the PINNED RELIABILITY fusion cross the ENSEMBLE corruption floor?
    d_corr_aligned_vs_ens = C.paired_corruption_delta(core["OFF"], core["CLS_ALIGNED"], core["CLS_ENSEMBLE"],
                                                      SEED + 60, nb)
    d_gain_aligned_vs_ens = G.paired_delta_acc(core["CLS_ALIGNED"], core["CLS_ENSEMBLE"], SEED + 61, nb)
    d_corr_reliab_vs_ens = C.paired_corruption_delta(core["OFF"], core["CLS_RELIABILITY"], core["CLS_ENSEMBLE"],
                                                     SEED + 62, nb)
    d_gain_reliab_vs_ens = G.paired_delta_acc(core["CLS_RELIABILITY"], core["CLS_ENSEMBLE"], SEED + 63, nb)
    print("[single-step]")
    for nm in arms:
        extra = ""
        if nm in decomp:
            extra = " corr=%s recov=%s ratio=%s" % (decomp[nm]["corruption_right_to_wrong"]["rate"],
                                                    decomp[nm]["recovery_wrong_to_right"]["rate"],
                                                    decomp[nm]["fixed_per_broken_ratio"])
        print("  %-14s acc=%s gain=%s%s" % (nm, arm_acc[nm]["acc"],
              gains[nm]["delta"] if nm in gains else "-", extra), flush=True)
    print("  ALIGNED - ENSEMBLE   corruption: %s | gain: %s" % (d_corr_aligned_vs_ens, d_gain_aligned_vs_ens),
          flush=True)
    print("  RELIABILITY-ENSEMBLE corruption: %s | gain: %s (PINNED precision-weighted cue integration)"
          % (d_corr_reliab_vs_ens, d_gain_reliab_vs_ens), flush=True)
    aligned_crosses_floor = bool(d_corr_aligned_vs_ens["separated_below"]
                                 and not d_gain_aligned_vs_ens["separated_below"])
    reliability_crosses_floor = bool(d_corr_reliab_vs_ens["separated_below"]
                                     and not d_gain_reliab_vs_ens["separated_below"])
    any_crosses_floor = bool(aligned_crosses_floor or reliability_crosses_floor)
    aligned_beats_unaligned = bool(gains["CLS_ALIGNED"]["separated_above"]
                                   and not gains["CLS_UNALIGNED"]["separated_above"])

    # ---- continual multi-step: RUNNING aligned vs unaligned fusion over the steps ----
    print("[continual] running fusion over steps %s" % steps, flush=True)
    base_correct_idx = [core_idx[p] for p, v in enumerate(core["OFF"]) if v == 1]

    def run_continual(do_align):
        run_vecs, run_idx = off_vecs, index
        curve = []
        for t in steps[1:]:
            run_vecs, run_idx = align_and_fuse(run_vecs, run_idx, step_vecs[t], index, ALPHA, do_align)
            sim_run = S.dense_vec_cosine_fn(run_vecs, run_idx)
            sc = G.score_items(items, sim_run)
            cc = [sc[i] if sc[i] is not None else 0 for i in core_idx]     # None -> wrong (conservative)
            g = G.paired_delta_acc(cc, core["OFF"], SEED + 80, nb)
            rcm = recovery_corruption(core["OFF"], cc, SEED + 81, nb)
            # rollback gate on the ORIGINAL 5M-correct probe at this step
            rb = M.rollback_eval(items, base_correct_idx, sim_prior=sim_off,
                                 updates={"step_%d" % t: sim_run},
                                 tolerance=M.CORRUPTION_BOUND, seed=SEED + 82, n_boot=nb)
            step_rec = {"tok": t, "acc": G.boot_ci(cc, SEED + 83, nb)["acc"],
                        "gain_vs_off": g, "corruption": rcm["corruption_right_to_wrong"]["rate"],
                        "fixed_per_broken_ratio": rcm["fixed_per_broken_ratio"],
                        "rollback_decision": rb["updates"]["step_%d" % t]["decision"],
                        "probe_corruption": rb["updates"]["step_%d" % t]["probe_corruption"]}
            curve.append(step_rec)
            print("  %s align=%s: acc=%.4f gain=%+.4f corr=%.4f ratio=%s rollback=%s"
                  % (t, do_align, step_rec["acc"], g["delta"], step_rec["corruption"],
                     step_rec["fixed_per_broken_ratio"], step_rec["rollback_decision"]), flush=True)
        return curve

    curve_aligned = run_continual(True)
    curve_unaligned = run_continual(False)
    final_corr_aligned = curve_aligned[-1]["corruption"]
    final_corr_unaligned = curve_unaligned[-1]["corruption"]
    # non-compounding = final aligned corruption <= the single-step aligned corruption bound (does not drift up)
    aligned_bounded = bool(all(s["corruption"] is not None and s["corruption"] < M.CORRUPTION_BOUND
                               for s in curve_aligned))
    continual_safe = bool(aligned_bounded and all(s["rollback_decision"] == "ACCEPT" for s in curve_aligned))

    best_ratio = max(d["fixed_per_broken_ratio"] for d in decomp.values()
                     if d["fixed_per_broken_ratio"] is not None)
    floor_txt = "SOME_FUSION_CROSSES_FLOOR" if any_crosses_floor else "CORRUPTION_FLOOR_IS_STORE_DISAGREEMENT_NO_FUSION_CROSSES"
    verdict = "%s__CONTINUAL_%s__NET_FIXED_PER_BROKEN_%.1f" % (
        floor_txt, "ROLLBACK_BOUNDED" if continual_safe else "ROLLBACK_GATE_BOUNDS_DRIFT", best_ratio)
    print("[verdict] %s | aligned_crosses=%s reliability_crosses=%s aligned_beats_unaligned=%s "
          "continual_safe=%s best_ratio=%.1f | %.0fs"
          % (verdict, aligned_crosses_floor, reliability_crosses_floor, aligned_beats_unaligned,
             continual_safe, best_ratio, time.time() - t0), flush=True)

    _write({
        "anchor_name": ANCHOR, "mode": mode, "seed": SEED, "alpha": ALPHA, "steps": steps,
        "config": dict(cfg, svd_k=S.SVD_K), "n_core": n_core, "n_tokens_biggest": ntok_all,
        "vocab": len(index),
        "arm_accuracy": arm_acc, "gains_vs_off": gains,
        "decomposition_single_step": decomp, "best_fixed_per_broken_ratio": best_ratio,
        "cross_floor_attempts": {
            "aligned_vs_ensemble": {"corruption_delta": d_corr_aligned_vs_ens,
                                    "gain_delta": d_gain_aligned_vs_ens,
                                    "crosses_floor": aligned_crosses_floor},
            "reliability_vs_ensemble_PINNED": {"corruption_delta": d_corr_reliab_vs_ens,
                                               "gain_delta": d_gain_reliab_vs_ens,
                                               "crosses_floor": reliability_crosses_floor},
            "any_crosses_floor": any_crosses_floor,
            "aligned_beats_unaligned": aligned_beats_unaligned},
        "continual": {"aligned": curve_aligned, "unaligned": curve_unaligned,
                      "final_corruption_aligned": final_corr_aligned,
                      "final_corruption_unaligned": final_corr_unaligned,
                      "aligned_bounded_all_steps": aligned_bounded, "continual_safe": continual_safe},
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
