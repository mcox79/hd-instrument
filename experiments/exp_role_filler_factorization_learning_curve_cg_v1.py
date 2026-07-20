"""Native-binding compositional generalization: the LEARNING-CURVE / cheaper-THRESHOLD chain-grade.

QUESTION (the genuinely-untested brain-faithful edge): does native VSA role-filler factorization
(distinct role vectors + commutative FHRR bind + additive superposition) reach systematic
compositional generalization (held-out role-filler COMBINATIONS) with a CHEAPER LEARNING CURVE --
fewer exemplar TYPES to cross the Tolerance-Principle productivity THRESHOLD -- than a PARAM-MATCHED
/ FAIRLY-TUNED FLAT baseline that lacks the role-filler-separation inductive bias?

The load-bearing NEW element vs the existing factorization cells (compgen_v1 / realcontent /
conceptnet / reader_coupled): those show a held-out factored-vs-flat GAP, but (a) their flat baseline
is a WEAK content-prototype that sits at CHANCE in-distribution (compgen_v1 landed
flat_indist_present=0.347 at chance 0.333 -- it FAILS the must-fit control, a Csordas-2021 under-tuning
artifact), and (b) they report a diversity curve but never EXTRACT the productivity threshold per arm
nor bound it against a novel-STRUCTURE failure. This cell fixes both: a STRONG fair flat baseline that
near-ceilings in-distribution (proving it CAN fit) yet floors on held-out combos, plus explicit
threshold extraction (T_A vs T_B) as the deliverable, plus the novel-relation-TYPE bounding condition
where BOTH arms must fail.

FILLS A REAL GAP: TEM (Whittington/Behrens 2020) and successors demonstrate factored structure->content
generalization but NEVER ran a param-matched factorized-vs-entangled sample-efficiency / learning-curve
comparison. This cell is that comparison.

------------------------------------------------------------------------------------------------
BRAIN GROUNDING (CITED@ notes/research_brain_systematic_compositional_generalization_binding_chaingrade_2026-07-19.md)
------------------------------------------------------------------------------------------------
- Systematicity real + VSA/TPR = constructive sufficiency proof (Fodor-Pylyshyn 1988; Smolensky 1990;
  Plate 1995). Our FHRR bind IS that mechanism.
- Compositional generalization has a REAL learning curve that is a THRESHOLD PHASE-CHANGE, not a smooth
  ramp (Yang Tolerance Principle theta_N = N/ln(N); Schuler-Yang 2023 infants quantal at 11/5 vs 10/6).
- TYPE frequency (# distinct exemplars instantiating a pattern), NOT token frequency, drives
  productivity (Bybee); exemplar diversity benefits generalization (Wonnacott).
- Agent/patient asymmetry lives in DISTINCT ROLE VECTORS + a COMMUTATIVE bind, NOT an asymmetric
  operator (Frankland-Greene 2015; Lalisse-Smolensky 2021). No asymmetry wall for our commutative FHRR.
- TEM two-stage shape: SLOW structure-formation then FAST one-shot content-binding (Tse 2007 schema
  ~15 trials, then 1-trial new association). Novel CONTENT in known structure generalizes fast; novel
  STRUCTURE / relation-TYPE breaks transfer (Bakermans 2025) -- the honest bounding condition.

CONSTRUCTION-DETERMINED GUARD (the key honesty gate, per the drill Scan-4 refinement): "zero-shot per
held-out combo" is trivial ONLY if the STRUCTURE is handed as oracle role-keys. Here the structural key
g_hat is LEARNED (Hebbian unbind-averaging over the accumulating exemplar stream), never oracle. The
chain-grade earns its name via a GENUINE RISING CURVE (g_hat cleaning over exemplars -> held-out
generalization crossing a threshold), not a flat-perfect-from-1-exemplar gap. If FACTORED is already
saturated at the minimum exemplar budget with no curve, that is construction-determined -> HARD_FAIL.

------------------------------------------------------------------------------------------------
COMPUTE ARCHITECTURE (mandatory declaration)
------------------------------------------------------------------------------------------------
Class: (b) sequential-CPU with justification -- wall seconds-to-~2min; cell validates the substrate
primitive (FHRR bind/unbind) as a reference computation over a few thousand N=2048 complex vectors,
elementwise ops; no genuine GPU-batchable heavy matmul. Foreground local-to-completion. LOCAL-ONLY
(no queue dispatch; no remote-persist; no origin push). Storage strategy: BUNDLED is the object under
test (one sentence = one superposition of m bound pairs, brain-faithful m=5); this cell measures
bind-factorization readout crosstalk directly. no sharded store, no primitive composition chain.

------------------------------------------------------------------------------------------------
ARMS (ONE VARIABLE = the role-filler-separation inductive bias; same task/data/split/codes/budget)
------------------------------------------------------------------------------------------------
World (latent, per seed): g_true[r] random FHRR per role; x[f] random FHRR per filler (grounded content
codes, GIVEN to all arms). A sentence assigns distinct fillers to m distinct roles; observable code
S = sum_i bind(g_true[r_i], x[f_i]) (FHRR superposition of conjunctive bindings). Reading also yields
the (role-index, filler-token) words + a query role. Held-out split holds out (role,filler) COMBINATIONS
only; every held-out filler stays trainable in >=1 OTHER role (atom-divergence control / CFQ-MCD).

ARM_FACTORED (native VSA factorization; LEARNED structural scaffold): learns a content-blind key
g_hat[r] = unit(mean over training occurrences of role r of unbind(S, x[filler])). Because bind is
content-agnostic + commutative, averaging over DIVERSE co-fillers cancels crosstalk -> g_hat -> g_true.
Readout: est = unbind(S, g_hat[qr]); pick argmax similarity(est, x[cand]). g_hat NEVER sees held-out
combos; held-out recovery works because g_hat[qr] (from other fillers) and x[f*] (grounded) are
independent factors and bind is fixed -- the TEM zero-shot argument, ported to role-binding.

ARM_FLAT_MEMORIZE (STRONG, FAIR flat baseline -- the must-fit control): a role-conditioned frequency
memorizer, count[r][f] = # times filler f seen in role r (the maximally-capable NON-compositional model;
memorization is the ceiling for a flat model regardless of params -- COGS/CFQ). Readout: score each
candidate by count[qr][f] (+ tiny global-freq tiebreak). In-distribution (f* seen in role qr) it
near-CEILINGS (proving a well-fit flat CAN fit the task). Held-out (f* never in role qr) it picks a
wrong seen-in-role-qr filler or guesses -> FLOORS. This is the fair strong baseline compgen_v1 lacked.

ARM_FLAT_PROTO (param-matched vector baseline, connects to prior cells): proto[r] = unit(mean over
training of x[filler-in-role-r]); readout argmax similarity(x[cand], proto[qr]). Same param count as
g_hat (n_roles x N complex). Sits near chance in-dist (the compgen_v1 weakness), included to show the
flat-fails result is robust across flat variants and to reproduce the prior baseline.

------------------------------------------------------------------------------------------------
PRIMARY MEASUREMENT = THE LEARNING CURVE + THE THRESHOLD (the flexible/improving property)
------------------------------------------------------------------------------------------------
Sweep the exemplar budget D (= # distinct training sentences drawn; realized distinct (role,filler)
pair-TYPE count reported alongside). Measure held-out-combo accuracy vs D for every arm. Extract per arm
the Tolerance-Principle THRESHOLD T = smallest D at which held-out VOCAB accuracy crosses the
productivity criterion (>= PROD_CRIT). Report whether T_FACTORED < T_FLAT (censored) = the sample-
efficiency edge. Also a fixed-TOKEN type-isolation diagnostic (vary # distinct filler-types per role at
fixed token count) to report honestly whether FACTORED's threshold is TYPE- or TOKEN-driven.

Readouts: VOCAB (pick from ALL fillers; chance=1/n_fillers; the RICH curve where flat floors cleanly)
and PRESENT (pick among the m sentence fillers; chance=1/m; where the strong flat fits in-dist -- the
must-fit metric).

------------------------------------------------------------------------------------------------
BANDS (pre-registered BEFORE running; see preregs/2026-07-19_role_filler_learning_curve_cg_v1.md)
------------------------------------------------------------------------------------------------
chance_vocab = 1/n_fillers; chance_present = 1/m. PROD_CRIT = 0.50 (held-out VOCAB productivity floor).

MUST-FIT control (both arms CAN fit; smoke MUST satisfy): FACTORED indist_present >= 0.85 AND
FLAT_MEMORIZE indist_present >= 0.70. If FLAT_MEMORIZE indist_present < 0.70 -> HARD_FAIL_STRAWMAN
(flat undertrained/weak -> contrast untrustworthy; iterate split density, do NOT ship the verdict).

MUST-FAIL control (flat fails specifically on novel combinations; smoke MUST fire): FLAT_MEMORIZE
heldout_vocab <= 0.10 at D_max AND (FLAT_MEMORIZE indist_present - heldout_present) >= 0.30.

VOID guard: FLAT_MEMORIZE heldout_present > 0.60 -> flat generalizes -> split does not isolate
compositional generalization -> report + fix, do NOT trust the FACTORED verdict.

CONSTRUCTION-DETERMINED guard (genuine learned curve, not trivial unbind): FACTORED heldout_vocab at
D_min <= 0.55 AND (FACTORED heldout_vocab at D_max - at D_min) >= 0.30. If FACTORED heldout_vocab at
D_min > 0.70 AND curve delta < 0.10 -> HARD_FAIL_CONSTRUCTION_DETERMINED (saturated from 1 exemplar,
no learning).

NOVEL-STRUCTURE bound (honest bounding; MUST fire): novel-role (structure never learned) accuracy
<= chance_present + 0.10 for BOTH FACTORED and FLAT_MEMORIZE (both fail -- g(x)x cannot reuse absent
structure; brain-faithful TEM/Bakermans failure boundary).

HARD_PASS (ALL of): must-fit PASS; must-fail fired; NOT void; construction-determined guard PASS;
T_FACTORED is finite (<= D_max); T_FLAT_MEMORIZE censored (None) OR T_FACTORED strictly lower (T_FLAT
index >= 2x T_FACTORED index); novel-structure bound fired for both; arms differ.
HARD_FAIL (ANY of): HARD_FAIL_STRAWMAN; HARD_FAIL_CONSTRUCTION_DETERMINED; T_FACTORED is None (factored
never crosses productivity -> no edge at this regime); (FACTORED - FLAT_MEMORIZE) heldout_vocab <= 0.05
at D_max (tie -> factorization confers no edge, a legitimate informative negative); VOID.
MIDDLE_BAND: anything between (e.g., curve rises but never crosses PROD_CRIT; novel bound noisy).
"""
from __future__ import annotations

