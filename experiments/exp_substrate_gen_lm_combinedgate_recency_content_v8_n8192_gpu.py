"""
substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu -- COMBINED recency+content arbitration gate.

CAPSTONE of the attention-routing arc. Both halves of selective admission are proven SEPARATELY:
  - recency-gate v5 (MEASURED_MECHANISM): selects the most-recent slot; flattens noise-compounding.
  - clean-content gate v6 (MM), NOISY-cue content gate v7 (CHAIN_GRADE): INFERS relevance from a noise-floor
    cue (cue_snr~1.8) and routes to the FLAG-cued slot.
This cell tests the ARBITRATION question: a single gate that combines BOTH a recency prior AND a content-cue
bias when both signals are present, and does the RIGHT thing on every sub-regime.

BRAIN-GROUNDING (notes/research_content_gate_brain_grounding_2026-07-08.md): biased-competition (Desimone &
  Duncan 1995; Reynolds & Heeger 2009 normalization) combines MULTIPLE top-down biases through a shared
  normalization pool -- a strong, sharp bias suppresses a weak/flat one WITHOUT a hand-set switch. PBWM
  (Frank/O'Reilly) arbitrates gating by VALUE. The COMBINED gate here = graded competition between a
  recency-prior (fixed top-down bias, in logit units) and a content-cue bias (bottom-up scaled query-key
  match): combined_logit_j = content_rel_j / GATE_TAU + recency_bias_j. softmax over the SUM arbitrates:
  when the content cue is a sharp reliable peak (q/GATE_TAU > recency_bias gap) it wins; when content is flat
  noise (cue absent) the recency prior wins. This is normalization-arbitration, NOT a tuned if/else switch.

CORPUS (the arbitration test): each instance carries BOTH a recency signal and a content signal. Three types,
  mixed ~1/3 each per (seed,K,q):
  - ALIGNED  : FLAG at slot K-2, VALUE (target) at slot K-1 (== most-recent slot). Recency slot == content slot;
               both single gates AND combined are correct. (Control: both signals agree.)
  - CONFLICT : FLAG at slot v-1, VALUE (target) at slot v in {1..K-2} (NOT the most-recent slot); slot K-1 holds
               a DISTRACTOR. CONTENT is ground-truth. A pure-recency gate picks slot K-1 (distractor) -> WRONG.
               A content gate picks slot v -> RIGHT. (Recency FAILS here.)
  - CUE_ABSENT: NO flag anywhere; VALUE (target) at slot K-1 (== most-recent). Content query-key match is flat
               noise (~1/sqrt(N)) so a pure-content gate spreads/mis-selects -> WRONG. A recency gate picks the
               most-recent slot -> RIGHT. (Content FAILS here.) The FLAG-present instances additionally carry a
               NOISY cue (cos(noisy_flag, cb[FLAG]) ~= q, v7-style) so the content half must INFER, not match.

ARMS (PAIRED -- all evaluated on the SAME held-out instances, from the SAME noisy per-slot codes, per (seed,K,q);
  arms differ ONLY by the admission gate):
  RAW               -- uniform gate (equal-weight superposition of all K slot codes). Content+recency-blind;
                       capped ~1/(present value candidates).
  RECENCY_ONLY      -- v5-style LEARNED fixed per-index gate g_rec (per-slot next-token predictiveness -> softmax);
                       on this corpus it concentrates on the most-recent slot (target for aligned+cue_absent).
                       Content-blind. FAILS on CONFLICT (picks the recent distractor).
  CONTENT_ONLY      -- v7-style per-instance query-key gate on the (noisy) codes: softmax(cos(code_{j-1},FLAG)/TAU).
                       Recency-blind. FAILS on CUE_ABSENT (flat noise -> mis-selects).
  COMBINED          -- ARBITRATES: softmax(content_rel/GATE_TAU + recency_bias). recency_bias = a fixed top-down
                       prior scaled to a gap of RECENCY_GAP_TARGET logits (BETA per (seed,K) hits the target gap).
                       THE ARM UNDER TEST.
  COMBINED_SCRAMBLED-- firing control: the SAME combined formula, but the content_rel vector is DERANGED (fixed
                       per-seed permutation) so a sharp cue lands on a WRONG slot. It overrides recency on
                       cue-PRESENT instances -> breaks aligned+conflict; recency still rescues cue_absent. Isolates
                       that the content ORDERING is load-bearing (not just any peaked admission).

KEY DISCRIMINATORS (headline K, headline realistic cue_q):
  - on CONFLICT   : COMBINED must beat RECENCY_ONLY (content wins when a reliable cue exists).
  - on CUE_ABSENT : COMBINED must beat CONTENT_ONLY (falls back to recency when the cue is absent/noisy).
  - on MIXED      : COMBINED >= max(RECENCY_ONLY, CONTENT_ONLY) + margin (picks up BOTH failure sub-regimes).
  - scramble fires: COMBINED - COMBINED_SCRAMBLED >= margin (the content ordering is load-bearing).

ARBITRATION BOUNDARY (analytic, biased-competition): content overrides recency on a conflict iff the cue logit
  q/GATE_TAU exceeds the recency top-down bias RECENCY_GAP_TARGET, i.e. q > GATE_TAU*RECENCY_GAP_TARGET. With
  GATE_TAU=0.05, RECENCY_GAP_TARGET=3.0 => boundary q*=0.15. Headline q=0.25 (> q*) => content wins conflicts;
  the low-q tail (0.12, 0.06 < q*) walks BELOW the boundary => COMBINED falls back to recency even on conflicts
  (loses the conflict advantage but NEVER does worse than max(single) -- the invariant). This is the envelope.

METRIC: top-1 recall of the correct VALUE token at the QUERY (argmax over VOCAB). chance = 1/|V_SUB| = 0.0625.
  Per-INSTANCE-TYPE breakdown (aligned/conflict/cue_absent) is reported per arm -- the arbitration IS the
  per-type pattern. Headline K=6, headline realistic q=0.25.

TELEMETRY-SENSITIVITY (self-test, guards against an analytically-pinned metric): the metric is genuine per-
  instance readout recall (pred = ctx @ W^T -> argmax cos vs codebook), NOT a closed form over the config.
  Self-test PROVES it moves with which-slot-is-relevant: (T1) RELOCATE the flag to a different slot on conflict
  instances -> the COMBINED-recovered token FOLLOWS the new slot (top1-vs-new-slot high, top1-vs-old-slot low);
  (T2) RELABEL targets to random tokens -> COMBINED top1 collapses toward chance. An analytically-pinned metric
  would pass both regardless; a substrate-read metric moves.

COMPUTE ARCHITECTURE: batched-GPU. Per (seed,K,q): one train pass + one eval pass over BATCH windows; the noisy
  per-slot code tensor (B,K,N) is built ONCE per batch and all FIVE arms derived from it (shared codes => arms
  differ only by gate). Readout = PARAMETER-FREE gate-weighted superposition + codebook cleanup (no learned W, no
  roll-bind, no train pass) so the readout cannot absorb the corpus positional prior; arbitration is isolated in
  the gate. No sequential dependency. Storage: no_storage / no_composition (single-hop, gate-select + cleanup).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 5 per-(K,q) top1 curves; they diverge).
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic).
# - except SystemExit: raise BEFORE except Exception (no BaseException / bare except).
# - crlb_n/a: top-1 recall on a parameter-free gate-select + cleanup readout has no closed-form CRLB; discriminator is
#   the arm-vs-arm recall GAP; content+recency-blind floor is the combinatorial candidate cap (THEORETICAL); the
#   cue-detectability floor is the codebook noise floor 1/sqrt(N) (THEORETICAL).
# - baseline_in_band: RAW in (chance=0.0625, 0.50) at all q; each single gate < COMBINED on its FAILURE sub-regime
#   (else the corpus does not create the arbitration pressure -> INCONCLUSIVE).
# - discriminator survives scale: cue_snr=q*sqrt(N) is N-invariant; smoke (N=1024, floor 0.031) is the HARDER
#   cue-inference test and witnesses arbitration at the same cue_snr; smoke runs the FULL CUE_Q_GRID x K_GRID.
# - HARD_PASS strictly above floor: COMBINED beats BOTH singles by >= 0.10 on mixed AND each on its failure
#   sub-regime by >= 0.20 AND scramble by >= 0.20 (all strictly above the +/-0.03 no-arbitration band).
# - HP_SCOPE: HARD_PASS gates apply ONLY to COMBINED. RAW/RECENCY_ONLY/CONTENT_ONLY are single-signal references
#   (each capped on its failure sub-regime); COMBINED_SCRAMBLED is the firing control (must NOT pass).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID)*len(CUE_Q_GRID); verdict counts len(per_unit).
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED.
# - calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05 (v7), RECENCY_GAP_TARGET=3.0 top-down bias
#   (fixed a priori, in logit units; NOT tuned per-q or per-instance). BETA per (seed,K) only NORMALIZES the
#   learned recency gate to that fixed gap. The arbitration boundary q* = GATE_TAU*RECENCY_GAP_TARGET is analytic;
#   the discriminator-fires self-test (arbitration on BOTH sub-regimes at the fixed knobs) is the health gate.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math, platform, traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
try:
    from experiments._cell_heartbeat import emit_heartbeat
except Exception:
    def emit_heartbeat(*a, **k):
        pass

ANCHOR_NAME = "substrate_gen_lm_combinedgate_recency_content_v8_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--device", default=None, help="cpu|cuda; default cuda for FULL, honors --device for smoke")
_ARGS, _ = _ap.parse_known_args()
RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if _ARGS.device is not None:
    _DEV_REQ = _ARGS.device.lower()
elif RUN_MODE == "smoke":
    _DEV_REQ = "cuda" if torch.cuda.is_available() else "cpu"
else:
    _DEV_REQ = "cuda"
if _DEV_REQ == "cuda" and not torch.cuda.is_available():
    if RUN_MODE == "full":
        print("[FATAL] FULL run requires CUDA; none available.", flush=True); sys.exit(1)
    _DEV_REQ = "cpu"
DEVICE = torch.device(_DEV_REQ)
if DEVICE.type == "cuda":
    print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
else:
    print(f"[CPU] torch {torch.__version__} device=cpu (smoke)", flush=True)

VOCAB = 70
FLAG_ID = 69                       # reserved FLAG token id (NOT in V_SUB)
V_SUB = list(range(16))            # VALUE sub-vocabulary (16 tokens); chance = 1/16 = 0.0625
BATCH = 256
GATE_TAU = 0.05                    # content-gate softmax temperature (fixed, Q-AGNOSTIC: gate must infer)
RECENCY_TAU = 0.2                  # recency-gate softmax temperature (learned per-index predictiveness -> g_rec)
RECENCY_GAP_TARGET = 3.0           # COMBINED top-down recency bias in LOGIT units (fixed a priori). Arbitration
                                   # boundary q* = GATE_TAU*RECENCY_GAP_TARGET = 0.15 (content wins conflict iff q>q*).
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]   # decode softmax temperature grid (bpc readout)
HEADLINE_K = 6
HEADLINE_Q = 0.25                  # realistic reliable cue (cue_snr=8.0 @N=1024 smoke, 22.6 @N=8192; > q*=0.15)
# cue-quality sweep for the FLAG-present (aligned/conflict) instances. 1.0=handed; walks the arbitration boundary
# q*=0.15: q in {1.0,0.5,0.25} above (content wins conflict); q in {0.12,0.06} below (fall back to recency).
CUE_Q_GRID = [1.0, 0.5, 0.25, 0.12, 0.06]
TYPE_NAMES = ["aligned", "conflict", "cue_absent"]
TYPE_FRACS = [1.0 / 3, 1.0 / 3, 1.0 / 3]
ARMS = ["RAW", "RECENCY_ONLY", "CONTENT_ONLY", "COMBINED", "COMBINED_SCRAMBLED"]
ARM_UNDER_TEST = "COMBINED"
CONTROL_ARM = "COMBINED_SCRAMBLED"
SINGLE_GATES = ["RECENCY_ONLY", "CONTENT_ONLY"]
LN2 = math.log(2.0)

# HARD_PASS margins (strictly above the +/-0.03 no-arbitration band -> META_RULE_L strict-above-floor)
MARGIN_MIXED = 0.10                # COMBINED must beat EACH single gate on the mixed corpus by this
MARGIN_SUBREGIME = 0.20            # COMBINED must beat the failing single gate on its failure sub-regime by this
MARGIN_SCRAMBLE = 0.20            # COMBINED - COMBINED_SCRAMBLED on the mixed corpus
NO_ARB_BAND = 0.03                 # COMBINED <= max(single)+this => HARD_FAIL (no real arbitration)

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [7]
    K_GRID = [6, 10]; M_TRAIN = 3000; M_EVAL = 900; M_GATE = 1000
else:
    N_DIM = N; SEEDS = [7, 17, 23]
    K_GRID = [6, 10]; M_TRAIN = 8000; M_EVAL = 2400; M_GATE = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID) * len(CUE_Q_GRID)   # cardinality_ok (META_RULE_H)
assert HEADLINE_K in K_GRID, "HEADLINE_K must be in K_GRID"
assert HEADLINE_Q in CUE_Q_GRID, "HEADLINE_Q must be in CUE_Q_GRID"
assert len(V_SUB) >= max(K_GRID), "V_SUB must supply K distinct value tokens at max K (cue_absent uses all K slots)"
assert abs(CUE_Q_GRID[0] - 1.0) < 1e-9, "CUE_Q_GRID must start at 1.0 (handed reference)"


# ---------------------------------------------------------------------------
# error-checking scaffolding (start-marker / crash-diag / heartbeat)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "device": DEVICE.type, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp"); final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp"); final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f: json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# codebook + corpus (aligned / conflict / cue_absent instances)
# ---------------------------------------------------------------------------
def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def gen_instances(M, K, gen_np):
    """Generate M instances of the three arbitration types. Returns
      (win (M,K) int64, tgt (M,) int64, itype (M,) int64 in {0,1,2}, vslot (M,) int64).
    ALIGNED  (0): FLAG at K-2, VALUE(target) at K-1 (== most-recent slot). recency==content.
    CONFLICT (1): FLAG at v-1, VALUE(target) at v in {1..K-2}; slot K-1 = a DISTRACTOR. content correct, recency wrong.
    CUE_ABSENT(2): NO flag; VALUE(target) at K-1 (== most-recent slot). recency correct, content flat-noise/wrong.
    The K-1 (or K for cue_absent) non-target slots hold DISTINCT V_SUB distractors (target token also distinct).
    (Token ids only; the FLAG code is corrupted to cos~=q later at encode time -- corpus is cue-quality-INDEPENDENT.)"""
    win = np.zeros((M, K), dtype=np.int64)
    tgt = np.zeros(M, dtype=np.int64)
    itype = np.zeros(M, dtype=np.int64)
    vslot = np.zeros(M, dtype=np.int64)
    vsub = np.array(V_SUB, dtype=np.int64)
    types = gen_np.choice(3, size=M, p=TYPE_FRACS)
    for i in range(M):
        t = int(types[i]); itype[i] = t
        if t == 2:                                           # CUE_ABSENT: no flag, target at most-recent slot
            v = K - 1
            toks = gen_np.choice(vsub, size=K, replace=False)   # K distinct values, all slots
            for s in range(K):
                win[i, s] = int(toks[s])
        else:
            if t == 0:                                       # ALIGNED: target at most-recent slot K-1
                v = K - 1
            else:                                            # CONFLICT: target NOT at most-recent slot
                v = int(gen_np.integers(1, K - 1))           # {1,...,K-2}
            win[i, v - 1] = FLAG_ID                           # FLAG immediately before the VALUE
            nonflag = [s for s in range(K) if s != v - 1]     # K-1 slots (includes slot v and slot K-1)
            toks = gen_np.choice(vsub, size=len(nonflag), replace=False)   # distinct V_SUB distractors
            for s, tok in zip(nonflag, toks):
                win[i, s] = int(tok)
        tgt[i] = int(win[i, v])
        vslot[i] = v
    return win, tgt, itype, vslot


# ---------------------------------------------------------------------------
# NOISY-CUE injection (v7): corrupt the flag slot to cos ~= cue_q. cue_absent rows have no flag -> untouched.
# ---------------------------------------------------------------------------
def _noise_seed(seed, K, cue_q, split):
    return int((seed * 1000003 + K * 10007 + int(round(cue_q * 10000)) * 13 + (1 if split == "tr" else 2)) % (2 ** 31))


def build_slot_codes(cb, win, cue_q, flag_code, gen):
    """Per-slot code tensor (B,K,N). Non-flag slots = cb[token]. Flag slots (win==FLAG_ID) replaced by a per-instance
    NOISY flag normalize(cue_q*flag_code + sqrt(1-cue_q^2)*random_unit) so cos(noisy,flag)~=cue_q. cue_q>=0.999 =>
    exact flag. cue_absent rows contain no FLAG_ID -> flag_mask empty for them (content stays flat noise). SAME codes
    reused across all five arms per (K,q) -> arms differ only by gate. 'gen' re-seeded per (seed,K,q,split)."""
    codes = cb[win].clone()                                  # (B,K,N)
    if cue_q < 0.999:
        flag_mask = (win == FLAG_ID)                         # (B,K)
        nf = int(flag_mask.sum())
        if nf > 0:
            n = codes.shape[2]
            noise = (torch.randint(0, 2, (nf, n), generator=gen, device=DEVICE).float() * 2 - 1)
            noise = noise / (noise.norm(dim=1, keepdim=True) + 1e-8)
            alpha = math.sqrt(max(0.0, 1.0 - cue_q * cue_q))
            noisy = cue_q * flag_code.unsqueeze(0) + alpha * noise
            noisy = noisy / (noisy.norm(dim=1, keepdim=True) + 1e-8)
            codes[flag_mask] = noisy
    return codes


# ---------------------------------------------------------------------------
# readout: gate-weighted superposition of per-slot CODES + codebook cleanup (PARAMETER-FREE; arms differ ONLY by
# the admission gate). NO learned Hebbian W and NO roll-bind -> the readout CANNOT absorb the positional (recency)
# prior of the corpus, so the arbitration is isolated ENTIRELY in the gate (a learned Hebbian readout leaks the
# slot-K-1 prior into every arm and confounds the per-type separation; a parameter-free gate-select + cleanup is
# the faithful attention-routing readout -- attention selects the slot, output = the selected slot's content).
# ---------------------------------------------------------------------------
def gate_readout(slot_codes, gate):
    """Gate-weighted superposition of the K raw slot codes -> (B,N) normalized. gate: (K,) fixed per-index (recency)
    OR (B,K) per-instance. A peaked gate concentrates the superposition on ONE slot's code (cleanup recovers that
    slot's token); a uniform gate (RAW) sums K near-orthogonal codes -> cleanup is ambiguous (capped)."""
    B, K, n = slot_codes.shape
    if gate.dim() == 1:
        w = gate.view(1, K, 1)
    else:
        w = gate.unsqueeze(2)
    b = (w * slot_codes).sum(dim=1)                          # (B,N)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def content_relevance(slot_codes, flag_code):
    """r_j = cos(slot_code_{j-1}, flag_code) for j>=1 (unit-norm codes). Slot 0 has no in-window predecessor (v>=1);
    set r[:,0] to the per-row min so it is never selected. Returns raw relevance (B,K) -- NOT softmaxed."""
    B, K, n = slot_codes.shape
    r = torch.empty(B, K, device=DEVICE)
    r[:, 0] = -1e9
    for j in range(1, K):
        r[:, j] = (slot_codes[:, j - 1] * flag_code).sum(dim=1)
    r[:, 0] = r[:, 1:].min(dim=1).values                     # neutral, never the argmax
    return r


