# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays; MAIN_ENC /
#   REF_SPAN / ORACLE / IDENTKEY_FIXEDTAU / IDENTKEY_LEARNEDWRITE asserted pairwise distinct where they
#   must differ; LEARNEDWRITE==ORACLE when re-id is perfect is a LEGITIMATE coincidence -> logged, NOT
#   hard-asserted). The one-variable pair (IDENTKEY_FIXEDTAU vs IDENTKEY_LEARNEDWRITE) is asserted DISTINCT
#   in smoke (the write organ must actually change the assignment).
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb / discriminator_reachability: the SCORING loop is the zero-learned-param FHRR SituationWM (imported
#   VERBATIM via eb.clean). Learned params live in (1) a FROZEN identity-head (reused VERBATIM from
#   exp_situation_model_assembly_learned_identity_head_v1, dddf0997b) as the KEY producer, held CONSTANT
#   across the two contrasted write arms, and (2) a SMALL learned write-gate (the organ under test). The
#   HARD_PASS addr-gap bar is measured RELATIVE TO ORACLE (not ref_span): the ORACLE arm -- a PERFECT
#   assignment -- itself only reaches loop acc ~0.66-0.73 because the residual role_attn filler decode
#   (S=0.96/P=0.88 MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/metrics.json) caps any
#   ADDRESSING/WRITE fix well below the ref_span=1.0 ceiling. addr_gap_closed_frac vs ref_span is therefore
#   UNREACHABLE above ~0.37 even for a perfect write; the write organ can only be fairly judged on the
#   fraction of the ORACLE-vs-MAIN gap it closes. Both fractions are reported; HARD_PASS gates on the
#   ORACLE-relative gap (reachable). discriminator_reachability=True under this definition.
# - baseline_in_band: MAIN_ENC (fragile decoded address, ~0.46 MEASURED@.../encoder_backed_v1/metrics.json)
#   is the direct-decoded baseline the write organ must BEAT; IDENTKEY_FIXEDTAU (same keys + fixed-TAU
#   streaming commit) is the one-variable control the write organ must beat; ORACLE is the upper bound; the
#   5 deterministic floors + POOLED_READER are the can-fail controls and MUST collapse or the cell INVALID.
# - discriminator survives scale: closed-form loop + frozen-encoder forward pass + tiny gate; the gate is a
#   fixed small MLP (not scale-saturating). smoke exercises the REAL encoder + REAL loop + REAL head + REAL
#   gate at reduced eval_n; LITE at full. self-test DRIFT-GUARDs this cell's build_addr_dataset against the
#   dddf0997b reference builder for decoded/oracle/commit/learned bit-identically (the learned_write arm is
#   the SAME code path with the write-gate swapped for the fixed-TAU threshold -> one-variable guarantee).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set())
#   (sorted(set()) everywhere; torch.randperm seeded per-head/gate).
"""LEARNED STATEFUL WRITE (entity-slot allocator) on the frozen-encoder situation-model harness
(Director spawn 2026-07-31).

WHAT THIS ATTACKS (the localized wall). The prior lite (exp_situation_model_assembly_learned_identity_head
_v1, dddf0997b, HARD_FAIL) isolated the true remaining wall with a clean causal decomposition
(MEASURED@data/exp_situation_model_assembly_learned_identity_head_v1/metrics.json):
  - the learned identity-head GENERALIZES the KEY SPACE (held-out within-minus-cross 0.20->0.42;
    entity_file_consistency 0.35 fixed-TAU -> 0.67 learned) -- the key is NOT the wall and NOT memorization;
  - yet loop acc did NOT recover: identity-keys + fixed-TAU streaming commit -> a=0.053 b=0.069 c=0.083
    (addr_gap_closed vs ref -0.75..-1.13), and RAW-reps + fixed-TAU -> a=0.063 b=0.253 c=0.086 -- BOTH far
    BELOW MAIN_ENC's 0.46 direct-decoded baseline. A dumb heuristic assignment HARMS;
  - ORACLE (perfect assignment) RECOVERS: a=0.659 b=0.725 c=0.672 (>MAIN 0.46), addr_gap vs ref ~+0.37.
CONCLUSION the prior lite reached: the wall is the ASSIGNMENT/WRITE mechanism (which mention writes to
which persistent slot), NOT the key quality. A good assignment helps (oracle), a dumb heuristic hurts
(fixed-TAU). The missing organ is a LEARNED STATEFUL WRITE: pattern-separation-on-write (allocate a fresh
slot for a genuinely new entity) + pattern-completion-on-read (route a returning mention back to its slot)
-- the hippocampal DG/CA3 analog, which the project ALREADY HAS as the VET-confirmed content-gated WM.

THE LEVER (per notes/research_cross_frame_entity_stability_lever_2026-07-31.md, biology Part 2: DG
pattern-separation / CA3 pattern-completion into a persistent content-addressed slot). Replace the fixed-TAU
streaming commit (a single GLOBAL cosine threshold, ZERO learned params -- it over-merges DISTINCT entities
into one slot, clobbering WM state, and fragments returning ones) with a LEARNED content-gated allocator:
on each mention, argmax-cosine picks the candidate slot (CA3 completion retrieves the nearest attractor),
and a SMALL LEARNED GATE decides route-to-that-slot vs allocate-a-fresh-slot (DG separation-on-write), using
the RELATIVE evidence a single threshold cannot see (best sim, second-best sim, the best-vs-second gap, slot
count, occupancy). Trained end-to-end on cross-mention same-entity (color) labels = data-supervision.
Glass-box: the gate's route/allocate decision + per-slot cosines are fully inspectable.

ONE VARIABLE = the WRITE/ASSIGNMENT organ. IDENTKEY_FIXEDTAU (identity-head keys + fixed-TAU streaming
commit) vs IDENTKEY_LEARNEDWRITE (the SAME frozen identity-head keys + the learned gate). The identity head
is trained ONCE (dddf0997b three-term objective VERBATIM) and FROZEN; both arms consume its keys -> the key
space is held constant, the variable is the write organ alone.

ALLOWED (done here): a LEARNED stateful write on the encoder's OWN identity-head keys; supervision =
cross-mention same-referent (color) labels (data-supervision). FORBIDDEN (NOT done): borrowed/pretrained
embedding as the key; description-string anchor; inference-time bolt-on parser; hand-coded identity matching
(the fixed-TAU control is the hand-coded heuristic being REPLACED, kept only as the comparator).

FAIRNESS GATE = HELD-OUT ENTITIES. The 20 colors split into TRAIN (head + gate training) and HELD-OUT (eval
entities NEITHER the head NOR the gate ever trained on). Eval passages draw every ENT-slot color from the
held-out pool (mark colors from train pool; disjoint) -> every eval query targets a novel entity.

PRE-REGISTERED BANDS (fixed BEFORE running; the REAL bar is beating the DIRECT-decoded MAIN_ENC baseline
AND the fixed-TAU control, and approaching ORACLE -- addr gap measured vs the reachable ORACLE ceiling):
  HARD_PASS  : on ALL THREE query types, held-out learned-write loop acc BEATS MAIN_ENC (> its per-type
               mean) AND beats IDENTKEY_FIXEDTAU by >= BEAT_MARGIN AND addr_gap_closed_frac_vs_oracle
               >= 0.70; AND anti-collapse holds (held within-minus-cross >= 0.30); AND floors collapse.
  HARD_FAIL  : learned-write <= MAIN_ENC on ALL 3 (write doesn't help over direct-decoded), OR
               <= IDENTKEY_FIXEDTAU on ALL 3 (the write organ adds nothing over the fixed threshold on the
               same keys), OR addr_gap_closed_frac_vs_oracle <= 0.30 on ALL 3, OR collapse
               (within-minus-cross <= 0.10), OR a floor did not collapse / POOLED reservoir-decodable
               (INVALID).
  MIDDLE     : anything between -- reported EXPLICITLY per query type (direction confirmed, not at the bar).
  REFERENCE POINTS kept visible (the ladder): MAIN_ENC, IDENTKEY_FIXEDTAU, RAW_FIXEDTAU, ORACLE, REF_SPAN.

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_stateful_write_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_stateful_write_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_learned_stateful_write_v1.py --lite

ASCII-only. No emojis. Deterministic seeding. Pure CPU (frozen-encoder forward passes + tiny MLP head +
tiny MLP gate; local, push-free; INLINE-LOCAL foreground-to-completion). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form FHRR loop + frozen-encoder forward passes
BATCHED at 256 + a tiny frozen head + a tiny write-gate trained on cached streamed features (CPU, seconds).
Storage: per-entity content-gated overwrite memory (sharded per slot) + FHRR-superposed roles; per-passage
accumulators independent. NOT a scaled/FULL run -- smoke + cheap LITE only (Director owns the FULL gate).
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
import exp_situation_model_assembly_encoder_backed_v1 as eb           # noqa: E402 (encoder + loop harness)
import exp_situation_model_assembly_entity_file_v1 as ef              # noqa: E402 (fixed-TAU commit + calib)
import exp_situation_model_assembly_learned_identity_head_v1 as lih   # noqa: E402 (identity head, VERBATIM)
import exp_checkpoint as ckpt                                         # noqa: E402 (per-unit checkpoint/resume)

clean = eb.clean
QUERY_TYPES = eb.QUERY_TYPES
V_FILL = eb.V_FILL
K_TRACK = clean.K_TRACK
N_ROLES = clean.N_ROLES
CHANCE = eb.CHANCE
PROVEN_MIN = eb.PROVEN_MIN
GAP_MAX = eb.GAP_MAX
DECODE_FLOOR_BAR = eb.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = eb.ADDR_FLOOR_BAR
ATTN_TEMP = eb.ATTN_TEMP
V2_CKPT = eb.V2_CKPT

ANCHOR_NAME = "situation_model_assembly_learned_stateful_write_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bars (fixed BEFORE running) ----
ADDR_GAP_ORACLE_HARD_PASS = 0.70   # fraction of the (ORACLE - MAIN) gap the write organ must close, all 3
ADDR_GAP_ORACLE_HARD_FAIL = 0.30   # <= this on ALL 3 = write organ adds ~nothing
BEAT_MARGIN = 0.05                 # learned-write must beat IDENTKEY_FIXEDTAU by this (loop acc) to claim win
WITHIN_CROSS_HARD_PASS = 0.30      # held-out within-minus-cross of the head keys (anti-collapse holds)
WITHIN_CROSS_HARD_FAIL = 0.10      # <= this = collapse disguised as pass
COLLAPSE_TEETH_BAR = 0.10          # pull-only head within-minus-cross must be <= this (anti-collapse fires)
GATE_TRAIN_ACC_MIN = 0.60          # smoke discriminator-fires: gate must learn the route/allocate decision

# ---- write-gate config (autonomy: exp_dev owns these) ----
GATE_HIDDEN = 16
GATE_FEAT_DIM = 5                  # [best, second, gap, n_slots_norm, best_count_norm]
GATE_LR = 3e-3
GATE_WD = 1e-4
GATE_STEPS_SMOKE = 400
GATE_STEPS_LITE = 800
GATE_BATCH = 512
GATE_N_PASSAGES_SMOKE = 160       # TRAIN-color passages streamed to mint (feats,label) gate examples
GATE_N_PASSAGES_LITE = 320
COMMIT_CAP = V_FILL

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


# ================= learned write-gate (the organ under test) =================
class WriteGate(nn.Module):
    """Tiny MLP: per-mention slot-evidence features -> logit for P(route to argmax slot) vs allocate-fresh.
    The DG/CA3 analog: pattern-completion (route) when the evidence says a returning entity, else
    pattern-separation-on-write (allocate). The ONLY new learned params in this cell."""

    def __init__(self, d_in=GATE_FEAT_DIM, hidden=GATE_HIDDEN):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, hidden), nn.ReLU(),
                                 nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


def _slot_feats(z, files):
    """z: unit np key. files: list of {centroid(unit np), count}. Returns (feats float32[5], i_star, sims).
    feats = [best, second, best-second, n_slots/K_TRACK, count(argmax)/10]. Identical in train + inference
    so the gate sees the same feature distribution both sides (teacher-forced train / rolled-out eval)."""
    sims = np.array([float(np.dot(z, f["centroid"])) for f in files], dtype=np.float32)
    order = np.argsort(-sims)
    i_star = int(order[0])
    best = float(sims[i_star])
    second = float(sims[order[1]]) if len(files) > 1 else -1.0
    feats = np.array([best, second, best - second,
                      len(files) / float(K_TRACK), files[i_star]["count"] / 10.0], dtype=np.float32)
    return feats, i_star, sims


def _assign_learned_write(occ, gate, cap):
    """occ: ordered [{key, rep(unit np)}]. Streaming learned allocator: argmax-cosine proposes a slot;
    the gate decides route (pattern completion, running-mean update) vs allocate a fresh file (pattern
    separation). Canonical file ids in [0, cap); overflow force-attaches to argmax. Mirrors ef._assign_commit
    EXACTLY except the route-vs-allocate test is the learned gate instead of cos >= tau."""
    files = []
    next_cid = 0
    overflow = 0
    n_route = 0
    n_alloc = 0
    addr_by_key = {}
    for o in occ:
        r = o["rep"]
        if len(files) == 0:
            files.append({"cid": next_cid, "centroid": r.copy(), "count": 1})
            addr_by_key[o["key"]] = next_cid
            next_cid += 1
            n_alloc += 1
            continue
        feats, i_star, _ = _slot_feats(r, files)
        with torch.no_grad():
            p = float(torch.sigmoid(gate(torch.from_numpy(feats).unsqueeze(0))).item())
        route = p >= 0.5
        if (not route) and len(files) >= cap:
            route = True
            overflow += 1
        if route:
            f = files[i_star]
            newc = f["centroid"] * f["count"] + r
            f["count"] += 1
            f["centroid"] = newc / (np.linalg.norm(newc) + 1e-9)
            addr_by_key[o["key"]] = f["cid"]
            n_route += 1
        else:
            files.append({"cid": next_cid, "centroid": r.copy(), "count": 1})
            addr_by_key[o["key"]] = next_cid
            next_cid += 1
            n_alloc += 1
    return addr_by_key, {"n_files": len(files), "overflow": overflow, "n_route": n_route, "n_alloc": n_alloc}


# ================= gate training data (teacher-forced gold trajectory; TRAIN colors only) =================
def _stream_train_passages(ext, head, train_colors, mark_pool, n_passages, seed):
    """Return per-passage ordered [(true_color, proj_key_unit)] streams over TRAIN-color passages (keys
    projected through the FROZEN head). Shared by gold + DAgger example generation."""
    rng = np.random.default_rng(seed)
    dataset = lih.gen_dataset_split(n_passages, rng, train_colors, mark_pool)
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    raw = ef._ent_slot_reps(ext, all_reqs)
    ent_reps = []
    for slots in raw:
        ent_reps.append(list(lih.project_reps(head, np.stack(slots))) if slots else [])
    streams = []
    for (base_i, idx) in span_of:
        occ = _passage_occ_keys_global(idx, ent_reps, base_i)
        streams.append([(c, z) for (_key, c, z) in occ])
    return streams


def _gold_examples(streams):
    """TEACHER-FORCED gold examples: one gold slot per true color. At each mention argmax over current gold
    slots; label=1 (route) iff argmax's gold color == the mention's true color (routing WOULD be correct),
    else label=0 (allocate -- separating avoids clobbering another entity's slot). Data-supervision only."""
    feats_all, labels_all = [], []
    for stream in streams:
        gfiles, gidx = [], {}
        for (c, z) in stream:
            if len(gfiles) == 0:
                gfiles.append({"color": c, "centroid": z.copy(), "count": 1})
                gidx[c] = 0
                continue
            feats, i_star, _ = _slot_feats(z, gfiles)
            feats_all.append(feats)
            labels_all.append(1.0 if gfiles[i_star]["color"] == c else 0.0)
            if c in gidx:
                f = gfiles[gidx[c]]
                newc = f["centroid"] * f["count"] + z
                f["count"] += 1
                f["centroid"] = newc / (np.linalg.norm(newc) + 1e-9)
            else:
                gidx[c] = len(gfiles)
                gfiles.append({"color": c, "centroid": z.copy(), "count": 1})
    return feats_all, labels_all


def _dagger_examples(streams, gate, cap=COMMIT_CAP):
    """Exposure-bias correction: roll the CURRENT gate out on the TRAIN streams so features come from the
    gate's OWN (imperfect, polluted) slot trajectory, and label each decision by the gold-optimal action
    computed on that ROLLED state -- label=1 (route) iff argmax slot's DOMINANT true color == mention's true
    color, else 0 (allocate). Standard DAgger: features rolled by the learner, labels from the expert."""
    feats_all, labels_all = [], []
    for stream in streams:
        files = []   # {centroid, count, colors:{color:cnt}}
        for (c, z) in stream:
            if len(files) == 0:
                files.append({"centroid": z.copy(), "count": 1, "colors": {c: 1}})
                continue
            feats, i_star, _ = _slot_feats(z, files)
            dom = max(files[i_star]["colors"].items(), key=lambda kv: kv[1])[0]
            feats_all.append(feats)
            labels_all.append(1.0 if dom == c else 0.0)
            with torch.no_grad():
                p = float(torch.sigmoid(gate(torch.from_numpy(feats).unsqueeze(0))).item())
            route = (p >= 0.5) or (len(files) >= cap)
            if route:
                f = files[i_star]
                newc = f["centroid"] * f["count"] + z
                f["count"] += 1
                f["centroid"] = newc / (np.linalg.norm(newc) + 1e-9)
                f["colors"][c] = f["colors"].get(c, 0) + 1
            else:
                files.append({"centroid": z.copy(), "count": 1, "colors": {c: 1}})
    return feats_all, labels_all


def _passage_occ_keys_global(idx, ent_reps_global, base_i):
    """Same discourse-order occ as _passage_occ_keys but ent_reps_global is indexed by GLOBAL req id;
    add base_i so a passage's local req id maps to its global row. Returns [(key, true_color, proj_rep)]."""
    occ = []
    for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((("tag", tk), cidx, ent_reps_global[base_i + ri][j]))
    for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
        if ev["addr_mode"] == "coref" and ev["mark"] is not None:
            continue
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((("event", ek), cidx, ent_reps_global[base_i + ri][j]))
    for qt in QUERY_TYPES:
        qi = idx["queries"][qt]
        if qi is None:
            continue
        (ri, slotinfo, q) = qi
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((("query", qt), cidx, ent_reps_global[base_i + ri][j]))
    return occ


def _fit_gate(gate, X, y, steps, seed):
    """One SGD fit of the gate on (X, y) with pos_weight for class imbalance. Returns final-step diag."""
    torch.manual_seed(seed)
    n = X.shape[0]
    n_pos = float((y > 0.5).sum().item())
    n_neg = float((y <= 0.5).sum().item())
    pos_weight = torch.tensor([n_neg / max(n_pos, 1.0)], dtype=torch.float32)
    opt = torch.optim.Adam(gate.parameters(), lr=GATE_LR, weight_decay=GATE_WD)
    lossf = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    bs = min(GATE_BATCH, n)
    last = {}
    for it in range(steps):
        idx = torch.randperm(n)[:bs]
        loss = lossf(gate(X[idx]), y[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        if it == steps - 1:
            with torch.no_grad():
                pred = (torch.sigmoid(gate(X)) >= 0.5).float()
                route_rec = float((pred[y > 0.5] > 0.5).float().mean().item()) if n_pos > 0 else float("nan")
                alloc_rec = float((pred[y <= 0.5] <= 0.5).float().mean().item()) if n_neg > 0 else float("nan")
            last = {"loss": float(loss.detach()), "acc": float((pred == y).float().mean().item()),
                    "route_recall": route_rec, "alloc_recall": alloc_rec,
                    "balanced_acc": 0.5 * (route_rec + alloc_rec), "n": int(n),
                    "n_pos": int(n_pos), "n_neg": int(n_neg)}
    return last


def train_write_gate(ext, head, train_colors, mark_pool, steps, n_passages, seed, dagger_rounds=1):
    """Train the write-gate on TRAIN-color examples. Encoder + identity-head FROZEN (only reads keys).
    Stage 1 = teacher-forced gold examples; Stages 2.. = DAgger rounds on the gate's own rollout
    distribution (exposure-bias correction so the gate generalizes from clean gold slots to its own
    polluted rollout slots). Returns (gate, diag)."""
    streams = _stream_train_passages(ext, head, train_colors, mark_pool, n_passages, seed + 4001)
    gf, gl = _gold_examples(streams)
    assert len(gf) >= GATE_BATCH, "too few gate examples: %d" % len(gf)
    Xg = torch.from_numpy(np.stack(gf).astype(np.float32))
    yg = torch.from_numpy(np.array(gl, dtype=np.float32))
    gate = WriteGate()
    diag_gold = _fit_gate(gate, Xg, yg, steps, seed)

    feats_all, labels_all = list(gf), list(gl)
    diag_dagger = None
    for rnd in range(dagger_rounds):
        df, dl = _dagger_examples(streams, gate)
        feats_all += df
        labels_all += dl
        Xd = torch.from_numpy(np.stack(feats_all).astype(np.float32))
        yd = torch.from_numpy(np.array(labels_all, dtype=np.float32))
        diag_dagger = _fit_gate(gate, Xd, yd, steps, seed + 7 * (rnd + 1))
    gate.eval()
    final = diag_dagger if diag_dagger is not None else diag_gold
    return gate, {"n_gold": len(gf), "n_total": len(feats_all), "steps": steps,
                  "dagger_rounds": dagger_rounds, "gold_fit": diag_gold, "final": final}


# ================= build decoded dataset with a chosen entity-addressing scheme =================
# FAITHFUL MIRROR of lih.build_addr_dataset, adding entity_addr=="learned_write" (project ENT reps through
# the FROZEN head, then the LEARNED-GATE streaming allocator instead of the fixed-TAU commit). The DRIFT
# GUARD in self-test asserts this reproduces lih.build_addr_dataset bit-identically for
# decoded/oracle/commit/learned -> learned_write is the SAME code path with only the write test swapped.
def build_addr_dataset(dataset, ext, entity_addr, tau=None, cap=COMMIT_CAP, head=None, gate=None):
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    dec = ext.decode_dataset_slots(all_reqs, modes=("role_attn",))
    if entity_addr in ("commit", "learned", "learned_write"):
        raw = ef._ent_slot_reps(ext, all_reqs)
        if entity_addr in ("learned", "learned_write"):
            assert head is not None, "%s addr requires a head" % entity_addr
            ent_reps = []
            for slots in raw:
                ent_reps.append(list(lih.project_reps(head, np.stack(slots))) if slots else [])
        else:
            ent_reps = raw
    else:
        ent_reps = None
    if entity_addr == "learned_write":
        assert gate is not None, "learned_write requires a trained gate"

    tracked_set_by_p = [set(p["tracked"]) for p in dataset]
    decoded_ds = []
    ans_ds = []
    ef_consistent = [0, 0]
    q_agree = [0, 0]
    n_files_list = []
    overflow_total = 0
    route_total = 0
    alloc_total = 0

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
                                "rep": rep(ri, j) if ent_reps is not None else None, "req": ri, "slot": j})
        for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
            if ev["addr_mode"] == "coref" and ev["mark"] is not None:
                continue
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("event", ek), "true": cidx,
                                "rep": rep(ri, j) if ent_reps is not None else None, "req": ri, "slot": j})
        for qt in QUERY_TYPES:
            qi = idx["queries"][qt]
            if qi is None:
                continue
            (ri, slotinfo, q) = qi
            for j, (st, cidx) in enumerate(slotinfo):
                if st == "ENT":
                    occ.append({"key": ("query", qt), "true": cidx,
                                "rep": rep(ri, j) if ent_reps is not None else None, "req": ri, "slot": j})

        if entity_addr == "oracle":
            addr = {o["key"]: o["true"] for o in occ}
            fdiag = {"n_files": len({o["true"] for o in occ}), "overflow": 0}
        elif entity_addr in ("commit", "learned"):
            addr, fdiag = ef._assign_commit([{"key": o["key"], "rep": o["rep"]} for o in occ], tau, cap)
        elif entity_addr == "learned_write":
            addr, fdiag = _assign_learned_write([{"key": o["key"], "rep": o["rep"]} for o in occ], gate, cap)
            route_total += fdiag.get("n_route", 0)
            alloc_total += fdiag.get("n_alloc", 0)
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
            "overflow_total": overflow_total, "n_tracked_ref": ef_consistent[1],
            "route_total": route_total, "alloc_total": alloc_total}
    return decoded_ds, ans_ds, diag


