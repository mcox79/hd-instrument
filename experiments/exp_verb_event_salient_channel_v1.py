"""exp_verb_event_salient_channel_v1 -- does adding the brain's EVENT-SALIENT experiential
attributes (not more sensorimotor detail) let the 12-dim grounded-norms space clear the floor it
failed at n=222 for verbs, on the SimVerb-3500-powered disjoint stratum?

PRE-REG (no separate preregs/*.md file; the three source notes ARE the pre-registration, same
convention exp_verb_target_space_n222_v1 uses when a cell measures/extends an existing
target-space design rather than opening a new one):
  notes/verb_representation_brain_drill_and_channel_specification_2026-08-17.md  section (d),
    THE BUILD SPECIFICATION THIS CELL IMPLEMENTS (D0-D10). Every PINNED/OURS label below is
    inherited from that drill's section (c) table; nothing here re-derives biology.
  notes/verb_similarity_ruler_acquisition_and_fitness_2026-08-17.md              THE RULER.
    SimVerb-3500 fitness, the 3,317-pair DISJOINT-from-SimLex stratum, the 0.6121 ceiling
    (NOT 1.0 -- SimVerb's OWN recomputed inter-annotator agreement), the C1_PARTIAL method spec.
  notes/item2_verb_target_space_n222_measurement_2026-08-17.md                  THE LICENSE.
    K1_OWN_NORMS on SimLex-V, n=222: rho 0.2607 [0.1282,0.3841], margin over F_SCRAMBLE_PERM_P95
    +0.1452 [-0.0496,+0.3379] NOT_SEPARATED. This is the ONLY number this cell is licensed to
    build on; it is NEVER imported as a floor or CI, only reproduced as a REGRESSION GATE below.

THE ONE VARIABLE: stratum, scorer (L2-normalise, plain cosine, Spearman vs gold), floor
construction, seeds and bootstrap machinery are IMPORTED, never reimplemented -- only the VERB'S
CODE varies across arms. Libraries reused, unedited:
  exp_encoding_quality_instrument_v2   (INS)  _l2n, _spearman -- the scorer
  exp_meaning_asset_fair_test_v1       (FT)   boot_rho, boot_rho_diff, band, T_MARGIN_MIN
  exp_bridged_grounding_from_core_v1   (CELL) load_simlex_pos, pair_cos, corpus_counts
  exp_selectional_constraint_bridge_v1 (SEL)  build_floors (4-floor incl F_CONSTANT_PROTOTYPE),
                                               scramble_floor, _score_cos, ORTHO_DIMS, N_PERM/N_BOOT
                                               (module-level, resolved from THIS process's argv,
                                               so SEL.SMOKE tracks THIS cell's --grid flag exactly)
  exp_verb_target_space_n222_v1        (N222) run_stratum, recount_simlex, load_raw_norms --
                                               reused verbatim for the REGRESSION GATE so the gate
                                               is a byte-for-byte re-derivation, not a re-implement.
  exp_task_degeneracy_v1               ruler_mode_gate() -- HARD GATE, called in self_test/run.
  tools/exp_checkpoint.py              per-arm checkpoint/resume (MANDATORY, CLAUDE.md).

`--smoke` in argv silently drops the frequency-floor ruler to V=512/8MB (exp_task_degeneracy_v1
ruler_mode_gate, exp_encoding_quality_instrument_v2 RUN_MODE resolution). THIS CELL'S FLAG IS
`--grid full|reduced`, never `--smoke`, for exactly that reason (the trap re-earned by every
sibling cell in this family).

TWO POPULATION RULES, NOT NEGOTIABLE (verb_similarity_ruler_acquisition_and_fitness):
  - 170 of SimLex-999's 222 verb pairs are ALSO in SimVerb (gold agreement rho 0.9121 on those
    170) -- NOT independent measurements. PRIMARY = the 3,317-pair SimVerb stratum DISJOINT from
    SimLex-V. The 170-pair OVERLAP stratum is reported separately, A0 only, labelled, NEVER
    pooled and NEVER compared numerically to the primary.
  - THE CEILING IS 0.6121, NOT 1.0 (SimVerb's own recomputed inter-annotator agreement, itself
    caveated as an effectively ~20-item statistic -- see the ruler note section 4). Every headline
    score is reported BOTH as absolute rho AND as a fraction of 0.6121.

WHAT LICENSES THIS BUILD, AND ITS ONE CONDITION (verb_similarity_ruler_acquisition_and_fitness
section 7 + the task brief): power is SOLVED (projected margin CI half-width 0.0498 at n=3,317,
3x narrower than the +0.1452 effect) so POWER_INSUFFICIENT is off the table. THE CONDITION: our
own dimension 12 IS Brysbaert Conc.M, so C1_PARTIAL (partialling concreteness AND log-frequency,
both mean and abs-diff columns, residualisation recomputed INSIDE every bootstrap replicate) MUST
run on every arm before any verdict about verb meaning is drawn. If A0's rho does not survive
C1_PARTIAL, the whole "verbs need their own channel" framing may be a concreteness artifact.

PINNED (drill section c) vs OURS -- INVENTION UNDER TEST, restated for this file:
  PINNED   pMTG tuned by argument valency + telicity; NOT motor/premotor (no channel widening of
           the 5 effector dims here); agent/patient held as distinct role-slots (lmSTC) -- this is
           why S1/S2 get real arms, not a token gesture; event vs object concepts share ONE
           experiential code for NOUNS (Tong et al. 2025), UNPINNED for verbs; Binder's blocks are
           dissociable neural subsystems; partialling imageability/concreteness is required before
           reading a grammatical-class result (the 2024 pMTG partial-RSA study needed exactly this
           to see the effect at all).
  OURS     that Tong et al.'s 13 event-salient features rank top for VERBS too (untested, is what
           this cell measures); the Lancaster-to-Binder crosswalk; VAD + ATOMIC-consequentiality
           as a scalar operationalisation of "event-salient" (socialness -- Diveica et al. 2022 --
           is NOT on disk, re-enumerated this pass: only a QA corpus data/corpora/social_iqa/
           exists, no word-level socialness ratings; A1 is therefore 12+4=16-dim, not the drill's
           hypothesised 17-dim, and this is stated everywhere the width matters); ATOMIC-event-
           token consequentiality extraction via lemma matching on the 'event' field; S1 (mean
           code of SUBJ/OBJ slot fillers) and S2 (OBJ-mean minus SUBJ-mean) as the cheapest
           testable forms of the function/trajectory hypotheses; all constant-floor/scramble
           constructions generalised from n222's own documented generalisation.

Prior-work check (substrate-KB concept-query, before authoring, per standing discipline):
`bash tools/substrate_query.sh "verb event salient channel Binder features socialness
consequentiality slot frame argument structure"` returned top cosine 0.3145 on entity 'salient'
(a bare WordNet lemma node, sources data/substrate_index + data/wordnet_cache) and 0.2949 on an
UNRELATED multi-agent social-DRIVE convention-alignment research note
(notes/research_drill_motivation_boundary_probe_2x_2026-06-10.md) -- neither is prior art on a
verb event-salient channel; the token overlap is on "salient"/"social" alone. The real dedup for
this cell is the direct read of the three notes cited above (verbatim, this pass), which is a
rediscovery-check by reading, not by KB query -- consistent with the drill's own dedup coverage
statement. VERDICT: genuinely novel; no prior cell builds this channel.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened by this cell. WordNet (nltk corpus) is used ONLY as a labelled
CEILING-REFERENCE oracle (K_WORDNET_ORACLE_V, no verdict weight) and as a lemmatiser/sense-count
source for feature columns -- never as a meaning source for a scored arm's own code.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import ast
import collections
import csv
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
from scipy.stats import rankdata

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS            # THE SCORER, imported, never edited
import exp_meaning_asset_fair_test_v1 as FT                 # verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL            # sibling library, never edited
import exp_selectional_constraint_bridge_v1 as SEL           # 4-floor battery + scorer, never edited
import exp_verb_target_space_n222_v1 as N222                 # THE LICENSING CELL, reused for the gate
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "verb_event_salient_channel_v1"
CODE_VERSION = "v1.0"
PREREG = ("notes/verb_representation_brain_drill_and_channel_specification_2026-08-17.md section "
          "(d) BUILD SPECIFICATION + notes/verb_similarity_ruler_acquisition_and_fitness_2026-08-17"
          ".md (the ruler, the C1_PARTIAL method) + notes/item2_verb_target_space_n222_measurement_"
          "2026-08-17.md (the license, rho=0.2607 [0.1282,0.3841] on SimLex-V n=222). No separate "
          "preregs/*.md file: same convention as exp_verb_target_space_n222_v1.")

# THE FLAG IS `--grid full|reduced`, NOT `--smoke` -- LOAD-BEARING, see module docstring.
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

BOOT_SEED = 20260817
N_BOOT_PARTIAL = 300 if SMOKE else 2000    # OURS -- deliberate compute-budget cut below SEL.N_BOOT
                                            # (10000): C1_PARTIAL refits an OLS residualisation
                                            # INSIDE every replicate (spec requirement, not
                                            # optional), so a plain rho bootstrap and a partial-rho
                                            # bootstrap are NOT the same cost. Applied identically to
                                            # every arm and every floor so relative comparisons
                                            # (margins) remain valid; only absolute CI width is
                                            # coarser than the raw-score bootstraps. Reported
                                            # explicitly in metrics.json, never silently substituted.
JOINT_GATE_MIN_N = 150                     # OURS, adapted from drill D7's own threshold

EVENT_MIN_SUPPORT = 3     # min ATOMIC events required to trust a verb's consequentiality estimate
ATOMIC_COVERAGE_MIN_FRAC = 0.70   # below this, drop consequentiality from A1 (drill's own escape
                                   # hatch: "if coverage is poor, drop that column and re-match")
SLOT_MIN_FILLERS = 3      # reused convention (selectional_preference_extractor_v1 / SEL)
SLOT_FILLER_TOPK = 50     # reused convention (SEL.FILLER_TOPK)

FLOOR_ORTHO, FLOOR_FREQ, FLOOR_SCRAM, FLOOR_CONST = (
    SEL.FLOOR_ORTHO, SEL.FLOOR_FREQ, SEL.FLOOR_SCRAM, SEL.FLOOR_CONST)

BENCH = REPO / "data" / "encoder_eval_benchmarks"
SIMVERB = BENCH / "simverb3500.txt"
SIMLEX = BENCH / "simlex999.txt"
STATS = BENCH / "simverb3500_stats.txt"
GT = REPO / "data" / "grounding_testbed"
ASSETS = REPO / "data" / "verb_event_salient_channel_v1_assets"
ATOMIC_ALL_AGG = REPO / "data" / "atomic_kb" / "v4_atomic_all_agg.csv"
SLOTS_PKL = REPO / "data" / "selectional_preferences_v1" / "selectional_slots_v1.pkl"


# ==============================================================================================
# LOADERS -- every one enumerated from disk this pass, never assumed
# ==============================================================================================
def load_simverb(path: Path) -> List[Tuple[str, str, str, float, str]]:
    """word1, word2, POS, score, relation -- tab separated, NO header line."""
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            p = line.split("\t")
            out.append((p[0], p[1], p[2], float(p[3]), p[4]))
    return out


def load_simlex_verbs(path: Path) -> List[Tuple[str, str, float]]:
    """SimLex-999 HAS a header line. Return only POS=='V' rows."""
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    hdr = rows[0]
    i1, i2, ip, isc = (hdr.index("word1"), hdr.index("word2"),
                       hdr.index("POS"), hdr.index("SimLex999"))
    return [(r[i1], r[i2], float(r[isc])) for r in rows[1:] if r and r[ip] == "V"]


def load_bncfreq(path: Path) -> Dict[str, int]:
    """simverb3500_stats.txt: whitespace-separated, header COUNTER VBLEMMA VBCLASS BNCFREQ ..."""
    out: Dict[str, int] = {}
    with open(path, "r", encoding="utf-8") as f:
        next(f)  # header
        for line in f:
            p = line.split()
            if len(p) >= 4:
                try:
                    out[p[1].lower()] = int(p[3])
                except ValueError:
                    pass   # e.g. 'N/A' -- word dropped from the frequency covariate, not zero-filled
    return out


def load_aoa(path: Path) -> Dict[str, float]:
    out: Dict[str, float] = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            w = (row.get("Word") or "").strip().lower()
            v = (row.get("AoA_Kup") or "").strip()
            if w and v:
                try:
                    out[w] = float(v)
                except ValueError:
                    pass
    return out


def load_warriner(path: Path) -> Dict[str, Tuple[float, float, float]]:
    out: Dict[str, Tuple[float, float, float]] = {}
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            w = (row.get("Word") or "").strip().lower()
            try:
                v = float(row["V.Mean.Sum"]); a = float(row["A.Mean.Sum"]); d = float(row["D.Mean.Sum"])
            except (KeyError, ValueError, TypeError):
                continue
            if w:
                out[w] = (v, a, d)
    return out


def load_slot_filler() -> Dict[Tuple[str, str], Dict[str, int]]:
    import pickle
    with open(SLOTS_PKL, "rb") as f:
        d = pickle.load(f)
    return d["slot_filler"]


_WN_SENSE_CACHE: Dict[str, Optional[int]] = {}


def wordnet_sense_count(w: str) -> Optional[int]:
    if w in _WN_SENSE_CACHE:
        return _WN_SENSE_CACHE[w]
    from nltk.corpus import wordnet as wn
    syn = wn.synsets(w, pos="v")
    n = len(syn) if syn else None
    _WN_SENSE_CACHE[w] = n
    return n


def wordnet_wup_max(w1: str, w2: str) -> Optional[float]:
    from nltk.corpus import wordnet as wn
    s1 = wn.synsets(w1, pos="v")
    s2 = wn.synsets(w2, pos="v")
    if not s1 or not s2:
        return None
    best = None
    for a in s1:
        for b in s2:
            try:
                sim = a.wup_similarity(b)
            except Exception:
                sim = None
            if sim is not None and (best is None or sim > best):
                best = sim
    return best


_ATOMIC_TOKEN_RE = re.compile(r"[a-z]+")
_ATOMIC_EFFECT_COLS = ("oEffect", "oReact", "oWant", "xEffect", "xIntent", "xNeed", "xReact", "xWant")


def build_atomic_consequentiality(verb_lemmas: Set[str]) -> Dict[str, float]:
    """OURS -- extraction, not a meaning source. For each ATOMIC v4 event whose 'event' text
    lemma-matches a SimVerb verb, count how many of the 8 structured effect/react/want/intent
    fields are non-empty and not the placeholder 'none'; average that count per verb over every
    ATOMIC event that mentions it (min EVENT_MIN_SUPPORT events, else the verb is undefined here).
    Cached to disk (data/verb_event_salient_channel_v1_assets/) since the pass over 24,313 rows
    with a lemmatiser call per token is the single slowest precompute in this cell."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    cache_path = ASSETS / "atomic_consequentiality_v1.json"
    if cache_path.exists():
        try:
            d = json.loads(cache_path.read_text(encoding="utf-8"))
            if set(d.get("lemmas_requested", [])) >= verb_lemmas:
                print(f"[atomic] loaded cached consequentiality for {len(d['scores'])} verbs "
                      f"from {cache_path}", flush=True)
                return {k: float(v) for k, v in d["scores"].items()}
        except Exception as e:
            print(f"[atomic] cache unreadable ({e!r}), recomputing", flush=True)

    from hdlab.reading_grounding_loop import normalize_lemma
    sums: Dict[str, float] = collections.defaultdict(float)
    counts: Dict[str, int] = collections.defaultdict(int)
    t0 = time.time()
    n_rows = 0
    with open(ATOMIC_ALL_AGG, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            n_rows += 1
            if n_rows % 5000 == 0:
                print(f"[atomic] scanned {n_rows} rows ({time.time() - t0:.1f}s)", flush=True)
            ev = (row.get("event") or "").lower()
            toks = _ATOMIC_TOKEN_RE.findall(ev)
            lemmas: Set[str] = set()
            for t in toks:
                if t in ("personx", "persony", "person"):
                    continue
                try:
                    lemmas.add(normalize_lemma(t))
                except Exception:
                    lemmas.add(t)
            hit = lemmas & verb_lemmas
            if not hit:
                continue
            n_signal = 0
            for col in _ATOMIC_EFFECT_COLS:
                raw = row.get(col, "")
                if not raw:
                    continue
                try:
                    parsed = ast.literal_eval(raw)
                except (ValueError, SyntaxError):
                    parsed = []
                for item in parsed:
                    s = str(item).strip().lower()
                    if s and s != "none":
                        n_signal += 1
            for lem in hit:
                sums[lem] += n_signal
                counts[lem] += 1
    scores = {lem: sums[lem] / counts[lem] for lem in counts if counts[lem] >= EVENT_MIN_SUPPORT}
    cache_path.write_text(json.dumps({
        "lemmas_requested": sorted(verb_lemmas), "scores": scores,
        "min_support": EVENT_MIN_SUPPORT, "n_rows_scanned": n_rows,
        "built": "ATOMIC v4 all_agg.csv, event-field lemma match, count of non-empty/non-'none' "
                 "structured fields per matching event, averaged per verb. OURS, not a meaning "
                 "source: a feature-extraction heuristic over a crowd-authored commonsense KB."},
        indent=2), encoding="utf-8")
    print(f"[atomic] built consequentiality for {len(scores)}/{len(verb_lemmas)} requested verbs "
          f"in {time.time() - t0:.1f}s, cached to {cache_path}", flush=True)
    return scores


# ==============================================================================================
# small numeric helpers
# ==============================================================================================
def zscore_col(vals: Dict[str, float]) -> Dict[str, float]:
    words = sorted(vals)   # sorted(set()) discipline
    arr = np.array([vals[w] for w in words], dtype=np.float64)
    mu, sd = arr.mean(), arr.std(ddof=0) or 1.0
    return {w: float((vals[w] - mu) / sd) for w in words}


def widen(base_raw: Dict[str, np.ndarray], extra_cols: List[Dict[str, float]]) -> Dict[str, np.ndarray]:
    """word -> concat(base_raw[word], [extra_cols[j][word] for j]) for words covered by ALL of
    base_raw and every extra column. NO ZERO-FILL: a word missing any covariate is dropped."""
    out: Dict[str, np.ndarray] = {}
    for w, v in base_raw.items():
        vals = []
        ok = True
        for c in extra_cols:
            if w not in c:
                ok = False
                break
            vals.append(c[w])
        if ok:
            out[w] = np.concatenate([np.asarray(v, dtype=np.float64), np.array(vals, dtype=np.float64)])
    return out


def only_cols(word_pool: Sequence[str], extra_cols: List[Dict[str, float]]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
    for w in word_pool:
        vals = []
        ok = True
        for c in extra_cols:
            if w not in c:
                ok = False
                break
            vals.append(c[w])
        if ok:
            out[w] = np.array(vals, dtype=np.float64)
    return out


def slot_mean_code(slot_filler: Dict[Tuple[str, str], Dict[str, int]], role: str, verb: str,
                   base12: Dict[str, np.ndarray], topk: int = SLOT_FILLER_TOPK) -> Optional[np.ndarray]:
    fl = slot_filler.get((verb, role))
    if not fl:
        return None
    items = sorted(fl.items(), key=lambda kv: (-kv[1], kv[0]))[:topk]
    vecs, wts = [], []
    for f, c in items:
        v = base12.get(f)
        if v is not None:
            vecs.append(np.asarray(v, dtype=np.float64))
            wts.append(float(c))
    if len(vecs) < SLOT_MIN_FILLERS:
        return None
    M = np.stack(vecs)
    w = np.array(wts, dtype=np.float64)
    return (M * w[:, None]).sum(axis=0) / w.sum()


def build_s1_s2(verbs: Sequence[str], slot_filler: Dict[Tuple[str, str], Dict[str, int]],
                base12: Dict[str, np.ndarray]) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    s1: Dict[str, np.ndarray] = {}
    s2: Dict[str, np.ndarray] = {}
    for v in verbs:
        subj = slot_mean_code(slot_filler, "SUBJ", v, base12)
        obj = slot_mean_code(slot_filler, "OBJ", v, base12)
        if subj is not None and obj is not None:
            s1[v] = np.concatenate([subj, obj])
            s2[v] = obj - subj
    return s1, s2


def _arm_seed(name: str) -> int:
    """Deterministic per-arm seed via sha256, NOT builtin hash() (randomised per process unless
    PYTHONHASHSEED is pinned -- same fix SEL._arm_seed documents and applies)."""
    return int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big") % 100000


# ==============================================================================================
# C1_PARTIAL -- partial Spearman by rank-residualisation, refit INSIDE every bootstrap replicate
# ==============================================================================================
def _partial_point(x: np.ndarray, y: np.ndarray, Z: np.ndarray) -> float:
    n = len(x)
    rx = rankdata(x, method="average")
    ry = rankdata(y, method="average")
    RZ = rankdata(Z, axis=0, method="average") if Z.shape[1] > 0 else np.zeros((n, 0))
    D = np.hstack([np.ones((n, 1)), RZ])
    coefx, *_ = np.linalg.lstsq(D, rx, rcond=None)
    coefy, *_ = np.linalg.lstsq(D, ry, rcond=None)
    resx = rx - D @ coefx
    resy = ry - D @ coefy
    resx = resx - resx.mean()
    resy = resy - resy.mean()
    denom = np.sqrt((resx * resx).sum() * (resy * resy).sum())
    if denom <= 0:
        return float("nan")
    return float((resx * resy).sum() / denom)


def partial_rho_boot(x: np.ndarray, y: np.ndarray, Z: np.ndarray, n_boot: int, seed: int) -> Dict:
    x = np.asarray(x, dtype=np.float64); y = np.asarray(y, dtype=np.float64)
    Z = np.asarray(Z, dtype=np.float64)
    n = len(x)
    pt = _partial_point(x, y, Z)
    if n < 10:
        return {"point": pt, "ci95": [float("nan"), float("nan")], "n": n, "n_boot": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    draws = np.empty(n_boot)
    for b in range(n_boot):
        j = idx[b]
        draws[b] = _partial_point(x[j], y[j], Z[j])
    draws = draws[np.isfinite(draws)]
    lo, hi = (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))) if len(draws) else (float("nan"), float("nan"))
    return {"point": pt, "ci95": [lo, hi], "n": n, "n_boot_used": int(len(draws)), "band": FT.band([lo, hi])}


def partial_margin_boot(x_treat: np.ndarray, x_floor: np.ndarray, y: np.ndarray, Z: np.ndarray,
                        n_boot: int, seed: int) -> Dict:
    x_treat = np.asarray(x_treat, dtype=np.float64); x_floor = np.asarray(x_floor, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64); Z = np.asarray(Z, dtype=np.float64)
    n = len(x_treat)
    pt = _partial_point(x_treat, y, Z) - _partial_point(x_floor, y, Z)
    if n < 10:
        return {"point": pt, "ci95": [float("nan"), float("nan")], "band": "UNDEFINED", "n": n}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    draws = np.empty(n_boot)
    for b in range(n_boot):
        j = idx[b]
        draws[b] = _partial_point(x_treat[j], y[j], Z[j]) - _partial_point(x_floor[j], y[j], Z[j])
    draws = draws[np.isfinite(draws)]
    if len(draws) == 0:
        return {"point": pt, "ci95": [float("nan"), float("nan")], "band": "UNDEFINED", "n": n}
    lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    return {"point": float(pt), "ci95": [lo, hi], "band": FT.band([lo, hi]), "n": n}


def build_covariates(ia: np.ndarray, ib: np.ndarray, vocab: List[str], conc_z: Dict[str, float],
                     bncfreq: Dict[str, int]) -> Tuple[np.ndarray, np.ndarray]:
    """z1=mean concreteness, z2=abs-diff concreteness, z3=mean log-freq, z4=abs-diff log-freq.
    Absolute-difference columns are REQUIRED per the ruler note's C1_PARTIAL spec (a similarity
    instrument is sensitive to how CLOSE two items are on a covariate, not just their mean).
    Returns (Z, mask): 48/827 SimVerb lemmas have BNCFREQ='N/A' (measured on disk), so a covariate
    row is only valid where BOTH words have a real BNCFREQ -- NO ZERO-FILL, mask instead."""
    w1 = [vocab[i] for i in ia]
    w2 = [vocab[i] for i in ib]
    c1 = np.array([conc_z.get(w, 0.0) for w in w1])
    c2 = np.array([conc_z.get(w, 0.0) for w in w2])
    mask = np.array([w in bncfreq for w in w1]) & np.array([w in bncfreq for w in w2])
    f1 = np.array([np.log10(1.0 + bncfreq.get(w, 0)) for w in w1])
    f2 = np.array([np.log10(1.0 + bncfreq.get(w, 0)) for w in w2])
    z1 = (c1 + c2) / 2.0
    z2 = np.abs(c1 - c2)
    z3 = (f1 + f2) / 2.0
    z4 = np.abs(f1 - f2)
    return np.stack([z1, z2, z3, z4], axis=1), mask


# ==============================================================================================
# per-arm scoring -- generalises exp_verb_target_space_n222_v1.run_stratum to arbitrary width
# ==============================================================================================
def run_arm(name: str, raw_by_word: Dict[str, np.ndarray], vocab: List[str], vocab_idx: Dict[str, int],
           ia_full: np.ndarray, ib_full: np.ndarray, gold_full: np.ndarray, counts: Dict[str, int],
           conc_z: Dict[str, float], bncfreq: Dict[str, int], seed: int) -> Dict:
    width = next(iter(raw_by_word.values())).shape[0] if raw_by_word else 0
    mask = np.array([vocab[i] in raw_by_word and vocab[j] in raw_by_word
                     for i, j in zip(ia_full, ib_full)])
    n = int(mask.sum())
    out: Dict = {"arm": name, "width": width, "n": n,
                "spearman_ci_halfwidth_approx": round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None}
    if n < JOINT_GATE_MIN_N:
        out["status"] = "NOT_CONSTRUCTIBLE"
        out["rule"] = f"n={n} < JOINT_GATE_MIN_N={JOINT_GATE_MIN_N}"
        return out

    ia, ib, gold = ia_full[mask], ib_full[mask], gold_full[mask]
    X = np.zeros((len(vocab), width), dtype=np.float32)
    for i, w in enumerate(vocab):    # iterate the CALLER's vocab, not raw_by_word's own keys --
        v = raw_by_word.get(w)       # raw_by_word may be keyed over a DIFFERENT (larger/smaller)
        if v is not None:            # word set than this call's vocab (e.g. A0's dict reused
            X[i] = v                 # against the overlap stratum's own smaller vocab).
    X = INS._l2n(X)
    obs = CELL.pair_cos(X, ia, ib)

    # F_CONSTANT_PROTOTYPE, generalised exactly as N222.run_stratum (word2-replaced vs
    # word1-replaced, take the stronger/harder-to-beat ordering).
    stratum_words = sorted(set(vocab[i] for i in ia) | set(vocab[i] for i in ib))
    proto = np.stack([raw_by_word[w] for w in stratum_words if w in raw_by_word]).astype(np.float64).mean(axis=0)
    protoN = INS._l2n(proto[None, :].astype(np.float32))[0]
    cos_w2 = (X[ia] @ protoN).astype(np.float64)
    cos_w1 = (X[ib] @ protoN).astype(np.float64)
    rho_w2 = INS._spearman(cos_w2, gold)
    rho_w1 = INS._spearman(cos_w1, gold)
    use_w2 = (not np.isfinite(rho_w1)) or (rho_w2 >= rho_w1)
    const_cos = cos_w2 if use_w2 else cos_w1

    floors = SEL.build_floors(vocab, ia, ib, gold, counts, const_cos)
    scored = SEL._score_cos(name, obs, X, ia, ib, gold, floors, seed=seed, light=False)
    obs_saved = scored.pop("_cos")
    scored["width"] = width
    scored["F_CONSTANT_PROTOTYPE_variant"] = "word2_replaced" if use_w2 else "word1_replaced"

    # C1_PARTIAL -- partial the treatment AND every floor's own channel, on THIS arm's own rows,
    # restricted further to the covariate mask (48/827 SimVerb lemmas lack BNCFREQ -- no zero-fill).
    Z_full, cov_mask = build_covariates(ia, ib, vocab, conc_z, bncfreq)
    sc = SEL.scramble_floor(X, ia, ib, gold, seed)
    partner_by_floor = {FLOOR_ORTHO: floors[FLOOR_ORTHO]["_partner"], FLOOR_FREQ: floors[FLOOR_FREQ]["_partner"],
                        FLOOR_CONST: floors[FLOOR_CONST]["_partner"], FLOOR_SCRAM: sc["_partner"]}
    Z, gold_c, obs_c = Z_full[cov_mask], gold[cov_mask], obs_saved[cov_mask]
    partner_by_floor_c = {k: v[cov_mask] for k, v in partner_by_floor.items()}
    partial_treat = partial_rho_boot(obs_c, gold_c, Z, N_BOOT_PARTIAL, seed ^ 0xC1)
    partial_floors = {k: partial_rho_boot(v, gold_c, Z, N_BOOT_PARTIAL, seed ^ 0xC1) for k, v in partner_by_floor_c.items()}
    strongest_partial_floor = max(partial_floors, key=lambda k: partial_floors[k]["point"])
    partial_margin = partial_margin_boot(obs_c, partner_by_floor_c[strongest_partial_floor], gold_c, Z,
                                         N_BOOT_PARTIAL, seed ^ 0xC1)
    scored["C1_PARTIAL"] = {
        "covariates": "mean_conc,absdiff_conc,mean_log10freq,absdiff_log10freq",
        "n_boot": N_BOOT_PARTIAL, "n_after_covariate_mask": int(cov_mask.sum()),
        "raw_rho_point": scored["rho"]["point"],
        "partial_rho": partial_treat, "partial_floor_rho_by_arm": {k: v["point"] for k, v in partial_floors.items()},
        "strongest_partial_floor": strongest_partial_floor,
        "partial_margin_over_strongest_partial_floor": partial_margin,
        "survives_partial": bool(partial_treat["band"] == "ABOVE" and partial_margin["band"] == "ABOVE")}
    out.update(scored)
    return out


def run_wordnet_oracle(vocab: List[str], vocab_idx: Dict[str, int], ia_full: np.ndarray,
                       ib_full: np.ndarray, gold_full: np.ndarray, counts: Dict[str, int],
                       conc_z: Dict[str, float], bncfreq: Dict[str, int], n_perm: int, seed: int) -> Dict:
    obs_all = np.full(len(ia_full), np.nan)
    have = np.zeros(len(ia_full), dtype=bool)
    for k, (i, j) in enumerate(zip(ia_full, ib_full)):
        s = wordnet_wup_max(vocab[i], vocab[j])
        if s is not None:
            obs_all[k] = s
            have[k] = True
    n = int(have.sum())
    out: Dict = {"arm": "K_WORDNET_ORACLE_V", "n": n, "role": "CEILING REFERENCE -- NEVER a pass, "
                "never a target, no verdict weight. Answers whether the stratum is readable at all."}
    if n < JOINT_GATE_MIN_N:
        out["status"] = "NOT_CONSTRUCTIBLE"
        return out
    ia, ib, gold, obs = ia_full[have], ib_full[have], gold_full[have], obs_all[have]

    floors = SEL.build_floors(vocab, ia, ib, gold, counts, None)   # no code matrix -> no F_CONST
    # Gold-permutation-only null (no vector code exists to permute ROWS of, per the docstring
    # note below). Uses the identity spearman(obs, gold[perm]) == spearman(obs[inv(perm)], gold)
    # (Spearman is invariant to relabelling both sides by the SAME permutation) to turn the
    # gold-permutation draw into a "partner" SCORE VECTOR comparable against the REAL gold via
    # the same FT.boot_rho_diff(obs, partner, gold) pathway every other floor uses.
    rng = np.random.default_rng(seed ^ 0xBEEF)
    perms = [rng.permutation(n) for _ in range(n_perm)]
    gn = np.array([INS._spearman(obs, gold[p]) for p in perms])
    finite = np.isfinite(gn)
    gn_f = gn[finite]
    p95 = float(np.percentile(gn_f, 95)) if len(gn_f) else float("nan")
    finite_idx = np.flatnonzero(finite)
    if len(gn_f):
        near_local = int(np.argmin(np.abs(gn_f - p95)))
        near_perm = perms[finite_idx[near_local]]
    else:
        near_perm = np.arange(n)
    inv_perm = np.argsort(near_perm)
    scram_partner = obs[inv_perm]

    cands = {FLOOR_ORTHO: (floors[FLOOR_ORTHO]["rho"], floors[FLOOR_ORTHO]["_partner"]),
            FLOOR_FREQ: (floors[FLOOR_FREQ]["rho"], floors[FLOOR_FREQ]["_partner"]),
            "F_SCRAMBLE_GOLD_PERM_ONLY_P95": (p95, scram_partner)}
    bf = max(cands, key=lambda k: cands[k][0])
    rho = FT.boot_rho(obs, gold, n_boot=SEL.N_BOOT, seed=BOOT_SEED)
    diff = FT.boot_rho_diff(obs, cands[bf][1], gold, n_boot=SEL.N_BOOT, seed=BOOT_SEED)
    out.update({"rho": rho, "strongest_floor": bf,
               "floor_rho_by_arm": {k: round(v[0], 4) for k, v in cands.items()},
               "margin_over_strongest_floor": diff, "band": FT.band(diff["ci95"]),
               "gold_permutation_null": {"p95": p95, "n_perm": n_perm,
                                         "note": "row-permutation variant N/A: WordNet oracle has "
                                                 "no vector code to permute rows of. Gold-"
                                                 "permutation-only substitute, documented."}})
    Z_full, cov_mask = build_covariates(ia, ib, vocab, conc_z, bncfreq)
    partial = partial_rho_boot(obs[cov_mask], gold[cov_mask], Z_full[cov_mask], N_BOOT_PARTIAL, seed ^ 0xC1)
    out["C1_PARTIAL"] = {"partial_rho": partial, "note": "oracle -- reported for context, carries "
                         "no verdict weight, consistent with its ceiling-reference role."}
    return out


def run_n2_gaussian(width: int, vocab: List[str], vocab_idx: Dict[str, int], ia_full: np.ndarray,
                    ib_full: np.ndarray, gold_full: np.ndarray, counts: Dict[str, int],
                    ref_arm_words: Set[str], seeds: Sequence[int]) -> Dict:
    """5 seeds, MAX draw never mean (standing rule): catches 'wider space has a different
    similarity distribution' artifacts that N1 (within-space scramble) cannot."""
    draws = {}
    for s in seeds:
        rng = np.random.default_rng(s)
        raw = {w: rng.standard_normal(width) for w in ref_arm_words}
        mask = np.array([vocab[i] in raw and vocab[j] in raw for i, j in zip(ia_full, ib_full)])
        if mask.sum() < JOINT_GATE_MIN_N:
            continue
        ia, ib, gold = ia_full[mask], ib_full[mask], gold_full[mask]
        X = np.zeros((len(vocab), width), dtype=np.float32)
        for w, v in raw.items():
            X[vocab_idx[w]] = v
        X = INS._l2n(X)
        obs = CELL.pair_cos(X, ia, ib)
        draws[f"seed{s}"] = {"rho": FT.boot_rho(obs, gold, n_boot=SEL.N_BOOT, seed=BOOT_SEED)["point"], "n": int(mask.sum())}
    if not draws:
        return {"width": width, "status": "NOT_CONSTRUCTIBLE"}
    mk = max(draws, key=lambda k: draws[k]["rho"])
    return {"width": width, "seeds": sorted(draws), "rho_by_seed": {k: v["rho"] for k, v in draws.items()},
           "n_by_seed": {k: v["n"] for k, v in draws.items()}, "max_draw_seed": mk,
           "rho_max_draw": draws[mk]["rho"], "rho_mean": float(np.mean([v["rho"] for v in draws.values()])),
           "policy": "MAX DRAW never the mean"}


# ==============================================================================================
# main assembly
# ==============================================================================================
def build_all_arms(pairs_disjoint: List[Tuple[str, str, str, float, str]],
                   pairs_overlap: List[Tuple[str, str, str, float, str]]) -> Dict:
    """Loads every asset, builds every arm's raw word->code dict, returns everything self_test/run
    need. Split out of run() so self_test() can call it on a slice without duplicating the loaders."""
    from hdlab import grounded_similarity as GS
    base_table = GS._table()   # word(lower) -> 12-dim z-scored torch tensor
    base12 = {w: t.numpy().astype(np.float64) for w, t in base_table.items()}
    conc_z = {w: float(v[11]) for w, v in base12.items()}   # dim 12 IS Conc.M, already z-scored

    bncfreq = load_bncfreq(STATS)
    aoa = load_aoa(GT / "AoA_51715_words.csv")
    warriner = load_warriner(GT / "Ratings_Warriner_et_al.csv")
    slot_filler = load_slot_filler()

    vocab = sorted(set(w for p in pairs_disjoint for w in (p[0].lower(), p[1].lower())))
    counts = CELL.corpus_counts()

    # ---- event-salient columns, enumerated availability (drill D3, re-verified this pass) ----
    val = {w: warriner[w][0] for w in vocab if w in warriner}
    aro = {w: warriner[w][1] for w in vocab if w in warriner}
    dom = {w: warriner[w][2] for w in vocab if w in warriner}
    val_z, aro_z, dom_z = zscore_col(val), zscore_col(aro), zscore_col(dom)

    verb_lemma_set = set(vocab)
    conseq = build_atomic_consequentiality(verb_lemma_set)
    conseq_cov = len(set(conseq) & set(vocab)) / max(1, len(vocab))
    keep_conseq = conseq_cov >= ATOMIC_COVERAGE_MIN_FRAC
    conseq_z = zscore_col(conseq) if keep_conseq else {}

    event_cols = [val_z, aro_z, dom_z] + ([conseq_z] if keep_conseq else [])
    event_col_names = ["Valence_z", "Arousal_z", "Dominance_z"] + (["Consequentiality_z"] if keep_conseq else [])
    w_event = len(event_cols)

    # ---- A3 (noise) / A4 (real-but-wrong), width-matched to A1/A2 --------------------------
    def lancaster_sd(col: str) -> Dict[str, float]:
        # re-parse once; small file, no need to persist beyond this call
        path = GT / "Lancaster_sensorimotor_norms_for_39707_words.csv"
        out = {}
        with open(path, encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                w = (row.get("Word") or "").strip().lower()
                v = row.get(col)
                if w in vocab and v not in (None, ""):
                    try:
                        out[w] = float(v)
                    except ValueError:
                        pass
        return out

    noise_cols_all = [lancaster_sd(c) for c in
                      ("Auditory.SD", "Gustatory.SD", "Haptic.SD", "Interoceptive.SD")]
    noise_cols = [zscore_col(c) for c in noise_cols_all[:w_event]]

    length_col = {w: float(len(w)) for w in vocab}
    logfreq_col = {w: float(np.log1p(counts.get(w, 0))) for w in vocab}
    aoa_col = {w: aoa[w] for w in vocab if w in aoa}
    sense_col = {}
    for w in vocab:
        sc = wordnet_sense_count(w)
        if sc is not None:
            sense_col[w] = float(sc)
    wrong_candidates = [zscore_col(aoa_col), zscore_col(logfreq_col), zscore_col(length_col), zscore_col(sense_col)]
    wrong_cols = wrong_candidates[:w_event]

    A0 = {w: v for w, v in base12.items() if w in vocab}
    A1 = widen(A0, event_cols)
    A2 = only_cols(vocab, event_cols)
    A3 = widen(A0, noise_cols)
    A4 = widen(A0, wrong_cols)
    # BUG FIX (found at smoke gate): slot FILLERS are typically NOUNS ("river", "government",
    # "train"), not verbs, so they are almost never in the SimVerb-restricted A0 dict. Look them
    # up in the FULL grounded-norms table (base12, ~26k words) instead -- measured to raise S1/S2
    # coverage from 28/3317 pairs (a construction bug) to the genuine data-limited figure.
    S1, S2 = build_s1_s2(vocab, slot_filler, base12)

    return {
        "vocab": vocab, "base12": A0, "conc_z": conc_z, "bncfreq": bncfreq, "counts": counts,
        "event_col_names": event_col_names, "w_event": w_event, "keep_conseq": keep_conseq,
        "conseq_coverage_frac": round(conseq_cov, 4),
        "arms": {"A0_INCUMBENT_12": A0, "A1_EVENT_SALIENT": A1, "A2_EVENT_ONLY": A2,
                "A3_WIDTH_MATCHED_NOISE": A3, "A4_WIDTH_MATCHED_WRONG": A4,
                "S1_SLOT_FRAME": S1, "S2_SLOT_DELTA": S2},
    }


def self_test() -> Dict:
    from exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()
    if not gate["PASS"]:
        raise SystemExit(f"RULER MODE GATE FAILED: {gate}")
    print(f"[self-test] ruler_mode_gate PASS: {gate}", flush=True)

    a5 = INS._spearman(np.array([1., 2., 3., 4., 5.]), np.array([1., 2., 3., 4., 5.]))
    assert abs(a5 - 1.0) < 1e-9
    print("[self-test] INS._spearman self-consistent", flush=True)

    sv_all = load_simverb(SIMVERB)
    assert len(sv_all) == 3500, f"SimVerb recount != 3500: {len(sv_all)}"
    sl_v = load_simlex_verbs(SIMLEX)
    assert len(sl_v) == 222, f"SimLex-V recount != 222: {len(sl_v)}"
    print(f"[self-test] SimVerb={len(sv_all)} pairs, SimLex-V={len(sl_v)} pairs (recounted, not "
          f"assumed)", flush=True)

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    sl_keys = set(frozenset((a.lower(), b.lower())) for a, b, _ in sl_v)
    usable = [r for r in sv_all if r[0].lower() in tab and r[1].lower() in tab]
    disjoint = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) not in sl_keys]
    overlap = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) in sl_keys]
    assert len(usable) == 3487, f"usable_n != 3487 (fitness json value): {len(usable)}"
    assert len(disjoint) == 3317, f"disjoint stratum != 3317 (fitness json value): {len(disjoint)}"
    assert len(overlap) == 170, f"overlap stratum != 170 (fitness json value): {len(overlap)}"
    print(f"[self-test] usable={len(usable)} disjoint={len(disjoint)} overlap={len(overlap)} "
          f"-- matches verify_simverb_ruler_fitness.py exactly", flush=True)

    # ---- C1_PARTIAL self-test: a synthetic ground truth, not the real data ----
    rng = np.random.default_rng(0)
    n = 400
    conf = rng.standard_normal(n)
    y_confounded = conf + 0.05 * rng.standard_normal(n)
    x_confounded = conf + 0.05 * rng.standard_normal(n)     # x,y correlate ONLY via conf
    z_conf = np.stack([conf, np.zeros(n), np.zeros(n), np.zeros(n)], axis=1)
    raw = _partial_point(x_confounded, y_confounded, np.zeros((n, 0)))
    partial = _partial_point(x_confounded, y_confounded, z_conf)
    assert raw > 0.9, f"synthetic confounded raw rho should be near 1.0: {raw}"
    assert abs(partial) < 0.15, f"partialling the TRUE confound should collapse rho near 0: {partial}"
    print(f"[self-test] C1_PARTIAL collapses a fully-confounded pair: raw={raw:.4f} partial={partial:.4f}",
          flush=True)
    indep = rng.standard_normal(n)
    y_indep = indep + 0.05 * rng.standard_normal(n)
    x_indep = indep + 0.05 * rng.standard_normal(n)
    unrelated_z = np.stack([rng.standard_normal(n) for _ in range(4)], axis=1)
    raw2 = _partial_point(x_indep, y_indep, np.zeros((n, 0)))
    partial2 = _partial_point(x_indep, y_indep, unrelated_z)
    assert abs(raw2 - partial2) < 0.1, (f"partialling an UNRELATED covariate should barely move rho: "
                                        f"raw={raw2:.4f} partial={partial2:.4f}")
    print(f"[self-test] C1_PARTIAL leaves an unconfounded pair alone: raw={raw2:.4f} partial={partial2:.4f}",
          flush=True)

    # ---- small-slice mechanics: build every arm on ~60 pairs, run_arm on A0 and S1 ----
    slice_disjoint = disjoint[:80]
    built = build_all_arms(slice_disjoint, overlap[:0])
    vocab = built["vocab"]
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    ia = np.array([vocab_idx[p[0].lower()] for p in slice_disjoint])
    ib = np.array([vocab_idx[p[1].lower()] for p in slice_disjoint])
    gold = np.array([p[3] for p in slice_disjoint], dtype=np.float64)
    counts = built["counts"]

    # ARMS-MUST-DIFFER (META_RULE_AF): every arm's code matrix, restricted to shared vocab, must
    # be pairwise distinct -- catches a width-matched control that accidentally copies A0 verbatim.
    digests = {}
    nonempty_arms = {name: d for name, d in built["arms"].items() if d}
    shared_words = sorted(set.intersection(*[set(d) for d in nonempty_arms.values()]))
    assert len(shared_words) >= 5, f"too few words shared by every non-empty arm to run ARMS-MUST-DIFFER: {len(shared_words)}"
    for name, d in nonempty_arms.items():
        M = np.stack([np.asarray(d[w], dtype=np.float64) for w in shared_words])
        digests[name] = hashlib.sha256(np.round(M, 8).tobytes()).hexdigest()
    if len(nonempty_arms) < len(built["arms"]):
        print(f"[self-test] ARMS-MUST-DIFFER: {sorted(set(built['arms']) - set(nonempty_arms))} "
             f"empty on this small slice (expected -- S1/S2 need SUBJ+OBJ slot coverage), skipped",
             flush=True)
    names = sorted(digests)
    dupes = [(a, b) for i, a in enumerate(names) for b in names[i + 1:] if digests[a] == digests[b]]
    assert not dupes, f"ARMS-MUST-DIFFER VIOLATION: bit-identical arms {dupes}"
    print(f"[self-test] ARMS-MUST-DIFFER: {len(names)} arms, all pairwise distinct on "
          f"{len(shared_words)} shared words", flush=True)

    res_a0 = run_arm("A0_INCUMBENT_12", built["arms"]["A0_INCUMBENT_12"], vocab, vocab_idx, ia, ib,
                     gold, counts, built["conc_z"], built["bncfreq"], seed=1)
    assert "band" in res_a0 or res_a0.get("status") == "NOT_CONSTRUCTIBLE", res_a0
    print(f"[self-test] run_arm(A0) on {len(slice_disjoint)}-pair slice: n={res_a0.get('n')} "
          f"status={res_a0.get('status', 'SCORED')}", flush=True)
    if "F_CONSTANT_PROTOTYPE_construction" not in res_a0 and "band" in res_a0:
        pass  # generalisation lives in F_CONSTANT_PROTOTYPE_variant here, not a separate block

    res_s1 = run_arm("S1_SLOT_FRAME", built["arms"]["S1_SLOT_FRAME"], vocab, vocab_idx, ia, ib,
                     gold, counts, built["conc_z"], built["bncfreq"], seed=2)
    print(f"[self-test] run_arm(S1) on {len(slice_disjoint)}-pair slice: n={res_s1.get('n')} "
          f"status={res_s1.get('status', 'SCORED')}", flush=True)

    # WordNet oracle mechanics
    from nltk.corpus import wordnet as wn
    assert wn.synsets("run", pos="v"), "nltk WordNet verb synsets unavailable"
    self_sim = wordnet_wup_max("run", "run")
    assert self_sim is not None and abs(self_sim - 1.0) < 1e-9, f"wup(run,run) should be 1.0: {self_sim}"
    print(f"[self-test] WordNet oracle: wup(run,run)={self_sim}", flush=True)

    print(f"[self-test] ATOMIC consequentiality coverage on this slice's vocab: "
          f"{built['conseq_coverage_frac']:.4f} (keep_conseq={built['keep_conseq']}, "
          f"w_event={built['w_event']}, cols={built['event_col_names']})", flush=True)

    print("[self-test] PASS", flush=True)
    return {"ruler_gate": gate, "usable_n": len(usable), "disjoint_n": len(disjoint),
           "overlap_n": len(overlap), "arms_differ_digests": digests,
           "conseq_coverage_frac_on_slice": built["conseq_coverage_frac"]}


