"""exp_schema_reorg_targeted_reindex_v1 -- the ONE confirmed consolidation gap: schema REORGANIZATION of old memories.

QUESTION (from notes/research_consolidation_function_inventory_schema_reorg_2026-07-16.md, function 2b):
single-pass-exact-write covers ~5/6 consolidation functions but MISSES re-filing EARLIER facts when later
evidence shifts an entity's schema (the 'fish' case: fish typed prey-like from early eats-OBJECT evidence,
later corroborated as an AGENT that lives_in/eats, never revisited).
  (a) does OLD-record staleness cause measurable QUERY ERROR as the foundation grows?
  (b) does an EXACT-ADDRESSED TARGETED RE-INDEX (revisit + re-file ONLY the affected records on a schema-shift)
      recover it -- beating BOTH doing-nothing AND a coarse full-re-fit, at bounded cost?
This is the Frontier-2 native-advantage claim: exact surgical re-filing vs the brain's lossy replay.
Glass-box, local numpy, NO LLM, no push/atoms.

WHY STALENESS CAN BE REAL HERE (honest mechanism, NOT a strawman):
  The note's HARD-FAIL route (a) is explicit -- if reads are FRESH EXACT LOOKUPS (flat scan over all facts),
  nothing goes stale and there is no gap. Staleness is real ONLY when the read path relies on a CACHED
  schema-membership derivative -- exactly the note's condition. At scale you cannot flat-scan every fact per
  query; you INDEX. The natural index is TYPE-PARTITIONED retrieval: query(s,r) routes through the subject's
  CACHED type to pick which partition to search. That cached type is a derived, MUTABLE attribute; when an
  entity's type shifts, its OLD facts sit stranded in the OLD partition and type-routed queries MISS them.
  THIS CELL BUILDS THAT SCALE-NECESSARY TYPE-INDEXED READ PATH and reports BOTH:
    - FLAT_SCAN (reference-cell style, argmax over all facts): NO staleness (note route-a; reported honestly).
    - TYPE_ROUTED (scalable index): staleness IS real; targeted exact re-index fixes it cheaply.
  So the gap = the cost of scalable indexing; the native fix = a cheap O(affected) exact re-index of the index.

TYPE (glass-box, principled, NO hand-coded lexical types): an entity's type is inferred purely from its
  role statistics -- AGENT if it appears predominantly as a SUBJECT (agent), PATIENT if predominantly as an
  OBJECT (patient). This subject/object (agent/patient) split is the minimal schema derivable from role counts.
  A shifter appears first as OBJECT-of-eats (typed PATIENT/prey), then accrues SUBJECT facts until
  subject_count > object_count -> belief flips PATIENT->AGENT. That belief flip is the schema-shift.

WRITE MODEL (single-pass-exact-write, per current architecture): each fact stored SHARDED (one exact VSA
  vector). The per-entity type BELIEF updates cheaply from the running tally (O(1), no revisit). What
  single-pass does NOT do = move the already-stored OLD fact vectors when the belief updates. That un-moved
  old record is the stale memory. Query routes through the (updated) belief -> old records stranded -> MISS.

ARMS (differ ONLY in the reorg policy on a belief flip):
  (1) NO_REORG      = update the belief, file NEW facts under it, NEVER move OLD facts (the current baseline).
  (2) TARGETED      = on a GLASS-BOX-DETECTED belief flip, EXACT-ADDRESS that entity's stored facts and
                      re-file ONLY them into the new partition. O(affected). (the native surgical fix.)
  (3) FULL_REFIT    = terminal coarse rebuild: re-derive EVERY entity's type from full evidence, re-file ALL
                      facts. O(all). The charitable (cheapest) full-refit -- one pass, not per-trigger.
  (4) ORACLE_REINDEX= like TARGETED but told the true shift-set (detection upper bound; isolates
                      detection-quality from re-file-quality).

DETECTION (glass-box, principled, NOT oracle for arm 2): after each ingested fact, recompute the type of the
  two entities it touches (subject, object) from their OWN running tallies (O(1) each). If a recomputed type
  != the entity's cached belief -> SCHEMA-SHIFT DETECTED -> trigger re-file of that entity's records. This is
  the biology's prediction-error-at-reactivation trigger (new evidence contradicts the stored type), using
  only the store's own evidence -- never the ground-truth answer.

METRICS (reported SEPARATELY, never blobbed):
  (a) STALENESS: TYPE_ROUTED query accuracy on SHIFTED-subject facts vs on STABLE-subject facts (the
      same-schema-consistent control). staleness_drop = stable_acc - noreorg_shifted_acc. Must be > 0 (the
      no-reorg-degrades control must FIRE) or the gap is not real / test vacuous.
  (b) RECOVERY: TARGETED shifted acc vs NO_REORG and vs FULL_REFIT. recovery_frac = fraction of the drop
      that TARGETED recovers.
  (c) COST: records_touched (re-file writes) for TARGETED vs FULL_REFIT, at TWO store sizes. targeted must be
      FLAT in store size (scales with #affected, not #total); full_refit grows with store size; report the ratio.
  Plus FLAT_SCAN diagnostic (no staleness -> read-path-contingent) + ORACLE_ROUTE localization (VSA is exact;
  the only error is routing) + glass-box detector precision/recall.

PRE-REG (envelope-fail-bands; I own the bands; verdict on the scale-relevant LARGE store):
  HARD_PASS (gap real AND cheaply fixable natively):
    staleness_drop >= 0.20 (NO_REORG shifted materially below stable control) AND
    recovery_frac >= 0.80 (TARGETED recovers most of the drop) AND
    targeted_shifted_acc >= full_refit_shifted_acc - 0.05 (targeted ties full-refit on accuracy) AND
    targeted records_touched FLAT across sizes (large == small, tol) AND
    full_refit_records / targeted_records >= 5.0 at LARGE (native cost advantage materializes) AND
    detector_recall >= 0.90 AND detector_precision >= 0.90 (glass-box detector catches shifts, no false reindex).
  HARD_FAIL (any):
    staleness_drop < 0.05 (NO_REORG ties control -> NO GAP: single-pass-exact is FINE; HONEST + important
        negative -- reads never rely on a stale derivative) OR
    recovery_frac < 0.50 (targeted re-index does NOT recover) OR
    full_refit_records / targeted_records < 2.0 (targeted ~ as expensive as full-refit -> native affordance
        does NOT materialize; trigger-detection/re-file cost half stays open).
  MIDDLE otherwise (real but small drop, partial recovery, or modest cost advantage 2-5x).

Local numpy, NO queue/GPU/atoms/push. ASCII-only. FHRR = complex128 unit phasors (reused). Sequential-CPU
(genuine sequential dependency: foundation grows fact-by-fact; type belief depends on accumulated tally;
reindex state depends on prior admissions -> chained). Storage: SHARDED (one VSA vector per fact) per
META_STORAGE_STRATEGY. Compute: V ~ 60 concepts, N=1024, <=5 seeds, 2 sizes, <=150 facts -> wall < 10s.
progress_logging=print_flush_true.
"""
# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; NO_REORG vs TARGETED vs FULL_REFIT partition-hash differ)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no quantitative noise floor. FHRR cleanup among ~60 concepts at N=1024, 3-term bundle,
#     within-partition <= ~150 facts -> z ~ sqrt(2N/3) ~ 26 sigma -> within-partition decode ~1.0. The ONLY
#     error source is partition MISROUTING (stale membership), isolated by the ORACLE_ROUTE localization arm.
# - baseline_in_band at smoke: NO_REORG shifted acc in (0.05, 0.95) band (partial staleness, not saturated);
#     stable control ~1.0; FLAT_SCAN ~1.0 (no staleness on flat path). Discriminator = staleness_drop > 0.
# - discriminator survives scale: scale IS the discriminator here (cost ratio grows with store size); run at
#     SMALL + LARGE. Staleness fires at BOTH (routing miss is size-independent); cost advantage GROWS at LARGE.
# - HARD_PASS strictly above floor; margins declared in prereg JSON.
# - real_code_path (F.1): self_test constructs the REAL objects (imported make_phasors/encode/decode_meaning +
#     TypedPartitionStore) at tiny scale and asserts (not a synthetic-only branch).
# - deterministic seeding (F.5): fixed int seeds; sorted() vocab ordering; NO hash()/list(set()) for seeds/splits.
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

