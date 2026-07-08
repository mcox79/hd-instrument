"""
substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu -- CONTENT-dependent context gating (honest follow-on to v5's
  recency-gate headline). v5 (exp_substrate_gen_lm_contextgate_depth_v5_n8192_gpu, commit 4692cd9cc) learned a
  RECENCY gate: a single per-slot-index weight vector g_j, identical for every sequence, that concentrates on the
  MOST-RECENT slot because in a 1st-order Markov corpus the most-recent slot IS always the relevant one. That is
  index-selection, not content-selection -- it is mathematically guaranteed to fail the moment the relevant
  slot's POSITION varies from instance to instance. The untested harder capability = CONTENT-dependent gating:
  select the relevant past slot by its CONTENT (query-key attention), not its position.

BRAIN-GROUNDING (notes/research_content_gate_brain_grounding_2026-07-08.md): biased-competition / top-down
  attentional template (Desimone & Duncan 1995; Reynolds & Heeger 2009 normalization model) == query-key
  attention (Ramsauer et al. 2020 prove modern-Hopfield retrieval update = softmax(beta Q K^T) V); PBWM
  (O'Reilly & Frank 2006) shows content/task-relevance beats recency in sequential (12-AX) tasks. All three
  literatures reduce to ONE computation: similarity-weighted (soft) selection among a candidate set by match to a
  top-down cue. The substrate primitive: enc_gate with the per-slot weight g_j(query) = softmax(cos(cue,key_j)/tau)
  RE-COMPUTED PER INSTANCE from content, instead of v5's fixed-once-per-corpus g[j].

THE CORPUS (regime where recency provably fails; variable-lag flagged dependency):
  Each instance = a K-slot context window preceding a QUERY. Reserve one token id as FLAG. Exactly one slot v is
  the informative VALUE (drawn from a small VALUE sub-vocab V_SUB); slot v-1 holds FLAG. The target (next token
  at the QUERY) = the VALUE at slot v. v is drawn UNIFORMLY AT RANDOM in {1,...,K-1} per instance, so the
  informative slot's POSITION carries ZERO information by construction, while its CONTENT (preceded-by-FLAG) is a
  deterministic always-present signal. CRITICAL DISCRIMINATOR-HARDENING: the K-1 NON-FLAG slots are ALL filled
  with DISTINCT distractor tokens ALSO drawn from V_SUB. So every candidate in the window looks like a valid
  VALUE; a content-blind readout over the bundle cannot tell the target from the K-1 distractors and is
  ANALYTICALLY capped at 1/(K-1) recall (guess among the K-1 present candidates). The ONLY way to exceed the cap
  is to use the FLAG cue to select the correct slot. (Chance = 1/|V_SUB|, strictly below the 1/(K-1) cap.)

ARMS (paired -- all arms evaluated on the SAME held-out instances per seed):
  RAW            -- uniform roll-bind bundle of all K slots (v5's enc_raw, unchanged). Content-blind; ~1/(K-1).
  RECENCY_GATE   -- v5's mechanism: ONE fixed per-index weight g_j learned from per-slot next-token
                    predictiveness, averaged over instances, applied identically to every instance. On this
                    corpus every slot is equally (un)predictive (target position is uniform) so g ~= uniform and
                    the arm is content-blind; capped ~1/(K-1). This is the honest paired recency control.
  CONTENT_GATE   -- NEW: per-instance gate g_j(instance) = softmax(cos(cb[tok_at_slot_{j-1}], cb[FLAG])/tau), i.e.
                    admit the slot whose immediate predecessor was FLAG (query-key attention with query=FLAG code,
                    keys=per-slot predecessor codes). Concentrates on slot v -> reads the true VALUE -> should
                    exceed the 1/(K-1) cap.
  CONTENT_GATE_SCRAMBLED -- firing control: identical query-key relevance SPECTRUM, but the per-slot relevance
                    vector is DERANGED (fixed per-seed permutation) so the peaked admission lands on a WRONG
                    (non-VALUE) slot. Same magnitude/entropy, content-correctness destroyed. Must NOT recover:
                    isolates genuine content-match from any peaked admission helping by variance-reduction alone.

METRIC: top-1 recall of the correct VALUE token at QUERY positions (chance = 1/|V_SUB|). bpc reported for
  continuity. Headline at K=HEADLINE_K (matches research's analytic 1/(K-1) example).

PRE-REGISTERED BANDS (headline K):
  VALID-ONLY-IF (discriminator fires / corpus discriminates): RAW <= 0.35 AND RECENCY_GATE <= 0.35 (both near the
    1/(K-1) analytic cap; if either > 0.50 the corpus does NOT force content-selection -- RAW already solves it
    -- INCONCLUSIVE, re-spec, the saturation-vacuous inverse).
  HARD_PASS = CONTENT_GATE recall >= 0.70 AND RECENCY_GATE recall <= 0.30 AND
              (CONTENT_GATE - CONTENT_GATE_SCRAMBLED) >= 0.30. Content-addressed selection is the lever; the
              corpus provably discriminates; the scramble control does not replicate.
  MIDDLE_BAND = (CONTENT_GATE - RECENCY_GATE) >= 0.15 but no full HARD_PASS, OR scramble separation positive but
              < 0.30.
  HARD_FAIL = (CONTENT_GATE - RECENCY_GATE) < 0.15 (content gate gives no real lift over a fixed-index gate on a
              corpus built so index carries zero information -> query-key primitive fails to transfer from the
              spatial/simultaneous biased-competition literature to the temporal/sequential slot-selection
              setting), OR CONTENT_GATE_SCRAMBLED matches CONTENT_GATE (no genuine content-selection).

COMPUTE ARCHITECTURE: batched-GPU. Encoders = elementwise-scaled roll-bind bundles batched over BATCH windows;
  readout = mean outer-product Hebbian (N x N) accumulated in batches; content gate = per-instance query-key
  cosine + softmax (batched). No sequential dependency. Storage: no_storage / no_composition (single-hop
  content-addressed readout; not a chained composition).

FORMULA SELF-TESTS (PROT-022): 1. roll-bind order-sensitive. 2. content gate concentrates on the FLAGGED slot
  (argmax g == true slot v; mean g at true slot > 0.5). 3. scramble moves the admission peak OFF the true slot.
  4. RECENCY/RAW analytically capped ~1/(K-1) on this corpus AND CONTENT_GATE lifts >= 0.30 over RAW at small
  scale (discriminator-fires at real K). 5. bpc_bits = nats/ln2, ppl = exp(nats). 6. enc_gate uniform-g ==
  enc_raw. 7. FULL => N=8192. ASCII-only. print(flush=True). start-marker + crash-diag + heartbeat.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ARMS-MUST-DIFFER hash of the 4 K-curves)
# - final_metrics_atomicity: tmp_replace (write_metrics + crash-diag both os.replace atomic)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: top-1 recall on a content-addressed readout has no closed-form CRLB at this regime; the
#   discriminator is the arm-vs-arm recall GAP, whose floor is the combinatorial 1/(K-1) content-blind cap
#   (THEORETICAL, closed-form) -- RAW/RECENCY must land near it, CONTENT_GATE must exceed 0.70.
# - baseline_in_band: content-blind arms (RAW/RECENCY) must be in (chance=1/|V_SUB|, 0.50); if >0.50 corpus is
#   broken (INCONCLUSIVE), if at chance the readout itself failed (logged).
# - discriminator survives scale: analytical -- the 1/(K-1) cap is combinatorial (dimension-independent) and
#   codebook near-orthogonality IMPROVES with N, so a gap that fires at smoke N=1024 fires at FULL N=8192.
#   Smoke additionally runs the FULL K_GRID so the discriminator is exercised at the real K.
# - HARD_PASS strictly above floor: CONTENT_GATE >= 0.70 (>> the 0.30 controls) + >=0.30 scramble separation.
# - HP_SCOPE: HARD_PASS gates apply ONLY to CONTENT_GATE; RAW/RECENCY_GATE are content-blind controls (must be
#   capped, not gated for HARD_PASS); CONTENT_GATE_SCRAMBLED is the firing control (must NOT pass).
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(ARMS)*len(K_GRID); verdict counts len(per_unit).
# - per-unit failure-class: except Exception (not bare/BaseException); crash-diag writes CELL_CRASHED.
# - calibration_check: default_ok_for_this_regime (GATE_TAU=0.05 sharp; content-gate concentration self-test is
#   the gate-health gate; RECENCY_TAU=0.1 as v5).
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

ANCHOR_NAME = "substrate_gen_lm_contentgate_flagdep_v6_n8192_gpu"
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
GATE_TAU = 0.05                    # content-gate softmax temperature (sharp query-key admission)
RECENCY_TAU = 0.1                  # recency-gate softmax temperature (v5 value)
TEMP_GRID = [1.0, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1]   # decode softmax temperature grid (bpc readout)
HEADLINE_K = 6                     # headline K (research analytic example: 1/(K-1) = 0.20)
ARMS = ["RAW", "RECENCY_GATE", "CONTENT_GATE", "CONTENT_GATE_SCRAMBLED"]
ANTIDOTE_ARMS = ["CONTENT_GATE"]                  # HP_SCOPE: HARD_PASS applies ONLY here
CONTROL_ARM = "CONTENT_GATE_SCRAMBLED"
CONTENT_BLIND = ["RAW", "RECENCY_GATE"]           # must be capped ~1/(K-1)
LN2 = math.log(2.0)

if RUN_MODE == "smoke":
    N_DIM = 1024; SEEDS = [7]
    K_GRID = [4, 6, 8]; M_TRAIN = 3000; M_EVAL = 1000; M_GATE = 1000
else:
    N_DIM = N; SEEDS = [7, 17, 23]
    K_GRID = [4, 6, 8]; M_TRAIN = 8000; M_EVAL = 2000; M_GATE = 2000

EXPECTED_N_UNITS = len(SEEDS) * len(ARMS) * len(K_GRID)   # cardinality_ok gate (META_RULE_H)
assert HEADLINE_K in K_GRID, "HEADLINE_K must be in K_GRID"
assert len(V_SUB) >= max(K_GRID) - 1, "V_SUB must supply K-1 distinct distractors at max K"


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
    v ~ uniform {1,...,K-1} => target POSITION is uniform (zero positional info); target CONTENT = post-FLAG."""
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
    """Recover the true VALUE slot v per instance (the slot AFTER the FLAG). For self-test only."""
    flag_slot = (win_np == FLAG_ID).argmax(axis=1)          # slot holding FLAG (v-1)
    return flag_slot + 1                                     # v


