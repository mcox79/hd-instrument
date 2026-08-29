"""exp_shared_predarg_frontend_v1 -- proves there is no SHARED predicate-argument (semantic-role)
front end in this substrate: the live who-did-what reader assigns agent/patient with an inline
positional rule and produces NO goal/recipient; the SPACE organ (location_register) and
parse_goal_extraction each re-derive argument structure inline, separately. This cell builds a
SHARED dispatch, extract_predicate_arguments(tokens, pos, heads, verb_idx) -> {agent, theme, goal,
recipient, instrument, goal_belongs_to}, by COMPOSING already-validated organs (never inventing a
new role-assignment RULE):

  PARSE (glass-box, no spaCy): hdlab.candidate_generator.CandidateGenerator (persisted UPOS tagger +
    hashed arc-factored parser, trained on gold UD-EWT).
  AGENT/THEME (word-order + voice): hdlab.graded_role_assigner.hybrid_role_patient (the validated
    Competition-Model patient binder) for theme; hdlab.relcl_resolver.precise_passive (the SAME
    accurate BE-aux+participle-or-participle+by-PP gate hybrid_role_patient itself consults
    internally) for the agent voice-swap decision.
  PP ROLES (VerbNet-lexicon gates): experiments.location_register.is_motion_verb / is_place_ground /
    _COMM_TRANSFER_BLOCK route each preposition's object to GOAL / RECIPIENT / INSTRUMENT.

DISK-VERIFIED DEVIATION FROM THE LITERAL BRIEF (recorded here because it changed a load-bearing
design decision -- see PRE-DISPATCH VET below): the brief's pinned algorithm says "Apply
robust_passive/voice_cues ... on passive, swap". Measured directly on this cell's own arc-parser
output (17 hand sentences, see notes below): hdlab.graded_role_assigner.robust_passive returns
True on 12 of 17, including 9 genuinely ACTIVE clauses with no auxiliary at all ("The guard hurried
to the ground.", "Tom handed the letter to Mary.", "The old man pointed to the door."). This is
NOT a bug in robust_passive -- its own docstring calls it "the recall arm", deliberately
over-inclusive so the graded-competition mechanism's LEARNED validity (vc_partN: -2.99, "correctly
driven negative, never a trigger") can down-weight the weak bare-participle-after-nominal cue.
Using it as a hard external boolean gate outside that competition context reintroduces exactly the
false-positive class the learned weights exist to suppress -- it would misroute AGENT on the
majority of active sentences in this cell's own gold. hybrid_role_patient itself consults
precise_passive (BE-aux + participle morphology) for its own confident-route decision; this cell's
external agent-swap gate reuses THAT SAME function for consistency with the already-validated
internal theme computation, rather than the permissive recall-arm one named in the literal brief
text. voice_cues/robust_passive are still imported and available; the swap decision is
precise_passive. This is disclosed, not silent -- see the PRE-DISPATCH VET section of the final
report for the full 17-sentence measurement.

ARMS (one variable = the role-assignment rule; see ARM_NAMES):
  SHARED    the extractor above.
  INLINE    the fragmented status-quo floor: agent=subject-before-verb, patient=nearest nominal
            after (NO voice swap); goal=first to/into/onto/toward-PP object, attributed to the
            AGENT unconditionally (no VerbNet gate, no moved-theme gate); recipient/instrument
            never produced. Recomputed fresh on every population, never cached.
  TWIN      SHARED with a RANDOM PERMUTATION of the verb->class (motion/comm/other) mapping, fixed
            seed, same overall class rate -- an info-free control that must LOSE on goal/recipient.
  RANDOM    each role SHARED realized gets a uniformly random candidate nominal (fixed seed).

GOLDS: (1) the 32-item minimal-pair positive control (notes/problems/.../minimal_pair_role_gold_v1
.jsonl), scored by per-role head-word match on decisive vs contrast items; (2) a QA-SRL v2 (dev+
test) 4-role gold: agent/theme via experiments.exp_reader_vs_twoline_qasrl_power_v1._entry_spans
(reused unmodified), goal/recipient built fresh here per the pre-registered filter spec (locative-
prep-first-token / length<=6 / no figure-table-example word / no clause-bleed word for goal;
prep in {to,for} / not an infinitival slot / nominal-tagged head for recipient), span-based scoring.
(3) downstream lift: coverage on QA-SRL entries that HAVE a gold goal or recipient (INLINE cannot
answer these -> 0 by construction).

WRITE ONLY: this file and data/exp_shared_predarg_frontend_v1/ (+ _smoke / _selftest siblings).
Does not modify hdlab/, preregs/, data/foundation/, or any arm_key* file.

Usage: --self-test (fast, hand cases) | --smoke (32 minimal pairs + 400-sentence QA-SRL/dev sample)
| (bare) full (minimal pairs + full QA-SRL dev+test).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import gzip
import json
import random
import sys
import time
import traceback
import zlib
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ANCHOR_NAME = "shared_predarg_frontend_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")
QASRL_DIR = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "qasrl", "qasrl-v2", "orig")
GOLD_PATH = os.path.join(REPO_ROOT, "notes", "problems",
                         "no_shared_shallow_predicate_argument_front_end",
                         "minimal_pair_role_gold_v1.jsonl")
POS_CKPT = os.path.join(REPO_ROOT, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json")
ARC_CKPT = os.path.join(REPO_ROOT, "data", "frontend_assets", "arc_parser_hashed_ud_ewt.npz")

from hdlab.candidate_generator import CandidateGenerator  # noqa: E402
from hdlab.graded_role_assigner import voice_cues, robust_passive, hybrid_role_patient, competition_pick  # noqa: E402
from hdlab.relcl_resolver import precise_passive  # noqa: E402
from hdlab.thematic_role_labeler import lemma_verb  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402
from hdlab.parse_goal_extraction import parse_extract_goal  # noqa: E402  (optional cross-check, self-test only)
from experiments.location_register import (  # noqa: E402
    is_motion_verb, is_place_ground, _COMM_TRANSFER_BLOCK, _MOTION_VERBS,
)
from experiments.exp_reader_vs_twoline_qasrl_power_v1 import _entry_spans, _majority_span  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

NOMINAL = {"NOUN", "PROPN", "PRON"}
# bullets 1 & 2 of the pinned PP-routing algorithm (recipient-if-comm-verb / goal-if-motion-verb).
PP_CORE_PREPS = {"to", "into", "onto", "toward", "towards", "for"}
# bullet 4 (literal): "a bare place particle ('on'/'out'/'up'/'down') ... only treat as goal if it
# has a locative nominal object (is_place_ground)" -- these 4 words get an EXTRA place-typing gate.
PP_PARTICLE_TYPED_PREPS = {"on", "out", "up", "down"}
_INLINE_GOAL_PREPS = {"to", "into", "onto", "toward"}  # INLINE's narrower, ungated trigger set
# idiom/reflexive moved-theme exclusions (own-path nominals that are not a competing theme).
IDIOM_THEME_WORDS = {"way", "himself", "herself", "themselves", "myself", "ourselves", "yourself",
                     "yourselves", "course", "steps", "footsteps", "path", "route", "head", "feet"}
LOCATIVE_PREP_WHITELIST = {"in", "on", "at", "to", "into", "onto", "down", "up", "through", "across",
                           "toward", "towards", "over", "under", "inside", "outside", "near", "beside",
                           "beyond", "along", "around", "from", "off", "out"}
BAD_FIGURE_WORDS = {"figure", "fig", "table", "example", "exercise", "chapter", "section", "page"}
CLAUSE_BLEED_WORDS = {"because", "when", "where", "which", "that", "while", "since", "although", "if",
                      "whether"}

N_BOOT = 10000
N_BOOT_PAIRED = 2000        # brief's explicit paired-CI resample count for SHARED-minus-INLINE
N_PERM_NULL = 2000
BOOT_SEED = 20260828
TWIN_SEED = 20260828
RANDOM_SEED = 20260828
MAX_HOPS = 4
ARM_NAMES = ["SHARED", "INLINE", "TWIN", "RANDOM"]

_GEN_CACHE: Optional[CandidateGenerator] = None


def _default_generator() -> CandidateGenerator:
    global _GEN_CACHE
    if _GEN_CACHE is None:
        _GEN_CACHE = CandidateGenerator.load(POS_CKPT, ARC_CKPT)
    return _GEN_CACHE


# =============================================================================================
# structural plumbing (NOT a role-assignment decision): interface the arc-parse's own UD 'case'
# convention (an ADP's head IS its nominal object) with the reused VerbNet-lexicon gates.
# =============================================================================================
def _cands(pos: Sequence[str]) -> List[int]:
    return [i for i in range(1, len(pos) + 1) if pos[i - 1] in NOMINAL]


def _attaches_to_verb(start: int, v: int, heads: Dict[int, int], pos: Sequence[str],
                      max_hops: int = MAX_HOPS) -> bool:
    """Walk UP the head chain from `start`; True iff verb v is reached within max_hops without first
    hitting a DIFFERENT verb or the root. Tolerates one intervening ADV/NOUN hop -- this UD-EWT
    parser sometimes attaches a caused-motion goal PP to the moved-theme NOUN rather than the verb
    directly (measured: 'dragged the cannon to the hill' -> hill's head is cannon, cannon's head is
    the verb), and sometimes routes a satellite ADV between an adverbial and its own PP (measured:
    'slipped away to the sailor' -> sailor's head is 'away', away's head is the verb)."""
    cur = start
    for _ in range(max_hops + 1):
        if cur == v:
            return True
        if cur is None or cur == 0:
            return False
        if pos[cur - 1] == "VERB" and cur != v:
            return False
        cur = heads.get(cur)
    return False


def _pp_args_for_verb(tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int], v: int,
                      max_hops: int = MAX_HOPS) -> List[Tuple[str, int]]:
    """[(prep_lower, obj_idx), ...] sorted by obj position, for every ADP token whose own head (its UD
    'case' relation target -- the nominal it introduces) transitively attaches to verb v."""
    n = len(tokens)
    out = []
    for p in range(1, n + 1):
        if pos[p - 1] != "ADP":
            continue
        obj = heads.get(p)
        if obj is None or obj in (0, p):
            continue
        if _attaches_to_verb(obj, v, heads, pos, max_hops=max_hops):
            out.append((tokens[p - 1].lower(), obj))
    out.sort(key=lambda x: x[1])
    return out


def _goal_belongs_to(theme_idx: Optional[int], goal_obj_idx: int, tokens: Sequence[str]) -> str:
    """MOVED-THEME GATE: a non-idiom theme DISTINCT from the PP's own object is the true goal-holder
    (caused-motion: 'shoved him to the ground' -> him). If the theme binder found nothing, found the
    PP object itself (an intransitive+PP construction with no real direct object -- the binder's
    positional default falls back to the only candidate available), or found an idiom/reflexive
    path-noun, the goal belongs to the agent (self-motion: 'hurried to the ground')."""
    if theme_idx is None or theme_idx == goal_obj_idx:
        return "agent"
    if tokens[theme_idx - 1].lower() in IDIOM_THEME_WORDS:
        return "agent"
    return "theme"


# =============================================================================================
# THE SHARED EXTRACTOR (pinned)
# =============================================================================================
def extract_predicate_arguments(tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int],
                                verb_idx: int, motion_fn=is_motion_verb, comm_block=None,
                                max_hops: int = MAX_HOPS, include_location: bool = True) -> dict:
    """Returns 1-based token indices (or None): {agent, theme, goal, recipient, instrument, location,
    goal_belongs_to}. motion_fn/comm_block are override points ONLY for the TWIN info-free control
    (a random permutation of the verb->class mapping); SHARED always uses the true is_motion_verb /
    _COMM_TRANSFER_BLOCK (the defaults).

    LOCATION (coordinator-directed addition, 2026-08-28, isolating the GOAL loss on QA-SRL's 'where'
    gold): a locative PP (is_place_ground object) under a verb that is NEITHER motion NOR comm/
    transfer names a STATIVE location, distinct from GOAL (a destination reached via motion). The
    hand-audit found QA-SRL's 'where' wh-question conflates the two (~25% motion-destination, ~60%
    stative-location); this role isolates the stative half instead of silently missing it. Additive
    ONLY -- agent/theme/goal/recipient/instrument/goal_belongs_to are computed exactly as before."""
    if comm_block is None:
        comm_block = _COMM_TRANSFER_BLOCK
    v = verb_idx
    cands = _cands(pos)
    passive = precise_passive(tokens, pos, v)          # see module docstring: NOT robust_passive
    theme_idx = hybrid_role_patient(tokens, pos, v, cands=cands)
    pp_args = _pp_args_for_verb(tokens, pos, heads, v, max_hops=max_hops)

    by_obj = next((o for (p, o) in pp_args if p == "by"), None)
    if passive:
        agent_idx = by_obj
    else:
        before = [i for i in cands if i < v]
        agent_idx = before[-1] if before else None

    lemma = lemma_verb(tokens[v - 1])
    is_comm = lemma in comm_block
    is_motion = (not is_comm) and motion_fn(lemma)
    goal_idx = None
    goal_belongs_to = None
    recipient_idx = None
    instrument_idx = None
    consumed = set()
    for prep, obj in pp_args:
        if prep == "by":
            continue
        if prep == "with":
            if instrument_idx is None:
                word = tokens[obj - 1]
                if not is_place_ground(word):
                    anim = lookup_animacy(word, pos[obj - 1] if obj - 1 < len(pos) else None)
                    animacy = anim["animacy"] if anim else "unk"
                    if animacy != "animate":
                        instrument_idx = obj
                        consumed.add(obj)
            continue
        if prep in PP_CORE_PREPS:
            if is_comm:
                if recipient_idx is None:
                    recipient_idx = obj
                    consumed.add(obj)
            elif is_motion:
                if goal_idx is None:
                    goal_idx = obj
                    goal_belongs_to = _goal_belongs_to(theme_idx, goal_idx, tokens)
                    consumed.add(obj)
        elif prep in PP_PARTICLE_TYPED_PREPS:
            if goal_idx is None and is_motion and is_place_ground(tokens[obj - 1]):
                goal_idx = obj
                goal_belongs_to = _goal_belongs_to(theme_idx, goal_idx, tokens)
                consumed.add(obj)

    location_idx = None
    if include_location and not is_motion and not is_comm:
        for prep, obj in pp_args:
            if prep in ("by", "with") or obj in consumed:
                continue
            if is_place_ground(tokens[obj - 1]):
                location_idx = obj
                break

    return {"agent": agent_idx, "theme": theme_idx, "goal": goal_idx, "recipient": recipient_idx,
            "instrument": instrument_idx, "location": location_idx, "goal_belongs_to": goal_belongs_to}


def arm_inline(tokens: Sequence[str], pos: Sequence[str], heads: Dict[int, int], verb_idx: int) -> dict:
    """FLOOR: fragmented status-quo. agent=subject-before-verb, patient=nearest nominal after (NO
    voice check); goal=first to/into/onto/toward-PP object, attributed to the AGENT unconditionally
    (no VerbNet gate, no moved-theme gate); recipient/instrument never produced."""
    v = verb_idx
    cands = _cands(pos)
    before = [i for i in cands if i < v]
    after = [i for i in cands if i > v]
    agent_idx = before[-1] if before else None
    theme_idx = after[0] if after else None
    pp_args = _pp_args_for_verb(tokens, pos, heads, v)
    goal_idx = None
    for prep, obj in pp_args:
        if prep in _INLINE_GOAL_PREPS:
            goal_idx = obj
            break
    return {"agent": agent_idx, "theme": theme_idx, "goal": goal_idx, "recipient": None,
            "instrument": None, "goal_belongs_to": ("agent" if goal_idx is not None else None)}


def build_twin_classifiers(lemmas: Sequence[str], seed: int = TWIN_SEED):
    """SHARED but with a RANDOM PERMUTATION of the verb->class (motion/comm/other) mapping: same
    overall class rate, WHICH lemma gets WHICH class is shuffled with a fixed seed."""
    lemmas = sorted(set(lemmas))

    def true_cls(lem):
        if lem in _COMM_TRANSFER_BLOCK:
            return "comm"
        if is_motion_verb(lem):
            return "motion"
        return "other"

    true = [true_cls(l) for l in lemmas]
    shuffled = true[:]
    random.Random(seed).shuffle(shuffled)
    twin_map = dict(zip(lemmas, shuffled))
    twin_comm_block = frozenset(l for l in lemmas if twin_map.get(l) == "comm")

    def twin_is_motion(lem):
        return twin_map.get(lem, "other") == "motion"

    return twin_is_motion, twin_comm_block


def arm_random(shared: dict, cands: List[int], seed: int) -> dict:
    """RANDOM floor: each role SHARED realized gets a uniformly random candidate nominal."""
    rng = random.Random(seed)
    out = {}
    for k in ("agent", "theme", "goal", "recipient", "instrument", "location"):
        out[k] = rng.choice(cands) if (shared.get(k) is not None and cands) else None
    out["goal_belongs_to"] = (rng.choice(["agent", "theme"]) if shared.get("goal") is not None else None)
    return out


def _crc_seed(*parts) -> int:
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8")) & 0x7FFFFFFF


# =============================================================================================
# MINIMAL-PAIR positive control
# =============================================================================================
def load_minimal_pairs(path: str) -> List[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def _find_verb_idx(tokens: Sequence[str], pos: Sequence[str], gold_verb: str) -> Optional[int]:
    gv = gold_verb.lower()
    for i, (t, p) in enumerate(zip(tokens, pos), start=1):
        if p == "VERB" and t.lower() == gv:
            return i
    gvl = lemma_verb(gv)
    for i, (t, p) in enumerate(zip(tokens, pos), start=1):
        if p == "VERB" and lemma_verb(t.lower()) == gvl:
            return i
    return None


ROLE_FIELDS = ["agent", "theme", "goal", "recipient", "instrument"]


def score_minimal_pairs(gen: CandidateGenerator) -> dict:
    items = load_minimal_pairs(GOLD_PATH)
    twin_motion_fn, twin_comm_block = build_twin_classifiers(
        [lemma_verb(it["verb"]) for it in items], seed=TWIN_SEED)
    rows = []
    n_parse_fail = 0
    for it in items:
        cr = gen.generate(it["text"], extended=True)
        toks, pos, heads = cr.tokens, cr.pos, cr.heads
        v = _find_verb_idx(toks, pos, it["verb"])
        # gold field is "none -- <explanation of why both arms agree>" for contrast items, not the
        # literal 4-char string "none" -- match by prefix.
        decisive = not it["naive_inline_error"].startswith("none")
        if v is None:
            n_parse_fail += 1
            rows.append({"id": it["id"], "decisive": decisive, "parse_fail": True,
                        "field_acc": {a: 0.0 for a in ARM_NAMES}})
            continue
        cands = _cands(pos)
        shared = extract_predicate_arguments(toks, pos, heads, v)
        inline = arm_inline(toks, pos, heads, v)
        twin = extract_predicate_arguments(toks, pos, heads, v, motion_fn=twin_motion_fn,
                                           comm_block=twin_comm_block)
        randm = arm_random(shared, cands, seed=_crc_seed("mp", it["id"]))
        gold = it["roles"]
        gold_gbt = it.get("goal_belongs_to")
        field_acc = {}
        for arm_name, res in (("SHARED", shared), ("INLINE", inline), ("TWIN", twin), ("RANDOM", randm)):
            matches = []
            for f in ROLE_FIELDS:
                gv = gold.get(f)
                pv_idx = res.get(f)
                pv = toks[pv_idx - 1].lower() if pv_idx else None
                gv_norm = gv.lower() if gv else None
                matches.append(1.0 if pv == gv_norm else 0.0)
            if gold_gbt is not None:
                matches.append(1.0 if res.get("goal_belongs_to") == gold_gbt else 0.0)
            field_acc[arm_name] = float(np.mean(matches))
        rows.append({"id": it["id"], "decisive": decisive, "parse_fail": False, "field_acc": field_acc})

    decisive_rows = [r for r in rows if r["decisive"]]
    contrast_rows = [r for r in rows if not r["decisive"]]

    def avg(rows_, arm):
        vals = [r["field_acc"][arm] for r in rows_]
        return float(np.mean(vals)) if vals else float("nan")

    return {
        "n_items": len(items), "n_parse_fail": n_parse_fail,
        "n_decisive": len(decisive_rows), "n_contrast": len(contrast_rows),
        "decisive_acc": {a: avg(decisive_rows, a) for a in ARM_NAMES},
        "contrast_acc": {a: avg(contrast_rows, a) for a in ARM_NAMES},
        "rows": rows,
    }


# =============================================================================================
# QA-SRL v2 4-role gold construction
# =============================================================================================
def _clean_goal_span(toks: List[str], span) -> bool:
    s, e = span
    if e <= s or (e - s) > 6:
        return False
    words = [w.lower() for w in toks[s:e]]
    if words[0] not in LOCATIVE_PREP_WHITELIST:
        return False
    if any(w in BAD_FIGURE_WORDS for w in words):
        return False
    if any(w in CLAUSE_BLEED_WORDS for w in words):
        return False
    return True


def _clean_recipient_span(sl: dict, span, toks: List[str]) -> bool:
    if span is None:
        return False
    s, e = span
    if e <= s or (e - s) > 6:
        return False
    # QA-SRL's 'obj2' slot is the PP's OWN object; obj2=='_' means the wh-word targets exactly that
    # slot (a genuine "...to/for WHOM/WHAT?" question). Without this check, prep in {to,for} alone
    # also matches SUBJECT questions that merely CONTAIN an unrelated to/for-PP elsewhere in the
    # clause (measured: "Weather refers to the conditions..." -> gold answer "Weather", the SUBJECT,
    # slots {'subj':'_','obj2':'something'} -- obj2 filled means the PP is GIVEN, subj is asked).
    # subj!='_' additionally requires the subject be given/filled, not itself the wh-target.
    if sl.get("obj2", "_") != "_":
        return False
    if sl.get("subj", "_") == "_":
        return False
    words = [w.lower() for w in toks[s:e]]
    if words[0] in ("to", "for"):        # residual infinitival/purpose leakage in the answer itself
        return False
    return True


def _head_in_span(pos: Sequence[str], span) -> Optional[int]:
    s, e = span
    for k in range(e, s, -1):
        if k - 1 < len(pos) and pos[k - 1] in NOMINAL:
            return k
    return None


def load_qasrl_items(split_file: str, max_sentences: Optional[int] = None) -> List[dict]:
    items = []
    n_sent = 0
    p = os.path.join(QASRL_DIR, split_file)
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        for line in fh:
            if max_sentences is not None and n_sent >= max_sentences:
                break
            d = json.loads(line)
            toks = d["sentenceTokens"]
            n_sent += 1
            for vk, ve in d["verbEntries"].items():
                v0 = ve["verbIndex"]
                sp = _entry_spans(ve)
                if sp["patient"] is not None:
                    items.append({"toks": toks, "verb_idx0": v0, "role_type": "theme",
                                 "span": list(sp["patient"])})
                if sp["agent"] is not None:
                    items.append({"toks": toks, "verb_idx0": v0, "role_type": "agent",
                                 "span": list(sp["agent"])})
                for q, lab in ve["questionLabels"].items():
                    sl = lab["questionSlots"]
                    if sl["wh"] == "where":
                        span = _majority_span(lab)
                        if span is not None and _clean_goal_span(toks, span):
                            items.append({"toks": toks, "verb_idx0": v0, "role_type": "goal",
                                         "span": list(span)})
                            break
                for q, lab in ve["questionLabels"].items():
                    sl = lab["questionSlots"]
                    if sl["wh"] in ("who", "what") and sl.get("prep") in ("to", "for"):
                        span = _majority_span(lab)
                        if span is not None and _clean_recipient_span(sl, span, toks):
                            items.append({"toks": toks, "verb_idx0": v0, "role_type": "recipient",
                                         "span": list(span)})
                            break
    return items


def parse_and_align(gen: CandidateGenerator, items: List[dict]) -> Tuple[List[dict], int]:
    cache: Dict[str, object] = {}
    out = []
    n_mismatch = 0
    for it in items:
        text = " ".join(it["toks"])
        cr = cache.get(text)
        if cr is None:
            cr = gen.generate(text, extended=True)
            cache[text] = cr
        if list(cr.tokens) != list(it["toks"]):
            n_mismatch += 1
            continue
        it = dict(it)
        it["pos"] = list(cr.pos)
        it["heads"] = dict(cr.heads)
        it["verb_idx"] = it["verb_idx0"] + 1
        vi = it["verb_idx"]
        if not (1 <= vi <= len(it["pos"])) or it["pos"][vi - 1] != "VERB":
            n_mismatch += 1
            continue
        out.append(it)
    return out, n_mismatch


_ROLE_KEY = {"agent": "agent", "theme": "theme", "goal": "goal", "recipient": "recipient"}


def score_qasrl_items(items: List[dict], twin_motion_fn, twin_comm_block, seed: int) -> List[dict]:
    rng_master = random.Random(seed)
    recs = []
    for idx, it in enumerate(items):
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        cands = _cands(pos)
        shared = extract_predicate_arguments(toks, pos, heads, v)
        inline = arm_inline(toks, pos, heads, v)
        twin = extract_predicate_arguments(toks, pos, heads, v, motion_fn=twin_motion_fn,
                                           comm_block=twin_comm_block)
        randm = arm_random(shared, cands, seed=rng_master.randint(0, 2**31 - 1))
        role = it["role_type"]
        s, e = it["span"]

        def correct(pick):
            return int(pick is not None and (s < pick <= e))

        recs.append({
            "role_type": role, "split": it.get("split"), "verb_lemma": lemma_verb(toks[v - 1]),
            "correct": {"SHARED": correct(shared.get(_ROLE_KEY[role])),
                       "INLINE": correct(inline.get(_ROLE_KEY[role])),
                       "TWIN": correct(twin.get(_ROLE_KEY[role])),
                       "RANDOM": correct(randm.get(_ROLE_KEY[role]))},
        })
    return recs


# =============================================================================================
# bootstrap utilities (generic; matches exp_reader_vs_twoline_qasrl_power_v1's convention)
# =============================================================================================
def _boot_means(x: np.ndarray, n_boot: int, seed: int, chunk: int = 500) -> np.ndarray:
    n = len(x)
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot, dtype=np.float64)
    done = 0
    while done < n_boot:
        c = min(chunk, n_boot - done)
        idx = rng.integers(0, n, size=(c, n))
        out[done:done + c] = x[idx].mean(axis=1)
        done += c
    return out


def boot_mean(a: np.ndarray, n_boot: int, seed: int) -> dict:
    n = len(a)
    pt = float(a.mean()) if n else float("nan")
    if n == 0:
        return {"point": pt, "ci95": [float("nan"), float("nan")], "n": 0}
    means = _boot_means(a.astype(np.float64), n_boot, seed)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"point": pt, "ci95": [float(lo), float(hi)], "n": n}


def boot_diff(a: np.ndarray, b: np.ndarray, n_boot: int, seed: int) -> dict:
    n = len(a)
    pt = float(a.mean() - b.mean()) if n else float("nan")
    if n == 0:
        return {"point": pt, "ci95": [float("nan"), float("nan")], "n": 0, "half_width": float("nan")}
    d = a.astype(np.float64) - b.astype(np.float64)
    means = _boot_means(d, n_boot, seed)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"point": pt, "ci95": [float(lo), float(hi)], "n": n, "half_width": float((hi - lo) / 2)}


def _band(diff: dict) -> str:
    lo, hi = diff["ci95"]
    if lo != lo:
        return "NA"
    if lo > 0:
        return "ABOVE"
    if hi < 0:
        return "BELOW"
    return "NOT_SEPARATED"


def _label_perm_null_p95(a: np.ndarray, b: np.ndarray, n_perm: int, seed: int) -> float:
    """Label-permutation null for mean(a)-mean(b): per item, randomly swap a/b with p=0.5 (fixed
    seed), recompute the diff; the 95th percentile of |null diffs| is the noise floor the observed
    effect must clear to be distinguishable from arm-label shuffling."""
    n = len(a)
    if n == 0:
        return float("nan")
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_perm, dtype=np.float64)
    for i in range(n_perm):
        swap = rng.integers(0, 2, size=n).astype(bool)
        aa = np.where(swap, b, a)
        bb = np.where(swap, a, b)
        diffs[i] = aa.mean() - bb.mean()
    return float(np.percentile(np.abs(diffs), 95))


# =============================================================================================
# full run
# =============================================================================================
def run_full(gen: CandidateGenerator, smoke: bool, out_dir: str) -> dict:
    t0 = time.time()
    n_boot = 1500 if smoke else N_BOOT
    n_boot_paired = 500 if smoke else N_BOOT_PAIRED
    n_perm = 300 if smoke else N_PERM_NULL

    print("[minimal-pairs] scoring 32-item positive control", flush=True)
    mp = score_minimal_pairs(gen)
    print(f"[minimal-pairs] done n_decisive={mp['n_decisive']} n_contrast={mp['n_contrast']} "
         f"n_parse_fail={mp['n_parse_fail']} {time.time()-t0:.1f}s", flush=True)

    splits = ["dev"] if smoke else ["dev", "test"]
    max_sentences = 400 if smoke else None
    all_raw = []
    for split in splits:
        raw = load_qasrl_items(f"{split}.jsonl.gz", max_sentences=max_sentences)
        for it in raw:
            it["split"] = split
        all_raw.extend(raw)
        print(f"[qasrl-load] {split}: {len(raw)} raw items, {time.time()-t0:.1f}s", flush=True)

    aligned, n_mismatch = parse_and_align(gen, all_raw)
    # post-parse recipient filter: require a NOMINAL-tagged head token in the gold span.
    n_recip_pre = sum(1 for it in aligned if it["role_type"] == "recipient")
    aligned = [it for it in aligned
              if it["role_type"] != "recipient" or _head_in_span(it["pos"], tuple(it["span"])) is not None]
    n_recip_post = sum(1 for it in aligned if it["role_type"] == "recipient")
    print(f"[qasrl-align] {len(aligned)} aligned items (dropped {n_mismatch} tokenization mismatches, "
         f"recipient nominal-head filter {n_recip_pre}->{n_recip_post}), {time.time()-t0:.1f}s",
         flush=True)

    counts_by_role = {}
    for it in aligned:
        counts_by_role[it["role_type"]] = counts_by_role.get(it["role_type"], 0) + 1
    print(f"[qasrl-align] counts by role: {counts_by_role}", flush=True)

    vocab = sorted({lemma_verb(it["toks"][it["verb_idx"] - 1]) for it in aligned})
    twin_motion_fn, twin_comm_block = build_twin_classifiers(vocab, seed=TWIN_SEED)
    print(f"[twin] vocab={len(vocab)} lemmas, twin_comm_block_size={len(twin_comm_block)}", flush=True)

    recs_all: List[dict] = []
    for split in splits:
        for role in ("theme", "agent", "goal", "recipient"):
            key = unit_key(split, role)
            done = completed_units(out_dir)
            if key in done:
                recs_all.extend(load_units(out_dir)[key])
                print(f"[score] {key}: resumed from checkpoint", flush=True)
                continue
            subset = [it for it in aligned if it["split"] == split and it["role_type"] == role]
            recs = score_qasrl_items(subset, twin_motion_fn, twin_comm_block,
                                     seed=_crc_seed(RANDOM_SEED, split, role))
            record_unit(out_dir, key, recs)
            recs_all.extend(recs)
            print(f"[score] {key}: {len(recs)} items, {time.time()-t0:.1f}s", flush=True)

    def _vec(rows, arm):
        return np.array([r["correct"][arm] for r in rows], dtype=np.float64)

    def _role_stats(role_filter, seed_off):
        rows = [r for r in recs_all if role_filter(r)]
        n = len(rows)
        acc = {a: boot_mean(_vec(rows, a), n_boot, BOOT_SEED + seed_off + i)
              for i, a in enumerate(ARM_NAMES)}
        diff = boot_diff(_vec(rows, "SHARED"), _vec(rows, "INLINE"), n_boot_paired,
                         BOOT_SEED + seed_off + 50) if n else \
            {"point": float("nan"), "ci95": [float("nan"), float("nan")], "n": 0, "half_width": float("nan")}
        null_p95 = _label_perm_null_p95(_vec(rows, "SHARED"), _vec(rows, "INLINE"), n_perm,
                                        BOOT_SEED + seed_off + 99) if n else float("nan")
        return {"n": n, "acc": {a: acc[a]["point"] for a in ARM_NAMES},
               "acc_ci": {a: acc[a]["ci95"] for a in ARM_NAMES},
               "shared_minus_inline": diff, "band": _band(diff), "null_p95": null_p95}

    qasrl_strata = {
        "theme": _role_stats(lambda r: r["role_type"] == "theme", 0),
        "agent": _role_stats(lambda r: r["role_type"] == "agent", 10),
        "goal": _role_stats(lambda r: r["role_type"] == "goal", 20),
        "recipient": _role_stats(lambda r: r["role_type"] == "recipient", 30),
        "unified_4role": _role_stats(lambda r: True, 40),
        "downstream_goal_or_recipient": _role_stats(
            lambda r: r["role_type"] in ("goal", "recipient"), 60),
    }
    print(f"[qasrl-score] strata computed, {time.time()-t0:.1f}s", flush=True)

    # hand-audit sample: first 20 goal items (post-parse, post-filter) for manual eyeball.
    goal_sample = []
    for it in aligned:
        if it["role_type"] == "goal" and len(goal_sample) < 20:
            s, e = it["span"]
            goal_sample.append({"sentence": " ".join(it["toks"]), "span_text": " ".join(it["toks"][s:e])})

    allc = qasrl_strata["unified_4role"]
    downstream = qasrl_strata["downstream_goal_or_recipient"]
    verdict = ("SHARED_CI_SEPARATED_ABOVE_INLINE" if allc["band"] == "ABOVE"
              else ("SHARED_BELOW_OR_TIED_INLINE" if allc["band"] in ("BELOW", "NOT_SEPARATED")
                    else "UNSCORED"))

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | unified n={allc['n']} SHARED={allc['acc']['SHARED']:.4f} "
            f"INLINE={allc['acc']['INLINE']:.4f} TWIN={allc['acc']['TWIN']:.4f} "
            f"RANDOM={allc['acc']['RANDOM']:.4f} SHARED-INLINE={allc['shared_minus_inline']['point']:+.4f} "
            f"CI[{allc['shared_minus_inline']['ci95'][0]:+.4f},{allc['shared_minus_inline']['ci95'][1]:+.4f}] "
            f"{allc['band']} null_p95={allc['null_p95']:.4f} || "
            f"minimal-pair decisive SHARED={mp['decisive_acc']['SHARED']:.4f} "
            f"INLINE={mp['decisive_acc']['INLINE']:.4f} contrast SHARED={mp['contrast_acc']['SHARED']:.4f} "
            f"INLINE={mp['contrast_acc']['INLINE']:.4f} || "
            f"downstream(goal|recipient) SHARED={downstream['acc']['SHARED']:.4f} "
            f"INLINE={downstream['acc']['INLINE']:.4f} lift={downstream['shared_minus_inline']['point']:+.4f} "
            f"{downstream['band']}"
        ),
        "summary": f"{verdict}: SHARED vs INLINE predicate-argument dispatch, QA-SRL unified n={allc['n']}",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": ("smoke" if smoke else "full"),
        "anchor_name": ANCHOR_NAME, "n_boot": n_boot, "n_boot_paired": n_boot_paired, "n_perm": n_perm,
        "minimal_pairs": mp,
        "qasrl": {"splits": splits, "max_sentences_per_split": max_sentences,
                 "n_raw_items": len(all_raw), "n_aligned_items": len(aligned),
                 "n_tokenization_mismatch": n_mismatch, "counts_by_role": counts_by_role,
                 "n_recipient_pre_head_filter": n_recip_pre, "n_recipient_post_head_filter": n_recip_post,
                 "twin_vocab_size": len(vocab), "strata": qasrl_strata,
                 "goal_slice_hand_audit_sample": goal_sample},
        "scored_population": {
            "minimal_pairs_ids": sorted(it["id"] for it in load_minimal_pairs(GOLD_PATH)),
            "qasrl_units_jsonl": os.path.join(out_dir, "units.jsonl"),
            "qasrl_unit_keys": sorted(unit_key(s, r) for s in splits
                                      for r in ("theme", "agent", "goal", "recipient")),
        },
    }


# =============================================================================================
# GOAL DEEP-DIVE (coordinator-directed, 2026-08-28): isolate the mechanism behind the GOAL-role
# loss on QA-SRL's 'where' gold (see module docstring's DISK-VERIFIED DEVIATION section for the
# analogous precise_passive finding -- same discipline, applied to the goal-vs-location conflation
# the hand-audit surfaced). Three additive analyses; none touches agent/theme/goal/recipient/
# instrument/goal_belongs_to's existing values.
# =============================================================================================
def analyze_goal_motion_split(out_dir: str, splits: List[str], n_boot: int, n_perm: int) -> dict:
    """TASK 1: split the already-CHECKPOINTED QA-SRL goal-role units into MOTION vs STATIVE
    subsets by the GOLD VERB's lemma membership in the CURATED experiments.location_register.
    _MOTION_VERBS set ONLY -- independent of is_motion_verb's WordNet fallback and of SHARED's own
    routing decision (avoids circularity: the split must not be defined by the thing being tested).
    Reuses units.jsonl (score_qasrl_items already records 'verb_lemma' per item) -- NO re-parsing."""
    units = load_units(out_dir)
    recs = []
    for split in splits:
        key = unit_key(split, "goal")
        if key not in units:
            raise RuntimeError(f"missing checkpointed unit {key!r} in {out_dir} -- run the full "
                               f"pipeline (bare invocation) first")
        recs.extend(units[key])
    motion_recs = [r for r in recs if r["verb_lemma"] in _MOTION_VERBS]
    stative_recs = [r for r in recs if r["verb_lemma"] not in _MOTION_VERBS]

    def _stats(rows, seed_off):
        n = len(rows)
        if n == 0:
            return {"n": 0}
        vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in ARM_NAMES}
        acc = {a: boot_mean(vecs[a], n_boot, BOOT_SEED + seed_off + i) for i, a in enumerate(ARM_NAMES)}
        diff = boot_diff(vecs["SHARED"], vecs["INLINE"], n_boot, BOOT_SEED + seed_off + 50)
        null_p95 = _label_perm_null_p95(vecs["SHARED"], vecs["INLINE"], n_perm, BOOT_SEED + seed_off + 99)
        return {"n": n, "acc": {a: acc[a]["point"] for a in ARM_NAMES},
               "acc_ci": {a: acc[a]["ci95"] for a in ARM_NAMES},
               "shared_minus_inline": diff, "band": _band(diff), "null_p95": null_p95}

    return {"motion_subset": _stats(motion_recs, 1500), "stative_subset": _stats(stative_recs, 1600)}


def analyze_goal_or_location(gen: CandidateGenerator, splits: List[str], seed: int = RANDOM_SEED) -> dict:
    """TASK 2: does SHARED's goal-OR-location unified pick match/beat INLINE's plain goal pick on
    the FULL 'where' gold? Re-parses only the (small) goal-role item subset via load_qasrl_items/
    parse_and_align -- NOT the full ~40k-item pipeline (INLINE is unchanged, has no location
    concept, so its column here is identical to qasrl_strata['goal']['acc']['INLINE'])."""
    raw = []
    for split in splits:
        items = [it for it in load_qasrl_items(f"{split}.jsonl.gz") if it["role_type"] == "goal"]
        for it in items:
            it["split"] = split
        raw.extend(items)
    aligned, n_mismatch = parse_and_align(gen, raw)
    vocab = sorted({lemma_verb(it["toks"][it["verb_idx"] - 1]) for it in aligned})
    twin_motion_fn, twin_comm_block = build_twin_classifiers(vocab, seed=TWIN_SEED)

    rng_master = random.Random(_crc_seed(seed, "goal_or_location"))
    rows = []
    for it in aligned:
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        cands = _cands(pos)
        s, e = it["span"]

        def correct(pick):
            return int(pick is not None and (s < pick <= e))

        shared = extract_predicate_arguments(toks, pos, heads, v)
        inline = arm_inline(toks, pos, heads, v)
        twin = extract_predicate_arguments(toks, pos, heads, v, motion_fn=twin_motion_fn,
                                           comm_block=twin_comm_block)
        randm = arm_random(shared, cands, seed=rng_master.randint(0, 2**31 - 1))

        def unified(res):
            return res.get("goal") if res.get("goal") is not None else res.get("location")

        rows.append({
            "goal_only": {"SHARED": correct(shared.get("goal")), "INLINE": correct(inline.get("goal")),
                         "TWIN": correct(twin.get("goal")), "RANDOM": correct(randm.get("goal"))},
            "goal_or_location": {"SHARED": correct(unified(shared)), "INLINE": correct(unified(inline)),
                                 "TWIN": correct(unified(twin)), "RANDOM": correct(unified(randm))},
        })

    def _stats(field, seed_off):
        n = len(rows)
        if n == 0:
            return {"n": 0}
        vecs = {a: np.array([r[field][a] for r in rows], dtype=np.float64) for a in ARM_NAMES}
        acc = {a: boot_mean(vecs[a], N_BOOT, BOOT_SEED + seed_off + i) for i, a in enumerate(ARM_NAMES)}
        diff = boot_diff(vecs["SHARED"], vecs["INLINE"], N_BOOT_PAIRED, BOOT_SEED + seed_off + 50)
        null_p95 = _label_perm_null_p95(vecs["SHARED"], vecs["INLINE"], N_PERM_NULL, BOOT_SEED + seed_off + 99)
        return {"n": n, "acc": {a: acc[a]["point"] for a in ARM_NAMES},
               "acc_ci": {a: acc[a]["ci95"] for a in ARM_NAMES},
               "shared_minus_inline": diff, "band": _band(diff), "null_p95": null_p95}

    return {"n_raw": len(raw), "n_aligned": len(aligned), "n_mismatch": n_mismatch,
           "goal_only": _stats("goal_only", 1700), "goal_or_location": _stats("goal_or_location", 1800)}


def analyze_causedmotion_theme_attribution(gen: CandidateGenerator) -> dict:
    """TASK 3: of the minimal-pair items whose GOLD goal_belongs_to=='theme' (the caused-motion
    decisive construction), what fraction does SHARED correctly attribute to the theme (not the
    agent)? Reuses load_minimal_pairs/_find_verb_idx/extract_predicate_arguments -- no re-parsing
    beyond the already-fast 32-item minimal-pair pass."""
    items = [it for it in load_minimal_pairs(GOLD_PATH) if it.get("goal_belongs_to") == "theme"]
    n_correct = 0
    n_parse_fail = 0
    rows = []
    for it in items:
        cr = gen.generate(it["text"], extended=True)
        toks, pos, heads = cr.tokens, cr.pos, cr.heads
        v = _find_verb_idx(toks, pos, it["verb"])
        if v is None:
            n_parse_fail += 1
            rows.append({"id": it["id"], "parse_fail": True, "correct": False,
                        "predicted_goal_belongs_to": None})
            continue
        res = extract_predicate_arguments(toks, pos, heads, v)
        ok = res.get("goal_belongs_to") == "theme"
        n_correct += int(ok)
        rows.append({"id": it["id"], "parse_fail": False, "correct": bool(ok),
                    "predicted_goal_belongs_to": res.get("goal_belongs_to")})
    n = len(items)
    return {"n_items": n, "n_parse_fail": n_parse_fail, "n_correct": n_correct,
           "fraction_correct": (n_correct / n if n else float("nan")), "rows": rows}


# =============================================================================================
# self-test
# =============================================================================================
def self_test() -> dict:
    print("[self-test] starting", flush=True)
    gen = _default_generator()

    def parse(text):
        cr = gen.generate(text, extended=True)
        return cr.tokens, cr.pos, cr.heads

    # case 1: caused-motion moved-theme gate. SHARED must get it right; INLINE must get it WRONG.
    toks, pos, heads = parse("The guard shoved him to the ground .")
    v = _find_verb_idx(toks, pos, "shoved")
    assert v is not None, "verb not found: shoved"
    res = extract_predicate_arguments(toks, pos, heads, v)
    assert toks[res["theme"] - 1].lower() == "him", res
    assert toks[res["goal"] - 1].lower() == "ground", res
    assert res["goal_belongs_to"] == "theme", res
    inline_res = arm_inline(toks, pos, heads, v)
    assert inline_res["goal_belongs_to"] == "agent", inline_res
    print("  [PASS] caused-motion moved-theme gate: SHARED=theme, INLINE=agent (WRONG, as required)",
         flush=True)

    # case 2: ditransitive recipient, not goal.
    toks2, pos2, heads2 = parse("Tom handed the letter to Mary .")
    v2 = _find_verb_idx(toks2, pos2, "handed")
    assert v2 is not None
    res2 = extract_predicate_arguments(toks2, pos2, heads2, v2)
    assert res2["goal"] is None, res2
    assert toks2[res2["recipient"] - 1].lower() == "mary", res2
    print("  [PASS] ditransitive recipient (Mary), not goal", flush=True)

    # case 3: aspectual particle, no goal.
    toks3, pos3, heads3 = parse("The argument went on .")
    v3 = _find_verb_idx(toks3, pos3, "went")
    assert v3 is not None
    res3 = extract_predicate_arguments(toks3, pos3, heads3, v3)
    assert res3["goal"] is None, res3
    print("  [PASS] aspectual particle 'went on' -> no goal", flush=True)

    # case 4: passive swaps agent/patient.
    toks4, pos4, heads4 = parse("The vase was broken by the boy .")
    v4 = _find_verb_idx(toks4, pos4, "broken")
    assert v4 is not None
    res4 = extract_predicate_arguments(toks4, pos4, heads4, v4)
    assert toks4[res4["agent"] - 1].lower() == "boy", res4
    assert toks4[res4["theme"] - 1].lower() == "vase", res4
    print("  [PASS] passive swaps agent/patient (agent=boy, theme=vase)", flush=True)

    # case 5 (coordinator-directed addition, 2026-08-28): stative LOCATION, distinct from GOAL --
    # a non-motion, non-comm verb's locative PP is a LOCATION, and must NOT also fire as a goal.
    toks5, pos5, heads5 = parse("The workers stayed in the factory .")
    v5 = _find_verb_idx(toks5, pos5, "stayed")
    assert v5 is not None
    res5 = extract_predicate_arguments(toks5, pos5, heads5, v5)
    assert res5["goal"] is None, res5
    assert toks5[res5["location"] - 1].lower() == "factory", res5
    print("  [PASS] stative location 'stayed in the factory' -> location=factory, goal=None",
         flush=True)

    # robust_passive vs precise_passive VET (why SHARED uses precise_passive as the swap gate).
    n_robust_fp = 0
    for text, v_word in [("The guard hurried to the ground .", "hurried"),
                         ("Tom handed the letter to Mary .", "handed"),
                         ("The old man walked to the door .", "walked")]:
        tt, pp2, hh = parse(text)
        vv = _find_verb_idx(tt, pp2, v_word)
        if robust_passive(tt, pp2, vv) and not precise_passive(tt, pp2, vv):
            n_robust_fp += 1
    assert n_robust_fp >= 2, (
       f"expected robust_passive to over-fire on active sentences (measured VET), got {n_robust_fp}/3")
    print(f"  [PASS] robust_passive over-fires on {n_robust_fp}/3 active hand sentences "
         f"(confirms the precise_passive design deviation documented in the module docstring)",
         flush=True)

    # TWIN must differ from SHARED (recipient -> goal misroute under the permuted verb class).
    twin_motion_fn, twin_comm_block = build_twin_classifiers(
        [lemma_verb(w) for w in ("hand", "shove", "go", "point", "break", "carry", "sweep")],
        seed=TWIN_SEED)
    twin_res2 = extract_predicate_arguments(toks2, pos2, heads2, v2, motion_fn=twin_motion_fn,
                                            comm_block=twin_comm_block)
    assert twin_res2 != res2, (twin_res2, res2)
    print(f"  [PASS] TWIN differs from SHARED on 'Tom handed the letter to Mary.' "
         f"(SHARED recipient={toks2[res2['recipient']-1] if res2['recipient'] else None}, "
         f"TWIN recipient={toks2[twin_res2['recipient']-1] if twin_res2['recipient'] else None}, "
         f"TWIN goal={toks2[twin_res2['goal']-1] if twin_res2['goal'] else None})", flush=True)

    # optional cross-check: parse_goal_extraction agrees there IS a nominal-request/purpose reading
    # available on a sentence it covers (diagnostic only, not asserted -- different construction class).
    pg = parse_extract_goal("She asked for a window seat .")
    print(f"  [diagnostic] parse_extract_goal cross-check: {pg}", flush=True)

    # bootstrap sanity.
    a = np.array([1, 1, 1, 0.0])
    b = np.array([0, 0, 1, 0.0])
    d = boot_diff(a, b, 500, 1)
    assert abs(d["point"] - 0.5) < 1e-9, d
    print("[self-test] PASS", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "SELFTEST_PASS",
           "elapsed_s": 0.0, "run_mode": "self_test", "anchor_name": ANCHOR_NAME}


def _write(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--mode", choices=["full", "smoke"], default=None)
    p.add_argument("--goal-deep-dive", action="store_true", dest="goal_deep_dive",
                  help="coordinator-directed addition: append motion/stative goal split + "
                       "goal-or-location unified metric + caused-motion theme-attribution to an "
                       "EXISTING full-run metrics.json (reuses checkpointed units where possible; "
                       "requires a prior bare/full run in data/exp_shared_predarg_frontend_v1/).")
    args = p.parse_args()
    smoke = bool(args.smoke) or (args.mode == "smoke")
    suffix = "_selftest" if args.self_test else ("_smoke" if smoke else "")
    out_dir = OUTPUT_DIR + suffix

    if args.goal_deep_dive:
        existing_path = os.path.join(OUTPUT_DIR, "metrics.json")
        if not os.path.exists(existing_path):
            raise RuntimeError(f"{existing_path} not found -- run the full pipeline (bare "
                              f"invocation) first; --goal-deep-dive ADDS to it, does not replace it")
        with open(existing_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        splits = metrics["qasrl"]["splits"]
        gen = _default_generator()
        t0 = time.time()
        motion_split = analyze_goal_motion_split(OUTPUT_DIR, splits, n_boot=N_BOOT, n_perm=N_PERM_NULL)
        print(f"[goal-deep-dive] motion/stative split (checkpoint reuse, no re-parse) done, "
             f"{time.time()-t0:.1f}s", flush=True)
        goal_or_loc = analyze_goal_or_location(gen, splits)
        print(f"[goal-deep-dive] goal-or-location (re-parsed goal subset, n_raw="
             f"{goal_or_loc['n_raw']}) done, {time.time()-t0:.1f}s", flush=True)
        cm_theme = analyze_causedmotion_theme_attribution(gen)
        print(f"[goal-deep-dive] caused-motion theme-attribution done, {time.time()-t0:.1f}s",
             flush=True)
        metrics["goal_deep_dive"] = {
            "motion_vs_stative_split": motion_split,
            "goal_or_location": goal_or_loc,
            "causedmotion_theme_attribution": cm_theme,
            "computed_elapsed_s": round(time.time() - t0, 2),
        }
        _write(OUTPUT_DIR, metrics)
        print(f"[goal-deep-dive] wrote {existing_path} with goal_deep_dive section, "
             f"motion_n={motion_split['motion_subset'].get('n')} "
             f"stative_n={motion_split['stative_subset'].get('n')} "
             f"cm_theme_fraction={cm_theme['fraction_correct']:.4f}", flush=True)
        return

    try:
        if args.self_test:
            metrics = self_test()
        else:
            gen = _default_generator()
            metrics = run_full(gen, smoke=smoke, out_dir=out_dir)
        _write(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
        print(metrics["verdict_msg"], flush=True)
    except Exception as e:  # noqa: BLE001
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
               "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _write(out_dir, diag)
        raise


if __name__ == "__main__":
    main()
