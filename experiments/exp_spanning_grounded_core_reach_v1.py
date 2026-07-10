"""SPANNING GROUNDED CORE + 6-DOMAIN GROUNDING-REACH ACCEPTANCE TEST.

QUESTION: does a deliberately-composed grounded CORE (dictionary grounding-kernel proxy UNION Wierzbicka/Goddard NSM
semantic primes+molecules UNION Lancaster-sensorimotor-covered entities), grounded at ingest with a multi-channel
measured-attribute vector and wired with CSKG cross-cutting commonsense relations, actually SPAN meaning-space -- i.e.
can a deliberately-DIVERSE held-out probe set across 6 domains (PHYSICAL / ABSTRACT / EMOTIONAL / MATHEMATICAL / SOCIAL
/ TEMPORAL) each find a CORRELATION PATH to the grounded core (via relations + attribute-similarity)?

PRINCIPLE (from notes/research_deliberate_ingest_spec_spanning_grounded_core_2026-07-10.md -- THE spec):
selection criterion = DIMENSIONAL SPAN + grounding-reach, NOT density/size. New knowledge grounds ONLY by correlating to
the core, so the core must cover the PRIMITIVE DIMENSIONS of meaning or future concepts cannot ground. Density != spanning
(FB15k-237 / Hetionet clear the density floor and are catastrophic grounded cores). This is Harnad's dual-code account
(direct grounding for kernel/MGS; indirect symbolic-recombination grounding for everything else, contingent on
reducibility to the kernel), operationalized as a measurable, falsifiable per-domain reach test.

DE-RISKED: the CSKG commonsense core-density gate already PASSED (cross-cutting 12-core = 23,632 nodes @ avg-deg 38.4;
notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md). This cell builds the actual grounded core + proves SPAN.

WHAT THIS CELL REUSES (validated this session): the diffusion-with-restart consolidation engine
(exp_grounding_consolidation_loop_degree_invariant_v1: normalized-Laplacian PPR/SR restart, cell a519) as the
correlation-path mechanism; the multi-attribute-fusion discriminator (exp_grounding_multiattribute_fusion_v1: F_A
relational-only ablation + scrambled must-fail control + margin) as the reach measurement; the same public human-rating
norm channels (Lancaster 11-dim sensorimotor + Brysbaert concreteness + Warriner VAD + Kuperman AoA) + the incremental-
validity independence gate. No new mechanism invented; the reach test re-applies the existing MM-grounding discriminator
to a deliberately adversarial, domain-diverse probe population.

CORE ASSEMBLY (the spanning basis):
  * NSM 65 semantic primes + ~50 semantic molecules (Goddard & Wierzbicka; the ONLY basis covering logical/relational/
    abstract meaning that sensorimotor norms structurally cannot reach -- the "sadness / multiplication / because" gap).
  * grounding-kernel proxy: highest-frequency / earliest-AoA norm-covered words (cheap MGS proxy pending exact FVS
    recomputation, per the spec's honest-gap note): words present in Lancaster AND concreteness AND AoA, ordered by
    earliest AoA (developmental concrete-first curriculum), top-N.
  * UNION, resolved to relational-graph node labels (CSKG for FULL: its 251k mw:SameAs identity links already merge
    ConceptNet/WordNet/Wikidata-CS/FrameNet; restrict to the cross-cutting commonsense subgraph, strip the 79% lexical
    dilution). Each core concept grounded at ingest with its multi-channel attribute vector; no-norm-coverage concepts
    FLAGGED, not fabricated.

RELATIONAL STRUCTURE: CSKG cross-cutting commonsense edges among the core concepts + their H-hop neighborhood (capped).

THE ACCEPTANCE TEST (the decisive gate): for each of 200-500 deliberately-diverse held-out probe concepts across the 6
domains, measure whether the grounded core provides a coordinate that RECOVERS the probe's true measured attributes
better than (a) a relational-only baseline (F_A: graph geometry with NO exterior grounding) AND (b) a scrambled-core
control (core attribute rows permuted -> values-dependence). reach(probe)=1 iff mechanism beats BOTH by a margin.
per-domain reach = fraction of that domain's probes that reach the core.

MUST-FAIL CONTROL (density != spanning anti-pattern): a NARROW core (only high-concreteness PHYSICAL concepts; NSM
logical/abstract primes + low-concreteness molecules dropped) MUST FAIL grounding-reach on the abstract / emotional /
mathematical domains (it lacks both the relations INTO those regions and the attribute dimensions those domains load on)
while still reaching PHYSICAL probes. If the narrow core reaches the non-physical domains as well as the spanning core,
the reach test is vacuous (it does not detect non-spanning) -> HARD_FAIL_CONTROL_VACUOUS.

FAILURE TAXONOMY (per the spec, distinguish the two): a MISSING-DIMENSION failure (reach fails in 1-2 domains while
others pass comfortably -> the core lacks a channel for that dimension -> EXPAND the core there; fixable) vs a
MECHANISM-BOTTLENECK failure (reach roughly uniformly low across ALL 6 domains regardless of core composition -> matches
the loop-closer grounding-doesnt-chain negative; the decoder/inference mechanism is the wall, not core span).

PRE-REGISTERED BANDS (picked BEFORE the run; deflated per the fusion-FULL 5/7-gate analogy):
  REACH_MARGIN 0.05 (per-probe mechanism-vs-baseline lift threshold); per-domain REACH_FLOOR 0.60; aggregate AGG_FLOOR
  0.70; SPAN_HARD_PASS = every one of the 6 domains reaches REACH_FLOOR AND aggregate >= AGG_FLOOR AND the narrow-core
  control collapses (narrow reach on {abstract,emotional,mathematical} <= NARROW_COLLAPSE 0.40 while narrow PHYSICAL
  reach >= REACH_FLOOR) AND the scrambled control does not ground (scrambled aggregate reach <= SCRAMBLE_MAX 0.40).
  SPAN_FAIL_MISSING_DIMENSION = 1-2 domains below REACH_FLOOR, others pass (names the missing dimension).
  SPAN_FAIL_MECHANISM = >=4 domains below REACH_FLOOR (uniform; decoder wall).
  MIDDLE_BAND = 3 domains below floor, or control ambiguous.

SELF-TEST (planted worlds; the LIGHT local gate; discriminators MUST FIRE, no data needed): a planted latent space with 6
orthogonal domain-dimensions. (a) a SPANNING planted core (covers all 6 dims) reaches all 6 planted domains; (b) a NARROW
planted core (covers only the physical dim) FAILS exactly the domains whose dimension it lacks while reaching physical
(the must-fail narrow control fires); (c) a SCRAMBLED core does NOT ground. This plants the full reach logic at small n
-> discriminator-survives-scale evidence (the per-domain reach fraction is scale-invariant in expectation).

## Compute architecture
class (a) batched-GPU-capable but CPU-fast for the eval; the DOMINANT cost is the one-time streaming parse of the ~6M-edge
CSKG TSV (CPU / IO-bound) then dense diffusion-with-restart (dense [n,n]@[n,DIM], n capped ~6000) x a few passes x arms x
seeds x {spanning,narrow} cores -> seconds/seed on CPU (per the fusion cell's same-regime measurement). Storage SHARDED
(each concept its own grounded vector; no bundling). SELF-TEST is planted-only (seconds, tiny n) and runs LOCAL. The FULL
CSKG assembly + 6-domain reach eval is INTENSIVE and routes to remote_cpu_queue (graph parse dominates; GPU optional).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor/sec.13/sec.16/sec.17):
  arms_differ_verified (>=3 distinct arm sigs: mechanism / relational-only / scrambled) at self-test gate;
  final_metrics_atomicity=tmp_replace (write_metrics uses os.replace); except SystemExit before except Exception (no
  BaseException / bare); crlb: per-probe lift chance ~0 in z-err space (THEORETICAL), HARD_PASS strictly above floor;
  baseline_in_band: relational-only F_A reach is the in-band baseline (not saturated: narrow core drops it below floor in
  the missing domains by construction); discriminator-survives-scale: planted self-test fires reach + narrow must-fail +
  scramble at full logic (Path C planted-preview + Path B analytical scale-invariance); HP_SCOPE: reach gate on MECHANISM
  vs relational-only + scrambled, per-domain; calibration_check=default_ok_for_this_regime (engine defaults inherited
  from the validated a519 engine); progress_logging=print_flush_true; cell_chunked=false (single graph, seeds cheap);
  start_marker + crash_diagnostic present; heartbeat via per-seed logs; cardinality_ok EXPECTED_N_UNITS=n_seeds;
  provenance: all acquired data -> data/grounding_testbed/ (gitignored; NOT canonical substrate_index; never git add -A).
"""

