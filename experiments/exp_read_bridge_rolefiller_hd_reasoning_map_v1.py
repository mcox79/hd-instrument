"""
THE BRIDGE / PAYOFF TEST -- does the reader's role-filler structure REASON END-TO-END in HD?
(Stage-1 of notes/learned_in_substrate_reader_plan_forms_hd_reasoning_maps_2026-07-18.md.)

THE UNIFICATION UNDER TEST (USER): a comprehended sentence IS a bound role-filler relational
structure = a reasoning-map = exactly what a reasoner composes over
([[feedback_sentences_are_reasoning_maps_comprehension_reasoning_one_substrate_...USER_2026-07-18]]).
THE GAP (nesting VET atom 29330): the current reader is PURELY SYMBOLIC -- it emits svo/loc/goal/
recipient/pred/nest TUPLES and NEVER calls HD bind(); the reasoning primitives use HD binding. They
are DIFFERENT representations, NOT yet bridged. THIS CELL BUILDS + TESTS THE BRIDGE.

WHAT IT DOES (one variable = the symbolic->HD->reason bridge; everything else held):
  1. FRONT-END: the CURRENT reader (exp_read_nested_clause_relative_third_reader_v1, nest=True) emits
     role-filler tuples on a CLEAN narrative slice (age-appropriate clean SVO/loc/goal/recipient
     micro-passages = the fair bar). This is the SAME shipped reader; we do NOT touch extraction.
  2. BRIDGE (zero-training, REAL hdlab FHRR primitives): each tuple -> a FACT vector =
     bundle_i bind(role_i, filler_i) + bind(RTYPE, type-marker), using hdlab.binding.bind /
     hdlab.bundling.bundle / hdlab.binding.unbind. The reasoning-map = the SHARDED set of fact
     vectors (per META_STORAGE_STRATEGY: sharded for compositional/multi-hop; bundled only as the
     explicit capacity-stress control).
  3. REASONER (VSA compositional readout = constraint-satisfaction): a query brings K constraints to
     bear by bundling K bind(role, filler) terms -> select the fact by cosine -> unbind the read role
     -> cleanup against the atom codebook. Multi-hop = chain the readout (a hop's answer becomes the
     next hop's constraint). Conjunctive = intersect two single-hop readouts. This IS "resolution
     scales with # constraints brought to bear" (reasoning theory 07-14).
  4. SECONDARY INTERFACE PROBE -- the NAMED additive_map reasoner (hdlab.additive_map.AdditiveKGMap):
     ingest the SAME tuples as (h,r,t) triples, fit, single-hop recall. Answers "can the additive_map
     reasoner consume the reader's role scheme?" + surfaces the LEARNED-coordinate vs ZERO-training
     representation-family distinction (the load-bearing Stage-2 localization).

REAL BASELINE (design-gate #1): SYMBOLIC = query the reader's tuples directly (dict filter + graph
  join). NOT a strawman. On the clean gold it is the CEILING by construction (gold is auto-derived
  from the reader's own tuples -> symbolic ~1.0 = the fair reference). The HD path must at least MATCH
  it single-hop (bridge preserves info) and the DISCRIMINATING value is whether the HD reasoner
  COMPOSES multi-hop where a single flat lookup can't, AND where the map degrades (capacity).

CAN-FAIL (design-gate #2; all genuinely reachable + measured):
  (a) CROSSTALK destroys the map: with ~200 distractor facts + a ~200-atom vocab, unbind->cleanup can
      pick the wrong filler -> HD single-hop < symbolic. MEASURED.
  (b) MULTI-HOP does NOT compose: per-hop cleanup error propagates across the chain -> HD multi-hop
      collapses while single-hop is fine. MEASURED (HD multi-hop accuracy is the discriminator).
  (c) the additive_map reasoner CANNOT consume the reader's role scheme (API / representation family).
      MEASURED (probe status + single-hop recall).
  (d) CAPACITY: the bundled-map readout MUST degrade at high load (Plate O(N/log N) bound at N=2048 ~
      hundreds); if it did not, the capacity discriminator would be vacuous. The sweep asserts
      readout(load=256) < 0.90 (discriminator-fires gate). MEASURED.

DIFFICULTY-ON (design-gate #3): the reasoning-map carries ~200 real-corpus distractor facts (crosstalk
  pressure); every gold query is filtered to have a UNIQUE symbolic answer over the FULL map (non-
  vacuous, unambiguous); multi-hop queries are genuine cross-fact JOINS that a single lookup can't do.

ONE VARIABLE (design-gate #4): symbolic and HD run the SAME query-program (typed steps: rel_type +
  role-constraints + read-role); only the substrate differs (dict filter vs bind/bundle/unbind/cleanup).

HONEST SCOPING: this uses the CURRENT (symbolic, ~0.40 corpus-wide) reader as the front-end, so we
  measure on the CLEAN slice where the reader's tuples are correct (reader errors hit BOTH arms
  equally; we test the BRIDGE + REASONER, NOT the reader's extraction quality). reader_fidelity =
  fraction of authored queries symbolic-answerable is reported as CONTEXT, never folded into the
  bridge headline. Gold is AUTO-derived from the reader's own tuples (reproducible; not a hand gold).

BRAIN-CHECK (pre-reg; outcome NOT pre-assumed): the additive_map's compositional readout (mean of
  per-edge estimates; bring K constraints to bear) is the substrate analog of constraint-satisfaction
  over a situation-model in cortex (resolution scales with # constraints -- Kintsch construction-
  integration; MEG constituent tracking Ding 2016). "comprehension-output IS thought-input" is
  brain-faithful IN KIND (a bound relational structure feeds the same relational machinery).
  DEVIATION FLAGGED: the brain's binding is neither pure FHRR-multiplicative nor TransE-additive; both
  are engineering stand-ins for a phase/assembly binding we do not claim to have matched. The bounded-
  depth crosstalk ceiling (this cell measures it) mirrors the human working-memory / center-embedding
  limit (~2-3), which is a REAL capacity bound, not a bug to engineer away.

BANDS (strict, above-floor per META_RULE_L):
  HARD-PASS = BRIDGE_REASONS_END_TO_END: HD single-hop >= symbolic - 0.10 AND HD multi-hop >= 0.70 AND
    HD conjunctive >= 0.70 AND additive_map single-hop recall >= 0.90 AND capacity discriminator fired
    (a load with readout < 0.90 exists) AND n_singlehop >= 12 AND n_multihop >= 6.
  HARD-FAIL = BRIDGE_BROKEN: HD single-hop < symbolic - 0.10 (crosstalk destroys the map) OR HD
    multi-hop < 0.40 (does not compose) OR additive_map probe ERROR/recall < 0.50 (named reasoner
    cannot consume) -> a REAL localization: the map representation or the reasoner interface needs
    rework before Stage-2.
  MIDDLE = BRIDGE_PARTIAL: anything between -> localize which piece is weak + honest deflate.

MEASURED/HYPOTHESIZED (META_RULE_AC): all band thresholds are HYPOTHESIZED@this-prereg. The additive_map
  memorizes a 16-triple reader-derived KB at recall@1 = 1.000 MEASURED@scratch probe (fit 1.9s, k=32,
  epochs=300) -> the >=0.90 additive_map gate is reachable. Plate bundle bound ~ N/(2 ln N) ~ 134 at
  N=2048 THEORETICAL -> load=256 degradation is physics-guaranteed (capacity gate reachable).

COMPUTE ARCHITECTURE: sequential-CPU. Justified: (a) wall << 10s expected for the FHRR path (a few
  hundred facts, N=2048, small matmuls); (b) the cell VALIDATES the substrate FHRR primitives (bit
  reference) so a CPU reference is correct; (c) the only training is the additive_map probe (~2s SGD,
  torch.Generator-seeded). No GPU batching win at this scale. STORAGE STRATEGY: SHARDED reasoning-map
  (compositional) + a BUNDLED capacity-stress control arm (declared). CRLB: n/a -- no additive-Gaussian
  estimator noise floor; the relevant capacity bound is the Plate bundle bound (stated above), and the
  HARD-PASS thresholds sit on its achievable side.

DETERMINISM: OMP/MKL=1; fixed int SEED; np.random.default_rng(seed); torch.Generator seeded in the
  additive_map fit; sorted(set(...)) ordering everywhere; NO builtin hash()-derived seeding/ordering.

Glass-box (POS + perceptron role-assigner + WordNet grounding reader front-end; REAL hdlab FHRR
  bind/bundle/unbind + REAL AdditiveKGMap; NO external LLM, NO runtime LLM). Local / foreground-to-
  completion. NO push / NO remote-persist. CLAIM-VET-pending; strategic read = HYPOTHESIS pending
  skunkworks landed-VET.

ANCHOR: read_bridge_rolefiller_hd_reasoning_map_v1
BUILDS ON: exp_read_nested_clause_relative_third_reader_v1 (reader front-end) + hdlab.binding/bundling
  (FHRR reasoning-map) + hdlab.additive_map.AdditiveKGMap (named reasoner interface probe).
CORPUS: hand-authored clean micro-passages (fair bar) + mcguffey_third_reader distractor tuples.
PRIOR-WORK CHECK: substrate_query "role filler binding reasoning map end to end reader reasoner bridge
  multihop" -> top cosine 0.369 = KB concept 'Reasoning' (a lexical/framenet atom) + 0.353 =
  design-note 'reasoning_multihop_cluster'; NO prior-arc EXPERIMENT cell at cosine>0.30 -> NOVEL bridge.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke (SYMBOLIC / FHRR_VSA / ADDITIVE_MAP produce distinct outputs)
# - final_metrics_atomicity: tmp_replace (single-shot; os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (VSA cleanup; capacity = Plate bundle bound, stated)
# - baseline_in_band: SYMBOLIC is the reference ceiling (=~1.0 by construction, declared not a
#   discriminator baseline); the FIRING discriminator is HD multi-hop + the capacity sweep
# - discriminator survives scale: capacity sweep runs at FULL N=2048 and MUST show load with acc<0.90
# - HARD_PASS strictly above floor
# - real_code_path: self-test constructs REAL hdlab bind/bundle/unbind + REAL AdditiveKGMap + REAL reader
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import time
import math
import hashlib
import argparse
import platform
import traceback
from datetime import datetime, timezone

_THIS = os.path.abspath(__file__)
REPO = os.path.dirname(os.path.dirname(_THIS))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments import exp_read_nested_clause_relative_third_reader_v1 as NEST     # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2       # noqa: E402

ANCHOR_NAME = "read_bridge_rolefiller_hd_reasoning_map_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
SEED = 20260718
N_DIM = 2048
N_SEEDS = 5
N_DISTRACTORS = 200

# ---------------------------------------------------------------------------
# Role scheme: (rel_type -> [(ROLE, tuple_slot_index)]). tuple_slot_index indexes the raw reader tuple
# t = (rel_type, a, b, c...) so slot 1 = first arg. This SAME map drives BOTH executors (one variable).
# ---------------------------------------------------------------------------
REL_SCHEMA = {
    "svo":       [("RVERB", 1), ("RAGENT", 2), ("RPATIENT", 3)],
    "loc":       [("RENT", 1), ("RPLACE", 2)],
    "goal":      [("RVERB", 1), ("RAGENT", 2), ("RDEST", 3)],
    "recipient": [("RVERB", 1), ("RAGENT", 2), ("RRECIP", 3)],
    "pred":      [("RVERB", 1), ("RAGENT", 2)],
}
ROLE_NAMES = sorted({r for sch in REL_SCHEMA.values() for (r, _s) in sch} | {"RTYPE"})
TYPE_MARKERS = sorted({"T_" + k for k in REL_SCHEMA})

# ---------------------------------------------------------------------------
# CLEAN micro-passages (the fair bar: age-appropriate clean narrative, distinctive entities so gold
# stays unambiguous, cross-relation shared entities so multi-hop JOINS exist). RC/complementizer
# passages are DELIBERATELY excluded (the reader still mis-attaches those -- out of the clean slice).
# ---------------------------------------------------------------------------
MICRO_PASSAGES = {
    "m01": "The hound chased the rabbit at the pond. The rabbit ate a carrot.",
    "m02": "Tom gave a book to Mary. Mary read the book in the cabin.",
    "m03": "A fox ran to the barn. The farmer saw the fox.",
    "m04": "The knight rode to the castle. The knight fought a dragon.",
    "m05": "The maiden picked a lily in the meadow. The wasp stung the maiden.",
    "m06": "The hunter shot a heron near the marsh. The heron fell.",
    "m07": "Anna sent a letter to John. John kept the letter.",
    "m08": "The wolf ran to the ridge. The shepherd chased the wolf.",
    "m09": "The lad fed the pony in the stable. The pony kicked the gate.",
    "m10": "The sailor rowed to the island. The sailor found a chest.",
    "m11": "The widow baked a pie for the vicar. The vicar praised the pie.",
    "m12": "The miller carried the sack to the mill. The thief robbed the miller.",
}


# ===========================================================================
# Reader front-end.
# ===========================================================================
def read_tuples(passages, clf):
    """Run the REAL reader (nest=True) over passages; return {pid: sorted list of role-filler tuples}."""
    out = {}
    for pid, text in passages.items():
        rels, _rbp, _rm, _inj = NEST.extract_passage_nest(
            text, clf, pid, passages, "handrule", NEST._VF_MODE,
            role_fix=True, self_loop_guard=True, deixis=True, nest=True)
        keep = [tuple(r) for r in rels if r[0] in REL_SCHEMA]
        out[pid] = sorted(set(keep), key=lambda t: (t[0], tuple(str(x) for x in t[1:])))
    return out


def collect_facts(store):
    """Flatten a {pid: tuples} store to a de-duplicated, deterministically-ordered fact list."""
    facts = set()
    for pid in sorted(store):
        for t in store[pid]:
            facts.add(tuple(t))
    return sorted(facts, key=lambda t: (t[0], tuple(str(x) for x in t[1:])))


def load_distractors(clf, n_want):
    """Real-corpus reader tuples used as DISTRACTOR facts (crosstalk pressure). No gold on these."""
    passages = NEST.load_lessons()
    slice_pids = sorted(passages)[:24]
    sub = {pid: passages[pid] for pid in slice_pids}
    store = read_tuples(sub, clf)
    facts = collect_facts(store)
    return facts[:n_want]


# ===========================================================================
# Symbolic executor (the REAL baseline).
# ===========================================================================
def _slot_of(rel, role):
    for (r, s) in REL_SCHEMA[rel]:
        if r == role:
            return s
    return None


def sym_select(facts, rel, constraints):
    """Return the list of facts matching rel + all role==filler constraints."""
    out = []
    for t in facts:
        if t[0] != rel:
            continue
        ok = True
        for role, val in constraints.items():
            s = _slot_of(rel, role)
            if s is None or s >= len(t) or t[s] != val:
                ok = False
                break
        if ok:
            out.append(t)
    return out


def sym_answer(facts, rel, constraints, read_role):
    """Unique-answer symbolic readout. Returns (answer_or_None, unique_bool)."""
    cand = sym_select(facts, rel, constraints)
    s = _slot_of(rel, read_role)
    vals = sorted({t[s] for t in cand if s is not None and s < len(t)})
    if len(vals) == 1:
        return vals[0], True
    return None, False


# ===========================================================================
# Gold auto-generation from the reader's OWN micro-passage tuples (reproducible; symbolic ~1.0 by
# construction). Only queries with a UNIQUE symbolic answer over the FULL map (distractors incl.) are
# kept -> non-vacuous + unambiguous + difficulty-on.
# ===========================================================================
def gen_singlehop(gold_facts, all_facts):
    """For each gold fact, read each role given the others as constraints; keep unique-answer queries."""
    qs = []
    for t in gold_facts:
        rel = t[0]
        roles = [r for (r, _s) in REL_SCHEMA[rel]]
        for read_role in roles:
            constraints = {}
            for r in roles:
                if r == read_role:
                    continue
                s = _slot_of(rel, r)
                if s < len(t):
                    constraints[r] = t[s]
            gold, uniq = sym_answer(all_facts, rel, constraints, read_role)
            rs = _slot_of(rel, read_role)
            if uniq and rs < len(t) and gold == t[rs]:
                qs.append(dict(kind="single", rel=rel, constraints=constraints,
                               read_role=read_role, gold=gold))
    # de-dup identical programs deterministically
    seen, uniq_qs = set(), []
    for q in qs:
        key = (q["rel"], tuple(sorted(q["constraints"].items())), q["read_role"])
        if key not in seen:
            seen.add(key)
            uniq_qs.append(q)
    return uniq_qs


def gen_multihop(gold_facts, all_facts):
    """2-hop JOINS: hop1 reads an entity E from fact A; hop2 uses E as a constraint on fact B (sharing
    E) and reads a final role. Genuine cross-fact composition a single lookup cannot do."""
    qs = []
    ent_slots = ("RAGENT", "RPATIENT", "RENT", "RDEST", "RRECIP")
    for a in gold_facts:
        rel_a = a[0]
        for (ra, sa) in REL_SCHEMA[rel_a]:
            if ra not in ent_slots or sa >= len(a):
                continue
            shared = a[sa]  # the entity produced by hop1 (read ra of A given A's OTHER roles)
            # hop1 constraints = A's other roles
            c1 = {r: a[s] for (r, s) in REL_SCHEMA[rel_a] if r != ra and s < len(a)}
            g1, u1 = sym_answer(all_facts, rel_a, c1, ra)
            if not (u1 and g1 == shared):
                continue
            for b in gold_facts:
                if b is a:
                    continue
                rel_b = b[0]
                for (rb, sb) in REL_SCHEMA[rel_b]:
                    if rb not in ent_slots or sb >= len(b) or b[sb] != shared:
                        continue
                    # hop2: constrain B by rb==shared (via hop1) + B's remaining fixed roles except read
                    for (read_r, s_read) in REL_SCHEMA[rel_b]:
                        if read_r == rb or s_read >= len(b):
                            continue
                        c2_fixed = {r: b[s] for (r, s) in REL_SCHEMA[rel_b]
                                    if r not in (rb, read_r) and s < len(b)}
                        c2 = dict(c2_fixed); c2[rb] = shared
                        g2, u2 = sym_answer(all_facts, rel_b, c2, read_r)
                        if u2 and g2 == b[s_read] and g2 != shared:
                            qs.append(dict(
                                kind="multi",
                                hop1=dict(rel=rel_a, constraints=c1, read_role=ra),
                                hop2=dict(rel=rel_b, fixed=c2_fixed, link_role=rb, read_role=read_r),
                                gold=g2))
    # de-dup + cap deterministically
    seen, uniq_qs = set(), []
    for q in qs:
        key = (q["hop1"]["rel"], tuple(sorted(q["hop1"]["constraints"].items())), q["hop1"]["read_role"],
               q["hop2"]["rel"], tuple(sorted(q["hop2"]["fixed"].items())),
               q["hop2"]["link_role"], q["hop2"]["read_role"], q["gold"])
        if key not in seen:
            seen.add(key)
            uniq_qs.append(q)
    return uniq_qs


def gen_conjunctive(gold_facts, all_facts):
    """Entity that is AGENT of two distinct facts -> 'which entity is agent of both X and Y'."""
    qs = []
    agent_facts = {}
    for t in gold_facts:
        s = _slot_of(t[0], "RAGENT")
        if s is not None and s < len(t):
            agent_facts.setdefault(t[s], []).append(t)
    for ent in sorted(agent_facts):
        fs = agent_facts[ent]
        if len(fs) < 2:
            continue
        a, b = fs[0], fs[1]
        ca = {r: a[s] for (r, s) in REL_SCHEMA[a[0]] if r != "RAGENT" and s < len(a)}
        cb = {r: b[s] for (r, s) in REL_SCHEMA[b[0]] if r != "RAGENT" and s < len(b)}
        ga, ua = sym_answer(all_facts, a[0], ca, "RAGENT")
        gb, ub = sym_answer(all_facts, b[0], cb, "RAGENT")
        if ua and ub and ga == ent and gb == ent:
            qs.append(dict(kind="conj",
                           armA=dict(rel=a[0], constraints=ca, read_role="RAGENT"),
                           armB=dict(rel=b[0], constraints=cb, read_role="RAGENT"),
                           gold=ent))
    return qs


def run_symbolic_query(facts, q):
    if q["kind"] == "single":
        ans, _u = sym_answer(facts, q["rel"], q["constraints"], q["read_role"])
        return ans
    if q["kind"] == "multi":
        e, _u1 = sym_answer(facts, q["hop1"]["rel"], q["hop1"]["constraints"], q["hop1"]["read_role"])
        if e is None:
            return None
        c2 = dict(q["hop2"]["fixed"]); c2[q["hop2"]["link_role"]] = e
        ans, _u2 = sym_answer(facts, q["hop2"]["rel"], c2, q["hop2"]["read_role"])
        return ans
    if q["kind"] == "conj":
        a, _ua = sym_answer(facts, q["armA"]["rel"], q["armA"]["constraints"], q["armA"]["read_role"])
        b, _ub = sym_answer(facts, q["armB"]["rel"], q["armB"]["constraints"], q["armB"]["read_role"])
        return a if (a is not None and a == b) else None
    return None


# ===========================================================================
# FHRR reasoning-map + VSA compositional reasoner (REAL hdlab primitives).
# ===========================================================================
def _fhrr_codebook(atoms, n_dim, rng):
    import torch
    import numpy as np

    def fhrr():
        ph = torch.tensor(rng.uniform(-np.pi, np.pi, size=n_dim), dtype=torch.float64)
        return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)
    return {a: fhrr() for a in atoms}


def _cos(a, b):
    import torch
    a = a.flatten(); b = b.flatten()
    num = torch.vdot(a, b).abs(); den = a.norm() * b.norm()
    return float(num / den) if float(den) > 0 else 0.0


class FHRRReasoner:
    """Zero-training role-filler reasoning-map + VSA compositional readout. SHARDED fact vectors."""

    def __init__(self, facts, n_dim, seed):
        import numpy as np
        from hdlab.binding import bind
        from hdlab.bundling import bundle
        self._bind = bind
        self._bundle = bundle
        rng = np.random.default_rng(seed)
        atoms = sorted({str(x) for t in facts for x in t[1:]})
        self.role_cb = _fhrr_codebook(ROLE_NAMES, n_dim, rng)
        self.type_cb = _fhrr_codebook(TYPE_MARKERS, n_dim, rng)
        self.atom_cb = _fhrr_codebook(atoms, n_dim, rng)
        self.facts = list(facts)
        self.fact_vecs = [self._encode_fact(t) for t in self.facts]

    def _encode_fact(self, t):
        import torch
        rel = t[0]
        terms = [self._bind(self.role_cb["RTYPE"], self.type_cb["T_" + rel])]
        for (role, slot) in REL_SCHEMA[rel]:
            if slot < len(t):
                terms.append(self._bind(self.role_cb[role], self.atom_cb[str(t[slot])]))
        return self._bundle(torch.stack(terms))

    def _query_vec(self, rel, constraints):
        import torch
        terms = [self._bind(self.role_cb["RTYPE"], self.type_cb["T_" + rel])]
        for role, val in sorted(constraints.items()):
            if str(val) in self.atom_cb:
                terms.append(self._bind(self.role_cb[role], self.atom_cb[str(val)]))
        return self._bundle(torch.stack(terms))

    def _cleanup(self, q):
        best, bs = None, -1.0
        for a, v in self.atom_cb.items():
            c = _cos(q, v)
            if c > bs:
                bs, best = c, a
        return best

    def _wrong_role(self, rel, read_role):
        """Negative control: a WRONG role to unbind (a real bound role != read_role; fallback RTYPE)."""
        for (r, _s) in REL_SCHEMA[rel]:
            if r != read_role:
                return r
        return "RTYPE"

    def _readout(self, rel, constraints, read_role, wrong_role=False):
        """Select the fact by cosine to the constraint vector, unbind read_role, cleanup.
        wrong_role=True unbinds a DIFFERENT role (mechanism-load-bearing negative control)."""
        q = self._query_vec(rel, constraints)
        cand = [i for i in range(len(self.facts)) if self.facts[i][0] == rel]
        if not cand:
            return None
        best_i, bs = None, -2.0
        for i in cand:
            c = _cos(self.fact_vecs[i], q)
            if c > bs:
                bs, best_i = c, i
        use_role = self._wrong_role(rel, read_role) if wrong_role else read_role
        got = self._bind(self.fact_vecs[best_i], self.role_cb[use_role].conj())  # unbind
        return self._cleanup(got)

    def run(self, q, wrong_role=False):
        if q["kind"] == "single":
            return self._readout(q["rel"], q["constraints"], q["read_role"], wrong_role)
        if q["kind"] == "multi":
            e = self._readout(q["hop1"]["rel"], q["hop1"]["constraints"], q["hop1"]["read_role"], wrong_role)
            if e is None:
                return None
            c2 = dict(q["hop2"]["fixed"]); c2[q["hop2"]["link_role"]] = e
            return self._readout(q["hop2"]["rel"], c2, q["hop2"]["read_role"], wrong_role)
        if q["kind"] == "conj":
            a = self._readout(q["armA"]["rel"], q["armA"]["constraints"], q["armA"]["read_role"], wrong_role)
            b = self._readout(q["armB"]["rel"], q["armB"]["constraints"], q["armB"]["read_role"], wrong_role)
            return a if (a is not None and a == b) else None
        return None


# ===========================================================================
# Capacity / crosstalk sweep (mandatory discriminator-fires gate). BUNDLED-map control: bundle P random
# bind(role, filler) pairs into ONE vector, unbind each role, cleanup among the P loaded fillers.
# ===========================================================================
def capacity_curve(n_dim, loads, seed):
    import numpy as np
    import torch
    from hdlab.binding import bind
    from hdlab.bundling import bundle
    rng = np.random.default_rng(seed)

    def fhrr(n):
        ph = torch.tensor(rng.uniform(-np.pi, np.pi, size=(n, n_dim)), dtype=torch.float64)
        return torch.complex(torch.cos(ph), torch.sin(ph)).to(torch.complex64)

    curve = {}
    for P in loads:
        roles = fhrr(P)
        fillers = fhrr(P)
        M = bundle(torch.stack([bind(roles[i], fillers[i]) for i in range(P)]))
        hits = 0
        for i in range(P):
            got = bind(M, roles[i].conj())  # unbind role i
            # cleanup among the P loaded fillers
            best, bs = -1, -2.0
            for j in range(P):
                c = _cos(got, fillers[j])
                if c > bs:
                    bs, best = c, j
            hits += int(best == i)
        curve[P] = round(hits / P, 4)
    return curve


# ===========================================================================
# additive_map interface probe (the NAMED reasoner). Ingest reader tuples as (h,r,t) triples, fit,
# single-hop recall@1 on trained triples + on forward-shaped gold single-hops.
# ===========================================================================
def tuples_to_triples(facts):
    """Reader role-filler tuple -> (head, relation, tail) triple(s). Forward = predict tail given h,r."""
    triples = []
    for t in facts:
        rel = t[0]
        if rel == "svo" and len(t) >= 4:
            triples.append((str(t[2]), "V_" + str(t[1]), str(t[3])))       # subj -verb-> obj
        elif rel == "goal" and len(t) >= 4:
            triples.append((str(t[2]), "GOAL", str(t[3])))                  # mover -GOAL-> dest
        elif rel == "loc" and len(t) >= 3:
            triples.append((str(t[1]), "LOC", str(t[2])))                   # ent -LOC-> place
        elif rel == "recipient" and len(t) >= 4:
            triples.append((str(t[2]), "RECIP", str(t[3])))                 # giver -RECIP-> recip
        elif rel == "pred" and len(t) >= 3:
            triples.append((str(t[2]), "PRED_" + str(t[1]), str(t[2])))     # (degenerate; excluded below)
    # drop self-loops / degenerate
    triples = [(h, r, t) for (h, r, t) in triples if h != t and not r.startswith("PRED_")]
    # de-dup deterministically
    return sorted(set(triples), key=lambda x: (x[0], x[1], x[2]))


def additive_map_probe(gold_facts, seed):
    """Returns dict with status + single-hop recall. Loud-but-nonfatal: exceptions recorded, not raised."""
    import torch
    from hdlab.additive_map import AdditiveKGMap
    triples = tuples_to_triples(gold_facts)
    if len(triples) < 6:
        return dict(status="TOO_FEW_TRIPLES", n_triples=len(triples))
    m = AdditiveKGMap(device="cpu")
    m.fit(triples, k=32, epochs=300, seed=seed)
    hit = 0
    for (h, r, t) in triples:
        sc = m.score_all(h, r)
        top = int(torch.argmax(sc).item())
        hit += int(top == m.entity_to_idx[t])
    return dict(status="OK", n_triples=len(triples), n_entities=m.num_entities,
                n_relations=m.num_relations, k=int(m.k),
                recall_at_1=round(hit / len(triples), 4))


# ===========================================================================
# Markers / metrics / crash-diagnostic (atomic).
# ===========================================================================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=f"{type(exc).__name__}: {str(exc)[:500]}",
                summary=f"CELL_CRASHED: {type(exc).__name__}", elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000],
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
                anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# ===========================================================================
# Shared build: reader front-end -> gold -> map (used by self-test + full).
# ===========================================================================
def build_setup(clf, n_distractors=N_DISTRACTORS):
    gold_store = read_tuples(MICRO_PASSAGES, clf)
    gold_facts = collect_facts(gold_store)
    distractors = load_distractors(clf, n_distractors)
    # all_facts = gold + distractors (distractors that duplicate a gold fact are folded in by the set)
    all_facts = sorted(set(gold_facts) | set(distractors),
                       key=lambda t: (t[0], tuple(str(x) for x in t[1:])))
    single = gen_singlehop(gold_facts, all_facts)
    multi = gen_multihop(gold_facts, all_facts)
    conj = gen_conjunctive(gold_facts, all_facts)
    return dict(gold_store=gold_store, gold_facts=gold_facts, all_facts=all_facts,
                distractors=distractors, single=single, multi=multi, conj=conj)


def _score_arm(run_fn, queries):
    hits = 0
    for q in queries:
        got = run_fn(q)
        hits += int(got is not None and got == q["gold"])
    return hits


def evaluate(setup, seed):
    """Run symbolic + FHRR over the query set at one FHRR seed. Returns per-category counts + digests."""
    import numpy as np
    all_facts = setup["all_facts"]
    single, multi, conj = setup["single"], setup["multi"], setup["conj"]
    reasoner = FHRRReasoner(all_facts, N_DIM, seed)

    sym_single = _score_arm(lambda q: run_symbolic_query(all_facts, q), single)
    sym_multi = _score_arm(lambda q: run_symbolic_query(all_facts, q), multi)
    sym_conj = _score_arm(lambda q: run_symbolic_query(all_facts, q), conj)
    hd_single = _score_arm(reasoner.run, single)
    hd_multi = _score_arm(reasoner.run, multi)
    hd_conj = _score_arm(reasoner.run, conj)
    # NEGATIVE CONTROL (mechanism load-bearing): wrong-role unbind must collapse single-hop accuracy.
    hd_single_wrong = _score_arm(lambda q: reasoner.run(q, wrong_role=True), single)
    return dict(
        n_single=len(single), n_multi=len(multi), n_conj=len(conj),
        sym_single=sym_single, sym_multi=sym_multi, sym_conj=sym_conj,
        hd_single=hd_single, hd_multi=hd_multi, hd_conj=hd_conj,
        hd_single_wrong=hd_single_wrong)


# ===========================================================================
# Self-test (design-gate).
# ===========================================================================
def _witness():
    """Scaffold-free 2-hop witness on a hand-built 3-fact map with ZERO training (random FHRR codes)."""
    facts = [("loc", "cat", "pond"), ("svo", "chased", "dog", "cat"), ("svo", "ate", "cat", "fish")]
    reasoner = FHRRReasoner(facts, N_DIM, seed=SEED)
    # single-hop: AGENT of chased with PATIENT=cat -> dog
    q1 = dict(kind="single", rel="svo", constraints={"RVERB": "chased", "RPATIENT": "cat"},
              read_role="RAGENT", gold="dog")
    a1 = reasoner.run(q1)
    # 2-hop: read ENT at pond (=cat), then AGENT that chased that ENT -> dog
    q2 = dict(kind="multi",
              hop1=dict(rel="loc", constraints={"RPLACE": "pond"}, read_role="RENT"),
              hop2=dict(rel="svo", fixed={"RVERB": "chased"}, link_role="RPATIENT", read_role="RAGENT"),
              gold="dog")
    a2 = reasoner.run(q2)
    return a1, a2


def self_test():
    import numpy as np
    print("[self-test] building reader front-end + gold + map ...")
    clf = V2._fit_clf()

    # WITNESS (scaffold-free, zero-training).
    a1, a2 = _witness()
    assert a1 == "dog", f"WITNESS single-hop FAIL: expected dog got {a1}"
    assert a2 == "dog", f"WITNESS 2-hop FAIL: expected dog got {a2}"
    print("[self-test] witness: single-hop -> dog; 2-hop (chaser of the thing at the pond) -> dog")

    # real_code_path: REAL reader emits tuples, REAL AdditiveKGMap consumes them.
    setup = build_setup(clf, n_distractors=60)  # smaller distractor set for a fast smoke
    assert len(setup["gold_facts"]) >= 15, f"too few gold facts: {len(setup['gold_facts'])}"
    assert len(setup["single"]) >= 12, f"too few single-hop queries: {len(setup['single'])}"
    assert len(setup["multi"]) >= 6, f"too few multi-hop queries: {len(setup['multi'])}"
    print(f"[self-test] gold facts={len(setup['gold_facts'])} distractors={len(setup['distractors'])} "
          f"| queries single={len(setup['single'])} multi={len(setup['multi'])} conj={len(setup['conj'])}")

    # DESIGN-GATE: symbolic (the reference) answers its own auto-gold at ~1.0 (non-vacuous, unambiguous).
    ev = evaluate(setup, seed=SEED)
    assert ev["sym_single"] == ev["n_single"], f"symbolic single not 1.0: {ev['sym_single']}/{ev['n_single']}"
    assert ev["sym_multi"] == ev["n_multi"], f"symbolic multi not 1.0: {ev['sym_multi']}/{ev['n_multi']}"
    print(f"[self-test] SYMBOLIC reference: single {ev['sym_single']}/{ev['n_single']}, "
          f"multi {ev['sym_multi']}/{ev['n_multi']}, conj {ev['sym_conj']}/{ev['n_conj']} (=1.0 by construction)")

    print(f"[self-test] FHRR reasoner: single {ev['hd_single']}/{ev['n_single']}, "
          f"multi {ev['hd_multi']}/{ev['n_multi']}, conj {ev['hd_conj']}/{ev['n_conj']}")

    # MECHANISM LOAD-BEARING (arms-differ, done right): the FHRR path is genuinely doing HD binding, not
    # passing the symbolic answer through -> a WRONG-role unbind must collapse single-hop accuracy.
    wrong_f = ev["hd_single_wrong"] / ev["n_single"]
    real_f = ev["hd_single"] / ev["n_single"]
    assert real_f - wrong_f >= 0.30, \
        f"MECHANISM NOT LOAD-BEARING: real single {real_f:.3f} vs wrong-role {wrong_f:.3f} (gap < 0.30) -> " \
        "FHRR readout may not depend on the binding (arm bug)"
    print(f"[self-test] mechanism load-bearing: real-role single {real_f:.3f} vs wrong-role {wrong_f:.3f} "
          f"(gap {real_f - wrong_f:.3f} >= 0.30)")

    # DISCRIMINATOR-FIRES: capacity sweep MUST show degradation at high load at FULL N.
    cap = capacity_curve(N_DIM, loads=[8, 64, 256], seed=SEED)
    assert cap[256] < 0.90, f"capacity discriminator VACUOUS: load-256 readout {cap[256]} >= 0.90 at N={N_DIM}"
    print(f"[self-test] capacity (N={N_DIM}): load8={cap[8]} load64={cap[64]} load256={cap[256]} "
          f"(discriminator fires: 256 < 0.90)")

    # additive_map interface probe (REAL object).
    probe = additive_map_probe(setup["gold_facts"], seed=SEED)
    assert probe["status"] == "OK", f"additive_map probe not OK: {probe}"
    print(f"[self-test] additive_map probe: {probe['n_triples']} triples, "
          f"recall@1={probe['recall_at_1']} (k={probe['k']}, ent={probe['n_entities']})")

    # determinism: two evaluates identical.
    ev2 = evaluate(setup, seed=SEED)
    assert ev == ev2, "non-deterministic evaluate"
    print("[self-test] deterministic (two evaluates identical)")
    print("[self-test] PASS")
    return 0


# ===========================================================================
# --dump: show the reader tuples + generated queries (inspection).
# ===========================================================================
def dump():
    clf = V2._fit_clf()
    setup = build_setup(clf)
    print(f"[dump] gold facts ({len(setup['gold_facts'])}):")
    for t in setup["gold_facts"]:
        print("   ", t)
    print(f"[dump] single-hop queries ({len(setup['single'])}):")
    for q in setup["single"][:20]:
        print("   ", q["rel"], q["constraints"], "->", q["read_role"], "=", q["gold"])
    print(f"[dump] multi-hop queries ({len(setup['multi'])}):")
    for q in setup["multi"][:20]:
        print("   ", q["hop1"], "THEN", q["hop2"], "=", q["gold"])
    print(f"[dump] conjunctive queries ({len(setup['conj'])}):")
    for q in setup["conj"]:
        print("   ", q["armA"], "AND", q["armB"], "=", q["gold"])
    return 0


# ===========================================================================
# Full verdict.
# ===========================================================================
def build_verdict(timeout_s=600):
    import numpy as np
    t0 = time.perf_counter()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    _write_start_marker(OUTPUT_DIR, "full", expected_n_units=N_SEEDS)
    clf = V2._fit_clf()
    setup = build_setup(clf, n_distractors=N_DISTRACTORS)

    n_single, n_multi, n_conj = len(setup["single"]), len(setup["multi"]), len(setup["conj"])

    # multi-seed reasoning (guards against a lucky FHRR draw).
    seeds = [SEED + 7919 * i for i in range(N_SEEDS)]
    per_seed = [evaluate(setup, seed=s) for s in seeds]

    def frac(key_hit, key_n):
        vals = [ps[key_hit] / ps[key_n] if ps[key_n] else 0.0 for ps in per_seed]
        return float(np.mean(vals)), float(np.std(vals))

    sym_single_f = per_seed[0]["sym_single"] / n_single if n_single else 0.0
    sym_multi_f = per_seed[0]["sym_multi"] / n_multi if n_multi else 0.0
    sym_conj_f = per_seed[0]["sym_conj"] / n_conj if n_conj else 0.0
    hd_single_m, hd_single_s = frac("hd_single", "n_single")
    hd_multi_m, hd_multi_s = frac("hd_multi", "n_multi")
    hd_conj_m, hd_conj_s = frac("hd_conj", "n_conj")
    hd_wrong_m, _hd_wrong_s = frac("hd_single_wrong", "n_single")

    # capacity sweep (full load ladder), multi-seed.
    loads = [4, 8, 16, 32, 64, 128, 192, 256]
    cap_seeds = [capacity_curve(N_DIM, loads, seed=s) for s in seeds]
    cap_mean = {P: round(float(np.mean([cs[P] for cs in cap_seeds])), 4) for P in loads}
    # capacity ceiling = largest load with mean readout >= 0.90
    ceiling = max([P for P in loads if cap_mean[P] >= 0.90], default=0)
    plate_bound = round(N_DIM / (2.0 * math.log(max(ceiling, 2))), 1)
    cap_fired = cap_mean[256] < 0.90

    # additive_map interface probe (loud-but-nonfatal).
    try:
        probe = additive_map_probe(setup["gold_facts"], seed=SEED)
    except Exception as e:  # noqa: BLE001 -- recorded loudly, does not invalidate the primary FHRR verdict
        probe = dict(status="ERROR", error=f"{type(e).__name__}: {str(e)[:300]}",
                     traceback=traceback.format_exc()[:2000])
    am_ok = probe.get("status") == "OK"
    am_recall = probe.get("recall_at_1", 0.0)

    # reader fidelity context: authored-passage count vs symbolic-answerable query count.
    reader_fidelity = dict(n_gold_facts=len(setup["gold_facts"]),
                           n_single=n_single, n_multi=n_multi, n_conj=n_conj,
                           note="gold auto-derived from reader tuples; symbolic-answerable by construction")

    # mechanism load-bearing (arms-differ, done right): wrong-role unbind collapses accuracy.
    mechanism_load_bearing = (hd_single_m - hd_wrong_m) >= 0.30

    hard_pass = (hd_single_m >= sym_single_f - 0.10 and hd_multi_m >= 0.70 and hd_conj_m >= 0.70 and
                 am_ok and am_recall >= 0.90 and cap_fired and n_single >= 12 and n_multi >= 6)
    hard_fail = (hd_single_m < sym_single_f - 0.10 or hd_multi_m < 0.40 or
                 (not am_ok) or (am_ok and am_recall < 0.50))

    if hard_pass:
        verdict = "BRIDGE_REASONS_END_TO_END"
    elif hard_fail:
        verdict = "BRIDGE_BROKEN"
    else:
        verdict = "BRIDGE_PARTIAL"

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        anchor_name=ANCHOR_NAME, verdict=verdict,
        verdict_msg=(
            f"HD single {hd_single_m:.3f}+/-{hd_single_s:.3f} (sym {sym_single_f:.3f}); "
            f"HD multi {hd_multi_m:.3f}+/-{hd_multi_s:.3f} (sym {sym_multi_f:.3f}); "
            f"HD conj {hd_conj_m:.3f} (sym {sym_conj_f:.3f}); "
            f"additive_map recall@1={am_recall} ({probe.get('status')}); "
            f"capacity ceiling={ceiling} facts@N={N_DIM} (Plate~{plate_bound}); "
            f"n_q single/multi/conj={n_single}/{n_multi}/{n_conj}"),
        summary=f"{verdict}: HD single {hd_single_m:.2f} multi {hd_multi_m:.2f} conj {hd_conj_m:.2f}; "
                f"additive_map {am_recall}; cap-ceiling {ceiling}",
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(),
        seed=SEED, n_dim=N_DIM, n_seeds=N_SEEDS, n_distractors=len(setup["distractors"]),
        symbolic=dict(single=sym_single_f, multi=sym_multi_f, conj=sym_conj_f),
        fhrr=dict(single_mean=hd_single_m, single_std=hd_single_s,
                  multi_mean=hd_multi_m, multi_std=hd_multi_s,
                  conj_mean=hd_conj_m, conj_std=hd_conj_s),
        negative_control=dict(wrong_role_single_mean=hd_wrong_m,
                              real_minus_wrong=round(hd_single_m - hd_wrong_m, 4),
                              mechanism_load_bearing=bool(mechanism_load_bearing)),
        bridge_fidelity_single=round(hd_single_m - sym_single_f, 4),
        capacity=dict(curve_mean=cap_mean, ceiling_facts=ceiling, plate_bound_est=plate_bound,
                      discriminator_fired=cap_fired),
        additive_map_probe=probe,
        reader_fidelity=reader_fidelity,
        n_query=dict(single=n_single, multi=n_multi, conj=n_conj),
        per_seed=per_seed,
        arms_differ_verified=bool(mechanism_load_bearing),
        REQUIRED_FIELDS=["verdict", "symbolic", "fhrr", "capacity", "additive_map_probe",
                         "bridge_fidelity_single", "n_query"],
        cited=dict(front_end="exp_read_nested_clause_relative_third_reader_v1",
                   reasoner_named="hdlab.additive_map.AdditiveKGMap",
                   plan="notes/learned_in_substrate_reader_plan_forms_hd_reasoning_maps_2026-07-18.md"),
        caveats=[
            "CLEAN-SLICE front-end: hand-authored age-appropriate clean narrative; reader errors (the "
            "~0.40 corpus-wide extraction wall) are OUT of scope -- we test the bridge+reasoner, not "
            "extraction. Gold auto-derived from the reader's OWN tuples (symbolic ~1.0 by construction).",
            "SYMBOLIC is the CEILING on a clean toy KB (exact lookup/join). HD matching it single-hop = "
            "bridge preserves info; HD composing multi-hop = the reasoner earns its keep. HD does NOT "
            "'beat' symbolic on accuracy here -- that is not the claim.",
            "TWO binding families: FHRR (multiplicative, ZERO-training) is the reasoning-map the reader's "
            "structure maps onto directly; additive_map (TransE additive) is the NAMED reasoner and "
            "consumes the tuples-as-triples but REQUIRES a learning step to place coordinates. This "
            "learned-vs-zero-training distinction is the load-bearing Stage-2 localization.",
            "additive_map probe is single-hop FORWARD recall on a small reader-derived KB (memorization "
            "regime); reverse/multi-hop in additive_map = its compose_entity path (prior MRR ~0.128), "
            "out of scope for this bridge diagnostic.",
            "Capacity ceiling is the BUNDLED-map crosstalk bound (Plate O(N/log N)); the reasoning map "
            "is SHARDED (per META_STORAGE), so realistic-passage reasoning sits well inside the ceiling.",
            "single-annotator/auto gold; CLAIM-VET-pending (skunkworks landed-VET before fact).",
        ],
    )
    _write_metrics(OUTPUT_DIR, metrics)
    print(f"[verdict] {verdict} :: {metrics['verdict_msg']} :: {elapsed}s")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()
    try:
        if args.dump:
            return dump()
        if args.self_test:
            return self_test()
        if args.full:
            return build_verdict(timeout_s=args.timeout)
        return self_test()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        print(f"[CRASH] {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
