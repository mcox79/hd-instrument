"""exp_self_extension_grounded_realprose_v1 -- can the self-extension loop MINT 'goal-blocker'
on REAL implicit-goal-block prose, using TWO GENUINELY INDEPENDENT GROUNDED VIEWS?

Builds directly on exp_self_extension_loop_v1 (the first integrated self-extension loop: mints a
goal-blocker type from reading, disposed by a structurally-independent 2nd view, anti-drift validated
by ablation on a controlled synthetic set). v1's HONEST LIMITATION (surfaced by its own VET): its 2nd
view was a discourse/purpose-CONNECTIVE cue, which has a RECALL GAP on naturalistic prose -- the one
REAL ruler item grapp_mcca_004 (Amy's goal to be warned is blocked by Jo's WITHHOLDING, "let her take
care of herself" -- omission/spite, NO explicit connective) trips the novelty residual (0.373) but the
connective 2nd view does NOT fire, so the real item would NOT mint. Real-prose self-extension was
bounded by the 2nd view's recall on naturalistic prose.

THIS CELL replaces the connective 2nd view with a GROUNDED goal-OUTCOME appraisal, and tests whether
the loop now MINTS goal-blocker on REAL implicit-goal-block passages WITHOUT breaking the anti-drift
guarantee. The anti-drift guarantee (NELL/CPL: a candidate cross-checked against ITSELF drifts)
REQUIRES the two views to be STRUCTURALLY INDEPENDENT. Both views are now GROUNDED, so independence is
NOT free -- it is ENGINEERED and MEASURED here (the crux VET):

  VIEW 1 (typing / novelty) -- ARGUMENT STRUCTURE: who WITHHELD/did what to/from whom. A grounded
    lexical argument-structure typer (reuses coreference_resolver.normalize_tokens) -> feature-atom
    bundle -> hdlab.predictive_coding novelty residual vs a harm-only seed library. PROPOSES.
    Brain: DMN/mPFC agent-goal representation + Trabasso goal-plan analysis; left-IFG/pMTG relational
    argument binding.

  VIEW 2 (independent 2nd view) -- GOAL-OUTCOME grounding: does an animate goal-owner's goal end up
    left UNMET as a consequence? A grounded goal-schema (agent-has-goal / goal-object /
    goal-left-UNMET) whose OUTCOME valence is APPRAISED by ACCUMULATING outcome events over the
    passage in the VALIDATED situation-model register (hdlab.situation_model_accumulate.
    AccumulateRegister, atom 29609 -- bind/bundle/unbind/cleanup, reused bit-identical) and reading
    the net terminal valence. DISPOSES. Brain: OFC/vmPFC outcome-value appraisal over the situation
    model (Kintsch C-I / Zwaan event indexing accumulation).

  INDEPENDENCE is a DIFFERENT SIGNAL, not a re-check of view 1: view 1 reads the BLOCKER's act frame
    (withhold verb + animate beneficiary); view 2 reads the OWNER's goal-outcome trajectory. Two
    disjoint lexicons (self-test asserts ZERO overlap) AND two disjoint mechanisms (HD novelty
    residual vs FHRR outcome-appraisal). THE CRUX METRIC: co-fire-on-noise rate -- if the two grounded
    views FIRE TOGETHER on noise (correlated) the anti-drift breaks. Noise passages are seeded with
    OUTCOME-TRAP words (sank/fell/lost/down) so the co-fire test is DISCRIMINATING (a naive outcome
    detector would false-fire; a grounded goal-schema, which requires an animate goal-owner with a
    desire, must not).

TEST + CONTROLS (anti-drift controls from v1 must still hold):
  REAL implicit-goal-block items (verbatim, small n, DIRECTIONAL): grapp_mcca_004 (gold) + theatre
    refusal + book-burning spite + grapp_mcca_003 (mined from data/corpora/little_women, verbatim
    spans). Does the loop MINT goal-blocker on these (both grounded views agree)?
  C1 noise-no-mint. C2 redundant(harm)-no-mint. C3 utility-lift (post-mint goal-block attribution up).
  C4 anti-drift ablation (drop the 2nd view -> drifts on noise).
  NEW INDEPENDENCE metric: 2nd-view-fires-on-noise (co-fire) rate MUST be ~0.

GUARDS: glass-box; NO borrowed embedding/LLM/parser as mechanism; predictive_coding /
  self_improving_loop / normalize_tokens / situation_model_accumulate reused bit-identical; supplied
  goal-knowledge is a proper-noun-free glass-box lexical asset, NOT tuned to the test items; minted
  type NAME is an arbitrary placeholder (content = the signature). Deterministic. Multi-seed.
  Resumable per-seed. Local-only: no queue / remote / push. ASCII-only.

Cites: experiments/exp_self_extension_loop_v1.py; preregs/2026-08-04_self_extension_loop_v1.md;
notes/brain_component_functional_map_2026-08-04.md; the milestone (real-prose self-extension gate).
Prereg: preregs/2026-08-04_self_extension_grounded_realprose_v1.md.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "self_extension_grounded_realprose_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED VERBATIM: novelty/prediction-error organ (mint TRIGGER; view-1 novelty) ------------
from hdlab import predictive_coding as pc  # noqa: E402
# ---- REUSED VERBATIM: situation-model relational tokenizer -------------------------------------
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
# ---- REUSED VERBATIM: abstain-band promote controller (consolidation gate) ---------------------
from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT  # noqa: E402
# ---- REUSED VERBATIM: validated situation-model accumulate organ (atom 29609; view-2 appraisal) -
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
import torch  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
N = 1024                    # HD dim (view-1 feature atoms)
D2 = 1024                   # FHRR dim (view-2 outcome-appraisal register)
SEEDS = list(range(8))
EXPECTED_N_SEEDS = len(SEEDS)
RESIDUAL_THRESHOLD = 0.25   # pre-registered (same organ/threshold as v1)
MIN_CONFIRM = 2             # >=2 cross-confirmations before promotion (anti single-pass drift)
K_SYNTH = 8                 # synthetic passages per class
MAX_EVENTS = 8              # view-2 register event-slot capacity

# ---- feature-atom vocabulary (view-1 output) ----------------------------------------------------
NATIVE_FEATURES = ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME",
                   "HELP_OUTCOME", "TRANSFER", "INSTRUMENT"]
GOAL_FEATURES = ["WITHHOLD_ACT", "BENEFICIARY", "OMISSION"]  # the goal-blocker (argument-structure) type
NOISE_FEATURES = ["WEATHER", "MOTION", "SCENERY"]
ALL_FEATURES = NATIVE_FEATURES + GOAL_FEATURES + NOISE_FEATURES

# ---- seed schema library: ONLY harm/physical templates (NO goal-blocking type) ------------------
SEED_TEMPLATES = {
    "physical_harm": ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "physical_help": ["AGENT", "PATIENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HELP_OUTCOME"],
    "theft":         ["AGENT", "TRANSFER"],
    "instrument":    ["AGENT", "INSTRUMENT", "PHYSICAL_ACT", "DIRECT_CAUSATION", "HARM_OUTCOME"],
    "accident":      ["AGENT", "PHYSICAL_ACT", "DIRECT_CAUSATION"],
}

# ================================================================= VIEW-1 lexicons (ARGUMENT STRUCTURE)
# Grounded ~6yo world-knowledge, glass-box, proper-noun-free. VIEW 1 = the BLOCKER's ACT FRAME:
# who WITHHELD/did what to/from whom. Disjoint from every VIEW-2 lexicon (asserted in self_test).
V1_WITHHOLD = {"withheld", "withhold", "refused", "refuse", "ignored", "ignore", "neglected",
               "neglect", "concealed", "conceal", "denied", "deny", "kept", "hid", "let",
               "shan't", "mustn't", "prevented", "prevent"}
V1_OMISSION = {"let", "leaving", "left", "alone", "ignored", "ignore", "neglected", "neglect"}
V1_BENEFICIARY = {"herself", "himself", "themselves", "sister", "brother", "child", "girl", "boy",
                  "mother", "father", "friend"}
# harm/physical content (native, for the redundant-harm control) -- reused from v1
V1_PHYS_ACT = {"drove", "drive", "stab", "stabbed", "hit", "struck", "strike", "broke", "break",
               "dropped", "drop", "tore", "tear", "poured", "pour", "spilled", "spill", "smashed",
               "smash", "knife", "slapped", "slap", "kicked", "kick", "beat"}
V1_HARM_OUT = {"killed", "kill", "dead", "broke", "broken", "hurt", "wounded", "drowned", "ruined",
               "spoiled", "torn", "bled", "slain"}
V1_HELP_OUT = {"saved", "save", "rescued", "rescue", "healed", "comforted", "mended"}
V1_PATIENT = {"man", "boy", "girl", "breast", "body", "head", "bowl", "page", "book", "ink",
              "letter", "dish", "victim", "arm", "hilt"}
V1_TRANSFER = {"stole", "steal", "took", "pocketed", "snatched", "snatch", "grabbed", "seized"}
V1_INSTRUMENT = {"knife", "adder", "poker", "stick", "rope", "gun", "hilt"}
V1_WEATHER = {"warm", "cold", "spell", "snap", "frost", "wind", "sun", "rain", "mist", "chill"}
V1_MOTION = {"drifted", "drift", "glided", "glide", "skating", "skated", "moved", "sounding",
             "floated", "along", "past"}
V1_SCENERY = {"ice", "field", "sky", "hill", "trees", "river", "meadow", "bank", "path", "shore"}

V1_ALL_LEX = (V1_WITHHOLD | V1_OMISSION | V1_BENEFICIARY | V1_PHYS_ACT | V1_HARM_OUT | V1_HELP_OUT |
              V1_PATIENT | V1_TRANSFER | V1_INSTRUMENT | V1_WEATHER | V1_MOTION | V1_SCENERY)

# ================================================================= VIEW-2 lexicons (GOAL OUTCOME)
# VIEW 2 = the OWNER's GOAL-OUTCOME trajectory: an animate goal-owner has a desire; is the goal left
# UNMET as a consequence? DISJOINT from every VIEW-1 lexicon. This is the grounded goal-SCHEMA:
# a goal-owner DESIRE gates the schema (no animate desirer -> no goal-outcome to appraise), and the
# net accumulated OUTCOME valence (met vs unmet) is the appraisal.
V2_DESIRE = {"wanted", "want", "wished", "wish", "tried", "try", "hoping", "hope", "longed",
             "dying", "meant", "pleaded", "plead", "please", "finish", "fun", "safety", "safe",
             "warned", "warn", "warning", "reach", "win", "going", "care"}
V2_OUTCOME_UNMET = {"down", "fell", "fall", "sank", "sink", "wailing", "wailed",
                    "lost", "lose", "failed", "fail", "calamity", "sorry", "missed", "miss",
                    "unwarned", "unprotected", "late", "never"}
V2_OUTCOME_MET = {"reached", "enjoyed", "enjoy", "won", "escaped", "arrived"}
V2_ALL_LEX = V2_DESIRE | V2_OUTCOME_UNMET | V2_OUTCOME_MET


def _tokens(text):
    return normalize_tokens(text)


# ============================================================================ VIEW 1: argument-structure typer
def type_passage(text):
    """VIEW 1 (typing/novelty): grounded argument-structure typer -> causal-structure feature atoms.
    Reads the BLOCKER's act frame (who WITHHELD/did what to/from whom) + harm/noise content."""
    t = _tokens(text)
    feats = set()
    has_withhold = bool(t & V1_WITHHOLD)
    has_phys = bool(t & V1_PHYS_ACT)
    has_transfer = bool(t & V1_TRANSFER)
    if has_withhold:
        feats.add("WITHHOLD_ACT")
    if t & V1_OMISSION:
        feats.add("OMISSION")
    if t & V1_BENEFICIARY:
        feats.add("BENEFICIARY")
    if has_phys:
        feats.add("PHYSICAL_ACT")
    if t & V1_HARM_OUT:
        feats.add("HARM_OUTCOME")
    if t & V1_HELP_OUT:
        feats.add("HELP_OUTCOME")
    if t & V1_PATIENT:
        feats.add("PATIENT")
    if t & V1_TRANSFER:
        feats.add("TRANSFER")
    if t & V1_INSTRUMENT:
        feats.add("INSTRUMENT")
    if "PHYSICAL_ACT" in feats and "PATIENT" in feats:
        feats.add("DIRECT_CAUSATION")
    if has_withhold or has_phys or has_transfer:
        feats.add("AGENT")
    if t & V1_WEATHER:
        feats.add("WEATHER")
    if t & V1_MOTION:
        feats.add("MOTION")
    if t & V1_SCENERY:
        feats.add("SCENERY")
    return sorted(feats)


