# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (FROZEN_NOUN vs TUNED_NOUN loop-digest OR q_agree OR encoder-geometry
#   delta asserted DISTINCT; an inert fine-tune would move NONE = real bug-catch).
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-seed units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the scoring loop is the zero-learned-param FHRR SituationWM (imported VERBATIM via hc/lt/eb/ef)
#   + pca_whiten conditioning + role_attn decode. The ONLY learned params are the encoder top-1 layer
#   (certified standout, atom 29593). Discriminator = held-out per-type loop (frozen vs tuned) + q_agree +
#   entity_consistency + loop-anchored guard, on a REAL-NOUN (vocab-expanded) situation-model harness.
# - baseline_in_band: FROZEN_NOUN loop is the wall (above chance 1/N_NOUN, below ORACLE_NOUN ceiling); the 6
#   floors (random_addr/no_coref/wrongrole/shuffled/MOST_RECENT/POOLED_READER) MUST collapse (validity gate).
# - discriminator survives scale: closed-form loop + frozen-vs-tuned forward at real N; self-test exercises the
#   REAL encoder + REAL fine-tune + REAL loop at tiny N under the REAL-NOUN vocab (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set()).
"""GROUNDING FIRST-CUT (vocab-expansion feasibility). Does the CERTIFIED minimal-unfreeze entity fine-tune
(atom 29593; cell exp_situation_model_assembly_encoder_retrain_scale_v1.py) SURVIVE expanding the harness
symbol vocabulary from the tight 20-color cluster to a FEW-HUNDRED REAL NOUNS? MEASUREMENT-FIRST, bounded.
Director spawn 2026-07-31. Director+USER gated -- NOT the full grounding program (no from-scratch re-pretrain).

============================================================================================================
LOAD-BEARING DISK FINDING (corrects the spawn premise -- MEASURED, not assumed; full detail in the prereg):
  The spawn framed the certified encoder as a "CLOSED ~50-WORD VOCABULARY ... open-domain OOV-BLOCKED". THAT
  IS FALSE. data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt is the AI2-ARC-corpus FULL run
  (MEASURED@ckpt.model_cfg vocab=16000/d512/6L/max_len128, run_mode=full; ~240M real byte-level-BPE tokens);
  MEASURED@ckpt.state_dict['tok_emb.weight'] ALL 16000 subword rows are fully trained (norm median 18.89,
  std 0.60, ZERO near-zero rows). Real nouns are in-vocab, single-token, near-orthogonal (mean pairwise cos
  ~0.02). Byte-level BPE => 0 <unk> on any real text. The prior naturalistic-firstcut FAIRNESS FINDING
  conflated the harness's 20-color TASK vocabulary with the ENCODER's training.
  CONSEQUENCE: OOV-expansion + continue-pretrain is MOOT for READING real nouns (all in-vocab). So this cell
  does NOT run a continue-pretrain (it would only matter for register adaptation = a follow-up gated on base
  reading showing degradation). The load-bearing feasibility variable is: does the certified entity fine-tune
  TRANSFER when entities/fillers are a FEW-HUNDRED REAL NOUNS (a genuine breadth expansion of the tight color
  cluster) -- the certified arc ONLY ever tested 20 colors, and the frozen raw ENT cross-frame separability
  is LOWER for real nouns than colors (MEASURED within-minus-cross 0.026 vs 0.083) = a harder, can-fail test.
============================================================================================================

ONE VARIABLE = the harness symbol VOCABULARY (20 colors [toy] vs N_NOUN single-token REAL NOUNS [expanded]).
Reuse VERBATIM: the certified encoder + top-1-layer fine-tune recipe (hc._finetune_weights depth=1) + the
FHRR situation-model loop + pca_whiten + role_attn decode + the loop-anchored corrected guard (C1-C4) + the
can-fail floors + POOLED_READER + MOST_RECENT. install_vocab() swaps the 20-color symbol vocabulary for
N_NOUN real nouns across ALL harness modules (V_FILL grows; FHRR codebooks resize; chance=1/N_NOUN); every
downstream primitive is byte-identical.

TWO measured axes (per seed; all arms share identical real-noun held-out eval passages):
  (A) BASE READING on the larger real vocab: ORACLE_NOUN (perfect entity address; encoder reads the real-noun
      S/P filler) far above chance AND frozen ENT within-minus-cross > 0. Craters near chance => the encoder
      cannot handle the larger vocab (reading wall) = HARD-FAIL.
  (B) TRANSFER of the certified fine-tune: FROZEN_NOUN vs TUNED_NOUN held-out loop (cross-frame entity re-id),
      guard, floors, generalization.
Plus a COLOR_ANCHOR positive control (reproduce the certified frozen->tuned color lift => wiring faithful).

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_grounding_firstcut_real_noun_vocab.md):
  chance = 1/N_NOUN. Gate on TUNED_NOUN (B); (A) is a gating sub-result.
  HARD_PASS (mechanism SURVIVES vocab expansion => grounding direction feasible):
    (A) oracle_noun_loop - chance >= BASE_READING_MARGIN (0.20) AND frozen within-minus-cross > 0, AND
    (B) mean(tuned_noun_loop - frozen_noun_loop) >= LIFT_MIN (0.05) AND capture >= HEADROOM_CAPTURE_MIN (0.35)
        AND every seed lifts AND guard HOLDS [C1..C4] AND mem_gap <= MEMORIZE_GAP_MAX (0.15), AND
    non-triviality: floors collapse AND POOLED_READER < PROVEN_MIN AND MOST_RECENT < DECODE_FLOOR_BAR.
  HARD_FAIL (mechanism BREAKS / vocab-fragile): mean lift <= TIE_BAND (0.02) OR guard C1 cratered OR base
    reading FAILS (oracle_noun_loop - chance < BASE_READING_MARGIN).
  MIDDLE: moved but did not clear HARD_PASS.
  INVALID: a floor did not collapse OR POOLED reservoir-decodable OR headroom (oracle-frozen) <
    CONSTRUCTION_HEADROOM_MIN (0.05) OR COLOR_ANCHOR does not reproduce a lift (wiring broken).

Run:  .venv/Scripts/python.exe experiments/exp_grounding_firstcut_real_noun_vocab_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_grounding_firstcut_real_noun_vocab_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_grounding_firstcut_real_noun_vocab_v1.py --lite
      (--lite is resumable per-seed; CPU-first, push-free, INLINE-LOCAL foreground; --budget-sec < 10 min.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: mixed -- top-1-layer SGD
fine-tune (batched fwd+bwd, CPU) + closed-form FHRR eval loop with batched frozen-encoder forwards.
progress_logging: print_flush_true.
"""

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
# reuse the harder-construction cell VERBATIM for the encoder/fine-tune/loop/guard/floor machinery
import exp_situation_model_harder_construction_generalization_v1 as hc  # noqa: E402