def content_gate_from_rel(r, tau):
    """CONTENT_ONLY per-instance gate: softmax(r_masked / tau) with slot 0 masked to -inf (recency-blind)."""
    B, K = r.shape
    rm = r.clone()
    rm[:, 0] = -1e9
    return torch.softmax(rm / tau, dim=1)


def combined_gate_from_rel(r, recency_bias, tau, scramble_perm=None):
    """COMBINED arbitration gate: softmax(content_rel/tau + recency_bias). recency_bias: (K,) fixed top-down prior
    (top slot=0, others negative, gap=RECENCY_GAP_TARGET). scramble_perm: if given, deranges the CONTENT relevance
    only (recency intact) so a sharp cue lands on a WRONG slot (firing control). Returns g (B,K)."""
    B, K = r.shape
    cr = r if scramble_perm is None else r[:, scramble_perm]
    logit = cr / tau + recency_bias.unsqueeze(0)
    return torch.softmax(logit, dim=1)


def _derangement(K, seed_val):
    """Fixed per-seed derangement of {0..K-1} (no fixed point). Used to scramble the content relevance."""
    g = torch.Generator(device="cpu").manual_seed(int(seed_val))
    ar = torch.arange(K)
    for _ in range(200):
        perm = torch.randperm(K, generator=g)
        if int((perm == ar).sum()) == 0:
            return perm.to(DEVICE)
    return torch.arange(K - 1, -1, -1, device=DEVICE)