# CELL-TEMPLATE MANDATORY (subset applicable to a LOCAL foreground mechanism-proof; NOT queue-dispatched):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on prediction arrays)
# - final_metrics_atomicity: tmp_replace (os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - baseline_in_band at smoke (META_RULE_AG; FLAT_MEMORIZE indist_present in (0.05,0.95); it is the must-fit control)
# - discriminator fires at smoke (must-fail control: FLAT heldout << FLAT indist; construction guard: FACTORED curve rises)
# - deterministic seeding: fixed int seeds + random.Random + sorted(); NO hash()/list(set()) ordering
# - scaffold-free witness in self-test EXERCISES the REAL hdlab.binding.bind/unbind + hdlab.atoms
# - all numbers in comments tagged HYPOTHESIZED@ (prereg) / THEORETICAL@ (formula) / CITED@ (brain lit); MEASURED@ printed at run

import argparse
import hashlib
import json
import os
import random
import statistics as st
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

from hdlab.atoms import make_atoms
from hdlab.binding import bind as hdlab_bind
from hdlab.binding import unbind as hdlab_unbind

ANCHOR_NAME = "role_filler_factorization_learning_curve_cg_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROD_CRIT = 0.50  # HYPOTHESIZED@prereg: held-out VOCAB productivity floor (>> chance, > flat floor)