ANCHOR_NAME = "schema_reorg_targeted_reindex_v1"
N_DIM = 1024

# --- reuse the proven FHRR primitives + role-filler SVO parse+bind (exp_nativelang_svo_vsa_probe_v1) ---
from experiments.exp_nativelang_svo_vsa_probe_v1 import (
    make_phasors as _make_phasors,
    bind as _bind,
    unbind as _unbind,
    cleanup as _cleanup,
    encode_meaning as _encode_meaning,   # M = sum_i bind(role_i, filler_i)
)

RELATIONS = ["eats", "lives_in", "chases"]
SUBJ, VERB, OBJ = 0, 1, 2
AGENT, PATIENT = "AGENT", "PATIENT"

# ---------------------------------------------------------------------------
# CORPUS with a SCHEMA SHIFT (the fish/whale pattern), generated deterministically.
# A "shifter" appears first as OBJECT-of-eats (typed PATIENT/prey), then accrues SUBJECT facts until
# subject_count > object_count -> belief flips PATIENT->AGENT. Its EARLY subject-facts are the stale records.
# ---------------------------------------------------------------------------
FOODS = sorted(["seed", "worm", "grass", "bread", "apple", "berry", "kibble", "nut"])
PLACES = sorted(["barn", "nest", "pond", "tree", "field", "den", "burrow", "reef"])
# PREY = pure-patient chase-objects (never subjects). Routing all `chases` objects here keeps stable animals
# from ever being objects -> they stay robustly AGENT (subj_count > obj_count=0), so the ONLY entities that
# genuinely shift are the designed shifters (keeps the glass-box detector's precision clean at 1.0).
PREY = sorted(["mouse", "rabbit", "minnow", "cricket", "moth", "vole", "shrew", "gnat"])
N_SHIFTED = 2
K_EARLY_OBJ = 2        # object-appearances that type a shifter PATIENT first (obj_count=2)
# a shifter's 5 SUBJECT facts. The belief flips PATIENT->AGENT when subj_count > obj_count(=2), i.e. AT the
# 3rd subject fact. Facts filed BEFORE/AT the flip (1,2,3) land in the PATIENT partition = STALE/stranded;
# facts AFTER the flip (4,5) land correctly in AGENT. Under NO_REORG the belief updates to AGENT (cheap) but
# the 3 stranded records are never moved -> a type-routed query (through the updated belief) MISSES them.
# -> shifted_acc = 2/5 = 0.40 (partial staleness, not saturated). TARGETED re-files the 3 stranded -> 1.0.
def _shifter_subject_facts(shifter):
    return [
        (shifter, "eats", FOODS[0]),       # [1] pre-flip  -> stranded in PATIENT
        (shifter, "lives_in", PLACES[0]),  # [2] pre-flip  -> stranded in PATIENT
        (shifter, "chases", PREY[0]),      # [3] FLIP (subj 3 > obj 2); filed pre-flip -> stranded in PATIENT
        (shifter, "eats", FOODS[1]),       # [4] post-flip -> filed correctly in AGENT
        (shifter, "lives_in", PLACES[1]),  # [5] post-flip -> filed correctly in AGENT
    ]


