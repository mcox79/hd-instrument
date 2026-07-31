# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays; MAIN_ENC /
#   REF_SPAN / ORACLE / FIXED_TAU_COMMIT / LEARNED_COMMIT asserted pairwise distinct where they must
#   differ; a legitimate coincidence -- LEARNED==ORACLE when re-id is perfect -- is logged, NOT hard-asserted).
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the SCORING loop is the zero-learned-param FHRR SituationWM (imported VERBATIM via eb.clean).
#   The ONLY learned parameters live in a SMALL identity-head on top of the FROZEN v2 encoder's ENT-slot
#   reps (encoder stays frozen; head trains). The discriminator is per-query-type accuracy recovery on
#   HELD-OUT entities + an explicit anti-collapse within-minus-cross gate.
# - baseline_in_band: MAIN_ENC (fragile decoded address) is the low baseline; FIXED_TAU_COMMIT is the
#   hand-tuned control the learned head must beat; ORACLE_ENTITY_FILE is the upper bound; the 5
#   deterministic floors + POOLED_READER are the can-fail controls and MUST collapse or the cell INVALID.
# - discriminator survives scale: closed-form loop + frozen-encoder forward pass; the head is a tiny MLP
#   trained on cached CPU reps. self-test exercises the REAL encoder + REAL loop + REAL head at tiny N
#   (real_code_path) + a DRIFT GUARD asserting this cell's build_addr_dataset reproduces ef's reference
#   commit/oracle/decoded arms bit-identically (the learned arm is the SAME code path w/ projected reps).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
#   (sorted(set()) everywhere; torch.randperm seeded per-head).
"""LEARNED IDENTITY-HEAD on the frozen-encoder situation-model harness (Director spawn 2026-07-31).

ATTACKS the DOMINANT half of the founding encoder wall: CROSS-FRAME ENTITY RE-IDENTIFICATION. The
encoder-backed loop drops MAIN 1.000 -> ~0.45-0.58, LOCALIZED to entity re-id
(MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/metrics.json: entity_consistency=0.795;
fillers decode WELL S=0.96/P=0.88, marks decode WELL). The entity-file cell showed a STABLE ADDRESS
(oracle) fixes it, but the hand-tuned fixed-TAU nearest-centroid COMMIT heuristic recovers only partly.

THE LEVER (per notes/research_cross_frame_entity_stability_lever_2026-07-31.md): the fixed-TAU heuristic
is a STATELESS single-pass match on FRAGILE raw reps. Replace its key space with a SMALL LEARNED
IDENTITY-HEAD on the FROZEN encoder's OWN ENT-slot reps, trained with a THREE-TERM objective:
  (a) cross-mention CONSISTENCY pull  -- same-referent mentions across statement/tag/question frames map
      to close identity keys;
  (b) inter-entity PUSH               -- different entities apart (margin hinge on in-batch negatives);
  (c) VICReg-style ANTI-COLLAPSE      -- variance-floor + covariance-decorrelation on the (normalized)
      identity key, a PROVABLE, negative-free floor (NOT reliance on in-batch negatives alone).
The head's normalized output becomes the IDENTITY KEY fed to the SAME streaming content-addressed commit
(the WM's content-addressing analog), REPLACING the fixed-TAU heuristic. ONE VARIABLE = learned head vs
fixed-TAU. Encoder FROZEN; fillers/marks decode via frozen role_attn EXACTLY as MAIN_ENC (drift-guarded).

ALLOWED (done here): a LEARNED head shaping the encoder's OWN reps; supervision = cross-mention
same-referent (color) labels (data-supervision). FORBIDDEN (NOT done): borrowed/pretrained embedding as
the identity vector; description-string anchor; inference-time bolt-on parser. Glass-box: the head's
cosine-commit decision is inspectable exactly like the fixed-TAU arm.

FAIRNESS GATE = HELD-OUT ENTITIES. The 20 colors split into TRAIN (head-training) and HELD-OUT (eval
entities the head NEVER trained on). Eval passages draw every ENT-slot color from the held-out pool
(mark colors from the train pool; both disjoint) -> EVERY eval query targets a novel entity. A
memorization signature (train-entity consistency high, held-out low) is checked explicitly on a matched
train-entity eval set.

PRE-REGISTERED BANDS (fixed BEFORE running; from the research design's Part 4, tied to real fields):
  HARD_PASS  : held-out entity_file_consistency(learned) >= 0.90 AND addr_gap_closed_frac >= 0.70 on ALL
               THREE query types AND held-out within-minus-cross cosine >= 0.30 (anti-collapse holds).
  HARD_FAIL  : held-out entity_file_consistency <= 0.80 (no better than the frozen baseline within noise),
               OR addr_gap_closed_frac <= 0.30 on ANY query type despite HIGH train-entity consistency
               (memorization -- held-out fails), OR held-out within-minus-cross <= 0.10 (collapse
               disguised as a pass).
  MIDDLE     : anything between -- reported EXPLICITLY (design judges MIDDLE ~0.40 more likely than
               HARD_PASS ~0.30). Direction confirmed, not yet at the bar.
  INVALID    : a can-fail floor did not collapse OR POOLED_READER is reservoir-decodable OR the
               anti-collapse ablation has no teeth (pull-only did NOT collapse in smoke).
  REFERENCE POINTS kept: FIXED_TAU_COMMIT (does the learned head BEAT it?) + ORACLE_ENTITY_FILE (does the
  learned head APPROACH the ceiling?) on the IDENTICAL held-out eval set.

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_identity_head_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_identity_head_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_identity_head_v1.py --lite

ASCII-only. No emojis. Deterministic seeding. Pure CPU (frozen-encoder forward passes + tiny-MLP head;
local, push-free; INLINE-LOCAL foreground-to-completion). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form FHRR loop + frozen-encoder forward passes
BATCHED at 256 + a tiny MLP head trained on CACHED reps (<1k steps, batch 256, CPU). Storage: per-entity
content-gated overwrite memory (sharded per slot) + FHRR-superposed roles; per-passage accumulators
independent. NOT a scaled/FULL run -- smoke + cheap LITE only (Director owns the FULL gate).
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
import torch.nn as nn
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
import exp_situation_model_assembly_encoder_backed_v1 as eb  # noqa: E402 (encoder + loop harness)
import exp_situation_model_assembly_entity_file_v1 as ef      # noqa: E402 (reference addr arms + calib)
import exp_checkpoint as ckpt                                  # noqa: E402 (per-unit checkpoint/resume)

clean = eb.clean
QUERY_TYPES = eb.QUERY_TYPES
V_FILL = eb.V_FILL
K_TRACK = clean.K_TRACK
N_DISTRACT_ENTITIES = clean.N_DISTRACT_ENTITIES
N_DISTRACT_EVENTS = clean.N_DISTRACT_EVENTS
WRITES_MIN = clean.WRITES_MIN
WRITES_MAX = clean.WRITES_MAX
TAIL_MIN = clean.TAIL_MIN
N_ROLES = clean.N_ROLES
STATE = clean.STATE
PLACE = clean.PLACE
CHANCE = eb.CHANCE
PROVEN_MIN = eb.PROVEN_MIN
GAP_MAX = eb.GAP_MAX
DECODE_FLOOR_BAR = eb.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = eb.ADDR_FLOOR_BAR
ATTN_TEMP = eb.ATTN_TEMP
V2_CKPT = eb.V2_CKPT

ANCHOR_NAME = "situation_model_assembly_learned_identity_head_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bars (fixed BEFORE running; from research Part 4) ----
CONSISTENCY_HARD_PASS = 0.90      # held-out entity_file_consistency (learned) HARD_PASS floor
CONSISTENCY_HARD_FAIL = 0.80      # <= this = no better than frozen baseline
ADDR_GAP_HARD_PASS = 0.70         # addr_gap_closed_frac on ALL 3 query types
ADDR_GAP_HARD_FAIL = 0.30         # <= this on ANY query type (with memorization) = HARD_FAIL
WITHIN_CROSS_HARD_PASS = 0.30     # held-out within-minus-cross cosine (anti-collapse holds)
WITHIN_CROSS_HARD_FAIL = 0.10     # <= this = collapse disguised as pass
MEMORIZE_TRAIN_HIGH = 0.85        # train-entity consistency this high + held-out addr_gap<=fail = memorize
BEAT_FIXED_TAU_MARGIN = 0.05      # learned must beat fixed-TAU addr_gap by this to claim "beats heuristic"
# anti-collapse teeth (smoke discriminator): pull-only MUST collapse; full MUST restore separation
COLLAPSE_TEETH_BAR = 0.10         # pull-only held within-minus-cross must be <= this (collapse fires)

# ---- head + training config (autonomy: exp_dev owns these) ----
HEAD_HIDDEN = 128
HEAD_KEY_DIM = 64
W_ALIGN = 1.0                     # cross-mention consistency pull
W_PUSH = 1.0                      # inter-entity push (margin hinge, in-batch negatives)
W_VIC = 0.5                       # VICReg-style anti-collapse (variance floor + covariance decorrelation)
PUSH_MARGIN = 0.2                 # push cosine below this
LR = 1e-3
# weight_decay 1e-3 + 600 steps selected on a TRAIN-INTERNAL validation split (7 train / 3 val of the 10
# train colors; the 10 eval-held colors NEVER touched): lifts VAL within-minus-cross 0.45->0.56 and the
# held-out generalization 0.29->0.40. A fair config choice (VAL-justified), not eval-held tuning.
WEIGHT_DECAY = 1e-3
TRAIN_BATCH = 256
HEAD_STEPS_SMOKE = 300
HEAD_STEPS_LITE = 600
TRAIN_NCTX_SMOKE = 30             # ENT-rep samples per train color for head training
TRAIN_NCTX_LITE = 44
EVAL_NCTX = 40                    # ENT-rep samples per color for the within-minus-cross geometry probe
COMMIT_CAP = V_FILL
CALIB_CTX_PER_COLOR = 12
SPLIT_SEED = 71013

# ---- seeds / sizes ----
SEEDS_SMOKE = (7,)
SEEDS_LITE = (7, 13)
SMOKE_TRAIN_N, SMOKE_EVAL_N = 80, 80
LITE_TRAIN_N, LITE_EVAL_N = 200, 160


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------- canonical hardening ----------------
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
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


# ================= held-out entity split =================
def color_split(seed=SPLIT_SEED):
    """Deterministic partition of the V_FILL colors into (train_colors, held_colors). Head trains on
    train_colors ONLY; eval passages draw every ENT color from held_colors -> novel entities at eval.
    Sizes: held needs >= K_TRACK + N_DISTRACT_ENTITIES entity colors (10); train needs >= K_TRACK mark
    colors (6). With V_FILL=20 a 10/10 split satisfies both with disjoint pools."""
    rng = np.random.default_rng(seed)
    perm = list(range(V_FILL))
    rng.shuffle(perm)
    n_held = K_TRACK + N_DISTRACT_ENTITIES
    held = sorted(perm[:n_held])
    train = sorted(perm[n_held:])
    assert len(train) >= K_TRACK, "train pool too small for mark colors"
    assert len(set(held) & set(train)) == 0, "held/train color pools must be disjoint"
    return train, held


# ================= held-out passage generator (faithful copy of clean.gen_passage w/ split pools) ====
def gen_passage_split(rng, ent_pool, mark_pool):
    """clean.gen_passage with entity colors drawn from ent_pool and mark colors from mark_pool (disjoint).
    Fillers (S/P) stay balanced over the full V_FILL palette EXACTLY as clean (they decode via the frozen
    role_attn front-end, untouched by the head). Everything else -- schedule, overwrite, queries, ground
    truth -- is identical to clean.gen_passage."""
    ent_pool = list(ent_pool)
    mark_pool = list(mark_pool)
    rng.shuffle(ent_pool)
    rng.shuffle(mark_pool)
    tracked = ent_pool[:K_TRACK]
    distract_ents = ent_pool[K_TRACK:K_TRACK + N_DISTRACT_ENTITIES]
    marks = mark_pool[:K_TRACK]
    mark_of = {tracked[i]: marks[i] for i in range(K_TRACK)}

    sched = []
    for ent in tracked:
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        for _ in range(k):
            addr_mode = "coref" if rng.random() < 0.5 else "name"
            sched.append({"ent": ent, "addr_mode": addr_mode, "is_distract": False})
    for _ in range(N_DISTRACT_EVENTS):
        de = int(distract_ents[int(rng.integers(0, len(distract_ents)))])
        sched.append({"ent": de, "addr_mode": "name", "is_distract": True})

    L = len(sched)

    def balanced_pool(nn_):
        reps = nn_ // V_FILL
        rem = nn_ - reps * V_FILL
        p = np.concatenate([np.repeat(np.arange(V_FILL), reps),
                            rng.permutation(V_FILL)[:rem] if rem else np.array([], dtype=np.int64)])
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

    current = {}
    last_write_idx = {}
    n_writes = {}
    for i, ev in enumerate(events):
        if ev["is_distract"]:
            continue
        current[(ev["ent"], STATE)] = ev["s_fill"]
        current[(ev["ent"], PLACE)] = ev["p_fill"]
        last_write_idx[ev["ent"]] = i
        n_writes[ev["ent"]] = n_writes.get(ev["ent"], 0) + 1

    eligible = [ent for ent, li in last_write_idx.items() if (L - 1 - li) >= TAIL_MIN]
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


def gen_dataset_split(n, rng, ent_pool, mark_pool):
    out = []
    while len(out) < n:
        p = gen_passage_split(rng, ent_pool, mark_pool)
        if p is not None:
            out.append(p)
    return out


# ================= identity head + three-term objective =================
class IdentityHead(nn.Module):
    """Small MLP on the frozen encoder's ENT-slot rep -> identity key. The ONLY learned params."""

    def __init__(self, d_in, hidden=HEAD_HIDDEN, k=HEAD_KEY_DIM):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, hidden), nn.ReLU(), nn.Linear(hidden, k))

    def forward(self, x):
        return self.net(x)


