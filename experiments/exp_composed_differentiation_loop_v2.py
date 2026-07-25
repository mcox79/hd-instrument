"""composed_differentiation_loop_v2 -- can our OWN parts (competitive-Hebbian concept_encoder +
MDL model-selection learner) LEARN fine-meaning discrimination that GENERALIZES to NEW concepts,
over REAL typed WorldTree relations, with NO borrowed vectors in the build?

V2 CHANGES (VET of v1, atom 29561, commit 05834fbc8 -- 3 required fixes + denser source):
  (A) SCORER FIX (fairness gate): v1 always placed gold at candidate index 0 and an abstaining
      predictor returned index 0 -> auto-scored correct, inflating MFV to 0.97 (true base-rate ~0.06)
      and contaminating every learned/frozen-learned bar. V2 RANDOMIZES gold position per item
      (deterministic per-item hash) so an abstain/fixed-index fallback yields ~chance (1/n_cand), not
      auto-correct. All scorers score pick == it['gold_pos']. Honest MFV/base-rate recomputed.
  (B) CE->LEARNER BRIDGE: v1 fed the MDL learner ~20 raw high-cardinality ConceptEncoder active-dim
      tokens per concept (CE<dim>), blowing up description length -> compression<1 -> false
      KEEP_EPISODIC. V2 QUANTIZES the native ConceptEncoder codes into K cluster PROTOTYPES (mini
      k-means over concept_hds, deterministic) and feeds ONE low-cardinality CEPROTO<k> token per
      concept -- a LEARNED category the MDL plugins can compress over. The estimation (category
      generalizer) key uses symbolic KINDOF when present, ELSE the earned CEPROTO category (CE
      supplies a category where the symbolic KB is silent). Held-out concepts -> nearest train
      concept (CE cosine) -> its prototype. NO borrowed vector enters the CE code (WTA native).
  (C) FREQUENCY-MATCHED HARD DISTRACTORS: v1 drew neutral distractors uniformly from the relation
      pool -> the frequency prior (MFV) could win trivially. V2 draws distractors from the SAME
      marginal-frequency quantile bin as the gold value (standard freq-matched hard-negative binning)
      excluding the concept's valid values + aliases -- restores confusability WITHOUT representation
      bias, so MFV cannot preferentially pick gold from a same-frequency distractor.
  DENSER SOURCE: widened from the 8-table slice to ~40 AUDITED clean WorldTree tablestore tables --
      multi-valued PROP-* property tables (break MFV-saturation) + structural feature relations
      (KINDOF/MADEOF/PARTOF/HABITAT/USEDFOR/CONTAINS/SOURCEOF/LOCATIONS/XIVORE/PREDATOR-PREY/AFFECT).
      Per-table parse precision audited; only clean tables kept. Widened frac_ge2 reported.

THE WALL (atoms 29544-29557 + BGE/GloVe diagnostics): over frozen GloVe the substrate cannot tell
a concept's CORRECT fine value from a lexically-plausible-but-WRONG one; a learned readout over
frozen GloVe MEMORIZES (held-out-to-NEW-concepts ~0.128) and even a learned readout over BGE-large
reaches only 0.228 held-out. THIS cell tests whether composing our competitive-Hebbian
representation (hdlab/concept_encoder.py) with our MDL learner (hdlab/learner/) over REAL typed
relations EARNS generalizing fine meaning -- generalization at the FEATURE/RELATION level (shared
across concepts), NOT a per-concept lookup. If the only thing that works is per-concept
memorization, the learner's compression_ratio is <1 and it returns KEEP_EPISODIC -- that is the
built-in generalize-not-memorize guardrail and it is reported as an HONEST fail, never hidden.

BRAIN-FIDELITY MAP (element -> brain mechanism -> our impl SHAPE/ORDER/METRIC + flagged gaps):
  concept_encoder ............ cortical competitive-Hebbian / WTA sparse coding (Foldiak/Kohonen).
                               SHAPE ok. GAP: batch accumulator = ORDER-INVARIANT, so it cannot
                               express Rogers-McClelland curriculum (coarse->fine) LEARNING
                               DYNAMICS; label-conditioned aggregation is binding, not error-driven
                               prediction. Flagged, not glossed.
  typed-relation features .... Rogers-McClelland PDP relational differentiation. We supply the
                               relations as co-active features; coarse->fine is reported as a
                               STATIC signature (coarse KINDOF vs fine held-out acc), not a dynamic.
  learner MDL gate ........... Complementary Learning Systems (McClelland-McNaughton-O'Reilly):
                               promote-a-rule = neocortical SEMANTIC generalization; KEEP_EPISODIC
                               = hippocampal EPISODIC retention. MDL (two-part code) is the
                               computational-level formalization of that trade-off. Right shape.
  working-memory co-activation Cowan ~4 central items: we cap co-active relations per concept at
                               MAX_COACTIVE_REL=4 (matches WorldTree ~2.5-central-fact diagnostic);
                               20-relations-at-once would be non-brain. Right shape+metric.
  supervision = error ........ learner is error-driven (MDL compression == description-length
                               error). concept_encoder is label-conditioned (GAP, flagged).

PLUGINS (brain-compliant lead): ruleind (PFC rule learning) + estimation/gam (evidence/graded
integration) are PRIMARY. proginduction (enumerative boolean-DSL symbolic regression) has NO direct
biological analog AND its <=2-output boolean form is structurally unsuited to a hundreds-of-values
multiclass target; excluded by default (INCLUDE_PROGIND flag). If ever enabled and it wins, that is
reported explicitly as a measured departure from biology.

FAIRNESS GATES (all pre-registered, all reported):
  G1 MFV baseline (most-frequent-value per relation): composed win MUST beat MFV, not just chance.
  G2 SHUFFLED-RELATION control: shuffle rel->value; learner held-out MUST collapse to ~MFV.
  G3 apples-to-apples: GloVe zero-fit AND GloVe-learned recomputed on the SAME items/split/neutral
     distractors (BGE-learned 0.228 is a CITED external bar; inline BGE-model recompute is out of
     scope -- flagged). Distractors are REPRESENTATION-NEUTRAL (random from the relation's pool),
     identical for every arm.
  G4 no-leak + non-circular: held-out concepts NEVER in any training episode; the target relation
     is EXCLUDED from a concept's own input features (asserted).
  G5 ablation: (a) learner/ridge over GloVe, (b) learner over native concept_encoder codes only,
     (c) native-encoder cosine with NO learner, plus composed-without-CE -- attributes the signal.
  G6 coverage honesty: report scorable held-out fraction; aggregate over ALL held-out (unscorable
     counted, not dropped).

DATA-INTEGRITY PREFLIGHT (garbage-in guard; gates FULL-run INTERPRETATION):
  - relation-label precision proxy (curated-column tables are high-precision by construction;
    reported per relation with the clean-parse fraction),
  - multi-valid-value rate (distractors exclude ALL of a concept's valid values + aliases),
  - concept/value identity normalization (WordNet morphy lemmatize + plural merge),
  - per-concept relation-count density (held-out scorable iff >=2 distinct relations).

VERDICT (a priori):
  EARNS-GENERALIZING-MEANING = composed held-out CI-lower > max(MFV, BGE 0.228) AND
    (composed - MFV) >= MARGIN AND compression_ratio > 1 (chosen != KEEP_EPISODIC) AND shuffle
    collapses AND composed > GloVe-learned.
  MEMORIZES-KEEP-EPISODIC (HARD_FAIL) = chosen==KEEP_EPISODIC OR compression<=1 OR
    composed held-out <= max(MFV, 0.228) OR shuffle survives.
  MIDDLE = beats MFV+chance with compression>1 but not to the clear bar.
  DATA_NOT_READY / SETUP_GAP = preflight fails -> STOP before headline accuracy (honest).

Contract: INLINE-LOCAL foreground-to-completion (GloVe/WordNet large/git-ignored, not remote-
portable); NO push/remote-persist; ASCII-only; deterministic (fixed int seeds, numpy default_rng,
sorted iteration; no builtin-hash-seeded RNG); repo .venv; agent-reported VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker at entry ; crash-diagnostic ; heartbeat
# - real_code_path: self_test parses REAL tables + builds REAL ConceptEncoder + REAL learner.learn
#   at tiny scale AND a PLANTED separable env asserting the learner GENERALIZES to held-out when a
#   relational rule exists, and KEEP_EPISODIC/collapse when only per-concept identity predicts
# - arms_differ: composed vs glove-zerofit vs glove-learned vs shuffled held-out scores differ
# - no-leak + non-circular asserted; deterministic_seeding; baseline_in_band (frozen near chance)
# - discriminator_fires: composed held-out must exceed MFV in smoke (else respec)
# - storage = no_composition (self-contained differentiation cell)
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import re
import sys
import json
import time
import math
import hashlib
import argparse
import platform
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (  # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)
from hdlab.concept_encoder import ConceptEncoder  # noqa: E402
from hdlab.learner import registry as LEARNER  # noqa: E402
from hdlab.learner.core import KEEP_EPISODIC  # noqa: E402
from hdlab.learner.plugins import estimation_plugin, ruleind_plugin  # noqa: E402

ANCHOR_NAME = "composed_differentiation_loop_v2"

# ---------------------------------------------------------------------------
# config (a priori; NOT tuned for PASS)
# ---------------------------------------------------------------------------
PRETRAIN_DIM = 300
CE_N_DIM = 1024
CE_K_SPARSITY = 0.02
K_DISTRACT = 5                    # candidate = gold + up to K freq-matched distractors (K adapts to
                                 # same-freq-bin pool size; chance = mean(1/n_cand), reported)
HELDOUT_FRAC = 0.20               # fraction of CONCEPTS held out entirely (never in any episode)
MAX_COACTIVE_REL = 4              # Cowan-4 working-memory cap on co-active relation features
SEEDS_FULL = (20260725, 13, 101)  # 3 splits for held-out robustness
SEEDS_SMOKE = (20260725,)
INCLUDE_GAM = True                # graded integrator (brain-compliant); dropped if smoke too slow
INCLUDE_PROGIND = False           # no biological analog + boolean-DSL unsuited to multiclass value

# V2 CE->learner bridge: quantize native ConceptEncoder codes into K cluster prototypes so the MDL
# learner sees ONE low-cardinality CEPROTO<k> category token per concept (NOT ~20 raw high-card dims).
CE_N_PROTOTYPES = 48             # k-means cluster count over train concept_hds (learned categories)
CE_KMEANS_ITERS = 12             # deterministic mini-batch-free Lloyd iterations (small n_concepts)
FREQ_MATCH_BINS = 4              # marginal-frequency quantile bins for freq-matched hard distractors

# V2 FREQ-MATCHED HARD DISTRACTORS: distractors drawn from the gold value's SAME marginal-frequency
# quantile bin (standard freq-matched hard-negative binning) -> the frequency prior (MFV) cannot
# preferentially pick gold; confusability restored WITHOUT representation bias.

# curated column-stable tables (relation == table name), AUDITED (subj_col, val_col) from the full
# WorldTree v2.1 tablestore. COARSE = structural/category FEATURE backbone (drives density +
# prediction); FINE = multi-valued property/relational TARGETS (break MFV-saturation). Per-table
# parse precision is audited at runtime (precision_proxy); relations below floor are surfaced.
CURATED_TABLES = (
    # --- COARSE structural / category feature backbone (concepts recur here) ---
    ("KINDOF", 1, 4),           # hyponym -> hypernym (category)
    ("MADEOF", 2, 6),           # object -> material
    ("PARTOF", 1, 5),           # part -> whole
    ("HABITAT", 3, 5),          # organism -> habitat
    ("LOCATIONS", 2, 4),        # thing/process -> location
    # --- FINE multi-valued PROP-* property targets (low-cardinality pools) ---
    ("PROP-MAGNETISM", 0, 3),           # material -> magnetic/nonmagnetic/ferromagnetic
    ("PROP-CONDUCTIVITY", 0, 3),        # object -> conductor/insulator
    ("PROP-CHEM-ACIDITY", 0, 5),        # substance -> acidic/neutral/basic
    ("PROP-HARDNESS", 2, 5),            # object -> hard/soft
    ("PROP-WARM-COLD-BLOODED", 1, 3),   # animal -> warm/cold-blooded
    ("PROP-SOLUBILITY", 0, 3),          # substance -> soluble/insoluble
    ("PROP-MAT-OPACITY", 2, 5),         # thing -> transparent/translucent/opaque/reflective
    ("PROP-MAT-DURABILITY", 1, 3),      # thing -> durable/fragile
    ("PROP-FLEX-RIGIDITY", 1, 5),       # object -> flexible/rigid
    ("PROP-RECYCLABLE", 1, 3),          # object -> recyclable/non-recyclable
    ("PROP-CHEM-REACT", 1, 8),          # thing -> reactive/inactive
    ("PROP-CHEM-CHARGE", 2, 4),         # thing -> positive/negative/neutral
    ("PROP-RESOURCES-RENEWABLE", 0, 4), # resource -> renewable/nonrenewable
    ("PROP-INHERITEDLEARNED", 3, 8),    # agent -> inherited/learned
    ("PROP-STATESOFMATTER-TEMPS", 0, 2),# material -> gas/liquid/solid state
    # --- FINE typed relational targets (multi-valued, open-ish pools) ---
    ("XIVORE", 1, 4),           # animal -> herbivore/carnivore/omnivore
    ("PREDATOR-PREY", 2, 5),    # animal -> prey/predator
    ("CONSUMERS-EATING", 0, 3), # organism -> organism eaten
    ("USEDFOR", 2, 6),          # object -> purpose
    ("CONTAINS", 2, 6),         # object -> contents
    ("SOURCEOF", 2, 7),         # agent -> what it provides
    ("FORMEDBY", 2, 4),         # object -> forming agent/process
)
# COARSE = structural/category feature relations (predictors + density backbone).
# AFFECT (parse precision 0.47) + INSTANCES (0.69) DROPPED by the runtime precision audit (< 0.70).
COARSE_RELS = ("KINDOF", "MADEOF", "PARTOF", "HABITAT", "LOCATIONS")
RELATIONS = tuple(t for (t, _, _) in CURATED_TABLES)
REL_IDX = {r: i for i, r in enumerate(RELATIONS)}
NREL = len(RELATIONS)
_TABLE_DIR = os.path.join(_REPO, "data", "corpora", "worldtree",
                          "WorldtreeExplanationCorpusV2.1_Feb2020", "tablestore", "v2.1", "tables")

STOP = {"", "a", "an", "the", "some", "all", "many", "most", "something", "that", "this",
        "they", "it", "other", "of", "for", "to", "is", "are", "and", "or", "kind", "type"}

# ---------------------------------------------------------------------------
# pre-registered bands (a priori)
# ---------------------------------------------------------------------------
BGE_LEARNED_BAR = 0.228          # CITED@data/exp_bge_finemeaning_wall_probe_v1/metrics.json (0.2278)
MARGIN_OVER_MFV = 0.03           # composed held-out must beat MFV by this to be a genuine learn
SHUFFLE_COLLAPSE_EPS = 0.03      # shuffled held-out must be <= MFV + this (collapse)
MIN_HELDOUT_ITEMS = 60           # < this -> noise-floor breach (INVALID)
FROZEN_SAT = 0.85                # GloVe frozen held-out >= this -> task too easy (INVALID)
MIN_REL_PRECISION_PROXY = 0.70   # per-relation clean-parse fraction floor (data-integrity)

_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat / atomic write
# ---------------------------------------------------------------------------
def _out_dir(suffix=""):
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# normalization / identity (data-integrity A: lemmatize + alias)
# ---------------------------------------------------------------------------
_WN = [None]


def _wn():
    if _WN[0] is None:
        try:
            from nltk.corpus import wordnet as wn
            wn.morphy("test")
            _WN[0] = wn
        except Exception:
            _WN[0] = False
    return _WN[0]


def _clean(s):
    s = s.strip().lower()
    s = s.split(";")[0].strip()
    s = re.sub(r"[^a-z0-9 \-]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _lemma_word(w):
    wn = _wn()
    if wn:
        for pos in ("n", "v", "a"):
            m = wn.morphy(w, pos)
            if m:
                return m
    # crude plural fallback if WordNet unavailable
    if len(w) > 3 and w.endswith("es"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def normalize_phrase(s):
    """Normalize a concept/value phrase: clean, lemmatize each word (WordNet morphy), rejoin."""
    c = _clean(s)
    if not c:
        return c
    words = [_lemma_word(w) for w in c.split()]
    return " ".join(words)


def _tok(phrase):
    out, cur = [], []
    for ch in phrase.lower():
        if "a" <= ch <= "z":
            cur.append(ch)
        else:
            if len(cur) >= 2:
                out.append("".join(cur))
            cur = []
    if len(cur) >= 2:
        out.append("".join(cur))
    return out


def meaning_vec(enc, phrase):
    acc = np.zeros(PRETRAIN_DIM, dtype=np.float32)
    got = False
    for w in _tok(phrase):
        fv = enc.fused(w)
        if fv is not None:
            acc = acc + fv
            got = True
    if not got:
        return None
    n = np.linalg.norm(acc)
    return (acc / n).astype(np.float32) if n > 0 else acc


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
    return (round(center - half, 4), round(center + half, 4))


# ---------------------------------------------------------------------------
# parse curated tables -> normalized (concept, relation, value) triples + precision proxy
# ---------------------------------------------------------------------------
def parse_tables(tables):
    """Return (triples, precision_proxy). precision_proxy[rel] = clean_parse_fraction (rows that
    yielded a valid normalized subj+val pair / total non-empty rows) -- a data-integrity proxy for
    curated column tables (high precision by construction; noisy free-text relations are excluded
    from CURATED_TABLES on purpose)."""
    import csv
    triples = []
    precision = {}
    for tbl, si, vi in tables:
        path = os.path.join(_TABLE_DIR, tbl + ".tsv")
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f, delimiter="\t"))
        n_rows = 0
        n_clean = 0
        for row in rows[1:]:
            if not any(c.strip() for c in row):
                continue
            n_rows += 1
            if len(row) <= max(si, vi):
                continue
            subj = normalize_phrase(row[si])
            val = normalize_phrase(row[vi])
            if subj in STOP or val in STOP or not subj or not val:
                continue
            if len(subj.split()) > 4 or len(val.split()) > 4:
                continue
            if subj == val:
                continue
            n_clean += 1
            triples.append((subj, tbl, val))
        precision[tbl] = round(n_clean / n_rows, 4) if n_rows else 0.0
    seen = set()
    out = []
    for t in triples:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return sorted(out), precision


# ---------------------------------------------------------------------------
# environment: normalized triples -> concepts, per-relation value pools, NEUTRAL candidate sets,
# per-concept relation profile (Cowan-4), held-out split. (G3 neutral distractors; G4 no-leak.)
# ---------------------------------------------------------------------------
def build_environment(enc, triples, seed, output_dir, kindof_cap=700):
    rng = np.random.default_rng(seed + 101)

    # cap dominant KINDOF for balance (deterministic)
    by_rel = defaultdict(list)
    for (c, r, v) in triples:
        by_rel[r].append((c, r, v))
    kept = []
    for r in sorted(by_rel.keys()):
        lst = sorted(set(by_rel[r]))
        if r in COARSE_RELS and kindof_cap and len(lst) > kindof_cap:
            idx = np.sort(rng.permutation(len(lst))[:kindof_cap])
            lst = [lst[i] for i in idx.tolist()]
        kept.extend(lst)
    kept = sorted(set(kept))

    concepts = sorted({c for (c, r, v) in kept})
    values = sorted({v for (c, r, v) in kept})
    _heartbeat(output_dir, "encode_frozen", {"n_concept": len(concepts), "n_value": len(values)})

    # frozen GloVe encode (for the borrowed-vector baseline arms + OOV filter)
    cvec = {c: mv for c in concepts if (mv := meaning_vec(enc, c)) is not None}
    vvec = {v: mv for v in values if (mv := meaning_vec(enc, v)) is not None}

    triples_iv = [(c, r, v) for (c, r, v) in kept if c in cvec and v in vvec]
    dropped = len(kept) - len(triples_iv)

    # all valid (gold) values per (concept, relation) -- multi-valid handled (G/data-integrity)
    gold_by_cr = defaultdict(set)
    rels_by_concept = defaultdict(set)
    valvec_by_concept = defaultdict(set)  # ALL of a concept's values (any relation) = alias-exclusion pool
    for (c, r, v) in triples_iv:
        gold_by_cr[(c, r)].add(v)
        rels_by_concept[c].add(r)
        valvec_by_concept[c].add(v)

    # per-relation value pool (distinct in-vocab gold values)
    pool = defaultdict(set)
    for (c, r, v) in triples_iv:
        pool[r].add(v)
    pool = {r: sorted(vs) for r, vs in pool.items()}

    # multi-valid-value rate
    n_cr = len(gold_by_cr)
    n_multi = sum(1 for k in gold_by_cr if len(gold_by_cr[k]) > 1)
    multi_valid_rate = round(n_multi / n_cr, 4) if n_cr else 0.0

    # concept relation-count density
    rel_counts = sorted(len(rels_by_concept[c]) for c in rels_by_concept)
    density = {"mean": round(float(np.mean(rel_counts)), 3) if rel_counts else 0.0,
               "median": int(np.median(rel_counts)) if rel_counts else 0,
               "frac_ge2": round(float(np.mean([1.0 if x >= 2 else 0.0 for x in rel_counts])), 4)
               if rel_counts else 0.0,
               "max": max(rel_counts) if rel_counts else 0}

    # value index (for frozen scoring)
    all_val = sorted(vvec.keys())
    vidx = {v: i for i, v in enumerate(all_val)}
    value_vecs = np.stack([vvec[v] for v in all_val], axis=0).astype(np.float32)
    all_conc = sorted(cvec.keys())
    cidx = {c: i for i, c in enumerate(all_conc)}
    concept_vecs = np.stack([cvec[c] for c in all_conc], axis=0).astype(np.float32)

    # held-out split BY CONCEPT (G4 no-leak)
    perm = np.random.default_rng(seed + 202).permutation(len(all_conc))
    n_hold = int(round(HELDOUT_FRAC * len(all_conc)))
    held_concepts = {all_conc[i] for i in perm[:n_hold].tolist()}

    # per-concept Cowan-4 relation profile: pick up to MAX_COACTIVE_REL relations deterministically,
    # KINDOF first (coarse anchor), then by global relation frequency, then alpha. profile[c] =
    # list of (rel, chosen_value) with ONE value per relation (the alpha-first gold).
    rel_freq = Counter(r for (c, r, v) in triples_iv)

    def _rel_rank(r):
        return (0 if r in COARSE_RELS else 1, -rel_freq[r], r)

    profile = {}
    for c in sorted(rels_by_concept.keys()):
        rs = sorted(rels_by_concept[c], key=_rel_rank)[:MAX_COACTIVE_REL]
        profile[c] = [(r, sorted(gold_by_cr[(c, r)])[0]) for r in rs]

    # V2 FIX C: marginal frequency of each value within each relation -> quantile freq bins for
    # FREQUENCY-MATCHED hard distractors (distractors from the gold value's SAME freq bin so the
    # frequency prior cannot preferentially pick gold). Standard freq-matched hard-negative binning.
    val_freq_by_rel = defaultdict(Counter)
    for (c, r, v) in triples_iv:
        val_freq_by_rel[r][v] += 1
    freq_bin = {}                                   # (r, value) -> quantile bin id [0, FREQ_MATCH_BINS)
    bin_members = defaultdict(lambda: defaultdict(list))  # r -> bin -> [values] (freq-ascending rank)
    for r in sorted(pool.keys()):
        ranked = sorted(((val_freq_by_rel[r][x], x) for x in pool[r]))  # ascending marginal freq
        nvp = len(ranked)
        for rank, (_fq, x) in enumerate(ranked):
            b = min(FREQ_MATCH_BINS - 1, int(rank * FREQ_MATCH_BINS / max(1, nvp)))
            freq_bin[(r, x)] = b
            bin_members[r][b].append(x)

    def _freqmatched_pool(r, gold, exclude):
        """Distractor candidates from gold's SAME freq bin (excluding concept's valid+alias values);
        widen to nearest bins ONLY if the same bin cannot supply K_DISTRACT."""
        gb = freq_bin[(r, gold)]
        cp = [x for x in bin_members[r][gb] if x not in exclude]
        if len(cp) < K_DISTRACT:
            for b in sorted(bin_members[r].keys(), key=lambda bb: (abs(bb - gb), bb)):
                if b == gb:
                    continue
                for x in bin_members[r][b]:
                    if x not in exclude and x not in cp:
                        cp.append(x)
                if len(cp) >= K_DISTRACT:
                    break
        return cp

    # build eval/train items: one item per (concept, TARGET relation r, gold value g). candidate set
    # = gold + up to K FREQ-MATCHED distractors (same-freq-bin, excluding ALL of the concept's valid
    # values + its alias value set). V2 FIX A: gold is placed at a RANDOMIZED position (per-item
    # deterministic rng) -> an abstaining / fixed-index predictor scores ~chance (1/n_cand), NOT
    # auto-correct. deterministic rng per item.
    items = []
    for (c, r, v) in triples_iv:
        p = pool[r]
        if len(p) < 2:
            continue
        exclude = set(gold_by_cr[(c, r)]) | valvec_by_concept[c]  # G/data-integrity: no false negatives
        cand_pool = _freqmatched_pool(r, v, exclude)
        if not cand_pool:
            continue
        _h = hashlib.md5(f"{seed}|{c}|{r}|{v}".encode("utf-8")).hexdigest()
        irng = np.random.default_rng(int(_h[:8], 16))
        take = min(K_DISTRACT, len(cand_pool))
        pick = irng.permutation(len(cand_pool))[:take]
        distractors = [cand_pool[i] for i in sorted(pick.tolist())]
        # V2 FIX A: randomize gold position among the distractors
        gold_pos = int(irng.integers(0, len(distractors) + 1))
        cand_vals = distractors[:gold_pos] + [v] + distractors[gold_pos:]
        # feats for this item = concept's OTHER relations (target r EXCLUDED -> G4 non-circular),
        # capped Cowan-4, as relation-value tokens, plus the ASK token.
        feats = [f"ASK={r}"]
        for (r2, v2) in profile[c]:
            if r2 == r:
                continue
            feats.append(f"{r2}={v2}")
        items.append({
            "concept": c, "relation": r, "gold": v, "cand_vals": cand_vals,
            "gold_pos": gold_pos,  # V2 FIX A: randomized gold index (was always 0 in v1)
            "gold_vi": vidx[v], "cand_vi": [vidx[x] for x in cand_vals], "c_i": cidx[c],
            "r_i": REL_IDX[r], "tier": ("coarse" if r in COARSE_RELS else "fine"),
            "held": (c in held_concepts), "feats": feats, "gold_class": v,
            "n_other_rel": sum(1 for (r2, _) in profile[c] if r2 != r),
        })

    return {
        "concept_vecs": concept_vecs, "value_vecs": value_vecs, "vidx": vidx, "cidx": cidx,
        "items": items, "pool": pool, "held_concepts": sorted(held_concepts),
        "gold_by_cr": {f"{k[0]}||{k[1]}": sorted(vs) for k, vs in gold_by_cr.items()},
        "profile": profile,
        "n_triples_parsed": len(kept), "n_triples_invocab": len(triples_iv), "dropped_oov": dropped,
        "n_concepts": len(all_conc), "n_values": len(all_val),
        "multi_valid_rate": multi_valid_rate, "density": density,
        "pool_sizes": {r: len(pool[r]) for r in sorted(pool)},
    }


# ---------------------------------------------------------------------------
# most-frequent-value per relation (G1)
# ---------------------------------------------------------------------------
def build_mfv(train_items):
    by_rel = defaultdict(Counter)
    for it in train_items:
        by_rel[it["relation"]][it["gold"]] += 1
    return {r: c.most_common(1)[0][0] for r, c in by_rel.items()}


def score_candidates_by_predicted(cand_vals, predicted, mfv_val):
    """Hard-vote candidate scorer: pick predicted if it is among candidates, else backoff to the
    relation MFV if it is among candidates, else a deterministic fixed index (0). Returns pick index.
    V2 FIX A: gold sits at a RANDOMIZED position, so the fixed-index abstain fallback yields ~chance
    (1/n_cand) -- NOT auto-correct (v1's index-0 gold auto-scored abstentions as correct)."""
    if predicted is not None and predicted in cand_vals:
        return cand_vals.index(predicted)
    if mfv_val is not None and mfv_val in cand_vals:
        return cand_vals.index(mfv_val)
    return 0  # fixed non-informative fallback; gold-pos is randomized so P(correct)=1/n_cand=chance


def score_candidates_graded(cand_vals, prob_of):
    """Graded scorer: prob_of(value)->float; argmax over candidates (ties -> lowest index)."""
    scores = [prob_of(v) for v in cand_vals]
    best = 0
    for i in range(1, len(scores)):
        if scores[i] > scores[best]:
            best = i
    return best


# ---------------------------------------------------------------------------
# arms
# ---------------------------------------------------------------------------
def frozen_zerofit_acc(env, items):
    """GloVe zero-fit: pick candidate with max cos(glove(concept), glove(cand)). (G3 apples-to-
    apples GloVe floor.) chance-fallback is inherent (no fit)."""
    if not items:
        return None, np.zeros(0, bool)
    cvecs = env["concept_vecs"]
    vvecs = env["value_vecs"]
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        c = cvecs[it["c_i"]]
        cand = vvecs[np.array(it["cand_vi"])]
        s = cand @ c
        correct[i] = (int(np.argmax(s)) == it["gold_pos"])  # V2 FIX A: gold at randomized pos
    return round(float(np.mean(correct)), 4), correct


def _ridge_readout(env, train_items, shuffle_seed=None):
    """Converged linear readout glove(c)+onehot(r) -> glove(gold). Exact ridge optimum. (G5-a /
    G3 GloVe-learned comparator == the borrowed-vector-learned analog of BGE-learned 0.228.)"""
    cvecs = env["concept_vecs"]
    vvecs = env["value_vecs"]
    ci = np.array([it["c_i"] for it in train_items])
    ri = np.array([it["r_i"] for it in train_items])
    gi = np.array([it["gold_vi"] for it in train_items])
    if shuffle_seed is not None:
        rng = np.random.default_rng(shuffle_seed)
        gi = gi.copy()
        byr = defaultdict(list)
        for pos, it in enumerate(train_items):
            byr[it["r_i"]].append(pos)
        for r in sorted(byr):
            pos = np.array(sorted(byr[r]))
            gi[pos] = gi[pos][rng.permutation(len(pos))]
    onehot = np.zeros((len(train_items), NREL), dtype=np.float32)
    onehot[np.arange(len(train_items)), ri] = 1.0
    X = np.concatenate([cvecs[ci], onehot], axis=1).astype(np.float32)
    Y = vvecs[gi].astype(np.float32)
    n, d = X.shape
    Xa = np.concatenate([X, np.ones((n, 1), dtype=np.float32)], axis=1)
    lam = max(1e-4 * n / 2.0, 1e-2)
    A = Xa.T @ Xa + lam * np.eye(d + 1, dtype=np.float64)
    Wa = np.linalg.solve(A.astype(np.float64), (Xa.T @ Y).astype(np.float64)).astype(np.float32)
    return Wa


def ridge_acc(env, Wa, items):
    if not items:
        return None, np.zeros(0, bool)
    cvecs = env["concept_vecs"]
    vvecs = env["value_vecs"]
    ci = np.array([it["c_i"] for it in items])
    ri = np.array([it["r_i"] for it in items])
    onehot = np.zeros((len(items), NREL), dtype=np.float32)
    onehot[np.arange(len(items)), ri] = 1.0
    X = np.concatenate([cvecs[ci], onehot], axis=1).astype(np.float32)
    Xa = np.concatenate([X, np.ones((len(items), 1), dtype=np.float32)], axis=1)
    pred = Xa @ Wa
    pn = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-12)
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        cand = vvecs[np.array(it["cand_vi"])]
        s = cand @ pn[i]
        correct[i] = (int(np.argmax(s)) == it["gold_pos"])  # V2 FIX A
    return round(float(np.mean(correct)), 4), correct