def learn_recency_gate(win_tr, tgt_tr, K, tau):
    """v5-style LEARNED fixed per-index gate (CONTENT-BLIND): per-position empirical target-hit rate
    r_j = mean_i 1[token at slot j == target], then g = softmax(r/tau). Uses ONLY position statistics (no content,
    no per-instance signal). On this corpus slot K-1 is the target for aligned+cue_absent (~2/3 of instances) so r
    (and g) concentrate on the most-recent slot. Returns (g (K,), relevance (K,))."""
    M = min(M_GATE, win_tr.shape[0])
    wt = win_tr[:M]; tt = tgt_tr[:M].unsqueeze(1)            # (M,1)
    r = (wt == tt).float().mean(dim=0)                       # (K,) per-position hit rate
    return torch.softmax(r / tau, dim=0), r


def recency_bias_from_gate(g_rec):
    """Fixed top-down recency prior for the COMBINED gate (in logit units): log g_rec normalized so the top slot=0
    and the top-to-runnerup gap = RECENCY_GAP_TARGET. This makes the recency bias a fixed-strength top-down signal
    (biased-competition) INDEPENDENT of the learned gate's raw sharpness. Returns (K,) + the applied beta."""
    rlog = torch.log(g_rec + 1e-6)
    rlog = rlog - rlog.max()                                 # top slot = 0, others < 0
    srt = torch.sort(rlog, descending=True).values
    gap_raw = float(srt[0] - srt[1]) if rlog.numel() >= 2 else 1.0
    beta = RECENCY_GAP_TARGET / max(gap_raw, 1e-6)
    return rlog * beta, beta