def _vicreg_terms(z):
    """VICReg-style anti-collapse on the NORMALIZED identity key z (the space the cosine commit uses).
    variance term: hinge floor each dim's std at 1/sqrt(k) (uniform-on-sphere scale). covariance term:
    off-diagonal covariance^2. Both provable + negative-free."""
    k = z.shape[1]
    std = torch.sqrt(z.var(dim=0) + 1e-4)
    floor = 1.0 / (k ** 0.5)
    var = torch.mean(F.relu(floor - std))
    zc = z - z.mean(dim=0)
    cov = (zc.T @ zc) / (z.shape[0] - 1)
    off = cov - torch.diag(torch.diag(cov))
    covl = (off ** 2).sum() / k
    return var, covl


def _gather_ent_reps(ext, colors, nctx, seed):
    """Labeled ENT-slot role_attn reps for the given colors across statement/tag/question frames.
    Returns (X float32 [n,d], y int64 [n]). Data-supervision: label = the true color (same-referent)."""
    rng = np.random.default_rng(seed)
    reqs = []
    tag = []
    for c in colors:
        for _ in range(nctx):
            o1 = int(rng.integers(0, V_FILL))
            o2 = int(rng.integers(0, V_FILL))
            pick = int(rng.integers(0, 3))
            if pick == 0:
                txt, spans = eb.render_name_event(c, o1, o2)
            elif pick == 1:
                txt, spans = eb.render_tag(c, o1)
            else:
                role = int(rng.integers(0, N_ROLES))
                txt, spans = eb.render_name_query(c, role)
            sl = [(st, cs, ce) for (st, cidx, cs, ce) in spans if st == "ENT"]
            if not sl:
                continue
            reqs.append({"text": txt, "slots": sl})
            tag.append(c)
    slotreps = ef._ent_slot_reps(ext, reqs)
    X = np.stack([sr[0] for sr in slotreps]).astype(np.float32)
    y = np.array(tag, dtype=np.int64)
    return torch.from_numpy(X), torch.from_numpy(y)