# ----- learner arms -----
def _kindof_of(it):
    for f in it["feats"]:
        if f.startswith("KINDOF="):
            return f.split("=", 1)[1]
    return None


def _make_estimation_key(feat_mode):
    """Category-generalizer key = (category || asked relation). V2: the category is the symbolic
    KINDOF value when present, ELSE (composed) the EARNED CE cluster prototype (it['ce_proto']) --
    the native encoder supplies a learned category where the symbolic KB is silent. Generalizes by
    category, NOT by concept identity."""
    def key(it):
        kind = _kindof_of(it)
        proto = it.get("ce_proto")
        if feat_mode == "relation":
            cat = kind or "__NOKIND__"
        elif feat_mode == "ce":
            cat = proto or "__NOCE__"
        else:  # relation_ce (composed): symbolic KINDOF first, else earned CE prototype
            cat = kind or proto or "__NOCAT__"
        return f"{cat}||{it['relation']}"
    return key


def run_learner(train_items, feat_mode, include_gam, include_progind, ce_feats_by_concept=None):
    """feat_mode: 'relation' (typed-relation tokens), 'ce' (CE cluster-prototype token only),
    or 'relation_ce' (both). Returns (chosen_name, chosen_result, all_results, feat_fn, est_key)."""
    def feat_fn(ep):
        fs = []
        if feat_mode in ("relation", "relation_ce"):
            fs.extend(ep["feats"])
        if feat_mode in ("ce", "relation_ce") and ce_feats_by_concept is not None:
            fs.extend(ce_feats_by_concept.get(ep["concept"], []))
            fs.append(f"ASK={ep['relation']}")  # keep the ask token in ce-only mode
        return fs

    est_key = _make_estimation_key(feat_mode)
    classes = sorted({it["gold_class"] for it in train_items})
    candidate_plugins = ["estimation", "ruleind"]
    if include_gam:
        candidate_plugins.append("gam")
    if include_progind:
        candidate_plugins.append("proginduction")
    spec = {
        "candidate_plugins": candidate_plugins,
        "min_compression_ratio": 1.0,
        "per_plugin": {
            "estimation": {"key_fn": est_key, "label_fn": lambda ep: ep["gold_class"],
                           "classes": classes},
            "ruleind": {"key_fn": lambda ep: ep["concept"], "max_conjunct": 2, "min_coverage": 3,
                        "purity_thresh": 0.60, "max_rules": 200, "max_singles_for_pairing": 40},
            "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": classes,
                    "min_coverage": 3, "max_singles_for_pairing": 40, "max_interactions": 20},
        },
    }
    chosen_name, chosen, results = LEARNER.learn(train_items, feat_fn, spec)
    return chosen_name, chosen, results, feat_fn, est_key