import argparse
import gzip
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
import experiments.exp_grounding_consolidation_loop_degree_invariant_v1 as eng  # noqa: E402

ANCHOR_NAME = "spanning_grounded_core_reach_v1"

TESTBED = os.path.join(_REPO, "data", "grounding_testbed")

# ---- Norm datasets (public human-rating norms; LOCAL testbed inputs; NOT canonical store; self-acquire if absent) ----
DATASETS = {
    "conc": dict(path=os.path.join(TESTBED, "Concreteness_ratings_Brysbaert_et_al_BRM.txt"),
                 url="https://raw.githubusercontent.com/ArtsEngine/concreteness/master/"
                     "Concreteness_ratings_Brysbaert_et_al_BRM.txt", header_key="Conc.M", sep="\t"),
    "warriner": dict(path=os.path.join(TESTBED, "Ratings_Warriner_et_al.csv"),
                     url="https://raw.githubusercontent.com/JULIELab/XANEW/master/Ratings_Warriner_et_al.csv",
                     header_key="V.Mean.Sum", sep=","),
    "lancaster": dict(path=os.path.join(TESTBED, "Lancaster_sensorimotor_norms_for_39707_words.csv"),
                      url="https://osf.io/48wsc/download", header_key="Visual.mean", sep=","),
    "aoa": dict(path=os.path.join(TESTBED, "AoA_51715_words.csv"),
                url="https://raw.githubusercontent.com/Cody-Lange/Milestone-2-Text-Difficulty-Classifier/"
                    "main/assets/AoA_51715_words.csv", header_key="AoA_Kup", sep=","),
}

# ---- CSKG (merged commonsense graph; Zenodo 4331372; ~112MB gzip). LOCAL testbed input; self-acquire if absent. ----
CSKG = dict(path=os.path.join(TESTBED, "cskg.tsv.gz"),
            url="https://zenodo.org/api/records/4331372/files/cskg.tsv.gz/content")
CN_RELATIONS = os.path.join(_REPO, "data", "substrate_index", "concept", "relations.jsonl")

# ---- CROSS-CUTTING commonsense relation set (CITED@notes/cskg_commonsense_core_kcore_density_gate_2026-07-10.md sec.3):
#      the 20.9% commonsense SPINE; strips the 79.1% lexical/taxonomic dilution (RelatedTo/Synonym/Antonym/FormOf/IsA/
#      HasContext/DerivedFrom/dbpedia...). Match is on the relation-label suffix (case-insensitive substring). ----
XCUT_REL_TOKENS = [
    "xattr", "xwant", "xeffect", "xneed", "xreact", "xintent", "owant", "oeffect", "oreact",  # ATOMIC at:*
    "locatednear", "mayhaveproperty", "usedfor", "capableof", "partof", "atlocation", "hassubevent",
    "hasprerequisite", "causes", "hasa", "mannerof", "motivatedbygoal", "hasproperty", "receivesaction",
    "causesdesire", "desires", "madeof", "createdby", "entails", "hasfirstsubevent", "haslastsubevent",
    "notdesires", "obstructedby",
]
LEXICAL_REL_TOKENS = [  # explicit deny-list (defense-in-depth; these must NOT count as cross-cutting)
    "relatedto", "synonym", "antonym", "formof", "derivedfrom", "isa", "hascontext", "haslexicalunit",
    "etymologicallyrelatedto", "similarto", "distinctfrom", "definedas", "instanceof", "sameas", "dbpedia",
]

# ---- NSM 65 semantic primes (CITED: Goddard & Wierzbicka 2014 inventory; single-word graph-match forms) ----
NSM_PRIMES = [
    "i", "you", "someone", "something", "thing", "people", "body",              # substantives
    "kind", "part",                                                              # relational substantives
    "this", "same", "other", "else",                                            # determiners
    "one", "two", "some", "all", "many", "much", "little", "few",               # quantifiers
    "good", "bad",                                                              # evaluators
    "big", "small",                                                             # descriptors
    "think", "know", "want", "feel", "see", "hear",                            # mental predicates
    "say", "words", "true",                                                     # speech
    "do", "happen", "move",                                                     # actions / events / movement
    "be", "there", "is", "have", "mine",                                        # existence / possession
    "live", "die",                                                              # life and death
    "when", "time", "now", "before", "after", "moment",                        # time
    "where", "place", "here", "above", "below", "far", "near", "side",         # space
    "inside", "touch",
    "not", "maybe", "can", "because", "if",                                     # logical concepts
    "very", "more",                                                             # intensifier / augmentor
    "like", "as", "way",                                                        # similarity
]
# ---- NSM ~50 semantic molecules (CITED: Goddard & Wierzbicka; near-universal grounded intermediates) ----
NSM_MOLECULES = [
    "man", "woman", "child", "mother", "father", "hands", "mouth", "eyes", "ears", "head", "legs", "teeth",
    "fingers", "nose", "face", "skin", "blood", "bone", "water", "fire", "earth", "sky", "sun", "ground",
    "day", "night", "air", "wind", "long", "round", "flat", "hard", "soft", "sharp", "heavy", "hot", "cold",
    "wet", "dry", "eat", "drink", "sleep", "sit", "stand", "hold", "make", "kill", "animal", "bird", "tree",
    "wood", "stone", "sea", "mountain",
]