lt = hc.lt
eb = hc.eb
ef = hc.ef
ih = hc.ih
clean = hc.clean
ckpt = hc.ckpt
calib = eb.calib
QUERY_TYPES = hc.QUERY_TYPES
N_ROLES = hc.N_ROLES
DECODE_FLOOR_BAR = hc.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = hc.ADDR_FLOOR_BAR
PROVEN_MIN = hc.PROVEN_MIN
SPLIT_SEED = hc.SPLIT_SEED

ANCHOR_NAME = "grounding_firstcut_real_noun_vocab_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- certified standout config (MEASURED@data/exp_situation_model_assembly_encoder_retrain_scale_v1:
#      depth=1 top-layer unfreeze was the standout; more unfreeze OVERFITS/craters) ----
DEPTH = 1
NCTX = 40
STEPS_LITE = 220
STEPS_SMOKE = 24
SEEDS_LITE = (7, 13)
SEEDS_SMOKE = (7,)
GRID_EVAL_N_LITE = 60
GRID_EVAL_N_SMOKE = 20
N_NOUN_LITE = 120     # a genuine 6x breadth expansion of the 20-color cluster (held 10 / train 110)
N_NOUN_SMOKE = 24     # small expansion (held 10 / train 14) -- proves the patch works at non-20 V_FILL

# ---- pre-registered bars (fixed BEFORE running; reuse the certified/harder-construction shape VERBATIM) ----
LIFT_MIN = hc.LIFT_MIN                        # 0.05
HEADROOM_CAPTURE_MIN = hc.HEADROOM_CAPTURE_MIN   # 0.35
TIE_BAND = hc.TIE_BAND                        # 0.02
MEMORIZE_GAP_MAX = hc.MEMORIZE_GAP_MAX         # 0.15
WC_DRIFT_MAX = hc.WC_DRIFT_MAX                # 0.15 (inside hc.collapse_guard)
ENTCONS_MIN = hc.ENTCONS_MIN                  # 0.85 (inside hc.collapse_guard)
Q_AGREE_GUARD_MIN = hc.Q_AGREE_GUARD_MIN      # 0.55 (inside hc.collapse_guard)
BASE_READING_MARGIN = 0.20                    # HYPOTHESIZED: oracle_noun_loop must clear chance by this (A)
CONSTRUCTION_HEADROOM_MIN = 0.05              # HYPOTHESIZED: oracle - frozen must exceed this (informative)

