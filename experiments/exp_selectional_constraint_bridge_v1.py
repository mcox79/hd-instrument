"""exp_selectional_constraint_bridge_v1 -- does a held-out word's meaning come from THE VERBS THAT
CONSTRAIN IT, rather than from the words that sit next to it?

PRE-REG: preregs/2026-08-16_selectional_constraint_bridge_v1.md (every threshold fixed there first)
INCUMBENT (imported, never edited): experiments/exp_thematic_relation_supply_bridged_grounding_v2.py
SIBLING LIBRARY (imported, never edited): experiments/exp_bridged_grounding_from_core_v1.py
NEW ASSET: experiments/selectional_preference_extractor_v1.py

WHY. The owner, asked what they take from "the tove ran across the road" (BOARD Q5), answered:
"Since the tove ran - it must be an animal (or at least something that has legs). Since it ran
accross the road, I think of rabbits and deer which I've seen cross roads, and so I assume it's a
smallish animal, most likely a mammel but it could also be a reptile."
THEY NEVER COPIED A NEIGHBOURING WORD. The first inference is the VERB'S SELECTIONAL CONSTRAINT.
Our incumbent bridge copies the code of a co-occurring neighbour and lands
rho 0.0270 [-0.0737,0.1251] against a 0.0900 scramble p95 -- NOT_SEPARATED, 8.2% retention.

BRAIN STRUCTURE: temporo-parietal cortex -- posterior middle temporal gyrus + ANGULAR GYRUS, which
carries EVENT concepts and verb-argument structure and whose activation scales with argument-
structure complexity. PINNED (Schwartz 2011 PNAS; Mirman 2017; J Neurosci 36(16):4405;
Neuropsychologia PMID 30735675). Selectional restriction is a thematic-role phenomenon, so this
cell RIDES the hub the thematic extractor opened; it does not build a third one. The SLOT, the
ESTIMATOR and every gate are OURS -- INVENTION UNDER TEST.

THE ONE VARIABLE: same held-out words, same SimLex pairs, same 12-dim L2-normalised norms cosine,
same gold, same bootstrap seed, same process. Only WHERE THE SOURCE WORDS COME FROM changes:
  I1 (incumbent)  words that CO-OCCUR with w in a sentence
  S1 (treatment)  words that fill THE SAME VERB SLOT as w, anywhere in the corpus

FOUR FLOORS, all recomputed on every stratum: orthographic, hardened-frequency, permutation-
calibrated scramble p95, and CONSTANT/PROTOTYPE (new and mandatory) -- the last is also the exact
control for "you just averaged a lot of words together".

TRAPS RE-EARNED BY RUNTIME EVERY RUN, NEVER INHERITED: grounded_similarity() saturates >70% of
SimLex onto two values and is NEVER the scorer; exp_task_degeneracy_v1.ruler_mode_gate() is CALLED
and hard-fails unless the instrument resolved RUN_MODE=full / V=4096 / CORPUS_BYTES=64,000,000, and
this cell's reduced-grid flag is `--grid reduced` precisely so the token `--smoke` never enters argv
and cannot silently swap the ruler under the frequency floor.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. ASCII-only. CPU. No network.
data/foundation/** is never opened by this cell.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE INSTRUMENT, IMPORTED, NEVER EDITED
import exp_meaning_asset_fair_test_v1 as FT               # verdict machinery, unchanged
import exp_bridged_grounding_from_core_v1 as CELL         # sibling library, NEVER EDITED
import exp_thematic_relation_supply_bridged_grounding_v2 as INC   # INCUMBENT, NEVER EDITED
import thematic_relation_extractor_v1 as THEM
import selectional_preference_extractor_v1 as SEL
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "selectional_constraint_bridge_v1"
CODE_VERSION = "v1.0"
PREREG = "preregs/2026-08-16_selectional_constraint_bridge_v1.md"

# THE FLAG IS `--grid reduced`, NOT `--smoke`, AND THAT IS LOAD-BEARING.
# exp_encoding_quality_instrument_v2 resolves RUN_MODE FROM argv AT IMPORT: the bare token
# "--smoke" anywhere in argv silently drops the ruler to V=512 and shrinks CORPUS_BYTES, which
# would silently recompute this cell's FREQUENCY FLOOR on a different corpus budget with no error
# and no warning. exp_task_degeneracy_v1.ruler_mode_gate() exists for exactly this and is CALLED
# in selftest() below. (Correction of record: an earlier pass in this session asserted no such gate
# existed on disk, on the strength of `ls tools/` plus a grep of four candidate files. That was an
# absence claim from a search rather than an enumeration, and it was wrong -- the gate is at
# experiments/exp_task_degeneracy_v1.py:121.)
_ap = argparse.ArgumentParser()
_ap.add_argument("--grid", choices=("full", "reduced"), default="full")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = _ARGS.grid == "reduced"
RUN_MODE = "reduced" if SMOKE else "full"

# ---- PRE-REGISTERED CONSTANTS (prereg section 6). NEVER EDITED AFTER A RUN. -----------------
AOA_CORE_MAX = CELL.AOA_CORE_MAX          # 6.0
SLOT_MIN_FILLERS = 3
WSLOT_MIN_COUNT = 2
SLOT_TOPK = 12
FILLER_TOPK = 50
T_MARGIN_MIN = FT.T_MARGIN_MIN            # 0.05
N_BOOT = 2000 if SMOKE else 10000
N_PERM = 400 if SMOKE else 2000
NULL_SEEDS = (7, 13, 17, 23, 29)
BOOT_SEED = 20260816
POS_MIN_N = CELL.POS_MIN_N                # 25
HUB_INDEGREE_MAX = CELL.HUB_INDEGREE_MAX  # 10
ORTHO_DIMS = CELL.ORTHO_DIMS
MIDDLE_BAND_FRAC = CELL.MIDDLE_BAND_FRAC
JACCARD_DEGENERATE = 0.5

FLOOR_ORTHO = "F_ORTHOGRAPHIC"
FLOOR_FREQ = "F_FREQUENCY_HARDENED"
FLOOR_SCRAM = "F_SCRAMBLE_PERM_P95"
FLOOR_CONST = "F_CONSTANT_PROTOTYPE"
FLOOR_KEYS = (FLOOR_ORTHO, FLOOR_FREQ, FLOOR_SCRAM, FLOOR_CONST)

SEL_ARMS = ("S1_SELECTIONAL_MEAN", "S2_SELECTIONAL_PMI", "S3_SELECTIONAL_NOCOOC",
            "S4_SELECTIONAL_SUBJ_ONLY", "S5_SELECTIONAL_CORE_ROLES")
PRIMARY_ARM = "S1_SELECTIONAL_MEAN"
DECISIVE_CONTROL_ARM = "S3_SELECTIONAL_NOCOOC"
INCUMBENT_ARM = "I1_NEIGHBOUR_COPY_INCUMBENT"
NULL_TAGS = ("N1_NULL_SLOT_REWIRE", "N2_NULL_RANDOM_TARGET")

# _ORTHO_CACHE is keyed on (dimension, VOCABULARY), never on the dimension alone. Keying on the
# dimension alone made the cache return the FIRST vocabulary's code table to every later caller:
# selftest() runs build_floors on a ~60-word fixture BEFORE the real run, so the real ~1000-word
# stratum got back a 60-row matrix and pair_cos indexed off the end within seconds. A per-stratum
# floor table is per-stratum-vocabulary by definition.
_ORTHO_CACHE: Dict[Tuple[int, int, str], np.ndarray] = {}


def _arm_seed(name: str) -> int:
    """DETERMINISTIC per-arm seed. Python's builtin hash() of a str is randomised per process
    unless PYTHONHASHSEED is pinned, so hash(arm) would give a DIFFERENT scramble null on a
    resumed run than on the original -- a silent non-reproducibility, and this cell is
    checkpointed and therefore WILL be resumed."""
    return int.from_bytes(hashlib.sha256(name.encode("ascii")).digest()[:4], "big") % 100000


# ==========================================================================================
# THE SELECTIONAL MECHANISM -- the one genuinely new component
# ==========================================================================================
class SelectionalSource:
    """Turns the raw slot tables into, for each held-out word, the set of (slot, fillers) that
    CONSTRAIN it. The fillers are the verb's OTHER arguments corpus-wide; the sentence w actually
    occurred in never contributes a source word. That is the whole difference from neighbour-copy.
    """

    def __init__(self, slots: Dict, br: "CELL.Bridger", sources: Set[str]):
        self.sf: Dict[Tuple[str, str], Dict[str, int]] = slots["slot_filler"]
        self.cooc: Dict[str, Dict[str, int]] = slots["word_cooc"]
        self.br = br
        self.sources = sources
        self.slot_total: Dict[Tuple[str, str], int] = {s: sum(v.values())
                                                       for s, v in self.sf.items()}
        self.N = float(sum(self.slot_total.values()))
        self.word_total: collections.Counter = collections.Counter()
        self.word_slots: Dict[str, List[Tuple[Tuple[str, str], int]]] = collections.defaultdict(list)
        for s, fill in self.sf.items():
            for w, c in fill.items():
                self.word_total[w] += c
                if c >= WSLOT_MIN_COUNT:
                    self.word_slots[w].append((s, c))
        # top fillers per slot, precomputed once, deterministic
        self.top_fillers: Dict[Tuple[str, str], List[Tuple[str, int]]] = {
            s: sorted(v.items(), key=lambda kv: (-kv[1], kv[0]))[:FILLER_TOPK]
            for s, v in self.sf.items()}
        self._size_decile: Optional[Dict[Tuple[str, str], int]] = None
        self._by_dec: Optional[Dict[int, List[Tuple[str, str]]]] = None
        self._slots_cache: Dict[Tuple, List] = {}

    def pmi(self, w: str, s: Tuple[str, str], c: int) -> float:
        pw = self.word_total.get(w, 0)
        ps = self.slot_total.get(s, 0)
        if pw <= 0 or ps <= 0 or self.N <= 0:
            return 0.0
        return math.log((c * self.N) / (pw * ps), 2.0)

    def slot_fillers_for(self, w: str, s: Tuple[str, str], morph_block: bool,
                         drop_cooc: bool) -> List[Tuple[str, int]]:
        """The ELIGIBLE CORE fillers of slot s, from w's point of view.

        Eligibility is the sibling cell's own rule (never self, never held-out, never w's SimLex
        partner, must be a CORE source with a hidden code). `drop_cooc` additionally deletes every
        filler that EVER shares a sentence with w -- the decisive control that separates a verb
        CONSTRAINT from lexical ASSOCIATION.
        """
        co = self.cooc.get(w) if drop_cooc else None
        out = []
        for f, c in self.top_fillers.get(s, ()):
            if not self.br.eligible(w, f, self.sources, morph_block):
                continue
            if co is not None and f in co:
                continue
            out.append((f, c))
        return out

    def slots_for(self, w: str, roles: Optional[Set[str]], morph_block: bool,
                  drop_cooc: bool) -> List[Tuple[Tuple[str, str], float, List[Tuple[str, int]]]]:
        """-> [(slot, pmi_weight, eligible_fillers)] capped at SLOT_TOPK, deterministic order.

        MEMOISED. Not an optimisation detail: this is called once per supply statistic, once per
        distinctness witness, once per additive form, once per null seed and once per episodic
        arm, and it rescans every slot the word occurs in. Without the cache the run is O(10^8)
        eligibility checks. The cache is keyed on every argument that changes the answer.
        """
        ck = (w, tuple(sorted(roles)) if roles else None, morph_block, drop_cooc)
        hit = self._slots_cache.get(ck)
        if hit is not None:
            return hit
        cand = []
        for s, c in self.word_slots.get(w, ()):
            if roles is not None:
                role = s[1]
                if role not in roles and not (("obl" in roles) and role.startswith("obl:")):
                    continue
            fl = self.slot_fillers_for(w, s, morph_block, drop_cooc)
            if len(fl) < SLOT_MIN_FILLERS:
                continue
            cand.append((s, self.pmi(w, s, c), fl, c))
        cand.sort(key=lambda t: (-t[1], -t[3], t[0]))
        out = [(s, p, fl) for s, p, fl, _ in cand[:SLOT_TOPK]]
        self._slots_cache[ck] = out
        return out

    @staticmethod
    def slot_pref(hidden: Dict[str, np.ndarray], fl: Sequence[Tuple[str, int]]) -> np.ndarray:
        """THE SELECTIONAL RESTRICTION, estimated: count-weighted mean grounded code of the slot's
        eligible fillers. OURS -- INVENTION UNDER TEST."""
        M = np.stack([hidden[f] for f, _ in fl]).astype(np.float64)
        w = np.array([c for _, c in fl], dtype=np.float64)
        return (M * w[:, None]).sum(axis=0) / w.sum()

    def code(self, w: str, form: str, morph_block: bool = False) -> Optional[np.ndarray]:
        roles = None
        drop_cooc = False
        if form == "S3_SELECTIONAL_NOCOOC":
            drop_cooc = True
        elif form == "S4_SELECTIONAL_SUBJ_ONLY":
            roles = {"SUBJ"}
        elif form == "S5_SELECTIONAL_CORE_ROLES":
            roles = {"SUBJ", "OBJ", "IOBJ"}
        sl = self.slots_for(w, roles, morph_block, drop_cooc)
        if not sl:
            return None
        P = np.stack([self.slot_pref(self.br.hidden, fl) for _, _, fl in sl])
        if form == "S2_SELECTIONAL_PMI":
            wt = np.array([max(p, 0.0) for _, p, _ in sl], dtype=np.float64)
            if wt.sum() > 0:
                return (P * wt[:, None]).sum(axis=0) / wt.sum()
        return P.mean(axis=0)

    def episodic_conjunctive(self, w: str, morph_block: bool = False) -> Optional[np.ndarray]:
        """OWNER MECHANISM 2, APPROXIMATED AND LABELLED AS SUCH.

        "rabbits and deer which I've SEEN cross roads" is retrieval of a whole remembered SITUATION.
        We do not store episodes, so this is the nearest thing the slot tables support: CORE words
        that fill AT LEAST TWO of w's slots -- i.e. that match the PATTERN as a conjunction rather
        than each slot independently. It is NOT episodic memory and must never be reported as such.
        """
        sl = self.slots_for(w, None, morph_block, False)
        if len(sl) < 2:
            return None
        hits: collections.Counter = collections.Counter()
        for _, _, fl in sl:
            for f, _c in fl:
                hits[f] += 1
        keep = [(f, k) for f, k in hits.items() if k >= 2]
        if not keep:
            return None
        M = np.stack([self.br.hidden[f] for f, _ in keep]).astype(np.float64)
        wt = np.array([k for _, k in keep], dtype=np.float64)
        return (M * wt[:, None]).sum(axis=0) / wt.sum()

    def source_words(self, w: str) -> Set[str]:
        return {f for _, _, fl in self.slots_for(w, None, False, False) for f, _ in fl}

    def size_decile(self) -> Dict[Tuple[str, str], int]:
        if self._size_decile is None:
            keys = sorted(self.sf)
            sizes = np.array([len(self.sf[k]) for k in keys], dtype=np.float64)
            cuts = np.percentile(sizes, np.arange(10, 100, 10))
            self._size_decile = {k: int(d) for k, d in zip(keys, np.digitize(sizes, cuts))}
        return self._size_decile

    def null_rewire(self, w: str, seed: int) -> Optional[np.ndarray]:
        """NULL N1 -- keep the ESTIMATOR, destroy WHICH VERB constrains w. Each of w's slots is
        replaced by a random slot of the same filler-count decile."""
        sl = self.slots_for(w, None, False, False)
        if not sl:
            return None
        dec = self.size_decile()
        if self._by_dec is None:                 # hoisted: rebuilding this per word per seed
            bd: Dict[int, List[Tuple[str, str]]] = collections.defaultdict(list)
            for k, d in dec.items():             # scans every slot, and there are ~10^5 of them
                bd[d].append(k)
            self._by_dec = {k: sorted(v) for k, v in bd.items()}
        by_dec = self._by_dec
        rng = np.random.default_rng(seed ^ (int.from_bytes(w.encode("utf-8")[:6], "big")
                                            % (2 ** 31)))
        prefs = []
        for s, _, _ in sl:
            pool = by_dec.get(dec.get(s, 0)) or sorted(self.sf)
            for _ in range(64):
                s2 = pool[int(rng.integers(len(pool)))]
                fl = self.slot_fillers_for(w, s2, False, False)
                if len(fl) >= SLOT_MIN_FILLERS:
                    prefs.append(self.slot_pref(self.br.hidden, fl))
                    break
        if not prefs:
            return None
        return np.stack(prefs).mean(axis=0)

    def filler_distribution(self, w: str) -> Optional[Tuple[List[str], np.ndarray]]:
        """OWNER MECHANISM 3 -- the DISTRIBUTION over candidate fillers with its weights, not a
        point code. Returns (filler_words, probabilities)."""
        sl = self.slots_for(w, None, False, False)
        if not sl:
            return None
        acc: collections.Counter = collections.Counter()
        for _, _, fl in sl:
            tot = float(sum(c for _, c in fl))
            for f, c in fl:
                acc[f] += c / tot
        items = sorted(acc.items(), key=lambda kv: (-kv[1], kv[0]))
        words = [f for f, _ in items]
        p = np.array([v for _, v in items], dtype=np.float64)
        return words, p / p.sum()


# ==========================================================================================
# floors -- FOUR, all recomputed on every stratum
# ==========================================================================================
def _ortho_codes(vocab: List[str], d: int) -> np.ndarray:
    key = (d, len(vocab),
           hashlib.sha256("\n".join(vocab).encode("utf-8")).hexdigest())
    X = _ORTHO_CACHE.get(key)
    if X is None:
        X = INS._l2n(INS.enc_orthographic(vocab, d, 7))
        _ORTHO_CACHE[key] = X
    return X


def build_floors(vocab: List[str], ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                 counts: Dict[str, int], const_cos: Optional[np.ndarray]) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    best = None
    per_d = {}
    for d in ORTHO_DIMS:
        c = CELL.pair_cos(_ortho_codes(vocab, d), ia, ib)
        r = INS._spearman(c, gold)
        per_d[f"d{d}"] = float(r)
        if best is None or r > best[0]:
            best = (r, c, d)
    out[FLOOR_ORTHO] = {"rho": float(best[0]), "per_dim": per_d, "argmax_d": int(best[2]),
                        "_partner": best[1],
                        "what_it_is": "SPELLING CHOOSES THE CODE"}
    lf = np.array([np.log(counts.get(w, 0) + 1.0) for w in vocab], dtype=np.float64)
    la, lb = lf[ia], lf[ib]
    ch = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
          "FREQ_MIN": np.minimum(la, lb),
          "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    rh = {k: float(INS._spearman(v, gold)) for k, v in ch.items()}
    bk = max(rh, key=lambda k: rh[k])
    out[FLOOR_FREQ] = {"rho": rh[bk], "per_channel": rh, "argmax_channel": bk, "_partner": ch[bk]}
    if const_cos is not None:
        out[FLOOR_CONST] = {
            "rho": float(INS._spearman(const_cos, gold)), "_partner": const_cos,
            "what_it_is": "EVERY BRIDGED WORD GETS THE SAME CODE (the mean of all eligible CORE "
                          "codes), so the bridged endpoint carries ZERO information about the "
                          "query. Pair-similarity analogue of tools/floor_battery."
                          "constant_prototype_floor. THE CONSTRUCTION is carried across, THE "
                          "NUMBER IS NOT -- that instrument's 0.1390/0.1518 has no meaning here."}
    return out


def scramble_floor(X: np.ndarray, ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                   seed: int) -> Dict:
    n = X.shape[0]
    rhos = np.empty(N_PERM)
    for i in range(N_PERM):
        p = np.random.default_rng(seed + i).permutation(n)
        rhos[i] = INS._spearman(CELL.pair_cos(X[p], ia, ib), gold)
    rhos = rhos[np.isfinite(rhos)]
    p95_row = float(np.percentile(rhos, 95))
    obs = CELL.pair_cos(X, ia, ib)
    g_rng = np.random.default_rng(seed ^ 0xBEEF)
    gn = np.array([INS._spearman(obs, gold[g_rng.permutation(len(gold))]) for _ in range(N_PERM)])
    gn = gn[np.isfinite(gn)]
    p95_gold = float(np.percentile(gn, 95))
    p95 = max(p95_row, p95_gold)
    near_i = int(np.argmin(np.abs(rhos - p95)))
    near = CELL.pair_cos(X[np.random.default_rng(seed + near_i).permutation(n)], ia, ib)
    return {"p95": p95, "p95_row_permutation": p95_row, "p95_gold_permutation": p95_gold,
            "row_null_mean": float(rhos.mean()), "row_null_sd": float(rhos.std(ddof=1)),
            "n_perm": int(len(rhos)),
            "permutation_p_value": float((np.sum(rhos >= INS._spearman(obs, gold)) + 1)
                                         / (len(rhos) + 1)),
            "_partner": near}


def _score_cos(name: str, obs: np.ndarray, X: Optional[np.ndarray], ia: np.ndarray,
               ib: np.ndarray, gold: np.ndarray, floors: Dict[str, Dict], seed: int,
               light: bool = False) -> Dict:
    if light or X is None:
        return {"arm": name, "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
                "scoring": "LIGHT (rho only; not a verdict-bearing arm)", "_cos": obs}
    sc = scramble_floor(X, ia, ib, gold, seed)
    cands = {k: (floors[k]["rho"], floors[k]["_partner"]) for k in floors}
    cands[FLOOR_SCRAM] = (sc["p95"], sc["_partner"])
    bf = max(cands, key=lambda k: cands[k][0])
    diff = FT.boot_rho_diff(obs, cands[bf][1], gold, n_boot=N_BOOT, seed=BOOT_SEED)
    b = FT.band(diff["ci95"])
    per_floor = {}
    for k, (r, p) in cands.items():
        dd = FT.boot_rho_diff(obs, p, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        per_floor[k] = {"floor_rho": float(r), "margin": dd, "band": FT.band(dd["ci95"])}
    min_ci_lo = min(per_floor[k]["margin"]["ci95"][0] for k in per_floor)
    clears = bool(b == "ABOVE" and diff["point"] >= T_MARGIN_MIN)
    middle = bool(clears and (diff["point"] - T_MARGIN_MIN)
                  < MIDDLE_BAND_FRAC * max(abs(diff["ci95"][1] - diff["ci95"][0]), 1e-12))
    return {"arm": name, "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
            "strongest_floor": bf, "floor_rho_by_arm": {k: round(v[0], 4) for k, v in cands.items()},
            "margin_over_strongest_floor": diff, "band": b, "clears_floor": clears,
            "clears_ALL_FOUR_floors_ci_separated": bool(clears and min_ci_lo > 0.0),
            "min_ci_lo_over_all_floors": float(min_ci_lo), "middle_band": middle,
            "scramble_null": {k: v for k, v in sc.items() if not k.startswith("_")},
            "DECOMPOSED_per_floor": per_floor, "_cos": obs}


def _pos_stratified(cos: np.ndarray, gold: np.ndarray, pos_of: np.ndarray, vocab: List[str],
                    ia: np.ndarray, ib: np.ndarray, counts: Dict[str, int], seed: int,
                    X: np.ndarray, const_cos: np.ndarray) -> Dict:
    out: Dict[str, Dict] = {}
    for tag in ("N", "V", "A"):
        m = pos_of == tag
        k = int(m.sum())
        if k < POS_MIN_N:
            out[tag] = {"n": k, "status": "NOT_CONSTRUCTIBLE",
                        "rule": f"n < POS_MIN_N={POS_MIN_N}; NOT a null and NOT a passed falsifier"}
            continue
        fl = build_floors(vocab, ia[m], ib[m], gold[m], counts, const_cos[m])
        sc = scramble_floor(X, ia[m], ib[m], gold[m], seed + 101)
        cands = {kk: (fl[kk]["rho"], fl[kk]["_partner"]) for kk in fl}
        cands[FLOOR_SCRAM] = (sc["p95"], sc["_partner"])
        bf = max(cands, key=lambda kk: cands[kk][0])
        dd = FT.boot_rho_diff(cos[m], cands[bf][1], gold[m], n_boot=N_BOOT, seed=BOOT_SEED)
        out[tag] = {"n": k, "rho": FT.boot_rho(cos[m], gold[m], n_boot=N_BOOT, seed=BOOT_SEED),
                    "strongest_floor": bf,
                    "floor_rho_by_arm": {kk: round(v[0], 4) for kk, v in cands.items()},
                    "margin_over_strongest_floor": dd, "band": FT.band(dd["ci95"]),
                    "clears_floor": bool(FT.band(dd["ci95"]) == "ABOVE"
                                         and dd["point"] >= T_MARGIN_MIN)}
    return out


# ==========================================================================================
def run_config(cfg: str, ctx: Dict, *, morph_block: bool = False, do_pos: bool = False,
               restrict_words: Optional[Set[str]] = None,
               which: str = "COMMON") -> Dict:
    t0 = time.time()
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out, partners = ctx["idx"], ctx["held_out"], ctx["partners"]
    counts, core = ctx["counts"], ctx["core"]
    br: CELL.Bridger = ctx["br"]
    S: SelectionalSource = ctx["sel"]
    graph = ctx["enriched"]

    sel_words = ctx["sel_words"]
    inc_words = ctx["inc_words"]
    if which == "COMMON":
        words = sorted(sel_words & inc_words)
    elif which == "SEL_OWN":
        words = sorted(sel_words)
    elif which == "INC_OWN":
        words = sorted(inc_words)
    else:
        raise ValueError(which)
    if restrict_words is not None:
        words = [w for w in words if w in restrict_words]

    Sset = set(words)
    strat = [p for p in pairs if (p[0] in Sset) != (p[1] in Sset)]
    n = len(strat)
    res: Dict = {"config": cfg, "which_words": which, "morph_block": morph_block,
                 "n_bridged_words": len(words), "n_stratum": n,
                 "pos_counts": dict(collections.Counter(p[2] for p in strat)),
                 "spearman_ci_halfwidth_approx": (round(1.96 / max(n - 3, 1) ** 0.5, 4)
                                                  if n > 3 else None)}
    if n < 10:
        res["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        res["elapsed_s"] = round(time.time() - t0, 1)
        return res

    ia = np.array([idx[p[0]] for p in strat])
    ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    pos_of = np.array([p[2] for p in strat])

    # ---- supply statistics (reported whatever the verdict)
    slot_stats = []
    for w in words:
        sl = S.slots_for(w, None, morph_block, False)
        slot_stats.append((len(sl), sum(len(fl) for _, _, fl in sl)))
    if slot_stats:
        ns = np.array([a for a, _ in slot_stats]); nf = np.array([b for _, b in slot_stats])
        res["selectional_supply"] = {
            "slots_per_word_mean": round(float(ns.mean()), 3),
            "slots_per_word_median": int(np.median(ns)),
            "fillers_per_word_mean": round(float(nf.mean()), 2),
            "fillers_per_word_median": int(np.median(nf)),
            "frac_words_with_ge2_slots": round(float((ns >= 2).mean()), 4)}
    inc_deg = [len(br.neighbours(w, graph, core, morph_block)) for w in words]
    if inc_deg:
        res["incumbent_bridge_degree"] = {"mean": round(float(np.mean(inc_deg)), 3),
                                          "median": int(np.median(inc_deg))}

    # ---- MECHANISM-DISTINCTNESS WITNESS (prereg section 3) -- read BEFORE any number
    jac = []
    for w in words:
        a = S.source_words(w)
        b = {nb for nb, _ in br.neighbours(w, graph, core, morph_block)}
        u = a | b
        jac.append(len(a & b) / len(u) if u else 0.0)
    res["MECHANISM_DISTINCTNESS"] = {
        "mean_jaccard_source_overlap": round(float(np.mean(jac)), 4) if jac else None,
        "median_jaccard": round(float(np.median(jac)), 4) if jac else None,
        "frac_words_with_zero_overlap": round(float(np.mean(np.array(jac) == 0.0)), 4) if jac else None,
        "DEGENERATE_if_mean_gt": JACCARD_DEGENERATE,
        "DEGENERATE": bool(jac and float(np.mean(jac)) > JACCARD_DEGENERATE)}

    # ---- the CONSTANT/PROTOTYPE floor's code table (built before any arm is scored)
    core_src = sorted(w for w in core if w in raw and w not in held_out)
    proto = np.stack([raw[c] for c in core_src]).astype(np.float64).mean(axis=0)
    X_const = CELL.code_matrix(vocab, raw, {w: proto for w in words})
    const_cos = CELL.pair_cos(X_const, ia, ib)

    floors = build_floors(vocab, ia, ib, gold, counts, const_cos)
    res["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}

    CM = INS._l2n(np.stack([raw[w] for w in core_src]).astype(np.float32))

    def oracle_nbrs(w: str, k: int) -> List[Tuple[str, float]]:
        v = INS._l2n(raw[w][None, :].astype(np.float32))[0]
        s = CM @ v
        out = []
        for j in np.argsort(-s):
            cw = core_src[j]
            if cw == w or cw in partners.get(w, ()):
                continue
            out.append((cw, float(s[j])))
            if len(out) >= k:
                break
        return out

    # ---- arms -------------------------------------------------------------------------
    arms: Dict[str, Dict[str, np.ndarray]] = {"K1_OWN_NORMS": {}}
    arms["K2_ORACLE_BRIDGE"] = {w: br.mean_code(oracle_nbrs(w, 1), False) for w in words}
    arms["K2b_ORACLE_BRIDGE_MEAN3"] = {w: br.mean_code(oracle_nbrs(w, 3), False) for w in words}
    for form in SEL_ARMS:
        tbl = {}
        for w in words:
            v = S.code(w, form, morph_block)
            if v is not None:
                tbl[w] = v
        arms[form] = tbl
    tbl = {}
    for w in words:
        v = S.episodic_conjunctive(w, morph_block)
        if v is not None:
            tbl[w] = v
    arms["E1_EPISODIC_CONJUNCTIVE"] = tbl
    tbl = {}
    for w in words:
        nb = br.neighbours(w, graph, core, morph_block)
        if nb:
            tbl[w] = br.mean_code(nb, False)
    arms[INCUMBENT_ARM] = tbl
    for s in NULL_SEEDS:
        t1 = {}
        for w in words:
            v = S.null_rewire(w, s)
            if v is not None:
                t1[w] = v
        arms[f"N1_NULL_SLOT_REWIRE|s{s}"] = t1
        rng = np.random.default_rng(s ^ 0x51F7)
        t2 = {}
        for w in words:
            for _ in range(64):
                c2 = core_src[int(rng.integers(len(core_src)))]
                if br.eligible(w, c2, core, False):
                    t2[w] = br.hidden[c2].astype(np.float64)
                    break
        arms[f"N2_NULL_RANDOM_TARGET|s{s}"] = t2

    # ---- G3 arms-must-differ
    k1 = CELL.code_matrix(vocab, raw, {})
    g3 = []
    for a in sorted(arms):
        if a == "K1_OWN_NORMS" or not arms[a]:
            continue
        g3.append({"arm": a,
                   "differs_from_K1": bool(not np.allclose(CELL.code_matrix(vocab, raw, arms[a]),
                                                           k1))})
    s1x = CELL.code_matrix(vocab, raw, arms[PRIMARY_ARM]) if arms.get(PRIMARY_ARM) else None
    i1x = CELL.code_matrix(vocab, raw, arms[INCUMBENT_ARM]) if arms.get(INCUMBENT_ARM) else None
    res["G3_arms_must_differ"] = g3
    res["G3_S1_differs_from_I1"] = bool(s1x is not None and i1x is not None
                                        and not np.allclose(s1x, i1x))
    res["G3_passed"] = bool(g3 and all(g["differs_from_K1"] for g in g3)
                            and res["G3_S1_differs_from_I1"])

    # ---- score
    rows: Dict[str, Dict] = {}
    cos_by_arm: Dict[str, np.ndarray] = {}
    verdict_arms = set(SEL_ARMS) | {"K1_OWN_NORMS", "K2_ORACLE_BRIDGE", "K2b_ORACLE_BRIDGE_MEAN3",
                                    INCUMBENT_ARM, "E1_EPISODIC_CONJUNCTIVE"}
    for a in sorted(arms):
        if not arms[a] and a != "K1_OWN_NORMS":
            rows[a] = {"arm": a, "status": "EMPTY_NO_WORDS_REACHED"}
            continue
        X = CELL.code_matrix(vocab, raw, arms[a])
        light = a not in verdict_arms
        r = _score_cos(a, CELL.pair_cos(X, ia, ib), None if light else X, ia, ib, gold, floors,
                       seed=_arm_seed(a), light=light)
        cos_by_arm[a] = r.pop("_cos")
        r["n_words_reached"] = len(arms[a]) if a != "K1_OWN_NORMS" else len(words)
        rows[a] = r
        if do_pos and a in ("K1_OWN_NORMS", PRIMARY_ARM, INCUMBENT_ARM,
                            DECISIVE_CONTROL_ARM):
            rows[a]["POS_STRATIFIED"] = _pos_stratified(cos_by_arm[a], gold, pos_of, vocab, ia, ib,
                                                        counts, _arm_seed(a), X, const_cos)

    # null floors = MAX DRAW, never the mean
    for tag in NULL_TAGS:
        draws = {k: rows[k]["rho"]["point"] for k in rows
                 if k.startswith(tag) and "rho" in rows[k]}
        if not draws:
            continue
        mk = max(draws, key=lambda k: draws[k])
        res[f"{tag}_FLOOR"] = {"seeds": sorted(draws), "rho_by_seed": draws,
                               "max_draw_seed": mk, "rho_max_draw": draws[mk],
                               "rho_mean": float(np.mean(list(draws.values()))),
                               "policy": "MAX DRAW never the mean"}
        for a in (PRIMARY_ARM, DECISIVE_CONTROL_ARM, INCUMBENT_ARM):
            if a in cos_by_arm and mk in cos_by_arm:
                d = FT.boot_rho_diff(cos_by_arm[a], cos_by_arm[mk], gold, n_boot=N_BOOT,
                                     seed=BOOT_SEED)
                res.setdefault("VS_NULL", {})[f"{a}_vs_{tag}"] = {
                    "margin": d, "band": FT.band(d["ci95"])}

    # ---- THE HEAD-TO-HEAD the brief asks for, identical stratum / scorer / n / pool / gold
    if PRIMARY_ARM in cos_by_arm and INCUMBENT_ARM in cos_by_arm:
        d = FT.boot_rho_diff(cos_by_arm[PRIMARY_ARM], cos_by_arm[INCUMBENT_ARM], gold,
                             n_boot=N_BOOT, seed=BOOT_SEED)
        res["HEAD_TO_HEAD_S1_minus_I1"] = {
            "margin": d, "band": FT.band(d["ci95"]),
            "scorer": "SimLex Spearman rho on 12-dim L2-normalised norms cosine",
            "n": n, "note": "paired over the SAME pairs; both arms computed in this process"}
    for a in SEL_ARMS + ("E1_EPISODIC_CONJUNCTIVE",):
        if a in cos_by_arm and INCUMBENT_ARM in cos_by_arm:
            d = FT.boot_rho_diff(cos_by_arm[a], cos_by_arm[INCUMBENT_ARM], gold, n_boot=N_BOOT,
                                 seed=BOOT_SEED)
            res.setdefault("VS_INCUMBENT", {})[a] = {"margin": d, "band": FT.band(d["ci95"])}

    # ---- retention + identity, reported whatever the verdict, never averaged together
    if "K1_OWN_NORMS" in rows and PRIMARY_ARM in rows and "rho" in rows[PRIMARY_ARM]:
        rk = rows["K1_OWN_NORMS"]["rho"]["point"]
        ra = rows[PRIMARY_ARM]["rho"]["point"]
        d = FT.boot_rho_diff(cos_by_arm[PRIMARY_ARM], cos_by_arm["K1_OWN_NORMS"], gold,
                             n_boot=N_BOOT, seed=BOOT_SEED)
        res["RETENTION"] = {"rho_arm": ra, "rho_K1": rk,
                            "retention_fraction": (ra / rk) if rk else None,
                            "incumbent_landed_retention_for_reference": 0.0819,
                            "paired_difference": d, "band": FT.band(d["ci95"])}
    if arms.get(PRIMARY_ARM):
        M = np.stack([arms[PRIMARY_ARM][w] for w in sorted(arms[PRIMARY_ARM])])
        Mn = INS._l2n(M.astype(np.float32))
        G = Mn @ Mn.T
        iu = np.triu_indices(len(Mn), 1)
        res["IDENTITY_AXIS_never_averaged_with_structure"] = {
            "n_bridged": int(len(Mn)),
            "n_distinct_codes": int(len(set(np.round(M, 9).tobytes()[i:i + 8]
                                            for i in range(0, 0)) ) or len(
                {np.round(v, 9).tobytes() for v in M})),
            "distinct_fraction": round(len({np.round(v, 9).tobytes() for v in M}) / len(M), 4),
            "mean_pairwise_cosine": round(float(G[iu].mean()), 4),
            "frac_pairs_cos_above_0.99": round(float((G[iu] > 0.99).mean()), 5)}

    # ---- G0 POWER GATE, read before any treatment number is interpreted
    k1r = rows.get("K1_OWN_NORMS", {})
    res["G0_POWER_GATE"] = {
        "K1_rho": k1r.get("rho", {}).get("point"),
        "K1_strongest_floor": k1r.get("strongest_floor"),
        "K1_margin": k1r.get("margin_over_strongest_floor", {}).get("point"),
        "K1_band": k1r.get("band"),
        "PASSED": bool(k1r.get("band") == "ABOVE"),
        "rule": "if K1 does not clear THIS stratum's own max(4 floors) CI-separated, every arm on "
                "this stratum is POWER_INSUFFICIENT, NEVER FAIL"}

    res["arms"] = rows
    res["elapsed_s"] = round(time.time() - t0, 1)
    return res


# ==========================================================================================
# OWNER MECHANISM 3 -- distribution over categories with explicit uncertainty
# ==========================================================================================
def run_distributional(ctx: Dict) -> Dict:
    """SEPARATE BLOCK, its own floors. It changes the READOUT, not the code: the pair score is
    E_{f~P(f|w)}[cos(code(f), code(partner))] instead of cos(mean_f code(f), code(partner)).
    Reported separately so it cannot contaminate the primary."""
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, counts, core = ctx["idx"], ctx["counts"], ctx["core"]
    br: CELL.Bridger = ctx["br"]
    S: SelectionalSource = ctx["sel"]
    words = sorted(ctx["sel_words"] & ctx["inc_words"])
    Sset = set(words)
    strat = [p for p in pairs if (p[0] in Sset) != (p[1] in Sset)]
    if len(strat) < 10:
        return {"status": "STRATUM_TOO_SMALL"}
    ia = np.array([idx[p[0]] for p in strat]); ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)

    dist: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    unc = []
    for w in words:
        fd = S.filler_distribution(w)
        if fd is None:
            continue
        fw, p = fd
        M = INS._l2n(np.stack([br.hidden[f] for f in fw]).astype(np.float32))
        dist[w] = (M, p)
        ent = float(-(p * np.log(np.maximum(p, 1e-12))).sum())
        G = M @ M.T
        iu = np.triu_indices(len(M), 1)
        unc.append((ent, float(G[iu].mean()) if len(iu[0]) else 1.0))

    Xn = CELL.code_matrix(vocab, raw, {})   # everything at its own code; bridged rows overridden
    obs = np.empty(len(strat))
    for j, p4 in enumerate(strat):
        a, b = p4[0], p4[1]
        w, other = (a, b) if a in dist else (b, a)
        if w not in dist:
            obs[j] = float(Xn[idx[a]] @ Xn[idx[b]])
            continue
        M, pr = dist[w]
        v = Xn[idx[other]]
        obs[j] = float((pr * (M @ v)).sum())

    core_src = sorted(x for x in core if x in raw and x not in ctx["held_out"])
    proto = np.stack([raw[c] for c in core_src]).astype(np.float64).mean(axis=0)
    const_cos = CELL.pair_cos(CELL.code_matrix(vocab, raw, {w: proto for w in words}), ia, ib)
    floors = build_floors(vocab, ia, ib, gold, counts, const_cos)

    # scramble for a READOUT arm: permute WHICH WORD'S DISTRIBUTION is used, recompute the score
    keys = sorted(dist)
    rhos = []
    for i in range(N_PERM):
        rng = np.random.default_rng(90210 + i)
        perm = {k: keys[j] for k, j in zip(keys, rng.permutation(len(keys)))}
        o2 = np.empty(len(strat))
        for j, p4 in enumerate(strat):
            a, b = p4[0], p4[1]
            w, other = (a, b) if a in dist else (b, a)
            if w not in dist:
                o2[j] = float(Xn[idx[a]] @ Xn[idx[b]])
                continue
            M, pr = dist[perm[w]]
            o2[j] = float((pr * (M @ Xn[idx[other]])).sum())
        rhos.append(INS._spearman(o2, gold))
    rhos = np.array([r for r in rhos if np.isfinite(r)])
    p95 = float(np.percentile(rhos, 95))
    near = int(np.argmin(np.abs(rhos - p95)))
    rng = np.random.default_rng(90210 + near)
    perm = {k: keys[j] for k, j in zip(keys, rng.permutation(len(keys)))}
    near_cos = np.empty(len(strat))
    for j, p4 in enumerate(strat):
        a, b = p4[0], p4[1]
        w, other = (a, b) if a in dist else (b, a)
        if w not in dist:
            near_cos[j] = float(Xn[idx[a]] @ Xn[idx[b]])
        else:
            M, pr = dist[perm[w]]
            near_cos[j] = float((pr * (M @ Xn[idx[other]])).sum())

    cands = {k: (floors[k]["rho"], floors[k]["_partner"]) for k in floors}
    cands[FLOOR_SCRAM] = (p95, near_cos)
    bf = max(cands, key=lambda k: cands[k][0])
    d = FT.boot_rho_diff(obs, cands[bf][1], gold, n_boot=N_BOOT, seed=BOOT_SEED)
    ua = np.array(unc) if unc else np.zeros((1, 2))
    return {"arm": "D1_DISTRIBUTIONAL_EXPECTED_COS",
            "WHAT_IT_IS": "owner mechanism 3 -- a DISTRIBUTION over candidate fillers with explicit "
                          "uncertainty, scored as the EXPECTED cosine under that distribution "
                          "instead of the cosine of the mean code. SEPARATE BLOCK; it changes the "
                          "READOUT and must not be pooled with the primary.",
            "n_stratum": len(strat), "n_words_with_a_distribution": len(dist),
            "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
            "strongest_floor": bf,
            "floor_rho_by_arm": {k: round(v[0], 4) for k, v in cands.items()},
            "margin_over_strongest_floor": d, "band": FT.band(d["ci95"]),
            "clears_floor": bool(FT.band(d["ci95"]) == "ABOVE" and d["point"] >= T_MARGIN_MIN),
            "UNCERTAINTY": {"filler_entropy_mean": round(float(ua[:, 0].mean()), 4),
                            "mean_pairwise_filler_cosine": round(float(ua[:, 1].mean()), 4),
                            "reading": "high entropy + low pairwise cosine = the model is saying "
                                       "'most likely a mammal but it could also be a reptile'"}}


# ==========================================================================================
def selftest() -> Dict:
    print("[selftest] start", flush=True)
    ev: Dict = {}
    from hdlab import grounded_similarity as GS

    # --- RULER GATE: the EXISTING one, imported and called, not a reimplementation.
    # It hard-fails (SystemExit) unless the instrument resolved RUN_MODE=full, V=4096 and
    # CORPUS_BYTES=64,000,000 -- i.e. unless the ruler this cell's floors are computed on is the
    # real one. This is why this cell's reduced-grid flag is `--grid reduced` and never `--smoke`.
    from exp_task_degeneracy_v1 import ruler_mode_gate
    ev["RULER_MODE_GATE"] = ruler_mode_gate()
    ev["RULER_MODE_GATE"]["source"] = "experiments/exp_task_degeneracy_v1.py:121, imported"

    tab = GS._table()
    assert len(tab) == 36810, f"RULER GATE: norms table {len(tab)} != 36810 (grid={RUN_MODE})"
    assert len(next(iter(tab.values()))) == 12, "RULER GATE: norms are not 12-dim"
    ev["RULER_GATE_norms"] = {"n_words": len(tab), "n_dim": 12, "run_mode": RUN_MODE,
                        "asserted_identically_in_both_grids": True}

    # --- TRAP: grounded_similarity is SATURATED and is never the scorer. Re-measured, not inherited.
    pairs = CELL.load_simlex_pos()
    vals = [GS.grounded_similarity(a, b) for a, b, _, _ in pairs]
    c = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(n for _, n in c.most_common(2)) / len(vals)
    assert frac2 > 0.70, f"expected saturation; top-2 mass {frac2:.4f}"
    ev["TRAP_grounded_similarity_saturation"] = {"n_pairs": len(vals), "n_distinct": len(c),
                                                 "fraction_on_two_values": round(frac2, 4)}

    # --- G1: the scorer reproduces an independent per-pair recompute on the full 999
    vocab = sorted({w for p in pairs for w in p[:2]})
    raw = {w: np.asarray(tab[w], dtype=np.float64) for w in vocab}
    idx = {w: i for i, w in enumerate(vocab)}
    ia = np.array([idx[p[0]] for p in pairs]); ib = np.array([idx[p[1]] for p in pairs])
    gold = np.array([p[3] for p in pairs], dtype=np.float64)
    rf = INS._spearman(CELL.pair_cos(CELL.code_matrix(vocab, raw, {}), ia, ib), gold)
    ref = []
    for a, b, _, _ in pairs:
        va, vb = np.asarray(tab[a], np.float64), np.asarray(tab[b], np.float64)
        ref.append(float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb))))
    rr = INS._spearman(np.array(ref), gold)
    assert abs(rf - rr) < 1e-6, f"scorer {rf} != recompute {rr}"
    ev["G1_norms_rho_simlex999"] = {"vectorised": round(float(rf), 6),
                                    "independent_recompute": round(float(rr), 6)}

    # --- the SELECTIONAL MECHANISM does what the docstring says, on a fixture with a KNOWN answer.
    # CORE fillers of run/SUBJ are {dog, cat}; the held-out word `tove` fills that slot; so its
    # derived code must be the count-weighted mean of dog and cat and MUST NOT involve `road`,
    # which is the word that CO-OCCURS with it. This is the one-variable claim, asserted.
    hid = {"dog": np.array([1.0] * 12), "cat": np.array([3.0] * 12), "road": np.array([50.0] * 12),
           "brick": np.array([7.0] * 12), "tove": np.array([-9.0] * 12)}
    br = CELL.Bridger(hid, {"tove"}, {"tove": set()})
    slots = {"slot_filler": {("run", "SUBJ"): {"dog": 3, "cat": 1, "tove": 2},
                             ("run", "obl:across"): {"road": 9, "brick": 4, "tove": 2}},
             "word_cooc": {"tove": {"road": 5}}}
    S = SelectionalSource(slots, br, {"dog", "cat", "road", "brick"})
    got = S.code("tove", "S1_SELECTIONAL_MEAN")
    assert got is None, "SLOT_MIN_FILLERS=3 must refuse a 2-filler slot; got a code anyway"
    slots["slot_filler"][("run", "SUBJ")]["brick"] = 1
    S = SelectionalSource(slots, br, {"dog", "cat", "road", "brick"})
    got = S.code("tove", "S1_SELECTIONAL_MEAN")
    assert got is not None, "the slot now has 3 eligible fillers and must yield a code"
    exp_subj = (3 * 1.0 + 1 * 3.0 + 1 * 7.0) / 5.0
    assert abs(float(got[0]) - exp_subj) < 1e-9, \
        f"S1 must be the count-weighted filler mean {exp_subj}, got {float(got[0])}"
    ev["S_MECHANISM_known_answer"] = {"expected": exp_subj, "got": round(float(got[0]), 9),
                                      "note": "only run/SUBJ is usable; run/obl:across has 2 "
                                              "eligible fillers and is correctly refused"}

    # --- the DECISIVE CONTROL really removes co-occurring fillers
    slots["slot_filler"][("run", "SUBJ")]["road"] = 4
    S = SelectionalSource(slots, br, {"dog", "cat", "road", "brick"})
    with_co = S.code("tove", "S1_SELECTIONAL_MEAN")
    without = S.code("tove", "S3_SELECTIONAL_NOCOOC")
    assert with_co is not None and without is not None
    assert abs(float(with_co[0]) - float(without[0])) > 1e-9, \
        "S3 did not change anything -- the co-occurrence filter is a no-op"
    exp_no = (3 * 1.0 + 1 * 3.0 + 1 * 7.0) / 5.0
    assert abs(float(without[0]) - exp_no) < 1e-9, "S3 must drop `road`, the co-occurring filler"
    ev["S3_decisive_control"] = {"with_cooccurring_filler": round(float(with_co[0]), 4),
                                 "without": round(float(without[0]), 4)}

    # --- G2: a held-out row is DELETED from the table the bridger reads
    assert "tove" not in br.hidden, "G2 self-leak"
    ev["G2_no_self_leak"] = True

    # --- the FOUR floors are four different functions, and the CONSTANT floor is really constant
    rng = np.random.default_rng(1)
    vsm = [f"w{i}" for i in range(60)]
    rr2 = {w: rng.normal(size=12) for w in vsm}
    i2 = {w: i for i, w in enumerate(vsm)}
    iaa = np.array([i2[vsm[i]] for i in range(0, 58, 2)])
    ibb = np.array([i2[vsm[i]] for i in range(1, 59, 2)])
    gg = rng.normal(size=len(iaa))
    proto = np.stack([rr2[w] for w in vsm[:20]]).mean(axis=0)
    Xc = CELL.code_matrix(vsm, rr2, {w: proto for w in vsm[:10]})
    assert np.allclose(Xc[0], Xc[9]), "CONSTANT floor code table is not constant across bridged rows"
    fl = build_floors(vsm, iaa, ibb, gg, {w: i + 1 for i, w in enumerate(vsm)},
                      CELL.pair_cos(Xc, iaa, ibb))
    parts = [fl[k]["_partner"] for k in (FLOOR_ORTHO, FLOOR_FREQ, FLOOR_CONST)]
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            assert not np.allclose(parts[i], parts[j]), "two floors are the same function"
    ev["FOUR_FLOORS_are_distinct"] = sorted(FLOOR_KEYS)

    # --- the bootstrap must be able to BOTH fire and fail
    a = np.arange(60.0); g2 = a + rng.normal(scale=0.01, size=60)
    b2 = rng.normal(size=60)
    fire = FT.boot_rho_diff(a, b2, g2, n_boot=400, seed=1)
    fail = FT.boot_rho_diff(b2, rng.normal(size=60), g2, n_boot=400, seed=1)
    assert FT.band(fire["ci95"]) == "ABOVE", "bootstrap cannot FIRE on a planted signal"
    assert FT.band(fail["ci95"]) == "NOT_SEPARATED", "bootstrap cannot FAIL on a planted null"
    ev["bootstrap_can_fire_and_fail"] = {"planted_signal": FT.band(fire["ci95"]),
                                         "planted_null": FT.band(fail["ci95"])}

    # --- the extractor's own self-test runs here too, so a broken parser is caught before a run
    SEL.self_test()
    ev["extractor_selftest"] = "PASS"

    print("[selftest] ALL PASS " + json.dumps(ev, default=str)[:1200], flush=True)
    return ev


def main() -> int:
    t_start = time.time()
    ev = selftest()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK")
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_reduced" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} out={out_dir}", flush=True)

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    pairs = CELL.load_simlex_pos()
    vocab = sorted({w for p in pairs for w in p[:2]})
    raw = {w: np.asarray(v, dtype=np.float64) for w, v in tab.items()}
    idx = {w: i for i, w in enumerate(vocab)}
    partners: Dict[str, Set[str]] = collections.defaultdict(set)
    for a, b, _, _ in pairs:
        partners[a].add(b)
        partners[b].add(a)
    aoa = CELL.load_aoa()
    core = {w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in tab}
    held_out = {w for w in vocab if w not in core}
    counts = CELL.corpus_counts()

    def_graph, _pat, _rows = CELL.load_def_graph()
    them_edges = THEM.build_or_load()
    them_graph, them_info = INC.build_thematic_graph(them_edges)
    enriched = INC.merge(def_graph, them_graph)

    slots = SEL.build_or_load()
    br = CELL.Bridger(raw, held_out, partners)
    S = SelectionalSource(slots, br, core)

    sel_words = {w for w in held_out if S.slots_for(w, None, False, False)}
    inc_words = {w for w in held_out if br.neighbours(w, enriched, core, False)}
    print(f"[assets] core={len(core)} held_out={len(held_out)} slots={len(S.sf)} "
          f"sel_reach={len(sel_words)} inc_reach={len(inc_words)} "
          f"common={len(sel_words & inc_words)}", flush=True)

    g4 = {"n_slots": len(S.sf), "n_verb_slots": len({v for v, _ in S.sf}),
          "n_held_out_reached_by_selectional": len(sel_words),
          "n_held_out_reached_by_incumbent": len(inc_words),
          "n_common": len(sel_words & inc_words),
          "role_histogram": slots.get("role_histogram"),
          "passed": bool(S.sf and len(sel_words) >= 100)}
    if not g4["passed"]:
        raise SystemExit(f"[fatal] G4: selectional channel too thin to test: {g4}")

    ctx = {"vocab": vocab, "raw": raw, "pairs": pairs, "idx": idx, "held_out": held_out,
           "core": core, "partners": partners, "counts": counts, "br": br, "sel": S,
           "enriched": enriched, "sel_words": sel_words, "inc_words": inc_words}

    CONFIGS = [
        ("PRIMARY_COMMON_STRATUM", {"which": "COMMON", "do_pos": True}),
        ("PRIMARY_COMMON_MORPHBLOCK", {"which": "COMMON", "morph_block": True}),
        ("SELECTIONAL_OWN_STRATUM", {"which": "SEL_OWN"}),
        ("INCUMBENT_OWN_STRATUM_reproduces_landed_v2", {"which": "INC_OWN"}),
    ]
    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results: Dict[str, Dict] = {}
    for name, kw in CONFIGS:
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, name)
        if key in done and key in units:
            results[name] = units[key]
            print(f"[cfg] {name} RESUMED", flush=True)
            continue
        print(f"[cfg] {name} start", flush=True)
        r = run_config(name, ctx, **kw)
        record_unit(str(out_dir), key, r)
        results[name] = r
        print(f"[cfg] {name} done n={r.get('n_stratum')} t={r.get('elapsed_s')}s", flush=True)

    key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "D1_DISTRIBUTIONAL")
    if key in done and key in units:
        dist_block = units[key]
    else:
        print("[cfg] D1_DISTRIBUTIONAL start", flush=True)
        dist_block = run_distributional(ctx)
        record_unit(str(out_dir), key, dist_block)

    # ---- verdict
    P = results.get("PRIMARY_COMMON_STRATUM", {})
    arms = P.get("arms", {})
    g0 = P.get("G0_POWER_GATE", {}).get("PASSED", False)
    degen = P.get("MECHANISM_DISTINCTNESS", {}).get("DEGENERATE", False)
    s1 = arms.get(PRIMARY_ARM, {})
    s3 = arms.get(DECISIVE_CONTROL_ARM, {})
    vs_n1 = (P.get("VS_NULL") or {}).get(f"{PRIMARY_ARM}_vs_N1_NULL_SLOT_REWIRE", {})
    if degen:
        verdict = "DEGENERATE_MECHANISMS_NOT_DISTINCT"
    elif not g0:
        verdict = "POWER_INSUFFICIENT_ON_THE_PRIMARY_STRATUM"
    elif s1.get("clears_floor") and s3.get("clears_floor") and vs_n1.get("band") == "ABOVE":
        verdict = "SELECTIONAL_CONSTRAINT_BRIDGE_CLEARS_THE_FLOOR"
    elif s1.get("clears_floor"):
        verdict = "MIDDLE_BAND_CLEARS_FLOOR_BUT_NOT_THE_DECISIVE_CONTROL"
    else:
        verdict = "SELECTIONAL_CONSTRAINT_BRIDGE_DOES_NOT_CLEAR_THE_FLOOR"

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "prereg": PREREG, "verdict": verdict,
        "verdict_msg": ("Does deriving a held-out word's meaning from THE SELECTIONAL RESTRICTIONS "
                        "OF THE VERBS IT IS AN ARGUMENT OF beat copying the code of a co-occurring "
                        "neighbour, on the identical stratum / scorer / n / pool / gold, against "
                        "FOUR floors including the constant/prototype floor? -> " + verdict),
        "OWNER_ANSWER_THIS_CELL_IMPLEMENTS": (
            "Since the tove ran - it must be an animal (or at least something that has legs). "
            "Since it ran accross the road, I think of rabbits and deer which I've seen cross "
            "roads, and so I assume it's a smallish animal, most likely a mammel but it could "
            "also be a reptile. [BOARD Q5, 2026-08-16T15:11:42Z]"),
        "HOW_TO_READ_A_NULL": (
            "The owner performed this inference in front of us, so the CAPABILITY IS DEMONSTRATED. "
            "A miss is a fact about OUR IMPLEMENTATION -- our slot definition, our estimator, our "
            "target space -- and never about selectional bridging."),
        "config": {"AOA_CORE_MAX": AOA_CORE_MAX, "SLOT_MIN_FILLERS": SLOT_MIN_FILLERS,
                   "WSLOT_MIN_COUNT": WSLOT_MIN_COUNT, "SLOT_TOPK": SLOT_TOPK,
                   "FILLER_TOPK": FILLER_TOPK, "N_BOOT": N_BOOT, "N_PERM": N_PERM,
                   "T_MARGIN_MIN": T_MARGIN_MIN, "NULL_SEEDS": list(NULL_SEEDS),
                   "BOOT_SEED": BOOT_SEED, "FLOORS": list(FLOOR_KEYS)},
        "G4_channel_exists": g4,
        "selectional_extraction": {k: v for k, v in slots.items()
                                   if k not in ("slot_filler", "word_cooc")},
        "thematic_extraction_for_the_incumbent_arm": them_info,
        "selftest_evidence": ev,
        "results": results,
        "OWNER_MECHANISM_3_DISTRIBUTIONAL_SEPARATE_BLOCK": dist_block,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[done] {time.time() - t_start:.0f}s -> {out_dir}/metrics.json", flush=True)
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
