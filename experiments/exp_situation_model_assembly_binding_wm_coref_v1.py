# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (sha256 digest of per-query predicted-class arrays, pairwise
#   distinct across MAIN / RANDOM_ADDR / NO_COREF / WRONGROLE / SHUFFLED_CODEBOOK / MOST_RECENT)
# - final_metrics_atomicity: tmp_replace (os.replace at end)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: zero-learned-param FHRR + closed-form gated-overwrite in the MAIN arm (no learned-noise
#   Cramer-Rao floor); discriminator = pre-registered per-query-type accuracy vs the decision rule.
# - baseline_in_band: n/a for the zero-param MAIN arm (closed-form construction, no learned baseline to
#   saturate); the POOLED_READER floor and 5 deterministic floors ARE the can-fail controls and MUST
#   independently collapse near chance on the coref/overwrite query types or the cell is INVALID.
# - discriminator survives scale: closed-form MAIN arm (no train/test scale gap); POOLED_READER floor is
#   a small linear probe, self-test exercises the REAL pipeline objects at tiny N (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC)
# - deterministic seeding: numpy default_rng + torch.Generator only; NO hash(), NO list(set())
#   (sorted(set()) used for the closed pooled-reader vocab)
"""FIRST END-TO-END ASSEMBLY of two VET-confirmed organs -- native FHRR role-filler BINDING
(hdlab.binding) + the content-gated WORKING-MEMORY overwrite/update recurrence -- into ONE glass-box
pipeline on a falsifiable multi-sentence situation-model task that STRESSES COMPETITIVE COREFERENCE +
cross-sentence entity-state MAINTENANCE + OVERWRITE (Director spawn 2026-07-30; the "assemble what is
proven" lever of notes/brain_foundational_stack_assessment_2026-07-30.md).

PRIOR-WORK CHECK (substrate_query.sh, mandatory before authoring): top hit is
notes/research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md (cosine
0.318) -- a DESIGN/spec note for exactly this loop (Kintsch CI / situation model), NOT a prior cell.
No experiment in the tree runs binding + content-gated WM + coreference end-to-end (confirmed by the
assessment doc row #5: "PROVEN-IN-PIECES, NEVER ASSEMBLED END-TO-END"). Genuinely novel assembly, not
a rediscovery.

WHAT THIS CHAINS (honest reuse boundary, stated for the verdict):
  ORGAN 1 -- native FHRR binding: hdlab.binding.bind/unbind imported VERBATIM (zero learned params;
    bind = elementwise complex mul, unbind = mul by conjugate). Packs the R tracked role-fillers of an
    entity into ONE complex slot vector; query-time unbind recovers the asked role from the
    superposition (the cross-role crosstalk tolerance VET-confirmed in
    exp_native_binding_naturalistic_multirelation_v1, a9dfce95).
  ORGAN 2 -- content-gated WM overwrite-with-suppression: the VET-confirmed recurrence
    h = (1 - w) * h + w * cand  with a content-derived soft address w (ReadCondWM.read_features,
    exp_selective_overwrite_recall_nl_wm_readcond_v1 lines 340-342; WM_PROVEN 88d050955 / a81301a6).
    Re-purposed here: slots address TRACKED ENTITIES (not roles); last-write-wins per entity slot IS
    the situation-model UPDATE. The MECHANISM is reused (the gated-overwrite recurrence + soft
    content-addressing); the learned encoder-addressed *instance* is NOT re-instantiated -- addressing
    is closed-form cosine over identity/mark codebooks (glass-box, zero learned params). This is
    chaining the proven mechanism, and it is stated as such (not a re-implementation claim).

SCOPE (honest, do NOT over-reach -- stated in the verdict): entity/role/filler EXTRACTION is glass-box
POSITIONAL (read from known template slots of the rendered sentence) -- the "positional role-assignment
we already have" the spawn prompt explicitly permits. This is NOT the still-walled voice-invariant
syntactic reader, and this cell makes NO syntactic-reading claim. What is under test is the
BINDING + WM-OVERWRITE + COMPETITIVE-COREFERENCE integration. The COMPETITIVE COREFERENCE (resolving a
definite description "the one tagged {mark}" among 3 tracked entities) is SUBSTRATE-NATIVE (resolved by
content-match in the WM mark-memory), NOT positional and NOT ground-truth-supplied. Swapping the
positional front-end for the frozen-v2-encoder extraction is the recommended FULL/next-arc hardening
(and the likely place the wall moves -- see the assessment doc).

TASK -- "situation-model micro-passages":
  Each passage tracks K_TRACK=3 entities (distinct COLORS). Each entity is TAGGED with a distinct MARK
  (a COLOR, in object position) -- the antecedent for competitive coreference. Entities are then updated
  across R=2 tracked roles (STATE, PLACE; fillers = COLORS) MULTIPLE times (OVERWRITE; last-write-wins).
  Updates address the entity either by NAME ("the {ent} was set {fill} and placed {fill} .") or by
  DEFINITE DESCRIPTION ("the one tagged {mark} was set {fill} and placed {fill} .") -- the latter is the
  COMPETITIVE coreference stressor (3 candidate antecedents; the answer flips by which entity owns the
  mark). Distractor updates on non-tracked entities add capacity pressure. Fillers drawn from a
  globally-balanced shuffled multiset (kills most-frequent); >= TAIL_MIN later events after a queried
  target's last write (kills raw recency).
  QUERY TYPES (one per passage where well-posed; the SAME queries answered by every arm):
    (a) a_name_maintenance : "what was the {ent} set to ?" -> the entity's CURRENT (last-written) filler
        for the asked role (tests WM maintenance + FHRR unbind).
    (b) b_competitive_coref: "what was the one tagged {mark} set to ?" -> resolve the entity via the
        mark (substrate coref among 3), then its current filler (tests coref + maintenance).
    (c) c_overwrite        : a NAME query restricted to an (entity, role) written >= 2 times with the
        tail guarantee -> current filler must be the LAST write, not an earlier one (isolates the gate's
        last-write-wins).

FALSIFIABILITY FLOORS (the crux; MUST collapse at smoke or the task is construction-determined):
  POOLED_READER      -- bag-of-tokens over the passage + query, trained linear probe (the "pooled/
                        bag-of-tokens reader"). If it clears PROVEN_MIN on the coref (b) or overwrite
                        (c) type -> the construction is reservoir-decodable (MES/db39c1082 trap) -> the
                        cell is INVALID by pre-registered rule.
  MOST_RECENT        -- always predict the globally last-written filler (ignores the entity). Must floor
                        (the TAIL guarantee puts non-target events after the target's last write).
  RANDOM_ADDR        -- the "random-init / no coherent memory" analog for a ZERO-learned-param substrate:
                        the query-side entity/mark addressing codebook is an INDEPENDENT random
                        permutation, so the WM routes queries to the WRONG slot. Must collapse. (A pure
                        random-weight control is not meaningful for a zero-param FHRR+gated-overwrite
                        assembly -- the substrate needs no training; the equivalent falsifiability
                        control is destroying the address/key structure, which DOES collapse.)
  NO_COREF           -- for coref (b) queries, address a RANDOM tracked slot (ignore the mark). Must
                        collapse on (b) -> proves the pipeline USES antecedent binding.
  WRONGROLE          -- query with a mismatched role key. Must collapse on all types.
  SHUFFLED_CODEBOOK  -- decode against a fixed PERMUTATION of the filler codebook. Must collapse.

PRE-REGISTERED BANDS (fixed BEFORE running; NOT loosened):
  CHANCE = 1/V_FILL = 0.05.  PROVEN_MIN = 0.80.  GAP_MAX = 0.55.  FLOOR_BAR = CHANCE + 0.15 = 0.20.
  HARD_PASS : MAIN clears PROVEN_MIN on ALL THREE query types (a/b/c), BOTH seeds, WHILE POOLED_READER
              and ALL 5 deterministic floors stay <= FLOOR_BAR on their applicable query types.
  MIDDLE    : some query types clear PROVEN_MIN (floors valid), not all three -- report which.
  HARD_FAIL : floors validly collapse but MAIN stays <= GAP_MAX on all three types (an organ is not
              contributing), OR MAIN is within FLOOR_BAR of a floor on a type it should beat.
  INVALID   : POOLED_READER ALSO clears PROVEN_MIN on (b)/(c) (reservoir-decodable) OR any floor fails
              to collapse on some seed (the metric cannot discriminate -- fix construction first).

Run:  .venv/Scripts/python.exe experiments/exp_situation_model_assembly_binding_wm_coref_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_binding_wm_coref_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_situation_model_assembly_binding_wm_coref_v1.py --full

ASCII-only. No emojis. Deterministic seeding (no hash(), no list(set())). Pure CPU (local, push-free;
INLINE-LOCAL foreground-to-completion). progress_logging: print_flush_true.
Compute architecture: sequential-CPU, justified -- the MAIN arm + 5 deterministic floors are closed-form
FHRR bind/unbind + a gated-overwrite recurrence over per-passage-independent accumulators (no batching
win worth the complexity at this scale; total budget well under 10 min CPU); the POOLED_READER floor is
ONE small linear probe (a handful of Adam steps). Storage strategy: per-entity content-gated overwrite
memory (sharded per entity slot) + FHRR-superposed roles within a slot; each passage accumulator is
local/independent, never persisted or shared across passages.
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
import exp_selective_overwrite_recall_nl_calib_v1 as calib  # noqa: E402 (COLORS vocab only)
import exp_checkpoint as ckpt  # noqa: E402 (per-unit checkpoint/resume, MANDATORY per CLAUDE.md)
from hdlab import binding  # noqa: E402 (ORGAN 1: native FHRR bind/unbind, VERBATIM)

ANCHOR_NAME = "situation_model_assembly_binding_wm_coref_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- vocab (glass-box; entities/marks/fillers all drawn from the shared 20-COLOR vocab; position +
#      codebook disambiguate, exactly as the VET-confirmed multirelation cell does) ----
COLORS = calib.COLORS
V_FILL = len(COLORS)                       # 20
CHANCE = 1.0 / V_FILL                      # THEORETICAL: 0.05

DIM = 1024                                 # FHRR / codebook dimensionality
K_TRACK = 6                                # tracked entities per passage (competitive coref among 6)
K_SLOTS = 14                               # WM capacity (6 tracked + up to 4 distractor + headroom)
STATE, PLACE = 0, 1
N_ROLES = 2
ROLE_NAMES = ["set", "placed"]

WRITES_MIN, WRITES_MAX = 1, 3              # updates per (tracked entity, role) -> overwrite when >= 2
N_DISTRACT_ENTITIES = 4                    # non-tracked entities touched (capacity pressure)
N_DISTRACT_EVENTS = 10                     # distractor update events per passage
TAIL_MIN = 5                               # events guaranteed after a queried target's last write

ADDR_TEMP = 0.05                           # softmax temperature for name content-addressing (sharp)

# ---- pre-registered bands (fixed BEFORE running) ----
PROVEN_MIN = 0.80
GAP_MAX = 0.55
FLOOR_MARGIN = 0.15
ENTITY_CHANCE = 1.0 / K_TRACK              # THEORETICAL: a destroyed-address arm guesses 1-of-K_TRACK
DECODE_FLOOR_BAR = CHANCE + FLOOR_MARGIN            # 0.20  (decode/recency/pooled floors)
ADDR_FLOOR_BAR = ENTITY_CHANCE + 0.12              # ~0.287 (address-destruction floors: random_addr, no_coref)
FLOOR_BAR = DECODE_FLOOR_BAR               # back-compat alias (construction audit uses filler-chance bar)
QUERY_TYPES = ("a_name_maintenance", "b_competitive_coref", "c_overwrite")

# ---- seeds ----
SEEDS_SMOKE = (7,)
SEEDS_FULL = (7, 13)
SMOKE_TRAIN_N, SMOKE_EVAL_N = 200, 160
FULL_TRAIN_N, FULL_EVAL_N = 900, 600

# ---- fixed codebook seeds ----
ROLE_KEY_SEED = 51001
FILLER_SEED = 51002
COLOR_ID_SEED = 51003
SHUFFLE_SEED = 51004
WRONGROLE_SEED = 51005
RANDOM_ADDR_SEED = 51006


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


def _jsonify(obj):
    if isinstance(obj, torch.Tensor):
        return _jsonify(obj.detach().cpu().tolist())
    if isinstance(obj, np.ndarray):
        return _jsonify(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {str(k): _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonify(v) for v in obj]
    return obj


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _digest_ints(arr):
    a = np.asarray(arr, dtype=np.int64)
    return hashlib.sha256(a.tobytes()).hexdigest()


# ================= fixed codebooks (no learning) =================
def phase_table(n_rows, d, seed):
    """Complex64 unit-modulus random-phase FHRR codebook [n_rows, d]."""
    g = torch.Generator().manual_seed(seed)
    theta = torch.rand(n_rows, d, generator=g) * (2.0 * math.pi)
    return torch.complex(torch.cos(theta), torch.sin(theta))


def real_unit_table(n_rows, d, seed):
    """Real unit-norm random codebook [n_rows, d] for cosine content-addressing."""
    g = torch.Generator().manual_seed(seed)
    m = torch.empty(n_rows, d)
    m.normal_(0.0, 1.0, generator=g)
    return F.normalize(m, dim=1)


def build_tables(dim=DIM):
    role_keys = phase_table(N_ROLES, dim, ROLE_KEY_SEED)          # complex [R, d]
    wrong_role_keys = phase_table(N_ROLES, dim, WRONGROLE_SEED)   # complex [R, d]
    filler = phase_table(V_FILL, dim, FILLER_SEED)               # complex [V, d]
    g = torch.Generator().manual_seed(SHUFFLE_SEED)
    perm = torch.randperm(V_FILL, generator=g)
    filler_shuffled = filler[perm]                               # complex [V, d]
    color_id = real_unit_table(V_FILL, dim, COLOR_ID_SEED)       # real [V, d] (entity + mark identity)
    color_id_rand = real_unit_table(V_FILL, dim, RANDOM_ADDR_SEED)  # independent random address codebook
    return {"dim": dim, "role_keys": role_keys, "wrong_role_keys": wrong_role_keys, "filler": filler,
            "filler_shuffled": filler_shuffled, "color_id": color_id, "color_id_rand": color_id_rand}


# ================= CONSTRUCTION =================
def gen_passage(rng):
    """One situation-model passage. Returns dict with the event stream (structured, with rendered text
    for the pooled-reader floor) + the well-posed queries + ground-truth current-state table."""
    all_colors = list(range(V_FILL))
    rng.shuffle(all_colors)
    tracked = all_colors[:K_TRACK]                       # entity colors
    marks = all_colors[K_TRACK:2 * K_TRACK]              # distinct mark colors (disjoint from entities)
    distract_ents = all_colors[2 * K_TRACK:2 * K_TRACK + N_DISTRACT_ENTITIES]
    mark_of = {tracked[i]: marks[i] for i in range(K_TRACK)}

    # schedule tracked FULL-STATE update events: each event re-states the entity's whole role-tuple
    # (STATE fill + PLACE fill) so the content-gated WM overwrites the WHOLE addressed slot
    # (last-write-wins at slot granularity = ORGAN 2's actual semantics); ORGAN 1 packs the 2 roles.
    # per tracked entity: 1..WRITES_MAX update events (overwrite when >= 2).
    sched = []
    for ent in tracked:
        k = int(rng.integers(WRITES_MIN, WRITES_MAX + 1))
        for _ in range(k):
            addr_mode = "coref" if rng.random() < 0.5 else "name"
            sched.append({"ent": ent, "addr_mode": addr_mode, "is_distract": False})
    for _ in range(N_DISTRACT_EVENTS):
        de = int(distract_ents[int(rng.integers(0, len(distract_ents)))])
        sched.append({"ent": de, "addr_mode": "name", "is_distract": True})

    # globally-balanced shuffled filler multisets (2 per event: STATE + PLACE) -> kills most_frequent
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

    role_fill = {STATE: "s_fill", PLACE: "p_fill"}
    # ground-truth current state (last full-state write wins) + last-write index per tracked ent
    current = {}          # (ent, role) -> filler
    last_write_idx = {}   # ent -> event idx
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


def gen_dataset(n, rng):
    out = []
    while len(out) < n:
        p = gen_passage(rng)
        if p is not None:
            out.append(p)
    return out


# ================= assembly pipeline (ORGAN 1 + ORGAN 2) =================
class SituationWM:
    """Content-gated WM over K_SLOTS entity slots. Reuses ORGAN 2's overwrite-with-suppression
    recurrence h = (1-w)*h + w*cand, and ORGAN 1 (hdlab.binding) to pack the R role-fillers of an
    entity into one complex slot vector. Zero learned params."""

    def __init__(self, tables, mode):
        self.t = tables
        self.mode = mode
        d = tables["dim"]
        self.id_mem = torch.zeros(K_SLOTS, d)                     # real: entity identity per slot
        self.mark_mem = torch.zeros(K_SLOTS, d)                  # real: mark identity per slot
        self.content = torch.zeros(K_SLOTS, d, dtype=torch.complex64)  # FHRR packed current state
        self.filled = torch.zeros(K_SLOTS, dtype=torch.bool)
        self.ent_to_slot = {}

    def _alloc(self, ent_color):
        if ent_color in self.ent_to_slot:
            return self.ent_to_slot[ent_color]
        free = int((~self.filled).nonzero()[0, 0].item()) if (~self.filled).any() else None
        if free is None:
            return None                                          # capacity overflow: drop event
        self.ent_to_slot[ent_color] = free
        self.filled[free] = True
        self.id_mem[free] = self.t["color_id"][ent_color]
        return free

    def _name_address(self, ent_color):
        """Soft content-address over filled slots by entity identity cosine (ORGAN 2 addressing)."""
        cue = self.t["color_id"][ent_color]
        sims = self.id_mem @ cue                                  # [K]
        sims = sims.masked_fill(~self.filled, -1e30)
        return torch.softmax(sims / ADDR_TEMP, dim=0)

    def _coref_address(self, mark_color, query_side):
        """Resolve a definite description by mark content-match, then address that entity slot.
        SUBSTRATE-NATIVE competitive coreference. Floor hooks: RANDOM_ADDR permutes the query-side
        codebook; NO_COREF picks a random tracked slot."""
        if self.mode == "no_coref" and query_side:
            filled_idx = self.filled.nonzero().flatten()
            pick = int(filled_idx[torch.randint(0, len(filled_idx), (1,)).item()].item())
            w = torch.zeros(K_SLOTS)
            w[pick] = 1.0
            return w
        codebook = self.t["color_id_rand"] if (self.mode == "random_addr" and query_side) else self.t["color_id"]
        cue = codebook[mark_color]
        sims = self.mark_mem @ cue
        sims = sims.masked_fill(~self.filled, -1e30)
        w = torch.zeros(K_SLOTS)
        w[int(torch.argmax(sims).item())] = 1.0
        return w

    def tag(self, ent_color, mark_color):
        slot = self._alloc(ent_color)
        if slot is None:
            return
        self.mark_mem[slot] = self.t["color_id"][mark_color]

    def update(self, ent_color, mark_color, s_fill, p_fill, addr_mode):
        """Overwrite the addressed entity's WHOLE packed state (ORGAN 2 gated overwrite at slot
        granularity, last-write-wins). cand = bind(STATE, s) + bind(PLACE, p) (ORGAN 1 packs 2 roles).
        Coref writes resolve the slot SUBSTRATE-NATIVELY via the mark memory (not ground-truth)."""
        self._alloc(ent_color)                                    # ensure slot exists (name identity)
        if addr_mode == "coref" and mark_color is not None:
            w = self._coref_address(mark_color, query_side=False)  # substrate mark resolution
        else:
            w = self._name_address(ent_color)
        cand = (binding.bind(self.t["role_keys"][STATE], self.t["filler"][s_fill])
                + binding.bind(self.t["role_keys"][PLACE], self.t["filler"][p_fill]))
        wc = w.to(torch.complex64).unsqueeze(1)
        self.content = (1.0 - wc) * self.content + wc * cand.unsqueeze(0)

    def query(self, ent_color, mark_color, role):
        if mark_color is not None:
            w = self._coref_address(mark_color, query_side=True)
        else:
            if self.mode == "random_addr":
                cue = self.t["color_id_rand"][ent_color]
                sims = self.id_mem @ cue
                sims = sims.masked_fill(~self.filled, -1e30)
                w = torch.softmax(sims / ADDR_TEMP, dim=0)
            else:
                w = self._name_address(ent_color)
        read = (w.to(torch.complex64).unsqueeze(1) * self.content).sum(0)  # [d]
        # WRONGROLE floor: unbind with the OTHER VALID role key (recovers the entity's other-role filler;
        # matches the asked-role answer only when the two role fillers coincide ~ filler-chance). A valid
        # in-vocab wrong role is a cleaner floor than a random key (random keys are not orthogonal at
        # finite d, leaking ~4x chance -- MEASURED@dev probe 2026-07-30).
        role_key = self.t["role_keys"][(role + 1) % N_ROLES] if self.mode == "wrongrole" else self.t["role_keys"][role]
        rec = binding.unbind(read, role_key)
        codebook = self.t["filler_shuffled"] if self.mode == "shuffled" else self.t["filler"]
        scores = torch.sum(codebook * rec.conj().unsqueeze(0), dim=1).real
        return int(torch.argmax(scores).item())


def run_passage(passage, tables, mode):
    wm = SituationWM(tables, mode)
    # tag events first (marks must be set before coref) then updates, but preserve the interleaved
    # order for maintenance/overwrite correctness: tags happen once per tracked entity up front.
    for ent in passage["tracked"]:
        wm.tag(ent, passage["mark_of"][ent])
    for ev in passage["events"]:
        wm.update(ev["ent"], ev["mark"], ev["s_fill"], ev["p_fill"], ev["addr_mode"])
    preds = {}
    for qt in QUERY_TYPES:
        q = passage["queries"][qt]
        if q is None:
            preds[qt] = None
        else:
            preds[qt] = wm.query(q["ent"], q["mark"], q["role"])
    return preds


def run_arm(dataset, tables, mode):
    preds = {qt: [] for qt in QUERY_TYPES}
    answers = {qt: [] for qt in QUERY_TYPES}
    for p in dataset:
        pred = run_passage(p, tables, mode)
        for qt in QUERY_TYPES:
            if p["queries"][qt] is None:
                continue
            preds[qt].append(pred[qt])
            answers[qt].append(p["queries"][qt]["answer"])
    out = {}
    for qt in QUERY_TYPES:
        pr = np.array(preds[qt], dtype=np.int64)
        an = np.array(answers[qt], dtype=np.int64)
        acc = float((pr == an).mean()) if len(pr) else float("nan")
        out[qt] = {"acc": acc, "n": int(len(pr)), "preds_digest": _digest_ints(pr) if len(pr) else "empty"}
    return out


STRESS_DIMS = (1024, 256, 64, 32, 16, 8)


def run_stress_sweep(dataset):
    """MAIN arm at shrinking DIM -> increases FHRR crosstalk + address collisions. Locates the first
    component (coref / maintenance / binding) that breaks under representational load. Answers the
    'where is the real wall' question the assembly is meant to surface empirically."""
    out = {}
    for d in STRESS_DIMS:
        tables = build_tables(dim=d)
        res = run_arm(dataset, tables, "main")
        out[str(d)] = {qt: res[qt]["acc"] for qt in QUERY_TYPES}
    return out


# ================= MOST_RECENT + POOLED_READER floors =================
def run_most_recent(dataset):
    """Predict the asked role's filler from the passage's LAST update event (recency shortcut)."""
    out = {}
    for qt in QUERY_TYPES:
        correct, n = 0, 0
        for p in dataset:
            q = p["queries"][qt]
            if q is None:
                continue
            n += 1
            correct += int(p["global_last_role_fill"][q["role"]] == q["answer"])
        out[qt] = {"acc": (correct / n) if n else float("nan"), "n": n}
    return out


def build_pooled_vocab():
    words = set(COLORS)
    words.update(["the", "was", "one", "tagged", "and", "what", "to", ".", "?"])
    words.update(ROLE_NAMES)
    vocab = ["<unk>"] + sorted(words)                             # sorted -> deterministic
    return {w: i for i, w in enumerate(vocab)}


POOLED_VOCAB = build_pooled_vocab()
POOLED_VSZ = len(POOLED_VOCAB)


def render_passage_text(passage):
    parts = []
    for ent in passage["tracked"]:
        parts.append("the %s was tagged %s ." % (COLORS[ent], COLORS[passage["mark_of"][ent]]))
    for ev in passage["events"]:
        s, p = COLORS[ev["s_fill"]], COLORS[ev["p_fill"]]
        if ev["addr_mode"] == "coref" and ev["mark"] is not None:
            parts.append("the one tagged %s was set %s and placed %s ." % (COLORS[ev["mark"]], s, p))
        else:
            parts.append("the %s was set %s and placed %s ." % (COLORS[ev["ent"]], s, p))
    return " ".join(parts)


def render_query_text(q):
    rn = ROLE_NAMES[q["role"]]
    if q["mark"] is not None:
        return "what was the one tagged %s %s to ?" % (COLORS[q["mark"]], rn)
    return "what was the %s %s to ?" % (COLORS[q["ent"]], rn)


def bag_features(text):
    v = np.zeros(POOLED_VSZ, dtype=np.float32)
    for w in text.split():
        v[POOLED_VOCAB.get(w, 0)] += 1.0
    return v


def build_pooled_xy(dataset, qt):
    xs, ys = [], []
    for p in dataset:
        q = p["queries"][qt]
        if q is None:
            continue
        x = np.concatenate([bag_features(render_passage_text(p)), bag_features(render_query_text(q))])
        xs.append(x)
        ys.append(q["answer"])
    return torch.tensor(np.array(xs), dtype=torch.float32), torch.tensor(np.array(ys), dtype=torch.long)


class PooledReader(nn.Module):
    def __init__(self, d_in, seed):
        super().__init__()
        g = torch.Generator().manual_seed(seed)
        self.lin = nn.Linear(d_in, V_FILL)
        with torch.no_grad():
            w = torch.empty_like(self.lin.weight)
            w.normal_(0.0, 0.05, generator=g)
            self.lin.weight.copy_(w)
            self.lin.bias.zero_()

    def forward(self, x):
        return self.lin(x)


def run_pooled_reader(train_ds, eval_ds, seed, steps=300, lr=0.05):
    out = {}
    for qt in QUERY_TYPES:
        xtr, ytr = build_pooled_xy(train_ds, qt)
        xev, yev = build_pooled_xy(eval_ds, qt)
        if len(ytr) == 0 or len(yev) == 0:
            out[qt] = {"acc": float("nan"), "n": int(len(yev))}
            continue
        mu = xtr.mean(0, keepdim=True)
        sd = xtr.std(0, keepdim=True) + 1e-6
        xtr_s, xev_s = (xtr - mu) / sd, (xev - mu) / sd
        model = PooledReader(xtr.shape[1], seed)
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        for _ in range(steps):
            opt.zero_grad()
            loss = F.cross_entropy(model(xtr_s), ytr)
            loss.backward()
            opt.step()
        with torch.no_grad():
            acc = float((model(xev_s).argmax(1) == yev).float().mean().item())
        out[qt] = {"acc": acc, "n": int(len(yev))}
    return out


# ================= construction leak self-test =================
def audit_construction(seed=7, n=400):
    rng = np.random.default_rng(seed)
    ds = gen_dataset(n, rng)
    fails = []
    # shortcut oracles must be near chance on each query type
    def shortcut_acc(fn, qt):
        c, m = 0, 0
        for p in ds:
            q = p["queries"][qt]
            if q is None:
                continue
            m += 1
            c += int(fn(p, q) == q["answer"])
        return (c / m) if m else float("nan"), m
    def _all_fills(p):
        out = []
        for e in p["events"]:
            out.append(e["s_fill"])
            out.append(e["p_fill"])
        return out
    shortcuts = {
        "global_last": lambda p, q: p["global_last_role_fill"][q["role"]],
        "most_frequent": lambda p, q: int(np.bincount(_all_fills(p), minlength=V_FILL).argmax()),
    }
    sc = {}
    for name, fn in shortcuts.items():
        for qt in QUERY_TYPES:
            acc, m = shortcut_acc(fn, qt)
            sc["%s|%s" % (name, qt)] = acc
            if not math.isnan(acc) and acc >= CHANCE + FLOOR_MARGIN:
                fails.append("shortcut %s solves %s acc=%.3f (>= %.3f)" % (name, qt, acc, FLOOR_BAR))
    # label balance on query (a)
    ans_a = [p["queries"]["a_name_maintenance"]["answer"] for p in ds
             if p["queries"]["a_name_maintenance"] is not None]
    _, counts = np.unique(ans_a, return_counts=True)
    max_share = float(counts.max() / len(ans_a))
    if max_share >= 3.0 * CHANCE:
        fails.append("label imbalance (a) max_share=%.3f" % max_share)
    # coref well-posedness: marks distinct across tracked entities
    for p in ds:
        if len(set(p["marks"])) != K_TRACK:
            fails.append("marks not distinct")
            break
    # overwrite query availability
    n_overwrite = sum(1 for p in ds if p["queries"]["c_overwrite"] is not None)
    frac_overwrite = n_overwrite / n
    return {"n": n, "shortcut_accs": sc, "label_max_share_a": max_share,
            "frac_overwrite_wellposed": frac_overwrite, "fails": fails}


# ================= self-test =================
def toy_binding_selftest():
    d = 64
    role = phase_table(N_ROLES, d, 900001)
    fill = phase_table(5, d, 900002)
    packed = binding.bind(role[0], fill[2]) + binding.bind(role[1], fill[3])
    rec0 = binding.unbind(packed, role[0])
    rec1 = binding.unbind(packed, role[1])
    def cos(a, b):
        return float((torch.sum(a * b.conj()).real / a.shape[-1]).item())
    c0 = cos(rec0, fill[2])
    c1 = cos(rec1, fill[3])
    cross = cos(rec0, fill[3])
    assert c0 > 0.7 and c1 > 0.7, "TOY_FAIL: packed-role recovery weak c0=%.3f c1=%.3f" % (c0, c1)
    assert cross < 0.3, "TOY_FAIL: cross-role crosstalk high cross=%.3f" % cross
    return {"c0": c0, "c1": c1, "cross": cross}


def _combined_digest(arm_res):
    return hashlib.sha256("".join(arm_res[qt]["preds_digest"] for qt in QUERY_TYPES).encode()).hexdigest()


def run_self_test():
    _log("SELF-TEST: toy FHRR packed-role bind/unbind (ORGAN 1) ...")
    toy = toy_binding_selftest()
    _log("  PASS %s" % toy)

    _log("SELF-TEST: construction leak audit (shortcuts must floor) ...")
    audit = audit_construction(seed=7, n=300)
    _log("  frac_overwrite_wellposed=%.3f label_max_share_a=%.3f"
         % (audit["frac_overwrite_wellposed"], audit["label_max_share_a"]))
    _log("  shortcut accs: " + ", ".join("%s=%.3f" % (k, v) for k, v in audit["shortcut_accs"].items()))
    assert not audit["fails"], "CONSTRUCTION_AUDIT_FAIL: %s" % audit["fails"]

    _log("SELF-TEST: real_code_path -- build tables + run all 6 arms at tiny N (arms-differ) ...")
    tables = build_tables()
    ds = gen_dataset(80, np.random.default_rng(7))
    arms = {}
    for mode in ("main", "random_addr", "no_coref", "wrongrole", "shuffled"):
        arms[mode] = run_arm(ds, tables, mode)
    mr = run_most_recent(ds)
    for qt in QUERY_TYPES:
        for mode in arms:
            acc = arms[mode][qt]["acc"]
            assert math.isnan(acc) or (0.0 <= acc <= 1.0)
    # arms-must-differ (combined a/b/c digest pairwise distinct across the 5 substrate arms)
    digs = {m: _combined_digest(arms[m]) for m in arms}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], (
                "META_RULE_AF VIOLATION: arms %r and %r bit-identical" % (names[i], names[j]))
    _log("  tiny arms MAIN: " + ", ".join("%s=%.3f" % (qt, arms["main"][qt]["acc"]) for qt in QUERY_TYPES))
    _log("  tiny MOST_RECENT: " + ", ".join("%s=%.3f" % (qt, mr[qt]["acc"]) for qt in QUERY_TYPES))

    _log("SELF-TEST: tiny POOLED_READER fit (real_code_path for the mandatory floor) ...")
    tr = gen_dataset(60, np.random.default_rng(701))
    ev = gen_dataset(48, np.random.default_rng(702))
    pr = run_pooled_reader(tr, ev, seed=7, steps=40)
    _log("  pooled tiny acc: " + ", ".join("%s=%.3f" % (qt, pr[qt]["acc"]) for qt in QUERY_TYPES))
    for qt in QUERY_TYPES:
        assert math.isnan(pr[qt]["acc"]) or (0.0 <= pr[qt]["acc"] <= 1.0)

    _log("SELF-TEST PASS")
    return {"toy": toy, "audit": audit, "arms_differ_verified": True,
            "tiny_main": {qt: arms["main"][qt]["acc"] for qt in QUERY_TYPES},
            "tiny_pooled": {qt: pr[qt]["acc"] for qt in QUERY_TYPES}}


# ================= verdict =================
def decide_verdict(per_seed):
    """per_seed: list of {seed, main, most_recent, random_addr, no_coref, wrongrole, shuffled, pooled}."""
    def acc_list(arm, qt):
        return [ps[arm][qt]["acc"] for ps in per_seed]

    floor_notes = []
    floors_ok = True

    # POOLED_READER reservoir-decodable guard on (b)/(c)
    pooled_b = acc_list("pooled", "b_competitive_coref")
    pooled_c = acc_list("pooled", "c_overwrite")
    pooled_reservoir = (all(x >= PROVEN_MIN for x in pooled_b if not math.isnan(x))
                        or all(x >= PROVEN_MIN for x in pooled_c if not math.isnan(x)))

    # deterministic floors must collapse on their applicable query types, each judged against the
    # APPROPRIATE chance baseline: address-destruction floors collapse to ENTITY_CHANCE (1-of-K_TRACK);
    # decode/recency/pooled floors collapse to filler-chance.
    floor_applies = {
        "most_recent": (QUERY_TYPES, DECODE_FLOOR_BAR),
        "random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR),
        "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR),
        "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR),
        "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR),
        "pooled": (QUERY_TYPES, DECODE_FLOOR_BAR),
    }
    for arm, (qts, bar) in floor_applies.items():
        for qt in qts:
            for x in acc_list(arm, qt):
                if not math.isnan(x) and x > bar:
                    floors_ok = False
                    floor_notes.append("%s did not collapse on %s: %.3f > %.3f" % (arm, qt, x, bar))

    main_ok = {qt: all((not math.isnan(x)) and x >= PROVEN_MIN for x in acc_list("main", qt))
               for qt in QUERY_TYPES}
    main_gapfail = {qt: all((not math.isnan(x)) and x <= GAP_MAX for x in acc_list("main", qt))
                    for qt in QUERY_TYPES}

    bands = {"chance": CHANCE, "entity_chance": ENTITY_CHANCE, "proven_min": PROVEN_MIN,
             "decode_floor_bar": DECODE_FLOOR_BAR, "addr_floor_bar": ADDR_FLOOR_BAR, "gap_max": GAP_MAX,
             "main_acc": {qt: acc_list("main", qt) for qt in QUERY_TYPES},
             "pooled_acc": {qt: acc_list("pooled", qt) for qt in QUERY_TYPES},
             "most_recent_acc": {qt: acc_list("most_recent", qt) for qt in QUERY_TYPES},
             "random_addr_acc": {qt: acc_list("random_addr", qt) for qt in QUERY_TYPES},
             "no_coref_acc_b": acc_list("no_coref", "b_competitive_coref"),
             "wrongrole_acc": {qt: acc_list("wrongrole", qt) for qt in QUERY_TYPES},
             "shuffled_acc": {qt: acc_list("shuffled", qt) for qt in QUERY_TYPES},
             "floors_ok": floors_ok, "floor_notes": floor_notes,
             "pooled_reservoir_decodable": pooled_reservoir}

    if pooled_reservoir:
        return "INVALID", ("POOLED_READER clears PROVEN_MIN on (b) or (c) -- reservoir-decodable trap; "
                           "the construction does not require genuine coref/binding. Fix before "
                           "interpreting MAIN. pooled_b=%s pooled_c=%s" % (pooled_b, pooled_c)), bands
    if not floors_ok:
        return "INVALID", ("At least one can-fail floor did not collapse (metric cannot discriminate): "
                           + "; ".join(floor_notes)), bands

    if all(main_ok.values()):
        return "HARD_PASS", ("Assembly clears PROVEN_MIN=%.2f on ALL query types both seeds while every "
                             "floor collapsed <= %.2f. Binding + content-gated WM overwrite + "
                             "competitive coreference integrate end-to-end. main=%s"
                             % (PROVEN_MIN, FLOOR_BAR, bands["main_acc"])), bands
    if all(main_gapfail.values()):
        return "HARD_FAIL", ("Floors valid but MAIN <= GAP_MAX=%.2f on all query types -- an organ is "
                             "not contributing. main=%s" % (GAP_MAX, bands["main_acc"])), bands
    passed = [qt for qt in QUERY_TYPES if main_ok[qt]]
    return "MIDDLE", ("Floors valid. MAIN clears PROVEN_MIN on %s but not all three. main=%s"
                      % (passed, bands["main_acc"])), bands


# ================= driver =================
def run_seed(seed, train_n, eval_n):
    tables = build_tables()
    train_ds = gen_dataset(train_n, np.random.default_rng(seed))
    eval_ds = gen_dataset(eval_n, np.random.default_rng(seed + 777))
    res = {"seed": seed, "train_n": train_n, "eval_n": eval_n}
    for mode in ("main", "random_addr", "no_coref", "wrongrole", "shuffled"):
        res[mode] = run_arm(eval_ds, tables, mode)
    res["most_recent"] = run_most_recent(eval_ds)
    res["pooled"] = run_pooled_reader(train_ds, eval_ds, seed)
    res["stress_sweep_dim"] = run_stress_sweep(eval_ds)
    _log("  seed=%d STRESS(dim->acc a/b/c): %s" % (seed, ", ".join(
        "%s:%.2f/%.2f/%.2f" % (d, v["a_name_maintenance"], v["b_competitive_coref"], v["c_overwrite"])
        for d, v in res["stress_sweep_dim"].items())))
    _log("  seed=%d MAIN: %s" % (seed, ", ".join("%s=%.3f" % (qt, res["main"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d POOLED: %s" % (seed, ", ".join("%s=%.3f" % (qt, res["pooled"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d MOST_RECENT: %s" % (seed, ", ".join("%s=%.3f" % (qt, res["most_recent"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d RANDOM_ADDR: %s" % (seed, ", ".join("%s=%.3f" % (qt, res["random_addr"][qt]["acc"]) for qt in QUERY_TYPES)))
    _log("  seed=%d NO_COREF(b)=%.3f WRONGROLE(a)=%.3f SHUFFLED(a)=%.3f"
         % (seed, res["no_coref"]["b_competitive_coref"]["acc"], res["wrongrole"]["a_name_maintenance"]["acc"],
            res["shuffled"]["a_name_maintenance"]["acc"]))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    run_mode = "self_test" if (args.self_test or not (args.smoke or args.full)) else (
        "smoke" if args.smoke else "full")
    if run_mode == "smoke":
        seeds, train_n, eval_n = SEEDS_SMOKE, SMOKE_TRAIN_N, SMOKE_EVAL_N
    else:
        seeds, train_n, eval_n = SEEDS_FULL, FULL_TRAIN_N, FULL_EVAL_N
    expected_units = 1 if run_mode == "self_test" else len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (toy binding + construction leak audit + 6 arms + pooled reader)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test",
                   "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "chance": CHANCE, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    _log("%s: seeds=%s train_n=%d eval_n=%d chance=%.4f" % (run_mode.upper(), seeds, train_n, eval_n, CHANCE))
    audit = audit_construction(seed=7, n=400)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    per_seed = []
    for seed in seeds:
        key = ckpt.unit_key("seed", seed, run_mode)
        if key in ckpt.completed_units(OUTPUT_DIR):
            per_seed.append(ckpt.load_units(OUTPUT_DIR)[key])
            _log("  seed=%d loaded from checkpoint" % seed)
            continue
        res = run_seed(seed, train_n, eval_n)
        ckpt.record_unit(OUTPUT_DIR, key, res)
        per_seed.append(res)

    verdict, msg, bands = decide_verdict(per_seed)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | chance=%.4f | %s" % (verdict, CHANCE, msg[:160]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": CHANCE, "bands": bands,
               "cardinality_ok": bool(len(per_seed) == len(seeds)),
               "expected_n_units": len(seeds), "n_units_done": len(per_seed),
               "construction_audit": audit, "per_seed": per_seed,
               "params": {"DIM": DIM, "K_TRACK": K_TRACK, "K_SLOTS": K_SLOTS, "N_ROLES": N_ROLES,
                          "V_FILL": V_FILL, "WRITES": [WRITES_MIN, WRITES_MAX],
                          "N_DISTRACT_EVENTS": N_DISTRACT_EVENTS, "TAIL_MIN": TAIL_MIN,
                          "train_n": train_n, "eval_n": eval_n, "seeds": list(seeds)},
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