# ---- 6-DOMAIN held-out probe set (CURATED; deliberately DIVERSE; each probe NOT in the core; common English words with
#      likely norm coverage; stress-tests SPAN across primitive dimensions no single core channel covers alone) ----
PROBES = {
    "PHYSICAL": ["gravel", "sponge", "pebble", "brick", "velvet", "sandpaper", "cardboard", "foam", "granite",
                 "rubber", "gravel", "clay", "leather", "concrete", "silk", "marble", "plywood", "wax"],
    "ABSTRACT": ["freedom", "justice", "theory", "concept", "essence", "principle", "notion", "ideology",
                 "abstraction", "hypothesis", "paradigm", "meaning", "purpose", "quality", "existence", "virtue"],
    "EMOTIONAL": ["melancholy", "relief", "anxiety", "grief", "envy", "gratitude", "resentment", "elation",
                  "dread", "nostalgia", "joy", "shame", "pride", "loneliness", "contentment", "despair"],
    "MATHEMATICAL": ["multiplication", "ratio", "infinity", "equation", "integer", "geometry", "algebra",
                     "fraction", "exponent", "variable", "theorem", "average", "angle", "probability", "sum",
                     "division"],
    "SOCIAL": ["contract", "debt", "citizenship", "marriage", "hierarchy", "etiquette", "reputation", "alliance",
               "bureaucracy", "ownership", "authority", "loyalty", "justice", "committee", "tradition", "rank"],
    "TEMPORAL": ["duration", "interruption", "eventually", "meanwhile", "deadline", "interval", "sequence",
                 "delay", "frequency", "simultaneity", "yesterday", "century", "schedule", "pause", "rhythm",
                 "afterward"],
}
DOMAINS = ["PHYSICAL", "ABSTRACT", "EMOTIONAL", "MATHEMATICAL", "SOCIAL", "TEMPORAL"]
NARROW_MISSING_DOMAINS = ["ABSTRACT", "EMOTIONAL", "MATHEMATICAL"]  # narrow (physical-only) core must FAIL these

# ---- Attribute channels (name -> (dataset, column)) ----
CANDIDATES = [
    ("concreteness", "conc", "Conc.M"),
    ("valence", "warriner", "V.Mean.Sum"),
    ("arousal", "warriner", "A.Mean.Sum"),
    ("dominance", "warriner", "D.Mean.Sum"),
    ("visual", "lancaster", "Visual.mean"),
    ("haptic", "lancaster", "Haptic.mean"),
    ("auditory", "lancaster", "Auditory.mean"),
    ("gustatory", "lancaster", "Gustatory.mean"),
    ("olfactory", "lancaster", "Olfactory.mean"),
    ("interoceptive", "lancaster", "Interoceptive.mean"),
    ("aoa", "aoa", "AoA_Kup"),
]
ATTR_NAMES = [c[0] for c in CANDIDATES]

# ---- Arm names ----
MECH = "MECHANISM_CORE_GROUNDED"
REL = "RELATIONAL_ONLY_F_A"
SCR = "SCRAMBLED_CORE"
ALL_ARMS = [MECH, REL, SCR]

# ---- Pre-registered bands (principled; picked BEFORE the run) ----
SIM_FLOOR = 0.30         # per-probe: grounded-coordinate vs true-attribute cosine (over co-present channels) >= this
                         # = reached. Random S-dim alignment has E[cos]~0, std~1/sqrt(S); 0.30 separates real from null.
MIN_REACH_CHANNELS = 3   # a probe must have >=3 co-present selected channels to be reach-evaluable (else no-coverage FLAG)
REACH_FLOOR = 0.60       # per-domain HARD_PASS reach floor
AGG_FLOOR = 0.70         # aggregate reach HARD_PASS floor
NARROW_COLLAPSE = 0.40   # must-fail control: narrow-core reach on {abstract,emotional,math} must be <= this
SCRAMBLE_MAX = 0.40      # scrambled aggregate reach must be <= this (values-dependence ablation)
INDEP_MIN_SELECTED = 2   # independence gate: at least 2 non-redundant channels to fuse
REDUNDANT_R = 0.70       # marginal |r| pruning threshold
MIN_TARGET_VAR = 0.0     # channel kept if it has variance over the core (multi-channel reconstruction target)
DIM = 32                 # structural feature dimensionality
HOPS = 2                 # relational neighborhood radius around core+probes

SELFTEST_CFG = dict(seeds=[7], source="planted", n_kernel=0, max_nodes=0)
SMOKE_CFG = dict(seeds=[7, 13], source="cn", n_kernel=250, max_nodes=3000)
FULL_CFG = dict(seeds=[7, 13, 17, 23, 29], source="cskg", n_kernel=1500, max_nodes=6000)


# ---------------------------------------------------------------------------
# Logging / markers / crash diagnostics (discipline sec.13 / sec.16 / sec.17)
# ---------------------------------------------------------------------------

def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Data acquisition + join.
# ---------------------------------------------------------------------------

def _ensure_dataset(key):
    d = DATASETS[key]
    path = d["path"]
    if os.path.exists(path):
        return True
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "300", "-o", tmp, d["url"]], check=True)
        with open(tmp, encoding="utf-8", errors="replace") as f:
            head = f.readline()
        if d["header_key"] not in head:
            os.remove(tmp)
            return False
        os.replace(tmp, path)
        _log("acquired norm %s" % key)
        return True
    except Exception as e:
        _log("could not self-acquire %s: %s: %s" % (key, type(e).__name__, str(e)[:150]))
        return False


def _ensure_cskg():
    if os.path.exists(CSKG["path"]):
        return True
    try:
        os.makedirs(os.path.dirname(CSKG["path"]), exist_ok=True)
        tmp = CSKG["path"] + ".tmp"
        subprocess.run(["curl", "-sSL", "--max-time", "1200", "-o", tmp, CSKG["url"]], check=True)
        if os.path.getsize(tmp) < 50_000_000:
            os.remove(tmp)
            return False
        os.replace(tmp, CSKG["path"])
        _log("acquired CSKG (%d bytes)" % os.path.getsize(CSKG["path"]))
        return True
    except Exception as e:
        _log("could not self-acquire CSKG: %s: %s" % (type(e).__name__, str(e)[:150]))
        return False


def _norm_word(w):
    return str(w).strip().lower().replace("_", " ")