def build_shift_corpus(seed, n_entities):
    """Deterministic typed corpus. Returns (facts, shifters, truetype, concepts).
    facts: ordered list of (s,r,o). shifters: set. truetype: concept->final GT type (metric-only)."""
    rng = np.random.default_rng(seed)
    n_stable = max(4, n_entities - N_SHIFTED)
    stable = [f"anml{i:02d}" for i in range(n_stable)]
    shifters = [f"shift{i}" for i in range(N_SHIFTED)]

    truetype = {}
    for a in stable:
        truetype[a] = AGENT
    for f in FOODS:
        truetype[f] = PATIENT
    for p in PLACES:
        truetype[p] = PATIENT
    for q in PREY:
        truetype[q] = PATIENT
    for s in shifters:
        truetype[s] = AGENT   # final true type AFTER the shift

    facts = []
    # -- Block A: early OBJECT-appearances of each shifter (types it PATIENT first). Stable subjects here get
    #    their first appearance as SUBJECT -> AGENT immediately (never shift). --
    for si, s in enumerate(shifters):
        for j in range(K_EARLY_OBJ):
            a = stable[(si * K_EARLY_OBJ + j) % n_stable]
            facts.append((a, "eats", s))          # 'a eats shifter' -> shifter is object/prey
    # -- Block B: each shifter's SUBJECT facts (contiguous; the 4th flips the belief) --
    for s in shifters:
        for (ss, rr, oo) in _shifter_subject_facts(s):
            if oo is None:                        # 'chases' object = a stable animal
                oo = stable[0]
            facts.append((ss, rr, oo))
    # -- Block C: stable-animal subject facts to populate AGENT partition + pad the store to n_entities --
    for i, a in enumerate(stable):
        facts.append((a, "eats", FOODS[i % len(FOODS)]))
        facts.append((a, "lives_in", PLACES[i % len(PLACES)]))
        facts.append((a, "chases", PREY[i % len(PREY)]))   # chase a pure-patient prey (stable never an object)

    concepts = sorted(set(stable) | set(shifters) | set(FOODS) | set(PLACES) | set(PREY) | set(RELATIONS))
    return facts, set(shifters), truetype, concepts