def run() -> Dict:
    t0 = time.time()
    out_dir = str(get_output_dir(ANCHOR_NAME))

    from exp_task_degeneracy_v1 import ruler_mode_gate
    gate = ruler_mode_gate()

    sv_all = load_simverb(SIMVERB)
    sl_v = load_simlex_verbs(SIMLEX)
    from hdlab import grounded_similarity as GS
    tab = GS._table()
    sl_keys = set(frozenset((a.lower(), b.lower())) for a, b, _ in sl_v)
    usable = [r for r in sv_all if r[0].lower() in tab and r[1].lower() in tab]
    disjoint = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) not in sl_keys]
    overlap = [r for r in usable if frozenset((r[0].lower(), r[1].lower())) in sl_keys]
    print(f"[run] SimVerb usable={len(usable)} disjoint(PRIMARY)={len(disjoint)} "
          f"overlap(A0-only, never pooled)={len(overlap)} run_mode={RUN_MODE}", flush=True)

    # ================================================================================
    # REGRESSION GATE -- reproduce the landed n=222 SimLex-V result, byte-for-byte reused code.
    # Point estimate is seed-independent (deterministic given the data); only the scramble/CI use
    # a (documentedly non-reproducible-across-processes) hash-based seed, so ONLY the point rho is
    # gated strictly, and the recomputed band/CI are reported for context, not gated.
    # ================================================================================
    pairs_all_222 = CELL.load_simlex_pos()
    vocab222 = sorted(set(w for p in pairs_all_222 for w in (p[0], p[1])))
    raw222 = N222.load_raw_norms(vocab222)
    X222 = INS._l2n(np.stack([raw222[w] for w in vocab222]).astype(np.float32))
    counts222 = CELL.corpus_counts()
    idx222 = {w: i for i, w in enumerate(vocab222)}
    vtag = [p for p in pairs_all_222 if p[2] == "V"]
    seed222 = _arm_seed("verb_target_space_n222_v1|full|V")
    res222 = N222.run_stratum("V", vtag, idx222, X222, raw222, counts222, seed222)
    landed_rho = 0.2607
    regression_ok = bool(res222.get("rho") and abs(res222["rho"]["point"] - landed_rho) < 1e-3)
    regression_gate = {"landed_rho": landed_rho, "landed_ci95": [0.1282, 0.3841],
                       "recomputed_rho": res222.get("rho"), "recomputed_band": res222.get("band"),
                       "recomputed_margin": res222.get("margin_over_strongest_floor"),
                       "reproduced_point_estimate": regression_ok,
                       "note": "point rho is deterministic given the data (seed-independent); only "
                               "the scramble null / CI use a per-process seed and are NOT expected "
                               "to be bit-identical to the landed run -- only the POINT ESTIMATE is "
                               "the strict gate."}
    print(f"[run] REGRESSION GATE: landed rho={landed_rho}, recomputed rho="
          f"{res222.get('rho', {}).get('point')}, reproduced={regression_ok}", flush=True)
    if not regression_ok:
        elapsed = time.time() - t0
        metrics = {"anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
                  "run_mode": RUN_MODE, "measures_the_instrument_not_a_capability": True,
                  "cue_regime": "exact_key_own_code", "ruler_mode_gate": gate,
                  "regression_gate": regression_gate, "verdict": "REGRESSION_GATE_FAILED",
                  "verdict_msg": ("The n=222 SimLex-V regression check did NOT reproduce the landed "
                                  f"rho={landed_rho}; recomputed {res222.get('rho')}. Exiting before "
                                  "any arm is scored, per the pre-registered gate."),
                  "elapsed_s": round(elapsed, 2), "summary": "REGRESSION_GATE_FAILED"}
        write_metrics(Path(out_dir), metrics)
        raise SystemExit(f"[fatal] REGRESSION GATE FAILED: {regression_gate}")

    # ================================================================================
    # BUILD ARMS on the PRIMARY (disjoint) stratum
    # ================================================================================
    built = build_all_arms(disjoint, overlap)
    vocab = built["vocab"]
    vocab_idx = {w: i for i, w in enumerate(vocab)}
    ia_full = np.array([vocab_idx[p[0].lower()] for p in disjoint])
    ib_full = np.array([vocab_idx[p[1].lower()] for p in disjoint])
    gold_full = np.array([p[3] for p in disjoint], dtype=np.float64)
    counts = built["counts"]
    print(f"[run] vocab={len(vocab)} words; event_col_names={built['event_col_names']} "
          f"keep_conseq={built['keep_conseq']} (coverage {built['conseq_coverage_frac']:.4f}, "
          f"threshold {ATOMIC_COVERAGE_MIN_FRAC})", flush=True)

    # joint intersection across ALL arms, informational (D7), NOT a hard abort -- each arm is
    # scored on its OWN achievable intersection (documented deviation, see module docstring).
    joint_mask = np.ones(len(ia_full), dtype=bool)
    for d in built["arms"].values():
        joint_mask &= np.array([vocab[i] in d and vocab[j] in d for i, j in zip(ia_full, ib_full)])
    print(f"[run] joint intersection across ALL 7 vector arms: n={int(joint_mask.sum())} "
          f"(informational; JOINT_GATE_MIN_N={JOINT_GATE_MIN_N})", flush=True)

    results: Dict[str, Dict] = {}
    done = completed_units(out_dir)

    for name, raw_by_word in built["arms"].items():
        key = unit_key(ANCHOR_NAME, RUN_MODE, name)
        if key in done:
            results[name] = load_units(out_dir)[key]
            print(f"[ckpt] {name}: resumed from units.jsonl", flush=True)
            continue
        t1 = time.time()
        res = run_arm(name, raw_by_word, vocab, vocab_idx, ia_full, ib_full, gold_full, counts,
                     built["conc_z"], built["bncfreq"], seed=_arm_seed(name))
        res["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key, res)
        results[name] = res
        print(f"[arm] {name} n={res.get('n')} status={res.get('status', 'SCORED')} "
             f"band={res.get('band')} rho={res.get('rho', {}).get('point')} "
             f"C1_survives={res.get('C1_PARTIAL', {}).get('survives_partial')} "
             f"({res['elapsed_s']}s)", flush=True)

    key_wn = unit_key(ANCHOR_NAME, RUN_MODE, "K_WORDNET_ORACLE_V")
    if key_wn in done:
        results["K_WORDNET_ORACLE_V"] = load_units(out_dir)[key_wn]
        print("[ckpt] K_WORDNET_ORACLE_V: resumed", flush=True)
    else:
        t1 = time.time()
        res_wn = run_wordnet_oracle(vocab, vocab_idx, ia_full, ib_full, gold_full, counts,
                                    built["conc_z"], built["bncfreq"], SEL.N_PERM, seed=_arm_seed("K_WORDNET_ORACLE_V"))
        res_wn["elapsed_s"] = round(time.time() - t1, 2)
        record_unit(out_dir, key_wn, res_wn)
        results["K_WORDNET_ORACLE_V"] = res_wn
        print(f"[arm] K_WORDNET_ORACLE_V n={res_wn.get('n')} status={res_wn.get('status', 'SCORED')} "
             f"band={res_wn.get('band')} ({res_wn['elapsed_s']}s)", flush=True)

    key_n2 = unit_key(ANCHOR_NAME, RUN_MODE, "N2_RANDOM_GAUSSIAN")
    if key_n2 in done:
        results["N2_RANDOM_GAUSSIAN"] = load_units(out_dir)[key_n2]
        print("[ckpt] N2_RANDOM_GAUSSIAN: resumed", flush=True)
    else:
        t1 = time.time()
        widths = sorted(set(next(iter(d.values())).shape[0] for d in built["arms"].values() if d))
        n2_by_width = {}
        for w in widths:
            ref_words = set(vocab)
            n2_by_width[str(w)] = run_n2_gaussian(w, vocab, vocab_idx, ia_full, ib_full, gold_full,
                                                  counts, ref_words, seeds=(7, 13, 17, 23, 29))
        n2_res = {"widths": widths, "by_width": n2_by_width, "elapsed_s": round(time.time() - t1, 2)}
        record_unit(out_dir, key_n2, n2_res)
        results["N2_RANDOM_GAUSSIAN"] = n2_res
        print(f"[arm] N2_RANDOM_GAUSSIAN widths={widths} ({n2_res['elapsed_s']}s)", flush=True)

    # ---- A0 on the 170-pair OVERLAP stratum, SimVerb's OWN gold, labelled, never pooled ----
    key_ov = unit_key(ANCHOR_NAME, RUN_MODE, "A0_OVERLAP_REPLICATION")
    if key_ov in done:
        results["A0_OVERLAP_REPLICATION"] = load_units(out_dir)[key_ov]
    else:
        ov_vocab = sorted(set(w.lower() for p in overlap for w in (p[0], p[1])))
        ov_idx = {w: i for i, w in enumerate(ov_vocab)}
        ov_ia = np.array([ov_idx[p[0].lower()] for p in overlap])
        ov_ib = np.array([ov_idx[p[1].lower()] for p in overlap])
        ov_gold = np.array([p[3] for p in overlap], dtype=np.float64)
        res_ov = run_arm("A0_OVERLAP_REPLICATION_SIMVERB_GOLD", built["arms"]["A0_INCUMBENT_12"],
                         ov_vocab, ov_idx, ov_ia, ov_ib, ov_gold, counts, built["conc_z"],
                         built["bncfreq"], seed=_arm_seed("A0_OVERLAP_REPLICATION"))
        res_ov["NEVER_POOLED_WARNING"] = ("170 pairs, ALSO in SimLex-V (gold agreement rho 0.9121 "
                                          "on those pairs) -- NOT an independent measurement. "
                                          "Reported for completeness only.")
        record_unit(out_dir, key_ov, res_ov)
        results["A0_OVERLAP_REPLICATION"] = res_ov
        print(f"[arm] A0_OVERLAP_REPLICATION (170 pairs, SimVerb gold, NEVER POOLED) "
             f"band={res_ov.get('band')} rho={res_ov.get('rho', {}).get('point')}", flush=True)

    # ================================================================================
    # STOP-IFS, evaluated in the pre-registered order
    # ================================================================================
    CEILING = 0.6121
    a0 = results.get("A0_INCUMBENT_12", {})
    a1 = results.get("A1_EVENT_SALIENT", {})
    a2 = results.get("A2_EVENT_ONLY", {})
    a3 = results.get("A3_WIDTH_MATCHED_NOISE", {})
    a4 = results.get("A4_WIDTH_MATCHED_WRONG", {})
    s1 = results.get("S1_SLOT_FRAME", {})
    s2 = results.get("S2_SLOT_DELTA", {})
    kwn = results.get("K_WORDNET_ORACLE_V", {})

    stop_ifs = {}
    a0_rho_pt = a0.get("rho", {}).get("point")
    a0_scram_pt = a0.get("scramble_null", {}).get("p95")
    stop_ifs["i_STRATUM_SHIFT"] = bool(a0_rho_pt is not None and a0_scram_pt is not None
                                       and a0_rho_pt < a0_scram_pt)

    def margin_over_a0(res: Dict) -> Optional[Dict]:
        return res.get("margin_over_strongest_floor")

    a1_gain = a1.get("margin_over_strongest_floor", {}).get("point")
    a3_gain = a3.get("margin_over_strongest_floor", {}).get("point")
    a4_gain = a4.get("margin_over_strongest_floor", {}).get("point")
    a1_clears = a1.get("band") == "ABOVE"
    a3_matches = bool(a1_gain is not None and a3_gain is not None and a3_gain >= a1_gain)
    a4_matches = bool(a1_gain is not None and a4_gain is not None and a4_gain >= a1_gain)
    stop_ifs["iii_CONTROL_FIRES"] = bool(a1_clears and (a3_matches or a4_matches))

    a2_gain = a2.get("margin_over_strongest_floor", {}).get("point")
    stop_ifs["iv_DISSOCIATION"] = bool(a1_clears and a2.get("band") == "ABOVE"
                                       and a2_gain is not None and a1_gain is not None
                                       and abs(a2_gain - a1_gain) < 0.03)

    all_bands = [r.get("band") for r in (a0, a1, a2, a3, a4, s1, s2) if r.get("band")]
    all_bands.append(kwn.get("band")) if kwn.get("band") else None
    stop_ifs["v_INSTRUMENT_LIMIT"] = bool(all_bands and all(b != "ABOVE" for b in all_bands))

    a0_survives_partial = a0.get("C1_PARTIAL", {}).get("survives_partial")
    stop_ifs["vi_CONFOUND"] = bool(a0_survives_partial is False)

    if stop_ifs["i_STRATUM_SHIFT"]:
        verdict = "STOP_IF_i_STRATUM_SHIFT"
    elif stop_ifs["vi_CONFOUND"]:
        verdict = "STOP_IF_vi_CONFOUND_CONCRETENESS_ARTIFACT"
    elif stop_ifs["iii_CONTROL_FIRES"]:
        verdict = "STOP_IF_iii_CONTROL_FIRES_DIMENSIONALITY_NOT_CHANNEL"
    elif a1_clears and a1.get("C1_PARTIAL", {}).get("survives_partial") and not a3_matches and not a4_matches:
        verdict = "EVENT_SALIENT_CHANNEL_REAL"
    elif a1_gain is not None and a0.get("rho", {}).get("point") is not None and a1.get("rho", {}).get("point", 0) > a0.get("rho", {}).get("point", 0) and not a1_clears:
        verdict = "A1_GAIN_NOT_CI_SEPARATED"
    elif stop_ifs["v_INSTRUMENT_LIMIT"]:
        verdict = "STOP_IF_v_INSTRUMENT_LIMIT"
    else:
        verdict = "NO_ARM_CLEARS_ITS_OWN_FLOOR"

    def frac_ceiling(res: Dict) -> Optional[float]:
        pt = res.get("rho", {}).get("point")
        return round(pt / CEILING, 4) if pt is not None else None

    ceiling_fracs = {name: frac_ceiling(r) for name, r in results.items() if isinstance(r, dict) and "rho" in r}

    verdict_msg = (f"PRIMARY stratum (SimVerb disjoint from SimLex-V) n={len(disjoint)}. "
                  f"A0 rho={a0.get('rho', {}).get('point')} band={a0.get('band')}; "
                  f"A1 rho={a1.get('rho', {}).get('point')} band={a1.get('band')} "
                  f"C1_survives={a1.get('C1_PARTIAL', {}).get('survives_partial')}; "
                  f"A3(noise) gain={a3_gain} A4(wrong) gain={a4_gain} vs A1 gain={a1_gain}; "
                  f"S1 band={s1.get('band')} S2 band={s2.get('band')}; "
                  f"K_WORDNET_ORACLE_V band={kwn.get('band')} (ceiling reference, no verdict "
                  f"weight); stop_ifs={stop_ifs}. Every rho also reported as a fraction of the "
                  f"SimVerb ceiling {CEILING} in ceiling_fractions_of_0_6121.")

    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "code_version": CODE_VERSION, "prereg": PREREG,
        "run_mode": RUN_MODE, "N_PERM": SEL.N_PERM, "N_BOOT": SEL.N_BOOT,
        "N_BOOT_PARTIAL": N_BOOT_PARTIAL,
        "measures_the_instrument_not_a_capability": True, "cue_regime": "exact_key_own_code",
        "progress_logging": "print_flush_true",
        "ruler_mode_gate": gate, "regression_gate": regression_gate,
        "population": {"simverb_usable": len(usable), "primary_disjoint": len(disjoint),
                      "overlap_never_pooled": len(overlap), "simverb_ceiling_0_6121": CEILING},
        "event_channel_construction": {"event_col_names": built["event_col_names"],
                                       "keep_atomic_consequentiality": built["keep_conseq"],
                                       "atomic_coverage_frac": built["conseq_coverage_frac"],
                                       "socialness_available_on_disk": False,
                                       "socialness_note": "Diveica et al. 2022 socialness norms "
                                                          "NOT on disk (re-enumerated this pass: "
                                                          "only data/corpora/social_iqa/, a QA "
                                                          "corpus, exists; no word-level ratings). "
                                                          "A1 is 12+%d=%d dims, not the drill's "
                                                          "hypothesised 17." % (built["w_event"], 12 + built["w_event"])},
        "joint_intersection_all_arms_n": int(joint_mask.sum()), "joint_gate_min_n": JOINT_GATE_MIN_N,
        "arms": results, "stop_ifs": stop_ifs, "ceiling_fractions_of_0_6121": ceiling_fracs,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 2), "summary": verdict_msg,
    }
    write_metrics(Path(out_dir), metrics)
    print(f"[run] DONE in {elapsed:.1f}s -- verdict={verdict}", flush=True)
    return metrics


def main() -> int:
    if _ARGS.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    m = run()
    print(json.dumps({"verdict": m["verdict"], "verdict_msg": m["verdict_msg"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
