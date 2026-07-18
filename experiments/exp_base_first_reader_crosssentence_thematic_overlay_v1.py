"""
Base-first reader v2: does CROSS-SENTENCE context (the real packaged state-of-mind
overlay) let a glass-box reader recover a held-out concrete word's THEMATIC meaning
better than the within-sentence window v1 fed -- when scored on the RIGHT target
(thematic/relational structure, not taxonomy)?

This disentangles the THREE factors the v1 VET (a865a0b) + a human-reading walkthrough
exposed in exp_base_first_reader_heldout_context_learn_v1 (MIDDLE_BAND, +0.064 NS):

  (1) FED-CONTEXT TRUNCATION: v1 fed only a within-sentence +/-4 window and missed the
      cross-sentence context where meaning lives ("She has left the nest" -> the reader
      must carry hen/eggs/Ned across sentence boundaries). FIX = the accumulated
      cross-sentence running picture from hdlab.state_of_mind.WorkingOverlay.
  (2) TARGET-MISMATCH (the key VET finding): distributional context clusters words by
      SITUATION / THEMATIC role, NOT taxonomy. v1 scored TAXONOMIC category -> ANIMAL
      0.62 but BODY/PLACE/PLANT/SUBSTANCE = 0. FIX = score the THEMATIC meaning context
      actually provides; keep taxonomy as the EXPLICIT CONTRAST (dictionary owns it).
  (3) READER-WEAKNESS: v1 had no context-richness arm. Here the a/b/c arms isolate the
      value of the context SOURCE (the one variable) at fixed reader + fixed target.

INTEGRATION: this is the FIRST cell to drive the REAL packaged overlay
(hdlab/state_of_mind.py, verification/verify_state_of_mind_overlay.py) as the reader's
cross-sentence context source. The overlay's observe_surface() (recognize-KNOWN vs
surprise-flag-NEW, name->entity), salience-weighted active_set(), and resolve() (coref)
are used unmodified -- no fork, no stub. SetKnownBase is wired to the reduced base so
held-out words flag surprise=1.0 (recognize-NEW fires; reported as telemetry).

PRIMARY metric  = THEMATIC-NEIGHBOR AUC: for each held-out word, does its context place
                  its true world-knowledge scene-mates (KNOWN anchors) ABOVE unrelated
                  KNOWN anchors? Mann-Whitney AUC per word, chance = 0.5.
CONTRAST metric = TAXONOMIC-NEIGHBOR AUC (same machinery, taxonomic gold) for the context
                  arms (expected WEAK) + dictionary taxonomic-lookup ACCURACY (expected
                  STRONG, v1 ceiling ~0.98) -- demonstrates the mismatch, does not hide it.

Arms (ONE variable = CONTEXT SOURCE):
  (a) CROSS-SENTENCE via WorkingOverlay running picture   [the fix]
  (b) WITHIN-SENTENCE +/-4 window                          [reproduce v1, the must-beat]
  (c) NO-CONTEXT (empty context -> AUC 0.5 by construction) [floor]
  (d) DICTIONARY lookup (WordNet supersense -> taxon)       [taxonomy reference/ceiling]

Glass-box (symbolic overlay + cosine over interpretable context Counters + NB-free
Mann-Whitney AUC); learn-in-substrate; NO external LLM; NOT next-word prediction.

ANCHOR: base_first_reader_crosssentence_thematic_overlay_v1
COMPUTE: sequential-CPU, no substrate HD primitive, no GPU, wall < 30s (justified:
         symbolic overlay + tiny corpus; the cell IS the reader logic, not an HD sweep).
DETERMINISM: OMP_NUM_THREADS=1; fixed RNG seed 12345; sorted(set(...)) ordering only.

CELL-TEMPLATE MANDATES (relevant subset; many SCHEMA-VET gates N/A for this cell-type):
# - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
# - ATOMIC final metrics write (tmp + os.replace)          [META_RULE_AH: tmp_replace]
# - ARMS-MUST-DIFFER hash check at gate                     [META_RULE_AF]
# - baseline_in_band (within-sentence thematic AUC in band; no-context == 0.5) [META_RULE_AG]
# - discriminator CAN-FAIL (gap a-b can be <= 0; a can be <= 0.52) [design-gate]
# - deterministic seeding (fixed int seed, sorted set)      [F.5 / PROT-023]
# - start-marker + crash-diagnostic; heartbeat EXEMPT (wall < 30s)
# - all reported numbers MEASURED@this metrics.json
# - real_code_path: self_test() constructs the REAL WorkingOverlay + SetKnownBase at tiny
#   scale and asserts cross-sentence recovers a thematic pair the window misses
# - N/A: KGStore/substrate_signature (no KGStore); N/A cardinality sweep; N/A CRLB (AUC, no HD noise floor)
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import csv
import re
import json
import math
import time
import random
import argparse
import hashlib
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nltk.corpus import wordnet as wn

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from hdlab.state_of_mind import WorkingOverlay, SetKnownBase, PRONOUN_SCOPE

ANCHOR_NAME = "base_first_reader_crosssentence_thematic_overlay_v1"
OUTPUT_DIR = os.path.join(REPO, "data", "exp_" + ANCHOR_NAME)
BASE_CSV = os.path.join(REPO, "data", "corpora", "base_vocabulary", "cleaned", "base_vocabulary_ordered.csv")
READER_PATHS = [
    os.path.join(REPO, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_first_reader.clean.txt"),
    os.path.join(REPO, "data", "corpora", "graded_readers_grade1", "cleaned", "mcguffey_primer.clean.txt"),
]

SEED = 12345
WINDOW = 4          # within-sentence +/- window (arm b) -- reproduces v1 verbatim
ACTIVE_M = 10       # cross-sentence overlay active-set cap (working-memory content heads)
RECENCY_WIN = 30    # snapshot scope: only entities mentioned within this many mentions of now
                    # (the overlay's own recency notion -> a LOCAL working scene, not the whole book)
MIN_OCC = 2         # a word must appear >= MIN_OCC times to have usable context
N_BOOT = 5000

# ---- Pre-registered bands (set BEFORE the final run; HYPOTHESIZED@this file) ----------
# PRIMARY = thematic-neighbor AUC (chance 0.5). Gap = a_cross - b_within on the THEMATIC gold.
COVERAGE_GATE = 0.98        # full-base AND understood-surround must both clear this (fairness)
HP_AUC = 0.62              # a_cross thematic AUC must clear chance by a real margin (strict; META_RULE_L)
HP_GAP = 0.05             # PRIMARY gap(a_cross - b_within) HARD-PASS threshold on thematic AUC
HP_ALPHA = 0.05           # bootstrap significance P(gap <= 0) < alpha
MB_GAP = 0.02             # MIDDLE_BAND floor: positive but not HP
BASELINE_BAND = (0.40, 0.90)  # within-sentence thematic AUC must be measurable, not saturated (META_RULE_AG)

# ---------------------------------------------------------------------------------------
# GOLD 1 -- TAXONOMIC (coarse category). Ported VERBATIM from v1 (the CONTRAST target).
# GOLD 2 -- THEMATIC SCENE (world-knowledge situation cluster). Hand-authored HERE, BLIND
# to within- vs cross-sentence co-occurrence (I have not measured which pairs are within vs
# cross); scenes cross-cut taxonomy on purpose (a hen ANIMAL + its nest ARTIFACT + egg FOOD
# share the FARMYARD scene). Noise in scene assignment makes the test HARDER (can-fail), not
# easier. Both golds are INDEPENDENT of the inference path; the context arms never look up a
# held-out word's label (only arm d looks up, and only taxonomy).
# ---------------------------------------------------------------------------------------
HELDOUT_TAXON = {
    "hen": "ANIMAL", "frog": "ANIMAL", "owl": "ANIMAL", "duck": "ANIMAL",
    "fox": "ANIMAL", "bee": "ANIMAL", "rat": "ANIMAL", "chick": "ANIMAL",
    "grass": "PLANT", "rose": "PLANT", "corn": "PLANT", "nut": "PLANT",
    "bush": "PLANT", "willow": "PLANT", "vine": "PLANT",
    "bread": "FOOD", "honey": "FOOD", "meat": "FOOD", "milk": "FOOD",
    "apple": "FOOD", "cracker": "FOOD",
    "doll": "ARTIFACT", "basket": "ARTIFACT", "cart": "ARTIFACT", "cage": "ARTIFACT",
    "bell": "ARTIFACT", "flag": "ARTIFACT", "mill": "ARTIFACT", "skate": "ARTIFACT", "fan": "ARTIFACT",
    "hand": "BODY", "mouth": "BODY", "head": "BODY", "neck": "BODY",
    "arm": "BODY", "lap": "BODY", "hair": "BODY",
    "pond": "PLACE", "brook": "PLACE", "hill": "PLACE", "sea": "PLACE",
    "shore": "PLACE", "beach": "PLACE", "river": "PLACE",
    "ice": "SUBSTANCE", "sand": "SUBSTANCE", "wood": "SUBSTANCE",
    "log": "SUBSTANCE", "fur": "SUBSTANCE", "snow": "SUBSTANCE",
}
KNOWN_TAXON = {
    "dog": "ANIMAL", "cat": "ANIMAL", "bird": "ANIMAL", "horse": "ANIMAL",
    "fish": "ANIMAL", "cow": "ANIMAL", "lamb": "ANIMAL", "wolf": "ANIMAL",
    "goat": "ANIMAL", "sheep": "ANIMAL",
    "tree": "PLANT", "flower": "PLANT", "moss": "PLANT", "stump": "PLANT",
    "egg": "FOOD", "tea": "FOOD", "hay": "FOOD", "cake": "FOOD",
    "hat": "ARTIFACT", "box": "ARTIFACT", "boat": "ARTIFACT", "mat": "ARTIFACT",
    "slate": "ARTIFACT", "cap": "ARTIFACT", "barn": "ARTIFACT", "kite": "ARTIFACT",
    "house": "ARTIFACT", "drum": "ARTIFACT",
    "feet": "BODY", "face": "BODY", "wing": "BODY", "eye": "BODY", "foot": "BODY",
    "rock": "PLACE", "bank": "PLACE", "town": "PLACE", "home": "PLACE", "spot": "PLACE",
    "water": "SUBSTANCE", "air": "SUBSTANCE", "fat": "SUBSTANCE", "foam": "SUBSTANCE",
}

# THEMATIC SCENE gold (world-knowledge situation clusters; each word -> ONE scene).
HELDOUT_SCENE = {
    # FARMYARD: farm birds/animals + their products + farm structures
    "hen": "FARMYARD", "chick": "FARMYARD", "duck": "FARMYARD", "corn": "FARMYARD",
    "milk": "FARMYARD", "mill": "FARMYARD",
    # WOODS: wild woodland creatures + woodland plants/material
    "fox": "WOODS", "owl": "WOODS", "bee": "WOODS", "rat": "WOODS", "frog": "WOODS",
    "nut": "WOODS", "bush": "WOODS", "willow": "WOODS", "vine": "WOODS", "log": "WOODS",
    "fur": "WOODS",
    # WATER: water bodies + shore + water substances
    "pond": "WATER", "brook": "WATER", "sea": "WATER", "shore": "WATER",
    "beach": "WATER", "river": "WATER", "ice": "WATER", "sand": "WATER", "snow": "WATER",
    # FOOD_MEAL: table food + eating
    "bread": "FOOD_MEAL", "honey": "FOOD_MEAL", "meat": "FOOD_MEAL",
    "apple": "FOOD_MEAL", "cracker": "FOOD_MEAL",
    # HOME_PLAY: indoor objects + toys + play things
    "doll": "HOME_PLAY", "basket": "HOME_PLAY", "cart": "HOME_PLAY", "cage": "HOME_PLAY",
    "bell": "HOME_PLAY", "flag": "HOME_PLAY", "skate": "HOME_PLAY", "fan": "HOME_PLAY",
    # BODY: body parts
    "hand": "BODY", "mouth": "BODY", "head": "BODY", "neck": "BODY",
    "arm": "BODY", "lap": "BODY", "hair": "BODY",
    # LANDSCAPE: outdoor land features + outdoor plants
    "hill": "LANDSCAPE", "grass": "LANDSCAPE", "rose": "LANDSCAPE", "wood": "LANDSCAPE",
}
KNOWN_SCENE = {
    "cow": "FARMYARD", "goat": "FARMYARD", "sheep": "FARMYARD", "lamb": "FARMYARD",
    "horse": "FARMYARD", "egg": "FARMYARD", "hay": "FARMYARD", "barn": "FARMYARD",
    "wolf": "WOODS", "bird": "WOODS", "tree": "WOODS", "moss": "WOODS", "stump": "WOODS",
    "fish": "WATER", "boat": "WATER", "water": "WATER", "foam": "WATER",
    "cake": "FOOD_MEAL", "tea": "FOOD_MEAL", "fat": "FOOD_MEAL",
    "hat": "HOME_PLAY", "box": "HOME_PLAY", "mat": "HOME_PLAY", "slate": "HOME_PLAY",
    "cap": "HOME_PLAY", "kite": "HOME_PLAY", "house": "HOME_PLAY", "drum": "HOME_PLAY",
    "feet": "BODY", "face": "BODY", "wing": "BODY", "eye": "BODY", "foot": "BODY",
    "rock": "LANDSCAPE", "bank": "LANDSCAPE", "town": "LANDSCAPE", "home": "LANDSCAPE",
    "spot": "LANDSCAPE", "flower": "LANDSCAPE", "air": "LANDSCAPE", "dog": "HOME_PLAY",
    "cat": "HOME_PLAY",
}

STOP = set((
    "the a an and or of to in on is it he she we you i they his her its my your our "
    "their this that these those with at by for as be are was were do does did has "
    "have had not no yes will would can could so too now here there then when what who "
    "me him us them if but out up down all one two see come let get put go went"
).split())

CONTRACTIONS = {
    "can't", "don't", "won't", "it's", "he's", "she's", "that's", "i'm",
    "let's", "there's", "what's",
}

LEX2CAT = {
    "noun.animal": "ANIMAL", "noun.plant": "PLANT", "noun.food": "FOOD",
    "noun.artifact": "ARTIFACT", "noun.body": "BODY", "noun.location": "PLACE",
    "noun.object": "PLACE", "noun.substance": "SUBSTANCE", "noun.shape": "ARTIFACT",
}


# ------------------------------------------------------------------ data helpers
def load_base(path):
    ranked = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = (row.get("word") or "").strip().lower()
            if w:
                ranked.append(w)
    return ranked


def make_normalizer(base_all):
    def norm(t):
        if "'" in t and t not in CONTRACTIONS:
            j = t.replace("'", "")
            if j in base_all:
                return j
            if t.endswith("'s") and t[:-2] in base_all:
                return t[:-2]
        return t
    return norm


def roman_set(upto=120):
    def roman(n):
        vals = [(100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"),
                (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
        s = ""
        for v, sy in vals:
            while n >= v:
                s += sy
                n -= v
        return s
    return set(roman(i) for i in range(1, upto + 1))


def detect_names(reader_paths, base_all, label_words):
    raw = " ".join(open(p, encoding="utf-8").read() for p in reader_paths)
    cap = set(m.lower() for m in re.findall(r"\b([A-Z][a-z]+)\b", raw))
    return set(w for w in cap if w not in base_all and w not in label_words)


def prose_sentences(path):
    """Prose filter (reuses Director scratchpad passage.py): drop lesson headers, phonics
    word-grid lines (3+ consecutive spaces), and <=3-char fragment lines; THEN split the
    remaining prose into sentences. Returns list of (surface_tokens_with_case, lower_tokens).
    This removes the junk that polluted v1's window (the first 'hen' window was
    ['a','big','box','fat','iv','lesson','rat','u','x'] -- all phonics-grid noise)."""
    prose = []
    for ln in open(path, encoding="utf-8").read().splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("#") or "LESSON" in s.upper():
            continue
        if re.search(r"\s{3,}", ln):
            continue                       # word-grid / phonics columns
        if len(s) <= 3:
            continue
        prose.append(s)
    text = " ".join(prose)
    out = []
    for seg in re.split(r"(?<=[.!?])\s+", text):
        seg = seg.strip()
        if not seg:
            continue
        # keep only proper sentence-final split; further split residual .?! inside
        for sub in re.split(r"[.?!]+", seg):
            surf = re.findall(r"[A-Za-z']+", sub)
            if surf:
                out.append((surf, [w.lower() for w in surf]))
    return out


def make_lemmatizer(label_words):
    def lemma(t):
        if t in label_words:
            return t
        if t.endswith("s") and t[:-1] in label_words:
            return t[:-1]
        if t.endswith("es") and t[:-2] in label_words:
            return t[:-2]
        return t
    return lemma


def coverage(sents_lower, base, norm, names, romans):
    tot = known = 0
    for _surf, toks in sents_lower:
        for t in toks:
            if t in names:
                continue
            if t in romans and t != "i":
                continue
            nt = norm(t)
            if nt not in base and len(nt) <= 2:
                continue
            tot += 1
            known += (1 if nt in base else 0)
    return (known / tot if tot else 0.0), known, tot


def surround_coverage(sents_lower, reduced_base, heldout, norm, lemma, names, romans, window):
    known = total = 0
    for _surf, toks in sents_lower:
        lem = [lemma(t) for t in toks]
        for i, w in enumerate(lem):
            if w not in heldout:
                continue
            lo = max(0, i - window)
            hi = min(len(lem), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                tj = toks[j]
                if tj in names or (tj in romans and tj != "i"):
                    continue
                if lem[j] in heldout:
                    continue
                nt = norm(tj)
                if nt not in reduced_base and len(nt) <= 2:
                    continue
                total += 1
                known += (1 if nt in reduced_base else 0)
    return (known / total if total else 0.0), known, total


# ------------------------------------------------------------ feature extraction
def is_feature_ok(head, target, heldout_set, names, romans):
    """A context head is a usable feature iff it is not the target itself, not any held-out
    word (LEAK FIX: v1 leaked held-out identities as features for self-co-occurring words),
    not a stopword, not a name, not a roman numeral, and length >= 3."""
    if head == target:
        return False
    if head in heldout_set:
        return False
    if head in STOP:
        return False
    if head in names:
        return False
    if head in romans and head != "i":
        return False
    if len(head) < 3:
        return False
    return True


def build_within_sentence_vectors(sents_lower, targets, heldout_set, lemma, names, romans, window):
    """Arm (b): +/-window content words within the same sentence (v1 reproduce)."""
    vecs = defaultdict(Counter)
    occ = Counter()
    for _surf, toks in sents_lower:
        lem = [lemma(t) for t in toks]
        for i, w in enumerate(lem):
            if w not in targets:
                continue
            occ[w] += 1
            lo = max(0, i - window)
            hi = min(len(lem), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                h = lem[j]
                if is_feature_ok(h, w, heldout_set, names, romans):
                    vecs[w][h] += 1
    return vecs, occ


def build_cross_sentence_vectors(sents, targets, heldout_set, lemma, names, romans,
                                  reduced_base, active_m, recency_win):
    """Arm (a): the REAL packaged overlay's SALIENCE-WEIGHTED cross-sentence running picture.

    Drives hdlab.state_of_mind.WorkingOverlay UNMODIFIED: SetKnownBase wired to the reduced
    base so held-out words flag surprise=1.0 (recognize-NEW fires); observe_surface() builds
    the salience-weighted active set + resolves coref. For each sentence: observe every token
    (faithful mention stream), then for each target occurrence snapshot active_set(top=None).
    The snapshot is scoped to a LOCAL working scene (the overlay's own recency notion): only
    entities mentioned within recency_win mentions of now are kept, and each content head is
    weighted by its overlay SALIENCE (count + beta*exp(-lam*dist)) -- so the recent scene
    dominates and a stale cross-scene word contributes little. This is the working-memory
    behavior the two-layer state-of-mind arc validated; it crosses sentence boundaries (the v1
    fed-context fix) without collapsing the whole book into one diffuse bag. Coref-resolved
    pronoun heads are added at unit weight. Overlay resets per reader file (per-book state)."""
    vecs = defaultdict(Counter)
    occ = Counter()
    surprise_new = Counter()   # telemetry: held-out words flagged surprise (recognize-NEW)
    known_recognized = Counter()
    active_sizes = []
    for _fname, file_sents in sents:
        base_probe = SetKnownBase(reduced_base)
        ov = WorkingOverlay(base=base_probe)
        for surf, low in file_sents:
            lem = [lemma(t) for t in low]
            sent_pron_heads = []
            for k, raw_surf in enumerate(surf):
                res = ov.observe_surface(raw_surf, at_sentence_start=(k == 0))
                if res.is_pronoun:
                    pl = res.head
                    if pl in PRONOUN_SCOPE:
                        ent = ov.resolve_pronoun(pl, strategy="maintained")
                        if ent is not None:
                            sent_pron_heads.append(ent.head)
                else:
                    if res.is_known:
                        known_recognized[res.head] += 1
            # snapshot AFTER reading the whole sentence: the working scene now holds the full
            # current sentence (both sides of the target) + the recent accumulated scene.
            now = ov.n_observed
            ranked = ov.active_set(top=None)       # (entity, salience) desc
            content = []                            # (head, salience) within recency window
            for ent, sal in ranked:
                if len(content) >= active_m:
                    break
                if (now - ent.last_midx) > recency_win:
                    continue                        # stale: outside the local working scene
                h = ent.head
                if h in STOP or h in names or (h in romans and h != "i") or len(h) < 3:
                    continue
                content.append((h, sal))
            for i, w in enumerate(lem):
                if w not in targets:
                    continue
                occ[w] += 1
                if w in heldout_set:
                    surprise_new[w] += (1 if base_probe.surprise(w) >= 0.5 else 0)
                for h, sal in content:
                    if is_feature_ok(h, w, heldout_set, names, romans):
                        vecs[w][h] += sal          # salience-weighted feature
                for h in sent_pron_heads:
                    if is_feature_ok(h, w, heldout_set, names, romans):
                        vecs[w][h] += 1.0
            active_sizes.append(len(content))
    return vecs, occ, surprise_new, known_recognized, active_sizes


# ---------------------------------------------------------------- similarity + AUC
def cosine(u, v):
    if not u or not v:
        return 0.0
    common = set(u) & set(v)
    if not common:
        return 0.0
    dot = sum(u[k] * v[k] for k in common)
    nu = math.sqrt(sum(x * x for x in u.values()))
    nv = math.sqrt(sum(x * x for x in v.values()))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    return dot / (nu * nv)


def auc_mann_whitney(pos, neg):
    """AUC = P(pos_score > neg_score) + 0.5 P(tie). Empty -> None."""
    if not pos or not neg:
        return None
    wins = 0.0
    for p in pos:
        for q in neg:
            if p > q:
                wins += 1.0
            elif p == q:
                wins += 0.5
    return wins / (len(pos) * len(neg))


def per_word_auc(target_vecs, anchor_vecs, gold, target_words, anchor_words):
    """For each target word, AUC over (same-gold anchor sims) vs (diff-gold anchor sims).
    Returns dict word->auc (only words with >=1 pos AND >=1 neg anchor). Context-based sim."""
    out = {}
    for w in target_words:
        if w not in gold:
            continue
        tv = target_vecs.get(w, Counter())
        pos, neg = [], []
        for a in anchor_words:
            if a == w or a not in gold:
                continue
            s = cosine(tv, anchor_vecs.get(a, Counter()))
            if gold[a] == gold[w]:
                pos.append(s)
            else:
                neg.append(s)
        a_val = auc_mann_whitney(pos, neg)
        if a_val is not None:
            out[w] = a_val
    return out


def dict_taxon_auc(target_words, anchor_words, gold_taxon, dict_cat):
    """Arm (d) taxonomic AUC: 'similarity' = 1 if same dict-predicted taxon else 0."""
    out = {}
    for w in target_words:
        if w not in gold_taxon:
            continue
        cw = dict_cat.get(w)
        pos, neg = [], []
        for a in anchor_words:
            if a == w or a not in gold_taxon:
                continue
            ca = dict_cat.get(a)
            sim = 1.0 if (cw is not None and ca is not None and cw == ca) else 0.0
            if gold_taxon[a] == gold_taxon[w]:
                pos.append(sim)
            else:
                neg.append(sim)
        a_val = auc_mann_whitney(pos, neg)
        if a_val is not None:
            out[w] = a_val
    return out


def dict_lookup(w):
    ss = wn.synsets(w, pos=wn.NOUN)
    if not ss:
        return None
    return LEX2CAT.get(ss[0].lexname())


def mean(d):
    return sum(d.values()) / len(d) if d else 0.0


def bootstrap_gap_over_words(words, auc_a, auc_b, seed, n_boot):
    """Bootstrap the mean gap (mean auc_a - mean auc_b) resampling held-out WORDS."""
    common = [w for w in words if w in auc_a and w in auc_b]
    n = len(common)
    if n == 0:
        return 0.0, 0.0, 1.0, 0
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        ga = sum(auc_a[common[i]] for i in idx) / n
        gb = sum(auc_b[common[i]] for i in idx) / n
        diffs.append(ga - gb)
    diffs.sort()
    lo = diffs[int(0.025 * len(diffs))]
    hi = diffs[int(0.975 * len(diffs))]
    p_le0 = sum(1 for x in diffs if x <= 0) / len(diffs)
    return lo, hi, p_le0, n


# ---------------------------------------------------------------- infra helpers
def _write_start_marker(output_dir, run_mode):
    import platform
    os.makedirs(output_dir, exist_ok=True)
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
    }
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: %s" % type(exc).__name__,
        "elapsed_s": 0.0, "run_mode": "crash",
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(), "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _arms_differ(arms_vecs):
    """Hash per-arm target-vector dicts; assert no two arms produced bit-identical output."""
    digests = {}
    for name, vecs in arms_vecs.items():
        norm = {w: dict(sorted(c.items())) for w, c in sorted(vecs.items())}
        blob = json.dumps(norm, sort_keys=True).encode("utf-8")
        digests[name] = hashlib.sha256(blob).hexdigest()
    names = sorted(digests)
    for a in names:
        for b in names:
            if a < b:
                assert digests[a] != digests[b], (
                    "META_RULE_AF: arms %r and %r produced bit-identical vectors" % (a, b))
    return digests


# ----------------------------------------------------------------- core pipeline
def run_pipeline(run_mode, n_boot):
    t0 = time.perf_counter()
    ranked = load_base(BASE_CSV)
    base_all = set(ranked)
    norm = make_normalizer(base_all)
    romans = roman_set()
    label_words = set(KNOWN_TAXON) | set(HELDOUT_TAXON)
    names = detect_names(READER_PATHS, base_all, label_words)
    lemma = make_lemmatizer(label_words)

    # prose-filtered sentences, per file (overlay resets per book)
    per_file = []
    all_sents = []
    for p in READER_PATHS:
        fs = prose_sentences(p)
        per_file.append((os.path.basename(p), fs))
        all_sents += fs

    # occurrence filter
    occ_all = Counter()
    for _surf, toks in all_sents:
        for t in toks:
            occ_all[lemma(t)] += 1
    heldout = sorted(w for w in HELDOUT_TAXON if occ_all[w] >= MIN_OCC)
    known = sorted(w for w in KNOWN_TAXON if occ_all[w] >= 1)
    heldout_set = set(heldout)
    dropped_held = sorted(set(HELDOUT_TAXON) - heldout_set)
    dropped_known = sorted(set(KNOWN_TAXON) - set(known))
    reduced_base = base_all - heldout_set
    targets = heldout_set | set(known)

    # ---- fairness gates
    cov_full, kf, tf = coverage(all_sents, base_all, norm, names, romans)
    cov_red, _kr, _tr = coverage(all_sents, reduced_base, norm, names, romans)
    cov_sur, ks, ts = surround_coverage(all_sents, reduced_base, heldout_set, norm, lemma,
                                        names, romans, WINDOW)
    heldout_absent_from_reduced = sorted(w for w in heldout if w in reduced_base)

    # ---- feature vectors per arm
    b_vecs, b_occ = build_within_sentence_vectors(all_sents, targets, heldout_set, lemma,
                                                  names, romans, WINDOW)
    a_vecs, a_occ, surprise_new, known_recog, active_sizes = build_cross_sentence_vectors(
        per_file, targets, heldout_set, lemma, names, romans, reduced_base, ACTIVE_M, RECENCY_WIN)
    # arm (c) no-context: empty vectors -> cosine 0 -> AUC 0.5 by construction (asserted below)
    c_vecs = {w: Counter() for w in targets}

    known_present = sorted(k for k in known if k in a_vecs or k in b_vecs)
    held_present = sorted(w for w in heldout if a_occ[w] > 0 or b_occ[w] > 0)
    n = len(held_present)

    dict_cat = {w: dict_lookup(w) for w in targets}

    # ---- PRIMARY: thematic-neighbor AUC per arm
    scene_gold = {}
    scene_gold.update(KNOWN_SCENE)
    scene_gold.update(HELDOUT_SCENE)
    taxon_gold = {}
    taxon_gold.update(KNOWN_TAXON)
    taxon_gold.update(HELDOUT_TAXON)

    a_thematic = per_word_auc(a_vecs, a_vecs, scene_gold, held_present, known_present)
    b_thematic = per_word_auc(b_vecs, b_vecs, scene_gold, held_present, known_present)
    c_thematic = per_word_auc(c_vecs, c_vecs, scene_gold, held_present, known_present)

    a_taxon = per_word_auc(a_vecs, a_vecs, taxon_gold, held_present, known_present)
    b_taxon = per_word_auc(b_vecs, b_vecs, taxon_gold, held_present, known_present)
    d_taxon = dict_taxon_auc(held_present, known_present, taxon_gold, dict_cat)
    d_thematic = dict_taxon_auc(held_present, known_present, scene_gold, dict_cat)  # dict sim vs THEMATIC gold

    # arm (d) taxonomic-lookup ACCURACY (v1 ceiling): dict category == taxon gold
    d_lookup_correct = {w: (1 if dict_cat.get(w) == HELDOUT_TAXON.get(w) else 0)
                        for w in held_present}
    d_lookup_acc = mean(d_lookup_correct)

    a_th, b_th, c_th = mean(a_thematic), mean(b_thematic), mean(c_thematic)
    a_tx, b_tx, d_tx, d_th = mean(a_taxon), mean(b_taxon), mean(d_taxon), mean(d_thematic)

    thematic_gap = a_th - b_th   # PRIMARY gap
    ci_lo, ci_hi, p_le0, n_common = bootstrap_gap_over_words(
        held_present, a_thematic, b_thematic, SEED, n_boot)

    # ---- discipline gates
    baseline_in_band = BASELINE_BAND[0] < b_th < BASELINE_BAND[1]
    nocontext_is_chance = abs(c_th - 0.5) < 1e-9
    scene_counts_held = Counter(scene_gold[w] for w in held_present if w in scene_gold)
    scene_counts_known = Counter(scene_gold[k] for k in known_present if k in scene_gold)
    degenerate_scenes = [s for s in scene_counts_held
                         if scene_counts_known.get(s, 0) < 2 or scene_counts_held[s] < 2]

    arms_vecs_for_hash = {"a_cross": a_vecs, "b_within": b_vecs}
    arms_digests = _arms_differ(arms_vecs_for_hash)

    # ---- per-word table
    per_word = []
    for w in held_present:
        per_word.append({
            "word": w, "taxon": HELDOUT_TAXON.get(w), "scene": HELDOUT_SCENE.get(w),
            "occ_cross": a_occ[w], "occ_within": b_occ[w],
            "a_cross_thematic_auc": round(a_thematic.get(w, float("nan")), 4) if w in a_thematic else None,
            "b_within_thematic_auc": round(b_thematic.get(w, float("nan")), 4) if w in b_thematic else None,
            "a_cross_taxon_auc": round(a_taxon.get(w, float("nan")), 4) if w in a_taxon else None,
            "dict_cat": dict_cat.get(w), "dict_taxon_correct": bool(d_lookup_correct.get(w)),
            "surprise_new_flagged": surprise_new.get(w, 0),
        })

    # ---- VERDICT (pre-registered bands)
    gates_ok = (cov_full >= COVERAGE_GATE and cov_sur >= COVERAGE_GATE
                and baseline_in_band and nocontext_is_chance and not degenerate_scenes
                and not heldout_absent_from_reduced and n >= 20)
    if not gates_ok:
        verdict = "GATE_FAIL"
        why = []
        if cov_full < COVERAGE_GATE:
            why.append("base_coverage %.4f < %.2f" % (cov_full, COVERAGE_GATE))
        if cov_sur < COVERAGE_GATE:
            why.append("surround_coverage %.4f < %.2f" % (cov_sur, COVERAGE_GATE))
        if not baseline_in_band:
            why.append("within-sentence thematic AUC %.3f out of band %s" % (b_th, BASELINE_BAND))
        if not nocontext_is_chance:
            why.append("no-context AUC %.4f != 0.5" % c_th)
        if degenerate_scenes:
            why.append("degenerate_scenes %s" % degenerate_scenes)
        if heldout_absent_from_reduced:
            why.append("heldout leaked into reduced base %s" % heldout_absent_from_reduced)
        if n < 20:
            why.append("n_heldout %d < 20" % n)
        verdict_msg = "GATE_FAIL: " + "; ".join(why)
    else:
        significant = p_le0 < HP_ALPHA
        if thematic_gap >= HP_GAP and a_th >= HP_AUC and significant:
            verdict = "HARD_PASS"
            verdict_msg = ("HARD_PASS: cross-sentence overlay recovers held-out THEMATIC "
                           "meaning significantly better than within-sentence window "
                           "(a_cross=%.3f b_within=%.3f gap=%.3f p=%.4f); the fed-context + "
                           "target fixes resolve the v1 weak result" % (a_th, b_th, thematic_gap, p_le0))
        elif thematic_gap >= MB_GAP and a_th > b_th:
            verdict = "MIDDLE_BAND"
            verdict_msg = ("MIDDLE_BAND: cross-sentence helps thematic recovery weakly "
                           "(a_cross=%.3f b_within=%.3f gap=%.3f p=%.4f CI=[%.3f,%.3f]) but "
                           "below significance/strict-AUC bar" % (a_th, b_th, thematic_gap, p_le0, ci_lo, ci_hi))
        else:
            verdict = "HARD_FAIL"
            verdict_msg = ("HARD_FAIL: cross-sentence overlay no better than within-sentence "
                           "on thematic recovery (a_cross=%.3f b_within=%.3f gap=%.3f) -- deeper "
                           "issue than fed-context/target; likely needs multi-source grounding"
                           % (a_th, b_th, thematic_gap))

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": ("%s | PRIMARY thematic AUC: a_cross=%.3f b_within=%.3f c_nocontext=%.3f "
                    "gap=%.3f p=%.4f | CONTRAST taxon AUC: a_cross=%.3f b_within=%.3f d_dict=%.3f "
                    "d_lookup_acc=%.3f | n=%d cov_base=%.4f cov_surround=%.4f"
                    % (verdict, a_th, b_th, c_th, thematic_gap, p_le0, a_tx, b_tx, d_tx,
                       d_lookup_acc, n, cov_full, cov_sur)),
        "run_mode": run_mode,
        "elapsed_s": round(elapsed, 3),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seed": SEED, "window": WINDOW, "active_m": ACTIVE_M, "min_occ": MIN_OCC,
        "prereg_bands": {
            "coverage_gate": COVERAGE_GATE, "hp_auc": HP_AUC, "hp_gap": HP_GAP,
            "hp_alpha": HP_ALPHA, "mb_gap": MB_GAP, "baseline_band": list(BASELINE_BAND),
            "primary_metric": "thematic_neighbor_AUC", "primary_gap": "a_cross - b_within",
        },
        "coverage": {
            "full_base_gate": round(cov_full, 4), "full_base_frac": [kf, tf],
            "understood_surround_gate": round(cov_sur, 4), "surround_frac": [ks, ts],
            "reduced_base_info_only": round(cov_red, 4),
            "gate_passed": bool(cov_full >= COVERAGE_GATE and cov_sur >= COVERAGE_GATE),
            "heldout_leaked_into_reduced_base": heldout_absent_from_reduced,
        },
        "primary_thematic_auc": {
            "a_cross_overlay": round(a_th, 4),
            "b_within_sentence": round(b_th, 4),
            "c_no_context": round(c_th, 4),
            "d_dictionary": round(d_th, 4),
        },
        "contrast_taxonomic": {
            "a_cross_overlay_auc": round(a_tx, 4),
            "b_within_sentence_auc": round(b_tx, 4),
            "d_dictionary_auc": round(d_tx, 4),
            "d_dictionary_lookup_accuracy_CEILING": round(d_lookup_acc, 4),
            "note": "context arms expected WEAK on taxonomy; dictionary STRONG -- the target-mismatch",
        },
        "primary_gap_a_minus_b": round(thematic_gap, 4),
        "bootstrap": {"ci95_lo": round(ci_lo, 4), "ci95_hi": round(ci_hi, 4),
                      "p_gap_le_0": round(p_le0, 4), "n_boot": n_boot, "n_words": n_common},
        "n_heldout_present": n,
        "n_known_present": len(known_present),
        "heldout_scene_distribution": dict(scene_counts_held),
        "known_scene_distribution": dict(scene_counts_known),
        "degenerate_scenes": degenerate_scenes,
        "baseline_in_band": bool(baseline_in_band),
        "nocontext_is_chance_0p5": bool(nocontext_is_chance),
        "overlay_telemetry": {
            "module": "hdlab.state_of_mind.WorkingOverlay (unmodified)",
            "heldout_surprise_new_flag_total": int(sum(surprise_new.values())),
            "heldout_words_all_surprise_flagged": bool(
                all(surprise_new.get(w, 0) > 0 for w in held_present)),
            "known_recognized_total": int(sum(known_recog.values())),
            "mean_active_set_content_heads": round(
                sum(active_sizes) / len(active_sizes), 2) if active_sizes else 0.0,
        },
        "dropped_heldout_low_occ": dropped_held,
        "dropped_known_absent": dropped_known,
        "n_detected_names_excluded": len(names),
        "arms_differ_verified": True,
        "arms_differ_digests": arms_digests,
        "final_metrics_atomicity": "tmp_replace",
        "compute_class": "sequential_cpu_wall_lt_30s_symbolic_overlay_no_hd_primitive",
        "leak_fix": "context vectors exclude the target itself AND the entire held-out set "
                    "(v1 leaked held-out identities for self-co-occurring words)",
        "anti_circularity": "thematic + taxonomic golds hand-authored independently; context "
                            "arms never look up a held-out word's label; dictionary is the only "
                            "lookup and only for taxonomy",
        "v1_reference": {
            "cell": "exp_base_first_reader_heldout_context_learn_v1",
            "v1_taxonomic_a_wnsup": 0.234, "v1_taxonomic_b": 0.170, "v1_gap": 0.064,
            "v1_p": 0.1954, "v1_dict_ceiling": 0.979,
            "note": "v1 measured TAXONOMIC accuracy (the WRONG target); this cell measures "
                    "THEMATIC AUC (the right target for distributional context) as PRIMARY",
        },
        "per_word": per_word,
    }
    return metrics


# ------------------------------------------------------------------- self-test
def self_test():
    """Exercises the REAL code path: constructs the REAL WorkingOverlay + SetKnownBase, and
    asserts cross-sentence context recovers a thematic pair that the within-sentence window
    MISSES. Fails loud before any full run."""
    # toy discourse: 'nest' shares no SENTENCE with 'hen'/'egg' (within-sentence MISSES the
    # pair); only the cross-sentence running picture carries hen/egg into nest's context. A
    # FARMYARD block and a HOME block are separated by neutral filler so the recency window
    # clears one scene before the next (working-memory scoping). scene gold cross-cuts.
    def S(s):
        toks = s.split()
        return ([t.capitalize() if i == 0 else t for i, t in enumerate(toks)],
                [t for t in toks])
    filler = [S("boys run in the road") for _ in range(4)]   # flush working memory between scenes
    toy_paths = [("toy", (
        [S("ned fed the hen"), S("the hen and the chick"), S("look at the nest")]
        + filler
        + [S("ann has the hat"), S("the hat and the box"), S("get the cap")]
    ))]
    known = {"hen", "chick", "hat", "box"}
    heldg = {"nest", "cap"}
    targets = known | heldg
    lemma = make_lemmatizer(targets)
    names = {"ned", "ann"}
    romans = set()
    scene = {"hen": "FARMYARD", "chick": "FARMYARD", "nest": "FARMYARD",
             "hat": "HOME", "box": "HOME", "cap": "HOME"}
    reduced_base = {"the", "a", "fed", "and", "look", "at", "has", "get", "boys", "run",
                    "in", "road", "hen", "chick", "hat", "box", "ned", "ann"}  # nest/cap held out

    a_vecs, a_occ, surprise_new, _kr, _asz = build_cross_sentence_vectors(
        toy_paths, targets, heldg, lemma, names, romans, reduced_base, 10, 10)
    flat = list(toy_paths[0][1])
    b_vecs, b_occ = build_within_sentence_vectors(flat, targets, heldg, lemma, names, romans, 4)

    known_words = sorted(known)
    a_th = per_word_auc(a_vecs, a_vecs, scene, ["nest"], known_words)
    b_th = per_word_auc(b_vecs, b_vecs, scene, ["nest"], known_words)
    assert "nest" in a_th, "self-test: cross-sentence produced no AUC for nest"
    assert a_th["nest"] > 0.5, ("self-test: cross-sentence should rank hen/egg above hat/box "
                                "for nest, got AUC=%.3f" % a_th["nest"])
    # within-sentence sees only {see} for nest -> hen/egg not in its window -> no discrimination
    assert (("nest" not in b_th) or b_th["nest"] <= a_th["nest"]), (
        "self-test: within-sentence should NOT beat cross-sentence on nest "
        "(a=%.3f b=%s)" % (a_th["nest"], b_th.get("nest")))
    # leak fix: no held-out word appears as a feature in any vector
    for w, vec in list(a_vecs.items()) + list(b_vecs.items()):
        for h in vec:
            assert h not in heldg, "self-test: LEAK -- held-out %r used as feature for %r" % (h, w)
    # surprise: held-out words flagged new by the real overlay KnownBase
    assert surprise_new.get("nest", 0) > 0, "self-test: overlay failed to surprise-flag nest"
    # no-context AUC == 0.5
    c_vecs = {w: Counter() for w in targets}
    c_th = per_word_auc(c_vecs, c_vecs, scene, ["nest"], known_words)
    assert abs(c_th.get("nest", 0.5) - 0.5) < 1e-9, "self-test: no-context AUC should be 0.5"
    # arms-differ raises on identical
    try:
        _arms_differ({"x": {"w": Counter({"a": 1})}, "y": {"w": Counter({"a": 1})}})
        raise AssertionError("self-test: _arms_differ failed to catch identical arms")
    except AssertionError as e:
        if "META_RULE_AF" not in str(e):
            raise
    # real WordNet lookup path
    assert dict_lookup("hen") == "ANIMAL", "self-test: wn lookup hen should be ANIMAL"
    print("SELFTEST_PASS: real overlay cross-sentence recovers thematic pair window misses; "
          "leak-fixed; surprise fires; no-context=0.5; arms-differ; wn OK", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run-mode", default=None)
    args = ap.parse_args()

    run_mode = "full"
    if args.run_mode:
        run_mode = args.run_mode
    elif args.self_test:
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"

    _write_start_marker(OUTPUT_DIR, run_mode)

    if run_mode == "self_test":
        self_test()
        _atomic_write_metrics(OUTPUT_DIR, {
            "anchor_name": ANCHOR_NAME, "verdict": "SELFTEST_PASS",
            "verdict_msg": "SELFTEST_PASS (self-test only; not a full run)",
            "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": 0.0,
        })
        return

    # full/smoke: self-test first (fail loud before the run), then pipeline
    self_test()
    n_boot = 800 if run_mode == "smoke" else N_BOOT
    metrics = run_pipeline(run_mode, n_boot)
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    print(metrics["summary"], flush=True)
    print(metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
