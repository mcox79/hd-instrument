"""Attractor-settling subject selection inside the VSA scaffold (envelope-push on the
TEM-on-VSA HARD_FAIL selection wall).

SCIENCE QUESTION (Director envelope-push task):
TEM-on-VSA (exp_agreement_tem_on_vsa_trained_codes_v1) localized the number-agreement wall
PRECISELY: not the codes (content generalizes; oracle-select+morph SNF ~= 0.9925), not the
scaffold, not gradient-vs-Hebbian. The wall is INPUT-DEPENDENT HIERARCHICAL SELECTION -- a
LINEAR readout over the bound superposition applies a FIXED weighting and CANNOT select a
BURIED subject (subject when NOT the first noun). SNF stuck at majority 0.6279; subject-FIRST
0.77; oracle-select+morph 0.9925 -> selection is the wall.

THE FIX (brain-faithful + glass-box): replace the LINEAR readout with the substrate's OWN
NONLINEAR, INPUT-DEPENDENT, INSPECTABLE selection = ATTRACTOR SETTLING (Hopfield-style
competitive winner-take-all over per-noun structural saliencies). Attractor settling is
glass-box (inspectable iterative dynamics); it was WRONGLY treated as excluded. Brain-check:
humans select non-first subjects via competitive/attractor cue-retrieval (Wagers, Lau &
Phillips 2009), not a linear map.

FACTORIZATION (PIVOT-compliant; which parts are build-time vs runtime):
  - SCAFFOLD (pre-given, glass-box, UNCHANGED): VSA role-filler codes. content code
    f_k = W_f @ surf_k (char-trigram, carries number morphology). role code
    r_k = tanh(W_r @ struct_k) (structural, NO number leak).
  - SELECTION (the ONE change): per-noun structural saliency s0_k = <q_subj, r_k>; an
    ITERATIVE competitive attractor settles a selection distribution alpha over noun-slots
    (soft winner-take-all, self-excitation + divisive-normalization lateral inhibition);
    number is read from the selected slot's content: n_k = <v_num, f_k>; z = sum_k alpha_k n_k.
  - BUILD/FOUNDATION-time (pivot-authorized gradient): W_f, W_r, cue q_subj, number readout
    v_num, and the attractor scalars (beta inverse-temp, rho self-excitation) are gradient-shaped
    to minimize number-prediction loss. The model is NEVER handed subj_pos -- it must DISCOVER
    that "select-the-subject-then-read-its-number" minimizes loss (weak structural supervision).
  - RUNTIME (glass-box, inspectable, NO gradient at inference): the settling loop (dot to cue,
    iterate softmax-competition with self-excitation, weighted-sum number readout). Inspectable:
    the alpha trajectory a^0..a^T is logged; argmax(alpha) vs subj_pos = selection accuracy.

ARMS (ONE variable = the SELECTION mechanism; same codes/scaffold/data/eval):
  (i)  attractor : per-noun saliency + iterative competitive attractor selection + per-slot
                   number readout. TEST ARM.
  (ii) linear    : the FAILED control (base tem arm) -- bind r_k*f_k, bundle (sum over nouns),
                   FIXED linear readout w_out. Same trained content+role maps. MUST FAIL on SNF
                   (a fixed weighting cannot select a buried subject).

FAIRNESS / DIFFICULTY:
  - NOVEL-LEXEME held-out: subject words disjoint train/test (same sha256 hash split as
    atom 29443 / base cell; majority-SNF reproduces ~0.628). Content code via SHARED surface
    map; selection via SHARED structural role map -> must generalize to NOVEL words.
  - PRIMARY EVAL SUBSET = SNF (subj_pos != 0): subject is NOT the first noun -- the hard cases
    where positional heuristics fail (first-noun/nearest/linear all <= majority on SNF).
  - STRUCTURE-SHUFFLE control: permute the structural features across nouns within each test
    example (destroy structure<->slot pairing). If attractor SNF drops >= 0.10, selection
    genuinely USES structure (not memorized content).
  - selection alpha depends ONLY on role codes r_k (structure; NO number leak) -> the ONLY way
    to get SNF number right is to STRUCTURALLY select the right noun (no label leak into alpha).
  - report-only diagnostics: selection_acc (argmax alpha == subj_pos), and a^0 (1-step attention)
    vs a^T (full settling) SNF acc = does the iterative attractor add over 1-step softmax.

BARS (pre-registered; LANDMARK if HARD_PASS):
  HARD_PASS = attractor novel-lexeme SNF >= majority_ref + 0.10 AND
              attractor SNF - linear SNF >= 0.05 AND
              attractor structure-shuffle drop >= 0.10.
  HARD_FAIL = attractor SNF <= linear SNF + 0.02 OR attractor SNF <= majority_ref + 0.02
              OR structure-shuffle drop < 0.03. (selection wall holds even with nonlinear
              glass-box settling = deep terminal finding: the wall is deeper than the readout.)
  MIDDLE    = partial (beats majority narrowly / ambiguous shuffle).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - baseline_in_band at smoke (META_RULE_AG; 0.05 < majority 0.628 < 0.95 OK)
# - discriminator survives scale (smoke fires attractor-vs-linear gap; full at full-cap)
# - HARD_PASS strictly above floor + margin (majority + 0.10)
# - crlb_n/a: classification accuracy, no per-decode Gaussian noise floor (deterministic argmax)
# - deterministic seeding: hashlib digests + fixed int seeds + sorted(set); NO builtin hash(), NO list(set())
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the design report

Build-time gradient: torch autograd (CPU). Runtime path (settling + weighted number readout) is
the inspectable VSA algebra. Local foreground; NO push, NO bank (skunkworks banks).
"""

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

