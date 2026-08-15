"""AUDITOR RECOMPUTE (not a pre-registered cell; wires nothing; changes no hdlab default).

Adds the ORTHOGRAPHIC/STRING-FORM floor the ledger-validity audit (2026-08-15,
tools/ledger_validity_audit.py) found missing from M25 (exp_graded_divisive_comparator_v1). M25 is
SOUND IN ITS OWN CURRENCY (n=4000, chance 0.5, real positive control, PRIMARY-LIVE delta CI-separated
at +0.0602 [+0.044,+0.076]) but was scored SOFT because its corpus is simplewiki real words (vocab
2377 anchor words used here) and no trigram/spelling-alone arm had been run.

TASK SHAPE DIFFERS FROM THE C3 FAMILY: C3-style cells ask "given a lemma L, which anchor means the
same thing" -- the query IS a spelled word, so A6_TRIGRAM_ONLY (tools/orthographic_floor_vet_v1.py)
compares the QUERY WORD's own spelling to CANDIDATE spellings directly. M25 (inherited from its
PARENT, exp_context_conditioned_near_neighbour_v1) is a 2AFC near-neighbour-in-CONTEXT task: given a
sentence with TARGET and DISTRACTOR masked out, which of the two (both already spelled out as
candidates) fits the visible context. There is no single "query word" to compare spellings against.
The construction is therefore ADAPTED, not copied verbatim: character-trigram-hash the VISIBLE
CONTEXT (the same masked kept-word set the real queries use, via the module's own _kept_words) into
one query bag, and character-trigram-hash TARGET and DISTRACTOR each on their own (same "^word$"
per-word construction A6_TRIGRAM_ONLY uses) -- then pick whichever candidate's spelling shares more
character-trigrams with the surrounding VISIBLE text. This is the direct 2AFC analogue of "does a
spell-checker with no meaning already know the answer" for a discrimination task: zero embeddings,
zero substrate signal, same masking, same items, same 2AFC scorer (module.score_arm's tie-break
convention) and the module's own paired_bootstrap for the CI.

SCORER/ITEM REUSE (zero reimplementation): items come from PARENT.build_corpus_assets /
split_pools / build_items, byte-identical to what M25.run() uses (M25 imports PARENT wholesale for
exactly this reason -- "arithmetic is the only difference" is the parent cell's own stated invariant,
and this script inherits that same invariant for its comparison arm). LIVE (A_SSN) and PRIMARY
(A_GGZ) are recomputed via M25's own _signed / _graded / _sign_anchor / _normalise / _cos_rows /
score_arm so the ORTHO arm sits in the SAME paired_bootstrap alongside them, on the SAME items.

Run:  .venv/Scripts/python.exe tools/orthographic_floor_comparator_v1.py
Output: data/exp_orthographic_floor_comparator_v1/metrics.json (atomic os.replace, ts_iso).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
# DISCLOSURE (found while authoring this script, 2026-08-15): hdlab/reading_grounding_loop.py
# commit 38f7a0d5c (2026-08-14) flipped context_vector_masked's default to graded=True (the graded
# comparator is now ON by default on the live reading path -- it wires exactly the capability M25
# measured). M25's own module-scope self-test (_instrumentation_selftest, its "LOAD-BEARING
# NON-FORK CONTROL") calls context_vector_masked WITHOUT graded=False and now FAILS AT IMPORT
# (AssertionError: "_signed FORKED hdlab.context_vector_masked"), independent of anything in this
# script -- reproduced with a bare `import experiments.exp_graded_divisive_comparator_v1`. The
# commit message documents HD_GRADED_COMPARATOR=0 as the sanctioned switch for byte-identical
# pre-2026-08-14 behaviour; setting it here restores M25's self-test to PASS and its LIVE/PRIMARY
# arms to bit-identical reproduction of the landed 0.6395 / 0.69975 (verified below). Not a
# workaround invented for this script -- it is M25's OWN documented compatibility switch, applied
# because M25's non-fork assumption (LIVE == hdlab's current default) was invalidated by a later,
# unrelated commit, not by anything wrong in M25 itself.
os.environ["HD_GRADED_COMPARATOR"] = "0"

import hashlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_context_conditioned_near_neighbour_v1 as PARENT  # noqa: E402
import experiments.exp_graded_divisive_comparator_v1 as M25  # noqa: E402

ANCHOR_NAME = "orthographic_floor_comparator_v1"
OUT = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
TRIGRAM_DIM = 512  # matches exp_meaning_supply_separation_v1.TRIGRAM_DIM / relinfer-family floor width
ORTHO_ARM = "H_ORTHO_TRIGRAM"


def _word_trigram(w: str, dim: int = TRIGRAM_DIM) -> np.ndarray:
    v = np.zeros(dim, dtype=np.float64)
    s = "^" + w.lower() + "$"
    for k in range(len(s) - 2):
        j = int.from_bytes(hashlib.sha256(s[k:k + 3].encode("utf-8")).digest()[:4], "big") % dim
        v[j] += 1.0
    n = float(np.linalg.norm(v))
    return v / n if n >= 1e-9 else v


def _text_trigram(words, dim: int = TRIGRAM_DIM) -> np.ndarray:
    """Trigram bag over the VISIBLE (kept, target/distractor-masked) context words -- the same
    masking M25's real queries use, joined into one string, hashed the same way as a single word."""
    v = np.zeros(dim, dtype=np.float64)
    s = "^" + " ".join(words).lower() + "$"
    for k in range(len(s) - 2):
        j = int.from_bytes(hashlib.sha256(s[k:k + 3].encode("utf-8")).digest()[:4], "big") % dim
        v[j] += 1.0
    n = float(np.linalg.norm(v))
    return v / n if n >= 1e-9 else v