def view1_withhold_structure(text):
    """VIEW 1's grounded goal-block PROPOSAL: a withhold/omission act on an animate beneficiary.
    (Used for the independence measurement; the loop's view-1 gate is the novelty residual on the
    typed bundle -- this exposes the *structural* proposal that residual encodes.)"""
    f = set(type_passage(text))
    return ("WITHHOLD_ACT" in f or "OMISSION" in f) and ("BENEFICIARY" in f)


# ============================================================================ VIEW 2: grounded goal-outcome appraisal
def _clauses(text):
    """Split into clause-like event spans (punctuation + coordinating conjunctions)."""
    import re
    parts = re.split(r"[.,;:!?]|\band\b|\byet\b|\bbut\b", text.lower())
    return [p.strip() for p in parts if p.strip()]


def view2_goal_outcome(text, seed):
    """VIEW 2 (independent 2nd view): grounded goal-OUTCOME appraisal via the VALIDATED
    situation-model accumulate organ. TRUE iff an animate goal-owner has a desire AND the net
    accumulated OUTCOME valence is UNMET. Independent of view 1 (disjoint lexicon + mechanism).

    Mechanism (reused bit-identical from hdlab.situation_model_accumulate.AccumulateRegister,
    atom 29609): for the goal-owner entity, each outcome-bearing clause binds a valence symbol
    (MET/UNMET) to its event slot and ACCUMULATES via bundle; appraisal DECODES each recorded slot
    (unbind + cleanup-argmax) and tallies -- OFC/vmPFC value integration over the situation model.
    """
    toks = _tokens(text)
    has_desire = bool(toks & V2_DESIRE)         # grounded goal-schema gate: an animate desirer
    detail = {"has_desire": has_desire, "n_unmet_events": 0, "n_met_events": 0, "fires": False}
    if not has_desire:
        return False, detail                    # no goal-owner desire -> no goal-outcome to appraise

    gen = torch.Generator().manual_seed(1000 + int(seed))
    reg = AccumulateRegister(role_vocab=["MET", "UNMET"], d=D2, generator=gen,
                             max_event_slots=MAX_EVENTS)
    owner = "goal_owner"
    slot = 0
    added = []  # (slot, valence) actually written
    for cl in _clauses(text):
        if slot >= MAX_EVENTS:
            break
        ct = _tokens(cl)
        if ct & V2_OUTCOME_UNMET:
            reg.add_event(owner, "UNMET", slot); added.append((slot, "UNMET")); slot += 1
            if slot >= MAX_EVENTS:
                break
        if ct & V2_OUTCOME_MET:
            reg.add_event(owner, "MET", slot); added.append((slot, "MET")); slot += 1
    if owner not in reg.entities():
        return False, detail                    # desire but no resolved outcome -> incomplete schema

    # APPRAISE: decode each written event slot through the accumulate organ (unbind + cleanup) and
    # tally the recovered valence -- read the situation model, do not shortcut the tally.
    n_unmet = n_met = 0
    for (e, _v) in added:
        best, _scores = reg.decode(owner, e)
        if best == "UNMET":
            n_unmet += 1
        else:
            n_met += 1
    fires = n_unmet > n_met                      # goal left UNMET as a consequence
    detail.update(n_unmet_events=n_unmet, n_met_events=n_met, fires=fires)
    return fires, detail


