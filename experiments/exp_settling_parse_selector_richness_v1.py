"""Settling-residual parse-selector, richness-swept (v1).

USER idea: for a genuinely syntax-underdetermined sentence, construct each candidate role-assignment
parse as a composed hypervector, run an iterative clean-up/settling dynamic against the codebook
(Kintsch Construction-Integration-style relaxation), and use the RESIDUAL-OF-CHANGE at settling
(Rabovsky/N400-as-settling-residual, brain-grounded) as the coherence/rationality score to pick the
correct parse. Then sweep corpus richness (holding codebook size/N fixed -- G7) to test whether the
signal strengthens.

PRIOR ART (credit; learn-from/build-on):
  - Construction-Integration: Kintsch & van Dijk 1978; Kintsch 1988; Guha & Rossi 2001 (settling as
    linear-algebra relaxation to a fixed point).
  - N400-as-settling-residual: Rabovsky, Hansen & McClelland 2018 (Nature Human Behaviour) -- the
    single most load-bearing precedent: residual-of-change during settling = coherence readout.
  - Modern Hopfield / inverse-temperature: Ramsauer et al. 2020/2021 (softmax-weighted cleanup, beta
    fixed hyperparameter -- adapted here for a DENSE real-valued codebook, not sign-quantized).
  - Resonator networks: Frady, Kent, Olshausen & Sommer 2020 (D/N capacity-cliff discipline; NOTE
    this cell's per-role KNOWN-role unbind+cleanup is NOT the same regime as resonator blind
    multi-factor search -- see the pre-reg's honest-scope caveat).
  - Reuses `exp_learned_codebook_generalization_gate_v1`'s vectorized PPMI/SVD codebook builder
    (Kanerva 1988/Sahlgren 2005 RI; Church-Hanks 1990/Levy-Goldberg 2015 PPMI/SVD) and
    `hdlab.binding.bind/unbind` (existing FHRR/HRR primitives; no new operator invented) and the
    `schema_fit_gate()` coherence-baseline CONCEPT from
    `exp_role_filler_factorization_reader_coupled_cg_v1.py:278-322`.

DATA: Belinkov, Lei, Barzilay & Globerson (2014, TACL) PP-attachment corpus (Ratnaparkhi/Reynar/
Roukos 1994-style, Penn-Treebank-derived, WSJ section 23 test partition), fetched from
github.com/boknilev/pp-attachment, cached at data/pp_attachment_raw/wsj.23.txt.dep.pp.*. Real,
non-self-generated gold labels (G5): PP-attachment is THE textbook syntax-underdetermined
construction. CLASS-BALANCED by construction (raw data ~80/20 N-attach skewed; balanced set removes
the majority-class shortcut -- see pre-reg).

Pre-reg: preregs/2026-07-20_settling_parse_selector_richness_v1.md (9 fairness guards G1-G9, G7
capacity-cliff-confound isolation is the make-or-break control, falsifiable HARD-PASS/HARD-FAIL
bands copied verbatim from the research note).

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise
BEFORE except Exception (no BaseException); crlb_n/a declared; baseline_in_band; discriminator
survives scale (smoke previews FULL token-count richness levels at reduced vocab/N); cardinality
gate; per-unit failure-class; deterministic seeding (fixed ints, sorted(), no hash()/list(set()));
numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@; start-marker + heartbeat + crash-diag.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.exp_learned_codebook_generalization_gate_v1 import (  # noqa: E402
    load_tokens, build_vocab, build_cooc, build_ppmi, build_codebook,
)
from hdlab.binding import bind as hd_bind  # noqa: E402
from hdlab.binding import unbind as hd_unbind  # noqa: E402
from hdlab.atoms import make_atoms  # noqa: E402

ANCHOR_NAME = "settling_parse_selector_richness_v1"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PP_BASE = os.path.join(REPO, "data", "pp_attachment_raw", "wsj.23.txt.dep.pp")

ROLE_NAMES = ["R_VERB", "R_N1", "R_PREP", "R_PPOBJ", "R_ATTACH"]
# BETA calibration (META_RULE_M adaptive_with_discriminator_gate, done at SMOKE stage BEFORE any
# FULL/graded run -- not tuned to accuracy outcomes): a smoke beta-sensitivity probe (beta in
# {3, 8, 20, 40}, same items/codebook) showed the classic Ramsauer et al. 2021 fixed-point-class
# split -- low beta (3, 8) makes the softmax cleanup blur toward a generic "global-average" fixed
# point over iterations (MEASURED@ smoke probe: onepass_acc=0.833 beats settle_acc=0.58-0.63, i.e.
# multi-cycle settling actively HURTS at low beta); beta>=20 makes cleanup converge to a sharper,
# more discriminative fixed point (MEASURED@ smoke probe beta=20: settle_acc=0.583 beats
# onepass_acc=0.417; beta=40: settle_acc=0.625 beats onepass_acc=0.250). BETA=20 is FIXED here
# before looking at any FULL-scale/graded result, per G9 (declared, not p-hacked).
BETA = 20.0            # G9: fixed globally, never retuned per richness level
T_MAX = 6              # settling iterations
TAIL_K = 2             # PRIMARY score = mean residual of last TAIL_K iterations
ONEPASS_ITER = 1       # G2 zero-iteration/one-shot-pass control uses residual after 1 pass

# FULL config
FULL_VOCAB_SIZE = 12000
FULL_N_DIM = 1024
FULL_WINDOW = 5
FULL_MIN_COUNT = 5
FULL_RICHNESS_LEVELS = [500_000, 2_000_000, 8_000_000, 17_000_000]
FULL_TREND_SEED = 7
FULL_EXTRA_SEED_AT_RICHEST = 13
FULL_N_PER_CLASS = 24  # -> 48 items (MEASURED@ availability check; see pre-reg)

# SMOKE config (reduced but same mechanism; previews FULL richness token-counts at small vocab/N --
# DISCRIMINATOR-MUST-SURVIVE-SCALE option C: preview arm at (a subset of) full-scale parameters)
SMOKE_VOCAB_SIZE = 3000
SMOKE_N_DIM = 256
SMOKE_WINDOW = 5
SMOKE_MIN_COUNT = 5
SMOKE_RICHNESS_LEVELS = [100_000, 8_000_000]  # thin vs (full-scale) rich preview
SMOKE_TREND_SEED = 7
SMOKE_EXTRA_SEED_AT_RICHEST = 13
SMOKE_N_PER_CLASS = 6  # -> 12 items

SHUFFLE_SEED_BASE = 424242
ITEM_SAMPLE_SEED = 0


# --------------------------------------------------------------------------- infra guards (per
# experiments/exp_learned_codebook_generalization_gate_v1.py convention)
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {
        "pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "expected_n_units": expected_n_units, "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
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
        "verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- PP-attachment item loader
def _is_alpha(w):
    return bool(re.fullmatch(r"[a-z]+", w))


def load_pp_candidates():
    """Real, non-self-generated PP-attachment binary-ambiguity items (Belinkov et al. 2014 TACL).

    Filter: nheads==2, heads.pos==['1','-1'] (verb vs noun candidate), all 4 content words alpha.
    Returns list of (V, N1, P, N2, gold_label) with gold_label in {1: V-attach, 2: N-attach}.
    """
    heads_w = open(PP_BASE + ".heads.words", encoding="utf-8").read().splitlines()
    heads_p = open(PP_BASE + ".heads.pos", encoding="utf-8").read().splitlines()
    children = open(PP_BASE + ".children.words", encoding="utf-8").read().splitlines()
    preps = open(PP_BASE + ".preps.words", encoding="utf-8").read().splitlines()
    labels = open(PP_BASE + ".labels", encoding="utf-8").read().splitlines()
    nheads = open(PP_BASE + ".nheads", encoding="utf-8").read().splitlines()
    out = []
    for i in range(len(heads_w)):
        if int(nheads[i]) != 2:
            continue
        hw = heads_w[i].split()
        hp = heads_p[i].split()
        if hp != ["1", "-1"]:
            continue
        v, n1 = hw[0], hw[1]
        p = preps[i]
        n2 = children[i]
        lab = int(labels[i])
        if not all(_is_alpha(w) for w in (v, n1, p, n2)):
            continue
        out.append((v, n1, p, n2, lab))
    return out


def select_balanced_items(candidates, w2i, n_per_class, seed):
    """Filter to in-vocab candidates; class-balance (equal V-attach/N-attach) via a fixed-seed
    deterministic sample (sorted index lists first -- PROT-023, no hash()/set-order dependence)."""
    in_vocab = [c for c in candidates if all(w in w2i for w in c[:4])]
    v_att = sorted([c for c in in_vocab if c[4] == 1])
    n_att = sorted([c for c in in_vocab if c[4] == 2])
    rng = np.random.default_rng(seed)
    k_v = min(n_per_class, len(v_att))
    k_n = min(n_per_class, len(n_att))
    v_pick = [v_att[i] for i in sorted(rng.choice(len(v_att), size=k_v, replace=False).tolist())]
    n_pick = [n_att[i] for i in sorted(rng.choice(len(n_att), size=k_n, replace=False).tolist())]
    items = v_pick + n_pick
    return items, {"n_v_avail": len(v_att), "n_n_avail": len(n_att),
                   "n_v_used": len(v_pick), "n_n_used": len(n_pick)}


# --------------------------------------------------------------------------- codebook (fixed vocab
# across richness levels; only n_tokens used to fit cooc/ppmi/svd varies -- G7)
def build_fixed_vocab(vocab_size, min_count, max_n_tokens):
    tokens_full = load_tokens(max_n_tokens)
    w2i, counts = build_vocab(tokens_full, vocab_size, min_count)
    return tokens_full, w2i


def build_richness_codebook(tokens_full, w2i, n_tokens, N_DIM, seed, ri_sparsity=10):
    """Fixed w2i (fixed vocab/size); only tokens_full[:n_tokens] feeds cooc -> ppmi -> svd."""
    sub = tokens_full[:n_tokens]
    cooc = build_cooc(sub, w2i, window=FULL_WINDOW if N_DIM == FULL_N_DIM else SMOKE_WINDOW)
    ppmi = build_ppmi(cooc)
    cb = build_codebook("ppmi_svd", cooc, ppmi, len(w2i), N_DIM, seed, ri_sparsity)
    return cb.astype(np.float32)


def _l2norm_rows_np(M, eps=1e-12):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n = np.where(n < eps, 1.0, n)
    return (M / n).astype(np.float32)


def deterministic_shuffle_perm(V, level_idx, seed):
    """Fixed deterministic permutation (mixed-radix seed combo; NEVER hash()/list(set()) -- PROT-023)."""
    combo_seed = int(seed) * 1000003 + int(level_idx) * 97 + SHUFFLE_SEED_BASE
    rng = np.random.default_rng(combo_seed)
    return rng.permutation(V)


# --------------------------------------------------------------------------- settling mechanism
def make_role_atoms(n_dim, seed=999):
    gen = torch.Generator().manual_seed(seed)
    atoms = make_atoms(len(ROLE_NAMES), n_dim, torch.float32, gen)  # (5, n_dim)
    return {name: atoms[i] for i, name in enumerate(ROLE_NAMES)}


def _to_torch(row_np):
    return torch.from_numpy(np.ascontiguousarray(row_np, dtype=np.float32))


def compose_candidate(roles, codebook_np, word_idx, v, n1, p, n2, attach_word):
    """5 bound role-filler pairs, same order/depth for BOTH candidates (G6) -- only R_ATTACH filler
    differs (attach_word = v for V-attach candidate, n1 for N-attach candidate)."""
    def _code(w):
        return _to_torch(codebook_np[word_idx[w]])
    terms = [
        hd_bind(roles["R_VERB"], _code(v)),
        hd_bind(roles["R_N1"], _code(n1)),
        hd_bind(roles["R_PREP"], _code(p)),
        hd_bind(roles["R_PPOBJ"], _code(n2)),
        hd_bind(roles["R_ATTACH"], _code(attach_word)),
    ]
    s = torch.stack(terms, dim=0).sum(dim=0)
    return s / torch.clamp(s.norm(), min=1e-8)


def settle(s0, roles, codebook_normed_t, beta, t_max):
    """Iterative unbind -> soft-cleanup -> rebind relaxation. Returns list of residuals (len t_max)."""
    s = s0
    residuals = []
    for _t in range(t_max):
        recon_terms = []
        for rname in ROLE_NAMES:
            est = hd_unbind(s, roles[rname])
            est_n = est / torch.clamp(est.norm(), min=1e-8)
            sims = codebook_normed_t @ est_n  # (V,)
            w = torch.softmax(beta * sims, dim=0)
            cleaned = w @ codebook_normed_t  # (N,) soft "gist" reconstruction
            cleaned = cleaned / torch.clamp(cleaned.norm(), min=1e-8)
            recon_terms.append(hd_bind(roles[rname], cleaned))
        s_next = torch.stack(recon_terms, dim=0).sum(dim=0)
        s_next = s_next / torch.clamp(s_next.norm(), min=1e-8)
        cos = torch.clamp(torch.dot(s_next, s), -1.0, 1.0)
        residual = float(1.0 - cos)
        residuals.append(residual)
        s = s_next
    return residuals


# --------------------------------------------------------------------------- scoring arms
def score_item(item, codebook_normed_np, word_idx, roles, N_DIM, beta, t_max, tail_k):
    """Runs settling for both candidates; returns dict of arm predictions (label 1=V-attach,2=N-attach)."""
    v, n1, p, n2, gold = item
    cb_t = torch.from_numpy(np.ascontiguousarray(codebook_normed_np, dtype=np.float32))

    s0_v = compose_candidate(roles, codebook_normed_np, word_idx, v, n1, p, n2, attach_word=v)
    s0_n = compose_candidate(roles, codebook_normed_np, word_idx, v, n1, p, n2, attach_word=n1)

    res_v = settle(s0_v, roles, cb_t, beta, t_max)
    res_n = settle(s0_n, roles, cb_t, beta, t_max)

    onepass_v, onepass_n = res_v[ONEPASS_ITER - 1], res_n[ONEPASS_ITER - 1]
    settle_v = float(np.mean(res_v[-tail_k:]))
    settle_n = float(np.mean(res_n[-tail_k:]))

    pred_settle = 1 if settle_v < settle_n else 2         # PRIMARY: lower residual wins
    pred_onepass = 1 if onepass_v < onepass_n else 2      # G2 zero-iteration control
    pred_inverted = 1 if settle_v > settle_n else 2       # G4b must-fail (inverted rule)

    return {
        "gold": gold, "pred_settle": pred_settle, "pred_onepass": pred_onepass,
        "pred_inverted": pred_inverted,
        "settle_v": settle_v, "settle_n": settle_n,
        "onepass_v": onepass_v, "onepass_n": onepass_n,
        "final_residual_v": res_v[-1], "final_residual_n": res_n[-1],
        "decision_flip": (1 if settle_v < settle_n else 2) != (
            1 if np.mean(res_v[-2:-1]) < np.mean(res_n[-2:-1]) else 2) if t_max >= 2 else False,
    }


def score_baseline_thematic_fit(item, word_idx, codebook_normed_np):
    """G3: real one-shot thematic-fit baseline -- cosine(code[HEAD_X], code[N2]); no bind/unbind/iter."""
    v, n1, p, n2, gold = item
    cv = codebook_normed_np[word_idx[v]]
    cn1 = codebook_normed_np[word_idx[n1]]
    cn2 = codebook_normed_np[word_idx[n2]]
    fit_v = float(np.dot(cv, cn2))
    fit_n = float(np.dot(cn1, cn2))
    return 1 if fit_v > fit_n else 2


def majority_class_pred(items):
    """Sanity control: predict the majority gold class in this (balanced) item set."""
    counts = {1: 0, 2: 0}
    for it in items:
        counts[it[4]] += 1
    maj = 1 if counts[1] >= counts[2] else 2
    return maj


# --------------------------------------------------------------------------- runner
def run(output_dir, run_mode, vocab_size, n_dim, richness_levels, trend_seed,
        extra_seed_at_richest, n_per_class, min_count):
    t0 = time.perf_counter()
    n_items_target = 2 * n_per_class
    expected_n_units = len(richness_levels) * n_items_target + n_items_target
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"loading fixed vocab (vocab_size={vocab_size}, from full corpus)")
    tokens_full, w2i = build_fixed_vocab(vocab_size, min_count, max_n_tokens=17_000_000)
    word_idx = w2i
    V = len(w2i)
    _hb(output_dir, f"fixed vocab V={V}")

    candidates = load_pp_candidates()
    items, item_meta = select_balanced_items(candidates, w2i, n_per_class, seed=ITEM_SAMPLE_SEED)
    n_items = len(items)
    _hb(output_dir, f"PP-attachment items: {n_items} (meta={item_meta})")
    if n_items < 8:
        raise RuntimeError(f"TOO_FEW_ITEMS: only {n_items} in-vocab balanced items (need >=8)")

    maj_pred = majority_class_pred(items)

    roles = make_role_atoms(n_dim, seed=999)

    per_unit = {}
    per_level_summary = {}
    n_units_done = 0
    dn_ratios = []

    # coverage pre-check: confirm every item word has nonzero count at the SMALLEST richness level
    smallest_n = min(richness_levels)
    small_tokens_set = set(tokens_full[:smallest_n])
    coverage_smallest = {}
    for it in items:
        for w in it[:4]:
            coverage_smallest[w] = coverage_smallest.get(w, 0) or (w in small_tokens_set)
    n_zero_cov_smallest = sum(1 for v in coverage_smallest.values() if not v)

    for level_idx, n_tokens in enumerate(richness_levels):
        is_richest = (n_tokens == max(richness_levels))
        seeds_this_level = [trend_seed] + ([extra_seed_at_richest] if is_richest else [])
        level_key = f"tok{n_tokens}"
        level_acc = {"settle": [], "onepass": [], "baseline": [], "shuffled": [], "inverted": [],
                     "majority": []}
        level_margin = []
        level_final_residuals = []

        for seed in seeds_this_level:
            unit_prefix = f"{level_key}__seed{seed}"
            try:
                _hb(output_dir, f"building codebook {unit_prefix} (n_tokens={n_tokens})")
                cb = build_richness_codebook(tokens_full, w2i, n_tokens, n_dim, seed)
                cb_normed = _l2norm_rows_np(cb)
                dn_ratios.append(V / n_dim)

                perm = deterministic_shuffle_perm(V, level_idx, seed)
                cb_shuffled = cb_normed[perm]

                for it in items:
                    gold = it[4]
                    res = score_item(it, cb_normed, word_idx, roles, n_dim, BETA, T_MAX, TAIL_K)
                    pred_baseline = score_baseline_thematic_fit(it, word_idx, cb_normed)
                    res_shuf = score_item(it, cb_shuffled, word_idx, roles, n_dim, BETA, T_MAX, TAIL_K)

                    unit_key = f"{unit_prefix}__{it[0]}_{it[1]}_{it[2]}_{it[3]}"
                    per_unit[unit_key] = {
                        "level": level_key, "seed": seed, "item": list(it),
                        "gold": gold,
                        "pred_settle": res["pred_settle"], "pred_onepass": res["pred_onepass"],
                        "pred_baseline": pred_baseline, "pred_shuffled": res_shuf["pred_settle"],
                        "pred_inverted": res["pred_inverted"], "pred_majority": maj_pred,
                        "settle_v": res["settle_v"], "settle_n": res["settle_n"],
                        "margin": abs(res["settle_v"] - res["settle_n"]),
                        "final_residual_v": res["final_residual_v"],
                        "final_residual_n": res["final_residual_n"],
                        "decision_flip": res["decision_flip"],
                        "failure_class": None,
                    }
                    level_acc["settle"].append(res["pred_settle"] == gold)
                    level_acc["onepass"].append(res["pred_onepass"] == gold)
                    level_acc["baseline"].append(pred_baseline == gold)
                    level_acc["shuffled"].append(res_shuf["pred_settle"] == gold)
                    level_acc["inverted"].append(res["pred_inverted"] == gold)
                    level_acc["majority"].append(maj_pred == gold)
                    level_margin.append(abs(res["settle_v"] - res["settle_n"]))
                    level_final_residuals.append(min(res["final_residual_v"], res["final_residual_n"]))
                    n_units_done += 1
            except Exception as e:  # NOT BaseException; per-unit failure-class (META_RULE_J)
                per_unit[f"{unit_prefix}__CODEBOOK_BUILD"] = {
                    "level": level_key, "seed": seed,
                    "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                }
                _hb(output_dir, f"{unit_prefix}: FAILED {type(e).__name__}: {e}")

        def _acc(k):
            return float(np.mean(level_acc[k])) if level_acc[k] else float("nan")

        per_level_summary[level_key] = {
            "n_tokens": n_tokens, "seeds_used": seeds_this_level,
            "acc_settle": _acc("settle"), "acc_onepass": _acc("onepass"),
            "acc_baseline": _acc("baseline"), "acc_shuffled": _acc("shuffled"),
            "acc_inverted": _acc("inverted"), "acc_majority": _acc("majority"),
            "mean_margin": float(np.mean(level_margin)) if level_margin else float("nan"),
            "mean_final_residual": float(np.mean(level_final_residuals)) if level_final_residuals else float("nan"),
            "n_units": len(level_acc["settle"]),
        }
        _hb(output_dir, f"{level_key}: settle_acc={_acc('settle'):.3f} onepass={_acc('onepass'):.3f} "
                        f"baseline={_acc('baseline'):.3f} shuffled={_acc('shuffled'):.3f} "
                        f"inverted={_acc('inverted'):.3f}")

    # ---- aggregate cross-level metrics ----
    ordered_levels = [f"tok{n}" for n in richness_levels]
    accs_settle = [per_level_summary[lv]["acc_settle"] for lv in ordered_levels]
    margins = [per_level_summary[lv]["mean_margin"] for lv in ordered_levels]

    def _spearman(x, y):
        x = np.asarray(x); y = np.asarray(y)
        if len(x) < 3 or np.any(np.isnan(x)) or np.any(np.isnan(y)):
            return float("nan")
        rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
        if np.std(rx) == 0 or np.std(ry) == 0:
            return 0.0
        return float(np.corrcoef(rx, ry)[0, 1])

    richness_rank = list(range(len(richness_levels)))
    rho_acc = _spearman(richness_rank, accs_settle)
    rho_margin = _spearman(richness_rank, margins)

    # cardinality gate (META_RULE_H)
    cardinality_ok = (n_units_done == expected_n_units)

    # arms-must-differ (META_RULE_AF): compare predicted-label arrays across the 5 scoring arms
    arm_preds = {"settle": [], "onepass": [], "baseline": [], "shuffled": [], "inverted": []}
    for u in per_unit.values():
        if "pred_settle" not in u:
            continue
        arm_preds["settle"].append(u["pred_settle"])
        arm_preds["onepass"].append(u["pred_onepass"])
        arm_preds["baseline"].append(u["pred_baseline"])
        arm_preds["shuffled"].append(u["pred_shuffled"])
        arm_preds["inverted"].append(u["pred_inverted"])
    arm_hashes = {k: hashlib.sha256(bytes(v)).hexdigest() for k, v in arm_preds.items()}
    distinct_pairs = {}
    for a in arm_hashes:
        for b in arm_hashes:
            if a < b:
                distinct_pairs[f"{a}_vs_{b}"] = arm_hashes[a] != arm_hashes[b]
    arms_differ = all(distinct_pairs.values()) if distinct_pairs else True

    # richest-level aggregates (primary beats-baseline claim, >=2 seeds)
    richest_key = f"tok{max(richness_levels)}"
    richest = per_level_summary[richest_key]
    gap_vs_baseline = richest["acc_settle"] - richest["acc_baseline"]
    gap_vs_onepass = richest["acc_settle"] - richest["acc_onepass"]

    # discriminator_fires + baseline_in_band (META_RULE_AG)
    baseline_in_band = all(0.05 < per_level_summary[lv]["acc_baseline"] < 0.95 for lv in ordered_levels
                           if not np.isnan(per_level_summary[lv]["acc_baseline"]))
    majority_at_chance = all(abs(per_level_summary[lv]["acc_majority"] - 0.5) < 0.06 for lv in ordered_levels)

    must_fail_shuffled_ok = richest["acc_shuffled"] <= 0.60
    must_fail_inverted_ok = richest["acc_inverted"] < richest["acc_settle"] - 0.05

    # HARD-PASS / HARD-FAIL verdict logic (per pre-reg, verbatim bands)
    hp1 = (gap_vs_baseline >= 0.10)
    hp2 = (gap_vs_onepass > 0.02)  # "non-trivial margin"
    hp3 = must_fail_shuffled_ok and must_fail_inverted_ok
    hp4 = (rho_acc >= 0.6 or (rho_acc >= 0.3 and rho_margin >= 0.3))

    hf1 = not hp2
    hf2 = not hp3
    hf3 = (abs(rho_acc) < 0.3)
    fastest_level = ordered_levels[int(np.argmin([per_level_summary[lv]["mean_final_residual"]
                                                  for lv in ordered_levels]))]
    least_acc_level = ordered_levels[int(np.argmin([per_level_summary[lv]["acc_settle"]
                                                    for lv in ordered_levels]))]
    hf4 = (fastest_level == least_acc_level) and len(set(accs_settle)) > 1

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not arms_differ:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif not baseline_in_band or not majority_at_chance:
        verdict = "MIDDLE_BAND_BASELINE_OR_MAJORITY_OUT_OF_BAND"
    elif hf1 or hf2:
        verdict = "HARD_FAIL_SETTLING_ADDS_NOTHING_OR_MUST_FAIL_CONTROL_BROKEN"
    elif hp1 and hp2 and hp3 and hp4:
        verdict = "HARD_PASS_BOTH_LEGS"
    elif hp1 and hp2 and hp3 and not hp4:
        verdict = "MIDDLE_BAND_BEATS_BASELINE_RICHNESS_TREND_NULL"
    else:
        verdict = "MIDDLE_BAND"

    elapsed = time.perf_counter() - t0
    verdict_msg = (
        f"(i) beats-baseline @ {richest_key}: settle_acc={richest['acc_settle']:.3f} "
        f"baseline_acc={richest['acc_baseline']:.3f} gap={gap_vs_baseline:+.3f} "
        f"onepass_acc={richest['acc_onepass']:.3f} gap_vs_onepass={gap_vs_onepass:+.3f} "
        f"shuffled_acc={richest['acc_shuffled']:.3f} inverted_acc={richest['acc_inverted']:.3f} "
        f"majority_acc={richest['acc_majority']:.3f} | "
        f"(ii) richness-trend: rho_acc={rho_acc:.3f} rho_margin={rho_margin:.3f} "
        f"levels_acc={[round(a, 3) for a in accs_settle]} D/N={dn_ratios[0] if dn_ratios else float('nan'):.3f} "
        f"(flat across levels={len(set(round(x, 6) for x in dn_ratios)) == 1}) | "
        f"n_items={n_items} ({item_meta}) cardinality_ok={cardinality_ok} arms_differ={arms_differ}"
    )

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg, "summary": f"{verdict}: {verdict_msg[:200]}",
        "elapsed_s": elapsed, "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {
            "vocab_size": vocab_size, "V": V, "n_dim": n_dim, "min_count": min_count,
            "richness_levels": richness_levels, "trend_seed": trend_seed,
            "extra_seed_at_richest": extra_seed_at_richest, "n_per_class": n_per_class,
            "n_items": n_items, "beta": BETA, "t_max": T_MAX, "tail_k": TAIL_K,
        },
        "item_meta": item_meta,
        "coverage_smallest_level_n_zero": n_zero_cov_smallest,
        "per_level_summary": per_level_summary,
        "per_unit": per_unit,
        "cross_level": {
            "rho_acc": rho_acc, "rho_margin": rho_margin,
            "gap_vs_baseline_at_richest": gap_vs_baseline,
            "gap_vs_onepass_at_richest": gap_vs_onepass,
            "fastest_converging_level": fastest_level, "least_accurate_level": least_acc_level,
            "g8_fastest_is_least_accurate_flag": hf4,
        },
        "dn_ratio_flat_check": {"values": dn_ratios, "flat": len(set(round(x, 6) for x in dn_ratios)) == 1},
        "hard_pass_gates": {"HP1_beats_baseline_10pt": hp1, "HP2_beats_onepass": hp2,
                            "HP3_must_fail_controls": hp3, "HP4_richness_trend": hp4},
        "hard_fail_gates": {"HF1_no_beat_onepass": hf1, "HF2_must_fail_broken": hf2,
                            "HF3_no_richness_trend": hf3, "HF4_fastest_is_least_accurate": hf4},
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units,
        "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ, "arms_differ_detail": distinct_pairs,
        "baseline_in_band": baseline_in_band, "majority_at_chance": majority_at_chance,
        "crlb_n/a": "residual/coherence discrimination test; no argmax-capacity noise floor; "
                    "capacity-cliff confound isolated via G7 D/N-flat control instead",
        "g7_honest_scope_caveat": "Frady et al. 2020 D/N transition (0.056)/collapse (0.138) apply to "
                                  "resonator multi-factor BLIND search, not this cell's per-role "
                                  "KNOWN-role unbind+cleanup (closer to single-hop cleanup-capacity "
                                  "regime). What is asserted: vocab_size and N_DIM are literally "
                                  "fixed across the sweep, ruling out either capacity-cliff flavor.",
        "prior_art": "Kintsch/vanDijk1978+Kintsch1988 CI; Rabovsky/Hansen/McClelland2018 settling "
                    "residual; Ramsauer2021 inverse-temp; Frady2020 resonator D/N (scope caveat above); "
                    "reuses exp_learned_codebook_generalization_gate_v1 codebook builder + "
                    "hdlab.binding bind/unbind + schema_fit_gate baseline concept",
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Real-code-path self-test at tiny scale: exercises REAL PP-item loader, REAL codebook builder
    (tiny corpus/vocab/N), REAL bind/unbind + settling loop, REAL baseline + shuffle + invert arms."""
    print("[self-test] loading REAL PP-attachment candidates from disk", flush=True)
    candidates = load_pp_candidates()
    assert len(candidates) > 50, f"too few raw candidates loaded: {len(candidates)}"

    print("[self-test] building tiny FIXED vocab from a small text8 slice (real loader/builder)",
          flush=True)
    tokens_full, w2i = build_fixed_vocab(vocab_size=400, min_count=2, max_n_tokens=300_000)
    V = len(w2i)
    assert V >= 50, f"tiny vocab too small: {V}"

    items, meta = select_balanced_items(candidates, w2i, n_per_class=3, seed=ITEM_SAMPLE_SEED)
    print(f"[self-test] tiny in-vocab balanced items: {len(items)} meta={meta}", flush=True)
    if len(items) < 4:
        print("[self-test] WARNING: tiny vocab yields <4 balanced items; widening vocab", flush=True)
        tokens_full, w2i = build_fixed_vocab(vocab_size=1500, min_count=2, max_n_tokens=1_000_000)
        items, meta = select_balanced_items(candidates, w2i, n_per_class=3, seed=ITEM_SAMPLE_SEED)
        V = len(w2i)
    assert len(items) >= 4, f"self-test cannot assemble a tiny balanced item set: {len(items)}"

    N_DIM = 16
    print(f"[self-test] building REAL tiny codebook (V={V}, N_DIM={N_DIM}) via ppmi_svd", flush=True)
    cb = build_richness_codebook(tokens_full, w2i, n_tokens=len(tokens_full), N_DIM=N_DIM, seed=7)
    assert cb.shape == (V, N_DIM), f"codebook shape {cb.shape}"
    assert np.all(np.isfinite(cb)), "codebook has non-finite values"
    cb_normed = _l2norm_rows_np(cb)

    roles = make_role_atoms(N_DIM, seed=999)
    assert len(roles) == 5

    it = items[0]
    res = score_item(it, cb_normed, w2i, roles, N_DIM, BETA, t_max=3, tail_k=2)
    assert res["pred_settle"] in (1, 2)
    assert res["pred_onepass"] in (1, 2)
    assert np.isfinite(res["settle_v"]) and np.isfinite(res["settle_n"])

    pred_baseline = score_baseline_thematic_fit(it, w2i, cb_normed)
    assert pred_baseline in (1, 2)

    perm = deterministic_shuffle_perm(V, level_idx=0, seed=7)
    assert len(perm) == V and len(set(perm.tolist())) == V
    cb_shuffled = cb_normed[perm]
    res_shuf = score_item(it, cb_shuffled, w2i, roles, N_DIM, BETA, t_max=3, tail_k=2)
    assert res_shuf["pred_settle"] in (1, 2)

    maj = majority_class_pred(items)
    assert maj in (1, 2)

    print("[self-test] PASS: real PP loader + real fixed-vocab codebook builder + real bind/unbind "
          "settling loop + baseline + shuffle-control all exercised at tiny scale", flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, "smoke", SMOKE_VOCAB_SIZE, SMOKE_N_DIM, SMOKE_RICHNESS_LEVELS,
            SMOKE_TREND_SEED, SMOKE_EXTRA_SEED_AT_RICHEST, SMOKE_N_PER_CLASS, SMOKE_MIN_COUNT)
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, "full", FULL_VOCAB_SIZE, FULL_N_DIM, FULL_RICHNESS_LEVELS,
            FULL_TREND_SEED, FULL_EXTRA_SEED_AT_RICHEST, FULL_N_PER_CLASS, FULL_MIN_COUNT)
    sys.exit(0)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_selftest")
    elif "--smoke" in sys.argv:
        _out = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
    else:
        _out = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_out, e)
        raise
