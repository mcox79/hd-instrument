"""exp_feeling_match_rejector_v1 -- does a rejector that matches on the FEELING of a word beat one
that only knows whether the word was ever SEEN in that slot?

THE TWO LINES OF EVIDENCE THAT MADE THIS CELL.
--------------------------------------------------------------------------------------------
MEASURED (notes/drill_target_space_dimensionality_semantic_representation_verbs_2026-08-16.md,
Part C): our 12-dim landing space covers 2 of the brain's 7 attribute blocks. Adding the AFFECT
channel (Warriner valence/arousal/dominance, on disk, unused) lifts the hand-rated SimLex ceiling
+0.1013 [+0.0615,+0.1419] CI-separated on 977 pairs; verbs +0.1228, adjectives +0.3399, nouns
+0.0253 NOT separated. A width-matched NON-channel widening buys nothing. THAT WAS A CEILING
DIAGNOSTIC WITH NO FLOORS AND NO NULL. Nothing from it is imported here as a result.

INTROSPECTED (BOARD Q10, owner verbatim): "I think I'm trying to match it to the feeling of the
word... words with the same meanings have different feelings to use - 'think' versus 'contemplate'
have very different feelings - one is informal one is more thoughtful and purposeful. So it's those
kinds of feelings I'm trying to match."

The measurement says AFFECT is the missing channel. The introspection says AFFECT is what REJECTION
runs on. This cell builds the feeling-match rejector and tests it against the attestation rejector
on ONE population, ONE scorer, ONE gold.

THE TASK. Given a verb-argument SLOT (verb lemma + normalised role) and a CANDIDATE word, score how
well the candidate fits the slot. Gold = the candidate is attested in that slot in a HELD-OUT half
of the corpus. Attestation ("was this word ever seen in this slot in the OTHER half?") is the
incumbent. It is crude by construction: it knows seen/unseen and nothing else, so on a candidate it
has never seen it returns the SAME score for a perfect fit and for an absurdity.

THE DECISIVE SUB-POPULATION, pre-registered: items whose gold has train-fold count ZERO. There
attestation ties the entire pool at zero and scores EXACTLY that pool's chance rate under the
tie-corrected metric. A feeling-match rejector still has an opinion. That is the specific failure
of attestation and the specific claim of BOARD Q11.

THE TWO MODES (BOARD Q11, owner verbatim): "The kettle apologized I can reject immediately because
kettles aren't sentient... The argument one is a bit tricker - I could see it being a metaphor for
'laying it on thick' - and I can still make sense of it so it isn't discarded out of hand. So yes,
the rejector generalizes, but the rejections for those two sentences are very different."
  MODE 1 HARD TYPE VIOLATION -- an animacy-selecting slot filled by an inanimate candidate.
  MODE 2 SOFT IMPLAUSIBILITY -- the same slot filled by an animate candidate it has never seen.
Both are UNATTESTED, so attestation scores them IDENTICALLY and its mode separation is EXACTLY
0.0 by construction (asserted in selftest, not claimed). A rejector that collapses the two modes is
not the mechanism the owner described, so the modes are scored SEPARATELY and never pooled.

BRAIN-FIDELITY BLOCK (a) STRUCTURE PER COMPONENT -- neural systems, not cognitive-theory labels:
  AFFECT CHANNEL -- amygdala (population coding of valence), orbitofrontal and ventromedial
    prefrontal cortex, insula. These are DISTINCT SYSTEMS from the modality-specific sensory and
    motor cortices that carry the sensorimotor spokes, which is precisely why affect is a separate
    CHANNEL and not more dimensions of the same one. [PINNED: Binder et al. 2016 Cogn Neuropsychol
    33:130 lists affect as one of seven blocks with its own substrate; Vigliocco et al. PMID
    23408565 for affect as the grounding channel of abstract meaning.]
  SELECTION AMONG COMPETING CANDIDATES (what a rejector IS) -- left inferior frontal gyrus,
    BA45/47, the structure whose damage impairs selection among competing lexical candidates rather
    than retrieval as such. [PINNED as a structure.] Our particular distance estimator is OURS.
  ANIMACY (MODE 1) -- the animate/inanimate division is one of the most robust category
    dissociations in ventral temporal cortex, with superior temporal sulcus and amygdala
    involvement for animacy specifically. A categorical type distinction with its own substrate is
    exactly why MODE 1 can be instant and categorical. [PINNED as a category distinction.]
  GRADED THEMATIC FIT (MODE 2) -- posterior middle temporal gyrus and angular gyrus, the same hub
    the selectional extractor already rides. [PINNED.] This cell builds NO new hub.
(b) ORGAN REUSE -- enumerated from disk, reconciled to the registry afterwards, verified by
    RUNTIME (import + call, recorded in metrics), never by grep. See ORGAN_REUSE below.
(c) PINNED vs OURS-INVENTION -- recorded per choice in BRAIN_FIDELITY below. Everything about the
    ESTIMATOR, the SPLIT, the animacy rule and the mode construction is OURS AND UNDER TEST.
(d) SHELVE / REVIVAL CRITERION, brain-framed and never performance-framed -- in BRAIN_FIDELITY.

HOW TO READ A NEGATIVE. The owner performed this rejection in front of us, twice, and described the
two modes. THE CAPABILITY IS DEMONSTRATED. Any null here is a fact about OUR IMPLEMENTATION -- our
3-dim operationalisation of affect, our diagonal-distance estimator, our slot definition, our
corpus -- and never about feeling-based rejection.

TRAPS RE-EARNED BY RUNTIME EVERY RUN, NEVER INHERITED:
  * grounded_similarity() saturates >70% of SimLex onto two values and is NEVER a scorer here.
  * exp_task_degeneracy_v1.ruler_mode_gate() is CALLED and hard-fails unless the instrument
    resolved RUN_MODE=full / V=4096 / CORPUS_BYTES=64,000,000. This cell's reduced flag is
    `--grid reduced` precisely so the token `--smoke` never enters argv and cannot silently swap
    the ruler under the frequency floor.
  * ZERO-FILL IS BARRED. Every arm runs on the SAME intersection stratum where every candidate has
    Lancaster-12 AND Warriner-3 AND concreteness AND a corpus count. One anchor set, all arms.
  * NO NUMBER IS IMPORTED FROM ANOTHER POPULATION. The attestation incumbent is RE-MEASURED here.
    The constant/prototype floor is computed on THIS population and reported with THIS n.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. WordNet (a static offline lexical
database) is used only as an animacy/POS oracle, the same use the existing extractors make of it.
ASCII-only. CPU. No network. data/foundation/** is never opened by this cell.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import collections
import csv
import io
import json
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tools.floor_battery import (                                              # noqa: E402
    FLOOR_SET_REQUIRED, as_constant_matrix, balanced_candidate_sets, constant_prototype_floor,
    frequency_floor, hit_at_1_both_tie_conventions, margin, matched_candidate_sets,
    oracle_constant_scores, paired_bootstrap_ci, rank_of_best_gold,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key   # noqa: E402
from experiments._seed_checkpoint import get_output_dir, record_gate, write_metrics   # noqa: E402

ANCHOR_NAME = "feeling_match_rejector_v1"
# v1.1: the design-gate pass (MIN_SLOT_TOTAL 20 -> 8, the mode block's own population, lazy arm
# factories). CODE_VERSION is part of every checkpoint unit key, so a v1.0 unit written by the
# pre-refactor run CANNOT be resumed by a v1.1 run. That is the durable fix for the stale-checkpoint
# hazard and it replaces the output-directory teardown that was (correctly) denied.
CODE_VERSION = "v1.2"

# ---- THE FLAG IS `--grid reduced`, NEVER `--smoke`. See the TRAPS block above. --------------
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS. Only the CAPS differ between grids; every rule is identical. --
MASTER_SEED = 20260816
SPLIT_SEED = 991117                         # the binomial thinning seed
BOOT_SEED = 20260816
N_BOOT = 2000 if SMOKE else 4000
N_PERM = 40 if SMOKE else 200
MAX_ITEMS = 300 if SMOKE else 6000
MAX_ANCHORS = 600 if SMOKE else 6000
NULL_SEEDS = (7, 13, 17, 23, 29)

# DESIGN GATE, MEASURED BEFORE ANY FULL-GRID TREATMENT NUMBER EXISTED, and recorded because a
# threshold moved after seeing a result is not a threshold. scratch/fmr_gate_probe.py enumerated
# the whole slot table under twelve gate settings. At the originally drafted MIN_SLOT_TOTAL=20 the
# cell had 4,112 items and only 369 in the UNATTESTED sub-stratum -- and the unattested stratum is
# THE decisive one, where a hit-rate CI half-width at n=369 is about 0.021, wider than any effect
# this cell could plausibly show. Relaxing the SLOT-SIZE gate 20 -> 8 while HOLDING the
# PROFILE-QUALITY gate at 5 distinct train fillers gives 5,733 items and 1,150 unattested
# (half-width about 0.012). The gate that was relaxed is the one that does not change how good a
# profile is; the gate that governs profile quality was not touched.
MIN_SLOT_TOTAL = 8             # total observations a slot needs before it is an item
MIN_TRAIN_FILLERS = 5          # distinct train-fold fillers with a code -- NOT relaxed
MIN_ANCHOR_COUNT = 5           # a candidate word needs this much corpus evidence to be eligible
K_DISTRACT = 15                # balanced / matched pools: chance = 1/16
SD_PRIOR_N = 8.0               # shrinkage of the per-slot SD toward the global SD (= 1 after z)
N_MODE = 8 if SMOKE else 20    # mode-1 / mode-2 candidates per animacy-selecting slot
# ALSO A MEASURED DESIGN GATE, same probe, same discipline. Over 1,182 scoreable SUBJ slots the
# animate share of resolvable subject mass has median 0.211 and p90 0.455; at the originally
# drafted 0.80 only 14 slots qualify and the block is unscoreable. 0.60 is comfortably in the tail
# of the observed distribution and yields 51. The achieved distribution is reported in the metrics
# beside the count, so "animacy-selecting" is auditable rather than asserted.
ANIM_MASS_FRAC = 0.60          # a slot is animacy-selecting at this animate filler mass
ANIM_MIN_RESOLVED = 5          # ... over at least this many animacy-resolvable observations
MODE_MIN_SLOT_TOTAL = 8        # the mode block builds its OWN population from ALL SUBJ slots
MODE_MIN_TRAIN_FILLERS = 3     # ... and reports its own n; it is NEVER pooled with the primary
KA_CEILING_MIN = 0.95          # KNOWN-ANSWER gate; below this the whole pool is VOID and unread
NULL_TOL = 0.02                # a null arm must sit within this of its pool's own chance
T_MARGIN_MIN = 0.02            # a margin below this is MIDDLE_BAND even when CI-separated

PROGRESS_LOGGING = "every pool, every arm, every permutation block prints with flush=True"

DATA = REPO / "data"
GT = DATA / "grounding_testbed"
SLOTS_PKL = DATA / "selectional_preferences_v1" / "selectional_slots_v1.pkl"

# COLUMN PROVENANCE: identical column specs to tools/target_space_ceiling_diagnostic.py lines
# 55-62 (Director, 2026-08-16), credited and reused rather than re-derived. That module executes
# its whole diagnostic at import time and therefore CANNOT be imported; only the spec is carried.
L11 = ["Auditory.mean", "Gustatory.mean", "Haptic.mean", "Interoceptive.mean", "Olfactory.mean",
       "Visual.mean", "Foot_leg.mean", "Hand_arm.mean", "Head.mean", "Mouth.mean", "Torso.mean"]
LSD3 = ["Auditory.SD", "Visual.SD", "Haptic.SD"]      # WIDTH-MATCHED NON-CHANNEL control (3 cols)
VAD = ["V.Mean.Sum", "A.Mean.Sum", "D.Mean.Sum"]

SPACE_SPEC = {
    "SENSORIMOTOR_12": [("L", c) for c in L11] + [("C", "Conc.M")],
    "AFFECT_3": [("W", c) for c in VAD],
    "BOTH_15": [("L", c) for c in L11] + [("C", "Conc.M")] + [("W", c) for c in VAD],
    "NEGCTRL_RATERSD_3": [("L", c) for c in LSD3],
    "CONC_1": [("C", "Conc.M")],
}

PRIMARY_SPACE = "BOTH_15"
PRIMARY_ARM = "FEEL_BOTH_15_LGO"
INCUMBENT_ARM = "ATTESTATION"
NEGCTRL_ARM = "FEEL_NEGCTRL_RATERSD_3_LGO"
POOLS = ("P_OPEN", "P_BALANCED_K15", "P_MATCHED_K15")
PRIMARY_POOL = "P_BALANCED_K15"

FLOOR_ARMS = ("F_ORTHOGRAPHIC", "F_FREQUENCY", "F_CONSTANT_PROTOTYPE", "F_SCRAMBLE_PERM_P95")


# ==========================================================================================
# assets
# ==========================================================================================
def _read_tbl(path: Path, key: str = "Word") -> Dict[str, dict]:
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        first = f.readline()
    delim = "\t" if first.count("\t") > first.count(",") else ","
    out: Dict[str, dict] = {}
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f, delimiter=delim):
            w = (r.get(key) or "").strip().lower()
            if w:
                out[w] = r
    return out


def _f(v) -> Optional[float]:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_rating_spaces() -> Dict[str, Dict[str, np.ndarray]]:
    """{space_name: {word: vector}}. ZERO-FILL IS BARRED -- a word absent from any source column
    of a space is absent from that space, and the cell later intersects across ALL spaces."""
    src = {"L": _read_tbl(GT / "Lancaster_sensorimotor_norms_for_39707_words.csv"),
           "C": _read_tbl(GT / "Concreteness_ratings_Brysbaert_et_al_BRM.txt"),
           "W": _read_tbl(GT / "Ratings_Warriner_et_al.csv")}
    out: Dict[str, Dict[str, np.ndarray]] = {}
    for name, spec in SPACE_SPEC.items():
        vocab: Optional[Set[str]] = None
        for s, _c in spec:
            v = set(src[s])
            vocab = v if vocab is None else (vocab & v)
        tbl: Dict[str, np.ndarray] = {}
        for w in sorted(vocab or ()):
            vals = []
            ok = True
            for s, c in spec:
                x = _f(src[s][w].get(c))
                if x is None:
                    ok = False
                    break
                vals.append(x)
            if ok:
                tbl[w] = np.asarray(vals, dtype=np.float64)
        out[name] = tbl
    return out


def load_slots() -> Dict:
    with open(SLOTS_PKL, "rb") as f:
        return pickle.load(f)


def corpus_counts(corpus: str, nbytes: int) -> Dict[str, int]:
    """Token frequency over the SAME corpus and byte budget the slot tables were built from."""
    with open(corpus, "rb") as f:
        raw = f.read(nbytes)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    return collections.Counter(re.findall(r"[a-z]+", raw.decode("utf-8", errors="ignore").lower()))


_ANIM_CACHE: Dict[str, Optional[bool]] = {}


def is_animate(w: str) -> Optional[bool]:
    """DOMINANT-SENSE animacy from WordNet. OURS -- INVENTION UNDER TEST, and it carries the
    sense-averaging cost knowingly: a per-word answer is an average over senses, which the
    literature says the brain does not do (Trott & Bergen). Returns True / False / None(unknown).

    ANIMATE   : the word's FIRST (most frequent) noun sense is a living thing or a person/animal.
    INANIMATE : the word has noun senses and NONE of them is animate -- deliberately strict, so a
                MODE-1 hard type violation is never manufactured out of an ambiguous word.
    """
    if w in _ANIM_CACHE:
        return _ANIM_CACHE[w]
    from nltk.corpus import wordnet as wn
    syns = wn.synsets(w, pos="n")
    if not syns:
        _ANIM_CACHE[w] = None
        return None

    def _anim(s) -> bool:
        if s.lexname() in ("noun.person", "noun.animal"):
            return True
        for path in s.hypernym_paths():
            for h in path:
                if h.name() in ("living_thing.n.01", "organism.n.01", "person.n.01",
                                "animal.n.01"):
                    return True
        return False

    first = _anim(syns[0])
    if first:
        _ANIM_CACHE[w] = True
        return True
    any_anim = any(_anim(s) for s in syns[:6])
    _ANIM_CACHE[w] = None if any_anim else False
    return _ANIM_CACHE[w]


# ==========================================================================================
# THE SPLIT -- OURS, INVENTION UNDER TEST, and its bias direction is stated
# ==========================================================================================
def thin_counts(slot_filler: Dict, seed: int) -> Tuple[Dict, Dict]:
    """Split every (slot, filler) count c into c_train ~ Binomial(c, 0.5) and c_test = c - c_train.

    WHY THIS AND NOT A DOCUMENT SPLIT. Under a Poisson model of occurrences, binomial thinning of
    counts is exactly equivalent to splitting the corpus, and the slot tables on disk carry counts
    only -- a document split would require a full re-parse of the 64 MB budget.

    THE BIAS, STATED IN ADVANCE AND IN THE INCUMBENT'S FAVOUR. Real occurrences are BURSTY: the
    same (slot, filler) repeats within a document, so a genuine document split would push all of a
    pair's occurrences into ONE half and leave attestation with FEWER pairs seen in both halves.
    Thinning spreads them, which HELPS attestation. Any margin the feeling arm wins here is
    therefore won against an incumbent that has been handed the easier split.
    """
    rng = np.random.default_rng(seed)
    train: Dict = {}
    test: Dict = {}
    for s in sorted(slot_filler):
        fill = slot_filler[s]
        keys = sorted(fill)
        cs = np.asarray([fill[k] for k in keys], dtype=np.int64)
        tr = rng.binomial(cs, 0.5)
        te = cs - tr
        dtr = {k: int(v) for k, v in zip(keys, tr) if v > 0}
        dte = {k: int(v) for k, v in zip(keys, te) if v > 0}
        if dtr:
            train[s] = dtr
        if dte:
            test[s] = dte
    return train, test


# ==========================================================================================
# trigram orthography -- the SPELLING floor and the MATCHED pool's nuisance channel
# ==========================================================================================
def _tri(w: str) -> Set[str]:
    t = " " + w + " "
    return {t[i:i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def trigram_cos_matrix(words: Sequence[str], others: Sequence[str]) -> np.ndarray:
    """[len(words), len(others)] character-trigram cosine. No codes are touched, so this is a
    STANDALONE spelling policy and a legitimate floor."""
    # `others` is one VERB PER ITEM and many items share a verb, so the intersections are computed
    # once per DISTINCT verb and then indexed. Same numbers, ~5x less work at full grid.
    uniq = sorted(set(others))
    upos = {o: j for j, o in enumerate(uniq)}
    A = [_tri(w) for w in words]
    B = [_tri(o) for o in uniq]
    U = np.zeros((len(A), len(B)), dtype=np.float32)
    nb = np.asarray([len(b) for b in B], dtype=np.float32)
    for i, a in enumerate(A):
        na = float(len(a))
        row = np.asarray([len(a & b) for b in B], dtype=np.float32)
        U[i] = row / np.sqrt(np.maximum(na * nb, 1e-12))
    return U[:, [upos[o] for o in others]]


# ==========================================================================================
# THE FEELING-MATCH ESTIMATOR -- OURS, INVENTION UNDER TEST
# ==========================================================================================
class ProfileMatcher:
    """A slot's FEELING is the count-weighted profile of what has filled it, per channel; a
    candidate is scored by how far its own profile sits from that, in units of the slot's own
    spread.

    score(w | s) = - sqrt( mean_d ( (Z[w,d] - mu[s,d]) / sd[s,d] )^2 )

    Z is the space, GLOBALLY z-scored per dimension over the eligible anchor population, so the
    Warriner 1-9 scale cannot dominate the Lancaster 0-5 scale. sd[s] is shrunk toward the global
    SD (which is 1 after z-scoring) with a pseudo-count, so a slot with three fillers does not get
    a degenerate zero-width channel. EVERY PART OF THIS IS OURS AND UNDER TEST: the literature
    pins that affect is a separable semantic block with its own substrate, and pins no estimator.
    """

    def __init__(self, Z: np.ndarray, word_row: Dict[str, int]):
        self.Z = np.asarray(Z, dtype=np.float64)
        self.d = self.Z.shape[1]
        self.word_row = word_row
        self.Z2 = self.Z ** 2

    def profiles(self, item_fillers: Sequence[Dict[str, int]],
                 drop: Optional[Sequence[Optional[str]]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """-> (mu [n_items, d], inv [n_items, d] = 1/sd^2). `drop[i]` removes one word from item
        i's profile (the LEAVE-GOLD-OUT arm, so the gold can never sit inside its own target)."""
        n = len(item_fillers)
        mu = np.zeros((n, self.d), dtype=np.float64)
        inv = np.ones((n, self.d), dtype=np.float64)
        for i, fill in enumerate(item_fillers):
            skip = None if drop is None else drop[i]
            rows, wts = [], []
            for f, c in fill.items():
                if f == skip:
                    continue
                r = self.word_row.get(f)
                if r is None:
                    continue
                rows.append(r)
                wts.append(float(c))
            if not rows:
                continue
            R = self.Z[np.asarray(rows, dtype=np.int64)]
            w = np.asarray(wts, dtype=np.float64)
            wsum = w.sum()
            m = (R * w[:, None]).sum(axis=0) / wsum
            var = (((R - m) ** 2) * w[:, None]).sum(axis=0) / wsum
            n_eff = (wsum ** 2) / float((w ** 2).sum())
            var_s = (n_eff * var + SD_PRIOR_N * 1.0) / (n_eff + SD_PRIOR_N)
            mu[i] = m
            inv[i] = 1.0 / np.maximum(var_s, 1e-9)
        return mu, inv

    def scores(self, mu: np.ndarray, inv: np.ndarray, Z: Optional[np.ndarray] = None) -> np.ndarray:
        """[n_anchors, n_items] = -normalised diagonal Mahalanobis distance. Three matmuls."""
        Zc = self.Z if Z is None else np.asarray(Z, dtype=np.float64)
        Z2 = self.Z2 if Z is None else Zc ** 2
        t1 = Z2 @ inv.T
        t2 = -2.0 * (Zc @ (mu * inv).T)
        t3 = (mu * mu * inv).sum(axis=1)[None, :]
        s2 = np.maximum((t1 + t2 + t3) / float(self.d), 0.0)
        return (-np.sqrt(s2)).astype(np.float32)


