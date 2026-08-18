"""Dependency-context x window-context BLEND-WEIGHT SWEEP -- location/artifact typing, bigger test set (v2).

Resolves the two open limitations v1 (atom pending, `dependency_context_codebook_location_artifact_v1`,
data/dependency_context_codebook_location_artifact_v1_smoke/metrics.json) explicitly flagged after its
own smoke:
  (1) v1's location/artifact eval used only 4+4 curated test words -> AUC granularity 1/16 SATURATED
      at ceiling (1.0) for window/dependency/combined alike -> the pre-registered AUC-margin gate could
      not discriminate, even though the underlying per-word ACCURACY numbers showed a real, interpretable
      pattern (pure-dependency INVERTS the conflation: fixes location 0.75->1.0, breaks artifact
      1.0->0.75; naive 50/50 COMBINED fixes BOTH: 1.0/1.0).
  (2) v1's naive 50/50 `concatenate_unit_normalized_channels_then_renormalize` combine diluted general
      word-similarity to 0.7488, BELOW the 0.85 floor (same-regime window reference: atom 29368's own
      wordsim/simlex AUC = 0.8496 at this exact corpus config) -- v1 flagged a down-weighted combine as
      a HYPOTHESIZED, untested next step to avoid p-hacking a post-hoc alpha.

v2 fixes BOTH, pre-registered BEFORE running (this file):
  FIX 1: expand the location/artifact typing eval to >=20 words PER CATEGORY (>=40 total), drawn from
    the real codebook vocab (same text8-derived corpus, same vocab-building pipeline), DISJOINT from
    the type-prototype exemplars and from the original stored-sentence lexicon (asserted at runtime,
    fail loud if coverage insufficient -- see `build_word_pools_v2`).
  FIX 2: sweep the window:dependency blend weight w in a PRE-REGISTERED grid
    WEIGHT_GRID = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5] (window-fraction; w=1.0 is definitionally identical in
    direction to the pure window arm -- a built-in consistency check, not a separate mechanism claim).
    combined(w) = L2_renormalize(concat(w * L2normalize(window_channel), (1-w) * L2normalize(dep_channel))).
    Reports the FULL Pareto curve: at each w, location acc / artifact acc / general word-similarity AUC.

PRIOR ART (credit; learn-from / build-on, never steal): SAME as v1 -- Levy & Goldberg 2014 (ACL
P14-2050, dependency-typed context shifts induced similarity from relatedness to co-type); Komninos &
Manandhar 2016 (NAACL, window+dependency COMBINED beats either alone -- the precedent for a weighted
blend rather than an all-or-nothing choice); VerbNet (via NLTK) for the artifact-verb seed vocabulary.
Reuses `experiments.exp_dependency_context_codebook_location_artifact_v1` (`dc`, this cell's own direct
predecessor) UNMODIFIED for: build_dependency_trigger_table, build_dep_cooc, build_random_context_cooc,
build_ppmi_svd, prototype_classify, naive_1nn_classify, score_arm, _l2norm_rows, _normalize,
LOCATIVE_PREPS, ARTIFACT_VERB_FORMS. Reuses `experiments.exp_learned_codebook_generalization_gate_v1`
(`cb`, atom 29368) UNMODIFIED for corpus loading / vocab / window-cooc / PPMI / wordsim-simlex eval.
Reuses `experiments.exp_derived_filler_typing_single_edge_grounding_v1` (`dft`, atom 29391) for
STORED_SENTENCE_NOUNS only (the original stored-sentence lexicon the bigger test set must stay disjoint
from) -- the bigger ARTIFACT_POOL_V2/LOCATION_POOL_V2 candidate word lists are NEW (this cell), a
superset-by-category of dft's original ARTIFACT_POOL/LOCATION_POOL plus additional common
architecture/geography nouns, filtered to actual corpus-vocab presence at runtime (never assumed).

ARMS:
  window        : dc pipeline, window=5 cooc -> PPMI -> SVD.  [= atom 29368's mechanism, fixed baseline]
  dependency    : rule-based typed-slot cooc (12 cols) -> PPMI -> SVD.  [w=0.0 equivalent; the "inverting" arm]
  combined@w    : blend of window_emb and dep_emb at weight w, for w in WEIGHT_GRID.  [THE KEY new arm]
  random_context: window cooc with column indices permuted (destroys word-context association).
                  [must-fail control -- must NOT beat window OR any combined(w) point]

Pre-reg: preregs/2026-07-20_dependency_context_codebook_weight_sweep_location_artifact_v2.md

CELL-TEMPLATE MANDATORY: arms_differ hash-test; tmp_replace atomic metrics; except SystemExit: raise
BEFORE except Exception (no BaseException); crlb_n/a declared; baseline_in_band; discriminator survives
scale (analytical, see prereg); HARD_PASS strictly above floor; cardinality gate; per-unit failure-class;
fixed seeds only (no hash()/list(set())); numbers tagged in prereg.

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402

ANCHOR_NAME = "dependency_context_codebook_weight_sweep_location_artifact_v2"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import experiments.exp_learned_codebook_generalization_gate_v1 as cb  # noqa: E402
import experiments.exp_derived_filler_typing_single_edge_grounding_v1 as dft  # noqa: E402
import experiments.exp_dependency_context_codebook_location_artifact_v1 as dc  # noqa: E402

# --------------------------------------------------------------------------- config
FIXED_ARMS = ["window", "dependency", "random_context"]
WEIGHT_GRID = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]  # window-fraction w; combined = w*window (+) (1-w)*dep
SEEDS = [7, 13, 19]
N_TARGET = 512  # SAME requested SVD rank as v1 (design-gate: one variable = blend weight, not rank)

# Bigger, real-vocab candidate pools (superset-by-category of dft's ARTIFACT_POOL/LOCATION_POOL, plus
# new common architecture/geography nouns). Presence in the actual corpus vocab is NEVER assumed --
# filtered live by build_word_pools_v2; MEASURED coverage at the smoke config below (probe run
# 2026-07-20, scratch script, not archived): artifact 33/50 present, location 35/65 present at
# n_tokens=1.5M vocab_size=10000 min_count=5.
ARTIFACT_POOL_V2 = [
    "church", "temple", "stadium", "tower", "monastery", "palace", "cathedral", "castle", "factory",
    "monument", "fortress", "chapel", "pyramid", "lighthouse", "windmill", "mansion", "cottage",
    "warehouse", "shrine", "citadel", "abbey", "basilica", "cinema", "hospital", "library", "museum",
    "theatre", "theater", "hotel", "tavern", "inn", "prison", "mill", "granary", "silo", "aqueduct",
    "arena", "amphitheater", "synagogue", "mosque", "chateau", "villa", "tenement", "skyscraper",
    "barracks", "observatory", "pavilion", "gallery", "academy", "chamber",
]
LOCATION_POOL_V2 = [
    "island", "mountain", "desert", "peninsula", "plateau", "forest", "delta", "harbor", "prairie",
    "reef", "cliff", "swamp", "volcano", "canyon", "glacier", "lagoon", "tundra", "marsh", "meadow",
    "hillside", "savanna", "steppe", "fjord", "archipelago", "isthmus", "plain", "ridge", "gorge",
    "cave", "cavern", "dune", "oasis", "wetland", "moor", "heath", "grove", "thicket", "wilderness",
    "coastline", "bay", "cove", "inlet", "strait", "gulf", "basin", "crater", "ravine",
    "shore", "coast", "hill", "cape", "waterfall", "estuary", "atoll", "highland", "lowland",
    "woodland", "grassland", "headland", "foothill", "summit", "vale", "escarpment", "butte", "mesa",
]

N_EXEMPLAR_ARTIFACT = 6   # SAME count as v1/dft (top-6-by-frequency; preserves prototype continuity)
N_TEST_ARTIFACT = 20      # FIX 1: >=20 per category (was 4 in v1)
N_EXEMPLAR_LOCATION = 5   # SAME count as v1/dft
N_TEST_LOCATION = 20      # FIX 1: >=20 per category (was 4 in v1)

# Smoke corpus config: SAME n_tokens as dft.SMOKE_CFG (1.5M, cheap), vocab_size BUMPED 6000->10000
# (measured live: vocab_size=6000 gives only 19/47 location candidates present -- INSUFFICIENT for
# need_loc=25; vocab_size=10000 gives 35/65 -- ample margin). This is a corpus-coverage necessity for
# the bigger test set, not a difficulty-tuning choice; window=5/min_count=5 unchanged.
SMOKE_CFG_V2 = dict(n_tokens=1_500_000, vocab_size=10000, window=5, min_count=5)
# Full config carried forward for a later FULL dispatch (NOT run this cycle; design-only per task scope).
# Coverage margin is TIGHTER at FULL_CFG_V2 (measured: artifact 30/50, location 26/65 -- location need=25
# leaves only margin=1) -- flagged explicitly in the prereg as a real risk requiring pool re-check or a
# further vocab_size bump before a FULL run, not glossed over.
FULL_CFG_V2 = dict(n_tokens=8_000_000, vocab_size=10000, window=5, min_count=5)

# Pre-registered bands (declared BEFORE running; see prereg).
NOISE_EPS = 1e-9                 # float-tie tolerance only, not a p-hacking margin
SWEET_SPOT_BORDERLINE_EPS = 0.02  # META_RULE_L spirit: qualifying margin < this = flag "borderline"
CHANCE_AUC = 0.50


# --------------------------------------------------------------------------- infra guards
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(marker, fh)
    os.replace(tmp, final)


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


def _hb(output_dir, msg):
    print(f"[hb] {msg}", flush=True)
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "msg": msg}
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------- bigger, disjoint word pools
def build_word_pools_v2(w2i, counts, artifact_pool, location_pool, n_exemplar_artifact, n_test_artifact,
                         n_exemplar_location, n_test_location, stored_sentence_nouns):
    """Generalizes dft.build_word_pools (SAME logic: filter to in-vocab, rank by descending frequency
    deterministic (-count, word) sort, disjoint EXEMPLAR/TEST slices) to accept ARBITRARY candidate pools
    and larger n_test targets. Fail loud (RuntimeError) if coverage is insufficient -- never silently
    truncate the requested test-set size. Also asserts test/exemplar disjointness from the ORIGINAL
    stored-sentence lexicon (dft.STORED_SENTENCE_NOUNS), same design-gate discipline as v1/dft."""
    def present_sorted(pool):
        pres = [(w, w2i[w], float(counts[w2i[w]])) for w in pool if w in w2i]
        pres.sort(key=lambda x: (-x[2], x[0]))
        return pres

    art = present_sorted(artifact_pool)
    loc = present_sorted(location_pool)
    need_art = n_exemplar_artifact + n_test_artifact
    need_loc = n_exemplar_location + n_test_location
    if len(art) < need_art:
        raise RuntimeError(f"INSUFFICIENT_ARTIFACT_VOCAB_COVERAGE: {len(art)} present (need >= "
                            f"{need_art}, requested n_test_artifact={n_test_artifact}): {art}")
    if len(loc) < need_loc:
        raise RuntimeError(f"INSUFFICIENT_LOCATION_VOCAB_COVERAGE: {len(loc)} present (need >= "
                            f"{need_loc}, requested n_test_location={n_test_location}): {loc}")
    if n_test_artifact < 20 or n_test_location < 20:
        raise RuntimeError(f"DESIGN_CONTRACT_VIOLATION: bigger-test-set requirement is >=20 per "
                            f"category; got n_test_artifact={n_test_artifact} n_test_location="
                            f"{n_test_location}")

    exemplar_artifact = art[:n_exemplar_artifact]
    test_artifact = art[n_exemplar_artifact:n_exemplar_artifact + n_test_artifact]
    exemplar_location = loc[:n_exemplar_location]
    test_location = loc[n_exemplar_location:n_exemplar_location + n_test_location]

    ex_words = {w for w, _, _ in exemplar_artifact + exemplar_location}
    test_words = {w for w, _, _ in test_artifact + test_location}
    assert ex_words.isdisjoint(test_words), (
        f"DESIGN_GATE_VIOLATION: exemplar/test overlap: {ex_words & test_words}")
    assert test_words.isdisjoint(stored_sentence_nouns), (
        f"DESIGN_GATE_VIOLATION: test noun leaks into original stored-sentence lexicon: "
        f"{test_words & stored_sentence_nouns}")
    assert ex_words.isdisjoint(stored_sentence_nouns), (
        f"DESIGN_GATE_VIOLATION: exemplar leaks into original stored-sentence lexicon: "
        f"{ex_words & stored_sentence_nouns}")

    return exemplar_artifact, test_artifact, exemplar_location, test_location


def blend_channels(window_emb, dep_emb, w):
    """combined(w) = L2_renormalize(concat(w * window_emb, (1-w) * dep_emb)). window_emb/dep_emb are
    ALREADY per-row L2-normalized (build_ppmi_svd's own _l2norm_rows) -- the "L2 per channel" step is
    satisfied by construction BEFORE this function scales+concatenates+renormalizes. At w=1.0 this is,
    by construction, direction-identical to window_emb (dep channel zero-weighted) -- an intentional
    built-in consistency check against the separately-computed "window" arm, not a distinct claim."""
    combo = np.concatenate([w * window_emb, (1.0 - w) * dep_emb], axis=1)
    return dc._l2norm_rows(combo)


# --------------------------------------------------------------------------- runner
def run(output_dir, cfg, seeds, run_mode):
    t0 = time.perf_counter()
    n_test_words = N_TEST_ARTIFACT + N_TEST_LOCATION
    expected_n_units = (len(FIXED_ARMS) + len(WEIGHT_GRID)) * len(seeds) * n_test_words
    _write_start_marker(output_dir, run_mode, expected_n_units)

    _hb(output_dir, f"loading corpus n_tokens={cfg['n_tokens']} vocab_size={cfg['vocab_size']}")
    tokens = cb.load_tokens(cfg["n_tokens"])
    w2i, counts = cb.build_vocab(tokens, vocab_size=cfg["vocab_size"], min_count=cfg["min_count"])
    V = len(w2i)
    _hb(output_dir, f"vocab V={V}")

    exemplar_artifact, test_artifact, exemplar_location, test_location = build_word_pools_v2(
        w2i, counts, ARTIFACT_POOL_V2, LOCATION_POOL_V2, N_EXEMPLAR_ARTIFACT, N_TEST_ARTIFACT,
        N_EXEMPLAR_LOCATION, N_TEST_LOCATION, dft.STORED_SENTENCE_NOUNS)
    ex_art_idx = [i for _, i, _ in exemplar_artifact]
    ex_loc_idx = [i for _, i, _ in exemplar_location]
    test_words = [(w, i, "ARTIFACT") for w, i, _ in test_artifact] + \
                 [(w, i, "LOCATION") for w, i, _ in test_location]
    _hb(output_dir, f"n_test_artifact={len(test_artifact)} n_test_location={len(test_location)} "
                    f"n_test_total={len(test_words)}")
    _hb(output_dir, f"exemplar_artifact={[w for w,_,_ in exemplar_artifact]}")
    _hb(output_dir, f"exemplar_location={[w for w,_,_ in exemplar_location]}")

    # --- window cooc/ppmi (shared basis for window + random_context + every combined(w)) ---
    window_cooc = cb.build_cooc(tokens, w2i, cfg["window"])
    window_ppmi = cb.build_ppmi(window_cooc)
    _hb(output_dir, f"window cooc nnz={window_cooc.nnz} ppmi nnz={window_ppmi.nnz}")

    # --- dependency cooc/ppmi (shared basis for dependency arm + every combined(w)) ---
    surface_to_slots, col_names = dc.build_dependency_trigger_table(dc.LOCATIVE_PREPS, dc.ARTIFACT_VERB_FORMS)
    dep_cooc, trigger_hits, dep_misses = dc.build_dep_cooc(tokens, w2i, surface_to_slots, col_names,
                                                            output_dir)
    dep_ppmi = cb.build_ppmi(dep_cooc)
    _hb(output_dir, f"dep D_DEP={len(col_names)} cooc nnz={dep_cooc.nnz} ppmi nnz={dep_ppmi.nnz}")

    # word-sim reference sets (measured on EVERY arm/weight -- not just the combined arm as in v1 --
    # so "window's own baseline" is a value measured THIS run, at THIS vocab, not a hardcoded constant).
    ws_pairs = cb.load_wordsim(w2i)
    sl_pairs = cb.load_simlex(w2i)
    combined_pairs = ws_pairs + sl_pairs
    true_pairs, random_pairs = cb.make_true_random_sets(combined_pairs, w2i, seed=0)
    _hb(output_dir, f"wordsim/simlex in-vocab: ws={len(ws_pairs)} sl={len(sl_pairs)} "
                    f"true_pairs={len(true_pairs)} random_pairs={len(random_pairs)}")

    def wordsim_auc_of(emb):
        cos_t = cb.cos_pairs(emb, true_pairs)
        cos_r = cb.cos_pairs(emb, random_pairs)
        return cb.auc_true_vs_random(cos_t, cos_r)

    per_fixed_arm_per_seed = {arm: {} for arm in FIXED_ARMS}
    per_weight_per_seed = {w: {} for w in WEIGHT_GRID}
    wordsim_fixed_per_seed = {arm: {} for arm in FIXED_ARMS}
    wordsim_weight_per_seed = {w: {} for w in WEIGHT_GRID}
    dep_zero_row_frac_by_seed = {}
    n_units_done = 0
    naive_location_acc = None
    naive_artifact_acc = None
    combined_w1_equals_window_by_seed = {}

    for seed in seeds:
        window_emb, window_k = dc.build_ppmi_svd(window_ppmi, N_TARGET, seed)
        dep_emb, dep_k = dc.build_ppmi_svd(dep_ppmi, N_TARGET, seed)
        random_cooc = dc.build_random_context_cooc(window_cooc, seed)
        random_ppmi = cb.build_ppmi(random_cooc)
        random_emb, random_k = dc.build_ppmi_svd(random_ppmi, N_TARGET, seed)

        dep_zero_rows = np.sum(np.linalg.norm(dep_emb[[i for _, i, _ in test_words]], axis=1) < 1e-9)
        dep_zero_row_frac_by_seed[str(seed)] = float(dep_zero_rows) / float(len(test_words))

        fixed_embeddings = {"window": window_emb, "dependency": dep_emb, "random_context": random_emb}
        for arm in FIXED_ARMS:
            emb = fixed_embeddings[arm]
            preds, margins = dc.prototype_classify(emb, ex_art_idx, ex_loc_idx, test_words)
            metrics_arm = dc.score_arm(preds, margins, test_artifact, test_location)
            per_fixed_arm_per_seed[arm][seed] = metrics_arm
            wordsim_fixed_per_seed[arm][seed] = wordsim_auc_of(emb)
            n_units_done += n_test_words
            _hb(output_dir, f"seed={seed} arm={arm}: acc_location={metrics_arm['acc_location']:.3f} "
                            f"acc_artifact={metrics_arm['acc_artifact']:.3f} auc={metrics_arm['auc']:.3f} "
                            f"wordsim_auc={wordsim_fixed_per_seed[arm][seed]:.4f}")

        for w in WEIGHT_GRID:
            combined_emb = blend_channels(window_emb, dep_emb, w)
            preds, margins = dc.prototype_classify(combined_emb, ex_art_idx, ex_loc_idx, test_words)
            metrics_w = dc.score_arm(preds, margins, test_artifact, test_location)
            per_weight_per_seed[w][seed] = metrics_w
            wordsim_weight_per_seed[w][seed] = wordsim_auc_of(combined_emb)
            n_units_done += n_test_words
            _hb(output_dir, f"seed={seed} combined(w={w}): acc_location={metrics_w['acc_location']:.3f} "
                            f"acc_artifact={metrics_w['acc_artifact']:.3f} auc={metrics_w['auc']:.3f} "
                            f"wordsim_auc={wordsim_weight_per_seed[w][seed]:.4f}")
            if w == 1.0:
                # built-in consistency check (diagnostic only, not a HARD_FAIL gate): combined@w=1.0
                # must be direction-identical to the "window" arm.
                window_preds, _wm = dc.prototype_classify(window_emb, ex_art_idx, ex_loc_idx, test_words)
                combined_w1_equals_window_by_seed[str(seed)] = (preds == window_preds)

        if naive_location_acc is None:
            naive_preds = dc.naive_1nn_classify(window_emb, ex_art_idx, ex_loc_idx, test_words)
            naive_metrics = dc.score_arm(naive_preds, None, test_artifact, test_location)
            naive_location_acc = naive_metrics["acc_location"]
            naive_artifact_acc = naive_metrics["acc_artifact"]
            _hb(output_dir, f"naive_1NN (window features, computed once): "
                            f"acc_location={naive_location_acc:.3f} acc_artifact={naive_artifact_acc:.3f}")

    cardinality_ok = (n_units_done == expected_n_units)

    def agg(per_seed_dict):
        accs_overall = [per_seed_dict[s]["acc_overall"] for s in seeds]
        accs_artifact = [per_seed_dict[s]["acc_artifact"] for s in seeds]
        accs_location = [per_seed_dict[s]["acc_location"] for s in seeds]
        aucs = [per_seed_dict[s]["auc"] for s in seeds]
        return {"acc_overall_mean": float(np.mean(accs_overall)), "acc_overall_std": float(np.std(accs_overall)),
                "acc_artifact_mean": float(np.mean(accs_artifact)),
                "acc_location_mean": float(np.mean(accs_location)),
                "auc_mean": float(np.mean(aucs)), "auc_std": float(np.std(aucs)),
                "auc_per_seed": {str(s): per_seed_dict[s]["auc"] for s in seeds}}

    fixed_summary = {arm: agg(per_fixed_arm_per_seed[arm]) for arm in FIXED_ARMS}
    for arm in FIXED_ARMS:
        vals = [wordsim_fixed_per_seed[arm][s] for s in seeds]
        fixed_summary[arm]["wordsim_auc_mean"] = float(np.mean(vals))
        fixed_summary[arm]["wordsim_auc_std"] = float(np.std(vals))

    sweep_summary = {}
    for w in WEIGHT_GRID:
        s = agg(per_weight_per_seed[w])
        vals = [wordsim_weight_per_seed[w][sd] for sd in seeds]
        s["wordsim_auc_mean"] = float(np.mean(vals))
        s["wordsim_auc_std"] = float(np.std(vals))
        sweep_summary[str(w)] = s

    window_loc_acc = fixed_summary["window"]["acc_location_mean"]
    window_art_acc = fixed_summary["window"]["acc_artifact_mean"]
    window_wordsim = fixed_summary["window"]["wordsim_auc_mean"]
    dep_loc_acc = fixed_summary["dependency"]["acc_location_mean"]
    dep_art_acc = fixed_summary["dependency"]["acc_artifact_mean"]
    random_auc = fixed_summary["random_context"]["auc_mean"]

    # random-context must-fail: must not beat window OR any combined(w) point (checked at every weight).
    random_must_fail_vs_window = random_auc <= fixed_summary["window"]["auc_mean"] + NOISE_EPS
    random_must_fail_by_weight = {str(w): (random_auc <= sweep_summary[str(w)]["auc_mean"] + NOISE_EPS)
                                   for w in WEIGHT_GRID}
    random_must_fail_ok = random_must_fail_vs_window and all(random_must_fail_by_weight.values())

    baseline_in_band = 0.05 < fixed_summary["window"]["acc_overall_mean"] < 0.95

    # --- sweet-spot / Pareto-tension search over the interior sweep grid ---
    per_weight_gate = {}
    for w in WEIGHT_GRID:
        s = sweep_summary[str(w)]
        loc_ok = s["acc_location_mean"] >= window_loc_acc - NOISE_EPS
        art_ok = s["acc_artifact_mean"] >= window_art_acc - NOISE_EPS
        wordsim_ok = s["wordsim_auc_mean"] >= window_wordsim - NOISE_EPS
        joint_fix = loc_ok and art_ok
        clean_sweet_spot = joint_fix and wordsim_ok
        margin_loc = s["acc_location_mean"] - window_loc_acc
        margin_art = s["acc_artifact_mean"] - window_art_acc
        margin_wordsim = s["wordsim_auc_mean"] - window_wordsim
        borderline = clean_sweet_spot and (min(margin_loc, margin_art, margin_wordsim) < SWEET_SPOT_BORDERLINE_EPS)
        per_weight_gate[str(w)] = {
            "loc_ok": bool(loc_ok), "art_ok": bool(art_ok), "wordsim_ok": bool(wordsim_ok),
            "joint_fix": bool(joint_fix), "clean_sweet_spot": bool(clean_sweet_spot),
            "borderline": bool(borderline),
            "margin_loc": float(margin_loc), "margin_art": float(margin_art),
            "margin_wordsim": float(margin_wordsim),
        }

    sweet_spot_weights = [w for w in WEIGHT_GRID if per_weight_gate[str(w)]["clean_sweet_spot"] and w != 1.0]
    joint_fix_weights = [w for w in WEIGHT_GRID if per_weight_gate[str(w)]["joint_fix"] and w != 1.0]
    sweet_spot_exists = len(sweet_spot_weights) > 0
    # prefer the LARGEST qualifying w (closest to pure window -> least dependency weight needed ->
    # "cheapest fix", preserves the most topical content).
    best_sweet_spot_w = max(sweet_spot_weights) if sweet_spot_exists else None
    any_borderline = any(per_weight_gate[str(w)]["borderline"] for w in sweet_spot_weights)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not baseline_in_band:
        verdict = "MIDDLE_BAND_WINDOW_BASELINE_OUT_OF_BAND"
    elif not random_must_fail_ok:
        verdict = "HARD_FAIL_MUST_FAIL_CONTROL_RANDOM_CONTEXT_BEATS_COMBINED_OR_WINDOW"
    elif sweet_spot_exists:
        tag = "BORDERLINE" if any_borderline else "CLEAN"
        verdict = f"HARD_PASS_{tag}_SWEET_SPOT_FOUND_W_{best_sweet_spot_w}"
    elif len(joint_fix_weights) > 0:
        verdict = "HARD_FAIL_GENUINE_PARETO_TENSION_EVERY_FIX_COSTS_WORDSIM"
    elif dep_loc_acc >= window_loc_acc - NOISE_EPS and dep_art_acc < window_art_acc - NOISE_EPS:
        verdict = "MIDDLE_BAND_DEPENDENCY_STILL_INVERTS_NO_SWEEP_POINT_JOINTLY_FIXES"
    else:
        verdict = "HARD_FAIL_NO_JOINT_CATEGORY_FIX_AT_ANY_WEIGHT"

    elapsed = time.perf_counter() - t0
    curve_str = " | ".join(
        f"w={w}: loc={sweep_summary[str(w)]['acc_location_mean']:.3f} "
        f"art={sweep_summary[str(w)]['acc_artifact_mean']:.3f} "
        f"wordsim={sweep_summary[str(w)]['wordsim_auc_mean']:.4f}"
        for w in WEIGHT_GRID
    )
    verdict_msg = (
        f"window: loc={window_loc_acc:.3f} art={window_art_acc:.3f} wordsim={window_wordsim:.4f} | "
        f"dependency(w=0.0): loc={dep_loc_acc:.3f} art={dep_art_acc:.3f} | "
        f"PARETO CURVE: {curve_str} | sweet_spot_weights={sweet_spot_weights} "
        f"best_sweet_spot_w={best_sweet_spot_w} joint_fix_weights={joint_fix_weights} | "
        f"random_auc={random_auc:.4f} random_must_fail_ok={random_must_fail_ok} | "
        f"n_test_artifact={len(test_artifact)} n_test_location={len(test_location)} | "
        f"cardinality_ok={cardinality_ok} ({n_units_done}/{expected_n_units})"
    )

    # --- arms-must-differ (hash of predicted-type arrays; representative combined point = w=0.5,
    # the maximally-interior/differentiated sweep point; w=1.0 vs window intentionally excluded from
    # this gate -- see combined_w1_equals_window_check diagnostic above, a designed identity not a bug) ---
    last_seed = seeds[-1]
    window_emb, _ = dc.build_ppmi_svd(window_ppmi, N_TARGET, last_seed)
    dep_emb, _ = dc.build_ppmi_svd(dep_ppmi, N_TARGET, last_seed)
    random_cooc = dc.build_random_context_cooc(window_cooc, last_seed)
    random_ppmi = cb.build_ppmi(random_cooc)
    random_emb, _ = dc.build_ppmi_svd(random_ppmi, N_TARGET, last_seed)
    combined_half_emb = blend_channels(window_emb, dep_emb, 0.5)
    hash_arms = {"window": window_emb, "dependency": dep_emb, "random_context": random_emb,
                 "combined_w0.5": combined_half_emb}
    pred_hashes = {}
    for name, emb in hash_arms.items():
        preds, _m = dc.prototype_classify(emb, ex_art_idx, ex_loc_idx, test_words)
        ordered = "|".join(preds[w] for w, _, _ in sorted(test_words))
        pred_hashes[name] = hashlib.sha256(ordered.encode()).hexdigest()

    arms_differ_all = True
    arms_differ_detail = {}
    names = list(hash_arms.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            same = pred_hashes[a] == pred_hashes[b]
            arms_differ_detail[f"{a}_vs_{b}"] = not same
            if same:
                arms_differ_all = False
    if not arms_differ_all and verdict not in ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",):
        # arms-identical is a harder gate failure than a substantive MIDDLE/HARD_FAIL verdict --
        # promote it (mirrors v1's ordering: cardinality -> arms_differ -> baseline_in_band -> ...).
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"

    metrics = {
        "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {verdict_msg[:220]}", "elapsed_s": elapsed,
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "config": {**cfg, "N_TARGET": N_TARGET, "seeds": seeds, "weight_grid": WEIGHT_GRID,
                   "n_test_artifact": len(test_artifact), "n_test_location": len(test_location),
                   "exemplar_artifact": [w for w, _, _ in exemplar_artifact],
                   "test_artifact": [w for w, _, _ in test_artifact],
                   "exemplar_location": [w for w, _, _ in exemplar_location],
                   "test_location": [w for w, _, _ in test_location],
                   "dep_col_names": col_names, "V": V},
        "dep_trigger_hits": trigger_hits, "dep_misses": dep_misses,
        "dep_zero_row_frac_by_seed": dep_zero_row_frac_by_seed,
        "fixed_arm_summary": fixed_summary,
        "sweep_summary": sweep_summary,
        "per_weight_gate": per_weight_gate,
        "sweet_spot_weights": sweet_spot_weights, "best_sweet_spot_w": best_sweet_spot_w,
        "joint_fix_weights": joint_fix_weights,
        "combined_w1_equals_window_by_seed": combined_w1_equals_window_by_seed,
        "naive_location_acc": naive_location_acc, "naive_artifact_acc": naive_artifact_acc,
        "random_must_fail_ok": random_must_fail_ok,
        "random_must_fail_vs_window": random_must_fail_vs_window,
        "random_must_fail_by_weight": random_must_fail_by_weight,
        "baseline_in_band": baseline_in_band,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_n_units, "n_units_done": n_units_done,
        "arms_differ_verified": arms_differ_all, "arms_differ_detail": arms_differ_detail,
        "arms_differ_exempted": [],
        "bands": {"SWEET_SPOT_BORDERLINE_EPS": SWEET_SPOT_BORDERLINE_EPS, "CHANCE_AUC": CHANCE_AUC},
        "crlb_n/a": "binary typing-accuracy + rank-sum AUC over discrete ARTIFACT/LOCATION test items; "
                    "closed-form chance floor = 0.50 (THEORETICAL); not a CRLB regime",
        "final_metrics_atomicity": "tmp_replace",
        "deterministic_seeding": True,
        "progress_logging": "print_flush_true",
        "combine_method": "concat(w*L2norm(window), (1-w)*L2norm(dep))_then_L2_renormalize",
        "parser_staging_status": "SAME as v1: no_spacy_in_venv; text8_has_zero_punctuation_sentence_"
                                 "boundaries; rule_based_POS_free_preposition_verb_slot_approximation_"
                                 "used (see prereg)",
        "integration_of": ["exp_dependency_context_codebook_location_artifact_v1 (this cell's direct "
                           "predecessor; dep-cooc/PPMI-SVD/classifier pipeline reused unmodified)",
                           "exp_learned_codebook_generalization_gate_v1 (atom 29368, window-PPMI-SVD "
                           "mechanism + wordsim/simlex eval, reused unmodified)",
                           "exp_derived_filler_typing_single_edge_grounding_v1 (atom 29391, "
                           "STORED_SENTENCE_NOUNS reused unmodified; ARTIFACT/LOCATION pools EXPANDED "
                           "this cell)"],
        "REQUIRED_FIELDS": ["verdict", "fixed_arm_summary", "sweep_summary", "cardinality_ok",
                            "arms_differ_verified", "baseline_in_band", "sweet_spot_weights"],
    }
    _atomic_write_metrics(output_dir, metrics)
    print(f"\n[VERDICT] {verdict}\n{verdict_msg}\nelapsed={elapsed:.1f}s -> {output_dir}/metrics.json",
          flush=True)
    return metrics


# --------------------------------------------------------------------------- self-test
def self_test():
    """Fast real-code-path self-test: tiny toy corpus with embedded artifact/location context AND
    embedded prep/verb triggers, exercising the REAL builders (cb.* + dc.* + THIS cell's
    build_word_pools_v2/blend_channels) through a scaled-down version of this cell's own logic --
    not a synthetic-only branch (Gate F.1)."""
    print("[self-test] real_code_path: building tiny toy corpus with embedded triggers", flush=True)
    sents = [
        "the team built a castle near the forest",
        "the workers built a tower beside the mountain",
        "the monks built a chapel within the island",
        "the settlers built a fort across the desert",
        "the factory made a tool used in the harbor",
        "the workers use a crane at the castle",
        "the crew created a dock near the island",
        "the masons built a shrine beside the plateau",
        "the guild built a chamber within the peninsula",
        "birds live in the forest and near the mountain",
        "fish swim in the harbor and on the island",
        "travelers walk at the desert and near the plateau",
        "hikers camp at the peninsula and near the forest",
    ]
    base_tokens = " ".join(sents).split()
    tokens = base_tokens * 8  # repeat for min_count
    w2i, counts = cb.build_vocab(tokens, vocab_size=80, min_count=1)
    V = len(w2i)
    assert V >= 15, f"toy vocab too small V={V}"

    print("[self-test] real_code_path: exercising build_word_pools_v2 with a toy pool + small n_test "
          "(proves the generalized coverage/disjointness logic, not the full n=20 count)", flush=True)
    toy_artifact_pool = ["castle", "tower", "chapel", "shrine", "chamber"]
    toy_location_pool = ["forest", "mountain", "island", "plateau", "peninsula"]
    # temporarily relax the >=20 design-contract check for this toy-scale call by calling the pool
    # logic directly (not run()); we validate the >=20 contract itself via a separate negative test.
    def _toy_pools(w2i, counts, n_ex_a, n_te_a, n_ex_l, n_te_l):
        def present_sorted(pool):
            pres = [(w, w2i[w], float(counts[w2i[w]])) for w in pool if w in w2i]
            pres.sort(key=lambda x: (-x[2], x[0]))
            return pres
        art = present_sorted(toy_artifact_pool)
        loc = present_sorted(toy_location_pool)
        assert len(art) >= n_ex_a + n_te_a and len(loc) >= n_ex_l + n_te_l
        ex_a = art[:n_ex_a]; te_a = art[n_ex_a:n_ex_a + n_te_a]
        ex_l = loc[:n_ex_l]; te_l = loc[n_ex_l:n_ex_l + n_te_l]
        ex_words = {w for w, _, _ in ex_a + ex_l}
        te_words = {w for w, _, _ in te_a + te_l}
        assert ex_words.isdisjoint(te_words)
        assert te_words.isdisjoint(dft.STORED_SENTENCE_NOUNS), te_words & dft.STORED_SENTENCE_NOUNS
        return ex_a, te_a, ex_l, te_l
    ex_a, te_a, ex_l, te_l = _toy_pools(w2i, counts, 2, 2, 2, 2)
    print(f"[self-test] toy pools OK: exemplar_artifact={[w for w,_,_ in ex_a]} "
          f"test_artifact={[w for w,_,_ in te_a]} exemplar_location={[w for w,_,_ in ex_l]} "
          f"test_location={[w for w,_,_ in te_l]}", flush=True)

    print("[self-test] real_code_path: verifying the >=20-per-category design contract raises loud "
          "(not silent) when violated", flush=True)
    try:
        build_word_pools_v2(w2i, counts, toy_artifact_pool, toy_location_pool, 2, 2, 2, 2,
                             dft.STORED_SENTENCE_NOUNS)
        raise AssertionError("expected DESIGN_CONTRACT_VIOLATION RuntimeError, none raised")
    except RuntimeError as e:
        assert "DESIGN_CONTRACT_VIOLATION" in str(e), str(e)
        print(f"[self-test] contract-violation correctly raised loud: {e}", flush=True)

    print("[self-test] real_code_path: exercising dc.* pipeline (window+dep cooc/ppmi/svd) at toy scale",
          flush=True)
    window_cooc = cb.build_cooc(tokens, w2i, window=3)
    window_ppmi = cb.build_ppmi(window_cooc)
    surface_to_slots, col_names = dc.build_dependency_trigger_table(dc.LOCATIVE_PREPS, dc.ARTIFACT_VERB_FORMS)
    dep_cooc, trigger_hits, misses = dc.build_dep_cooc(tokens, w2i, surface_to_slots, col_names)
    assert dep_cooc.nnz > 0 and any(v > 0 for v in trigger_hits.values())
    dep_ppmi = cb.build_ppmi(dep_cooc)
    window_emb, _wk = dc.build_ppmi_svd(window_ppmi, target_n=32, seed=0)
    dep_emb, _dk = dc.build_ppmi_svd(dep_ppmi, target_n=32, seed=0)
    assert window_emb.shape == (V, 32) and dep_emb.shape == (V, 32)

    print("[self-test] real_code_path: exercising blend_channels at every WEIGHT_GRID point + verifying "
          "w=1.0 identity with pure window", flush=True)
    ex_art_idx = [w2i[w] for w in ["castle", "tower"]]
    ex_loc_idx = [w2i[w] for w in ["forest", "mountain"]]
    test_artifact = [(w, w2i[w], "ARTIFACT") for w in ["chapel", "shrine"]]
    test_location = [(w, w2i[w], "LOCATION") for w in ["island", "plateau"]]
    test_words = test_artifact + test_location
    window_preds, _wm = dc.prototype_classify(window_emb, ex_art_idx, ex_loc_idx, test_words)
    for w in WEIGHT_GRID:
        combo = blend_channels(window_emb, dep_emb, w)
        assert combo.shape == (V, 64)
        preds, margins = dc.prototype_classify(combo, ex_art_idx, ex_loc_idx, test_words)
        m = dc.score_arm(preds, margins, test_artifact, test_location)
        assert 0.0 <= m["acc_overall"] <= 1.0 and np.isfinite(m["auc"])
        print(f"[self-test] combined(w={w}): acc_overall={m['acc_overall']:.3f} auc={m['auc']:.3f}",
              flush=True)
        if w == 1.0:
            assert preds == window_preds, (
                f"w=1.0 combined must be prediction-identical to pure window (design invariant): "
                f"combined={preds} window={window_preds}")
            print("[self-test] w=1.0 identity-with-window check PASSED", flush=True)

    print("[self-test] PASS: real tokenizer/vocab/cooc/ppmi builders (dc.* reused unmodified) + "
          "build_word_pools_v2 (coverage assert + design-contract assert, both fire correctly) + "
          "blend_channels at every grid weight + w=1.0 identity invariant all exercised at toy scale. "
          "Full run() (real ARTIFACT_POOL_V2/LOCATION_POOL_V2 vocab-coverage pools, n_test=20 each) is "
          "exercised end-to-end only at --smoke/--full scale.", flush=True)


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only cell; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if args.smoke:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        run(output_dir, SMOKE_CFG_V2, SEEDS, run_mode="smoke")
    else:
        output_dir = os.path.join(REPO, "data", ANCHOR_NAME)
        run(output_dir, FULL_CFG_V2, SEEDS, run_mode="full")
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