try:
    import torch
except Exception:  # torch is required
    torch = None

# ---- line-buffered stdout for progress (section 17) ----
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

ANCHOR_NAME = "agreement_attractor_select_vsa_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(REPO, "data", "corpora", "agreement",
                          "agreement_word_cache_v1.json.gz")
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)

# ---- hyperparameters (owned by exp_dev) ----
N_DIM = 1024          # VSA vector dimensionality
F_SURF = 256          # char-trigram hash buckets (content channel)
N_STRUCT = 10         # structural role features (no number leak)
MAX_NN = 8            # cap nouns per example
SETTLE_T = 5          # attractor settling iterations (glass-box; runtime dynamics)
PATIENCE = 25         # early-stop patience on val-SNF (generalization guard); high enough to
                      # confirm val truly plateaus, not a premature stop restoring untrained weights
LOG_EVERY = 20        # progress cadence
FULL_SEEDS = [7, 13, 19]
SMOKE_SEEDS = [7, 13]

# ---- pre-registered bands (majority reference tagged) ----
MAJORITY_REF_SNF = 0.6279   # MEASURED@base split (matches atom 29443 majority-SNF / task 0.6269)
HP_MARGIN_OVER_MAJ = 0.10   # attractor SNF must beat majority by this
HP_MARGIN_OVER_LINEAR = 0.05  # ... AND beat linear control SNF by this
HP_SHUFFLE_DROP = 0.10      # ... AND structure-shuffle drop >= this
HF_TIE_LINEAR = 0.02        # HARD_FAIL if attractor SNF <= linear + this
HF_TIE_MAJ = 0.02           # HARD_FAIL if attractor SNF <= majority + this
HF_SHUFFLE_MIN = 0.03       # HARD_FAIL if shuffle drop < this

# ---- novel-lexeme split (identical hash to base cell / atom 29443) ----
TEST_HASH_MOD = 5
TEST_FRAC_CUT = 2


def _is_test(subj_word):
    h = int.from_bytes(hashlib.sha256(subj_word.encode("utf-8")).digest()[:8], "big")
    return (h % TEST_HASH_MOD) < TEST_FRAC_CUT


def _stable_seed(*parts):
    """Deterministic 63-bit seed from a string key via sha256 (NOT builtin hash; F.5-clean)."""
    key = "|".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") & ((1 << 63) - 1)


# ==================================================================================================
# Data loading + featurization (identical to base cell).
# ==================================================================================================
PREPS = {"of", "in", "on", "with", "by", "for", "to", "from", "at", "as", "into",
         "over", "under", "between", "among", "through", "during", "against", "about"}
DETS = {"the", "a", "an", "this", "that", "these", "those", "its", "their", "his", "her", "our"}


def load_items(max_items=None):
    with gzip.open(CACHE_PATH, "rt", encoding="utf-8") as f:
        d = json.load(f)
    items = d["linzen"]
    if max_items is not None:
        items = items[:max_items]
    return items


def surf_features(word):
    """Char-trigram hash-count features (L2-normalized). Deterministic (hashlib). Carries number
    morphology and generalizes to novel words."""
    s = "^" + word.lower() + "$"
    vec = np.zeros(F_SURF, dtype=np.float32)
    if len(s) < 3:
        grams = [s]
    else:
        grams = [s[i:i + 3] for i in range(len(s) - 2)]
    for g in grams:
        b = int.from_bytes(hashlib.md5(g.encode("utf-8")).digest()[:4], "big") % F_SURF
        vec[b] += 1.0
    nrm = np.linalg.norm(vec)
    if nrm > 0:
        vec /= nrm
    return vec