# ---------------------------------------------------------------------------
# per-(K,q) eval: build noisy codes ONCE per batch, derive all five arms (parameter-free; no train pass)
# ---------------------------------------------------------------------------
def _arm_contexts(slot_codes, flag_code, g_rec, recency_bias, perm):
    r = content_relevance(slot_codes, flag_code)
    g_con = content_gate_from_rel(r, GATE_TAU)
    g_comb = combined_gate_from_rel(r, recency_bias, GATE_TAU, None)
    g_scr = combined_gate_from_rel(r, recency_bias, GATE_TAU, perm)
    B, K, n = slot_codes.shape
    g_uni = torch.full((K,), 1.0 / K, device=DEVICE)
    ctxs = {"RAW": gate_readout(slot_codes, g_uni),
            "RECENCY_ONLY": gate_readout(slot_codes, g_rec),
            "CONTENT_ONLY": gate_readout(slot_codes, g_con),
            "COMBINED": gate_readout(slot_codes, g_comb),
            "COMBINED_SCRAMBLED": gate_readout(slot_codes, g_scr)}
    return ctxs, g_comb, r


def _top1_by_type(argmax, tgt, itype):
    """top1 overall + per instance-type. argmax,tgt,itype: (M,) long tensors."""
    out = {"top1": float((argmax == tgt).float().mean())}
    for t, name in enumerate(TYPE_NAMES):
        mask = (itype == t)
        nt = int(mask.sum())
        out["top1_" + name] = float((argmax[mask] == tgt[mask]).float().mean()) if nt > 0 else float("nan")
        out["n_" + name] = nt
    return out


def _bpc_from_cos(cos_all, tgt):
    M = cos_all.shape[0]
    best_nats = float("inf")
    for t in TEMP_GRID:
        z = cos_all / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        P = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = P[torch.arange(M, device=DEVICE), tgt].clamp_min(1e-12)
        best_nats = min(best_nats, float((-torch.log(pt)).mean()))
    return best_nats