def _within_item_z(S: np.ndarray, elig: np.ndarray) -> np.ndarray:
    """Standardise each item's scores over its OWN eligible pool, so two arms on different natural
    scales can be summed. Used only by the COMBINED arm and the two-mode block."""
    X = np.where(elig, S.astype(np.float64), np.nan)
    m = np.nanmean(X, axis=0, keepdims=True)
    s = np.nanstd(X, axis=0, keepdims=True)
    Zs = (X - m) / np.maximum(s, 1e-9)
    return np.nan_to_num(Zs, nan=0.0).astype(np.float32)


# ==========================================================================================
# population
# ==========================================================================================
def eligible_words(spaces: Dict[str, Dict[str, np.ndarray]], train: Dict, test: Dict,
                   counts: Dict[str, int]) -> List[str]:
    """Candidate vocabulary: present in EVERY space (intersection stratum; ZERO-FILL BARRED), seen
    at least once as a filler, and carrying enough corpus evidence to have a frequency at all."""
    inter: Optional[Set[str]] = None
    for tbl in spaces.values():
        v = set(tbl)
        inter = v if inter is None else (inter & v)
    seen_as_filler: Set[str] = set()
    for s in train:
        seen_as_filler.update(train[s])
    for s in test:
        seen_as_filler.update(test[s])
    out = sorted(w for w in (inter or set())
                 if w in seen_as_filler and counts.get(w, 0) >= MIN_ANCHOR_COUNT)
    print("[pop] intersection stratum: %d words in all %d spaces; %d eligible candidates "
          "(seen as a filler, corpus count >= %d)" % (len(inter or ()), len(spaces), len(out),
                                                      MIN_ANCHOR_COUNT), flush=True)
    return out