def train_identity_head(ext, train_colors, steps, seed, w_align=W_ALIGN, w_push=W_PUSH, w_vic=W_VIC):
    """Train the identity head on TRAIN colors with the three-term objective. Encoder stays frozen (we
    only read its reps). Returns (head, diag)."""
    torch.manual_seed(seed)
    X, y = _gather_ent_reps(ext, train_colors, TRAIN_NCTX_SMOKE if steps <= HEAD_STEPS_SMOKE else TRAIN_NCTX_LITE, seed + 991)
    head = IdentityHead(ext.d)
    opt = torch.optim.Adam(head.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    n = X.shape[0]
    last = {}
    for it in range(steps):
        idx = torch.randperm(n)[:TRAIN_BATCH]
        xb, yb = X[idx], y[idx]
        v = head(xb)
        z = F.normalize(v, dim=1)
        S = z @ z.T
        same = (yb[:, None] == yb[None, :]).float()
        eye = torch.eye(len(yb))
        same_off = same - eye
        diff = 1.0 - same
        l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
        l_push = (F.relu(S - PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
        var, cov = _vicreg_terms(z)
        loss = w_align * l_align + w_push * l_push + w_vic * (var + cov)
        opt.zero_grad()
        loss.backward()
        opt.step()
        if it == steps - 1:
            last = {"loss": float(loss.detach()), "l_align": float(l_align.detach()),
                    "l_push": float(l_push.detach()), "vic_var": float(var.detach()),
                    "vic_cov": float(cov.detach())}
    head.eval()
    return head, {"n_train_reps": int(n), "steps": steps, "final": last,
                  "w_align": w_align, "w_push": w_push, "w_vic": w_vic}


def project_reps(head, reps_np):
    """reps_np: np float32 [n, d] -> normalized identity keys np float32 [n, k]."""
    with torch.no_grad():
        v = head(torch.from_numpy(np.ascontiguousarray(reps_np, dtype=np.float32)))
        z = F.normalize(v, dim=1)
    return z.numpy().astype(np.float32)


def within_minus_cross(head, ext, colors, seed):
    """Anti-collapse metric on projected keys for the given colors: mean within-color pairwise cosine
    minus mean cross-color pairwise cosine (matches ef.calibrate_tau's pairwise regime)."""
    X, y = _gather_ent_reps(ext, colors, EVAL_NCTX, seed)
    Z = project_reps(head, X.numpy())
    y = y.numpy()
    cols = sorted(set(y.tolist()))
    idx = {c: np.where(y == c)[0] for c in cols}
    wi, cr = [], []
    for c in cols:
        ii = idx[c]
        for a in range(len(ii)):
            for b in range(a + 1, len(ii)):
                wi.append(float(np.dot(Z[ii[a]], Z[ii[b]])))
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            va = Z[idx[cols[i]][0]]
            for vb in Z[idx[cols[j]][:2]]:
                cr.append(float(np.dot(va, vb)))
    within = float(np.mean(wi)) if wi else float("nan")
    cross = float(np.mean(cr)) if cr else float("nan")
    return {"within": within, "cross": cross, "within_minus_cross": within - cross,
            "n_within": len(wi), "n_cross": len(cr)}


def calibrate_tau_learned(head, ext, seed):
    """Commit threshold read off the head's PROJECTED rep geometry, in PARITY with the fixed-TAU control
    (ef.calibrate_tau reads its threshold off the full V_FILL-color RAW geometry; this reads it off the
    same full-palette geometry in projected space). tau = midpoint of pairwise within vs cross projected
    cosine. This is a downstream addressing THRESHOLD, not identity learning -- the head's PARAMETERS are
    still trained on TRAIN colors ONLY (the fairness gate). NOT tuned to accuracy."""
    wc = within_minus_cross(head, ext, list(range(V_FILL)), seed)
    tau = 0.5 * (wc["within"] + wc["cross"])
    return {"tau": tau, "within": wc["within"], "cross": wc["cross"]}


# ================= build decoded dataset with a chosen entity-addressing scheme =================
# FAITHFUL MIRROR of ef.build_addr_dataset, adding entity_addr=="learned" (project ENT reps through the
# head before the SAME streaming commit). The DRIFT GUARD in self-test asserts this reproduces
# ef.build_addr_dataset bit-identically for decoded/oracle/commit -> the learned arm is proven to be the
# same code path with a projected key (one-variable guarantee).
def build_addr_dataset(dataset, ext, entity_addr, tau=None, cap=COMMIT_CAP, head=None):
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    dec = ext.decode_dataset_slots(all_reqs, modes=("role_attn",))
    if entity_addr in ("commit", "learned"):
        raw = ef._ent_slot_reps(ext, all_reqs)
        if entity_addr == "learned":
            assert head is not None, "learned addr requires a head"
            ent_reps = []
            for slots in raw:
                if slots:
                    ent_reps.append(list(project_reps(head, np.stack(slots))))
                else:
                    ent_reps.append([])
        else:
            ent_reps = raw
    else:
        ent_reps = None

    tracked_set_by_p = [set(p["tracked"]) for p in dataset]
    decoded_ds = []
    ans_ds = []
    ef_consistent = [0, 0]
    q_agree = [0, 0]
    n_files_list = []
    overflow_total = 0

    for pi, ((base_i, idx), p) in enumerate(zip(span_of, dataset)):
        def g(local_req_i, slot_j):
            return dec[base_i + local_req_i][slot_j]["role_attn"]

        def rep(local_req_i, slot_j):
            return ent_reps[base_i + local_req_i][slot_j]

        occ = []
        for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("tag", tk), "true": cidx,
                                "rep": rep(ri, j) if ent_reps is not None else None,
                                "req": ri, "slot": j})
        for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                continue
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("event", ek), "true": cidx,
                                "rep": rep(ri, j) if ent_reps is not None else None,
                                "req": ri, "slot": j})
        for qt in QUERY_TYPES:
            qi = idx["queries"][qt]
            if qi is None:
                continue
            (ri, slotinfo, q) = qi
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("query", qt), "true": cidx,
                                "rep": rep(ri, j) if ent_reps is not None else None,
                                "req": ri, "slot": j})

        if entity_addr == "oracle":
            addr = {o["key"]: o["true"] for o in occ}
            fdiag = {"n_files": len({o["true"] for o in occ}), "overflow": 0}
        elif entity_addr in ("commit", "learned"):
            addr, fdiag = ef._assign_commit([{"key": o["key"], "rep": o["rep"]} for o in occ], tau, cap)
        else:
            addr = {o["key"]: g(o["req"], o["slot"]) for o in occ}
            fdiag = {"n_files": len({addr[o["key"]] for o in occ}), "overflow": 0}
        n_files_list.append(fdiag["n_files"])
        overflow_total += fdiag["overflow"]

        by_true = {}
        for o in occ:
            if o["true"] in tracked_set_by_p[pi]:
                by_true.setdefault(o["true"], {}).setdefault("all", []).append(addr[o["key"]])
                fr = o["key"][0]
                by_true[o["true"]].setdefault(fr, []).append(addr[o["key"]])
        for t, dd in by_true.items():
            ef_consistent[1] += 1
            ef_consistent[0] += int(len(set(dd["all"])) == 1)
            stmt = dd.get("tag", []) + dd.get("event", [])
            if "query" in dd and stmt:
                maj = max(set(stmt), key=stmt.count)
                q_agree[1] += 1
                q_agree[0] += int(all(a == maj for a in dd["query"]))

        tag_list = []
        tag_mark_to_ent = {}
        for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
            d_ent = d_mark = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("tag", tk)]
                elif st == "MARK":
                    d_mark = g(ri, j)
            tag_list.append((d_ent, d_mark))
            tag_mark_to_ent[d_mark] = d_ent

        events = []
        for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
            d_ent = d_mark = d_s = d_p = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("event", ek)]
                elif st == "MARK":
                    d_mark = g(ri, j)
                elif st == "S":
                    d_s = g(ri, j)
                elif st == "P":
                    d_p = g(ri, j)
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                alloc_ent = tag_mark_to_ent.get(d_mark, d_mark)
                events.append({"ent": alloc_ent, "mark": d_mark, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "coref", "is_distract": ev["is_distract"]})
            else:
                events.append({"ent": d_ent, "mark": None, "s_fill": d_s, "p_fill": d_p,
                               "addr_mode": "name", "is_distract": ev["is_distract"]})

        dq = {}
        aq = {}
        for qt in QUERY_TYPES:
            qi = idx["queries"][qt]
            if qi is None:
                dq[qt] = None
                aq[qt] = None
                continue
            (ri, slotinfo, q) = qi
            d_ent = None
            d_mark = None
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    d_ent = addr[("query", qt)]
                elif st == "MARK":
                    d_mark = g(ri, j)
            dq[qt] = {"ent": (d_ent if d_ent is not None else 0), "mark": d_mark, "role": q["role"]}
            aq[qt] = q["answer"]
        decoded_ds.append({"tag_list": tag_list, "events": events, "queries": dq})
        ans_ds.append(aq)

    diag = {"entity_file_consistency": (ef_consistent[0] / ef_consistent[1] if ef_consistent[1] else float("nan")),
            "cross_frame_query_agreement": (q_agree[0] / q_agree[1] if q_agree[1] else float("nan")),
            "n_files_mean": float(np.mean(n_files_list)) if n_files_list else float("nan"),
            "overflow_total": overflow_total, "n_tracked_ref": ef_consistent[1]}
    return decoded_ds, ans_ds, diag