def struct_features(item, k, widx):
    """Structural role features for noun k at word index widx. NO number leak (no nums, no ndiff)."""
    words = item["words"]
    L = len(words)
    nn = len(item["noun_word_idx"])
    prev = words[widx - 1].lower() if widx - 1 >= 0 else ""
    near_and = 0.0
    for j in range(max(0, widx - 2), min(L, widx + 3)):
        if words[j].lower() in ("and", "or"):
            near_and = 1.0
            break
    denom = max(L - 1, 1)
    return np.array([
        1.0,                              # bias
        widx / denom,                     # position from start
        (L - 1 - widx) / denom,           # position from end (proxy: distance to verb)
        k / max(nn - 1, 1),               # noun order
        1.0 if k == 0 else 0.0,           # is first noun
        1.0 if k == nn - 1 else 0.0,      # is last noun
        min(nn, 8) / 8.0,                 # number of nouns
        1.0 if prev in PREPS else 0.0,    # preceded by preposition (PP-embedded -> attractor-like)
        1.0 if prev in DETS else 0.0,     # preceded by determiner
        near_and,                         # coordination nearby
    ], dtype=np.float32)


def encode_items(items, surf_cache):
    """Vectorize items into padded arrays. surf[B,NN,F], struct[B,NN,S], mask[B,NN], y[B],
    subj_pos[B], ndiff[B]."""
    B = len(items)
    surf = np.zeros((B, MAX_NN, F_SURF), dtype=np.float32)
    struct = np.zeros((B, MAX_NN, N_STRUCT), dtype=np.float32)
    mask = np.zeros((B, MAX_NN), dtype=np.float32)
    y = np.zeros(B, dtype=np.float32)
    subj_pos = np.zeros(B, dtype=np.int64)
    ndiff = np.zeros(B, dtype=np.int64)
    for bi, it in enumerate(items):
        y[bi] = float(it["label"])
        subj_pos[bi] = int(it["subj_pos"])
        ndiff[bi] = int(it["ndiff"])
        nidx = it["noun_word_idx"]
        for k in range(min(len(nidx), MAX_NN)):
            widx = nidx[k]
            w = it["words"][widx]
            if w not in surf_cache:
                surf_cache[w] = surf_features(w)
            surf[bi, k] = surf_cache[w]
            struct[bi, k] = struct_features(it, k, widx)
            mask[bi, k] = 1.0
    return {"surf": surf, "struct": struct, "mask": mask, "y": y,
            "subj_pos": subj_pos, "ndiff": ndiff}


def split_items(items, train_cap, test_cap, seed):
    rng = np.random.default_rng(seed)
    train = [r for r in items if not _is_test(r["subj_word"])]
    test = [r for r in items if _is_test(r["subj_word"])]
    rng.shuffle(train)
    rng.shuffle(test)
    return train[:train_cap], test[:test_cap]


def subject_split(items, val_frac, seed):
    """Carve a VALIDATION set from train by disjoint SUBJECT WORDS (novel-lexeme within train,
    for early stopping). Deterministic (sorted set + seeded shuffle)."""
    subjects = sorted(set(r["subj_word"] for r in items))
    rng = np.random.default_rng(_stable_seed("valsplit", seed))
    rng.shuffle(subjects)
    n_val = max(1, int(len(subjects) * val_frac))
    val_subj = set(subjects[:n_val])
    fit = [r for r in items if r["subj_word"] not in val_subj]
    val = [r for r in items if r["subj_word"] in val_subj]
    return fit, val