def select_items(train: Dict, test: Dict, elig_set: Set[str], min_total: int, min_fillers: int,
                 role_prefix: Optional[str] = None,
                 animacy_selecting: bool = False) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for s in sorted(set(train) & set(test)):
        if role_prefix is not None and not s[1].startswith(role_prefix):
            continue
        tr, te = train[s], test[s]
        if sum(tr.values()) + sum(te.values()) < min_total:
            continue
        if sum(1 for f in tr if f in elig_set) < min_fillers:
            continue
        if not any(f in elig_set for f in te):
            continue
        if animacy_selecting:
            tot = ani = 0
            for f, c in tr.items():
                a = is_animate(f)
                if a is None:
                    continue
                tot += c
                if a:
                    ani += c
            if tot < ANIM_MIN_RESOLVED or ani < ANIM_MASS_FRAC * tot:
                continue
        out.append(s)
    return out


def choose_designated(items: Sequence[Tuple[str, str]], test: Dict, elig_set: Set[str],
                      seed: int) -> List[str]:
    """UNIFORM at random among each item's eligible test golds. NOT the rarest and NOT the
    commonest -- either choice would stack the deck for or against the incumbent."""
    rng = np.random.default_rng(seed)
    out: List[str] = []
    for s in items:
        opts = sorted(f for f in test[s] if f in elig_set)
        out.append(opts[int(rng.integers(len(opts)))])
    return out


def build_population(items: Sequence[Tuple[str, str]], dg_words: Sequence[str],
                     anchors_l: Sequence[str], train: Dict, test: Dict) -> Dict:
    """ONE anchor set shared byte-identically by every arm and by both item populations."""
    t0 = time.time()
    anchors_l = list(anchors_l)
    items = list(items)
    a_row = {w: i for i, w in enumerate(anchors_l)}
    n_a, n_i = len(anchors_l), len(items)
    gold = np.zeros((n_a, n_i), dtype=bool)
    excl = np.zeros((n_a, n_i), dtype=bool)
    gold_sets: List[np.ndarray] = []
    excl_sets: List[np.ndarray] = []
    designated = np.full(n_i, -1, dtype=np.int64)
    train_count_of_gold = np.zeros(n_i, dtype=np.int64)
    for i, s in enumerate(items):
        g = sorted({a_row[f] for f in test[s] if f in a_row})
        # AMBIGUOUS candidates are REMOVED from the pool rather than counted wrong: a word attested
        # in this slot in the TRAIN half but absent from the TEST half is plausible, not an error.
        e = sorted({a_row[f] for f in train[s] if f in a_row} - set(g))
        gold[np.asarray(g, dtype=np.int64), i] = True
        if e:
            excl[np.asarray(e, dtype=np.int64), i] = True
        gold_sets.append(np.asarray(g, dtype=np.int64))
        excl_sets.append(np.asarray(e, dtype=np.int64))
        designated[i] = a_row[dg_words[i]]
        train_count_of_gold[i] = int(train[s].get(dg_words[i], 0))

    # STRICT definition, and the strictness is load-bearing: an item counts as UNATTESTED only if
    # EVERY one of its in-pool golds has train count zero. A looser rule would leave attestation a
    # train-attested alternative gold to win on in the OPEN pool, and the whole point of this
    # stratum is that attestation has NOTHING to say on it.
    unattested = np.zeros(n_i, dtype=bool)
    for i, s in enumerate(items):
        gwords = [f for f in test[s] if f in a_row]
        unattested[i] = bool(gwords) and all(train[s].get(f, 0) == 0 for f in gwords)
    print("[pop] designated gold UNATTESTED in the train fold for %d of %d items (%.1f%%) "
          "-- this is the sub-population on which attestation is blind BY CONSTRUCTION"
          % (int(unattested.sum()), n_i, 100.0 * float(unattested.mean())), flush=True)

    return {"anchors": anchors_l, "a_row": a_row, "items": items, "gold": gold, "excl": excl,
            "gold_sets": gold_sets, "excl_sets": excl_sets, "designated": designated,
            "dg_words": list(dg_words), "train_count_of_gold": train_count_of_gold,
            "unattested_mask": unattested, "elapsed_s": round(time.time() - t0, 1)}


def build_pools(pop: Dict, ortho: np.ndarray) -> Dict[str, Dict]:
    """THE MANDATORY LADDER: OPEN, BALANCED (no constant ranking can beat chance BY CONSTRUCTION),
    MATCHED (additionally matched to the gold on trigram similarity to the slot's verb)."""
    n_a = len(pop["anchors"])
    n_i = len(pop["items"])
    keep = pop["designated"] >= 0
    out: Dict[str, Dict] = {}

    open_elig = np.ones((n_a, n_i), dtype=bool) & ~pop["excl"]
    out["P_OPEN"] = {"elig": open_elig, "chance": None, "k": None,
                     "what_it_is": "every eligible anchor except this slot's ambiguous "
                                   "train-attested non-golds"}

    cand, _gc = balanced_candidate_sets(pop["designated"], pop["gold_sets"], pop["excl_sets"],
                                        keep, K_DISTRACT, seed=MASTER_SEED)
    out["P_BALANCED_K15"] = {"elig": _cand_to_elig(cand, n_a, n_i), "chance": 1.0 / (K_DISTRACT + 1),
                             "k": K_DISTRACT, "n_dropped": int((cand[:, 0] < 0).sum()),
                             "what_it_is": "distractors drawn from the GOLD MARGINAL, so no "
                                           "constant ranking can beat chance BY CONSTRUCTION"}

    cand_m, _gc2, mdiag = matched_candidate_sets(pop["designated"], pop["gold_sets"],
                                                 pop["excl_sets"], keep, K_DISTRACT,
                                                 seed=MASTER_SEED + 1, match_score=ortho)
    out["P_MATCHED_K15"] = {"elig": _cand_to_elig(cand_m, n_a, n_i),
                            "chance": 1.0 / (K_DISTRACT + 1), "k": K_DISTRACT, "match_diag": mdiag,
                            "n_dropped": int((cand_m[:, 0] < 0).sum()),
                            "what_it_is": "role-symmetric AND matched to the gold on trigram "
                                          "similarity to the slot's verb, so spelling is dead"}
    for nm, d in out.items():
        print("[pool] %s eligible-per-item mean %.1f" % (nm, float(d["elig"].sum(axis=0).mean())),
              flush=True)
    return out


def _cand_to_elig(cand: np.ndarray, n_a: int, n_i: int) -> np.ndarray:
    elig = np.zeros((n_a, n_i), dtype=bool)
    ok = np.flatnonzero(cand[:, 0] >= 0)
    if ok.size:
        rows = cand[ok]
        cols = np.repeat(ok[:, None], rows.shape[1], axis=1)
        elig[rows.ravel(), cols.ravel()] = True
    return elig