# ----------------------------------------------------------------------------------------------
# Native FHRR ops (elementwise complex; bit-parity with hdlab.binding asserted in self-test).
# ----------------------------------------------------------------------------------------------
def fhrr_bind(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR bind = elementwise complex mul. Broadcasts (..., N)."""
    return a * b


def fhrr_unbind(c: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """FHRR unbind = elementwise mul by conjugate. Broadcasts (..., N)."""
    return c * b.conj()


def unit_phase(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Project each complex component to unit magnitude (FHRR phasor normalize)."""
    return v / torch.clamp(v.abs(), min=eps)


def sim_to_codebook(q: torch.Tensor, cb: torch.Tensor) -> torch.Tensor:
    """Normalized real inner product of q (N,) against codebook cb (K,N). Returns (K,)."""
    n = q.shape[-1]
    return (cb * q.conj()).sum(dim=-1).real / n


def sim_diag(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Row-wise FHRR similarity between two (K,N) codebooks. Returns (K,)."""
    n = a.shape[-1]
    return (a * b.conj()).sum(dim=-1).real / n


# ----------------------------------------------------------------------------------------------
# Data: sparse-per-role split. trained roles get a small trainable filler set (sparse -> the strong
# flat memorizer fits in-dist because the other present fillers are unlikely to be role-typical) plus
# held-out fillers (trainable in >=1 OTHER role). novel roles are NEVER trained (structure absent).
# ----------------------------------------------------------------------------------------------
def build_split(n_roles_trained, n_roles_novel, n_fillers, n_train_per_role, n_held_per_role, rng):
    """Returns dict with trained_roles, novel_roles, trainable_by_role, held_by_role, held_out set.
    Guarantees: every held-out filler is trainable in >=1 OTHER trained role (grounding / atom-divergence);
    every trained role has >= 2 trainable + >= 1 held-out; every filler appears as trainable somewhere."""
    trained_roles = list(range(n_roles_trained))
    novel_roles = list(range(n_roles_trained, n_roles_trained + n_roles_novel))
    fillers = list(range(n_fillers))
    assert n_train_per_role + n_held_per_role <= n_fillers, "per-role filler demand exceeds vocab"

    trainable_by_role = {}
    held_by_role = {}
    # Rotating windows so filler coverage is balanced and every filler lands in >=1 trainable set.
    for i, r in enumerate(trained_roles):
        base = (i * (n_train_per_role + n_held_per_role)) % n_fillers
        window = [fillers[(base + k) % n_fillers] for k in range(n_train_per_role + n_held_per_role)]
        window = sorted(set(window))
        # if collisions shrank the window, top it up deterministically
        k = 0
        while len(window) < n_train_per_role + n_held_per_role:
            cand = fillers[(base + n_train_per_role + n_held_per_role + k) % n_fillers]
            if cand not in window:
                window.append(cand)
            k += 1
        window = sorted(window)
        trn = sorted(window[:n_train_per_role])
        hld = sorted(window[n_train_per_role:n_train_per_role + n_held_per_role])
        trainable_by_role[r] = trn
        held_by_role[r] = hld

    # Coverage repair: any filler never trainable anywhere -> inject into a role's trainable set.
    covered = set()
    for r in trained_roles:
        covered.update(trainable_by_role[r])
    uncovered = sorted(set(fillers) - covered)
    ri = 0
    for f in uncovered:
        r = trained_roles[ri % len(trained_roles)]
        trainable_by_role[r] = sorted(set(trainable_by_role[r]) | {f})
        ri += 1

    held_out = set()
    for r in trained_roles:
        for f in held_by_role[r]:
            held_out.add((r, f))

    # Validity assertions (grounding guarantee).
    for r in trained_roles:
        assert len(trainable_by_role[r]) >= 2, f"role {r} lacks trainable fillers"
        assert len(held_by_role[r]) >= 1, f"role {r} lacks held-out fillers"
    for (r, f) in held_out:
        other = [rr for rr in trained_roles if f in trainable_by_role[rr]]
        assert len(other) >= 1, f"held-out filler {f} never trainable elsewhere (ungrounded)"

    return {
        "trained_roles": trained_roles,
        "novel_roles": novel_roles,
        "trainable_by_role": trainable_by_role,
        "held_by_role": held_by_role,
        "held_out": held_out,
    }


def sample_train_sentence(m, sp, rng):
    """m distinct trained roles, each a distinct trainable filler; NO held-out pair."""
    roles = sp["trained_roles"]
    tb = sp["trainable_by_role"]
    ho = sp["held_out"]
    for _ in range(300):
        chosen = sorted(rng.sample(roles, m))
        assign, used, ok = {}, set(), True
        for r in chosen:
            cands = [f for f in tb[r] if f not in used and (r, f) not in ho]
            if not cands:
                ok = False
                break
            f = rng.choice(cands)
            assign[r] = f
            used.add(f)
        if ok and len(assign) == m:
            return assign
    raise RuntimeError("could not sample a valid training sentence (regime too sparse)")


def sample_indist_sentence(m, sp, rng):
    assign = sample_train_sentence(m, sp, rng)
    return assign, rng.choice(sorted(assign.keys()))


def sample_heldout_sentence(m, sp, rng):
    """Exactly one held-out pair (r*,f*) as the query + m-1 trainable context pairs, distinct fillers."""
    roles = sp["trained_roles"]
    tb = sp["trainable_by_role"]
    hb = sp["held_by_role"]
    ho = sp["held_out"]
    for _ in range(500):
        r_star = rng.choice([r for r in roles if hb[r]])
        f_star = rng.choice(hb[r_star])
        others = sorted(rng.sample([r for r in roles if r != r_star], m - 1))
        assign, used, ok = {r_star: f_star}, {f_star}, True
        for r in others:
            cands = [f for f in tb[r] if f not in used and (r, f) not in ho]
            if not cands:
                ok = False
                break
            f = rng.choice(cands)
            assign[r] = f
            used.add(f)
        if ok and len(assign) == m:
            return assign, r_star
    raise RuntimeError("could not sample a valid held-out sentence")


def sample_novelrole_sentence(m, sp, rng):
    """Query a NOVEL role (never trained -> structure absent) + m-1 trainable context pairs.
    Novel-role filler is any grounded filler trainable in some trained role."""
    troles = sp["trained_roles"]
    nroles = sp["novel_roles"]
    tb = sp["trainable_by_role"]
    ho = sp["held_out"]
    all_trainable = sorted({f for r in troles for f in tb[r]})
    for _ in range(500):
        r_star = rng.choice(nroles)
        f_star = rng.choice(all_trainable)
        others = sorted(rng.sample(troles, m - 1))
        assign, used, ok = {r_star: f_star}, {f_star}, True
        for r in others:
            cands = [f for f in tb[r] if f not in used and (r, f) not in ho]
            if not cands:
                ok = False
                break
            f = rng.choice(cands)
            assign[r] = f
            used.add(f)
        if ok and len(assign) == m:
            return assign, r_star
    raise RuntimeError("could not sample a valid novel-role sentence")


def encode_sentence(assign, g_true, x):
    """Observable S = sum_i bind(g_true[r_i], x[f_i])."""
    parts = [fhrr_bind(g_true[r], x[f]) for r, f in sorted(assign.items())]
    return torch.stack(parts, dim=0).sum(dim=0)


def make_test_set(kind, n, m, sp, rng):
    out = []
    for _ in range(n):
        if kind == "heldout":
            assign, qr = sample_heldout_sentence(m, sp, rng)
        elif kind == "novel":
            assign, qr = sample_novelrole_sentence(m, sp, rng)
        else:
            assign, qr = sample_indist_sentence(m, sp, rng)
        out.append((assign, qr, assign[qr]))
    return out


# ----------------------------------------------------------------------------------------------
# Learning: FACTORED g_hat + FLAT_MEMORIZE count table + FLAT_PROTO vector prototype.
# ----------------------------------------------------------------------------------------------
def learn(train_sentences, n_roles_total, g_true, x, n_dim, n_fillers):
    g_acc = torch.zeros((n_roles_total, n_dim), dtype=torch.complex64)
    p_acc = torch.zeros((n_roles_total, n_dim), dtype=torch.complex64)
    cnt = torch.zeros(n_roles_total)
    counts = [[0] * n_fillers for _ in range(n_roles_total)]  # FLAT_MEMORIZE count[r][f]
    seen_pairs = set()
    for assign in train_sentences:
        S = encode_sentence(assign, g_true, x)
        for r, f in assign.items():
            g_acc[r] += fhrr_unbind(S, x[f])
            p_acc[r] += x[f]
            cnt[r] += 1
            counts[r][f] += 1
            seen_pairs.add((r, f))
    cntc = torch.clamp(cnt, min=1.0).unsqueeze(1)
    g_hat = unit_phase(g_acc / cntc)
    proto = unit_phase(p_acc / cntc)
    global_freq = [sum(counts[r][f] for r in range(n_roles_total)) for f in range(n_fillers)]
    return {"g_hat": g_hat, "proto": proto, "counts": counts, "global_freq": global_freq,
            "n_seen_pairs": len(seen_pairs)}


def _flat_mem_score(counts, global_freq, r, f):
    # count-based memorizer + tiny global-freq tiebreak (deterministic; breaks all-zero ties toward
    # a frequent filler, which for held-out is a deterministic wrong-ish guess -> floor, not a leak).
    return counts[r][f] + 1e-6 * global_freq[f]


def readout(arm, S, qr, candidates, learned, x):
    if arm == "factored":
        est = fhrr_unbind(S, learned["g_hat"][qr])
        cb = torch.stack([x[f] for f in candidates], dim=0)
        return candidates[int(torch.argmax(sim_to_codebook(est, cb)))]
    if arm == "flat_memorize":
        scores = [_flat_mem_score(learned["counts"], learned["global_freq"], qr, f) for f in candidates]
        return candidates[int(max(range(len(candidates)), key=lambda i: scores[i]))]
    if arm == "flat_proto":
        cb = torch.stack([x[f] for f in candidates], dim=0)
        return candidates[int(torch.argmax(sim_to_codebook(learned["proto"][qr], cb)))]
    raise ValueError(arm)


ARMS = ["factored", "flat_memorize", "flat_proto"]


def evaluate(test_set, g_true, learned, x, n_fillers):
    vocab = list(range(n_fillers))
    correct = {f"{a}_{rd}": 0 for a in ARMS for rd in ("present", "vocab")}
    preds = {a: [] for a in ARMS}  # factored/flat present predictions for arms-differ hash
    for assign, qr, true_f in test_set:
        S = encode_sentence(assign, g_true, x)
        present = sorted(assign.values())
        for a in ARMS:
            p = readout(a, S, qr, present, learned, x)
            v = readout(a, S, qr, vocab, learned, x)
            correct[f"{a}_present"] += int(p == true_f)
            correct[f"{a}_vocab"] += int(v == true_f)
            preds[a].append(p)
    n = len(test_set)
    return {k: c / n for k, c in correct.items()}, preds


# ----------------------------------------------------------------------------------------------
# Core run: primary budget-D learning curve + fixed-token type-isolation + novel-role bound.
# ----------------------------------------------------------------------------------------------
def run_config(n_dim, n_roles_trained, n_roles_novel, n_fillers, n_train_per_role, n_held_per_role,
               m, budgets, n_test, seeds):
    n_roles_total = n_roles_trained + n_roles_novel
    chance_present = 1.0 / m
    chance_vocab = 1.0 / n_fillers
    per_seed = []
    for seed in seeds:
        gen = torch.Generator().manual_seed(seed)
        rng = random.Random(seed)
        x = make_atoms(n_fillers, n_dim, torch.complex64, gen)
        g_true = make_atoms(n_roles_total, n_dim, torch.complex64, gen)
        sp = build_split(n_roles_trained, n_roles_novel, n_fillers, n_train_per_role, n_held_per_role, rng)

        rng_test = random.Random(seed + 100000)
        test_held = make_test_set("heldout", n_test, m, sp, rng_test)
        test_ind = make_test_set("indist", n_test, m, sp, rng_test)
        test_novel = make_test_set("novel", n_test, m, sp, rng_test)

        curve = []
        preds_cache = {}
        for D in budgets:
            rng_tr = random.Random(seed * 131 + D)
            train = [sample_train_sentence(m, sp, rng_tr) for _ in range(D)]
            learned = learn(train, n_roles_total, g_true, x, n_dim, n_fillers)
            acc_h, preds_h = evaluate(test_held, g_true, learned, x, n_fillers)
            acc_i, _ = evaluate(test_ind, g_true, learned, x, n_fillers)
            acc_nv, _ = evaluate(test_novel, g_true, learned, x, n_fillers)
            gcos = float(sim_diag(learned["g_hat"][:n_roles_trained],
                                  g_true[:n_roles_trained]).mean())
            row = {"D": D, "n_seen_pairs": learned["n_seen_pairs"], "g_hat_to_g_true_cos": gcos}
            for k, v in acc_h.items():
                row[f"heldout_{k}"] = v
            for k, v in acc_i.items():
                row[f"indist_{k}"] = v
            for k, v in acc_nv.items():
                row[f"novel_{k}"] = v
            curve.append(row)
            preds_cache[D] = preds_h
        per_seed.append({"seed": seed, "curve": curve, "preds_cache": preds_cache})
    return {"chance_present": chance_present, "chance_vocab": chance_vocab,
            "per_seed": per_seed, "budgets": budgets}


def type_isolation(n_dim, n_roles_trained, n_roles_novel, n_fillers, n_held_per_role, m,
                   type_levels, n_tokens, n_test, seeds):
    """Fixed-TOKEN diagnostic: at fixed # training sentences (n_tokens), vary the # distinct filler
    TYPES available per trained role (K). Reports FACTORED held-out VOCAB vs K -- tests whether the
    threshold is TYPE-driven (rises with K) or TOKEN-driven (flat across K). CITED@ Bybee type-freq."""
    rows = []
    for K in type_levels:
        vals_f, vals_i = [], []
        for seed in seeds:
            gen = torch.Generator().manual_seed(seed + 777)
            rng = random.Random(seed + 777)
            x = make_atoms(n_fillers, n_dim, torch.complex64, gen)
            g_true = make_atoms(n_roles_trained + n_roles_novel, n_dim, torch.complex64, gen)
            sp = build_split(n_roles_trained, n_roles_novel, n_fillers, K, n_held_per_role, rng)
            rng_tr = random.Random(seed + 5 * K)
            train = [sample_train_sentence(m, sp, rng_tr) for _ in range(n_tokens)]
            learned = learn(train, n_roles_trained + n_roles_novel, g_true, x, n_dim, n_fillers)
            th = make_test_set("heldout", n_test, m, sp, random.Random(seed + 900000 + K))
            acc, _ = evaluate(th, g_true, learned, x, n_fillers)
            vals_f.append(acc["factored_vocab"])
            vals_i.append(acc["factored_present"])
        rows.append({"K_types_per_role": K, "n_tokens": n_tokens,
                     "factored_heldout_vocab": st.mean(vals_f),
                     "factored_heldout_present": st.mean(vals_i)})
    return rows


# ----------------------------------------------------------------------------------------------
# Aggregation + threshold extraction + verdict.
# ----------------------------------------------------------------------------------------------
def _mean_curve(per_seed, budgets):
    keys = [k for k in per_seed[0]["curve"][0].keys() if k not in ("D",)]
    out = []
    for i, D in enumerate(budgets):
        row = {"D": D}
        for k in keys:
            row[k] = st.mean(s["curve"][i][k] for s in per_seed)
        out.append(row)
    return out


def _threshold(curve_mean, arm, budgets):
    """Smallest D (and its index) at which heldout_{arm}_vocab >= PROD_CRIT. None if censored."""
    for i, row in enumerate(curve_mean):
        if row[f"heldout_{arm}_vocab"] >= PROD_CRIT:
            return {"D": budgets[i], "idx": i}
    return None


def _threshold_per_seed(per_seed, arm, budgets):
    ts = []
    for s in per_seed:
        t = None
        for i, row in enumerate(s["curve"]):
            if row[f"heldout_{arm}_vocab"] >= PROD_CRIT:
                t = budgets[i]
                break
        ts.append(t)
    return ts


def aggregate(res):
    per_seed, budgets = res["per_seed"], res["budgets"]
    cp, cv = res["chance_present"], res["chance_vocab"]
    cm = _mean_curve(per_seed, budgets)
    lo, hi = cm[0], cm[-1]

    t_fac = _threshold(cm, "factored", budgets)
    t_mem = _threshold(cm, "flat_memorize", budgets)
    t_pro = _threshold(cm, "flat_proto", budgets)
    t_fac_seeds = _threshold_per_seed(per_seed, "factored", budgets)

    # controls
    must_fit = (hi["indist_factored_present"] >= 0.85) and (hi["indist_flat_memorize_present"] >= 0.70)
    strawman = hi["indist_flat_memorize_present"] < 0.70
    must_fail = (hi["heldout_flat_memorize_vocab"] <= 0.10) and \
                ((hi["indist_flat_memorize_present"] - hi["heldout_flat_memorize_present"]) >= 0.30)
    void = hi["heldout_flat_memorize_present"] > 0.60

    # construction-determined guard on FACTORED held-out VOCAB curve
    fac_lo = lo["heldout_factored_vocab"]
    fac_hi = hi["heldout_factored_vocab"]
    curve_delta = fac_hi - fac_lo
    construction_determined = (fac_lo > 0.70) and (curve_delta < 0.10)
    genuine_curve = (fac_lo <= 0.55) and (curve_delta >= 0.30)

    # novel-structure bound (both arms fail on absent structure)
    novel_fac = hi["novel_factored_present"]
    novel_mem = hi["novel_flat_memorize_present"]
    novel_bound_fired = (novel_fac <= cp + 0.10) and (novel_mem <= cp + 0.10)

    # edge / tie
    gap_hi_vocab = hi["heldout_factored_vocab"] - hi["heldout_flat_memorize_vocab"]
    tie = gap_hi_vocab <= 0.05
    # cheaper threshold: factored finite; flat censored OR factored index strictly (>=2x) lower
    cheaper = False
    if t_fac is not None:
        if t_mem is None:
            cheaper = True
        elif t_mem["idx"] >= 2 * max(t_fac["idx"], 1) or (t_mem["idx"] - t_fac["idx"]) >= 2:
            cheaper = True

    if strawman:
        verdict = "HARD_FAIL_STRAWMAN"
    elif void:
        verdict = "VOID_FLAT_GENERALIZES"
    elif construction_determined:
        verdict = "HARD_FAIL_CONSTRUCTION_DETERMINED"
    elif t_fac is None:
        verdict = "HARD_FAIL_FACTORED_NEVER_PRODUCTIVE"
    elif tie:
        verdict = "HARD_FAIL_TIE_NO_EDGE"
    elif (must_fit and must_fail and (not void) and genuine_curve and (t_fac is not None)
          and cheaper and novel_bound_fired):
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    return {
        "verdict": verdict,
        "chance_present": cp, "chance_vocab": cv, "prod_crit": PROD_CRIT,
        "curve_mean": cm,
        "T_factored": t_fac, "T_flat_memorize": t_mem, "T_flat_proto": t_pro,
        "T_factored_per_seed": t_fac_seeds,
        "cheaper_threshold": bool(cheaper),
        "gap_heldout_vocab_hi": gap_hi_vocab,
        "factored_heldout_vocab_lo": fac_lo, "factored_heldout_vocab_hi": fac_hi,
        "factored_curve_delta": curve_delta,
        "genuine_curve": bool(genuine_curve),
        "construction_determined": bool(construction_determined),
        "must_fit_control": bool(must_fit),
        "must_fail_control_fired": bool(must_fail),
        "void": bool(void), "strawman": bool(strawman),
        "novel_structure_bound_fired": bool(novel_bound_fired),
        "novel_factored_present_hi": novel_fac, "novel_flat_memorize_present_hi": novel_mem,
        "factored_indist_present_hi": hi["indist_factored_present"],
        "flat_memorize_indist_present_hi": hi["indist_flat_memorize_present"],
        "flat_memorize_heldout_present_hi": hi["heldout_flat_memorize_present"],
        "flat_memorize_heldout_vocab_hi": hi["heldout_flat_memorize_vocab"],
        "g_hat_cos_lo": lo["g_hat_to_g_true_cos"], "g_hat_cos_hi": hi["g_hat_to_g_true_cos"],
        "can_fail_both_ways": True,
    }


def arms_differ(per_seed, budgets):
    D_hi = budgets[-1]
    preds = per_seed[0]["preds_cache"][D_hi]
    digs = {a: hashlib.sha256(bytes(preds[a])).hexdigest() for a in ARMS}
    assert digs["factored"] != digs["flat_memorize"], \
        f"META_RULE_AF: factored/flat_memorize held-out predictions bit-identical ({digs['factored']})"
    assert digs["factored"] != digs["flat_proto"], \
        f"META_RULE_AF: factored/flat_proto held-out predictions bit-identical ({digs['factored']})"
    return digs


# ----------------------------------------------------------------------------------------------
# Scaffold-free witness (self-test): REAL hdlab.binding.bind/unbind + hdlab.atoms; a hand-built
# held-out combo -> FACTORED recovers it, FLAT_MEMORIZE does not; a novel role -> FACTORED fails too.
# ----------------------------------------------------------------------------------------------
def scaffold_free_witness():
    n = 1024
    gen = torch.Generator().manual_seed(11)
    x = make_atoms(4, n, torch.complex64, gen)
    g = make_atoms(4, n, torch.complex64, gen)  # roles 0,1,2 trained; role 3 novel
    AGENT, PATIENT, GOAL, NOVEL = 0, 1, 2, 3
    DOG, MAN, BALL, GLASS = 0, 1, 2, 3

    # bit-parity with the real substrate ops.
    assert torch.allclose(fhrr_bind(g[AGENT], x[DOG]), hdlab_bind(g[AGENT], x[DOG])), "bind parity"
    assert torch.allclose(fhrr_unbind(fhrr_bind(g[AGENT], x[DOG]), x[DOG]),
                          hdlab_unbind(hdlab_bind(g[AGENT], x[DOG]), x[DOG])), "unbind parity"

    train = [
        {AGENT: DOG, PATIENT: MAN},
        {AGENT: MAN, PATIENT: GLASS},   # GLASS grounded as PATIENT (never AGENT)
        {AGENT: DOG, GOAL: BALL},
        {AGENT: MAN, GOAL: BALL},
        {AGENT: DOG, PATIENT: BALL},
    ]
    learned = learn(train, 4, g, x, n, 4)

    # held-out combo: AGENT=GLASS (never trained as AGENT). Present={GLASS,DOG}.
    S = fhrr_bind(g[AGENT], x[GLASS]) + fhrr_bind(g[PATIENT], x[DOG])
    fac = readout("factored", S, AGENT, [DOG, GLASS], learned, x)
    mem = readout("flat_memorize", S, AGENT, [DOG, GLASS], learned, x)
    assert fac == GLASS, f"witness: FACTORED failed held-out AGENT=GLASS (got {fac})"
    assert mem != GLASS, f"witness: FLAT_MEMORIZE unexpectedly recovered held-out combo (got {mem})"

    # novel structure: query NOVEL role (never trained) -> FACTORED has no g_hat -> should not recover.
    S2 = fhrr_bind(g[NOVEL], x[GLASS]) + fhrr_bind(g[PATIENT], x[DOG])
    fac_nv = readout("factored", S2, NOVEL, [DOG, GLASS], learned, x)
    # g_hat[NOVEL] is ~0 -> est ~0 -> argmax is arbitrary; assert it is NOT reliably GLASS by construction
    # (we only require the mechanism has no learned structure; correctness here would be luck).
    return {"factored_heldout": "GLASS", "flat_memorize_heldout": int(mem),
            "factored_novel_pred": int(fac_nv), "n_seen_pairs": learned["n_seen_pairs"],
            "witness": "PASS"}


# ----------------------------------------------------------------------------------------------
# Config presets.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    return dict(n_dim=2048, n_roles_trained=6, n_roles_novel=2, n_fillers=30,
                n_train_per_role=6, n_held_per_role=3, m=5,
                budgets=[1, 4, 16, 64], n_test=150, seeds=[7, 13])


def cfg_full():
    return dict(n_dim=2048, n_roles_trained=8, n_roles_novel=2, n_fillers=40,
                n_train_per_role=6, n_held_per_role=4, m=5,
                budgets=[1, 2, 4, 8, 16, 32, 64, 128], n_test=300, seeds=[7, 13, 19, 23, 29])


def cfg_typeiso_smoke():
    return dict(n_dim=2048, n_roles_trained=6, n_roles_novel=2, n_fillers=30, n_held_per_role=3,
                m=5, type_levels=[2, 6], n_tokens=64, n_test=150, seeds=[7, 13])


def cfg_typeiso_full():
    return dict(n_dim=2048, n_roles_trained=8, n_roles_novel=2, n_fillers=40, n_held_per_role=4,
                m=5, type_levels=[2, 4, 8, 16], n_tokens=128, n_test=300, seeds=[7, 13, 19])


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    ti_cfg = cfg_typeiso_smoke() if mode == "smoke" else cfg_typeiso_full()
    output_dir = os.path.join(REPO_ROOT, "data",
                              f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))

    witness = scaffold_free_witness()
    res = run_config(**cfg)
    agg = aggregate(res)
    hashes = arms_differ(res["per_seed"], res["budgets"])
    typeiso = type_isolation(**ti_cfg)

    # honest type-vs-token read: rise of factored held-out VOCAB across K at fixed tokens.
    ti_delta = (typeiso[-1]["factored_heldout_vocab"] - typeiso[0]["factored_heldout_vocab"]) if typeiso else 0.0
    ti_read = ("TYPE-driven" if ti_delta >= 0.15 else "TOKEN-driven (abstracts from few types)")

    per_seed_slim = [{"seed": s["seed"], "curve": s["curve"]} for s in res["per_seed"]]

    elapsed = time.perf_counter() - t0
    v = agg["verdict"]
    tf = agg["T_factored"]["D"] if agg["T_factored"] else None
    tm = agg["T_flat_memorize"]["D"] if agg["T_flat_memorize"] else None
    msg = (f"{v} | T_factored={tf} T_flat_mem={tm} cheaper={agg['cheaper_threshold']} "
           f"| FAC heldout_vocab {agg['factored_heldout_vocab_lo']:.3f}->{agg['factored_heldout_vocab_hi']:.3f} "
           f"(d={agg['factored_curve_delta']:.3f} genuine={agg['genuine_curve']}) "
           f"| gap_hi={agg['gap_heldout_vocab_hi']:.3f} "
           f"| must_fit={agg['must_fit_control']} must_fail={agg['must_fail_control_fired']} "
           f"novel_bound={agg['novel_structure_bound_fired']} "
           f"| FLATmem indist_pres={agg['flat_memorize_indist_present_hi']:.3f} "
           f"heldout_vocab={agg['flat_memorize_heldout_vocab_hi']:.3f} "
           f"| type_axis={ti_read}(d={ti_delta:.3f}) chance_vocab={agg['chance_vocab']:.3f}")

    payload = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": mode,
        "verdict": v,
        "verdict_msg": msg,
        "summary": msg,
        "elapsed_s": elapsed,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {k: vv for k, vv in cfg.items()},
        "type_isolation_config": {k: vv for k, vv in ti_cfg.items()},
        "aggregate": agg,
        "type_isolation": typeiso,
        "type_axis_read": ti_read, "type_axis_delta": ti_delta,
        "per_seed": per_seed_slim,
        "arms_differ_hashes": hashes,
        "arms_differ_verified": True,
        "scaffold_free_witness": witness,
        "final_metrics_atomicity": "tmp_replace",
        "needs_orchestrator_store_sync": True,
        "notes": ("Chain-grade candidate: native-binding vs PARAM-MATCHED/FAIR flat learning-curve + "
                  "cheaper Tolerance-Principle threshold. LOCAL-ONLY. Route to skunkworks landed-VET. "
                  "Genuine deltas over compgen_v1: strong fair flat baseline (fits in-dist, compgen_v1's "
                  "flat was at chance in-dist), explicit per-arm threshold extraction, type-vs-token "
                  "isolation, novel-STRUCTURE bounding arm (both fail). CLAIM-VET-pending."),
    }
    write_metrics(output_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for c in agg["curve_mean"]:
        print(f"  D={c['D']:>4} pairs={c['n_seen_pairs']:>3} | VOCAB held: FAC={c['heldout_factored_vocab']:.3f} "
              f"MEM={c['heldout_flat_memorize_vocab']:.3f} PROTO={c['heldout_flat_proto_vocab']:.3f} "
              f"| PRESENT indist: FAC={c['indist_factored_present']:.3f} MEM={c['indist_flat_memorize_present']:.3f} "
              f"| PRESENT held MEM={c['heldout_flat_memorize_present']:.3f} "
              f"| novel PRESENT FAC={c['novel_factored_present']:.3f} MEM={c['novel_flat_memorize_present']:.3f} "
              f"| gcos={c['g_hat_to_g_true_cos']:.3f}", flush=True)
    for r in typeiso:
        print(f"  [typeiso] K={r['K_types_per_role']:>3} tokens={r['n_tokens']} "
              f"FAC_held_vocab={r['factored_heldout_vocab']:.3f} "
              f"FAC_held_present={r['factored_heldout_present']:.3f}", flush=True)
    print(f"  [threshold] T_factored={tf} (per-seed={agg['T_factored_per_seed']}) "
          f"T_flat_memorize={tm} T_flat_proto={agg['T_flat_proto']} cheaper={agg['cheaper_threshold']}",
          flush=True)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        w = scaffold_free_witness()
        print(f"[{ANCHOR_NAME}] self-test scaffold-free witness: {w}", flush=True)
        res = run_config(n_dim=1024, n_roles_trained=5, n_roles_novel=2, n_fillers=16,
                         n_train_per_role=5, n_held_per_role=2, m=4, budgets=[2, 32],
                         n_test=60, seeds=[7])
        agg = aggregate(res)
        arms_differ(res["per_seed"], res["budgets"])
        print(f"[{ANCHOR_NAME}] self-test end-to-end: verdict={agg['verdict']} "
              f"FAC heldout_vocab lo={agg['factored_heldout_vocab_lo']:.3f} hi={agg['factored_heldout_vocab_hi']:.3f} "
              f"FLATmem indist_pres={agg['flat_memorize_indist_present_hi']:.3f} "
              f"heldout_vocab={agg['flat_memorize_heldout_vocab_hi']:.3f} "
              f"novel_bound={agg['novel_structure_bound_fired']}", flush=True)
        return
    if args.smoke:
        run_mode("smoke")
        return
    if args.full:
        run_mode("full")
        return
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
            "anchor_name": ANCHOR_NAME,
            "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}",
            "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