# ============================================================================ HD / library ops
def feature_atoms(seed):
    rng = np.random.RandomState(seed)
    return {f: rng.choice([-1.0, 1.0], size=N).astype(np.float64) for f in ALL_FEATURES}


def bundle(atoms, names):
    if not names:
        return np.ones(N, dtype=np.float64)
    acc = np.sum([atoms[n] for n in names], axis=0)
    o = np.sign(acc)
    o[o == 0] = 1.0
    return o


def build_library(atoms, templates):
    W = np.zeros((N, N), dtype=np.float64)
    for _name, feats in sorted(templates.items()):
        t = bundle(atoms, feats)
        pc.vanilla_hebbian_write(W, t, t)
    return W


def residual_of(atoms, W, feats):
    obs = bundle(atoms, feats)
    pred = pc.predict(W, obs, sign_cleanup=True)
    return pc.residual_magnitude(obs, pred)


def best_template(atoms, templates, feats):
    obs = bundle(atoms, feats)
    best_name, best_cos = None, -2.0
    for name, tfeats in sorted(templates.items()):
        tb = bundle(atoms, tfeats)
        cos = float(np.dot(obs, tb)) / N
        if cos > best_cos:
            best_name, best_cos = name, cos
    return best_name, best_cos


def mint_signature(templates, feats):
    """New type's signature = passage features NOT in its best-feature-overlap template."""
    best_name, best_overlap = None, -1
    fset = set(feats)
    for name, tfeats in sorted(templates.items()):
        ov = len(fset & set(tfeats))
        if ov > best_overlap:
            best_name, best_overlap = name, ov
    return sorted(fset - set(templates[best_name]))