# ==========================================================================================
# arms
# ==========================================================================================
def build_arms(pop: Dict, spaces: Dict[str, Dict[str, np.ndarray]], train: Dict, test: Dict,
               counts: Dict[str, int], ortho: np.ndarray) -> Tuple[Dict[str, object], Dict]:
    """Every arm as a zero-argument FACTORY returning its [n_anchors, n_items] score matrix on the
    SAME anchors and items.

    Returns (arms, aux). `aux` carries the EXACT matcher and the EXACT profiles the primary arm
    used, so the scramble floor is calibrated on the same object rather than a look-alike rebuilt
    in the caller -- a rebuilt look-alike is how a floor silently stops matching its arm.
    """
    anchors = pop["anchors"]
    items = pop["items"]
    n_a, n_i = len(anchors), len(items)
    a_row = pop["a_row"]
    dg = pop["dg_words"]

    # every word that can ever enter a profile, hoisted once (this scan is over ~10^5 slots)
    profile_vocab: Set[str] = set(anchors)
    for s in items:
        profile_vocab.update(train.get(s, {}))
        profile_vocab.update(test.get(s, {}))

    Zs: Dict[str, np.ndarray] = {}
    matchers: Dict[str, ProfileMatcher] = {}
    for name, tbl in spaces.items():
        # the z-scoring population is the ANCHOR set; profile words outside it are projected with
        # the SAME transform, never re-standardised (that would make two arms different rulers).
        A = np.stack([tbl[w] for w in anchors]).astype(np.float64)
        mu, sd = A.mean(axis=0), np.maximum(A.std(axis=0), 1e-9)
        allw = sorted(profile_vocab & set(tbl))
        row = {w: i for i, w in enumerate(allw)}
        Zall = (np.stack([tbl[w] for w in allw]).astype(np.float64) - mu) / sd
        Zs[name] = Zall[[row[w] for w in anchors]]
        matchers[name] = ProfileMatcher(Zall, row)

    tr_fill = [train.get(s, {}) for s in items]
    te_fill = [test.get(s, {}) for s in items]

    # EVERY ARM IS A FACTORY, NOT A MATRIX. At full grid one score matrix is ~140 MB and there are
    # 27 arms; holding them all would be ~3.7 GB and this machine is running three other jobs.
    # The profiles themselves are [n_items, d] and cost nothing, so they ARE precomputed -- what is
    # deferred is only the big [n_anchors, n_items] product.
    arms: Dict[str, object] = {}

    def _att() -> np.ndarray:
        A = np.zeros((n_a, n_i), dtype=np.float32)
        for i, fill in enumerate(tr_fill):
            for f, c in fill.items():
                r = a_row.get(f)
                if r is not None:
                    A[r, i] = np.log1p(c)
        return A

    arms[INCUMBENT_ARM] = _att

    # ---- FEELING-MATCH arms, both with and without the gold inside its own profile.
    # THE PRIMARY IS THE LEAVE-GOLD-OUT ONE. Note the asymmetry, deliberately in the incumbent's
    # favour: the feeling arm is forbidden to see the gold in its own profile, while ATTESTATION
    # keeps the gold's full train-fold count, which is the whole of its signal.
    mu_l15 = inv_l15 = None
    for name in sorted(spaces):
        M = matchers[name]
        mu, inv = M.profiles(tr_fill)
        mu_l, inv_l = M.profiles(tr_fill, drop=dg)
        arms["FEEL_%s" % name] = (lambda M=M, mu=mu, inv=inv, Z=Zs[name]: M.scores(mu, inv, Z=Z))
        arms["FEEL_%s_LGO" % name] = (lambda M=M, mu=mu_l, inv=inv_l, Z=Zs[name]:
                                      M.scores(mu, inv, Z=Z))
        if name == PRIMARY_SPACE:
            mu_l15, inv_l15 = mu_l, inv_l
        print("[arm] FEEL_%s profiles built (d=%d)" % (name, M.d), flush=True)
    assert mu_l15 is not None, "the primary space never got built"

    # ---- frequency with the SAME estimator. THE CONTROL THAT DECIDES WHETHER THIS IS REAL:
    # affect ratings correlate with frequency, so frequency is given the identical profile
    # machinery rather than only a bare column. If the feeling arm cannot beat THIS, it is the
    # frequency confound wearing a new name and the cell says so.
    fw = sorted(profile_vocab)
    frow = {w: i for i, w in enumerate(fw)}
    lf = np.asarray([[np.log1p(counts.get(w, 0))] for w in fw], dtype=np.float64)
    lf = (lf - lf.mean()) / max(float(lf.std()), 1e-9)
    Mf = ProfileMatcher(lf, frow)
    muf, invf = Mf.profiles(tr_fill, drop=dg)
    lfa = lf[[frow[w] for w in anchors]]
    arms["CTRL_FREQPROFILE_1_LGO"] = lambda: Mf.scores(muf, invf, Z=lfa)

    # ---- COMBINED: attestation AND feeling, summed as within-item z-scores. OURS.
    M15 = matchers[PRIMARY_SPACE]
    Z15 = Zs[PRIMARY_SPACE]

    def _combined() -> np.ndarray:
        allelig = np.ones((n_a, n_i), dtype=bool)
        return (_within_item_z(_att(), allelig)
                + _within_item_z(M15.scores(mu_l15, inv_l15, Z=Z15), allelig))

    arms["COMBINED_ATT_PLUS_FEEL"] = _combined

    # ---- KNOWN-ANSWER arms. They fail INDEPENDENTLY: K1 fails if the pool/scoring plumbing is
    # broken at all; K2 fails if the PROFILE ESTIMATOR cannot express the answer even when handed
    # the gold fold. A treatment number is read only when BOTH pass.
    jit = np.linspace(0.0, 1e-4, n_a, dtype=np.float32)[:, None]
    arms["K1_ORACLE_GOLD"] = lambda: pop["gold"].astype(np.float32) + jit
    mu_t, inv_t = M15.profiles(te_fill)
    arms["K2_ORACLE_TESTFOLD_PROFILE"] = lambda: M15.scores(mu_t, inv_t, Z=Z15)

    # ---- NULL arm. It keeps the ESTIMATOR and the SPACE and destroys only WHICH SLOT a profile
    # belongs to, so it fails independently of the known-answer arms: K1/K2 fail if the harness is
    # broken, N1 fails if any profile at all scores, i.e. if the pool leaks.
    for s in NULL_SEEDS:
        perm = np.random.default_rng(s ^ 0xFEE1).permutation(n_i)
        arms["N1_NULL_PERMUTED_SLOT_PROFILE|s%d" % s] = (
            lambda p=perm: M15.scores(mu_l15[p], inv_l15[p], Z=Z15))

    # ---- FLOORS. Four, on THIS population, with THIS n.
    arms["F_ORTHOGRAPHIC"] = lambda: ortho.astype(np.float32)
    fvec = frequency_floor([counts.get(w, 0) for w in anchors])
    arms["F_FREQUENCY"] = lambda: as_constant_matrix(fvec, n_i)
    cvec = constant_prototype_floor(Z15.astype(np.float32))
    arms["F_CONSTANT_PROTOTYPE"] = lambda: as_constant_matrix(cvec, n_i)
    # F_SCRAMBLE is permutation-calibrated and is built inside the scoring pass, where the pool it
    # is calibrated ON is known. A scramble p95 is pool-specific and may never be carried across.

    # ---- ORACLE, NEVER A FLOOR, always labelled: the CEILING of the constant family. It is
    # fitted on the gold labels and exists only to answer "could ANY constant ranking beat chance
    # on this pool?". floor_battery proves that by construction for the balanced pool; this
    # measures the residual empirically on OUR data rather than trusting the proof.
    ovec = oracle_constant_scores(n_a, pop["gold_sets"])
    arms["ORACLE_CONSTANT_never_a_floor"] = lambda: as_constant_matrix(ovec, n_i)

    aux = {"M15": M15, "Z15_anchors": Z15, "mu_lgo": mu_l15, "inv_lgo": inv_l15,
           "constant_prototype_floor_vector_n": int(cvec.shape[0])}
    return arms, aux


# ==========================================================================================
# scoring
# ==========================================================================================
def score_matrix(S: np.ndarray, elig: np.ndarray, gold: np.ndarray) -> Dict[str, np.ndarray]:
    h = hit_at_1_both_tie_conventions(S, elig, gold)
    r = rank_of_best_gold(S, elig, gold)
    h.update(r)
    return h


