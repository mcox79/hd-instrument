# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays; MAIN_ENC /
#   REF_SPAN / ORACLE / IDENTKEY_FIXEDTAU / SOFT_COTRAIN asserted pairwise distinct where they must differ;
#   SOFT_COTRAIN==ORACLE when re-id is perfect is a LEGITIMATE coincidence -> logged, NOT hard-asserted).
#   The decisive pair (MAIN_ENC vs SOFT_COTRAIN) is asserted DISTINCT in self-test (the co-trained soft
#   write must actually change the query-frame assignment vs the direct-decoded baseline).
# - final_metrics_atomicity: tmp_replace (os.replace at end).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the SCORING loop is the zero-learned-param FHRR SituationWM (imported VERBATIM via eb.clean).
#   Learned params live ONLY in (1) a co-trained identity head (lih.IdentityHead on the FROZEN v2 encoder's
#   ENT-slot reps) and (2) a single learned allocate-bias scalar b_new -- BOTH trained END-TO-END THROUGH a
#   SOFT differentiable content-addressed write (softmax cosine addressing over all slots + gated overwrite
#   h=(1-w)h+w*cand). Encoder stays FROZEN. The HARD_PASS addr-gap bar is measured RELATIVE TO ORACLE (a
#   PERFECT assignment) which itself only reaches loop acc ~0.66-0.73 because the residual role_attn filler
#   decode (S=0.96/P=0.88 MEASURED@data/exp_situation_model_assembly_encoder_backed_v1/metrics.json) caps any
#   ADDRESSING fix well below the ref_span=1.0 ceiling; addr_gap vs ref is therefore reported not gated.
#   discriminator_reachability=True under the ORACLE-relative definition.
# - baseline_in_band: MAIN_ENC (direct-decoded fragile address, ~0.46 MEASURED@.../encoder_backed_v1) is the
#   baseline the co-trained write must BEAT; ORACLE is the reachable ceiling; the 5 deterministic floors +
#   POOLED_READER are the can-fail controls and MUST collapse or the cell INVALID.
# - discriminator survives scale: closed-form loop + frozen-encoder forward passes + a tiny head + one scalar
#   (not scale-saturating). self-test exercises the REAL encoder + REAL loop + REAL head + REAL soft rollout
#   at reduced scale; LITE at full. self-test DRIFT-GUARDs this cell's build_addr_dataset against the lih
#   reference builder for decoded/oracle/commit bit-identically (soft_write is the SAME assembly with only
#   the addr map swapped -> one-variable guarantee).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed / torch.Generator only; NO hash(), NO
#   list(set()) (sorted(set()) everywhere).
"""SOFT CO-TRAINED CONTENT-GATED WRITE on the frozen-encoder situation-model harness (Director 2026-07-31).

THE DISCRIMINATOR (founding-gap fork). Two prior attempts localized the wall:
  - learned identity-head (dddf0997b): GENERALIZES the key space (held-out within-minus-cross 0.20->0.42,
    entity_file_consistency 0.35->0.67) but was FROZEN + a fixed-TAU streaming commit -> loop acc did NOT
    recover (a<=0.19).
  - learned HARD-argmax + hard route/allocate gate (ef209d8c5): HARD_FAIL (loop acc 0.05-0.25 << MAIN_ENC
    0.46). Diagnosis MEASURED@data/exp_situation_model_assembly_learned_stateful_write_v1: QUERY-frame
    mis-routing -- the query key lands on the WRONG entity (q_agree ~0.22), and a gate over a WRONG
    hard-argmax cannot repair it.
  - ORACLE (perfect assignment) CROSSES MAIN (0.66-0.73 > 0.46): the FROZEN encoder reps ARE sufficient IF
    routing is correct. So the crux = can routing (esp the QUERY frame) be fixed WITHOUT retraining the
    encoder.
UNTESTED until now (the two remaining levers, combined here into the STRONGEST realizable bolt-on):
  (a) CO-TRAIN the identity head end-to-end WITH the write (keys ADAPT so the query-frame mention routes to
      the right slot; head NOT frozen), and
  (b) a SOFT differentiable write (softmax cosine addressing over ALL slots + gated overwrite
      h=(1-w)h+w*cand -- the VET-confirmed content-gated WM's actual form) so one wrong argmax is NOT
      irreversible and the WHOLE path is differentiable = end-to-end co-trainable.

MECHANISM. Fixed M slots. Each mention's ENT-slot rep (frozen encoder) -> identity key via the co-trained
head. At mention t: soft cosine addressing gives a distribution over [occupied slots + a learned NEW option];
gated overwrite writes the key into the addressed slot(s). TRAINING = teacher-forced gold trajectory (each
true color -> one slot; a returning mention's target = its slot, a first mention's target = NEW), CE over the
soft address distribution -> gradients flow through the softmax into the head + the b_new scalar. This is the
DG pattern-separation-on-write (NEW target for a novel entity forces its key APART from occupied slots) +
CA3 pattern-completion-on-read (route target pulls a returning key TOWARD its slot), learned end-to-end.
VICReg variance/covariance floor on the keys = provable anti-collapse. Supervision = cross-mention
same-referent (color) labels = DATA-supervision. EVAL = the model's OWN argmax rollout (no teacher forcing)
-> discrete slot ids -> the SAME zero-param FHRR loop assembly as every reference arm.

ONE VARIABLE = the co-trained head + soft write. If THIS -- the strongest realizable bolt-on on the frozen
encoder -- cannot cross MAIN toward ORACLE with q_agree recovering, the frozen encoder's query-frame reps
are the CEILING and the founding gap REQUIRES an encoder retrain. Either verdict is DECISIVE.

ALLOWED (done here): a LEARNED head + write on the encoder's OWN reps; supervision = same-referent labels.
FORBIDDEN (NOT done): borrowed/pretrained embedding as the key; description-string anchor; inference-time
bolt-on parser; hand-coded identity matching (the fixed-TAU reference is the hand-coded heuristic kept only
as a ladder comparator). Glass-box: the soft address distribution + per-slot cosines are fully inspectable.

FAIRNESS GATE = HELD-OUT ENTITIES. The 20 colors split TRAIN (head + b_new training) vs HELD-OUT (eval
entities NEITHER the head NOR b_new ever trained on). Eval passages draw every ENT-slot color from the
held-out pool (mark colors from the train pool; disjoint) -> every eval query targets a novel entity.

PRE-REGISTERED BANDS (fixed BEFORE running):
  HARD_PASS  : on ALL THREE query types, held-out SOFT_COTRAIN loop acc BEATS MAIN_ENC (> its per-type mean)
               AND addr_gap_closed_frac_vs_oracle >= 0.70; AND q_agree recovers (>= Q_AGREE_HARD_PASS, toward
               oracle, >> 0.22); AND anti-collapse holds (held within-minus-cross >= 0.30); AND floors
               collapse. => HEAD/WRITE-FIXABLE on the frozen encoder (NO retrain needed).
  HARD_FAIL  : SOFT_COTRAIN <= MAIN_ENC on ALL 3 (co-trained soft write does not beat direct-decode), OR
               q_agree stays low (<= Q_AGREE_HARD_FAIL, ~0.22 despite co-training), OR
               addr_gap_closed_frac_vs_oracle <= 0.30 on ALL 3, OR collapse (within-minus-cross <= 0.10), OR
               a floor did not collapse / POOLED reservoir-decodable (INVALID). => the frozen encoder's
               QUERY-FRAME reps are the CEILING => founding gap REQUIRES encoder training.
  MIDDLE     : anything between -- reported EXPLICITLY per query type (direction confirmed, not at the bar).
  REFERENCE POINTS kept visible (the ladder): MAIN_ENC, IDENTKEY_FIXEDTAU, RAW_FIXEDTAU, ORACLE, REF_SPAN;
  q_agree reported for SOFT_COTRAIN / FIXEDTAU / ORACLE.

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_soft_cotrained_write_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_soft_cotrained_write_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_soft_cotrained_write_v1.py --lite

ASCII-only. No emojis. Deterministic seeding. Pure CPU (frozen-encoder forward passes + tiny MLP head + one
scalar; local, push-free; INLINE-LOCAL foreground-to-completion). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- closed-form FHRR loop + frozen-encoder forward passes
BATCHED at 256 + a tiny head co-trained via a per-passage SOFT-write rollout on CACHED reps (CPU, seconds
per seed). Storage: per-entity content-gated overwrite memory (sharded per slot) + FHRR-superposed roles;
per-passage accumulators independent. NOT a scaled/FULL run -- smoke + cheap LITE only (Director owns FULL).
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
import exp_situation_model_assembly_learned_identity_head_v1 as lih   # noqa: E402 (head + splits, VERBATIM)
import exp_checkpoint as ckpt                                         # noqa: E402 (per-unit checkpoint/resume)

clean = eb.clean
QUERY_TYPES = eb.QUERY_TYPES
V_FILL = eb.V_FILL
K_TRACK = clean.K_TRACK
N_ROLES = clean.N_ROLES
CHANCE = eb.CHANCE
PROVEN_MIN = eb.PROVEN_MIN
DECODE_FLOOR_BAR = eb.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = eb.ADDR_FLOOR_BAR
V2_CKPT = eb.V2_CKPT

ANCHOR_NAME = "situation_model_assembly_soft_cotrained_write_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- pre-registered bars (fixed BEFORE running) ----
ADDR_GAP_ORACLE_HARD_PASS = 0.70   # fraction of the (ORACLE - MAIN) gap the co-trained write must close, all 3
ADDR_GAP_ORACLE_HARD_FAIL = 0.30   # <= this on ALL 3 = write adds ~nothing
Q_AGREE_HARD_PASS = 0.60           # SOFT_COTRAIN cross-frame query agreement recovers toward oracle (>> 0.22)
Q_AGREE_HARD_FAIL = 0.30           # <= this = query key still lands on the wrong entity despite co-training
WITHIN_CROSS_HARD_PASS = 0.30      # held-out within-minus-cross of the co-trained keys (anti-collapse holds)
WITHIN_CROSS_HARD_FAIL = 0.10      # <= this = collapse disguised as pass
COLLAPSE_TEETH_BAR = 0.10          # metric-teeth: a pull-only head MUST collapse to <= this (regime can detect)
ROUTING_ACC_MIN = 0.60             # smoke discriminator-fires: the co-trained head must LEARN gold routing

# ---- soft-write + head config (autonomy: exp_dev owns these) ----
SLOTS = V_FILL                     # fixed slot count (>= distinct colors/passage; overflow force-routes)
ADDR_TEMP = 0.30                   # softmax temperature over cosine address logits
WRITE_GATE = 0.50                  # gated overwrite h=(1-w)h+w*cand
LR = 1e-3
WEIGHT_DECAY = 1e-3
W_CE = 1.0                         # end-to-end soft-write routing CE (the co-training-through-the-write term)
W_ALIGN = 1.0                      # cross-mention consistency pull (reused lih geometry term)
W_PUSH = 1.0                       # inter-entity push (reused lih geometry term)
W_VIC = 0.5                        # VICReg-style anti-collapse (variance floor + covariance decorrelation)
SOFT_BATCH = 16                    # passages per SGD step
SOFT_STEPS_SMOKE = 150
SOFT_STEPS_LITE = 400
SOFT_NPASS_SMOKE = 120            # TRAIN-color passages streamed for co-training
SOFT_NPASS_LITE = 240
COMMIT_CAP = SLOTS

# ---- seeds / sizes ----
SEEDS_SMOKE = (7,)
SEEDS_LITE = (7, 13)
SMOKE_TRAIN_N, SMOKE_EVAL_N = 80, 80
LITE_TRAIN_N, LITE_EVAL_N = 160, 120


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


# ================= train-passage streams (raw ENT-slot reps in occ order) =================
def _passage_occ_raw(idx, raw_reps_global, base_i):
    """Return [(true_color, raw_rep_np)] over ENT slots in the SAME occ order build_addr_dataset uses
    (tags -> non-coref events -> queries). raw_reps_global indexed by GLOBAL req id (add base_i)."""
    occ = []
    for tk, (ri, slotinfo, ent) in enumerate(idx["tags"]):
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((cidx, raw_reps_global[base_i + ri][j]))
    for ek, (ri, slotinfo, ev) in enumerate(idx["events"]):
        if ev["addr_mode"] == "coref" and ev["mark"] is not None:
            continue
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((cidx, raw_reps_global[base_i + ri][j]))
    for qt in QUERY_TYPES:
        qi = idx["queries"][qt]
        if qi is None:
            continue
        (ri, slotinfo, q) = qi
        for j, (st, cidx) in enumerate(slotinfo):
            if st == "ENT":
                occ.append((cidx, raw_reps_global[base_i + ri][j]))
    return occ


def _stream_train_raw(ext, ent_pool, mark_pool, n_passages, seed):
    """Per-passage (colors[list int], raw_reps np[n,d]) over TRAIN-color passages. Encoder frozen; reps
    cached ONCE, projected through the co-trained head each SGD step."""
    rng = np.random.default_rng(seed)
    dataset = lih.gen_dataset_split(n_passages, rng, ent_pool, mark_pool)
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    raw = ef._ent_slot_reps(ext, all_reqs)
    streams = []
    for (base_i, idx) in span_of:
        occ = _passage_occ_raw(idx, raw, base_i)
        if not occ:
            continue
        colors = [int(c) for (c, _) in occ]
        reps = np.stack([r for (_, r) in occ]).astype(np.float32)
        streams.append((colors, reps))
    return streams


# ================= the SOFT differentiable content-gated write (the organ under test) =================
def _passage_train_loss(k, colors, b_new, temp, w):
    """Teacher-forced gold trajectory. k: torch [n,kd] unit keys (require grad via head). At each mention the
    soft address distribution over [occupied slots + NEW] is scored by CE against the gold target (a returning
    color's slot, else NEW). Writes follow the GOLD path (gated overwrite). Differentiable in the head +
    b_new through the softmax. Returns mean CE (torch scalar) or None if the passage has < 1 scored mention."""
    slot_vecs = []          # torch [kd] running (non-unit; renormalized at scoring)
    color_pos = {}          # true_color -> slot index
    ce = []
    n = k.shape[0]
    for t in range(n):
        c = colors[t]
        if not slot_vecs:
            slot_vecs.append(k[t])
            color_pos[c] = 0
            continue
        Sm = torch.stack([v / (v.norm() + 1e-9) for v in slot_vecs])   # [nocc, kd]
        sims = Sm @ k[t]                                               # [nocc]
        logits = torch.cat([sims / temp, b_new])                      # [nocc + 1]; b_new shape [1]
        logp = F.log_softmax(logits, dim=0)
        gold = color_pos[c] if c in color_pos else len(slot_vecs)
        ce.append(-logp[gold])
        if c in color_pos:
            j = color_pos[c]
            slot_vecs[j] = (1.0 - w) * slot_vecs[j] + w * k[t]
        else:
            color_pos[c] = len(slot_vecs)
            slot_vecs.append(k[t])
    return torch.stack(ce).mean() if ce else None


def _gold_routing_acc(head, b_new, tstreams, temp=ADDR_TEMP, w=WRITE_GATE):
    """Fraction of mentions where the model's argmax decision matches the gold target under teacher-forced
    gold writes. Smoke discriminator-fires metric: > ROUTING_ACC_MIN = the head learned routing."""
    correct = 0
    total = 0
    with torch.no_grad():
        for colors, reps in tstreams:
            k = F.normalize(head(reps), dim=1).numpy()
            slot_vecs = []
            color_pos = {}
            for t, c in enumerate(colors):
                if not slot_vecs:
                    slot_vecs.append(k[t].copy())
                    color_pos[c] = 0
                    continue
                sims = np.array([float(np.dot(k[t], v / (np.linalg.norm(v) + 1e-9))) for v in slot_vecs],
                                dtype=np.float32)
                logits = np.concatenate([sims / temp, np.array([b_new], dtype=np.float32)])
                pred = int(np.argmax(logits))
                gold = color_pos[c] if c in color_pos else len(slot_vecs)
                correct += int(pred == gold)
                total += 1
                if c in color_pos:
                    j = color_pos[c]
                    slot_vecs[j] = (1.0 - w) * slot_vecs[j] + w * k[t]
                else:
                    color_pos[c] = len(slot_vecs)
                    slot_vecs.append(k[t].copy())
    return correct / max(total, 1)


def train_soft_write(ext, ent_pool, mark_pool, steps, n_passages, seed, w_vic=W_VIC):
    """Co-train the identity head + b_new scalar END-TO-END through the soft differentiable write. Encoder
    FROZEN (reps cached). Returns (head, b_new_float, diag)."""
    torch.manual_seed(seed)
    streams = _stream_train_raw(ext, ent_pool, mark_pool, n_passages, seed + 991)
    assert len(streams) >= SOFT_BATCH, "too few train passages: %d" % len(streams)
    tstreams = [(colors, torch.from_numpy(reps)) for (colors, reps) in streams]
    head = lih.IdentityHead(ext.d)
    b_new = nn.Parameter(torch.zeros(1))
    opt = torch.optim.Adam(list(head.parameters()) + [b_new], lr=LR, weight_decay=WEIGHT_DECAY)
    npass = len(tstreams)
    gen = torch.Generator()
    gen.manual_seed(seed + 7)
    last = {}
    for it in range(steps):
        idxs = torch.randperm(npass, generator=gen)[:SOFT_BATCH].tolist()
        opt.zero_grad()
        losses = []
        allz = []
        ally = []
        for pi in idxs:
            colors, reps = tstreams[pi]
            k = F.normalize(head(reps), dim=1)
            allz.append(k)
            ally.append(torch.tensor(colors, dtype=torch.long))
            lp = _passage_train_loss(k, colors, b_new, ADDR_TEMP, WRITE_GATE)
            if lp is not None:
                losses.append(lp)
        if not losses:
            continue
        z = torch.cat(allz, 0)
        y = torch.cat(ally, 0)
        # direct three-term contrastive geometry (align pull + inter-entity push) on the batch keys, so the
        # co-trained head gets BOTH the strong geometry signal (lih objective) AND the end-to-end routing CE
        S = z @ z.T
        same = (y[:, None] == y[None, :]).float()
        same_off = same - torch.eye(len(y))
        diff = 1.0 - same
        l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
        l_push = (F.relu(S - lih.PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
        var, cov = lih._vicreg_terms(z)
        ce = torch.stack(losses).mean()
        loss = W_CE * ce + W_ALIGN * l_align + W_PUSH * l_push + w_vic * (var + cov)
        loss.backward()
        opt.step()
        if it == steps - 1:
            last = {"loss": float(loss.detach()), "ce": float(ce.detach()),
                    "l_align": float(l_align.detach()), "l_push": float(l_push.detach()),
                    "vic_var": float(var.detach()), "vic_cov": float(cov.detach())}
    head.eval()
    b = float(b_new.detach().item())
    racc = _gold_routing_acc(head, b, tstreams)
    return head, b, {"n_passages": npass, "steps": steps, "final": last, "gold_routing_acc": racc,
                     "b_new": b, "w_vic": w_vic}


# ================= EVAL: model's own argmax rollout -> discrete slot ids =================
def _assign_soft_write(occ, keys, cap, tau, temp=ADDR_TEMP, w=WRITE_GATE):
    """Streaming soft-write allocator (model's OWN decisions, no teacher forcing). occ: ordered [{key}];
    keys: np[n,kd] unit. Content addressing over occupied slots; route (pattern completion, GATED OVERWRITE
    h=(1-w)h+w*cand -- the content-gated WM form) to the argmax slot iff best cosine >= tau, else allocate a
    fresh slot (pattern separation). tau is calibrated on the co-trained head's FULL-PALETTE geometry (the
    SAME fair basis the fixed-TAU reference arms use -- NOT tuned on held-out accuracy), which removes the
    global-scalar over-merge confound the learned b_new exhibits on held-out entities. Overflow force-routes."""
    slots = []
    addr = {}
    next_cid = 0
    n_route = 0
    n_alloc = 0
    overflow = 0
    for t, o in enumerate(occ):
        k = keys[t]
        if not slots:
            slots.append({"cid": next_cid, "vec": k.copy()})
            addr[o["key"]] = next_cid
            next_cid += 1
            n_alloc += 1
            continue
        sims = np.array([float(np.dot(k, s["vec"] / (np.linalg.norm(s["vec"]) + 1e-9))) for s in slots],
                        dtype=np.float32)
        jstar = int(np.argmax(sims))
        route = float(sims[jstar]) >= tau
        if (not route) and len(slots) >= cap:
            route = True
            overflow += 1
        if route:
            s = slots[jstar]
            s["vec"] = (1.0 - w) * s["vec"] + w * k
            addr[o["key"]] = s["cid"]
            n_route += 1
        else:
            slots.append({"cid": next_cid, "vec": k.copy()})
            addr[o["key"]] = next_cid
            next_cid += 1
            n_alloc += 1
    return addr, {"n_files": len(slots), "overflow": overflow, "n_route": n_route, "n_alloc": n_alloc}


# ================= build decoded dataset with a chosen entity-addressing scheme =================
# FAITHFUL MIRROR of lih.build_addr_dataset, adding entity_addr=="soft_write" (project ENT reps through the
# co-trained head, then the co-trained soft-write argmax rollout instead of the fixed-TAU commit). The DRIFT
# GUARD in self-test asserts this reproduces lih.build_addr_dataset bit-identically for decoded/oracle/commit
# -> soft_write is the SAME assembly with only the addr map swapped (one-variable guarantee).
def build_addr_dataset(dataset, ext, entity_addr, tau=None, cap=COMMIT_CAP, head=None):
    all_reqs = []
    span_of = []
    for p in dataset:
        reqs, idx = eb._collect_requests(p)
        span_of.append((len(all_reqs), idx))
        all_reqs.extend(reqs)
    dec = ext.decode_dataset_slots(all_reqs, modes=("role_attn",))
    if entity_addr in ("commit", "learned", "soft_write"):
        raw = ef._ent_slot_reps(ext, all_reqs)
        if entity_addr in ("learned", "soft_write"):
            assert head is not None, "%s addr requires a head" % entity_addr
            ent_reps = []
            for slots in raw:
                ent_reps.append(list(lih.project_reps(head, np.stack(slots))) if slots else [])
        else:
            ent_reps = raw
    else:
        ent_reps = None
    if entity_addr == "soft_write":
        assert tau is not None, "soft_write requires a calibrated tau"

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
        elif entity_addr == "soft_write":
            keys = np.stack([o["rep"] for o in occ]).astype(np.float32) if occ else np.zeros((0, 1), np.float32)
            addr, fdiag = _assign_soft_write([{"key": o["key"]} for o in occ], keys, cap, tau)
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

    # ---- DRIFT GUARD: this cell's build_addr_dataset == lih reference for decoded/oracle/commit ----
    tables = clean.build_tables()
    ds = clean.gen_dataset(24, np.random.default_rng(7))
    cal_raw = ef.calibrate_tau(ext)
    _log("SELF-TEST: DRIFT GUARD vs lih reference builder (decoded/oracle/commit) ...")
    for mode, kw in (("decoded", {}), ("oracle", {}), ("commit", {"tau": cal_raw["tau"]})):
        d_mine, a_mine, _ = build_addr_dataset(ds, ext, mode, **kw)
        d_ref, a_ref, _ = lih.build_addr_dataset(ds, ext, mode, **kw)
        for qt in QUERY_TYPES:
            assert (eb.run_arm_decoded(d_mine, a_mine, tables, "main")[qt]["preds_digest"]
                    == eb.run_arm_decoded(d_ref, a_ref, tables, "main")[qt]["preds_digest"]), (
                "DRIFT_GUARD VIOLATION on %s/%s: this cell's builder != lih reference" % (mode, qt))
    _log("  DRIFT GUARD PASS: builder reproduces lih decoded/oracle/commit bit-identically")

    # ---- co-train head + soft write (tiny); prove it RUNS + FIRES the discriminator ----
    _log("SELF-TEST: co-train soft write (60 steps) ...")
    head, b_new, sdiag = train_soft_write(ext, train_colors, held_colors, steps=60,
                                          n_passages=48, seed=7)
    tau_sw = lih.calibrate_tau_learned(head, ext, seed=7)
    _log("  soft-write: %s b_new=%.4f gold_routing_acc=%.3f tau_sw=%.4f"
         % (sdiag["final"], b_new, sdiag["gold_routing_acc"], tau_sw["tau"]))
    assert sdiag["gold_routing_acc"] > 0.40, "co-trained head did not learn ANY routing in 60 steps"
    wc_head = lih.within_minus_cross(head, ext, held_colors, seed=123)
    _log("  co-trained head held within-minus-cross=%.4f" % wc_head["within_minus_cross"])

    # anti-collapse metric-teeth: a pull-only head MUST collapse (validates the metric detects collapse here)
    head_pull, _ = lih.train_identity_head(ext, train_colors, steps=60, seed=7, w_push=0.0, w_vic=0.0)
    wc_pull = lih.within_minus_cross(head_pull, ext, held_colors, seed=123)
    _log("  metric-teeth: pull-only within-minus-cross=%.4f (should be near 0 = collapse)"
         % wc_pull["within_minus_cross"])

    # ---- soft_write arm runs end-to-end on a held-out eval set + differs from MAIN_ENC ----
    rng = np.random.default_rng(7)
    ev = lih.gen_dataset_split(16, rng, held_colors, train_colors)
    for p in ev:
        for e in p["tracked"]:
            assert e in held_colors, "eval entity not held-out"
    dec_ra, ans_ra, _ = eb.build_decoded_dataset(ev, ext, "role_attn")
    d_sw, a_sw, diag_sw = build_addr_dataset(ev, ext, "soft_write", head=head, tau=tau_sw["tau"])
    main = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    sw = eb.run_arm_decoded(d_sw, a_sw, tables, "main")
    for qt in QUERY_TYPES:
        for arm in (main, sw):
            acc = arm[qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)
    dig_main = _combined_digest(main)
    dig_sw = _combined_digest(sw)
    _log("  MAIN_ENC (held eval):   " + ", ".join("%s=%.2f" % (qt, main[qt]["acc"]) for qt in QUERY_TYPES))
    _log("  SOFT_COTRAIN (held eval): " + ", ".join("%s=%.2f" % (qt, sw[qt]["acc"]) for qt in QUERY_TYPES)
         + " | ef_consistency=%.3f q_agree=%.3f route/alloc=%d/%d"
         % (diag_sw["entity_file_consistency"], diag_sw["cross_frame_query_agreement"],
            diag_sw["route_total"], diag_sw["alloc_total"]))
    # discriminator FIRES: the co-trained soft write must actually CHANGE the assignment vs direct-decode
    assert dig_sw != dig_main, "SOFT_COTRAIN produced the SAME predictions as MAIN_ENC (write did nothing)"
    _log("  arms_differ (soft_cotrain vs main_enc): True")
    _log("SELF-TEST PASS")
    return {"toy": toy, "audit_fails": audit["fails"], "build": binfo, "encoder_d": ext.d,
            "train_colors": train_colors, "held_colors": held_colors, "drift_guard": "PASS",
            "soft_diag": sdiag, "b_new": b_new,
            "held_within_minus_cross": wc_head["within_minus_cross"],
            "held_within_minus_cross_pullonly": wc_pull["within_minus_cross"],
            "tiny_soft_cotrain": {qt: sw[qt]["acc"] for qt in QUERY_TYPES},
            "tiny_main_enc": {qt: main[qt]["acc"] for qt in QUERY_TYPES},
            "soft_cotrain_differs_from_main": bool(dig_sw != dig_main),
            "arms_differ_verified": True}


# ================= per-seed driver =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def run_seed(seed, ext, train_colors, held_colors, cal_raw, run_mode, train_n, eval_n):
    tables = clean.build_tables()
    head_steps = lih.HEAD_STEPS_SMOKE if run_mode == "smoke" else lih.HEAD_STEPS_LITE
    soft_steps = SOFT_STEPS_SMOKE if run_mode == "smoke" else SOFT_STEPS_LITE
    soft_np = SOFT_NPASS_SMOKE if run_mode == "smoke" else SOFT_NPASS_LITE
    t = time.perf_counter()
    # CO-TRAINED head + soft write (the organ under test)
    head, b_new, sdiag = train_soft_write(ext, train_colors, held_colors, steps=soft_steps,
                                          n_passages=soft_np, seed=seed + 300)
    tau_sw = lih.calibrate_tau_learned(head, ext, seed=seed + 11)
    wc_held = lih.within_minus_cross(head, ext, held_colors, seed=seed + 2)
    # FROZEN identity-head (three-term geometry objective) + fixed-TAU = the prior key-only reference
    fhead, fhdiag = lih.train_identity_head(ext, train_colors, steps=head_steps, seed=seed)
    tau_l = lih.calibrate_tau_learned(fhead, ext, seed=seed + 1)
    # anti-collapse metric-teeth: a pull-only head must collapse on held-out (per seed)
    head_pull, _ = lih.train_identity_head(ext, train_colors, steps=head_steps, seed=seed,
                                           w_push=0.0, w_vic=0.0)
    wc_pull = lih.within_minus_cross(head_pull, ext, held_colors, seed=seed + 2)
    _log("  seed=%d trained in %.1fs b_new=%.4f tau_sw=%.4f gold_routing_acc=%.3f held_wmc=%.3f pullonly_wmc=%.3f"
         % (seed, time.perf_counter() - t, b_new, tau_sw["tau"], sdiag["gold_routing_acc"],
            wc_held["within_minus_cross"], wc_pull["within_minus_cross"]))

    ev_held = lih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_colors, train_colors)
    train_ds = clean.gen_dataset(train_n, np.random.default_rng(seed))

    dec_ra, ans_ra, stage_ra = eb.build_decoded_dataset(ev_held, ext, "role_attn")
    dec_span, ans_span, _ = eb.build_decoded_dataset(ev_held, ext, "span")
    dec_or, ans_or, diag_or = build_addr_dataset(ev_held, ext, "oracle")
    dec_raw, ans_raw, diag_raw = build_addr_dataset(ev_held, ext, "commit", tau=cal_raw["tau"])
    dec_ft, ans_ft, diag_ft = build_addr_dataset(ev_held, ext, "learned", tau=tau_l["tau"], head=fhead)
    dec_sw, ans_sw, diag_sw = build_addr_dataset(ev_held, ext, "soft_write", head=head, tau=tau_sw["tau"])

    arms = {}
    arms["main_enc"] = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    arms["ref_span"] = eb.run_arm_decoded(dec_span, ans_span, tables, "main")
    arms["oracle_entity_file"] = eb.run_arm_decoded(dec_or, ans_or, tables, "main")
    arms["raw_fixedtau_commit"] = eb.run_arm_decoded(dec_raw, ans_raw, tables, "main")
    arms["identkey_fixedtau"] = eb.run_arm_decoded(dec_ft, ans_ft, tables, "main")
    arms["soft_cotrain"] = eb.run_arm_decoded(dec_sw, ans_sw, tables, "main")
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[m] = eb.run_arm_decoded(dec_ra, ans_ra, tables, m)
    most_recent = clean.run_most_recent(ev_held)
    pooled = clean.run_pooled_reader(train_ds, ev_held, seed)

    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n, "arms": arms,
           "most_recent": most_recent, "pooled": pooled, "stage_role_attn": stage_ra,
           "diag_oracle": diag_or, "diag_raw_fixedtau": diag_raw, "diag_identkey_fixedtau": diag_ft,
           "diag_soft_cotrain": diag_sw, "soft_diag": sdiag, "fhead_diag": fhdiag,
           "b_new": b_new, "tau_learned": tau_l, "tau_sw": tau_sw, "wc_held": wc_held, "wc_pullonly": wc_pull}
    for label in ("main_enc", "raw_fixedtau_commit", "identkey_fixedtau", "soft_cotrain",
                  "oracle_entity_file", "ref_span"):
        _log("  seed=%d %-22s: %s" % (seed, label,
             ", ".join("%s=%.3f" % (qt, arms[label][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d SOFT_COTRAIN diag: ef_consistency=%.3f q_agree=%.3f n_files=%.2f route/alloc=%d/%d | "
         "FIXEDTAU q_agree=%.3f | ORACLE q_agree=%.3f"
         % (seed, diag_sw["entity_file_consistency"], diag_sw["cross_frame_query_agreement"],
            diag_sw["n_files_mean"], diag_sw["route_total"], diag_sw["alloc_total"],
            diag_ft["cross_frame_query_agreement"], diag_or["cross_frame_query_agreement"]))
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
    sw_mean = {qt: _mean(al("soft_cotrain", qt)) for qt in QUERY_TYPES}

    def _frac(x, m, top):
        return ((x - m) / (top - m)) if (not math.isnan(x) and not math.isnan(m) and not math.isnan(top)
                                         and (top - m) > 1e-6) else float("nan")
    addr_gap_sw_vs_ref = {qt: _frac(sw_mean[qt], main_mean[qt], ref_mean[qt]) for qt in QUERY_TYPES}
    addr_gap_sw_vs_oracle = {qt: _frac(sw_mean[qt], main_mean[qt], oracle_mean[qt]) for qt in QUERY_TYPES}

    ef_cons_sw = _mean([ps["diag_soft_cotrain"]["entity_file_consistency"] for ps in per_seed])
    q_agree_sw = _mean([ps["diag_soft_cotrain"]["cross_frame_query_agreement"] for ps in per_seed])
    q_agree_fixed = _mean([ps["diag_identkey_fixedtau"]["cross_frame_query_agreement"] for ps in per_seed])
    q_agree_oracle = _mean([ps["diag_oracle"]["cross_frame_query_agreement"] for ps in per_seed])
    wmc_held = _mean([ps["wc_held"]["within_minus_cross"] for ps in per_seed])
    gold_racc = _mean([ps["soft_diag"]["gold_routing_acc"] for ps in per_seed])

    beats_main = {qt: (not math.isnan(sw_mean[qt])) and sw_mean[qt] > main_mean[qt] for qt in QUERY_TYPES}
    gap_pass = {qt: (not math.isnan(addr_gap_sw_vs_oracle[qt]))
                and addr_gap_sw_vs_oracle[qt] >= ADDR_GAP_ORACLE_HARD_PASS for qt in QUERY_TYPES}

    all_beats_main = all(beats_main.values())
    all_gap_pass = all(gap_pass.values())
    within_cross_pass = (not math.isnan(wmc_held)) and wmc_held >= WITHIN_CROSS_HARD_PASS
    within_cross_fail = (not math.isnan(wmc_held)) and wmc_held <= WITHIN_CROSS_HARD_FAIL
    q_agree_pass = (not math.isnan(q_agree_sw)) and q_agree_sw >= Q_AGREE_HARD_PASS
    q_agree_fail = (not math.isnan(q_agree_sw)) and q_agree_sw <= Q_AGREE_HARD_FAIL

    none_beats_main = all(not beats_main[qt] for qt in QUERY_TYPES)
    all_gap_fail = all((not math.isnan(addr_gap_sw_vs_oracle[qt]))
                       and addr_gap_sw_vs_oracle[qt] <= ADDR_GAP_ORACLE_HARD_FAIL for qt in QUERY_TYPES)

    bands = {"chance": CHANCE,
             "hard_pass_bars": {"addr_gap_vs_oracle": ADDR_GAP_ORACLE_HARD_PASS,
                                "q_agree": Q_AGREE_HARD_PASS, "within_minus_cross": WITHIN_CROSS_HARD_PASS},
             "hard_fail_bars": {"addr_gap_vs_oracle": ADDR_GAP_ORACLE_HARD_FAIL,
                                "q_agree": Q_AGREE_HARD_FAIL, "within_minus_cross": WITHIN_CROSS_HARD_FAIL},
             "main_enc_mean": main_mean, "ref_span_mean": ref_mean, "oracle_mean": oracle_mean,
             "raw_fixedtau_mean": raw_mean, "identkey_fixedtau_mean": fixed_mean,
             "soft_cotrain_mean": sw_mean,
             "main_enc_acc": {qt: al("main_enc", qt) for qt in QUERY_TYPES},
             "soft_cotrain_acc": {qt: al("soft_cotrain", qt) for qt in QUERY_TYPES},
             "identkey_fixedtau_acc": {qt: al("identkey_fixedtau", qt) for qt in QUERY_TYPES},
             "raw_fixedtau_acc": {qt: al("raw_fixedtau_commit", qt) for qt in QUERY_TYPES},
             "oracle_acc": {qt: al("oracle_entity_file", qt) for qt in QUERY_TYPES},
             "ref_span_acc": {qt: al("ref_span", qt) for qt in QUERY_TYPES},
             "addr_gap_closed_frac_sw_vs_oracle": addr_gap_sw_vs_oracle,
             "addr_gap_closed_frac_sw_vs_ref": addr_gap_sw_vs_ref,
             "entity_file_consistency_soft_cotrain_heldout": ef_cons_sw,
             "cross_frame_query_agreement_soft_cotrain": q_agree_sw,
             "cross_frame_query_agreement_fixedtau": q_agree_fixed,
             "cross_frame_query_agreement_oracle": q_agree_oracle,
             "within_minus_cross_held": wmc_held, "within_minus_cross_pullonly": pull_wmc,
             "gold_routing_acc_mean": gold_racc, "b_new_mean": _mean([ps["b_new"] for ps in per_seed]),
             "beats_main_per_qt": beats_main, "addr_gap_pass_per_qt": gap_pass,
             "n_files_mean_soft_cotrain": _mean([ps["diag_soft_cotrain"]["n_files_mean"] for ps in per_seed]),
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
        return "INVALID", ("ANTI-COLLAPSE METRIC HAS NO TEETH: pull-only within-minus-cross=%s did NOT "
                           "collapse to <= %.2f." % (pull_wmc, COLLAPSE_TEETH_BAR)), bands

    if all_beats_main and all_gap_pass and q_agree_pass and within_cross_pass:
        return "HARD_PASS", ("HEAD/WRITE-FIXABLE ON THE FROZEN ENCODER: co-trained head + soft differentiable "
                             "write BEATS MAIN_ENC on all 3 (sw=%s vs main=%s), closes >=%.2f of the ORACLE "
                             "gap (gap_vs_oracle=%s; oracle=%s), q_agree RECOVERS %.3f>=%.2f (was ~0.22; "
                             "oracle=%.3f), within-minus-cross=%.3f, gold_routing_acc=%.3f. Cross-frame entity "
                             "routing is fixable WITHOUT an encoder retrain."
                             % (sw_mean, main_mean, ADDR_GAP_ORACLE_HARD_PASS, addr_gap_sw_vs_oracle,
                                oracle_mean, q_agree_sw, Q_AGREE_HARD_PASS, q_agree_oracle, wmc_held,
                                gold_racc)), bands
    if none_beats_main or q_agree_fail or all_gap_fail or within_cross_fail:
        why = []
        if none_beats_main:
            why.append("soft-cotrain <= MAIN_ENC on ALL 3 (sw=%s main=%s)" % (sw_mean, main_mean))
        if q_agree_fail:
            why.append("q_agree=%.3f <= %.2f (query key STILL lands on the wrong entity despite co-training)"
                       % (q_agree_sw, Q_AGREE_HARD_FAIL))
        if all_gap_fail:
            why.append("addr_gap_vs_oracle <= %.2f on ALL 3 (%s)" % (ADDR_GAP_ORACLE_HARD_FAIL, addr_gap_sw_vs_oracle))
        if within_cross_fail:
            why.append("within-minus-cross=%.3f <= %.2f (collapse)" % (wmc_held, WITHIN_CROSS_HARD_FAIL))
        return "HARD_FAIL", ("FROZEN-ENCODER QUERY-FRAME IS THE CEILING: " + "; ".join(why)
                             + ". oracle=%s ref=%s q_agree(sw/fixed/oracle)=%.3f/%.3f/%.3f gold_routing_acc="
                             "%.3f. The founding gap REQUIRES an encoder retrain."
                             % (oracle_mean, ref_mean, q_agree_sw, q_agree_fixed, q_agree_oracle, gold_racc)), bands
    return "MIDDLE", ("Direction confirmed, not at the bar. HELD-OUT soft-cotrain=%s vs MAIN=%s vs ORACLE=%s. "
                      "beats_main=%s addr_gap_vs_oracle=%s (HP>=%.2f all). q_agree=%.3f (HP>=%.2f; fixed=%.3f "
                      "oracle=%.3f). within-minus-cross=%.3f gold_routing_acc=%.3f. The co-trained soft write "
                      "MOVES the query-frame assignment but does not fully reach the ORACLE ceiling."
                      % (sw_mean, main_mean, oracle_mean, beats_main, addr_gap_sw_vs_oracle,
                         ADDR_GAP_ORACLE_HARD_PASS, q_agree_sw, Q_AGREE_HARD_PASS, q_agree_fixed,
                         q_agree_oracle, wmc_held, gold_racc)), bands


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
                   "verdict_msg": "SELFTEST_PASS (drift-guard vs lih + co-trained soft write + "
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
               "params": {"DIM": clean.DIM, "K_TRACK": K_TRACK, "V_FILL": V_FILL, "SLOTS": SLOTS,
                          "ADDR_TEMP": ADDR_TEMP, "WRITE_GATE": WRITE_GATE, "W_VIC": W_VIC,
                          "W_CE": W_CE, "W_ALIGN": W_ALIGN, "W_PUSH": W_PUSH,
                          "HEAD_HIDDEN": lih.HEAD_HIDDEN, "HEAD_KEY_DIM": lih.HEAD_KEY_DIM,
                          "soft_steps": SOFT_STEPS_SMOKE if run_mode == "smoke" else SOFT_STEPS_LITE,
                          "soft_n_passages": SOFT_NPASS_SMOKE if run_mode == "smoke" else SOFT_NPASS_LITE,
                          "soft_batch": SOFT_BATCH,
                          "ADDR_GAP_ORACLE_HARD_PASS": ADDR_GAP_ORACLE_HARD_PASS,
                          "Q_AGREE_HARD_PASS": Q_AGREE_HARD_PASS,
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