# ==================================================================================================
# Model. Build-time gradient (torch); runtime path = glass-box VSA algebra.
# ONE variable across arms = the SELECTION mechanism (attractor vs linear readout).
# ==================================================================================================
class AgreementModel:
    """arm in {'attractor','linear'}. Same content+role maps; differ ONLY in the readout head."""

    def __init__(self, arm, seed, device="cpu"):
        self.arm = arm
        self.device = device
        g = torch.Generator(device=device).manual_seed(seed)
        scale_f = 1.0 / np.sqrt(F_SURF)
        scale_r = 1.0 / np.sqrt(N_STRUCT)
        scale_n = 1.0 / np.sqrt(N_DIM)
        # shared: content map W_f [N,F]; role map W_r [N,S]
        self.W_f = (torch.randn(N_DIM, F_SURF, generator=g) * scale_f).requires_grad_(True)
        self.W_r = (torch.randn(N_DIM, N_STRUCT, generator=g) * scale_r).requires_grad_(True)
        if arm == "attractor":
            # scales tuned so pre-softmax saliency and per-slot number logit start O(1) (NOT
            # over-shrunk): the raw dots <q,r> and <v,f> are already O(1) because r_k~O(0.5)/comp
            # and f_k~O(0.06)/comp, so we do NOT apply an extra 1/sqrt(N) in forward (that killed
            # the signal in v0-smoke -> near-uniform alpha, z~0, no learnable selection).
            self.q_subj = (torch.randn(N_DIM, generator=g) * (2.0 / np.sqrt(N_DIM))).requires_grad_(True)  # cue
            self.v_num = (torch.randn(N_DIM, generator=g) * 0.4).requires_grad_(True)          # number readout
            self.b_num = torch.zeros(1, requires_grad=True)
            self.log_beta = torch.tensor(1.0, requires_grad=True)  # softplus -> inverse temperature
            self.log_rho = torch.tensor(0.5, requires_grad=True)   # softplus -> self-excitation
        else:  # linear (the failed control): bind r*f -> bundle -> fixed linear readout
            self.w_out = (torch.randn(N_DIM, generator=g) * scale_n).requires_grad_(True)
            self.bias = torch.zeros(1, requires_grad=True)

    def params(self):
        if self.arm == "attractor":
            return [self.W_f, self.W_r, self.q_subj, self.v_num, self.b_num,
                    self.log_beta, self.log_rho]
        return [self.W_f, self.W_r, self.w_out, self.bias]

    def _codes(self, batch, struct_override=None):
        surf = batch["surf"]
        struct = struct_override if struct_override is not None else batch["struct"]
        f = torch.matmul(surf, self.W_f.t())                    # [B,NN,N] content filler
        r = torch.tanh(torch.matmul(struct, self.W_r.t()))      # [B,NN,N] structural role
        return f, r

    def forward(self, batch, struct_override=None, settle_T=None, return_detail=False):
        """Runtime path (inspectable). linear: bind(elementwise) -> bundle(sum) -> readout(dot).
        attractor: saliency -> iterative competitive settling -> per-slot number readout."""
        mask = batch["mask"]                                    # [B,NN]
        f, r = self._codes(batch, struct_override)
        if self.arm == "linear":
            bound = (r * f) * mask.unsqueeze(-1)                # BIND (masked)
            S = bound.sum(dim=1)                                # BUNDLE
            z = torch.matmul(S, self.w_out) + self.bias         # FIXED linear readout
            return z
        # ---- attractor selection (glass-box competitive settling) ----
        T = SETTLE_T if settle_T is None else settle_T
        s0 = torch.matmul(r, self.q_subj)                       # [B,NN] structural saliency (O(1))
        neg = (1.0 - mask) * (-1e9)                             # mask invalid slots
        beta = torch.nn.functional.softplus(self.log_beta)      # inverse temperature > 0
        rho = torch.nn.functional.softplus(self.log_rho)        # self-excitation >= 0
        a = torch.softmax(beta * s0 + neg, dim=1)               # a^0 = 1-step attention
        a0 = a
        for _ in range(T):                                      # settle: self-excite + normalize
            drive = s0 + rho * a                                # winner deepens its basin
            a = torch.softmax(beta * drive + neg, dim=1)        # divisive norm = lateral inhibition
        n = torch.matmul(f, self.v_num) + self.b_num           # [B,NN] per-slot number logit (O(1))
        z = (a * n).sum(dim=1)                                  # selected-slot number
        if return_detail:
            z0 = (a0 * n).sum(dim=1)                            # 1-step-attention readout (report)
            return z, {"alpha": a, "alpha0": a0, "z0": z0}
        return z


def _snf_acc_of(model, t_batch, subj_pos, gold):
    with torch.no_grad():
        z = model.forward(t_batch)
        p = (torch.sigmoid(z) >= 0.5).numpy().astype(int)
    snf = subj_pos != 0
    return float(np.mean(p[snf] == gold[snf])) if snf.sum() else 0.0