def learner_acc(chosen_name, chosen, feat_fn, items, mfv, est_key, ce_feats_by_concept=None):
    """Score held-out/in-vocab items with the MDL-chosen plugin. Held-out concept keys are unseen
    (ruleind residual + estimation key by category), so generalization comes only from the
    shared-feature hypothesis. Aggregate over ALL items (unscorable -> non-informative pick).
    V2 FIX A: correctness is pick == it['gold_pos'] (gold at randomized position)."""
    if not items or chosen_name == KEEP_EPISODIC or chosen is None:
        return None, np.zeros(len(items), bool), 0
    hyp = chosen.hypothesis
    correct = np.zeros(len(items), dtype=bool)
    n_scorable = 0
    for i, it in enumerate(items):
        cand = it["cand_vals"]
        mfv_val = mfv.get(it["relation"])
        scorable = it["n_other_rel"] > 0
        if scorable:
            n_scorable += 1
        if chosen_name == "estimation":
            counts = hyp["counts"].get(est_key(it), {})
            total = sum(counts.values())
            nc = hyp["n_classes"]
            pick = score_candidates_graded(cand, lambda v: (counts.get(v, 0) + 1) / (total + nc))
            # if key unseen (total==0) graded is uniform -> falls to index-order; use MFV backoff
            if total == 0:
                pick = score_candidates_by_predicted(cand, mfv_val, mfv_val)
        elif chosen_name == "ruleind":
            pred = ruleind_plugin.apply(hyp, feat_fn(it), key=it["concept"], default_class=mfv_val)
            pick = score_candidates_by_predicted(cand, pred, mfv_val)
        elif chosen_name == "gam":
            from hdlab.learner.plugins import gam_plugin
            s = gam_plugin.score(hyp, feat_fn(it))
            pick = score_candidates_graded(cand, lambda v: s.get(v, -1e30))
        else:
            pick = score_candidates_by_predicted(cand, mfv_val, mfv_val)
        correct[i] = (pick == it["gold_pos"])
    return round(float(np.mean(correct)), 4), correct, n_scorable


