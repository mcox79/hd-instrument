"""floor_battery -- THE REQUIRED FLOOR SET for any hit@1 / rank claim on a read-out instrument.

WHY THIS FILE EXISTS (2026-08-16).
The standing bar was `max(orthographic, frequency, scramble)`. On 2026-08-16 a CONSTANT ranking
that uses ZERO information about the query -- cosine to the mean anchor direction, i.e. the same
answer to every question -- scored hit@1 0.1390 / 0.1518 on the open-vocabulary read-out and beat
the spelling floor by +0.0523 [+0.0391,+0.0658] and +0.0627 [+0.0475,+0.0778], CI-separated
(scratch/sparsify_right_object/decisive.json, reproduced here). That floor had NEVER been run, so
every hit@1 gate on that instrument had been set against a floor set missing its strongest member.

A floor that lives only in a report is forgotten by the next morning. It lives here instead.

WHAT A FLOOR IS, AND WHAT THIS IS NOT
A floor is a STANDALONE policy that could produce the answer WITHOUT understanding. A shortcut
added ON TOP of the system under test is a decomposition, not a floor. `oracle_constant_scores`
below is NOT a floor -- it is fitted on the gold labels and is reported as a CEILING OF THE
CONSTANT FAMILY, always labelled ORACLE.

CONTENTS
  constant_prototype_floor(mat, mat_ok)   the missing fourth floor -- a CONSTANT column
  frequency_floor(counts)                 log corpus count -- also a constant column
  scramble_null(mat, seed)                the permuted-anchor null
  oracle_constant_scores(...)             ORACLE: the best constant ranking, fitted on the golds
  balanced_candidate_sets(...)            build a pool on which NO constant ranking can beat chance
  matched_candidate_sets(...)             as above, ADDITIONALLY matched on a nuisance channel
  pool_admits_a_winning_constant(...)     THE POOL'S OWN VALIDITY CHECK, callable not commented
  hit_at_1_both_tie_conventions(...)      hit@1 optimistic AND conservative, plus tie mass

2026-08-16, SECOND ENTRY. `matched_candidate_sets` FAILED ITS OWN ORACLE CHECK in four banked
cells -- the fitted oracle constant read 0.7262 / 0.7313 / 0.7323 / 0.7354 against a chance of
0.0625 -- because its nearest-k selection discarded the gold marginal and, on a tie-heavy
channel, picked the same low-index anchors as distractors over and over. It has been rebuilt on
stratified marginal-preserving sampling; the broken construction is kept as
`_matched_candidate_sets_NEAREST_K_LEGACY` and used ONLY as the negative control that proves the
new check can fire. THE CHECK IS NOW RUN AND RETURNED (`diagnostics["validity"]`), never assumed.

ASCII-only. No unicode. numpy only; no substrate import, so any cell can use it.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

FLOOR_SET_REQUIRED = ("ORTHOGRAPHIC", "FREQUENCY", "SCRAMBLE", "CONSTANT_PROTOTYPE")


def l2n(A: np.ndarray) -> np.ndarray:
    """Row-wise L2 normalisation, zero-safe."""
    A = np.asarray(A, dtype=np.float32)
    n = np.linalg.norm(A, axis=-1, keepdims=True)
    return (A / np.maximum(n, 1e-12)).astype(np.float32)


# ------------------------------------------------------------------ THE FOURTH FLOOR
def constant_prototype_floor(mat: np.ndarray, mat_ok: Optional[np.ndarray] = None,
                             normalize_rows_first: bool = False) -> np.ndarray:
    """score(anchor) = cos(anchor, MEAN ANCHOR DIRECTION). Returns [n_anchors].

    CONSTANT across items: the same ranking answers every question, so it carries ZERO query
    information and ZERO orthography. It is NOT the frequency floor -- it measures how GENERIC an
    anchor's accumulated profile is, not how often the word occurs.

    `normalize_rows_first=False` reproduces the 2026-08-16 measurement exactly (mean of the RAW
    rows, then normalised). True gives the mean of the UNIT rows; both are reported by --self-test.
    """
    mat = np.asarray(mat, dtype=np.float32)
    ok = np.ones(mat.shape[0], dtype=bool) if mat_ok is None else np.asarray(mat_ok, dtype=bool)
    src = l2n(mat[ok]) if normalize_rows_first else mat[ok]
    mean_dir = l2n(src.mean(axis=0)[None, :])[0]
    return (l2n(mat) @ mean_dir).astype(np.float32)


def frequency_floor(counts: Sequence[float]) -> np.ndarray:
    """score(anchor) = log1p(corpus count). Also a CONSTANT column; kept separate because it is a
    different no-understanding story (popularity, not genericity) and the two can disagree."""
    return np.log1p(np.asarray(counts, dtype=np.float64)).astype(np.float32)


def scramble_null(mat: np.ndarray, seed: int) -> np.ndarray:
    """The anchor -> vector assignment permuted. Destroys the mapping, keeps every marginal."""
    rng = np.random.default_rng(seed)
    return np.asarray(mat, dtype=np.float32)[rng.permutation(mat.shape[0])]


def as_constant_matrix(v: np.ndarray, n_items: int) -> np.ndarray:
    """Broadcast a [n_anchors] constant floor to the [n_anchors, n_items] score-matrix shape every
    scorer expects. Materialised (not a view) so callers can mutate safely."""
    return np.repeat(np.asarray(v, dtype=np.float32)[:, None], n_items, axis=1)


# ------------------------------------------------------------------ ORACLE (NOT a floor)
def oracle_constant_scores(n_anchors: int, gold_sets: Sequence[np.ndarray],
                           eligible_sets: Optional[Sequence[np.ndarray]] = None,
                           smooth: bool = True) -> np.ndarray:
    """ORACLE, fitted on the gold labels: the CEILING of the constant family.

    With an open pool (eligible_sets=None) this is the gold-degree ranking -- how many items have
    this anchor as a correct answer. With per-item candidate sets it is the smoothed empirical odds
    that an anchor is the correct answer GIVEN it appears in a candidate set, which is the quantity
    a constant policy would have to exploit.

    NEVER a floor: it sees the answers. Its only job is to answer "could ANY constant ranking do
    better than chance here?".
    """
    ng = np.zeros(n_anchors, dtype=np.float64)
    na = np.zeros(n_anchors, dtype=np.float64)
    for i, g in enumerate(gold_sets):
        if len(g):
            ng[np.asarray(g, dtype=np.int64)] += 1.0
        if eligible_sets is not None:
            na[np.asarray(eligible_sets[i], dtype=np.int64)] += 1.0
    if eligible_sets is None:
        return ng.astype(np.float32)
    if smooth:
        return ((ng + 1.0) / (na + 2.0)).astype(np.float32)
    return (ng / np.maximum(na, 1.0)).astype(np.float32)


# ------------------------------------------------------------------ THE DE-BIASED POOL
def balanced_candidate_sets(designated_gold: np.ndarray, gold_sets: Sequence[np.ndarray],
                            excl_sets: Sequence[np.ndarray], keep: np.ndarray,
                            k_distract: int, seed: int,
                            max_tries_mult: int = 40) -> Tuple[np.ndarray, np.ndarray]:
    """Build per-item candidate sets on which NO CONSTANT RANKING CAN BEAT CHANCE.

    THE CONSTRUCTION AND WHY IT WORKS. For item i the candidate set is
        {designated_gold[i]} + k_distract distractors DRAWN FROM THE POPULATION OF OTHER ITEMS'
        DESIGNATED GOLDS.
    Because the distractors are sampled from the SAME marginal distribution over anchors as the
    golds themselves, an anchor is no more likely to be the CORRECT candidate than to be a WRONG
    one. Any score that depends on the anchor alone (a constant ranking: prototypicality,
    popularity, genericity, length, anything) therefore has expected hit@1 = 1/(k_distract+1) --
    exactly chance. This is a property of the construction, not an empirical hope; it is
    nevertheless VERIFIED empirically by scoring `oracle_constant_scores` on the result.

    THE ONE RESIDUAL, STATED. A distractor is rejected if it lies in item i's OWN gold set (it
    would be a second correct answer). Anchors that are gold for many items are therefore slightly
    UNDER-represented among distractors, which biases the design very slightly TOWARDS a generic
    constant ranking -- i.e. conservative for a "the constant is dead here" conclusion. The oracle
    arm measures exactly this residual.

    Returns (cand [n_items, k_distract+1] int64, gold_col [n_items] int64); rows for items with
    keep=False or no designated gold are filled with -1.
    """
    n_items = len(gold_sets)
    keep = np.asarray(keep, dtype=bool)
    dg = np.asarray(designated_gold, dtype=np.int64)
    donor_idx = np.flatnonzero(keep & (dg >= 0))
    if donor_idx.size < k_distract + 2:
        raise ValueError("not enough items to build a role-symmetric donor pool: %d" % donor_idx.size)
    donors = dg[donor_idx]                      # THE GOLD MARGINAL -- distractors come from here
    rng = np.random.default_rng(seed)
    cand = np.full((n_items, k_distract + 1), -1, dtype=np.int64)
    gold_col = np.full(n_items, -1, dtype=np.int64)
    n_short = 0
    for i in range(n_items):
        if not keep[i] or dg[i] < 0:
            continue
        banned = set(np.asarray(gold_sets[i], dtype=np.int64).tolist())
        banned.update(np.asarray(excl_sets[i], dtype=np.int64).tolist())
        chosen: List[int] = []
        seen = set(banned)
        tries = 0
        limit = max_tries_mult * (k_distract + 1)
        while len(chosen) < k_distract and tries < limit:
            draw = donors[rng.integers(0, donors.size, size=k_distract)]
            for d in draw.tolist():
                if d not in seen:
                    seen.add(d)
                    chosen.append(d)
                    if len(chosen) == k_distract:
                        break
            tries += k_distract
        if len(chosen) < k_distract:
            n_short += 1
            continue
        row = np.array([dg[i]] + chosen, dtype=np.int64)
        perm = rng.permutation(k_distract + 1)   # gold position randomised: index order leaks nothing
        cand[i] = row[perm]
        gold_col[i] = int(np.flatnonzero(perm == 0)[0])
    if n_short:
        print("[floor_battery] %d items dropped: could not fill a candidate set" % n_short,
              flush=True)
    return cand, gold_col


def _matched_candidate_sets_NEAREST_K_LEGACY(
        designated_gold: np.ndarray, gold_sets: Sequence[np.ndarray],
        excl_sets: Sequence[np.ndarray], keep: np.ndarray, k_distract: int, seed: int,
        match_score: np.ndarray, n_sample: int = 384) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """THE BROKEN CONSTRUCTION, KEPT ONLY AS A NEGATIVE CONTROL. Do not call it for a result.

    This is `matched_candidate_sets` exactly as it stood until 2026-08-16, byte for byte in its
    selection logic. It is retained -- and only ever called from `self_test` and from
    `verification/test_verdict_bar_checker.py` -- so that the new validity assertion can be shown
    TO FAIL on a pool that is genuinely broken. A guard that has never been seen to fire is not a
    guard.

    WHAT IS WRONG WITH IT, measured rather than asserted (scratch/pool_floor_repro2.py,
    scratch/pool_fix_proto2.py):

      D1  `sorted(set(draw))` DISCARDS the multiplicity of the with-replacement draw. The
          distractor distribution is therefore NOT the gold marginal -- it is roughly the
          marginal's SUPPORT, flattened.
      D2  `argsort(err, kind="stable")[:k]` is a DETERMINISTIC nearest-k pick. On a channel with
          heavy EXACT ties -- and a real trigram-overlap matrix is exactly 0.0 for the large
          majority of (anchor, query) pairs -- the error is 0 for hundreds of donors at once and
          the STABLE sort resolves the tie by the order of `sorted(...)`, i.e. by ASCENDING
          ANCHOR INDEX. The same few anchors are then used as distractors again and again.

    The result is an ITEM-INDEPENDENT signal with nothing to do with the query: an anchor that
    appears in very many candidate sets is almost never the correct answer, and one that appears
    in exactly one set usually is. `oracle_constant_scores` fits precisely that, which is why the
    fitted oracle constant reads 0.7262 / 0.7313 / 0.7323 / 0.7354 against a chance of 0.0625 in
    the four cells that banked this pool.
    """
    n_items = len(gold_sets)
    keep = np.asarray(keep, dtype=bool)
    dg = np.asarray(designated_gold, dtype=np.int64)
    donor_idx = np.flatnonzero(keep & (dg >= 0))
    donors = dg[donor_idx]
    rng = np.random.default_rng(seed)
    cand = np.full((n_items, k_distract + 1), -1, dtype=np.int64)
    gold_col = np.full(n_items, -1, dtype=np.int64)
    errs: List[float] = []
    n_short = 0
    for i in range(n_items):
        if not keep[i] or dg[i] < 0:
            continue
        banned = set(np.asarray(gold_sets[i], dtype=np.int64).tolist())
        banned.update(np.asarray(excl_sets[i], dtype=np.int64).tolist())
        draw = donors[rng.integers(0, donors.size, size=n_sample)]
        uniq = np.array(sorted(set(int(x) for x in draw.tolist()) - banned), dtype=np.int64)
        if uniq.size < k_distract:
            n_short += 1
            continue
        target = float(match_score[dg[i], i])
        err = np.abs(match_score[uniq, i].astype(np.float64) - target)
        sel = uniq[np.argsort(err, kind="stable")[:k_distract]]
        errs.append(float(np.mean(np.abs(match_score[sel, i].astype(np.float64) - target))))
        row = np.concatenate([np.array([dg[i]], dtype=np.int64), sel])
        perm = rng.permutation(k_distract + 1)
        cand[i] = row[perm]
        gold_col[i] = int(np.flatnonzero(perm == 0)[0])
    diag = {"n_dropped": int(n_short), "mean_abs_match_error": round(float(np.mean(errs)), 6)
            if errs else None, "n_sample_per_item": n_sample,
            "CONSTRUCTION": "NEAREST_K_LEGACY_BROKEN_do_not_use_for_a_result"}
    return cand, gold_col, diag


def pool_admits_a_winning_constant(cand: np.ndarray, gold_sets: Sequence[np.ndarray],
                                   n_anchors: int, k_distract: int,
                                   tol: float = 0.03) -> Dict:
    """THE POOL'S OWN VALIDITY CHECK, as a callable rather than as a comment.

    A candidate pool is only a de-biased pool if NO ranking that ignores the query can beat
    chance on it. The strongest such ranking is the one FITTED ON THE GOLD LABELS, so scoring
    `oracle_constant_scores` on the pool is the check -- if the fitted ceiling of the constant
    family is at chance, every unfitted constant is too.

    Returns a dict with `ok`, the measured oracle hit rate, the pool's own chance, and the
    margin. `ok` is False when the fitted oracle exceeds chance by more than `tol`.

    THIS IS THE CHECK THAT WAS NEVER RUN ON THE MATCHED POOL. `self_test` S5 ran it on the
    balanced pool and S7 did not run it on the matched one, so the matched pool shipped broken
    for as long as it existed while its sibling was guarded.
    """
    ok_rows = np.flatnonzero(np.asarray(cand)[:, 0] >= 0)
    n_items = len(gold_sets)
    GOLD = np.zeros((n_anchors, n_items), dtype=bool)
    for i in ok_rows:
        g = np.asarray(gold_sets[i], dtype=np.int64)
        if g.size:
            GOLD[g, i] = True
    E = np.zeros((n_anchors, n_items), dtype=bool)
    cols = np.repeat(ok_rows[:, None], k_distract + 1, axis=1)
    E[np.asarray(cand)[ok_rows].ravel(), cols.ravel()] = True
    orc = oracle_constant_scores(n_anchors, [np.flatnonzero(GOLD[:, i]) for i in ok_rows],
                                 [np.asarray(cand)[i] for i in ok_rows])
    h = hit_at_1_both_tie_conventions(as_constant_matrix(orc, n_items), E, GOLD)
    hit = float(h["hit_exp"][ok_rows].mean()) if ok_rows.size else float("nan")
    chance = 1.0 / (k_distract + 1)
    return {"ok": bool(hit <= chance + tol), "oracle_constant_hit_exp": round(hit, 4),
            "chance": round(chance, 6), "margin_over_chance": round(hit - chance, 4),
            "tol": tol, "n_items": int(ok_rows.size)}


def matched_candidate_sets(designated_gold: np.ndarray, gold_sets: Sequence[np.ndarray],
                           excl_sets: Sequence[np.ndarray], keep: np.ndarray, k_distract: int,
                           seed: int, match_score: np.ndarray,
                           n_sample: int = 384, n_bins: int = 64,
                           validity_tol: float = 0.03) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """A STRICTER pool: role-symmetric AS `balanced_candidate_sets`, and additionally MATCHED to
    the gold on a nuisance channel (in practice: orthographic similarity to the query word).

    REWRITTEN 2026-08-16 BECAUSE THE PREVIOUS CONSTRUCTION FAILED ITS OWN ORACLE CHECK IN FOUR
    BANKED CELLS (fitted oracle constant 0.7262 / 0.7313 / 0.7323 / 0.7354 against chance
    0.0625). The old nearest-k selection is preserved verbatim as
    `_matched_candidate_sets_NEAREST_K_LEGACY`, whose docstring states exactly what it does
    wrong; it is now only ever used as the NEGATIVE CONTROL that proves the new check can fail.

    THE CONSTRUCTION, AND WHY IT KEEPS ROLE SYMMETRY. For item i:
      1. STRATIFY the match channel using edges that DO NOT LOOK AT WHICH MEMBER IS THE GOLD --
         quantiles of `match_score[donors, i]` over the donor population. Equal values always
         land in the same stratum, so an exact-tie mass (a trigram matrix is 0.0 for most pairs)
         forms ONE stratum rather than being split by an arbitrary tiebreak.
      2. Take the gold's stratum `b`.
      3. Draw the k_distract distractors FROM THE GOLD MARGINAL RESTRICTED TO STRATUM b -- that
         is, resample the donor multiset (golds WITH their multiplicity) filtered to b.

    THE ARGUMENT. `designated_gold[i]` is a draw from the gold marginal P. Conditioning a draw on
    an event defined by its own value gives the restricted law, so GIVEN that the gold fell in
    stratum b it is distributed exactly as `P restricted to b` -- which is exactly the law the
    distractors are drawn from. The k+1 members are therefore EXCHANGEABLE within the stratum, so
    any ranking that depends on the anchor alone has expected hit@1 = 1/(k_distract+1). This is
    the same argument that makes `balanced_candidate_sets` work, applied inside a stratum; the
    old code broke it by (a) discarding the draw's multiplicity and (b) picking deterministically.

    FAIL CLOSED. If the gold's stratum cannot supply k_distract distinct admissible anchors the
    ITEM IS DROPPED and counted in `n_dropped`. The stratum is NEVER widened to rescue it:
    widening would draw distractors from a superset of the gold's own law and re-break the
    exchangeability this construction exists to preserve. Finer `n_bins` buys a tighter match and
    costs dropped items; both numbers are in the diagnostics so the trade is visible.

    THE SAME RESIDUAL AS THE BALANCED POOL, STATED: a distractor in item i's own gold/exclusion
    set is rejected, so anchors that are gold for many items are slightly under-represented among
    distractors. `diagnostics["validity"]` MEASURES the total residual by scoring the fitted
    oracle constant on the pool that was actually built -- it is not assumed.

    Returns (cand [n_items, k_distract+1], gold_col [n_items], diagnostics).
    """
    n_items = len(gold_sets)
    keep = np.asarray(keep, dtype=bool)
    dg = np.asarray(designated_gold, dtype=np.int64)
    donor_idx = np.flatnonzero(keep & (dg >= 0))
    if donor_idx.size < k_distract + 2:
        raise ValueError("not enough items to build a role-symmetric donor pool: %d"
                         % donor_idx.size)
    donors = dg[donor_idx]                   # THE GOLD MARGINAL, multiplicity intact
    rng = np.random.default_rng(seed)
    cand = np.full((n_items, k_distract + 1), -1, dtype=np.int64)
    gold_col = np.full(n_items, -1, dtype=np.int64)
    errs: List[float] = []
    strat_sizes: List[int] = []
    n_short = 0
    # RESOLUTION IS CAPPED BY DONOR DIVERSITY, not by the caller's optimism. A stratum must be
    # able to supply k_distract DISTINCT admissible anchors or the item is dropped, so asking for
    # more strata than the population can fill silently deletes most of the data -- measured: on
    # a gold-concentrated population `n_bins=64` dropped 1881 of 3000 items. The cap depends only
    # on the donor population, never on which member is the gold, so it does not touch the
    # exchangeability argument. It is REPORTED (`n_bins_effective`), never silent.
    n_distinct_donors = int(np.unique(donors).size)
    n_bins_eff = max(1, min(int(n_bins), n_distinct_donors // (2 * (k_distract + 1))))
    qs = np.linspace(0.0, 1.0, n_bins_eff + 1)[1:-1]
    if n_bins_eff <= 1:
        print("[floor_battery] matched pool: donor diversity (%d distinct anchors) supports NO "
              "stratification at k_distract=%d -- this pool is NOT matched on the nuisance "
              "channel, it is merely role-symmetric. Do not report it as matched."
              % (n_distinct_donors, k_distract), flush=True)
    for i in range(n_items):
        if not keep[i] or dg[i] < 0:
            continue
        dv = np.asarray(match_score[donors, i], dtype=np.float64)
        # np.unique on the edges is REQUIRED, not tidiness: with a heavy tie mass many quantiles
        # coincide, and duplicate edges would create empty strata between two copies of the same
        # value. Collapsing them is what puts a whole tie into ONE stratum.
        edges = np.unique(np.quantile(dv, qs)) if qs.size else np.empty(0, dtype=np.float64)
        b = np.searchsorted(edges, dv, side="right")
        gb = int(np.searchsorted(edges, float(match_score[dg[i], i]), side="right"))
        strat = donors[b == gb]
        if strat.size == 0:
            n_short += 1
            continue
        banned = set(np.asarray(gold_sets[i], dtype=np.int64).tolist())
        banned.update(np.asarray(excl_sets[i], dtype=np.int64).tolist())
        chosen: List[int] = []
        seen = set(banned)
        tries = 0
        limit = 40 * (k_distract + 1)
        while len(chosen) < k_distract and tries < limit:
            draw = strat[rng.integers(0, strat.size, size=k_distract)]
            for d in draw.tolist():
                if d not in seen:
                    seen.add(d)
                    chosen.append(d)
                    if len(chosen) == k_distract:
                        break
            tries += k_distract
        if len(chosen) < k_distract:
            n_short += 1
            continue
        strat_sizes.append(int(np.unique(strat).size))
        sel = np.array(chosen, dtype=np.int64)
        target = float(match_score[dg[i], i])
        errs.append(float(np.mean(np.abs(match_score[sel, i].astype(np.float64) - target))))
        row = np.concatenate([np.array([dg[i]], dtype=np.int64), sel])
        perm = rng.permutation(k_distract + 1)   # gold position randomised
        cand[i] = row[perm]
        gold_col[i] = int(np.flatnonzero(perm == 0)[0])
    if n_short:
        print("[floor_battery] matched pool: %d items dropped (stratum could not supply %d "
              "distinct distractors); the stratum is NEVER widened -- see docstring"
              % (n_short, k_distract), flush=True)
    n_anchors = int(np.asarray(match_score).shape[0])
    diag = {"n_dropped": int(n_short),
            "mean_abs_match_error": round(float(np.mean(errs)), 6) if errs else None,
            "n_sample_per_item": n_sample, "n_bins_requested": int(n_bins),
            "n_bins_effective": int(n_bins_eff), "n_distinct_donors": n_distinct_donors,
            "median_stratum_distinct_anchors": int(np.median(strat_sizes)) if strat_sizes else 0,
            "CONSTRUCTION": "STRATIFIED_MARGINAL_PRESERVING",
            "validity": pool_admits_a_winning_constant(cand, gold_sets, n_anchors, k_distract,
                                                       tol=validity_tol)}
    if not diag["validity"]["ok"]:
        print("[floor_battery] WARNING: the matched pool ADMITS A WINNING CONSTANT -- fitted "
              "oracle %.4f against chance %.4f. Its numbers carry no verdict weight."
              % (diag["validity"]["oracle_constant_hit_exp"], diag["validity"]["chance"]),
              flush=True)
    return cand, gold_col, diag


# ------------------------------------------------------------------ SCORING
def hit_at_1_both_tie_conventions(S: np.ndarray, elig: np.ndarray,
                                  gold: np.ndarray) -> Dict[str, np.ndarray]:
    """hit@1 under BOTH tie conventions, vectorised over items.

    S     [n_anchors, n_items] scores
    elig  [n_anchors, n_items] bool -- the eligible pool for each item
    gold  [n_anchors, n_items] bool -- correct answers for each item

    hit_exp     : THE PRIMARY. (#golds tied at the max) / (#tied at the max) -- the unbiased
                  expectation under a random tie-break, and the only one of the three that cannot
                  be gamed by a channel that ties everything. A channel whose whole pool ties
                  scores EXACTLY the item's chance rate under hit_exp, which is what it deserves.
    optimistic  : a gold is AMONG the top-scoring set (best case within a tie)
    conservative: EVERY top-scoring entry is a gold (worst case within a tie)
    All three coincide when the argmax is unique. `tie_mass` is the tied fraction of the pool.

    WHY ALL THREE ARE ALWAYS RETURNED. On 2026-08-16 an optimistic top-50 read gave a binary
    coverage channel 0.993 (conservative 0.000), and on a 16-candidate pool the prefix floor read
    0.4384 optimistic because every candidate tied at zero. A channel with heavy tie mass can flip
    a comparison by convention alone, so the convention is never chosen silently.
    """
    Sm = np.where(elig, S.astype(np.float32), -np.inf)
    mx = Sm.max(axis=0)
    finite = np.isfinite(mx)
    tied = (Sm == mx[None, :]) & elig
    n_tied = np.maximum(tied.sum(axis=0), 1)
    n_gold_tied = (tied & gold).sum(axis=0)
    n_elig = np.maximum(elig.sum(axis=0), 1)
    opt = (tied & gold).any(axis=0) & finite
    cons = finite & ~((tied & ~gold).any(axis=0))
    return {"hit_exp": (n_gold_tied / n_tied) * finite,
            "hit_opt": opt.astype(np.float64), "hit_cons": (cons & finite).astype(np.float64),
            "tie_mass": ((tied.sum(axis=0) - 1) / n_elig).astype(np.float64),
            "scored": finite & (gold & elig).any(axis=0)}


def rank_of_best_gold(S: np.ndarray, elig: np.ndarray,
                      gold: np.ndarray) -> Dict[str, np.ndarray]:
    """Rank of the best gold under BOTH conventions: opt = #(strictly greater)+1, cons = #(>=)."""
    Sm = np.where(elig, S.astype(np.float32), -np.inf)
    gbest = np.where(gold & elig, Sm, -np.inf).max(axis=0)
    gt = (Sm > gbest[None, :]).sum(axis=0) + 1
    ge = (Sm >= gbest[None, :]).sum(axis=0)
    return {"rank_opt": gt.astype(np.float64), "rank_cons": ge.astype(np.float64)}


def paired_bootstrap_ci(hits: Dict[str, np.ndarray], mask: np.ndarray, n_boot: int,
                        seed: int) -> Dict[str, Dict]:
    """Paired bootstrap over the COMMON scored items. Returns per-arm acc+CI and the resample
    matrix so callers can form any paired margin without re-drawing."""
    idx_pool = np.flatnonzero(mask)
    nc = idx_pool.size
    rng = np.random.default_rng(seed)
    IDX = rng.integers(0, nc, size=(n_boot, nc))
    boot = {k: np.asarray(v, dtype=np.float64)[idx_pool][IDX].mean(axis=1) for k, v in hits.items()}
    acc = {k: float(np.asarray(v, dtype=np.float64)[idx_pool].mean()) for k, v in hits.items()}
    return {"n_common": int(nc), "acc": acc, "boot": boot}


def margin(boot: Dict[str, np.ndarray], a: str, b: str) -> Dict:
    d = boot[a] - boot[b]
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"point": round(float(np.mean(d)), 4), "ci95": [round(lo, 4), round(hi, 4)],
            "band": "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEPARATED")}


