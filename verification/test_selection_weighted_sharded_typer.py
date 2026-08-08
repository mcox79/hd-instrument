# WIRE-DON'T-ISLAND PROMOTION WITNESS (2026-08-07). Scaffold-free w.r.t. the PROMOTED organ
# (hdlab.selection_weighted_sharded_typer.SelectionWeightedShardedTyper; tracing=False -- the
# organ takes no tracing flag; hdlab.binding/bundling emit tracing events only if the tracing
# module is armed, which it is not by default / under pytest).
"""verification/test_selection_weighted_sharded_typer.py -- reproduces the overnight-drill
winner (commit d47643d87, exp_pragmatic_curriculum_dialogue_role_sharded_shard_attention_v1.py)
BIT-FOR-BIT off the PROMOTED production organ (hdlab.selection_weighted_sharded_typer.
SelectionWeightedShardedTyper), not off the experiment cell's own inline arm functions. Data/
split/vocab/atoms are IMPORTED from the certified experiment cells (never re-authored) so this
witness cannot silently drift from the landed record:
  - experiments/exp_pragmatic_curriculum_dialogue_role_sharded_scaling_v1.py (SCALE: the 72-item
    scaling data loader, fixed TEST split, per-(n_train,seed) train subsample formula)
  - experiments/exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1.py (RS: the dialogue
    request/response ROLE MAP -- role_of_term / ROLES -- and the live attention_flat/role_sharded
    baselines re-measured via SCALE.run_one_point)
  - experiments/exp_pragmatic_curriculum_vsa_superposition_map_v1.py (VSA_BASE: N_DIM/VOCAB_SEED/
    OUTCOME_SEED/vocab-term list -- fed into the organ's fit() so its atoms are bit-identical to
    the landed run's)
  - experiments/exp_pragmatic_curriculum_dialogue_request_response_first_test_v1.py (MDL_BASE:
    feat_fn, build_episodes, scramble_train_labels)
  - experiments/exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1.py (DD:
    SCRAMBLE_SEED/SCRAMBLE_BAND)

Named test_*.py rather than verify_*.py (the sibling promotion-witness naming convention used
elsewhere in this directory, e.g. verify_goal_typing.py) so pytest (python_files = ["test_*.py"],
pyproject.toml) actually COLLECTS this witness into `python verification/run_certification.py`
-- a witness pytest never runs is not a gate. Follows verification/test_goal_owner_select.py's
promotion-witness convention verbatim (check_* functions doing the real work, thin test_*
wrappers for pytest collection, a run()-equivalent __main__ block).

Checks:
  (1) predict() (the DEFAULT/VALIDATED shard-LOO-weighted route) reproduces `role_shard_weighted`
      EXACTLY: mean_acc=0.8333333333333334 over the SAME 5 seeds at n_train=40 (std=0.000 in the
      landed run -- every seed individually hits 20/24 -- so exact-equality is the right bar, not
      a tolerance band), AND beats the LIVE-remeasured attention_flat baseline (SCALE.
      run_one_point, called not re-derived).
  (2) predict_select() (hard one-hot shard routing) reproduces `role_shard_select` EXACTLY:
      mean_acc=0.8333333333333334 (ties predict() on this construction, per the landed record).
  (3) SCRAMBLE control for both routes: re-fit from scratch (cue weights, shard weights, sup_maps
      ALL re-derived, not just the final map -- matching the source cells' own rigor) on
      MDL_BASE.scramble_train_labels-permuted TRAIN; must reproduce the landed collapse EXACTLY
      (predict()=0.40, predict_select()=0.4416666666666667) and both must sit <= DD.SCRAMBLE_BAND
      (0.60).
  (4) determinism: re-running the whole 5-seed sweep is byte-identical.
  (5) the module's own internal self-tests (data-independent formula + synthetic-task checks)
      are green.

Run: .venv/Scripts/python.exe verification/test_selection_weighted_sharded_typer.py
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENTS_DIR = os.path.join(REPO_ROOT, "experiments")
for _p in (REPO_ROOT, EXPERIMENTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import torch  # noqa: E402

from hdlab.selection_weighted_sharded_typer import (  # noqa: E402
    SelectionWeightedShardedTyper,
    _run_all_selftests,
)

# ---- REUSED (imported, not re-authored): the certified experiment cells' own data/split/atoms
import experiments.exp_pragmatic_curriculum_dialogue_request_response_first_test_v1 as MDL_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_vsa_superposition_map_v1 as VSA_BASE  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_request_response_dailydialog_v1 as DD  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_binding_v1 as RS  # noqa: E402
import experiments.exp_pragmatic_curriculum_dialogue_role_sharded_scaling_v1 as SCALE  # noqa: E402

N_TRAIN = 40           # the decisive scale the landed run measured
N_SEEDS = SCALE.N_SEEDS  # 5

EXPECTED_ACC_SHARD_WEIGHTED = 0.8333333333333334
EXPECTED_ACC_SHARD_SELECT = 0.8333333333333334
EXPECTED_ACC_SCRAMBLE_SHARD_WEIGHTED = 0.4
EXPECTED_ACC_SCRAMBLE_SHARD_SELECT = 0.4416666666666667

_CACHE = {}


def _fit_one(train_items, vocab_terms, gold_labels_override=None):
    """Fits the PROMOTED organ on one (train_items, [scrambled]-labels) draw, atoms seeded
    bit-identically to VSA_BASE.build_vocab/build_outcome_vecs (VOCAB_SEED/OUTCOME_SEED)."""
    train_terms = [MDL_BASE.feat_fn(it) for it in train_items]
    labels = gold_labels_override if gold_labels_override is not None else [
        it["gold_class"] for it in train_items]
    typer = SelectionWeightedShardedTyper(n_dim=VSA_BASE.N_DIM, seed=0)
    typer.fit(
        train_terms, labels, RS.role_of_term, roles=RS.ROLES,
        vocab_terms=vocab_terms,
        vocab_generator=torch.Generator().manual_seed(VSA_BASE.VOCAB_SEED),
        outcome_generator=torch.Generator().manual_seed(VSA_BASE.OUTCOME_SEED),
    )
    return typer


def _acc(preds, gold):
    return sum(1 for p, g in zip(preds, gold) if p == g) / len(gold)


def run_sweep():
    """Runs the full 5-seed n_train=40 sweep through the PROMOTED organ (real + scramble, both
    predict() and predict_select() routes) plus the LIVE attention_flat baseline (SCALE.
    run_one_point, reused unmodified). Cached (module-level) so repeated check_* calls in one
    pytest session don't redo the ~5s computation five times over."""
    if _CACHE:
        return _CACHE

    raw_items = SCALE.load_scaling_items()
    items = MDL_BASE.build_episodes(raw_items)
    assert sorted(set(it["gold_class"] for it in items)) == ["MET", "UNMET"]

    pool_items, test_items = SCALE.stratified_test_split(items, seed=SCALE.SPLIT_SEED, test_size=SCALE.TEST_SIZE)
    vocab_vecs, vocab_terms = VSA_BASE.build_vocab(items)
    outcome_vecs = VSA_BASE.build_outcome_vecs()
    RS.assert_full_role_coverage(vocab_terms)
    cue_bundles_flat = VSA_BASE.build_cue_bundles(items, vocab_vecs)
    subb_role_unweighted, _fb = RS.build_role_subbundles(items, vocab_vecs)
    gold = [it["gold_class"] for it in test_items]

    accs, accs_sel, accs_scr, accs_sel_scr, attn_flat_accs = [], [], [], [], []
    for seed_idx in range(N_SEEDS):
        seed = SCALE.SUBSAMPLE_SEED_BASE + N_TRAIN * 1000 + seed_idx
        train_items = SCALE.subsample_train(pool_items, N_TRAIN, seed)

        # ---- LIVE attention_flat baseline (re-measured via SCALE's own harness, not stale) ----
        pt = SCALE.run_one_point(train_items, test_items, ["MET", "UNMET"], vocab_vecs, outcome_vecs,
                                  cue_bundles_flat, subb_role_unweighted)
        attn_flat_accs.append(pt["attention_flat"]["acc"])

        typer = _fit_one(train_items, vocab_terms)
        preds = [typer.predict(MDL_BASE.feat_fn(it)) for it in test_items]
        preds_sel = [typer.predict_select(MDL_BASE.feat_fn(it)) for it in test_items]
        accs.append(_acc(preds, gold))
        accs_sel.append(_acc(preds_sel, gold))

        train_scr = MDL_BASE.scramble_train_labels(train_items, seed=DD.SCRAMBLE_SEED)
        scr_labels = [it["gold_class"] for it in train_scr]
        typer_scr = _fit_one(train_items, vocab_terms, gold_labels_override=scr_labels)
        preds_scr = [typer_scr.predict(MDL_BASE.feat_fn(it)) for it in test_items]
        preds_sel_scr = [typer_scr.predict_select(MDL_BASE.feat_fn(it)) for it in test_items]
        accs_scr.append(_acc(preds_scr, gold))
        accs_sel_scr.append(_acc(preds_sel_scr, gold))

    result = {
        "mean_acc_predict": sum(accs) / len(accs),
        "mean_acc_predict_select": sum(accs_sel) / len(accs_sel),
        "mean_acc_predict_scramble": sum(accs_scr) / len(accs_scr),
        "mean_acc_predict_select_scramble": sum(accs_sel_scr) / len(accs_sel_scr),
        "mean_acc_attention_flat_live": sum(attn_flat_accs) / len(attn_flat_accs),
        "n_seeds": N_SEEDS, "n_train": N_TRAIN,
    }
    _CACHE.update(result)
    return result