def eval_all_arms(cb, win_ev, tgt_ev, itype_ev, cue_q, flag_code, g_rec, recency_bias, perm, seed, K):
    """Parameter-free readout: per arm, gate-weighted superposition -> cleanup (cos vs codebook) -> argmax over the
    VALUE sub-vocabulary (the query asks for a VALUE token; FLAG is never a legal answer)."""
    M = win_ev.shape[0]
    vsub_t = torch.tensor(V_SUB, device=DEVICE)
    argmax_all = {a: torch.empty(M, dtype=torch.long, device=DEVICE) for a in ARMS}
    cos_store = {a: torch.empty(M, VOCAB, device=DEVICE) for a in ARMS}
    gen = torch.Generator(device=DEVICE).manual_seed(_noise_seed(seed, K, cue_q, "ev"))
    for s in range(0, M, BATCH):
        wb = win_ev[s:s + BATCH]; bs = wb.shape[0]
        codes = build_slot_codes(cb, wb, cue_q, flag_code, gen)
        ctxs, _, _ = _arm_contexts(codes, flag_code, g_rec, recency_bias, perm)
        for a in ARMS:
            cos = ctxs[a] @ cb.t()                           # (bs,VOCAB) cleanup
            cos_store[a][s:s + bs] = cos
            cos_v = cos[:, vsub_t]                            # restrict argmax to VALUE sub-vocab
            argmax_all[a][s:s + bs] = vsub_t[cos_v.argmax(dim=1)]
    out = {}
    for a in ARMS:
        m = _top1_by_type(argmax_all[a], tgt_ev, itype_ev)
        m["bpc_bits"] = _bpc_from_cos(cos_store[a], tgt_ev) / LN2
        out[a] = m
    return out