def main() -> int:
    t0 = time.time()
    assets = PARENT.build_corpus_assets()
    profile_pool, eval_pool = PARENT.split_pools(assets["buckets"])
    items, item_diag = PARENT.build_items(assets["pairs_strict"], eval_pool, M25.MAX_ITEMS)
    n = len(items)
    print("[items] n=%d elapsed=%.1fs" % (n, time.time() - t0), flush=True)
    if n < M25.MIN_ITEMS:
        raise AssertionError("only %d items (floor %d)" % (n, M25.MIN_ITEMS))

    words_used = sorted({w for it in items for w in (it["target"], it["distractor"])})
    wpos = {w: i for i, w in enumerate(words_used)}
    nw = len(words_used)

    # ---- LIVE (A_SSN) and PRIMARY (A_GGZ) anchors, M25's own encoders, one pass ----
    d = M25.CTX_D
    sum_S = np.zeros((nw, d), dtype=np.float64)
    sum_G = np.zeros((nw, d), dtype=np.float64)
    for i, w in enumerate(words_used):
        drop = frozenset({w})
        for sent in profile_pool.get(w, ()):
            sum_S[i] += M25._signed(sent, drop)
            sum_G[i] += M25._graded(sent, drop)
        if (i + 1) % 500 == 0:
            print("[anchors] %d/%d elapsed=%.1fs" % (i + 1, nw, time.time() - t0), flush=True)
    A_SS = np.stack([M25._sign_anchor(sum_S[i]) for i in range(nw)])
    A_GG = sum_G
    amu, asd = A_GG.mean(axis=0), A_GG.std(axis=0)
    A_GGZ = M25._normalise(A_GG, amu, asd, "Z")
    print("[anchors] done nw=%d elapsed=%.1fs" % (nw, time.time() - t0), flush=True)

    # ---- ORTHO word-trigram "anchors": one per candidate word, single-word construction ----
    A_ORTHO = np.stack([_word_trigram(w) for w in words_used])

    # ---- queries: S (for LIVE), G (for PRIMARY, pool-normalised), and kept-word list (for ORTHO) ----
    Q_S = np.zeros((n, d), dtype=np.float64)
    Q_G = np.zeros((n, d), dtype=np.float64)
    Q_ORTHO = np.zeros((n, TRIGRAM_DIM), dtype=np.float64)
    qs_G, qs_G2 = np.zeros(d), np.zeros(d)
    n_prof_sent = 0
    for w in words_used:
        for sent in profile_pool.get(w, ()):
            vg = M25._graded(sent, frozenset({w}))
            qs_G += vg
            qs_G2 += vg * vg
            n_prof_sent += 1
    qmu_G = qs_G / max(1, n_prof_sent)
    qsd_G = np.sqrt(np.maximum(qs_G2 / max(1, n_prof_sent) - qmu_G ** 2, 0.0))

    for i, it in enumerate(items):
        drop = frozenset({normalize_lemma(it["target"]), normalize_lemma(it["distractor"]),
                           it["target"], it["distractor"]})
        Q_S[i] = M25._signed(it["sentence"], drop)
        Q_G[i] = M25._graded(it["sentence"], drop)
        kept = M25._kept_words(it["sentence"], drop)
        Q_ORTHO[i] = _text_trigram(kept)
    Q_GZ = M25._normalise(Q_G, qmu_G, qsd_G, "Z")
    print("[queries] n=%d elapsed=%.1fs" % (n, time.time() - t0), flush=True)

    # ---- score LIVE, PRIMARY, ORTHO with M25's own 2AFC scorer ----
    correct = {}
    diag = {}
    correct[M25.LIVE_ARM], diag[M25.LIVE_ARM] = M25.score_arm(items, wpos, A_SS, Q_S)
    correct[M25.PRIMARY_ARM], diag[M25.PRIMARY_ARM] = M25.score_arm(items, wpos, A_GGZ, Q_GZ)
    correct[ORTHO_ARM], diag[ORTHO_ARM] = M25.score_arm(items, wpos, A_ORTHO, Q_ORTHO)
    accs = {k: float(v.mean()) for k, v in correct.items()}
    print("[arms] %s" % json.dumps({k: round(v, 4) for k, v in accs.items()}), flush=True)

    landed_live, landed_primary = 0.6395, 0.69975
    reproduction_ok = (abs(accs[M25.LIVE_ARM] - landed_live) < 1e-6
                        and abs(accs[M25.PRIMARY_ARM] - landed_primary) < 1e-6)

    keys = [M25.LIVE_ARM, M25.PRIMARY_ARM, ORTHO_ARM]
    contrasts = [
        ("d_PRIMARY_minus_ORTHO", M25.PRIMARY_ARM, ORTHO_ARM),
        ("d_LIVE_minus_ORTHO", M25.LIVE_ARM, ORTHO_ARM),
        ("d_ORTHO_minus_CHANCE", ORTHO_ARM, "__CHANCE__"),
        ("d_PRIMARY_minus_LIVE", M25.PRIMARY_ARM, M25.LIVE_ARM),
    ]
    bs = M25.paired_bootstrap(correct, keys, 5000, 20260815, contrasts)

    clears_primary = bool(bs["deltas"]["d_PRIMARY_minus_ORTHO"]["ci_excludes_zero"]
                           and bs["deltas"]["d_PRIMARY_minus_ORTHO"]["delta"] > 0.0)
    clears_live = bool(bs["deltas"]["d_LIVE_minus_ORTHO"]["ci_excludes_zero"]
                        and bs["deltas"]["d_LIVE_minus_ORTHO"]["delta"] > 0.0)

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "AUDITOR RECOMPUTE: trigram-only ORTHO arm (visible-context-vs-candidate-spelling, "
                "zero substrate signal) added to M25's own paired_bootstrap alongside re-derived "
                "LIVE and PRIMARY",
        "target_cell": "exp_graded_divisive_comparator_v1",
        "compares_against": {"landed_metrics": "data/exp_graded_divisive_comparator_v1/metrics.json",
                              "landed_LIVE_A_SSN": landed_live, "landed_PRIMARY_A_GGZ": landed_primary},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "reproduction_check": {"recomputed_LIVE": accs[M25.LIVE_ARM],
                                "recomputed_PRIMARY": accs[M25.PRIMARY_ARM],
                                "exact_match": reproduction_ok},
        "n_items": n, "n_anchors": nw, "chance": 0.5,
        "arm_accuracy": accs,
        "ortho_arm_construction": "trigram bag over VISIBLE (target/distractor-masked) context words "
                                   "vs single-word trigram of TARGET / DISTRACTOR spelling; same 2AFC "
                                   "tie-break as score_arm; TRIGRAM_DIM=%d" % TRIGRAM_DIM,
        "bootstrap": bs,
        "clears_ortho_floor_ci_separated": {"PRIMARY_vs_ORTHO": clears_primary,
                                            "LIVE_vs_ORTHO": clears_live},
        "item_construction": item_diag,
        "elapsed_s": round(time.time() - t0, 2),
    }
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print("[verdict] LIVE=%.4f PRIMARY=%.4f ORTHO=%.4f | d(PRIMARY-ORTHO)=%.4f CI=[%.4f,%.4f] "
          "clears=%s | d(LIVE-ORTHO)=%.4f CI=[%.4f,%.4f] clears=%s"
          % (accs[M25.LIVE_ARM], accs[M25.PRIMARY_ARM], accs[ORTHO_ARM],
             bs["deltas"]["d_PRIMARY_minus_ORTHO"]["delta"], bs["deltas"]["d_PRIMARY_minus_ORTHO"]["ci_lo"],
             bs["deltas"]["d_PRIMARY_minus_ORTHO"]["ci_hi"], clears_primary,
             bs["deltas"]["d_LIVE_minus_ORTHO"]["delta"], bs["deltas"]["d_LIVE_minus_ORTHO"]["ci_lo"],
             bs["deltas"]["d_LIVE_minus_ORTHO"]["ci_hi"], clears_live), flush=True)
    print("WROTE", p, flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        os.makedirs(OUT, exist_ok=True)
        crash = {"anchor_name": ANCHOR_NAME, "error": "%s: %s" % (type(exc).__name__, exc),
                  "traceback": traceback.format_exc(), "ts_iso": datetime.now(timezone.utc).isoformat()}
        p = os.path.join(OUT, "_crash_diagnostic.json")
        with open(p + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(crash, fh, indent=2)
        os.replace(p + ".tmp", p)
        raise