def train_arm(arm, fit, val, te, seed, epochs, lr, batch_size, weight_decay=3e-3,
              patience=8, eval_every=2, log_every=50):
    """Build-time gradient training with L2 weight decay + validation-based early stopping
    (val = disjoint subject words carved from train). Returns eval metrics on the test split."""
    torch.manual_seed(seed)
    model = AgreementModel(arm, seed)
    opt = torch.optim.Adam(model.params(), lr=lr, weight_decay=weight_decay)
    bce = torch.nn.BCEWithLogitsLoss()

    fit_t = {k: torch.from_numpy(fit[k]) for k in ("surf", "struct", "mask")}
    fit_y = torch.from_numpy(fit["y"])
    val_t = {k: torch.from_numpy(val[k]) for k in ("surf", "struct", "mask")}
    te_t = {k: torch.from_numpy(te[k]) for k in ("surf", "struct", "mask")}

    val_gold = val["y"].astype(int)
    fit_gold = fit["y"].astype(int)
    n = fit_y.shape[0]
    idx = np.arange(n)
    best_val = -1.0
    best_state = None
    best_ep = 0
    since = 0
    for ep in range(epochs):
        rng = np.random.default_rng(_stable_seed("epoch", seed, ep))
        rng.shuffle(idx)
        tl = 0.0
        nb = 0
        for start in range(0, n, batch_size):
            sel = idx[start:start + batch_size]
            sel_t = torch.from_numpy(sel)
            batch = {k: fit_t[k][sel_t] for k in fit_t}
            z = model.forward(batch)
            loss = bce(z, fit_y[sel_t])
            opt.zero_grad()
            loss.backward()
            opt.step()
            tl += float(loss.detach())
            nb += 1
        if ep % eval_every == 0 or ep == epochs - 1:
            vacc = _snf_acc_of(model, val_t, val["subj_pos"], val_gold)
            if vacc > best_val:
                best_val = vacc
                best_state = [p.detach().clone() for p in model.params()]
                best_ep = ep
                since = 0
            else:
                since += eval_every
            if log_every and (ep % log_every == 0 or ep == epochs - 1):
                facc = _snf_acc_of(model, fit_t, fit["subj_pos"], fit_gold)
                print("[%s:%s] seed=%d ep=%d/%d fit_loss=%.4f fit_snf=%.4f val_snf=%.4f best=%.4f@%d" %
                      (ANCHOR_NAME, arm, seed, ep, epochs, tl / max(nb, 1), facc, vacc, best_val, best_ep),
                      flush=True)
            if since >= patience:
                break
    if best_state is not None:
        with torch.no_grad():
            for p, b in zip(model.params(), best_state):
                p.copy_(b)

    # ---- eval (runtime path; no grad) ----
    with torch.no_grad():
        if arm == "attractor":
            z_te, det = model.forward(te_t, return_detail=True)
            pred = (torch.sigmoid(z_te) >= 0.5).numpy().astype(int)
            pred_att0 = (torch.sigmoid(det["z0"]) >= 0.5).numpy().astype(int)
            sel_slot = det["alpha"].argmax(dim=1).numpy().astype(int)
        else:
            z_te = model.forward(te_t)
            pred = (torch.sigmoid(z_te) >= 0.5).numpy().astype(int)
            pred_att0 = None
            sel_slot = None
        # structure-shuffle: permute struct rows within each test example
        struct_sh = te["struct"].copy()
        rng = np.random.default_rng(_stable_seed("shuffle", seed))
        for bi in range(struct_sh.shape[0]):
            m = int(te["mask"][bi].sum())
            if m > 1:
                perm = rng.permutation(m)
                struct_sh[bi, :m] = struct_sh[bi, :m][perm]
        z_sh = model.forward(te_t, struct_override=torch.from_numpy(struct_sh))
        shuf_pred = (torch.sigmoid(z_sh) >= 0.5).numpy().astype(int)

    gold = te["y"].astype(int)
    snf = te["subj_pos"] != 0
    easy = ~snf
    out = {"pred": pred, "best_val_snf": round(float(best_val), 4), "best_ep": int(best_ep)}
    out["all_acc"] = float(np.mean(pred == gold))
    out["snf_acc"] = float(np.mean(pred[snf] == gold[snf])) if snf.sum() else None
    out["subj_first_acc"] = float(np.mean(pred[easy] == gold[easy])) if easy.sum() else None
    out["n_snf"] = int(snf.sum())
    out["snf_shuffle_acc"] = float(np.mean(shuf_pred[snf] == gold[snf])) if snf.sum() else None
    # attractor-only inspectable diagnostics (report-only)
    if arm == "attractor" and snf.sum():
        out["selection_acc_snf"] = float(np.mean(sel_slot[snf] == te["subj_pos"][snf]))
        out["att0_snf_acc"] = float(np.mean(pred_att0[snf] == gold[snf]))  # 1-step attention
    else:
        out["selection_acc_snf"] = None
        out["att0_snf_acc"] = None
    # per-ndiff-bin SNF acc
    bin_acc = {}
    for nd in range(5):
        m = snf & (te["ndiff"] == nd)
        bin_acc[str(nd)] = float(np.mean(pred[m] == gold[m])) if m.sum() else None
    out["snf_by_ndiff"] = bin_acc
    return out