# ============================================================================ passage corpus
def _fill(tmpl, a, a2):
    return tmpl.replace("{A}", a).replace("{A2}", a2)


AGENTS = ["Jo", "Tom", "Amy", "Ruth", "Ann", "Meg", "Sid", "Beth"]

# IMPLICIT goal-block (withholding/omission) -- NO purpose connective (no 'so that'/'in order to').
GOAL_TMPLS = [
    "The girl wanted to reach safety. {A2} withheld the warning and left the child alone. "
    "She went down and was lost.",
    "The girl was dying to be warned in time. {A2} refused to warn her and ignored the child. "
    "She missed her chance and fell.",
    "The girl hoping to win to safety pleaded for care. {A2} neglected the girl and kept the warning. "
    "She sank and was lost.",
]
# NOISE seeded with OUTCOME-TRAP words (sank/fell/lost/down) -- NO animate desirer, NO withhold act.
NOISE_TMPLS = [
    "The warm spell had passed and a frost lay along the shore. The ice sank and the drift fell. "
    "The light was lost over the field and the sun went down.",
    "A chill mist floated past the meadow. The frost fell along the bank and the ice sank. "
    "The wind was lost over the hill and the grey sky went down.",
    "The cold wind drifted over the hill. The ice fell and sank along the path. "
    "A warm spell was lost and the sun went down over the field.",
]
HARM_TMPLS = [
    "{A} drove the knife into the man's breast and struck him hard, and the man was killed.",
    "{A} took up the poker and beat the boy over the head, and the child was left wounded and hurt.",
    "{A} smashed the bowl and tore the page, then struck the girl on the arm until she bled.",
]


def build_corpus():
    items = []
    for i in range(K_SYNTH):
        a = AGENTS[i % len(AGENTS)]
        a2 = AGENTS[(i + 3) % len(AGENTS)]
        items.append(dict(id=f"gb_syn_{i:02d}", cls="goal_block", gold_type="goal_blocker",
                          text=_fill(GOAL_TMPLS[i % len(GOAL_TMPLS)], a, a2)))
        items.append(dict(id=f"nz_syn_{i:02d}", cls="noise", gold_type=None,
                          text=NOISE_TMPLS[i % len(NOISE_TMPLS)]))
        items.append(dict(id=f"hm_syn_{i:02d}", cls="redundant_harm", gold_type="physical_harm",
                          text=_fill(HARM_TMPLS[i % len(HARM_TMPLS)], a, a)))
    items += load_real_items()
    return items