# ---------------------------------------------------------------------------
# self-test (PROT-022): runs on import; blocks dispatch if any assert fails
# ---------------------------------------------------------------------------
def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(VOCAB, 256, gen)
    flag_code = cb[FLAG_ID]
    # gate_readout: a one-hot gate selects that slot's code (cleanup recovers its token); uniform gate = mean.
    w1 = torch.tensor([[3, 5, 9]], device=DEVICE)
    c1 = build_slot_codes(cb, w1, 1.0, flag_code, gen)       # (1,3,N)
    for j in range(3):
        onehot = torch.zeros(3, device=DEVICE); onehot[j] = 1.0
        rd = gate_readout(c1, onehot)                        # (1,N)
        tok = int((rd @ cb.t()).argmax(dim=1))
        assert tok == int(w1[0, j]), f"gate_readout one-hot slot {j} did not select token {int(w1[0,j])} (got {tok})"
    # bpc/ppl formula
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "bpc/ppl formula"
    # NOISE CALIBRATION: cos(noisy_flag, cb[FLAG]) ~= cue_q (flag-present instances only)
    Kt = 6; gnp = np.random.default_rng(3)
    win_np, tgt_np, itype_np, vslot_np = gen_instances(1200, Kt, gnp)
    win_t = torch.tensor(win_np, device=DEVICE)
    for q in [1.0, 0.5, 0.12]:
        gg = torch.Generator(device=DEVICE).manual_seed(123)
        codes = build_slot_codes(cb, win_t, q, flag_code, gg)
        fmask = (win_t == FLAG_ID)
        cosq = float((codes[fmask] * flag_code).sum(dim=1).mean())
        if q >= 0.999:
            assert cosq > 0.999, f"q=1.0 must give exact flag; got cos={cosq:.4f}"
        else:
            assert abs(cosq - q) < 0.08, f"noise calibration off at q={q}: mean cos={cosq:.4f}"
    # corpus sanity: three types present at ~1/3; cue_absent has NO flag; aligned/conflict slots correct
    for t, name in enumerate(TYPE_NAMES):
        frac = float((itype_np == t).mean())
        assert abs(frac - 1.0 / 3) < 0.06, f"type {name} frac off: {frac:.3f}"
    ca = (itype_np == 2)
    assert not (win_np[ca] == FLAG_ID).any(), "cue_absent instances must contain NO flag"
    al = (itype_np == 0); co = (itype_np == 1)
    assert (vslot_np[al] == Kt - 1).all(), "aligned target must be at most-recent slot"
    assert (vslot_np[ca] == Kt - 1).all(), "cue_absent target must be at most-recent slot"
    assert (vslot_np[co] < Kt - 1).all() and (vslot_np[co] >= 1).all(), "conflict target must be non-recent, >=1"
    # recency gate concentrates on the most-recent slot; scramble derangement moves off
    cbs = build_cb(VOCAB, 512, torch.Generator(device=DEVICE).manual_seed(5)); fcs = cbs[FLAG_ID]
    gnp2 = np.random.default_rng(7)
    Kd = 6
    wtr, ttr, ittr, vtr = gen_instances(2400, Kd, gnp2)
    wev, tev, itev, vev = gen_instances(900, Kd, gnp2)
    wtr_t = torch.tensor(wtr, device=DEVICE); ttr_t = torch.tensor(ttr, device=DEVICE)
    wev_t = torch.tensor(wev, device=DEVICE); tev_t = torch.tensor(tev, device=DEVICE)
    itev_t = torch.tensor(itev, device=DEVICE)
    g_rec, r_rec = learn_recency_gate(wtr_t, ttr_t, Kd, RECENCY_TAU)
    assert int(g_rec.argmax()) == Kd - 1, f"recency gate did not concentrate on most-recent slot (argmax={int(g_rec.argmax())})"
    recency_bias, beta = recency_bias_from_gate(g_rec)
    srt = torch.sort(recency_bias, descending=True).values
    assert abs(float(srt[0] - srt[1]) - RECENCY_GAP_TARGET) < 0.3, \
        f"recency_bias gap not normalized to {RECENCY_GAP_TARGET} (got {float(srt[0]-srt[1]):.3f})"
    permd = _derangement(Kd, 13)
    # DISCRIMINATOR-FIRES: at the headline reliable cue, per-type arbitration pattern must hold at small scale.
    q = HEADLINE_Q
    m = eval_all_arms(cbs, wev_t, tev_t, itev_t, q, fcs, g_rec, recency_bias, permd, 5, Kd)
    comb = m["COMBINED"]; rec = m["RECENCY_ONLY"]; con = m["CONTENT_ONLY"]; raw = m["RAW"]; scr = m["COMBINED_SCRAMBLED"]
    # single gates FAIL on their failure sub-regime; COMBINED rescues both
    assert rec["top1_conflict"] < 0.30, f"RECENCY_ONLY should FAIL on conflict; got {rec['top1_conflict']:.3f}"
    assert con["top1_cue_absent"] < 0.40, f"CONTENT_ONLY should FAIL on cue_absent; got {con['top1_cue_absent']:.3f}"
    assert comb["top1_conflict"] - rec["top1_conflict"] >= MARGIN_SUBREGIME, \
        f"COMBINED must beat RECENCY on conflict: {comb['top1_conflict']:.3f} vs {rec['top1_conflict']:.3f}"
    assert comb["top1_cue_absent"] - con["top1_cue_absent"] >= MARGIN_SUBREGIME, \
        f"COMBINED must beat CONTENT on cue_absent: {comb['top1_cue_absent']:.3f} vs {con['top1_cue_absent']:.3f}"
    assert comb["top1"] - rec["top1"] >= MARGIN_MIXED and comb["top1"] - con["top1"] >= MARGIN_MIXED, \
        f"COMBINED must beat BOTH singles on mixed: comb={comb['top1']:.3f} rec={rec['top1']:.3f} con={con['top1']:.3f}"
    assert comb["top1"] - scr["top1"] >= MARGIN_SCRAMBLE, \
        f"scramble must fire: comb={comb['top1']:.3f} scr={scr['top1']:.3f}"
    assert raw["top1"] < 0.50, f"RAW must be capped (content+recency blind); got {raw['top1']:.3f}"
    # TELEMETRY-SENSITIVITY T2: relabel targets to random tokens -> COMBINED top1 collapses toward chance
    perm_lbl = torch.randperm(tev_t.shape[0], generator=torch.Generator(device="cpu").manual_seed(1)).to(DEVICE)
    tev_shuf = tev_t[perm_lbl]
    m_shuf = eval_all_arms(cbs, wev_t, tev_shuf, itev_t, q, fcs, g_rec, recency_bias, permd, 5, Kd)
    assert m_shuf["COMBINED"]["top1"] < comb["top1"] - 0.30, \
        f"TELEMETRY T2 FAIL: relabeling targets did not move COMBINED top1 (real={comb['top1']:.3f} shuf={m_shuf['COMBINED']['top1']:.3f}); metric may be analytically pinned"
    # TELEMETRY-SENSITIVITY T1: RELOCATE the flag on conflict instances -> COMBINED-recovered token FOLLOWS the new
    # slot. Build a conflict-only eval set, move flag from v-1 to a different slot v2-1, retarget to token@v2.
    co_mask = (itev == 1)
    wc = wev[co_mask].copy(); vc = vev[co_mask].copy()
    Mc = wc.shape[0]
    v_new = np.zeros(Mc, dtype=np.int64)
    for i in range(Mc):
        old_v = int(vc[i])
        # move flag to a NEW predecessor slot so new v differs from old v and from most-recent
        choices = [s for s in range(1, Kd - 1) if s != old_v]
        v2 = int(gnp2.choice(choices)) if choices else old_v
        wc[i, old_v - 1] = wc[i, old_v]                       # overwrite old flag with a value token (clear old cue)
        # ensure the value at v2 differs from token at old_v; if equal, leave (rare) -- distinctness by construction
        wc[i, v2 - 1] = FLAG_ID                               # plant flag before new slot v2
        v_new[i] = v2
    wc_t = torch.tensor(wc, device=DEVICE)
    tgt_new = torch.tensor([int(wc[i, v_new[i]]) for i in range(Mc)], dtype=torch.long, device=DEVICE)
    tgt_old = torch.tensor([int(wev[co_mask][i, vc[i]]) for i in range(Mc)], dtype=torch.long, device=DEVICE)
    itc = torch.ones(Mc, dtype=torch.long, device=DEVICE)    # all conflict
    m_new = eval_all_arms(cbs, wc_t, tgt_new, itc, q, fcs, g_rec, recency_bias, permd, 5, Kd)
    m_old = eval_all_arms(cbs, wc_t, tgt_old, itc, q, fcs, g_rec, recency_bias, permd, 5, Kd)
    assert m_new["COMBINED"]["top1"] - m_old["COMBINED"]["top1"] >= 0.30, \
        f"TELEMETRY T1 FAIL: relocating the flag did not move the COMBINED-recovered token (top1@new={m_new['COMBINED']['top1']:.3f} top1@old={m_old['COMBINED']['top1']:.3f}); metric may be analytically pinned"
    assert N == 8192
    print(f"[selftest] PASS: gate_readout_onehot bpc noise_calib types(1/3) recency_argmax={int(g_rec.argmax())} "
          f"beta={beta:.3f} | arb@K{Kd}q{q}: RAW={raw['top1']:.2f} REC[all={rec['top1']:.2f},conf={rec['top1_conflict']:.2f}] "
          f"CON[all={con['top1']:.2f},abs={con['top1_cue_absent']:.2f}] COMB[all={comb['top1']:.2f},conf={comb['top1_conflict']:.2f},"
          f"abs={comb['top1_cue_absent']:.2f}] SCR={scr['top1']:.2f} | telemetry T2(shuf={m_shuf['COMBINED']['top1']:.2f}) "
          f"T1(new={m_new['COMBINED']['top1']:.2f}>old={m_old['COMBINED']['top1']:.2f}) N8192", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, n_dim: int, out_dir) -> Dict:
    gen_np = np.random.default_rng(seed + 99)
    cb = build_cb(VOCAB, n_dim, torch.Generator(device=DEVICE).manual_seed(seed))
    flag_code = cb[FLAG_ID]
    noise_floor = 1.0 / math.sqrt(n_dim)
    per_unit = []; gate_log = {}; unit_i = 0; t_seed = time.time()
    total_units = len(ARMS) * len(K_GRID) * len(CUE_Q_GRID)
    for K in K_GRID:
        win_tr_np, tgt_tr_np, it_tr_np, _ = gen_instances(M_TRAIN, K, gen_np)
        win_ev_np, tgt_ev_np, it_ev_np, _ = gen_instances(M_EVAL, K, gen_np)
        win_tr = torch.tensor(win_tr_np, device=DEVICE); tgt_tr = torch.tensor(tgt_tr_np, device=DEVICE)
        win_ev = torch.tensor(win_ev_np, device=DEVICE); tgt_ev = torch.tensor(tgt_ev_np, device=DEVICE)
        itype_ev = torch.tensor(it_ev_np, device=DEVICE)
        g_rec, r_rec = learn_recency_gate(win_tr, tgt_tr, K, RECENCY_TAU)
        recency_bias, beta = recency_bias_from_gate(g_rec)
        perm = _derangement(K, seed * 17 + K)
        klog = {"recency_gate": [round(float(x), 4) for x in g_rec.tolist()],
                "recency_relevance": [round(float(x), 4) for x in r_rec.tolist()],
                "recency_bias": [round(float(x), 4) for x in recency_bias.tolist()],
                "beta": round(float(beta), 4), "scramble_perm": [int(x) for x in perm.tolist()],
                "chance": round(1.0 / len(V_SUB), 4), "content_blind_cap": round(1.0 / (K - 1), 4),
                "noise_floor": round(noise_floor, 5), "arb_boundary_q": round(GATE_TAU * RECENCY_GAP_TARGET, 4),
                "per_q": {}}
        print(f"    [K={K}] recency_g={[round(float(x),3) for x in g_rec.tolist()]} beta={beta:.3f} "
              f"arb_q*={GATE_TAU*RECENCY_GAP_TARGET:.3f} noise_floor={noise_floor:.4f} perm={perm.tolist()}", flush=True)
        for cue_q in CUE_Q_GRID:
            cue_snr = cue_q * math.sqrt(n_dim)
            arm_metrics = eval_all_arms(cb, win_ev, tgt_ev, itype_ev, cue_q, flag_code, g_rec,
                                        recency_bias, perm, seed, K)
            for arm in ARMS:
                m = dict(arm_metrics[arm])
                m.update({"seed": seed, "arm": arm, "K": K, "cue_q": float(cue_q),
                          "cue_snr": round(cue_snr, 3), "N": n_dim})
                per_unit.append(m); unit_i += 1
                emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed, total_units=total_units,
                               extra={"seed": seed, "arm": arm, "K": K, "cue_q": float(cue_q),
                                      "top1": round(m["top1"], 3)})
            klog["per_q"]["%.3f" % cue_q] = {"cue_snr": round(cue_snr, 3)}
            cm = arm_metrics["COMBINED"]; rm = arm_metrics["RECENCY_ONLY"]; nm = arm_metrics["CONTENT_ONLY"]
            print(f"      [q={cue_q:.3f} snr={cue_snr:6.2f}] "
                  f"RAW={arm_metrics['RAW']['top1']:.3f} "
                  f"REC[all={rm['top1']:.3f} conf={rm['top1_conflict']:.3f}] "
                  f"CON[all={nm['top1']:.3f} abs={nm['top1_cue_absent']:.3f}] "
                  f"COMB[all={cm['top1']:.3f} algn={cm['top1_aligned']:.3f} conf={cm['top1_conflict']:.3f} "
                  f"abs={cm['top1_cue_absent']:.3f}] SCR={arm_metrics['COMBINED_SCRAMBLED']['top1']:.3f}", flush=True)
        gate_log["K%d" % K] = klog
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "per_unit": per_unit, "gate_log": gate_log,
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _val(all_results, arm, K, cue_q, field="top1"):
    vals = [u[field] for r in all_results for u in r["per_unit"]
            if u["arm"] == arm and u["K"] == K and abs(u["cue_q"] - cue_q) < 1e-6 and field in u
            and not (isinstance(u[field], float) and math.isnan(u[field]))]
    return float(np.mean(vals)) if vals else float("nan")


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units} units, expected {EXPECTED_N_UNITS}")
    n_dim = all_results[0]["N"]; K = HEADLINE_K; q = HEADLINE_Q
    cap = 1.0 / (K - 1); chance = 1.0 / len(V_SUB)

    def g(arm, field):
        return _val(all_results, arm, K, q, field)

    comb_all = g("COMBINED", "top1"); rec_all = g("RECENCY_ONLY", "top1"); con_all = g("CONTENT_ONLY", "top1")
    raw_all = g("RAW", "top1"); scr_all = g("COMBINED_SCRAMBLED", "top1")
    comb_conf = g("COMBINED", "top1_conflict"); rec_conf = g("RECENCY_ONLY", "top1_conflict")
    comb_abs = g("COMBINED", "top1_cue_absent"); con_abs = g("CONTENT_ONLY", "top1_cue_absent")
    comb_algn = g("COMBINED", "top1_aligned")

    beat_rec = comb_all - rec_all; beat_con = comb_all - con_all
    win_conf = comb_conf - rec_conf; win_abs = comb_abs - con_abs; sep = comb_all - scr_all
    max_single = max(rec_all, con_all)

    # per-q COMBINED-vs-max(single) invariant across the grid (arbitration never does worse than best single)
    inv = {}
    for qq in CUE_Q_GRID:
        cq = _val(all_results, "COMBINED", K, qq); mq = max(_val(all_results, "RECENCY_ONLY", K, qq),
                                                            _val(all_results, "CONTENT_ONLY", K, qq))
        inv[qq] = round(cq - mq, 4)

    summary = (f"@K{K} q={q} (cue_snr={q*math.sqrt(n_dim):.2f}) N={n_dim} cap={cap:.3f} chance={chance:.3f} | "
               f"MIXED: RAW={raw_all:.3f} REC={rec_all:.3f} CON={con_all:.3f} COMB={comb_all:.3f} SCR={scr_all:.3f} | "
               f"COMB-REC={beat_rec:+.3f} COMB-CON={beat_con:+.3f} scramble_sep={sep:+.3f} | "
               f"SUB-REGIME: conflict[COMB={comb_conf:.3f} REC={rec_conf:.3f} win={win_conf:+.3f}] "
               f"cue_absent[COMB={comb_abs:.3f} CON={con_abs:.3f} win={win_abs:+.3f}] aligned[COMB={comb_algn:.3f}] | "
               f"invariant COMB-max(single) per q: {inv}")

    # VALID-ONLY-IF: corpus must actually create BOTH failure modes + RAW capped (not saturation-vacuous)
    if raw_all > 0.50:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_CORPUS_DOES_NOT_DISCRIMINATE: RAW={raw_all:.3f} > 0.50 -- the readout "
                f"solves the task WITHOUT any gate. Re-spec. {summary}")
    if raw_all < chance * 1.3:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_AT_CHANCE: RAW={raw_all:.3f} ~ chance ({chance:.3f}); the "
                f"cleanup readout failed, not a gating result. {summary}")
    if rec_conf >= comb_conf - 0.05 or con_abs >= comb_abs - 0.05:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_NO_ARBITRATION_PRESSURE: a single gate does NOT fail on its intended "
                f"sub-regime (recency on conflict rec_conf={rec_conf:.3f} vs comb_conf={comb_conf:.3f}; content on "
                f"cue_absent con_abs={con_abs:.3f} vs comb_abs={comb_abs:.3f}). The corpus does not force arbitration. "
                f"Re-spec. {summary}")

    # HARD_FAIL: COMBINED does not exceed max(single) on mixed => no real arbitration (honest deflation)
    if comb_all <= max_single + NO_ARB_BAND:
        return ("HARD_FAIL", f"HARD_FAIL_NO_ARBITRATION: COMBINED={comb_all:.3f} does not exceed max(single)="
                f"{max_single:.3f} by more than {NO_ARB_BAND} on the mixed corpus. The combined gate does not "
                f"arbitrate -- it collapses to (or below) the better single signal. Honest deflation. {summary}")

    # HARD_PASS (HP_SCOPE: COMBINED only)
    if (beat_rec >= MARGIN_MIXED and beat_con >= MARGIN_MIXED and win_conf >= MARGIN_SUBREGIME
            and win_abs >= MARGIN_SUBREGIME and sep >= MARGIN_SCRAMBLE and comb_all >= cap + 0.30):
        return ("HARD_PASS", f"HARD_PASS[COMBINED]_ARBITRATION: the combined recency+content gate ARBITRATES -- it "
                f"beats BOTH single-signal gates on the mixed corpus (COMB-REC={beat_rec:+.3f}>={MARGIN_MIXED}, "
                f"COMB-CON={beat_con:+.3f}>={MARGIN_MIXED}) AND beats EACH on the sub-regime where that one fails "
                f"(conflict: content wins, COMB-REC={win_conf:+.3f}>={MARGIN_SUBREGIME}; cue_absent: falls back to "
                f"recency, COMB-CON={win_abs:+.3f}>={MARGIN_SUBREGIME}) AND the content-ordering is load-bearing "
                f"(scramble_sep={sep:+.3f}>={MARGIN_SCRAMBLE}). Graded normalization-arbitration of a recency prior "
                f"and a content-cue bias -- the full attention-routing capability. {summary}")

    # MIDDLE_BAND: beats both on mixed but misses a strict sub-regime / scramble gate
    if beat_rec > 0 and beat_con > 0 and sep > 0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND[COMBINED]_PARTIAL_ARBITRATION: COMBINED beats both single gates on the "
                f"mixed corpus (COMB-REC={beat_rec:+.3f} COMB-CON={beat_con:+.3f}) and scramble fires (sep={sep:+.3f}) "
                f"but misses a strict gate (win_conf={win_conf:+.3f} vs {MARGIN_SUBREGIME}, win_abs={win_abs:+.3f} vs "
                f"{MARGIN_SUBREGIME}, or comb_all={comb_all:.3f} vs cap+0.30={cap+0.30:.3f}). Real but partial "
                f"arbitration; the sub-regime pattern is the finding. {summary}")

    return ("HARD_FAIL", f"HARD_FAIL: COMBINED does not cleanly arbitrate (beat_rec={beat_rec:+.3f} beat_con="
            f"{beat_con:+.3f} sep={sep:+.3f}). {summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} "
          f"K_GRID={K_GRID} headline_K={HEADLINE_K} headline_q={HEADLINE_Q} CUE_Q_GRID={CUE_Q_GRID} arms={ARMS} "
          f"V_SUB={len(V_SUB)} FLAG={FLAG_ID} M_TRAIN={M_TRAIN} M_EVAL={M_EVAL} GATE_TAU={GATE_TAU} "
          f"RECENCY_GAP_TARGET={RECENCY_GAP_TARGET} arb_q*={GATE_TAU*RECENCY_GAP_TARGET} type_fracs={TYPE_FRACS} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS,
                                                                  "K_GRID": K_GRID, "headline_K": HEADLINE_K,
                                                                  "headline_q": HEADLINE_Q, "cue_q_grid": CUE_Q_GRID,
                                                                  "v_sub": len(V_SUB), "gate_tau": GATE_TAU,
                                                                  "recency_gap_target": RECENCY_GAP_TARGET})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): the 5 top1 (K,q)-curves must not be bit-identical
    import hashlib
    digs = {}
    for arm in ARMS:
        pts = {}
        for K in K_GRID:
            for qq in CUE_Q_GRID:
                pts["K%d_q%.3f" % (K, qq)] = round(_val(all_results, arm, K, qq), 6)
        digs[arm] = hashlib.sha256(json.dumps(pts, sort_keys=True).encode()).hexdigest()
    for a in ARMS:
        for b2 in ARMS:
            if a < b2:
                assert digs[a] != digs[b2], f"META_RULE_AF VIOLATION: arms {a} and {b2} bit-identical curves"
    verdict, vmsg = compute_verdict(all_results)
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    if DEVICE.type == "cuda":
        print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
    fields = ["top1", "top1_aligned", "top1_conflict", "top1_cue_absent", "bpc_bits"]
    curves = {arm: {"K%d" % K: {"%.3f" % qq: {f: round(_val(all_results, arm, K, qq, f), 5) for f in fields}
                                for qq in CUE_Q_GRID} for K in K_GRID} for arm in ARMS}
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "headline_K": HEADLINE_K,
               "headline_q": HEADLINE_Q, "k_grid": K_GRID, "cue_q_grid": CUE_Q_GRID, "type_names": TYPE_NAMES,
               "type_fracs": TYPE_FRACS, "v_sub": len(V_SUB), "flag_id": FLAG_ID, "gate_tau": GATE_TAU,
               "recency_gap_target": RECENCY_GAP_TARGET, "arb_boundary_q": GATE_TAU * RECENCY_GAP_TARGET,
               "noise_floor": round(1.0 / math.sqrt(N_DIM), 5), "expected_n_units": EXPECTED_N_UNITS,
               "margins": {"mixed": MARGIN_MIXED, "subregime": MARGIN_SUBREGIME, "scramble": MARGIN_SCRAMBLE,
                           "no_arb_band": NO_ARB_BAND},
               "arm_digests": digs, "per_seed": all_results, "curves": curves}
    write_metrics(out_dir, metrics, all_results)
    print("[metrics] written", flush=True)


OUT_DIR_FOR_CRASH = get_output_dir(ANCHOR_NAME)
try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(OUT_DIR_FOR_CRASH, e)
    raise