def baselines(te):
    """Majority baseline + oracle-select+morph ceiling on the test split."""
    gold = te["y"].astype(int)
    snf = te["subj_pos"] != 0
    maj_class = int(round(float(np.mean(gold))))
    pred_maj = np.full(len(gold), maj_class, dtype=int)

    def snf_acc(p):
        return float(np.mean(p[snf] == gold[snf])) if snf.sum() else None

    return {"majority_snf": snf_acc(pred_maj), "majority_all": float(np.mean(pred_maj == gold))}


# ==================================================================================================
# Verdict.
# ==================================================================================================
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def decide_verdict(per_seed, majority_ref):
    att = _mean([s["attractor"]["snf_acc"] for s in per_seed])
    lin = _mean([s["linear"]["snf_acc"] for s in per_seed])
    att_sh = _mean([s["attractor"]["snf_shuffle_acc"] for s in per_seed])
    shuffle_drop = (att - att_sh) if (att is not None and att_sh is not None) else None

    hp = (att is not None and lin is not None and shuffle_drop is not None
          and att >= majority_ref + HP_MARGIN_OVER_MAJ
          and (att - lin) >= HP_MARGIN_OVER_LINEAR
          and shuffle_drop >= HP_SHUFFLE_DROP)
    hf = (att is None or lin is None
          or att <= lin + HF_TIE_LINEAR
          or att <= majority_ref + HF_TIE_MAJ
          or (shuffle_drop is not None and shuffle_drop < HF_SHUFFLE_MIN))
    if hp:
        verdict = "HARD_PASS"
    elif hf:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"
    return verdict, {"attractor_snf": att, "linear_snf": lin,
                     "attractor_snf_shuffle": att_sh, "shuffle_drop": shuffle_drop,
                     "majority_ref_snf": majority_ref}