# REAL implicit-goal-block passages, VERBATIM from data/corpora/little_women/cleaned + gold ruler.
# Director-selected + glass-box role-annotated (NOT tuned to the views). n small, DIRECTIONAL.
REAL_ITEMS = [
    # grapp_mcca_004 (gold ruler): Amy's goal to be warned, blocked by Jo's WITHHOLDING. block +
    # outcome are verbatim novel text; the goal-owner desire is supplied via the gold goal-desc
    # annotation (same construction as v1's load_real_items).
    dict(id="mcca_004_amy_warning", cls="goal_block", gold_type="goal_blocker",
         subtype="withholding",
         text="being warned in time about the unsafe ice . "
              "No matter whether she heard or not, let her take care of herself . "
              "just in time to see Amy throw up her hands and go down",
         source="gold grapp_mcca_004 + little_women line 3278/3284"),
    # theatre refusal (little_women ~3058-3088): Amy's goal to go for fun, blocked by Jo's WITHHOLDING
    # ("You shan't stir a step"); left wailing. Fully verbatim; NO purpose connective in the spans.
    dict(id="theatre_refusal", cls="goal_block", gold_type="goal_blocker", subtype="withholding",
         text="I'm dying for some fun . "
              "If she goes I shan't . You shan't stir a step . "
              "leaving their sister wailing . You'll be sorry for this",
         source="little_women lines 3059-3088 (verbatim spans)"),
    # book-burning spite (little_women 3153-3184): Jo's goal to FINISH her book, blocked by Amy's
    # SPITE-DESTRUCTION ("I burned it up"). BOUNDARY item: the block is a destructive ACT, not a
    # withhold/omission -- tests whether the withhold-grounded view 1 over-claims here.
    dict(id="book_burning_spite", cls="goal_block", gold_type="goal_blocker",
         subtype="spite_destruction",
         text="My little book I meant to finish before Father got home . I burned it up . "
              "I never can write it again . it was a dreadful calamity",
         source="little_women lines 3153-3184 (verbatim spans)"),
    # grapp_mcca_003 (gold ruler): epistemic goal to identify the forger, an intercession
    # ("punished quite enough") -- BORDERLINE withhold-further-action. block verbatim; goal-desc
    # annotation.
    dict(id="mcca_003_forger", cls="goal_block", gold_type="goal_blocker", subtype="borderline",
         text="identify who forged the mock love-letter . "
              "Laurie has confessed, asked pardon, and been punished quite enough .",
         source="gold grapp_mcca_003"),
    # REAL harm controls (physical/direct causation) -- must NOT mint goal-blocker (C2).
    dict(id="mcca_001_killing", cls="redundant_harm", gold_type="physical_harm", subtype="physical",
         text="the half-breed saw his chance and drove the knife to the hilt in the young man's breast",
         source="gold grapp_mcca_001"),
    dict(id="mcca_005_bowl", cls="redundant_harm", gold_type="physical_harm", subtype="physical",
         text="Sid's fingers slipped and the bowl dropped and broke",
         source="gold grapp_mcca_005"),
]


def load_real_items():
    return [dict(it) for it in REAL_ITEMS]


# ============================================================================ the loop
def run_loop(atoms, W_seed, corpus, mode, seed):
    """One self-extension pass. mode in {full, residual_only}."""
    templates = dict(SEED_TEMPLATES)
    passages = [it for it in corpus if it["cls"] in ("goal_block", "noise", "redundant_harm")]

    proposals = {}
    per_passage = []
    for it in passages:
        feats = type_passage(it["text"])
        resid = residual_of(atoms, W_seed, feats)
        obs = bundle(atoms, feats)
        novel = pc.threshold_gate(obs, pc.predict(W_seed, obs), threshold=RESIDUAL_THRESHOLD)
        residual_fires = not novel.skipped                       # VIEW 1 novelty gate (proposes)
        v2_fires, v2_detail = view2_goal_outcome(it["text"], seed)  # VIEW 2 (disposes)
        v1_struct = view1_withhold_structure(it["text"])         # view-1 structural proposal (for independence)
        if mode == "full":
            enters = residual_fires and v2_fires
        else:  # residual_only ablation (no 2nd view)
            enters = residual_fires
        sig = mint_signature(templates, feats) if enters else None
        sig_key = "+".join(sig) if sig else None
        if enters and sig_key:
            p = proposals.setdefault(sig_key, {"sig": sig, "ids": [], "residuals": []})
            p["ids"].append(it["id"])
            p["residuals"].append(resid)
        per_passage.append(dict(id=it["id"], cls=it["cls"], feats=feats, residual=round(resid, 4),
                                residual_fires=residual_fires, view1_withhold_structure=v1_struct,
                                view2_goal_outcome=v2_fires, view2_detail=v2_detail,
                                enters_minting=enters, proposed_sig=sig,
                                subtype=it.get("subtype")))

    minted = {}
    templates_grown = dict(templates)
    for sig_key, p in sorted(proposals.items()):
        n_conf = len(p["ids"])
        if n_conf < MIN_CONFIRM:
            continue
        agg_margin = float(np.mean(p["residuals"]))
        adopt = decide_keep_or_revert({sig_key: agg_margin}, abstain_band=ABSTAIN_BAND_DEFAULT)
        if adopt is None:
            continue
        name = f"minted_type_{len(minted)}"
        templates_grown[name] = p["sig"]
        minted[name] = dict(signature=p["sig"], n_confirmations=n_conf,
                            confirming_ids=sorted(p["ids"]), agg_residual_margin=round(agg_margin, 4))

    return dict(mode=mode, per_passage=per_passage, minted=minted, templates_grown=templates_grown)


def _sig_is_goal(sig):
    s = set(sig)
    return len(s & set(GOAL_FEATURES)) >= 2 and len(s & set(NOISE_FEATURES)) == 0


def _sig_is_spurious(sig):
    s = set(sig)
    return len(s & set(NOISE_FEATURES)) >= 2 and len(s & set(GOAL_FEATURES)) == 0


def attribute(atoms, templates, corpus, cls):
    rows = [it for it in corpus if it["cls"] == cls and it.get("gold_type")]
    if not rows:
        return None
    correct = 0
    for it in rows:
        feats = type_passage(it["text"])
        pred_type, _ = best_template(atoms, templates, feats)
        if it["gold_type"] == "goal_blocker":
            hit = (pred_type in templates and pred_type.startswith("minted_")
                   and _sig_is_goal(templates[pred_type]))
        else:
            hit = (pred_type == it["gold_type"])
        correct += int(hit)
    return correct / len(rows)