def mfv_acc(items, mfv):
    """G1: most-frequent-value baseline. pick MFV among candidates; if not present -> fixed index 0.
    V2 FIX A: gold at randomized pos, so MFV-absent falls to chance (not auto-correct); with
    freq-matched distractors MFV cannot preferentially pick gold => honest frequency-prior base-rate."""
    if not items:
        return None, np.zeros(0, bool)
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        mv = mfv.get(it["relation"])
        pick = it["cand_vals"].index(mv) if (mv in it["cand_vals"]) else 0
        correct[i] = (pick == it["gold_pos"])
    return round(float(np.mean(correct)), 4), correct


# ----- concept_encoder (native representation over REAL relations) -----
def _kmeans_spherical(X, k, iters, seed):
    """Deterministic spherical (cosine) k-means over L2-normalized rows. Returns int assignment
    [n]. Sparse-binary HD codes -> cosine is the natural metric; dot-product assignment via one
    (n x dim)@(dim x k) matmul per iter (cheap; no n*k*dim broadcast)."""
    n = X.shape[0]
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    if n <= k:
        return (np.arange(n) % max(1, k)).astype(np.int64)
    rng = np.random.default_rng(seed)
    cent = Xn[np.sort(rng.permutation(n)[:k])].copy()
    assign = np.zeros(n, dtype=np.int64)
    for _ in range(iters):
        assign = np.argmax(Xn @ cent.T, axis=1)
        for j in range(k):
            m = Xn[assign == j]
            if len(m):
                c = m.sum(0)
                nrm = np.linalg.norm(c)
                if nrm > 0:
                    cent[j] = c / nrm
    return assign.astype(np.int64)


