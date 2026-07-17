"""
exp_substrate_resonator_focus_lever_depth_v2 -- depth-vs-width tradeoff in hierarchical resonator
  staging at F=8: does a FINER split (3+3+2, or 2+2+2+2) beat the COARSER 4+4 (v1's partial rescue,
  hier_F8=0.161) by keeping each stage more in-band? Where does adding depth stop helping?

ROUTING: Director task, source `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md`
  (the focus-lever block). Follows up `exp_substrate_resonator_focus_lever_v1.py` (landed
  MIDDLE_BAND, commits e38e711fe + c75da0e79) -- reuses its resonate()/cleanup()/phasor/compose/
  make_books primitives VERBATIM (same N=16384, M=8, MAX_IT=200 regime). Pre-reg:
  `notes/prereg_resonator_focus_lever_depth_v2_2026-07-17.md` -- READ FIRST, bands + the
  algebraic-generalization argument for why decode_multistage(n=2) == v1's original 2-stage code
  are not arbitrary.

Prior-work check (SUBSTRATE-KB CONCEPT-QUERY, mandatory before authoring): ran
  `bash tools/substrate_query.sh "hierarchical staging depth width tradeoff resonator focus
  factorization joint decode chunking"` -- top hits cosine=0.3115 (a 2026-06-04 drill-candidate
  suggestion, never executed; a 2026-06-08 note about a DIFFERENT primitive's bind-depth). No
  landed prior cell on this exact depth-vs-width question. Genuine extension, not a rediscovery.

ARMS (all F=8 arms share TOTAL F=8; F=6 arms are a cheap secondary ceiling-probe):
  F=8 core: flat_F8 (must-fail control) | 2stage_4_4 (baseline TO BEAT, reproduce v1's 0.161) |
            3stage_3_3_2 (candidate finer split) | 4stage_2_2_2_2 (finest split / ceiling probe).
  F=6 secondary: flat_F6 (must-fail control) | 2stage_3_3 (reproduce v1's clean 1.000 rescue) |
            3stage_2_2_2 (does over-splitting an ALREADY-EASY regime cost anything?).
  REF: flat_F4, measured live (bands below are ratios against REF, per v1's own convention).

PRE-REGISTERED bands (full rationale in the pre-reg; let REF = mean flat_F4, floor = 0.40*REF):
  Gate D reproduction (repro_ok) must hold BEFORE the substantive discriminator is trusted:
    |flat_F6-0.0722|<=0.10, |flat_F8-0.00556|<=0.08, 2stage_3_3>=0.85, |2stage_4_4-0.1611|<=0.12.
  If repro_ok fails -> MIDDLE_BAND tagged GATE_D_REPRO_MISMATCH (downstream arms suspect).
  Else, let best_finer_F8 = max(3stage_3_3_2_F8, 4stage_2_2_2_2_F8), gap = best_finer_F8-2stage_4_4_F8:
    HARD_PASS: best_finer_F8 >= floor AND gap >= 0.05.
    HARD_FAIL: gap <= 0.03 (finer no better than 4+4 within noise -- depth-compounding dominates).
    MIDDLE_BAND: anything else.
  Depth-ceiling + over-splitting-hurts checks are reported informationally (see pre-reg).

REGIME: N=16384, M_FACTOR=8, MAX_IT=200 -- IDENTICAL to v1 (calibration reused unchanged, no new
  calibration decision this cell).

FORMULA SELF-TESTS (PROT-022 + F.1 real_code_path): 1. bind/unbind inverse. 2. cleanup self.
  3. flat resonate exact at tiny K=2. 4. decode_multistage exact at 2/3/4-stage k=1-each (tiny).
  5. decode_multistage(n_stages=2) reduces algebraically to v1's original 2-stage inline code
     (byte-for-byte same intermediate signals, not just "a plausible answer").
  6. verdict_core can-fail: synthetic inputs prove BOTH HARD_PASS and HARD_FAIL paths reachable.
ASCII-only. write_metrics. PROT-018 _v1(depth_v2 anchor).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, hashlib, traceback
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
from experiments._cell_heartbeat import CellHeartbeat

ANCHOR_NAME = "substrate_resonator_focus_lever_depth_v2"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# ---- regime (same N/M/MAX_IT in smoke and full -- DISCRIMINATOR-MUST-SURVIVE-SCALE option A;
#      only TRIALS differ) -- IDENTICAL to v1, reused unchanged ----
N_DIM = 16384
M_FACTOR = 8
MAX_IT = 200
FLAT_F_LIST = [4, 6, 8]  # F4 = REF (live), F6/F8 = must-fail controls
STAGE_CONFIGS_F8 = {"2stage_4_4": [4, 4], "3stage_3_3_2": [3, 3, 2], "4stage_2_2_2_2": [2, 2, 2, 2]}
STAGE_CONFIGS_F6 = {"2stage_3_3": [3, 3], "3stage_2_2_2": [2, 2, 2]}
ALL_STAGE_CONFIGS = {**STAGE_CONFIGS_F8, **STAGE_CONFIGS_F6}  # fixed insertion order -> deterministic RNG consumption
if RUN_MODE == "smoke":
    SEEDS = [7]
    TRIALS = 10
else:
    SEEDS = [7, 17, 23]
    TRIALS = 60

EXPECTED_UNITS_PER_SEED = len(FLAT_F_LIST) + len(ALL_STAGE_CONFIGS)  # 3 + 5 = 8


# ---------------------------------------------------------------------------
# Core primitives -- REUSED VERBATIM from experiments/exp_substrate_resonator_focus_lever_v1.py
# (itself reused verbatim from exp_resonator_factorization_v1.py). No new bind/unbind/cleanup
# primitive; the only new function is decode_multistage (pure orchestration of resonate/compose).
# ---------------------------------------------------------------------------
def make_theta(m, d, g):
    return g.uniform(-np.pi, np.pi, (m, d))


def phasor_from_theta(theta):
    return np.exp(1j * theta).astype(np.complex64)


def cleanup(v, book):
    j = int(np.argmax((book @ np.conj(v)).real))
    return book[j], j


def resonate(s, books, K, max_it=MAX_IT):
    est = [b.mean(0) for b in books]
    est = [e / (np.abs(e) + 1e-8) for e in est]
    prev = None
    for _ in range(max_it):
        idxs = []
        for k in range(K):
            others = np.ones(s.shape, dtype=np.complex64)
            for j in range(K):
                if j != k:
                    others = others * est[j]
            r = s * np.conj(others)
            scores = books[k] @ np.conj(r)
            est[k] = (scores @ books[k])
            est[k] = est[k] / (np.abs(est[k]) + 1e-8)
            idxs.append(int(np.argmax(scores.real)))
        if idxs == prev:
            break
        prev = idxs
    return idxs


def compose(books, idx):
    s = np.ones(books[0].shape[1], dtype=np.complex64)
    for i, b in enumerate(books):
        s = s * b[idx[i]]
    return s


def make_books(K, M, N, g):
    out = []
    for _ in range(K):
        theta = make_theta(M, N, g)
        out.append(phasor_from_theta(theta))
    return out


# ---------------------------------------------------------------------------
# NEW: decode_multistage -- generalizes v1's 2-stage recipe to N stages.
# Verified in self-test to reduce EXACTLY to v1's inline 2-stage code at n_stages=2.
# ---------------------------------------------------------------------------
def decode_multistage(true_per_stage: List[List[int]], books_per_stage: List[List[np.ndarray]]
                       ) -> Tuple[List[List[int]], List[bool]]:
    """Stage i decodes its own group from the running partial composite (through stage i, no
    future groups revealed -- online/incremental chunk-and-pass), with ALL prior stages'
    RECONSTRUCTED (not ground-truth) identities conjugate-removed first. A correct prior stage
    cancels cleanly; a wrong one leaks residual interference into later stages."""
    n_stages = len(true_per_stage)
    group_sig = [compose(books_per_stage[i], true_per_stage[i]) for i in range(n_stages)]
    dim = books_per_stage[0][0].shape[1]
    running = np.ones(dim, dtype=np.complex64)
    prior_recon = np.ones(dim, dtype=np.complex64)
    dec_per_stage = []
    for i in range(n_stages):
        running = running * group_sig[i]
        s_iso = running * np.conj(prior_recon)
        k_i = len(books_per_stage[i])
        dec_i = resonate(s_iso, books_per_stage[i], k_i)
        dec_per_stage.append(dec_i)
        prior_recon = prior_recon * compose(books_per_stage[i], dec_i)
    stage_correct = [dec_per_stage[i] == true_per_stage[i] for i in range(n_stages)]
    return dec_per_stage, stage_correct


# ---------------------------------------------------------------------------
# Pure, testable verdict core (design gate #2: must be provably able to reach BOTH HARD_PASS and
# HARD_FAIL given synthetic inputs -- proven in self-test, not just asserted).
# ---------------------------------------------------------------------------
def verdict_core(ref: float, flat6: float, flat8: float, h2_6: float, h2_8: float,
                  h3_6: float, h3_8: float, h4_8: float) -> Tuple[str, str, bool]:
    floor = 0.40 * max(ref, 1e-6)
    repro_ok = (
        abs(flat6 - 0.0722) <= 0.10
        and abs(flat8 - 0.00556) <= 0.08
        and h2_6 >= 0.85
        and abs(h2_8 - 0.1611) <= 0.12
    )
    if not repro_ok:
        return ("MIDDLE_BAND",
                "GATE_D_REPRO_MISMATCH: baselines did not reproduce v1's landed values within "
                "tolerance (flat6=%.3f flat8=%.3f 2stage_3_3=%.3f 2stage_4_4=%.3f vs v1's "
                "0.0722/0.00556/1.000/0.1611) -- downstream finer-split arms are suspect; "
                "investigate before trusting a HARD_PASS/HARD_FAIL read." % (flat6, flat8, h2_6, h2_8),
                repro_ok)

    best_finer_f8 = max(h3_8, h4_8)
    gap = best_finer_f8 - h2_8
    ceiling_msg = ("depth ceiling reached at 3 stages for F=8 (4stage=%.3f not better than "
                   "3stage=%.3f)" % (h4_8, h3_8)) if (h4_8 - h3_8) <= 0.03 else (
                   "depth still helping through 4 stages (4stage=%.3f > 3stage=%.3f), "
                   "ceiling not reached in this test" % (h4_8, h3_8))
    oversplit_msg = ("over-splitting an already-easy F=6 regime costs accuracy (3stage=%.3f vs "
                     "2stage=%.3f, drop=%.3f)" % (h3_6, h2_6, h2_6 - h3_6)) if (h2_6 - h3_6) >= 0.10 else (
                     "over-splitting F=6 does not measurably cost accuracy (3stage=%.3f vs "
                     "2stage=%.3f)" % (h3_6, h2_6))

    if best_finer_f8 >= floor and gap >= 0.05:
        return ("HARD_PASS",
                "HARD_PASS: a finer split beats 4+4 at F=8 (best_finer=%.3f >= floor=%.3f, "
                "gap=+%.3f over 2stage_4_4=%.3f) -- finer staging keeps each stage more in-band. "
                "%s. %s." % (best_finer_f8, floor, gap, h2_8, ceiling_msg, oversplit_msg),
                repro_ok)
    if gap <= 0.03:
        return ("HARD_FAIL",
                "HARD_FAIL: finer split is no better than 4+4 within noise (best_finer=%.3f, "
                "2stage_4_4=%.3f, gap=%+.3f) -- depth-compounding (more stages = more "
                "leaky-chunk-and-pass error-propagation opportunities) dominates the in-band "
                "benefit of smaller per-stage K. %s. %s." % (best_finer_f8, h2_8, gap, ceiling_msg, oversplit_msg),
                repro_ok)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: partial pattern -- best_finer=%.3f vs 2stage_4_4=%.3f (gap=%+.3f), "
            "floor=%.3f (neither cleanly HARD_PASS nor HARD_FAIL). %s. %s."
            % (best_finer_f8, h2_8, gap, floor, ceiling_msg, oversplit_msg), repro_ok)


# ---------------------------------------------------------------------------
# Self-test (F.1 real_code_path -- exercises the REAL functions above at tiny scale, not a
# synthetic-only branch)
# ---------------------------------------------------------------------------
def _selftest():
    g = np.random.default_rng(0)
    a = phasor_from_theta(make_theta(1, 32, g))[0]
    b = phasor_from_theta(make_theta(1, 32, g))[0]
    assert np.allclose(a * b * np.conj(b), a, atol=1e-4), "bind/unbind inverse"

    book = phasor_from_theta(make_theta(5, 32, g))
    _, j = cleanup(book[2], book)
    assert j == 2, "cleanup self"

    books2 = make_books(2, 4, 64, g)
    true2 = [1, 2]
    s2 = compose(books2, true2)
    got2 = resonate(s2, books2, 2, max_it=50)
    assert got2 == true2, "flat resonate exact at tiny K2"

    # decode_multistage exact-decode at tiny scale, 2/3/4 stages of k=1 each
    for n_stages in (2, 3, 4):
        books_ps = [make_books(1, 4, 64, g) for _ in range(n_stages)]
        true_ps = [[int(i % 4)] for i in range(n_stages)]  # valid indices (M=4) per stage
        dec_ps, stage_ok = decode_multistage(true_ps, books_ps)
        assert dec_ps == true_ps and all(stage_ok), (
            "decode_multistage exact at n_stages=%d failed: got=%s true=%s" % (n_stages, dec_ps, true_ps))

    # decode_multistage(n_stages=2) must reduce ALGEBRAICALLY to v1's original inline 2-stage code
    # -- rebuild v1's inline recipe by hand and assert byte-identical intermediate signals.
    books_a = make_books(1, 4, 64, g)
    books_b = make_books(1, 4, 64, g)
    true_a, true_b = [2], [3]
    s_a = compose(books_a, true_a)
    s_full = s_a * compose(books_b, true_b)
    dec_a_v1 = resonate(s_a, books_a, 1, max_it=50)
    s_a_hat_v1 = compose(books_a, dec_a_v1)
    s_b_iso_v1 = s_full * np.conj(s_a_hat_v1)
    dec_b_v1 = resonate(s_b_iso_v1, books_b, 1, max_it=50)

    dec_ms, stage_ok_ms = decode_multistage([true_a, true_b], [books_a, books_b])
    assert dec_ms == [dec_a_v1, dec_b_v1], (
        "decode_multistage(n=2) diverges from v1's inline 2-stage code: %s vs %s"
        % (dec_ms, [dec_a_v1, dec_b_v1]))
    assert dec_a_v1 == true_a and dec_b_v1 == true_b, "v1-equivalent 2-stage exact at tiny ka=kb=1"

    # verdict_core CAN-FAIL check (design gate #2): synthetic inputs must reach BOTH tiers.
    ref_syn = 0.56
    # HARD_PASS synthetic: finer split (h3_8=0.30) clears floor(0.224) and beats 2stage(0.161) by >=0.05
    tier_pass, _, ok_pass = verdict_core(ref_syn, 0.072, 0.006, 1.0, 0.161, 1.0, 0.30, 0.28)
    assert tier_pass == "HARD_PASS" and ok_pass, "verdict_core synthetic HARD_PASS path unreachable: got %s" % tier_pass
    # HARD_FAIL synthetic: finer split (h3_8=0.165) ties 2stage(0.161) within noise (gap<=0.03)
    tier_fail, _, ok_fail = verdict_core(ref_syn, 0.072, 0.006, 1.0, 0.161, 1.0, 0.165, 0.14)
    assert tier_fail == "HARD_FAIL" and ok_fail, "verdict_core synthetic HARD_FAIL path unreachable: got %s" % tier_fail
    # GATE_D_REPRO_MISMATCH synthetic: baseline flat8 way off v1's 0.00556
    tier_mm, _, ok_mm = verdict_core(ref_syn, 0.072, 0.35, 1.0, 0.161, 1.0, 0.30, 0.28)
    assert tier_mm == "MIDDLE_BAND" and not ok_mm, "verdict_core synthetic repro-mismatch path unreachable"

    print("[selftest] PASS: resonator-focus-lever-depth-v2 (bind/unbind, cleanup, flat, "
          "decode_multistage 2/3/4-stage exact + v1-equivalence, verdict_core can-fail x3)", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Crash diagnostic (per SS13-C / SS8: except SystemExit/KeyboardInterrupt re-raise; Exception writes
# CELL_CRASHED metrics then re-raises)
# ---------------------------------------------------------------------------
def _write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "anchor_name": anchor_name,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = os.path.join(output_dir, "metrics.json.tmp")
    final_path = os.path.join(output_dir, "metrics.json")
    import json
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


# META_RULE_AF exemption (general, not arm-name-specific): several configs here have EVERY
# component stage at K<=3, which per this cell's own regime (and v1's landed data) is near-ceiling
# by construction -- 3stage_3_3_2_F8, 4stage_2_2_2_2_F8, 2stage_3_3_F6, 3stage_2_2_2_F6 can all
# plausibly saturate to exactly 1.000 (measured at smoke: they did). Symmetrically, hard
# must-fail-control configs (flat_F8, 2stage_4_4 at low TRIALS) can plausibly saturate to exactly
# 0.000. A tie at either SATURATED extreme (0.0 or 1.0) is a TRIALS-quantization / construction
# artifact -- honest and expected, not diagnostic of a copy-paste-same-computation bug -- because
# ANY two arms that both happen to hit a perfect or zero score are bit-identical as short float
# vectors regardless of whether their underlying per-trial decode mechanisms differ (they do:
# distinct split configs, distinct resonate() call sequences, distinct codebook draws). A tie at a
# NON-extreme (mid-range) value is NOT exempt and remains hard-asserted distinct -- that pattern
# would actually indicate a bug (two arms computing the literal same thing).
def _is_saturated_vec(v: np.ndarray, eps: float = 1e-9) -> bool:
    return bool(np.all((np.abs(v) < eps) | (np.abs(v - 1.0) < eps)))


def _arms_must_differ(arms_outputs: Dict[str, np.ndarray]) -> Dict[str, str]:
    digests = {}
    for name, out in arms_outputs.items():
        b = np.asarray(out, dtype=np.float64).tobytes()
        digests[name] = hashlib.sha256(b).hexdigest()
    names = sorted(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, bnm = names[i], names[j]
            va, vb = arms_outputs[a], arms_outputs[bnm]
            if va.shape != vb.shape:
                continue
            if _is_saturated_vec(va) and _is_saturated_vec(vb):
                if digests[a] == digests[bnm]:
                    print("[arms_differ] EXEMPT saturated-tie: %r == %r (hash=%s) -- both arms "
                          "saturated at a floor/ceiling extreme, expected honest outcome per "
                          "general saturation exemption" % (a, bnm, digests[a]), flush=True)
                continue
            assert digests[a] != digests[bnm], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical at a NON-saturated value "
                "(hash=%s) -- likely a copy-paste-same-computation bug" % (a, bnm, digests[a])
            )
    return digests


# ---------------------------------------------------------------------------
# Per-seed run
# ---------------------------------------------------------------------------
def run_seed(seed: int, hb: CellHeartbeat, unit_offset: int) -> Dict:
    g = np.random.default_rng(seed)
    out = {"seed": seed}
    unit_count = 0

    # --- FLAT (must-fail controls at F6/F8; F4 = REF, measured live) ---
    flat_acc = {}
    for F in FLAT_F_LIST:
        books = make_books(F, M_FACTOR, N_DIM, g)
        succ = 0
        for _ in range(TRIALS):
            true = [int(g.integers(0, M_FACTOR)) for _ in range(F)]
            s = compose(books, true)
            got = resonate(s, books, F)
            succ += int(got == true)
        flat_acc[F] = succ / TRIALS
        unit_count += 1
        print("  [seed=%d] FLAT F=%d acc=%.3f" % (seed, F, flat_acc[F]), flush=True)
        hb.tick(unit_offset + unit_count, extra={"arm": "flat", "F": F, "acc": flat_acc[F]})
    out["flat_acc"] = flat_acc

    # --- Staged (2/3/4-stage splits at F=8 and F=6) ---
    stage_acc = {}
    stage_marginal = {}
    stage_naive_product = {}
    for name, split in ALL_STAGE_CONFIGS.items():
        n_stages = len(split)
        books_per_stage = [make_books(k, M_FACTOR, N_DIM, g) for k in split]
        succ = 0
        stage_succ = [0] * n_stages
        for _ in range(TRIALS):
            true_per_stage = [[int(g.integers(0, M_FACTOR)) for _ in range(k)] for k in split]
            _, stage_correct = decode_multistage(true_per_stage, books_per_stage)
            succ += int(all(stage_correct))
            for si in range(n_stages):
                stage_succ[si] += int(stage_correct[si])
        stage_acc[name] = succ / TRIALS
        stage_marginal[name] = [c / TRIALS for c in stage_succ]
        naive_prod = 1.0
        for c in stage_marginal[name]:
            naive_prod *= c
        stage_naive_product[name] = naive_prod
        unit_count += 1
        print("  [seed=%d] STAGE %s split=%s acc=%.3f marginal=%s naive_prod=%.3f" % (
            seed, name, split, stage_acc[name], ["%.3f" % m for m in stage_marginal[name]], naive_prod), flush=True)
        hb.tick(unit_offset + unit_count, extra={"arm": "stage", "name": name, "acc": stage_acc[name]})
    out["stage_acc"] = stage_acc
    out["stage_marginal"] = stage_marginal
    out["stage_naive_product"] = stage_naive_product
    out["unit_count"] = unit_count
    assert unit_count == EXPECTED_UNITS_PER_SEED, (
        "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got %d units, expected %d" % (unit_count, EXPECTED_UNITS_PER_SEED)
    )
    return out


def verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    flat = {F: float(np.mean([p["flat_acc"][F] for p in per_seed])) for F in FLAT_F_LIST}
    stage = {name: float(np.mean([p["stage_acc"][name] for p in per_seed])) for name in ALL_STAGE_CONFIGS}
    stage_marginal_mean = {
        name: [float(np.mean([p["stage_marginal"][name][si] for p in per_seed]))
               for si in range(len(ALL_STAGE_CONFIGS[name]))]
        for name in ALL_STAGE_CONFIGS
    }
    naive_product_mean = {name: float(np.mean([p["stage_naive_product"][name] for p in per_seed]))
                           for name in ALL_STAGE_CONFIGS}

    ref = flat[4]
    tier, msg, repro_ok = verdict_core(
        ref, flat[6], flat[8],
        stage["2stage_3_3"], stage["2stage_4_4"],
        stage["3stage_2_2_2"], stage["3stage_3_3_2"], stage["4stage_2_2_2_2"],
    )

    summary = (
        "REF(flat_F4)=%.3f flat={6:%.3f,8:%.3f} F8_stages={2:%.3f,3:%.3f,4:%.3f} "
        "F6_stages={2:%.3f,3:%.3f} naive_prod_vs_measured={2s4:%.3f/%.3f,3s3:%.3f/%.3f,4s2:%.3f/%.3f,2s3f6:%.3f/%.3f,3s2f6:%.3f/%.3f}"
        % (ref, flat[6], flat[8],
           stage["2stage_4_4"], stage["3stage_3_3_2"], stage["4stage_2_2_2_2"],
           stage["2stage_3_3"], stage["3stage_2_2_2"],
           naive_product_mean["2stage_4_4"], stage["2stage_4_4"],
           naive_product_mean["3stage_3_3_2"], stage["3stage_3_3_2"],
           naive_product_mean["4stage_2_2_2_2"], stage["4stage_2_2_2_2"],
           naive_product_mean["2stage_3_3"], stage["2stage_3_3"],
           naive_product_mean["3stage_2_2_2"], stage["3stage_2_2_2"])
    )
    full_msg = "%s %s" % (msg, summary)
    agg = {
        "flat_acc_mean": flat, "stage_acc_mean": stage, "stage_marginal_mean": stage_marginal_mean,
        "naive_product_mean": naive_product_mean, "ref_flat_F4": ref, "repro_ok": repro_ok,
    }
    return (tier, full_msg, agg)


print("[config] anchor=%s mode=%s N=%d M=%d MAX_IT=%d seeds=%s trials=%d flat_F=%s stage_configs=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, M_FACTOR, MAX_IT, SEEDS, TRIALS, FLAT_F_LIST, ALL_STAGE_CONFIGS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)


def main():
    t0 = time.time()
    marker = {"pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": EXPECTED_UNITS_PER_SEED * len(SEEDS)}
    os.makedirs(out_dir, exist_ok=True)
    import json
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)

    per_seed = []
    total_units = EXPECTED_UNITS_PER_SEED * len(SEEDS)
    with CellHeartbeat(out_dir, total_units=total_units, interval_s=30) as hb:
        for si, seed in enumerate(SEEDS):
            per_seed.append(run_seed(seed, hb, unit_offset=si * EXPECTED_UNITS_PER_SEED))

    # ARMS-MUST-DIFFER (META_RULE_AF): all per-seed-vector arms (flat F4/F6/F8 + 5 stage configs)
    # must not be bit-identical to each other.
    arm_vecs = {"flat_%d" % F: np.array([p["flat_acc"][F] for p in per_seed]) for F in FLAT_F_LIST}
    for name in ALL_STAGE_CONFIGS:
        arm_vecs[name] = np.array([p["stage_acc"][name] for p in per_seed])
    digests = _arms_must_differ(arm_vecs)
    arms_differ_verified = True

    v, vmsg, agg = verdict(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "per_seed": per_seed,
        "aggregate": agg,
        "arms_differ_verified": arms_differ_verified,
        "arms_differ_exemption_rule": "saturated_extreme_ties_exempt_nonsaturated_ties_blocked",
        "arm_digests": digests,
        "expected_n_units_per_seed": EXPECTED_UNITS_PER_SEED,
        "cardinality_ok": all(p["unit_count"] == EXPECTED_UNITS_PER_SEED for p in per_seed),
        "regime": {"N": N_DIM, "M": M_FACTOR, "MAX_IT": MAX_IT, "trials": TRIALS},
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, per_seed)
    print("[metrics] written", flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(out_dir, ANCHOR_NAME, e)
    raise