# ---------------------------------------------------------------------------
# (1) predict() reproduces role_shard_weighted EXACTLY and beats attention_flat
# ---------------------------------------------------------------------------
def check_predict_reproduces_role_shard_weighted():
    r = run_sweep()
    assert abs(r["mean_acc_predict"] - EXPECTED_ACC_SHARD_WEIGHTED) < 1e-9, (
        "predict() mean_acc=%.16f != landed role_shard_weighted=%.16f"
        % (r["mean_acc_predict"], EXPECTED_ACC_SHARD_WEIGHTED))
    assert r["mean_acc_predict"] > r["mean_acc_attention_flat_live"], (
        "predict() (%.4f) must beat the LIVE attention_flat baseline (%.4f)"
        % (r["mean_acc_predict"], r["mean_acc_attention_flat_live"]))
    print("[CHECK predict] mean_acc=%.4f (== landed 0.8333) beats attention_flat=%.4f"
          % (r["mean_acc_predict"], r["mean_acc_attention_flat_live"]))
    return r


# ---------------------------------------------------------------------------
# (2) predict_select() reproduces role_shard_select EXACTLY
# ---------------------------------------------------------------------------
def check_predict_select_reproduces_role_shard_select():
    r = run_sweep()
    assert abs(r["mean_acc_predict_select"] - EXPECTED_ACC_SHARD_SELECT) < 1e-9, (
        "predict_select() mean_acc=%.16f != landed role_shard_select=%.16f"
        % (r["mean_acc_predict_select"], EXPECTED_ACC_SHARD_SELECT))
    print("[CHECK predict_select] mean_acc=%.4f (== landed 0.8333)" % r["mean_acc_predict_select"])
    return r