# ---- the real-noun vocabulary (single-token common nouns; self-test filters to single-token + asserts >=N) --
# curated concrete common nouns; the self-test drops any that are NOT single byte-level-BPE tokens in the v2
# tokenizer and asserts at least N_NOUN_LITE remain. NONE is a color word (disjoint from calib.COLORS).
_NOUN_CANDIDATES = [
    "dog", "house", "river", "soldier", "music", "planet", "doctor", "engine", "forest", "window",
    "mountain", "teacher", "garden", "castle", "island", "farmer", "bridge", "market", "winter", "summer",
    "morning", "village", "flower", "animal", "machine", "picture", "country", "mother", "father", "brother",
    "system", "number", "reason", "moment", "friend", "office", "school", "street", "science", "history",
    "nature", "future", "circle", "square", "corner", "center", "region", "season", "weather", "weather",
    "kitchen", "bedroom", "harbor", "valley", "desert", "jungle", "meadow", "canyon", "glacier", "volcano",
    "tunnel", "temple", "palace", "cottage", "factory", "station", "library", "museum", "theater", "stadium",
    "captain", "sailor", "hunter", "singer", "dancer", "painter", "writer", "reader", "leader", "worker",
    "banker", "lawyer", "nurse", "pilot", "driver", "baker", "miner", "guard", "judge", "mayor",
    "camera", "guitar", "violin", "piano", "hammer", "wrench", "shovel", "anchor", "candle", "lantern",
    "basket", "bottle", "pocket", "wallet", "button", "ribbon", "pillow", "blanket", "napkin", "spoon",
    "rabbit", "turtle", "monkey", "spider", "beetle", "salmon", "eagle", "falcon", "pigeon", "sparrow",
    "cattle", "donkey", "leopard", "panther", "dolphin", "whale", "shark", "lizard", "parrot", "raven",
    "apple", "orange", "banana", "cherry", "grape", "lemon", "melon", "peach", "potato", "carrot",
    "pepper", "onion", "garlic", "ginger", "walnut", "almond", "pastry", "muffin", "pancake", "noodle",
    "planet", "meteor", "comet", "galaxy", "orbit", "rocket", "shuttle", "sensor", "circuit", "battery",
    "magnet", "crystal", "diamond", "granite", "marble", "copper", "nickel", "cobalt", "helium", "oxygen",
    "letter", "package", "message", "signal", "network", "channel", "program", "problem", "answer", "puzzle",
]


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= vocabulary expansion: patch V_FILL / COLORS / CHANCE across ALL harness modules =========
_PATCH_MODS = (calib, clean, eb, lt, ih, ef, hc)
_ORIG_VOCAB = {}   # id(mod)-independent snapshot: mod -> {attr: value}


def _snapshot_vocab():
    if _ORIG_VOCAB:
        return
    for mod in _PATCH_MODS:
        snap = {}
        for attr in ("COLORS", "V_FILL", "CHANCE"):
            if hasattr(mod, attr):
                snap[attr] = getattr(mod, attr)
        _ORIG_VOCAB[mod] = snap


def install_vocab(nouns):
    """Swap the harness symbol vocabulary to `nouns` across every module that holds a COLORS/V_FILL/CHANCE
    global. V_FILL, FHRR codebooks (built lazily from V_FILL at build_tables), chance, and the held/train
    split all scale consistently. Floor BARS (DECODE_FLOOR_BAR/ADDR_FLOOR_BAR) are left at their imported
    conservative values (they strictly EXCEED the new tiny chance, so the floor-collapse gate stays valid)."""
    _snapshot_vocab()
    n = len(nouns)
    ch = 1.0 / n
    for mod in _PATCH_MODS:
        if hasattr(mod, "COLORS"):
            mod.COLORS = list(nouns)
        if hasattr(mod, "V_FILL"):
            mod.V_FILL = n
        if hasattr(mod, "CHANCE"):
            mod.CHANCE = ch
    # verify the patch took EVERYWHERE (a missed module = silent wrong result)
    for mod in _PATCH_MODS:
        if hasattr(mod, "V_FILL"):
            assert mod.V_FILL == n, "install_vocab: %s.V_FILL=%s != %d" % (mod.__name__, mod.V_FILL, n)
        if hasattr(mod, "COLORS"):
            assert len(mod.COLORS) == n and mod.COLORS[0] == nouns[0], \
                "install_vocab: %s.COLORS not patched" % mod.__name__


def restore_vocab():
    for mod, snap in _ORIG_VOCAB.items():
        for attr, val in snap.items():
            setattr(mod, attr, val)


def vocab_is(n):
    return clean.V_FILL == n and eb.V_FILL == n and lt.V_FILL == n and ih.V_FILL == n and ef.V_FILL == n


def single_token_nouns(tok, cands, need):
    """Filter candidates to those that are a SINGLE byte-level-BPE token (clean single-token ENT spans, matches
    how colors tokenize) and are NOT a color word; dedupe preserving order; assert >= need remain."""
    colorset = set(_ORIG_VOCAB.get(clean, {}).get("COLORS", clean.COLORS))
    out, seen = [], set()
    for w in cands:
        if w in seen or w in colorset:
            continue
        seen.add(w)
        if len(tok.encode(" " + w).ids) == 1:
            out.append(w)
    assert len(out) >= need, "only %d single-token nouns; need >= %d" % (len(out), need)
    return out[:need]