# ---------------------------------------------------------------------------
# encoders (windowed roll-bind; all arms differ only by the admission gate)
# ---------------------------------------------------------------------------
def enc_raw_win(cb, win):
    """Uniform roll-bind bundle of K slots (== v5 enc_raw). win: (B,K) int64. Returns (B,N) normalized."""
    B, K = win.shape
    b = torch.zeros(B, cb.shape[1], device=DEVICE)
    for j in range(K):
        b = b + torch.roll(cb[win[:, j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def enc_gate_win(cb, win, gate):
    """Gated roll-bind bundle. gate: (K,) fixed per-index (recency) OR (B,K) per-instance (content). The ONLY
    delta vs enc_raw_win is the multiplicative admission weight. Uniform gate reduces to enc_raw_win."""
    B, K = win.shape
    b = torch.zeros(B, cb.shape[1], device=DEVICE)
    for j in range(K):
        gj = gate[j] if gate.dim() == 1 else gate[:, j:j + 1]
        b = b + gj * torch.roll(cb[win[:, j]], shifts=j + 1, dims=1)
    return b / (b.norm(dim=1, keepdim=True) + 1e-8)


def content_gate(cb, win, tau, scramble_perm=None):
    """Per-instance query-key admission: r_j = cos(cb[tok_at_slot_{j-1}], cb[FLAG]); g = softmax(r/tau).
    slot 0 has no in-window predecessor and can never be the VALUE (v>=1) -> masked to -inf.
    scramble_perm: (K,) derangement; if given, r columns are permuted so the peaked admission lands on a WRONG
    slot (firing control -- same spectrum/entropy, content-correctness destroyed). Returns g (B,K)."""
    B, K = win.shape
    flag_code = cb[FLAG_ID]                                  # (N,) query
    r = torch.full((B, K), -1e9, device=DEVICE)
    for j in range(1, K):
        pred_code = cb[win[:, j - 1]]                        # (B,N) predecessor of slot j = key
        r[:, j] = (pred_code * flag_code).sum(dim=1)         # cos (unit-norm codes)
    if scramble_perm is not None:
        r = r[:, scramble_perm]                              # derange -> peak off true slot
    return torch.softmax(r / tau, dim=1)


def _derangement(K, seed_val):
    """Fixed per-seed derangement of {0..K-1} (no fixed point). Used to scramble the content gate."""
    g = torch.Generator(device="cpu").manual_seed(int(seed_val))
    ar = torch.arange(K)
    for _ in range(200):
        perm = torch.randperm(K, generator=g)
        if int((perm == ar).sum()) == 0:
            return perm.to(DEVICE)
    return torch.arange(K - 1, -1, -1, device=DEVICE)        # reversal fallback (derangement for K>=2 even/odd)


def learn_recency_gate(cb, win_tr, tgt_tr, K, tau):
    """v5-style fixed per-index gate: per-slot next-token predictiveness via a lightweight mean-outer Hebbian
    readout from the rolled slot-j code to the target, then g = softmax(relevance/tau). CONTENT-BLIND (uses only
    slot INDEX, applied identically to every instance). On this corpus every slot is equally (un)predictive
    (target position uniform) so g ~= uniform; the arm is capped ~1/(K-1). Returns (g (K,), relevance (K,))."""
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
# arm encode / readout / eval
# ---------------------------------------------------------------------------
def encode_arm(cb, win, arm, g_rec, perm):
    if arm == "RAW":
        return enc_raw_win(cb, win)
    if arm == "RECENCY_GATE":
        return enc_gate_win(cb, win, g_rec)
    if arm == "CONTENT_GATE":
        return enc_gate_win(cb, win, content_gate(cb, win, GATE_TAU, None))
    if arm == "CONTENT_GATE_SCRAMBLED":
        return enc_gate_win(cb, win, content_gate(cb, win, GATE_TAU, perm))
    raise ValueError(f"unknown arm {arm}")


def train_readout(cb, win_tr, tgt_tr, arm, g_rec, perm):
    """Mean-outer Hebbian readout W = mean_i outer(cb[target_i], gated_ctx_i). Batched accumulation."""
    n = cb.shape[1]; M = win_tr.shape[0]
    W = torch.zeros(n, n, device=DEVICE)
    for s in range(0, M, BATCH):
        wb = win_tr[s:s + BATCH]; tb = tgt_tr[s:s + BATCH]
        ctx = encode_arm(cb, wb, arm, g_rec, perm)
        W = W + LR * (cb[tb].t() @ ctx)
    return W / M


def eval_arm(cb, W, win_ev, tgt_ev, arm, g_rec, perm):
    """Top-1 recall of the target VALUE (argmax over full VOCAB) + best-temp bpc, on held-out instances."""
    M = win_ev.shape[0]
    argmax_all = torch.empty(M, dtype=torch.long, device=DEVICE)
    cos_all = torch.empty(M, VOCAB, device=DEVICE)
    for s in range(0, M, BATCH):
        wb = win_ev[s:s + BATCH]
        ctx = encode_arm(cb, wb, arm, g_rec, perm)
        pred = ctx @ W.t(); pred = pred / (pred.norm(dim=1, keepdim=True) + 1e-8)
        cos = pred @ cb.t()                                  # (b,VOCAB)
        cos_all[s:s + wb.shape[0]] = cos
        argmax_all[s:s + wb.shape[0]] = cos.argmax(dim=1)
    top1 = float((argmax_all == tgt_ev).float().mean())
    # target restricted to V_SUB by construction; also report recall among V_SUB-argmax for diagnosis
    vsub_t = torch.tensor(V_SUB, device=DEVICE)
    cos_vsub = cos_all[:, vsub_t]
    argmax_vsub = vsub_t[cos_vsub.argmax(dim=1)]
    top1_vsub = float((argmax_vsub == tgt_ev).float().mean())
    best_nats = float("inf")
    for t in TEMP_GRID:
        z = cos_all / t; z = z - z.max(dim=1, keepdim=True).values; ez = torch.exp(z)
        P = ez / (ez.sum(dim=1, keepdim=True) + 1e-30)
        pt = P[torch.arange(M, device=DEVICE), tgt_ev].clamp_min(1e-12)
        nats = float((-torch.log(pt)).mean())
        best_nats = min(best_nats, nats)
    distinct = float(torch.unique(argmax_all).numel()) / float(VOCAB)
    return {"top1": top1, "top1_vsub": top1_vsub, "bpc_nats": best_nats, "bpc_bits": best_nats / LN2,
            "perplexity": math.exp(best_nats), "distinct_token_rate": distinct}


# ---------------------------------------------------------------------------
# self-test (PROT-022): runs on import; blocks dispatch if any assert fails
# ---------------------------------------------------------------------------
def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0); cb = build_cb(VOCAB, 256, gen)
    # roll-bind order-sensitive
    w1 = torch.tensor([[3, 5, 9]], device=DEVICE); w2 = torch.tensor([[9, 5, 3]], device=DEVICE)
    b1 = enc_raw_win(cb, w1); b2 = enc_raw_win(cb, w2)
    assert float((b1 * b2).sum()) < 0.95, "roll-bind not order-sensitive"
    # enc_gate uniform == enc_raw
    gate_uni = enc_gate_win(cb, w1, torch.ones(3, device=DEVICE)); raw = enc_raw_win(cb, w1)
    assert float((gate_uni * raw).sum()) > 0.999, "enc_gate uniform-g != enc_raw"
    # bpc/ppl formula
    assert abs(math.exp(1.6094) - 5.0) < 0.01 and abs((math.log(5.0) / LN2) - 2.3219) < 0.01, "bpc/ppl formula"
    # content gate concentrates on the FLAGGED slot; scramble moves off
    Kt = 5; gnp = np.random.default_rng(3)
    win_np, tgt_np = gen_instances(400, Kt, gnp)
    win_t = torch.tensor(win_np, device=DEVICE)
    v_true = torch.tensor(_true_slots(win_np, Kt), device=DEVICE)
    g = content_gate(cb, win_t, GATE_TAU, None)
    conc = float((g.argmax(dim=1) == v_true).float().mean())
    gval = float(g[torch.arange(g.shape[0], device=DEVICE), v_true].mean())
    assert conc > 0.95, f"content gate did not concentrate on FLAGGED slot (argmax==v frac={conc:.3f})"
    assert gval > 0.5, f"content gate weight on true slot too low ({gval:.3f} <= 0.5)"
    perm = _derangement(Kt, 99)
    gs = content_gate(cb, win_t, GATE_TAU, perm)
    off = float((gs.argmax(dim=1) != v_true).float().mean())
    assert off > 0.90, f"scrambled gate still admits true slot too often (off-frac={off:.3f})"
    # DISCRIMINATOR-FIRES at real K (small scale): CONTENT lifts >= 0.30 over RAW; RAW/RECENCY capped ~1/(K-1)
    n_small = 512; Kd = 5
    cbs = build_cb(VOCAB, n_small, torch.Generator(device=DEVICE).manual_seed(5))
    gnp2 = np.random.default_rng(7)
    wtr, ttr = gen_instances(2000, Kd, gnp2); wev, tev = gen_instances(800, Kd, gnp2)
    wtr_t = torch.tensor(wtr, device=DEVICE); ttr_t = torch.tensor(ttr, device=DEVICE)
    wev_t = torch.tensor(wev, device=DEVICE); tev_t = torch.tensor(tev, device=DEVICE)
    g_rec, _ = learn_recency_gate(cbs, wtr_t, ttr_t, Kd, RECENCY_TAU)
    permd = _derangement(Kd, 13)
    res = {}
    for arm in ARMS:
        W = train_readout(cbs, wtr_t, ttr_t, arm, g_rec, permd)
        res[arm] = eval_arm(cbs, W, wev_t, tev_t, arm, g_rec, permd)["top1"]
    cap = 1.0 / (Kd - 1)   # 0.25
    assert res["RAW"] <= cap + 0.15, f"RAW not capped near 1/(K-1)={cap:.3f}: got {res['RAW']:.3f}"
    assert res["RECENCY_GATE"] <= cap + 0.15, f"RECENCY not capped: got {res['RECENCY_GATE']:.3f}"
    assert res["CONTENT_GATE"] >= 0.60, f"CONTENT_GATE did not lift at small scale: got {res['CONTENT_GATE']:.3f}"
    assert res["CONTENT_GATE"] - res["RAW"] >= 0.30, \
        f"CONTENT-RAW lift < 0.30 at small scale: {res['CONTENT_GATE']:.3f}-{res['RAW']:.3f}"
    assert res["CONTENT_GATE"] - res["CONTENT_GATE_SCRAMBLED"] >= 0.25, \
        f"scramble separation < 0.25: {res['CONTENT_GATE']:.3f}-{res['CONTENT_GATE_SCRAMBLED']:.3f}"
    assert N == 8192
    print(f"[selftest] PASS: rollbind gate_uniform==raw bpc content_concentrates(conc={conc:.2f},g={gval:.2f}) "
          f"scramble_off({off:.2f}) discrim@K{Kd}[RAW={res['RAW']:.2f} REC={res['RECENCY_GATE']:.2f} "
          f"CONT={res['CONTENT_GATE']:.2f} SCR={res['CONTENT_GATE_SCRAMBLED']:.2f} cap={cap:.2f}] N8192", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, n_dim: int, out_dir) -> Dict:
    gen_np = np.random.default_rng(seed + 99)
    cb = build_cb(VOCAB, n_dim, torch.Generator(device=DEVICE).manual_seed(seed))
    per_unit = []; gate_log = {}; unit_i = 0; t_seed = time.time()
    for K in K_GRID:
        win_tr_np, tgt_tr_np = gen_instances(M_TRAIN, K, gen_np)
        win_ev_np, tgt_ev_np = gen_instances(M_EVAL, K, gen_np)
        win_tr = torch.tensor(win_tr_np, device=DEVICE); tgt_tr = torch.tensor(tgt_tr_np, device=DEVICE)
        win_ev = torch.tensor(win_ev_np, device=DEVICE); tgt_ev = torch.tensor(tgt_ev_np, device=DEVICE)
        g_rec, r_rec = learn_recency_gate(cb, win_tr, tgt_tr, K, RECENCY_TAU)
        perm = _derangement(K, seed * 17 + K)
        gate_log["K%d" % K] = {"recency_gate": [round(float(x), 4) for x in g_rec.tolist()],
                               "recency_relevance": [round(float(x), 4) for x in r_rec.tolist()],
                               "scramble_perm": [int(x) for x in perm.tolist()],
                               "chance": round(1.0 / len(V_SUB), 4), "content_blind_cap": round(1.0 / (K - 1), 4)}
        print(f"    [gate K={K}] recency_g={[round(float(x),3) for x in g_rec.tolist()]} "
              f"cap=1/(K-1)={1.0/(K-1):.3f} perm={perm.tolist()}", flush=True)
        for arm in ARMS:
            W = train_readout(cb, win_tr, tgt_tr, arm, g_rec, perm)
            m = eval_arm(cb, W, win_ev, tgt_ev, arm, g_rec, perm)
            m.update({"seed": seed, "arm": arm, "K": K, "N": n_dim})
            per_unit.append(m); unit_i += 1
            emit_heartbeat(out_dir, unit_idx=unit_i, elapsed_s=time.time() - t_seed,
                           total_units=len(ARMS) * len(K_GRID),
                           extra={"seed": seed, "arm": arm, "K": K, "top1": round(m["top1"], 3)})
            print(f"    [{arm} K={K}] top1={m['top1']:.3f} top1_vsub={m['top1_vsub']:.3f} "
                  f"bpc_bits={m['bpc_bits']:.3f} distinct={m['distinct_token_rate']:.2f}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    return {"seed": seed, "N": n_dim, "per_unit": per_unit, "gate_log": gate_log,
            "peak_gpu_gb": float(peak), "elapsed_s": 0.0}


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _arm_curve(all_results, arm, field="top1"):
    out = {}
    for K in K_GRID:
        vals = [u[field] for r in all_results for u in r["per_unit"] if u["arm"] == arm and u["K"] == K]
        out[K] = float(np.mean(vals)) if vals else float("nan")
    return out


def compute_verdict(all_results) -> Tuple[str, str]:
    if not all_results:
        return ("HARD_FAIL", "no results")
    n_units = sum(len(r["per_unit"]) for r in all_results)
    if n_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: got {n_units} units, expected {EXPECTED_N_UNITS}")
    cur = {arm: _arm_curve(all_results, arm) for arm in ARMS}
    Kh = HEADLINE_K
    raw = cur["RAW"][Kh]; rec = cur["RECENCY_GATE"][Kh]
    con = cur["CONTENT_GATE"][Kh]; scr = cur["CONTENT_GATE_SCRAMBLED"][Kh]
    cap = 1.0 / (Kh - 1); chance = 1.0 / len(V_SUB)
    lift_rec = con - rec; lift_raw = con - raw; sep = con - scr
    curstr = " ".join(f"{a}={ {k: round(v,3) for k,v in cur[a].items()} }" for a in ARMS)
    summary = (f"@K{Kh}: RAW={raw:.3f} RECENCY={rec:.3f} CONTENT={con:.3f} SCRAMBLE={scr:.3f} | "
               f"cap=1/(K-1)={cap:.3f} chance=1/|Vsub|={chance:.3f} | lift_vs_recency={lift_rec:+.3f} "
               f"lift_vs_raw={lift_raw:+.3f} scramble_sep={sep:+.3f} | curves: {curstr}")

    # VALID-ONLY-IF: corpus must force content-selection (content-blind arms capped). Saturation-vacuous inverse.
    if raw > 0.50 or rec > 0.50:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_CORPUS_DOES_NOT_DISCRIMINATE: a content-blind arm exceeds 0.50 "
                f"(RAW={raw:.3f} RECENCY={rec:.3f}) -- the readout solves the task WITHOUT content-selection, so "
                f"the corpus does not isolate content-vs-recency. Re-spec (tighter distractors / larger K). {summary}")
    # readout-health: content-blind arms should be near the 1/(K-1) cap, not at chance (readout dead)
    if raw < chance * 1.5 and rec < chance * 1.5:
        return ("INCONCLUSIVE", f"INCONCLUSIVE_READOUT_AT_CHANCE: content-blind arms near chance ({chance:.3f}) "
                f"(RAW={raw:.3f} RECENCY={rec:.3f}); the Hebbian readout itself failed, not a gating result. {summary}")

    # HARD_PASS (HP_SCOPE: CONTENT_GATE only)
    if con >= 0.70 and rec <= 0.30 and sep >= 0.30:
        return ("HARD_PASS", f"HARD_PASS[CONTENT_GATE]: content-addressed (query-key) admission gate exceeds the "
                f"1/(K-1) content-blind cap -- CONTENT={con:.3f}>=0.70, RECENCY={rec:.3f}<=0.30 (near analytic "
                f"cap={cap:.3f}), scramble_sep={sep:.3f}>=0.30. Content-dependent gating is the lever; recency "
                f"provably fails when the informative slot's position is uniform. {summary}")

    # MIDDLE_BAND
    if lift_rec >= 0.15 or (0.0 < sep < 0.30):
        return ("MIDDLE_BAND", f"MIDDLE_BAND[CONTENT_GATE]: content gate lifts over recency (lift={lift_rec:+.3f}) "
                f"but misses full HARD_PASS (need CONTENT>=0.70 [{con:.3f}], RECENCY<=0.30 [{rec:.3f}], "
                f"scramble_sep>=0.30 [{sep:+.3f}]). Real but partial content-selection. {summary}")

    # HARD_FAIL
    return ("HARD_FAIL", f"HARD_FAIL: content gate gives no real lift over the fixed-index recency gate "
            f"(lift_vs_recency={lift_rec:+.3f}<0.15) OR scramble replicates (sep={sep:+.3f}). The query-key "
            f"primitive did not transfer to temporal-slot selection on this corpus. {summary}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} dev={DEVICE.type} seeds={SEEDS} N={N_DIM} "
          f"K_GRID={K_GRID} headline_K={HEADLINE_K} arms={ARMS} V_SUB={len(V_SUB)} FLAG={FLAG_ID} "
          f"M_TRAIN={M_TRAIN} M_EVAL={M_EVAL} GATE_TAU={GATE_TAU} expected_units={EXPECTED_N_UNITS}", flush=True)
    if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")
    if RUN_MODE == "full" and DEVICE.type != "cuda":
        raise RuntimeError("FULL must run on cuda")
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "arms": ARMS,
                                                                  "K_GRID": K_GRID, "headline_K": HEADLINE_K,
                                                                  "v_sub": len(V_SUB), "gate_tau": GATE_TAU})
    for seed in remaining:
        print(f"[seed={seed}] ...", flush=True); t0 = time.time()
        r = run_seed(seed, N_DIM, out_dir); r["elapsed_s"] = time.time() - t0
        print(f"  seed={seed} done ({r['elapsed_s']:.0f}s)", flush=True)
        write_partial(out_dir, seed, r)
    all_results = list(aggregate_partials(out_dir, SEEDS).values())
    # ARMS-MUST-DIFFER (META_RULE_AF): the 4 top1 K-curves must not be bit-identical
    import hashlib
    digs = {}
    for arm in ARMS:
        c = _arm_curve(all_results, arm)
        digs[arm] = hashlib.sha256(json.dumps({k: round(v, 6) for k, v in c.items()}).encode()).hexdigest()
    for a in ARMS:
        for b2 in ARMS:
            if a < b2:
                assert digs[a] != digs[b2], f"META_RULE_AF VIOLATION: arms {a} and {b2} bit-identical curves"
    verdict, vmsg = compute_verdict(all_results)
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    peak = (torch.cuda.max_memory_allocated(0) / 1e9) if DEVICE.type == "cuda" else 0.0
    if DEVICE.type == "cuda":
        print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
    metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM,
               "run_mode": RUN_MODE, "device": DEVICE.type, "n_seeds": len(SEEDS), "headline_K": HEADLINE_K,
               "v_sub": len(V_SUB), "flag_id": FLAG_ID, "gate_tau": GATE_TAU,
               "expected_n_units": EXPECTED_N_UNITS, "arm_digests": digs, "per_seed": all_results,
               "curves": {arm: _arm_curve(all_results, arm) for arm in ARMS},
               "curves_bpc": {arm: _arm_curve(all_results, arm, "bpc_bits") for arm in ARMS}}
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