# ---------------------------------------------------------------------------
# TYPE-PARTITIONED SHARDED VSA store with belief-update + targeted/full re-index.
# ---------------------------------------------------------------------------
class TypedPartitionStore:
    def __init__(self, C, roles, cid_idx, reorg_mode, shifters_truth=None):
        # reorg_mode in {"no_reorg","targeted","oracle","full_refit"}
        self.C = C
        self.roles = roles
        self.cid_idx = cid_idx
        self.inv = {v: k for k, v in cid_idx.items()}
        self.reorg_mode = reorg_mode
        self.shifters_truth = shifters_truth or set()
        self.subj_count = defaultdict(int)
        self.obj_count = defaultdict(int)
        self.store_M = []                       # SHARDED: one exact VSA vector per fact
        self.store_T = []                       # parallel (s,r,o)
        self.belief = {}                        # entity -> cached inferred type (the schema-membership derivative)
        self.partition = defaultdict(list)      # type -> list of store indices (subject's belief at file time)
        self.fact_part = []                     # parallel: which partition each stored fact currently lives in
        self.subj_facts = defaultdict(list)     # entity -> list of store indices with that subject (exact address)
        # cost / detector telemetry
        self.records_touched = 0                # re-file writes (the reorg cost)
        self.type_rederivations = 0             # detector type recomputations
        self.detection_ops = 0
        self.detected_shifts = set()            # entities the glass-box detector flagged as shifted

    def _infer(self, e):
        """glass-box type from role statistics: AGENT if predominantly subject, else PATIENT."""
        return AGENT if self.subj_count[e] > self.obj_count[e] else PATIENT

    def _file(self, idx, t):
        self.partition[t].append(idx)
        self.fact_part[idx] = t

    def _unfile(self, idx, t):
        self.partition[t].remove(idx)

    def _reindex_entity(self, e):
        """EXACT-ADDRESSED targeted re-file: move ONLY entity e's stored facts to its current belief. O(affected)."""
        cur = self.belief[e]
        moved = 0
        for idx in self.subj_facts[e]:
            old = self.fact_part[idx]
            if old != cur:
                self._unfile(idx, old)
                self._file(idx, cur)
                moved += 1
        self.records_touched += moved
        return moved

    def ingest(self, fact):
        s, r, o = fact
        idx = len(self.store_M)
        si, ri, oi = self.cid_idx[s], self.cid_idx[r], self.cid_idx[o]
        M = _encode_meaning((si, ri, oi), self.C, self.roles)   # exact, sharded
        self.store_M.append(M)
        self.store_T.append(fact)
        self.fact_part.append(None)
        self.subj_facts[s].append(idx)
        # update role tallies
        self.subj_count[s] += 1
        self.obj_count[o] += 1
        # set / update the subject's cached belief (O(1); this is within single-pass -- no record revisit).
        if s not in self.belief:
            self.belief[s] = self._infer(s)
        self._file(idx, self.belief[s])         # file the NEW fact under the subject's CURRENT belief

        # detector + reorg policy on the two entities this fact touches (subject, object).
        if self.reorg_mode in ("targeted", "oracle"):
            for e in (s, o):
                if e not in self.belief:
                    continue
                self.detection_ops += 1
                self.type_rederivations += 1
                new_t = self._infer(e)
                flip = (new_t != self.belief[e])
                if self.reorg_mode == "oracle":
                    # upper bound: told which entities truly shift; act when the belief lags the truth.
                    flip = (e in self.shifters_truth and new_t != self.belief[e])
                if flip:
                    self.belief[e] = new_t
                    self.detected_shifts.add(e)
                    self._reindex_entity(e)
        elif self.reorg_mode == "no_reorg":
            # belief updates (cheap), but OLD facts are NEVER moved.
            new_t = self._infer(s)
            if new_t != self.belief[s]:
                self.belief[s] = new_t          # belief now up to date; old facts stranded in old partition
                self.detected_shifts.add(s)     # (recorded only for telemetry; NO re-file happens)
        # full_refit: do nothing per-fact; terminal rebuild in finalize().

    def finalize(self):
        if self.reorg_mode == "full_refit":
            # coarse rebuild: re-derive EVERY entity's type from FULL evidence, re-file ALL facts. O(all).
            self.partition = defaultdict(list)
            self.fact_part = [None] * len(self.store_M)
            for e in list(self.belief.keys()):
                self.belief[e] = self._infer(e)
                self.type_rederivations += 1
            for idx, (s, r, o) in enumerate(self.store_T):
                if s not in self.belief:
                    self.belief[s] = self._infer(s)
                self._file(idx, self.belief[s])
                self.records_touched += 1        # every fact re-filed = O(all)

    # ---- retrieval ----
    # A fact is retrieved iff its EXACT vector lives in the ROUTED partition AND a real VSA unbind+cleanup of
    # that vector's OBJ slot decodes to o. Decoding the fact's OWN vector (not an argmax over the partition)
    # isolates the STALENESS mechanism (partition MEMBERSHIP / routing) from VSA cue-collision noise -- a
    # localization discipline: the only thing that can differ across arms is which partition the record is in.
    def _decode_obj(self, idx):
        """exact VSA: unbind the OBJ role from the stored fact vector + cleanup -> object concept string."""
        oi = _cleanup(_unbind(self.store_M[idx], self.roles[OBJ]), self.C)
        return self.inv.get(oi)

    def retrieve_typed(self, s, r, o):
        """TYPE-ROUTED read: search ONLY the partition of the subject's CACHED belief. Stranded records
        (filed under the old type, never moved) are NOT in the routed partition -> MISS."""
        t = self.belief.get(s)
        if t is None:
            return False
        for i in self.partition[t]:
            if self.store_T[i] == (s, r, o) and self._decode_obj(i) == o:
                return True
        return False

    def retrieve_flat(self, s, r, o):
        """FLAT_SCAN read (reference-cell style): search ALL facts. No staleness (fresh exact lookup)."""
        for i in range(len(self.store_M)):
            if self.store_T[i] == (s, r, o) and self._decode_obj(i) == o:
                return True
        return False

    def retrieve_oracle_route(self, s, r, o):
        """ORACLE_ROUTE localization: route to the partition that ACTUALLY holds the fact. ~1.0 -> proves VSA
        decode is exact and the only TYPE_ROUTED error is routing (stale membership), not decode noise."""
        for i in range(len(self.store_M)):
            if self.store_T[i] == (s, r, o):
                t = self.fact_part[i]
                if i in self.partition[t] and self._decode_obj(i) == o:
                    return True
        return False

    def partition_hash(self):
        payload = []
        for t in sorted(self.partition.keys()):
            members = sorted(self.store_T[i] for i in self.partition[t])
            payload.append(t + ":" + "|".join(",".join(m) for m in members))
        return hashlib.sha256("##".join(payload).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# one (seed, size, arm) run.
# ---------------------------------------------------------------------------
def run_arm(seed, n_entities, reorg_mode):
    facts, shifters, truetype, concepts = build_shift_corpus(seed, n_entities)
    cid_idx = {c: i for i, c in enumerate(concepts)}
    rng = np.random.default_rng(seed * 131 + 7)
    C = _make_phasors(rng, len(concepts), N_DIM)
    roles = _make_phasors(rng, 3, N_DIM)

    store = TypedPartitionStore(C, roles, cid_idx, reorg_mode, shifters_truth=shifters)
    for f in facts:
        store.ingest(f)
    store.finalize()

    # query set = all SUBJECT facts (a fact is queryable by its subject). Split shifted vs stable subject.
    subject_facts = [(s, r, o) for (s, r, o) in store.store_T if s in truetype and truetype.get(s) == AGENT]
    # dedupe exact triples (a fact vector per triple)
    subj_facts_unique = sorted(set(subject_facts))
    shifted_q = [(s, r, o) for (s, r, o) in subj_facts_unique if s in shifters]
    stable_q = [(s, r, o) for (s, r, o) in subj_facts_unique if s not in shifters]

    def acc(qset, fn):
        if not qset:
            return None
        return float(np.mean([fn(s, r, o) for (s, r, o) in qset]))

    shifted_typed = acc(shifted_q, store.retrieve_typed)
    stable_typed = acc(stable_q, store.retrieve_typed)
    shifted_flat = acc(shifted_q, store.retrieve_flat)
    shifted_oracle_route = acc(shifted_q, store.retrieve_oracle_route)

    # glass-box detector quality (targeted arm): entities flagged vs the true shift-set.
    detected = set(e for e in store.detected_shifts if e in cid_idx)
    tp = len(detected & shifters)
    det_recall = tp / float(len(shifters)) if shifters else None
    det_precision = (tp / float(len(detected))) if detected else (1.0 if not shifters else 0.0)

    return {
        "seed": seed, "n_entities": n_entities, "reorg_mode": reorg_mode,
        "n_facts": len(facts), "n_shifted": len(shifters),
        "shifted_typed_acc": shifted_typed,
        "stable_typed_acc": stable_typed,
        "shifted_flat_acc": shifted_flat,
        "shifted_oracle_route_acc": shifted_oracle_route,
        "records_touched": store.records_touched,
        "type_rederivations": store.type_rederivations,
        "detection_ops": store.detection_ops,
        "detector_recall": det_recall,
        "detector_precision": det_precision,
        "partition_hash": store.partition_hash(),
        "n_shifted_queries": len(shifted_q),
        "n_stable_queries": len(stable_q),
    }


def _meanopt(vals):
    v = [x for x in vals if x is not None]
    return float(np.mean(v)) if v else None


def avg_arm(seeds, n_entities, reorg_mode):
    runs = [run_arm(s, n_entities, reorg_mode) for s in seeds]
    keys = ["shifted_typed_acc", "stable_typed_acc", "shifted_flat_acc", "shifted_oracle_route_acc",
            "records_touched", "type_rederivations", "detection_ops", "detector_recall",
            "detector_precision", "n_facts"]
    out = {k: _meanopt([r[k] for r in runs]) for k in keys}
    out["per_seed"] = runs
    out["reorg_mode"] = reorg_mode
    out["n_entities"] = n_entities
    return out


# ---------------------------------------------------------------------------
# verdict (on the scale-relevant LARGE store; SMALL used for cost-flatness).
# ---------------------------------------------------------------------------
def compute_verdict(small, large):
    L = large
    noreorg = L["no_reorg"]
    targ = L["targeted"]
    full = L["full_refit"]
    oracle = L["oracle"]

    stable_ctrl = noreorg["stable_typed_acc"]                 # same-schema-consistent control
    noreorg_shifted = noreorg["shifted_typed_acc"]
    targ_shifted = targ["shifted_typed_acc"]
    full_shifted = full["shifted_typed_acc"]

    staleness_drop = (stable_ctrl - noreorg_shifted) if (stable_ctrl is not None and noreorg_shifted is not None) else 0.0
    denom = (stable_ctrl - noreorg_shifted)
    recovery_frac = ((targ_shifted - noreorg_shifted) / denom) if denom and denom > 1e-9 else (1.0 if (targ_shifted is not None and staleness_drop <= 1e-9) else 0.0)

    # cost: records touched, LARGE store; ratio full/targeted. targeted flatness across sizes.
    targ_records_L = targ["records_touched"]
    full_records_L = full["records_touched"]
    targ_records_S = small["targeted"]["records_touched"]
    cost_ratio = (full_records_L / targ_records_L) if targ_records_L and targ_records_L > 0 else float("inf")
    targeted_flat = abs(targ_records_L - targ_records_S) <= 1e-6   # scales with #affected, not store size

    det_recall = targ["detector_recall"] if targ["detector_recall"] is not None else 0.0
    det_precision = targ["detector_precision"] if targ["detector_precision"] is not None else 0.0

    hp = (
        staleness_drop >= 0.20 and
        recovery_frac >= 0.80 and
        (targ_shifted is not None and full_shifted is not None and targ_shifted >= full_shifted - 0.05) and
        targeted_flat and
        cost_ratio >= 5.0 and
        det_recall >= 0.90 and det_precision >= 0.90
    )
    hf = (
        staleness_drop < 0.05 or
        recovery_frac < 0.50 or
        cost_ratio < 2.0
    )
    if hp:
        tier = "HARD_PASS"
    elif hf:
        tier = "HARD_FAIL"
    else:
        tier = "MIDDLE_BAND"

    # honest read of WHICH way a fail/pass goes.
    notes = []
    if staleness_drop < 0.05:
        notes.append("NO_GAP: NO_REORG ties the control -> single-pass-exact is FINE on this read path")
    if L["no_reorg"]["shifted_flat_acc"] is not None and L["no_reorg"]["shifted_flat_acc"] >= 0.95:
        notes.append("FLAT_SCAN has NO staleness -> gap is CONTINGENT on the (scale-necessary) type-indexed read path")
    if recovery_frac < 0.50:
        notes.append("TARGETED re-index does NOT recover -> re-file mechanism suspect")
    if cost_ratio < 2.0:
        notes.append("targeted ~ full-refit cost -> native affordance does NOT materialize")

    msg = (f"{tier} | staleness_drop={staleness_drop:.3f} (stable_ctrl={stable_ctrl:.3f} vs "
           f"noreorg_shifted={noreorg_shifted:.3f}) | flat_scan_shifted={L['no_reorg']['shifted_flat_acc']:.3f} "
           f"(no staleness) | recovery_frac={recovery_frac:.3f} (targ_shifted={targ_shifted:.3f}, "
           f"full_shifted={full_shifted:.3f}, oracle_shifted={oracle['shifted_typed_acc']:.3f}) | "
           f"cost: targ_records(L)={targ_records_L} full_records(L)={full_records_L} ratio={cost_ratio:.1f}x "
           f"targ_flat(S={targ_records_S},L={targ_records_L})={targeted_flat} | "
           f"detector rec={det_recall:.2f} prec={det_precision:.2f} | oracle_route(loc)="
           f"{L['no_reorg']['shifted_oracle_route_acc']:.3f} | {'; '.join(notes) if notes else 'clean'}")
    return tier, msg, {
        "staleness_drop": staleness_drop, "recovery_frac": recovery_frac, "cost_ratio": cost_ratio,
        "targeted_flat": targeted_flat, "targ_records_L": targ_records_L, "full_records_L": full_records_L,
        "targ_records_S": targ_records_S, "detector_recall": det_recall, "detector_precision": det_precision,
        "stable_ctrl": stable_ctrl, "noreorg_shifted": noreorg_shifted, "targ_shifted": targ_shifted,
        "full_shifted": full_shifted, "flat_scan_shifted": L["no_reorg"]["shifted_flat_acc"],
        "oracle_route_localization": L["no_reorg"]["shifted_oracle_route_acc"], "notes": notes,
    }


# ---------------------------------------------------------------------------
# infra.
# ---------------------------------------------------------------------------
def _out_dir(run_mode):
    sub = ("exp_schema_reorg_targeted_reindex_v1" if run_mode == "full" else
           ("exp_schema_reorg_targeted_reindex_v1_smoke" if run_mode == "smoke" else
            "exp_schema_reorg_targeted_reindex_v1_selftest"))
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


# ---------------------------------------------------------------------------
# self-test: EXERCISE THE REAL code path + assert the discriminator FIRES (no-reorg degrades) + arms differ.
# ---------------------------------------------------------------------------
def self_test():
    print("[self_test] constructing REAL objects (imported make_phasors/encode/decode + TypedPartitionStore)...", flush=True)
    exercised = set()
    # real FHRR round-trip at tiny scale.
    rng = np.random.default_rng(3)
    C = _make_phasors(rng, 8, 256); exercised.add("make_phasors")
    roles = _make_phasors(rng, 3, 256)
    M = _encode_meaning((1, 4, 6), C, roles); exercised.add("encode_meaning")
    oi = _cleanup(_unbind(M, roles[OBJ]), C); exercised.add("unbind_cleanup")
    assert oi == 6, f"FHRR SVO round-trip failed: obj={oi}"

    seeds = [7, 13]
    small = {m: avg_arm(seeds, 10, m) for m in ("no_reorg", "targeted", "oracle", "full_refit")}
    exercised.add("run_arm")
    nr, tg, fr = small["no_reorg"], small["targeted"], small["full_refit"]

    # localization: VSA is exact -> oracle-route retrieval ~1.0 (only error is routing).
    assert nr["shifted_oracle_route_acc"] >= 0.95, \
        f"oracle-route (localization) not ~1.0: {nr['shifted_oracle_route_acc']} -> VSA decode broken, not routing"
    # FLAT_SCAN has no staleness (note route-a).
    assert nr["shifted_flat_acc"] >= 0.95, \
        f"flat_scan shifted acc not ~1.0: {nr['shifted_flat_acc']} -> exact store broken"
    # DISCRIMINATOR MUST FIRE: NO_REORG type-routed shifted acc must be BELOW the stable control.
    drop = nr["stable_typed_acc"] - nr["shifted_typed_acc"]
    assert drop > 0.05, \
        f"discriminator did NOT fire: no-reorg shifted={nr['shifted_typed_acc']} vs stable={nr['stable_typed_acc']} (drop={drop})"
    # baseline_in_band: NO_REORG shifted acc not saturated at 0 or 1 (partial staleness).
    assert 0.0 <= nr["shifted_typed_acc"] < 0.95, f"no-reorg shifted acc saturated high: {nr['shifted_typed_acc']}"
    # TARGETED recovers toward FULL_REFIT accuracy.
    assert tg["shifted_typed_acc"] >= nr["shifted_typed_acc"] + 0.10, \
        f"targeted did NOT recover: targ={tg['shifted_typed_acc']} noreorg={nr['shifted_typed_acc']}"
    assert tg["shifted_typed_acc"] >= fr["shifted_typed_acc"] - 0.05, \
        f"targeted below full-refit accuracy: targ={tg['shifted_typed_acc']} full={fr['shifted_typed_acc']}"
    # COST: targeted < full-refit records touched.
    assert tg["records_touched"] < fr["records_touched"], \
        f"targeted not cheaper than full-refit: targ={tg['records_touched']} full={fr['records_touched']}"
    # ARMS-MUST-DIFFER (META_RULE_AF): partition membership differs across the reorg arms.
    hashes = {m: small[m]["per_seed"][0]["partition_hash"] for m in ("no_reorg", "targeted", "full_refit")}
    assert hashes["no_reorg"] != hashes["targeted"], "META_RULE_AF: no_reorg and targeted partitions bit-identical"
    assert hashes["no_reorg"] != hashes["full_refit"], "META_RULE_AF: no_reorg and full_refit partitions bit-identical"
    # detector caught the shifts glass-box.
    assert tg["detector_recall"] >= 0.90, f"glass-box detector missed shifts: recall={tg['detector_recall']}"
    assert tg["detector_precision"] >= 0.90, f"glass-box detector false-reindexed stable entities: prec={tg['detector_precision']}"

    for ep in ["make_phasors", "encode_meaning", "unbind_cleanup", "run_arm"]:
        assert ep in exercised, f"real_code_path: entrypoint {ep} not exercised"
    print(f"[self_test] PASS | oracle_route={nr['shifted_oracle_route_acc']:.3f} flat={nr['shifted_flat_acc']:.3f} "
          f"| stable_ctrl={nr['stable_typed_acc']:.3f} noreorg_shifted={nr['shifted_typed_acc']:.3f} "
          f"(drop={drop:.3f}) | targ_shifted={tg['shifted_typed_acc']:.3f} full_shifted={fr['shifted_typed_acc']:.3f} "
          f"| records targ={tg['records_touched']:.1f} full={fr['records_touched']:.1f} | "
          f"detector rec={tg['detector_recall']:.2f} prec={tg['detector_precision']:.2f}", flush=True)
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
    SIZE_SMALL, SIZE_LARGE = 10, 50
    arms = ("no_reorg", "targeted", "oracle", "full_refit")
    out_dir = _out_dir(run_mode)
    expected_n_units = len(seeds) * 2 * len(arms)   # seeds x sizes x arms
    _write_start_marker(out_dir, run_mode, expected_n_units)

    t0 = time.perf_counter()
    print(f"[reorg] run_mode={run_mode} seeds={seeds} sizes=({SIZE_SMALL},{SIZE_LARGE}) arms={arms}", flush=True)

    small = {m: avg_arm(seeds, SIZE_SMALL, m) for m in arms}
    print(f"[reorg] SMALL done: noreorg_shifted={small['no_reorg']['shifted_typed_acc']:.3f} "
          f"targ_records={small['targeted']['records_touched']:.1f}", flush=True)
    large = {m: avg_arm(seeds, SIZE_LARGE, m) for m in arms}
    print(f"[reorg] LARGE done: noreorg_shifted={large['no_reorg']['shifted_typed_acc']:.3f} "
          f"stable_ctrl={large['no_reorg']['stable_typed_acc']:.3f} "
          f"targ_records={large['targeted']['records_touched']:.1f} full_records={large['full_refit']['records_touched']:.1f}", flush=True)

    tier, msg, summ = compute_verdict(small, large)
    elapsed = time.perf_counter() - t0

    def strip(a):
        return {k: v for k, v in a.items() if k != "per_seed"}

    metrics = {
        "verdict": tier,
        "verdict_msg": msg,
        "summary": msg[:300],
        "run_mode": run_mode,
        "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": seeds,
        "sizes": {"small": SIZE_SMALL, "large": SIZE_LARGE},
        "expected_n_units": expected_n_units,
        "verdict_summary": summ,
        "arms_LARGE": {m.upper(): strip(large[m]) for m in arms},
        "arms_SMALL": {m.upper(): strip(small[m]) for m in arms},
        "metric_a_staleness_drop": summ["staleness_drop"],
        "metric_a_stable_control_acc": summ["stable_ctrl"],
        "metric_a_noreorg_shifted_acc": summ["noreorg_shifted"],
        "metric_a_flat_scan_shifted_acc": summ["flat_scan_shifted"],
        "metric_b_recovery_frac": summ["recovery_frac"],
        "metric_b_targeted_shifted_acc": summ["targ_shifted"],
        "metric_b_full_refit_shifted_acc": summ["full_shifted"],
        "metric_c_targeted_records_large": summ["targ_records_L"],
        "metric_c_full_refit_records_large": summ["full_records_L"],
        "metric_c_targeted_records_small": summ["targ_records_S"],
        "metric_c_cost_ratio_full_over_targeted": summ["cost_ratio"],
        "metric_c_targeted_flat_across_sizes": summ["targeted_flat"],
        "glassbox_detector_recall": summ["detector_recall"],
        "glassbox_detector_precision": summ["detector_precision"],
        "localization_oracle_route_acc": summ["oracle_route_localization"],
        "full_LARGE_per_seed": {m.upper(): large[m]["per_seed"] for m in arms},
        "prereg": {
            "hard_pass": "staleness_drop>=0.20 & recovery_frac>=0.80 & targ>=full-0.05 & targeted_flat & "
                         "cost_ratio>=5.0 & detector_recall>=0.90 & detector_precision>=0.90",
            "hard_fail": "staleness_drop<0.05 (NO GAP) | recovery_frac<0.50 | cost_ratio<2.0",
            "middle": "real-but-small drop / partial recovery / modest cost advantage 2-5x",
            "compute_architecture": "sequential-CPU (genuine sequential dependency: foundation grows fact-by-fact; "
                                    "belief depends on accumulated tally; reindex state depends on prior admissions)",
            "storage_strategy": "sharded (one exact VSA vector per fact) + type-partition index (cached derivative)",
            "final_metrics_atomicity": "tmp_replace",
            "progress_logging": "print_flush_true",
            "deterministic_seeding": True,
            "detection": "glass-box prediction-error: recompute touched entity's type from own tally; flip -> reindex",
            "honest_note": "staleness is real ONLY for the type-indexed (scale-necessary) read path; FLAT_SCAN "
                           "(fresh exact lookup) has no staleness -> gap = cost of scalable indexing; native fix "
                           "= O(affected) exact re-index. Accuracy side is partly by-construction (indexed routing "
                           "misses stranded entries); the empirical content is the COST SCALING (targeted flat vs "
                           "full-refit growing) + the flat-scan contrast.",
            "real_code_path_exercised": ["make_phasors", "encode_meaning", "unbind", "cleanup", "run_arm"],
        },
    }
    _write_metrics(out_dir, metrics)
    print(f"[reorg] {tier} in {elapsed:.2f}s -> {out_dir/'metrics.json'}", flush=True)
    print(f"[reorg] {msg}", flush=True)
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