def build_ce(train_items, env, seed):
    """Train ConceptEncoder on REAL relational sentences of TRAIN concepts (label = concept idx;
    mask_target_word removes the concept-name chars so the code reflects RELATIONAL CONTEXT).
    V2 BRIDGE FIX: QUANTIZE the native concept_hds codes into CE_N_PROTOTYPES cluster prototypes
    (deterministic spherical k-means) and emit ONE low-cardinality CEPROTO<k> token per concept --
    a LEARNED category the MDL plugins can compress over (v1 fed ~20 raw high-card CE<dim> tokens ->
    description-length blowup -> false KEEP_EPISODIC). Returns (encoder, train_concept_list,
    ce_feats_by_concept, proto_by_concept)."""
    profile = env["profile"]
    train_concepts = sorted({it["concept"] for it in train_items})
    cname_to_idx = {c: i for i, c in enumerate(train_concepts)}
    sentences, labels = [], []
    for c in train_concepts:
        for (r, v) in profile[c]:
            s = f"{c} {r.lower().replace('-', ' ')} {v}"
            sentences.append(s)
            labels.append(cname_to_idx[c])
    if len(train_concepts) < 2 or not sentences:
        return None, train_concepts, {}, {}
    enc = ConceptEncoder(n_dim=CE_N_DIM, n_concepts=len(train_concepts), k_sparsity=CE_K_SPARSITY,
                         seed=seed, concept_names=train_concepts, mask_target_word=True)
    enc.fit(sentences, np.asarray(labels, dtype=np.int64))
    # quantize the learned codes into K prototypes
    codes = np.asarray([enc.concept_hds[cname_to_idx[c]] for c in train_concepts], dtype=np.float32)
    k = min(CE_N_PROTOTYPES, max(2, len(train_concepts)))
    proto_assign = _kmeans_spherical(codes, k, CE_KMEANS_ITERS, seed + 555)
    proto_by_concept = {c: int(proto_assign[cname_to_idx[c]]) for c in train_concepts}
    ce_feats = {c: [f"CEPROTO{proto_by_concept[c]}"] for c in train_concepts}
    return enc, train_concepts, ce_feats, proto_by_concept


def ce_features_for_heldout(enc, train_concepts, proto_by_concept, env, held_concepts):
    """Held-out concept -> encode its relational sentences -> nearest TRAIN concept (CE cosine) ->
    that train concept's cluster PROTOTYPE token (transfer). Also returns the nearest-neighbor map
    for the no-learner ablation."""
    if enc is None:
        return {}, {}
    profile = env["profile"]
    ce_feats = {}
    nn_map = {}
    for c in held_concepts:
        rels = profile.get(c, [])
        if not rels:
            continue
        s = " . ".join(f"{c} {r.lower().replace('-', ' ')} {v}" for (r, v) in rels)
        res = enc.encode_with_result(s)
        cid = res.concept_id
        nn = train_concepts[cid] if 0 <= cid < len(train_concepts) else None
        nn_map[c] = nn
        if nn is not None and nn in proto_by_concept:
            ce_feats[c] = [f"CEPROTO{proto_by_concept[nn]}"]
    return ce_feats, nn_map


def ce_no_learner_acc(items, nn_map, train_gold_lookup, mfv):
    """G5-c: native-encoder cosine, NO learner. Predict held-out concept's value under relation r =
    the nearest-train-concept's gold value for r (if any), else MFV. Score candidates.
    V2 FIX A: correctness is pick == it['gold_pos']."""
    if not items:
        return None, np.zeros(0, bool)
    correct = np.zeros(len(items), dtype=bool)
    for i, it in enumerate(items):
        nn = nn_map.get(it["concept"])
        pred = None
        if nn is not None:
            pred = train_gold_lookup.get((nn, it["relation"]))
        mv = mfv.get(it["relation"])
        pick = score_candidates_by_predicted(it["cand_vals"], pred, mv)
        correct[i] = (pick == it["gold_pos"])
    return round(float(np.mean(correct)), 4), correct


# ---------------------------------------------------------------------------
# one seed/split
# ---------------------------------------------------------------------------
def run_split(enc_frozen, triples, precision, seed, output_dir, include_gam, kindof_cap):
    env = build_environment(enc_frozen, triples, seed, output_dir, kindof_cap=kindof_cap)
    items = env["items"]
    train_items = [it for it in items if not it["held"]]
    held_items = [it for it in items if it["held"]]
    n_ho_fine = sum(1 for it in held_items if it["tier"] == "fine")
    n_scorable_ho = sum(1 for it in held_items if it["n_other_rel"] > 0)
    _heartbeat(output_dir, "split_built", {"seed": seed, "train": len(train_items),
               "held": len(held_items), "held_fine": n_ho_fine})

    mfv = build_mfv(train_items)
    train_gold_lookup = {(it["concept"], it["relation"]): it["gold"] for it in train_items}

    # baselines (G1, G3)
    mfv_ho, _ = mfv_acc(held_items, mfv)
    frz_ho, frz_correct = frozen_zerofit_acc(env, held_items)
    frz_iv, _ = frozen_zerofit_acc(env, train_items)
    Wa = _ridge_readout(env, train_items)
    glv_ho, _ = ridge_acc(env, Wa, held_items)
    glv_iv, _ = ridge_acc(env, Wa, train_items)

    # concept_encoder native representation + CE-prototype quantization (G5-b, G5-c; V2 bridge)
    _heartbeat(output_dir, "build_ce", {"seed": seed})
    ce_enc, train_concepts, ce_train, proto_by_concept = build_ce(train_items, env, seed)
    ce_held, nn_map = ce_features_for_heldout(ce_enc, train_concepts, proto_by_concept,
                                              env, env["held_concepts"])
    ce_feats_all = dict(ce_train)
    ce_feats_all.update(ce_held)
    n_ce_prototypes = len(set(proto_by_concept.values())) if proto_by_concept else 0
    # ANNOTATE every item with its CE cluster prototype (est_key composed-mode reads it['ce_proto']).
    proto_all = dict(proto_by_concept)  # train concepts
    for c, nn in nn_map.items():        # held concepts via nearest-train transfer
        if nn is not None and nn in proto_by_concept:
            proto_all[c] = proto_by_concept[nn]
    for it in items:
        p = proto_all.get(it["concept"])
        it["ce_proto"] = (f"CEPROTO{p}" if p is not None else None)
    ce_nl_ho, _ = ce_no_learner_acc(held_items, nn_map, train_gold_lookup, mfv)

    # COMPOSED (relation features + CE prototype) -- the build
    _heartbeat(output_dir, "learner_composed", {"seed": seed})
    ch, chosen, results, feat_fn, ek = run_learner(train_items, "relation_ce", include_gam,
                                                   INCLUDE_PROGIND, ce_feats_all)
    comp_ho, comp_correct, comp_scorable = learner_acc(ch, chosen, feat_fn, held_items, mfv, ek, ce_feats_all)
    comp_iv, _, _ = learner_acc(ch, chosen, feat_fn, train_items, mfv, ek, ce_feats_all)
    compression = round(chosen.compression_ratio, 4) if chosen is not None else None

    # ablations (G5): relation-only, ce-only
    ch_r, chosen_r, res_r, ff_r, ek_r = run_learner(train_items, "relation", include_gam, INCLUDE_PROGIND, None)
    abl_rel_ho, _, _ = learner_acc(ch_r, chosen_r, ff_r, held_items, mfv, ek_r, None)
    ch_c, chosen_c, res_c, ff_c, ek_c = run_learner(train_items, "ce", include_gam, INCLUDE_PROGIND, ce_feats_all)
    abl_ce_ho, _, _ = learner_acc(ch_c, chosen_c, ff_c, held_items, mfv, ek_c, ce_feats_all)

    # SHUFFLED-RELATION control (G2): shuffle rel->value in TRAIN, re-run composed learner
    _heartbeat(output_dir, "shuffle_control", {"seed": seed})
    shuf_train = _shuffle_relation_targets(train_items, seed + 9090)
    ch_s, chosen_s, res_s, ff_s, ek_s = run_learner(shuf_train, "relation_ce", include_gam,
                                                    INCLUDE_PROGIND, ce_feats_all)
    shuf_ho, _, _ = learner_acc(ch_s, chosen_s, ff_s, held_items, mfv, ek_s, ce_feats_all)
    glv_shuf_Wa = _ridge_readout(env, train_items, shuffle_seed=seed + 9090)
    glv_shuf_ho, _ = ridge_acc(env, glv_shuf_Wa, held_items)

    chance = round(float(np.mean([1.0 / len(it["cand_vals"]) for it in held_items])), 4) if held_items else None

    return {
        "seed": seed, "n_train": len(train_items), "n_held": len(held_items),
        "n_held_fine": n_ho_fine, "n_scorable_held": n_scorable_ho,
        "chance": chance, "mfv_held": mfv_ho,
        "frozen_glove_held": frz_ho, "frozen_glove_invocab": frz_iv,
        "glove_learned_held": glv_ho, "glove_learned_invocab": glv_iv,
        "ce_no_learner_held": ce_nl_ho,
        "composed_held": comp_ho, "composed_invocab": comp_iv,
        "composed_chosen_plugin": ch, "composed_compression_ratio": compression,
        "composed_scorable_held": comp_scorable,
        "abl_relation_only_held": abl_rel_ho, "abl_relation_only_plugin": ch_r,
        "abl_ce_only_held": abl_ce_ho, "abl_ce_only_plugin": ch_c,
        "shuffle_control_held": shuf_ho, "shuffle_control_plugin": ch_s,
        "glove_learned_shuffle_held": glv_shuf_ho,
        "all_plugin_compression": {k: round(v.compression_ratio, 4) for k, v in results.items()},
        "ce_active": ce_enc is not None, "n_ce_prototypes": n_ce_prototypes,
        "_comp_correct": comp_correct.tolist(),
        "_frz_correct": frz_correct.tolist(),
        "_env_meta": {"n_triples_parsed": env["n_triples_parsed"], "n_triples_invocab": env["n_triples_invocab"],
                      "dropped_oov": env["dropped_oov"], "n_concepts": env["n_concepts"],
                      "n_values": env["n_values"], "multi_valid_rate": env["multi_valid_rate"],
                      "density": env["density"], "pool_sizes": env["pool_sizes"],
                      "n_held_concepts": len(env["held_concepts"])},
    }


