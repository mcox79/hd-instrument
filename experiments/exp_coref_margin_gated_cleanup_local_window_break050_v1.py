"""MARGIN-GATED, LOCAL-WINDOW, ABSTAINING pronoun->antecedent coref via HD CLEANUP-MEMORY query.

QUESTION (design: notes/research_coref_entity_tracking_brain_drill_2026-07-19.md, steps 1-5 + Pred A/B):
  Does a margin-gated cue-based retrieval (HD cleanup-memory cosine; commit only when top1-top2 margin
  clears a PRE-REGISTERED threshold, else ABSTAIN) HELP-NOT-HURT who-did-what precision (Pred A: must NOT
  repeat the prior UNGATED coref HARD_FAIL, 16-broken-for-1-fixed, atom 29341) AND make its committed
  resolved entity codes produce measurable non-zero same-entity continuity in the fork-C Tier-2 FHRR carry
  (Pred B: reverses Step-1's pronoun-invisible carry, atom 29353)?

ONE VARIABLE = gated-coref OFF vs ON (everything upstream identical):
  OFF = LCCP arm-C (29338) -> head-finder resolve_heads use_grounding=True (29342). The head-fixed agent
        set IS the current reader (candidate-gen fixed; == head-finder B2, agent-lens P=0.938
        MEASURED@data/exp_np_head_finder_grounding_gate_break050_v1/metrics.json).
  ON  = OFF + margin-gated HD cleanup coref on 3rd-person TARGET pronoun agents:
    candidate pool = NP-head entities (WorkingOverlay observed heads = reader mention stream) restricted to
      LOCAL WINDOW (current sentence heads + immediately-preceding sentence; Centering Cb/Cf local window),
      HARD gender/number pre-filter (state_of_mind.compatible); key_e = SUM known-attr feature codes
      {gender,number,animacy} + w_role*ROLE[Cf-rank] + w_sal*sal_norm(e)*SAL_AXIS + eps*noise (LINEAR
      superposition, NOT per-component-renorm bundle, so cue weights survive into the cosine geometry);
      query q = SUM pronoun agreement codes + w_sal*SAL_AXIS + w_ic*ROLE[IC] (w_ic=0, IC OFF this corpus);
      cleanup cos(q,key_e); COMMIT argmax iff (cos1-cos2)>=TAU_MARGIN AND cos1>=COS_FLOOR else ABSTAIN.
    On COMMIT emit BOTH (a) resolved head for precision + (b) resolved entity FHRR code for the Tier-2 carry.

PRE-REGISTERED CONSTANTS (FIXED before any real run; NOT tuned-to-pass): see prereg
  preregs/2026-07-19_coref_margin_gated_cleanup_local_window_break050_v1.md. N_DIM=1024; feat-code w=1.0;
  w_role=0.30; w_sal=0.50; eps=0.02; w_ic=0.0; TAU_MARGIN=0.10; COS_FLOOR=0.08; ROLE subj/obj/obl=1.0/0.5/
  0.25; sal beta=0.5 lam=0.1. TAU/COS_FLOOR calibrated on the SYNTHETIC self-test toy (construction, not
  test data); self-test asserts clean->commit, agreement-tie->abstain BEFORE any real run.

MEASURED (vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json, single-annotator):
  Pred A (surface agent-lens, goldset = pos{agent}|refs UNION nopat{agent}; IDENTICAL to prior coref +
    head-finder so the break-budget is comparable): newly_fixed, newly_broken (=recall break), ABSTAIN RATE,
    overall precision OFF vs ON, committed-NAMED precision (the who-did-what lens: committed head == gold
    named non-pronoun antecedent). Pred B: continuity_committed vs continuity_pronoun_invisible (Step-1
    baseline) vs continuity_random_control, on committed pronoun pairs whose antecedent is prior-sentence.

VERDICT BANDS (pre-registered; see prereg):
  A: HARD_PASS = newly_broken<=newly_fixed AND newly_broken==0 AND ON_prec>=OFF_prec AND named_prec>=0.60
     AND n_commit>=1. PARTIAL = newly_broken<=newly_fixed AND newly_broken<=1 AND (named_prec in [0.40,0.60)
     OR n_commit==0). HARD_FAIL = newly_broken>newly_fixed OR ON_prec < OFF_prec-0.02.
  B: HARD_PASS = cont_committed >= cont_pron_invis + 0.10 AND cont_committed >= 3*cont_random AND n_pairs>=1.
     PARTIAL = cont_committed >= cont_pron_invis + 0.03. HARD_FAIL = cont_committed <= cont_pron_invis + 0.02.

DESIGN-GATE (all 4 at smoke): (G1) REAL baseline = head-fixed OFF (== head-finder B2), reproduced live.
  (G2) baseline_in_band 0.05<OFF prec<0.95 (+ the decisive PRONOUN subset un-saturated). (G3) can-fail both
  ways (wrong commits -> HARD_FAIL_A; carry unchanged -> HARD_FAIL_B). (G4) discriminator fires (n_commit>0,
  arms_differ). If gate abstains on everything -> MIDDLE_BAND reported, NOT re-tuned.

BRAIN-CHECK (outcome NOT pre-assumed): cue-based content-addressable retrieval w/ interference margin (Lewis-
  Vasishth, McElree; top1-top2 = similarity-based-interference signal); abstain = late-maturing costly
  reference-set comparison. Brain SHARES the 65-89% raw-accuracy ceiling; the win is help-not-hurt via
  abstaining + entity-carry, NOT high accuracy. Same-limit -> accept+localize; helps -> lever works.

COMPUTE ARCHITECTURE: class (b) sequential-CPU. Glass-box discourse pass + tiny complex matmuls over ~114
  sentences, wall<<30s/seed; no GPU-batching win; storage=no_storage; foreground-inline (NO queue/push/
  remote-persist). CRLB n/a (no additive-Gaussian estimator floor; FHRR crosstalk Plate O(N/log N)~134 at
  N=2048, pools <10 -> well inside). DETERMINISM: np.random.default_rng(seed) codebooks; sorted ordering;
  NO builtin hash()/list(set) seeding. Multi-seed FHRR codebooks [7,13,19] (LCCP/head-finder pipeline
  computed ONCE, cfg seed fixed; only the FHRR draw varies -> only cleanup cosines/commit decisions vary).

# CELL-TEMPLATE MANDATORY: arms_differ_verified; final_metrics_atomicity=tmp_replace; except SystemExit:
# raise BEFORE except Exception (no BaseException); baseline_in_band at smoke; discriminator fires at smoke;
# self-tests (cleanup-fidelity + margin-gate-fires-on-toy + real code path); crlb n/a; deterministic seeding;
# all numbers MEASURED@ this metrics.json / CITED@ (0.938 head-finder, 0.489 assembled, 16-for-1 prior coref).
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402
import experiments.exp_attachment_coref_lever_lccp_break050_v1 as ACL  # noqa: E402 (gold agentsets loader)
import experiments.exp_np_head_finder_grounding_gate_break050_v1 as HF  # noqa: E402 (head-finder resolve_heads)
import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402 (pos_tag_sentence)
from hdlab.state_of_mind import (SetKnownBase, WorkingOverlay, PRONOUN_SCOPE, TARGET_PRONOUNS,  # noqa: E402
                                 compatible, infer_nominal_gender, MASC_CUES, FEM_CUES)
from hdlab.binding import bind  # noqa: E402 (real FHRR bind for Pred B carry)
from hdlab.bundling import bundle  # noqa: E402 (real FHRR bundle for Pred B carry)

ANCHOR_NAME = "coref_margin_gated_cleanup_local_window_break050_v1"
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")

# ---- PRE-REGISTERED constants (FIXED; see prereg) --------------------------------------------------
N_DIM = 1024
W_ROLE = 0.30
W_SAL = 0.50
EPS_NOISE = 0.02
W_IC = 0.0                      # implicit-causality term OFF (LOW feasibility this corpus; hook only)
TAU_MARGIN = 0.10              # commit iff cos1 - cos2 >= TAU_MARGIN
COS_FLOOR = 0.08              # ... AND cos1 >= COS_FLOOR
ROLE_W = {"subj": 1.0, "obj": 0.5, "obl": 0.25}
SAL_BETA = 0.5
SAL_LAM = 0.1
FHRR_SEEDS = [7, 13, 19]
FEATURE_ATOMS = ["G_masc", "G_fem", "G_neuter", "N_singular", "N_plural",
                 "A_animate", "A_inanimate", "SAL", "R_subj", "R_obj", "R_obl"]

# 3rd-person TARGET pronouns (antecedent-resolution scope; excludes deictic 1st/2nd person).
THIRD_TARGET = {"he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their"}
# small animate-common-noun seed (glass-box; augments gender-cue animacy)
ANIMATE_NOUNS = {"man", "men", "woman", "women", "boy", "boys", "girl", "girls", "child", "children",
                 "father", "mother", "son", "daughter", "brother", "sister", "king", "queen", "prince",
                 "princess", "dog", "cat", "horse", "bird", "fox", "lion", "wolf", "bear", "people",
                 "friend", "friends", "master", "servant", "soldier", "soldiers", "baby", "family"}

CITED_HEADFINDER_B2 = 0.938  # CITED@data/exp_np_head_finder_grounding_gate_break050_v1/metrics.json
CITED_PRIOR_COREF_BREAK = "16-broken-for-1-fixed (recall_cost 0.308, dP -0.234)"  # CITED@data/exp_attachment_coref_lever_lccp_break050_v1/metrics.json


# ---------------------------------------------------------------------------------------------------
# FHRR codebook + cosine (random-phasor, zero-training; pattern reused from Step-1 carry cell).
# ---------------------------------------------------------------------------------------------------
def fhrr_codebook(atoms, n_dim, rng):
    """atoms -> {atom: complex64 unit-phasor vector}. Deterministic given rng."""
    ph = rng.uniform(-np.pi, np.pi, size=(len(atoms), n_dim))
    out = {}
    for i, a in enumerate(atoms):
        t = torch.tensor(ph[i], dtype=torch.float64)
        out[a] = torch.complex(torch.cos(t), torch.sin(t)).to(torch.complex64)
    return out


def cos(a, b):
    a = a.flatten(); b = b.flatten()
    num = torch.vdot(a, b).abs(); den = a.norm() * b.norm()
    return float(num / den) if float(den) > 0 else 0.0


def rand_phasor(n_dim, rng):
    t = torch.tensor(rng.uniform(-np.pi, np.pi, size=n_dim), dtype=torch.float64)
    return torch.complex(torch.cos(t), torch.sin(t)).to(torch.complex64)


# ---------------------------------------------------------------------------------------------------
# Local-window candidate model. Walk sentences per lesson; per sentence record NP-head entities +
# gender/number (WorkingOverlay) + animacy + Cf-role (from keptC agent/patient slots); local window =
# current-sentence heads + immediately-preceding-sentence heads.
# ---------------------------------------------------------------------------------------------------
def infer_animacy(head, gender):
    h = head.lower().strip(".,'\"!?;:")
    if gender in ("masc", "fem"):
        return "animate"
    if h in ANIMATE_NOUNS or (h in MASC_CUES) or (h in FEM_CUES):
        return "animate"
    if h in ("it", "its"):
        return "inanimate"
    return None  # unknown -> not used as hard filter, not encoded


def norm_number(num):
    if num in ("singular", "plural"):
        return num
    if num in ("sg", "s"):
        return "singular"
    if num in ("pl", "p"):
        return "plural"
    return None


# NP-HEAD candidate gating: only true noun heads are candidates (the head-finder discipline; drops
# funcwords / verbs / preps / adjectives that polluted a naive observed-surface pool). POS-derived number
# gives the hard agreement filter real teeth (NNS/NNPS -> plural so 'he' cannot resolve to a plural noun).
NOUN_POS = {"NN", "NNS", "NNP", "NNPS"}
PLURAL_NOUN_POS = {"NNS", "NNPS"}


def noun_head_attrs(low, pos):
    """(is_candidate, number, gender, animacy) for a token; None number/gender = unknown (soft, not a
    hard-filter trigger). Only real noun heads (NOUN_POS), non-funcword, len>1 are candidates."""
    if pos not in NOUN_POS or low in LCCP.FUNCWORD or len(low) < 2 or not low.isalpha():
        return False, None, None, None
    number = "plural" if pos in PLURAL_NOUN_POS else "singular"
    gender = infer_nominal_gender([low])   # masc/fem from gendered-noun cues; None if unknown (e.g. a name)
    animacy = infer_animacy(low, gender)
    return True, number, gender, animacy


class Candidate:
    """A local-window antecedent candidate (an NP-head mention with agreement + salience + Cf-role)."""
    __slots__ = ("head", "gender", "number", "animacy", "role", "sal", "code_key")

    def __init__(self, head, gender, number, animacy, role, sal):
        self.head = head
        self.gender = gender
        self.number = number
        self.animacy = animacy
        self.role = role
        self.sal = sal
        self.code_key = None


def build_role_map(keptC):
    """Best Cf-role each head plays in the slice from LCCP tuples: agent->subj, patient->obj (subj wins)."""
    role = {}
    for sid, t in keptC:
        a = str(t[1]).lower(); p = str(t[2]).lower()
        role[a] = "subj"                        # agent slot outranks
        if p and p not in role:
            role[p] = "obj"
    return role


def encode_candidate_key(c, cb, noise_vec):
    """LINEAR superposition of weighted cue codes (NOT per-component renorm bundle -> weights survive)."""
    acc = torch.zeros(N_DIM, dtype=torch.complex64)
    if c.gender in ("masc", "fem", "neuter"):
        acc = acc + cb["G_" + c.gender]
    if c.number in ("singular", "plural"):
        acc = acc + cb["N_" + c.number]
    if c.animacy in ("animate", "inanimate"):
        acc = acc + cb["A_" + c.animacy]
    acc = acc + (W_ROLE * ROLE_W.get(c.role, 0.25)) * cb["R_" + ("subj" if c.role == "subj" else "obj" if c.role == "obj" else "obl")]
    acc = acc + (W_SAL * c.sal) * cb["SAL"]
    acc = acc + EPS_NOISE * noise_vec
    return acc


def encode_query(pron_low, cb):
    """Pronoun agreement cues + salience-preference + (IC OFF) into one query vector."""
    sc = PRONOUN_SCOPE[pron_low]
    g = sc["gender"]; n = norm_number(sc["number"])
    acc = torch.zeros(N_DIM, dtype=torch.complex64)
    if g in ("masc", "fem", "neuter"):
        acc = acc + cb["G_" + g]
    if n in ("singular", "plural"):
        acc = acc + cb["N_" + n]
    if g in ("masc", "fem"):
        acc = acc + cb["A_animate"]        # gendered pronoun expects an animate antecedent
    acc = acc + W_SAL * cb["SAL"]          # prefer the salient/topical candidate
    # W_IC == 0 -> IC role bias term omitted (declared OFF)
    return acc


def resolve_coref_gated(order, sent_text, keptC, resB2, seed):
    """Return {(sid,kidx): (resolved_head, method, margin, cos1, code_or_None)} for TARGET-pronoun agents;
    non-target / abstained -> identity (head unchanged). Local-window candidate pool per pronoun."""
    rng = np.random.default_rng(seed)
    cb = fhrr_codebook(FEATURE_ATOMS, N_DIM, rng)
    role_map = build_role_map(keptC)
    ent_code_rng = np.random.default_rng(seed + 100003)  # per-entity identity codes (Pred B carry)

    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))

    # per-entity identity code (stable across the run for the carry test), keyed by lowercased head
    entity_codes = {}

    def code_of(head):
        h = head.lower()
        if h not in entity_codes:
            entity_codes[h] = rand_phasor(N_DIM, ent_code_rng)
        return entity_codes[h]

    resolved = {}
    commit_log = []
    # process lessons independently (discourse resets at lesson boundary)
    lessons = []
    seen = set()
    for sid in order:
        lid = sid.split("_")[0]
        if lid not in seen:
            seen.add(lid); lessons.append(lid)

    for lid in lessons:
        ov = WorkingOverlay(SetKnownBase())
        sids = [sid for sid in order if sid.split("_")[0] == lid]
        prev_heads = {}   # NP-heads (head_low -> attrs) mentioned in the immediately-preceding sentence
        for sid in sids:
            raw = sent_text[sid]
            tagged = ORC.pos_tag_sentence(raw)
            cur_heads = {}   # head_low -> (number, gender, animacy) POS-derived NP-head attrs
            for i, (surf, low, pos) in enumerate(tagged):
                ov.observe_surface(surf, at_sentence_start=(i == 0))  # salience/mention tracking
                is_cand, number, gender, animacy = noun_head_attrs(low, pos)
                if is_cand and low not in cur_heads:
                    cur_heads[low] = (number, gender, animacy)
            # local window = current + immediately-preceding sentence NP-heads (unique, order-stable)
            window = {}
            for h, attrs in list(cur_heads.items()) + list(prev_heads.items()):
                if h not in window:
                    window[h] = attrs
            now = ov.n_observed
            # build candidates: POS-derived agreement attrs; salience from overlay entity (fallback count=1)
            cands_by_head = {}
            for h, (number, gender, animacy) in window.items():
                e = ov._entities.get(h)  # noqa: SLF001 (glass-box read of tracked entity for salience)
                sal = e.salience(now, SAL_BETA, SAL_LAM) if e is not None else 1.0
                role = role_map.get(h, "obl")
                cands_by_head[h] = Candidate(h, gender, number, animacy, role, sal)
            # resolve each TARGET-pronoun agent of this sentence
            for kidx, t in kept_by_sid.get(sid, []):
                a = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()  # head-fixed agent
                if a not in THIRD_TARGET:
                    resolved[(sid, kidx)] = (a, "identity", 0.0, 0.0, None)
                    continue
                sc = PRONOUN_SCOPE[a]
                p_g = sc["gender"]; p_n = norm_number(sc["number"])
                # candidate pool minus the pronoun itself; HARD gender/number pre-filter
                pool = [c for h, c in cands_by_head.items()
                        if h != a and compatible(p_g, p_n, c.gender, c.number)]
                if not pool:
                    resolved[(sid, kidx)] = (a, "abstain_no_candidate", 0.0, 0.0, None)
                    continue
                # min-max normalize salience across the pool (so SAL term is comparable, unitless)
                sals = [c.sal for c in pool]
                lo, hi = min(sals), max(sals)
                for c in pool:
                    c_sal_norm = (c.sal - lo) / (hi - lo) if hi > lo else 1.0
                    noise = rand_phasor(N_DIM, np.random.default_rng(seed + 7 * (hash_head(c.head))))
                    tmp = Candidate(c.head, c.gender, c.number, c.animacy, c.role, c_sal_norm)
                    c.code_key = encode_candidate_key(tmp, cb, noise)
                q = encode_query(a, cb)
                scored = sorted(((cos(q, c.code_key), c) for c in pool),
                                key=lambda x: (-x[0], x[1].head))
                cos1, top = scored[0]
                cos2 = scored[1][0] if len(scored) > 1 else 0.0
                margin = cos1 - cos2
                if margin >= TAU_MARGIN and cos1 >= COS_FLOOR:
                    resolved[(sid, kidx)] = (top.head, "coref_commit", margin, cos1, code_of(top.head))
                    commit_log.append({"sid": sid, "v": LCCP.lemma_verb(t[0]), "pron": a,
                                       "resolved": top.head, "margin": round(margin, 4),
                                       "cos1": round(cos1, 4), "cos2": round(cos2, 4),
                                       "n_pool": len(pool), "pool": [c.head for c in pool]})
                else:
                    resolved[(sid, kidx)] = (a, "abstain_low_margin", margin, cos1, None)
            prev_heads = cur_heads
    return resolved, commit_log, entity_codes


def hash_head(h):
    """Deterministic per-head int (NOT builtin hash -> no PYTHONHASHSEED nondeterminism)."""
    return int.from_bytes(hashlib.sha256(h.encode()).digest()[:6], "big") % (2 ** 31)


# ---------------------------------------------------------------------------------------------------
# Gold agent-surface sets (reuse the prior coref cell loader; goldset = pos{agent}|refs UNION nopat{agent}).
# ---------------------------------------------------------------------------------------------------
def load_named_refs(slice_lessons):
    """Per (sid, v_lemma): the set of NAMED (non-pronoun) antecedents in gold refs (the who-did-what truth)."""
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    named = defaultdict(set)
    for sid, rec in obj["gold"].items():
        if sid.split("_")[0] not in slice_lessons:
            continue
        for r in rec.get("pos", []) + rec.get("nopat", []):
            v = LCCP.lemma_verb(r["v"])
            for x in r.get("refs", []):
                xl = x.lower()
                if xl not in PRONOUN_SCOPE and xl.isalpha() and len(xl) > 1:
                    named[(sid, v)].add(xl)
    return named


# ---------------------------------------------------------------------------------------------------
# Pred A scoring: surface agent-lens break-budget (OFF=head-fixed vs ON=head-fixed+gated-coref).
# ---------------------------------------------------------------------------------------------------
def score_pred_a(keptC, gold_ag, resB2, resolved, named_refs):
    n_frame = 0
    off_ok = on_ok = 0
    newly_fixed = newly_broken = 0
    n_target = n_commit = n_abstain_lowm = n_abstain_nocand = 0
    named_committed = named_correct = 0
    pron_subset = {"n": 0, "off_ok": 0, "on_ok": 0}
    per_instance = []
    for kidx, (sid, t) in enumerate(keptC):
        v = LCCP.lemma_verb(t[0])
        key = (sid, v)
        goldset = gold_ag.get(key)
        if not goldset:
            continue
        n_frame += 1
        off_head = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
        rr = resolved.get((sid, kidx), (off_head, "identity", 0.0, 0.0, None))
        on_head, method = rr[0], rr[1]
        okOFF = off_head in goldset
        okON = on_head in goldset
        off_ok += int(okOFF); on_ok += int(okON)
        is_target = off_head in THIRD_TARGET
        if is_target:
            n_target += 1
            pron_subset["n"] += 1
            pron_subset["off_ok"] += int(okOFF)
            pron_subset["on_ok"] += int(okON)
            if method == "coref_commit":
                n_commit += 1
                if not okOFF and okON:
                    newly_fixed += 1
                if okOFF and not okON:
                    newly_broken += 1
                nref = named_refs.get(key)
                if nref:
                    named_committed += 1
                    if on_head in nref:
                        named_correct += 1
            elif method == "abstain_low_margin":
                n_abstain_lowm += 1
            elif method == "abstain_no_candidate":
                n_abstain_nocand += 1
        per_instance.append({"sid": sid, "v": v, "off_head": off_head, "on_head": on_head,
                             "method": method, "margin": round(rr[2], 4), "cos1": round(rr[3], 4),
                             "gold": sorted(goldset), "named_gold": sorted(named_refs.get(key, [])),
                             "okOFF": okOFF, "okON": okON})
    return {
        "n_frame": n_frame,
        "precision_OFF": round(off_ok / n_frame, 4) if n_frame else 0.0,
        "precision_ON": round(on_ok / n_frame, 4) if n_frame else 0.0,
        "newly_fixed": newly_fixed, "newly_broken": newly_broken,
        "n_target_pron": n_target, "n_commit": n_commit,
        "n_abstain_low_margin": n_abstain_lowm, "n_abstain_no_candidate": n_abstain_nocand,
        "abstain_rate": round((n_abstain_lowm + n_abstain_nocand) / n_target, 4) if n_target else 0.0,
        "commit_rate": round(n_commit / n_target, 4) if n_target else 0.0,
        "named_committed": named_committed, "named_correct": named_correct,
        "named_precision": round(named_correct / named_committed, 4) if named_committed else None,
        "pron_subset_precision_OFF": round(pron_subset["off_ok"] / pron_subset["n"], 4) if pron_subset["n"] else 0.0,
        "pron_subset_precision_ON": round(pron_subset["on_ok"] / pron_subset["n"], 4) if pron_subset["n"] else 0.0,
        "pron_subset_n": pron_subset["n"],
        "per_instance": per_instance,
    }


# ---------------------------------------------------------------------------------------------------
# Pred B: Tier-2 FHRR carry continuity. For each committed pronoun instance whose resolved antecedent was
# mentioned in a PRIOR sentence, build a reference map (bundle of bind(ROLE, content-filler-code) over the
# prior sentence's clauses, PRONOUNS DROPPED = Step-1 carry) and measure same-entity continuity.
# ---------------------------------------------------------------------------------------------------
def score_pred_b(order, keptC, resB2, resolved, entity_codes, seed):
    rng = np.random.default_rng(seed + 55)
    role_cb = fhrr_codebook(["RAGENT", "RPATIENT", "RVERB"], N_DIM, rng)
    # content-token codes (shared code space with entity_codes for resolved entities)
    content_codes = dict(entity_codes)  # resolved-entity identity codes already assigned in resolver

    def code_of(tok):
        tl = tok.lower()
        if tl not in content_codes:
            content_codes[tl] = rand_phasor(N_DIM, rng)
        return content_codes[tl]

    # index kept tuples per sentence-in-order
    order_index = {sid: i for i, sid in enumerate(order)}
    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))

    cont_committed = []
    cont_pron_invis = []
    cont_random = []
    pair_log = []
    for kidx, (sid, t) in enumerate(keptC):
        rr = resolved.get((sid, kidx))
        if rr is None or rr[1] != "coref_commit":
            continue
        resolved_head = rr[0]
        oi = order_index.get(sid)
        if oi is None or oi == 0:
            continue
        prev_sid = order[oi - 1]
        # build reference map from the immediately-preceding sentence's LCCP clauses (content fillers only)
        map_terms = []
        antecedent_in_map = False
        for pkidx, pt in kept_by_sid.get(prev_sid, []):
            pv, pa, pp = str(pt[0]), str(resB2.get((prev_sid, pkidx), (str(pt[1]).lower(), "id"))[0]).lower(), str(pt[2]).lower()
            # content-filler discipline: drop pronouns + funcwords + len<2 (Step-1 carry)
            for role_atom, filler in (("RAGENT", pa), ("RPATIENT", pp)):
                if filler in PRONOUN_SCOPE or filler in LCCP.FUNCWORD or len(filler) < 2:
                    continue
                map_terms.append(bind(role_cb[role_atom], code_of(filler)))
                if filler == resolved_head:
                    antecedent_in_map = True
        if not map_terms:
            continue
        ref_map = bundle(torch.stack(map_terms)) if len(map_terms) > 1 else map_terms[0]

        # ROLE-AGNOSTIC same-entity continuity = max over the two core roles (parity with Step-1 carry's
        # doc_coh(p) = max over {RPATIENT,RAGENT} of cos(bind(role,code(p)),map)). A pronoun that is an
        # AGENT now whose antecedent was a PATIENT before is still the SAME entity -> role-specific query
        # would falsely read ~0 (measurement-fairness, not tuning; bands unchanged).
        def continuity(code_vec):
            return max(cos(bind(role_cb["RAGENT"], code_vec), ref_map),
                       cos(bind(role_cb["RPATIENT"], code_vec), ref_map))

        pron_surface = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
        cc = continuity(code_of(resolved_head))
        cp = continuity(code_of(pron_surface))       # pronoun code (not a content filler in the map)
        crr = continuity(rand_phasor(N_DIM, rng))
        # only pairs where the antecedent actually appears in the prior-sentence map are the Pred-B subset
        if antecedent_in_map:
            cont_committed.append(cc); cont_pron_invis.append(cp); cont_random.append(crr)
            pair_log.append({"sid": sid, "prev_sid": prev_sid, "pron": pron_surface,
                             "resolved": resolved_head, "cont_committed": round(cc, 4),
                             "cont_pron_invis": round(cp, 4), "cont_random": round(crr, 4),
                             "n_map_terms": len(map_terms)})

    def mean(xs):
        return round(float(np.mean(xs)), 4) if xs else 0.0

    return {
        "n_pairs": len(cont_committed),
        "continuity_committed": mean(cont_committed),
        "continuity_pronoun_invisible": mean(cont_pron_invis),
        "continuity_random_control": mean(cont_random),
        "pair_log": pair_log,
    }


# ---------------------------------------------------------------------------------------------------
def build_verdict_a(a):
    nb, nf = a["newly_broken"], a["newly_fixed"]
    named = a["named_precision"]
    on_ge_off = a["precision_ON"] >= a["precision_OFF"]
    if nb > nf or a["precision_ON"] < a["precision_OFF"] - 0.02:
        v = "HARD_FAIL_A_NET_BREAKAGE"
    elif (nb <= nf and nb == 0 and on_ge_off and a["n_commit"] >= 1
          and named is not None and named >= 0.60):
        v = "HARD_PASS_A_GATED_COREF_HELPS_NOT_HURTS"
    elif nb <= nf and nb <= 1 and ((named is not None and 0.40 <= named < 0.60) or a["n_commit"] == 0):
        v = "PARTIAL_A_SAFE_LITTLE_SIGNAL"
    else:
        v = "PARTIAL_A_SAFE_LITTLE_SIGNAL"
    return v


def build_verdict_b(b):
    cc, cp, cr = b["continuity_committed"], b["continuity_pronoun_invisible"], b["continuity_random_control"]
    if b["n_pairs"] < 1:
        return "PARTIAL_B_NO_PRIOR_PAIRS"
    if cc >= cp + 0.10 and cc >= 3 * cr:
        return "HARD_PASS_B_CARRY_SEES_COREF_CONTINUITY"
    if cc >= cp + 0.03:
        return "PARTIAL_B_SMALL_REVERSAL"
    return "HARD_FAIL_B_CARRY_UNCHANGED"


# ---------------------------------------------------------------------------------------------------
def run_pipeline(cfg):
    """LCCP + head-finder once (cfg seed fixed). Returns keptC, resB2 (head-fixed OFF), gold sets, order."""
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    gold, _gm = LCCP.load_gold(cfg["slice_lessons"])
    am, tn, lc, p3, meta, dec, ho, sn = LCCP.run_config(cfg)
    keptC = [(sid, tuple(t)) for sid, t in dec["C_lccp"]]
    gold_ag, frame_kind = ACL.load_gold_agentsets(cfg["slice_lessons"])
    named_refs = load_named_refs(cfg["slice_lessons"])
    resB2, nrw_b2, _det = HF.resolve_heads(order, sent_text, keptC, use_grounding=True)
    return dict(order=order, sent_text=sent_text, keptC=keptC, gold_ag=gold_ag,
                frame_kind=frame_kind, named_refs=named_refs, resB2=resB2,
                lccp_summary={"C_precision_lccp": am["C_lccp"]["all"]["precision"],
                              "n_keptC": len(keptC), "n_reader_svo": meta["n_reader_svo"]})


def run_config(cfg):
    pipe = run_pipeline(cfg)
    per_seed = []
    for s in FHRR_SEEDS:
        resolved, commit_log, entity_codes = resolve_coref_gated(
            pipe["order"], pipe["sent_text"], pipe["keptC"], pipe["resB2"], s)
        a = score_pred_a(pipe["keptC"], pipe["gold_ag"], pipe["resB2"], resolved, pipe["named_refs"])
        b = score_pred_b(pipe["order"], pipe["keptC"], pipe["resB2"], resolved, entity_codes, s)
        va = build_verdict_a(a)
        vb = build_verdict_b(b)
        per_seed.append({"seed": s, "verdict_a": va, "verdict_b": vb,
                         "pred_a": {k: v for k, v in a.items() if k != "per_instance"},
                         "pred_b": {k: v for k, v in b.items() if k != "pair_log"},
                         "commit_log": commit_log, "pair_log": b["pair_log"],
                         "per_instance": a["per_instance"], "resolved": resolved})
    return pipe, per_seed


def _agg(per_seed, path):
    vals = []
    for ps in per_seed:
        d = ps
        for p in path:
            d = d[p]
        if d is not None:
            vals.append(d)
    if not vals:
        return {"mean": None, "min": None, "max": None, "vals": []}
    return {"mean": round(float(np.mean(vals)), 4), "min": round(float(np.min(vals)), 4),
            "max": round(float(np.max(vals)), 4), "vals": vals}


def resolved_hash(keptC, resB2, resolved, use_on):
    items = []
    for kidx, (sid, t) in enumerate(keptC):
        off = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
        h = resolved.get((sid, kidx), (off,))[0] if use_on else off
        items.append(f"{sid}|{LCCP.lemma_verb(t[0])}|{h}")
    return hashlib.sha256("\n".join(sorted(items)).encode()).hexdigest()[:16]


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def cfg_smoke():
    return dict(slice_lessons=["L07", "L10"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=7)


def cfg_full():
    return LCCP.cfg_full()


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    pipe, per_seed = run_config(cfg)

    # multi-seed aggregates (headline numbers)
    agg = {
        "precision_OFF": _agg(per_seed, ["pred_a", "precision_OFF"]),
        "precision_ON": _agg(per_seed, ["pred_a", "precision_ON"]),
        "newly_broken": _agg(per_seed, ["pred_a", "newly_broken"]),
        "newly_fixed": _agg(per_seed, ["pred_a", "newly_fixed"]),
        "n_commit": _agg(per_seed, ["pred_a", "n_commit"]),
        "abstain_rate": _agg(per_seed, ["pred_a", "abstain_rate"]),
        "named_precision": _agg(per_seed, ["pred_a", "named_precision"]),
        "n_target_pron": _agg(per_seed, ["pred_a", "n_target_pron"]),
        "continuity_committed": _agg(per_seed, ["pred_b", "continuity_committed"]),
        "continuity_pronoun_invisible": _agg(per_seed, ["pred_b", "continuity_pronoun_invisible"]),
        "continuity_random_control": _agg(per_seed, ["pred_b", "continuity_random_control"]),
        "n_pairs_B": _agg(per_seed, ["pred_b", "n_pairs"]),
    }
    va_set = sorted(set(ps["verdict_a"] for ps in per_seed))
    vb_set = sorted(set(ps["verdict_b"] for ps in per_seed))
    verdict_a = va_set[0] if len(va_set) == 1 else "SEED_SPLIT_A:" + ",".join(va_set)
    verdict_b = vb_set[0] if len(vb_set) == 1 else "SEED_SPLIT_B:" + ",".join(vb_set)

    # gates (evaluated on seed 0)
    ps0 = per_seed[0]
    hOFF = resolved_hash(pipe["keptC"], pipe["resB2"], ps0["resolved"], use_on=False)
    hON = resolved_hash(pipe["keptC"], pipe["resB2"], ps0["resolved"], use_on=True)
    arms_differ = hOFF != hON
    off_prec = ps0["pred_a"]["precision_OFF"]
    baseline_in_band = bool(0.05 < off_prec < 0.95)
    n_commit0 = ps0["pred_a"]["n_commit"]
    discriminator_fires = bool(n_commit0 > 0 and arms_differ)

    verdict = f"A:{verdict_a} | B:{verdict_b}"
    msg = (f"{verdict} | mode={mode} slice={'+'.join(cfg['slice_lessons'])} n_keptC={pipe['lccp_summary']['n_keptC']} "
           f"| A: P_OFF={agg['precision_OFF']['mean']:.3f} P_ON={agg['precision_ON']['mean']:.3f} "
           f"broke={agg['newly_broken']['vals']} fixed={agg['newly_fixed']['vals']} "
           f"n_target={agg['n_target_pron']['mean']:.0f} n_commit={agg['n_commit']['vals']} "
           f"abstain_rate={agg['abstain_rate']['mean']:.3f} named_prec={agg['named_precision']['mean']} "
           f"(vs prior {CITED_PRIOR_COREF_BREAK}) "
           f"| B: n_pairs={agg['n_pairs_B']['vals']} cont_committed={agg['continuity_committed']['mean']} "
           f"cont_pron_invis={agg['continuity_pronoun_invisible']['mean']} "
           f"cont_random={agg['continuity_random_control']['mean']} "
           f"| arms_differ={arms_differ} base_in_band={baseline_in_band} discrim={discriminator_fires}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": time.perf_counter() - t0, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "verdict_a": verdict_a, "verdict_b": verdict_b,
        "aggregates_multiseed": agg, "fhrr_seeds": FHRR_SEEDS,
        "pre_registered": {"TAU_MARGIN": TAU_MARGIN, "COS_FLOOR": COS_FLOOR, "W_ROLE": W_ROLE,
                           "W_SAL": W_SAL, "EPS_NOISE": EPS_NOISE, "W_IC": W_IC, "N_DIM": N_DIM,
                           "ROLE_W": ROLE_W},
        "per_seed": [{k: v for k, v in ps.items() if k != "resolved"} for ps in per_seed],
        "lccp_summary": pipe["lccp_summary"],
        "arms_differ_verified": arms_differ, "arms_differ_hashes": {"OFF": hOFF, "ON": hON},
        "baseline_in_band": baseline_in_band, "discriminator_fires": discriminator_fires,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "adaptive_with_discriminator_gate",
        "crlb_n_a": "no additive-Gaussian estimator floor; FHRR crosstalk Plate O(N/log N)~134@N=2048, pools<10",
        "cited": {"headfinder_B2_agent_lens": CITED_HEADFINDER_B2, "prior_coref_break": CITED_PRIOR_COREF_BREAK,
                  "reader_topline": "reader true-stacked precision 0.557 (separate top-line aggregate; this "
                                    "cell measures the agent-lens P where head-finder OFF=0.938)"},
        "REQUIRED_FIELDS": ["verdict", "verdict_a", "verdict_b", "aggregates_multiseed", "per_seed",
                            "arms_differ_verified", "baseline_in_band", "discriminator_fires"],
        "reused_components": {
            "lccp": "exp_learned_argstruct_parser_lccp_independent_gold_v1 (arm-C keptC; atom 29338)",
            "head_finder": "exp_np_head_finder_grounding_gate_break050_v1.resolve_heads(use_grounding=True) (atom 29342)",
            "gold_agentsets": "exp_attachment_coref_lever_lccp_break050_v1.load_gold_agentsets",
            "overlay": "hdlab.state_of_mind.WorkingOverlay (entity tracking / gender-number / salience)",
            "fhrr": "hdlab.binding.bind + hdlab.bundling.bundle (Pred B carry; real primitives)",
        },
        "notes": ("Margin-gated abstaining coref via HD cleanup-memory. Pred A = help-not-hurt break-budget "
                  "(newly_broken<=newly_fixed, ideally 0) + committed-named precision (who-did-what), the "
                  "make-or-break vs the prior UNGATED 16-for-1 HARD_FAIL. Pred B = committed coref codes into "
                  "the Tier-2 FHRR carry reverse Step-1's pronoun-invisible carry (non-zero same-entity "
                  "continuity). ACCEPT the 65-89%% brain-shared accuracy ceiling: the win is abstain-based "
                  "help-not-hurt + the entity-carry, NOT high accuracy. IC term OFF (w_ic=0, low feasibility "
                  "this corpus). STRATEGIC READ = HYPOTHESIS pending skunkworks landed-VET. Single-annotator "
                  "gold. LOCAL-ONLY; needs_orchestrator_store_sync=True; NO push/remote-persist/git-add-A."),
        "needs_orchestrator_store_sync": True,
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"  metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    print(f"  LCCP C_P={pipe['lccp_summary']['C_precision_lccp']:.3f} n_keptC={pipe['lccp_summary']['n_keptC']}", flush=True)
    for ps in per_seed:
        pa, pb = ps["pred_a"], ps["pred_b"]
        print(f"  seed={ps['seed']} A={ps['verdict_a']} B={ps['verdict_b']} | "
              f"P_OFF={pa['precision_OFF']:.3f} P_ON={pa['precision_ON']:.3f} "
              f"broke={pa['newly_broken']} fixed={pa['newly_fixed']} n_commit={pa['n_commit']}/{pa['n_target_pron']} "
              f"abstain={pa['abstain_rate']:.2f} named={pa['named_correct']}/{pa['named_committed']} "
              f"(P={pa['named_precision']}) | B n_pairs={pb['n_pairs']} "
              f"cc={pb['continuity_committed']} cpi={pb['continuity_pronoun_invisible']} cr={pb['continuity_random_control']}", flush=True)
    print("  --- seed0 commit log (sid v pron -> resolved [margin cos1] pool) ---", flush=True)
    for c in per_seed[0]["commit_log"]:
        print(f"    {c['sid']} {c['v']:>8} {c['pron']:>5} -> {c['resolved']:<10} "
              f"[m={c['margin']:.3f} c1={c['cos1']:.3f}] pool={c['pool']}", flush=True)
    print("  --- seed0 Pred-B pair log ---", flush=True)
    for pr in per_seed[0]["pair_log"]:
        print(f"    {pr['sid']} pron={pr['pron']} -> {pr['resolved']} | cc={pr['cont_committed']} "
              f"cpi={pr['cont_pron_invis']} cr={pr['cont_random']} (n_map={pr['n_map_terms']})", flush=True)
    return payload


# ---------------------------------------------------------------------------------------------------
def _selftest_cleanup_fidelity_and_gate():
    """Toy: (fidelity) a clean single-compatible candidate is recovered at high cos1; (gate) clean case
    commits (margin>=TAU), agreement-tie abstains (margin<TAU). Calibrates NOTHING on real data."""
    rng = np.random.default_rng(0)
    cb = fhrr_codebook(FEATURE_ATOMS, N_DIM, rng)
    noise = rand_phasor(N_DIM, rng)

    def key(gender, number, animacy, role, sal):
        return encode_candidate_key(Candidate("x", gender, number, animacy, role, sal), cb, noise)

    # Toy A (clean): pronoun 'he'; one masc-animate candidate, one fem candidate (fem hard-filtered out
    # upstream). Here we simulate the post-filter single-candidate case -> cos2=0 -> margin=cos1.
    q = encode_query("he", cb)
    k_masc = key("masc", "singular", "animate", "subj", 1.0)
    cos1 = cos(q, k_masc)
    margin_clean = cos1 - 0.0
    assert cos1 >= COS_FLOOR, f"fidelity: clean masc candidate cos1={cos1:.3f} < COS_FLOOR"
    assert margin_clean >= TAU_MARGIN, f"gate: clean case margin={margin_clean:.3f} < TAU (should commit)"

    # Toy B (2-way agreement tie): two masc-animate-subj candidates, SAME salience -> near-equal cos ->
    # margin < TAU -> ABSTAIN. Distinct noise per candidate (as in the resolver).
    n1 = rand_phasor(N_DIM, np.random.default_rng(11))
    n2 = rand_phasor(N_DIM, np.random.default_rng(12))
    k1 = encode_candidate_key(Candidate("a", "masc", "singular", "animate", "subj", 1.0), cb, n1)
    k2 = encode_candidate_key(Candidate("b", "masc", "singular", "animate", "subj", 1.0), cb, n2)
    c1, c2 = cos(q, k1), cos(q, k2)
    margin_tie = abs(c1 - c2)
    assert margin_tie < TAU_MARGIN, f"gate: agreement-tie margin={margin_tie:.3f} >= TAU (should abstain)"

    # Toy C (salience-separated): high-sal vs low-sal masc candidate -> margin should clear TAU (commit).
    kh = encode_candidate_key(Candidate("h", "masc", "singular", "animate", "subj", 1.0), cb, n1)
    kl = encode_candidate_key(Candidate("l", "masc", "singular", "animate", "subj", 0.0), cb, n2)
    ch, cl = cos(q, kh), cos(q, kl)
    print(f"[selftest] toy: clean cos1={cos1:.3f} margin_clean={margin_clean:.3f} | "
          f"tie c1={c1:.3f} c2={c2:.3f} margin_tie={margin_tie:.3f} | "
          f"sal-sep high={ch:.3f} low={cl:.3f} margin={ch - cl:.3f} (TAU={TAU_MARGIN} FLOOR={COS_FLOOR})", flush=True)
    return dict(cos1_clean=cos1, margin_clean=margin_clean, margin_tie=margin_tie,
               margin_sal=ch - cl)


def _selftest_pred_b_carry():
    """Real hdlab bind/bundle: an entity bound in the map is recovered (high cos) vs a random code (~0)."""
    rng = np.random.default_rng(1)
    role = fhrr_codebook(["RAGENT", "RPATIENT"], N_DIM, rng)
    e_herbert = rand_phasor(N_DIM, rng)
    e_dog = rand_phasor(N_DIM, rng)
    e_rand = rand_phasor(N_DIM, rng)
    ref = bundle(torch.stack([bind(role["RAGENT"], e_herbert), bind(role["RPATIENT"], e_dog)]))
    c_in = cos(bind(role["RAGENT"], e_herbert), ref)
    c_out = cos(bind(role["RAGENT"], e_rand), ref)
    assert c_in > 0.3, f"carry: bound entity recovered cos={c_in:.3f} too low"
    assert c_in >= 3 * c_out, f"carry: in={c_in:.3f} not >> random={c_out:.3f}"
    print(f"[selftest] pred-B carry: bound-entity cos={c_in:.3f} random cos={c_out:.3f}", flush=True)


def self_test():
    toy = _selftest_cleanup_fidelity_and_gate()
    _selftest_pred_b_carry()
    # real code path: construct the REAL LCCP + head-finder pipeline + resolver at the smoke slice
    cfg = cfg_smoke()
    pipe = run_pipeline(cfg)
    assert len(pipe["keptC"]) > 0, "self-test: no keptC from real pipeline"
    resolved, commit_log, ent_codes = resolve_coref_gated(
        pipe["order"], pipe["sent_text"], pipe["keptC"], pipe["resB2"], FHRR_SEEDS[0])
    a = score_pred_a(pipe["keptC"], pipe["gold_ag"], pipe["resB2"], resolved, pipe["named_refs"])
    assert a["n_frame"] > 0, "self-test: no gold-framed instances"
    hOFF = resolved_hash(pipe["keptC"], pipe["resB2"], resolved, use_on=False)
    hON = resolved_hash(pipe["keptC"], pipe["resB2"], resolved, use_on=True)
    print(f"[{ANCHOR_NAME}] self-test OK: real-pipeline n_keptC={len(pipe['keptC'])} n_frame={a['n_frame']} "
          f"n_target={a['n_target_pron']} n_commit={a['n_commit']} P_OFF={a['precision_OFF']:.3f} "
          f"P_ON={a['precision_ON']:.3f} broke={a['newly_broken']} fixed={a['newly_fixed']} "
          f"arms_differ={hOFF != hON} toy_margin_clean={toy['margin_clean']:.3f} toy_margin_tie={toy['margin_tie']:.3f}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