# ------------------------------------------------------------------ self-test
def self_test() -> dict:
    res: dict = {}
    rng = np.random.default_rng(11)

    # S1 -- the constant floor really is CONSTANT and really is a cosine to the mean direction.
    mat = rng.standard_normal((200, 32)).astype(np.float32) + 0.7
    f = constant_prototype_floor(mat)
    assert f.shape == (200,)
    md = l2n(mat.mean(axis=0)[None, :])[0]
    assert np.allclose(f, l2n(mat) @ md, atol=1e-6), "constant floor is not cos-to-mean-direction"
    M = as_constant_matrix(f, 5)
    assert M.shape == (200, 5) and np.allclose(M[:, 0], M[:, 4]), "constant column is not constant"
    # and it is NOT the frequency floor: on random counts the two disagree
    cnt = rng.integers(1, 5000, size=200)
    assert abs(float(np.corrcoef(f, frequency_floor(cnt))[0, 1])) < 0.5, "floors are collinear"
    res["S1_constant_floor"] = {"is_cos_to_mean_dir": True, "is_constant_across_items": True}

    # S2 -- ROW-NORMALISED variant is a genuinely different vector (both reported, never conflated)
    f2 = constant_prototype_floor(mat, normalize_rows_first=True)
    res["S2_variant_corr_raw_vs_rownorm"] = round(float(np.corrcoef(f, f2)[0, 1]), 6)

    # S3 -- the tie conventions actually separate, and coincide when the argmax is unique.
    S = np.zeros((4, 3), dtype=np.float32)
    elig = np.ones((4, 3), dtype=bool)
    gold = np.zeros((4, 3), dtype=bool)
    S[:, 0] = [1.0, 1.0, 0.0, 0.0]; gold[0, 0] = True          # gold tied with a non-gold
    S[:, 1] = [2.0, 0.0, 0.0, 0.0]; gold[0, 1] = True          # gold strictly top
    S[:, 2] = [0.0, 3.0, 0.0, 0.0]; gold[0, 2] = True          # gold loses outright
    h = hit_at_1_both_tie_conventions(S, elig, gold)
    assert list(h["hit_opt"]) == [1.0, 1.0, 0.0], "optimistic hit wrong: %r" % h["hit_opt"]
    assert list(h["hit_cons"]) == [0.0, 1.0, 0.0], "conservative hit wrong: %r" % h["hit_cons"]
    assert list(h["hit_exp"]) == [0.5, 1.0, 0.0], "expected-hit wrong: %r" % h["hit_exp"]
    assert abs(h["tie_mass"][0] - 0.25) < 1e-9 and h["tie_mass"][1] == 0.0
    # THE GUARD THAT MATTERS: a channel that ties its whole pool scores EXACTLY chance under
    # hit_exp, while the optimistic convention would hand it a perfect score.
    flat = np.zeros((16, 200), dtype=np.float32)
    fg = np.zeros((16, 200), dtype=bool)
    fg[np.random.default_rng(0).integers(0, 16, size=200), np.arange(200)] = True
    hf = hit_at_1_both_tie_conventions(flat, np.ones((16, 200), dtype=bool), fg)
    assert hf["hit_opt"].mean() == 1.0 and abs(hf["hit_exp"].mean() - 1.0 / 16) < 1e-9, (
        "the tie-corrected metric did not neutralise an all-ties channel")
    r = rank_of_best_gold(S, elig, gold)
    # col2: gold scores 0.0 and three entries tie AT 0.0, so the conservative rank is 4 (worst
    # case inside the tie), not 2. Getting this wrong is exactly the tie artefact being guarded.
    assert list(r["rank_opt"]) == [1.0, 1.0, 2.0], "rank_opt wrong: %r" % r["rank_opt"]
    assert list(r["rank_cons"]) == [2.0, 1.0, 4.0], "rank_cons wrong: %r" % r["rank_cons"]
    res["S3_tie_conventions"] = {"separate_on_a_tie": True, "coincide_when_unique": True}

    # S4 -- eligibility is honoured: an excluded anchor can never win.
    elig2 = elig.copy(); elig2[1, 2] = False
    h2 = hit_at_1_both_tie_conventions(S, elig2, gold)
    assert h2["hit_opt"][2] == 1.0, "masking the winner did not hand the item to the gold"
    res["S4_eligibility_respected"] = True

    # S5 -- THE LOAD-BEARING ONE. On a balanced candidate set built by this module, a STRONGLY
    # prototype-shaped constant ranking scores CHANCE, and the ORACLE constant does too --
    # while on the SAME items with an open pool the same constant ranking scores far above it.
    n_anchors, n_items, K = 400, 3000, 15
    proto = np.linspace(1.0, 0.0, n_anchors).astype(np.float32)      # anchor 0 = most generic
    # golds are prototype-skewed, exactly the pathology being tested for
    p = proto ** 8; p = p / p.sum()
    dg = rng.choice(n_anchors, size=n_items, p=p)
    gold_sets = [np.array([g], dtype=np.int64) for g in dg]
    excl_sets = [np.zeros(0, dtype=np.int64) for _ in range(n_items)]
    keep = np.ones(n_items, dtype=bool)
    # open pool: the constant ranking always answers anchor 0 -> hit rate = P(gold == 0)
    GOLDM = np.zeros((n_anchors, n_items), dtype=bool)
    GOLDM[dg, np.arange(n_items)] = True
    open_elig = np.ones((n_anchors, n_items), dtype=bool)
    open_hit = hit_at_1_both_tie_conventions(as_constant_matrix(proto, n_items),
                                             open_elig, GOLDM)["hit_opt"].mean()
    cand, gcol = balanced_candidate_sets(dg, gold_sets, excl_sets, keep, K, seed=5)
    ok = cand[:, 0] >= 0
    bal_elig = np.zeros((n_anchors, n_items), dtype=bool)
    rows = cand[ok]
    cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
    bal_elig[rows.ravel(), cols.ravel()] = True
    bal = hit_at_1_both_tie_conventions(as_constant_matrix(proto, n_items), bal_elig, GOLDM)
    bal_hit = float(bal["hit_opt"][ok].mean())
    chance = 1.0 / (K + 1)
    orc = oracle_constant_scores(n_anchors, [gold_sets[i] for i in np.flatnonzero(ok)],
                                 [cand[i] for i in np.flatnonzero(ok)])
    orc_hit = float(hit_at_1_both_tie_conventions(as_constant_matrix(orc, n_items), bal_elig,
                                                  GOLDM)["hit_opt"][ok].mean())
    # EACH POOL IS COMPARED TO ITS OWN CHANCE. The open pool's chance is 1/n_anchors and the
    # balanced pool's is 1/(K+1); comparing the two hit rates directly would be the exact
    # "a number may not be carried between populations" error this module exists to prevent.
    open_chance = 1.0 / n_anchors
    assert open_hit > 5 * open_chance, (
        "the synthetic open pool is not prototype-dominated (%.4f vs its own chance %.4f) -- "
        "the test cannot fail" % (open_hit, open_chance))
    assert abs(bal_hit - chance) < 0.02, ("a constant ranking beat chance on the BALANCED pool: "
                                          "%.4f vs %.4f -- construction is broken" % (bal_hit, chance))
    assert orc_hit < chance + 0.03, ("the fitted ORACLE constant beat chance on the BALANCED pool: "
                                     "%.4f vs %.4f" % (orc_hit, chance))
    # and a QUERY-DEPENDENT arm can still win on the balanced pool -- it is not just a hard task
    Sq = np.zeros((n_anchors, n_items), dtype=np.float32)
    Sq[dg, np.arange(n_items)] = 1.0
    know_hit = float(hit_at_1_both_tie_conventions(Sq, bal_elig, GOLDM)["hit_opt"][ok].mean())
    assert know_hit > 0.99, "the balanced pool is not winnable by a knowing arm: %.4f" % know_hit
    res["S5_balanced_pool_kills_constant_rankings"] = {
        "constant_open_pool": round(float(open_hit), 4),
        "open_pool_own_chance": round(float(open_chance), 6),
        "constant_balanced": round(bal_hit, 4),
        "oracle_constant_balanced": round(orc_hit, 4), "balanced_own_chance": round(chance, 4),
        "known_answer_balanced": round(know_hit, 4)}

    # S6 -- distractors really are drawn from the gold marginal (role symmetry), measured.
    d_counts = np.bincount(cand[ok][:, :].ravel(), minlength=n_anchors).astype(np.float64)
    g_counts = np.bincount(dg[ok], minlength=n_anchors).astype(np.float64)
    m = (g_counts + d_counts) > 0
    rho = float(np.corrcoef(g_counts[m], d_counts[m])[0, 1])
    assert rho > 0.9, "distractor marginal does not track the gold marginal: rho=%.3f" % rho
    res["S6_role_symmetry_corr_gold_vs_candidate_marginal"] = round(rho, 4)

    # S7 -- the MATCHED pool must do THREE things, and until 2026-08-16 only two were checked.
    # It must neutralise a nuisance channel that wins on the unmatched pool; it must stay
    # winnable by a knowing arm (a pool nobody can win is useless); and -- THE ONE THAT WAS
    # MISSING -- it must still admit NO winning constant, which is the property the whole
    # de-biased-pool family exists for. S5 ran that check on the balanced pool and S7 did not run
    # it here, so the matched pool shipped broken while its sibling was guarded.
    #
    # THE CHANNEL IS DELIBERATELY TIE-HEAVY AND QUANTISED. A smooth Gaussian nuisance channel
    # does NOT expose the defect (it reads 0.08 against chance 0.0625 -- measured). The real
    # channel is trigram overlap, which is EXACTLY 0.0 for most (anchor, query) pairs and takes
    # few distinct values, and that tie mass is what the broken nearest-k selection turned into
    # an item-independent signal. A test on the easy channel would have passed forever.
    #
    # S7 GETS ITS OWN POPULATION, and that is not laziness avoided but a requirement. S5's golds
    # are prototype-dominated BY DESIGN (p ~ proto**8, ~30 distinct answers), which is the right
    # pathology for S5 and the wrong population here: stratified matching needs enough DISTINCT
    # donors to fill a stratum, and on S5's population the resolution cap collapses to no
    # stratification at all. The population below is the shape the real cells have -- thousands
    # of anchors, a skewed but not degenerate answer distribution.
    n_anchors7, n_items7, K7 = 3000, 3000, 15
    chance7 = 1.0 / (K7 + 1)
    w7 = np.linspace(1.0, 0.02, n_anchors7) ** 3.0
    w7 = w7 / w7.sum()
    dg7 = rng.choice(n_anchors7, size=n_items7, p=w7)
    gold_sets7 = [np.array([g], dtype=np.int64) for g in dg7]
    excl7 = [np.zeros(0, dtype=np.int64) for _ in range(n_items7)]
    keep7 = np.ones(n_items7, dtype=bool)
    GOLD7 = np.zeros((n_anchors7, n_items7), dtype=bool)
    GOLD7[dg7, np.arange(n_items7)] = True
    Sq7 = np.zeros((n_anchors7, n_items7), dtype=np.float32)
    Sq7[dg7, np.arange(n_items7)] = 1.0
    LEVELS = np.round(np.linspace(0.04, 1.0, 25), 3).astype(np.float32)
    nuis = np.zeros((n_anchors7, n_items7), dtype=np.float32)
    nzm = rng.random((n_anchors7, n_items7)) >= 0.85          # 85 per cent EXACT ZERO
    nuis[nzm] = LEVELS[rng.integers(0, LEVELS.size, size=int(nzm.sum()))]
    gv = LEVELS[rng.integers(LEVELS.size // 2, LEVELS.size, size=n_items7)]
    gv[rng.random(n_items7) < 0.35] = 0.0                     # the gold is often at the tie too
    nuis[dg7, np.arange(n_items7)] = gv                       # gold easy, but IN the value set
    cand_b7, _gb7 = balanced_candidate_sets(dg7, gold_sets7, excl7, keep7, K7, seed=5)
    ok7 = cand_b7[:, 0] >= 0
    elig_u = np.zeros((n_anchors7, n_items7), dtype=bool)
    rb = cand_b7[ok7]
    cb = np.repeat(np.flatnonzero(ok7)[:, None], K7 + 1, axis=1)
    elig_u[rb.ravel(), cb.ravel()] = True
    u_hit = float(hit_at_1_both_tie_conventions(nuis, elig_u, GOLD7)["hit_exp"][ok7].mean())
    cand_m, _gc, mdiag = matched_candidate_sets(dg7, gold_sets7, excl7, keep7, K7, 9, nuis)
    okm = cand_m[:, 0] >= 0
    m_elig = np.zeros((n_anchors7, n_items7), dtype=bool)
    rr = cand_m[okm]
    cc = np.repeat(np.flatnonzero(okm)[:, None], K7 + 1, axis=1)
    m_elig[rr.ravel(), cc.ravel()] = True
    m_hit = float(hit_at_1_both_tie_conventions(nuis, m_elig, GOLD7)["hit_exp"][okm].mean())
    m_know = float(hit_at_1_both_tie_conventions(Sq7, m_elig, GOLD7)["hit_exp"][okm].mean())
    assert u_hit > 4.0 * chance7, ("the nuisance channel does not win the unmatched pool: %.4f "
                                   "against that pool's own chance %.4f" % (u_hit, chance7))
    assert m_hit < u_hit / 2.0, ("matching failed to neutralise the nuisance channel: %.4f -> %.4f"
                                 % (u_hit, m_hit))
    assert m_know > 0.99, "the matched pool is not winnable by a knowing arm: %.4f" % m_know
    assert mdiag["validity"]["ok"], (
        "THE MATCHED POOL ADMITS A WINNING CONSTANT: fitted oracle %.4f against chance %.4f. "
        "This is the 2026-08-16 defect; do not weaken this assertion to make it pass."
        % (mdiag["validity"]["oracle_constant_hit_exp"], mdiag["validity"]["chance"]))
    res["S7_matched_pool_neutralises_a_nuisance_channel"] = {
        "nuisance_unmatched": round(u_hit, 4), "nuisance_matched": round(m_hit, 4),
        "known_answer_matched": round(m_know, 4), "match_diag": mdiag}

    # S8 -- NEGATIVE CONTROL FOR S7's NEW ASSERTION. The check above is only worth having if it
    # can fire. Run the SAME inputs through the construction that shipped until 2026-08-16 and
    # require that the validity check REJECTS it. If this ever starts passing, the check has been
    # weakened and S7 no longer means anything.
    cand_l, _gl, _dl = _matched_candidate_sets_NEAREST_K_LEGACY(dg7, gold_sets7, excl7, keep7,
                                                                K7, 9, nuis)
    legacy = pool_admits_a_winning_constant(cand_l, gold_sets7, n_anchors7, K7)
    assert not legacy["ok"], (
        "the NEGATIVE CONTROL passed: the known-broken nearest-k pool was NOT rejected "
        "(fitted oracle %.4f, chance %.4f). The validity check is inert."
        % (legacy["oracle_constant_hit_exp"], legacy["chance"]))
    assert legacy["oracle_constant_hit_exp"] > 3.0 * chance7, (
        "the legacy pool no longer reproduces the defect at scale: %.4f vs chance %.4f"
        % (legacy["oracle_constant_hit_exp"], chance7))
    res["S8_negative_control_legacy_pool_is_rejected"] = {
        "legacy_oracle_constant_hit_exp": legacy["oracle_constant_hit_exp"],
        "fixed_oracle_constant_hit_exp": mdiag["validity"]["oracle_constant_hit_exp"],
        "chance": legacy["chance"], "legacy_rejected": not legacy["ok"]}

    print("[floor_battery.self-test] PASS " + json.dumps(res), flush=True)
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    print(__doc__)
    print("REQUIRED FLOOR SET: " + ", ".join(FLOOR_SET_REQUIRED), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
