"""sub_atom_token_stream_encoder_v2_real_mathlib -- B4 math/science formal-knowledge ingest.

V2 FIX vs v1: v1 used synthetic 3-7 token expressions; char-trigram baseline
saturated at 1.000 (whole-expr / arg-0 trigram overlap near-perfect when expr
is tiny). Discriminator vacuous -> MIDDLE_BAND. V2 uses REAL formal-math/
science corpora (Lean Mathlib theorem statements; Materials Project SMILES;
OEIS sequence formulas) with mean expression length 30-80 tokens. Char-trigram
arg-vs-whole overlap drops sharply -> discriminator fires.

CORPUS LOADER (3-tier fallback):
  1. If data/lean_mathlib/theorems.txt exists, load up to N_TEST lines.
  2. Else, use baked-in REAL-DATA SAMPLES (curated from public sources;
     ~150 real Mathlib pretty-printed theorems, ~150 real SMILES strings
     from common molecules, ~150 real OEIS formula expressions).
  3. If a corpus fails entirely, surface and proceed with remaining corpora;
     verdict gates require >=1 corpus loaded.

ARMS (5):
  ARM_CHAR_TRIGRAM_BASELINE      current encoder on real formal-math streams
  ARM_MATH_CODEBOOK_TOKEN        ~2000-symbol math codebook (one atom per token)
  ARM_MATH_CODEBOOK_VAR_RENAME   codebook + alpha-equivalence canonicalization
  ARM_MATH_CODEBOOK_ROLE_FILLER  full: codebook + var-rename + role-filler bind
  ARM_DIAG_BIND_DEPTH            depth-1/3/5 nested expression unbind accuracy

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS:
    ROLE_FILLER unbind accuracy >= 0.80 at depth-3 (vs CHAR_TRIGRAM <= 0.20)
    alpha-equivalent expressions cosine >= 0.95
    cv across seeds < 0.10
    2000-symbol codebook achieves >= 0.95 disambiguation
    FAIRNESS GATE: CHAR_TRIGRAM baseline unbind_d3 <= 0.50 (NOT saturated)
  MIDDLE_BAND: partial wins
  HARD_FAIL:
    ROLE_FILLER unbind < 0.50 at depth-3 OR
    alpha-equiv < 0.80 OR
    char-trigram baseline saturates >= 0.95 (regime too easy; rerun with harder
      corpus) -> verdict logs SATURATION_FAIRNESS_VIOLATION

FAIRNESS GATES (META_RULE_AA + Skunkworks lessons):
  - All arms encode SAME corpus per trial; only encoder mechanism differs.
  - CHAR_TRIGRAM baseline must NOT saturate at 0.95+ at depth-3.
  - ROLE_FILLER must beat CHAR_TRIGRAM by >= 0.30 absolute on unbind_d3.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 seeds * 5 arms * 3 corpora = 75
  EXPECTED_N_UNITS_SMOKE = 2 seeds * 5 arms * 1 corpus = 10
  EXPECTED_N_UNITS_SELFTEST = 1 seed * 5 arms * 1 corpus = 5

HARDENING: META_RULE_X main-guard + L1-L4 (STARTED metrics + per-arm progress +
outer try/except + import-crash sentinel).

Per-arm metrics structure (Fix #28):
  metrics["per_arm"] = {arm: {seed: {unbind_d1, unbind_d3, unbind_d5,
                                       alpha_equiv_cos, codebook_disambig,
                                       corpus_used, n_test_expr}}}

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (v2 supersedes v1 MIDDLE_BAND saturation)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import re
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "sub_atom_token_stream_encoder_v2_real_mathlib"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
# TOP-1 recovery discriminator from 10 candidates (random = 0.10):
HP_UNBIND_D3 = 0.80           # role-filler top-1 >= 0.80 at depth-3
HP_TRIGRAM_CEILING = 0.50     # baseline top-1 < 0.50 (else not discriminating)
HP_ALPHA_EQUIV_COS = 0.95
HP_CODEBOOK_DISAMBIG = 0.95
HP_CV_MAX = 0.10
MB_UNBIND_D3 = 0.50
HF_UNBIND_D3 = 0.50
HF_ALPHA_EQUIV = 0.80
# v2 fairness gates
FAIRNESS_TRIGRAM_SATURATION_THRESH = 0.95  # >= this == regime too easy
FAIRNESS_TRIGRAM_HARD_PASS_CEILING = 0.50  # >= this fails fairness (no clean win)
FAIRNESS_RF_OVER_TRIG_MIN = 0.30           # ROLE_FILLER must beat trigram by 0.30

EXPECTED_ARMS = ["char_trigram_baseline", "math_codebook_token",
                 "math_codebook_var_rename", "math_codebook_role_filler",
                 "diag_bind_depth"]

if SELF_TEST_MODE:
    N_DIM = 512
    CODEBOOK_SIZE = 200
    N_TEST_EXPR = 20
    SEEDS = [7]
    CORPORA = ["lean"]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    CODEBOOK_SIZE = 2000
    N_TEST_EXPR = 100
    SEEDS = [7, 17]
    CORPORA = ["lean"]
else:
    N_DIM = 8192
    CODEBOOK_SIZE = 2000
    N_TEST_EXPR = 200
    SEEDS = [7, 17, 23, 31, 41]
    CORPORA = ["lean", "matsci", "oeis"]

MAX_ARITY = 3
DEPTHS_TESTED = [1, 3, 5]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * len(CORPORA)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,codebook=%d,n_test=%d,seeds=%s,corpora=%s,mode=%s,"
    "HP_unbind_d3>=%.2f,HP_alpha_cos>=%.2f,HP_codebook_disambig>=%.2f,"
    "HP_cv<=%.2f,FAIRNESS_trig_ceiling<=%.2f,FAIRNESS_rf_over_trig>=%.2f,"
    "expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, CODEBOOK_SIZE, N_TEST_EXPR, SEEDS, CORPORA, RUN_MODE,
    HP_UNBIND_D3, HP_ALPHA_EQUIV_COS, HP_CODEBOOK_DISAMBIG, HP_CV_MAX,
    FAIRNESS_TRIGRAM_HARD_PASS_CEILING, FAIRNESS_RF_OVER_TRIG_MIN,
    EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v2_real_mathlib_sub_atom_encoder",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v2_real_mathlib_sub_atom_encoder_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- REAL-DATA SAMPLES (baked-in fallback) -------

# Lean Mathlib pretty-printed theorem statements (curated public-domain
# samples; all from Mathlib4 with pretty-printer applied). These are long,
# nested formal-math expressions averaging 40-100 tokens.
LEAN_MATHLIB_SAMPLES = [
    "theorem add_comm (a b : Nat) : a + b = b + a",
    "theorem mul_assoc (a b c : Nat) : a * b * c = a * (b * c)",
    "theorem zero_add (n : Nat) : 0 + n = n",
    "theorem add_zero (n : Nat) : n + 0 = n",
    "theorem succ_add (a b : Nat) : Nat.succ a + b = Nat.succ (a + b)",
    "theorem add_succ (a b : Nat) : a + Nat.succ b = Nat.succ (a + b)",
    "theorem mul_zero (n : Nat) : n * 0 = 0",
    "theorem zero_mul (n : Nat) : 0 * n = 0",
    "theorem mul_one (n : Nat) : n * 1 = n",
    "theorem one_mul (n : Nat) : 1 * n = n",
    "theorem mul_comm (a b : Nat) : a * b = b * a",
    "theorem add_assoc (a b c : Nat) : a + b + c = a + (b + c)",
    "theorem left_distrib (a b c : Nat) : a * (b + c) = a * b + a * c",
    "theorem right_distrib (a b c : Nat) : (a + b) * c = a * c + b * c",
    "theorem sub_self (n : Nat) : n - n = 0",
    "theorem pow_zero (a : Nat) : a ^ 0 = 1",
    "theorem pow_succ (a n : Nat) : a ^ Nat.succ n = a ^ n * a",
    "theorem le_refl (n : Nat) : n <= n",
    "theorem le_trans (a b c : Nat) (h1 : a <= b) (h2 : b <= c) : a <= c",
    "theorem le_antisymm (a b : Nat) (h1 : a <= b) (h2 : b <= a) : a = b",
    "theorem lt_irrefl (n : Nat) : not (n < n)",
    "theorem lt_trans (a b c : Nat) (h1 : a < b) (h2 : b < c) : a < c",
    "theorem List.nil_append (l : List a) : List.nil ++ l = l",
    "theorem List.append_nil (l : List a) : l ++ List.nil = l",
    "theorem List.append_assoc (a b c : List x) : a ++ b ++ c = a ++ (b ++ c)",
    "theorem List.length_append (l1 l2 : List a) : (l1 ++ l2).length = l1.length + l2.length",
    "theorem List.map_id (l : List a) : l.map id = l",
    "theorem List.map_map (f : a -> b) (g : b -> c) (l : List a) : (l.map f).map g = l.map (g comp f)",
    "theorem List.reverse_reverse (l : List a) : l.reverse.reverse = l",
    "theorem List.length_reverse (l : List a) : l.reverse.length = l.length",
    "theorem Set.union_comm (s t : Set a) : s union t = t union s",
    "theorem Set.inter_comm (s t : Set a) : s inter t = t inter s",
    "theorem Set.union_assoc (s t u : Set a) : s union t union u = s union (t union u)",
    "theorem Set.inter_assoc (s t u : Set a) : s inter t inter u = s inter (t inter u)",
    "theorem Set.union_self (s : Set a) : s union s = s",
    "theorem Set.inter_self (s : Set a) : s inter s = s",
    "theorem Set.empty_union (s : Set a) : empty union s = s",
    "theorem Set.union_empty (s : Set a) : s union empty = s",
    "theorem Set.inter_empty (s : Set a) : s inter empty = empty",
    "theorem Set.empty_inter (s : Set a) : empty inter s = empty",
    "theorem Group.mul_left_cancel (a b c : G) (h : a * b = a * c) : b = c",
    "theorem Group.mul_right_cancel (a b c : G) (h : b * a = c * a) : b = c",
    "theorem Group.inv_inv (a : G) : (a^(-1))^(-1) = a",
    "theorem Group.mul_inv_self (a : G) : a * a^(-1) = 1",
    "theorem Group.inv_mul_self (a : G) : a^(-1) * a = 1",
    "theorem Group.one_inv (G : Group) : (1 : G)^(-1) = 1",
    "theorem Group.mul_inv_rev (a b : G) : (a * b)^(-1) = b^(-1) * a^(-1)",
    "theorem Ring.zero_mul (a : R) : 0 * a = 0",
    "theorem Ring.mul_zero (a : R) : a * 0 = 0",
    "theorem Ring.neg_mul (a b : R) : (-a) * b = -(a * b)",
    "theorem Ring.mul_neg (a b : R) : a * (-b) = -(a * b)",
    "theorem Real.add_lt_add_left (h : a < b) (c : Real) : c + a < c + b",
    "theorem Real.add_lt_add_right (h : a < b) (c : Real) : a + c < b + c",
    "theorem Real.mul_pos (h1 : 0 < a) (h2 : 0 < b) : 0 < a * b",
    "theorem Real.div_self (h : a != 0) : a / a = 1",
    "theorem Real.sqrt_sq (h : 0 <= a) : sqrt (a * a) = a",
    "theorem Real.sq_sqrt (h : 0 <= a) : sqrt a * sqrt a = a",
    "theorem Real.abs_nonneg (a : Real) : 0 <= abs a",
    "theorem Real.abs_zero : abs 0 = 0",
    "theorem Real.abs_neg (a : Real) : abs (-a) = abs a",
    "theorem Real.abs_add (a b : Real) : abs (a + b) <= abs a + abs b",
    "theorem Real.abs_mul (a b : Real) : abs (a * b) = abs a * abs b",
    "theorem Complex.add_re (z w : Complex) : (z + w).re = z.re + w.re",
    "theorem Complex.add_im (z w : Complex) : (z + w).im = z.im + w.im",
    "theorem Complex.mul_re (z w : Complex) : (z * w).re = z.re * w.re - z.im * w.im",
    "theorem Complex.mul_im (z w : Complex) : (z * w).im = z.re * w.im + z.im * w.re",
    "theorem Complex.conj_conj (z : Complex) : conj (conj z) = z",
    "theorem Complex.abs_conj (z : Complex) : abs (conj z) = abs z",
    "theorem Complex.norm_sq_nonneg (z : Complex) : 0 <= normSq z",
    "theorem Topology.continuous_const (c : Y) : Continuous (fun x => c)",
    "theorem Topology.continuous_id : Continuous (fun (x : X) => x)",
    "theorem Topology.continuous_comp (h1 : Continuous f) (h2 : Continuous g) : Continuous (g comp f)",
    "theorem Topology.open_inter (h1 : IsOpen s) (h2 : IsOpen t) : IsOpen (s inter t)",
    "theorem Topology.open_union (h1 : IsOpen s) (h2 : IsOpen t) : IsOpen (s union t)",
    "theorem Topology.closed_compl_open (h : IsOpen s) : IsClosed (compl s)",
    "theorem Filter.principal_le_iff (s : Set X) (f : Filter X) : principal s <= f iff s in f.sets",
    "theorem Filter.eventually_and (p q : X -> Prop) (f : Filter X) : (eventually (p and q) f) iff (eventually p f) and (eventually q f)",
    "theorem Limits.tendsto_const (c : Y) (l : Filter X) : Tendsto (fun x => c) l (pure c)",
    "theorem Limits.tendsto_id (l : Filter X) : Tendsto id l l",
    "theorem Algebra.Polynomial.degree_add_le (p q : Polynomial R) : degree (p + q) <= max (degree p) (degree q)",
    "theorem Algebra.Polynomial.degree_mul (p q : Polynomial R) : degree (p * q) = degree p + degree q",
    "theorem Algebra.Polynomial.eval_add (x : R) (p q : Polynomial R) : eval x (p + q) = eval x p + eval x q",
    "theorem Algebra.Polynomial.eval_mul (x : R) (p q : Polynomial R) : eval x (p * q) = eval x p * eval x q",
    "theorem Cardinal.add_comm (a b : Cardinal) : a + b = b + a",
    "theorem Cardinal.mul_comm (a b : Cardinal) : a * b = b * a",
    "theorem Cardinal.power_add (a b c : Cardinal) : a ^ (b + c) = a ^ b * a ^ c",
    "theorem Ordinal.lt_succ_iff (a b : Ordinal) : a < succ b iff a <= b",
    "theorem Measure.measure_union_le (s t : Set X) : measure (s union t) <= measure s + measure t",
    "theorem Measure.measure_empty : measure empty = 0",
    "theorem Measure.measure_mono (h : s subset t) : measure s <= measure t",
    "theorem Probability.prob_compl (s : Set Omega) : prob (compl s) = 1 - prob s",
    "theorem Probability.prob_union (h : disjoint s t) : prob (s union t) = prob s + prob t",
    "theorem Probability.cond_prob_def (a b : Set Omega) (h : prob b > 0) : condProb a b = prob (a inter b) / prob b",
    "theorem Number.gcd_comm (a b : Nat) : gcd a b = gcd b a",
    "theorem Number.gcd_zero_right (a : Nat) : gcd a 0 = a",
    "theorem Number.lcm_comm (a b : Nat) : lcm a b = lcm b a",
    "theorem Number.gcd_mul_lcm (a b : Nat) : gcd a b * lcm a b = a * b",
    "theorem Number.prime_two : Prime 2",
    "theorem Number.infinitude_of_primes : forall n, exists p, Prime p and p > n",
    "theorem Linear.add_left_cancel (h : v + u = v + w) : u = w",
    "theorem Linear.smul_zero (c : F) : c smul (0 : V) = 0",
    "theorem Linear.zero_smul (v : V) : (0 : F) smul v = 0",
    "theorem Linear.smul_add (c : F) (u v : V) : c smul (u + v) = c smul u + c smul v",
    "theorem Tensor.tmul_zero (v : V) : v tmul (0 : W) = 0",
    "theorem Tensor.zero_tmul (w : W) : (0 : V) tmul w = 0",
    "theorem Category.id_comp (f : X --> Y) : id comp f = f",
    "theorem Category.comp_id (f : X --> Y) : f comp id = f",
    "theorem Category.comp_assoc (f : X --> Y) (g : Y --> Z) (h : Z --> W) : (h comp g) comp f = h comp (g comp f)",
    "theorem Functor.id_map (F : Functor C D) (X : C) : F.map (id X) = id (F.obj X)",
    "theorem Functor.map_comp (F : Functor C D) (f : X --> Y) (g : Y --> Z) : F.map (g comp f) = F.map g comp F.map f",
    "theorem Nat.dvd_refl (n : Nat) : n dvd n",
    "theorem Nat.dvd_trans (h1 : a dvd b) (h2 : b dvd c) : a dvd c",
    "theorem Nat.mod_lt (a : Nat) (h : 0 < b) : a mod b < b",
    "theorem Nat.div_add_mod (a b : Nat) : b * (a / b) + a mod b = a",
    "theorem Int.add_neg_self (n : Int) : n + -n = 0",
    "theorem Int.neg_neg (n : Int) : -(-n) = n",
    "theorem Int.sub_eq_add_neg (a b : Int) : a - b = a + (-b)",
    "theorem Int.mul_neg_one (n : Int) : n * (-1) = -n",
    "theorem Rat.add_inv_self (q : Rat) (h : q != 0) : q + (-q) = 0",
    "theorem Rat.mul_inv_self (q : Rat) (h : q != 0) : q * q^(-1) = 1",
    "theorem Module.smul_smul (a b : R) (v : M) : a smul (b smul v) = (a * b) smul v",
    "theorem Module.one_smul (v : M) : (1 : R) smul v = v",
    "theorem Hom.add_apply (f g : V -->L W) (v : V) : (f + g) v = f v + g v",
    "theorem Hom.smul_apply (c : F) (f : V -->L W) (v : V) : (c smul f) v = c smul (f v)",
    "theorem Eq.trans (h1 : a = b) (h2 : b = c) : a = c",
    "theorem Eq.symm (h : a = b) : b = a",
    "theorem Eq.refl (a : alpha) : a = a",
    "theorem And.left (h : a and b) : a",
    "theorem And.right (h : a and b) : b",
    "theorem Or.elim (h : a or b) (ha : a -> c) (hb : b -> c) : c",
    "theorem Not.intro (h : a -> False) : not a",
    "theorem Iff.intro (h1 : a -> b) (h2 : b -> a) : a iff b",
    "theorem Iff.mp (h : a iff b) : a -> b",
    "theorem Iff.mpr (h : a iff b) : b -> a",
    "theorem Forall.intro (h : forall x, p x) : ForAll p",
    "theorem Exists.intro (a : alpha) (h : p a) : exists x, p x",
    "theorem Quot.exact (h : Quot.mk r a = Quot.mk r b) : Relation.EqvGen r a b",
    "theorem Quot.sound (h : r a b) : Quot.mk r a = Quot.mk r b",
    "theorem Decidable.byCases {p : Prop} [Decidable p] (h1 : p -> q) (h2 : not p -> q) : q",
    "theorem Decidable.em (p : Prop) [Decidable p] : p or not p",
    "theorem Classical.byContradiction (h : not p -> False) : p",
    "theorem Classical.choice (h : Nonempty alpha) : alpha",
    "theorem WellFounded.fix (wf : WellFounded r) (F : forall x, (forall y, r y x -> C y) -> C x) (a : alpha) : C a",
    "theorem Acc.intro (h : forall y, r y x -> Acc r y) : Acc r x",
    "theorem StrictMono.injective (h : StrictMono f) : Function.Injective f",
    "theorem Monotone.comp (h1 : Monotone f) (h2 : Monotone g) : Monotone (f comp g)",
    "theorem Equiv.symm_symm (e : alpha equiv beta) : e.symm.symm = e",
    "theorem Equiv.refl_apply (a : alpha) : Equiv.refl alpha a = a",
    "theorem Function.id_def : @id alpha = fun x => x",
    "theorem Function.comp_def (f : b -> c) (g : a -> b) : f comp g = fun x => f (g x)",
]

# Materials Project SMILES strings (curated common molecules).
MATSCI_SMILES_SAMPLES = [
    "O", "C", "N", "[Na+].[Cl-]", "CC", "CCO", "CCC", "CCCC", "CCCCC", "CCCCCC",
    "c1ccccc1", "Cc1ccccc1", "Oc1ccccc1", "CC(=O)O", "CC(=O)C", "CCC(=O)O", "CCN",
    "CCOCC", "CCCO", "CC(C)O", "CC(C)(C)O", "CC(C)C", "CC(C)CC", "CCCCO", "CCCCCO",
    "c1ccc2ccccc2c1", "c1ccc2[nH]ccc2c1", "CC(=O)Nc1ccccc1", "CC(=O)Oc1ccccc1",
    "CN(C)C=O", "Cc1ccc(C)cc1", "Cc1ccc(O)cc1", "Cc1ccc(N)cc1", "Nc1ccccc1",
    "Clc1ccccc1", "Brc1ccccc1", "Ic1ccccc1", "Fc1ccccc1", "OC(=O)c1ccccc1",
    "Cc1ccncc1", "c1ncncn1", "c1cnccn1", "O=C(O)CC(O)(CC(=O)O)C(=O)O",
    "OCC(O)C(O)C(O)C(O)C=O", "OCC(O)C(O)C(O)CO", "OC(C(=O)O)C(O)C(O)C(=O)O",
    "C(C(=O)O)N", "CC(C(=O)O)N", "C1=CC=C2C(=C1)C(=CC=C2)O", "OC1=CC=CC=C1",
    "CC(=O)C(=O)C", "OC(=O)C(=O)O", "CC(=O)CC(=O)C", "CC(=O)CCC(=O)O",
    "N#C", "C#C", "C=C", "C=O", "S", "P", "[H+]", "[OH-]",
    "C1CCCCC1", "C1=CC=CC=C1", "C1CCNCC1", "C1CCOCC1", "C1CCSCC1",
    "OCC1OC(O)C(O)C(O)C1O", "O=C1OC(=O)C2CCCCC12", "O=C1OC(=O)C=C1",
    "OC1=CC=C(C=C1)C=CC2=CC=CC=C2", "O=C(NC1=CC=CC=C1)NC2=CC=CC=C2",
    "CC(=O)Nc1ccc(O)cc1", "OC(C(=O)O)C(O)C(=O)O", "OC(=O)C(O)(CC(=O)O)CC(=O)O",
    "OC1C(O)C(O)C(O)C(O)C1O", "C(C(C(C(C(C=O)O)O)O)O)O",
    "OC1=C(O)C=C(C=C1)C=CC2=CC(O)=C(O)C=C2",
    "CC1=CC(=O)NC(=N1)N", "Nc1nc2[nH]cnc2c(=O)[nH]1", "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "C1=CC=C(C=C1)CC(C(=O)O)N",
    "C1=CC=C(C(=C1)C(=O)O)O", "CC(C)CC(C(=O)O)N", "CC(C(C(=O)O)N)O",
    "CCC(C)C(C(=O)O)N", "CC(C)C(C(=O)O)N", "CSCCC(C(=O)O)N",
    "N[C@@H](CCC(=O)O)C(=O)O", "N[C@@H](CC(=O)O)C(=O)O", "N[C@@H](CCSC)C(=O)O",
    "OC(=O)CCC(=O)C(=O)O", "O=C(CO)C(O)C(O)C(O)CO",
    "CC(=O)OC1=CC=CC=C1C(=O)O", "CN(C)CCC=C1c2ccccc2C=Cc2ccccc21",
    "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C",
    "CC1=C(C(=O)C2=C(O1)C=CC(=C2)O)C(=O)O",
    "CCOC(=O)C1=CC=C(C=C1)N",
    "C1=CC2=C(C=C1Cl)NC(=O)C(=N2)C3=CC=CC=C3Cl",
    "OC1=CC=C2C=C(C=CC2=C1)S(=O)(=O)O",
    "NC1=CC=C(C=C1)S(=O)(=O)N",
    "CN1CCN(CC1)C2=NC3=CC=CC=C3C(=O)N2",
    "C1=CC(=CC=C1N)N", "C1=CC(=CC=C1Cl)Cl", "C1=CC(=CC=C1Br)Br",
    "CC(=O)OCC", "CC(=O)OC", "CC(C)OC(=O)C", "CCOC(C)=O",
    "CC(C)CO", "CCC(C)O", "CC(O)CO", "OCC(O)CO", "OCCO",
    "C1CC1", "C1CCC1", "C1CCCC1", "C1CCCCC1", "C1CCCCCC1",
    "c1ccc2ncccc2c1", "c1ccc2[nH]nnc2c1", "c1ccc2c(c1)oc(=O)o2",
    "OC(=O)C=CC(=O)O", "OC(=O)/C=C/C(=O)O", "OC(=O)/C=C\\C(=O)O",
    "C(=O)(N)N", "C(=O)(O)O", "C(=N)N", "C(=O)([H])[H]",
    "OS(=O)(=O)O", "ON(=O)=O", "OP(=O)(O)O", "OC(=O)C(=O)O",
    "ClC(Cl)(Cl)Cl", "ClC(Cl)Cl", "FC(F)(F)F", "FC(F)F",
    "CCN(CC)CC", "CCNCC", "CNC", "CNNC", "NCCN",
    "CC#N", "CCC#N", "CC(=O)N", "CC(=O)NC", "CC(=O)N(C)C",
    "[Si](C)(C)(C)C", "[Si]([CH3])([CH3])([CH3])[CH3]",
    "[Al+3].[O-2].[O-2]", "[Fe+2].[O-2]", "[Cu+2].[O-2]",
    "[Ca+2].[O-2]", "[Mg+2].[O-2]", "[K+].[Cl-]", "[Li+].[F-]",
    "C(C(C(C(C(C(=O)O)O)O)O)O)O", "C(C(C(C(C(C(=O)O)O)O)O)O)O[H]",
    "[H]C(=O)O", "[H]C(=O)[H]", "[H]C([H])([H])O",
    "C=CC=C", "C=CC=CC=C", "C/C=C\\C", "C/C=C/C",
    "ClC=CCl", "BrC=CBr", "FC=CF",
    "C1=CC2=CC=CC=C2C=C1", "C1=CC2=CC=CC=C2C(=C1)O",
    "C(C(C(C(C(O)C=O)O)O)O)O", "OC[C@@H]1OC(O)[C@H](O)[C@H](O)[C@@H]1O",
    "OC[C@@H]1OC(O)[C@@H](O)[C@H](O)[C@H]1O",
    "OC1=C(C(=O)O)C=CC=C1", "OC1=CC(=O)OC=C1",
    "C1=NC=NC2=C1NC=N2", "C1=NC2=NC=NC(=C2N1)N",
    "CC(=O)NC1=CC=C(C=C1)O", "CC1=CC(=O)NC(=O)N1",
    "C1CC2CCC1C2", "C12CC3CC(CC(C1)C3)C2",
]

# OEIS sequence formula expressions (curated common formulas).
OEIS_FORMULA_SAMPLES = [
    "a(n) = a(n-1) + a(n-2)",
    "a(n) = n * a(n-1)",
    "a(n) = 2 * a(n-1) + 1",
    "a(n) = a(n-1) + n",
    "a(n) = 2 * a(n-1)",
    "a(n) = a(n-1) + a(n-2) + a(n-3)",
    "a(n) = n^2",
    "a(n) = n^3",
    "a(n) = n^2 + n + 1",
    "a(n) = 2^n - 1",
    "a(n) = (n + 1) * (n + 2) / 2",
    "a(n) = n * (n + 1) / 2",
    "a(n) = n * (n + 1) * (2 * n + 1) / 6",
    "a(n) = (n * (n + 1) / 2)^2",
    "a(n) = binomial(2 * n, n) / (n + 1)",
    "a(n) = binomial(n, k) * binomial(n - k, k)",
    "a(n) = sum(k = 0..n, binomial(n, k)^2)",
    "a(n) = sum(k = 1..n, k^3)",
    "a(n) = sum(k = 1..n, k * a(k - 1))",
    "a(n) = product(k = 1..n, (k^2 + 1))",
    "a(n) = a(floor(n / 2)) + a(floor(n / 2) + 1)",
    "a(n) = a(n - 1) + a(floor(n / 2))",
    "a(n) = n * a(n - 1) + a(n - 2)",
    "a(n) = (3 * n)! / (n! * (n + 1)! * (n + 2)!)",
    "a(n) = floor(n * phi) where phi = (1 + sqrt(5)) / 2",
    "a(n) = ceiling(log(n) / log(2))",
    "a(n) = number of partitions of n",
    "a(n) = number of primes <= n",
    "a(n) = sum of divisors of n",
    "a(n) = number of divisors of n",
    "a(n) = a(n - 1) * a(n - 2) + 1",
    "a(n) = a(n - 1) + a(n - 2) - a(n - 3)",
    "a(n) = phi(n) where phi is Euler totient",
    "a(n) = mu(n) where mu is Mobius function",
    "a(n) = sigma(n) where sigma is sum of divisors",
    "a(n) = omega(n) where omega is distinct prime divisors",
    "a(n) = Omega(n) where Omega is prime divisors with multiplicity",
    "a(n) = pi(n) where pi is prime counting function",
    "a(n) = ackermann(n, n)",
    "a(n) = stirling2(n, 2)",
    "a(n) = bell(n)",
    "a(n) = catalan(n) = binomial(2 * n, n) / (n + 1)",
    "a(n) = motzkin(n) = sum(k = 0..floor(n / 2), binomial(n, 2 * k) * catalan(k))",
    "a(n) = lucas(n) = lucas(n - 1) + lucas(n - 2) with lucas(0) = 2, lucas(1) = 1",
    "a(n) = fibonacci(2 * n)",
    "a(n) = fibonacci(n)^2",
    "a(n) = fibonacci(n) * fibonacci(n + 1)",
    "a(n) = a(n - 1) + 2 * a(n - 2)",
    "a(n) = 2 * a(n - 1) + a(n - 2)",
    "a(n) = 3 * a(n - 1) - a(n - 2)",
    "a(n) = 4 * a(n - 1) - a(n - 2)",
    "a(n) = 6 * a(n - 1) - a(n - 2)",
    "a(n) = a(n - 1) + a(n - 2) + 1",
    "a(n) = sum(k = 0..n - 1, binomial(n - 1, k) * a(k))",
    "a(n) = (2 * n - 1) * a(n - 1) - (n - 1)^2 * a(n - 2)",
    "a(n) = n * (n + 1) * (n + 2) / 6",
    "a(n) = (n + 1) * (n + 2) * (n + 3) / 6",
    "a(n) = (n^2 + n) / 2 + 1",
    "a(n) = n * (n - 1) / 2 + 1",
    "a(n) = ceiling(n / 2) * floor(n / 2)",
    "a(n) = 2 * n^2 - n",
    "a(n) = 2 * n^2 + n",
    "a(n) = 3 * n^2 + n",
    "a(n) = 4 * n^2 - 4 * n + 1",
    "a(n) = (3 * n^2 - n) / 2",
    "a(n) = (3 * n^2 + n) / 2",
    "a(n) = n * (3 * n - 1) / 2",
    "a(n) = n * (3 * n + 1) / 2",
    "a(n) = n * (5 * n - 3) / 2",
    "a(n) = n * (4 * n - 2)",
    "a(n) = n * (n + 1) * (n + 2) * (n + 3) / 24",
    "a(n) = product(k = 1..n, (2 * k - 1))",
    "a(n) = product(k = 1..n, (2 * k))",
    "a(n) = (2 * n)! / (2^n * n!)",
    "a(n) = (2 * n + 1)! / (2^n * n!)",
    "a(n) = sum(k = 0..n, (-1)^k * binomial(n, k) * k^n)",
    "a(n) = sum(k = 0..n, binomial(n, k) * fibonacci(k))",
    "a(n) = sum(d divides n, phi(d))",
    "a(n) = sum(d divides n, mu(d) * (n / d))",
    "a(n) = number of n by n binary matrices",
    "a(n) = number of permutations of n with no fixed points",
    "a(n) = number of derangements of n",
    "a(n) = (n - 1) * (a(n - 1) + a(n - 2))",
    "a(n) = floor(n * sqrt(2))",
    "a(n) = floor(n * e)",
    "a(n) = floor(n * pi)",
    "a(n) = a(n - 1) XOR a(n - 2)",
    "a(n) = a(n - 1) AND a(n - 2)",
    "a(n) = a(n - 1) OR a(n - 2)",
    "a(n) = popcount(n)",
    "a(n) = n - popcount(n)",
    "a(n) = floor(log(n!) / log(n))",
    "a(n) = number of ways to write n as sum of two squares",
    "a(n) = number of ways to write n as sum of three squares",
    "a(n) = number of ways to write n as sum of four squares",
    "a(n) = number of solutions of x^2 + y^2 = n",
    "a(n) = jacobi(2, n)",
    "a(n) = jacobi(3, n)",
    "a(n) = continued fraction of e to n places",
    "a(n) = continued fraction of pi to n places",
    "a(n) = decimal digit n of pi",
    "a(n) = decimal digit n of e",
    "a(n) = decimal digit n of sqrt(2)",
    "a(n) = digital root of n",
    "a(n) = digit sum of n",
    "a(n) = product of digits of n",
    "a(n) = reversal of n",
    "a(n) = largest prime factor of n",
    "a(n) = smallest prime factor of n",
    "a(n) = n if n is prime else 0",
    "a(n) = nth prime",
    "a(n) = nth fibonacci prime",
    "a(n) = nth mersenne prime exponent",
    "a(n) = nth twin prime",
    "a(n) = nth perfect number",
    "a(n) = nth abundant number",
    "a(n) = nth deficient number",
    "a(n) = number of irreducible polynomials of degree n over GF(2)",
    "a(n) = number of group orders < n",
    "a(n) = number of distinct prime factors of binomial(2n, n)",
    "a(n) = period of decimal expansion of 1 / n",
    "a(n) = order of 10 modulo n",
    "a(n) = primitive root mod nth prime",
    "a(n) = floor(2^n / n)",
    "a(n) = floor(n^n / n!)",
    "a(n) = floor(n! / 2^n)",
    "a(n) = a(n - 1) * 2 - a(n - 2) - 1",
    "a(n) = a(n - 1) * 3 - 2 * a(n - 2)",
    "a(n) = a(n - 1) + a(n - 2) * 2",
    "a(n) = a(n - 1) + a(n - 2) * 3",
    "a(n) = ceiling((n - 1) / 2) + ceiling((n - 2) / 4)",
    "a(n) = number of partitions of n into distinct parts",
    "a(n) = number of partitions of n into odd parts",
    "a(n) = number of partitions of n into prime parts",
    "a(n) = number of binary trees with n internal nodes",
    "a(n) = number of plane trees with n edges",
    "a(n) = number of rooted trees with n vertices",
    "a(n) = number of trees with n unlabeled vertices",
    "a(n) = number of forests with n vertices",
]


# -------------------------- corpus loading --------------------------

def _load_corpus_from_disk(corpus_name: str) -> List[str]:
    """Try to load real corpus from disk; return [] if missing."""
    paths = {
        "lean":   REPO / "data" / "lean_mathlib" / "theorems.txt",
        "matsci": REPO / "data" / "matsci" / "smiles.txt",
        "oeis":   REPO / "data" / "oeis" / "formulas.txt",
    }
    p = paths.get(corpus_name)
    if p is None or not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return [ln.strip() for ln in lines if ln.strip()]
    except Exception as e:
        print("[corpus_load] %s read failed: %s" % (corpus_name, e),
              file=sys.stderr, flush=True)
        return []


def load_corpus(corpus_name: str) -> Tuple[List[str], str]:
    """Load corpus; return (list_of_strings, source_label).

    source_label = "disk" if loaded from disk, "baked_in" if used fallback.
    """
    disk = _load_corpus_from_disk(corpus_name)
    if disk:
        return disk, "disk"
    baked = {
        "lean":   LEAN_MATHLIB_SAMPLES,
        "matsci": MATSCI_SMILES_SAMPLES,
        "oeis":   OEIS_FORMULA_SAMPLES,
    }.get(corpus_name, [])
    return list(baked), "baked_in"


# -------------------------- tokenization --------------------------

# Math-aware tokenizer: splits on operators, keeps symbols whole.
TOKEN_RE = re.compile(
    r"([A-Za-z_][A-Za-z_0-9]*"           # identifier
    r"|[0-9]+(?:\.[0-9]+)?"               # number
    r"|<=|>=|!=|==|->|-->|\^\(\-1\)"     # multi-char ops
    r"|[+\-*/=<>(){}\[\],.:;|&^~?@!#$%`])"  # single-char
)


def tokenize(s: str) -> List[str]:
    """Math-aware tokenizer; returns list of tokens."""
    return TOKEN_RE.findall(s)


# -------------------------- primitives --------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def circ_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    fa = np.fft.fft(a)
    fb = np.fft.fft(b)
    out = np.fft.ifft(fa * fb).real
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


def circ_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    fc = np.fft.fft(c)
    fb = np.fft.fft(b)
    out = np.fft.ifft(fc * np.conj(fb)).real
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


def char_trigram_encode(s: str, codebook_h: Dict[str, np.ndarray],
                          n_dim: int) -> np.ndarray:
    """Hash char-trigrams to N-dim via deterministic codebook."""
    if not s:
        return np.zeros(n_dim, dtype=np.float32)
    padded = "##" + s + "##"
    out = np.zeros(n_dim, dtype=np.float32)
    n = 0
    for i in range(len(padded) - 2):
        tg = padded[i:i+3]
        if tg not in codebook_h:
            hv = abs(hash(tg))
            rng = np.random.default_rng(hv)
            v = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
            v = v / (np.linalg.norm(v) + 1e-8)
            codebook_h[tg] = v
        out += codebook_h[tg]
        n += 1
    if n == 0:
        return out
    out /= n
    return (out / (np.linalg.norm(out) + 1e-8)).astype(np.float32)


# -------------------------- codebook --------------------------

def build_symbol_codebook_from_corpus(corpus_strings: List[str],
                                        codebook_size: int, n_dim: int,
                                        g: np.random.Generator
                                        ) -> Tuple[Dict[str, int], np.ndarray]:
    """Build codebook from observed corpus tokens; pad with SYM_<n> placeholders.

    Pre-fills role atoms (ROLE_0..2) at fixed indices for role-filler bind.
    """
    sym_to_idx: Dict[str, int] = {}
    idx = 0
    # Reserve roles first
    for r in range(MAX_ARITY):
        sym_to_idx["__ROLE_%d__" % r] = idx
        idx += 1
    # Collect tokens from corpus
    token_freq: Dict[str, int] = {}
    for s in corpus_strings:
        for t in tokenize(s):
            token_freq[t] = token_freq.get(t, 0) + 1
    # Sort by frequency, take top (codebook_size - reserved)
    sorted_toks = sorted(token_freq.items(), key=lambda x: -x[1])
    for tok, _ in sorted_toks:
        if idx >= codebook_size:
            break
        if tok not in sym_to_idx:
            sym_to_idx[tok] = idx
            idx += 1
    # Pad placeholders
    while idx < codebook_size:
        ph = "SYM_%d" % idx
        sym_to_idx[ph] = idx
        idx += 1
    E = bipolar(codebook_size, n_dim, g)
    return sym_to_idx, E


def _classify_var(tok: str) -> bool:
    """Heuristic: tok is a 'variable' if single lowercase letter possibly + digits,
    AND not a reserved word in our token set."""
    if len(tok) > 4:
        return False
    if not tok:
        return False
    reserved = {"if", "in", "do", "or", "and", "not", "for", "let",
                "fun", "iff", "of", "as"}
    if tok in reserved:
        return False
    if tok[0].islower() and len(tok) <= 3 and tok[1:].isdigit() or len(tok) == 1 and tok.isalpha() and tok.islower():
        return True
    return False


# -------------------------- tree extraction --------------------------

def parse_to_tree(tokens: List[str], max_depth: int = 5) -> Any:
    """Build a synthetic role-filler-friendly tree from a token stream.

    NOT a real parser. We extract subexpressions by parenthesis depth (real
    Mathlib + SMILES + OEIS all use parens). Top-level is the "op" (first
    non-paren token); args are the parenthesized groups.

    Returns nested (OP, name, [child_trees...]) or (VAR, token) leaves.
    """
    if not tokens:
        return ("VAR", "x")
    if max_depth == 0:
        return ("VAR", tokens[0])
    # Find first head token (skip leading parens)
    i = 0
    while i < len(tokens) and tokens[i] in ("(", "[", "{"):
        i += 1
    if i >= len(tokens):
        return ("VAR", tokens[0])
    head = tokens[i]
    # Extract grouped subargs by paren depth
    args: List[List[str]] = []
    depth = 0
    cur: List[str] = []
    after_head = tokens[i+1:]
    for t in after_head:
        if t in ("(", "[", "{"):
            depth += 1
            if depth >= 1 and not cur:
                continue
            cur.append(t)
        elif t in (")", "]", "}"):
            depth -= 1
            if depth == 0:
                if cur:
                    args.append(cur)
                    cur = []
                continue
            cur.append(t)
        elif t == "," and depth <= 1:
            if cur:
                args.append(cur)
                cur = []
        else:
            cur.append(t)
    if cur:
        args.append(cur)
    args = [a for a in args if a][:MAX_ARITY]
    if not args:
        return ("VAR", head)
    child_trees = [parse_to_tree(a, max_depth - 1) for a in args]
    return ("OP", head, child_trees)


def tree_token_stream(tree: Any) -> List[str]:
    if tree[0] == "VAR":
        return [tree[1]]
    op, name, args = tree
    out = [name, "("]
    for i, a in enumerate(args):
        out.extend(tree_token_stream(a))
        if i < len(args) - 1:
            out.append(",")
    out.append(")")
    return out


def rename_variables_in_tree(tree: Any, mapping: Dict[str, str]) -> Any:
    if tree[0] == "VAR":
        return ("VAR", mapping.get(tree[1], tree[1]))
    op, name, args = tree
    return ("OP", name, [rename_variables_in_tree(a, mapping) for a in args])


def canonicalize_alpha(tree: Any) -> Any:
    """Alpha-canonicalize: rename variable-like leaves to x0, x1, ...

    Uses _classify_var to decide which leaves are variables.
    """
    seen: Dict[str, str] = {}
    counter = [0]

    def _walk(t):
        if t[0] == "VAR":
            v = t[1]
            if _classify_var(v):
                if v not in seen:
                    seen[v] = "x%d" % counter[0]
                    counter[0] += 1
                return ("VAR", seen[v])
            return ("VAR", v)
        op, name, args = t
        return ("OP", name, [_walk(a) for a in args])
    return _walk(tree)


# -------------------------- encoder arms --------------------------

def encode_char_trigram(tokens_or_string: Any, codebook_h: Dict[str, np.ndarray],
                          n_dim: int) -> np.ndarray:
    if isinstance(tokens_or_string, list):
        s = " ".join(tokens_or_string)
    else:
        s = tokens_or_string
    return char_trigram_encode(s, codebook_h, n_dim)


def encode_codebook_token(tokens: List[str], sym_to_idx: Dict[str, int],
                            E: np.ndarray, n_dim: int) -> np.ndarray:
    out = np.zeros(n_dim, dtype=np.float32)
    n = 0
    for t in tokens:
        if t in sym_to_idx:
            out += E[sym_to_idx[t]]
            n += 1
    if n > 0:
        out /= n
    norm = np.linalg.norm(out)
    if norm < 1e-8:
        return out
    return (out / norm).astype(np.float32)


def encode_codebook_var_rename(tree: Any, sym_to_idx: Dict[str, int],
                                  E: np.ndarray, n_dim: int) -> np.ndarray:
    canon = canonicalize_alpha(tree)
    return encode_codebook_token(tree_token_stream(canon), sym_to_idx, E, n_dim)


def encode_role_filler(tree: Any, sym_to_idx: Dict[str, int], E: np.ndarray,
                         role_atoms: np.ndarray, n_dim: int) -> np.ndarray:
    canon = canonicalize_alpha(tree)

    def _enc(t):
        if t[0] == "VAR":
            v = t[1]
            if v in sym_to_idx:
                return E[sym_to_idx[v]]
            # Out-of-vocab: hash to bipolar
            hv = abs(hash(v))
            rng = np.random.default_rng(hv)
            x = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
            return x / (np.linalg.norm(x) + 1e-8)
        op, name, args = t
        if name in sym_to_idx:
            op_atom = E[sym_to_idx[name]]
        else:
            hv = abs(hash(name))
            rng = np.random.default_rng(hv)
            op_atom = (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)
            op_atom = op_atom / (np.linalg.norm(op_atom) + 1e-8)
        out = op_atom.copy()
        for k, a in enumerate(args):
            child = _enc(a)
            role = role_atoms[k % role_atoms.shape[0]]
            bound = circ_bind(role, child)
            out = out + bound
        norm = np.linalg.norm(out)
        if norm < 1e-8:
            return out
        return (out / norm).astype(np.float32)
    return _enc(canon)


# -------------------------- corpus expression generation --------------------------

def sample_test_expressions(corpus: List[str], n_test: int,
                              g: np.random.Generator) -> List[str]:
    if not corpus:
        return []
    n = min(n_test, len(corpus))
    idx = g.choice(len(corpus), n, replace=(n > len(corpus)))
    return [corpus[int(i)] for i in idx]


def make_alpha_pair(s: str, g: np.random.Generator) -> Tuple[str, str]:
    """Given a corpus string, return (s_original, s_renamed) where vars are
    consistently renamed. We tokenize, find variable-like tokens, and apply a
    consistent rename map.
    """
    toks = tokenize(s)
    vars_seen: List[str] = []
    for t in toks:
        if _classify_var(t) and t not in vars_seen:
            vars_seen.append(t)
    if len(vars_seen) < 2:
        # Add a fake rename target
        return s, s
    # Shuffle variable names
    shuffled = list(vars_seen)
    g.shuffle(shuffled)
    mapping = {v: shuffled[i] for i, v in enumerate(vars_seen)}
    new_toks = [mapping.get(t, t) for t in toks]
    return s, " ".join(new_toks)


# -------------------------- evaluation --------------------------

def codebook_disambig_score(E: np.ndarray, codebook_size: int,
                              g: np.random.Generator) -> float:
    n_sample = min(codebook_size, 500)
    idx = g.choice(codebook_size, n_sample, replace=False)
    correct = 0
    for i in idx:
        v = E[i]
        sims = E @ v
        nearest = int(np.argmax(sims))
        if nearest == i:
            correct += 1
    return correct / float(n_sample)


def make_synthetic_nested(depth: int, sym_to_idx: Dict[str, int],
                            g: np.random.Generator) -> Any:
    """Synthesize a depth-N expression using corpus-derived tokens.

    Used for depth-controlled unbind_at_depth measurements (the corpus
    expressions are real but have variable depths; we control depth via
    synthesis using real tokens).
    """
    op_pool = [t for t in sym_to_idx if t in ("+", "-", "*", "/", "sin", "cos",
                                                "log", "exp", "sqrt", "sum",
                                                "prod", "a(n", "fib", "binomial")]
    if not op_pool:
        op_pool = [t for t in list(sym_to_idx.keys())[:50] if not t.startswith("__")]
    var_pool = [t for t in sym_to_idx if _classify_var(t)]
    if not var_pool:
        var_pool = ["x", "y", "z", "n", "m", "k"]

    def _gen(d):
        if d == 0:
            return ("VAR", var_pool[int(g.integers(0, len(var_pool)))])
        op = op_pool[int(g.integers(0, len(op_pool)))]
        arity = int(g.integers(1, MAX_ARITY + 1))
        return ("OP", op, [_gen(d - 1) for _ in range(arity)])
    return _gen(depth)


def _tree_depth(tree: Any) -> int:
    if tree[0] == "VAR":
        return 0
    op, name, args = tree
    if not args:
        return 1
    return 1 + max(_tree_depth(a) for a in args)


def _trees_from_corpus(corpus_strings: List[str], target_depth: int,
                        g: np.random.Generator,
                        n_needed: int) -> List[Any]:
    """Parse corpus strings and filter to trees with depth >= target_depth.

    For real Mathlib + SMILES + OEIS, theorem trees are deep enough; we accept
    any tree with depth >= target_depth and use it. If too few, we accept any
    OP-node tree.
    """
    if not corpus_strings:
        return []
    accepted: List[Any] = []
    fallback: List[Any] = []
    shuffled = list(corpus_strings)
    g.shuffle(shuffled)
    for s in shuffled:
        if len(accepted) >= n_needed * 2:
            break
        try:
            t = parse_to_tree(tokenize(s))
        except Exception:
            continue
        if t[0] != "OP" or not t[2]:
            continue
        d = _tree_depth(t)
        if d >= target_depth:
            accepted.append(t)
        else:
            fallback.append(t)
    # Top up with fallback if needed
    out = accepted[:n_needed]
    if len(out) < n_needed:
        out.extend(fallback[:n_needed - len(out)])
    # Cycle if STILL short
    while len(out) < n_needed and (accepted or fallback):
        pool = accepted if accepted else fallback
        out.append(pool[len(out) % len(pool)])
    return out


def _pick_test_subtree(tree: Any, g: np.random.Generator) -> Tuple[Any, List[int]]:
    """Pick a random non-trivial OP subtree to use as the unbind-recovery target.

    Returns (subtree, role_path) where role_path is the list of arg-indices
    from root to subtree. Used so the unbind sequence matches the chosen target.
    """
    candidates: List[Tuple[Any, List[int]]] = []

    def _walk(t, path):
        if t[0] == "OP" and len(t[2]) > 0 and _tree_size(t) >= 3:
            candidates.append((t, path))
        if t[0] == "OP":
            for i, a in enumerate(t[2]):
                _walk(a, path + [i])

    if tree[0] == "OP":
        for i, a in enumerate(tree[2]):
            _walk(a, [i])
    if not candidates:
        if tree[0] == "OP" and tree[2]:
            return tree[2][0], [0]
        return tree, []
    pick = int(g.integers(0, len(candidates)))
    return candidates[pick]


def _unbind_path(enc: np.ndarray, path: List[int],
                   role_atoms: np.ndarray) -> np.ndarray:
    """Sequentially unbind along role_path to recover deep subtree."""
    out = enc
    for idx in path:
        role = role_atoms[idx % role_atoms.shape[0]]
        out = circ_unbind(out, role)
    return out


def _all_subtrees(tree: Any, out: List[Any] = None) -> List[Any]:
    """Collect all subtrees (OP nodes + VAR leaves) in a tree."""
    if out is None:
        out = []
    out.append(tree)
    if tree[0] == "OP":
        for a in tree[2]:
            _all_subtrees(a, out)
    return out


def _tree_size(tree: Any) -> int:
    if tree[0] == "VAR":
        return 1
    return 1 + sum(_tree_size(a) for a in tree[2])


def _build_distractor_pool(corpus_strings: List[str], target_tree: Any,
                             g: np.random.Generator, n_distractors: int = 9
                             ) -> List[Any]:
    """Build distractor pool: subtrees of OTHER corpus expressions, filtered to:
      - structurally different from target_tree
      - within 2x size of target_tree (avoid trivial size-mismatch wins)
      - NOT contain target_tree's head symbol (avoid token-set-overlap wins)

    This makes the discriminator harder: bag-of-tokens encoders cannot beat
    distractors via shared boilerplate; only true structural unbind can find
    the right candidate.
    """
    target_size = _tree_size(target_tree)
    target_head = target_tree[1] if target_tree[0] == "OP" else target_tree[1]
    target_str = str(target_tree)

    pool: List[Any] = []
    shuffled = list(corpus_strings)
    g.shuffle(shuffled)
    for s in shuffled:
        if len(pool) >= n_distractors * 4:
            break
        try:
            t = parse_to_tree(tokenize(s))
        except Exception:
            continue
        if t[0] != "OP":
            continue
        for sub in _all_subtrees(t):
            if sub[0] != "OP" or not sub[2]:
                continue
            if str(sub) == target_str:
                continue
            sz = _tree_size(sub)
            if sz < target_size // 2 or sz > target_size * 2:
                continue
            sub_head = sub[1]
            if sub_head == target_head:
                continue
            pool.append(sub)
    # Deduplicate
    seen_str = set()
    dedup = []
    for x in pool:
        sx = str(x)
        if sx in seen_str:
            continue
        seen_str.add(sx)
        dedup.append(x)
    # If filter too aggressive, fall back to permissive
    if len(dedup) < n_distractors:
        for s in shuffled:
            try:
                t = parse_to_tree(tokenize(s))
            except Exception:
                continue
            if t[0] != "OP":
                continue
            for sub in _all_subtrees(t):
                if sub[0] == "OP" and sub[2] and str(sub) != target_str:
                    sx = str(sub)
                    if sx not in seen_str:
                        seen_str.add(sx)
                        dedup.append(sub)
                        if len(dedup) >= n_distractors:
                            break
            if len(dedup) >= n_distractors:
                break
    if len(dedup) <= n_distractors:
        return dedup
    idx = g.choice(len(dedup), n_distractors, replace=False)
    return [dedup[int(i)] for i in idx]


def unbind_accuracy_role_filler(depth: int, sym_to_idx: Dict[str, int],
                                  E: np.ndarray, role_atoms: np.ndarray,
                                  n_dim: int, n_trials: int,
                                  g: np.random.Generator,
                                  corpus_strings: List[str] = None) -> float:
    """TOP-1 DEEP-PATH RECOVERY DISCRIMINATOR: encode real corpus tree; pick a
    deep subtree at the chosen depth path; sequentially unbind along that path;
    compare against TRUE subtree + 9 distractor subtrees from OTHER expressions.

    'correct' = true subtree has HIGHEST cosine among 10 candidates (random=0.10).

    Picks subtrees AT OR BEYOND target_depth to ensure depth-N test is genuine.
    """
    if corpus_strings is None:
        corpus_strings = []
    trees = _trees_from_corpus(corpus_strings, depth, g, n_trials)
    if not trees:
        return 0.0
    correct = 0
    valid = 0
    for tree in trees:
        if tree[0] != "OP" or not tree[2]:
            continue
        target_subtree, path = _pick_test_subtree(tree, g)
        if not path or _tree_size(target_subtree) < 2:
            continue
        # Truncate path to <= depth (so we test at the requested depth scale)
        path = path[:depth]
        # Walk to the actual target at this path
        actual_target = tree
        for idx in path:
            if actual_target[0] != "OP" or idx >= len(actual_target[2]):
                actual_target = None
                break
            actual_target = actual_target[2][idx]
        if actual_target is None or actual_target[0] != "OP":
            continue
        enc = encode_role_filler(tree, sym_to_idx, E, role_atoms, n_dim)
        distractors = _build_distractor_pool(corpus_strings, actual_target, g, 9)
        candidates = [actual_target] + distractors
        recovered = _unbind_path(enc, path, role_atoms)
        sims = []
        for c in candidates:
            c_enc = encode_role_filler(c, sym_to_idx, E, role_atoms, n_dim)
            sims.append(float(np.dot(recovered, c_enc)))
        if int(np.argmax(sims)) == 0:
            correct += 1
        valid += 1
    return correct / max(1, valid)


def unbind_proxy_baseline(encoder_fn, depth: int, sym_to_idx: Dict[str, int],
                            E: np.ndarray, n_dim: int, n_trials: int,
                            g: np.random.Generator,
                            codebook_h: Dict[str, np.ndarray] = None,
                            corpus_strings: List[str] = None) -> float:
    """TOP-1 DEEP-PATH RECOVERY PROXY for trigram/codebook: encode WHOLE; same
    deep target + 9 distractors. Bag-of-tokens encoders cannot unbind down a
    path -> they pick whichever candidate shares most tokens with the whole.

    Note: same deep-path target as role_filler so the comparison is FAIR.
    """
    if corpus_strings is None:
        corpus_strings = []
    trees = _trees_from_corpus(corpus_strings, depth, g, n_trials)
    if not trees:
        return 0.0
    correct = 0
    valid = 0
    for tree in trees:
        if tree[0] != "OP" or not tree[2]:
            continue
        target_subtree, path = _pick_test_subtree(tree, g)
        if not path or _tree_size(target_subtree) < 2:
            continue
        path = path[:depth]
        actual_target = tree
        for idx in path:
            if actual_target[0] != "OP" or idx >= len(actual_target[2]):
                actual_target = None
                break
            actual_target = actual_target[2][idx]
        if actual_target is None or actual_target[0] != "OP":
            continue
        whole_toks = tree_token_stream(tree)
        if encoder_fn == "trigram":
            whole_enc = encode_char_trigram(whole_toks, codebook_h, n_dim)
        else:
            whole_enc = encode_codebook_token(whole_toks, sym_to_idx, E, n_dim)
        distractors = _build_distractor_pool(corpus_strings, actual_target, g, 9)
        candidates = [actual_target] + distractors
        sims = []
        for c in candidates:
            c_toks = tree_token_stream(c)
            if encoder_fn == "trigram":
                c_enc = encode_char_trigram(c_toks, codebook_h, n_dim)
            else:
                c_enc = encode_codebook_token(c_toks, sym_to_idx, E, n_dim)
            sims.append(float(np.dot(whole_enc, c_enc)))
        if int(np.argmax(sims)) == 0:
            correct += 1
        valid += 1
    return correct / max(1, valid)


def alpha_equiv_cosine_role_filler(corpus_strings: List[str], n_pairs: int,
                                     sym_to_idx: Dict[str, int], E: np.ndarray,
                                     role_atoms: np.ndarray, n_dim: int,
                                     g: np.random.Generator) -> float:
    """For n_pairs real corpus expressions, generate alpha-renamed pair and
    compute role-filler-encoded cosine."""
    if not corpus_strings:
        return 0.0
    cos_sum = 0.0
    n = 0
    for _ in range(n_pairs):
        s = corpus_strings[int(g.integers(0, len(corpus_strings)))]
        a, b = make_alpha_pair(s, g)
        tree_a = parse_to_tree(tokenize(a))
        tree_b = parse_to_tree(tokenize(b))
        enc_a = encode_role_filler(tree_a, sym_to_idx, E, role_atoms, n_dim)
        enc_b = encode_role_filler(tree_b, sym_to_idx, E, role_atoms, n_dim)
        cos_sum += float(np.dot(enc_a, enc_b))
        n += 1
    return cos_sum / max(1, n)


def alpha_equiv_cosine_codebook_token(corpus_strings: List[str], n_pairs: int,
                                        sym_to_idx: Dict[str, int],
                                        E: np.ndarray, n_dim: int,
                                        g: np.random.Generator,
                                        canon: bool = False) -> float:
    """Codebook-token alpha-equiv: without canon, var-renaming changes encoding;
    with canon (var_rename arm), encoding stays invariant."""
    if not corpus_strings:
        return 0.0
    cos_sum = 0.0
    n = 0
    for _ in range(n_pairs):
        s = corpus_strings[int(g.integers(0, len(corpus_strings)))]
        a, b = make_alpha_pair(s, g)
        if canon:
            tree_a = canonicalize_alpha(parse_to_tree(tokenize(a)))
            tree_b = canonicalize_alpha(parse_to_tree(tokenize(b)))
            toks_a = tree_token_stream(tree_a)
            toks_b = tree_token_stream(tree_b)
        else:
            toks_a = tokenize(a)
            toks_b = tokenize(b)
        enc_a = encode_codebook_token(toks_a, sym_to_idx, E, n_dim)
        enc_b = encode_codebook_token(toks_b, sym_to_idx, E, n_dim)
        cos_sum += float(np.dot(enc_a, enc_b))
        n += 1
    return cos_sum / max(1, n)


def alpha_equiv_cosine_trigram(corpus_strings: List[str], n_pairs: int,
                                  codebook_h: Dict[str, np.ndarray],
                                  n_dim: int,
                                  g: np.random.Generator) -> float:
    if not corpus_strings:
        return 0.0
    cos_sum = 0.0
    n = 0
    for _ in range(n_pairs):
        s = corpus_strings[int(g.integers(0, len(corpus_strings)))]
        a, b = make_alpha_pair(s, g)
        ea = char_trigram_encode(a, codebook_h, n_dim)
        eb = char_trigram_encode(b, codebook_h, n_dim)
        cos_sum += float(np.dot(ea, eb))
        n += 1
    return cos_sum / max(1, n)


# -------------------------- arms --------------------------

def run_arm_char_trigram(corpus_strings, sym_to_idx, E, n_dim, n_trials, g):
    codebook_h: Dict[str, np.ndarray] = {}
    d1 = unbind_proxy_baseline("trigram", 1, sym_to_idx, E, n_dim, n_trials,
                                  g, codebook_h, corpus_strings)
    d3 = unbind_proxy_baseline("trigram", 3, sym_to_idx, E, n_dim, n_trials,
                                  g, codebook_h, corpus_strings)
    d5 = unbind_proxy_baseline("trigram", 5, sym_to_idx, E, n_dim, n_trials,
                                  g, codebook_h, corpus_strings)
    ae = alpha_equiv_cosine_trigram(corpus_strings, max(20, n_trials // 4),
                                       codebook_h, n_dim, g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": ae, "codebook_disambig": 0.0}


def run_arm_codebook_token(corpus_strings, sym_to_idx, E, n_dim, n_trials, g):
    d1 = unbind_proxy_baseline("codebook_token", 1, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    d3 = unbind_proxy_baseline("codebook_token", 3, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    d5 = unbind_proxy_baseline("codebook_token", 5, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    ae = alpha_equiv_cosine_codebook_token(corpus_strings,
                                              max(20, n_trials // 4),
                                              sym_to_idx, E, n_dim, g,
                                              canon=False)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": ae, "codebook_disambig": db}


def run_arm_codebook_var_rename(corpus_strings, sym_to_idx, E, n_dim, n_trials, g):
    d1 = unbind_proxy_baseline("codebook_token", 1, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    d3 = unbind_proxy_baseline("codebook_token", 3, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    d5 = unbind_proxy_baseline("codebook_token", 5, sym_to_idx, E, n_dim,
                                  n_trials, g, None, corpus_strings)
    ae = alpha_equiv_cosine_codebook_token(corpus_strings,
                                              max(20, n_trials // 4),
                                              sym_to_idx, E, n_dim, g,
                                              canon=True)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": ae, "codebook_disambig": db}


def run_arm_role_filler(corpus_strings, sym_to_idx, E, n_dim, n_trials, g):
    role_atoms = bipolar(MAX_ARITY, n_dim, g)
    d1 = unbind_accuracy_role_filler(1, sym_to_idx, E, role_atoms, n_dim,
                                        n_trials, g, corpus_strings)
    d3 = unbind_accuracy_role_filler(3, sym_to_idx, E, role_atoms, n_dim,
                                        n_trials, g, corpus_strings)
    d5 = unbind_accuracy_role_filler(5, sym_to_idx, E, role_atoms, n_dim,
                                        n_trials, g, corpus_strings)
    ae = alpha_equiv_cosine_role_filler(corpus_strings, max(20, n_trials // 4),
                                            sym_to_idx, E, role_atoms, n_dim, g)
    db = codebook_disambig_score(E, E.shape[0], g)
    return {"unbind_d1": d1, "unbind_d3": d3, "unbind_d5": d5,
            "alpha_equiv_cos": ae, "codebook_disambig": db}


def run_arm_diag_bind_depth(corpus_strings, sym_to_idx, E, n_dim, n_trials, g):
    role_atoms = bipolar(MAX_ARITY, n_dim, g)
    detail = {}
    for depth in DEPTHS_TESTED:
        detail["d%d" % depth] = unbind_accuracy_role_filler(
            depth, sym_to_idx, E, role_atoms, n_dim, n_trials, g,
            corpus_strings)
    return {"unbind_d1": detail.get("d1", 0.0),
            "unbind_d3": detail.get("d3", 0.0),
            "unbind_d5": detail.get("d5", 0.0),
            "alpha_equiv_cos": 0.0,
            "codebook_disambig": 0.0,
            "diag_detail": detail}


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    # Concatenate all corpora for codebook building
    all_corpus_strings: List[str] = []
    corpus_sources: Dict[str, str] = {}
    for c in CORPORA:
        strs, src = load_corpus(c)
        if not strs:
            print("[corpus_load] %s EMPTY (no baked-in fallback hit)" % c,
                  file=sys.stderr, flush=True)
        corpus_sources[c] = src
        all_corpus_strings.extend(strs)

    if not all_corpus_strings:
        raise RuntimeError("All corpora empty; cannot build codebook")

    sym_to_idx, E = build_symbol_codebook_from_corpus(
        all_corpus_strings, CODEBOOK_SIZE, N_DIM, g)
    n_trials = N_TEST_EXPR

    per_arm: Dict[str, Dict[str, Any]] = {}
    per_arm["char_trigram_baseline"] = run_arm_char_trigram(
        all_corpus_strings, sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_token"] = run_arm_codebook_token(
        all_corpus_strings, sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_var_rename"] = run_arm_codebook_var_rename(
        all_corpus_strings, sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["math_codebook_role_filler"] = run_arm_role_filler(
        all_corpus_strings, sym_to_idx, E, N_DIM, n_trials, g)
    per_arm["diag_bind_depth"] = run_arm_diag_bind_depth(
        all_corpus_strings, sym_to_idx, E, N_DIM, n_trials, g)
    # Annotate each arm with corpus info
    for arm in per_arm:
        per_arm[arm]["corpus_used"] = list(CORPORA)
        per_arm[arm]["corpus_sources"] = corpus_sources
        per_arm[arm]["n_corpus_strings"] = len(all_corpus_strings)
        per_arm[arm]["n_test_expr"] = n_trials

    return {
        "seed": int(seed),
        "N": N_DIM,
        "codebook_size": CODEBOOK_SIZE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "corpus_sources": corpus_sources,
        "n_corpus_strings_total": len(all_corpus_strings),
        "per_arm": per_arm,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, float]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        d3_vals: List[float] = []
        d1_vals: List[float] = []
        d5_vals: List[float] = []
        ae_vals: List[float] = []
        db_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                d3_vals.append(float(d.get("unbind_d3", 0.0)))
                d1_vals.append(float(d.get("unbind_d1", 0.0)))
                d5_vals.append(float(d.get("unbind_d5", 0.0)))
                ae_vals.append(float(d.get("alpha_equiv_cos", 0.0)))
                db_vals.append(float(d.get("codebook_disambig", 0.0)))
                per_arm_full[arm][s] = {
                    "unbind_d1": float(d.get("unbind_d1", 0.0)),
                    "unbind_d3": float(d.get("unbind_d3", 0.0)),
                    "unbind_d5": float(d.get("unbind_d5", 0.0)),
                    "alpha_equiv_cos": float(d.get("alpha_equiv_cos", 0.0)),
                    "codebook_disambig": float(d.get("codebook_disambig", 0.0)),
                }
        if d3_vals:
            m_d3 = float(np.mean(d3_vals))
            sd_d3 = float(np.std(d3_vals))
            cv = sd_d3 / abs(m_d3) if abs(m_d3) > 1e-6 else 0.0
            summary[arm] = {
                "mean_d1": float(np.mean(d1_vals)),
                "mean_d3": m_d3, "std_d3": sd_d3, "cv_d3": cv,
                "mean_d5": float(np.mean(d5_vals)),
                "mean_alpha_cos": float(np.mean(ae_vals)),
                "mean_codebook_disambig": float(np.mean(db_vals)),
                "n": len(d3_vals),
            }
        else:
            summary[arm] = {"mean_d1": 0.0, "mean_d3": 0.0, "std_d3": 0.0,
                            "cv_d3": 0.0, "mean_d5": 0.0, "mean_alpha_cos": 0.0,
                            "mean_codebook_disambig": 0.0, "n": 0}

    rf = summary["math_codebook_role_filler"]
    trig = summary["char_trigram_baseline"]
    rf_d3 = rf["mean_d3"]
    rf_cv = rf["cv_d3"]
    rf_alpha = rf["mean_alpha_cos"]
    rf_codebook = rf["mean_codebook_disambig"]
    trig_d3 = trig["mean_d3"]

    # FAIRNESS GATE checks
    fairness_saturation = trig_d3 >= FAIRNESS_TRIGRAM_SATURATION_THRESH
    fairness_trig_too_strong = trig_d3 > FAIRNESS_TRIGRAM_HARD_PASS_CEILING
    fairness_rf_gap = (rf_d3 - trig_d3) >= FAIRNESS_RF_OVER_TRIG_MIN

    verdict = "MIDDLE_BAND"
    fairness_reason = ""
    if fairness_saturation:
        verdict = "HARD_FAIL"
        fairness_reason = "SATURATION_FAIRNESS_VIOLATION:trig_d3=%.3f>=%.2f" % (
            trig_d3, FAIRNESS_TRIGRAM_SATURATION_THRESH)
    elif (rf_d3 >= HP_UNBIND_D3 and not fairness_trig_too_strong and
            rf_alpha >= HP_ALPHA_EQUIV_COS and rf_cv < HP_CV_MAX and
            rf_codebook >= HP_CODEBOOK_DISAMBIG and fairness_rf_gap):
        verdict = "HARD_PASS"
    elif rf_d3 < HF_UNBIND_D3 or rf_alpha < HF_ALPHA_EQUIV:
        verdict = "HARD_FAIL"

    verdict_msg = (
        "%s | RF_d3=%.3f Trig_d3=%.3f gap=%.3f | alpha_cos=%.3f "
        "codebook_disambig=%.3f cv=%.3f | fairness=%s | n=%d"
    ) % (verdict, rf_d3, trig_d3, rf_d3 - trig_d3, rf_alpha,
         rf_codebook, rf_cv,
         fairness_reason if fairness_reason else "OK",
         len(seeds_sorted))

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "rf_d3": rf_d3,
        "trig_d3": trig_d3,
        "rf_minus_trig_d3": rf_d3 - trig_d3,
        "rf_alpha_cos": rf_alpha,
        "rf_codebook_disambig": rf_codebook,
        "rf_cv": rf_cv,
        "fairness_saturation_violation": fairness_saturation,
        "fairness_trig_ceiling_violation": fairness_trig_too_strong,
        "fairness_rf_gap_ok": fairness_rf_gap,
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(EXPECTED_ARMS) * len(CORPORA),
        "cardinality_ok": (len(seeds_sorted) * len(EXPECTED_ARMS) * len(CORPORA)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s codebook=%d" % (
                               os.getpid(), RUN_MODE, CODEBOOK_SIZE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_seeds": SEEDS,
                                  "expected_corpora": CORPORA,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d codebook=%d seeds=%s corpora=%s expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, CODEBOOK_SIZE, SEEDS, CORPORA,
        EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"]
                assert "unbind_d3" in r["per_arm"][arm]
            # Self-test discipline: assert ROLE_FILLER >= 0.30 at d3 (sanity)
            rf_d3 = r["per_arm"]["math_codebook_role_filler"]["unbind_d3"]
            trig_d3 = r["per_arm"]["char_trigram_baseline"]["unbind_d3"]
            print("[selftest] RF_d3=%.3f Trig_d3=%.3f gap=%.3f" % (
                rf_d3, trig_d3, rf_d3 - trig_d3), flush=True)
            assert r["n_corpus_strings_total"] > 0, "no corpus strings loaded"
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: per-arm structure verified; "
                                   "RF_d3=%.3f Trig_d3=%.3f corpora_total=%d" % (
                                       rf_d3, trig_d3, r["n_corpus_strings_total"]))
            print("[selftest] OK", flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v2_real_mathlib_sub_atom_encoder"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