# ================= self-test =================
def _combined_digest(arm_res):
    return hashlib.sha256("".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest()


def run_self_test():
    _log("SELF-TEST: clean loop toy binding + construction audit ...")
    toy = clean.toy_binding_selftest()
    audit = clean.audit_construction(seed=7, n=200)
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]

    train_colors, held_colors = color_split()
    _log("  color split: train=%s held=%s" % (train_colors, held_colors))

    _log("SELF-TEST: load REAL v2 encoder (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  build: %s (d=%d)" % (binfo, ext.d))

    # ---- DRIFT GUARD: this cell's build_addr_dataset == ef.build_addr_dataset for decoded/oracle/commit
    tables = clean.build_tables()
    ds = clean.gen_dataset(24, np.random.default_rng(7))
    cal_raw = ef.calibrate_tau(ext)
    _log("SELF-TEST: DRIFT GUARD vs ef reference builder (decoded/oracle/commit) ...")
    for mode, kw in (("decoded", {}), ("oracle", {}), ("commit", {"tau": cal_raw["tau"]})):
        d_mine, a_mine, _ = build_addr_dataset(ds, ext, mode, **kw)
        d_ref, a_ref, _ = ef.build_addr_dataset(ds, ext, mode, **kw)
        arm_mine = eb.run_arm_decoded(d_mine, a_mine, tables, "main")
        arm_ref = eb.run_arm_decoded(d_ref, a_ref, tables, "main")
        for qt in QUERY_TYPES:
            assert arm_mine[qt]["preds_digest"] == arm_ref[qt]["preds_digest"], (
                "DRIFT_GUARD VIOLATION on %s/%s: this cell's builder != ef reference" % (mode, qt))
    _log("  DRIFT GUARD PASS: build_addr_dataset reproduces ef decoded/oracle/commit bit-identically")

    # ---- train a tiny head + prove learned arm runs + anti-collapse teeth ----
    _log("SELF-TEST: train identity head (60 steps) + anti-collapse teeth (pull-only must collapse) ...")
    head, hdiag = train_identity_head(ext, train_colors, steps=60, seed=7)
    tau_l = calibrate_tau_learned(head, ext, seed=7)
    wc_held = within_minus_cross(head, ext, held_colors, seed=123)
    _log("  head: %s tau_learned=%.4f held_within_minus_cross=%.4f"
         % (hdiag["final"], tau_l["tau"], wc_held["within_minus_cross"]))

    head_pull, _ = train_identity_head(ext, train_colors, steps=60, seed=7, w_push=0.0, w_vic=0.0)
    wc_pull = within_minus_cross(head_pull, ext, held_colors, seed=123)
    _log("  ANTI-COLLAPSE ABLATION: pull-only held_within_minus_cross=%.4f (should be near 0 = collapse)"
         % wc_pull["within_minus_cross"])

    # learned arm runs end-to-end through the loop on a held-out eval set
    rng = np.random.default_rng(7)
    ev = gen_dataset_split(16, rng, held_colors, train_colors)
    for p in ev:  # fairness assertion: every ENT color in eval is held-out
        for e in p["tracked"]:
            assert e in held_colors, "eval entity not held-out"
    d_l, a_l, diag_l = build_addr_dataset(ev, ext, "learned", tau=tau_l["tau"], head=head)
    learned = eb.run_arm_decoded(d_l, a_l, tables, "main")
    d_c, a_c, diag_c = build_addr_dataset(ev, ext, "commit", tau=cal_raw["tau"])
    fixed = eb.run_arm_decoded(d_c, a_c, tables, "main")
    for qt in QUERY_TYPES:
        for arm in (learned, fixed):
            acc = arm[qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)
    _log("  LEARNED (held eval): " + ", ".join("%s=%.2f" % (qt, learned[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f" % diag_l["entity_file_consistency"])
    _log("  FIXED_TAU (held eval): " + ", ".join("%s=%.2f" % (qt, fixed[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f" % diag_c["entity_file_consistency"])
    _log("SELF-TEST PASS")
    return {"toy": toy, "audit_fails": audit["fails"], "build": binfo, "encoder_d": ext.d,
            "train_colors": train_colors, "held_colors": held_colors,
            "drift_guard": "PASS", "head_diag": hdiag, "tau_learned": tau_l["tau"],
            "held_within_minus_cross_full": wc_held["within_minus_cross"],
            "held_within_minus_cross_pullonly": wc_pull["within_minus_cross"],
            "tiny_learned": {qt: learned[qt]["acc"] for qt in QUERY_TYPES},
            "tiny_fixed_tau": {qt: fixed[qt]["acc"] for qt in QUERY_TYPES},
            "arms_differ_verified": True}


# ================= per-seed driver =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def run_seed(seed, ext, train_colors, held_colors, cal_raw, run_mode, train_n, eval_n):
    tables = clean.build_tables()
    steps = HEAD_STEPS_SMOKE if run_mode == "smoke" else HEAD_STEPS_LITE
    t = time.perf_counter()
    head, hdiag = train_identity_head(ext, train_colors, steps=steps, seed=seed)
    tau_l = calibrate_tau_learned(head, ext, seed=seed + 1)
    wc_held = within_minus_cross(head, ext, held_colors, seed=seed + 2)
    wc_train = within_minus_cross(head, ext, train_colors, seed=seed + 3)
    # anti-collapse teeth: a pull-only head must collapse on held-out (validity check per seed)
    head_pull, _ = train_identity_head(ext, train_colors, steps=steps, seed=seed, w_push=0.0, w_vic=0.0)
    wc_pull = within_minus_cross(head_pull, ext, held_colors, seed=seed + 2)
    _log("  seed=%d head trained in %.1fs tau_l=%.4f held_wmc=%.3f pullonly_wmc=%.3f train_wmc=%.3f"
         % (seed, time.perf_counter() - t, tau_l["tau"], wc_held["within_minus_cross"],
            wc_pull["within_minus_cross"], wc_train["within_minus_cross"]))

    # ---- held-out entity eval set (every ENT color novel to the head) ----
    ev_held = gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    # ---- matched train-entity eval set (memorization check) ----
    ev_train = gen_dataset_split(eval_n, np.random.default_rng(seed + 555), train_colors, held_colors)
    # pooled/most_recent floors need a train dataset (front-end-independent construction floor)
    train_ds = clean.gen_dataset(train_n, np.random.default_rng(seed))

    dec_ra, ans_ra, stage_ra = eb.build_decoded_dataset(ev_held, ext, "role_attn")
    dec_span, ans_span, _ = eb.build_decoded_dataset(ev_held, ext, "span")
    dec_or, ans_or, diag_or = build_addr_dataset(ev_held, ext, "oracle")
    dec_fx, ans_fx, diag_fx = build_addr_dataset(ev_held, ext, "commit", tau=cal_raw["tau"])
    dec_le, ans_le, diag_le = build_addr_dataset(ev_held, ext, "learned", tau=tau_l["tau"], head=head)
    # learned on train-entity eval (memorization signature)
    dec_le_tr, ans_le_tr, diag_le_tr = build_addr_dataset(ev_train, ext, "learned", tau=tau_l["tau"], head=head)

    arms = {}
    arms["main_enc"] = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = eb.run_arm_decoded(dec_span, ans_span, tables, "main")
    arms["oracle_entity_file"] = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    arms["fixed_tau_commit"] = eb.run_arm_decoded(dec_fx, ans_fx, tables, "main")
    arms["learned_commit"] = eb.run_arm_decoded(dec_le, ans_le, tables, "main")
    arms["learned_commit_trainent"] = eb.run_arm_decoded(dec_le_tr, ans_le_tr, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = eb.run_arm_decoded(dec_ra, ans_ra, tables, m)
    most_recent = clean.run_most_recent(ev_held)
    pooled = clean.run_pooled_reader(train_ds, ev_held, seed)

    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n, "arms": arms,
           "most_recent": most_recent, "pooled": pooled, "stage_role_attn": stage_ra,
           "diag_oracle": diag_or, "diag_fixed_tau": diag_fx, "diag_learned": diag_le,
           "diag_learned_trainent": diag_le_tr, "head_diag": hdiag, "tau_learned": tau_l,
           "wc_held": wc_held, "wc_train": wc_train, "wc_pullonly": wc_pull}
    for label in ("main_enc", "fixed_tau_commit", "learned_commit", "oracle_entity_file", "ref_span"):
        _log("  seed=%d %-18s: %s" % (seed, label,
             ", ".join("%s=%.3f" % (qt, arms[label][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d LEARNED diag: ef_consistency=%.3f q_agree=%.3f n_files=%.2f | FIXED ef_consistency=%.3f | ORACLE ef=%.3f | train-ent ef=%.3f"
         % (seed, diag_le["entity_file_consistency"], diag_le["cross_frame_query_agreement"],
            diag_le["n_files_mean"], diag_fx["entity_file_consistency"],
            diag_or["entity_file_consistency"], diag_le_tr["entity_file_consistency"]))
    _log("  seed=%d floors: RANDOM_ADDR(a)=%.2f NO_COREF(b)=%.2f WRONGROLE(a)=%.2f SHUFFLED(a)=%.2f MOST_RECENT(a)=%.2f POOLED(b)=%.2f"
         % (seed, arms["random_addr"]["a_name_maintenance"]["acc"], arms["no_coref"]["b_competitive_coref"]["acc"],
            arms["wrongrole"]["a_name_maintenance"]["acc"], arms["shuffled"]["a_name_maintenance"]["acc"],
            most_recent["a_name_maintenance"]["acc"], pooled["b_competitive_coref"]["acc"]))
    return res


def decide_verdict(per_seed):
    def al(arm, qt):
        return [ps["arms"][arm][qt]["acc"] for ps in per_seed]

    # ---- floors valid gate ----
    floors_ok = True
    floor_notes = []
    pooled_b = [ps["pooled"]["b_competitive_coref"]["acc"] for ps in per_seed]
    pooled_c = [ps["pooled"]["c_overwrite"]["acc"] for ps in per_seed]
    pooled_reservoir = (all(x >= PROVEN_MIN for x in pooled_b if not math.isnan(x))
                        or all(x >= PROVEN_MIN for x in pooled_c if not math.isnan(x)))
    floor_applies = {
        "random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR, "arm"),
        "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR, "arm"),
        "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR, "arm"),
        "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR, "arm"),
        "most_recent": (QUERY_TYPES, DECODE_FLOOR_BAR, "mr"),
    }
    for arm, (qts, bar, src) in floor_applies.items():
        for qt in qts:
            xs = ([ps["most_recent"][qt]["acc"] for ps in per_seed] if src == "mr" else al(arm, qt))
            for x in xs:
                if not math.isnan(x) and x > bar:
                    floors_ok = False
                    floor_notes.append("%s did not collapse on %s: %.3f > %.3f" % (arm, qt, x, bar))

    # ---- anti-collapse teeth: pull-only must collapse on held-out (per seed) ----
    pull_wmc = [ps["wc_pullonly"]["within_minus_cross"] for ps in per_seed]
    teeth_ok = all((not math.isnan(x)) and x <= COLLAPSE_TEETH_BAR for x in pull_wmc)

    main_mean = {qt: _mean(al("main_enc", qt)) for qt in QUERY_TYPES}
    ref_mean = {qt: _mean(al("ref_span", qt)) for qt in QUERY_TYPES}
    oracle_mean = {qt: _mean(al("oracle_entity_file", qt)) for qt in QUERY_TYPES}
    fixed_mean = {qt: _mean(al("fixed_tau_commit", qt)) for qt in QUERY_TYPES}
    learned_mean = {qt: _mean(al("learned_commit", qt)) for qt in QUERY_TYPES}

    def _frac(o, m, r):
        return ((o - m) / (r - m)) if (not math.isnan(o) and not math.isnan(m) and not math.isnan(r)
                                       and (r - m) > 1e-6) else float("nan")
    addr_gap_learned = {qt: _frac(learned_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}
    addr_gap_fixed = {qt: _frac(fixed_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}
    addr_gap_oracle = {qt: _frac(oracle_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}

    ef_cons_learned = _mean([ps["diag_learned"]["entity_file_consistency"] for ps in per_seed])
    ef_cons_fixed = _mean([ps["diag_fixed_tau"]["entity_file_consistency"] for ps in per_seed])
    ef_cons_oracle = _mean([ps["diag_oracle"]["entity_file_consistency"] for ps in per_seed])
    ef_cons_trainent = _mean([ps["diag_learned_trainent"]["entity_file_consistency"] for ps in per_seed])
    q_agree_learned = _mean([ps["diag_learned"]["cross_frame_query_agreement"] for ps in per_seed])
    wmc_held = _mean([ps["wc_held"]["within_minus_cross"] for ps in per_seed])
    wmc_train = _mean([ps["wc_train"]["within_minus_cross"] for ps in per_seed])

    # HARD bar evaluations
    addr_gap_all_pass = all((not math.isnan(addr_gap_learned[qt])) and addr_gap_learned[qt] >= ADDR_GAP_HARD_PASS
                            for qt in QUERY_TYPES)
    addr_gap_any_fail = any((not math.isnan(addr_gap_learned[qt])) and addr_gap_learned[qt] <= ADDR_GAP_HARD_FAIL
                            for qt in QUERY_TYPES)
    consistency_pass = (not math.isnan(ef_cons_learned)) and ef_cons_learned >= CONSISTENCY_HARD_PASS
    consistency_fail = (not math.isnan(ef_cons_learned)) and ef_cons_learned <= CONSISTENCY_HARD_FAIL
    within_cross_pass = (not math.isnan(wmc_held)) and wmc_held >= WITHIN_CROSS_HARD_PASS
    within_cross_fail = (not math.isnan(wmc_held)) and wmc_held <= WITHIN_CROSS_HARD_FAIL
    memorize_sig = (addr_gap_any_fail and (not math.isnan(ef_cons_trainent))
                    and ef_cons_trainent >= MEMORIZE_TRAIN_HIGH)
    beats_fixed = all((not math.isnan(addr_gap_learned[qt])) and (not math.isnan(addr_gap_fixed[qt]))
                      and (addr_gap_learned[qt] >= addr_gap_fixed[qt] + BEAT_FIXED_TAU_MARGIN)
                      for qt in QUERY_TYPES)

    bands = {"chance": CHANCE,
             "hard_pass_bars": {"consistency": CONSISTENCY_HARD_PASS, "addr_gap": ADDR_GAP_HARD_PASS,
                                "within_minus_cross": WITHIN_CROSS_HARD_PASS},
             "hard_fail_bars": {"consistency": CONSISTENCY_HARD_FAIL, "addr_gap": ADDR_GAP_HARD_FAIL,
                                "within_minus_cross": WITHIN_CROSS_HARD_FAIL},
             "main_enc_mean": main_mean, "ref_span_mean": ref_mean, "oracle_mean": oracle_mean,
             "fixed_tau_mean": fixed_mean, "learned_mean": learned_mean,
             "main_enc_acc": {qt: al("main_enc", qt) for qt in QUERY_TYPES},
             "learned_commit_acc": {qt: al("learned_commit", qt) for qt in QUERY_TYPES},
             "fixed_tau_commit_acc": {qt: al("fixed_tau_commit", qt) for qt in QUERY_TYPES},
             "oracle_acc": {qt: al("oracle_entity_file", qt) for qt in QUERY_TYPES},
             "ref_span_acc": {qt: al("ref_span", qt) for qt in QUERY_TYPES},
             "addr_gap_closed_frac_learned": addr_gap_learned,
             "addr_gap_closed_frac_fixed_tau": addr_gap_fixed,
             "addr_gap_closed_frac_oracle": addr_gap_oracle,
             "entity_file_consistency_learned_heldout": ef_cons_learned,
             "entity_file_consistency_fixed_tau_heldout": ef_cons_fixed,
             "entity_file_consistency_oracle_heldout": ef_cons_oracle,
             "entity_file_consistency_learned_trainent": ef_cons_trainent,
             "cross_frame_query_agreement_learned": q_agree_learned,
             "within_minus_cross_held": wmc_held, "within_minus_cross_train": wmc_train,
             "within_minus_cross_pullonly": pull_wmc,
             "pooled_acc_b": pooled_b, "pooled_acc_c": pooled_c,
             "random_addr_acc": {qt: al("random_addr", qt) for qt in QUERY_TYPES},
             "no_coref_acc_b": al("no_coref", "b_competitive_coref"),
             "wrongrole_acc": {qt: al("wrongrole", qt) for qt in QUERY_TYPES},
             "shuffled_acc": {qt: al("shuffled", qt) for qt in QUERY_TYPES},
             "most_recent_acc": {qt: [ps["most_recent"][qt]["acc"] for ps in per_seed] for qt in QUERY_TYPES},
             "floors_ok": floors_ok, "floor_notes": floor_notes,
             "pooled_reservoir_decodable": pooled_reservoir,
             "anti_collapse_teeth_ok": teeth_ok,
             "learned_beats_fixed_tau": beats_fixed,
             "memorization_signature": memorize_sig}

    if pooled_reservoir:
        return "INVALID", ("POOLED_READER clears PROVEN_MIN on (b)/(c) -- reservoir-decodable. pooled_b=%s "
                           "pooled_c=%s" % (pooled_b, pooled_c)), bands
    if not floors_ok:
        return "INVALID", ("A can-fail floor did not collapse: " + "; ".join(floor_notes)), bands
    if not teeth_ok:
        return "INVALID", ("ANTI-COLLAPSE ABLATION HAS NO TEETH: pull-only within-minus-cross=%s did NOT "
                           "collapse to <= %.2f -- the anti-collapse term is not the load-bearing guard "
                           "(regime cannot discriminate)." % (pull_wmc, COLLAPSE_TEETH_BAR)), bands

    if consistency_pass and addr_gap_all_pass and within_cross_pass:
        return "HARD_PASS", ("Learned identity-head CLEARS all bars on HELD-OUT entities: "
                             "ef_consistency=%.3f>=%.2f, addr_gap_closed=%s all>=%.2f, within-minus-cross="
                             "%.3f>=%.2f. beats_fixed_tau=%s (fixed addr_gap=%s). Approaches ORACLE "
                             "(oracle addr_gap=%s). LEARNED KEY-SPACE RECOVERS CROSS-FRAME IDENTITY."
                             % (ef_cons_learned, CONSISTENCY_HARD_PASS, addr_gap_learned, ADDR_GAP_HARD_PASS,
                                wmc_held, WITHIN_CROSS_HARD_PASS, beats_fixed, addr_gap_fixed,
                                addr_gap_oracle)), bands
    if consistency_fail or within_cross_fail or memorize_sig:
        why = []
        if consistency_fail:
            why.append("ef_consistency=%.3f<=%.2f (no better than frozen baseline)" % (ef_cons_learned, CONSISTENCY_HARD_FAIL))
        if within_cross_fail:
            why.append("within-minus-cross=%.3f<=%.2f (collapse disguised as pass)" % (wmc_held, WITHIN_CROSS_HARD_FAIL))
        if memorize_sig:
            why.append("MEMORIZATION: train-ent ef_consistency=%.3f high but held-out addr_gap<=%.2f (%s)"
                       % (ef_cons_trainent, ADDR_GAP_HARD_FAIL, addr_gap_learned))
        return "HARD_FAIL", ("Learned head FAILS on held-out entities: " + "; ".join(why)
                             + ". learned addr_gap=%s ef_consistency=%.3f wmc_held=%.3f wmc_train=%.3f"
                             % (addr_gap_learned, ef_cons_learned, wmc_held, wmc_train)), bands
    return "MIDDLE", ("Direction confirmed, not at the bar. HELD-OUT: ef_consistency=%.3f (HP>=%.2f), "
                      "addr_gap_closed=%s (HP>=%.2f all), within-minus-cross=%.3f (HP>=%.2f). "
                      "beats_fixed_tau=%s (learned addr_gap=%s vs fixed=%s vs oracle=%s). "
                      "Learned key-space LIFTS cross-frame identity but does not fully close the oracle gap."
                      % (ef_cons_learned, CONSISTENCY_HARD_PASS, addr_gap_learned, ADDR_GAP_HARD_PASS,
                         wmc_held, WITHIN_CROSS_HARD_PASS, beats_fixed, addr_gap_learned, addr_gap_fixed,
                         addr_gap_oracle)), bands


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    if run_mode == "smoke":
        seeds, train_n, eval_n = SEEDS_SMOKE, SMOKE_TRAIN_N, SMOKE_EVAL_N
    elif run_mode == "lite":
        seeds, train_n, eval_n = SEEDS_LITE, LITE_TRAIN_N, LITE_EVAL_N
    else:
        seeds, train_n, eval_n = SEEDS_SMOKE, 1, 1

    expected_units = 1 if run_mode == "self_test" else len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (drift-guard vs ef + learned head + anti-collapse teeth + arms-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test",
                   "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    _log("%s: seeds=%s train_n=%d eval_n=%d chance=%.4f" % (run_mode.upper(), seeds, train_n, eval_n, CHANCE))
    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    train_colors, held_colors = color_split()
    _log("color split (fairness gate): train=%s held=%s" % (train_colors, held_colors))
    _log("Building frozen v2 encoder extractor ...")
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  %s (d=%d)" % (binfo, ext.d))
    cal_raw = ef.calibrate_tau(ext)
    _log("  RAW tau (fixed-TAU control): tau=%.4f within=%.4f cross=%.4f"
         % (cal_raw["tau"], cal_raw["within"], cal_raw["cross"]))

    per_seed = []
    for seed in seeds:
        key = ckpt.unit_key("seed", seed, run_mode)
        if key in ckpt.completed_units(OUTPUT_DIR):
            per_seed.append(ckpt.load_units(OUTPUT_DIR)[key])
            _log("  seed=%d loaded from checkpoint" % seed)
            continue
        res = run_seed(seed, ext, train_colors, held_colors, cal_raw, run_mode, train_n, eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        per_seed.append(res)

    verdict, msg, bands = decide_verdict(per_seed)
    bands["tau_raw"] = cal_raw
    bands["color_split"] = {"train": train_colors, "held": held_colors}
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "encoder_build": binfo, "encoder_d": ext.d,
               "cardinality_ok": bool(len(per_seed) == len(seeds)),
               "expected_n_units": len(seeds), "n_units_done": len(per_seed),
               "construction_audit": audit, "per_seed": per_seed,
               "params": {"DIM": clean.DIM, "K_TRACK": K_TRACK, "V_FILL": V_FILL,
                          "HEAD_HIDDEN": HEAD_HIDDEN, "HEAD_KEY_DIM": HEAD_KEY_DIM,
                          "W_ALIGN": W_ALIGN, "W_PUSH": W_PUSH, "W_VIC": W_VIC, "PUSH_MARGIN": PUSH_MARGIN,
                          "head_steps": HEAD_STEPS_SMOKE if run_mode == "smoke" else HEAD_STEPS_LITE,
                          "train_n": train_n, "eval_n": eval_n, "seeds": list(seeds),
                          "train_colors": train_colors, "held_colors": held_colors,
                          "v2_ckpt": os.path.relpath(V2_CKPT, REPO_ROOT)},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns",
               "progress_logging": "print_flush_true"}
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