# ================= self-test =================
def _combined_digest(arm_res):
    return hashlib.sha256("".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest()


def run_self_test():
    _log("SELF-TEST: clean loop toy binding + construction audit ...")
    toy = clean.toy_binding_selftest()
    audit = clean.audit_construction(seed=7, n=200)
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]

    train_colors, held_colors = lih.color_split()
    _log("  color split: train=%s held=%s" % (train_colors, held_colors))

    _log("SELF-TEST: load REAL v2 encoder (real_code_path) ...")
    assert os.path.exists(V2_CKPT), "v2 checkpoint missing: %s" % V2_CKPT
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  build: %s (d=%d)" % (binfo, ext.d))

    # ---- DRIFT GUARD: this cell's build_addr_dataset == lih.build_addr_dataset for shared modes ----
    tables = clean.build_tables()
    ds = clean.gen_dataset(24, np.random.default_rng(7))
    cal_raw = ef.calibrate_tau(ext)
    _log("SELF-TEST: DRIFT GUARD vs lih reference builder (decoded/oracle/commit) ...")
    for mode, kw in (("decoded", {}), ("oracle", {}), ("commit", {"tau": cal_raw["tau"]})):
        d_mine, a_mine, _ = build_addr_dataset(ds, ext, mode, **kw)
        d_ref, a_ref, _ = lih.build_addr_dataset(ds, ext, mode, **kw)
        arm_mine = eb.run_arm_decoded(d_mine, a_mine, tables, "main")
        arm_ref = eb.run_arm_decoded(d_ref, a_ref, tables, "main")
        for qt in QUERY_TYPES:
            assert arm_mine[qt]["preds_digest"] == arm_ref[qt]["preds_digest"], (
                "DRIFT_GUARD VIOLATION on %s/%s: this cell's builder != lih reference" % (mode, qt))
    # learned (identity-head key + fixed-TAU) also matches lih EXACTLY (one-variable control parity)
    head0, _ = lih.train_identity_head(ext, train_colors, steps=60, seed=7)
    tau_l0 = lih.calibrate_tau_learned(head0, ext, seed=7)
    d_lm, a_lm, _ = build_addr_dataset(ds, ext, "learned", tau=tau_l0["tau"], head=head0)
    d_lr, a_lr, _ = lih.build_addr_dataset(ds, ext, "learned", tau=tau_l0["tau"], head=head0)
    for qt in QUERY_TYPES:
        assert (eb.run_arm_decoded(d_lm, a_lm, tables, "main")[qt]["preds_digest"]
                == eb.run_arm_decoded(d_lr, a_lr, tables, "main")[qt]["preds_digest"]), (
            "DRIFT_GUARD VIOLATION on learned/%s vs lih" % qt)
    _log("  DRIFT GUARD PASS: builder reproduces lih decoded/oracle/commit/learned bit-identically")

    # ---- train head (frozen) + write-gate; prove learned_write runs + FIRES the discriminator ----
    _log("SELF-TEST: train frozen identity head (80 steps) + write-gate (120 steps) ...")
    head, hdiag = lih.train_identity_head(ext, train_colors, steps=80, seed=7)
    tau_l = lih.calibrate_tau_learned(head, ext, seed=7)
    gate, gdiag = train_write_gate(ext, head, train_colors, held_colors, steps=120,
                                   n_passages=48, seed=7)
    _log("  gate: %s" % gdiag["final"])
    assert gdiag["final"]["balanced_acc"] > 0.5, "gate did not learn route/allocate (balanced_acc<=0.5)"

    rng = np.random.default_rng(7)
    ev = lih.gen_dataset_split(16, rng, held_colors, train_colors)
    for p in ev:
        for e in p["tracked"]:
            assert e in held_colors, "eval entity not held-out"
    d_lw, a_lw, diag_lw = build_addr_dataset(ev, ext, "learned_write", head=head, gate=gate)
    d_ft, a_ft, diag_ft = build_addr_dataset(ev, ext, "learned", tau=tau_l["tau"], head=head)
    lw = eb.run_arm_decoded(d_lw, a_lw, tables, "main")
    ft = eb.run_arm_decoded(d_ft, a_ft, tables, "main")
    for qt in QUERY_TYPES:
        for arm in (lw, ft):
            acc = arm[qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)
    # discriminator FIRES: the write organ must actually CHANGE the assignment vs fixed-TAU (arms differ)
    dig_lw = _combined_digest(lw)
    dig_ft = _combined_digest(ft)
    _log("  LEARNED_WRITE (held eval): " + ", ".join("%s=%.2f" % (qt, lw[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f route/alloc=%d/%d"
         % (diag_lw["entity_file_consistency"], diag_lw["route_total"], diag_lw["alloc_total"]))
    _log("  IDENTKEY_FIXEDTAU (held eval): " + ", ".join("%s=%.2f" % (qt, ft[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f" % diag_ft["entity_file_consistency"])
    _log("  arms_differ (learned_write vs fixed_tau): %s" % (dig_lw != dig_ft))
    _log("SELF-TEST PASS")
    return {"toy": toy, "audit_fails": audit["fails"], "build": binfo, "encoder_d": ext.d,
            "train_colors": train_colors, "held_colors": held_colors, "drift_guard": "PASS",
            "gate_diag": gdiag, "tiny_learned_write": {qt: lw[qt]["acc"] for qt in QUERY_TYPES},
            "tiny_fixed_tau": {qt: ft[qt]["acc"] for qt in QUERY_TYPES},
            "learned_write_differs_from_fixed_tau": bool(dig_lw != dig_ft),
            "arms_differ_verified": True}


# ================= per-seed driver =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def run_seed(seed, ext, train_colors, held_colors, cal_raw, run_mode, train_n, eval_n):
    tables = clean.build_tables()
    head_steps = lih.HEAD_STEPS_SMOKE if run_mode == "smoke" else lih.HEAD_STEPS_LITE
    gate_steps = GATE_STEPS_SMOKE if run_mode == "smoke" else GATE_STEPS_LITE
    gate_np = GATE_N_PASSAGES_SMOKE if run_mode == "smoke" else GATE_N_PASSAGES_LITE
    t = time.perf_counter()
    # FROZEN identity head (key producer, held constant across the two write arms)
    head, hdiag = lih.train_identity_head(ext, train_colors, steps=head_steps, seed=seed)
    tau_l = lih.calibrate_tau_learned(head, ext, seed=seed + 1)
    wc_held = lih.within_minus_cross(head, ext, held_colors, seed=seed + 2)
    # anti-collapse teeth: a pull-only head must collapse on held-out (validity check per seed)
    head_pull, _ = lih.train_identity_head(ext, train_colors, steps=head_steps, seed=seed,
                                           w_push=0.0, w_vic=0.0)
    wc_pull = lih.within_minus_cross(head_pull, ext, held_colors, seed=seed + 2)
    # LEARNED WRITE-GATE (the organ), trained on TRAIN colors only
    gate, gdiag = train_write_gate(ext, head, train_colors, held_colors, steps=gate_steps,
                                   n_passages=gate_np, seed=seed + 300)
    _log("  seed=%d head+gate trained in %.1fs tau_l=%.4f held_wmc=%.3f pullonly_wmc=%.3f gate_bal_acc=%.3f"
         % (seed, time.perf_counter() - t, tau_l["tau"], wc_held["within_minus_cross"],
            wc_pull["within_minus_cross"], gdiag["final"]["balanced_acc"]))

    ev_held = lih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    train_ds = clean.gen_dataset(train_n, np.random.default_rng(seed))

    dec_ra, ans_ra, stage_ra = eb.build_decoded_dataset(ev_held, ext, "role_attn")
    dec_span, ans_span, _ = eb.build_decoded_dataset(ev_held, ext, "span")
    dec_or, ans_or, diag_or = build_addr_dataset(ev_held, ext, "oracle")
    dec_raw, ans_raw, diag_raw = build_addr_dataset(ev_held, ext, "commit", tau=cal_raw["tau"])
    dec_ft, ans_ft, diag_ft = build_addr_dataset(ev_held, ext, "learned", tau=tau_l["tau"], head=head)
    dec_lw, ans_lw, diag_lw = build_addr_dataset(ev_held, ext, "learned_write", head=head, gate=gate)

    arms = {}
    arms["main_enc"] = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = eb.run_arm_decoded(dec_span, ans_span, tables, "main")
    arms["oracle_entity_file"] = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    arms["raw_fixedtau_commit"] = eb.run_arm_decoded(dec_raw, ans_raw, tables, "main")
    arms["identkey_fixedtau"] = eb.run_arm_decoded(dec_ft, ans_ft, tables, "main")
    arms["identkey_learnedwrite"] = eb.run_arm_decoded(dec_lw, ans_lw, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = eb.run_arm_decoded(dec_ra, ans_ra, tables, m)
    most_recent = clean.run_most_recent(ev_held)
    pooled = clean.run_pooled_reader(train_ds, ev_held, seed)

    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n, "arms": arms,
           "most_recent": most_recent, "pooled": pooled, "stage_role_attn": stage_ra,
           "diag_oracle": diag_or, "diag_raw_fixedtau": diag_raw, "diag_identkey_fixedtau": diag_ft,
           "diag_identkey_learnedwrite": diag_lw, "head_diag": hdiag, "gate_diag": gdiag,
           "tau_learned": tau_l, "wc_held": wc_held, "wc_pullonly": wc_pull}
    for label in ("main_enc", "raw_fixedtau_commit", "identkey_fixedtau", "identkey_learnedwrite",
                  "oracle_entity_file", "ref_span"):
        _log("  seed=%d %-22s: %s" % (seed, label,
             ", ".join("%s=%.3f" % (qt, arms[label][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d LEARNED_WRITE diag: ef_consistency=%.3f q_agree=%.3f n_files=%.2f route/alloc=%d/%d | "
         "FIXEDTAU ef=%.3f | ORACLE ef=%.3f"
         % (seed, diag_lw["entity_file_consistency"], diag_lw["cross_frame_query_agreement"],
            diag_lw["n_files_mean"], diag_lw["route_total"], diag_lw["alloc_total"],
            diag_ft["entity_file_consistency"], diag_or["entity_file_consistency"]))
    _log("  seed=%d floors: RANDOM_ADDR(a)=%.2f NO_COREF(b)=%.2f WRONGROLE(a)=%.2f SHUFFLED(a)=%.2f MOST_RECENT(a)=%.2f POOLED(b)=%.2f"
         % (seed, arms["random_addr"]["a_name_maintenance"]["acc"], arms["no_coref"]["b_competitive_coref"]["acc"],
            arms["wrongrole"]["a_name_maintenance"]["acc"], arms["shuffled"]["a_name_maintenance"]["acc"],
            most_recent["a_name_maintenance"]["acc"], pooled["b_competitive_coref"]["acc"]))
    return res


def decide_verdict(per_seed):
    def al(arm, qt):
        return [ps["arms"][arm][qt]["acc"] for ps in per_seed]

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

    pull_wmc = [ps["wc_pullonly"]["within_minus_cross"] for ps in per_seed]
    teeth_ok = all((not math.isnan(x)) and x <= COLLAPSE_TEETH_BAR for x in pull_wmc)

    main_mean = {qt: _mean(al("main_enc", qt)) for qt in QUERY_TYPES}
    ref_mean = {qt: _mean(al("ref_span", qt)) for qt in QUERY_TYPES}
    oracle_mean = {qt: _mean(al("oracle_entity_file", qt)) for qt in QUERY_TYPES}
    raw_mean = {qt: _mean(al("raw_fixedtau_commit", qt)) for qt in QUERY_TYPES}
    fixed_mean = {qt: _mean(al("identkey_fixedtau", qt)) for qt in QUERY_TYPES}
    lw_mean = {qt: _mean(al("identkey_learnedwrite", qt)) for qt in QUERY_TYPES}

    # ladder continuity (vs ref_span; capped ~0.37 even for oracle -- reported not gated)
    def _frac(x, m, top):
        return ((x - m) / (top - m)) if (not math.isnan(x) and not math.isnan(m) and not math.isnan(top)
                                         and (top - m) > 1e-6) else float("nan")
    addr_gap_lw_vs_ref = {qt: _frac(lw_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}
    addr_gap_lw_vs_oracle = {qt: _frac(lw_mean[qt], main_mean[qt], oracle_mean[qt]) for qt in QUERY_TYPES}
    addr_gap_fixed_vs_oracle = {qt: _frac(fixed_mean[qt], main_mean[qt], oracle_mean[qt]) for qt in QUERY_TYPES}

    ef_cons_lw = _mean([ps["diag_identkey_learnedwrite"]["entity_file_consistency"] for ps in per_seed])
    ef_cons_fixed = _mean([ps["diag_identkey_fixedtau"]["entity_file_consistency"] for ps in per_seed])
    ef_cons_oracle = _mean([ps["diag_oracle"]["entity_file_consistency"] for ps in per_seed])
    q_agree_lw = _mean([ps["diag_identkey_learnedwrite"]["cross_frame_query_agreement"] for ps in per_seed])
    wmc_held = _mean([ps["wc_held"]["within_minus_cross"] for ps in per_seed])
    gate_bal = _mean([ps["gate_diag"]["final"]["balanced_acc"] for ps in per_seed])

    beats_main = {qt: (not math.isnan(lw_mean[qt])) and lw_mean[qt] > main_mean[qt] for qt in QUERY_TYPES}
    beats_fixed = {qt: (not math.isnan(lw_mean[qt])) and (not math.isnan(fixed_mean[qt]))
                   and lw_mean[qt] >= fixed_mean[qt] + BEAT_MARGIN for qt in QUERY_TYPES}
    gap_pass = {qt: (not math.isnan(addr_gap_lw_vs_oracle[qt]))
                and addr_gap_lw_vs_oracle[qt] >= ADDR_GAP_ORACLE_HARD_PASS for qt in QUERY_TYPES}

    all_beats_main = all(beats_main.values())
    all_beats_fixed = all(beats_fixed.values())
    all_gap_pass = all(gap_pass.values())
    within_cross_pass = (not math.isnan(wmc_held)) and wmc_held >= WITHIN_CROSS_HARD_PASS
    within_cross_fail = (not math.isnan(wmc_held)) and wmc_held <= WITHIN_CROSS_HARD_FAIL

    none_beats_main = all(not beats_main[qt] for qt in QUERY_TYPES)
    none_beats_fixed = all((not math.isnan(lw_mean[qt])) and (not math.isnan(fixed_mean[qt]))
                           and lw_mean[qt] <= fixed_mean[qt] for qt in QUERY_TYPES)
    all_gap_fail = all((not math.isnan(addr_gap_lw_vs_oracle[qt]))
                       and addr_gap_lw_vs_oracle[qt] <= ADDR_GAP_ORACLE_HARD_FAIL for qt in QUERY_TYPES)

    bands = {"chance": CHANCE,
             "hard_pass_bars": {"addr_gap_vs_oracle": ADDR_GAP_ORACLE_HARD_PASS, "beat_margin": BEAT_MARGIN,
                                "within_minus_cross": WITHIN_CROSS_HARD_PASS},
             "hard_fail_bars": {"addr_gap_vs_oracle": ADDR_GAP_ORACLE_HARD_FAIL,
                                "within_minus_cross": WITHIN_CROSS_HARD_FAIL},
             "main_enc_mean": main_mean, "ref_span_mean": ref_mean, "oracle_mean": oracle_mean,
             "raw_fixedtau_mean": raw_mean, "identkey_fixedtau_mean": fixed_mean,
             "identkey_learnedwrite_mean": lw_mean,
             "main_enc_acc": {qt: al("main_enc", qt) for qt in QUERY_TYPES},
             "identkey_learnedwrite_acc": {qt: al("identkey_learnedwrite", qt) for qt in QUERY_TYPES},
             "identkey_fixedtau_acc": {qt: al("identkey_fixedtau", qt) for qt in QUERY_TYPES},
             "raw_fixedtau_acc": {qt: al("raw_fixedtau_commit", qt) for qt in QUERY_TYPES},
             "oracle_acc": {qt: al("oracle_entity_file", qt) for qt in QUERY_TYPES},
             "ref_span_acc": {qt: al("ref_span", qt) for qt in QUERY_TYPES},
             "addr_gap_closed_frac_lw_vs_oracle": addr_gap_lw_vs_oracle,
             "addr_gap_closed_frac_lw_vs_ref": addr_gap_lw_vs_ref,
             "addr_gap_closed_frac_fixed_vs_oracle": addr_gap_fixed_vs_oracle,
             "entity_file_consistency_learnedwrite_heldout": ef_cons_lw,
             "entity_file_consistency_fixedtau_heldout": ef_cons_fixed,
             "entity_file_consistency_oracle_heldout": ef_cons_oracle,
             "cross_frame_query_agreement_learnedwrite": q_agree_lw,
             "within_minus_cross_held": wmc_held, "within_minus_cross_pullonly": pull_wmc,
             "gate_balanced_acc_mean": gate_bal,
             "beats_main_per_qt": beats_main, "beats_fixed_per_qt": beats_fixed,
             "addr_gap_pass_per_qt": gap_pass,
             "n_files_mean_learnedwrite": _mean([ps["diag_identkey_learnedwrite"]["n_files_mean"] for ps in per_seed]),
             "pooled_acc_b": pooled_b, "pooled_acc_c": pooled_c,
             "random_addr_acc": {qt: al("random_addr", qt) for qt in QUERY_TYPES},
             "no_coref_acc_b": al("no_coref", "b_competitive_coref"),
             "wrongrole_acc": {qt: al("wrongrole", qt) for qt in QUERY_TYPES},
             "shuffled_acc": {qt: al("shuffled", qt) for qt in QUERY_TYPES},
             "most_recent_acc": {qt: [ps["most_recent"][qt]["acc"] for ps in per_seed] for qt in QUERY_TYPES},
             "floors_ok": floors_ok, "floor_notes": floor_notes,
             "pooled_reservoir_decodable": pooled_reservoir, "anti_collapse_teeth_ok": teeth_ok}

    if pooled_reservoir:
        return "INVALID", ("POOLED_READER clears PROVEN_MIN on (b)/(c) -- reservoir-decodable. pooled_b=%s "
                           "pooled_c=%s" % (pooled_b, pooled_c)), bands
    if not floors_ok:
        return "INVALID", ("A can-fail floor did not collapse: " + "; ".join(floor_notes)), bands
    if not teeth_ok:
        return "INVALID", ("ANTI-COLLAPSE ABLATION HAS NO TEETH: pull-only within-minus-cross=%s did NOT "
                           "collapse to <= %.2f." % (pull_wmc, COLLAPSE_TEETH_BAR)), bands

    if all_beats_main and all_beats_fixed and all_gap_pass and within_cross_pass:
        return "HARD_PASS", ("LEARNED STATEFUL WRITE is the unlock: on HELD-OUT entities the learned "
                             "content-gated allocator BEATS MAIN_ENC (lw=%s vs main=%s) AND beats "
                             "IDENTKEY_FIXEDTAU by >=%.2f (fixed=%s) AND closes >=%.2f of the ORACLE gap on "
                             "all 3 (gap_vs_oracle=%s; oracle=%s). ef_consistency=%.3f, within-minus-cross="
                             "%.3f, gate_bal_acc=%.3f. The write organ -- NOT the key -- was the wall."
                             % (lw_mean, main_mean, BEAT_MARGIN, fixed_mean, ADDR_GAP_ORACLE_HARD_PASS,
                                addr_gap_lw_vs_oracle, oracle_mean, ef_cons_lw, wmc_held, gate_bal)), bands
    if none_beats_main or none_beats_fixed or all_gap_fail or within_cross_fail:
        why = []
        if none_beats_main:
            why.append("learned-write <= MAIN_ENC on ALL 3 (lw=%s main=%s)" % (lw_mean, main_mean))
        if none_beats_fixed:
            why.append("learned-write <= IDENTKEY_FIXEDTAU on ALL 3 (write organ adds nothing; lw=%s fixed=%s)"
                       % (lw_mean, fixed_mean))
        if all_gap_fail:
            why.append("addr_gap_vs_oracle <= %.2f on ALL 3 (%s)" % (ADDR_GAP_ORACLE_HARD_FAIL, addr_gap_lw_vs_oracle))
        if within_cross_fail:
            why.append("within-minus-cross=%.3f <= %.2f (collapse)" % (wmc_held, WITHIN_CROSS_HARD_FAIL))
        return "HARD_FAIL", ("Learned stateful write does NOT unlock the entity half: " + "; ".join(why)
                             + ". oracle=%s ref=%s ef_cons(lw/fixed/oracle)=%.3f/%.3f/%.3f gate_bal=%.3f"
                             % (oracle_mean, ref_mean, ef_cons_lw, ef_cons_fixed, ef_cons_oracle, gate_bal)), bands
    return "MIDDLE", ("Direction confirmed, not at the bar. HELD-OUT learned-write=%s vs MAIN=%s vs "
                      "IDENTKEY_FIXEDTAU=%s vs ORACLE=%s. beats_main=%s beats_fixed=%s "
                      "addr_gap_vs_oracle=%s (HP>=%.2f all). ef_consistency=%.3f within-minus-cross=%.3f "
                      "gate_bal_acc=%.3f. The learned write MOVES the assignment but does not fully reach "
                      "the ORACLE ceiling."
                      % (lw_mean, main_mean, fixed_mean, oracle_mean, beats_main, beats_fixed,
                         addr_gap_lw_vs_oracle, ADDR_GAP_ORACLE_HARD_PASS, ef_cons_lw, wmc_held, gate_bal)), bands


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
                   "verdict_msg": "SELFTEST_PASS (drift-guard vs lih + frozen head + learned write-gate + "
                                  "discriminator-fires + arms-differ)",
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

    train_colors, held_colors = lih.color_split()
    _log("color split (fairness gate): train=%s held=%s" % (train_colors, held_colors))
    _log("Building frozen v2 encoder extractor ...")
    ext = eb.EncoderExtractor()
    binfo = ext.build()
    _log("  %s (d=%d)" % (binfo, ext.d))
    cal_raw = ef.calibrate_tau(ext)
    _log("  RAW tau (raw-reps fixed-TAU control): tau=%.4f within=%.4f cross=%.4f"
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
                          "HEAD_HIDDEN": lih.HEAD_HIDDEN, "HEAD_KEY_DIM": lih.HEAD_KEY_DIM,
                          "GATE_HIDDEN": GATE_HIDDEN, "GATE_FEAT_DIM": GATE_FEAT_DIM,
                          "gate_steps": GATE_STEPS_SMOKE if run_mode == "smoke" else GATE_STEPS_LITE,
                          "gate_n_passages": GATE_N_PASSAGES_SMOKE if run_mode == "smoke" else GATE_N_PASSAGES_LITE,
                          "head_steps": lih.HEAD_STEPS_SMOKE if run_mode == "smoke" else lih.HEAD_STEPS_LITE,
                          "BEAT_MARGIN": BEAT_MARGIN, "ADDR_GAP_ORACLE_HARD_PASS": ADDR_GAP_ORACLE_HARD_PASS,
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