# ==================================================================================================
# Orchestration.
# ==================================================================================================
def _write_start_marker(run_mode, expected_units):
    import platform
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_units, "host": platform.node()}
    tmp = os.path.join(OUTPUT_DIR, "_start_marker.json.tmp")
    final = os.path.join(OUTPUT_DIR, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic (META_RULE_AH)


def _write_crash_metrics(exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics(diag)


def _r(x):
    return round(float(x), 4) if x is not None else None


def run(run_mode):
    t0 = time.perf_counter()
    if run_mode == "smoke":
        seeds, train_cap, test_cap, epochs, bs = SMOKE_SEEDS, 1500, 1500, 120, 512
    else:  # full
        seeds, train_cap, test_cap, epochs, bs = FULL_SEEDS, 6000, 6000, 150, 512
    wd = 3e-3
    _write_start_marker(run_mode, len(seeds) * 2)

    items = load_items()
    surf_cache = {}
    per_seed = []
    for seed in seeds:
        tr_items, te_items = split_items(items, train_cap, test_cap, seed)
        assert not (set(r["subj_word"] for r in tr_items) & set(r["subj_word"] for r in te_items)), \
            "novel-lexeme split breach: subject-word overlap"
        fit_items, val_items = subject_split(tr_items, val_frac=0.2, seed=seed)
        fit = encode_items(fit_items, surf_cache)
        val = encode_items(val_items, surf_cache)
        te = encode_items(te_items, surf_cache)
        base = baselines(te)
        snf_m = te["subj_pos"] != 0
        oracle = np.array([1 if te_items[i]["words"][te_items[i]["noun_word_idx"][te_items[i]["subj_pos"]]].lower().endswith("s")
                           else 0 for i in range(len(te_items))])
        base["oracle_morph_snf"] = float(np.mean(oracle[snf_m] == te["y"].astype(int)[snf_m])) if snf_m.sum() else None
        arms = {}
        for arm in ("attractor", "linear"):
            arms[arm] = train_arm(arm, fit, val, te, seed, epochs, lr=0.01,
                                  batch_size=bs, weight_decay=wd,
                                  patience=PATIENCE, eval_every=2, log_every=LOG_EVERY)
        # arms-differ (META_RULE_AF)
        digs = {a: hashlib.sha256(arms[a]["pred"].tobytes()).hexdigest() for a in arms}
        assert len(set(digs.values())) >= 2, \
            "META_RULE_AF VIOLATION: arms bit-identical %s" % digs
        rec = {"seed": seed, "n_train": len(tr_items), "n_test": len(te_items),
               "n_snf": arms["attractor"]["n_snf"], "baselines": base,
               "arms_differ_digests": digs}
        for arm in arms:
            rec[arm] = {k: arms[arm][k] for k in
                        ("all_acc", "snf_acc", "subj_first_acc", "snf_shuffle_acc",
                         "selection_acc_snf", "att0_snf_acc", "n_snf", "snf_by_ndiff",
                         "best_val_snf")}
        per_seed.append(rec)
        print("[%s] seed=%d SNF: attractor=%.4f linear=%.4f maj=%.4f oracle=%.4f | "
              "att_shuf=%s sel_acc=%s att0(1step)=%s | attractor_easy(subj1st)=%.4f" %
              (ANCHOR_NAME, seed, arms["attractor"]["snf_acc"], arms["linear"]["snf_acc"],
               base["majority_snf"], base["oracle_morph_snf"],
               _r(arms["attractor"]["snf_shuffle_acc"]), _r(arms["attractor"]["selection_acc_snf"]),
               _r(arms["attractor"]["att0_snf_acc"]), arms["attractor"]["subj_first_acc"]),
              flush=True)

    majority_ref = MAJORITY_REF_SNF
    measured_maj = _mean([s["baselines"]["majority_snf"] for s in per_seed])
    oracle_snf = _mean([s["baselines"]["oracle_morph_snf"] for s in per_seed])
    att_easy = _mean([s["attractor"]["subj_first_acc"] for s in per_seed])
    sel_acc = _mean([s["attractor"]["selection_acc_snf"] for s in per_seed])
    att0 = _mean([s["attractor"]["att0_snf_acc"] for s in per_seed])
    verdict, agg = decide_verdict(per_seed, majority_ref)
    agg["attractor_subj_first"] = att_easy
    agg["oracle_morph_snf"] = oracle_snf
    agg["selection_acc_snf"] = sel_acc
    agg["att0_1step_snf"] = att0
    elapsed = time.perf_counter() - t0

    msg = ("Attractor-settling subject selection in VSA scaffold | novel-lexeme SNF: "
           "attractor=%s linear=%s vs majority_ref=%.4f (measured %s) | shuffle_drop=%s "
           "(att_shuf=%s) | selection_acc(argmax alpha==subj)=%s att0(1step)=%s [oracle-select+morph "
           "ceiling=%s] | attractor selects subj-FIRST=%s buried-SNF=%s | build=gradient(W_f,W_r,q_subj,"
           "v_num,beta,rho) runtime=glassbox(saliency->settle->number) | n_seeds=%d %s" %
           (_r(agg["attractor_snf"]), _r(agg["linear_snf"]), majority_ref, _r(measured_maj),
            _r(agg["shuffle_drop"]), _r(agg["attractor_snf_shuffle"]), _r(sel_acc), _r(att0),
            _r(oracle_snf), _r(att_easy), _r(agg["attractor_snf"]), len(per_seed), run_mode.upper()))

    metrics = {
        "verdict": verdict, "verdict_tag": verdict, "verdict_msg": msg,
        "summary": "%s | attractor_snf=%s vs maj=%.4f (linear=%s)" %
                   (verdict, _r(agg["attractor_snf"]), majority_ref, _r(agg["linear_snf"])),
        "elapsed_s": round(elapsed, 2), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "aggregate": {k: _r(v) for k, v in agg.items()},
        "measured_majority_snf": _r(measured_maj),
        "bands": {"MAJORITY_REF_SNF": MAJORITY_REF_SNF, "HP_MARGIN_OVER_MAJ": HP_MARGIN_OVER_MAJ,
                  "HP_MARGIN_OVER_LINEAR": HP_MARGIN_OVER_LINEAR, "HP_SHUFFLE_DROP": HP_SHUFFLE_DROP,
                  "HF_TIE_LINEAR": HF_TIE_LINEAR, "HF_TIE_MAJ": HF_TIE_MAJ,
                  "HF_SHUFFLE_MIN": HF_SHUFFLE_MIN},
        "invariant_note": ("gradient at BUILD-time (W_f content-map, W_r role-map, cue q_subj, "
                           "number readout v_num, attractor scalars beta/rho); runtime path = "
                           "saliency dot -> iterative competitive softmax settling (self-excitation "
                           "+ divisive-norm inhibition) -> per-slot number readout = inspectable VSA "
                           "algebra, no gradient at inference; alpha trajectory a^0..a^T inspectable"),
        "per_seed": per_seed,
        "config": {"N_DIM": N_DIM, "F_SURF": F_SURF, "N_STRUCT": N_STRUCT, "MAX_NN": MAX_NN,
                   "SETTLE_T": SETTLE_T, "seeds": seeds, "train_cap": train_cap,
                   "test_cap": test_cap, "epochs": epochs, "batch_size": bs},
    }
    _write_metrics(metrics)
    print("[%s] VERDICT=%s | %s" % (ANCHOR_NAME, verdict, msg), flush=True)
    return metrics


# ==================================================================================================
# Self-test: exercises the REAL code path (encode -> both arms -> verdict) at tiny scale.
# ==================================================================================================
def self_test():
    print("[%s] SELF-TEST start" % ANCHOR_NAME, flush=True)
    assert torch is not None, "torch required"
    # F.5 static scan of own source (deterministic seeding discipline)
    try:
        from experiments._validity_preflight import scan_source_for_nondeterminism
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            findings = scan_source_for_nondeterminism(f.read())
        errs = [x for x in (findings or []) if x.get("severity") == "error"]
        assert not errs, "nondeterministic seeding: %s" % errs
        print("[%s] F.5 source scan clean" % ANCHOR_NAME, flush=True)
    except ImportError:
        print("[%s] F.5 preflight module absent; relying on hashlib-only discipline" % ANCHOR_NAME, flush=True)

    items = load_items(max_items=1200)
    tr_items, te_items = split_items(items, 300, 300, 7)
    assert not (set(r["subj_word"] for r in tr_items) & set(r["subj_word"] for r in te_items)), \
        "novel-lexeme split breach in self-test"
    surf_cache = {}
    fit_items, val_items = subject_split(tr_items, val_frac=0.2, seed=7)
    fit = encode_items(fit_items, surf_cache)
    val = encode_items(val_items, surf_cache)
    te = encode_items(te_items, surf_cache)
    assert fit["surf"].shape[1:] == (MAX_NN, F_SURF)
    assert fit["struct"].shape[1:] == (MAX_NN, N_STRUCT)

    base = baselines(te)
    assert base["majority_snf"] is not None
    assert 0.05 < base["majority_snf"] < 0.95, "majority out of band (AG)"
    print("[%s] majority_snf(self-test sample)=%.4f" % (ANCHOR_NAME, base["majority_snf"]), flush=True)

    preds = {}
    for arm in ("attractor", "linear"):
        r = train_arm(arm, fit, val, te, 7, epochs=20, lr=0.02, batch_size=256,
                      weight_decay=0.0, patience=99, eval_every=1, log_every=0)
        assert r["snf_acc"] is not None and 0.0 <= r["snf_acc"] <= 1.0
        assert r["snf_shuffle_acc"] is not None, "structure-shuffle must run for %s" % arm
        preds[arm] = r["pred"]
    assert preds["attractor"].shape == preds["linear"].shape
    # arms-differ (META_RULE_AF)
    digs = {a: hashlib.sha256(preds[a].tobytes()).hexdigest() for a in preds}
    assert len(set(digs.values())) >= 2, "arms bit-identical: %s" % digs

    # runtime path is grad-free (glass-box-at-runtime invariant), both arms
    tt = {k: torch.from_numpy(te[k]) for k in ("surf", "struct", "mask")}
    for arm in ("attractor", "linear"):
        m = AgreementModel(arm, 7)
        with torch.no_grad():
            out = m.forward(tt, return_detail=(arm == "attractor"))
        z = out[0] if isinstance(out, tuple) else out
        assert z.requires_grad is False, "runtime forward must be grad-free under no_grad (%s)" % arm
        assert z.shape[0] == te["surf"].shape[0]
    # attractor alpha is a valid selection distribution (sums ~1 over valid slots)
    m = AgreementModel("attractor", 7)
    with torch.no_grad():
        _, det = m.forward(tt, return_detail=True)
    asum = det["alpha"].sum(dim=1).numpy()
    assert np.all(np.abs(asum - 1.0) < 1e-3), "alpha must be a distribution (sum=1); got %s" % asum[:5]
    print("[%s] SELF-TEST PASS (arms differ; shuffle runs; alpha is distribution; runtime grad-free)"
          % ANCHOR_NAME, flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode = "smoke" if args.smoke else "full"
    run(run_mode)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(e)
        raise