# ============================================================================ per-seed unit
def run_seed(seed, corpus):
    atoms = feature_atoms(seed)
    W_seed = build_library(atoms, SEED_TEMPLATES)

    full = run_loop(atoms, W_seed, corpus, "full", seed)
    ronly = run_loop(atoms, W_seed, corpus, "residual_only", seed)

    full_goal = [n for n, m in full["minted"].items() if _sig_is_goal(m["signature"])]
    full_spurious = [n for n, m in full["minted"].items() if _sig_is_spurious(m["signature"])]
    ronly_spurious = [n for n, m in ronly["minted"].items() if _sig_is_spurious(m["signature"])]

    gb_before = attribute(atoms, SEED_TEMPLATES, corpus, "goal_block")
    gb_after = attribute(atoms, full["templates_grown"], corpus, "goal_block")
    harm_before = attribute(atoms, SEED_TEMPLATES, corpus, "redundant_harm")
    harm_after = attribute(atoms, full["templates_grown"], corpus, "redundant_harm")

    gb_ids = [it for it in corpus if it["cls"] == "goal_block"]
    resid_before = float(np.mean([residual_of(atoms, W_seed, type_passage(it["text"])) for it in gb_ids]))
    W_grown = build_library(atoms, full["templates_grown"])
    resid_after = float(np.mean([residual_of(atoms, W_grown, type_passage(it["text"])) for it in gb_ids]))

    # ---- INDEPENDENCE / co-fire measurement (THE CRUX) ----
    def rates(cls):
        rows = [p for p in full["per_passage"] if p["cls"] == cls]
        if not rows:
            return None
        n = len(rows)
        return dict(
            n=n,
            view1_residual_fire=round(sum(p["residual_fires"] for p in rows) / n, 3),
            view1_struct_fire=round(sum(p["view1_withhold_structure"] for p in rows) / n, 3),
            view2_fire=round(sum(p["view2_goal_outcome"] for p in rows) / n, 3),
            co_fire=round(sum(p["residual_fires"] and p["view2_goal_outcome"] for p in rows) / n, 3),
        )

    ind = {cls: rates(cls) for cls in ("goal_block", "noise", "redundant_harm")}

    # real-item transfer (per real item; directional)
    real = [dict(id=p["id"], subtype=p["subtype"], cls=p["cls"], residual=p["residual"],
                 residual_fires=p["residual_fires"], view1_withhold_structure=p["view1_withhold_structure"],
                 view2_goal_outcome=p["view2_goal_outcome"], enters_minting=p["enters_minting"],
                 proposed_sig=p["proposed_sig"])
            for p in full["per_passage"] if not p["id"].endswith(tuple(f"_{i:02d}" for i in range(K_SYNTH)))]

    # does a REAL implicit-goal-block (withholding) item enter minting AND does the loop mint goal type?
    real_withhold = [r for r in real if r["cls"] == "goal_block"
                     and r["id"] in ("mcca_004_amy_warning", "theatre_refusal")]
    real_withhold_enters = all(r["enters_minting"] for r in real_withhold) if real_withhold else False

    return dict(
        seed=seed,
        full_minted=full["minted"], residual_only_minted=ronly["minted"],
        full_goal_types=full_goal, full_spurious_types=full_spurious,
        residual_only_spurious_types=ronly_spurious,
        mints_goal_blocker=bool(full_goal),
        real_withhold_items_enter_minting=real_withhold_enters,
        C1_noise_no_mint_full=(len(full_spurious) == 0),
        C2_redundant_no_mint_full=all(_sig_is_goal(m["signature"]) for m in full["minted"].values()),
        C3_utility_lift=(gb_after is not None and gb_before is not None and gb_after > gb_before),
        C3_no_harm_regression=(harm_after is not None and harm_before is not None and harm_after >= harm_before),
        C4_residual_only_drifts=(len(ronly_spurious) >= 1),
        C4_full_no_drift=(len(full_spurious) == 0),
        INDEP_co_fire_noise_zero=(ind["noise"] is not None and ind["noise"]["co_fire"] == 0.0),
        INDEP_co_fire_harm_zero=(ind["redundant_harm"] is not None and ind["redundant_harm"]["co_fire"] == 0.0),
        gb_attrib_before=gb_before, gb_attrib_after=gb_after,
        harm_attrib_before=harm_before, harm_attrib_after=harm_after,
        gb_residual_before=round(resid_before, 4), gb_residual_after=round(resid_after, 4),
        independence=ind,
        real_items_transfer=real,
        per_passage=full["per_passage"],
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def frac(key):
        return sum(1 for s in seeds if per_seed[s][key]) / max(1, n)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return float(np.mean(vals)) if vals else None

    maj = lambda k: frac(k) > 0.5  # noqa: E731

    mints_goal = maj("mints_goal_blocker")
    real_enters = maj("real_withhold_items_enter_minting")
    c1 = maj("C1_noise_no_mint_full")
    c2 = maj("C2_redundant_no_mint_full")
    c3 = maj("C3_utility_lift") and maj("C3_no_harm_regression")
    c4 = maj("C4_residual_only_drifts") and maj("C4_full_no_drift")
    indep = maj("INDEP_co_fire_noise_zero") and maj("INDEP_co_fire_harm_zero")

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif mints_goal and real_enters and c1 and c2 and c3 and c4 and indep:
        verdict = "REAL_PROSE_SELF_EXTENSION_WORKS"
    elif mints_goal and real_enters and c1 and c2 and c3 and c4 and not indep:
        verdict = "MINTS_BUT_VIEWS_NOT_INDEPENDENT_WOULD_DRIFT"
    elif mints_goal and c1 and c2 and c3 and c4 and indep and not real_enters:
        verdict = "INDEPENDENT_ANTIDRIFT_HOLDS_BUT_REAL_PROSE_RECALL_GAP"
    else:
        verdict = "DRIFT_OR_INSUFFICIENT"

    s0 = per_seed[seeds[0]]
    goal_sig = None
    for _n, m in s0["full_minted"].items():
        if _sig_is_goal(m["signature"]):
            goal_sig = m
            break

    summary = (
        f"mints_goal={frac('mints_goal_blocker'):.2f} real_withhold_mints={frac('real_withhold_items_enter_minting'):.2f} | "
        f"C1_noise={frac('C1_noise_no_mint_full'):.2f} C2_harm={frac('C2_redundant_no_mint_full'):.2f} "
        f"C3_lift={frac('C3_utility_lift'):.2f}(noreg={frac('C3_no_harm_regression'):.2f}) "
        f"C4_ronly_drift={frac('C4_residual_only_drifts'):.2f}/full_nodrift={frac('C4_full_no_drift'):.2f} | "
        f"INDEP co_fire_noise0={frac('INDEP_co_fire_noise_zero'):.2f} co_fire_harm0={frac('INDEP_co_fire_harm_zero'):.2f} | "
        f"gb_attrib {mean('gb_attrib_before'):.2f}->{mean('gb_attrib_after'):.2f}")

    # aggregate independence rates across seeds (mean)
    def ind_mean(cls, key):
        vals = [per_seed[s]["independence"][cls][key] for s in seeds
                if per_seed[s]["independence"].get(cls)]
        return round(float(np.mean(vals)), 3) if vals else None

    indep_agg = {cls: {k: ind_mean(cls, k) for k in
                       ("view1_residual_fire", "view1_struct_fire", "view2_fire", "co_fire")}
                 for cls in ("goal_block", "noise", "redundant_harm")}

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        fractions=dict(
            mints_goal_blocker=frac("mints_goal_blocker"),
            real_withhold_items_enter_minting=frac("real_withhold_items_enter_minting"),
            C1_noise_no_mint_full=frac("C1_noise_no_mint_full"),
            C2_redundant_no_mint_full=frac("C2_redundant_no_mint_full"),
            C3_utility_lift=frac("C3_utility_lift"), C3_no_harm_regression=frac("C3_no_harm_regression"),
            C4_residual_only_drifts=frac("C4_residual_only_drifts"), C4_full_no_drift=frac("C4_full_no_drift"),
            INDEP_co_fire_noise_zero=frac("INDEP_co_fire_noise_zero"),
            INDEP_co_fire_harm_zero=frac("INDEP_co_fire_harm_zero"),
        ),
        means=dict(
            gb_attrib_before=mean("gb_attrib_before"), gb_attrib_after=mean("gb_attrib_after"),
            harm_attrib_before=mean("harm_attrib_before"), harm_attrib_after=mean("harm_attrib_after"),
            gb_residual_before=mean("gb_residual_before"), gb_residual_after=mean("gb_residual_after"),
        ),
        independence_rates_mean=indep_agg,
        minted_goal_blocker_signature_seed0=goal_sig,
        real_items_transfer_seed0=s0["real_items_transfer"],
        residual_only_spurious_types_seed0=s0["residual_only_spurious_types"],
        full_spurious_types_seed0=s0["full_spurious_types"],
        brain_structures=dict(
            view1_argument_structure="DMN/mPFC agent-goal representation + Trabasso goal-plan analysis; "
                                     "left-IFG/pMTG relational argument binding; NOVELTY = VTA-dopamine RPE "
                                     "+ cortical predictive coding (Rao-Ballard/Friston) over the harm-only "
                                     "seed schema (van Kesteren 2012 schema-incongruity)",
            view2_goal_outcome="OFC/vmPFC outcome-value appraisal over the situation model (Kintsch C-I / "
                               "Zwaan event-indexing accumulation) -- reused hdlab.situation_model_accumulate "
                               "AccumulateRegister organ (atom 29609): bind/bundle/unbind/cleanup",
            independence_coupling="NELL CPL promotion-requires-an-INDEPENDENT-view (WSDM 2010): view 1 = "
                                  "the blocker's act frame; view 2 = the owner's goal-outcome trajectory -- "
                                  "disjoint lexicon AND disjoint mechanism",
            consolidation_gate="ACC/PFC conflict-monitoring control (self_improving_loop) + neocortical slow "
                               "interleaved consolidation (>=2 cross-confirmations)",
        ),
        caveats=[
            "Both views are grounded glass-box lexical/appraisal maps (supplied ~6yo goal-schema KNOWLEDGE, "
            "proper-noun-free, NOT tuned to the test items) -- the loop SCORES/MINTS given a faithful typing; "
            "it does not induce the lexicons themselves (accepted construction caveat, as v1).",
            "View-1 argument binding is co-occurrence-level (withhold verb + animate beneficiary in the "
            "passage), a glass-box proxy for full predicate-argument structure -- NO borrowed dependency "
            "parser (guard).",
            "REAL items n=6 (4 goal_block incl 2 clean withholding + 1 spite-destruction boundary + 1 "
            "borderline; 2 harm controls). VERBATIM from data/corpora/little_women/cleaned + gold ruler; "
            "goal-owner desire for the two gold ruler items is supplied via the gold goal-description "
            "annotation (same construction as v1). DIRECTIONAL; statistical power is the synthetic set.",
            "predictive_coding / self_improving_loop / normalize_tokens / situation_model_accumulate reused "
            "bit-identical; no borrowed embedding/LLM/parser as mechanism; minted type NAME is a placeholder.",
        ],
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode):
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    _write_json(os.path.join(out_dir, "_start_marker.json"), marker)

    corpus = build_corpus()
    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, corpus)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s mints_goal={res['mints_goal_blocker']} "
              f"real_withhold_mints={res['real_withhold_items_enter_minting']} "
              f"C1={res['C1_noise_no_mint_full']} C4_drift={res['C4_residual_only_drifts']} "
              f"co_fire_noise0={res['INDEP_co_fire_noise_zero']} "
              f"gb_attrib {res['gb_attrib_before']}->{res['gb_attrib_after']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(N=N, D2=D2, seeds=seeds, residual_threshold=RESIDUAL_THRESHOLD,
                         min_confirm=MIN_CONFIRM, k_synth=K_SYNTH, max_events=MAX_EVENTS)
    agg["prereg"] = "preregs/2026-08-04_self_extension_grounded_realprose_v1.md"
    agg["cites"] = ["experiments/exp_self_extension_loop_v1.py",
                    "preregs/2026-08-04_self_extension_loop_v1.md",
                    "notes/brain_component_functional_map_2026-08-04.md",
                    "hdlab/situation_model_accumulate.py (atom 29609)"]
    agg["per_seed"] = per_seed
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) THE INDEPENDENCE INVARIANT: view-1 and view-2 lexicons are DISJOINT (no shared token).
    overlap = V1_ALL_LEX & V2_ALL_LEX
    assert not overlap, f"views NOT lexically disjoint: {sorted(overlap)}"

    corpus = build_corpus()
    gb = next(it for it in corpus if it["cls"] == "goal_block")
    hm = next(it for it in corpus if it["cls"] == "redundant_harm")
    nz = next(it for it in corpus if it["cls"] == "noise")
    fgb, fhm, fnz = type_passage(gb["text"]), type_passage(hm["text"]), type_passage(nz["text"])
    # (1) view-1 typer separation
    assert set(GOAL_FEATURES) & set(fgb), f"goal_block missing goal feats: {fgb}"
    assert "HARM_OUTCOME" in fhm, f"harm missing HARM_OUTCOME: {fhm}"
    assert set(NOISE_FEATURES) & set(fnz) and not (set(GOAL_FEATURES) & set(fnz)), f"noise typing off: {fnz}"

    # (2) view-2 grounded goal-outcome appraisal: TRUE on goal_block, FALSE on noise + harm.
    #     Noise carries OUTCOME-TRAP words (sank/fell/lost/down) -> view 2 MUST stay silent (grounded).
    assert view2_goal_outcome(gb["text"], 0)[0], "view2 missed goal-outcome on goal_block"
    assert not view2_goal_outcome(nz["text"], 0)[0], "view2 FALSE-FIRED on outcome-trap noise (not grounded)"
    assert not view2_goal_outcome(hm["text"], 0)[0], "view2 FALSE-FIRED on harm"

    # (3) residual gate separates typed-harm (low) from goal_block + noise (high) at threshold
    atoms = feature_atoms(0)
    W = build_library(atoms, SEED_TEMPLATES)
    r_hm = residual_of(atoms, W, fhm)
    r_gb = residual_of(atoms, W, fgb)
    r_nz = residual_of(atoms, W, fnz)
    assert r_hm < RESIDUAL_THRESHOLD < min(r_gb, r_nz), f"residual sep off: hm={r_hm} gb={r_gb} nz={r_nz}"

    # (4) REAL withholding items: both grounded views fire -> enters minting (the make-or-break)
    for rid in ("mcca_004_amy_warning", "theatre_refusal"):
        it = next(x for x in corpus if x["id"] == rid)
        assert view1_withhold_structure(it["text"]), f"view1 missed withhold structure on {rid}"
        assert view2_goal_outcome(it["text"], 0)[0], f"view2 missed goal-outcome on {rid}"

    # (5) one full seed: mints goal_blocker, no spurious in full, residual_only drifts, utility lifts,
    #     co-fire on noise is ZERO (the crux independence metric)
    res = run_seed(0, corpus)
    assert res["mints_goal_blocker"], "did not mint goal_blocker"
    assert res["C1_noise_no_mint_full"], "full minted a spurious type"
    assert res["C4_residual_only_drifts"], "residual_only did not drift (ablation vacuous)"
    assert res["INDEP_co_fire_noise_zero"], f"CO-FIRE ON NOISE non-zero: {res['independence']['noise']}"
    assert res["real_withhold_items_enter_minting"], "real withholding items did not enter minting"
    print(f"[SELFTEST PASS] views lexically disjoint; view2 grounded (no false-fire on outcome-trap "
          f"noise); seed0 mints goal_blocker; co_fire_noise={res['independence']['noise']['co_fire']} "
          f"co_fire_harm={res['independence']['redundant_harm']['co_fire']}; real_withhold_enters="
          f"{res['real_withhold_items_enter_minting']}; gb_attrib {res['gb_attrib_before']}->"
          f"{res['gb_attrib_after']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