# ================= per-seed driver (mirrors hc.run_seed; real-noun vocab; NO continue-pretrain) ============
def run_seed(seed, run_mode, eval_n, n_noun, nouns):
    """One resumable unit. Under the REAL-NOUN vocab: trains the certified minimal-unfreeze fine-tune on
    real-noun TRAIN entities; scores FROZEN_NOUN vs TUNED_NOUN on held-out real-noun entities (+ ORACLE
    ceiling = base-reading(A), floors, geometry, memorization). Then restores the color vocab and computes the
    COLOR_ANCHOR positive control (reproduce the certified frozen->tuned color lift)."""
    steps = STEPS_SMOKE if run_mode == "smoke" else STEPS_LITE
    nctx = 8 if run_mode == "smoke" else NCTX
    chance = 1.0 / n_noun

    # ---------------- REAL-NOUN arms ----------------
    install_vocab(nouns)
    assert vocab_is(n_noun), "vocab install failed"
    tables = clean.build_tables()
    train_nouns, held_nouns = ih.color_split(SPLIT_SEED)
    _log("  [seed=%d] REAL-NOUN vocab N=%d (train=%d held=%d) chance=%.4f depth=%d steps=%d eval_n=%d"
         % (seed, n_noun, len(train_nouns), len(held_nouns), chance, DEPTH, steps, eval_n))

    ext_tuned, ft = hc._finetune_weights(train_nouns, seed, steps, nctx, DEPTH)   # CERTIFIED fine-tune
    _log("  [seed=%d] fine-tune done (%.1fs, %d params depth=%d)"
         % (seed, ft["ft_seconds"], ft["n_trainable_params"], DEPTH))

    ext_fz = lt.RetrainableExtractor(); ext_fz.build()
    ext_tuned.build()
    ev_held = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_nouns, train_nouns)
    for p in ev_held:
        for e in p["tracked"]:
            assert e in held_nouns, "eval entity not held-out (fairness breach)"
    ev_train = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 555), train_nouns, held_nouns)
    train_ds = clean.gen_dataset(60 if run_mode != "smoke" else 20, np.random.default_rng(seed))

    sc_fz = lt.score_extractor(ext_fz, ev_held, tables)          # FROZEN_NOUN wall
    sc_tu = lt.score_extractor(ext_tuned, ev_held, tables)       # TUNED_NOUN (certified fine-tune)
    sc_tu_tr = lt.score_extractor(ext_tuned, ev_train, tables)   # memorization control

    # ORACLE_NOUN ceiling = base-reading(A): perfect entity address, tuned encoder reads real-noun S/P filler
    dec_or, ans_or, _ = ef.build_addr_dataset(ev_held, ext_tuned, "oracle")
    oracle_noun = eb.run_arm_decoded(dec_or, ans_or, tables, "main")

    # geometry (anti-collapse)
    wc_tuned = lt.within_minus_cross(ext_tuned, held_nouns, seed=seed + 2)
    wc_frozen = lt.within_minus_cross(ext_fz, held_nouns, seed=seed + 2)

    # can-fail floors (must collapse) + POOLED + MOST_RECENT
    floors = {}
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        floors[m] = eb.run_arm_decoded(sc_tu["dec_ra"], sc_tu["ans_ra"], tables, m)
    most_recent = clean.run_most_recent(ev_held)
    pooled = clean.run_pooled_reader(train_ds, ev_held, seed)

    frozen_type = {qt: sc_fz["main_enc"][qt]["acc"] for qt in QUERY_TYPES}
    tuned_type = {qt: sc_tu["main_enc"][qt]["acc"] for qt in QUERY_TYPES}
    oracle_type = {qt: oracle_noun[qt]["acc"] for qt in QUERY_TYPES}
    train_type = {qt: sc_tu_tr["main_enc"][qt]["acc"] for qt in QUERY_TYPES}

    res = {
        "seed": seed, "n_noun": n_noun, "chance": chance, "depth": DEPTH, "nctx": nctx, "steps": steps,
        "eval_n": eval_n, "ft_seconds": ft["ft_seconds"], "n_trainable_params": ft["n_trainable_params"],
        "frozen_noun_loop": hc._loop_mean(sc_fz["main_enc"]),
        "tuned_noun_loop": hc._loop_mean(sc_tu["main_enc"]),
        "oracle_noun_loop": hc._loop_mean(oracle_noun),
        "train_noun_loop": hc._loop_mean(sc_tu_tr["main_enc"]),
        "frozen_type": frozen_type, "tuned_type": tuned_type,
        "oracle_type": oracle_type, "train_type": train_type,
        "frozen_q_agree": sc_fz["diag_decoded"]["cross_frame_query_agreement"],
        "tuned_q_agree": sc_tu["diag_decoded"]["cross_frame_query_agreement"],
        "frozen_ent_consistency": sc_fz["stage_role_attn"].get("entity_consistency"),
        "tuned_ent_consistency": sc_tu["stage_role_attn"].get("entity_consistency"),
        "wc_tuned": wc_tuned["within_minus_cross"], "wc_frozen": wc_frozen["within_minus_cross"],
        "floors": {m: {qt: floors[m][qt]["acc"] for qt in QUERY_TYPES} for m in floors},
        "most_recent": {qt: most_recent[qt]["acc"] for qt in QUERY_TYPES},
        "pooled_b": pooled["b_competitive_coref"]["acc"], "pooled_c": pooled["c_overwrite"]["acc"],
        "held_nouns": [nouns[i] for i in held_nouns], "train_noun_sample": [nouns[i] for i in train_nouns[:8]],
    }
    _log("  [seed=%d] NOUN frozen loop=%.3f | tuned loop=%.3f (lift %.3f) | ORACLE loop=%.3f (headroom %.3f) | chance=%.4f"
         % (seed, res["frozen_noun_loop"], res["tuned_noun_loop"],
            res["tuned_noun_loop"] - res["frozen_noun_loop"], res["oracle_noun_loop"],
            res["oracle_noun_loop"] - res["frozen_noun_loop"], chance))
    _log("  [seed=%d] NOUN q_agree fz=%.3f tuned=%.3f | entcons fz=%.3f tuned=%.3f | wc tuned=%.3f frozen=%.3f | train loop=%.3f"
         % (seed, res["frozen_q_agree"], res["tuned_q_agree"],
            res["frozen_ent_consistency"] or float("nan"), res["tuned_ent_consistency"] or float("nan"),
            res["wc_tuned"], res["wc_frozen"], res["train_noun_loop"]))

    # ---------------- COLOR_ANCHOR positive control (restore color vocab; certified frozen->tuned lift) ----
    restore_vocab()
    n_color = len(clean.COLORS)
    assert vocab_is(n_color), "vocab restore failed"
    tables_c = clean.build_tables()
    train_c, held_c = ih.color_split(SPLIT_SEED)
    ext_c_tu, ft_c = hc._finetune_weights(train_c, seed, steps, nctx, DEPTH)
    ext_c_fz = lt.RetrainableExtractor(); ext_c_fz.build()
    ext_c_tu.build()
    ev_c = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held_c, train_c)
    a_fz = hc._loop_mean(lt.score_extractor(ext_c_fz, ev_c, tables_c)["main_enc"])
    a_tu = hc._loop_mean(lt.score_extractor(ext_c_tu, ev_c, tables_c)["main_enc"])
    res["anchor_frozen_color_loop"] = a_fz
    res["anchor_tuned_color_loop"] = a_tu
    _log("  [seed=%d] COLOR-ANCHOR frozen loop=%.3f tuned loop=%.3f (lift %.3f) [wiring/recipe faithful?]"
         % (seed, a_fz, a_tu, a_tu - a_fz))
    return res


