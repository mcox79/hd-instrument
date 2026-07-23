#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_reversible_role_relational_case_sleep_v1

DECISIVE TEST: does the atomize+sleep consolidation loop (case+sleep CLS mechanism, per-cluster
rule-vs-episodic gate) learn a GENUINE STRUCTURAL RULE, or does it always reduce to a
similarity-vote? USER-routed task (2026-07-23): the parser/PP-attach loop
(exp_parser_selfimprove_case_sleep_ppattach_v1, atom-lineage 29480) tilted toward SIMILARITY
(+0.047 over kNN, seed-fragile, 89-95% kNN-agreement). TWO hypotheses for why:
  H1-task:    PP-attachment is intrinsically similarity-shaped (bad TASK).
  H2-learner: the centroid/linear consolidation is inherently similarity-shaped regardless
              of task (bad LEARNER).
This cell tests BOTH by moving to the DISCRIMINATING task with a representation that CAN
express beyond-similarity structure.

TASK: REVERSIBLE (non-canonical) THEMATIC-ROLE ASSIGNMENT (AGENT vs PATIENT), realized as the
  classic psycholinguistic ACTIVE/PASSIVE reversible-sentence paradigm (Bever 1970 Canonical
  Sentence Strategy; Caramazza & Zurif 1976 agrammatic-aphasia passive-comprehension deficits --
  patients who lose sensitivity to the passive morphosyntactic marker default to an agent-first
  heuristic and fail EXACTLY on reversible passives, succeed on actives and on semantically
  IRREVERSIBLE sentences). For a FIXED lexeme pair (mention1, mention2) and verb V, we realize
  BOTH voices:
    ACTIVE:  "mention1 V-ed mention2"          -> gold = MENTION1_AGENT
    PASSIVE: "mention1 was V-ed by mention2"   -> gold = MENTION2_AGENT
  mention1/mention2 IDENTITY is IDENTICAL across the pair (same two real lexemes, same verb);
  ONLY the voice marker (is_passive) differs, and gold FLIPS. This is the discriminating
  construction: a representation that reads only lexical content (mention1, mention2, verb) is
  BIT-IDENTICAL between the active and passive realization of the same pair, yet gold differs --
  a surface-similarity vote FAILS BY CONSTRUCTION (not merely empirically near-chance, as in
  29480's PP-attachment, but EXACTLY chance-forced by the construction).

REAL LEXEMES (per task pointer: "a controlled reversible set with real lexemes"): 48 real English
  animate common nouns (predator/authority to prey/subordinate, a real-world animacy-salience
  ordering used ONLY to bias the BASELINE heuristic below, never to compute gold) x 24 real
  English bidirectionally-plausible transitive action verbs (chase, bite, kick, ...).

BASELINE (the naive heuristic being corrected -- REAL, non-circular, brain-grounded):
  baseline_predict(mention1, mention2) = MENTION1_AGENT if status[mention1] >= status[mention2]
  else MENTION2_AGENT -- a VOICE-BLIND animacy/status heuristic (Bever's Canonical Sentence
  Strategy / agent-first default; ignores the passive marker entirely, exactly the documented
  agrammatic-aphasia failure mode). is_fail = (baseline_pred != gold_class). By construction,
  EXACTLY ONE of {active, passive} fails per pair (baseline is voice-invariant, gold is not) --
  every pair contributes exactly one seen/held error, and is_fail's gold_class is a DETERMINISTIC
  function of is_passive (gold=MENTION2_AGENT iff is_passive) -- a real, non-degenerate,
  50/50-ish mix of BOTH gold classes within the failure set (unlike a trivial single-class error
  surface), giving the per-cluster purity gate genuine work to do.

RELATIONAL SIGNATURE (per atom 29441 "role-binding relational feature... unbind-compare role
  features that EXPRESS beyond-similarity relations, where surface-kNN sits at chance"; the
  representation atom 29441 showed the substrate's HD algebra CAN express): HD role-BINDING
  (bipolar bind = elementwise multiply, per CLAUDE.md substrate-primitive convention) of each
  mention's lexeme code to its STRUCTURAL SLOT (ROLE_MENTION1 / ROLE_MENTION2), PLUS a
  role-bound VOICE marker (ROLE_VOICE bound to VOICE_CODE[is_passive], weighted x3 to give the
  only cross-instance-recurring signal a fair chance against per-instance lexeme noise), plus an
  unbound verb code:
    rel_sig = bind(ROLE_MENTION1, code(mention1)) + bind(ROLE_MENTION2, code(mention2))
              + 3.0 * bind(ROLE_VOICE, VOICE_CODE[is_passive]) + code(verb)
  This is fed to the SAME CLS case+sleep + per-cluster rule-vs-episodic gate mechanism as 29480
  (hdlab.continual.replay_cycle Hebbian consolidation; hdlab.schema_exemplar_bayes clustering;
  hdlab.glass_box_loop.cleanup_with_margin readout) -- ONE variable changed: the case SIGNATURE
  (relational/role-bound here vs surface-centroid in 29480), not the learner.

SURFACE-SIMILARITY-VOTE CONTROL (the primary, must-be-able-to-win discriminator; SAME raw input,
  no role-binding, no voice term -- literal lexical-content bag, matching 29480's surface
  features): surf_sig = code(mention1) + code(mention2) + code(verb). This is BIT-IDENTICAL
  between the active and passive realization of the same pair (voice excluded) -- a kNN vote over
  surf_sig is FORCED to chance on the discriminator by construction, not merely empirically weak.

RIGOR ADDITION informed directly by atom 29441's own caveat ("LEVER IS REPRESENTATION NOT
  LEARNER: kNN over the SAME hand-built relational features TIES the learned readout"): this
  cell ALSO runs ARM_KNN_RELATIONAL (a parameter-free kNN vote over the SAME rel_sig, no
  consolidation/learning at all) as a DIAGNOSTIC (not a HARD_PASS/HARD_FAIL gate -- the
  pre-registered headline gate is vs SURFACE similarity, per the task spec). If
  ARM_KNN_RELATIONAL ties CLUSTER_GATED, that reproduces 29441's exact lesson here too
  (representation carries the win, sleep-consolidation's LEARNING contribution is not shown
  load-bearing) and is reported HONESTLY regardless of the headline verdict.

BANDS (pre-registered BEFORE this run):
  HARD_PASS_REAL_STRUCTURAL_RULE: scramble_collapse >= 0.15 AND all-seed coherent net_gain > 0
    AND rescue_precision >= 0.60 AND leak_clean AND zero_cycles |net_gain| <= 0.02 AND coherent
    BEATS surface_knn DECISIVELY (margin >= 0.30 absolute net_gain, all seeds strictly greater
    fix_rate) AND coherent BEATS memorize DECISIVELY (margin >= 0.30, all seeds strictly greater).
  HARD_FAIL_SIMILARITY_COLLAPSE (H2 confirmed even here -- report honestly, reshapes the plan):
    ANY of coherent net_gain <= 0 OR coherent fix_rate < 0.10 OR scramble does not collapse
    (< 0.05) OR coherent does NOT beat surface_knn with margin (< 0.05, i.e. ties/loses -- the
    29440/29480 trap fires again on a task explicitly built to prevent it) OR does not beat
    memorize with margin.
  MIDDLE_BAND: otherwise (genuine but partial signal; localize which condition failed).
  DIAGNOSTIC (non-gating, reported): relational_knn_ties_cluster_gated = True if
    |beat_relational_knn_margin| < 0.02 -- per atom 29441, this qualifies (does not overturn) a
    HARD_PASS as "representation-driven, learning-contribution unproven."

BRAIN-CHECK: the baseline IS the documented brain failure mode (agrammatic aphasia loses passive
  comprehension, defaults to agent-first/canonical-order heuristic -- Caramazza & Zurif 1976;
  Grodzinsky 1986 Trace-Deletion Hypothesis). Healthy comprehenders use the passive morphosyntactic
  marker (a real structural/relational cue, not similarity) to correctly reassign roles on
  reversible passives -- exactly the capability this cell tests for in the substrate.

COMPUTE ARCHITECTURE: class (b) sequential-CPU (justified: pure HD arithmetic over <=300 seen +
  <=160 held instances x 3 seeds x 5 cycle-counts x ~6 arms; N_SIG=1024 dense vectors, no
  GPU-batchable primitive at this scale; wall budget < 2min). Storage: dense superposition
  (cortical W, per-cluster rule centroids) + near-exact episodic fallback; no external corpus,
  no hdlab mutation (compose-in-cell only). LOCAL-ONLY, foreground-to-completion; NO queue, NO
  push, NO remote-persist, NO git add of data/, NO atom bank (skunkworks VETs). Deterministic:
  OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng, hashlib feature codes (no hash()-seeded
  RNG), sorted() splits (no list(set()) ordering). progress_logging: print_flush_true.

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground measurement cell):
  - arms_differ_verified at smoke gate (hash test over per-arm predicted-class tuples)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: generalization fix-rate measurement; noise floor = 1/n_heldout_fail reported
  - baseline_in_band: baseline (voice-blind status heuristic) accuracy on held in (0.05, 0.95)
  - discriminator survives scale: smoke uses FULL-scale n_pairs (only fewer seeds) -- option (A)
  - cardinality_ok: EXPECTED per-seed rows = len(seeds); verdict counts len(per_seed)
  - calibration_check: adaptive_with_discriminator_gate (tau on SEEN net_gain; controls fire)
  - N-suffix: anchor name has no _n<NUMBER> suffix; production N_SIG=1024 (CLAUDE.md default HD
    dimensionality); rationale: safety margin against Hebbian crosstalk given ~150-300 stored
    role-bound cases sharing one dense W.
  - all numbers in this docstring are HYPOTHESIZED (pre-registration, not yet measured); every
    number in the verdict/metrics is MEASURED@ the on-disk metrics.json this run produces.
  - deterministic_seeding: true; progress_logging: print_flush_true
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import inspect as _insp
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ANCHOR_NAME = "reversible_role_relational_case_sleep_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

N_SIG = 1024
DG_DIM = 2048
SPARSITY = 0.02
ROLES = ("MENTION1_AGENT", "MENTION2_AGENT")
K_KNN = 5
VOICE_WEIGHT = 3.0

# ---- Pre-registered bands (set BEFORE this run; see docstring) ------------------------
SCRAMBLE_COLLAPSE_MIN = 0.15
RESCUE_PRECISION_MIN = 0.60
ZERO_CYCLES_FLAT_MAX = 0.02
BEAT_MARGIN_HARD_PASS = 0.30
BEAT_MARGIN_HARD_FAIL = 0.05
FIX_RATE_FLOOR = 0.10
CYCLES_CURVE = [0, 1, 2, 3, 6]
RELATIONAL_KNN_TIE_THRESH = 0.02

# ========================================================================================
# REAL LEXEME VOCABULARY (real English words; status = animacy/authority-salience ordering,
# used ONLY to bias the BASELINE heuristic -- never referenced by gold_class computation).
# ========================================================================================
ANIMATE_NOUNS = [
    "king", "general", "hunter", "wolf", "lion", "tiger", "eagle", "chief", "warrior", "farmer",
    "teacher", "captain", "doctor", "soldier", "fox", "bear", "hawk", "sailor", "driver", "guard",
    "man", "woman", "dog", "cat", "horse", "monkey", "goat", "sheep", "deer", "rabbit",
    "mouse", "bird", "child", "boy", "girl", "student", "servant", "clerk", "mule", "duck",
    "frog", "chicken", "kitten", "puppy", "lamb", "calf", "ant", "beetle",
]
VERBS = [
    "chase", "bite", "kick", "push", "pull", "hit", "greet", "hug", "scratch", "nudge",
    "watch", "follow", "tackle", "grab", "catch", "poke", "splash", "trip", "block", "startle",
    "surprise", "wake", "meet", "join",
]
STATUS = {n: float(s) for n, s in zip(ANIMATE_NOUNS, np.linspace(1.0, 0.0, len(ANIMATE_NOUNS)))}


def baseline_predict(mention1, mention2):
    """Voice-BLIND animacy/status heuristic (Bever's Canonical Sentence Strategy / the documented
    agrammatic-aphasia agent-first default). Never reads is_passive or gold_class."""
    return "MENTION1_AGENT" if STATUS[mention1] >= STATUS[mention2] else "MENTION2_AGENT"


def lexeme_verb_split(nouns, verbs, seed, frac_seen=0.6):
    """Lexeme-DISJOINT + verb-DISJOINT split (both nouns AND verb of a held instance are never
    seen in the SEEN set) -- the strongest generalization bar available here."""
    nouns_sorted = sorted(nouns)
    verbs_sorted = sorted(verbs)
    rng = np.random.default_rng(seed)
    n_perm = rng.permutation(len(nouns_sorted))
    v_perm = rng.permutation(len(verbs_sorted))
    n_seen_n = int(round(frac_seen * len(nouns_sorted)))
    n_seen_v = int(round(frac_seen * len(verbs_sorted)))
    seen_nouns = sorted(nouns_sorted[j] for j in n_perm[:n_seen_n])
    held_nouns = sorted(nouns_sorted[j] for j in n_perm[n_seen_n:])
    seen_verbs = sorted(verbs_sorted[j] for j in v_perm[:n_seen_v])
    held_verbs = sorted(verbs_sorted[j] for j in v_perm[n_seen_v:])
    return seen_nouns, held_nouns, seen_verbs, held_verbs


def make_instances(nouns_pool, verbs_pool, n_pairs, seed):
    """Generate n_pairs distinct unordered lexeme pairs from nouns_pool x verbs_pool; each pair
    realized in BOTH voices (active + passive) -- the reversible pair. Deterministic (sorted
    pools, no hash()/list(set()) ordering)."""
    nouns_sorted = sorted(nouns_pool)
    verbs_sorted = sorted(verbs_pool)
    rng = np.random.default_rng(seed)
    idx_pairs = set()
    attempts = 0
    max_pairs = len(nouns_sorted) * (len(nouns_sorted) - 1) // 2
    n_pairs = min(n_pairs, max_pairs)
    while len(idx_pairs) < n_pairs and attempts < n_pairs * 80 + 200:
        i, j = rng.integers(0, len(nouns_sorted), size=2)
        attempts += 1
        if i == j:
            continue
        lo, hi = (int(i), int(j)) if i < j else (int(j), int(i))
        idx_pairs.add((lo, hi))
    idx_pairs = sorted(idx_pairs)
    out = []
    for pair_id, (i, j) in enumerate(idx_pairs):
        mention1, mention2 = nouns_sorted[i], nouns_sorted[j]
        verb = verbs_sorted[int(rng.integers(0, len(verbs_sorted)))]
        pred = baseline_predict(mention1, mention2)
        for is_passive in (False, True):
            gold = "MENTION2_AGENT" if is_passive else "MENTION1_AGENT"
            out.append(dict(
                pair_id=pair_id, mention1_lemma=mention1, mention2_lemma=mention2,
                verb_lemma=verb, is_passive=bool(is_passive), gold_class=gold,
                pred_class=pred, is_fail=bool(pred != gold),
                key="%s|%s|%s|%s" % (mention1, mention2, verb, is_passive),
            ))
    return out


# ========================================================================================
# HD signatures: RELATIONAL (role-binding, per atom 29441) vs SURFACE (bag, no role-binding).
# ========================================================================================
_FEAT_CACHE = {}


def _feat_code(f):
    v = _FEAT_CACHE.get(f)
    if v is None:
        seed = int.from_bytes(hashlib.sha256(f.encode("utf-8")).digest()[:8], "big")
        v = (np.random.default_rng(seed).integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0)
        _FEAT_CACHE[f] = v
    return v


ROLE_MENTION1 = _feat_code("STRUCT_ROLE_MENTION1")
ROLE_MENTION2 = _feat_code("STRUCT_ROLE_MENTION2")
ROLE_VOICE = _feat_code("STRUCT_ROLE_VOICE")
VOICE_CODE = {False: _feat_code("VOICE_ACTIVE"), True: _feat_code("VOICE_PASSIVE")}


def relational_sig(inst):
    """Role-BINDING relational feature (atom 29441 lineage): bind = elementwise multiply
    (bipolar substrate primitive). Encodes WHICH lexeme is bound to WHICH structural slot AND
    the voice marker -- beyond-similarity relational structure a bag-of-lemmas cannot express."""
    v = (ROLE_MENTION1 * _feat_code("lem:" + inst["mention1_lemma"])
         + ROLE_MENTION2 * _feat_code("lem:" + inst["mention2_lemma"])
         + VOICE_WEIGHT * (ROLE_VOICE * VOICE_CODE[inst["is_passive"]])
         + _feat_code("verb:" + inst["verb_lemma"]))
    return v.astype(np.float32)


def surface_sig(inst):
    """SURFACE bag-of-lemmas (NO role-binding, NO voice) -- BIT-IDENTICAL between the active and
    passive realization of the same (mention1, mention2, verb) pair. The must-fail-by-
    construction control representation."""
    v = (_feat_code("lem:" + inst["mention1_lemma"])
         + _feat_code("lem:" + inst["mention2_lemma"])
         + _feat_code("verb:" + inst["verb_lemma"]))
    return v.astype(np.float32)


def _leak_probe(instances, n=200):
    src = _insp.getsource(relational_sig) + _insp.getsource(surface_sig)
    src_clean = ("gold_class" not in src) and ("pred_class" not in src) and ("is_fail" not in src)
    ok = True
    for inst in instances[:n]:
        r1, s1 = relational_sig(inst), surface_sig(inst)
        mutant = dict(inst, gold_class=("MENTION1_AGENT" if inst["gold_class"] == "MENTION2_AGENT"
                                         else "MENTION2_AGENT"),
                      pred_class=("MENTION1_AGENT" if inst["pred_class"] == "MENTION2_AGENT"
                                  else "MENTION2_AGENT"))
        r2, s2 = relational_sig(mutant), surface_sig(mutant)
        if not (np.array_equal(r1, r2) and np.array_equal(s1, s2)):
            ok = False
    return bool(ok and src_clean)


def _surface_identical_across_voice_probe(instances):
    """Verifies the by-construction property: surf_sig is BIT-IDENTICAL between active/passive
    of the same pair (the must-fail-by-construction discriminator), while rel_sig DIFFERS."""
    by_pair = {}
    for inst in instances:
        by_pair.setdefault(inst["pair_id"], []).append(inst)
    n_checked = 0
    for pair_id, pair_insts in by_pair.items():
        if len(pair_insts) != 2:
            continue
        a, b = pair_insts
        assert a["is_passive"] != b["is_passive"]
        s_a, s_b = surface_sig(a), surface_sig(b)
        r_a, r_b = relational_sig(a), relational_sig(b)
        assert np.array_equal(s_a, s_b), "surf_sig must be BIT-IDENTICAL across voice (by construction)"
        assert not np.array_equal(r_a, r_b), "rel_sig must DIFFER across voice (encodes the marker)"
        n_checked += 1
    return n_checked


# ========================================================================================
# CLS SLEEP store: dense Hebbian superposition W via hdlab.continual.replay_cycle (transcribed
# usage pattern from exp_parser_selfimprove_case_sleep_ppattach_v1.py, same mechanism, new
# signature space; NO hdlab mutation).
# ========================================================================================
def build_role_codebook(roles, seed=1234):
    rng = np.random.default_rng(seed)
    return {r: (rng.integers(0, 2, size=N_SIG).astype(np.float32) * 2.0 - 1.0) for r in roles}


def consolidate_store(case_sigs, case_roles, role_codebook, *, n_cycles, replay_frac, seed=7):
    import torch
    from hdlab.continual import replay_cycle
    keys = torch.from_numpy(np.asarray(case_sigs, dtype=np.float32))
    values = torch.from_numpy(np.asarray([role_codebook[r] for r in case_roles], dtype=np.float32))
    m = keys.shape[0]
    replay_idx = torch.from_numpy(np.arange(m).astype(np.int64))
    W = torch.zeros((N_SIG, N_SIG), dtype=torch.float32)
    torch.manual_seed(seed)
    for _ in range(int(n_cycles)):
        replay_cycle(W, replay_idx, keys, values, replay_frac=replay_frac, lr=1.0)
    return W.numpy()


def store_predict(W, role_codebook, roles, sig):
    from hdlab.glass_box_loop import cleanup_with_margin
    rs = (W @ sig.astype(np.float32))
    nrm = float(np.linalg.norm(rs))
    if nrm > 1e-9:
        rs = rs / nrm
    codebook = np.asarray([role_codebook[r] for r in roles], dtype=np.float32)
    idx, margin = cleanup_with_margin(rs, codebook)
    return roles[idx], margin


def knn_predict(seen_sigs, seen_roles, sig, k=K_KNN):
    """Parameter-free surface-similarity control (the '29440/29480 trap'): cosine-sim k-NN
    majority vote over SEEN case signatures. Generic over sig space (surface OR relational --
    used for BOTH the headline surface control and the relational-kNN diagnostic).

    MARGIN FIX (found during this cell's own smoke gate, 2026-07-23): the raw
    mean-top-k-cosine margin used by the 29480 template is NOT a confidence signal here --
    with a strong shared additive term (the voice component) present in EVERY relational-sig
    query regardless of correctness, mean-top-k-cosine stays uniformly high (~0.75-0.78) for
    BOTH correctly- and incorrectly-voting queries, so calibrate_tau (fit on SEEN) picks a tau
    that never fires on HELD -- both knn_surface AND knn_relational go flat at net_gain=0.0,
    which would make 'coherent BEATS knn' spuriously easy (knn crippled by miscalibration, not
    by genuine lack of signal) -- an unfair control. Fixed with a VOTE-margin: (2*winner_count -
    k)/k in [0,1], 0=unanimous-tie (no confidence), 1=unanimous vote (full confidence). Verified
    off-code before the FULL run: surface vote-margin on held ranges 0.2-1.0 (mean 0.355, noisy,
    matching its ~0.5 raw accuracy); relational vote-margin is a clean 1.0 for every held query
    (matching its ~1.0 raw accuracy) -- this metric properly discriminates confidence."""
    if not seen_sigs:
        return ROLES[0], 0.0
    sn = float(np.linalg.norm(sig)) + 1e-9
    sims = []
    for cs, cr in zip(seen_sigs, seen_roles):
        num = float(np.dot(cs, sig))
        den = (np.linalg.norm(cs) + 1e-9) * sn
        sims.append((num / den, cr))
    sims.sort(key=lambda x: -x[0])
    kk = min(k, len(sims))
    topk = sims[:kk]
    votes = Counter(r for _, r in topk)
    role, cnt = votes.most_common(1)[0]
    margin = float((2 * cnt - kk) / kk) if kk else 0.0
    return role, margin


def memorize_predict(memo_table, key, majority_role):
    """MEMORIZE floor: exact discrete (mention1,mention2,verb,is_passive) key lookup from SEEN.
    On a lexeme+verb-disjoint held-out split this can NEVER exact-match by construction."""
    if key in memo_table:
        return memo_table[key], 1.0
    return majority_role, 0.0


def calibrate_tau(predict_fn, seen):
    """EDGE-CASE FIX (found during this cell's own smoke gate, 2026-07-23): when a predict_fn's
    margins are DEGENERATE-CONSTANT (e.g. relational-kNN's vote-margin is a clean 1.0 for every
    unanimous top-k vote), the percentile grid collapses to the single candidate {max_margin},
    and eval_heldout's strict `margin > tau` can NEVER fire at tau==max_margin -- silently
    forcing net_gain=0.0 even when the predictor is perfectly informative. Always include an
    explicit 'always-override' floor candidate strictly below the minimum observed margin so
    this degenerate-but-legitimate (fully-confident) case is reachable."""
    margins = np.asarray([predict_fn(a)[1] for a in seen], dtype=np.float64)
    if margins.size == 0:
        return 0.0
    cand = sorted(set(float(np.percentile(margins, p)) for p in (0, 10, 20, 30, 40, 50, 60, 70, 80, 90)))
    cand = sorted(set(cand + [float(np.min(margins)) - 1e-6]))
    best_tau, best_gain = cand[0], -1e9
    for tau in cand:
        r = eval_heldout(predict_fn, seen, tau)
        g = r["net_gain"] if r["net_gain"] is not None else -1e9
        if g >= best_gain:
            best_gain, best_tau = g, tau
    return round(best_tau, 6)


def eval_heldout(predict_fn, held, tau):
    fixes = breaks = base_correct = loop_correct = overrides = 0
    n_fail = sum(1 for a in held if a["is_fail"])
    n_corr = len(held) - n_fail
    for a in held:
        rhat, margin = predict_fn(a)
        base_ok = (a["pred_class"] == a["gold_class"])
        base_correct += int(base_ok)
        net = a["pred_class"]
        if margin > tau and rhat != a["pred_class"]:
            net = rhat
            overrides += 1
        net_ok = (net == a["gold_class"])
        loop_correct += int(net_ok)
        if (not base_ok) and net_ok:
            fixes += 1
        if base_ok and (not net_ok):
            breaks += 1
    n = len(held)
    return {
        "n_heldout": n, "n_heldout_fail": n_fail, "n_heldout_correct": n_corr,
        "base_acc": round(base_correct / n, 4) if n else None,
        "loop_acc": round(loop_correct / n, 4) if n else None,
        "net_gain": round((loop_correct - base_correct) / n, 4) if n else None,
        "fixes": fixes, "breaks": breaks, "overrides": overrides,
        "heldout_fix_rate": round(fixes / n_fail, 4) if n_fail else None,
        "collateral_rate": round(breaks / n_corr, 4) if n_corr else None,
        "rescue_precision": round(fixes / (fixes + breaks), 4) if (fixes + breaks) else None,
    }


def _nz(x, default):
    """None-coalescing (NOT `x or default` -- a legitimate net_gain==0.0 is falsy in Python)."""
    return default if x is None else x


def _fast_seen_recall(seen_fail):
    if len(seen_fail) < 2:
        return None
    from hdlab.hippocampal_encoder import HippocampalEncoder
    X = np.asarray([a["rel_sig"] for a in seen_fail], dtype=np.float32)
    enc = HippocampalEncoder(input_dim=N_SIG, dg_dim=DG_DIM, sparsity=SPARSITY, seed=7)
    codes = enc.encode_and_write(X)
    ret = enc.retrieve(X, use_ca3=True, sparsify_after_settle=True)
    hits = sum(int(int(np.argmax(codes @ ret[i])) == i) for i in range(len(seen_fail)))
    return round(hits / len(seen_fail), 4)


# ========================================================================================
# PER-CLUSTER rule-vs-episodic gate (transcribed from exp_parser_selfimprove_case_sleep_
# ppattach_v1.py build_cluster_gated_store / cluster_gated_predict_factory / calibrate_tau_
# rule_only -- SAME mechanism, applied to the relational signature space here).
# ========================================================================================
PURITY_THRESH = 0.75
MIN_CLUSTER_SIZE = 3
EPISODIC_SIM_THRESH = 0.90


def build_cluster_gated_store(seen_fail, role_codebook, roles, *, n_cycles, replay_frac, seed=7):
    from hdlab.schema_exemplar_bayes import SchemaExemplarBayesIndex
    if len(seen_fail) < 6:
        return (np.zeros((N_SIG, N_SIG), dtype=np.float32), [], [],
                dict(n_clusters=0, n_rule_clusters=0, n_episodic_clusters=0,
                     n_rule_cases_abstracted=0, n_episodic_cases=len(seen_fail), clusters=[]))
    X = np.asarray([a["rel_sig"] for a in seen_fail], dtype=np.float32)
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    idx = SchemaExemplarBayesIndex(compression_ratio=5, seed=seed).fit(Xn)
    rule_sigs, rule_roles = [], []
    episodic_sigs, episodic_roles = [], []
    cluster_reports = []
    for c, fidxs in idx.schema_to_facts.items():
        members = [seen_fail[j] for j in fidxs]
        roles_in_cluster = [m["gold_class"] for m in members]
        maj_role, maj_count = Counter(roles_in_cluster).most_common(1)[0]
        purity = maj_count / len(members)
        is_rule = bool(len(members) >= MIN_CLUSTER_SIZE and purity >= PURITY_THRESH)
        cluster_reports.append(dict(cluster=int(c), size=len(members), purity=round(purity, 4),
                                    majority_role=maj_role, promoted_to_rule=is_rule))
        if is_rule:
            centroid = np.mean([m["rel_sig"] for m in members], axis=0).astype(np.float32)
            rule_sigs.append(centroid)
            rule_roles.append(maj_role)
        else:
            for m in members:
                episodic_sigs.append(m["rel_sig"])
                episodic_roles.append(m["gold_class"])
    if rule_sigs:
        W = consolidate_store(rule_sigs, rule_roles, role_codebook, n_cycles=n_cycles,
                              replay_frac=replay_frac, seed=seed)
    else:
        W = np.zeros((N_SIG, N_SIG), dtype=np.float32)
    n_rule = sum(1 for r in cluster_reports if r["promoted_to_rule"])
    summary = dict(n_clusters=len(cluster_reports), n_rule_clusters=n_rule,
                   n_episodic_clusters=len(cluster_reports) - n_rule,
                   n_rule_cases_abstracted=len(rule_sigs), n_episodic_cases=len(episodic_sigs),
                   clusters=cluster_reports)
    return W, episodic_sigs, episodic_roles, summary


def cluster_gated_predict_factory(W, role_codebook, roles, episodic_sigs, episodic_roles, tau_rule,
                                  ep_sim_thresh=EPISODIC_SIM_THRESH):
    fire_log = []

    def fn(a):
        role_rule, margin_rule = store_predict(W, role_codebook, roles, a["rel_sig"])
        if margin_rule > tau_rule:
            fire_log.append(("RULE", role_rule))
            return role_rule, 1.0
        if episodic_sigs:
            sn = float(np.linalg.norm(a["rel_sig"])) + 1e-9
            best_sim, best_role = -1.0, None
            for cs, cr in zip(episodic_sigs, episodic_roles):
                sim = float(np.dot(cs, a["rel_sig"])) / ((float(np.linalg.norm(cs)) + 1e-9) * sn)
                if sim > best_sim:
                    best_sim, best_role = sim, cr
            if best_sim > ep_sim_thresh:
                fire_log.append(("EPISODIC", best_role))
                return best_role, 1.0
        fire_log.append(("NONE", None))
        return a["pred_class"], -1.0
    fn.fire_log = fire_log
    return fn


def calibrate_tau_rule_only(W, role_codebook, roles, seen):
    rule_fn = lambda a: store_predict(W, role_codebook, roles, a["rel_sig"])  # noqa: E731
    return calibrate_tau(rule_fn, seen)


# ========================================================================================
# Per-seed run: generate instances, lexeme+verb-disjoint split, build ALL arms + controls.
# ========================================================================================
def run_seed(seen_pool, seed, n_pairs_seen, n_pairs_held, replay_frac=0.5,
             n_cycles_coherent=6):
    seen_nouns, held_nouns, seen_verbs, held_verbs = seen_pool
    seen = make_instances(seen_nouns, seen_verbs, n_pairs_seen, seed=1000 + seed)
    held = make_instances(held_nouns, held_verbs, n_pairs_held, seed=2000 + seed)
    for a in seen + held:
        a["rel_sig"] = relational_sig(a)
        a["surf_sig"] = surface_sig(a)
    seen_fail = [a for a in seen if a["is_fail"]]
    held_fail = [a for a in held if a["is_fail"]]
    base_correct_held = sum(1 for a in held if a["pred_class"] == a["gold_class"])
    base_acc_held = round(base_correct_held / len(held), 4) if held else None
    fast_recall = _fast_seen_recall(seen_fail)
    roles = list(ROLES)
    role_codebook = build_role_codebook(roles)

    rel_sigs = [a["rel_sig"] for a in seen_fail]
    case_roles = [a["gold_class"] for a in seen_fail]
    surf_sigs = [a["surf_sig"] for a in seen_fail]

    if len(rel_sigs) < 4:
        return {"seed": seed, "skipped": "too_few_seen_cases", "n_seen_fail": len(seen_fail),
                "n_heldout_fail": len(held_fail)}

    # ---- COHERENT (ungated, flat Hebbian over ALL seen_fail relational sigs) ----
    W = consolidate_store(rel_sigs, case_roles, role_codebook, n_cycles=n_cycles_coherent,
                          replay_frac=replay_frac, seed=seed)
    coh_fn = lambda a: store_predict(W, role_codebook, roles, a["rel_sig"])  # noqa: E731
    tau_coh = calibrate_tau(coh_fn, seen)
    coherent = eval_heldout(coh_fn, held, tau_coh)

    # ---- MUST-FAIL: SCRAMBLE gold_class among SEEN cases before consolidation ----
    rng = np.random.default_rng(1000 + seed)
    scr_roles = [case_roles[j] for j in rng.permutation(len(case_roles))]
    W_scr = consolidate_store(rel_sigs, scr_roles, role_codebook, n_cycles=n_cycles_coherent,
                              replay_frac=replay_frac, seed=seed)
    scr_fn = lambda a: store_predict(W_scr, role_codebook, roles, a["rel_sig"])  # noqa: E731
    scramble = eval_heldout(scr_fn, held, tau_coh)

    # ---- MUST-FAIL: ARM_ZERO_CYCLES (freeze the sleep pass) ----
    W_zero = consolidate_store(rel_sigs, case_roles, role_codebook, n_cycles=0,
                               replay_frac=replay_frac, seed=seed)
    zero_fn = lambda a: store_predict(W_zero, role_codebook, roles, a["rel_sig"])  # noqa: E731
    tau_zero = calibrate_tau(zero_fn, seen)
    zero_cycles = eval_heldout(zero_fn, held, tau_zero)

    # ---- HEADLINE CONTROL: ARM_SURFACE_KNN (surface bag, NO role-binding; must-fail-by-
    # construction between active/passive of a pair; primary discriminator per task spec) ----
    knn_fn = lambda a: knn_predict(surf_sigs, case_roles, a["surf_sig"], k=K_KNN)  # noqa: E731
    tau_knn = calibrate_tau(knn_fn, seen)
    knn_surface_arm = eval_heldout(knn_fn, held, tau_knn)

    # ---- ARM_MEMORIZE (exact discrete-key lookup; lexeme+verb-disjoint held-out floor) ----
    memo_table = {}
    for a in seen_fail:
        memo_table.setdefault(a["key"], Counter()).update([a["gold_class"]])
    memo_table = {k: c.most_common(1)[0][0] for k, c in memo_table.items()}
    maj_role = Counter(case_roles).most_common(1)[0][0]
    memo_fn = lambda a: memorize_predict(memo_table, a["key"], maj_role)  # noqa: E731
    memo_arm = eval_heldout(memo_fn, held, 0.5)

    # ---- DIAGNOSTIC (non-gating, per atom 29441's own caveat): ARM_KNN_RELATIONAL -- kNN over
    # the SAME relational signature, NO learning at all. If this TIES cluster_gated, the lever
    # is the REPRESENTATION not the LEARNER (29441's exact lesson, re-checked here). ----
    knn_rel_fn = lambda a: knn_predict(rel_sigs, case_roles, a["rel_sig"], k=K_KNN)  # noqa: E731
    tau_knn_rel = calibrate_tau(knn_rel_fn, seen)
    knn_relational_arm = eval_heldout(knn_rel_fn, held, tau_knn_rel)

    # ---- CYCLES CURVE (flexible/improving property) ----
    curve = []
    for nc in CYCLES_CURVE:
        Wc = consolidate_store(rel_sigs, case_roles, role_codebook, n_cycles=nc,
                               replay_frac=replay_frac, seed=seed)
        fn_c = lambda a, _W=Wc: store_predict(_W, role_codebook, roles, a["rel_sig"])  # noqa: E731
        tau_c = calibrate_tau(fn_c, seen)
        r_c = eval_heldout(fn_c, held, tau_c)
        curve.append({"n_cycles": nc, "net_gain": r_c["net_gain"],
                      "heldout_fix_rate": r_c["heldout_fix_rate"], "rescue_precision": r_c["rescue_precision"]})

    gain_collapse_scramble = round((coherent["heldout_fix_rate"] or 0) - (scramble["heldout_fix_rate"] or 0), 4)

    # ---- PER-CLUSTER GATE (headline arm) ----
    W_rule, ep_sigs, ep_roles, cluster_summary = build_cluster_gated_store(
        seen_fail, role_codebook, roles, n_cycles=n_cycles_coherent, replay_frac=replay_frac, seed=seed)
    tau_rule = calibrate_tau_rule_only(W_rule, role_codebook, roles, seen)
    cg_fn = cluster_gated_predict_factory(W_rule, role_codebook, roles, ep_sigs, ep_roles, tau_rule)
    cluster_gated = eval_heldout(cg_fn, held, 0.0)
    rule_routed = [(a, role) for a, (src, role) in zip(held, cg_fn.fire_log) if src == "RULE"]
    episodic_routed_n = sum(1 for (src, _r) in cg_fn.fire_log if src == "EPISODIC")

    seen_fail_scr = [dict(a, gold_class=scr_roles[i]) for i, a in enumerate(seen_fail)]
    W_rule_scr, ep_sigs_scr, ep_roles_scr, cluster_summary_scr = build_cluster_gated_store(
        seen_fail_scr, role_codebook, roles, n_cycles=n_cycles_coherent, replay_frac=replay_frac, seed=seed)
    tau_rule_scr = calibrate_tau_rule_only(W_rule_scr, role_codebook, roles, seen)
    cg_scr_fn = cluster_gated_predict_factory(W_rule_scr, role_codebook, roles, ep_sigs_scr, ep_roles_scr,
                                              tau_rule_scr)
    cluster_gated_scramble = eval_heldout(cg_scr_fn, held, 0.0)

    n_rule_routed = len(rule_routed)
    if n_rule_routed:
        agree = sum(1 for a, role in rule_routed
                    if knn_predict(surf_sigs, case_roles, a["surf_sig"], k=K_KNN)[0] == role)
        rule_surfaceknn_agreement = round(agree / n_rule_routed, 4)
    else:
        rule_surfaceknn_agreement = None

    gain_collapse_cg = round((cluster_gated["heldout_fix_rate"] or 0) -
                             (cluster_gated_scramble["heldout_fix_rate"] or 0), 4)
    beat_knn_margin_cg = round(_nz(cluster_gated["net_gain"], -9) - _nz(knn_surface_arm["net_gain"], -9), 4)
    beat_memo_margin_cg = round(_nz(cluster_gated["net_gain"], -9) - _nz(memo_arm["net_gain"], -9), 4)
    beat_ungated_margin = round(_nz(cluster_gated["net_gain"], -9) - _nz(coherent["net_gain"], -9), 4)
    beat_relational_knn_margin = round(_nz(cluster_gated["net_gain"], -9) - _nz(knn_relational_arm["net_gain"], -9), 4)

    return {
        "seed": seed, "n_seen_fail": len(seen_fail), "n_heldout": len(held),
        "n_heldout_fail": len(held_fail), "base_acc_held": base_acc_held,
        "tau_coherent": tau_coh, "fast_seen_recall": fast_recall,
        "coherent": coherent, "scramble": scramble, "zero_cycles": zero_cycles,
        "knn_surface": knn_surface_arm, "memorize": memo_arm, "knn_relational": knn_relational_arm,
        "gain_collapse_scramble": gain_collapse_scramble,
        "cycles_curve": curve,
        "cluster_gated": cluster_gated, "cluster_gated_scramble": cluster_gated_scramble,
        "cluster_summary": cluster_summary, "cluster_summary_scramble": cluster_summary_scr,
        "gain_collapse_cluster_gated": gain_collapse_cg,
        "beat_knn_margin_cg": beat_knn_margin_cg, "beat_memo_margin_cg": beat_memo_margin_cg,
        "beat_ungated_margin": beat_ungated_margin, "beat_relational_knn_margin": beat_relational_knn_margin,
        "cg_beats_knn_fixrate": bool((cluster_gated["heldout_fix_rate"] or 0) > (knn_surface_arm["heldout_fix_rate"] or 0)),
        "cg_beats_memo_fixrate": bool((cluster_gated["heldout_fix_rate"] or 0) > (memo_arm["heldout_fix_rate"] or 0)),
        "n_rule_routed_heldout": n_rule_routed, "n_episodic_routed_heldout": episodic_routed_n,
        "rule_surfaceknn_agreement": rule_surfaceknn_agreement,
    }


# ========================================================================================
# Mode configs + I/O. Smoke = FULL-scale n_pairs, fewer seeds (option A, discriminator survives
# scale by construction -- compute is trivial HD arithmetic, no reason to shrink scale).
# ========================================================================================
def cfg_smoke():
    return dict(mode="smoke", seeds=[7], n_pairs_seen=150, n_pairs_held=80, replay_frac=0.5,
                n_cycles_coherent=6, frac_seen=0.6)


def cfg_full():
    return dict(mode="full", seeds=[7, 13, 19], n_pairs_seen=150, n_pairs_held=80, replay_frac=0.5,
                n_cycles_coherent=6, frac_seen=0.6)


def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _arms_must_differ(per_seed_row):
    """META_RULE_AF: hash-test that arms produce genuinely different held-out predicted-class
    tuples (not a bit-identical bug)."""
    import hashlib as _hl
    arms = ("coherent", "scramble", "zero_cycles", "knn_surface", "memorize", "knn_relational",
            "cluster_gated", "cluster_gated_scramble")
    digests = {}
    for name in arms:
        r = per_seed_row.get(name)
        if not r:
            continue
        key = json.dumps([r.get("loop_acc"), r.get("net_gain"), r.get("fixes"), r.get("breaks")],
                          sort_keys=True)
        digests[name] = _hl.sha256(key.encode()).hexdigest()
    pairs_equal = []
    names = list(digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if digests[names[i]] == digests[names[j]]:
                pairs_equal.append((names[i], names[j]))
    return digests, pairs_equal


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = _out_dir(mode)
    _write_start_marker(output_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START reversible-role relational case+sleep test", flush=True)

    seen_nouns, held_nouns, seen_verbs, held_verbs = lexeme_verb_split(
        ANIMATE_NOUNS, VERBS, seed=42, frac_seen=cfg["frac_seen"])
    print(f"[{ANCHOR_NAME}:{mode}] split: seen_nouns={len(seen_nouns)} held_nouns={len(held_nouns)} "
          f"seen_verbs={len(seen_verbs)} held_verbs={len(held_verbs)}", flush=True)
    assert set(seen_nouns).isdisjoint(held_nouns)
    assert set(seen_verbs).isdisjoint(held_verbs)

    probe_insts = make_instances(seen_nouns, seen_verbs, min(cfg["n_pairs_seen"], 40), seed=1)
    leak_clean = _leak_probe(probe_insts)
    n_voice_checked = _surface_identical_across_voice_probe(probe_insts)
    print(f"[{ANCHOR_NAME}:{mode}] LEAK-CLEAN={leak_clean} surface_identical_across_voice checked="
          f"{n_voice_checked} pairs", flush=True)

    per_seed = []
    for seed in cfg["seeds"]:
        row = run_seed((seen_nouns, held_nouns, seen_verbs, held_verbs), seed,
                       n_pairs_seen=cfg["n_pairs_seen"], n_pairs_held=cfg["n_pairs_held"],
                       replay_frac=cfg["replay_frac"], n_cycles_coherent=cfg["n_cycles_coherent"])
        per_seed.append(row)
        if "coherent" in row:
            arms_digests, arms_equal_pairs = _arms_must_differ(row)
            cs = row["cluster_summary"]
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} n_seen_fail={row['n_seen_fail']} "
                  f"n_held_fail={row['n_heldout_fail']} base_acc_held={row['base_acc_held']} | "
                  f"CLUSTER_GATED fix={row['cluster_gated']['heldout_fix_rate']} gain={row['cluster_gated']['net_gain']} "
                  f"prec={row['cluster_gated']['rescue_precision']} clusters={cs['n_clusters']} "
                  f"rule={cs['n_rule_clusters']} episodic={cs['n_episodic_clusters']} | "
                  f"SCRAMBLE(cg) fix={row['cluster_gated_scramble']['heldout_fix_rate']} "
                  f"(collapse={row['gain_collapse_cluster_gated']}) | "
                  f"beat_SURFACE_knn={row['beat_knn_margin_cg']} beat_memo={row['beat_memo_margin_cg']} "
                  f"beat_ungated={row['beat_ungated_margin']} beat_RELATIONAL_knn={row['beat_relational_knn_margin']} | "
                  f"SURFACE_KNN fix={row['knn_surface']['heldout_fix_rate']} gain={row['knn_surface']['net_gain']} | "
                  f"RELATIONAL_KNN fix={row['knn_relational']['heldout_fix_rate']} gain={row['knn_relational']['net_gain']} | "
                  f"MEMO fix={row['memorize']['heldout_fix_rate']} gain={row['memorize']['net_gain']} | "
                  f"ZERO_CYCLES gain={row['zero_cycles']['net_gain']} | arms_equal_pairs={arms_equal_pairs}",
                  flush=True)
        else:
            print(f"[{ANCHOR_NAME}:{mode}] seed={seed} SKIPPED: {row.get('skipped')}", flush=True)

    scored = [s for s in per_seed if "coherent" in s]

    def mean(path):
        vals = []
        for s in scored:
            v = s
            for p in path:
                v = v[p] if isinstance(v, dict) else None
            if isinstance(v, (int, float)):
                vals.append(v)
        return round(float(np.mean(vals)), 4) if vals else None

    m_fix = mean(["cluster_gated", "heldout_fix_rate"])
    m_gain = mean(["cluster_gated", "net_gain"])
    m_prec = mean(["cluster_gated", "rescue_precision"])
    m_base = mean(["base_acc_held"])
    m_collapse = mean(["gain_collapse_cluster_gated"])
    m_recall = mean(["fast_seen_recall"])
    m_zero_gain = mean(["zero_cycles", "net_gain"])
    m_knn_gain = mean(["knn_surface", "net_gain"])
    m_knn_fix = mean(["knn_surface", "heldout_fix_rate"])
    m_memo_gain = mean(["memorize", "net_gain"])
    m_memo_fix = mean(["memorize", "heldout_fix_rate"])
    m_knnrel_gain = mean(["knn_relational", "net_gain"])
    m_knnrel_fix = mean(["knn_relational", "heldout_fix_rate"])
    m_beat_knn = mean(["beat_knn_margin_cg"])
    m_beat_memo = mean(["beat_memo_margin_cg"])
    m_beat_ungated = mean(["beat_ungated_margin"])
    m_beat_relknn = mean(["beat_relational_knn_margin"])
    base_acc = mean(["cluster_gated", "base_acc"])
    baseline_in_band = bool(m_base is not None and 0.05 < m_base < 0.95)

    m_fix_ungated = mean(["coherent", "heldout_fix_rate"])
    m_gain_ungated = mean(["coherent", "net_gain"])

    n_clusters_total = sum(s["cluster_summary"]["n_clusters"] for s in scored)
    n_rule_total = sum(s["cluster_summary"]["n_rule_clusters"] for s in scored)
    n_episodic_total = sum(s["cluster_summary"]["n_episodic_clusters"] for s in scored)
    rule_cluster_ratio = round(n_rule_total / n_clusters_total, 4) if n_clusters_total else None

    all_seeds_gain_pos = bool(scored) and all(_nz(s["cluster_gated"]["net_gain"], -1) > 0 for s in scored)
    all_seeds_beat_knn = bool(scored) and all(s["cg_beats_knn_fixrate"] for s in scored)
    all_seeds_beat_memo = bool(scored) and all(s["cg_beats_memo_fixrate"] for s in scored)
    scramble_collapses = (m_collapse is not None and m_collapse >= SCRAMBLE_COLLAPSE_MIN)
    net_gain_pos = (m_gain is not None and m_gain > 0.0)
    prec_ok = (m_prec is not None and m_prec >= RESCUE_PRECISION_MIN)
    zero_cycles_flat = (m_zero_gain is not None and abs(m_zero_gain) <= ZERO_CYCLES_FLAT_MAX)
    beats_knn_hp = (m_beat_knn is not None and m_beat_knn >= BEAT_MARGIN_HARD_PASS and all_seeds_beat_knn)
    beats_memo_hp = (m_beat_memo is not None and m_beat_memo >= BEAT_MARGIN_HARD_PASS and all_seeds_beat_memo)
    ties_or_loses_knn = (m_beat_knn is not None and m_beat_knn < BEAT_MARGIN_HARD_FAIL)
    ties_or_loses_memo = (m_beat_memo is not None and m_beat_memo < BEAT_MARGIN_HARD_FAIL)

    relational_knn_ties_cg = (m_beat_relknn is not None and abs(m_beat_relknn) < RELATIONAL_KNN_TIE_THRESH)

    similarity_collapse = (
        (not scored) or
        (m_fix is not None and m_fix < FIX_RATE_FLOOR) or
        (m_gain is not None and m_gain <= 0.0) or
        (m_collapse is not None and m_collapse < 0.05) or
        ties_or_loses_knn or ties_or_loses_memo
    )

    if not scored:
        verdict = "INSUFFICIENT_SURFACE"
    elif (scramble_collapses and net_gain_pos and all_seeds_gain_pos and prec_ok and leak_clean
          and zero_cycles_flat and beats_knn_hp and beats_memo_hp):
        verdict = "HARD_PASS_REAL_STRUCTURAL_RULE"
    elif similarity_collapse or (not leak_clean):
        verdict = "HARD_FAIL_SIMILARITY_COLLAPSE"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    msg = (f"{verdict} | reversible-role (active/passive) task: n_pairs_seen={cfg['n_pairs_seen']} "
           f"n_pairs_held={cfg['n_pairs_held']} baseline(voice-blind status heuristic) held_acc="
           f"{m_base} (in_band={baseline_in_band}); PER-CLUSTER GATE: {n_clusters_total} clusters total "
           f"({n_rule_total} RULE / {n_episodic_total} EPISODIC, rule_ratio={rule_cluster_ratio}); "
           f"HELDOUT LIFT (lexeme+verb-disjoint): CLUSTER_GATED fix_rate={m_fix} net_gain={m_gain} "
           f"rescue_prec={m_prec} | SCRAMBLE collapse={m_collapse} (need>={SCRAMBLE_COLLAPSE_MIN}) | "
           f"ZERO_CYCLES net_gain={m_zero_gain} (need flat<={ZERO_CYCLES_FLAT_MAX}) || "
           f"*** MARGIN-OVER-SIMILARITY-VOTE (headline) ***: SURFACE_KNN fix={m_knn_fix} gain={m_knn_gain} "
           f"(by-construction chance control) -> CG beat_margin={m_beat_knn} (need>={BEAT_MARGIN_HARD_PASS} "
           f"DECISIVE, all_seeds_beat={all_seeds_beat_knn}) | MEMORIZE fix={m_memo_fix} gain={m_memo_gain} "
           f"-> CG beat_margin={m_beat_memo} (need>={BEAT_MARGIN_HARD_PASS}) || DIAGNOSTIC (non-gating, "
           f"atom-29441 lever-check): RELATIONAL_KNN(no learning) fix={m_knnrel_fix} gain={m_knnrel_gain} "
           f"-> CG beat_margin={m_beat_relknn} (ties_cg={relational_knn_ties_cg}, |margin|<{RELATIONAL_KNN_TIE_THRESH} "
           f"means REPRESENTATION not LEARNER per 29441) || vs UNGATED(coherent) fix={m_fix_ungated} "
           f"gain={m_gain_ungated} (CG beats ungated by {m_beat_ungated}) | leak_clean={leak_clean}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "seeds": cfg["seeds"], "expected_n_seed_rows": len(cfg["seeds"]), "n_seed_rows": len(per_seed),
        "cardinality_ok": bool(len(per_seed) == len(cfg["seeds"])),
        "cfg": cfg,
        "PRIMARY_heldout_fix_rate_cluster_gated": m_fix, "baseline_held_acc": m_base,
        "heldout_net_gain_cluster_gated": m_gain, "rescue_precision_cluster_gated": m_prec,
        "MUSTFAIL_scramble_gain_collapse": m_collapse, "scramble_collapses_gain": scramble_collapses,
        "MUSTFAIL_zero_cycles_net_gain": m_zero_gain, "zero_cycles_flat": zero_cycles_flat,
        "HEADLINE_CONTROL_surface_knn_fix_rate": m_knn_fix, "HEADLINE_CONTROL_surface_knn_net_gain": m_knn_gain,
        "CONTROL_memorize_fix_rate": m_memo_fix, "CONTROL_memorize_net_gain": m_memo_gain,
        "DIAGNOSTIC_relational_knn_fix_rate": m_knnrel_fix, "DIAGNOSTIC_relational_knn_net_gain": m_knnrel_gain,
        "beat_surface_knn_margin_mean": m_beat_knn, "beat_memo_margin_mean": m_beat_memo,
        "beat_ungated_margin_mean": m_beat_ungated, "beat_relational_knn_margin_mean": m_beat_relknn,
        "relational_knn_ties_cluster_gated": relational_knn_ties_cg,
        "beats_surface_knn_hard_pass": beats_knn_hp, "beats_memo_hard_pass": beats_memo_hp,
        "all_seeds_net_gain_positive": all_seeds_gain_pos, "all_seeds_beat_surface_knn": all_seeds_beat_knn,
        "all_seeds_beat_memo": all_seeds_beat_memo,
        "n_clusters_total": n_clusters_total, "n_rule_clusters_total": n_rule_total,
        "n_episodic_clusters_total": n_episodic_total, "rule_cluster_ratio": rule_cluster_ratio,
        "UNGATED_COMPARISON_fix_rate": m_fix_ungated, "UNGATED_COMPARISON_net_gain": m_gain_ungated,
        "fast_seen_recall_mean": m_recall,
        "leak_clean": leak_clean, "n_voice_construction_probe_pairs_checked": n_voice_checked,
        "baseline_in_band": baseline_in_band,
        "final_metrics_atomicity": "tmp_replace", "crlb_n_a": "generalization fix-rate; noise floor=1/n_heldout_fail",
        "progress_logging": "print_flush_true", "compute_architecture": "sequential-CPU (justified <2min)",
        "calibration_check": "adaptive_with_discriminator_gate (tau on SEEN net_gain; scramble+zero_cycles+"
                              "surface_knn+memo+relational_knn all fire)",
        "deterministic_seeding": True, "compose_in_cell_no_hdlab_mutation": True,
        "voice_weight": VOICE_WEIGHT, "n_sig": N_SIG,
        "per_seed": per_seed,
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] DONE {round(elapsed,1)}s -> {verdict}", flush=True)
    print(msg, flush=True)
    return payload


def self_test():
    print("=== reversible-role relational case+sleep self-test (real code paths) ===", flush=True)
    seen_nouns, held_nouns, seen_verbs, held_verbs = lexeme_verb_split(ANIMATE_NOUNS, VERBS, seed=42)
    assert set(seen_nouns).isdisjoint(held_nouns), "lexeme split not disjoint"
    assert set(seen_verbs).isdisjoint(held_verbs), "verb split not disjoint"

    insts = make_instances(seen_nouns, seen_verbs, 40, seed=1)
    assert insts, "no instances generated at smoke scale"
    assert all(a["gold_class"] in ROLES for a in insts)
    n_fail = sum(1 for a in insts if a["is_fail"])
    assert n_fail > 0, "zero baseline errors (discriminator dead)"
    base_acc = 1 - n_fail / len(insts)
    assert 0.05 < base_acc < 0.98, f"base_acc {base_acc} outside plausible band"
    gold_classes_in_fail = set(a["gold_class"] for a in insts if a["is_fail"])
    assert len(gold_classes_in_fail) == 2, (
        f"seen_fail must contain BOTH gold classes for a non-degenerate per-cluster purity test, got "
        f"{gold_classes_in_fail}")

    for a in insts:
        a["rel_sig"] = relational_sig(a)
        a["surf_sig"] = surface_sig(a)
    r1 = relational_sig(insts[0])
    r2 = relational_sig(insts[0])
    assert np.array_equal(r1, r2), "relational_sig not deterministic"
    leak = _leak_probe(insts[:80])
    assert leak, "LEAK: signature not gold-free / not mutation-invariant"
    n_checked = _surface_identical_across_voice_probe(insts)
    assert n_checked > 0, "no reversible pairs checked for by-construction surface-identity property"

    sf = [a for a in insts if a["is_fail"]]
    roles = list(ROLES)
    rcb = build_role_codebook(roles)
    rel_sigs = [a["rel_sig"] for a in sf]
    case_roles = [a["gold_class"] for a in sf]
    surf_sigs = [a["surf_sig"] for a in sf]

    W_store = consolidate_store(rel_sigs, case_roles, rcb, n_cycles=2, replay_frac=1.0)
    assert W_store.shape == (N_SIG, N_SIG)
    r, m = store_predict(W_store, rcb, roles, sf[0]["rel_sig"])
    assert r in roles and isinstance(m, float)

    held_probe = make_instances(held_nouns, held_verbs, 20, seed=2)
    for a in held_probe:
        a["rel_sig"] = relational_sig(a)
        a["surf_sig"] = surface_sig(a)
    ev = eval_heldout(lambda a: store_predict(W_store, rcb, roles, a["rel_sig"]), held_probe, 0.0)
    assert set(("fixes", "breaks", "heldout_fix_rate")).issubset(ev)

    rng = np.random.default_rng(3)
    scr_roles = [case_roles[j] for j in rng.permutation(len(case_roles))]
    W_scr = consolidate_store(rel_sigs, scr_roles, rcb, n_cycles=2, replay_frac=1.0)
    assert not np.array_equal(W_store, W_scr) or len(set(scr_roles)) == 1, (
        "META_RULE_AF: scramble store bit-identical to coherent")

    r_knn, m_knn = knn_predict(surf_sigs, case_roles, sf[0]["surf_sig"], k=3)
    assert r_knn in roles
    r_knnrel, m_knnrel = knn_predict(rel_sigs, case_roles, sf[0]["rel_sig"], k=3)
    assert r_knnrel in roles
    memo = {}
    for a in sf:
        memo.setdefault(a["key"], a["gold_class"])
    r_memo, m_memo = memorize_predict(memo, sf[0]["key"], Counter(case_roles).most_common(1)[0][0])
    assert r_memo in roles
    # memorize floor: held instances (new lexemes) must NEVER exact-key-match seen memo table
    assert all(a["key"] not in memo for a in held_probe), "memorize key leaked across lexeme-disjoint split"

    fr = _fast_seen_recall(sf)
    assert fr is None or 0.0 <= fr <= 1.0

    W_rule, ep_sigs, ep_roles, csum = build_cluster_gated_store(sf, rcb, roles, n_cycles=2, replay_frac=1.0)
    assert W_rule.shape == (N_SIG, N_SIG)
    assert csum["n_clusters"] >= 0 and csum["n_rule_clusters"] + csum["n_episodic_clusters"] == csum["n_clusters"]
    n_cases_in_rule_clusters = sum(c["size"] for c in csum["clusters"] if c["promoted_to_rule"])
    assert n_cases_in_rule_clusters + csum["n_episodic_cases"] == len(sf) or csum["n_clusters"] == 0
    tau_rule = calibrate_tau_rule_only(W_rule, rcb, roles, insts)
    cg_fn = cluster_gated_predict_factory(W_rule, rcb, roles, ep_sigs, ep_roles, tau_rule)
    ev_cg = eval_heldout(cg_fn, held_probe, 0.0)
    assert set(("fixes", "breaks", "heldout_fix_rate")).issubset(ev_cg)
    assert len(cg_fn.fire_log) == len(held_probe), "fire_log length mismatch"
    sources = set(src for src, _r in cg_fn.fire_log)
    assert sources.issubset({"RULE", "EPISODIC", "NONE"})

    print(f"[selftest] cluster-gate real path OK: n_clusters={csum['n_clusters']} rule={csum['n_rule_clusters']} "
          f"episodic={csum['n_episodic_clusters']} fire_log_sources={sources}", flush=True)
    print(f"[selftest] real store/knn/memorize/cluster-gate paths OK: n_instances={len(insts)} n_fail={n_fail} "
          f"base_acc={round(base_acc,4)} n_seen_fail={len(sf)} gold_classes_in_fail={gold_classes_in_fail}",
          flush=True)
    print("[selftest] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run_mode(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        try:
            os.makedirs(output_dir, exist_ok=True)
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                    "summary": "CELL_CRASHED", "elapsed_s": 0.0, "traceback": traceback.format_exc()[:4000],
                    "ts_iso": datetime.now(timezone.utc).isoformat()}
            tmp = os.path.join(output_dir, "metrics.json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(diag, f, indent=2)
            os.replace(tmp, os.path.join(output_dir, "metrics.json"))
        finally:
            raise