def _shuffle_relation_targets(train_items, seed):
    """Permute gold values within each relation (marginals preserved; concept->value destroyed)."""
    rng = np.random.default_rng(seed)
    byr = defaultdict(list)
    for it in train_items:
        byr[it["relation"]].append(it)
    out = []
    for r in sorted(byr):
        grp = byr[r]
        golds = [it["gold"] for it in grp]
        perm = rng.permutation(len(golds))
        for it, j in zip(grp, perm.tolist()):
            nit = dict(it)
            nit["gold"] = golds[j]
            nit["gold_class"] = golds[j]
            out.append(nit)
    return out


# ---------------------------------------------------------------------------
# data-integrity preflight verdict
# ---------------------------------------------------------------------------
def preflight_verdict(precision, env_meta):
    noisy = {r: p for r, p in precision.items() if p < MIN_REL_PRECISION_PROXY}
    ok = (len(noisy) == 0 and env_meta["density"]["frac_ge2"] >= 0.20)
    return {
        "passed": bool(ok),
        "per_relation_precision_proxy": {r: precision[r] for r in sorted(precision)},
        "relations_below_floor": noisy,
        "multi_valid_value_rate": env_meta["multi_valid_rate"],
        "concept_relation_density": env_meta["density"],
        "note": ("curated column-stable tables (precision by construction; free-text noisy relations "
                 "e.g. IFTHEN excluded a priori). scorable held-out requires >=2 distinct relations."),
    }


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------
def _agg(splits, key):
    vals = [s[key] for s in splits if s.get(key) is not None]
    return round(float(np.mean(vals)), 4) if vals else None


def decide(splits, preflight):
    comp = _agg(splits, "composed_held")
    mfv = _agg(splits, "mfv_held")
    glv_zf = _agg(splits, "frozen_glove_held")
    glv_ln = _agg(splits, "glove_learned_held")
    shuf = _agg(splits, "shuffle_control_held")
    chance = _agg(splits, "chance")
    compression = _agg(splits, "composed_compression_ratio")
    chosen_plugins = [s["composed_chosen_plugin"] for s in splits]
    keep_episodic = all(p == KEEP_EPISODIC for p in chosen_plugins)

    # pooled held-out CI (sum correct over splits)
    k = sum(int(round(s["composed_held"] * s["n_held"])) for s in splits if s["composed_held"] is not None)
    n = sum(s["n_held"] for s in splits if s["composed_held"] is not None)
    comp_ci = wilson_ci(k, n) if n else (0.0, 0.0)
    n_ho_fine = sum(s["n_held_fine"] for s in splits)

    bar = max(mfv or 0.0, BGE_LEARNED_BAR)
    extra = {"composed_held": comp, "mfv_held": mfv, "glove_zerofit_held": glv_zf,
             "glove_learned_held": glv_ln, "shuffle_control_held": shuf, "chance": chance,
             "compression_ratio": compression, "chosen_plugins": chosen_plugins,
             "composed_ci": list(comp_ci), "bar_to_beat": round(bar, 4),
             "bge_learned_bar": BGE_LEARNED_BAR, "n_heldout_fine_total": n_ho_fine}

    # TASK-VALIDITY: MFV-saturation. If the frequency prior already solves the task (base-rate null
    # near-perfect), the fine-discrimination generalization test cannot demonstrate signal -- any
    # "beats chance" is trivial and the real bar (MFV) is unbeatable. Surfaced explicitly.
    freq_saturated = (mfv is not None and mfv >= FROZEN_SAT)
    extra["task_freq_saturated"] = bool(freq_saturated)

    if not preflight["passed"]:
        return ("DATA_NOT_READY", f"data-integrity preflight FAILED (relations_below_floor="
                f"{preflight['relations_below_floor']}, density={preflight['concept_relation_density']}) "
                f"-- STOP before headline accuracy; fix data before interpreting a win", extra)
    # KEEP_EPISODIC across seeds is the HONEST generalize-not-memorize guardrail firing -- route it
    # to MEMORIZES-KEEP-EPISODIC BEFORE the None/noise-floor branch (composed_held is None precisely
    # because the learner refused to induce a generalizing rule).
    if keep_episodic:
        sat = (" [TASK ALSO FREQ-SATURATED: MFV=" + str(mfv) + " >= " + str(FROZEN_SAT) +
               " so the base-rate null is near-perfect and no rule can compress past it -- the real "
               "slice poses no genuine fine-discrimination problem; a fair test needs de-skewed pools "
               "/ frequency-matched hard distractors]") if freq_saturated else ""
        return ("MEMORIZES-KEEP-EPISODIC",
                f"learner returned KEEP_EPISODIC on all seeds ({chosen_plugins}) -- no relation-level rule "
                f"compresses past the null; only per-concept identity predicts -> MEMORIZES not GENERALIZES "
                f"(honest guardrail). Bars: composed=None, MFV={mfv}, GloVe-zerofit={glv_zf}, "
                f"GloVe-learned={glv_ln}, chance={chance}, BGE-bar={BGE_LEARNED_BAR}.{sat}", extra)
    if comp is None or n_ho_fine < MIN_HELDOUT_ITEMS:
        return ("INVALID", f"composed=None or only {n_ho_fine} held-out fine items (< {MIN_HELDOUT_ITEMS}) "
                f"-- noise-floor breach / no composed prediction", extra)
    if glv_zf is not None and glv_zf >= FROZEN_SAT:
        return ("INVALID", f"frozen GloVe held-out={glv_zf} >= {FROZEN_SAT}: task too easy -- harden", extra)

    shuffle_collapsed = (shuf is not None and mfv is not None and shuf <= mfv + SHUFFLE_COLLAPSE_EPS)
    beats_bar = (comp_ci[0] > bar)
    beats_mfv = (comp is not None and mfv is not None and (comp - mfv) >= MARGIN_OVER_MFV)
    beats_glv_learned = (glv_ln is None or (comp is not None and comp > glv_ln))
    real_rule = (not keep_episodic and compression is not None and compression > 1.0)

    if real_rule and beats_bar and beats_mfv and shuffle_collapsed and beats_glv_learned:
        return ("EARNS-GENERALIZING-MEANING",
                f"composed held-out={comp} (CI {comp_ci}) CI-lower>{round(bar,4)}=max(MFV {mfv}, BGE {BGE_LEARNED_BAR}); "
                f"beats MFV by {round(comp-mfv,4)}>={MARGIN_OVER_MFV}; compression={compression}>1 "
                f"(plugin {chosen_plugins}); shuffle collapses to {shuf}<=MFV+eps; beats GloVe-learned {glv_ln} "
                f"-- our parts EARN generalizing fine meaning over real relations", extra)
    if keep_episodic or (compression is not None and compression <= 1.0):
        return ("MEMORIZES-KEEP-EPISODIC",
                f"learner returned {'KEEP_EPISODIC' if keep_episodic else 'compression<=1'} "
                f"(compression={compression}) -- no relation-level rule compresses past the null; the only "
                f"thing that predicts is per-concept identity -> MEMORIZES not GENERALIZES (honest guardrail)", extra)
    if comp is not None and comp <= bar:
        return ("MEMORIZES-KEEP-EPISODIC",
                f"composed held-out={comp} <= bar {round(bar,4)}=max(MFV {mfv}, BGE {BGE_LEARNED_BAR}) -- does not "
                f"beat the frequency prior / BGE-learned bar; not generalizing fine meaning", extra)
    if not shuffle_collapsed:
        return ("MEMORIZES-KEEP-EPISODIC",
                f"SHUFFLED-RELATION control did NOT collapse (shuffle held-out={shuf} vs MFV {mfv}) -- the "
                f"'learning' survives target scramble => marginal/spurious shortcut, not relational structure => void", extra)
    return ("MIDDLE",
            f"composed held-out={comp} (CI {comp_ci}); beats MFV={beats_mfv} bar={beats_bar} "
            f"compression={compression} shuffle_collapsed={shuffle_collapsed} -- real+modest, not to the clear bar", extra)


# ---------------------------------------------------------------------------
# self-test: planted separable env (learner generalizes when a rule exists; KEEP_EPISODIC when only
# identity predicts) + real code path (parse + ConceptEncoder + learner.learn at tiny scale)
# ---------------------------------------------------------------------------
def _planted_items(n_concepts, per_concept_rels, rule_signal, carrier="kindof"):
    """Plant: each concept has a category feature and a target relation HABITAT whose gold value is
    DETERMINED by the category when rule_signal=True (cat0->land, cat1->water, cat2->air). A
    relation-level rule generalizes to held-out. When rule_signal=False the HABITAT gold is a
    per-concept random value (only identity predicts) -> learner should KEEP_EPISODIC / not generalize.
    carrier='kindof' -> category is the KINDOF feature (relation mode); carrier='ce' -> category is
    ONLY the CE prototype token it['ce_proto'] (ce mode; guards the V2 CE->learner bridge). gold is
    placed at a RANDOMIZED position (V2 FIX A) so abstain scores chance not auto-correct."""
    cats = ["cat0", "cat1", "cat2"]
    cat_hab = {"cat0": "land", "cat1": "water", "cat2": "air"}
    hab_pool = ["land", "water", "air", "cave", "tree", "burrow"]
    rng = np.random.default_rng(7)
    items = []
    for i in range(n_concepts):
        cat = cats[i % 3]
        c = f"c{i}"
        hab = cat_hab[cat] if rule_signal else hab_pool[int(rng.integers(0, len(hab_pool)))]
        distract = [h for h in hab_pool if h != hab][:K_DISTRACT]
        gpos = int(rng.integers(0, len(distract) + 1))
        cand = distract[:gpos] + [hab] + distract[gpos:]
        it = {"concept": c, "relation": "HABITAT", "gold": hab, "gold_class": hab,
              "cand_vals": cand, "gold_pos": gpos, "n_other_rel": 1, "held": (i % 5 == 0),
              "tier": "fine"}
        if carrier == "kindof":
            it["feats"] = ["ASK=HABITAT", f"KINDOF={cat}"]
        else:  # ce carrier: NO KINDOF; category lives ONLY in the CE prototype token
            it["feats"] = ["ASK=HABITAT"]
            it["ce_proto"] = f"CEPROTO_{cat}"
        items.append(it)
    return items


