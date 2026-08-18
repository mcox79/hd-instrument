"""CONSOLIDATED WHO-DID-WHAT READER -- CHAIN-GRADE CANDIDATE (FULL, v1).

THE FINISH: consolidate ALL VET'd reader component winners into ONE composed reader, measure the composed
result on McGuffey (STEP 1 sanity), then run the 4 chain-grade bars on HELD-OUT LitBank (STEP 2, the real
chain-grade test). Builds on the VET'd/banked demo scaffold
(exp_consolidated_reader_chaingrade_demo_v1, banked 29496 -- corpus-invariant 4-bar wiring). This cell is
the CHAIN_GRADE CANDIDATE; it is NOT banked here -- skunkworks does the hardest VET.

COMPONENTS FOLDED IN (all VET'd/banked; every one an IMPORT of its banked cell, none re-transcribed):
  * do/have lever (enumext_v4 KEEPER; ECM dropped) -- E.content_verb_indices_ext(use_dohave=True) is the
    enumeration base; use_ecm=False.
  * POS-slotfix -- POSSLOT.content_verb_indices_ext_v5 (verb-in-noun-slot recovery) +
    POSSLOT.candidate_indices_slotfix (object-pron / reflexive / grounded-adj candidate recovery) +
    POSSLOT._assign_ecm_v5 (candidate->predicate routing with the candidate list threaded).
    NOTE the VET flagged Lever-1's irregular-verb WORD LIST (hurt/knocks/lay/taught) as DEV-SPECIFIC. This
    cell adds content_verb_indices_general (a SYNTACTIC-SLOT rule: recover a NN/NNS token in the empty verb
    slot after a subject candidate, NO McGuffey word list) and REPORTS whether the general version holds on
    McGuffey; LitBank uses the general version (word-list is dev-specific and would not fire on LitBank
    verbs anyway).
  * WH-gap object-relative -- RELGAP.add_relgap (additive post-processor: relative-clause object-gap tuples).
  * spurious-gate G1/G2/G3 + G4-v2 -- GATE1.is_contracted_aux (G1), GATE1._is_nonfactive +
    VC._has_genuine_direct_object (G2), self-loop drop (G3), GATESPLIT.g4_excludes(mode='v2') (G4-v2 =
    POS-skip governing-prep exclusion + RP-particle guard).
  * ROLES-4 relabel -- RELABEL.role_relabel_reassign (emission-preserving NP-head re-label). The banked VET
    found the ditransitive lexicon drives nothing (lexicon-redundant) -> omitted here (ditrans_fn = const
    False).

COMPOSE in pipeline order (per task): enumerate -> candidates -> role-assign -> ROLES relabel -> emission
  gate; WH-gap object-relative tuples added last as an additive post-processor. clause_predicate_pass_composed
  is the single unified pass; with ALL new components OFF it reproduces the demo's ARM A base config
  (E V4_DOHAVE_ONLY: use_dohave=True, use_ecm=False), F1 target 0.592
  CITED@data/exp_multipred_argstruct_enumext_v4/metrics.json:arms.V4_DOHAVE_ONLY.

STEP 1 (McGuffey composed sanity): composed patient-F1 on FULL_SLICE (163 golded sentences) vs V3 base
  0.5738 and DOHAVE base 0.592; per-component MARGINAL contribution (cumulative + each-alone deltas);
  NO net regression. Expected composed ~0.62-0.66.

STEP 2 (HELD-OUT LitBank = the chain-grade test): LitBank is distinct_from_mcguffey. REUSES the verbatim
  reconstruction + hand-authored gold from exp_multi_turn_loop_litbank_ood_fixed_gate_v1 (imported as LB):
  its LITBANK_QS_SPEC carries svo_agent / svo_patient specs = an INDEPENDENT who-did-what gold on verbatim
  public-domain novel prose (Poe/Wilde/Melville/Burnett/Austen), authored for a DIFFERENT cell (anti-circular:
  gold never saw this reader; no component was ever tuned on LitBank). METRIC = who-did-what recovery
  accuracy (fraction of svo gold items the composed reader emits with the correct patient/agent). The 4 bars:
    ARM A: composed reader who-did-what accuracy on the LitBank svo gold (report n_correct/n_gold).
    ARM B (DISCRIMINATOR): the SAME naive positional baseline on the SAME LitBank passages; must recover
      FEWER gold tuples than the composed reader (real baseline fails where structure succeeds).
    ARM C (causal glass-box): on a LitBank sentence -- deterministic replay hash stable; sha256 audit hash +
      one-field tamper breaks it; a causal hand-edit of ONE logged ROLE assignment flips the who-did-what
      tuple (agent<->patient); a bridge head-arc edit re-routes a candidate. Reuses DEMO.trace_clause /
      DEMO._emit_for_predicate / DEMO._canonical_trace_hash byte-identically on LitBank text.
    ARM D (non-ceiling/scale): LitBank IS the held-out generalization; report N (svo gold items across 5
      distinct novels) + the small-N caveat honestly.
  KEY QUESTION reported honestly: which component wins TRANSFER to held-out vs attenuate (VETs flagged: G4-RP
  = held-out insurance; POS-Lever1 word-list = dev-specific -> general slot rule on LitBank; WH-gap needs
  object-relatives present; ROLES-relabel should transfer being structural), and whether all 4 bars PASS
  (chain-grade earned on held-out) or which falls short.

PRE-REGISTERED BANDS (set BEFORE this run):
  STEP 1:
    P1 (fairness base reproduction): F1(BASE composed, all new off) in [0.58, 0.60] (reproduces DOHAVE 0.592
      within re-transcription tolerance) -- reported; a large miss flags a composition bug.
    STEP1_HARD_PASS: F1(FULL composed) >= 0.60 AND F1(FULL) >= F1(BASE) (no net regression) AND
      recall_ceiling(FULL) >= recall_ceiling(BASE) - 0.02.
    STEP1_MIDDLE: F1(FULL) >= F1(BASE) (no regression) but F1(FULL) < 0.60.
    STEP1_HARD_FAIL: F1(FULL) < F1(BASE) (net regression) OR recall_ceiling(FULL) < recall_ceiling(BASE)-0.05.
  STEP 2 (per-bar; the 4-bar chain-grade on held-out):
    ARM A: report acc = n_correct / n_gold on the LitBank svo who-did-what gold. (No fixed floor -- this is
      the held-out generalization measurement; transfer is the finding, reported honestly.)
    ARM B DISCRIMINATOR_FIRES: naive recovers >= 0 (in band, can-fail) AND composed recovers strictly MORE
      gold tuples than naive (n_composed_correct > n_naive_correct) AND naive does not saturate
      (n_naive_correct < n_gold).
    ARM C GLASS_BOX_OK: replay_hash_stable AND tamper_detected AND causal_role_edit_flipped AND
      bridge_head_edit_reroutes (all four True on a LitBank sentence).
    ARM D NON_CEILING_OK: N (svo gold items) reported >= 8 across >= 3 distinct novels + small-N caveat stated.
    CHAIN_GRADE_HELDOUT_EARNED iff ARM A shows POSITIVE transfer (n_composed_correct > 0 AND
      n_composed_correct >= n_naive_correct) AND ARM B FIRES AND ARM C OK AND ARM D reported. Otherwise
      PARTIAL (report which bars hold). Reported honestly; this is a held-out test that CAN attenuate.

FAIRNESS (P1/P2): STEP 1 same reader/gold/split as the demo (FULL_SLICE, gold =
  data/gold_mcguffey_lccp_argstruct_v1.json, independent single-annotator, never read while authoring).
  STEP 2 LitBank gold is verbatim-provenance + hand-authored for a DIFFERENT cell; NO component was tuned on
  LitBank (no train-on-test). Every component is a byte-identical IMPORT. ONE clear variable per arm.

BRAIN-CHECK: constraint-based lexicalist parsing -- syntax + selectional plausibility jointly constrain
  role assignment (MacDonald/Pearlmutter/Seidenberg 1994; Trueswell/Tanenhaus/Garnsey 1994); the positional
  baseline is the linear-order null hypothesis. The spurious-gate is brain-faithful explaining-away /
  precision-weighting / lateral inhibition (structural suppression). Out-of-domain (LitBank) the human
  reader also degrades on adult-literary syntax; the question is whether STRUCTURE still beats ORDER there.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- imports the banked arc-eager parser
  training (~50-65s, once) + per-clause greedy decode (ms/clause) + AveragedPerceptron role clf + O(cand)
  dict lookups; NO matmul/GPU-batchable primitive; ~10 McGuffey ablation arms + LitBank 4 bars, wall ~3-6min
  foreground. Storage: no_storage. Runtime invariant: glass-box (from-scratch parser + curated dicts +
  corpus-observed admissibility + build-time knowledge dict), NO LLM/network/autograd at inference.
  Determinism: OMP/MKL/OPENBLAS=1, fixed int SEED, sorted(set), sha256-derived indices (no builtin hash()).
  LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist / NO queue_add / NO bank (chain-grade
  candidate -> skunkworks VETs separately).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground candidate cell):
  - arms_differ_verified at smoke (hash over composed FULL vs BASE vs NAIVE kept-tuple sets)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band at smoke (0.05 < precision(BASELINE_svo) < 0.95; naive can-fail on LitBank)
  - discriminator fires at smoke: composed recovers >= naive; composed F1 > naive on McGuffey
  - glass-box witnesses at smoke: replay stable, tamper breaks hash, role-edit flips a tuple, head-edit
    re-routes a candidate (all four on a real slice sentence)
  - deterministic seeding (fixed int SEED; sorted(set); sha256 in relgap scramble control, no builtin hash)
  - all numbers tagged MEASURED@ (printed at run) / CITED@ (banked component metrics) in this docstring
  - N/A: KGStore (no KG); N/A CRLB (discrete count/precision measurement, no HD noise floor); N/A multi-seed
    (deterministic given fixed SEED; parser single-seed by design, inherited from V3/E, not hidden)
  - progress_logging: print_flush_true (sys.stdout line-buffered at cell start)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

ANCHOR_NAME = "consolidated_reader_chaingrade_FULL_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Banked components (import does NOT re-run their experiments -- all guarded by __main__).
from experiments import exp_multipred_argstruct_agentfix_kbgate_v3 as V3            # noqa: E402
from experiments import exp_multipred_argstruct_enumext_v4 as E                     # noqa: E402
from experiments import exp_multipred_depparse_argstruct_recall_v2 as M             # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402
from experiments import exp_oracle_mention_upperbound_reader_v1 as ORC              # noqa: E402
from experiments import exp_reader_clauseseg_topical_animate_subject_v2 as V2       # noqa: E402
from experiments import exp_reader_clauseseg_verbclass_filter_v1 as VC              # noqa: E402
# folded-in banked component modules
from experiments import exp_multipred_argstruct_enumext_posslot_v5 as POSSLOT       # noqa: E402
from experiments import exp_multipred_argstruct_relgap_v5 as RELGAP                 # noqa: E402
from experiments import exp_reader_structural_precision_gate_v1 as GATE1            # noqa: E402
from experiments import exp_reader_g4_particle_govprep_split_v1 as GATESPLIT        # noqa: E402
from experiments import exp_reader_role_relabel_emission_preserving_v4 as RELABEL   # noqa: E402
# the VET'd/banked 4-bar demo scaffold (trace + naive + band helpers reused byte-identically)
from experiments import exp_consolidated_reader_chaingrade_demo_v1 as DEMO          # noqa: E402
# held-out LitBank verbatim reconstruction + independent hand-authored who-did-what gold
from experiments import exp_multi_turn_loop_litbank_ood_fixed_gate_v1 as LB         # noqa: E402

FULL_SLICE = M.FULL_SLICE
SMOKE_SLICE = M.SMOKE_SLICE
HALF_A = ["L04", "L05", "L07"]
HALF_B = ["L08", "L09", "L10", "L12"]
SEED = 20260723

# References (MEASURED on disk in prior banked runs)
CITED_V3_F1 = 0.5738       # MEASURED@data/exp_multipred_argstruct_agentfix_kbgate_v3/metrics.json:arms.V3_INTEGRATED.f1
CITED_DOHAVE_F1 = 0.592    # MEASURED@data/exp_multipred_argstruct_enumext_v4/metrics.json:arms.V4_DOHAVE_ONLY.f1

# Pre-registered bands
P1_BASE_LO, P1_BASE_HI = 0.575, 0.605
STEP1_HP_F1 = 0.60
STEP1_RC_TOL = 0.02
STEP1_RC_FAIL = 0.05
ARMD_MIN_N = 8
ARMD_MIN_NOVELS = 3

DITRANS_FN = lambda vl: False   # ditransitive lexicon omitted (banked VET: lexicon-redundant, drives nothing)

_NOUN_POS_GEN = ("NN", "NNS")


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


# =======================================================================================
# Lever-1 GENERALIZATION: syntactic-slot verb-in-noun-slot recovery (NO McGuffey word list).
# Recover a NN/NNS token that sits in the empty verb slot after a subject candidate, when no finite VB
# verb intervenes. Word-identity-free (the banked v5 used a 4-word dev list; this generalizes it).
# =======================================================================================
def content_verb_indices_general(tagged, use_dohave=True):
    base = list(E.content_verb_indices_ext(tagged, use_dohave=use_dohave))
    have = set(base)
    cand = set(ORC.candidate_indices(tagged))
    for i, (surf, low, pos) in enumerate(tagged):
        if i in have:
            continue
        if pos not in _NOUN_POS_GEN:
            continue
        if low in ORC.AUX_LEMMAS:
            continue
        left_subj = [j for j in cand if j < i]
        if not left_subj:
            continue
        js = max(left_subj)
        if any(tagged[k][2].startswith("VB") for k in range(js + 1, i)):
            continue   # a finite verb already fills the slot -> this NN is a real noun
        base.append(i)
    return sorted(set(base))


# =======================================================================================
# The single unified COMPOSED clause pass (pipeline order: enumerate -> candidates -> assign -> role ->
# ROLES relabel -> emission gate). Every step calls a banked component function. With all new flags OFF it
# is byte-faithful to the demo's V4_DOHAVE_ONLY base.
# =======================================================================================
def clause_predicate_pass_composed(tagged, heads, clf, gate_fn, carried_agent_in, sel_fn, ditrans_fn,
                                   flags, supp):
    lows = [t[1] for t in tagged]

    # 1. ENUMERATE predicates
    if flags["enum_general"]:
        predicates = content_verb_indices_general(tagged, use_dohave=flags["use_dohave"])
    elif flags["use_action"]:
        predicates = POSSLOT.content_verb_indices_ext_v5(tagged, use_dohave=flags["use_dohave"], use_action=True)
    else:
        predicates = list(E.content_verb_indices_ext(tagged, use_dohave=flags["use_dohave"]))

    # G1 contraction-normalize drop (a contracted aux mis-tagged VB is never a content predicate)
    if flags["g1"]:
        kept_pred = []
        for i in predicates:
            if GATE1.is_contracted_aux(tagged[i][1]):
                supp["g1_pred_dropped"] += 1
                continue
            kept_pred.append(i)
        predicates = kept_pred

    # 2. CANDIDATES
    if flags["use_slotfix"]:
        candidates = POSSLOT.candidate_indices_slotfix(tagged, use_objpron=True, use_reflexive=True,
                                                       use_fish=True)
    else:
        candidates = ORC.candidate_indices(tagged)

    # 3. ASSIGN candidates -> predicates (posslot hoisted routing; use_ecm=False per DOHAVE keeper config)
    by_pred = POSSLOT._assign_ecm_v5(tagged, heads, predicates, candidates, use_ecm=flags["use_ecm"])
    main_idx, main_verb, main_passive = ORC.find_main_verb(tagged)

    out = []
    carried_agent = carried_agent_in
    evidence = {}
    for v0 in predicates:
        v1 = v0 + 1
        low = tagged[v0][1]
        passive = M._detect_passive(tagged, v0, lows)
        local_cand = sorted(by_pred.get(v1, []))
        first_cand = local_cand[0] if local_cand else None
        vl = L.lemma_verb(low)

        # 4. ROLE assign (AveragedPerceptron)
        roles = {}
        for i in local_cand:
            feats = ORC.candidate_features(tagged, i, v0, passive, first_cand)
            roles[i] = clf.predict(feats)

        # gate-INDEPENDENT bare-NP evidence (over PRE-relabel local_cand; identical to V3/posslot/audit)
        for i in local_cand:
            if i > v0 and ORC.prev_prep(tagged, i) is None:
                evidence[vl] = True

        # 5. ROLES relabel (emission-preserving NP-head re-label; mutates roles in place)
        if flags["relabel"]:
            RELABEL.role_relabel_reassign(roles, local_cand, tagged, v0, passive, gate_fn, ditrans_fn,
                                          use_np_head=True, emission_preserving=True)

        agents_local = [i for i in local_cand if roles.get(i) == "AGENT"]
        patients_local = [i for i in local_cand if roles.get(i) == "PATIENT"]
        resolved_agent = tagged[agents_local[0]][1] if agents_local else carried_agent

        kept_patients = patients_local
        if flags["use_argmax"] and sel_fn is not None and len(patients_local) >= 2:
            def _score(i):
                s = sel_fn(vl, tagged[i][1])
                return -1.0 if s is None else s
            best_i = max(patients_local, key=lambda i: (_score(i), -i))
            kept_patients = [best_i]

        # 6. EMISSION GATE
        # G4 (v2): governing-preposition hard-exclusion with POS-skip + RP-particle guard (per kept patient)
        if flags["g4_mode"] != "off" and kept_patients:
            filt = []
            for pi in kept_patients:
                if GATESPLIT.g4_excludes(tagged, pi, flags["g4_mode"]):
                    supp["g4_patient_excluded"] += 1
                else:
                    filt.append(pi)
            kept_patients = filt
        # G2: non-factive verb-class + no genuine NP direct object
        if flags["g2"] and kept_patients:
            if GATE1._is_nonfactive(low) and not VC._has_genuine_direct_object(tagged, v0):
                supp["g2_emissions_suppressed"] += len(kept_patients)
                kept_patients = []

        if resolved_agent is not None and kept_patients and low not in ("has", "is"):
            if gate_fn(vl):
                is_main = (v0 == main_idx)
                kind = M.predicate_kind(tagged, v0, is_main)
                for pi in kept_patients:
                    # G3: self-loop (agent surface == patient surface)
                    if flags["g3"] and resolved_agent == tagged[pi][1]:
                        supp["g3_selfloops_dropped"] += 1
                        continue
                    out.append((low, resolved_agent, tagged[pi][1], v0, kind))
        if agents_local:
            carried_agent = tagged[agents_local[0]][1]
    return out, carried_agent, evidence


def _one_pass(order, sent_text, W, clf, gate_fn, sel_fn, ditrans_fn, flags, supp):
    out_arm = {}
    evidence_total = {}
    for sid in order:
        raw = sent_text[sid]
        carried = None
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            ct, carried, ev = clause_predicate_pass_composed(tagged, heads, clf, gate_fn, carried,
                                                             sel_fn, ditrans_fn, flags, supp)
            tups.extend([(t[0], t[1], t[2]) for t in ct])
            for k, val in ev.items():
                evidence_total[k] = evidence_total.get(k, False) or val
        out_arm[sid] = tups
    return out_arm, evidence_total


def build_composed_arm(order, sent_text, W, clf, sel_fn, ditrans_fn, flags):
    """Two-pass (evidence -> learned admissibility gate -> real arm), mirroring the banked builders.
    WH-gap object-relative tuples added last as an additive post-processor when flags['whgap']."""
    supp = defaultdict(int)
    # PASS 1: evidence (gate always-True, relabel/gates/argmax off -- identical to V4/posslot evidence pass)
    p1flags = dict(flags)
    p1flags.update(relabel=False, g1=False, g2=False, g3=False, g4_mode="off", use_argmax=False)
    _arm1, evidence = _one_pass(order, sent_text, W, clf, lambda v: True, None, ditrans_fn, p1flags,
                                defaultdict(int))
    gate = M.build_learned_admissibility(evidence)
    # PASS 2: real arm
    arm, _ev2 = _one_pass(order, sent_text, W, clf, gate, sel_fn, ditrans_fn, flags, supp)
    if flags.get("whgap"):
        arm, _fires = RELGAP.add_relgap(arm, sent_text, gate, antescramble=False)
    return arm, gate, dict(supp)


# ---- flag presets --------------------------------------------------------------------
def base_flags():
    return dict(use_dohave=True, use_action=False, enum_general=False, use_slotfix=False, use_ecm=False,
                relabel=False, g1=False, g2=False, g3=False, g4_mode="off", use_argmax=True, whgap=False)


def full_flags():
    f = base_flags()
    f.update(use_action=True, use_slotfix=True, relabel=True, g1=True, g2=True, g3=True, g4_mode="v2",
             whgap=True)
    return f


def full_general_flags():
    """FULL but Lever-1 uses the general syntactic-slot rule instead of the dev word list."""
    f = full_flags()
    f.update(use_action=False, enum_general=True)
    return f


def litbank_flags():
    """Held-out config: general slot rule (word-list dev-specific), everything else on."""
    return full_general_flags()


# =======================================================================================
# Scoring (McGuffey).
# =======================================================================================
def _score_mcg(arm, gold):
    kept = M.to_kept_list(arm)
    sc = L.score_arm(kept, gold)
    rc, miss, npos, misses = M.recall_ceiling_of(arm, gold)
    return sc, rc


def _subset(arm, lessons):
    lset = set(lessons)
    return {sid: v for sid, v in arm.items() if sid.split("_")[0] in lset}


def _subset_gold(gold, lessons):
    lset = set(lessons)
    return {sid: v for sid, v in gold.items() if sid.split("_")[0] in lset}


# =======================================================================================
# STEP 1 -- McGuffey composed sanity + per-component marginal contribution.
# =======================================================================================
def step1_mcguffey(slice_lessons, W, clf, sel_fn):
    order, sent_text, reader_svo = L.load_slice_and_reader(slice_lessons)
    gold, _meta = L.load_gold(slice_lessons)

    def run(flags):
        arm, gate, supp = build_composed_arm(order, sent_text, W, clf, sel_fn, DITRANS_FN, flags)
        sc, rc = _score_mcg(arm, gold)
        return dict(f1=sc["f1"], precision=sc["precision"], recall=sc["recall"], recall_ceiling=rc,
                    n_pred=sc["n_pred"], tp=sc["tp"], n_gold=sc["n_gold"],
                    spurious_verb_fp=sc.get("spurious_verb_fp"), subcat_fp=sc.get("subcat_fp"),
                    kept_hash=M.arm_hash(arm), supp=supp), arm

    # cumulative chain
    cum = {}
    arms = {}
    f = base_flags();                                        cum["C0_BASE"], arms["C0_BASE"] = run(f)
    f = base_flags(); f.update(use_action=True, use_slotfix=True)
    cum["C1_SLOTFIX"], arms["C1_SLOTFIX"] = run(f)
    f.update(relabel=True);                                  cum["C2_RELABEL"], arms["C2_RELABEL"] = run(f)
    f.update(g1=True, g2=True, g3=True, g4_mode="v2");       cum["C3_GATE"], arms["C3_GATE"] = run(f)
    f.update(whgap=True);                                    cum["C4_FULL"], arms["C4_FULL"] = run(f)

    # each-alone over base (marginal attribution)
    alone = {}
    for name, upd in (("A_SLOTFIX", dict(use_action=True, use_slotfix=True)),
                      ("A_RELABEL", dict(relabel=True)),
                      ("A_GATE", dict(g1=True, g2=True, g3=True, g4_mode="v2")),
                      ("A_WHGAP", dict(whgap=True)),
                      ("A_ENUMGENERAL", dict(use_action=False, enum_general=True))):
        f = base_flags(); f.update(upd)
        alone[name], _ = run(f)

    # general-Lever-1 variant of the FULL composed (report whether it holds on McGuffey)
    fullgen, _ = run(full_general_flags())

    base_f1 = cum["C0_BASE"]["f1"]
    base_rc = cum["C0_BASE"]["recall_ceiling"]
    full_f1 = cum["C4_FULL"]["f1"]
    full_rc = cum["C4_FULL"]["recall_ceiling"]

    marginal = {
        "slotfix": round(cum["C1_SLOTFIX"]["f1"] - cum["C0_BASE"]["f1"], 4),
        "relabel": round(cum["C2_RELABEL"]["f1"] - cum["C1_SLOTFIX"]["f1"], 4),
        "gate": round(cum["C3_GATE"]["f1"] - cum["C2_RELABEL"]["f1"], 4),
        "whgap": round(cum["C4_FULL"]["f1"] - cum["C3_GATE"]["f1"], 4),
    }
    marginal_alone = {k: round(v["f1"] - base_f1, 4) for k, v in alone.items()}

    p1_ok = (P1_BASE_LO <= base_f1 <= P1_BASE_HI)
    no_regression = (full_f1 >= base_f1 - 1e-9)
    rc_ok = (full_rc >= base_rc - STEP1_RC_TOL)
    rc_fail = (full_rc < base_rc - STEP1_RC_FAIL)
    if not no_regression or rc_fail:
        step1_verdict = "STEP1_HARD_FAIL"
    elif full_f1 >= STEP1_HP_F1 and rc_ok:
        step1_verdict = "STEP1_HARD_PASS"
    else:
        step1_verdict = "STEP1_MIDDLE"

    return dict(order_n=len(order), gold_n=len(gold), cumulative=cum, alone=alone,
                full_general=fullgen, marginal_cumulative=marginal, marginal_alone=marginal_alone,
                base_f1=base_f1, full_f1=full_f1, base_rc=base_rc, full_rc=full_rc,
                v3_ref=CITED_V3_F1, dohave_ref=CITED_DOHAVE_F1,
                p1_base_reproduction_ok=p1_ok, no_net_regression=no_regression,
                recall_ceiling_ok=rc_ok, step1_verdict=step1_verdict,
                arms_hashes={k: v["kept_hash"] for k, v in cum.items()}), (order, sent_text, gold, arms)


# =======================================================================================
# STEP 2 -- HELD-OUT LitBank who-did-what (the 4 chain-grade bars).
# =======================================================================================
def _norm(w):
    return (w or "").lower().strip().strip('.,;:"\'!?()')


def litbank_gold_and_passages():
    passages, _qs = LB.build_litbank_corpus()
    gold = []
    novels = {}
    for (qid, pid, spec, ans, text) in LB.LITBANK_QS_SPEC:
        work = LB.LITBANK_WINDOWS[pid][0]
        novels[pid] = work
        if spec[0] == "svo_patient":
            gold.append(dict(qid=qid, pid=pid, kind="patient", verb=spec[1], other=spec[2], answer=ans))
        elif spec[0] == "svo_agent":
            gold.append(dict(qid=qid, pid=pid, kind="agent", verb=spec[1], other=spec[2], answer=ans))
    n_novels = len(set(LB.LITBANK_WINDOWS[g["pid"]][0] for g in gold))
    return passages, gold, n_novels


def _score_litbank(arm, gold):
    """arm: {pid: [(low, agent, patient)]}. Match each svo gold item to an emitted tuple with the same
    verb-lemma and the correct patient (kind=patient) or agent (kind=agent) surface (normalized)."""
    n_correct = 0
    per_item = []
    for g in gold:
        vlem = L.lemma_verb(g["verb"])
        hit = False
        matched = None
        for (low, agent, patient) in arm.get(g["pid"], []):
            if L.lemma_verb(low) != vlem:
                continue
            if g["kind"] == "patient" and _norm(patient) == _norm(g["answer"]):
                hit = True; matched = (low, agent, patient); break
            if g["kind"] == "agent" and _norm(agent) == _norm(g["answer"]):
                hit = True; matched = (low, agent, patient); break
        n_correct += int(hit)
        per_item.append(dict(qid=g["qid"], pid=g["pid"], kind=g["kind"], verb=g["verb"],
                             answer=g["answer"], correct=hit, matched=list(matched) if matched else None))
    return n_correct, per_item


def naive_positional_on_text(order, sent_text):
    """The demo's naive positional discriminator, adapted to raw passage text (nearest-noun-LEFT = agent,
    nearest-noun-RIGHT = patient; NO parse, NO role clf, NO gate)."""
    out = {}
    for sid in order:
        raw = sent_text[sid]
        tups = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            verbs = M.content_verb_indices(tagged)
            cands = ORC.candidate_indices(tagged)
            for v0 in verbs:
                left = [i for i in cands if i < v0]
                right = [i for i in cands if i > v0]
                if not right:
                    continue
                agent_i = max(left) if left else None
                if agent_i is None:
                    continue
                patient_i = min(right)
                tups.append((tagged[v0][1], tagged[agent_i][1], tagged[patient_i][1]))
        out[sid] = tups
    return out


def glass_box_on_texts(order, sent_text, W, clf, gate_fn, sel_fn):
    """Reuse DEMO.trace_clause / DEMO._emit_for_predicate / DEMO._canonical_trace_hash on LitBank passages.
    Returns the four glass-box gate booleans + witnesses. Byte-identical glass-box machinery to the banked
    demo; only the corpus (verbatim LitBank text) differs."""
    replay_hash_stable = None
    tamper_detected = None
    audit_witness = None
    for sid in order:
        raw = sent_text[sid]
        carried = None
        emitted_all = []
        traces = []
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            tr, emt, carried = DEMO.trace_clause(tagged, heads, clf, gate_fn, sel_fn, carried)
            traces.append(tr)
            emitted_all.extend(emt)
        if emitted_all:
            carried2 = None
            traces2 = []
            for clause_text in ORC.split_sentences(raw):
                tagged = ORC.pos_tag_sentence(clause_text)
                if not tagged:
                    continue
                heads = M.decode_clause(tagged, W)
                tr2, _e2, carried2 = DEMO.trace_clause(tagged, heads, clf, gate_fn, sel_fn, carried2)
                traces2.append(tr2)
            h1 = DEMO._canonical_trace_hash(traces)
            h2 = DEMO._canonical_trace_hash(traces2)
            replay_hash_stable = (h1 == h2)
            tampered = json.loads(json.dumps(traces))
            mutated = False
            for tr in tampered:
                for prec in tr["predicates"]:
                    if prec["roles"]:
                        k0 = sorted(prec["roles"].keys())[0]
                        orig = prec["roles"][k0]
                        prec["roles"][k0] = "PATIENT" if orig != "PATIENT" else "AGENT"
                        mutated = True
                        break
                if mutated:
                    break
            h_tamper = DEMO._canonical_trace_hash(tampered)
            tamper_detected = mutated and (h_tamper != h1)
            audit_witness = dict(sid=sid, sentence=raw[:160], audit_hash=h1, replay_hash=h2,
                                 tamper_hash=h_tamper, emitted=[list(t) for t in emitted_all])
            break

    # causal ROLE edit flip (single-clause passage for determinism)
    causal_role_edit_flipped = None
    causal_witness = None
    for sid in order:
        raw = sent_text[sid]
        clauses = ORC.split_sentences(raw)
        if len(clauses) != 1:
            continue
        tagged = ORC.pos_tag_sentence(clauses[0])
        if not tagged:
            continue
        heads = M.decode_clause(tagged, W)
        tr, emt, _c = DEMO.trace_clause(tagged, heads, clf, gate_fn, sel_fn, None)
        for prec in tr["predicates"]:
            roles = {int(k): v for k, v in prec["roles"].items()}
            agents = [i for i in prec["local_cand"] if roles.get(i) == "AGENT"]
            patients = [i for i in prec["local_cand"] if roles.get(i) == "PATIENT"]
            base_emit = DEMO._emit_for_predicate(prec, carried_agent=None)
            if len(agents) == 1 and len(patients) >= 1 and base_emit:
                a_i, p_i = agents[0], patients[0]
                override = {a_i: "PATIENT", p_i: "AGENT"}
                edited_emit = DEMO._emit_for_predicate(prec, carried_agent=None, role_overrides=override)
                if base_emit and edited_emit and base_emit[0] != edited_emit[0] and \
                        base_emit[0][1] == edited_emit[0][2] and base_emit[0][2] == edited_emit[0][1]:
                    causal_role_edit_flipped = True
                    causal_witness = dict(sid=sid, sentence=clauses[0], verb=prec["low"],
                                          edited_step="role assignment (AGENT<->PATIENT swap on one logged "
                                                      "candidate pair)",
                                          before=list(base_emit[0]), after=list(edited_emit[0]))
                    break
        if causal_role_edit_flipped:
            break
    if causal_role_edit_flipped is None:
        causal_role_edit_flipped = False

    # bridge parse head-arc edit reroutes a candidate
    bridge_head_edit_reroutes = None
    bridge_witness = None
    for sid in order:
        raw = sent_text[sid]
        for clause_text in ORC.split_sentences(raw):
            tagged = ORC.pos_tag_sentence(clause_text)
            if not tagged:
                continue
            heads = M.decode_clause(tagged, W)
            verbs = E.content_verb_indices_ext(tagged, use_dohave=True)
            if len(verbs) < 2:
                continue
            by_pred = E.assign_candidates_to_predicates_ecm(tagged, heads, verbs, use_ecm=False)
            cand0 = None
            p1a = None
            for p1, cands in by_pred.items():
                if cands:
                    cand0 = sorted(cands)[0]
                    p1a = p1
                    break
            if cand0 is None:
                continue
            others = [v + 1 for v in verbs if (v + 1) != p1a]
            if not others:
                continue
            p1b = sorted(others)[0]
            edited_heads = dict(heads)
            edited_heads[cand0 + 1] = p1b
            new_by_pred = E.assign_candidates_to_predicates_ecm(tagged, edited_heads, verbs, use_ecm=False)
            was_in_a = cand0 in by_pred.get(p1a, [])
            now_in_b = cand0 in new_by_pred.get(p1b, [])
            now_in_a = cand0 in new_by_pred.get(p1a, [])
            if was_in_a and now_in_b and not now_in_a:
                bridge_head_edit_reroutes = True
                bridge_witness = dict(sid=sid, sentence=clause_text[:160], candidate=tagged[cand0][1],
                                      edited_step="parse head-arc (re-pointed one candidate's head)",
                                      from_predicate=tagged[p1a - 1][1], to_predicate=tagged[p1b - 1][1])
                break
        if bridge_head_edit_reroutes:
            break
    if bridge_head_edit_reroutes is None:
        bridge_head_edit_reroutes = False

    glass_box_ok = bool(replay_hash_stable and tamper_detected and causal_role_edit_flipped
                        and bridge_head_edit_reroutes)
    return dict(replay_hash_stable=bool(replay_hash_stable), tamper_detected=bool(tamper_detected),
                causal_role_edit_flipped=bool(causal_role_edit_flipped),
                bridge_head_edit_reroutes=bool(bridge_head_edit_reroutes), glass_box_ok=glass_box_ok,
                audit_witness=audit_witness, causal_witness=causal_witness, bridge_witness=bridge_witness)


def step2_litbank(W, clf, sel_fn):
    passages, gold, n_novels = litbank_gold_and_passages()
    order = sorted(passages.keys())

    # ARM A: composed reader (held-out config: general slot rule) who-did-what accuracy
    arm, gate, supp = build_composed_arm(order, passages, W, clf, sel_fn, DITRANS_FN, litbank_flags())
    n_comp, per_item_comp = _score_litbank(arm, gold)

    # ARM B: naive positional discriminator on the same passages
    naive = naive_positional_on_text(order, passages)
    n_naive, per_item_naive = _score_litbank(naive, gold)

    n_gold = len(gold)
    arm_b_fires = (n_comp > n_naive and n_naive < n_gold)

    # ARM C: glass-box on a LitBank sentence
    gb = glass_box_on_texts(order, passages, W, clf, gate, sel_fn)

    # ARM D: N + small-N caveat
    arm_d_ok = (n_gold >= ARMD_MIN_N and n_novels >= ARMD_MIN_NOVELS)

    arm_a_positive_transfer = (n_comp > 0 and n_comp >= n_naive)
    chain_grade_heldout = bool(arm_a_positive_transfer and arm_b_fires and gb["glass_box_ok"] and arm_d_ok)

    # which recovered items are UNIQUE to composed (transfer evidence)
    comp_correct = set(x["qid"] for x in per_item_comp if x["correct"])
    naive_correct = set(x["qid"] for x in per_item_naive if x["correct"])
    recovered_vs_naive = sorted(comp_correct - naive_correct)

    return dict(
        n_gold=n_gold, n_novels=n_novels, n_passages=len(order),
        arm_a=dict(n_correct=n_comp, accuracy=round(n_comp / n_gold, 4) if n_gold else 0.0,
                   per_item=per_item_comp, arm_hash=M.arm_hash(arm), supp=supp),
        arm_b_naive=dict(n_correct=n_naive, accuracy=round(n_naive / n_gold, 4) if n_gold else 0.0,
                         per_item=per_item_naive, arm_hash=M.arm_hash(naive), fires=arm_b_fires,
                         recovered_by_composed_not_naive=recovered_vs_naive),
        arm_c_glass_box=gb,
        arm_d=dict(n_gold=n_gold, n_novels=n_novels, min_n=ARMD_MIN_N, min_novels=ARMD_MIN_NOVELS,
                   ok=arm_d_ok,
                   small_n_caveat=("Held-out who-did-what gold is SMALL (N=%d svo items across %d novels): "
                                   "this is a held-out GENERALIZATION probe, not a large-sample accuracy "
                                   "estimate. LitBank is the OOD generalization set; no component was tuned "
                                   "on it (no train-on-test). A larger held-out who-did-what gold would "
                                   "tighten the estimate (flagged follow-up)." % (n_gold, n_novels))),
        arm_a_positive_transfer=arm_a_positive_transfer,
        chain_grade_heldout_earned=chain_grade_heldout,
        bars=dict(ARM_A_transfer=arm_a_positive_transfer, ARM_B_discriminator_fires=arm_b_fires,
                  ARM_C_glass_box_ok=gb["glass_box_ok"], ARM_D_non_ceiling_reported=arm_d_ok),
    ), arm


# =======================================================================================
# Markers / metrics / crash-diagnostic (atomic).
# =======================================================================================
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
                ts_iso=datetime.now(timezone.utc).isoformat(), pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics(output_dir, diag)


# =======================================================================================
# Self-test (design-gate; smoke scale).
# =======================================================================================
def self_test():
    print("[self-test] fit clf + knowledge table + smoke parser ...", flush=True)
    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)
    W, parser_info = M.train_dep_parser("smoke")
    assert parser_info["uas_dev"] > 0.5, f"parser UAS suspiciously low: {parser_info}"

    order, sent_text, reader_svo = L.load_slice_and_reader(SMOKE_SLICE)
    gold, _ = L.load_gold(SMOKE_SLICE)

    # BASE composed reproduces the DOHAVE-only base regime (P1)
    base_arm, _g, _s = build_composed_arm(order, sent_text, W, clf, sel_fn, DITRANS_FN, base_flags())
    b_sc, b_rc = _score_mcg(base_arm, gold)
    print(f"[self-test] BASE composed (SMOKE) f1={b_sc['f1']} prec={b_sc['precision']} rc={b_rc}", flush=True)
    assert 0.05 < b_sc["precision"] < 0.95, f"BASE precision {b_sc['precision']} out of band"

    # FULL composed
    full_arm, gate, _s = build_composed_arm(order, sent_text, W, clf, sel_fn, DITRANS_FN, full_flags())
    f_sc, f_rc = _score_mcg(full_arm, gold)
    print(f"[self-test] FULL composed (SMOKE) f1={f_sc['f1']} prec={f_sc['precision']} rc={f_rc}", flush=True)

    # arms differ (composed FULL vs BASE vs naive)
    naive = naive_positional_on_text(order, sent_text)
    hb, hf, hn = M.arm_hash(base_arm), M.arm_hash(full_arm), M.arm_hash(naive)
    assert len({hb, hf, hn}) >= 2, f"META_RULE_AF: arm hashes collide base={hb} full={hf} naive={hn}"
    print(f"[self-test] arms_differ: base={hb} full={hf} naive={hn}", flush=True)

    # determinism (two FULL runs identical)
    full_arm2, _g2, _s2 = build_composed_arm(order, sent_text, W, clf, sel_fn, DITRANS_FN, full_flags())
    assert M.arm_hash(full_arm) == M.arm_hash(full_arm2), "non-deterministic composed reader"

    # LitBank gold reconstruction + provenance sanity
    passages, ldg, n_novels = litbank_gold_and_passages()
    assert len(ldg) >= ARMD_MIN_N, f"LitBank svo gold too small: {len(ldg)}"
    print(f"[self-test] LitBank svo who-did-what gold N={len(ldg)} across {n_novels} novels; "
          f"n_passages={len(passages)}", flush=True)

    # glass-box on LitBank (all four gates) -- design-gate that ARM C fires OOD
    order_lb = sorted(passages.keys())
    _arm_lb, gate_lb, _s = build_composed_arm(order_lb, passages, W, clf, sel_fn, DITRANS_FN, litbank_flags())
    gb = glass_box_on_texts(order_lb, passages, W, clf, gate_lb, sel_fn)
    print(f"[self-test] ARM C (LitBank) replay={gb['replay_hash_stable']} tamper={gb['tamper_detected']} "
          f"role_flip={gb['causal_role_edit_flipped']} bridge={gb['bridge_head_edit_reroutes']}", flush=True)
    assert gb["replay_hash_stable"], "GLASS-BOX: replay hash not stable on LitBank"
    assert gb["tamper_detected"], "GLASS-BOX: tamper did not break hash on LitBank"
    assert gb["causal_role_edit_flipped"], "GLASS-BOX: causal role-edit did not flip on LitBank"
    assert gb["bridge_head_edit_reroutes"], "GLASS-BOX: bridge head-edit did not re-route on LitBank"

    print("[self-test] PASS", flush=True)
    return 0


# =======================================================================================
# Full run (STEP 1 McGuffey to completion, then STEP 2 LitBank).
# =======================================================================================
def build_verdict(output_dir, run_mode):
    t0 = time.perf_counter()
    slice_lessons = SMOKE_SLICE if run_mode == "smoke" else FULL_SLICE
    _write_start_marker(output_dir, run_mode, expected_n_units=len(slice_lessons))
    print(f"[full] mode={run_mode} slice={slice_lessons}", flush=True)

    clf = V2._fit_clf()
    ratings_table = V3.load_knowledge_table()
    sel_fn = V3.build_sel_fn(ratings_table)
    W, parser_info = M.train_dep_parser(run_mode)
    print(f"[full] parser trained uas={parser_info['uas_dev']}", flush=True)

    # ---- STEP 1 (McGuffey composed sanity) ----
    print("[full] STEP 1 -- McGuffey composed + per-component marginal ...", flush=True)
    s1, _mcg = step1_mcguffey(slice_lessons, W, clf, sel_fn)
    print(f"[full] STEP1 base_f1={s1['base_f1']} full_f1={s1['full_f1']} verdict={s1['step1_verdict']} "
          f"marginal_cumulative={s1['marginal_cumulative']} full_general_f1={s1['full_general']['f1']}",
          flush=True)

    # ---- STEP 2 (HELD-OUT LitBank 4 bars) ----
    print("[full] STEP 2 -- HELD-OUT LitBank who-did-what 4 bars ...", flush=True)
    s2, _lb = step2_litbank(W, clf, sel_fn)
    print(f"[full] STEP2 ARM_A n_correct={s2['arm_a']['n_correct']}/{s2['n_gold']} "
          f"acc={s2['arm_a']['accuracy']} | ARM_B naive={s2['arm_b_naive']['n_correct']} "
          f"fires={s2['arm_b_naive']['fires']} | ARM_C ok={s2['arm_c_glass_box']['glass_box_ok']} | "
          f"ARM_D ok={s2['arm_d']['ok']} | chain_grade_heldout={s2['chain_grade_heldout_earned']}",
          flush=True)

    # ---- overall verdict ----
    step1_pass = s1["step1_verdict"] in ("STEP1_HARD_PASS", "STEP1_MIDDLE") and s1["no_net_regression"]
    heldout = s2["chain_grade_heldout_earned"]
    bars_held = [k for k, v in s2["bars"].items() if v]
    bars_short = [k for k, v in s2["bars"].items() if not v]

    if s1["step1_verdict"] == "STEP1_HARD_FAIL":
        verdict = "COMPOSED_STEP1_REGRESSION"
        vmsg = (f"STEP1 REGRESSION: composed FULL f1={s1['full_f1']} < base f1={s1['base_f1']} OR "
                f"recall-ceiling collapse. Localize the regressing component "
                f"(marginal_cumulative={s1['marginal_cumulative']}) before escalating.")
    elif heldout:
        verdict = "CHAIN_GRADE_HELDOUT_EARNED"
        vmsg = (f"CHAIN_GRADE on HELD-OUT LitBank: composed reader recovers "
                f"{s2['arm_a']['n_correct']}/{s2['n_gold']} svo who-did-what gold items (acc="
                f"{s2['arm_a']['accuracy']}) vs naive {s2['arm_b_naive']['n_correct']} (discriminator FIRES, "
                f"reader recovers {s2['arm_b_naive']['recovered_by_composed_not_naive']} the naive baseline "
                f"misses); glass-box OK on a LitBank sentence (replay/tamper/role-flip/bridge all True); "
                f"N={s2['n_gold']} across {s2['n_novels']} novels (small-N held-out probe). STEP1 McGuffey "
                f"composed f1={s1['full_f1']} (base {s1['base_f1']}, {s1['step1_verdict']}). "
                f"HYPOTHESIS pending skunkworks landed-VET.")
    else:
        verdict = "CHAIN_GRADE_HELDOUT_PARTIAL"
        vmsg = (f"HELD-OUT PARTIAL: bars held={bars_held} short={bars_short}. Composed LitBank "
                f"who-did-what {s2['arm_a']['n_correct']}/{s2['n_gold']} (acc={s2['arm_a']['accuracy']}) vs "
                f"naive {s2['arm_b_naive']['n_correct']}; ARM_B fires={s2['arm_b_naive']['fires']}; "
                f"glass_box_ok={s2['arm_c_glass_box']['glass_box_ok']}; ARM_D ok={s2['arm_d']['ok']}. "
                f"STEP1 McGuffey composed f1={s1['full_f1']} ({s1['step1_verdict']}). Report which component "
                f"wins TRANSFER vs attenuate; held-out generalization CAN attenuate -- reported honestly.")

    elapsed = round(time.perf_counter() - t0, 2)
    metrics = dict(
        verdict=verdict, verdict_msg=vmsg,
        summary=(f"{verdict}: STEP1 mcg composed f1={s1['full_f1']} (base={s1['base_f1']} "
                 f"dohave_ref={CITED_DOHAVE_F1} v3_ref={CITED_V3_F1}; {s1['step1_verdict']}; "
                 f"marginal={s1['marginal_cumulative']}) | STEP2 litbank who-did-what "
                 f"composed={s2['arm_a']['n_correct']}/{s2['n_gold']} naive={s2['arm_b_naive']['n_correct']} "
                 f"ARM_B_fires={s2['arm_b_naive']['fires']} glass_box={s2['arm_c_glass_box']['glass_box_ok']} "
                 f"ARM_D={s2['arm_d']['ok']} chain_grade_heldout={heldout} | parser_uas={parser_info['uas_dev']}"),
        elapsed_s=elapsed, ts_iso=datetime.now(timezone.utc).isoformat(),
        anchor_name=ANCHOR_NAME, run_mode=run_mode, seed=SEED, slice_lessons=slice_lessons,
        step1_mcguffey=s1, step2_litbank=s2,
        chain_grade_heldout_earned=heldout,
        one_variable=("STEP1: cumulative + each-alone component ablation over the DOHAVE base (one component "
                      "per arm). STEP2: ARM A composed reader (held-out general slot-rule config) vs ARM B "
                      "naive positional (structure vs order); ARM C one edited logged intermediate vs "
                      "unedited; ARM D which held-out sample. All components byte-identical IMPORT of banked "
                      "cells."),
        bands=dict(P1_BASE_LO=P1_BASE_LO, P1_BASE_HI=P1_BASE_HI, STEP1_HP_F1=STEP1_HP_F1,
                   STEP1_RC_TOL=STEP1_RC_TOL, ARMD_MIN_N=ARMD_MIN_N, ARMD_MIN_NOVELS=ARMD_MIN_NOVELS,
                   CITED_V3_F1=CITED_V3_F1, CITED_DOHAVE_F1=CITED_DOHAVE_F1),
        parser_info=parser_info,
        transfer_summary=("Component transfer to held-out LitBank (VET hypotheses): G4-RP = held-out "
                          "insurance; POS-Lever1 word-list DEV-SPECIFIC -> general syntactic-slot rule used "
                          "on LitBank; WH-gap needs object-relatives present; ROLES-relabel structural -> "
                          "should transfer. Which persist is MEASURED in step2_litbank.arm_b_naive."
                          "recovered_by_composed_not_naive + per_item."),
        scope_caveat=("Parser trained on UD-EWT (newswire/web) via from-scratch arc-eager at a foreground "
                      "budget; OOD transfer to McGuffey narrative AND LitBank adult-literary prose is the "
                      "SAME untested transfer V3/E flagged. STEP2 held-out who-did-what gold is SMALL "
                      "(verbatim-provenance, hand-authored for a DIFFERENT cell; anti-circular; NO train-on-"
                      "test) -- a held-out GENERALIZATION probe, not a large-sample estimate. This is a "
                      "CHAIN-GRADE CANDIDATE (composed reader wiring), CLAIM-VET-pending; strategic read = "
                      "HYPOTHESIS pending skunkworks landed-VET. NOT banked."),
    )
    _write_metrics(output_dir, metrics)
    print(metrics["summary"], flush=True)
    print("verdict:", verdict, flush=True)
    print("verdict_msg:", vmsg, flush=True)
    print("step1_marginal_cumulative:", json.dumps(s1["marginal_cumulative"]), flush=True)
    print("step1_marginal_alone:", json.dumps(s1["marginal_alone"]), flush=True)
    print("step2_arm_a_per_item:", json.dumps([{k: it[k] for k in ("qid", "kind", "verb", "answer",
          "correct")} for it in s2["arm_a"]["per_item"]]), flush=True)
    print("step2_recovered_by_composed_not_naive:",
          json.dumps(s2["arm_b_naive"]["recovered_by_composed_not_naive"]), flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run-mode", default="full")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    run_mode = "smoke" if args.smoke else args.run_mode
    output_dir = _out_dir(run_mode)
    return build_verdict(output_dir, run_mode)


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc if rc is not None else 0)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out_dir("full"), e)
        raise