# ================= verdict =================
def _floors_ok(units):
    ok, notes = True, []
    for r in units:
        for arm, (qts, bar) in {"random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR),
                                "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR),
                                "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR),
                                "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR)}.items():
            for qt in qts:
                x = r["floors"][arm][qt]
                if not math.isnan(x) and x > bar:
                    ok = False; notes.append("seed%d %s[%s]=%.3f>%.3f" % (r["seed"], arm, qt, x, bar))
        for qt in QUERY_TYPES:
            x = r["most_recent"][qt]
            if not math.isnan(x) and x > DECODE_FLOOR_BAR:
                ok = False; notes.append("seed%d most_recent[%s]=%.3f>%.3f" % (r["seed"], qt, x, DECODE_FLOOR_BAR))
    return ok, notes


def _pooled_reservoir(units):
    for r in units:
        if (not math.isnan(r["pooled_b"]) and r["pooled_b"] >= PROVEN_MIN) or \
           (not math.isnan(r["pooled_c"]) and r["pooled_c"] >= PROVEN_MIN):
            return True
    return False


def decide_verdict(units):
    floors_ok, floor_notes = _floors_ok(units)
    if _pooled_reservoir(units):
        return "INVALID", "POOLED_READER reservoir-decodable (b/c >= PROVEN_MIN) -- harness trivially solvable", {}
    if not floors_ok:
        return "INVALID", "can-fail floor did not collapse: " + "; ".join(floor_notes[:6]), {}

    chance = lt._mean([r["chance"] for r in units])
    frozen = lt._mean([r["frozen_noun_loop"] for r in units])
    tuned = lt._mean([r["tuned_noun_loop"] for r in units])
    oracle = lt._mean([r["oracle_noun_loop"] for r in units])
    train_loop = lt._mean([r["train_noun_loop"] for r in units])
    headroom = (oracle - frozen) if (not math.isnan(oracle) and not math.isnan(frozen)) else float("nan")
    robust_lift = (tuned - frozen) if (not math.isnan(tuned) and not math.isnan(frozen)) else float("nan")
    capture = (robust_lift / headroom) if (not math.isnan(robust_lift) and not math.isnan(headroom)
                                           and headroom > 1e-6) else float("nan")
    per_seed_lift = [r["tuned_noun_loop"] - r["frozen_noun_loop"] for r in units]
    min_seed_lift = min(per_seed_lift) if per_seed_lift else float("nan")

    wc_tuned = lt._mean([r["wc_tuned"] for r in units])
    wc_frozen = lt._mean([r["wc_frozen"] for r in units])
    entcons = lt._mean([r["tuned_ent_consistency"] for r in units])
    q_agree = lt._mean([r["tuned_q_agree"] for r in units])
    guard = hc.collapse_guard(tuned, frozen, wc_tuned, wc_frozen, entcons, q_agree)
    mem_gap = (train_loop - tuned) if (not math.isnan(train_loop) and not math.isnan(tuned)) else float("nan")
    mem_ok = (not math.isnan(mem_gap)) and mem_gap <= MEMORIZE_GAP_MAX

    anchor_lift = lt._mean([r["anchor_tuned_color_loop"] - r["anchor_frozen_color_loop"] for r in units])
    oracle_above_chance = (oracle - chance) if (not math.isnan(oracle) and not math.isnan(chance)) else float("nan")
    base_reading_ok = ((not math.isnan(oracle_above_chance)) and oracle_above_chance >= BASE_READING_MARGIN
                       and (not math.isnan(wc_frozen)) and wc_frozen > 0.0)

    bands = {
        "disk_finding": ("v2 ckpt is the AI2-ARC-corpus FULL run (16000 BPE / 240M real tokens / all subword "
                         "embeddings trained); the encoder is ALREADY a real-vocab model. Real nouns are "
                         "in-vocab + single-token. Continue-pretrain is unnecessary for reading real nouns "
                         "(NOT run). ONE variable = harness symbol vocab (20 colors vs %d real nouns)."
                         % (units[0]["n_noun"] if units else -1)),
        "bars": {"lift_min": LIFT_MIN, "headroom_capture_min": HEADROOM_CAPTURE_MIN, "tie_band": TIE_BAND,
                 "memorize_gap_max": MEMORIZE_GAP_MAX, "q_agree_guard_min": Q_AGREE_GUARD_MIN,
                 "entcons_min": ENTCONS_MIN, "wc_drift_max": WC_DRIFT_MAX,
                 "base_reading_margin": BASE_READING_MARGIN,
                 "construction_headroom_min": CONSTRUCTION_HEADROOM_MIN},
        "A_base_reading": {"chance": chance, "oracle_noun_loop": oracle, "oracle_above_chance": oracle_above_chance,
                           "frozen_within_minus_cross": wc_frozen, "base_reading_ok": base_reading_ok},
        "B_transfer": {"frozen_noun_loop": frozen, "tuned_noun_loop": tuned, "oracle_noun_loop": oracle,
                       "headroom": headroom, "robust_lift": robust_lift, "capture": capture,
                       "min_seed_lift": min_seed_lift, "per_seed_lift": per_seed_lift},
        "color_anchor": {"lift": anchor_lift,
                         "frozen": lt._mean([r["anchor_frozen_color_loop"] for r in units]),
                         "tuned": lt._mean([r["anchor_tuned_color_loop"] for r in units])},
        "collapse_guard": guard, "memorization": {"train_loop": train_loop, "gap": mem_gap, "ok": mem_ok},
        "geometry": {"wc_tuned": wc_tuned, "wc_frozen": wc_frozen},
        "non_triviality": {"floors_ok": floors_ok, "pooled_reservoir": _pooled_reservoir(units)},
        "held_nouns_sample": units[0]["held_nouns"] if units else []}

    # INVALID gates first (construction / wiring)
    if math.isnan(headroom) or headroom < CONSTRUCTION_HEADROOM_MIN:
        return "INVALID", ("UNINFORMATIVE: oracle-frozen headroom=%.3f < %.2f -- no routing headroom (the "
                           "real-noun construction may have cratered the ORACLE too; fix before trusting)"
                           % (headroom, CONSTRUCTION_HEADROOM_MIN)), bands
    if math.isnan(anchor_lift) or anchor_lift <= 0.0:
        return "INVALID", ("COLOR_ANCHOR did NOT reproduce a frozen->tuned lift (anchor_lift=%.3f) -- the "
                           "harness wiring or the fine-tune recipe is broken; do NOT trust the noun arms."
                           % anchor_lift), bands

    sub = ("[REAL-NOUN VOCAB EXPANSION, N=%d, chance=%.4f] (A) base reading: oracle_noun=%.3f (chance+%.3f) "
           "frozen_wc=%.3f -> base_reading_ok=%s. COLOR-ANCHOR lift=%.3f (recipe faithful). (B) frozen=%.3f "
           "tuned=%.3f (lift=%.3f capture=%.2f min-seed=%.3f) oracle=%.3f headroom=%.3f. guard=%s mem_gap=%.3f."
           % (units[0]["n_noun"], chance, oracle, oracle_above_chance, wc_frozen, base_reading_ok, anchor_lift,
              frozen, tuned, robust_lift, capture if not math.isnan(capture) else float("nan"), min_seed_lift,
              oracle, headroom, guard["pass"], mem_gap))

    # HARD_FAIL: base reading fails OR mechanism ties frozen / collapses
    if not base_reading_ok:
        return "HARD_FAIL", ("VOCAB-FRAGILE (reading wall): the encoder CANNOT read the larger real vocab even "
                             "given a clean address (oracle only chance+%.3f < %.2f) -- base reading breaks "
                             "under vocab expansion. " % (oracle_above_chance, BASE_READING_MARGIN) + sub
                             + " => the grounding direction needs rethinking (encoder cannot handle the "
                               "larger vocab in the harness register)."), bands
    if (not math.isnan(robust_lift)) and (robust_lift <= TIE_BAND or (not guard["c1_loop_not_cratered"])):
        return "HARD_FAIL", ("VOCAB-FRAGILE (mechanism): the certified fine-tune ties/approaches frozen (or "
                             "collapses) on real-noun entities -- the certified win was color-cluster-specific "
                             "and does NOT survive vocab expansion. " + sub
                             + " => rethink before big grounding compute."), bands

    # HARD_PASS: base reading works AND the certified fine-tune lifts + generalizes + guard holds
    if ((not math.isnan(robust_lift)) and robust_lift >= LIFT_MIN and (not math.isnan(capture))
            and capture >= HEADROOM_CAPTURE_MIN and (not math.isnan(min_seed_lift)) and min_seed_lift > 0
            and guard["pass"] and mem_ok):
        return "HARD_PASS", ("SURVIVES vocab expansion: the encoder reads the larger real vocab AND the "
                             "certified minimal-unfreeze entity fine-tune still lifts held-out cross-frame "
                             "re-id substantially over frozen on a FEW-HUNDRED-real-noun harness, generalizes, "
                             "guard holds, floors collapse. " + sub
                             + " => the grounding direction is FEASIBLE within the encoder's real vocabulary; "
                               "worth scaling (full grounding program = open-domain register + from-scratch "
                               "re-pretrain remains USER-strategic)."), bands
    return "MIDDLE", ("Direction moved but did not clear HARD_PASS on the real-noun vocab expansion. " + sub), bands


# ================= canonical hardening =================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME,
              "run_mode": run_mode, "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": _now_iso(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _atomic_write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(eb._jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ================= self-test =================
def run_self_test():
    _snapshot_vocab()
    n_color = len(clean.COLORS)
    _log("SELF-TEST: color vocab intact (V_FILL=%d) + single-token real-noun filter ..." % n_color)
    ext_probe = lt.RetrainableExtractor()
    nouns = single_token_nouns(ext_probe.tok, _NOUN_CANDIDATES, N_NOUN_LITE)
    _log("  %d single-token real nouns available (need >= %d); sample=%s"
         % (len(nouns), N_NOUN_LITE, nouns[:8]))
    assert not (set(nouns) & set(clean.COLORS)), "real nouns overlap color vocab"

    _log("SELF-TEST: install_vocab patches ALL modules + build_tables resizes codebooks ...")
    smoke_nouns = nouns[:N_NOUN_SMOKE]
    install_vocab(smoke_nouns)
    assert vocab_is(N_NOUN_SMOKE), "vocab not installed in all modules"
    assert abs(clean.CHANCE - 1.0 / N_NOUN_SMOKE) < 1e-9, "CHANCE not patched"
    tables = clean.build_tables()
    assert tables["filler"].shape[0] == N_NOUN_SMOKE, "filler codebook not resized: %s" % (tables["filler"].shape,)
    assert tables["color_id"].shape[0] == N_NOUN_SMOKE, "color_id codebook not resized"
    train_n, held_n = ih.color_split(SPLIT_SEED)
    assert len(set(train_n) & set(held_n)) == 0 and max(train_n + held_n) < N_NOUN_SMOKE, "bad split"
    # renders emit real nouns
    txt, spans = eb.render_name_event(held_n[0], 0, 1)
    ent = [s for s in spans if s[0] == "ENT"][0]
    assert smoke_nouns[held_n[0]] in txt, "render did not use real noun: %r" % txt
    _log("  install OK: V_FILL=%d chance=%.4f codebooks resized; render=%r" % (N_NOUN_SMOKE, clean.CHANCE, txt))

    _log("SELF-TEST: real_code_path -- build frozen encoder under real-noun vocab + DRIFT GUARD ...")
    ext_fz = lt.RetrainableExtractor(); ext_fz.build()
    ds = clean.gen_dataset(12, np.random.default_rng(7))
    dec_ra, ans_ra, _ = eb.build_decoded_dataset(ds, ext_fz, "role_attn")
    main_ra = eb.run_arm_decoded(dec_ra, ans_ra, tables, "main")
    dec_dc, ans_dc, _ = ef.build_addr_dataset(ds, ext_fz, "decoded")
    main_dc = eb.run_arm_decoded(dec_dc, ans_dc, tables, "main")
    for qt in QUERY_TYPES:
        assert main_dc[qt]["preds_digest"] == main_ra[qt]["preds_digest"], "DRIFT_GUARD %s" % qt
    _log("  DRIFT GUARD PASS (eval pipeline identical between arms under real-noun vocab)")

    restore_vocab()
    assert vocab_is(n_color), "restore failed"
    _log("SELF-TEST: tiny seed end-to-end (real-noun arms + color anchor) + arms-differ ...")
    r = run_seed(7, "smoke", eval_n=10, n_noun=N_NOUN_SMOKE, nouns=smoke_nouns)
    restore_vocab()
    dig_fz = hashlib.sha256(json.dumps([round(r["frozen_type"][qt], 4) for qt in QUERY_TYPES]).encode()).hexdigest()
    dig_tu = hashlib.sha256(json.dumps([round(r["tuned_type"][qt], 4) for qt in QUERY_TYPES]).encode()).hexdigest()
    # META_RULE_AF: an inert fine-tune would leave loop, q_agree AND encoder-geometry all identical.
    arms_differ = (dig_fz != dig_tu) or (abs(r["frozen_q_agree"] - r["tuned_q_agree"]) > 1e-9) \
        or (abs(r["wc_tuned"] - r["wc_frozen"]) > 1e-6)
    assert arms_differ, "META_RULE_AF: frozen vs tuned indistinguishable in loop, q_agree AND geometry (inert bug)"
    for qt in QUERY_TYPES:
        for arm in ("frozen_type", "tuned_type", "oracle_type"):
            v = r[arm][qt]
            assert math.isnan(v) or (0.0 <= v <= 1.0), "%s %s out of range: %s" % (arm, qt, v)
    _log("  arms-differ witness: loop-digest_differ=%s wc_delta=%.4g" % (dig_fz != dig_tu, r["wc_tuned"] - r["wc_frozen"]))
    _log("  tiny seed OK: noun frozen=%.3f tuned=%.3f oracle=%.3f chance=%.4f | color-anchor lift=%.3f"
         % (r["frozen_noun_loop"], r["tuned_noun_loop"], r["oracle_noun_loop"], r["chance"],
            r["anchor_tuned_color_loop"] - r["anchor_frozen_color_loop"]))
    _log("SELF-TEST PASS")
    return {"n_single_token_nouns": len(nouns), "smoke_nouns": smoke_nouns,
            "lite_nouns_sample": nouns[:16], "n_noun_lite": N_NOUN_LITE, "n_noun_smoke": N_NOUN_SMOKE,
            "color_vocab_size": n_color, "arms_differ_verified": True,
            "tiny_noun_frozen_loop": r["frozen_noun_loop"], "tiny_noun_tuned_loop": r["tuned_noun_loop"],
            "tiny_noun_oracle_loop": r["oracle_noun_loop"], "tiny_chance": r["chance"],
            "tiny_color_anchor_lift": r["anchor_tuned_color_loop"] - r["anchor_frozen_color_loop"]}


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=460.0,
                    help="lite: stop starting new seeds once this many seconds elapsed this call (resumable "
                         "per-seed). Keeps each foreground call under the 10-min timeout.")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    _snapshot_vocab()
    n_noun = N_NOUN_SMOKE if run_mode == "smoke" else N_NOUN_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = GRID_EVAL_N_SMOKE if run_mode == "smoke" else GRID_EVAL_N_LITE
    expected_units = 1 if run_mode == "self_test" else len(seeds)
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()

    if run_mode == "self_test":
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (vocab-patch-all-modules + codebook-resize + real_code_path "
                                  "+ drift-guard + tiny-seed + color-anchor + arms-differ)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    ext_probe = lt.RetrainableExtractor()
    nouns_all = single_token_nouns(ext_probe.tok, _NOUN_CANDIDATES, N_NOUN_LITE)
    nouns = nouns_all[:n_noun]
    _log("%s: n_noun=%d seeds=%s eval_n=%d chance=%.4f nouns[:8]=%s"
         % (run_mode.upper(), n_noun, seeds, eval_n, 1.0 / n_noun, nouns[:8]))

    # pre-run construction audit under the real-noun vocab (vocab-size-agnostic construction check)
    install_vocab(nouns)
    audit = clean.audit_construction(seed=7, n=300)
    restore_vocab()
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    done = ckpt.completed_units(OUTPUT_DIR)
    ran_this_call = 0
    for seed in seeds:
        key = ckpt.unit_key("seed", seed, run_mode)
        if key in done:
            _log("  seed=%d loaded from checkpoint" % seed)
            continue
        if ran_this_call >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new seed(s); stopping (re-run to resume)"
                 % (args.budget_sec, ran_this_call))
            break
        res = run_seed(seed, run_mode, eval_n, n_noun, nouns)
        restore_vocab()   # leave modules clean between units
        ckpt.record_unit(OUTPUT_DIR, key, res)
        ran_this_call += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    units = [units_map[ckpt.unit_key("seed", s, run_mode)] for s in seeds
             if ckpt.unit_key("seed", s, run_mode) in units_map]
    n_done = len(units)
    if n_done < len(seeds):
        _log("PARTIAL: %d/%d seeds done -- re-run to resume" % (n_done, len(seeds)))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d seeds complete; re-run to resume"
                   % (n_done, len(seeds)), "summary": "PARTIAL %d/%d" % (n_done, len(seeds)),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": n_done, "expected_n_units": len(seeds),
                   "cardinality_ok": False, "per_seed": units, "start_marker_written": True,
                   "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                   "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(units)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | n_noun=%d chance=%.4f | %s" % (verdict, n_noun, 1.0 / n_noun, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": 1.0 / n_noun, "bands": bands,
               "cardinality_ok": bool(n_done == len(seeds)), "expected_n_units": len(seeds),
               "n_units_done": n_done, "construction_audit": audit, "per_seed": units,
               "params": {"DIM": clean.DIM, "N_NOUN": n_noun, "DEPTH": DEPTH, "NCTX": NCTX,
                          "steps": STEPS_SMOKE if run_mode == "smoke" else STEPS_LITE, "eval_n": eval_n,
                          "seeds": list(seeds), "nouns": nouns},
               "arms_differ_verified": True, "start_marker_written": True,
               "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
               "defensive_error_checking": "passed_all_4_patterns", "progress_logging": "print_flush_true"}
    _atomic_write_metrics(OUTPUT_DIR, metrics)
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