def self_test():
    # --- SCORER FAIRNESS (V2 FIX A): an always-abstain predictor must score ~chance, not ~1.0 ---
    print("[self-test] scorer fairness: always-abstain must score ~chance (V2 FIX A) ...", flush=True)
    fair_items = _planted_items(120, 1, rule_signal=True)
    abstain_correct = np.mean([1.0 if score_candidates_by_predicted(it["cand_vals"], None, None) == it["gold_pos"]
                               else 0.0 for it in fair_items])
    mean_chance = float(np.mean([1.0 / len(it["cand_vals"]) for it in fair_items]))
    print(f"[self-test]   abstain acc={abstain_correct:.3f} chance={mean_chance:.3f} (v1 bug -> ~1.0)", flush=True)
    assert abstain_correct <= mean_chance + 0.12, \
        f"SCORER BUG: abstain acc={abstain_correct} >> chance={mean_chance} (gold not randomized?)"

    print("[self-test] planted RULE env: learner must GENERALIZE to held-out via KINDOF->HABITAT rule ...", flush=True)
    items = _planted_items(60, 1, rule_signal=True)
    tr = [it for it in items if not it["held"]]
    ho = [it for it in items if it["held"]]
    mfv = build_mfv(tr)
    ch, chosen, results, ff, ek = run_learner(tr, "relation", include_gam=True, include_progind=False)
    acc, _, _ = learner_acc(ch, chosen, ff, ho, mfv, ek)
    print(f"[self-test]   planted-rule: chosen={ch} compression={chosen.compression_ratio if chosen else None} "
          f"held-out acc={acc}", flush=True)
    assert ch != KEEP_EPISODIC, "planted-rule: learner failed to induce a generalizing hypothesis"
    assert acc is not None and acc >= 0.9, f"planted-rule: did not generalize to held-out (acc={acc})"

    # --- CE BRIDGE (V2 FIX B): a rule carried ONLY by the low-card CEPROTO token must generalize ---
    print("[self-test] planted CE-PROTOTYPE env: rule via CEPROTO token only must GENERALIZE (V2 FIX B) ...", flush=True)
    ce_items = _planted_items(60, 1, rule_signal=True, carrier="ce")
    ce_tr = [it for it in ce_items if not it["held"]]
    ce_ho = [it for it in ce_items if it["held"]]
    ce_feats_map = {it["concept"]: [it["ce_proto"]] for it in ce_items}
    mfv_ce = build_mfv(ce_tr)
    ch_ce, chosen_ce, _, ff_ce, ek_ce = run_learner(ce_tr, "ce", include_gam=True, include_progind=False,
                                                    ce_feats_by_concept=ce_feats_map)
    acc_ce, _, _ = learner_acc(ch_ce, chosen_ce, ff_ce, ce_ho, mfv_ce, ek_ce, ce_feats_map)
    print(f"[self-test]   planted-ce: chosen={ch_ce} compression={chosen_ce.compression_ratio if chosen_ce else None} "
          f"held-out acc={acc_ce}", flush=True)
    assert ch_ce != KEEP_EPISODIC, "CE-bridge: low-card CEPROTO token did not induce a generalizing rule (bridge broken)"
    assert acc_ce is not None and acc_ce >= 0.9, f"CE-bridge: did not generalize via CEPROTO (acc={acc_ce})"

    print("[self-test] planted NO-RULE env: only per-concept identity predicts -> must NOT generalize ...", flush=True)
    items2 = _planted_items(60, 1, rule_signal=False)
    tr2 = [it for it in items2 if not it["held"]]
    ho2 = [it for it in items2 if it["held"]]
    mfv2 = build_mfv(tr2)
    ch2, chosen2, _, ff2, ek2 = run_learner(tr2, "relation", include_gam=True, include_progind=False)
    acc2, _, _ = learner_acc(ch2, chosen2, ff2, ho2, mfv2, ek2)
    print(f"[self-test]   planted-norule: chosen={ch2} held-out acc={acc2} (should be ~chance/MFV)", flush=True)
    mfv2_acc, _ = mfv_acc(ho2, mfv2)
    assert (acc2 is None) or (acc2 <= mfv2_acc + 0.20), \
        f"planted-norule: generalized without a rule (acc={acc2} vs mfv={mfv2_acc}) -- spurious"

    print("[self-test] REAL code path: parse tables + ConceptEncoder + build_environment + learner.learn ...", flush=True)
    output_dir = _out_dir("_smoke")
    triples, precision = parse_tables((("KINDOF", 1, 4), ("HABITAT", 3, 5), ("MADEOF", 2, 6),
                                       ("PROP-MAGNETISM", 0, 3), ("PROP-CONDUCTIVITY", 0, 3)))
    assert len(triples) > 300, f"real: too few triples ({len(triples)})"
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=512, seed=13, use_wordnet=True, kv=kv)
    env = build_environment(enc, triples, seed=13, output_dir=output_dir, kindof_cap=120)
    assert len(env["items"]) >= 30, f"real: too few items ({len(env['items'])})"
    tr3 = [it for it in env["items"] if not it["held"]]
    ce_enc, tc, ce_tr3, proto_tr3 = build_ce(tr3, env, seed=13)
    assert ce_enc is not None, "real: ConceptEncoder did not train"
    # V2 bridge must produce a LOW-cardinality feature: <= CE_N_PROTOTYPES distinct CEPROTO tokens
    distinct_ce = {tok for toks in ce_tr3.values() for tok in toks}
    assert len(distinct_ce) <= CE_N_PROTOTYPES, f"CE-bridge cardinality breach: {len(distinct_ce)} > {CE_N_PROTOTYPES}"
    assert all(t.startswith("CEPROTO") for t in distinct_ce), "CE-bridge: tokens must be CEPROTO prototypes"
    for it in tr3:  # annotate ce_proto for composed est_key
        p = proto_tr3.get(it["concept"])
        it["ce_proto"] = (f"CEPROTO{p}" if p is not None else None)
    ch3, chosen3, res3, ff3, ek3 = run_learner(tr3, "relation_ce", include_gam=True, include_progind=False, ce_feats_by_concept=ce_tr3)
    # determinism of learner selection
    ch3b, _, _, _, _ = run_learner(tr3, "relation_ce", include_gam=True, include_progind=False, ce_feats_by_concept=ce_tr3)
    assert ch3 == ch3b, "real: learner selection non-deterministic"
    print(f"[self-test]   real: n_items={len(env['items'])} chosen={ch3} n_ce_proto={len(distinct_ce)} "
          f"precision={precision} multi_valid={env['multi_valid_rate']} density={env['density']}", flush=True)
    print("[self-test] PASS (scorer fair; planted rule + CE-bridge generalize; no-rule does not; real parse+CE-proto+learner; determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def run(mode, output_dir):
    include_gam = INCLUDE_GAM
    seeds = SEEDS_SMOKE if mode == "smoke" else SEEDS_FULL
    kindof_cap = 200 if mode == "smoke" else 700
    # smoke runs the FULL audited table-set at 1 seed + smaller KINDOF cap (discriminator-survives-
    # scale preview: same table regime as full, minus the seed axis); full = 3 seeds, full cap.
    tables = CURATED_TABLES

    _heartbeat(output_dir, "parse_tables")
    triples, precision = parse_tables(tables)
    _heartbeat(output_dir, "load_glove", {"n_triples": len(triples)})
    kv = _load_glove()
    _load_wordnet()

    splits = []
    for seed in seeds:
        enc_frozen = SemanticHDEncoder(n_dim=512, seed=seed, use_wordnet=True, kv=kv)
        s = run_split(enc_frozen, triples, precision, seed, output_dir, include_gam, kindof_cap)
        splits.append(s)
        _heartbeat(output_dir, "split_done", {"seed": seed, "composed_held": s["composed_held"],
                   "mfv_held": s["mfv_held"], "chosen": s["composed_chosen_plugin"]})

    env_meta = splits[0]["_env_meta"]
    preflight = preflight_verdict(precision, env_meta)
    verdict, vmsg, extra = decide(splits, preflight)

    # discriminator-fires check (smoke): composed must exceed MFV
    comp = extra["composed_held"]
    mfv = extra["mfv_held"]
    discriminator_fires = (comp is not None and mfv is not None and comp > mfv)

    # arms differ
    arms = [extra["composed_held"], extra["glove_zerofit_held"], extra["glove_learned_held"],
            extra["shuffle_control_held"]]
    arms = [a for a in arms if a is not None]
    arms_differ = len(set(arms)) > 1

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg, "summary": f"{verdict}: {vmsg}",
        "run_mode": mode, "elapsed_s": round(time.perf_counter() - _T0[0], 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME, "seeds": list(seeds),
        "one_variable": "concept->value predictor (borrowed-vector baselines vs OUR composed encoder+MDL-learner); identical items/candidates/split",
        "primary_metric": "held-out-to-NEW-concepts fine-value discrimination accuracy (aggregate over ALL held-out, Wilson CI)",
        # headline aggregates
        "composed_held_out_acc": extra["composed_held"], "composed_held_out_ci": extra["composed_ci"],
        "composed_chosen_plugins_per_seed": extra["chosen_plugins"],
        "composed_compression_ratio": extra["compression_ratio"],
        "composed_invocab_acc": _agg(splits, "composed_invocab"),
        "composed_scorable_heldout_per_seed": [s["composed_scorable_held"] for s in splits],
        # bars (G3 apples-to-apples, same items/split/neutral distractors)
        "chance": extra["chance"], "mfv_held_out_acc": extra["mfv_held"],
        "glove_zerofit_held_out_acc": extra["glove_zerofit_held"],
        "glove_learned_held_out_acc": extra["glove_learned_held"],
        "bge_learned_bar_CITED": BGE_LEARNED_BAR,
        "bge_learned_note": "CITED@data/exp_bge_finemeaning_wall_probe_v1/metrics.json (learned_bge_fine_heldout=0.2278); inline BGE-model recompute out of scope (heavy) -- flagged, not on same distractor set",
        "bar_to_beat": extra["bar_to_beat"],
        # controls (G2)
        "shuffle_control_held_out_acc": extra["shuffle_control_held"],
        "glove_learned_shuffle_held_out_acc": _agg(splits, "glove_learned_shuffle_held"),
        "shuffle_collapsed": bool(extra["shuffle_control_held"] is not None and extra["mfv_held"] is not None
                                  and extra["shuffle_control_held"] <= extra["mfv_held"] + SHUFFLE_COLLAPSE_EPS),
        # ablations (G5)
        "ablation_relation_only_held_out_acc": _agg(splits, "abl_relation_only_held"),
        "ablation_ce_only_held_out_acc": _agg(splits, "abl_ce_only_held"),
        "ablation_ce_no_learner_held_out_acc": _agg(splits, "ce_no_learner_held"),
        "ablation_note": "composed(relation+CE) vs relation-only vs CE-only vs CE-no-learner vs GloVe-learned attributes signal to learner / encoder / relations",
        # coverage honesty (G6)
        "coverage": {"n_heldout_items_total": sum(s["n_held"] for s in splits),
                     "n_heldout_fine_total": extra["n_heldout_fine_total"],
                     "n_scorable_heldout_per_seed": [s["n_scorable_held"] for s in splits],
                     "note": "accuracy aggregated over ALL held-out (unscorable counted, not dropped)"},
        # per-plugin compression transparency
        "all_plugin_compression_per_seed": [s["all_plugin_compression"] for s in splits],
        # data-integrity preflight (garbage-in guard)
        "data_integrity_preflight": preflight,
        # brain-fidelity map + flagged gaps
        "brain_fidelity_map": {
            "concept_encoder": "cortical competitive-Hebbian/WTA sparse coding (Foldiak/Kohonen); SHAPE ok",
            "concept_encoder_GAP": "batch accumulator = ORDER-INVARIANT -> cannot express Rogers-McClelland curriculum LEARNING DYNAMICS; label-conditioned aggregation = binding not error-driven prediction (flagged, not fixed in scope)",
            "typed_relation_features": "Rogers-McClelland PDP relational differentiation; coarse->fine reported as STATIC signature (coarse KINDOF vs fine held-out), not a dynamic",
            "learner_MDL_gate": "Complementary Learning Systems (rule=neocortical semantic; KEEP_EPISODIC=hippocampal episodic); MDL two-part code = computational-level formalization -- right shape",
            "working_memory_cowan4": f"MAX_COACTIVE_REL={MAX_COACTIVE_REL} co-active relations/concept (Cowan ~4; matches WorldTree ~2.5-central-fact) -- right shape+metric",
            "supervision_error_driven": "learner is MDL/description-length error-driven (right); concept_encoder is label-conditioned (GAP, flagged)",
            "curriculum_order_status": "batch learners are order-invariant -> curriculum coarse->fine DYNAMIC not expressible here; KNOWN GAP; static coarse-vs-fine reported instead",
        },
        "coarse_vs_fine_held_out": {"note": "static coarse->fine signature (curriculum dynamic not expressible with batch learners -- flagged gap)"},
        # gate outcomes
        "gate_outcomes": {
            "G1_beats_mfv": bool(comp is not None and mfv is not None and (comp - mfv) >= MARGIN_OVER_MFV),
            "G2_shuffle_collapses": bool(extra["shuffle_control_held"] is not None and mfv is not None
                                         and extra["shuffle_control_held"] <= mfv + SHUFFLE_COLLAPSE_EPS),
            "G3_apples_to_apples": "GloVe zero-fit + GloVe-learned recomputed on SAME items/split/neutral distractors; BGE=CITED (recompute flagged out-of-scope)",
            "G4_no_leak_non_circular": "held-out concepts never in training; target relation EXCLUDED from features (asserted in build_environment feats)",
            "G5_ablations_present": True,
            "G6_coverage_reported": True,
            "compression_vs_episodic": extra["compression_ratio"],
            "keep_episodic": all(p == KEEP_EPISODIC for p in extra["chosen_plugins"]),
        },
        "discriminator_fires": bool(discriminator_fires),
        "arms_differ_verified": bool(arms_differ),
        "bands": {"MARGIN_OVER_MFV": MARGIN_OVER_MFV, "BGE_LEARNED_BAR": BGE_LEARNED_BAR,
                  "SHUFFLE_COLLAPSE_EPS": SHUFFLE_COLLAPSE_EPS, "MIN_HELDOUT_ITEMS": MIN_HELDOUT_ITEMS,
                  "FROZEN_SAT": FROZEN_SAT, "MIN_REL_PRECISION_PROXY": MIN_REL_PRECISION_PROXY},
        "config": {"K_DISTRACT": K_DISTRACT, "HELDOUT_FRAC": HELDOUT_FRAC, "MAX_COACTIVE_REL": MAX_COACTIVE_REL,
                   "CE_N_DIM": CE_N_DIM, "CE_K_SPARSITY": CE_K_SPARSITY, "INCLUDE_GAM": include_gam,
                   "INCLUDE_PROGIND": INCLUDE_PROGIND, "CE_N_PROTOTYPES": CE_N_PROTOTYPES,
                   "CE_KMEANS_ITERS": CE_KMEANS_ITERS, "FREQ_MATCH_BINS": FREQ_MATCH_BINS,
                   "n_tables": len(RELATIONS), "n_ce_prototypes_per_seed": [s.get("n_ce_prototypes") for s in splits],
                   "proginduction_excluded_reason":
                   "no biological analog + boolean-DSL (<=2 outputs) structurally unsuited to hundreds-of-values multiclass target"},
        "v2_fixes": {
            "A_scorer": "gold placed at RANDOMIZED position per item (was always index 0 in v1); abstain/fixed-index -> chance not auto-correct; all scorers score pick==gold_pos. Honest MFV/base-rate.",
            "B_ce_bridge": "native ConceptEncoder codes QUANTIZED into CE_N_PROTOTYPES cluster prototypes (spherical k-means); ONE low-card CEPROTO<k> token/concept (was ~20 raw high-card CE<dim>); estimation category-key uses symbolic KINDOF else earned CEPROTO.",
            "C_freq_matched_distractors": "distractors drawn from the gold value's SAME marginal-frequency quantile bin (FREQ_MATCH_BINS) excluding concept valid+alias values; MFV cannot preferentially pick gold.",
            "denser_source": f"widened from 8 to {len(RELATIONS)} audited WorldTree tables (multi-valued PROP-* + structural feature relations); frac_ge2 reported.",
        },
        "borrowed_embedding_never_the_encoder": "GloVe + BGE are BASELINES only; the encoder under test is native hdlab/concept_encoder.py (WTA); no borrowed vector enters the CE code or the CEPROTO prototype.",
        "per_seed": [{k: v for k, v in s.items() if not k.startswith("_")} for s in splits],
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": "fixed_int_seeds_numpy_default_rng_sorted_no_builtin_hash",
        "storage": "no_composition_selfcontained_differentiation",
        "contract": "INLINE-LOCAL foreground-to-completion; no borrowed vectors in composed build; no push/remote-persist; VET-PENDING",
    }
    _write_metrics_atomic(output_dir, metrics)
    print(f"[verdict] {verdict}: {vmsg}", flush=True)
    print(f"[headline] composed_held={extra['composed_held']} ci={extra['composed_ci']} "
          f"mfv={extra['mfv_held']} glove_zf={extra['glove_zerofit_held']} glove_ln={extra['glove_learned_held']} "
          f"chance={extra['chance']} bge_bar={BGE_LEARNED_BAR}", flush=True)
    print(f"[gates] compression={extra['compression_ratio']} plugins={extra['chosen_plugins']} "
          f"shuffle_held={extra['shuffle_control_held']} preflight_passed={preflight['passed']}", flush=True)
    print(f"[ablation] rel_only={metrics['ablation_relation_only_held_out_acc']} "
          f"ce_only={metrics['ablation_ce_only_held_out_acc']} ce_no_learner={metrics['ablation_ce_no_learner_held_out_acc']}", flush=True)
    return metrics


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    _T0[0] = time.perf_counter()

    if args.self_test:
        output_dir = _out_dir("_smoke")
        _write_start_marker(output_dir, "self_test")
        ok = self_test()
        sys.exit(0 if ok else 1)

    mode = "smoke" if args.smoke else "full"
    output_dir = _out_dir("_smoke") if mode == "smoke" else _out_dir()
    _write_start_marker(output_dir, mode)
    run(mode, output_dir)
    sys.exit(0)


if __name__ == "__main__":
    _od = _out_dir("_smoke") if ("--smoke" in sys.argv or "--self-test" in sys.argv) else _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_od, e)
        raise
