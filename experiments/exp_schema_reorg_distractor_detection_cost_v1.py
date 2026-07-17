"""exp_schema_reorg_distractor_detection_cost_v1 -- close the OPEN half of the schema-reorg fix.

The prior cell (exp_schema_reorg_targeted_reindex_v1, commit 3840d0202) showed the native EDIT advantage:
on a glass-box-detected schema flip, an EXACT-ADDRESSED targeted re-index recovers the staleness at
O(affected) -- 26x fewer re-file WRITES than a full-refit, tying its accuracy. Its VET (the un-stressed-
precision + detection-O(all) flags) left the HARDER half OPEN:
  (1) the detector's PRECISION was never stressed: the prior corpus had NO distractor near-shifter entities,
      so there was ZERO false-positive opportunity -> precision=1.0 BY CONSTRUCTION.
  (2) the 26x counted re-file WRITES only; DETECTION cost (recompute touched types every ingest) was not
      measured end-to-end -- so it is unknown whether detection is bounded per-write or eats the advantage.

This cell closes BOTH, per the trigger-detection problem in
notes/research_consolidation_function_inventory_schema_reorg_2026-07-16.md (lines ~234-249): "exact addressing
tells you HOW to edit a known record cheaply, but not WHICH records a new item contradicts, without either
(i) an expensive exhaustive consistency check on every write, or (ii) a cheap incremental candidate step."

WHAT WE BUILD (glass-box, local numpy, NO LLM/atoms/push):
  * A corpus WITH DISTRACTOR WOBBLERS: entities whose subject/object type-tally WOBBLES across the AGENT/PATIENT
    boundary TRANSIENTLY but whose net/final type is UNCHANGED -- they must NOT be re-filed. Alongside GENUINE
    shifters (obj-heavy early, then a SUSTAINED subject run that permanently reorganizes PATIENT->AGENT). So the
    glass-box flip-detector faces REAL false-positive opportunity.
      - easy wobbler:  transient AGENT run length 1 (peak margin 1), final PATIENT.
      - hard wobbler:  transient AGENT run length 3 (peak margin 2), final PATIENT.
      - genuine shift: sustained AGENT run length 6 (final margin 6), final AGENT (should reindex).
  * A DETECTOR with two glass-box hysteresis knobs:
      - H = MARGIN deadband: accept a flip only when |subj_count - obj_count| >= H.
      - K = CONFIRMATION count: accept a flip only after K CONSECUTIVE touches of the entity agree on the new
        type (a sustained flip, not a transient wobble).
    NAIVE detector = (H=0, K=1): flip on any boundary crossing (the prior cell's implicit detector).

  KEY MECHANISM (measured, not assumed): peak_margin is COUPLED to the consecutive-AGENT run (each touch moves
    the margin by exactly 1), so to reach margin M an entity must have >= M consecutive same-direction touches.
    => the CONFIRMATION-count gate is the principled statistic; a MARGIN gate is a weaker proxy for the same
    "sustain" signal. We report BOTH curves and the class-conditional SEPARATION GAP (max wobbler sustain-run
    vs min genuine sustain-run) so the operating point is principled, not tuned-for-pass.

  * DETECTION COST scaling, two models contrasted across a store-size ladder:
      - INCREMENTAL (our design): per ingest, recompute the type of the (<=2) touched entities from their O(1)
        running tallies. detection_ops/write is CONSTANT vs store size N (bounded, incremental).
      - EXHAUSTIVE (the note's option-i strawman): per ingest, re-scan ALL entities seen so far to find which
        old records the new fact might contradict. detection_ops/write GROWS with N (O(all)/write -> O(N^2)).
  * END-TO-END cost = detection_ops + re-file WRITES, targeted(gated) vs full-refit, as N grows -- to answer
    the VET's question: does the EDIT advantage survive end-to-end, or does detection eat it?

METRICS (reported SEPARATELY, never blobbed):
  (a) DETECTOR precision + recall UNDER DISTRACTORS vs the gate (H curve and K curve); the class-conditional
      sustain-run separation gap; and the NAIVE-detector precision (must be < 1 or the distractor control is
      vacuous). Plus the THRASH cost: false triggers on wobblers add wasted re-file writes.
  (b) DETECTION cost scaling: incremental detection_ops/write (must be FLAT vs N) vs exhaustive (must GROW);
      and END-TO-END targeted-vs-full-refit as N grows.
  (c) does the confirmation/hysteresis gate improve precision without killing recall (naive vs gated).

PRE-REG (envelope-fail-bands; I own the bands; verdict at the LARGE store):
  HARD_PASS (glass-box detector holds high precision under distractors with a principled gate AND end-to-end
             targeted cost stays sub-full-refit as N grows):
    naive_precision < 0.90 (distractor control FIRES -- real false-positive opportunity) AND
    best_gate_precision >= 0.90 AND best_gate_recall >= 0.90 (a principled gate separates wobblers from shifters)
        with the sustain-run SEPARATION GAP > 0 (robust, not tuned) AND
    incremental detection FLAT: incr_ops_per_write(LARGE) <= 1.20 * incr_ops_per_write(SMALL) AND
    exhaustive strawman GROWS: exh_ops_per_write(LARGE) >= 2.0 * exh_ops_per_write(SMALL) AND
    re-file EDIT advantage survives+grows: targeted records FLAT across sizes AND
        full_refit_records/targeted_records(LARGE) >= 5.0 AND that ratio(LARGE) > ratio(SMALL) AND
    targeted END-TO-END < full-refit-CONTINUAL end-to-end at LARGE (advantage survives under continual freshness).
  HARD_FAIL (any):
    NO gate achieves precision >= 0.90 with recall >= 0.90 (detector cannot separate wobblers from genuine
        shifters -> trigger-detection half UNSOLVED; false-triggers on wobblers) OR
    incremental detection NOT flat (incr_ops_per_write grows with N -> detection is O(all), 26x illusory) OR
    re-file advantage collapses: full_refit_records/targeted_records(LARGE) < 2.0.
  MIDDLE otherwise (gate improves precision but recall drops below 0.90; or advantage survives continually only
    with a prominent terminal-batch-refit caveat; or detection flat but end-to-end only modestly better).

HONEST NOTE (reported regardless of tier): the SUSTAIN separation works BECAUSE genuine reorganizations are
  SUSTAINED and wobbles are TRANSIENT -- a separable statistic EXISTS here (construction proof of the gate). It
  does NOT prove real-world distractors always separate. And end-to-end: detection is optimal O(1)/write (you
  must look at each new fact once); the targeted advantage BEATS any continual-freshness full-refit, but a single
  TERMINAL batch refit (which gives up mid-stream freshness) costs one O(N) pass -- less than the per-fact
  detection sweep -- so "targeted beats full-refit end-to-end" is TRUE for continual freshness, FALSE vs a
  one-shot terminal refit. The EDIT advantage is real; detection is the (optimal) price of continual freshness.

Local numpy, NO queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors (reused from the SVO probe).
Sequential-CPU (genuine sequential dependency: the store grows fact-by-fact; belief + confirmation state depend
on the accumulated stream). Storage: SHARDED (one exact VSA vector per fact). Compute: V ~ 120 concepts,
N_DIM=1024, <=5 seeds, 4 store sizes, <=~700 facts -> wall < 20s. progress_logging=print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; NAIVE vs gated targeted vs FULL_REFIT partition-hash differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor. Detector precision/recall + cost are exact integer bookkeeping; VSA
#     decode among ~120 concepts at N=1024 3-term bundle -> within-partition decode ~1.0 (only error = misrouting).
# - baseline_in_band at smoke: NAIVE detector precision in (0.05, 0.95) (false triggers exist -> distractor
#     control FIRES) and best-gate precision > naive (the gate is the discriminator).
# - discriminator survives scale: scale IS the discriminator for the cost axis (detection-ops/write flatness +
#     cost ratio growth); run across a 4-size ladder. Precision separation is size-independent (fixed shift-set).
# - HARD_PASS strictly above floors; margins declared in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL objects (imported make_phasors/encode/decode + VSAStore +
#     simulate_gate) at tiny scale and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab; NO hash()/list(set()) for seeds/splits.
# - all numbers in comments tagged HYPOTHESIZED@prereg / THEORETICAL / MEASURED@metrics.
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
import argparse
import time
import json
import hashlib
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "schema_reorg_distractor_detection_cost_v1"
N_DIM = 1024

# reuse the proven FHRR primitives + role-filler SVO parse+bind (same imports the v1 reorg cell used).
from experiments.exp_nativelang_svo_vsa_probe_v1 import (
    make_phasors as _make_phasors,
    unbind as _unbind,
    cleanup as _cleanup,
    encode_meaning as _encode_meaning,   # M = sum_i bind(role_i, filler_i)
)

SUBJ, VERB, OBJ = 0, 1, 2
AGENT, PATIENT = "AGENT", "PATIENT"

# fixed patient pools (pure objects; never subjects -> robustly PATIENT).
FOODS = sorted(["seed", "worm", "grass", "bread", "apple", "berry", "kibble", "nut"])
PLACES = sorted(["barn", "nest", "pond", "tree", "field", "den", "burrow", "reef"])
PREY = sorted(["mouse", "rabbit", "minnow", "cricket", "moth", "vole", "shrew", "gnat"])

# boundary-entity run scripts. 'O' = an object-appearance (a stable agent eats it -> obj_count++).
# 'S' = a subject fact (entity does something to a patient -> subj_count++). The FIRST two 'O' type it PATIENT.
GENUINE_SCRIPT = ["O", "O"] + ["S"] * 8      # AGENT run 6 (subj3..8), final margin 6 AGENT  -> SHOULD reindex
HARD_SCRIPT = ["O", "O"] + ["S"] * 4 + ["O"] * 3   # AGENT run 3 (peak margin 2), final PATIENT -> should NOT
EASY_SCRIPT = ["O", "O"] + ["S"] * 3 + ["O"] * 2   # AGENT run 1 (peak margin 1), final PATIENT -> should NOT
N_GENUINE = 2
N_HARD = 2
N_EASY = 2


def build_distractor_corpus(seed, n_entities):
    """Deterministic typed corpus WITH distractor wobblers.
    Returns (facts, genuine_set, wobbler_set, boundary_set, truetype, concepts).
    facts: ordered [(s,r,o)]. genuine_set: entities that SHOULD reindex. wobbler_set: that should NOT."""
    rng = np.random.default_rng(seed)
    n_stable = max(4, n_entities - (N_GENUINE + N_HARD + N_EASY))
    stable = [f"anml{i:03d}" for i in range(n_stable)]
    genuine = [f"gshift{i}" for i in range(N_GENUINE)]
    hard = [f"whard{i}" for i in range(N_HARD)]
    easy = [f"weasy{i}" for i in range(N_EASY)]

    truetype = {}
    for a in stable:
        truetype[a] = AGENT
    for pool in (FOODS, PLACES, PREY):
        for p in pool:
            truetype[p] = PATIENT
    for e in genuine:
        truetype[e] = AGENT       # net reorganized
    for e in hard + easy:
        truetype[e] = PATIENT     # net UNCHANGED (transient wobble only)

    facts = []
    obj_cursor = [0]

    def emit_script(e, script, si):
        # object-appearances use a rotating stable agent as subject; subject facts use rotating patients.
        s_cnt = 0
        for tok in script:
            if tok == "O":
                a = stable[(si + obj_cursor[0]) % n_stable]
                obj_cursor[0] += 1
                facts.append((a, "eats", e))
            else:
                pool = (FOODS, PLACES, PREY)[s_cnt % 3]
                filler = pool[(si + s_cnt) % len(pool)]
                s_cnt += 1
                facts.append((e, ("eats", "lives_in", "chases")[(s_cnt) % 3], filler))

    # boundary entities first (contiguous per entity so consecutive touches are unambiguous).
    for i, e in enumerate(genuine):
        emit_script(e, GENUINE_SCRIPT, i)
    for i, e in enumerate(hard):
        emit_script(e, HARD_SCRIPT, i + 10)
    for i, e in enumerate(easy):
        emit_script(e, EASY_SCRIPT, i + 20)
    # stable padding (grows the store; stable agents are pure subjects -> robustly AGENT, never wobble).
    for i, a in enumerate(stable):
        facts.append((a, "eats", FOODS[i % len(FOODS)]))
        facts.append((a, "lives_in", PLACES[i % len(PLACES)]))
        facts.append((a, "chases", PREY[i % len(PREY)]))

    relations = sorted(set(r for (_, r, _) in facts))
    concepts = sorted(set(stable) | set(genuine) | set(hard) | set(easy)
                      | set(FOODS) | set(PLACES) | set(PREY) | set(relations))
    return facts, set(genuine), set(hard) | set(easy), set(genuine) | set(hard) | set(easy), truetype, concepts


def _infer(subj_c, obj_c, e):
    return AGENT if subj_c[e] > obj_c[e] else PATIENT


def simulate_gate(facts, boundary_set, H, K):
    """Pure-integer detector simulation (no VSA): apply the (H margin, K confirmation) gate to the streaming
    facts and report detected set, re-file WRITES (records_touched, incl. wobbler thrash), the two detection
    cost models, and per-entity class-conditional stats (max AGENT run + peak margin)."""
    subj_c = defaultdict(int)
    obj_c = defaultdict(int)
    belief = {}
    candidate = {}                      # e -> (candidate_type, consecutive_count)
    filed_part = defaultdict(dict)      # e -> {fact_slot: partition_type} (subject facts of e)
    detected = defaultdict(int)         # e -> number of re-file TRIGGERS (thrash count)
    records_touched = 0
    incr_ops = 0
    exhaustive_ops = 0
    seen_entities = set()
    run_len = defaultdict(int)          # current consecutive AGENT run per entity
    max_run = defaultdict(int)          # max consecutive AGENT run observed
    peak_margin = defaultdict(int)      # max (subj-obj) observed

    def reindex(e):
        nonlocal records_touched
        cur = belief[e]
        moved = 0
        for slot, part in list(filed_part[e].items()):
            if part != cur:
                filed_part[e][slot] = cur
                moved += 1
        records_touched += moved
        return moved

    for slot, (s, r, o) in enumerate(facts):
        seen_entities.add(s)
        seen_entities.add(o)
        subj_c[s] += 1
        obj_c[o] += 1
        if s not in belief:
            belief[s] = _infer(subj_c, obj_c, s)
        # file the NEW subject-fact under the subject's CURRENT belief.
        filed_part[s][slot] = belief[s]
        # EXHAUSTIVE strawman (note option-i): re-scan the WHOLE store once per write to find which old records
        # this new fact might contradict. O(all)/write -> O(n_facts^2) total. Counted once per ingest.
        exhaustive_ops += slot

        # detector on the touched entities (subject, object) that already have a belief.
        for e in (s, o):
            if e not in belief:
                continue
            incr_ops += 1                          # INCREMENTAL: O(1) tally recompute for this entity only
            new_t = _infer(subj_c, obj_c, e)
            margin = subj_c[e] - obj_c[e]
            if margin > peak_margin[e]:
                peak_margin[e] = margin
            # track consecutive AGENT run (touches where the entity currently reads AGENT).
            if new_t == AGENT:
                run_len[e] += 1
                if run_len[e] > max_run[e]:
                    max_run[e] = run_len[e]
            else:
                run_len[e] = 0
            # apply the gate: a flip must (i) clear the margin deadband H and (ii) be confirmed K consecutive.
            if new_t != belief[e] and margin >= H:
                cand_t, cnt = candidate.get(e, (None, 0))
                if cand_t == new_t:
                    cnt += 1
                else:
                    cand_t, cnt = new_t, 1
                candidate[e] = (cand_t, cnt)
                if cnt >= K:
                    belief[e] = new_t
                    detected[e] += 1
                    reindex(e)
                    candidate[e] = (None, 0)
            else:
                candidate[e] = (None, 0)           # agreement broken / inside deadband -> reset confirmation

    det_set = set(e for e, c in detected.items() if c > 0)
    return {
        "detected": det_set,
        "records_touched": records_touched,
        "incr_ops": incr_ops,
        "exhaustive_ops": exhaustive_ops,
        "n_facts": len(facts),
        "n_entities": len(seen_entities),
        "max_run": dict(max_run),
        "peak_margin": dict(peak_margin),
        "detected_counts": dict(detected),
    }


def precision_recall(det_set, genuine_set, wobbler_set):
    tp = len(det_set & genuine_set)
    fp = len(det_set & wobbler_set)
    fn = len(genuine_set - det_set)
    precision = (tp / (tp + fp)) if (tp + fp) > 0 else 1.0
    recall = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0
    return precision, recall, tp, fp, fn


# ---------------------------------------------------------------------------
# VSA store: exact SHARDED retrieval with the (H,K) gate, to CONFIRM the gated targeted arm recovers staleness
# and does NOT thrash-strand wobblers. Mirrors simulate_gate's filing/reindex but with real FHRR vectors.
# ---------------------------------------------------------------------------
class VSAStore:
    def __init__(self, C, roles, cid_idx, H, K, mode):
        self.C = C
        self.roles = roles
        self.cid_idx = cid_idx
        self.inv = {v: k for k, v in cid_idx.items()}
        self.H = H
        self.K = K
        self.mode = mode            # "no_reorg" | "targeted" | "full_refit"
        self.subj_c = defaultdict(int)
        self.obj_c = defaultdict(int)
        self.store_M = []
        self.store_T = []
        self.belief = {}
        self.candidate = {}
        self.partition = defaultdict(list)
        self.fact_part = []
        self.subj_facts = defaultdict(list)
        self.records_touched = 0

    def _file(self, idx, t):
        self.partition[t].append(idx)
        self.fact_part[idx] = t

    def _unfile(self, idx, t):
        self.partition[t].remove(idx)

    def _reindex(self, e):
        cur = self.belief[e]
        for idx in self.subj_facts[e]:
            old = self.fact_part[idx]
            if old != cur:
                self._unfile(idx, old)
                self._file(idx, cur)
                self.records_touched += 1

    def ingest(self, fact):
        s, r, o = fact
        idx = len(self.store_M)
        si, ri, oi = self.cid_idx[s], self.cid_idx[r], self.cid_idx[o]
        self.store_M.append(_encode_meaning((si, ri, oi), self.C, self.roles))
        self.store_T.append(fact)
        self.fact_part.append(None)
        self.subj_facts[s].append(idx)
        self.subj_c[s] += 1
        self.obj_c[o] += 1
        if s not in self.belief:
            self.belief[s] = _infer(self.subj_c, self.obj_c, s)
        self._file(idx, self.belief[s])
        if self.mode == "targeted":
            for e in (s, o):
                if e not in self.belief:
                    continue
                new_t = _infer(self.subj_c, self.obj_c, e)
                margin = self.subj_c[e] - self.obj_c[e]
                if new_t != self.belief[e] and margin >= self.H:
                    cand_t, cnt = self.candidate.get(e, (None, 0))
                    cand_t, cnt = (cand_t, cnt + 1) if cand_t == new_t else (new_t, 1)
                    self.candidate[e] = (cand_t, cnt)
                    if cnt >= self.K:
                        self.belief[e] = new_t
                        self._reindex(e)
                        self.candidate[e] = (None, 0)
                else:
                    self.candidate[e] = (None, 0)
        elif self.mode == "no_reorg":
            new_t = _infer(self.subj_c, self.obj_c, s)
            if new_t != self.belief[s]:
                self.belief[s] = new_t   # belief updates; old facts stranded (never moved)

    def finalize(self):
        if self.mode == "full_refit":
            self.partition = defaultdict(list)
            self.fact_part = [None] * len(self.store_M)
            for e in list(self.belief.keys()):
                self.belief[e] = _infer(self.subj_c, self.obj_c, e)
            for idx, (s, r, o) in enumerate(self.store_T):
                if s not in self.belief:
                    self.belief[s] = _infer(self.subj_c, self.obj_c, s)
                self._file(idx, self.belief[s])
                self.records_touched += 1

    def _decode_obj(self, idx):
        return self.inv.get(_cleanup(_unbind(self.store_M[idx], self.roles[OBJ]), self.C))

    def retrieve_typed(self, s, r, o):
        t = self.belief.get(s)
        if t is None:
            return False
        for i in self.partition[t]:
            if self.store_T[i] == (s, r, o) and self._decode_obj(i) == o:
                return True
        return False

    def partition_hash(self):
        payload = []
        for t in sorted(self.partition.keys()):
            members = sorted(self.store_T[i] for i in self.partition[t])
            payload.append(t + ":" + "|".join(",".join(m) for m in members))
        return hashlib.sha256("##".join(payload).encode("utf-8")).hexdigest()


def run_vsa_arm(seed, n_entities, H, K, mode):
    facts, genuine, wobbler, boundary, truetype, concepts = build_distractor_corpus(seed, n_entities)
    cid_idx = {c: i for i, c in enumerate(concepts)}
    rng = np.random.default_rng(seed * 131 + 7)
    C = _make_phasors(rng, len(concepts), N_DIM)
    roles = _make_phasors(rng, 3, N_DIM)
    store = VSAStore(C, roles, cid_idx, H, K, mode)
    for f in facts:
        store.ingest(f)
    store.finalize()

    subj_facts = sorted(set((s, r, o) for (s, r, o) in store.store_T
                            if truetype.get(s) == AGENT))            # queryable AGENT-final facts
    shifted_q = [(s, r, o) for (s, r, o) in subj_facts if s in genuine]
    stable_q = [(s, r, o) for (s, r, o) in subj_facts if s not in boundary]

    def acc(qset):
        return float(np.mean([store.retrieve_typed(*q) for q in qset])) if qset else None

    return {
        "shifted_typed_acc": acc(shifted_q), "stable_typed_acc": acc(stable_q),
        "records_touched": store.records_touched, "partition_hash": store.partition_hash(),
        "n_shifted_q": len(shifted_q), "n_stable_q": len(stable_q),
    }


# ---------------------------------------------------------------------------
# aggregation across seeds.
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x is not None]
    return float(np.mean(xs)) if xs else None


def gate_curve(seeds, n_entities, gate_list):
    """for each (H,K) gate, average precision/recall + cost across seeds."""
    out = {}
    for (H, K) in gate_list:
        pr, rc, rec_touch, incr, exh, nf, ne = [], [], [], [], [], [], []
        wob_runs, gen_runs = [], []
        for s in seeds:
            facts, genuine, wobbler, boundary, truetype, concepts = build_distractor_corpus(s, n_entities)
            r = simulate_gate(facts, boundary, H, K)
            p, rr, tp, fp, fn = precision_recall(r["detected"], genuine, wobbler)
            pr.append(p); rc.append(rr)
            rec_touch.append(r["records_touched"]); incr.append(r["incr_ops"]); exh.append(r["exhaustive_ops"])
            nf.append(r["n_facts"]); ne.append(r["n_entities"])
            wob_runs.append(max((r["max_run"].get(e, 0) for e in wobbler), default=0))
            gen_runs.append(min((r["max_run"].get(e, 0) for e in genuine), default=0))
        out[(H, K)] = {
            "H": H, "K": K, "precision": _mean(pr), "recall": _mean(rc),
            "records_touched": _mean(rec_touch), "incr_ops": _mean(incr), "exhaustive_ops": _mean(exh),
            "n_facts": _mean(nf), "n_entities": _mean(ne),
            "max_wobbler_run": max(wob_runs), "min_genuine_run": min(gen_runs),
        }
    return out


def cost_ladder(seeds, sizes, gate):
    """detection-cost + re-file-cost scaling across store sizes for the gated targeted arm + full_refit."""
    H, K = gate
    rows = {}
    for n in sizes:
        t_rec, incr, exh, nf, ne = [], [], [], [], []
        full_rec = []
        for s in seeds:
            facts, genuine, wobbler, boundary, truetype, concepts = build_distractor_corpus(s, n)
            r = simulate_gate(facts, boundary, H, K)
            t_rec.append(r["records_touched"]); incr.append(r["incr_ops"]); exh.append(r["exhaustive_ops"])
            nf.append(r["n_facts"]); ne.append(r["n_entities"])
            full_rec.append(len(facts))          # full_refit re-files EVERY fact
        nf_m = _mean(nf)
        rows[n] = {
            "n_entities": n, "n_facts": nf_m, "n_distinct_entities": _mean(ne),
            "targeted_records": _mean(t_rec), "full_refit_records": _mean(full_rec),
            "incr_detection_ops": _mean(incr), "exhaustive_detection_ops": _mean(exh),
            "incr_ops_per_write": _mean(incr) / nf_m if nf_m else None,
            "exhaustive_ops_per_write": _mean(exh) / nf_m if nf_m else None,
        }
    return rows


# ---------------------------------------------------------------------------
# verdict.
# ---------------------------------------------------------------------------
NAIVE_GATE = (0, 1)
BEST_GATE = (2, 4)   # margin deadband 2 + confirmation 4; principled (between wobbler run 3 and genuine run 6)


def compute_verdict(curve_K, curve_H, ladder, vsa, _best_res):
    small = min(ladder.keys())
    large = max(ladder.keys())
    L, S = ladder[large], ladder[small]

    # (a) detector precision under distractors.
    naive = curve_K[NAIVE_GATE]
    best = _best_res
    naive_precision = naive["precision"]
    best_precision = best["precision"]
    best_recall = best["recall"]
    sep_gap = best["min_genuine_run"] - best["max_wobbler_run"]   # class-conditional sustain-run separation

    # best achievable precision at recall>=0.90 across ALL swept gates (H and K curves).
    gates_ok = [g for g in list(curve_K.values()) + list(curve_H.values()) + [_best_res]
                if g["recall"] is not None and g["recall"] >= 0.90 and g["precision"] is not None]
    best_prec_at_recall = max((g["precision"] for g in gates_ok), default=0.0)

    # (b) detection cost scaling.
    incr_flat = (S["incr_ops_per_write"] is not None and L["incr_ops_per_write"] is not None and
                 L["incr_ops_per_write"] <= 1.20 * S["incr_ops_per_write"])
    exh_ratio = (L["exhaustive_ops_per_write"] / S["exhaustive_ops_per_write"]
                 if S["exhaustive_ops_per_write"] else float("inf"))
    exh_grows = exh_ratio >= 2.0

    # re-file EDIT advantage (records touched).
    targ_rec_L, targ_rec_S = L["targeted_records"], S["targeted_records"]
    full_rec_L, full_rec_S = L["full_refit_records"], S["full_refit_records"]
    targeted_flat = abs(targ_rec_L - targ_rec_S) <= 1e-6
    ratio_L = full_rec_L / targ_rec_L if targ_rec_L else float("inf")
    ratio_S = full_rec_S / targ_rec_S if targ_rec_S else float("inf")
    edit_adv_survives = targeted_flat and ratio_L >= 5.0 and ratio_L > ratio_S

    # end-to-end (detection + re-file writes) at LARGE.
    targ_e2e = L["incr_detection_ops"] + targ_rec_L
    full_terminal_e2e = L["n_facts"] + L["n_distinct_entities"]       # one refit pass (rederive + refile all)
    full_continual_e2e = N_GENUINE * (L["n_facts"] + L["n_distinct_entities"])  # refit per genuine shift event
    e2e_beats_continual = targ_e2e < full_continual_e2e
    e2e_beats_terminal = targ_e2e < full_terminal_e2e

    hp = (
        naive_precision < 0.90 and
        best_precision >= 0.90 and best_recall >= 0.90 and sep_gap > 0 and
        incr_flat and exh_grows and
        edit_adv_survives and
        e2e_beats_continual
    )
    hf = (
        best_prec_at_recall < 0.90 or
        (not incr_flat) or
        ratio_L < 2.0
    )
    tier = "HARD_PASS" if hp else ("HARD_FAIL" if hf else "MIDDLE_BAND")

    notes = []
    if naive_precision >= 0.90:
        notes.append("VACUOUS: naive detector already precise -> distractor control did NOT fire")
    if best_prec_at_recall < 0.90:
        notes.append("NO GATE separates wobblers from shifters at recall>=0.90 -> trigger-detection UNSOLVED")
    if not incr_flat:
        notes.append("incremental detection NOT flat -> detection is O(all), EDIT advantage illusory")
    if not e2e_beats_terminal:
        notes.append("CAVEAT: targeted end-to-end does NOT beat a single TERMINAL batch refit (detection = "
                     "optimal O(1)/write price of CONTINUAL freshness; beats continual-refit, not one-shot batch)")
    if edit_adv_survives:
        notes.append(f"EDIT advantage real: full/targeted re-file writes = {ratio_L:.1f}x at LARGE (grew from "
                     f"{ratio_S:.1f}x at SMALL)")

    msg = (f"{tier} | detector under distractors: naive_prec={naive_precision:.2f} (rec={naive['recall']:.2f}) "
           f"-> gated(H={BEST_GATE[0]},K={BEST_GATE[1]}) prec={best_precision:.2f} rec={best_recall:.2f} "
           f"| best_prec@recall>=.9={best_prec_at_recall:.2f} | sustain-run sep: wobbler<={best['max_wobbler_run']} "
           f"vs genuine>={best['min_genuine_run']} (gap={sep_gap}) | detection/write: incr {S['incr_ops_per_write']:.2f}"
           f"(S)->{L['incr_ops_per_write']:.2f}(L) FLAT={incr_flat} vs exhaustive {S['exhaustive_ops_per_write']:.1f}"
           f"->{L['exhaustive_ops_per_write']:.1f} ({exh_ratio:.1f}x GROWS) | re-file writes: targ FLAT "
           f"({targ_rec_S:.0f}->{targ_rec_L:.0f}) full {full_rec_S:.0f}->{full_rec_L:.0f} ratio {ratio_S:.1f}x->"
           f"{ratio_L:.1f}x | end-to-end(L): targ={targ_e2e:.0f} vs full_continual={full_continual_e2e:.0f} "
           f"(beats={e2e_beats_continual}) vs full_terminal={full_terminal_e2e:.0f} (beats={e2e_beats_terminal}) "
           f"| VSA recovery: noreorg_shifted={vsa['no_reorg']['shifted_typed_acc']:.2f} "
           f"targeted_shifted={vsa['targeted']['shifted_typed_acc']:.2f} "
           f"full_shifted={vsa['full_refit']['shifted_typed_acc']:.2f} | {'; '.join(notes) if notes else 'clean'}")
    summ = {
        "naive_precision": naive_precision, "naive_recall": naive["recall"],
        "best_gate": {"H": BEST_GATE[0], "K": BEST_GATE[1]},
        "best_gate_precision": best_precision, "best_gate_recall": best_recall,
        "best_precision_at_recall_ge_0.90": best_prec_at_recall,
        "sustain_run_separation_gap": sep_gap,
        "max_wobbler_run": best["max_wobbler_run"], "min_genuine_run": best["min_genuine_run"],
        "incr_ops_per_write_small": S["incr_ops_per_write"], "incr_ops_per_write_large": L["incr_ops_per_write"],
        "incr_detection_flat": incr_flat,
        "exhaustive_ops_per_write_small": S["exhaustive_ops_per_write"],
        "exhaustive_ops_per_write_large": L["exhaustive_ops_per_write"], "exhaustive_growth_ratio": exh_ratio,
        "targeted_records_small": targ_rec_S, "targeted_records_large": targ_rec_L, "targeted_flat": targeted_flat,
        "full_refit_records_small": full_rec_S, "full_refit_records_large": full_rec_L,
        "refile_ratio_small": ratio_S, "refile_ratio_large": ratio_L, "edit_advantage_survives": edit_adv_survives,
        "end_to_end_targeted_large": targ_e2e, "end_to_end_full_continual_large": full_continual_e2e,
        "end_to_end_full_terminal_large": full_terminal_e2e,
        "e2e_beats_continual": e2e_beats_continual, "e2e_beats_terminal_batch": e2e_beats_terminal,
        "vsa_noreorg_shifted": vsa["no_reorg"]["shifted_typed_acc"],
        "vsa_targeted_shifted": vsa["targeted"]["shifted_typed_acc"],
        "vsa_full_refit_shifted": vsa["full_refit"]["shifted_typed_acc"],
        "notes": notes,
    }
    return tier, msg, summ


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = ("exp_schema_reorg_distractor_detection_cost_v1" if run_mode == "full" else
           ("exp_schema_reorg_distractor_detection_cost_v1_smoke" if run_mode == "smoke" else
            "exp_schema_reorg_distractor_detection_cost_v1_selftest"))
    d = REPO / "data" / sub
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _write_metrics(out_dir, metrics):
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


H_SWEEP = [(h, 1) for h in [0, 1, 2, 3, 4, 5, 6, 7]]
K_SWEEP = [(0, k) for k in [1, 2, 3, 4, 5, 6, 7]]


def _vsa_arms(seeds, n_entities):
    return {
        "no_reorg": _avg_vsa(seeds, n_entities, 0, 1, "no_reorg"),
        "targeted": _avg_vsa(seeds, n_entities, BEST_GATE[0], BEST_GATE[1], "targeted"),
        "full_refit": _avg_vsa(seeds, n_entities, 0, 1, "full_refit"),
    }


def _avg_vsa(seeds, n_entities, H, K, mode):
    runs = [run_vsa_arm(s, n_entities, H, K, mode) for s in seeds]
    return {
        "shifted_typed_acc": _mean([r["shifted_typed_acc"] for r in runs]),
        "stable_typed_acc": _mean([r["stable_typed_acc"] for r in runs]),
        "records_touched": _mean([r["records_touched"] for r in runs]),
        "partition_hash": runs[0]["partition_hash"],
    }


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the distractor discriminator FIRES + arms differ.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (make_phasors/encode/decode + simulate_gate + VSAStore)...", flush=True)
    exercised = set()
    rng = np.random.default_rng(3)
    C = _make_phasors(rng, 8, 256); exercised.add("make_phasors")
    roles = _make_phasors(rng, 3, 256)
    M = _encode_meaning((1, 4, 6), C, roles); exercised.add("encode_meaning")
    oi = _cleanup(_unbind(M, roles[OBJ]), C); exercised.add("unbind_cleanup")
    assert oi == 6, f"FHRR SVO round-trip failed: obj={oi}"

    seeds = [7, 13]
    n = 24
    # corpus has real distractor opportunity: wobblers must exist + touch the boundary.
    facts, genuine, wobbler, boundary, truetype, concepts = build_distractor_corpus(7, n)
    assert len(wobbler) >= 2, f"no distractor wobblers in corpus: {wobbler}"
    assert len(genuine) >= 2, f"no genuine shifters: {genuine}"

    curve_K = gate_curve(seeds, n, K_SWEEP); exercised.add("simulate_gate")
    curve_H = gate_curve(seeds, n, H_SWEEP)
    naive = curve_K[(0, 1)]
    best = gate_curve(seeds, n, [BEST_GATE])[BEST_GATE]

    # DISTRACTOR CONTROL MUST FIRE: naive detector false-triggers on wobblers -> precision < 1.
    assert naive["precision"] < 0.90, \
        f"distractor control VACUOUS: naive precision={naive['precision']} (>=0.90 -> no false-positive opportunity)"
    assert naive["recall"] >= 0.90, f"naive should still catch genuine shifters: recall={naive['recall']}"
    # GATE FIXES IT: a principled gate reaches precision>=0.90 WITHOUT killing recall.
    assert best["precision"] >= 0.90, f"gated precision did NOT recover: {best['precision']}"
    assert best["recall"] >= 0.90, f"gate killed recall: {best['recall']}"
    assert best["precision"] > naive["precision"], "gate did not improve precision over naive"
    # separation is robust (not tuned): wobbler sustain-run strictly below genuine sustain-run.
    assert best["min_genuine_run"] > best["max_wobbler_run"], \
        f"sustain-run NOT separated: wobbler={best['max_wobbler_run']} genuine={best['min_genuine_run']}"

    # DETECTION COST: incremental flat, exhaustive grows, across two sizes.
    ladder = cost_ladder(seeds, [16, 48], BEST_GATE)
    lo, hi = ladder[16], ladder[48]
    assert hi["incr_ops_per_write"] <= 1.20 * lo["incr_ops_per_write"], \
        f"incremental detection NOT flat: {lo['incr_ops_per_write']:.2f}->{hi['incr_ops_per_write']:.2f}"
    assert hi["exhaustive_ops_per_write"] >= 2.0 * lo["exhaustive_ops_per_write"], \
        f"exhaustive strawman did NOT grow: {lo['exhaustive_ops_per_write']:.1f}->{hi['exhaustive_ops_per_write']:.1f}"
    # re-file EDIT advantage: targeted flat, full grows.
    assert abs(hi["targeted_records"] - lo["targeted_records"]) <= 1e-6, \
        f"targeted records NOT flat: {lo['targeted_records']}->{hi['targeted_records']}"
    assert hi["full_refit_records"] > lo["full_refit_records"], "full_refit records did not grow with size"

    # VSA recovery: gated targeted recovers staleness on genuine shifters; no_reorg is stale.
    vsa = _vsa_arms(seeds, n); exercised.add("run_vsa_arm")
    assert vsa["no_reorg"]["shifted_typed_acc"] < vsa["no_reorg"]["stable_typed_acc"] - 0.05, \
        f"no_reorg staleness did not fire: shifted={vsa['no_reorg']['shifted_typed_acc']} stable={vsa['no_reorg']['stable_typed_acc']}"
    assert vsa["targeted"]["shifted_typed_acc"] >= vsa["no_reorg"]["shifted_typed_acc"] + 0.10, \
        f"gated targeted did NOT recover: targ={vsa['targeted']['shifted_typed_acc']} noreorg={vsa['no_reorg']['shifted_typed_acc']}"
    # ARMS-MUST-DIFFER (META_RULE_AF): partition membership differs across arms.
    hashes = {m: vsa[m]["partition_hash"] for m in ("no_reorg", "targeted", "full_refit")}
    assert hashes["no_reorg"] != hashes["targeted"], "META_RULE_AF: no_reorg vs targeted bit-identical"
    assert hashes["no_reorg"] != hashes["full_refit"], "META_RULE_AF: no_reorg vs full_refit bit-identical"

    for ep in ["make_phasors", "encode_meaning", "unbind_cleanup", "simulate_gate", "run_vsa_arm"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | naive prec={naive['precision']:.2f} rec={naive['recall']:.2f} -> "
          f"gated prec={best['precision']:.2f} rec={best['recall']:.2f} | sep wobbler<={best['max_wobbler_run']} "
          f"genuine>={best['min_genuine_run']} | incr/write {lo['incr_ops_per_write']:.2f}->{hi['incr_ops_per_write']:.2f} "
          f"exh/write {lo['exhaustive_ops_per_write']:.1f}->{hi['exhaustive_ops_per_write']:.1f} | "
          f"targ_rec {lo['targeted_records']:.0f}={hi['targeted_records']:.0f} full_rec {lo['full_refit_records']:.0f}->"
          f"{hi['full_refit_records']:.0f} | VSA noreorg_shifted={vsa['no_reorg']['shifted_typed_acc']:.2f} "
          f"targ={vsa['targeted']['shifted_typed_acc']:.2f}", flush=True)
    return True


# ---------------------------------------------------------------------------
# main.
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default=None)
    args = ap.parse_args()

    if args.self_test or args.run_mode == "self_test":
        self_test()
        sys.exit(0)

    run_mode = "smoke" if (args.smoke or args.run_mode == "smoke") else "full"
    seeds = [7, 13] if run_mode == "smoke" else [7, 13, 29, 41, 53]
    sizes = [24, 48] if run_mode == "smoke" else [24, 60, 120, 240]
    vsa_size = sizes[-1]
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * (len(H_SWEEP) + len(K_SWEEP)) + len(seeds) * len(sizes) + len(seeds) * 3
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[distractor] run_mode={run_mode} seeds={seeds} sizes={sizes} vsa_size={vsa_size}", flush=True)

    curve_K = gate_curve(seeds, vsa_size, K_SWEEP)
    curve_H = gate_curve(seeds, vsa_size, H_SWEEP)
    print(f"[distractor] gate curves done: naive(K1)prec={curve_K[(0,1)]['precision']:.2f}", flush=True)
    ladder = cost_ladder(seeds, sizes, BEST_GATE)
    print(f"[distractor] cost ladder done: incr/write {ladder[sizes[0]]['incr_ops_per_write']:.2f}->"
          f"{ladder[sizes[-1]]['incr_ops_per_write']:.2f} exh/write {ladder[sizes[0]]['exhaustive_ops_per_write']:.1f}->"
          f"{ladder[sizes[-1]]['exhaustive_ops_per_write']:.1f}", flush=True)
    vsa = _vsa_arms(seeds, vsa_size)
    print(f"[distractor] VSA recovery done: noreorg_shifted={vsa['no_reorg']['shifted_typed_acc']:.2f} "
          f"targeted_shifted={vsa['targeted']['shifted_typed_acc']:.2f}", flush=True)

    best_res = gate_curve(seeds, vsa_size, [BEST_GATE])[BEST_GATE]
    tier, msg, summ = compute_verdict(curve_K, curve_H, ladder, vsa, best_res)
    elapsed = time.perf_counter() - t0

    def curve_dump(curve):
        return [{"H": v["H"], "K": v["K"], "precision": v["precision"], "recall": v["recall"],
                 "records_touched": v["records_touched"], "max_wobbler_run": v["max_wobbler_run"],
                 "min_genuine_run": v["min_genuine_run"]} for v in curve.values()]

    metrics = {
        "verdict": tier, "verdict_msg": msg, "summary": msg[:300], "run_mode": run_mode,
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds, "sizes": sizes, "vsa_size": vsa_size, "expected_n_units": expected_n_units,
        "verdict_summary": summ,
        "metric_a_confirmation_curve_K": curve_dump(curve_K),
        "metric_a_margin_curve_H": curve_dump(curve_H),
        "metric_b_cost_ladder": {str(k): v for k, v in ladder.items()},
        "metric_c_vsa_recovery": vsa,
        "prereg": {
            "hard_pass": "naive_prec<0.90 & gated_prec>=0.90 & gated_recall>=0.90 & sep_gap>0 & incr_flat & "
                         "exh_grows>=2x & targeted_flat & refile_ratio_L>=5 & ratio_L>ratio_S & e2e_beats_continual",
            "hard_fail": "best_prec@recall>=.9 <0.90 (no gate separates) | incr NOT flat (detection O(all)) | "
                         "refile_ratio_L<2.0",
            "middle": "gate improves precision but recall<0.90; or advantage only-continual w/ terminal caveat; "
                      "or detection flat but end-to-end only modestly better",
            "compute_architecture": "sequential-CPU (store grows fact-by-fact; belief+confirmation state depend "
                                     "on the accumulated stream)",
            "storage_strategy": "sharded (one exact VSA vector per fact) + type-partition index (cached derivative)",
            "final_metrics_atomicity": "tmp_replace", "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "detector": "glass-box hysteresis: margin deadband H + confirmation count K (require K consecutive "
                        "touches agreeing on the new type before re-filing); naive=(H0,K1)",
            "honest_note": "sustain separation works because genuine reorganizations are SUSTAINED and wobbles "
                           "TRANSIENT (construction proof of the gate; does NOT prove real distractors always "
                           "separate). detection is optimal O(1)/write; targeted beats any CONTINUAL-freshness "
                           "full-refit but NOT a single TERMINAL batch refit (which sacrifices mid-stream freshness).",
            "real_code_path_exercised": ["make_phasors", "encode_meaning", "unbind", "cleanup",
                                         "simulate_gate", "run_vsa_arm"],
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[distractor] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[distractor] {msg}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    _md = "full"
    try:
        if "--smoke" in sys.argv or ("--run-mode" in sys.argv and "smoke" in sys.argv):
            _md = "smoke"
        elif "--self-test" in sys.argv or "self_test" in sys.argv:
            _md = "self_test"
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            _write_crash_metrics(_out_dir(_md), e)
        except Exception:
            pass
        raise