# ---------------------------------------------------------------------------
# (3) scramble collapses EXACTLY as landed, and both sit under the pre-registered band
# ---------------------------------------------------------------------------
def check_scramble_collapses():
    r = run_sweep()
    assert abs(r["mean_acc_predict_scramble"] - EXPECTED_ACC_SCRAMBLE_SHARD_WEIGHTED) < 1e-9, (
        "predict() scramble mean_acc=%.16f != landed=%.16f"
        % (r["mean_acc_predict_scramble"], EXPECTED_ACC_SCRAMBLE_SHARD_WEIGHTED))
    assert abs(r["mean_acc_predict_select_scramble"] - EXPECTED_ACC_SCRAMBLE_SHARD_SELECT) < 1e-9, (
        "predict_select() scramble mean_acc=%.16f != landed=%.16f"
        % (r["mean_acc_predict_select_scramble"], EXPECTED_ACC_SCRAMBLE_SHARD_SELECT))
    assert r["mean_acc_predict_scramble"] <= DD.SCRAMBLE_BAND + 1e-9
    assert r["mean_acc_predict_select_scramble"] <= DD.SCRAMBLE_BAND + 1e-9
    print("[CHECK scramble] predict_scr=%.4f predict_select_scr=%.4f both <= band=%.2f"
          % (r["mean_acc_predict_scramble"], r["mean_acc_predict_select_scramble"], DD.SCRAMBLE_BAND))
    return r


# ---------------------------------------------------------------------------
# (4) determinism: the whole sweep, re-run from a fresh cache, is byte-identical
# ---------------------------------------------------------------------------
def check_determinism():
    r1 = dict(run_sweep())
    _CACHE.clear()
    r2 = dict(run_sweep())
    for k in ("mean_acc_predict", "mean_acc_predict_select",
              "mean_acc_predict_scramble", "mean_acc_predict_select_scramble"):
        assert r1[k] == r2[k], "determinism FAIL on %s: %r != %r" % (k, r1[k], r2[k])
    print("[CHECK determinism] full 5-seed sweep byte-identical across two independent runs")
    return {"ok": True}


# ---------------------------------------------------------------------------
# pytest collection wrappers
# ---------------------------------------------------------------------------
def test_predict_reproduces_role_shard_weighted():
    check_predict_reproduces_role_shard_weighted()


def test_predict_select_reproduces_role_shard_select():
    check_predict_select_reproduces_role_shard_select()


def test_scramble_collapses():
    check_scramble_collapses()


def test_determinism():
    check_determinism()


def test_module_self_test_green():
    res = _run_all_selftests()
    assert res["cue_weight_formula"] == "OK"
    assert res["shard_weight_formula"] == "OK"
    assert res["synthetic_shard_separation"] == "OK"
    assert res["determinism"] == "OK"
    assert res["validated_mean_acc_role_shard_weighted_n_train_40"] == EXPECTED_ACC_SHARD_WEIGHTED


def run():
    r1 = check_predict_reproduces_role_shard_weighted()
    r2 = check_predict_select_reproduces_role_shard_select()
    r3 = check_scramble_collapses()
    r4 = check_determinism()
    print("[ALL CHECKS PASS] hdlab.selection_weighted_sharded_typer.SelectionWeightedShardedTyper "
          "reproduces role_shard_weighted=0.8333 / role_shard_select=0.8333 (scramble 0.40/0.4417) "
          "bit-for-bit off the PROMOTED organ, beats the live attention_flat baseline, deterministic.")
    return {"predict": r1, "predict_select": r2, "scramble": r3, "determinism": r4}


if __name__ == "__main__":
    run()
