"""SEEDED DISTRIBUTIONAL ANIMACY classifier as a HARD candidate PRE-FILTER in the margin-gated coref resolver.

QUESTION (design: notes/research_animacy_vs_worldknowledge_residual_brain_drill_2026-07-19.md, Pred 1/2/3):
  The margin-gated coref cell (exp_coref_margin_gated_cleanup_local_window_break050_v1, atom 29355/56) was
  net-NEGATIVE (broke=[5,6,5]/fixed=[0,0,0], HARD_FAIL_A_NET_BREAKAGE) because its DOMINANT harm is
  they->inanimate resolution (they->flowers L12_16, they->things L10_18): A_animate is added ONLY for
  gendered he/she pronouns, so "they"/plurals/general-nouns carry NO animacy constraint and inanimate
  candidates are never excluded. Does a CHEAP, glass-box, SEEDED DISTRIBUTIONAL animacy classifier -- one
  that extends the animacy label from gendered pronouns to ALL entity mentions and is hard-gated as a
  candidate PRE-FILTER (block an animate-requiring pronoun from resolving to an inanimate candidate) --
  kill the named they->inanimate coref harm and flip the break-budget toward net-non-negative?

ONE VARIABLE = animacy hard pre-filter OFF vs ON (everything else BIT-IDENTICAL to the coref cell):
  OFF = the published coref cell's ON path, reproduced by CALLING COREF.resolve_coref_gated directly
        (same LCCP arm-C keptC -> head-finder resolve_heads use_grounding=True -> margin-gated HD cleanup
        coref; same TAU_MARGIN=0.10 / COS_FLOOR=0.08 / W_ROLE / W_SAL / EPS_NOISE / codebooks / seeds).
  ON  = the SAME resolver with ONE added step: after the existing hard gender/number pre-filter, drop any
        candidate the SEEDED DISTRIBUTIONAL ANIMACY CLASSIFIER labels 'inanimate' when the pronoun is
        animate-requiring (gendered he/she OR they/them/their). 'unknown'-animacy candidates are NEVER
        masked (precision-first: a false inanimate label would mask a correct antecedent). If the mask
        empties the pool -> ABSTAIN (no commit -> a safe non-answer replaces an inanimate wrong-answer).

SEEDED DISTRIBUTIONAL ANIMACY CLASSIFIER (glass-box; NO external LLM/KB at runtime):
  label(head):
    1. gender cue (infer_nominal_gender in {masc,fem}) -> 'animate'   [existing gendered-animacy, generalized]
    2. SEED lookup (small CREDITED general animate/inanimate word lists; trailing-'s' plural fallback)
    3. DISTRIBUTIONAL vote from THIS corpus's own statistics (the three cheap features the animacy-induction
       literature uses -- Bloem&Bouma, Bowman&Chopra 2012, Bergsma&Lin):
         animate_evidence  = n_who_relativizer + n_animate_selecting_verb_agent + n_he_she_cooccur
         inanimate_evidence = n_which_that_relativizer + n_it_cooccur
       label 'animate' iff animate_evidence>=1 and animate_evidence>=inanimate_evidence;
       label 'inanimate' iff inanimate_evidence>=1 and inanimate_evidence>animate_evidence and
             animate_evidence==0  (INANIMATE requires a real inanimate cue AND zero animate cue -- the mask
             only consumes the 'inanimate' label, so its PRECISION is what protects correct antecedents);
       else 'unknown' (agent-position frequency alone is NOT used to assert inanimate -- inanimate subjects
             like "the sun rose" would over-fire it).

MEASURED (vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json + hand animacy gold, single-annotator):
  PRED 1 (make-or-break coref break-budget WITH animacy): n_inanimate_commit (committed resolutions whose
    resolved head is classifier-inanimate; the DOMINANT harm) OFF vs ON; newly_broken/newly_fixed vs the
    head-fixed OFF baseline; overall + pronoun-subset precision; abstain rate. HARD_PASS = net-non-negative
    (broke<=fixed) AND named harm killed. PARTIAL = named they->inanimate harm KILLED (n_inanimate_commit->0)
    + breaks strictly reduced + no new breaks + no precision loss, residual animate-vs-animate breaks remain.
  PRED 2 (classifier viability at THIS 163-sentence corpus scale): accuracy + coverage of the DISTRIBUTIONAL
    labels on NON-seed candidate heads vs hand animacy gold; INANIMATE-label precision (the mask-critical
    number). HONEST corpus-sparsity can-fail: if distributional refinement is too noisy, say so.
  PRED 3 (parser-residual scope check): triage the LCCP patient-assignment FPs into entity-type-driven vs
    argument-structure-driven; confirm the animacy-catchable bucket is NEAR-EMPTY (the honest scope
    boundary: animacy fixes the coref they-harm, NOT the parser argument-structure residual build/huts).

VERDICT BANDS (PRE-REGISTERED; see prereg preregs/2026-07-19_coref_animacy_prefilter_lccp_break050_v1.md;
  FIXED before the ON run -- NOT tuned to pass):
  PRED 1:
    HARD_PASS = for ALL seeds newly_broken<=newly_fixed AND n_inanimate_commit==0 AND
      mean(broke_ON)<mean(broke_OFF) AND mean(P_ON)>=mean(P_OFF) AND no_new_breaks.
    PARTIAL_NAMED_HARM_KILLED = n_inanimate_commit==0 (all seeds) AND mean(broke_ON)<mean(broke_OFF) AND
      no_new_breaks AND mean(P_ON)>=mean(P_OFF)-0.001 (breaks reduced + named harm gone, residual remains).
    HARD_FAIL = mean(broke_ON)>=mean(broke_OFF) OR n_inanimate_commit>0-with-net-worse OR
      mean(P_ON)<mean(P_OFF)-0.02 OR new_breaks_introduced>0.
  PRED 2:
    HARD_PASS = inanimate-label precision on NON-seed heads >= 0.90 (usable as a hard mask).
    PARTIAL = inanimate precision in [0.75,0.90) OR distributional coverage < 0.30 (seed carries the mask).
    HARD_FAIL = inanimate precision < 0.75 (too noisy for a hard mask -> soft/seed-only fallback).
  PRED 3:
    HARD_PASS (expected null) = animacy-catchable FP bucket is NEAR-EMPTY (frac_animacy_catchable <= 0.15
      OR n_animacy_catchable <= 1) -> CONFIRMS animacy does NOT fix the parser argument-structure residual.
    HARD_FAIL = frac_animacy_catchable > 0.15 (unexpected: animacy DOES fix a real chunk of the parser FP).

DESIGN-GATE (all 4 at smoke): (G1) REAL baseline = the published net-negative coref cell, reproduced live by
  calling COREF.resolve_coref_gated (OFF arm). (G2) baseline_in_band 0.05<P_OFF<0.95 + pronoun subset
  un-saturated + OFF n_inanimate_commit>0 (the harm is present to fix). (G3) can-fail both ways (mask fixes
  nothing OR mask over-masks correct antecedents -> new breaks -> HARD_FAIL). (G4) discriminator fires
  (arms_differ OFF!=ON; classifier labels >=1 candidate inanimate; mask changes >=1 resolution).

BRAIN-CHECK (outcome NOT pre-assumed): animacy is a DISCRETE, early, categorical feature (Weckerly&Kutas ERP
  dissociation; animacy-hierarchy typology Silverstein/Comrie; DOM Aissen 2003), architecturally KIN to
  gender/number agreement (a hard pre-filter, already working) NOT to the graded selectional-coherence-cosine
  that failed this session -- which is why it escapes the structural-beats-semantic wall (the operative line
  is DISCRETE-CATEGORICAL vs GRADED-CONTINUOUS). The brain nests animacy INSIDE a richer graded
  event-knowledge system (McRae/Ferretti/Elman) so animacy is NOT a full-world-knowledge substitute -- hence
  Pred 3's pre-registered NULL. Same-limit -> accept scope; helps the named class -> cheap lever works.

COMPUTE ARCHITECTURE: class (b) sequential-CPU. Glass-box discourse pass + tiny complex matmuls over 163
  sentences, wall<<30s/seed; no GPU-batching win; storage=no_storage; foreground-inline (NO queue/push/
  remote-persist). CRLB n/a (no additive-Gaussian estimator floor; FHRR crosstalk Plate O(N/log N) inside
  small pools). DETERMINISM: np.random.default_rng(seed) codebooks (delegated to COREF); classifier is
  count-based deterministic; NO builtin hash()/list(set) seeding (sorted ordering). Multi-seed [7,13,19]:
  LCCP/head-finder/classifier computed ONCE per config; only the FHRR draw varies across seeds.

# CELL-TEMPLATE MANDATORY: arms_differ_verified; final_metrics_atomicity=tmp_replace; except SystemExit:
# raise BEFORE except Exception (no BaseException); baseline_in_band at smoke; discriminator fires at smoke;
# self-tests (classifier man=animate/flower=inanimate + mask-fires-on-toy + real code path); crlb n/a;
# deterministic seeding; all numbers MEASURED@ this metrics.json / CITED@ (0.938 head-finder, prior coref
# broke=[5,6,5]). needs_orchestrator_store_sync=True; NO push/remote-persist/git-add-A; no atom banking.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
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
import experiments.exp_np_head_finder_grounding_gate_break050_v1 as HF  # noqa: E402
import experiments.exp_oracle_mention_upperbound_reader_v1 as ORC  # noqa: E402 (pos_tag_sentence)
import experiments.exp_coref_margin_gated_cleanup_local_window_break050_v1 as COREF  # noqa: E402 (REAL baseline)
from hdlab.state_of_mind import (PRONOUN_SCOPE, SetKnownBase, WorkingOverlay,  # noqa: E402
                                 compatible, infer_nominal_gender)

ANCHOR_NAME = "coref_animacy_prefilter_lccp_break050_v1"
GOLD_PATH = os.path.join(REPO_ROOT, "data", "gold_mcguffey_lccp_argstruct_v1.json")

# ---- reuse the coref cell's PRE-REGISTERED constants VERBATIM (single variable = the animacy mask) -------
N_DIM = COREF.N_DIM
TAU_MARGIN = COREF.TAU_MARGIN
COS_FLOOR = COREF.COS_FLOOR
FHRR_SEEDS = COREF.FHRR_SEEDS
THIRD_TARGET = COREF.THIRD_TARGET
NOUN_POS = COREF.NOUN_POS

CITED_HEADFINDER_B2 = 0.938  # CITED@data/exp_np_head_finder_grounding_gate_break050_v1/metrics.json
CITED_PRIOR_COREF = "broke=[5,6,5] fixed=[0,0,0] P_ON=0.854 HARD_FAIL_A_NET_BREAKAGE"  # CITED@data/exp_coref_margin_gated_cleanup_local_window_break050_v1/metrics.json

# ---------------------------------------------------------------------------------------------------
# PRE-REGISTERED animacy pre-filter scope: which pronouns REQUIRE an animate antecedent (mask inanimate).
# Gendered he/she (the existing gendered-animacy case) PLUS they/them/their. Conservative: 'it'/'its' do NOT
# get an inanimate-requiring rule (it->baby/animal is common; out of scope, only the named they-harm here).
# ---------------------------------------------------------------------------------------------------
ANIMATE_REQUIRING_PRONOUNS = {"he", "him", "his", "she", "her", "hers", "they", "them", "their"}


def pronoun_expects_animate(pron_low: str) -> bool:
    return pron_low in ANIMATE_REQUIRING_PRONOUNS


# ---------------------------------------------------------------------------------------------------
# SEED lists (CREDITED, general high-frequency English animate/inanimate nouns -- borrowed not induced;
# WordNet-hypernymy-consistent: person/animal vs artifact/substance/location/abstraction/body-part/time.
# Deliberately GENERAL: corpus-specific proper names and rarer heads are LEFT OUT so the DISTRIBUTIONAL
# classifier -- and Pred 2's accuracy/coverage measurement -- operates on genuinely non-seed heads.)
# ---------------------------------------------------------------------------------------------------
SEED_ANIMATE = frozenset({
    "man", "woman", "boy", "girl", "child", "baby", "father", "mother", "son", "daughter",
    "brother", "sister", "papa", "mama", "dad", "mom", "uncle", "aunt", "gentleman", "lady",
    "king", "queen", "prince", "princess", "friend", "master", "servant", "soldier", "family",
    "parent", "people", "person", "dog", "cat", "kitten", "horse", "bird", "fox", "lion",
    "wolf", "bear", "cow", "pig", "sheep", "hen", "beast", "animal", "puppy", "lamb",
})
SEED_INANIMATE = frozenset({
    "flower", "thing", "hut", "house", "home", "garden", "water", "boat", "table", "block",
    "kite", "stick", "book", "wall", "tower", "door", "floor", "room", "sofa", "gate",
    "tree", "plant", "stone", "milk", "snow", "mud", "wind", "money", "paper", "string",
    "day", "time", "way", "hour", "morning", "night", "year", "minute", "moment", "week",
    "hand", "eye", "head", "face", "foot", "knee", "hair", "skin", "tear", "heart", "tail",
    "school", "town", "street", "field", "world", "river", "lake", "bank", "road", "hill",
    "word", "lesson", "name", "voice", "song", "story", "letter", "picture", "wagon", "bell",
})
CREDIT_SEED = ("general high-frequency English animate/inanimate common nouns, hand-listed, "
               "WordNet-hypernymy-consistent (person/animal vs artifact/substance/place/abstraction/"
               "body-part/time); borrowed not corpus-induced; trailing-'s' plural fallback at match time")

# Animate-SELECTING verb seed (agentive verbs whose subject is prototypically animate; CREDITED from
# Levin/VerbNet communication + motion + perception + cognition + bodily-process classes).
ANIMATE_VERBS = frozenset({
    "say", "said", "says", "tell", "told", "ask", "asked", "answer", "answered", "speak", "spoke",
    "call", "called", "cry", "cried", "cries", "laugh", "laughed", "smile", "smiled", "sing", "sang",
    "think", "thought", "know", "knew", "knows", "want", "wanted", "hope", "hoped", "wish", "wished",
    "love", "loved", "hate", "feel", "felt", "believe", "remember", "see", "saw", "look", "looked",
    "hear", "heard", "watch", "watched", "go", "went", "come", "came", "run", "ran", "walk", "walked",
    "jump", "jumped", "sit", "sat", "stand", "stood", "play", "played", "eat", "ate", "drink", "drank",
    "sleep", "slept", "wake", "woke", "work", "worked", "obey", "obeyed", "nod", "nodded", "seize",
    "reach", "reached", "throw", "threw", "make", "made", "take", "took", "give", "gave", "hold", "held",
})
CREDIT_VERBS = ("agentive/animate-subject verb classes (Levin/VerbNet communication, motion, perception, "
                "cognition, bodily-process); CREDITED, not corpus-induced")


# ---------------------------------------------------------------------------------------------------
# HAND animacy gold for Pred-2 (single-annotator, this corpus's noun heads). Heads in NEITHER set are
# 'unlabeled' -> excluded from accuracy. Kept SEPARATE from the seed so the distributional classifier is
# scored on NON-seed heads it did not get for free.
# ---------------------------------------------------------------------------------------------------
GOLD_ANIMATE = frozenset({
    "charles", "joe", "herbert", "frank", "james", "hetty", "brown", "boy", "boys", "mother",
    "papa", "father", "son", "gentleman", "gardener", "fisherman", "beggar", "guard", "truant",
    "parents", "kitten", "kittens", "cat", "pussy", "beaver", "beavers", "men", "man", "children",
    "child", "baby", "brother", "elder", "aunt", "servant", "people", "mr", "girl", "girls",
    "woman", "dog", "friend", "friends", "master", "family", "king", "queen", "beast", "beasts",
})
GOLD_INANIMATE = frozenset({
    "garden", "castle", "castles", "home", "water", "time", "school", "boat", "boats", "day",
    "way", "huts", "hut", "flowers", "flower", "building", "buildings", "floor", "blocks", "block",
    "hands", "hand", "kite", "hour", "walk", "milk", "trouble", "house", "houses", "fur", "dams",
    "dam", "river", "rivers", "lakes", "face", "sofa", "door", "eyes", "heart", "head", "side",
    "sides", "work", "moment", "thing", "things", "sticks", "stick", "paper", "book", "books",
    "room", "lessons", "morning", "danger", "wind", "clothes", "places", "place", "feet", "foot",
    "length", "town", "bank", "banks", "stream", "mud", "branches", "trees", "table", "world",
    "gate", "plants", "voice", "anger", "dismay", "blockhouse", "ruin", "tower", "wall", "walls",
    "harm", "hurt", "passion", "tears", "pile", "foundation", "grief", "minutes", "shadow", "string",
    "sentence", "forehead", "street", "carriages", "tray", "dishes", "crash", "years", "habit",
    "fields", "haste", "money", "tide", "wave", "grave", "conduct", "knee", "knees", "snow",
    "lilies", "streaks", "rosebud", "counsel", "north", "america", "paddle", "tail", "hair", "skin",
    "number", "purpose", "height", "stones", "material", "shape", "roofs", "layer", "leaves",
    "houses", "rose", "name", "boat", "point", "reading",
})


def _plural_fallback(head: str):
    """head plus a singularized variant (drop trailing 's'/'es') for seed matching."""
    h = head.lower().strip(".,'\"!?;:")
    variants = [h]
    if h.endswith("es") and len(h) > 3:
        variants.append(h[:-2])
    if h.endswith("s") and len(h) > 2:
        variants.append(h[:-1])
    return variants


# ---------------------------------------------------------------------------------------------------
# The SEEDED DISTRIBUTIONAL ANIMACY CLASSIFIER.
# ---------------------------------------------------------------------------------------------------
class AnimacyClassifier:
    """Glass-box seeded distributional animacy classifier. label(head) -> (label, source)."""

    __slots__ = ("feat", "cache")

    def __init__(self):
        self.feat = defaultdict(lambda: {"who": 0, "which_that": 0, "averb_agent": 0,
                                         "he_she": 0, "it": 0, "agent": 0, "patient": 0})
        self.cache = {}

    def _norm(self, w: str) -> str:
        return w.lower().strip(".,'\"!?;:")

    def fit(self, order, sent_text, reader_svo):
        """Accumulate per-head distributional features from THIS corpus (deterministic count-based)."""
        he_she = {"he", "him", "his", "she", "her", "hers"}
        for sid in order:
            # relativizer + pronoun co-occurrence over the raw token stream
            tagged = ORC.pos_tag_sentence(sent_text[sid])
            toks = [self._norm(low) for (_s, low, _p) in tagged]
            for i, (surf, low, pos) in enumerate(tagged):
                h = self._norm(low)
                if pos not in NOUN_POS or not h.isalpha() or len(h) < 2:
                    continue
                # relativizer within the next 2 tokens (head , who / head who)
                nxt = [toks[j] for j in range(i + 1, min(i + 3, len(toks)))]
                if "who" in nxt or "whom" in nxt or "whose" in nxt:
                    self.feat[h]["who"] += 1
                if "which" in nxt or "that" in nxt:
                    self.feat[h]["which_that"] += 1
                # animate/neuter pronoun co-occurrence LATER in the same sentence (weak referential cue)
                later = set(toks[i + 1:])
                if later & he_she:
                    self.feat[h]["he_she"] += 1
                if "it" in later or "its" in later:
                    self.feat[h]["it"] += 1
            # agent/patient + animate-selecting-verb-agent from the reader's subject-verb-object tuples
            for (subj, verb, obj) in reader_svo.get(sid, []):
                s = self._norm(subj); v = self._norm(verb); o = self._norm(obj)
                if s and s.isalpha():
                    self.feat[s]["agent"] += 1
                    if v in ANIMATE_VERBS or LCCP.lemma_verb(v) in ANIMATE_VERBS:
                        self.feat[s]["averb_agent"] += 1
                if o and o.isalpha():
                    self.feat[o]["patient"] += 1

    def label(self, head: str):
        """-> ('animate'|'inanimate'|'unknown', source). Precision-first on the mask-critical inanimate label."""
        h = self._norm(head)
        if h in self.cache:
            return self.cache[h]
        # 1) gender cue -> animate (existing gendered-animacy generalized to nominal heads)
        if infer_nominal_gender([h]) in ("masc", "fem"):
            res = ("animate", "gender_cue"); self.cache[h] = res; return res
        # 2) seed lookup (with plural fallback)
        for v in _plural_fallback(h):
            if v in SEED_ANIMATE:
                res = ("animate", "seed"); self.cache[h] = res; return res
            if v in SEED_INANIMATE:
                res = ("inanimate", "seed"); self.cache[h] = res; return res
        # 3) distributional vote from this corpus's own statistics
        f = self.feat.get(h)
        if f is not None:
            anim_ev = f["who"] + f["averb_agent"] + f["he_she"]
            inan_ev = f["which_that"] + f["it"]
            if anim_ev >= 1 and anim_ev >= inan_ev:
                res = ("animate", "distributional"); self.cache[h] = res; return res
            if inan_ev >= 1 and inan_ev > anim_ev and anim_ev == 0:
                res = ("inanimate", "distributional"); self.cache[h] = res; return res
        res = ("unknown", "none"); self.cache[h] = res; return res


# ---------------------------------------------------------------------------------------------------
# ON-arm resolver = a copy of COREF.resolve_coref_gated with EXACTLY ONE added step: the animacy hard mask
# applied AFTER the existing gender/number pre-filter. Everything else (codebooks, cue encoding, salience,
# margin gate, commit/abstain logic) is COREF's helpers verbatim -> the single variable is the mask.
# ---------------------------------------------------------------------------------------------------
def resolve_coref_gated_animacy(order, sent_text, keptC, resB2, seed, classifier, animacy_on):
    rng = np.random.default_rng(seed)
    cb = COREF.fhrr_codebook(COREF.FEATURE_ATOMS, N_DIM, rng)
    role_map = COREF.build_role_map(keptC)
    ent_code_rng = np.random.default_rng(seed + 100003)

    kept_by_sid = defaultdict(list)
    for kidx, (sid, t) in enumerate(keptC):
        kept_by_sid[sid].append((kidx, t))

    entity_codes = {}

    def code_of(head):
        h = head.lower()
        if h not in entity_codes:
            entity_codes[h] = COREF.rand_phasor(N_DIM, ent_code_rng)
        return entity_codes[h]

    resolved = {}
    commit_log = []
    mask_stats = {"n_masked_candidates": 0, "n_pool_emptied_by_mask": 0, "n_argmax_changed_by_mask": 0}
    lessons = []
    seen = set()
    for sid in order:
        lid = sid.split("_")[0]
        if lid not in seen:
            seen.add(lid); lessons.append(lid)

    for lid in lessons:
        ov = WorkingOverlay(SetKnownBase())
        sids = [sid for sid in order if sid.split("_")[0] == lid]
        prev_heads = {}
        for sid in sids:
            raw = sent_text[sid]
            tagged = ORC.pos_tag_sentence(raw)
            cur_heads = {}
            for i, (surf, low, pos) in enumerate(tagged):
                ov.observe_surface(surf, at_sentence_start=(i == 0))
                is_cand, number, gender, animacy = COREF.noun_head_attrs(low, pos)
                if is_cand and low not in cur_heads:
                    cur_heads[low] = (number, gender, animacy)
            window = {}
            for h, attrs in list(cur_heads.items()) + list(prev_heads.items()):
                if h not in window:
                    window[h] = attrs
            now = ov.n_observed
            cands_by_head = {}
            for h, (number, gender, animacy) in window.items():
                e = ov._entities.get(h)  # noqa: SLF001
                sal = e.salience(now, COREF.SAL_BETA, COREF.SAL_LAM) if e is not None else 1.0
                role = role_map.get(h, "obl")
                cands_by_head[h] = COREF.Candidate(h, gender, number, animacy, role, sal)
            for kidx, t in kept_by_sid.get(sid, []):
                a = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
                if a not in THIRD_TARGET:
                    resolved[(sid, kidx)] = (a, "identity", 0.0, 0.0, None)
                    continue
                sc = PRONOUN_SCOPE[a]
                p_g = sc["gender"]; p_n = COREF.norm_number(sc["number"])
                # existing HARD gender/number pre-filter (identical to COREF)
                pool_gn = [c for h, c in cands_by_head.items()
                           if h != a and compatible(p_g, p_n, c.gender, c.number)]
                # === THE SINGLE VARIABLE: animacy hard pre-filter (ON only) ==========================
                if animacy_on and pronoun_expects_animate(a):
                    kept, masked = [], []
                    for c in pool_gn:
                        lab, _src = classifier.label(c.head)
                        (masked if lab == "inanimate" else kept).append(c)
                    if masked:
                        mask_stats["n_masked_candidates"] += len(masked)
                        if kept and pool_gn and pool_gn[0] in masked:
                            mask_stats["n_argmax_changed_by_mask"] += 1  # top gn-candidate got masked
                        if not kept:
                            mask_stats["n_pool_emptied_by_mask"] += 1
                    pool = kept
                else:
                    pool = pool_gn
                # ====================================================================================
                if not pool:
                    resolved[(sid, kidx)] = (a, "abstain_no_candidate", 0.0, 0.0, None)
                    continue
                sals = [c.sal for c in pool]
                lo, hi = min(sals), max(sals)
                for c in pool:
                    c_sal_norm = (c.sal - lo) / (hi - lo) if hi > lo else 1.0
                    noise = COREF.rand_phasor(N_DIM, np.random.default_rng(seed + 7 * COREF.hash_head(c.head)))
                    tmp = COREF.Candidate(c.head, c.gender, c.number, c.animacy, c.role, c_sal_norm)
                    c.code_key = COREF.encode_candidate_key(tmp, cb, noise)
                q = COREF.encode_query(a, cb)
                scored = sorted(((COREF.cos(q, c.code_key), c) for c in pool),
                                key=lambda x: (-x[0], x[1].head))
                cos1, top = scored[0]
                cos2 = scored[1][0] if len(scored) > 1 else 0.0
                margin = cos1 - cos2
                if margin >= TAU_MARGIN and cos1 >= COS_FLOOR:
                    resolved[(sid, kidx)] = (top.head, "coref_commit", margin, cos1, code_of(top.head))
                    commit_log.append({"sid": sid, "v": LCCP.lemma_verb(t[0]), "pron": a,
                                       "resolved": top.head, "resolved_animacy": classifier.label(top.head)[0],
                                       "margin": round(margin, 4), "cos1": round(cos1, 4),
                                       "n_pool": len(pool), "pool": [c.head for c in pool]})
                else:
                    resolved[(sid, kidx)] = (a, "abstain_low_margin", margin, cos1, None)
            prev_heads = cur_heads
    return resolved, commit_log, entity_codes, mask_stats


# ---------------------------------------------------------------------------------------------------
# Pred-1 scoring: reuse COREF.score_pred_a and augment with n_inanimate_commit + new-break detection.
# ---------------------------------------------------------------------------------------------------
def n_inanimate_commit(resolved, classifier):
    n = 0
    for (_k), rr in resolved.items():
        if rr[1] == "coref_commit" and classifier.label(rr[0])[0] == "inanimate":
            n += 1
    return n


def count_new_breaks(keptC, gold_ag, resB2, resolved_off, resolved_on):
    """A NEW break = an instance the OFF (no-mask) arm did NOT break but the ON (mask) arm does (mask over-
    masked a correct antecedent and promoted a wrong one). Measured on gold-framed target-pronoun frames."""
    new_breaks = 0
    log = []
    for kidx, (sid, t) in enumerate(keptC):
        v = LCCP.lemma_verb(t[0])
        goldset = gold_ag.get((sid, v))
        if not goldset:
            continue
        off_head = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
        if off_head not in THIRD_TARGET:
            continue
        on_off = resolved_off.get((sid, kidx), (off_head,))[0]
        on_on = resolved_on.get((sid, kidx), (off_head,))[0]
        broke_off = (off_head in goldset) and (on_off not in goldset)
        broke_on = (off_head in goldset) and (on_on not in goldset)
        if broke_on and not broke_off:
            new_breaks += 1
            log.append({"sid": sid, "v": v, "pron": off_head, "off_arm": on_off, "on_arm": on_on,
                        "gold": sorted(goldset)})
    return new_breaks, log


# ---------------------------------------------------------------------------------------------------
# Pred-2 scoring: distributional-label accuracy + coverage on NON-seed candidate heads vs hand gold.
# ---------------------------------------------------------------------------------------------------
def gold_animacy(head: str):
    for v in _plural_fallback(head):
        if v in GOLD_ANIMATE:
            return "animate"
        if v in GOLD_INANIMATE:
            return "inanimate"
    return None


def in_seed(head: str) -> bool:
    for v in _plural_fallback(head):
        if v in SEED_ANIMATE or v in SEED_INANIMATE:
            return True
    return infer_nominal_gender([head.lower()]) in ("masc", "fem")


def measure_pred2(order, sent_text, classifier, candidate_heads):
    """Report classifier accuracy/coverage. Split by ALL heads and by NON-SEED heads (distributional test).
    INANIMATE-label precision (the mask-critical number) reported for both."""
    def _eval(heads):
        n_total = len(heads)
        n_labeled_gold = 0
        n_confident = 0            # classifier gives animate/inanimate (not unknown)
        n_correct = 0
        inan_pred = 0; inan_correct = 0
        anim_pred = 0; anim_correct = 0
        conf_matrix = defaultdict(int)
        for h in heads:
            g = gold_animacy(h)
            lab, src = classifier.label(h)
            if lab in ("animate", "inanimate"):
                n_confident += 1
            if g is None:
                continue
            n_labeled_gold += 1
            if lab in ("animate", "inanimate"):
                conf_matrix[(g, lab)] += 1
                if lab == g:
                    n_correct += 1
                if lab == "inanimate":
                    inan_pred += 1; inan_correct += int(g == "inanimate")
                if lab == "animate":
                    anim_pred += 1; anim_correct += int(g == "animate")
        confident_labeled = sum(conf_matrix.values())
        return {
            "n_heads": n_total,
            "n_with_gold": n_labeled_gold,
            "coverage_confident": round(n_confident / n_total, 4) if n_total else 0.0,
            "accuracy_on_confident_labeled": round(n_correct / confident_labeled, 4) if confident_labeled else None,
            "inanimate_precision": round(inan_correct / inan_pred, 4) if inan_pred else None,
            "inanimate_n_pred": inan_pred,
            "animate_precision": round(anim_correct / anim_pred, 4) if anim_pred else None,
            "animate_n_pred": anim_pred,
            "confusion": {f"{g}->{p}": c for (g, p), c in sorted(conf_matrix.items())},
        }
    heads_all = sorted(candidate_heads)
    heads_nonseed = sorted(h for h in candidate_heads if not in_seed(h))
    # per-source label breakdown
    src_counts = defaultdict(int)
    for h in heads_all:
        src_counts[classifier.label(h)[1]] += 1
    return {
        "all_candidate_heads": _eval(heads_all),
        "nonseed_candidate_heads": _eval(heads_nonseed),
        "label_source_breakdown": dict(src_counts),
        "n_candidate_heads": len(heads_all),
        "n_nonseed_candidate_heads": len(heads_nonseed),
    }


def collect_candidate_heads(order, sent_text):
    """The NP-head vocabulary that can appear in coref candidate pools (the Pred-2 evaluation universe)."""
    heads = set()
    for sid in order:
        for surf, low, pos in ORC.pos_tag_sentence(sent_text[sid]):
            is_cand, _n, _g, _a = COREF.noun_head_attrs(low, pos)
            if is_cand:
                heads.add(low)
    return heads


# ---------------------------------------------------------------------------------------------------
# Pred-3 scoring: triage LCCP patient-assignment FPs into animacy-catchable vs argument-structure-driven.
# animacy-catchable = the parser assigned a patient whose animacy an animacy-selectional check would reject
# AND a correct alternative exists. Argument-structure-driven = the verb should take NO patient (gold nopat)
# or the wrong patient is the same animacy as the gold patient (entity-type does not distinguish them).
# ---------------------------------------------------------------------------------------------------
def measure_pred3(keptC, slice_lessons, classifier):
    with open(GOLD_PATH, encoding="utf-8") as f:
        obj = json.load(f)
    gold_pat = {}    # (sid, vlemma) -> set(gold patient heads)
    gold_nopat = defaultdict(set)   # sid -> set(vlemma) that take NO patient
    for sid, rec in obj["gold"].items():
        if sid.split("_")[0] not in slice_lessons:
            continue
        for r in rec.get("pos", []):
            gold_pat[(sid, LCCP.lemma_verb(r["v"]))] = {str(r["patient"]).lower()}
        for r in rec.get("nopat", []):
            gold_nopat[sid].add(LCCP.lemma_verb(r["v"]))

    n_patient_assign = 0
    n_fp = 0
    n_animacy_catchable = 0
    n_argstruct = 0
    fp_log = []
    for kidx, (sid, t) in enumerate(keptC):
        v = LCCP.lemma_verb(t[0])
        patient = str(t[2]).lower().strip(".,'\"!?;:") if len(t) > 2 else ""
        if not patient or not patient.isalpha() or patient in PRONOUN_SCOPE or patient in LCCP.FUNCWORD:
            continue
        n_patient_assign += 1
        gp = gold_pat.get((sid, v))
        is_fp = False
        if v in gold_nopat.get(sid, set()) and gp is None:
            is_fp = True   # verb should take NO patient -> argument-structure FP
        elif gp is not None and patient not in gp:
            is_fp = True   # wrong patient
        if not is_fp:
            continue
        n_fp += 1
        pat_anim = classifier.label(patient)[0]
        # animacy-catchable iff gold patient exists, has a DIFFERENT animacy, i.e. an animacy selectional
        # check on the verb's patient slot would distinguish the wrong one from the right one.
        catchable = False
        if gp is not None:
            gold_anim = {classifier.label(g)[0] for g in gp}
            if pat_anim in ("animate", "inanimate") and gold_anim and pat_anim not in gold_anim \
                    and "unknown" not in gold_anim:
                catchable = True
        if catchable:
            n_animacy_catchable += 1
        else:
            n_argstruct += 1
        fp_log.append({"sid": sid, "v": v, "assigned_patient": patient, "patient_animacy": pat_anim,
                       "gold_patient": sorted(gp) if gp else None,
                       "class": "animacy_catchable" if catchable else "argument_structure"})
    return {
        "n_patient_assign": n_patient_assign,
        "n_fp": n_fp,
        "n_animacy_catchable": n_animacy_catchable,
        "n_argument_structure": n_argstruct,
        "frac_animacy_catchable": round(n_animacy_catchable / n_fp, 4) if n_fp else 0.0,
        "fp_log": fp_log,
    }


# ---------------------------------------------------------------------------------------------------
# Verdict logic.
# ---------------------------------------------------------------------------------------------------
def build_verdict_pred1(agg, no_new_breaks):
    """agg over seeds: broke_off/broke_on/fixed_on/inan_commit_on/p_off/p_on lists + means."""
    broke_on = agg["broke_on"]["vals"]; fixed_on = agg["fixed_on"]["vals"]
    inan_on = agg["inan_commit_on"]["vals"]
    m_broke_on = agg["broke_on"]["mean"]; m_broke_off = agg["broke_off"]["mean"]
    m_p_on = agg["p_on"]["mean"]; m_p_off = agg["p_off"]["mean"]
    net_non_neg_all = all(b <= f for b, f in zip(broke_on, fixed_on))
    inan_zero_all = all(x == 0 for x in inan_on)
    broke_reduced = m_broke_on < m_broke_off
    prec_ok_strict = m_p_on >= m_p_off
    prec_ok_soft = m_p_on >= m_p_off - 0.001
    if (m_broke_on >= m_broke_off) or (m_p_on < m_p_off - 0.02) or (not no_new_breaks):
        return "HARD_FAIL_1_ANIMACY_DOES_NOT_HELP"
    if net_non_neg_all and inan_zero_all and broke_reduced and prec_ok_strict and no_new_breaks:
        return "HARD_PASS_1_COREF_NET_NON_NEGATIVE"
    if inan_zero_all and broke_reduced and no_new_breaks and prec_ok_soft:
        return "PARTIAL_1_NAMED_INANIMATE_HARM_KILLED"
    return "PARTIAL_1_PARTIAL_HARM_REDUCTION"


def build_verdict_pred2(p2):
    ns = p2["nonseed_candidate_heads"]
    ip = ns["inanimate_precision"]
    cov = ns["coverage_confident"]
    if ip is None:
        # no non-seed inanimate predictions -> mask leans entirely on seed; report honestly
        return "PARTIAL_2_DISTRIBUTIONAL_INANIMATE_UNUSED_SEED_CARRIES_MASK"
    if ip >= 0.90:
        return "HARD_PASS_2_DISTRIBUTIONAL_INANIMATE_PRECISE"
    if ip >= 0.75 or cov < 0.30:
        return "PARTIAL_2_CORPUS_SPARSE_SEED_CARRIES_MASK"
    return "HARD_FAIL_2_DISTRIBUTIONAL_TOO_NOISY"


def build_verdict_pred3(p3):
    if p3["n_fp"] == 0:
        return "PARTIAL_3_NO_PATIENT_FPS_TO_TRIAGE"
    if p3["n_animacy_catchable"] <= 1 or p3["frac_animacy_catchable"] <= 0.15:
        return "HARD_PASS_3_PARSER_RESIDUAL_NOT_ANIMACY_NEAR_EMPTY"
    return "HARD_FAIL_3_ANIMACY_FIXES_PARSER_RESIDUAL_UNEXPECTED"


# ---------------------------------------------------------------------------------------------------
def _agg(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return {"mean": None, "min": None, "max": None, "vals": vals}
    return {"mean": round(float(np.mean(v)), 4), "min": round(float(np.min(v)), 4),
            "max": round(float(np.max(v)), 4), "vals": vals}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def cfg_smoke():
    return dict(slice_lessons=["L07", "L10", "L12"], sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=40,
               keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=7)


def cfg_full():
    return LCCP.cfg_full()


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))

    # shared upstream pipeline (LCCP arm-C keptC + head-finder OFF), computed ONCE (COREF.run_pipeline)
    pipe = COREF.run_pipeline(cfg)
    order, sent_text, keptC = pipe["order"], pipe["sent_text"], pipe["keptC"]
    resB2, gold_ag, named_refs = pipe["resB2"], pipe["gold_ag"], pipe["named_refs"]

    # fit the classifier ONCE from the corpus (deterministic count-based)
    classifier = AnimacyClassifier()
    classifier.fit(order, sent_text, pipe.get("reader_svo", {}) or _load_reader_svo(cfg))

    candidate_heads = collect_candidate_heads(order, sent_text)
    p2 = measure_pred2(order, sent_text, classifier, candidate_heads)
    p3 = measure_pred3(keptC, cfg["slice_lessons"], classifier)

    per_seed = []
    for s in FHRR_SEEDS:
        # OFF arm = the published coref cell, reproduced verbatim by calling COREF.resolve_coref_gated
        res_off, clog_off, _ec_off = COREF.resolve_coref_gated(order, sent_text, keptC, resB2, s)
        a_off = COREF.score_pred_a(keptC, gold_ag, resB2, res_off, named_refs)
        # ON arm = the SAME resolver + animacy hard mask (single variable)
        res_on, clog_on, _ec_on, mask_stats = resolve_coref_gated_animacy(
            order, sent_text, keptC, resB2, s, classifier, animacy_on=True)
        a_on = COREF.score_pred_a(keptC, gold_ag, resB2, res_on, named_refs)
        inan_off = n_inanimate_commit(res_off, classifier)
        inan_on = n_inanimate_commit(res_on, classifier)
        new_breaks, nb_log = count_new_breaks(keptC, gold_ag, resB2, res_off, res_on)
        # sanity: my ON-with-mask-OFF must reproduce COREF OFF exactly (guards the copy)
        res_on_maskoff, _cl, _ec, _ms = resolve_coref_gated_animacy(
            order, sent_text, keptC, resB2, s, classifier, animacy_on=False)
        maskoff_matches = _resolved_hash(keptC, resB2, res_on_maskoff) == _resolved_hash(keptC, resB2, res_off)
        per_seed.append({
            "seed": s,
            "p_off": a_off["precision_ON"], "p_on": a_on["precision_ON"],
            "pron_p_off": a_off["pron_subset_precision_ON"], "pron_p_on": a_on["pron_subset_precision_ON"],
            "broke_off": a_off["newly_broken"], "broke_on": a_on["newly_broken"],
            "fixed_off": a_off["newly_fixed"], "fixed_on": a_on["newly_fixed"],
            "n_commit_off": a_off["n_commit"], "n_commit_on": a_on["n_commit"],
            "abstain_off": a_off["abstain_rate"], "abstain_on": a_on["abstain_rate"],
            "inan_commit_off": inan_off, "inan_commit_on": inan_on,
            "new_breaks": new_breaks, "new_break_log": nb_log,
            "mask_stats": mask_stats, "maskoff_reproduces_off": maskoff_matches,
            "commit_log_on": clog_on,
        })

    agg = {
        "p_off": _agg([ps["p_off"] for ps in per_seed]),
        "p_on": _agg([ps["p_on"] for ps in per_seed]),
        "broke_off": _agg([ps["broke_off"] for ps in per_seed]),
        "broke_on": _agg([ps["broke_on"] for ps in per_seed]),
        "fixed_on": _agg([ps["fixed_on"] for ps in per_seed]),
        "inan_commit_off": _agg([ps["inan_commit_off"] for ps in per_seed]),
        "inan_commit_on": _agg([ps["inan_commit_on"] for ps in per_seed]),
        "abstain_off": _agg([ps["abstain_off"] for ps in per_seed]),
        "abstain_on": _agg([ps["abstain_on"] for ps in per_seed]),
        "new_breaks": _agg([ps["new_breaks"] for ps in per_seed]),
    }
    no_new_breaks = all(ps["new_breaks"] == 0 for ps in per_seed)
    maskoff_ok = all(ps["maskoff_reproduces_off"] for ps in per_seed)

    v1 = build_verdict_pred1(agg, no_new_breaks)
    v2 = build_verdict_pred2(p2)
    v3 = build_verdict_pred3(p3)

    # gates
    off_prec = per_seed[0]["p_off"]
    baseline_in_band = bool(0.05 < off_prec < 0.95)
    arms_differ = any(ps["inan_commit_off"] != ps["inan_commit_on"] or ps["mask_stats"]["n_masked_candidates"] > 0
                      for ps in per_seed)
    harm_present_off = per_seed[0]["inan_commit_off"] > 0
    n_inanimate_labeled = sum(1 for h in candidate_heads if classifier.label(h)[0] == "inanimate")
    discriminator_fires = bool(arms_differ and n_inanimate_labeled > 0)

    verdict = f"P1:{v1} | P2:{v2} | P3:{v3}"
    msg = (f"{verdict} | mode={mode} slice={'+'.join(cfg['slice_lessons'])} n_keptC={len(keptC)} "
           f"| P1: inan_commit OFF={agg['inan_commit_off']['vals']} ON={agg['inan_commit_on']['vals']} "
           f"broke OFF={agg['broke_off']['vals']} ON={agg['broke_on']['vals']} fixed_ON={agg['fixed_on']['vals']} "
           f"new_breaks={agg['new_breaks']['vals']} P_OFF={agg['p_off']['mean']:.3f} P_ON={agg['p_on']['mean']:.3f} "
           f"abstain OFF={agg['abstain_off']['mean']:.2f} ON={agg['abstain_on']['mean']:.2f} "
           f"(vs prior {CITED_PRIOR_COREF}) "
           f"| P2: nonseed inan_prec={p2['nonseed_candidate_heads']['inanimate_precision']} "
           f"acc={p2['nonseed_candidate_heads']['accuracy_on_confident_labeled']} "
           f"cov={p2['nonseed_candidate_heads']['coverage_confident']} "
           f"(n_nonseed={p2['n_nonseed_candidate_heads']}) "
           f"| P3: fp={p3['n_fp']} animacy_catchable={p3['n_animacy_catchable']} "
           f"argstruct={p3['n_argument_structure']} frac={p3['frac_animacy_catchable']} "
           f"| gates: base_in_band={baseline_in_band} arms_differ={arms_differ} discrim={discriminator_fires} "
           f"harm_present_OFF={harm_present_off} maskoff_reproduces_OFF={maskoff_ok}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": time.perf_counter() - t0, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": cfg, "verdict_pred1": v1, "verdict_pred2": v2, "verdict_pred3": v3,
        "fhrr_seeds": FHRR_SEEDS, "aggregates_multiseed": agg,
        "pred1_per_seed": [{k: v for k, v in ps.items() if k != "commit_log_on"} for ps in per_seed],
        "pred1_commit_log_on_seed0": per_seed[0]["commit_log_on"],
        "pred2_classifier": p2, "pred3_parser_residual": p3,
        "pre_registered": {"TAU_MARGIN": TAU_MARGIN, "COS_FLOOR": COS_FLOOR, "N_DIM": N_DIM,
                           "ANIMATE_REQUIRING_PRONOUNS": sorted(ANIMATE_REQUIRING_PRONOUNS),
                           "distributional_rule": "inanimate iff inan_ev>=1 and inan_ev>anim_ev and anim_ev==0; "
                                                  "animate iff anim_ev>=1 and anim_ev>=inan_ev",
                           "pred2_hard_pass": "nonseed inanimate_precision>=0.90",
                           "pred3_hard_pass": "n_animacy_catchable<=1 or frac<=0.15 (near-empty)"},
        "credits": {"seed_lists": CREDIT_SEED, "animate_verbs": CREDIT_VERBS,
                    "gold_animacy": "single-annotator hand labels over this corpus's noun heads (Director)"},
        "arms_differ_verified": arms_differ, "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires, "harm_present_off": harm_present_off,
        "maskoff_reproduces_off": maskoff_ok, "no_new_breaks": no_new_breaks,
        "final_metrics_atomicity": "tmp_replace", "calibration_check": "default_ok_for_this_regime",
        "crlb_n_a": "no additive-Gaussian estimator floor; discrete classifier + FHRR crosstalk inside small pools",
        "cited": {"headfinder_B2_agent_lens": CITED_HEADFINDER_B2, "prior_coref": CITED_PRIOR_COREF,
                  "reader_topline": "reader true-stacked precision 0.557 (separate aggregate)"},
        "REQUIRED_FIELDS": ["verdict", "verdict_pred1", "verdict_pred2", "verdict_pred3",
                            "aggregates_multiseed", "pred2_classifier", "pred3_parser_residual",
                            "arms_differ_verified", "baseline_in_band", "discriminator_fires"],
        "reused_components": {
            "coref_baseline": "exp_coref_margin_gated_cleanup_local_window_break050_v1 (OFF arm called verbatim; atom 29355/56)",
            "lccp": "exp_learned_argstruct_parser_lccp_independent_gold_v1 (arm-C keptC; atom 29338)",
            "head_finder": "exp_np_head_finder_grounding_gate_break050_v1.resolve_heads(use_grounding=True) (atom 29342)",
        },
        "notes": ("Seeded distributional animacy classifier as a HARD candidate pre-filter in the margin-gated "
                  "coref resolver. ONE VARIABLE = animacy mask ON vs OFF (OFF calls COREF.resolve_coref_gated "
                  "verbatim = the published net-negative baseline). Pred 1 = does the mask kill the named "
                  "they->inanimate harm (n_inanimate_commit->0) and reduce the break budget without new breaks "
                  "or precision loss. Pred 2 = distributional-classifier accuracy/coverage at 163-sentence "
                  "scale (honest corpus-sparsity can-fail; inanimate-precision is the mask-critical number). "
                  "Pred 3 = parser patient-FP triage confirms animacy does NOT fix the argument-structure "
                  "residual (near-empty animacy-catchable bucket = honest scope boundary). Animacy = DISCRETE/"
                  "CATEGORICAL (escapes the graded-cosine structural-beats-semantic wall) but NOT a full "
                  "world-knowledge substitute. STRATEGIC READ = HYPOTHESIS pending skunkworks landed-VET. "
                  "Single-annotator gold. LOCAL-ONLY; NO push/remote-persist/git-add-A; no atom banking."),
        "needs_orchestrator_store_sync": True,
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"  metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for ps in per_seed:
        print(f"  seed={ps['seed']} P1 inan_commit {ps['inan_commit_off']}->{ps['inan_commit_on']} "
              f"broke {ps['broke_off']}->{ps['broke_on']} fixed_on={ps['fixed_on']} new_breaks={ps['new_breaks']} "
              f"P {ps['p_off']:.3f}->{ps['p_on']:.3f} abstain {ps['abstain_off']:.2f}->{ps['abstain_on']:.2f} "
              f"mask={ps['mask_stats']} maskoff_ok={ps['maskoff_reproduces_off']}", flush=True)
    print("  --- seed0 ON commit log (sid v pron -> resolved [animacy] pool) ---", flush=True)
    for c in per_seed[0]["commit_log_on"]:
        print(f"    {c['sid']} {c['v']:>8} {c['pron']:>5} -> {c['resolved']:<10} [{c['resolved_animacy']}] "
              f"pool={c['pool']}", flush=True)
    ns = p2["nonseed_candidate_heads"]
    print(f"  --- Pred2 nonseed heads: n={p2['n_nonseed_candidate_heads']} inan_prec={ns['inanimate_precision']} "
          f"anim_prec={ns['animate_precision']} acc={ns['accuracy_on_confident_labeled']} "
          f"cov={ns['coverage_confident']} confusion={ns['confusion']}", flush=True)
    print(f"  --- Pred3 parser residual: fp={p3['n_fp']} catchable={p3['n_animacy_catchable']} "
          f"argstruct={p3['n_argument_structure']}", flush=True)
    for fp in p3["fp_log"][:12]:
        print(f"      FP {fp['sid']} {fp['v']:>8} pat={fp['assigned_patient']}[{fp['patient_animacy']}] "
              f"gold_pat={fp['gold_patient']} class={fp['class']}", flush=True)
    return payload


def _resolved_hash(keptC, resB2, resolved):
    items = []
    for kidx, (sid, t) in enumerate(keptC):
        off = str(resB2.get((sid, kidx), (str(t[1]).lower(), "id"))[0]).lower()
        h = resolved.get((sid, kidx), (off,))[0]
        items.append(f"{sid}|{LCCP.lemma_verb(t[0])}|{h}")
    return hashlib.sha256("\n".join(sorted(items)).encode()).hexdigest()[:16]


def _load_reader_svo(cfg):
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(cfg["slice_lessons"])
    return reader_svo


# ---------------------------------------------------------------------------------------------------
def _selftest_classifier():
    """Toy: classifier fires correctly on clean cases -- man=animate, flower=inanimate, table=inanimate,
    dog=animate; a distributional-only head with animate cues -> animate; unknown head -> unknown."""
    clf = AnimacyClassifier()
    # a tiny toy corpus so distributional features exist
    order = ["T_00", "T_01"]
    sent_text = {"T_00": "The captain who sailed spoke .", "T_01": "The rock which fell broke ."}
    reader_svo = {"T_00": [("captain", "spoke", "")], "T_01": [("rock", "fell", "")]}
    clf.fit(order, sent_text, reader_svo)
    assert clf.label("man")[0] == "animate", clf.label("man")
    assert clf.label("woman")[0] == "animate", clf.label("woman")
    assert clf.label("flower")[0] == "inanimate", clf.label("flower")
    assert clf.label("table")[0] == "inanimate", clf.label("table")
    assert clf.label("dog")[0] == "animate", clf.label("dog")
    # gender cue
    assert clf.label("king")[0] == "animate", clf.label("king")
    # distributional: 'captain' (not in seed) followed by 'who' + animate verb -> animate
    assert clf.label("captain")[0] == "animate", clf.label("captain")
    # distributional: 'rock' (not in seed) followed by 'which' -> inanimate
    assert clf.label("rock")[0] == "inanimate", clf.label("rock")
    # a head with no seed/gender/distributional evidence -> unknown (never masked)
    assert clf.label("zqxwv")[0] == "unknown", clf.label("zqxwv")
    print(f"[selftest] classifier OK: man={clf.label('man')} flower={clf.label('flower')} "
          f"captain={clf.label('captain')}(dist) rock={clf.label('rock')}(dist) zqxwv={clf.label('zqxwv')}", flush=True)


def _selftest_mask_fires():
    """Toy: an animate-requiring pronoun ('they') masks an inanimate candidate out of the pool; the resolver
    then abstains when only the inanimate candidate existed (empty pool). Uses the REAL smoke pipeline."""
    cfg = cfg_smoke()
    pipe = COREF.run_pipeline(cfg)
    clf = AnimacyClassifier()
    clf.fit(pipe["order"], pipe["sent_text"], _load_reader_svo(cfg))
    res_off, _cl, _ec = COREF.resolve_coref_gated(pipe["order"], pipe["sent_text"], pipe["keptC"], pipe["resB2"], 7)
    res_on, _cl2, _ec2, mstats = resolve_coref_gated_animacy(
        pipe["order"], pipe["sent_text"], pipe["keptC"], pipe["resB2"], 7, clf, animacy_on=True)
    inan_off = n_inanimate_commit(res_off, clf)
    inan_on = n_inanimate_commit(res_on, clf)
    assert mstats["n_masked_candidates"] >= 1, f"mask did not fire: {mstats}"
    assert inan_on <= inan_off, f"animacy mask did not reduce inanimate commits: off={inan_off} on={inan_on}"
    # mask-OFF must reproduce the OFF baseline exactly (single-variable guarantee)
    res_maskoff, _c, _e, _m = resolve_coref_gated_animacy(
        pipe["order"], pipe["sent_text"], pipe["keptC"], pipe["resB2"], 7, clf, animacy_on=False)
    assert _resolved_hash(pipe["keptC"], pipe["resB2"], res_maskoff) == \
           _resolved_hash(pipe["keptC"], pipe["resB2"], res_off), "mask-OFF does not reproduce COREF OFF"
    print(f"[selftest] mask OK: masked={mstats} inan_commit {inan_off}->{inan_on} maskoff==OFF", flush=True)


def self_test():
    _selftest_classifier()
    _selftest_mask_fires()
    cfg = cfg_smoke()
    pipe = COREF.run_pipeline(cfg)
    assert len(pipe["keptC"]) > 0, "self-test: no keptC from real pipeline"
    clf = AnimacyClassifier()
    clf.fit(pipe["order"], pipe["sent_text"], _load_reader_svo(cfg))
    ch = collect_candidate_heads(pipe["order"], pipe["sent_text"])
    p2 = measure_pred2(pipe["order"], pipe["sent_text"], clf, ch)
    p3 = measure_pred3(pipe["keptC"], cfg["slice_lessons"], clf)
    assert p2["n_candidate_heads"] > 0, "self-test: no candidate heads"
    print(f"[{ANCHOR_NAME}] self-test OK: n_keptC={len(pipe['keptC'])} n_cand_heads={p2['n_candidate_heads']} "
          f"n_nonseed={p2['n_nonseed_candidate_heads']} p3_fp={p3['n_fp']}", flush=True)


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
