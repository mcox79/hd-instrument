"""
substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu -- NOISY/INFERRED-cue promotion of v6's content-gate.

WHY (VET 2026-07-08): v6 (exp_substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu) executed content-addressed
  admission and hit CONTENT=1.000 -- but on a corpus where the FLAG cue gave an EXACT cos=1.0 query-key delta
  (the predecessor of the true slot IS the pure FLAG codebook vector, so cos(predecessor,FLAG)=1.0 exactly while
  all distractors sit at the ~1/sqrt(N) codebook noise floor). That is a HANDED delta: the gate does not have to
  INFER relevance, only match a perfect signal. v6 tiered MEASURED_MECHANISM ("too easy by construction"; the
  scramble->chance control proved the lift is real SELECTION, but the selection was of a handed cue). VET's
  promotion path (MM -> CG): make the cue NOISY/INFERRED (cos<1, degrading toward the codebook noise floor) so
  the gate must INFER relevance from a graded, noise-corrupted match. If content-selection still beats the
  1/(K-1) content-blind cap at a REALISTIC (near-noise-floor) cue-quality, that promotes MM->CG and is the real
  Stage-4 attention-routing test.

BRAIN-GROUNDING (notes/research_content_gate_brain_grounding_2026-07-08.md): biased-competition (Desimone &
  Duncan 1995; Reynolds & Heeger 2009 normalization) is a GRADED feature-similarity kernel -- attentional
  selection strength scales with the (partial) match between the top-down template and the stimulus, NOT a
  binary exact-match. A noisy/graded cue is therefore the NATURAL brain-aligned test of the same primitive:
  query-key attention (Ramsauer et al. 2020 modern-Hopfield = softmax(beta Q K^T) V) with a degraded query.

WHAT CHANGES vs v6: the FLAG marker deposited at slot v-1 is no longer the pure codebook vector cb[FLAG]. For a
  cue-quality q in CUE_Q_GRID, the flag slot's CODE is corrupted to  noisy = normalize(q*cb[FLAG] +
  sqrt(1-q^2)*random_unit)  so that cos(noisy, cb[FLAG]) ~= q (self-test asserts this). q=1.0 reproduces v6's
  handed delta (top of the sweep); q -> noise_floor(N)=1/sqrt(N) means the flag is indistinguishable from a
  random distractor (genuinely inferred / impossible). The SAME noisy codes are shared across all four arms per
  (K,q) so the arms differ ONLY by the admission gate (v6 discipline preserved). The content gate's KEY at slot
  j is cos(slot_code_{j-1}, cb[FLAG]) -- so at the true slot the key match is ~q, not 1.0: the gate must infer.

SWEEP AXES: cue-quality q (PRIMARY -- the robustness envelope) x window length K (K>=6 per VET: K=4 breaches the
  0.50 discrimination guard). CUE_Q_GRID spans handed (1.0) down to near the codebook noise floor. Because the
  detectability of a cue at cosine q scales as cue_snr = q*sqrt(N) (a mean-shift-of-q against a 1/sqrt(N) noise
  floor over K candidate slots), the BREAK-POINT is N-INVARIANT in cue_snr units. We report the break-point in
  BOTH cue_snr (N-invariant, primary) and absolute q (N-specific). This is also the discriminator-survives-scale
  argument: smoke (N=1024) has a HIGHER noise floor (0.031) than FULL (N=8192, 0.011), so smoke is the HARDER
  test and witnesses the knee at the same cue_snr -- if content-selection passes the realistic cue_snr bar in
  smoke, it passes (more easily) at FULL.

ARMS (paired -- all evaluated on the SAME held-out instances, from the SAME noisy codes, per (seed,K,q)):
  RAW            -- uniform roll-bind bundle of all K slots. Content-blind; analytically ~1/(K-1). Q-INDEPENDENT
                    (the noisy flag is just one more distractor in the bundle) -> a flat-across-q RAW curve is a
                    built-in sanity check that only CONTENT depends on cue-quality.
  RECENCY_GATE   -- v6's fixed per-index gate g_j (learned from per-slot next-token predictiveness, applied
                    identically to every instance). On this corpus target POSITION is uniform so g ~= uniform;
                    content-blind, capped ~1/(K-1), Q-independent. Honest paired recency control.
  CONTENT_GATE   -- per-instance gate g_j = softmax(cos(slot_code_{j-1}, cb[FLAG]) / GATE_TAU). With a NOISY flag
                    the true-slot key match is ~q (not 1.0), so the gate must infer relevance from a graded,
                    noise-corrupted signal. Degrades as q -> noise floor. THE ARM UNDER TEST.
  CONTENT_GATE_SCRAMBLED -- firing control: same query-key relevance spectrum, but the per-slot relevance vector
                    is DERANGED (fixed per-seed permutation) so the peaked admission lands on a WRONG slot. Must
                    NOT recover: isolates genuine content-match from variance-reduction-by-peaking.

METRIC: top-1 recall of the correct VALUE token at the QUERY (chance = 1/|V_SUB| = 0.0625). Headline K=6.

PRE-REGISTERED BANDS (headline K=6; realistic point = grid q whose cue_snr is closest to SNR_TARGET=7):
  VALID-ONLY-IF (corpus discriminates): at q=1.0, RAW<=0.35 AND RECENCY<=0.35 (both near the 1/(K-1) analytic
    cap). If either >0.50 the readout solves it WITHOUT content-selection -> INCONCLUSIVE (saturation-vacuous
    inverse), re-spec. Also content-blind arms must be above chance (readout alive).
  HARD_PASS (CG-promotion) = at the realistic point (cue_snr ~= 7, genuinely inferred): CONTENT-RECENCY >= 0.30
    AND CONTENT >= cap+0.30, AND scramble_sep(q=1.0) >= 0.30, AND CONTENT degrades MONOTONICALLY as q falls, AND
    CONTENT(q=1.0) >= 0.60 (handed reproduces). => content-addressed selection survives realistic cue noise:
    the gate INFERS relevance, not matches a handed delta. MM -> CG.
  MIDDLE_BAND = content-selection is real (CONTENT-RECENCY >= 0.15 at some q<1.0 with cue_snr<=20) and scramble
    fires, but it does NOT clear the realistic (cue_snr~7) bar -- it only beats the cap at higher cue-quality.
    Real but noise-fragile content-selection; the envelope is the finding; stays MM (honest deflation).
  HARD_FAIL = CONTENT-RECENCY < 0.15 already at the FIRST noisy point (q=0.7, cue_snr>>10). => content-selection
    collapses to the cap the moment the cue is anything but exact -> v6 only worked with the handed delta ->
    honest deflation, stays MM (the query-key primitive does not transfer to an INFERRED-cue regime here).
  BREAK-POINT (KEY ENVELOPE FINDING, reported regardless of tier): the cue_snr (and q) at which
    CONTENT-RECENCY first falls below 0.15 (content-selection stops beating the cap) as q descends.

COMPUTE ARCHITECTURE: batched-GPU. Per (seed,K,q): one train pass + one eval pass over BATCHed windows; per
  batch the noisy per-slot code tensor (B,K,N) is built ONCE and all four arms are derived from it (shared codes
  => arms differ only by gate; also avoids 4x recompute). Readout = mean-outer Hebbian (N x N) accumulated in
  batches, one W per arm. Content gate = per-instance query-key cosine + softmax (batched). No sequential
  dependency. Storage: no_storage / no_composition (single-hop content-addressed readout).

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. enc_gate uniform-g == enc_raw. 3. bpc/ppl
  formula. 4. build_slot_codes noise calibration: cos(noisy_flag, cb[FLAG]) ~= q for q in {1.0,0.4,0.1};
  q=1.0 => exact flag. 5. content gate concentrates on the FLAGGED slot at q=1.0 AND its concentration DEGRADES
  as q -> floor; scramble moves the peak OFF. 6. DISCRIMINATOR-FIRES ENVELOPE at real K (small scale): CONTENT
  lifts >= 0.30 over RAW at q=1.0, RAW/RECENCY capped ~1/(K-1) at all q, AND the CONTENT lift SHRINKS toward the
  cap as q -> floor (proves the noise-sweep is meaningful, not saturation-vacuous). 7. FULL => N=8192.
  ASCII-only. print(flush=True). start-marker + crash-diag + heartbeat.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 4 top1 (K,q)-curves; they diverge at q=1.0)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: top-1 recall on a content-addressed readout has no closed-form CRLB; the discriminator is the
#   arm-vs-arm recall GAP whose content-blind floor is the combinatorial 1/(K-1) cap (THEORETICAL, closed-form).
#   The cue-detectability floor is the codebook noise floor 1/sqrt(N) (THEORETICAL); break-point in cue_snr.
# - baseline_in_band: content-blind arms (RAW/RECENCY) in (chance=0.0625, 0.50) at ALL q; if >0.50 corpus broken
#   (INCONCLUSIVE), if at chance readout dead (INCONCLUSIVE). RAW/RECENCY must also be ~flat across q.
# - discriminator survives scale: cue_snr=q*sqrt(N) is N-invariant; smoke (N=1024, floor 0.031) is the HARDER
#   test (higher floor) and witnesses the break at the SAME cue_snr; smoke runs the FULL CUE_Q_GRID x K_GRID.
# - HARD_PASS strictly above floor: CONTENT >= cap+0.30 AND CONTENT-RECENCY >= 0.30 at the realistic cue_snr~7.
# - HP_SCOPE: HARD_PASS gates apply ONLY to CONTENT_GATE; RAW/RECENCY are content-blind controls (capped, not
#   HARD_PASS-gated); CONTENT_GATE_SCRAMBLED is the firing control (must NOT pass).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID)*len(CUE_Q_GRID); verdict counts len(per_unit).
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED.
# - calibration_check: default_ok_for_this_regime -- GATE_TAU=0.05 fixed and Q-AGNOSTIC (the gate does NOT know
#   q; a fixed temperature is the honest inferred test -- adapting tau to q would leak the answer). The
#   content-gate concentration self-test + the per-q content_gate_conc diagnostic are the gate-health gates.
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

ANCHOR_NAME = "substrate_gen_lm_contentgate_noisycue_v7_n8192_gpu"
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
LR = 1.0                           # Hebbian scale (mean-outer; LR folded into /M normalization)
BATCH = 256
GATE_TAU = 0.05                    # content-gate softmax temperature (fixed, Q-AGNOSTIC: gate must infer)
RECENCY_TAU = 0.1                  # recency-gate softmax temperature (v6 value)
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]   # decode softmax temperature grid (bpc readout)
HEADLINE_K = 6                     # headline K (research analytic example: 1/(K-1) = 0.20)
# cue-quality sweep: cos(noisy_flag, cb[FLAG]) target. 1.0 = v6 handed delta; low tail (0.02,0.01) sits at/below
# the FULL noise floor 1/sqrt(8192)=0.011 so the FULL run CAPTURES the break-point (smoke floor 0.031 is coarser).
CUE_Q_GRID = [1.0, 0.7, 0.4, 0.25, 0.15, 0.08, 0.04, 0.02, 0.01]
SNR_TARGET = 7.0                   # realistic-point selector: grid q with cue_snr=q*sqrt(N) closest to this
ARMS = ["RAW", "RECENCY_GATE", "CONTENT_GATE", "CONTENT_GATE_SCRAMBLED"]
ANTIDOTE_ARMS = ["CONTENT_GATE"]                  # HP_SCOPE: HARD_PASS applies ONLY here
CONTROL_ARM = "CONTENT_GATE_SCRAMBLED"
CONTENT_BLIND = ["RAW", "RECENCY_GATE"]           # must be capped ~1/(K-1), flat across q
LN2 = math.log(2.0)

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [7]
    K_GRID = [6, 10]; M_TRAIN = 3000; M_EVAL = 800; M_GATE = 1000
else:
    N_DIM = N; SEEDS = [7, 17, 23]
    K_GRID = [6, 10]; M_TRAIN = 8000; M_EVAL = 2000; M_GATE = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID) * len(CUE_Q_GRID)   # cardinality_ok (META_RULE_H)
assert HEADLINE_K in K_GRID, "HEADLINE_K must be in K_GRID"
assert len(V_SUB) >= max(K_GRID) - 1, "V_SUB must supply K-1 distinct distractors at max K"
assert abs(CUE_Q_GRID[0] - 1.0) < 1e-9, "CUE_Q_GRID must start at 1.0 (v6 handed reference)"


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
# codebook + corpus (variable-lag flagged-dependency instances)
# ---------------------------------------------------------------------------
def build_cb(V, n, gen):
    cb = (torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1)
    return cb / (cb.norm(dim=1, keepdim=True) + 1e-8)


def gen_instances(M, K, gen_np):
    """Generate M flagged-dependency instances. Returns (win (M,K) int64, tgt (M,) int64).
    Slot v-1 = FLAG; slot v = target VALUE; the K-1 non-FLAG slots hold DISTINCT V_SUB distractors (incl. slot v).
    v ~ uniform {1,...,K-1} => target POSITION is uniform (zero positional info); target CONTENT = post-FLAG.
    (Corpus is cue-quality-INDEPENDENT: token ids only; the flag CODE is corrupted later at encode time.)"""
    win = np.zeros((M, K), dtype=np.int64)
    tgt = np.zeros(M, dtype=np.int64)
    vsub = np.array(V_SUB, dtype=np.int64)
    for i in range(M):
        v = int(gen_np.integers(1, K))                       # {1,...,K-1}
        win[i, v - 1] = FLAG_ID                              # FLAG immediately before the VALUE
        nonflag = [s for s in range(K) if s != v - 1]        # K-1 slots (includes slot v)
        toks = gen_np.choice(vsub, size=len(nonflag), replace=False)   # distinct V_SUB distractors
        for s, t in zip(nonflag, toks):
            win[i, s] = int(t)
        tgt[i] = int(win[i, v])                              # target = VALUE at slot v
    return win, tgt


def _true_slots(win_np, K):
    """Recover the true VALUE slot v per instance (the slot AFTER the FLAG). Diagnostics/self-test only."""
    flag_slot = (win_np == FLAG_ID).argmax(axis=1)          # slot holding FLAG (v-1)
    return flag_slot + 1                                     # v


# ---------------------------------------------------------------------------
# NOISY-CUE injection: build per-slot code tensor with the flag slot corrupted to cos ~= cue_q
# ---------------------------------------------------------------------------
def _noise_seed(seed, K, cue_q, split):
    return int((seed * 1000003 + K * 10007 + int(round(cue_q * 10000)) * 13 + (1 if split == "tr" else 2)) % (2 ** 31))


def build_slot_codes(cb, win, cue_q, flag_code, gen):
    """Per-slot code tensor (B,K,N). Non-flag slots = cb[token]. Flag slots (win==FLAG_ID) are replaced by a
    per-instance NOISY flag  normalize(cue_q*flag_code + sqrt(1-cue_q^2)*random_unit)  so cos(noisy,flag)~=cue_q.
    cue_q>=0.999 => exact flag (v6 handed delta). The SAME codes tensor is reused across all four arms per
    (K,q) so the arms differ only by their admission gate. 'gen' is re-seeded per (seed,K,q,split) => reproducible."""
    codes = cb[win].clone()                                  # (B,K,N)
    if cue_q < 0.999:
        flag_mask = (win == FLAG_ID)                         # (B,K) exactly one True per row by construction
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
# encoders (windowed roll-bind on per-slot CODES; arms differ only by the admission gate)
# ---------------------------------------------------------------------------
def enc_raw_codes(slot_codes):
    """Uniform roll-bind bundle of K slots (== v6 enc_raw). slot_codes: (B,K,N). Returns (B,N) normalized."""
    B, K, n = slot_codes.shape
    b = torch.zeros(B, n, device=DEVICE)
    for j in range(K):
        b = b + torch.roll(slot_codes[:, j], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def enc_gate_codes(slot_codes, gate):
    """Gated roll-bind bundle. gate: (K,) fixed per-index (recency) OR (B,K) per-instance (content). The ONLY
    delta vs enc_raw_codes is the multiplicative admission weight. Uniform gate reduces to enc_raw_codes."""
    B, K, n = slot_codes.shape
    b = torch.zeros(B, n, device=DEVICE)
    for j in range(K):
        gj = gate[j] if gate.dim() == 1 else gate[:, j:j + 1]
        b = b + gj * torch.roll(slot_codes[:, j], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def content_gate_codes(slot_codes, flag_code, tau, scramble_perm=None):
    """Per-instance query-key admission on the (possibly NOISY) slot codes:
    r_j = cos(slot_code_{j-1}, flag_code); g = softmax(r/tau). At the true slot j=v the predecessor is the flag
    slot, whose code has cos ~= cue_q to flag_code (NOISY => the gate must infer relevance from a graded match).
    slot 0 has no in-window predecessor and can never be the VALUE (v>=1) -> masked to -inf.
    scramble_perm: (K,) derangement; if given, r columns are permuted so the peaked admission lands on a WRONG
    slot (firing control). Returns g (B,K)."""
    B, K, n = slot_codes.shape
    r = torch.full((B, K), -1e9, device=DEVICE)
    for j in range(1, K):
        r[:, j] = (slot_codes[:, j - 1] * flag_code).sum(dim=1)    # cos (unit-norm codes)
    if scramble_perm is not None:
        r = r[:, scramble_perm]                                    # derange -> peak off true slot
    return torch.softmax(r / tau, dim=1)


def _derangement(K, seed_val):
    """Fixed per-seed derangement of {0..K-1} (no fixed point). Used to scramble the content gate."""
    g = torch.Generator(device="cpu").manual_seed(int(seed_val))
    ar = torch.arange(K)
    for _ in range(200):
        perm = torch.randperm(K, generator=g)
        if int((perm == ar).sum()) == 0:
            return perm.to(DEVICE)
    return torch.arange(K - 1, -1, -1, device=DEVICE)              # reversal fallback (derangement for K>=2)


def learn_recency_gate(cb, win_tr, tgt_tr, K, tau):
    """v6-style fixed per-index gate (CONTENT-BLIND, cue-quality-INDEPENDENT): per-slot next-token predictiveness
    via a lightweight mean-outer Hebbian readout from the rolled CLEAN slot-j code to the target, then
    g = softmax(relevance/tau). On this corpus every slot is equally (un)predictive (target position uniform) so
    g ~= uniform; the arm is capped ~1/(K-1). Returns (g (K,), relevance (K,))."""
    n = cb.shape[1]
    M = min(M_GATE, win_tr.shape[0])
    wt = win_tr[:M]; tc = cb[tgt_tr[:M]]
    r = torch.zeros(K, device=DEVICE)
    for j in range(K):
        ctxj = torch.roll(cb[wt[:, j]], shifts=j + 1, dims=1)
        ctxj = ctxj / (ctxj.norm(dim=1, keepdim=True) + 1e-8)
        Wj = (tc.t() @ ctxj) / M                             # (N,N) mean-outer Hebbian
        pred = ctxj @ Wj.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
        r[j] = (pred * tc).sum(dim=1).mean()
        del Wj
    return torch.softmax(r / tau, dim=0), r


# ---------------------------------------------------------------------------
# per-(K,q) train / eval: build noisy codes ONCE per batch, derive all four arms
# ---------------------------------------------------------------------------
def _arm_contexts(slot_codes, flag_code, g_rec, perm):
    g_con = content_gate_codes(slot_codes, flag_code, GATE_TAU, None)
    g_scr = content_gate_codes(slot_codes, flag_code, GATE_TAU, perm)
    ctxs = {"RAW": enc_raw_codes(slot_codes),
            "RECENCY_GATE": enc_gate_codes(slot_codes, g_rec),
            "CONTENT_GATE": enc_gate_codes(slot_codes, g_con),
            "CONTENT_GATE_SCRAMBLED": enc_gate_codes(slot_codes, g_scr)}
    return ctxs, g_con


def train_all_arms(cb, win_tr, tgt_tr, cue_q, flag_code, g_rec, perm, seed, K):
    n = cb.shape[1]; M = win_tr.shape[0]
    Ws = {a: torch.zeros(n, n, device=DEVICE) for a in ARMS}
    gen = torch.Generator(device=DEVICE).manual_seed(_noise_seed(seed, K, cue_q, "tr"))
    for s in range(0, M, BATCH):
        wb = win_tr[s:s + BATCH]; tb = tgt_tr[s:s + BATCH]
        codes = build_slot_codes(cb, wb, cue_q, flag_code, gen)
        ctxs, _ = _arm_contexts(codes, flag_code, g_rec, perm)
        tcb = cb[tb].t()                                     # (N,B)
        for a in ARMS:
            Ws[a] = Ws[a] + LR * (tcb @ ctxs[a])
    return {a: Ws[a] / M for a in ARMS}


def _metrics_from_cos(cos_all, argmax_all, tgt_ev):
    M = cos_all.shape[0]
    top1 = float((argmax_all == tgt_ev).float().mean())
    vsub_t = torch.tensor(V_SUB, device=DEVICE)
    cos_vsub = cos_all[:, vsub_t]
    argmax_vsub = vsub_t[cos_vsub.argmax(dim=1)]
    top1_vsub = float((argmax_vsub == tgt_ev).float().mean())
    best_nats = float("inf")
    for t in TEMP_GRID:
        z = cos_all / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        P = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = P[torch.arange(M, device=DEVICE), tgt_ev].clamp_min(1e-12)
        best_nats = min(best_nats, float((-torch.log(pt)).mean()))
    distinct = float(torch.unique(argmax_all).numel()) / float(VOCAB)
    return {"top1": top1, "top1_vsub": top1_vsub, "bpc_nats": best_nats, "bpc_bits": best_nats / LN2,
            "perplexity": math.exp(best_nats), "distinct_token_rate": distinct}


def eval_all_arms(cb, Ws, win_ev, tgt_ev, cue_q, flag_code, g_rec, perm, v_true_ev, seed, K):
    M = win_ev.shape[0]
    cos_all = {a: torch.empty(M, VOCAB, device=DEVICE) for a in ARMS}
    argmax_all = {a: torch.empty(M, dtype=torch.long, device=DEVICE) for a in ARMS}
    conc_hits = 0; cue_cos_sum = 0.0
    gen = torch.Generator(device=DEVICE).manual_seed(_noise_seed(seed, K, cue_q, "ev"))
    for s in range(0, M, BATCH):
        wb = win_ev[s:s + BATCH]; bs = wb.shape[0]
        codes = build_slot_codes(cb, wb, cue_q, flag_code, gen)
        ctxs, g_con = _arm_contexts(codes, flag_code, g_rec, perm)
        vb = v_true_ev[s:s + bs]
        conc_hits += int((g_con.argmax(dim=1) == vb).sum())
        pred_true = codes[torch.arange(bs, device=DEVICE), vb - 1]     # code at the flag slot (predecessor of v)
        cue_cos_sum += float((pred_true * flag_code).sum(dim=1).sum())
        for a in ARMS:
            pred = ctxs[a] @ Ws[a].t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
            cos = pred @ cb.t()                              # (bs,VOCAB)
            cos_all[a][s:s + bs] = cos
            argmax_all[a][s:s + bs] = cos.argmax(dim=1)
    out = {a: _metrics_from_cos(cos_all[a], argmax_all[a], tgt_ev) for a in ARMS}
    return out, conc_hits / float(M), cue_cos_sum / float(M)


# ---------------------------------------------------------------------------
# self-test (PROT-022): runs on import; blocks dispatch if any assert fails
# ---------------------------------------------------------------------------
def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(VOCAB, 256, gen)
    flag_code = cb[FLAG_ID]
    # roll-bind order-sensitive
    w1 = torch.tensor([[3, 5, 9]], device=DEVICE); w2 = torch.tensor([[9, 5, 3]], device=DEVICE)
    c1 = build_slot_codes(cb, w1, 1.0, flag_code, gen); c2 = build_slot_codes(cb, w2, 1.0, flag_code, gen)
    b1 = enc_raw_codes(c1); b2 = enc_raw_codes(c2)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    # enc_gate uniform == enc_raw
    gate_uni = enc_gate_codes(c1, torch.ones(3, device=DEVICE)); raw = enc_raw_codes(c1)
    assert float((gate_uni * raw).sum()) > 0.999, "enc_gate uniform-g != enc_raw"
    # bpc/ppl formula
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "bpc/ppl formula"
    # NOISE CALIBRATION: cos(noisy_flag, cb[FLAG]) ~= cue_q
    Kt = 6; gnp = np.random.default_rng(3)
    win_np, _ = gen_instances(600, Kt, gnp)
    win_t = torch.tensor(win_np, device=DEVICE)
    v_true = torch.tensor(_true_slots(win_np, Kt), device=DEVICE)
    fmask = (win_t == FLAG_ID)
    for q in [1.0, 0.4, 0.1]:
        gg = torch.Generator(device=DEVICE).manual_seed(123)
        codes = build_slot_codes(cb, win_t, q, flag_code, gg)
        flagcodes = codes[fmask]                              # (M,N)
        cosq = float((flagcodes * flag_code).sum(dim=1).mean())
        if q >= 0.999:
            assert cosq > 0.999, f"q=1.0 must give exact flag; got cos={cosq:.4f}"
        else:
            assert abs(cosq - q) < 0.08, f"noise calibration off at q={q}: mean cos={cosq:.4f}"
    # content gate concentrates at q=1.0 and DEGRADES as q -> floor; scramble moves off
    g_hi = content_gate_codes(build_slot_codes(cb, win_t, 1.0, flag_code, torch.Generator(device=DEVICE).manual_seed(1)),
                              flag_code, GATE_TAU, None)
    conc_hi = float((g_hi.argmax(dim=1) == v_true).float().mean())
    gval_hi = float(g_hi[torch.arange(g_hi.shape[0], device=DEVICE), v_true].mean())
    assert conc_hi > 0.95, f"content gate did not concentrate at q=1.0 (conc={conc_hi:.3f})"
    assert gval_hi > 0.5, f"content gate weight on true slot too low at q=1.0 ({gval_hi:.3f})"
    g_lo = content_gate_codes(build_slot_codes(cb, win_t, 0.04, flag_code, torch.Generator(device=DEVICE).manual_seed(2)),
                              flag_code, GATE_TAU, None)
    conc_lo = float((g_lo.argmax(dim=1) == v_true).float().mean())
    # at N=256 noise floor ~0.0625; q=0.04 is BELOW floor -> concentration must collapse well below q=1.0
    assert conc_lo < conc_hi - 0.25, f"content gate concentration did not degrade with noise (hi={conc_hi:.3f} lo={conc_lo:.3f})"
    perm = _derangement(Kt, 99)
    gs = content_gate_codes(build_slot_codes(cb, win_t, 1.0, flag_code, torch.Generator(device=DEVICE).manual_seed(3)),
                            flag_code, GATE_TAU, perm)
    off = float((gs.argmax(dim=1) != v_true).float().mean())
    assert off > 0.90, f"scrambled gate still admits true slot too often (off-frac={off:.3f})"
    # DISCRIMINATOR-FIRES ENVELOPE at real K (small scale): CONTENT lifts >=0.30 over RAW at q=1.0, RAW/RECENCY
    #   capped ~1/(K-1) at all q, AND the CONTENT lift SHRINKS toward the cap as q -> floor.
    n_small = 512; Kd = 6
    cbs = build_cb(VOCAB, n_small, torch.Generator(device=DEVICE).manual_seed(5)); fcs = cbs[FLAG_ID]
    gnp2 = np.random.default_rng(7)
    wtr, ttr = gen_instances(2000, Kd, gnp2); wev, tev = gen_instances(800, Kd, gnp2)
    wtr_t = torch.tensor(wtr, device=DEVICE); ttr_t = torch.tensor(ttr, device=DEVICE)
    wev_t = torch.tensor(wev, device=DEVICE); tev_t = torch.tensor(tev, device=DEVICE)
    vte = torch.tensor(_true_slots(wev, Kd), device=DEVICE)
    g_rec, _ = learn_recency_gate(cbs, wtr_t, ttr_t, Kd, RECENCY_TAU)
    permd = _derangement(Kd, 13)
    cap = 1.0 / (Kd - 1)   # 0.20
    res = {}
    for q in [1.0, 0.04]:
        Ws = train_all_arms(cbs, wtr_t, ttr_t, q, fcs, g_rec, permd, 5, Kd)
        m, _, _ = eval_all_arms(cbs, Ws, wev_t, tev_t, q, fcs, g_rec, permd, vte, 5, Kd)
        res[q] = {a: m[a]["top1"] for a in ARMS}
    for q in [1.0, 0.04]:
        assert res[q]["RAW"] <= cap + 0.15, f"RAW not capped near 1/(K-1)={cap:.3f} at q={q}: got {res[q]['RAW']:.3f}"
        assert res[q]["RECENCY_GATE"] <= cap + 0.15, f"RECENCY not capped at q={q}: got {res[q]['RECENCY_GATE']:.3f}"
    assert res[1.0]["CONTENT_GATE"] >= 0.55, f"CONTENT_GATE did not lift at q=1.0 small scale: got {res[1.0]['CONTENT_GATE']:.3f}"
    assert res[1.0]["CONTENT_GATE"] - res[1.0]["RAW"] >= 0.30, \
        f"CONTENT-RAW lift < 0.30 at q=1.0: {res[1.0]['CONTENT_GATE']:.3f}-{res[1.0]['RAW']:.3f}"
    assert res[1.0]["CONTENT_GATE"] - res[1.0]["CONTENT_GATE_SCRAMBLED"] >= 0.25, \
        f"scramble separation < 0.25 at q=1.0: {res[1.0]['CONTENT_GATE']:.3f}-{res[1.0]['CONTENT_GATE_SCRAMBLED']:.3f}"
    assert res[1.0]["CONTENT_GATE"] - res[0.04]["CONTENT_GATE"] >= 0.20, \
        f"CONTENT lift did not shrink as q->floor (noise-sweep vacuous): q1={res[1.0]['CONTENT_GATE']:.3f} " \
        f"qlo={res[0.04]['CONTENT_GATE']:.3f}"
    assert N == 8192
    print(f"[selftest] PASS: rollbind gate_uni==raw bpc noise_calib content_conc(hi={conc_hi:.2f}->lo={conc_lo:.2f}) "
          f"scramble_off({off:.2f}) envelope@K{Kd}[q1.0:RAW={res[1.0]['RAW']:.2f} REC={res[1.0]['RECENCY_GATE']:.2f} "
          f"CON={res[1.0]['CONTENT_GATE']:.2f} SCR={res[1.0]['CONTENT_GATE_SCRAMBLED']:.2f} | q.04:CON={res[0.04]['CONTENT_GATE']:.2f} "
          f"RAW={res[0.04]['RAW']:.2f}] cap={cap:.2f} N8192", flush=True)


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
        win_tr_np, tgt_tr_np = gen_instances(M_TRAIN, K, gen_np)
        win_ev_np, tgt_ev_np = gen_instances(M_EVAL, K, gen_np)
        win_tr = torch.tensor(win_tr_np, device=DEVICE); tgt_tr = torch.tensor(tgt_tr_np, device=DEVICE)
        win_ev = torch.tensor(win_ev_np, device=DEVICE); tgt_ev = torch.tensor(tgt_ev_np, device=DEVICE)
        v_true_ev = torch.tensor(_true_slots(win_ev_np, K), device=DEVICE)
        g_rec, r_rec = learn_recency_gate(cb, win_tr, tgt_tr, K, RECENCY_TAU)
        perm = _derangement(K, seed * 17 + K)
        klog = {"recency_gate": [round(float(x), 4) for x in g_rec.tolist()],
                "recency_relevance": [round(float(x), 4) for x in r_rec.tolist()],
                "scramble_perm": [int(x) for x in perm.tolist()],
                "chance": round(1.0 / len(V_SUB), 4), "content_blind_cap": round(1.0 / (K - 1), 4),
                "noise_floor": round(noise_floor, 5), "per_q": {}}
        print(f"    [K={K}] recency_g={[round(float(x),3) for x in g_rec.tolist()]} cap=1/(K-1)={1.0/(K-1):.3f} "
              f"noise_floor={noise_floor:.4f} perm={perm.tolist()}", flush=True)
        for cue_q in CUE_Q_GRID:
            cue_snr = cue_q * math.sqrt(n_dim)
            Ws = train_all_arms(cb, win_tr, tgt_tr, cue_q, flag_code, g_rec, perm, seed, K)
            arm_metrics, content_conc, cue_cos_true = eval_all_arms(
                cb, Ws, win_ev, tgt_ev, cue_q, flag_code, g_rec, perm, v_true_ev, seed, K)
            for arm in ARMS:
                m = dict(arm_metrics[arm])
                m.update({"seed": seed, "arm": arm, "K": K, "cue_q": float(cue_q),
                          "cue_snr": round(cue_snr, 3), "N": n_dim})
                per_unit.append(m); unit_i += 1
                emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed, total_units=total_units,
                               extra={"seed": seed, "arm": arm, "K": K, "cue_q": float(cue_q),
                                      "top1": round(m["top1"], 3)})
            klog["per_q"]["%.3f" % cue_q] = {"content_gate_conc": round(content_conc, 4),
                                             "cue_cos_true": round(cue_cos_true, 4), "cue_snr": round(cue_snr, 3)}
            print(f"      [q={cue_q:.3f} snr={cue_snr:6.2f} conc={content_conc:.3f} cos_true={cue_cos_true:.3f}] "
                  f"RAW={arm_metrics['RAW']['top1']:.3f} REC={arm_metrics['RECENCY_GATE']['top1']:.3f} "
                  f"CON={arm_metrics['CONTENT_GATE']['top1']:.3f} SCR={arm_metrics['CONTENT_GATE_SCRAMBLED']['top1']:.3f}",
                  flush=True)
        gate_log["K%d" % K] = klog
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "per_unit": per_unit, "gate_log": gate_log,
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _val(all_results, arm, K, cue_q, field="top1"):
    vals = [u[field] for r in all_results for u in r["per_unit"]
            if u["arm"] == arm and u["K"] == K and abs(u["cue_q"] - cue_q) < 1e-6]
    return float(np.mean(vals)) if vals else float("nan")


def _curve_over_q(all_results, arm, K, field="top1"):
    return {q: _val(all_results, arm, K, q, field) for q in CUE_Q_GRID}


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units} units, expected {EXPECTED_N_UNITS}")
    n_dim = all_results[0]["N"]; K = HEADLINE_K
    con = _curve_over_q(all_results, "CONTENT_GATE", K)
    raw = _curve_over_q(all_results, "RAW", K)
    rec = _curve_over_q(all_results, "RECENCY_GATE", K)
    scr = _curve_over_q(all_results, "CONTENT_GATE_SCRAMBLED", K)
    cap = 1.0 / (K - 1); chance = 1.0 / len(V_SUB)
    q_hi = 1.0
    con1 = con[q_hi]; raw1 = raw[q_hi]; rec1 = rec[q_hi]; scr1 = scr[q_hi]
    sep1 = con1 - scr1
    lift_rec = {q: con[q] - rec[q] for q in CUE_Q_GRID}

    def snr(q):
        return q * math.sqrt(n_dim)

    # realistic point = grid q with cue_snr closest to SNR_TARGET
    q_real = min(CUE_Q_GRID, key=lambda q: abs(snr(q) - SNR_TARGET))
    lift_real = con[q_real] - rec[q_real]; con_real = con[q_real]

    # break-point: descending q, first q where lift_vs_recency < 0.15
    q_break_015 = None; q_break_030 = None
    for q in CUE_Q_GRID:                                       # already descending
        if q_break_030 is None and lift_rec[q] < 0.30:
            q_break_030 = q
        if q_break_015 is None and lift_rec[q] < 0.15:
            q_break_015 = q
    bp015 = "below_grid_min" if q_break_015 is None else f"{q_break_015:.3f}(snr={snr(q_break_015):.2f})"
    bp030 = "below_grid_min" if q_break_030 is None else f"{q_break_030:.3f}(snr={snr(q_break_030):.2f})"

    # monotone degradation of CONTENT as q falls (descending q; allow small tolerance)
    monotone = all(con[CUE_Q_GRID[i + 1]] <= con[CUE_Q_GRID[i]] + 0.06 for i in range(len(CUE_Q_GRID) - 1))
    # content-blind flatness sanity
    raw_span = max(raw.values()) - min(raw.values())

    curstr = (f"CON={ {round(q,3): round(con[q],3) for q in CUE_Q_GRID} } "
              f"RAW={ {round(q,3): round(raw[q],3) for q in CUE_Q_GRID} } "
              f"REC={ {round(q,3): round(rec[q],3) for q in CUE_Q_GRID} } "
              f"SCR={ {round(q,3): round(scr[q],3) for q in CUE_Q_GRID} }")
    summary = (f"@K{K} N={n_dim} floor=1/sqrt(N)={1.0/math.sqrt(n_dim):.4f} | q=1.0: RAW={raw1:.3f} REC={rec1:.3f} "
               f"CON={con1:.3f} SCR={scr1:.3f} scramble_sep={sep1:+.3f} | realistic q={q_real:.3f} "
               f"(snr={snr(q_real):.2f}): CON={con_real:.3f} lift_vs_recency={lift_real:+.3f} cap={cap:.3f} | "
               f"BREAK-POINT lift<0.15 at q={bp015} ; lift<0.30 at q={bp030} | monotone={monotone} raw_span={raw_span:.3f} | "
               f"curves: {curstr}")

    # VALID-ONLY-IF: corpus must force content-selection (content-blind arms capped). Saturation-vacuous inverse.
    if raw1 > 0.50 or rec1 > 0.50:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_CORPUS_DOES_NOT_DISCRIMINATE: a content-blind arm exceeds 0.50 at "
                f"q=1.0 (RAW={raw1:.3f} RECENCY={rec1:.3f}); readout solves the task WITHOUT content-selection. "
                f"Re-spec. {summary}")
    if raw1 < chance * 1.5 and rec1 < chance * 1.5:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_AT_CHANCE: content-blind arms near chance ({chance:.3f}) at "
                f"q=1.0 (RAW={raw1:.3f} RECENCY={rec1:.3f}); the Hebbian readout failed, not a gating result. {summary}")

    # HARD_FAIL: content collapses to cap as soon as the cue is noisy (first noisy grid point)
    q_first_noisy = CUE_Q_GRID[1]
    if lift_rec[q_first_noisy] < 0.15:
        return ("HARD_FAIL", f"HARD_FAIL_NOISE_FRAGILE: content gate gives no lift over the fixed-index recency "
                f"gate the moment the cue is noisy (lift_vs_recency@q={q_first_noisy:.2f}={lift_rec[q_first_noisy]:+.3f} "
                f"< 0.15). v6 worked only with the EXACT handed delta; the query-key primitive does not transfer to "
                f"an INFERRED-cue regime here. Honest deflation -> stays MEASURED_MECHANISM. {summary}")

    # HARD_PASS (HP_SCOPE: CONTENT_GATE only) -- content-selection survives realistic (near-floor) cue noise
    if (lift_real >= 0.30 and con_real >= cap + 0.30 and sep1 >= 0.30 and monotone and con1 >= 0.60):
        return ("HARD_PASS", f"HARD_PASS[CONTENT_GATE]_NOISY_CUE_PROMOTION: content-addressed (query-key) admission "
                f"beats the 1/(K-1) content-blind cap at a REALISTIC inferred cue-quality (q={q_real:.3f}, "
                f"cue_snr={snr(q_real):.2f}): CON={con_real:.3f}>=cap+0.30 ({cap+0.30:.3f}), "
                f"lift_vs_recency={lift_real:+.3f}>=0.30, scramble_sep(q=1.0)={sep1:+.3f}>=0.30, monotone degradation. "
                f"The gate INFERS relevance from a graded, noise-corrupted cue (not a handed delta) -> MM promotes to "
                f"CG (content-selection is the lever under realistic noise). {summary}")

    # MIDDLE_BAND: content-selection real but noise-fragile (passes only above the realistic bar)
    real_lift_anywhere = any((con[q] - rec[q]) >= 0.15 and snr(q) <= 20.0 and q < 1.0 for q in CUE_Q_GRID)
    if (real_lift_anywhere or lift_rec[q_first_noisy] >= 0.15) and sep1 > 0.0:
        return ("MIDDLE_BAND", f"MIDDLE_BAND[CONTENT_GATE]_NOISE_FRAGILE: content-selection is real (beats the cap at "
                f"higher cue-quality; scramble fires, sep(q=1.0)={sep1:+.3f}) but does NOT clear the realistic "
                f"cue_snr~{SNR_TARGET:.0f} bar (realistic q={q_real:.3f}: lift_vs_recency={lift_real:+.3f}, "
                f"CON={con_real:.3f} vs cap+0.30={cap+0.30:.3f}). The BREAK-POINT is the finding; stays "
                f"MEASURED_MECHANISM (noise-fragile inference). {summary}")

    # HARD_FAIL fallback
    return ("HARD_FAIL", f"HARD_FAIL: content gate did not beat the cap at any genuinely-inferred cue-quality "
            f"OR scramble replicated (sep(q=1.0)={sep1:+.3f}). {summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} "
          f"K_GRID={K_GRID} headline_K={HEADLINE_K} CUE_Q_GRID={CUE_Q_GRID} arms={ARMS} V_SUB={len(V_SUB)} "
          f"FLAG={FLAG_ID} M_TRAIN={M_TRAIN} M_EVAL={M_EVAL} GATE_TAU={GATE_TAU} SNR_TARGET={SNR_TARGET} "
          f"expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS,
                                                                  "K_GRID": K_GRID, "headline_K": HEADLINE_K,
                                                                  "cue_q_grid": CUE_Q_GRID, "v_sub": len(V_SUB),
                                                                  "gate_tau": GATE_TAU})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): the 4 top1 (K,q)-curves must not be bit-identical
    import hashlib
    digs = {}
    for arm in ARMS:
        pts = {}
        for K in K_GRID:
            for q in CUE_Q_GRID:
                pts["K%d_q%.3f" % (K, q)] = round(_val(all_results, arm, K, q), 6)
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
    curves = {arm: {"K%d" % K: {"%.3f" % q: round(_val(all_results, arm, K, q), 5) for q in CUE_Q_GRID}
                    for K in K_GRID} for arm in ARMS}
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "headline_K": HEADLINE_K,
               "k_grid": K_GRID, "cue_q_grid": CUE_Q_GRID, "snr_target": SNR_TARGET, "v_sub": len(V_SUB),
               "flag_id": FLAG_ID, "gate_tau": GATE_TAU, "noise_floor": round(1.0 / math.sqrt(N_DIM), 5),
               "expected_n_units": EXPECTED_N_UNITS, "arm_digests": digs, "per_seed": all_results,
               "curves_top1": curves,
               "curves_bpc": {arm: {"K%d" % K: {"%.3f" % q: round(_val(all_results, arm, K, q, "bpc_bits"), 5)
                                                for q in CUE_Q_GRID} for K in K_GRID} for arm in ARMS}}
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
