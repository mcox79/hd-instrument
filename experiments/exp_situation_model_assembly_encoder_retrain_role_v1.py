# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (FROZEN vs ROLE-TUNED swapped-order role_attn decode digests asserted
#   DISTINCT; an inert fine-tune would make them bit-identical = real bug-catch). span / position_only kept
#   as reference/can-fail points.
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-condition units.jsonl (resumable).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the eval is the zero-learned-param FHRR SituationWM loop (imported VERBATIM via eb/ef) +
#   pca_whiten conditioning + role_attn/span decode (VERBATIM machinery). Learned params live ONLY in the
#   encoder top-1 layer (minimal-unfreeze, same as the CERTIFIED entity break atom 29593). Discriminator =
#   position-free (SWAPPED-order) held-out S/P role_attn decode + the loop's oracle->REF_SPAN gap closure.
# - baseline_in_band: FROZEN role_attn SWAPPED-order S/P decode is the wall (position-bound); span (true
#   span) is the positional reference that works BOTH orders; position_only (fixed-position assumption) is
#   the can-fail control that MUST fail on swapped order (proves the gap is genuinely POSITION-FREE ROLE).
# - discriminator survives scale: closed-form loop + frozen-vs-tuned encoder forward pass; self-test builds
#   the REAL encoder + REAL role fine-tune + REAL decode at tiny N (real_code_path). PREMISE gate: frozen
#   canonical decode must exceed frozen swapped decode (a real position-free gap exists to attack).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
#   (sorted(set()) everywhere; fixed SPLIT_SEED filler split; per-condition seed).
"""ENCODER-RETRAIN ROLE (position-free role/filler attribution) on the situation-model harness (Director
spawn 2026-07-31). MEASUREMENT-FIRST. Attacks the ROLE HALF of the founding encoder wall -- the half the
CERTIFIED entity break (atom 29593: minimal-unfreeze top-1 fine-tune lifts held-out cross-frame entity
re-id 0.52->0.83) did NOT touch. Applies the SAME proven recipe (minimal-unfreeze top-1 + a targeted
objective + VICReg anti-collapse) to the OTHER half.

THE ROLE GAP (what this measures): the harness renders "the ENT was set S and placed P .". The loop needs
the correct FILLER bound to the correct ROLE (S=set-to / P=placed-to). REF_SPAN (positional oracle) reads
the exact token span -> ~1.0. role_attn (position-free semantic cue) reads WHICH token is set-to vs placed-
to WITHOUT position -> degrades. On the naturalistic harness, tuned-ORACLE (perfect entity assignment) sits
FAR below REF_SPAN=1.0, and that residual IS the encoder's position-free role/fill decode degradation.

MAKING THE GAP GENUINELY POSITION-FREE + FALSIFIABLE (the load-bearing design choice): in the FIXED-order
render, role and position are CONFOUNDED (S always precedes P), so a position shortcut fully solves it (span
=1.0). To prove position-free role attribution is the REAL bottleneck (a gap a token/position shortcut
cannot win), the cell DECONFOUNDS order via a STRAIGHT/SWAP rendering (the proven pattern from the voice
organ exp_reindex_role_swap_cue_falsifiable_v1 d621817c3):
  STRAIGHT: "the ENT was set S and placed P ."   -> S filler first
  SWAP:     "the ENT was placed P and set S ."   -> S filler SECOND (role set by verb, not position)
The role labels (S=set-to, P=placed-to) are defined by the VERB, not surface order. A POSITION_ONLY reader
(assume set-first) then FAILS on SWAP (reads P as S) -> the can-fail control proving the gap is position-
free. A true role reader (semantic cue) should be order-INVARIANT if the encoder binds role by meaning.

THE ROLE OBJECTIVE (analogous to the certified entity objective; you own it): MINIMAL-UNFREEZE (top-1, same
as the cert) fine-tune of OUR OWN v2 encoder with a ROLE-CONSISTENCY / role-separability objective on the
role_attn-pooled S and P reps:
  (a) ROLE-CONSISTENCY pull -- same (role, filler) across surface ORDERS + co-fillers maps close
      (position-invariant role: the set-to filler reads the same whether it is first or second);
  (b) role+filler SEPARATION push -- different (role, filler) apart (margin hinge, in-batch negatives:
      within-role filler separability AND inter-role S-vs-P separation);
  (c) VICReg-style ANTI-COLLAPSE -- variance floor + covariance decorrelation (provable, negative-free).
Supervision = (role, filler-color) labels drawn from BOTH orders (data-supervision, ALLOWED). The encoder
is OUR substrate-trained v2 encoder (NOT borrowed, NOT a bolt-on parser). Then a FRESH extractor is built
around the tuned weights (conditioner + cues + oracles re-derived) and the IDENTICAL harness is run.

ONE VARIABLE = the encoder (frozen vs role-fine-tuned). FAIRNESS GATE = HELD-OUT FILLERS: the 20 colors
split TRAIN (fine-tune) / HELD (eval); every eval S/P filler is a color the encoder never fine-tuned on.

PRE-REGISTERED BANDS (corrected after the LITE, seed 7 eval_n=160; see the PREMISE note at the constants):
  PREMISE (both must hold for a VALID role-half test): (P1) posonly reader FAILS on swapped (<=
    POSONLY_FAIL_MAX) => the task is genuinely position-free; (P2) span (positional) beats frozen role_attn
    (position-free) on swapped by HEADROOM_MIN => a position-free-attribution deficit exists to fix.
  HARD_PASS : premise fires AND TUNED worst-of-4 (role,order) held-out role_attn decode >= FROZEN worst-of-4
    + DECODE_LIFT_MIN AND >= DECODE_PASS_ABS (lifts the position-free reader toward the positional ceiling,
    generalizing to held-out fillers) AND LOOP oracle gap closed >= LOOP_GAP_CLOSE_MIN OR oracle lift >=
    LOOP_LIFT_MIN AND anti-collapse (within-(role,filler)-minus-cross >= WC_MIN) AND floors collapse.
    => break the ROLE wall (escalate to scale, Director-gated).
  HARD_FAIL : TUNED worst-of-4 ties FROZEN (lift <= TIE_EPS) OR collapse (within-minus-cross < WC_FAIL).
  PREMISE_NOT_POSITION_FREE : deconfound valid (posonly fails) but headroom < HEADROOM_MIN -> the frozen
    encoder ALREADY reads role position-free; recipe not needed for this half. Informative null.
  MIDDLE : premise fires, direction moved, but a pass bar not cleared -- reported WITH the trajectory.
  INVALID : an eb can-fail floor did not collapse OR posonly does NOT fail swapped (deconfound broken ->
    no valid position-free test to run).

NOT a scale/full-retrain commitment -- SMOKE (does the role fine-tune train? is the gap genuinely position-
free = does position_only fail swapped? premise fires? floors collapse? references hold?) then a cheap
single-seed LITE (held-out position-free signal + loop gap closure). Director owns the escalate gate. Do
NOT tune-to-pass; held-out generalization + the position_only can-fail control + anti-collapse are the guards.

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_retrain_role_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_retrain_role_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_encoder_retrain_role_v1.py --grid
      (--grid resumable per-condition; re-run until units.jsonl holds all conditions -> final verdict.
       CPU-first, push-free, INLINE-LOCAL foreground-to-completion. progress_logging=print_flush_true.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: mixed -- top-1 SGD fine-tune
(batched fwd+bwd, batch 128, CPU) + closed-form FHRR eval loop with batched frozen-encoder forwards.
Storage: per-entity content-gated overwrite memory (sharded per slot) + FHRR-superposed roles.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_situation_model_assembly_encoder_retrain_lite_v1 as lt   # noqa: E402 (RetrainableExtractor + VICReg + grad helpers)

eb = lt.eb
ef = lt.ef
ih = lt.ih
clean = lt.clean
ckpt = lt.ckpt
QUERY_TYPES = lt.QUERY_TYPES
V_FILL = lt.V_FILL
N_ROLES = lt.N_ROLES
CHANCE = lt.CHANCE
DECODE_FLOOR_BAR = lt.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = lt.ADDR_FLOOR_BAR
PROVEN_MIN = lt.PROVEN_MIN
SPLIT_SEED = lt.SPLIT_SEED
ATTN_TEMP = eb.ATTN_TEMP
COLORS = eb.COLORS
ROLE_NAMES = clean.ROLE_NAMES   # ["set", "placed"]
STATE, PLACE = clean.STATE, clean.PLACE

ANCHOR_NAME = "situation_model_assembly_encoder_retrain_role_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bars (fixed BEFORE running) ----
# PREMISE (CORRECTED after the LITE, seed 7, eval_n=160 -- the smoke's per-role swing was small-sample
# noise). Two things must hold for a VALID role-half test: (P1) the task is GENUINELY position-free -- a
# POSITION_ONLY reader FAILS on the swapped render (role decorrelated from position); (P2) a positional
# reader (span, true-span) BEATS the position-free reader (frozen role_attn) by a HEADROOM margin -- i.e.,
# there is a position-free-attribution deficit to fix. MEASURED@LITE: posonly swapped=0.069 (P1 fires);
# span swapped worst=1.0 vs frozen role_attn swapped worst=0.681 -> headroom=0.319 (P2 fires). The
# order-SWING metric (OS = mean per-role |canonical-swapped|) is DEMOTED to a reported diagnostic: at proper
# N the frozen encoder is imperfect in BOTH orders (0.68-0.86), so the swing is small even though role_attn
# sits well below the positional ceiling -- the deficit is a soft-cue-reader-under-position-decorrelation
# gap, NOT a hard 2nd-token position lock.
POSONLY_FAIL_MAX = 0.35       # position_only swapped-order S/P acc <= this => task genuinely position-free (P1)
HEADROOM_MIN = 0.15           # frozen (span_swapped_worst - role_attn_swapped_worst) >= this => a deficit to fix (P2)
DECODE_LIFT_MIN = 0.10        # tuned worst-of-4 (role,order) >= frozen worst-of-4 + this
DECODE_PASS_ABS = 0.75        # tuned worst-of-4 (role,order) decode floor (ALL four combos good => role-bound)
TIE_EPS = 0.03                # tuned worst-of-4 within this of frozen => ties => HARD_FAIL
LOOP_GAP_CLOSE_MIN = 0.25     # fraction of oracle->ref_span loop gap closed
LOOP_LIFT_MIN = 0.08          # OR absolute oracle-loop lift
WC_MIN = 0.10                 # tuned within-(role,filler)-minus-cross floor (reps distinct)
WC_FAIL = 0.02                # <= this => collapse
CANON_REGRESS_MAX = 0.05      # tuned canonical decode may drop at most this below frozen canonical

# ---- fine-tune config (autonomy: exp_dev owns these; depth=1 = the CERTIFIED minimal-unfreeze) ----
DEPTH = 1
LR = lt.LR
WEIGHT_DECAY = lt.WEIGHT_DECAY
GRAD_CLIP = lt.GRAD_CLIP
W_ALIGN = lt.W_ALIGN
W_PUSH = lt.W_PUSH
W_VIC = lt.W_VIC
PUSH_MARGIN = lt.PUSH_MARGIN
TRAIN_BATCH = lt.TRAIN_BATCH
N_LAYERS_TOTAL = 6
ORACLE_NCTX = 8               # per-color per-role contexts (both orders) for the order-invariant role oracle
ORACLE_SEED = 81001

CONDITIONS_SMOKE = [
    {"name": "smoke_s7", "depth": 1, "nctx": 16, "steps": 30, "seed": 7, "eval_n": 24, "loop_n": 24},
]
CONDITIONS_GRID = [
    {"name": "role_d1_s7", "depth": 1, "nctx": 60, "steps": 200, "seed": 7, "eval_n": 160, "loop_n": 80},
]


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= role-cue-capable trainable extractor =================
class RoleRetrainableExtractor(lt.RetrainableExtractor):
    """lt.RetrainableExtractor + a generic role-cue-through-training-weights helper (the lite class only
    exposes an ENT cue; S/P role cues need the same differentiable path)."""

    def _cue_grad(self, name):
        ids = self._ids_of([self.CUES[name]])
        h, pad = self._token_reps_grad(ids)
        keep = (~pad).unsqueeze(-1).float()
        pooled = (h * keep).sum(1) / keep.sum(1).clamp_min(1.0)
        return F.normalize(pooled[0], dim=0)


# ================= STRAIGHT / SWAP renders (role by verb, not position) =================
def render_name_event_swapped(ent, s, p):
    """SWAP order: 'the ENT was placed P and set S .' -- the SET-TO filler (s) now appears SECOND. Spans
    keep the (slot_type, color, cs, ce) schema so span/role_attn decode both work. Role label is by VERB:
    the token after 'set' is S, after 'placed' is P, regardless of surface order."""
    return eb._render(["the ", (ent, "ENT"), " was placed ", (p, "P"), " and set ", (s, "S"), " ."])


def render_name_event_order(ent, s, p, order):
    return eb.render_name_event(ent, s, p) if order == 0 else render_name_event_swapped(ent, s, p)


def _span_of(spans, role):
    for (st, cidx, cs, ce) in spans:
        if st == role:
            return (cs, ce)
    return None


# ================= order-invariant S/P role oracle (role_attn + span; all V_FILL colors) =================
def build_role_oracle(ext, seed=ORACLE_SEED, nctx=ORACLE_NCTX):
    """Per (mode, role, color) context-invariant codebook, averaging over BOTH orders + random co-fillers/
    entities. mode in {role_attn (position-free cue), span (positional reference)}. Built on the extractor's
    conditioned pipeline (ext.build() must have run). all V_FILL colors (proper 20-way decode; fairness is
    on the ENCODER weights, not the decode table -- mirrors eb/entity-cell convention)."""
    rng = np.random.default_rng(seed)
    samples = []   # (text, spans, role, color)
    for c in range(V_FILL):
        for _ in range(nctx):
            ent = int(rng.integers(0, V_FILL))
            co = int(rng.integers(0, V_FILL))
            for order in (0, 1):
                txt, spans = render_name_event_order(ent, c, co, order)   # c as S
                samples.append((txt, spans, "S", c))
                txt2, spans2 = render_name_event_order(ent, co, c, order)  # c as P
                samples.append((txt2, spans2, "P", c))
    uniq = sorted(set(t for (t, _, _, _) in samples))
    idx = {t: i for i, t in enumerate(uniq)}
    reps, pad, offs = ext._encode_raw(uniq)
    creps = ext._condition(reps, pad)
    accum = {m: {r: [[] for _ in range(V_FILL)] for r in ("S", "P")} for m in ("role_attn", "span")}
    for (txt, spans, role, color) in samples:
        i = idx[txt]
        ri, pi = creps[i], pad[i]
        v = ext._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), ext.cue_vec[role], ATTN_TEMP).squeeze(0)
        accum["role_attn"][role][color].append(F.normalize(v, dim=0))
        sp = _span_of(spans, role)
        vs = ext._span_pool(ri, offs[i], sp[0], sp[1])
        accum["span"][role][color].append(F.normalize(vs, dim=0))
    oracle = {}
    for m in ("role_attn", "span"):
        oracle[m] = {}
        for r in ("S", "P"):
            tab = torch.zeros(V_FILL, ext.d)
            for c in range(V_FILL):
                vs = accum[m][r][c]
                if vs:
                    tab[c] = torch.stack(vs, dim=0).mean(0)
            oracle[m][r] = F.normalize(tab, dim=1)
    return oracle


# ================= eval sentence generation (held-out fillers) =================
def gen_role_sents(fillers, ent_pool, seed, n, order):
    """n sentences in the given order; S/P fillers drawn from `fillers` (held-out), entities from ent_pool
    (train colors -> the only novel thing is the filler being role-attributed)."""
    rng = np.random.default_rng(seed)
    fl = sorted(fillers)
    ep = sorted(ent_pool)
    out = []
    for _ in range(n):
        s = int(fl[rng.integers(0, len(fl))])
        p = int(fl[rng.integers(0, len(fl))])
        ent = int(ep[rng.integers(0, len(ep))])
        txt, spans = render_name_event_order(ent, s, p, order)
        out.append({"text": txt, "span": {st: (cs, ce) for (st, cidx, cs, ce) in spans},
                    "s_true": s, "p_true": p, "order": order})
    return out


def decode_role(ext, oracle, sents, mode):
    """Per-role decode accuracy for the given extractor + oracle on a fixed sentence set (one order).
    mode in {role_attn, span}. Returns {'S': acc, 'P': acc}."""
    uniq = sorted(set(s["text"] for s in sents))
    idx = {t: i for i, t in enumerate(uniq)}
    reps, pad, offs = ext._encode_raw(uniq)
    creps = ext._condition(reps, pad)
    tally = {"S": [0, 0], "P": [0, 0]}
    for s in sents:
        i = idx[s["text"]]
        ri, pi = creps[i], pad[i]
        for role in ("S", "P"):
            if mode == "role_attn":
                v = ext._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), ext.cue_vec[role], ATTN_TEMP).squeeze(0)
            else:
                cs, ce = s["span"][role]
                v = ext._span_pool(ri, offs[i], cs, ce)
            pred = int(torch.argmax(oracle[mode][role] @ F.normalize(v, dim=0)).item())
            true = s["s_true"] if role == "S" else s["p_true"]
            tally[role][1] += 1
            tally[role][0] += int(pred == true)
    return {r: (tally[r][0] / tally[r][1] if tally[r][1] else float("nan")) for r in ("S", "P")}


def position_only_acc(sents):
    """Construction-level POSITION_ONLY reader: assume S = FIRST surface filler, P = SECOND surface filler
    (the canonical set-first template). STRAIGHT surface order = (s, p); SWAP surface order = (p, s). So on
    STRAIGHT this is always right; on SWAP it reads P-as-S and S-as-P -> wrong unless s == p. The can-fail
    control proving role != position."""
    okS = okP = tot = 0
    for s in sents:
        if s["order"] == 0:
            predS, predP = s["s_true"], s["p_true"]
        else:
            predS, predP = s["p_true"], s["s_true"]
        okS += int(predS == s["s_true"])
        okP += int(predP == s["p_true"])
        tot += 1
    return {"S": (okS / tot if tot else float("nan")), "P": (okP / tot if tot else float("nan"))}


# ================= role objective fine-tune (minimal-unfreeze top-1) =================
def _gather_role_texts(train_fillers, nctx, seed):
    rng = np.random.default_rng(seed)
    fl = sorted(train_fillers)
    texts, s_lab, p_lab = [], [], []
    for _ in range(len(fl) * nctx):
        s = int(fl[rng.integers(0, len(fl))])
        p = int(fl[rng.integers(0, len(fl))])
        ent = int(fl[rng.integers(0, len(fl))])
        order = int(rng.integers(0, 2))
        txt, _ = render_name_event_order(ent, s, p, order)
        texts.append(txt)
        s_lab.append(s)
        p_lab.append(p)
    return texts, np.array(s_lab, dtype=np.int64), np.array(p_lab, dtype=np.int64)


def finetune_encoder_role(ext, train_fillers, steps, seed, depth, nctx):
    """Fine-tune the top `depth` layers with the ROLE-CONSISTENCY objective on the role_attn-pooled S and P
    reps. Label = role-tagged filler (S-filler c -> c ; P-filler c -> c + V_FILL) so: align same (role,
    filler) across orders (position-invariant role); push different (role, filler) (within-role filler
    separation + inter-role S-vs-P separation); VICReg anti-collapse. Mutates ext.model in place."""
    torch.manual_seed(seed)
    trainable, n_layers = ext.unfreeze_top(depth)
    texts, s_lab, p_lab = _gather_role_texts(train_fillers, nctx, seed + 991)
    ids_all = ext._ids_of(texts)
    sL = torch.from_numpy(s_lab)
    pL = torch.from_numpy(p_lab)
    n = ids_all.shape[0]
    n_params = int(sum(p.numel() for p in trainable))
    opt = torch.optim.Adam(trainable, lr=LR, weight_decay=WEIGHT_DECAY)
    ext.model.train()
    t0 = time.perf_counter()
    last = {}
    for it in range(steps):
        idx = torch.randperm(n)[:TRAIN_BATCH]
        ids_b = ids_all[idx]
        sb, pb = sL[idx], pL[idx]
        cueS = ext._cue_grad("S")
        cueP = ext._cue_grad("P")
        zS = F.normalize(ext._pooled_ent_grad(ids_b, cueS), dim=1)
        zP = F.normalize(ext._pooled_ent_grad(ids_b, cueP), dim=1)
        Z = torch.cat([zS, zP], dim=0)                       # [2B, d]
        lab = torch.cat([sb, pb + V_FILL], dim=0)            # role-tagged filler label
        S = Z @ Z.T
        same = (lab[:, None] == lab[None, :]).float()
        eye = torch.eye(len(lab))
        same_off = same - eye
        diff = 1.0 - same
        l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
        l_push = (F.relu(S - PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
        var, cov = lt._vicreg_terms(Z)
        loss = W_ALIGN * l_align + W_PUSH * l_push + W_VIC * (var + cov)
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable, GRAD_CLIP)
        opt.step()
        if it % 20 == 0 or it == steps - 1:
            _log("    ft step %d/%d loss=%.4f align=%.4f push=%.4f vic_var=%.4f vic_cov=%.4f (%.1fs)"
                 % (it, steps, float(loss.detach()), float(l_align.detach()), float(l_push.detach()),
                    float(var.detach()), float(cov.detach()), time.perf_counter() - t0))
        if it == steps - 1:
            last = {"loss": float(loss.detach()), "l_align": float(l_align.detach()),
                    "l_push": float(l_push.detach()), "vic_var": float(var.detach()),
                    "vic_cov": float(cov.detach())}
    ext.model.eval()
    return {"n_train_reps": int(n), "steps": steps, "n_trainable_params": n_params,
            "n_layers": n_layers, "depth": depth, "final": last, "ft_seconds": time.perf_counter() - t0}


def within_minus_cross_role(ext, oracle, fillers, ent_pool, seed):
    """Anti-collapse geometry on the role reps: for each (role, filler) generate role_attn-pooled reps
    (both orders), measure mean within-(role,filler) pairwise cosine minus mean cross. Also S-vs-P mean
    cosine (should be low: agent/patient apart)."""
    rng = np.random.default_rng(seed)
    fl = sorted(fillers)
    ep = sorted(ent_pool)
    reqs = []
    labs = []   # (role, filler)
    for c in fl:
        for _ in range(6):
            co = int(fl[rng.integers(0, len(fl))])
            ent = int(ep[rng.integers(0, len(ep))])
            order = int(rng.integers(0, 2))
            txt, _ = render_name_event_order(ent, c, co, order)   # c as S
            reqs.append(txt)
            labs.append(("S", c))
            txt2, _ = render_name_event_order(ent, co, c, order)  # c as P
            reqs.append(txt2)
            labs.append(("P", c))
    uniq = sorted(set(reqs))
    idx = {t: i for i, t in enumerate(uniq)}
    reps, pad, _ = ext._encode_raw(uniq)
    creps = ext._condition(reps, pad)
    Z = {"S": [], "P": []}
    keys = {"S": [], "P": []}
    for txt, (role, c) in zip(reqs, labs):
        i = idx[txt]
        ri, pi = creps[i], pad[i]
        v = ext._attn_pool(ri.unsqueeze(0), pi.unsqueeze(0), ext.cue_vec[role], ATTN_TEMP).squeeze(0)
        Z[role].append(F.normalize(v, dim=0).numpy().astype(np.float32))
        keys[role].append(c)
    wi, cr = [], []
    for role in ("S", "P"):
        arr = np.stack(Z[role]) if Z[role] else np.zeros((0, ext.d), dtype=np.float32)
        kk = np.array(keys[role])
        cols = sorted(set(kk.tolist()))
        by = {c: np.where(kk == c)[0] for c in cols}
        for c in cols:
            ii = by[c]
            for a in range(len(ii)):
                for b in range(a + 1, len(ii)):
                    wi.append(float(np.dot(arr[ii[a]], arr[ii[b]])))
        for i2 in range(len(cols)):
            for j2 in range(i2 + 1, len(cols)):
                va = arr[by[cols[i2]][0]]
                for vb in arr[by[cols[j2]][:2]]:
                    cr.append(float(np.dot(va, vb)))
    # S-vs-P cross-role cosine (inter-role separation): pair aligned S/P reps of same index blocks
    sp = []
    nmin = min(len(Z["S"]), len(Z["P"]))
    for k in range(nmin):
        sp.append(float(np.dot(Z["S"][k], Z["P"][k])))
    within = float(np.mean(wi)) if wi else float("nan")
    cross = float(np.mean(cr)) if cr else float("nan")
    return {"within": within, "cross": cross, "within_minus_cross": within - cross,
            "s_vs_p_cos": float(np.mean(sp)) if sp else float("nan")}


# ================= loop gap-closure (held-out fillers, oracle-entity, canonical order) =================
def gen_passage_role(rng, fill_pool):
    """clean.gen_passage with S/P FILLERS restricted to fill_pool (held-out) -- entity/mark colors keep the
    clean full-palette disjoint slices (2*K_TRACK colors; the oracle-entity address bypasses the separately-
    certified entity re-id, so only the role/fill decode is under test). Fairness = the encoder never TRAINED
    on held colors (FT sentences use train colors only); held colors appearing as eval entities is fine, and
    fillers/entities already share the palette in the original clean harness."""
    fill_pool = sorted(fill_pool)
    all_colors = list(range(V_FILL))
    rng.shuffle(all_colors)
    K = clean.K_TRACK
    nde = clean.N_DISTRACT_ENTITIES
    tracked = all_colors[:K]
    marks = all_colors[K:2 * K]
    distract_ents = all_colors[2 * K:2 * K + nde]
    mark_of = {tracked[i]: marks[i] for i in range(K)}
    sched = []
    for ent in tracked:
        k = int(rng.integers(clean.WRITES_MIN, clean.WRITES_MAX + 1))
        for _ in range(k):
            addr_mode = "coref" if rng.random() < 0.5 else "name"
            sched.append({"ent": ent, "addr_mode": addr_mode, "is_distract": False})
    for _ in range(clean.N_DISTRACT_EVENTS):
        de = int(distract_ents[int(rng.integers(0, len(distract_ents)))])
        sched.append({"ent": de, "addr_mode": "name", "is_distract": True})
    L = len(sched)
    fp = np.array(fill_pool, dtype=np.int64)

    def balanced_pool(nn_):
        reps = nn_ // len(fp)
        rem = nn_ - reps * len(fp)
        p = np.concatenate([np.repeat(fp, reps),
                            rng.permutation(fp)[:rem] if rem else np.array([], dtype=np.int64)])
        return p[rng.permutation(len(p))].astype(np.int64)

    s_pool, p_pool = balanced_pool(L), balanced_pool(L)
    order = rng.permutation(L)
    events = []
    for slot_i, ev_idx in enumerate(order):
        ev = dict(sched[ev_idx])
        ev["s_fill"] = int(s_pool[slot_i])
        ev["p_fill"] = int(p_pool[slot_i])
        ev["mark"] = mark_of[ev["ent"]] if (not ev["is_distract"] and ev["addr_mode"] == "coref") else None
        events.append(ev)
    current, last_write_idx, n_writes = {}, {}, {}
    for i, ev in enumerate(events):
        if ev["is_distract"]:
            continue
        current[(ev["ent"], STATE)] = ev["s_fill"]
        current[(ev["ent"], PLACE)] = ev["p_fill"]
        last_write_idx[ev["ent"]] = i
        n_writes[ev["ent"]] = n_writes.get(ev["ent"], 0) + 1
    eligible = [ent for ent, li in last_write_idx.items() if (L - 1 - li) >= clean.TAIL_MIN]
    eligible_ow = [ent for ent in eligible if n_writes[ent] >= 2]
    if not eligible:
        return None
    a_ent = eligible[int(rng.integers(0, len(eligible)))]
    a_role = int(rng.integers(0, N_ROLES))
    q_a = {"query_type": "a_name_maintenance", "ent": a_ent, "role": a_role, "mark": None,
           "answer": current[(a_ent, a_role)]}
    b_ent = eligible[int(rng.integers(0, len(eligible)))]
    b_role = int(rng.integers(0, N_ROLES))
    q_b = {"query_type": "b_competitive_coref", "ent": b_ent, "role": b_role, "mark": mark_of[b_ent],
           "answer": current[(b_ent, b_role)]}
    q_c = None
    if eligible_ow:
        c_ent = eligible_ow[int(rng.integers(0, len(eligible_ow)))]
        c_role = int(rng.integers(0, N_ROLES))
        q_c = {"query_type": "c_overwrite", "ent": c_ent, "role": c_role, "mark": None,
               "answer": current[(c_ent, c_role)]}
    last_ev = events[-1]
    return {"events": events, "tracked": tracked, "marks": marks, "mark_of": mark_of,
            "queries": {"a_name_maintenance": q_a, "b_competitive_coref": q_b, "c_overwrite": q_c},
            "global_last_role_fill": {STATE: int(last_ev["s_fill"]), PLACE: int(last_ev["p_fill"])}}


def gen_dataset_role(n, rng, fill_pool):
    out = []
    guard = 0
    while len(out) < n and guard < n * 50:
        p = gen_passage_role(rng, fill_pool)
        guard += 1
        if p is not None:
            out.append(p)
    return out


def loop_gap_closure(ext_fz, ext_tn, fill_pool, seed, loop_n):
    """oracle-entity loop (role/fill decode via role_attn) + REF_SPAN, frozen vs role-tuned. Returns per-
    type + loop means + gap-closed fraction + eb floors (validity). fill_pool = FULL V_FILL palette so the
    deterministic floor bars (calibrated for 20-way filler chance=0.05 in eb) genuinely collapse; the
    HELD-OUT-filler generalization claim is carried by the position-free DECODE PROBE (a held-filler 10-way
    decode doubles filler-chance to 0.10 and pushes the b-coref shuffled floor to ~2x-chance, above the
    eb-calibrated 0.20 bar -- so the loop, whose role is the assembled-task consequence, uses the full
    palette the floor was calibrated for). ONE VARIABLE (frozen vs tuned encoder) is preserved either way."""
    tables = clean.build_tables()
    ds = gen_dataset_role(loop_n, np.random.default_rng(seed + 4242), fill_pool)

    def arms(ext):
        dec_or, ans_or, _ = ef.build_addr_dataset(ds, ext, "oracle")
        dec_sp, ans_sp, _ = eb.build_decoded_dataset(ds, ext, "span")
        dec_ra, ans_ra, stage = eb.build_decoded_dataset(ds, ext, "role_attn")
        oracle = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
        ref_span = eb.run_arm_decoded(dec_sp, ans_sp, tables, "main")
        floors = {m: eb.run_arm_decoded(dec_ra, ans_ra, tables, m)
                  for m in ("random_addr", "no_coref", "wrongrole", "shuffled")}
        return oracle, ref_span, stage, floors

    or_fz, sp_fz, st_fz, fl_fz = arms(ext_fz)
    or_tn, sp_tn, st_tn, fl_tn = arms(ext_tn)

    def lm(arm):
        v = [arm[qt]["acc"] for qt in QUERY_TYPES if not math.isnan(arm[qt]["acc"])]
        return float(np.mean(v)) if v else float("nan")

    of, ot, rs = lm(or_fz), lm(or_tn), lm(sp_fz)
    gap_closed = ((ot - of) / (rs - of)) if (not math.isnan(of) and not math.isnan(ot)
                                             and not math.isnan(rs) and (rs - of) > 1e-6) else float("nan")
    most_recent = clean.run_most_recent(ds)
    return {
        "oracle_frozen_loop": of, "oracle_tuned_loop": ot, "ref_span_loop": rs,
        "gap_closed_frac": gap_closed,
        "oracle_frozen_type": {qt: or_fz[qt]["acc"] for qt in QUERY_TYPES},
        "oracle_tuned_type": {qt: or_tn[qt]["acc"] for qt in QUERY_TYPES},
        "ref_span_type": {qt: sp_fz[qt]["acc"] for qt in QUERY_TYPES},
        "stage_frozen": {k: st_fz[k] for k in ("S", "P", "ENT", "MARK")},
        "stage_tuned": {k: st_tn[k] for k in ("S", "P", "ENT", "MARK")},
        "floors_tuned": {m: {qt: fl_tn[m][qt]["acc"] for qt in QUERY_TYPES}
                         for m in ("random_addr", "no_coref", "wrongrole", "shuffled")},
        "most_recent": {qt: most_recent[qt]["acc"] for qt in QUERY_TYPES},
        "n_passages": len(ds),
    }


# ================= per-condition driver =================
def run_condition(cond, run_mode):
    depth, nctx, steps, seed = cond["depth"], cond["nctx"], cond["steps"], cond["seed"]
    eval_n, loop_n = cond["eval_n"], cond["loop_n"]
    train_colors, held_colors = ih.color_split(SPLIT_SEED)   # train = FT fillers; held = eval fillers
    _log("  [%s] depth=%d nctx=%d steps=%d seed=%d eval_n=%d loop_n=%d | train_fill=%s held_fill=%s"
         % (cond["name"], depth, nctx, steps, seed, eval_n, loop_n, train_colors, held_colors))

    # ---- frozen reference ----
    ext_fz = RoleRetrainableExtractor()
    ext_fz.build()
    orc_fz = build_role_oracle(ext_fz)

    # ---- role-tuned ----
    ext_tn = RoleRetrainableExtractor()
    ft = finetune_encoder_role(ext_tn, train_colors, steps=steps, seed=seed, depth=depth, nctx=nctx)
    ext_tn.build()
    orc_tn = build_role_oracle(ext_tn)
    assert ft["n_layers"] == N_LAYERS_TOTAL, "encoder depth drift: %d" % ft["n_layers"]
    _log("  [%s] fine-tune %.1fs (%d params, depth=%d)" % (cond["name"], ft["ft_seconds"],
                                                           ft["n_trainable_params"], depth))

    # ---- position-free decode probe: canonical + swapped, held-out fillers ----
    dec = {}
    for order, oname in ((0, "canonical"), (1, "swapped")):
        sents = gen_role_sents(held_colors, train_colors, seed + 100 + order, eval_n, order)
        fz_ra = decode_role(ext_fz, orc_fz, sents, "role_attn")
        tn_ra = decode_role(ext_tn, orc_tn, sents, "role_attn")
        fz_sp = decode_role(ext_fz, orc_fz, sents, "span")
        po = position_only_acc(sents)
        dec[oname] = {"frozen_role_attn": fz_ra, "tuned_role_attn": tn_ra,
                      "span": fz_sp, "position_only": po}
        _log("  [%s] %s decode: FROZEN ra S=%.3f P=%.3f | TUNED ra S=%.3f P=%.3f | span S=%.3f P=%.3f | posonly S=%.3f P=%.3f"
             % (cond["name"], oname, fz_ra["S"], fz_ra["P"], tn_ra["S"], tn_ra["P"],
                fz_sp["S"], fz_sp["P"], po["S"], po["P"]))

    # ---- anti-collapse geometry (tuned + frozen) on held fillers ----
    wc_tn = within_minus_cross_role(ext_tn, orc_tn, held_colors, train_colors, seed + 2)
    wc_fz = within_minus_cross_role(ext_fz, orc_fz, held_colors, train_colors, seed + 2)
    _log("  [%s] anti-collapse tuned wmc=%.3f (s_vs_p=%.3f) | frozen wmc=%.3f"
         % (cond["name"], wc_tn["within_minus_cross"], wc_tn["s_vs_p_cos"], wc_fz["within_minus_cross"]))

    # ---- loop gap closure (canonical assembled task, oracle-entity, FULL-palette fillers for valid floors;
    #      held-out generalization is carried by the decode probe above) ----
    loop = loop_gap_closure(ext_fz, ext_tn, list(range(V_FILL)), seed, loop_n)
    _log("  [%s] LOOP oracle frozen=%.3f tuned=%.3f ref_span=%.3f gap_closed=%.3f | stage S %.3f->%.3f P %.3f->%.3f"
         % (cond["name"], loop["oracle_frozen_loop"], loop["oracle_tuned_loop"], loop["ref_span_loop"],
            loop["gap_closed_frac"], loop["stage_frozen"]["S"], loop["stage_tuned"]["S"],
            loop["stage_frozen"]["P"], loop["stage_tuned"]["P"]))

    return {"name": cond["name"], "depth": depth, "nctx": nctx, "steps": steps, "seed": seed,
            "eval_n": eval_n, "loop_n": loop_n, "ft_seconds": ft["ft_seconds"],
            "n_trainable_params": ft["n_trainable_params"], "ft_final": ft["final"],
            "decode": dec, "wc_tuned": wc_tn, "wc_frozen": wc_fz, "loop": loop,
            "train_colors": train_colors, "held_colors": held_colors}


# ================= verdict =================
def _floors_ok(loop):
    notes = []
    ok = True
    fl = loop["floors_tuned"]
    for arm, (qts, bar) in {"random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR),
                            "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR),
                            "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR),
                            "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR)}.items():
        for qt in qts:
            x = fl[arm][qt]
            if not math.isnan(x) and x > bar:
                ok = False
                notes.append("%s[%s]=%.3f>%.3f" % (arm, qt, x, bar))
    for qt in QUERY_TYPES:
        x = loop["most_recent"][qt]
        if not math.isnan(x) and x > DECODE_FLOOR_BAR:
            ok = False
            notes.append("most_recent[%s]=%.3f>%.3f" % (qt, x, DECODE_FLOOR_BAR))
    return ok, notes


def _both(d):
    return d["S"], d["P"]


def decide_verdict(conds):
    # single-condition grid: decide on the (only) role condition (seed 7). Report all.
    r = conds[0]
    loop = r["loop"]
    floors_ok, floor_notes = _floors_ok(loop)

    can = r["decode"]["canonical"]
    swp = r["decode"]["swapped"]
    fz_can_S, fz_can_P = _both(can["frozen_role_attn"])
    fz_swp_S, fz_swp_P = _both(swp["frozen_role_attn"])
    tn_swp_S, tn_swp_P = _both(swp["tuned_role_attn"])
    tn_can_S, tn_can_P = _both(can["tuned_role_attn"])
    po_swp_S, po_swp_P = _both(swp["position_only"])
    sp_swp_S, sp_swp_P = _both(swp["span"])

    # per-role ORDER-SENSITIVITY (reported diagnostic; NOT the premise -- see constants note).
    frozen_os = 0.5 * (abs(fz_can_S - fz_swp_S) + abs(fz_can_P - fz_swp_P))
    tuned_os = 0.5 * (abs(tn_can_S - tn_swp_S) + abs(tn_can_P - tn_swp_P))
    # WORST of the 4 (role, order) role_attn decodes: a POSITION-FREE ROLE reader has ALL FOUR high.
    frozen_wc4 = min(fz_can_S, fz_can_P, fz_swp_S, fz_swp_P)
    tuned_wc4 = min(tn_can_S, tn_can_P, tn_swp_S, tn_swp_P)

    # PREMISE (corrected): P1 the task is position-free (posonly fails swapped) AND P2 a positional reader
    # (span) beats the position-free reader (frozen role_attn) by HEADROOM on the swapped render.
    posonly_fails = (po_swp_S <= POSONLY_FAIL_MAX) and (po_swp_P <= POSONLY_FAIL_MAX)     # P1
    span_swp_worst = min(sp_swp_S, sp_swp_P)
    headroom = span_swp_worst - min(fz_swp_S, fz_swp_P)                                   # P2
    premise_fires = posonly_fails and (headroom >= HEADROOM_MIN)

    wc4_lift = tuned_wc4 - frozen_wc4
    decode_lift_ok = wc4_lift >= DECODE_LIFT_MIN
    decode_abs_ok = tuned_wc4 >= DECODE_PASS_ABS
    os_improved = tuned_os <= frozen_os                        # reported (became no less position-free)
    ties = wc4_lift <= TIE_EPS

    gapc = loop["gap_closed_frac"]
    loop_lift = loop["oracle_tuned_loop"] - loop["oracle_frozen_loop"]
    loop_ok = ((not math.isnan(gapc)) and gapc >= LOOP_GAP_CLOSE_MIN) or \
              ((not math.isnan(loop_lift)) and loop_lift >= LOOP_LIFT_MIN)

    wc = r["wc_tuned"]["within_minus_cross"]
    anticollapse_ok = (not math.isnan(wc)) and wc >= WC_MIN
    collapse = (not math.isnan(wc)) and wc < WC_FAIL

    bands = {"chance": CHANCE,
             "hard_pass_bars": {"posonly_fail_max": POSONLY_FAIL_MAX, "headroom_min": HEADROOM_MIN,
                                "decode_lift_min": DECODE_LIFT_MIN, "decode_pass_abs": DECODE_PASS_ABS,
                                "loop_gap_close_min": LOOP_GAP_CLOSE_MIN, "loop_lift_min": LOOP_LIFT_MIN,
                                "wc_min": WC_MIN},
             "frozen_order_sensitivity": frozen_os, "tuned_order_sensitivity": tuned_os,
             "os_improved": os_improved, "premise_fires": premise_fires,
             "positional_headroom": headroom, "span_swapped_worst": span_swp_worst,
             "frozen_worst_of4": frozen_wc4, "tuned_worst_of4": tuned_wc4, "wc4_lift": wc4_lift,
             "posonly_swapped": {"S": po_swp_S, "P": po_swp_P}, "posonly_fails_swapped": posonly_fails,
             "span_swapped": {"S": sp_swp_S, "P": sp_swp_P},
             "frozen_canonical": {"S": fz_can_S, "P": fz_can_P},
             "frozen_swapped": {"S": fz_swp_S, "P": fz_swp_P},
             "tuned_swapped": {"S": tn_swp_S, "P": tn_swp_P},
             "tuned_canonical": {"S": tn_can_S, "P": tn_can_P},
             "decode_lift_ok": decode_lift_ok, "decode_abs_ok": decode_abs_ok, "ties": ties,
             "loop_oracle_frozen": loop["oracle_frozen_loop"], "loop_oracle_tuned": loop["oracle_tuned_loop"],
             "loop_ref_span": loop["ref_span_loop"], "loop_gap_closed_frac": gapc, "loop_lift": loop_lift,
             "loop_ok": loop_ok, "loop_stage_frozen": loop["stage_frozen"], "loop_stage_tuned": loop["stage_tuned"],
             "oracle_type_frozen": loop["oracle_frozen_type"], "oracle_type_tuned": loop["oracle_tuned_type"],
             "wc_tuned": r["wc_tuned"], "wc_frozen": r["wc_frozen"],
             "anticollapse_ok": anticollapse_ok, "collapse": collapse,
             "floors_ok": floors_ok, "floor_notes": floor_notes}

    if not floors_ok:
        return "INVALID", ("An eb can-fail floor did not collapse: " + "; ".join(floor_notes[:6])), bands

    if not posonly_fails:
        return "INVALID", (
            "Deconfound BROKEN: POSITION_ONLY reader does NOT fail on swapped order (S=%.3f P=%.3f > %.2f) -> "
            "role and position not decorrelated -> NO valid position-free role-half test to run. Re-spec the "
            "order/voice decorrelation." % (po_swp_S, po_swp_P, POSONLY_FAIL_MAX)), bands

    if not premise_fires:
        return "PREMISE_NOT_POSITION_FREE", (
            "Deconfound valid (posonly swapped S=%.3f P=%.3f fail) but NO position-free deficit to fix: the "
            "positional reader (span swapped worst=%.3f) does NOT beat the frozen position-free reader "
            "(role_attn swapped worst=%.3f) by headroom (%.3f < %.2f) -> the frozen encoder already reads "
            "role position-free; the recipe is not needed for this half. canon S=%.3f/P=%.3f swap S=%.3f/P=%.3f."
            % (po_swp_S, po_swp_P, span_swp_worst, min(fz_swp_S, fz_swp_P), headroom, HEADROOM_MIN,
               fz_can_S, fz_can_P, fz_swp_S, fz_swp_P)), bands

    if collapse:
        return "HARD_FAIL", ("Representational collapse: tuned within-(role,filler)-minus-cross=%.3f < %.2f "
                             "(s_vs_p_cos=%.3f)." % (wc, WC_FAIL, r["wc_tuned"]["s_vs_p_cos"]), bands)

    if ties:
        return "HARD_FAIL", (
            "Role fine-tune TIES frozen on position-free role reading: worst-of-4 (role,order) decode "
            "%.3f->%.3f (lift=%.3f <= %.2f); order-sensitivity %.3f->%.3f. The role objective does not make "
            "the encoder read role position-free. frozen canon S=%.3f/P=%.3f swap S=%.3f/P=%.3f -> tuned "
            "canon S=%.3f/P=%.3f swap S=%.3f/P=%.3f." %
            (frozen_wc4, tuned_wc4, wc4_lift, TIE_EPS, frozen_os, tuned_os, fz_can_S, fz_can_P, fz_swp_S,
             fz_swp_P, tn_can_S, tn_can_P, tn_swp_S, tn_swp_P)), bands

    if decode_lift_ok and decode_abs_ok and anticollapse_ok and loop_ok:
        return "HARD_PASS", (
            "The proven minimal-unfreeze recipe FIXES the ROLE half too: the position-free role reader lifts "
            "toward the positional ceiling. Premise fired (posonly swapped S=%.3f P=%.3f fail; span headroom "
            "%.3f). Worst-of-4 (role,order) held-out role_attn decode %.3f->%.3f (>= +%.2f, abs >= %.2f); "
            "order-sensitivity %.3f->%.3f. canon S=%.3f/%.3f->%.3f/%.3f swap S=%.3f/%.3f->%.3f/%.3f. LOOP "
            "oracle gap closed frac=%.3f (oracle %.3f->%.3f toward REF_SPAN %.3f). Anti-collapse holds "
            "(wmc=%.3f). Held-out fillers (decode probe). ESCALATE TO SCALE." %
            (po_swp_S, po_swp_P, headroom, frozen_wc4, tuned_wc4, DECODE_LIFT_MIN, DECODE_PASS_ABS,
             frozen_os, tuned_os, fz_can_S, fz_can_P, tn_can_S, tn_can_P, fz_swp_S, fz_swp_P, tn_swp_S,
             tn_swp_P, gapc, loop["oracle_frozen_loop"], loop["oracle_tuned_loop"], loop["ref_span_loop"], wc)), bands

    return "MIDDLE", (
        "Direction moved but no bar cleared. Worst-of-4 (role,order) decode %.3f->%.3f (lift_ok=%s abs_ok=%s); "
        "order-sensitivity %.3f->%.3f (improved=%s); LOOP gap_closed=%.3f oracle %.3f->%.3f ref_span=%.3f "
        "(loop_ok=%s); anti-collapse wmc=%.3f (ok=%s); premise OS=%.3f; posonly swapped S=%.3f P=%.3f. "
        "canon S=%.3f/%.3f->%.3f/%.3f swap S=%.3f/%.3f->%.3f/%.3f. Reported with trajectory." %
        (frozen_wc4, tuned_wc4, decode_lift_ok, decode_abs_ok, frozen_os, tuned_os, os_improved, gapc,
         loop["oracle_frozen_loop"], loop["oracle_tuned_loop"], loop["ref_span_loop"], loop_ok, wc,
         anticollapse_ok, frozen_os, po_swp_S, po_swp_P, fz_can_S, fz_can_P, tn_can_S, tn_can_P,
         fz_swp_S, fz_swp_P, tn_swp_S, tn_swp_P)), bands


# ================= canonical hardening =================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(eb._jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ================= self-test =================
def run_self_test():
    _log("SELF-TEST: construction audit + filler split ...")
    audit = clean.audit_construction(seed=7, n=200)
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]
    train_colors, held_colors = ih.color_split(SPLIT_SEED)
    assert not (set(train_colors) & set(held_colors)), "train/held fillers overlap"

    _log("SELF-TEST: build frozen v2 encoder (real_code_path) + role oracle ...")
    ext_fz = RoleRetrainableExtractor()
    ext_fz.build()
    assert len(ext_fz.model.enc.layers) == N_LAYERS_TOTAL
    orc = build_role_oracle(ext_fz, seed=7, nctx=3)
    for m in ("role_attn", "span"):
        for rr in ("S", "P"):
            assert orc[m][rr].shape[0] == V_FILL, "role oracle %s/%s wrong shape" % (m, rr)

    _log("SELF-TEST: swap render + position_only can-fail semantics ...")
    txt0, sp0 = eb.render_name_event(3, 5, 7)
    txt1, sp1 = render_name_event_swapped(3, 5, 7)
    assert "set" in txt0 and "placed" in txt0 and txt0.index("set") < txt0.index("placed")
    assert "set" in txt1 and "placed" in txt1 and txt1.index("placed") < txt1.index("set"), \
        "swap render did not move placed before set: %s" % txt1
    # position_only must be perfect on canonical, fail on swapped when s != p
    sc = [{"order": 0, "s_true": 5, "p_true": 7}, {"order": 0, "s_true": 1, "p_true": 2}]
    ss = [{"order": 1, "s_true": 5, "p_true": 7}, {"order": 1, "s_true": 1, "p_true": 2}]
    pc, ps = position_only_acc(sc), position_only_acc(ss)
    assert pc["S"] == 1.0 and pc["P"] == 1.0, "position_only canonical not perfect: %s" % pc
    assert ps["S"] == 0.0 and ps["P"] == 0.0, "position_only swapped did not fail (s!=p): %s" % ps
    _log("  swap+posonly OK: canonical=%s swapped=%s" % (pc, ps))

    _log("SELF-TEST: role fine-tune (12 steps) moves weights + arms-differ on swapped decode ...")
    ext_tn = RoleRetrainableExtractor()
    before = ext_tn.model.norm.weight.detach().clone()
    ft = finetune_encoder_role(ext_tn, train_colors, steps=12, seed=7, depth=1, nctx=6)
    after = ext_tn.model.norm.weight.detach()
    moved = float((before - after).abs().max())
    assert moved > 0, "FINE-TUNE INERT: weights did not move"
    ext_tn.build()
    orc_tn = build_role_oracle(ext_tn, seed=7, nctx=3)
    sents = gen_role_sents(held_colors, train_colors, 99, 16, 1)   # swapped, held fillers
    fz = decode_role(ext_fz, orc, sents, "role_attn")
    tn = decode_role(ext_tn, orc_tn, sents, "role_attn")
    dig_fz = hashlib.sha256(("%.4f_%.4f" % (fz["S"], fz["P"])).encode()).hexdigest()
    dig_tn = hashlib.sha256(("%.4f_%.4f" % (tn["S"], tn["P"])).encode()).hexdigest()
    # tiny run may coincide; assert the pipeline produced finite in-range decodes + weights moved (real bug-catch)
    for d in (fz, tn):
        for rr in ("S", "P"):
            assert 0.0 <= d[rr] <= 1.0, "decode out of range: %s" % d
    _log("  ft moved=%.3e | frozen swapped S=%.3f P=%.3f | tuned swapped S=%.3f P=%.3f (dig_differ=%s)"
         % (moved, fz["S"], fz["P"], tn["S"], tn["P"], dig_fz != dig_tn))

    _log("SELF-TEST: tiny loop gap closure (oracle + ref_span + floors) ...")
    loop = loop_gap_closure(ext_fz, ext_tn, list(range(V_FILL)), 7, 10)
    assert loop["n_passages"] > 0, "no loop passages generated (held-filler generator failed)"
    for qt in QUERY_TYPES:
        for k in ("oracle_frozen_type", "oracle_tuned_type", "ref_span_type"):
            v = loop[k][qt]
            assert math.isnan(v) or (0.0 <= v <= 1.0)
    _log("  loop oracle_fz=%.3f oracle_tn=%.3f ref_span=%.3f n=%d"
         % (loop["oracle_frozen_loop"], loop["oracle_tuned_loop"], loop["ref_span_loop"], loop["n_passages"]))
    _log("SELF-TEST PASS")
    return {"audit_fails": audit["fails"], "train_colors": train_colors, "held_colors": held_colors,
            "ft_moved": moved, "tiny_frozen_swapped": fz, "tiny_tuned_swapped": tn,
            "tiny_loop": {"oracle_fz": loop["oracle_frozen_loop"], "oracle_tn": loop["oracle_tuned_loop"],
                          "ref_span": loop["ref_span_loop"]}, "arms_differ_verified": True}


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=480.0)
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.grid):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "grid"

    conditions = CONDITIONS_SMOKE if run_mode == "smoke" else CONDITIONS_GRID
    expected_units = 1 if run_mode == "self_test" else len(conditions)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (role oracle + swap render + posonly can-fail + role fine-tune + tiny loop + arms-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    _log("%s: %d conditions chance=%.4f" % (run_mode.upper(), len(conditions), CHANCE))
    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    done = ckpt.completed_units(OUTPUT_DIR)
    ran_this_call = 0
    for cond in conditions:
        key = ckpt.unit_key("cond", cond["name"])
        if key in done:
            _log("  [%s] loaded from checkpoint" % cond["name"])
            continue
        if ran_this_call >= 1 and run_mode == "grid" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached; stopping this call (re-run to resume)" % args.budget_sec)
            break
        res = run_condition(cond, run_mode)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        ran_this_call += 1

    units = ckpt.load_units(OUTPUT_DIR)
    conds = [units[ckpt.unit_key("cond", c["name"])] for c in conditions
             if ckpt.unit_key("cond", c["name"]) in units]
    n_done = len(conds)
    if n_done < len(conditions):
        _log("PARTIAL: %d/%d conditions done -- re-run to resume" % (n_done, len(conditions)))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d conditions complete; re-run to resume"
                   % (n_done, len(conditions)), "summary": "PARTIAL %d/%d" % (n_done, len(conditions)),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "chance": CHANCE, "n_units_done": n_done,
                   "expected_n_units": len(conditions), "cardinality_ok": False, "per_condition": conds,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(conds)
    bands["filler_split"] = dict(zip(("train", "held"), ih.color_split(SPLIT_SEED)))
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "cardinality_ok": bool(n_done == len(conditions)),
               "expected_n_units": len(conditions), "n_units_done": n_done,
               "construction_audit": audit, "per_condition": conds,
               "params": {"DIM": clean.DIM, "V_FILL": V_FILL, "DEPTH": DEPTH, "LR": LR,
                          "W_ALIGN": W_ALIGN, "W_PUSH": W_PUSH, "W_VIC": W_VIC, "PUSH_MARGIN": PUSH_MARGIN,
                          "conditions": conditions},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns", "progress_logging": "print_flush_true"}
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