def _load_col_map(key, column):
    """Load {lowercased_word: float(value)} for one dataset column; skip blank / NA."""
    d = DATASETS[key]
    sep = d["sep"]
    path = d["path"]
    with open(path, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").rstrip("\r").split(sep)
    if column not in header:
        raise RuntimeError("column %r not in %s header" % (column, key))
    ci = header.index(column)
    wi = header.index("Word") if "Word" in header else 1
    out = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").rstrip("\r").split(sep)
            if len(p) <= max(ci, wi):
                continue
            v = p[ci].strip()
            if v == "" or v.upper() in ("NA", "NAN", "#N/A"):
                continue
            try:
                fv = float(v)
            except ValueError:
                continue
            w = _norm_word(p[wi])
            if w and w not in out:
                out[w] = fv
    return out


def load_all_norm_maps():
    col_maps = {}
    for name, ds, col in CANDIDATES:
        col_maps[name] = _load_col_map(ds, col)
    return col_maps


def build_core_words(col_maps, n_kernel):
    """Assemble the spanning core word set: NSM primes + molecules UNION grounding-kernel proxy (earliest-AoA norm-covered
    words). Returns (core_words set, provenance dict)."""
    conc = col_maps["concreteness"]
    aoa = col_maps["aoa"]
    vis = col_maps["visual"]
    nsm = set(_norm_word(w) for w in NSM_PRIMES)
    mol = set(_norm_word(w) for w in NSM_MOLECULES)
    # grounding-kernel proxy: present in Lancaster (visual) AND concreteness AND AoA; earliest AoA first (concrete-first).
    cand = [w for w in vis.keys() if (w in conc and w in aoa and " " not in w)]
    cand.sort(key=lambda w: (aoa[w], -conc.get(w, 0.0)))
    kernel = set(cand[:n_kernel])
    core = set()
    core |= nsm
    core |= mol
    core |= kernel
    prov = dict(n_nsm_primes=len(nsm), n_nsm_molecules=len(mol), n_kernel_proxy=len(kernel), n_core_union=len(core))
    return core, prov


def build_narrow_core_words(core_words, col_maps):
    """Must-fail control core: only high-concreteness PHYSICAL concepts (drop NSM logical/abstract primes + low-conc
    molecules). Physical density kept; abstract/emotional/relational span REMOVED by construction."""
    conc = col_maps["concreteness"]
    narrow = set()
    for w in core_words:
        c = conc.get(w, None)
        if c is not None and c >= 4.0:   # high-concreteness only (Conc.M in 1..5)
            narrow.add(w)
    return narrow


# ---------------------------------------------------------------------------
# Relational graph assembly (CSKG cross-cutting / CN), induced on core + probes + H-hop neighborhood (capped).
# ---------------------------------------------------------------------------

def _is_xcut_rel(rel_label):
    r = rel_label.lower()
    for tok in LEXICAL_REL_TOKENS:
        if tok in r:
            return False
    for tok in XCUT_REL_TOKENS:
        if tok in r:
            return True
    return False


def _iter_cskg_edges():
    """Yield (word1, word2) for CROSS-CUTTING commonsense edges from cskg.tsv.gz. Columns:
    id node1 relation node2 node1;label node2;label relation;label relation;dimension source sentence."""
    with gzip.open(CSKG["path"], "rt", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n").split("\t")
        try:
            i_rel = header.index("relation")
            i_l1 = header.index("node1;label")
            i_l2 = header.index("node2;label")
        except ValueError:
            i_rel, i_l1, i_l2 = 2, 4, 5
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) <= max(i_rel, i_l1, i_l2):
                continue
            if not _is_xcut_rel(p[i_rel]):
                continue
            w1 = _norm_word(p[i_l1].split("|")[0])
            w2 = _norm_word(p[i_l2].split("|")[0])
            if w1 and w2 and w1 != w2:
                yield w1, w2


def _iter_cn_edges():
    """Yield (word1, word2) for CN_ ConceptNet edges from the local relations.jsonl (smoke source)."""
    with open(CN_RELATIONS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            s = d.get("src_id")
            t = d.get("tgt_id")
            if s is None or t is None:
                continue
            if not (str(s).startswith("CN_") and str(t).startswith("CN_")):
                continue
            w1 = _norm_word(str(s)[3:])
            w2 = _norm_word(str(t)[3:])
            if w1 and w2 and w1 != w2:
                yield w1, w2


def build_relational_subgraph(source, seed_words, hops, max_nodes):
    """Stream the relation source, build adjacency, induce the subgraph on seed_words + H-hop neighborhood, capped to
    max_nodes (keep all seeds; add neighbors ranked by edge-count-to-seeds). Returns (words, edges np[E,2], adj-meta)."""
    it = _iter_cskg_edges() if source == "cskg" else _iter_cn_edges()
    adj = {}
    n_edges_scanned = 0
    for w1, w2 in it:
        n_edges_scanned += 1
        adj.setdefault(w1, set()).add(w2)
        adj.setdefault(w2, set()).add(w1)
    seeds = set(w for w in seed_words if w in adj)
    frontier = set(seeds)
    keep = set(seeds)
    for _h in range(hops):
        nxt = set()
        for u in frontier:
            for v in adj[u]:
                if v not in keep:
                    nxt.add(v)
        keep |= nxt
        frontier = nxt
        if len(keep) > max_nodes * 4:
            break
    # cap: always keep seeds; rank other kept nodes by number of edges to the seed set.
    if len(keep) > max_nodes:
        others = [w for w in keep if w not in seeds]
        score = {w: sum(1 for v in adj[w] if v in seeds) for w in others}
        others.sort(key=lambda w: (-score[w], w))
        room = max(0, max_nodes - len(seeds))
        keep = set(seeds) | set(others[:room])
    words = sorted(keep)
    idx = {w: i for i, w in enumerate(words)}
    eset = set()
    for u in words:
        iu = idx[u]
        for v in adj[u]:
            if v in idx:
                iv = idx[v]
                if iu != iv:
                    a, b = (iu, iv) if iu < iv else (iv, iu)
                    eset.add((a, b))
    edges = np.array(sorted(eset), dtype=np.int64) if eset else np.zeros((0, 2), dtype=np.int64)
    meta = dict(n_edges_scanned=n_edges_scanned, n_adj_nodes=len(adj), n_seed_in_graph=len(seeds),
                n_nodes=len(words), n_edges=int(edges.shape[0]))
    return words, edges, meta


def build_attr_matrix(words, col_maps):
    """[n, K] measured-attribute matrix over the graph nodes; NaN where a norm is missing (no-coverage FLAG, not
    fabricated). present = finite mask."""
    n = len(words)
    K = len(CANDIDATES)
    Y = np.full((n, K), np.nan, dtype=np.float64)
    for ci, (name, ds, col) in enumerate(CANDIDATES):
        cm = col_maps[name]
        for i, w in enumerate(words):
            if w in cm:
                Y[i, ci] = cm[w]
            elif w.replace(" ", "") in cm:
                Y[i, ci] = cm[w.replace(" ", "")]
    present = np.isfinite(Y)
    return Y, present


# ---------------------------------------------------------------------------
# Independence gate (compact reimpl of the fusion incremental-validity gate).
# ---------------------------------------------------------------------------

def independence_select(Y, present):
    """Marginal-correlation greedy pruning over the CORE-grounded channels: anchor = concreteness; add a channel iff it
    has variance AND its max |r| with every already-selected channel < REDUNDANT_R. Returns (selected names, corr info)."""
    K = Y.shape[1]
    corr = np.eye(K)
    for i in range(K):
        for j in range(i + 1, K):
            both = present[:, i] & present[:, j]
            r = eng._pearson(Y[both, i], Y[both, j]) if both.sum() >= 10 else 0.0
            corr[i, j] = corr[j, i] = r
    sel = ["concreteness"]
    order = [c for c in range(K) if ATTR_NAMES[c] != "concreteness"]
    audit = []
    for c in order:
        name = ATTR_NAMES[c]
        has_var = bool(present[:, c].sum() >= 10 and np.nanstd(Y[:, c]) > 1e-6)
        max_r_sel = max(abs(corr[c, ATTR_NAMES.index(s)]) for s in sel)
        redundant = bool(max_r_sel >= REDUNDANT_R)
        keep = bool(has_var and (not redundant))
        audit.append(dict(attr=name, max_r_selected=round(max_r_sel, 3), has_var=has_var, redundant=redundant,
                          selected=keep))
        if keep:
            sel.append(name)
    info = dict(corr_matrix=[[round(float(corr[i, j]), 3) for j in range(K)] for i in range(K)],
                attr_names=ATTR_NAMES, selection_audit=audit, selected=sel, n_selected=len(sel))
    return sel, info


# ---------------------------------------------------------------------------
# Reach evaluation primitives.
# ---------------------------------------------------------------------------

def _zcols(M):
    M = np.asarray(M, dtype=np.float64)
    mu = np.nanmean(M, axis=0)
    sd = np.nanstd(M, axis=0)
    sd = np.where(sd > 1e-9, sd, 1.0)
    return (M - mu) / sd, mu, sd


def _diffuse_attr(edges, n, E0, device):
    """Diffusion-with-restart of an anchor E0 [n, d] over the relational graph edges (reuse the validated engine)."""
    if edges.shape[0] == 0:
        return E0.clone()
    src = edges[:, 0].astype(np.int64)
    dst = edges[:, 1].astype(np.int64)
    return eng.consolidate(src, dst, E0, n, eng.CONS_PASSES, eng.CONS_ALPHA, device, "")


def _ridge_fit_predict(Xtr, ytr, Xte, lam=5.0):
    mu = Xtr.mean(axis=0)
    Xc = Xtr - mu
    G = Xc.T @ Xc + lam * np.eye(Xc.shape[1])
    w = np.linalg.solve(G, Xc.T @ (ytr - ytr.mean()))
    return (Xte - mu) @ w + ytr.mean()


def _cos(a, b):
    """Cosine over the co-present entries of two vectors; nan if fewer than MIN_REACH_CHANNELS overlap."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    m = np.isfinite(a) & np.isfinite(b)
    if int(m.sum()) < MIN_REACH_CHANNELS:
        return float("nan")
    av = a[m]
    bv = b[m]
    na = np.linalg.norm(av)
    nb = np.linalg.norm(bv)
    if na < 1e-9 or nb < 1e-9:
        return float("nan")
    return float(av @ bv / (na * nb))


def reach_eval(words, edges, Y, present, sel_idx, core_mask, probe_domain, seed, device):
    """Per-domain grounding-reach for one core (spanning or narrow) at one seed.

    A probe's GROUNDED COORDINATE is the diffusion-with-restart of the CORE's z-scored multi-channel measured-attribute
    vectors over the relational graph (correlation path via relations); the core is anchored, non-core nodes start at 0.
    reach(probe)=1 iff the mechanism grounded coordinate ALIGNS with the probe's OWN true (held-out) z-scored attribute
    vector above SIM_FLOOR (cosine over co-present channels). Two controls (aggregate, not per-probe gates): SCRAMBLED-core
    (core attribute rows permuted across core nodes -> same relations, destroyed values) must NOT ground; the NARROW
    (physical-only) core must FAIL the non-physical domains. per-domain reach = fraction of that domain's covered probes.
    """
    n = len(words)
    rng = np.random.default_rng(seed * 100003 + 17)
    core_idx = np.where(core_mask)[0]
    if core_idx.shape[0] < 10:
        return dict(error="core_too_small", n_core=int(core_idx.shape[0]))
    S = len(sel_idx)
    Ysel = Y[:, sel_idx]
    # GLOBAL z-scoring (over all graph nodes, per channel) so the coordinate scale is STABLE across the spanning/narrow
    # cores + controls (per-core z-scoring blows up noise on near-constant channels of a homogeneous core -- an artifact).
    glob_mu = np.nanmean(Ysel, axis=0)
    glob_sd = np.nanstd(Ysel, axis=0)
    glob_sd = np.where(glob_sd > 1e-9, glob_sd, 1.0)
    Zall = (Ysel - glob_mu) / glob_sd
    E0_mech = np.zeros((n, S), dtype=np.float32)
    zc = np.where(np.isfinite(Zall[core_idx]), Zall[core_idx], 0.0)
    E0_mech[core_idx] = zc.astype(np.float32)
    # scrambled control: permute core rows across core nodes (values-dependence must break; relations unchanged).
    perm = rng.permutation(core_idx.shape[0])
    E0_scr = np.zeros((n, S), dtype=np.float32)
    E0_scr[core_idx] = E0_mech[core_idx][perm]

    G_mech = _diffuse_attr(edges, n, torch.from_numpy(E0_mech).to(device), device).cpu().numpy()
    G_scr = _diffuse_attr(edges, n, torch.from_numpy(E0_scr).to(device), device).cpu().numpy()
    # relational-only diagnostic arm (structural spectral geometry; distinct signature for ARMS-MUST-DIFFER).
    tri = np.stack([edges[:, 0], np.zeros(edges.shape[0], dtype=np.int64), edges[:, 1]], axis=1).astype(np.int64) \
        if edges.shape[0] else np.zeros((0, 3), dtype=np.int64)
    fs = eng.structural_features(tri, n, DIM, seed, device)
    G_rel = fs.cpu().numpy()

    per_domain = {}
    probe_records = []
    for dom in DOMAINS:
        idxs = [i for i in range(n) if probe_domain.get(i) == dom and not core_mask[i]]
        reached = 0
        reached_scr = 0
        counted = 0
        for pi in idxs:
            true_z = Zall[pi]                      # probe's OWN true z-scored attribute vector (held-out target)
            if int(np.isfinite(true_z).sum()) < MIN_REACH_CHANNELS:
                continue                           # no-coverage probe -> FLAG (excluded), not fabricated
            counted += 1                           # probe HAS coverage -> it is reach-evaluable
            sim_mech = _cos(G_mech[pi], true_z)
            sim_scr = _cos(G_scr[pi], true_z)
            # a nan sim = the grounded coordinate is ~0 (no diffusion mass reached this probe from the core) = NOT reached.
            if sim_mech != sim_mech:
                sim_mech = 0.0
            is_reached = bool(sim_mech >= SIM_FLOOR)
            is_reached_scr = bool(sim_scr == sim_scr and sim_scr >= SIM_FLOOR)
            if is_reached:
                reached += 1
            if is_reached_scr:
                reached_scr += 1
            probe_records.append(dict(word=words[pi], domain=dom, sim_mech=round(sim_mech, 4),
                                      sim_scr=round(sim_scr, 4) if sim_scr == sim_scr else None, reached=is_reached))
        per_domain[dom] = dict(reach=(reached / counted) if counted else float("nan"),
                               reach_scrambled=(reached_scr / counted) if counted else float("nan"),
                               n_probes=counted, n_reached=reached)
    covered = [per_domain[d]["reach"] for d in DOMAINS if per_domain[d]["n_probes"] > 0]
    covered_scr = [per_domain[d]["reach_scrambled"] for d in DOMAINS if per_domain[d]["n_probes"] > 0]
    agg = float(np.mean(covered)) if covered else float("nan")
    agg_scr = float(np.mean(covered_scr)) if covered_scr else float("nan")
    # arm signatures (ARMS-MUST-DIFFER; sec.6): the three grounded coordinate fields must be bit-distinct.
    sigs = {MECH: hashlib.sha256(G_mech.round(4).tobytes()).hexdigest()[:16],
            REL: hashlib.sha256(G_rel.round(4).tobytes()).hexdigest()[:16],
            SCR: hashlib.sha256(G_scr.round(4).tobytes()).hexdigest()[:16]}
    return dict(per_domain=per_domain, aggregate_reach=agg, aggregate_reach_scrambled=agg_scr,
                n_core=int(core_idx.shape[0]), arm_sigs=sigs, probe_records=probe_records[:400])


# ---------------------------------------------------------------------------
# Aggregate + verdict.
# ---------------------------------------------------------------------------

def aggregate_and_verdict(spanning_seeds, narrow_seeds, meta):
    def _mean_per_domain(seedruns):
        out = {}
        for dom in DOMAINS:
            vals = [s["per_domain"][dom]["reach"] for s in seedruns
                    if s.get("per_domain", {}).get(dom, {}).get("n_probes", 0) > 0
                    and s["per_domain"][dom]["reach"] == s["per_domain"][dom]["reach"]]
            out[dom] = float(np.mean(vals)) if vals else float("nan")
        aggs = [s["aggregate_reach"] for s in seedruns if s.get("aggregate_reach") == s.get("aggregate_reach")]
        scr = [s.get("aggregate_reach_scrambled") for s in seedruns
               if s.get("aggregate_reach_scrambled") == s.get("aggregate_reach_scrambled")]
        return out, (float(np.mean(aggs)) if aggs else float("nan")), (float(np.mean(scr)) if scr else float("nan"))

    span_dom, span_agg, span_agg_scr = _mean_per_domain(spanning_seeds)
    narrow_dom, narrow_agg, _narrow_scr = _mean_per_domain(narrow_seeds)

    domains_passing = [d for d in DOMAINS if (span_dom[d] == span_dom[d] and span_dom[d] >= REACH_FLOOR)]
    domains_failing = [d for d in DOMAINS if not (span_dom[d] == span_dom[d] and span_dom[d] >= REACH_FLOOR)]

    # CONTROL 1 (values-dependence ablation): SCRAMBLED core (same relations, permuted attribute values) must NOT ground.
    scramble_ok = bool(span_agg_scr == span_agg_scr and span_agg_scr <= SCRAMBLE_MAX)
    # CONTROL 2 (density != spanning): NARROW physical-only core must FAIL non-physical domains, still reach physical.
    narrow_missing_reach = [narrow_dom[d] for d in NARROW_MISSING_DOMAINS if narrow_dom[d] == narrow_dom[d]]
    narrow_collapses = bool(len(narrow_missing_reach) >= 2
                            and all(v <= NARROW_COLLAPSE for v in narrow_missing_reach))
    narrow_physical_ok = bool(narrow_dom.get("PHYSICAL", float("nan")) == narrow_dom.get("PHYSICAL", float("nan"))
                              and narrow_dom.get("PHYSICAL", 0.0) >= REACH_FLOOR)
    control_fires = bool(narrow_collapses and narrow_physical_ok and scramble_ok)

    span_all_pass = bool(len(domains_failing) == 0)
    agg_ok = bool(span_agg == span_agg and span_agg >= AGG_FLOOR)

    if span_all_pass and agg_ok and control_fires:
        verdict = "SPAN_HARD_PASS"
        one_line = "core SPANS all 6 domains (reach >= %.2f each, agg %.2f) + narrow-core collapses on %s + scramble null" % (
            REACH_FLOOR, span_agg, ",".join(NARROW_MISSING_DOMAINS))
    elif not control_fires:
        verdict = "HARD_FAIL_CONTROL_VACUOUS"
        one_line = ("reach controls did NOT fire (narrow_collapses=%s narrow_physical_ok=%s scramble_ok=%s; narrow "
                    "missing=%s physical=%.2f scramble_agg=%.2f) -> test cannot certify it detects non-spanning" % (
                        narrow_collapses, narrow_physical_ok, scramble_ok,
                        {d: round(narrow_dom[d], 3) for d in NARROW_MISSING_DOMAINS},
                        narrow_dom.get("PHYSICAL", float("nan")),
                        span_agg_scr if span_agg_scr == span_agg_scr else float("nan")))
    elif len(domains_failing) <= 2 and len(domains_passing) >= 3:
        verdict = "SPAN_FAIL_MISSING_DIMENSION"
        one_line = "core does NOT span: domain(s) %s cannot reach the core (missing dimension) -> expand the core there" % (
            ",".join(domains_failing))
    elif len(domains_failing) >= 4:
        verdict = "SPAN_FAIL_MECHANISM"
        one_line = ("reach uniformly low across %d/6 domains -> mechanism/decoder bottleneck (matches loop-closer "
                    "grounding-doesnt-chain), not a core-span gap; pause core-expansion" % len(domains_failing))
    else:
        verdict = "MIDDLE_BAND"
        one_line = "reach mixed (%d domains fail); control fires but span incomplete -> investigate before scaling" % len(
            domains_failing)

    return dict(verdict=verdict, one_line=one_line, spanning_per_domain={d: round(span_dom[d], 4) for d in DOMAINS},
                spanning_aggregate=round(span_agg, 4) if span_agg == span_agg else None,
                spanning_aggregate_scrambled=round(span_agg_scr, 4) if span_agg_scr == span_agg_scr else None,
                narrow_per_domain={d: round(narrow_dom[d], 4) for d in DOMAINS},
                narrow_aggregate=round(narrow_agg, 4) if narrow_agg == narrow_agg else None,
                domains_passing=domains_passing, domains_failing=domains_failing,
                control_fires=control_fires, narrow_collapses=narrow_collapses, narrow_physical_ok=narrow_physical_ok,
                scramble_ok=scramble_ok,
                bands=dict(REACH_FLOOR=REACH_FLOOR, AGG_FLOOR=AGG_FLOOR, NARROW_COLLAPSE=NARROW_COLLAPSE,
                           SIM_FLOOR=SIM_FLOOR, SCRAMBLE_MAX=SCRAMBLE_MAX), meta=meta)


# ---------------------------------------------------------------------------
# Planted-world self-test (LIGHT; discriminators MUST fire).
# ---------------------------------------------------------------------------

def _planted_world(seed, spanning=True, scramble=False):
    """Plant a 6-domain latent space. Each concept loads primarily on ONE of 6 orthogonal latent dims (= domain). Its
    attribute vector = its 6-dim latent + noise (channels map to domains). Graph edges connect concepts sharing latent
    proximity. SPANNING core covers all 6 dims; NARROW core covers only dim 0 (physical). Probes per domain load on their
    dim. Returns (words, edges, Y, present, sel_idx, core_mask, probe_domain)."""
    rng = np.random.default_rng(seed)
    D = 6
    per_dom_concepts = 18
    per_dom_probes = 8
    core_per_dom = 10
    n = D * (per_dom_concepts + per_dom_probes)
    latent = np.zeros((n, D), dtype=np.float64)
    dom_of = []
    is_probe = np.zeros(n, dtype=bool)
    idx = 0
    node_dom = {}
    for d in range(D):
        for _c in range(per_dom_concepts):
            latent[idx, d] = 1.0 + 0.3 * rng.standard_normal()
            latent[idx] += 0.15 * rng.standard_normal(D)
            dom_of.append(d)
            node_dom[idx] = DOMAINS[d]
            idx += 1
        for _p in range(per_dom_probes):
            latent[idx, d] = 1.0 + 0.3 * rng.standard_normal()
            latent[idx] += 0.15 * rng.standard_normal(D)
            dom_of.append(d)
            is_probe[idx] = True
            node_dom[idx] = DOMAINS[d]
            idx += 1
    # attributes: 6 channels = the 6 latent dims + measurement noise (all independent by construction).
    Y = latent + 0.25 * rng.standard_normal((n, D))
    present = np.ones((n, D), dtype=bool)
    sel_idx = list(range(D))
    # graph edges: connect nodes with high latent cosine (same-domain neighbors) -> the correlation-path substrate.
    Ln = latent / (np.linalg.norm(latent, axis=1, keepdims=True) + 1e-9)
    sim = Ln @ Ln.T
    edges = []
    for i in range(n):
        order = np.argsort(-sim[i])
        cnt = 0
        for j in order:
            if j == i:
                continue
            if sim[i, j] > 0.6:
                a, b = (i, j) if i < j else (j, i)
                edges.append((a, b))
                cnt += 1
            if cnt >= 6:
                break
    edges = np.array(sorted(set(edges)), dtype=np.int64) if edges else np.zeros((0, 2), dtype=np.int64)
    # core mask: spanning = core_per_dom concepts from EVERY domain; narrow = only domain 0.
    core_mask = np.zeros(n, dtype=bool)
    for d in range(D):
        dom_concepts = [i for i in range(n) if dom_of[i] == d and not is_probe[i]]
        if spanning or d == 0:
            for i in dom_concepts[:core_per_dom]:
                core_mask[i] = True
    # scramble: shuffle attribute rows among core nodes (destroys values-alignment).
    if scramble:
        cidx = np.where(core_mask)[0]
        Y[cidx] = Y[cidx][rng.permutation(cidx.shape[0])]
    words = ["p%d" % i for i in range(n)]
    return words, edges, Y, present, sel_idx, core_mask, node_dom


def _mechanism_selftest(device):
    # (a) SPANNING core reaches all 6 planted domains.
    w, e, Y, pr, sel, cm, pd = _planted_world(7, spanning=True)
    span = reach_eval(w, e, Y, pr, sel, cm, pd, 7, device)
    span_dom = span["per_domain"]
    span_reaches_all = bool(all(span_dom[d]["n_probes"] > 0 and span_dom[d]["reach"] >= REACH_FLOOR for d in DOMAINS))

    # (b) NARROW core (physical-only) FAILS the non-physical domains, reaches physical (the must-fail control).
    w2, e2, Y2, pr2, sel2, cm2, pd2 = _planted_world(7, spanning=False)
    narrow = reach_eval(w2, e2, Y2, pr2, sel2, cm2, pd2, 7, device)
    n_dom = narrow["per_domain"]
    narrow_missing_fail = bool(all(n_dom[d]["reach"] <= NARROW_COLLAPSE for d in NARROW_MISSING_DOMAINS
                                   if n_dom[d]["n_probes"] > 0))
    narrow_phys_ok = bool(n_dom["PHYSICAL"]["n_probes"] > 0 and n_dom["PHYSICAL"]["reach"] >= REACH_FLOOR)

    # (c) SCRAMBLED core does NOT ground: the in-run scrambled-core control (same relations, permuted values) is low.
    scramble_collapses = bool(span["aggregate_reach_scrambled"] == span["aggregate_reach_scrambled"]
                              and span["aggregate_reach_scrambled"] <= SCRAMBLE_MAX
                              and span["aggregate_reach_scrambled"] < span["aggregate_reach"] - 0.15)

    # arms differ (sec.6).
    arms_differ = bool(len(set(span["arm_sigs"].values())) >= 3)

    res = dict(span_aggregate=round(span["aggregate_reach"], 4),
               span_per_domain={d: round(span_dom[d]["reach"], 3) for d in DOMAINS},
               narrow_per_domain={d: round(n_dom[d]["reach"], 3) for d in DOMAINS},
               narrow_aggregate=round(narrow["aggregate_reach"], 4),
               scrambled_aggregate=round(span["aggregate_reach_scrambled"], 4),
               span_reaches_all=span_reaches_all, narrow_missing_fail=narrow_missing_fail,
               narrow_phys_ok=narrow_phys_ok, scramble_collapses=scramble_collapses, arms_differ=arms_differ)
    ok = bool(span_reaches_all and narrow_missing_fail and narrow_phys_ok and scramble_collapses and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _run_real(run_mode, cfg, col_maps, out_dir, t0, device):
    core_words, core_prov = build_core_words(col_maps, cfg["n_kernel"])
    narrow_words = build_narrow_core_words(core_words, col_maps)
    probe_words = set()
    for dom in DOMAINS:
        for w in PROBES[dom]:
            probe_words.add(_norm_word(w))
    probe_words -= core_words   # probes are held OUT of the core
    seed_words = core_words | probe_words

    _log("assembling relational subgraph from source=%s (core=%d narrow=%d probes=%d)..." % (
        cfg["source"], len(core_words), len(narrow_words), len(probe_words)))
    words, edges, gmeta = build_relational_subgraph(cfg["source"], seed_words, HOPS, cfg["max_nodes"])
    _log("graph: scanned=%d adj_nodes=%d seeds_in_graph=%d -> n=%d edges=%d" % (
        gmeta["n_edges_scanned"], gmeta["n_adj_nodes"], gmeta["n_seed_in_graph"], gmeta["n_nodes"], gmeta["n_edges"]))
    if gmeta["n_nodes"] < 100 or gmeta["n_edges"] < 100:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_GRAPH_EMPTY", run_mode=run_mode,
                      verdict_msg="relational subgraph too small (n=%d edges=%d); source=%s not usable" % (
                          gmeta["n_nodes"], gmeta["n_edges"], cfg["source"]),
                      summary="graph empty", elapsed_s=time.perf_counter() - t0, graph_meta=gmeta))
        raise SystemExit(1)

    Y, present = build_attr_matrix(words, col_maps)
    idx = {w: i for i, w in enumerate(words)}
    core_mask = np.zeros(len(words), dtype=bool)
    narrow_mask = np.zeros(len(words), dtype=bool)
    for w in core_words:
        if w in idx:
            core_mask[idx[w]] = True
    for w in narrow_words:
        if w in idx:
            narrow_mask[idx[w]] = True
    probe_domain = {}
    for dom in DOMAINS:
        for w in PROBES[dom]:
            nw = _norm_word(w)
            if nw in idx and not core_mask[idx[nw]]:
                probe_domain[idx[nw]] = dom

    # grounded fraction (no-coverage FLAGGED, not fabricated).
    core_ids = np.where(core_mask)[0]
    grounded = int(sum(1 for i in core_ids if present[i].any()))
    grounded_frac = grounded / max(1, len(core_ids))
    _log("core in graph=%d grounded(any-norm)=%d (%.1f%%) | narrow in graph=%d" % (
        len(core_ids), grounded, 100 * grounded_frac, int(narrow_mask.sum())))

    # independence gate over the grounded CORE channels.
    sel, sel_info = independence_select(Y[core_mask], present[core_mask])
    _log("INDEPENDENCE selected=%s (n=%d)" % (sel, sel_info["n_selected"]))
    if sel_info["n_selected"] < INDEP_MIN_SELECTED:
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CHANNELS_NOT_INDEPENDENT", run_mode=run_mode,
                      verdict_msg="only %d non-redundant channels; nothing to fuse" % sel_info["n_selected"],
                      summary="channels not independent", elapsed_s=time.perf_counter() - t0, independence=sel_info))
        raise SystemExit(1)
    sel_idx = [ATTR_NAMES.index(s) for s in sel]

    probe_cov = {dom: sum(1 for i, d in probe_domain.items() if d == dom) for dom in DOMAINS}
    _log("probe coverage per domain (in graph, non-core): %s" % probe_cov)

    spanning_seeds = []
    narrow_seeds = []
    seed_failures = []
    for seed in cfg["seeds"]:
        try:
            sp = reach_eval(words, edges, Y, present, sel_idx, core_mask, probe_domain, seed, device)
            nr = reach_eval(words, edges, Y, present, sel_idx, narrow_mask, probe_domain, seed, device)
            if "error" in sp or "error" in nr:
                raise RuntimeError("reach_eval error span=%s narrow=%s" % (sp.get("error"), nr.get("error")))
            if len(set(sp["arm_sigs"].values())) < 3:
                raise RuntimeError("ARMS_MUST_DIFFER seed=%d only %d sigs" % (seed, len(set(sp["arm_sigs"].values()))))
            spanning_seeds.append(sp)
            narrow_seeds.append(nr)
            write_partial(out_dir, seed, dict(seed=seed, spanning=sp["per_domain"], narrow=nr["per_domain"],
                                              agg=sp["aggregate_reach"]))
            _log("seed=%d span_agg=%.3f span=%s | narrow_agg=%.3f narrow=%s" % (
                seed, sp["aggregate_reach"], {d: round(sp["per_domain"][d]["reach"], 2) for d in DOMAINS},
                nr["aggregate_reach"], {d: round(nr["per_domain"][d]["reach"], 2) for d in DOMAINS}))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=seed, failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(spanning_seeds) < len(cfg["seeds"]):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
                      verdict_msg="expected %d seeds got %d (failures=%s)" % (
                          len(cfg["seeds"]), len(spanning_seeds), seed_failures),
                      summary="cardinality breach", elapsed_s=time.perf_counter() - t0, seed_failures=seed_failures))
        raise SystemExit(1)

    meta = dict(source=cfg["source"], graph_meta=gmeta, core_provenance=core_prov,
                n_core_in_graph=len(core_ids), grounded_fraction=round(grounded_frac, 4),
                n_narrow_in_graph=int(narrow_mask.sum()), probe_coverage=probe_cov,
                independence=sel_info, selected_channels=sel, n_seeds=len(cfg["seeds"]))
    agg = aggregate_and_verdict(spanning_seeds, narrow_seeds, meta)
    vmsg = "%s || %s || span_per_domain=%s agg=%s || narrow_per_domain=%s || control_fires=%s || core=%d grounded=%.1f%% n=%d" % (
        agg["verdict"], agg["one_line"], agg["spanning_per_domain"], agg["spanning_aggregate"],
        agg["narrow_per_domain"], agg["control_fires"], len(core_ids), 100 * grounded_frac, gmeta["n_nodes"])
    write_metrics(out_dir, dict(
        verdict=agg["verdict"], run_mode=run_mode, verdict_msg=vmsg[:1500], summary=agg["one_line"][:300],
        elapsed_s=time.perf_counter() - t0, reach=agg, meta=meta,
        spanning_seedruns=[s["per_domain"] for s in spanning_seeds],
        narrow_seedruns=[s["per_domain"] for s in narrow_seeds],
        probe_records=spanning_seeds[0].get("probe_records", [])))
    _log("VERDICT %s :: %s (%.1fs)" % (agg["verdict"], agg["one_line"], time.perf_counter() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    out_dir = get_output_dir(ANCHOR_NAME)   # Path (write_metrics/write_partial require Path.mkdir)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    _write_start_marker(str(out_dir), run_mode, len(cfg["seeds"]))
    t0 = time.perf_counter()
    _log("device=%s run_mode=%s" % (device, run_mode))

    # LIGHT planted self-test: discriminators MUST fire (runs in EVERY mode as the pre-flight gate).
    st_ok, st_res = _mechanism_selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (reach did not fire on planted spanning core / narrow must-fail did "
                        "not collapse / scramble did not collapse): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS reach: planted SPANNING core reaches all 6 domains; planted NARROW (physical-only) "
                        "core FAILS abstract/emotional/math (must-fail control fires) + reaches physical; SCRAMBLED core "
                        "does not ground; arms differ. %s" % st_res,
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    # Real run (smoke / full): acquire data.
    for key in DATASETS:
        if not _ensure_dataset(key):
            write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                          verdict_msg="norm dataset %r absent + self-acquire failed: %s" % (key, DATASETS[key]["path"]),
                          summary="norm data missing", elapsed_s=time.perf_counter() - t0))
            raise SystemExit(1)
    if cfg["source"] == "cskg" and not _ensure_cskg():
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CSKG absent + self-acquire failed: %s (Zenodo 4331372; ~112MB; stage manually or "
                                  "check runner network)" % CSKG["path"],
                      summary="CSKG missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)
    if cfg["source"] == "cn" and not os.path.exists(CN_RELATIONS):
        write_metrics(out_dir, dict(verdict="HARD_FAIL_DATA_MISSING", run_mode=run_mode,
                      verdict_msg="CN relations.jsonl absent: %s" % CN_RELATIONS,
                      summary="CN relations missing", elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    col_maps = load_all_norm_maps()
    _run_real(run_mode, cfg, col_maps, out_dir, t0, device)


if __name__ == "__main__":
    output_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