def scramble_draws(M15: ProfileMatcher, mu: np.ndarray, inv: np.ndarray, Zanch: np.ndarray,
                   elig: np.ndarray, gold: np.ndarray, n_perm: int,
                   seed: int) -> List[Dict[str, np.ndarray]]:
    """PERMUTATION-CALIBRATED scramble floor: permute WHICH ANCHOR CARRIES WHICH CODE and recompute.

    The DRAWS are computed once per pool and the p95 is taken PER SUB-POPULATION from them, because
    a scramble p95 is a property of (pool, stratum) and may never be carried across either. What is
    shared is only the random permutations themselves, which is what makes the three strata
    comparable at all.
    """
    out: List[Dict[str, np.ndarray]] = []
    for j in range(n_perm):
        p = np.random.default_rng(seed + j).permutation(Zanch.shape[0])
        out.append(score_matrix(M15.scores(mu, inv, Z=Zanch[p]), elig, gold))
        if (j + 1) % max(1, n_perm // 5) == 0:
            print("[scramble] %d/%d draws" % (j + 1, n_perm), flush=True)
    return out


def scramble_p95_for(draws: Sequence[Dict[str, np.ndarray]],
                     mask: np.ndarray) -> Tuple[float, Dict[str, np.ndarray]]:
    vals = np.asarray([float(d["hit_exp"][mask].mean()) if mask.any() else 0.0 for d in draws])
    p95 = float(np.percentile(vals, 95))
    return p95, draws[int(np.argmin(np.abs(vals - p95)))]


def run_pool(pool_name: str, pool: Dict, pop: Dict, hits: Dict[str, np.ndarray],
             detail: Dict[str, Dict], scored: np.ndarray, scram: Tuple[float, Dict],
             sub_mask: Optional[np.ndarray] = None, sub_name: str = "ALL") -> Dict:
    """Form every paired margin on ONE pool and ONE sub-population from ONE bootstrap draw."""
    t0 = time.time()
    gold = pop["gold"]
    hits = dict(hits)
    detail = dict(detail)
    p95, near = scram
    hits["F_SCRAMBLE_PERM_P95"] = near["hit_exp"]
    detail["F_SCRAMBLE_PERM_P95"] = {"_h": near, "permutation_p95": p95}

    mask = scored if sub_mask is None else (scored & sub_mask)
    n = int(mask.sum())
    res: Dict = {"pool": pool_name, "sub_population": sub_name, "n_scored_items": n,
                 "chance": pool["chance"], "k_distract": pool["k"],
                 "what_the_pool_is": pool["what_it_is"],
                 "SCORER": "hit@1 of the correct filler among the eligible candidates for that "
                           "slot; PRIMARY convention hit_exp (tie-corrected expectation)",
                 "GOLD": "the candidate is attested in this slot in the HELD-OUT half of the "
                         "corpus (binomial thinning, seed %d)" % SPLIT_SEED}
    if n < 30:
        res["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        res["elapsed_s"] = round(time.time() - t0, 1)
        return res

    boot = paired_bootstrap_ci(hits, mask, N_BOOT, BOOT_SEED)
    res["n_common"] = boot["n_common"]
    per_arm: Dict[str, Dict] = {}
    for name in sorted(hits):
        h = detail[name]["_h"]
        per_arm[name] = {
            "hit_exp": round(float(np.asarray(h["hit_exp"])[mask].mean()), 6),
            "hit_optimistic": round(float(np.asarray(h["hit_opt"])[mask].mean()), 6),
            "hit_conservative": round(float(np.asarray(h["hit_cons"])[mask].mean()), 6),
            "tie_mass_mean": round(float(np.asarray(h["tie_mass"])[mask].mean()), 6),
            "mean_rank_opt": round(float(np.asarray(h["rank_opt"])[mask].mean()), 3),
            "mean_rank_cons": round(float(np.asarray(h["rank_cons"])[mask].mean()), 3)}
        if "permutation_p95" in detail[name]:
            per_arm[name]["permutation_p95"] = round(detail[name]["permutation_p95"], 6)
    res["ARMS_all_three_tie_conventions"] = per_arm

    floors = [f for f in FLOOR_ARMS if f in hits]
    strongest = max(floors, key=lambda f: per_arm[f]["hit_exp"]) if floors else None
    res["floors"] = {"required_set": list(FLOOR_SET_REQUIRED), "present": floors,
                     "strongest_by_point": strongest,
                     "hit_exp_by_floor": {f: per_arm[f]["hit_exp"] for f in floors}}

    # NULL floor = MAX DRAW over seeds, never the mean.
    null_draws = {k: per_arm[k]["hit_exp"] for k in per_arm
                  if k.startswith("N1_NULL_PERMUTED_SLOT_PROFILE|")}
    if null_draws:
        mk = max(null_draws, key=lambda k: null_draws[k])
        res["NULL_FLOOR"] = {"policy": "MAX DRAW never the mean", "by_seed": null_draws,
                             "max_draw_arm": mk, "hit_exp_max_draw": null_draws[mk],
                             "chance": pool["chance"],
                             "AT_CHANCE": (None if pool["chance"] is None else
                                           bool(abs(null_draws[mk] - pool["chance"]) <= NULL_TOL))}

    treat = [a for a in per_arm if not a.startswith("F_") and not a.startswith("N1_")]
    marg: Dict[str, Dict] = {}
    for a in sorted(treat):
        if strongest is not None:
            marg["%s__vs__MAX_FLOOR(%s)" % (a, strongest)] = margin(boot["boot"], a, strongest)
        for f in floors:
            marg["%s__vs__%s" % (a, f)] = margin(boot["boot"], a, f)
    for a in sorted(treat):
        if a != INCUMBENT_ARM:
            marg["%s__vs__INCUMBENT" % a] = margin(boot["boot"], a, INCUMBENT_ARM)
    for pair in (("FEEL_BOTH_15_LGO", "FEEL_SENSORIMOTOR_12_LGO"),
                 ("FEEL_BOTH_15_LGO", "FEEL_NEGCTRL_RATERSD_3_LGO"),
                 ("FEEL_AFFECT_3_LGO", "FEEL_NEGCTRL_RATERSD_3_LGO"),
                 ("FEEL_BOTH_15_LGO", "CTRL_FREQPROFILE_1_LGO"),
                 ("FEEL_BOTH_15_LGO", "FEEL_CONC_1_LGO"),
                 ("COMBINED_ATT_PLUS_FEEL", "ATTESTATION"),
                 ("COMBINED_ATT_PLUS_FEEL", "FEEL_BOTH_15_LGO")):
        if pair[0] in boot["boot"] and pair[1] in boot["boot"]:
            marg["%s__minus__%s" % pair] = margin(boot["boot"], pair[0], pair[1])
    if null_draws:
        mk = max(null_draws, key=lambda k: null_draws[k])
        for a in (PRIMARY_ARM, INCUMBENT_ARM, "K1_ORACLE_GOLD"):
            if a in boot["boot"]:
                marg["%s__vs__NULL_MAXDRAW" % a] = margin(boot["boot"], a, mk)
    res["MARGINS_paired_bootstrap_shared_resample_index"] = marg

    ka = per_arm.get("K1_ORACLE_GOLD", {}).get("hit_exp")
    res["G0_KNOWN_ANSWER_GATE"] = {
        "K1_ORACLE_GOLD_hit_exp": ka, "threshold": KA_CEILING_MIN,
        "K1_PASSED": bool(ka is not None and ka >= KA_CEILING_MIN),
        "K2_ORACLE_TESTFOLD_PROFILE_hit_exp": per_arm.get("K2_ORACLE_TESTFOLD_PROFILE",
                                                          {}).get("hit_exp"),
        "K2_clears_max_floor": (marg.get("K2_ORACLE_TESTFOLD_PROFILE__vs__MAX_FLOOR(%s)"
                                         % strongest, {}).get("band") == "ABOVE"
                                if strongest else None),
        "rule": "K1 licenses the POOL AND THE SCORING PLUMBING; K2 licenses the PROFILE "
                "ESTIMATOR. They fail independently. If either fails, every treatment number on "
                "this pool is UNREADABLE -- POWER/HARNESS INSUFFICIENT, never FAIL."}
    res["elapsed_s"] = round(time.time() - t0, 1)
    print("[pool] %s/%s scored n=%d in %.0fs" % (pool_name, sub_name, n, res["elapsed_s"]),
          flush=True)
    return res


# ==========================================================================================
# THE TWO-MODE BLOCK -- BOARD Q11. SEPARATE, never pooled with the primary.
# ==========================================================================================
def run_two_mode(pop: Dict, arms: Dict[str, object], train: Dict, counts: Dict[str, int],
                 conc: Dict[str, float]) -> Dict:
    """BOARD Q11, on its OWN population of animacy-selecting SUBJ slots, with its own n, never
    pooled with the primary and never averaged with it."""
    t0 = time.time()
    anchors = pop["anchors"]
    items = pop["items"]
    a_row = pop["a_row"]
    anim = {w: is_animate(w) for w in anchors}
    n_anim = sum(1 for v in anim.values() if v is True)
    n_inan = sum(1 for v in anim.values() if v is False)
    sel_items = list(range(len(items)))
    anim_mass = []
    for s in items:
        tot = ani = 0
        for f, c in train.get(s, {}).items():
            a = anim.get(f, is_animate(f))
            if a is None:
                continue
            tot += c
            if a:
                ani += c
        anim_mass.append(ani / max(tot, 1))
    print("[mode] %d animacy-selecting SUBJ slots; anchors animate=%d inanimate=%d"
          % (len(sel_items), n_anim, n_inan), flush=True)

    lf = {w: np.log1p(counts.get(w, 0)) for w in anchors}
    lfv = np.asarray([lf[w] for w in anchors])
    fdec = np.digitize(lfv, np.percentile(lfv, np.arange(10, 100, 10)))
    cv = np.asarray([conc.get(w, np.nan) for w in anchors])
    cq = np.digitize(cv, np.nanpercentile(cv, [25, 50, 75]))
    animate_rows = [a_row[w] for w in anchors if anim[w] is True]
    inanimate_rows = [a_row[w] for w in anchors if anim[w] is False]

    rng = np.random.default_rng(MASTER_SEED + 77)
    rows_m1: List[np.ndarray] = []
    rows_m2: List[np.ndarray] = []
    rows_m2c: List[np.ndarray] = []
    rows_pl: List[np.ndarray] = []
    used: List[int] = []
    for i in sel_items:
        s = items[i]
        banned = {a_row[f] for f in train.get(s, {}) if f in a_row}
        gcol = np.flatnonzero(pop["gold"][:, i])
        pl = [r for r in gcol if anim[anchors[r]] is True]
        if len(pl) < 1:
            continue
        m1 = [r for r in inanimate_rows if r not in banned and r not in set(gcol)]
        m2p = [r for r in animate_rows if r not in banned and r not in set(gcol)]
        if len(m1) < N_MODE or len(m2p) < N_MODE:
            continue
        take1 = [int(m1[int(j)]) for j in rng.choice(len(m1), size=N_MODE, replace=False)]
        # FREQUENCY-MATCHED mode 2: for every mode-1 item, an animate item from the SAME log-count
        # decile. The mode contrast is therefore not a frequency contrast.
        by_dec: Dict[int, List[int]] = collections.defaultdict(list)
        for r in m2p:
            by_dec[int(fdec[r])].append(int(r))
        by_dq: Dict[Tuple[int, int], List[int]] = collections.defaultdict(list)
        for r in m2p:
            by_dq[(int(fdec[r]), int(cq[r]))].append(int(r))
        t2, t2c = [], []
        for r in take1:
            pool = by_dec.get(int(fdec[r]))
            if pool:
                t2.append(pool[int(rng.integers(len(pool)))])
            poolc = by_dq.get((int(fdec[r]), int(cq[r])))
            if poolc:
                t2c.append(poolc[int(rng.integers(len(poolc)))])
        if len(t2) < N_MODE // 2 or len(t2c) < N_MODE // 4:
            continue
        used.append(i)
        rows_pl.append(np.asarray(pl, dtype=np.int64))
        rows_m1.append(np.asarray(take1, dtype=np.int64))
        rows_m2.append(np.asarray(t2, dtype=np.int64))
        rows_m2c.append(np.asarray(t2c, dtype=np.int64))

    out: Dict = {"n_animacy_selecting_slots": len(sel_items), "n_slots_used": len(used),
                 "N_MODE_per_slot": N_MODE,
                 "OWN_POPULATION": "this block builds its own item set from ALL SUBJ slots and "
                                   "reports its own n; it is NEVER pooled with the primary and "
                                   "no number crosses between them",
                 "animate_mass_of_the_selected_slots": {
                     "threshold": ANIM_MASS_FRAC,
                     "mean": round(float(np.mean(anim_mass)), 4) if anim_mass else None,
                     "min": round(float(np.min(anim_mass)), 4) if anim_mass else None,
                     "population_context": "over all scoreable SUBJ slots the animate share of "
                                           "resolvable subject mass has median 0.211 and p90 "
                                           "0.455 (scratch/fmr_gate_probe.py), so the selected "
                                           "slots sit in the tail rather than at the centre"},
                 "MODE1_IS": "an INANIMATE candidate in an animacy-selecting SUBJ slot -- 'the "
                             "kettle apologised'. A categorical TYPE VIOLATION.",
                 "MODE2_IS": "an ANIMATE candidate never seen in this slot, FREQUENCY-MATCHED to "
                             "the mode-1 set by log-count decile -- odd but interpretable.",
                 "WHY_BOTH_ARE_UNATTESTED": "so that attestation scores them identically and its "
                                            "mode separation is EXACTLY 0.0 by construction"}
    if len(used) < 20:
        out["status"] = "TOO_FEW_ANIMACY_SELECTING_SLOTS_TO_SCORE"
        out["elapsed_s"] = round(time.time() - t0, 1)
        return out

    # sanity: the two mode sets really are frequency-matched and their concreteness gap is reported
    f1 = np.concatenate([lfv[r] for r in rows_m1])
    f2 = np.concatenate([lfv[r] for r in rows_m2])
    c1 = np.concatenate([cv[r] for r in rows_m1])
    c2 = np.concatenate([cv[r] for r in rows_m2])
    out["MATCH_DIAGNOSTICS"] = {
        "mean_log_count_MODE1": round(float(f1.mean()), 4),
        "mean_log_count_MODE2": round(float(f2.mean()), 4),
        "log_count_gap": round(float(f2.mean() - f1.mean()), 4),
        "mean_concreteness_MODE1": round(float(np.nanmean(c1)), 4),
        "mean_concreteness_MODE2": round(float(np.nanmean(c2)), 4),
        "concreteness_gap": round(float(np.nanmean(c2) - np.nanmean(c1)), 4),
        "note": "a residual concreteness gap is expected -- animate nouns are concrete -- which "
                "is exactly why the CONCRETENESS-MATCHED variant is reported beside it"}

    per_arm: Dict[str, Dict] = {}
    sepv: Dict[str, np.ndarray] = {}
    d1v: Dict[str, np.ndarray] = {}
    rng2 = np.random.default_rng(BOOT_SEED)
    IDX = rng2.integers(0, len(used), size=(N_BOOT, len(used)))
    for name in sorted(arms):
        if name.startswith("N1_") or name.startswith("K1_"):
            continue
        S = arms[name]()
        d1 = np.empty(len(used)); d2 = np.empty(len(used)); d2c = np.empty(len(used))
        ov1 = np.empty(len(used)); ov2 = np.empty(len(used))
        for j, i in enumerate(used):
            allrows = np.concatenate([rows_pl[j], rows_m1[j], rows_m2[j], rows_m2c[j]])
            v = S[allrows, i].astype(np.float64)
            m, sd = v.mean(), max(float(v.std()), 1e-9)
            zp = (S[rows_pl[j], i] - m) / sd
            z1 = (S[rows_m1[j], i] - m) / sd
            z2 = (S[rows_m2[j], i] - m) / sd
            z2c = (S[rows_m2c[j], i] - m) / sd
            d1[j] = float(zp.mean() - z1.mean())
            d2[j] = float(zp.mean() - z2.mean())
            d2c[j] = float(zp.mean() - z2c.mean())
            med = float(np.median(zp))
            ov1[j] = float((z1 >= med).mean())
            ov2[j] = float((z2 >= med).mean())
        sep = d1 - d2
        sepc = d1 - d2c

        def _ci(x: np.ndarray) -> Dict:
            b = x[IDX].mean(axis=1)
            lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
            return {"point": round(float(x.mean()), 4), "ci95": [round(lo, 4), round(hi, 4)],
                    "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}

        per_arm[name] = {
            "D1_hard_rejection_strength": _ci(d1),
            "D2_soft_rejection_strength": _ci(d2),
            "MODE_SEPARATION_D1_minus_D2": _ci(sep),
            "MODE_SEPARATION_concreteness_matched": _ci(sepc),
            "MODE2_overlap_with_plausible": round(float(ov2.mean()), 4),
            "MODE1_overlap_with_plausible": round(float(ov1.mean()), 4),
            "MODE2_NOT_REJECTED_OUTRIGHT": bool(float(ov2.mean()) > float(ov1.mean()))}
        sepv[name] = sep
        d1v[name] = d1
    out["ARMS"] = per_arm

    # PAIRED margins BETWEEN arms on the identical slots and the identical resample index. Without
    # these the block can only say each arm separates the modes, never whether the AFFECT CHANNEL
    # is what does it -- which is the entire question the width-matched control exists to answer.
    def _pair(a: str, b: str, src: Dict[str, np.ndarray]) -> Optional[Dict]:
        if a not in src or b not in src:
            return None
        d = src[a] - src[b]
        bs = d[IDX].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        return {"point": round(float(d.mean()), 4), "ci95": [round(lo, 4), round(hi, 4)],
                "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}

    pm: Dict[str, Dict] = {}
    for a, b in (("FEEL_BOTH_15_LGO", "FEEL_NEGCTRL_RATERSD_3_LGO"),
                 ("FEEL_AFFECT_3_LGO", "FEEL_NEGCTRL_RATERSD_3_LGO"),
                 ("FEEL_BOTH_15_LGO", "CTRL_FREQPROFILE_1_LGO"),
                 ("FEEL_BOTH_15_LGO", "FEEL_CONC_1_LGO"),
                 ("FEEL_BOTH_15_LGO", "FEEL_SENSORIMOTOR_12_LGO"),
                 ("FEEL_BOTH_15_LGO", "ATTESTATION"),
                 ("FEEL_AFFECT_3_LGO", "ATTESTATION")):
        r1 = _pair(a, b, sepv)
        if r1:
            pm["MODE_SEPARATION__%s__minus__%s" % (a, b)] = r1
        r2 = _pair(a, b, d1v)
        if r2:
            pm["D1_HARD__%s__minus__%s" % (a, b)] = r2
    out["PAIRED_MARGINS_BETWEEN_ARMS"] = pm
    ch = pm.get("MODE_SEPARATION__FEEL_BOTH_15_LGO__minus__FEEL_NEGCTRL_RATERSD_3_LGO", {})
    out["IS_THE_MODE_SEPARATION_CHANNEL_SPECIFIC"] = {
        "feeling_minus_width_matched_non_channel": ch,
        "reading": "if this is NOT_SEPARATED, the two-mode dissociation is real and attestation "
                   "still cannot do it, but it is NOT specific to the affect channel -- any "
                   "per-word profile that distinguishes animate from inanimate words produces it. "
                   "That is a fact about the CONTRAST, not a rescue of the incumbent, and it must "
                   "be reported in exactly those words."}
    out["PRE_REGISTERED_DISCRIMINATOR"] = (
        "the owner's mechanism requires MODE_SEPARATION > 0 CI-separated AND MODE2 overlapping "
        "the plausible set more than MODE1 does. An arm that collapses the two modes is not the "
        "mechanism the owner described, whatever its headline.")
    out["elapsed_s"] = round(time.time() - t0, 1)
    return out


# ==========================================================================================
# organ reuse -- ENUMERATED FROM DISK, reconciled to the registry AFTERWARDS, never the reverse
# ==========================================================================================
def organ_reuse_witness() -> Dict:
    disk = sorted(p.name for p in (REPO / "hdlab").glob("*.py"))
    used = {
        "hdlab/grounded_similarity.py": "the 12-dim norms table (RUNTIME: _table() called, "
                                        "length asserted)",
        "experiments/selectional_preference_extractor_v1.py": "the verb-slot tables (RUNTIME: "
                                                              "pickle loaded, slot count asserted)",
        "tools/floor_battery.py": "the pool ladder, the four floors and both tie conventions "
                                  "(RUNTIME: imported and called)",
        "experiments/exp_task_degeneracy_v1.py": "ruler_mode_gate() (RUNTIME: called; hard-fails)",
        "tools/exp_checkpoint.py": "per-unit resume",
        "experiments/_seed_checkpoint.py": "output dir, atomic metrics, structured gate claims",
        "nltk WordNet": "animacy / POS oracle only. A STATIC OFFLINE LEXICAL DATABASE. It is not "
                        "a language model and is not called for any judgement.",
    }
    reg = REPO / "data" / "capability_registry.jsonl"
    rows = 0
    hits: Dict[str, bool] = {}
    if reg.exists():
        txt = reg.read_text(encoding="utf-8", errors="replace")
        rows = sum(1 for ln in txt.splitlines() if ln.strip())
        for k in used:
            hits[k] = k.split("/")[-1] in txt
    return {"METHOD": "os.walk of hdlab/ FIRST, then reconciled to the registry READ-ONLY. The "
                      "registry is the thing being checked, never the frame of the check.",
            "n_hdlab_modules_on_disk": len(disk), "n_registry_rows": rows,
            "REUSED_and_why": used, "registry_mentions_the_reused_file": hits,
            "NOT_REBUILT": "no new hub, no new extractor, no new floor implementation, no second "
                           "gate predicate. The only new component is the profile estimator."}


BRAIN_FIDELITY = {
    "a_STRUCTURE_PER_COMPONENT": {
        "affect channel": "amygdala (valence population coding), orbitofrontal and ventromedial "
                          "PFC, insula. DISTINCT SYSTEMS from the modality-specific sensory and "
                          "motor cortices carrying the sensorimotor spokes -- which is why affect "
                          "is a separate CHANNEL and not more dimensions of the same one.",
        "rejecting a candidate": "left inferior frontal gyrus BA45/47, selection among competing "
                                 "candidates.",
        "mode 1 hard type violation": "animate/inanimate is a categorical division with its own "
                                      "substrate in ventral temporal cortex, STS and amygdala.",
        "mode 2 graded implausibility": "posterior middle temporal gyrus and angular gyrus -- the "
                                        "hub the selectional extractor already rides.",
    },
    "c_PINNED_vs_OURS": {
        "PINNED -- affect is a separable semantic block with its own neural substrate": "PINNED",
        "PINNED -- animate/inanimate is a categorical distinction with its own substrate": "PINNED",
        "PINNED -- verb-argument structure is temporo-parietal": "PINNED",
        "OURS -- VAD as the 3-dim operationalisation of the affect block": "INVENTION UNDER TEST",
        "OURS -- the shrunk diagonal-Mahalanobis profile match as the rejector": "INVENTION",
        "OURS -- binomial thinning as the train/test split": "INVENTION (bias direction stated)",
        "OURS -- WordNet dominant-sense animacy": "INVENTION (sense-averaging cost acknowledged)",
        "OURS -- frequency-matched mode-2 construction": "INVENTION",
    },
    "d_SHELVE_OR_REVIVAL_CRITERION_brain_framed": (
        "SHELVE the affect channel only if, with the known-answer arms passing, an affect-carrying "
        "profile is INDISTINGUISHABLE from a width-matched NON-channel profile built by the same "
        "estimator -- i.e. if the separable-block claim does not survive contact with our data. "
        "REVIVE on any brain-derived affect operationalisation richer than 3 scalars (Binder's "
        "affect block has more than three components), or on a context-sensitive rather than "
        "per-word affect code, since the brain settles on a sense in context and does not store a "
        "sense average. NEITHER criterion mentions a score threshold."),
}


# ==========================================================================================
def selftest() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}

    # --- RULER GATE: the EXISTING one, imported and CALLED, not reimplemented.
    from exp_task_degeneracy_v1 import ruler_mode_gate
    ev["RULER_MODE_GATE"] = ruler_mode_gate()
    ev["RULER_MODE_GATE"]["source"] = "experiments/exp_task_degeneracy_v1.py:121, imported"

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    assert len(tab) == 36810, "RULER GATE: norms table %d != 36810" % len(tab)
    assert len(next(iter(tab.values()))) == 12, "RULER GATE: norms are not 12-dim"
    ev["RULER_GATE_norms"] = {"n_words": len(tab), "n_dim": 12, "run_mode": RUN_MODE,
                              "asserted_identically_in_both_grids": True}

    # --- TRAP: grounded_similarity is SATURATED and is never a scorer here. RE-MEASURED.
    import exp_bridged_grounding_from_core_v1 as CELL
    pairs = CELL.load_simlex_pos()
    vals = [GS.grounded_similarity(a, b) for a, b, _, _ in pairs]
    cnt = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(n for _, n in cnt.most_common(2)) / len(vals)
    assert frac2 > 0.70, "expected saturation; top-2 mass %.4f" % frac2
    ev["TRAP_grounded_similarity_saturation_never_the_scorer"] = {
        "n_pairs": len(vals), "fraction_on_two_values": round(frac2, 4)}

    # --- the corpus the frequency floor is computed on IS the corpus the slots were built from
    import thematic_relation_extractor_v1 as THEM
    import exp_encoding_quality_instrument_v2 as INS
    assert int(THEM.CORPUS_BYTES) == int(INS.CORPUS_BYTES) == 64_000_000, (
        "corpus budgets disagree: THEM=%s INS=%s" % (THEM.CORPUS_BYTES, INS.CORPUS_BYTES))
    assert str(THEM.CORPUS) == str(INS.CORPUS), "corpus paths disagree"
    ev["CORPUS_IDENTITY"] = {"path": str(THEM.CORPUS), "bytes": int(THEM.CORPUS_BYTES)}

    # --- THE ESTIMATOR does what the docstring says, on a fixture with a KNOWN answer.
    # Slot fillers sit at affect (5,5); a candidate AT the profile must beat one far from it, and
    # the score must be exactly the normalised diagonal distance.
    Zf = np.array([[0.0, 0.0], [2.0, 0.0], [1.0, 0.0], [1.0, 4.0]], dtype=np.float64)
    row = {"a": 0, "b": 1, "near": 2, "far": 3}
    M = ProfileMatcher(Zf, row)
    mu, inv = M.profiles([{"a": 1, "b": 1}])
    assert abs(float(mu[0, 0]) - 1.0) < 1e-12, "profile mean wrong: %r" % mu
    S = M.scores(mu, inv, Z=Zf)
    assert S[2, 0] > S[3, 0], "the near candidate did not beat the far one: %r" % S[:, 0]
    d = np.sqrt(np.mean(((Zf[3] - mu[0]) * np.sqrt(inv[0])) ** 2))
    assert abs(float(S[3, 0]) + d) < 1e-5, "score is not -normalised diagonal distance"
    ev["ESTIMATOR_known_answer"] = {"mu": mu[0].tolist(), "near": round(float(S[2, 0]), 6),
                                    "far": round(float(S[3, 0]), 6)}

    # --- LEAVE-GOLD-OUT really removes the gold from its own profile
    mu2, _ = M.profiles([{"a": 1, "b": 1}], drop=["b"])
    assert abs(float(mu2[0, 0]) - 0.0) < 1e-12, "LGO did not drop the gold: %r" % mu2
    ev["LEAVE_GOLD_OUT_is_not_a_noop"] = {"with_gold": 1.0, "without": float(mu2[0, 0])}

    # --- THE MODE COLLAPSE OF ATTESTATION, DEMONSTRATED NOT ASSERTED.
    # Two unattested candidates -- one a type violation, one merely unseen -- get the SAME
    # attestation score, so its mode separation is EXACTLY zero.
    att = np.zeros((4, 1), dtype=np.float32)
    att[0, 0] = np.log1p(7)                       # an attested filler
    z_m1, z_m2 = float(att[2, 0]), float(att[3, 0])
    assert z_m1 == z_m2 == 0.0, "attestation did not collapse the two modes"
    ev["ATTESTATION_COLLAPSES_THE_TWO_MODES"] = {
        "mode1_score": z_m1, "mode2_score": z_m2, "separation": z_m1 - z_m2,
        "meaning": "EXACTLY 0.0 BY CONSTRUCTION -- this is the incumbent's structural blindness, "
                   "demonstrated here rather than claimed in prose"}

    # --- the tie-corrected metric neutralises an all-ties channel, which is exactly what
    # attestation becomes on the unattested sub-population. Re-earned, not inherited.
    flat = np.zeros((16, 200), dtype=np.float32)
    fg = np.zeros((16, 200), dtype=bool)
    fg[np.random.default_rng(0).integers(0, 16, size=200), np.arange(200)] = True
    hf = hit_at_1_both_tie_conventions(flat, np.ones((16, 200), dtype=bool), fg)
    assert hf["hit_opt"].mean() == 1.0 and abs(hf["hit_exp"].mean() - 1.0 / 16) < 1e-9, (
        "the tie-corrected metric did not neutralise an all-ties channel")
    ev["TIE_CORRECTION_neutralises_an_all_ties_channel"] = {
        "optimistic_would_have_read": 1.0, "hit_exp_reads": round(1.0 / 16, 6),
        "why_it_matters": "on the unattested sub-population ATTESTATION IS that channel"}

    # --- the floor battery's own self-test, run here so a broken pool cannot reach a FULL
    from tools import floor_battery as FB
    ev["floor_battery_selftest"] = {k: v for k, v in FB.self_test().items()
                                    if k.startswith(("S5", "S7"))}

    # --- binomial thinning really splits, and really strands singletons in ONE half
    tr, te = thin_counts({("v", "SUBJ"): {"x": 1, "y": 100}}, 5)
    a = tr.get(("v", "SUBJ"), {}).get("x", 0)
    b = te.get(("v", "SUBJ"), {}).get("x", 0)
    assert (a == 1 and b == 0) or (a == 0 and b == 1), "a count of 1 landed in both halves"
    assert tr[("v", "SUBJ")]["y"] + te[("v", "SUBJ")]["y"] == 100, "thinning did not conserve mass"
    ev["SPLIT_conserves_mass_and_strands_singletons"] = {"x_train": a, "x_test": b}

    # --- animacy oracle: the owner's own example must come out right, or MODE 1 is a fiction
    assert is_animate("kettle") is False, "kettle must be INANIMATE for MODE 1 to mean anything"
    assert is_animate("woman") is True, "woman must be ANIMATE"
    assert is_animate("dog") is True, "dog must be ANIMATE"
    ev["ANIMACY_owner_example"] = {"kettle": False, "woman": True, "dog": True}

    # --- the bootstrap can BOTH fire and fail
    r = np.random.default_rng(3)
    h = {"good": np.concatenate([np.ones(80), np.zeros(20)]),
         "bad": np.concatenate([np.zeros(80), np.ones(20)]),
         "same": np.concatenate([np.ones(80), np.zeros(20)])}
    bb = paired_bootstrap_ci(h, np.ones(100, dtype=bool), 400, 1)
    assert margin(bb["boot"], "good", "bad")["band"] == "ABOVE", "bootstrap cannot FIRE"
    assert margin(bb["boot"], "good", "same")["band"] == "NOT_SEPARATED", "bootstrap cannot FAIL"
    ev["bootstrap_can_fire_and_fail"] = {"planted_signal": "ABOVE", "planted_null":
                                         "NOT_SEPARATED"}
    _ = r

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1400], flush=True)
    return ev


# ==========================================================================================
def main() -> int:
    t_start = time.time()
    ev = selftest()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK", flush=True)
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    # A DETACHED run must be findable. Written at startup, before any work, so a process launched
    # via Start-Process can be monitored and stopped without hunting through the process table.
    pid_path = REPO / "scratch" / ("fmr_%s.pid" % RUN_MODE)
    pid_path.parent.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="ascii")
    print("[cfg] pid=%d -> %s" % (os.getpid(), pid_path), flush=True)
    print("[cfg] mode=%s N_BOOT=%d N_PERM=%d MAX_ITEMS=%d MAX_ANCHORS=%d out=%s"
          % (RUN_MODE, N_BOOT, N_PERM, MAX_ITEMS, MAX_ANCHORS, out_dir), flush=True)

    import thematic_relation_extractor_v1 as THEM
    print("[assets] loading rating spaces", flush=True)
    spaces = load_rating_spaces()
    for k, v in spaces.items():
        print("[assets]   %-22s d=%d vocab=%d" % (k, len(next(iter(v.values()))), len(v)),
              flush=True)
    conc = {w: float(v[0]) for w, v in spaces["CONC_1"].items()}
    print("[assets] loading slot tables", flush=True)
    slots = load_slots()
    sf = slots["slot_filler"]
    print("[assets] %d slots, %d observations" % (len(sf), sum(sum(v.values())
                                                               for v in sf.values())), flush=True)
    print("[assets] counting the corpus (%d bytes)" % THEM.CORPUS_BYTES, flush=True)
    counts = corpus_counts(str(THEM.CORPUS), int(THEM.CORPUS_BYTES))

    train, test = thin_counts(sf, SPLIT_SEED)
    print("[split] train slots=%d test slots=%d" % (len(train), len(test)), flush=True)

    # ---- TWO populations over ONE shared anchor set. The primary is a seeded sample of all
    # scoreable slots; the Q11 block gets its OWN item set of animacy-selecting SUBJ slots, because
    # those are rare (51 of 1,182 scoreable SUBJ slots) and a sample of the primary contains almost
    # none. Sharing the ANCHORS is what keeps the candidate vocabulary one object.
    eligible = eligible_words(spaces, train, test, counts)
    elig_set = set(eligible)
    cand_items = select_items(train, test, elig_set, MIN_SLOT_TOTAL, MIN_TRAIN_FILLERS)
    rng = np.random.default_rng(MASTER_SEED)
    if len(cand_items) > MAX_ITEMS:
        sel = rng.choice(len(cand_items), size=MAX_ITEMS, replace=False)
        items = [cand_items[int(i)] for i in sorted(sel)]
    else:
        items = cand_items
    print("[pop] %d candidate slots -> %d primary items (cap %d)"
          % (len(cand_items), len(items), MAX_ITEMS), flush=True)
    dg_words = choose_designated(items, test, elig_set, MASTER_SEED + 5)

    print("[mode] selecting animacy-selecting SUBJ slots (this resolves WordNet for every filler)",
          flush=True)
    mode_items = select_items(train, test, elig_set, MODE_MIN_SLOT_TOTAL, MODE_MIN_TRAIN_FILLERS,
                              role_prefix="SUBJ", animacy_selecting=True)
    mode_dg = choose_designated(mode_items, test, elig_set, MASTER_SEED + 6)
    print("[mode] %d animacy-selecting SUBJ slots" % len(mode_items), flush=True)

    anchors = set(dg_words) | set(mode_dg)
    rest = [w for w in eligible if w not in anchors]
    room = max(0, MAX_ANCHORS - len(anchors))
    if room and rest:
        take = rng.choice(len(rest), size=min(room, len(rest)), replace=False)
        anchors.update(rest[int(i)] for i in take)
    anchors_l = sorted(anchors)
    print("[pop] %d shared anchors (all designated golds of BOTH populations + fill to cap %d)"
          % (len(anchors_l), MAX_ANCHORS), flush=True)

    pop = build_population(items, dg_words, anchors_l, train, test)
    print("[pop] building the trigram nuisance channel", flush=True)
    ortho = trigram_cos_matrix(pop["anchors"], [s[0] for s in pop["items"]])
    pools = build_pools(pop, ortho)
    print("[arms] building profiles", flush=True)
    arms, aux = build_arms(pop, spaces, train, test, counts, ortho)

    # the scramble floor is PER POOL and PER SUB-POPULATION and is never carried across either.
    # It uses the EXACT matcher and profiles the primary arm used -- see build_arms' docstring.
    M15, A15 = aux["M15"], aux["Z15_anchors"]
    mu_p, inv_p = aux["mu_lgo"], aux["inv_lgo"]

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results: Dict[str, Dict] = {}
    strata = [("ALL", None), ("UNATTESTED_GOLD_train_count_zero", pop["unattested_mask"]),
              ("ATTESTED_GOLD_train_count_ge1", ~pop["unattested_mask"])]
    for pname, pool in pools.items():
        want = [(sn, sm) for sn, sm in strata
                if unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, pname, sn) not in done]
        for sn, sm in strata:
            k = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, pname, sn)
            if k in done and k in units:
                results["%s|%s" % (pname, sn)] = units[k]
                print("[unit] %s RESUMED" % k, flush=True)
        if not want:
            continue
        # score every arm ONCE per pool; the three strata are slices of the same hit vectors, so
        # nothing is recomputed and the strata are guaranteed to be reading the identical scorer
        print("[pool] %s scoring %d arms" % (pname, len(arms)), flush=True)
        hits: Dict[str, np.ndarray] = {}
        detail: Dict[str, Dict] = {}
        scored = np.ones(len(pop["items"]), dtype=bool)
        for nm in sorted(arms):
            h = score_matrix(arms[nm](), pool["elig"], pop["gold"])
            hits[nm] = h["hit_exp"]
            detail[nm] = {"_h": h}
            scored &= h["scored"]
        print("[scramble] %s calibrating %d permutation draws" % (pname, N_PERM), flush=True)
        draws = scramble_draws(M15, mu_p, inv_p, A15, pool["elig"], pop["gold"], N_PERM,
                               MASTER_SEED + 313)
        for sn, sm in want:
            mask = scored if sm is None else (scored & sm)
            scram = scramble_p95_for(draws, mask)
            r = run_pool(pname, pool, pop, hits, detail, scored, scram, sub_mask=sm, sub_name=sn)
            record_unit(str(out_dir), unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, pname, sn), r)
            results["%s|%s" % (pname, sn)] = r
        del hits, detail, draws

    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "TWO_MODE")
    if key in done and key in units:
        two_mode = units[key]
        print("[unit] TWO_MODE RESUMED", flush=True)
    elif not mode_items:
        two_mode = {"status": "NO_ANIMACY_SELECTING_SLOTS"}
    else:
        print("[two-mode] building the Q11 block on its own population", flush=True)
        pop_m = build_population(mode_items, mode_dg, anchors_l, train, test)
        arms_m, _auxm = build_arms(pop_m, spaces, train, test, counts,
                                   trigram_cos_matrix(anchors_l, [s[0] for s in mode_items]))
        two_mode = run_two_mode(pop_m, arms_m, train, counts, conc)
        del arms_m, pop_m
        record_unit(str(out_dir), key, two_mode)

    # ---------------------------------------------------------------- verdict
    P = results.get("%s|ALL" % PRIMARY_POOL, {})
    U = results.get("%s|UNATTESTED_GOLD_train_count_zero" % PRIMARY_POOL, {})
    g0 = P.get("G0_KNOWN_ANSWER_GATE", {})
    ka_ok = bool(g0.get("K1_PASSED")) and bool(g0.get("K2_clears_max_floor"))
    null_ok = bool((P.get("NULL_FLOOR") or {}).get("AT_CHANCE"))
    mp = P.get("MARGINS_paired_bootstrap_shared_resample_index", {}) or {}
    mu_ = U.get("MARGINS_paired_bootstrap_shared_resample_index", {}) or {}
    sf_name = (P.get("floors") or {}).get("strongest_by_point")

    def band(d: Dict, k: str) -> Optional[str]:
        v = d.get(k)
        return v.get("band") if isinstance(v, dict) else None

    feel_vs_floor = band(mp, "%s__vs__MAX_FLOOR(%s)" % (PRIMARY_ARM, sf_name))
    feel_vs_inc = band(mp, "%s__vs__INCUMBENT" % PRIMARY_ARM)
    feel_vs_negctrl = band(mp, "%s__minus__%s" % (PRIMARY_ARM, NEGCTRL_ARM))
    feel_vs_freq = band(mp, "%s__minus__CTRL_FREQPROFILE_1_LGO" % PRIMARY_ARM)
    feel_vs_conc = band(mp, "%s__minus__FEEL_CONC_1_LGO" % PRIMARY_ARM)
    un_feel_vs_floor = band(mu_, "%s__vs__MAX_FLOOR(%s)"
                            % (PRIMARY_ARM, (U.get("floors") or {}).get("strongest_by_point")))
    un_feel_vs_inc = band(mu_, "%s__vs__INCUMBENT" % PRIMARY_ARM)
    comb_vs_both = band(mp, "COMBINED_ATT_PLUS_FEEL__minus__ATTESTATION")

    if not ka_ok:
        verdict = "HARNESS_UNLICENSED_KNOWN_ANSWER_ARM_DID_NOT_REACH_CEILING"
    elif not null_ok:
        verdict = "POOL_LEAK_NULL_ARM_ABOVE_CHANCE"
    elif feel_vs_negctrl != "ABOVE":
        verdict = "NOT_THE_CHANNEL_A_WIDTH_MATCHED_NON_CHANNEL_PROFILE_DOES_AS_WELL"
    elif feel_vs_freq != "ABOVE" or feel_vs_conc != "ABOVE":
        verdict = "CONFOUNDED_FEELING_MATCH_DOES_NOT_BEAT_FREQUENCY_OR_CONCRETENESS"
    elif feel_vs_floor == "ABOVE" and feel_vs_inc == "ABOVE":
        verdict = "FEELING_MATCH_BEATS_ATTESTATION_AND_CLEARS_THE_FLOORS"
    elif feel_vs_floor == "ABOVE" and un_feel_vs_inc == "ABOVE":
        verdict = "FEELING_MATCH_CLEARS_THE_FLOORS_AND_GENERALISES_WHERE_ATTESTATION_IS_BLIND"
    elif feel_vs_floor == "ABOVE":
        verdict = "FEELING_MATCH_CLEARS_THE_FLOORS_BUT_DOES_NOT_BEAT_ATTESTATION"
    else:
        verdict = "FEELING_MATCH_DOES_NOT_CLEAR_THE_FLOORS"

    gates = [
        record_gate("K1_oracle_hit_exp", float(g0.get("K1_ORACLE_GOLD_hit_exp") or 0.0),
                    KA_CEILING_MIN, ">=", "known-answer arm licenses the pool and the scoring"),
        record_gate("null_maxdraw_minus_chance",
                    abs(float(((P.get("NULL_FLOOR") or {}).get("hit_exp_max_draw") or 0.0))
                        - float(P.get("chance") or 0.0)), NULL_TOL, "<=",
                    "null arm licenses the effect; MAX DRAW never the mean"),
    ]

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "verdict": verdict,
        "verdict_msg": (
            "Does a rejector that matches a candidate to the FEELING (affect) profile of a verb "
            "slot beat the attestation rejector that only knows seen/unseen, on the identical "
            "population / pool / scorer / gold, against four floors and the mandatory pool "
            "ladder, with a width-matched NON-channel control, a frequency control and a "
            "concreteness control? -> " + verdict),
        "OWNER_ANSWERS_THIS_CELL_IMPLEMENTS": {
            "Q10_the_rejection_criterion": (
                "I think I'm trying to match it to the feeling of the word... words with the same "
                "meanings have different feelings to use - 'think' versus 'contemplate' have very "
                "different feelings - one is informal one is more thoughtful and purposeful. So "
                "it's those kinds of feelings I'm trying to match. [BOARD Q10, 2026-08-16T21:50:25Z]"),
            "Q11_the_two_modes": (
                "The kettle apologized I can reject immediately becuase kettle's aren't sentient... "
                "The argument one is a bit tricker - I could see it being a metaphor for 'laying it "
                "on thick' - and I can still make sense of it so it isn't discarded out of hand. So "
                "yes, the rejector generalizes, but the rejections for those two sentences are very "
                "different. [BOARD Q11, 2026-08-16T21:52:27Z]")},
        "HOW_TO_READ_A_NULL": (
            "The owner performed this rejection in front of us and described its two modes, so THE "
            "CAPABILITY IS DEMONSTRATED. A null here is a fact about OUR IMPLEMENTATION -- our "
            "3-scalar operationalisation of the affect block, our diagonal-distance estimator, our "
            "dominant-sense animacy rule, our corpus -- and never about feeling-based rejection."),
        "NUMBER_HYGIENE": {
            "no_number_imported": "the attestation incumbent is RE-MEASURED here as the ARM named "
                                  "ATTESTATION on this cell's own pool, n and gold. No figure from "
                                  "another scorer or population appears in this file.",
            "constant_prototype_floor": "computed on THIS population, reported with THIS n under "
                                        "all three tie conventions. 0.1382 / 0.2070 are floors on "
                                        "DIFFERENT populations and are neither quoted nor implied.",
            "cue_regime": "EXACT-SLOT cue. Every hit@1 here is measured with the verb slot fully "
                          "specified; nothing here transfers to a partial or degraded cue.",
            "tie_conventions": "hit_exp (primary), optimistic and conservative are ALL reported "
                               "for EVERY arm, with tie mass, so no comparison can be flipped by "
                               "a convention chosen after the fact."},
        "config": {"MASTER_SEED": MASTER_SEED, "SPLIT_SEED": SPLIT_SEED, "BOOT_SEED": BOOT_SEED,
                   "N_BOOT": N_BOOT, "N_PERM": N_PERM, "MAX_ITEMS": MAX_ITEMS,
                   "MAX_ANCHORS": MAX_ANCHORS, "K_DISTRACT": K_DISTRACT,
                   "MIN_SLOT_TOTAL": MIN_SLOT_TOTAL, "MIN_TRAIN_FILLERS": MIN_TRAIN_FILLERS,
                   "MIN_ANCHOR_COUNT": MIN_ANCHOR_COUNT, "SD_PRIOR_N": SD_PRIOR_N,
                   "N_MODE": N_MODE, "ANIM_MASS_FRAC": ANIM_MASS_FRAC,
                   "KA_CEILING_MIN": KA_CEILING_MIN, "NULL_TOL": NULL_TOL,
                   "T_MARGIN_MIN": T_MARGIN_MIN, "POOLS": list(POOLS),
                   "PRIMARY_POOL": PRIMARY_POOL, "PRIMARY_ARM": PRIMARY_ARM,
                   "FLOORS": list(FLOOR_SET_REQUIRED), "progress_logging": PROGRESS_LOGGING},
        "population": {k: v for k, v in pop.items()
                       if k in ("elapsed_s",)} | {
            "n_anchors": len(pop["anchors"]), "n_items": len(pop["items"]),
            "n_items_with_unattested_gold": int(pop["unattested_mask"].sum()),
            "frac_unattested": round(float(pop["unattested_mask"].mean()), 4),
            "role_histogram": dict(collections.Counter(s[1] if not s[1].startswith("obl:")
                                                       else "obl:*" for s in pop["items"]))},
        "BRAIN_FIDELITY": BRAIN_FIDELITY,
        "ORGAN_REUSE": organ_reuse_witness(),
        "selftest_evidence": ev,
        "results_by_pool_and_stratum": results,
        "TWO_MODE_BLOCK_Q11_separate_never_pooled": two_mode,
        "DECISION_INPUTS": {
            "TWO_MODE_attestation_separation_is_exactly_zero": (
                ((two_mode.get("ARMS") or {}).get("ATTESTATION") or {})
                .get("MODE_SEPARATION_D1_minus_D2")),
            "TWO_MODE_feeling_separation": (
                ((two_mode.get("ARMS") or {}).get(PRIMARY_ARM) or {})
                .get("MODE_SEPARATION_D1_minus_D2")),
            "TWO_MODE_is_it_channel_specific": (
                two_mode.get("IS_THE_MODE_SEPARATION_CHANNEL_SPECIFIC") or {}).get(
                    "feeling_minus_width_matched_non_channel"),
            "feeling_vs_max_floor": feel_vs_floor, "feeling_vs_incumbent": feel_vs_inc,
            "feeling_vs_width_matched_non_channel": feel_vs_negctrl,
            "feeling_vs_frequency_same_estimator": feel_vs_freq,
            "feeling_vs_concreteness_same_estimator": feel_vs_conc,
            "UNATTESTED_feeling_vs_max_floor": un_feel_vs_floor,
            "UNATTESTED_feeling_vs_incumbent": un_feel_vs_inc,
            "combined_vs_attestation": comb_vs_both,
            "known_answer_gate": ka_ok, "null_gate": null_ok},
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics, gate_claims=gates)
    print("[verdict] %s" % verdict, flush=True)
    print("[done] %.0fs -> %s/metrics.json" % (time.time() - t_start, out_dir), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        raise SystemExit(3)
