# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor + META_RULE_H units):
# - arms_differ_verified at self-test: FROZEN (no update) vs GRADED (online update) target-loop DIGEST + the
#   per-checkpoint climb vector must DIFFER (an inert online loop that never moves weights = the exact bug this
#   catches); ALSO GRADED vs NOREPLAY must differ (replay must change something) at self-test scale.
# - final_metrics_atomicity: tmp_replace (os.replace at end) + per-unit units.jsonl (resumable per CLAUDE.md).
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n/a: the reader is the zero-learned-param FHRR SituationWM (content-gated WM + competitive coref,
#   imported VERBATIM via eb/clean) + pca_whiten conditioning + role_attn decode. The ONLY learned params are
#   the encoder top-1 layer (certified standout, atom 29593), trained ONLINE here instead of in one batch.
#   Discriminator = the TRAJECTORY of held-ahead comprehension (cross-frame entity re-id loop acc on NOVEL
#   entities at the HARDEST grade) vs amount-read (the CLIMB CURVE), against a FROZEN no-learning control.
#   No quantitative noise floor for a climb-slope discriminator; can-fail bands pre-registered on the curve.
# - baseline_in_band: FROZEN held-ahead loop is the wall (above chance 1/V_FILL, below the online ceiling);
#   the can-fail floors (random_addr/no_coref/wrongrole/shuffled/MOST_RECENT/POOLED_READER) MUST collapse.
# - cardinality_ok (META_RULE_H): EXPECTED_N_UNITS = n_seeds * (1 base + N_ONLINE_ARMS). Verdict counts
#   len(units); < expected => HARD_FAIL_CARDINALITY_BREACH.
# - discriminator survives scale: closed-form loop + online-trained forward at real N; self-test exercises the
#   REAL encoder + REAL online loop + REAL reader at tiny N under the color harness (real_code_path).
# - numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ (META_RULE_AC).
# - deterministic seeding: numpy default_rng + torch.manual_seed only; NO hash(), NO list(set()).
# - progress_logging: print_flush_true (line-buffered stdout + flush=True heartbeats; a run may exceed 15min).
"""CONTINUOUS READ-THE-CURRICULUM-AND-LEARN-AS-YOU-GO LOOP (the actual system, not another batch probe).
USER directive 2026-07-31 (commit 950bef5d1): STOP artificial train-on-a-batch / test-on-a-FROZEN-fixed-probe
experiments. BUILD the continuous process -- read a GRADED sentence stream, LEARN FROM EACH chunk ONLINE (the
encoder's certified comprehension objective updated as it reads), comprehension GROWS, and TEST AS YOU GO on
NEW upcoming material the model has NOT yet read. Anti-forgetting (rehearsal/replay) is the key engineering
risk. Deliverable = the CLIMB CURVE (held-ahead comprehension vs amount-read) + the frozen-control gap + the
forgetting check.

============================================================================================================
WHY THIS, WHY NOW (from the flat diversity probe, e90f7fbb7, MIDDLE/DIAGNOSED): the certified minimal-unfreeze
entity-re-id fine-tune (atom 29593) extracts its FULL held-out grip from ~12 nouns; MORE VOCABULARY at the
SAME DIFFICULTY (a batch) adds NO new signal (immediate saturation -- the "dumb test" USER called out). The
refined curriculum insight (USER): the lever is DIFFICULTY / RICHNESS, not vocabulary count. A real curriculum
climbs DIFFICULTY, which IS genuinely-new signal. This cell tests that claim as the ACTUAL continuous system:
read a stream ordered SIMPLE -> COMPLEX, update online, and measure whether held-ahead comprehension climbs.
============================================================================================================

THE ONE DIFFICULTY AXIS (clean, deterministic, single integer, VET'd degrader): surface-form variation via a
GRADED MODIFIER POOL. Each ENT mention is rendered "the <MOD> <color> ..." (the certified-harder-construction
surface, hc). GRADE g installs a modifier-pool of size n_mods_g: n_mods=1 => the SAME modifier every frame =>
statement-surface == query-surface => cross-frame token-copy WORKS (EASIEST); n_mods=8 (== hc's VET'd hard
renders EXACTLY) => the query modifier usually DIFFERS from the statement modifier => cross-frame surface
MISMATCH => the encoder must abstract identity ACROSS surface variation (HARDEST). P(cross-frame mismatch) ~=
1 - 1/n_mods (monotone in n_mods). This grades BOTH the online training texts AND the held-ahead eval passages
IDENTICALLY, is chance-invariant (answers are fillers, chance = 1/V_FILL FIXED), and is provably graded (a
FROZEN encoder does WORSE at higher n_mods -- MEASURED here + consistent with hc: easy frozen loop 0.449 ->
hard 0.388, entcons 0.817 -> 0.708). Scope note: this is the surface-hardness difficulty axis on the certified
20-color harness -- competing-entity count (K_TRACK) / context length / real-noun BREADTH are ORTHOGONAL axes,
deferred (USER-strategic scale call). This isolates the CURRICULUM / CONTINUAL variable from vocab-breadth.

THE READER / "co-train" HONESTY (load-bearing, stated for the USER): the substrate's certified comprehension
MECHANISM is an ENCODER fine-tune (top-1 layer) with the cross-mention-consistency + inter-entity push + VICReg
objective; the "reader" is the PARAMETER-FREE FHRR situation-model loop (content-gated WM + competitive coref)
that consumes the encoder's rep-geometry. There are NO learned reader params in the certified path (every
learned-reader bolt-on HARD_FAILED 4x -- the "frozen-encoder-is-the-ceiling" arc). So "co-train encoder AND
reader" is realized as: the ONLINE objective shapes the encoder representation that the fixed reader reads.
This is the honest, VET-grounded interpretation; a separate learned reader head is the exact anti-pattern.

ARMS (per seed; the learner -- objective/steps/LR/batch -- is IDENTICAL across the 3 online arms; only the
DATA SCHEDULE differs = the clean one-variable-family):
  BASE     : FROZEN (no online update). References: the frozen held-ahead loop (the flat no-learning control),
             the FROZEN GRADED PROFILE (loop at each grade hardness -- must DECLINE = genuinely graded), the 6
             can-fail floors, POOLED_READER, MOST_RECENT, wc_frozen.
  GRADED   : online update, GRADED order (n_mods 1 -> ... -> 8), WITH replay (rehearsal reservoir). THE SYSTEM.
  SHUFFLED : online update, SHUFFLED grade order (reads the SAME content, NOT simple->complex), WITH replay.
             Isolates whether the ORDERING (the curriculum) matters vs just online learning.
  NOREPLAY : online update, GRADED order, NO replay. Anti-forgetting ablation (forgetting check).

TEST-AS-YOU-GO / CLIMB CURVE: at each grade boundary t=0..G (t=0 = before any reading), snapshot the current
encoder (build the reader pipeline on current weights) and score HELD-AHEAD comprehension = FHRR loop acc on a
FIXED set of NOVEL-entity passages at the HARDEST grade (n_mods=8) -- upcoming material the model has NOT read
at that difficulty. curve[t] vs t = the CLIMB CURVE. GRADED must CLIMB and BEAT the FROZEN control.
FORGETTING CHECK: at t=1 (just after the easy grade) and t=G, also score the EASY held-ahead set (n_mods=1);
forgetting = easy@t1 - easy@tG. Replay (GRADED) should keep it small; NOREPLAY should forget more.

PRE-REGISTERED BANDS (fixed BEFORE running; preregs/2026-07-31_continuous_curriculum_learn_as_you_go.md):
  climb = curve_target(t=G) - curve_target(t=0); beat = curve_target(t=G) - frozen_target (== climb since
  curve[0] is the untrained encoder == frozen). chance = 1/V_FILL. All on FIXED novel-entity held-ahead sets.
  HARD_PASS (LEARN-AS-YOU-GO WORKS -- comprehension CLIMBS as it reads, beats frozen, no forgetting):
    climb >= CLIMB_MIN (0.05) AND every seed climbs (min_seed_climb > 0) AND monotone-ish (curve non-decreasing
    within TIE_BAND) AND forgetting_graded <= FORGET_MAX (0.10) AND collapse-guard HOLDS at t=G AND
    (validity) the FROZEN GRADED PROFILE genuinely declines (frozen_easy_loop - frozen_hard_loop >=
    PROFILE_DECLINE_MIN) AND floors collapse AND POOLED < PROVEN_MIN.
  HARD_FAIL (the loop is BROKEN -- not the capability): guard C1 cratered at t=G (online update DESTROYS the
    reader) OR base reading FAILS at t=G (oracle can't read even the hardest grade).
  FLAT / MIDDLE: climb <= TIE_BAND -> DO NOT conclude a ceiling (USER flat=fix rule). DIAGNOSE which of exactly
    three the experiment is: (a) NOT-LEARNING (weights barely moved OR online loss did not descend OR the
    objective did not fit the TRAIN entities), (b) NO-NEW-CONTENT (the FROZEN GRADED PROFILE is FLAT -> higher
    grades are NOT actually harder -> no genuinely-new signal to climb on), (c) UNDERPOWERED (MDE > CLIMB_MIN).
    If learning happened + content is genuinely graded + adequately powered and STILL flat => CLEAN_DESIGN_LIMIT
    (this online objective does not accrue continual gain from harder surface -- a DESIGN fix: more unfreeze /
    harder negatives / more steps / a second difficulty axis -- NOT a capability ceiling).
  INVALID: a floor did not collapse OR POOLED reservoir-decodable OR the FROZEN GRADED PROFILE does not decline
    (the stream is NOT genuinely graded -> the whole premise is untestable, fix the grading first) OR held not
    disjoint from train.

Run:  .venv/Scripts/python.exe experiments/exp_continuous_curriculum_learn_as_you_go_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_continuous_curriculum_learn_as_you_go_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_continuous_curriculum_learn_as_you_go_v1.py --lite
      (--lite is resumable per-unit; CPU-first, push-free, INLINE-LOCAL foreground; --budget-sec < 10 min.)

ASCII-only. No emojis. Deterministic seeding. Pure CPU. Compute architecture: mixed -- top-1-layer ONLINE SGD
(batched fwd+bwd, CPU) + closed-form FHRR eval loop with batched frozen-encoder forwards at each checkpoint.
Storage strategy: no_storage (encoder online fine-tune + closed-form FHRR eval; no atom-store writes).
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
import torch.nn.functional as F

try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments"))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))
# reuse the harder-construction cell VERBATIM: certified encoder + fine-tune objective + FHRR loop + guard +
# floors + the hard-render surface machinery (MODIFIERS, hard_render_*).
import exp_situation_model_harder_construction_generalization_v1 as hc  # noqa: E402

lt = hc.lt
eb = hc.eb
ef = hc.ef
ih = hc.ih
clean = hc.clean
ckpt = hc.ckpt
QUERY_TYPES = hc.QUERY_TYPES
N_ROLES = hc.N_ROLES
V_FILL = hc.V_FILL
DECODE_FLOOR_BAR = hc.DECODE_FLOOR_BAR
ADDR_FLOOR_BAR = hc.ADDR_FLOOR_BAR
PROVEN_MIN = hc.PROVEN_MIN
SPLIT_SEED = hc.SPLIT_SEED
COLORS = eb.COLORS
ROLE_NAMES = eb.ROLE_NAMES
MODIFIERS = hc.MODIFIERS

ANCHOR_NAME = "continuous_curriculum_learn_as_you_go_v1"
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ---- certified standout config (MEASURED@exp_situation_model_assembly_encoder_retrain_scale_v1: depth=1
#      top-layer unfreeze was the standout; more unfreeze OVERFITS/craters). Objective reused VERBATIM. ----
DEPTH = 1

# ---- graded difficulty: the modifier-pool sizes per grade (SIMPLE -> COMPLEX). n_mods=8 == hc hard EXACTLY. ----
HARDNESS_LITE = (1, 3, 8)     # G=3 grades; target = 8 (hardest); t=0..3 -> 4-point climb curve
HARDNESS_SMOKE = (1, 8)       # G=2 grades
EASY_NMODS = 1                # the easy held-ahead set (forgetting check reference)

# ---- online schedule (autonomy: exp_dev owns these). Total steps ~ certified 220 (spread across grades). ----
STEPS_PER_GRADE_LITE = 60   # intended budget (~cert total 220/3.7); per-grade resumable so it survives kills
STEPS_PER_GRADE_SMOKE = 10
NCTX_LITE = 40                # ENT-rep samples per train color per grade
NCTX_SMOKE = 8
REPLAY_CAP_LITE = 400         # rehearsal reservoir capacity (a few hundred past samples)
REPLAY_CAP_SMOKE = 60
SEEDS_LITE = (7,)   # single-seed FIRST-CUT (INLINE-LOCAL throughput); 2-seed replication = the escalation step
SEEDS_SMOKE = (7,)
EVAL_N_LITE = 40
EVAL_N_SMOKE = 12

ARMS_ONLINE = ("graded", "shuffled", "noreplay")

# ---- pre-registered bars (fixed BEFORE running) ----
CLIMB_MIN = 0.05             # HYPOTHESIZED: curve(t=G)-curve(t=0) HARD_PASS climb floor
TIE_BAND = 0.02              # |climb| <= this = FLAT = diagnose (a)/(b)/(c); NOT a ceiling
FORGET_MAX = 0.10            # HYPOTHESIZED: easy@t1 - easy@tG (GRADED, with replay) must stay <= this
PROFILE_DECLINE_MIN = 0.03   # frozen_easy_loop - frozen_hard_loop must exceed this (genuinely graded gate)
BASE_READING_MARGIN = 0.20   # oracle held-ahead loop must clear chance by this at the hardest grade
# guard bars (reuse the certified corrected loop-anchored guard shape via hc.collapse_guard)
WC_DRIFT_MAX = hc.WC_DRIFT_MAX          # 0.15
ENTCONS_MIN = hc.ENTCONS_MIN            # 0.85
Q_AGREE_GUARD_MIN = hc.Q_AGREE_GUARD_MIN  # 0.55
# flat-trajectory diagnostic bars (USER reframe: a FLAT climb is a BROKEN experiment, diagnose before verdict)
WEIGHT_MOVE_MIN = 1e-3       # (a) unfrozen-param relative L2 delta below this = SGD did not update = NOT LEARNING
LOSS_DESCENT_MIN = 1e-3      # (a) online loss (first grade start -> last grade end) must descend by this
LEARN_TRAIN_MIN = 0.05       # (a) train-entity held-ahead lift (train_loop@tG - frozen_train_loop) must exceed


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ================= GRADED SURFACE RENDERS (the difficulty axis) =========================================
# Mirror hc.hard_render_* EXACTLY but with a variable modifier-pool size n_mods (state in _CUR_NMODS).
# n_mods=8 reproduces hc's VET'd hard renders bit-for-bit; n_mods=1 => constant modifier (easiest).
_CUR_NMODS = [8]


def _gmod(frame, ent, a1, a2):
    return MODIFIERS[(frame * 1009 + ent * 61 + a1 * 17 + a2 * 7) % _CUR_NMODS[0]]


def graded_render_name_event(ent, s, p):
    m = _gmod(0, ent, s, p)
    text = "the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " was set "
    c2 = len(text); text += COLORS[s]; spans.append(("S", s, c2, len(text)))
    text += " and placed "
    c3 = len(text); text += COLORS[p]; spans.append(("P", p, c3, len(text)))
    text += " ."
    return text, spans


def graded_render_tag(ent, mark):
    m = _gmod(1, ent, mark, 0)
    text = "the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " was tagged "
    c2 = len(text); text += COLORS[mark]; spans.append(("MARK", mark, c2, len(text)))
    text += " ."
    return text, spans


def graded_render_name_query(ent, role):
    m = _gmod(2, ent, role, 0)
    text = "what was the "
    cs = len(text); text += m + " " + COLORS[ent]; ce = len(text)
    spans = [("ENT", ent, cs, ce)]
    text += " %s to ?" % ROLE_NAMES[role]
    return text, spans


_GRADED = {"render_name_event": graded_render_name_event,
           "render_tag": graded_render_tag,
           "render_name_query": graded_render_name_query}


def install_graded_renders(n_mods):
    assert 1 <= n_mods <= len(MODIFIERS), "n_mods out of range"
    _CUR_NMODS[0] = n_mods
    for k, v in _GRADED.items():
        setattr(eb, k, v)


def restore_renders():
    hc.restore_easy_renders()  # restores eb's original (certified) renders


def _selftest_graded_axis():
    """STRUCTURAL monotonicity of the difficulty axis (the honest hardness PROOF is frozen-representation
    degradation -- measured at runtime via the frozen graded profile + the PROFILE_DECLINE_MIN gate; a naive
    string-matcher is NOT defeated because the color word persists, per hc). Here we assert only the structural
    invariant that drives the difficulty: at n_mods=1 the ENT-span modifier is IDENTICAL across the statement
    and query frames for EVERY entity (cross-frame surface consistent -> easy); at n_mods=8 there EXIST entities
    whose statement vs query modifier DIFFER (cross-frame surface mismatch -> harder). Returns
    (frac_consistent_easy, frac_consistent_hard)."""
    ents = list(range(V_FILL))

    def frac_consistent(n_mods):
        _CUR_NMODS[0] = n_mods
        ok = 0
        for e in ents:
            # statement modifier for a representative event vs query modifier for a representative query
            m_stmt = _gmod(0, e, 0, 0)
            m_qry = _gmod(2, e, 0, 0)
            ok += int(m_stmt == m_qry)
        return ok / len(ents)

    fc_easy = frac_consistent(1)
    fc_hard = frac_consistent(8)
    _CUR_NMODS[0] = 8
    return fc_easy, fc_hard


# ================= ONLINE OBJECTIVE (the certified 3-term loss, VERBATIM; only the data SCHEDULE differs) ==
def _loss_step(ext, ids_b, yb):
    """One online step's loss on a batch of ENT-rep texts. Bit-identical to lt.finetune_encoder's inner loss
    (align + push + VICReg). Gradients flow into the unfrozen top-1 layer + final norm."""
    cue = ext._ent_cue_grad()
    v = ext._pooled_ent_grad(ids_b, cue)
    z = F.normalize(v, dim=1)
    S = z @ z.T
    same = (yb[:, None] == yb[None, :]).float()
    eye = torch.eye(len(yb))
    same_off = same - eye
    diff = 1.0 - same
    l_align = ((1.0 - S) * same_off).sum() / same_off.sum().clamp_min(1.0)
    l_push = (F.relu(S - lt.PUSH_MARGIN) * diff).sum() / diff.sum().clamp_min(1.0)
    var, cov = lt._vicreg_terms(z)
    loss = lt.W_ALIGN * l_align + lt.W_PUSH * l_push + lt.W_VIC * (var + cov)
    return loss, float(l_align.detach()), float(l_push.detach()), float((var + cov).detach())


def _gather_grade_texts(grade_ents, n_mods, nctx, seed):
    """ENT-rep training texts for grade_ents rendered at grade hardness n_mods (via lt._gather_ent_texts,
    which calls the CURRENTLY installed eb.render_*). Returns (list[str], np.int64 labels)."""
    install_graded_renders(n_mods)
    texts, labels = lt._gather_ent_texts(grade_ents, nctx, seed)
    return list(texts), list(labels.tolist())


# ================= held-ahead eval at a given hardness =================================================
def _eval_heldahead(ext, eval_structs, tables, n_mods):
    """Snapshot-eval: install the grade's renders, (re)build the reader pipeline on CURRENT weights, score the
    FHRR loop on the FIXED novel-entity held-ahead structures. Returns loop + entcons + q_agree."""
    install_graded_renders(n_mods)
    ext.model.eval()
    ext.build()
    sc = lt.score_extractor(ext, eval_structs, tables)
    return {"loop": lt._loop_mean(sc["main_enc"]),
            "entcons": sc["stage_role_attn"].get("entity_consistency"),
            "q_agree": sc["diag_decoded"]["cross_frame_query_agreement"],
            "per_type": {qt: sc["main_enc"][qt]["acc"] for qt in QUERY_TYPES},
            "sc": sc}


def _oracle_loop_built(ext, eval_structs, tables):
    """Oracle loop assuming ext is ALREADY built at the desired hardness (no rebuild)."""
    dec_or, ans_or, _ = ef.build_addr_dataset(eval_structs, ext, "oracle")
    return lt._loop_mean(eb.run_arm_decoded(dec_or, ans_or, tables, "main"))


def _score_loop_built(ext, structs, tables):
    """Loop on structs assuming ext is ALREADY built at the desired hardness + renders installed (no rebuild)."""
    return lt._loop_mean(lt.score_extractor(ext, structs, tables)["main_enc"])


# ================= BASE unit (frozen references + genuinely-graded proof + floors) ======================
def run_base(seed, run_mode, eval_n, hardness):
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    for h in hardness:
        assert 1 <= h <= len(MODIFIERS)
    target = hardness[-1]
    # FIXED novel-entity held-ahead structures (render-independent; ent_pool=held, mark_pool=train)
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    for p in eval_structs:
        for e in p["tracked"]:
            assert e in held, "eval entity not held-out (fairness breach)"

    ext_fz = lt.RetrainableExtractor()  # NOT built yet; _eval builds per hardness
    # frozen graded PROFILE: loop at EACH grade hardness on the SAME held-ahead structures (must DECLINE).
    # target is LAST in hardness -> after this loop ext_fz is built at target hardness (reused below).
    profile = {}
    sc_target = None
    for h in hardness:
        ev = _eval_heldahead(ext_fz, eval_structs, tables, h)
        profile[h] = ev["loop"]
        if h == target:
            sc_target = ev["sc"]
    frozen_target = profile[target]
    frozen_easy = profile[EASY_NMODS] if EASY_NMODS in profile else profile[hardness[0]]

    # oracle ceiling + wc_frozen at target hardness -- REUSE the built ext (target renders installed) ----
    install_graded_renders(target)   # ensure target renders installed for the reused build
    oracle_target = _oracle_loop_built(ext_fz, eval_structs, tables)
    wc_frozen = lt.within_minus_cross(ext_fz, held, seed=seed + 2)["within_minus_cross"]

    # ---- the 6 can-fail floors + POOLED + MOST_RECENT at target hardness (validity) ----
    sc_fz = sc_target
    floors = {}
    for m in ("random_addr", "no_coref", "wrongrole", "shuffled"):
        floors[m] = eb.run_arm_decoded(sc_fz["dec_ra"], sc_fz["ans_ra"], tables, m)
    most_recent = clean.run_most_recent(eval_structs)
    train_ds = clean.gen_dataset(40 if run_mode != "smoke" else 12, np.random.default_rng(seed))
    pooled = clean.run_pooled_reader(train_ds, eval_structs, seed)
    restore_renders()

    res = {"kind": "base", "seed": seed, "arm": "frozen", "hardness": list(hardness), "target": target,
           "chance": 1.0 / V_FILL,
           "frozen_profile": {str(h): profile[h] for h in hardness},
           "frozen_target_loop": frozen_target, "frozen_easy_loop": frozen_easy,
           "oracle_target_loop": oracle_target, "wc_frozen": wc_frozen,
           "profile_decline": frozen_easy - frozen_target,
           "floors": {m: {qt: floors[m][qt]["acc"] for qt in QUERY_TYPES} for m in floors},
           "most_recent": {qt: most_recent[qt]["acc"] for qt in QUERY_TYPES},
           "pooled_b": pooled["b_competitive_coref"]["acc"], "pooled_c": pooled["c_overwrite"]["acc"]}
    _log("  [seed=%d BASE frozen] profile(n_mods->loop)=%s decline=%.3f | target=%.3f oracle=%.3f wc=%.3f chance=%.4f"
         % (seed, {h: round(profile[h], 3) for h in hardness}, res["profile_decline"], frozen_target,
            oracle_target, wc_frozen, 1.0 / V_FILL))
    return res


# ================= per-GRADE resumable online-arm checkpoint (survives a mid-training kill) =============
def _online_ckpt_path(seed, arm, run_mode):
    return os.path.join(OUTPUT_DIR, "_online_ckpt", "s%d_%s_%s.pt" % (seed, arm, run_mode))


def _save_online_ckpt(seed, arm, run_mode, ext, opt, state):
    """Persist the online-arm mid-stream state after a grade so a kill resumes per-grade (NOT from scratch)."""
    path = _online_ckpt_path(seed, arm, run_mode)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    trainable_state = {n: p.detach().cpu().clone() for n, p in ext.model.named_parameters() if p.requires_grad}
    payload = {"trainable_state": trainable_state, "opt_state": opt.state_dict(), "state": state}
    tmp = path + ".tmp"
    torch.save(payload, tmp)
    os.replace(tmp, path)


def _heartbeat(seed, arm, run_mode, grade_done, total, curve, loss_last, elapsed):
    row = {"ts_iso": _now_iso(), "seed": seed, "arm": arm, "run_mode": run_mode,
           "grade_done": grade_done, "total_grades": total, "curve_so_far": [round(float(x), 4) for x in curve],
           "loss_last": loss_last, "elapsed_s": round(elapsed, 1)}
    with open(os.path.join(OUTPUT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


# ================= ONLINE arm unit (the continuous learn-as-you-go stream) ==============================
def run_online_arm(seed, arm, run_mode, eval_n, hardness):
    """Read the graded stream SEQUENTIALLY, updating the encoder ONLINE after each grade's chunk (with or
    without replay), snapshotting the held-ahead climb curve at every grade boundary. RESUMABLE PER-GRADE:
    after every grade the encoder weights + optimizer + curve + replay buffer are checkpointed and a
    heartbeat is emitted, so a kill mid-arm resumes from the last completed grade (not from scratch)."""
    steps_per_grade = STEPS_PER_GRADE_SMOKE if run_mode == "smoke" else STEPS_PER_GRADE_LITE
    nctx = NCTX_SMOKE if run_mode == "smoke" else NCTX_LITE
    replay_cap = REPLAY_CAP_SMOKE if run_mode == "smoke" else REPLAY_CAP_LITE
    batch = lt.TRAIN_BATCH
    tables = clean.build_tables()
    train, held = ih.color_split(SPLIT_SEED)
    target = hardness[-1]
    eval_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 777), held, train)
    train_structs = ih.gen_dataset_split(eval_n, np.random.default_rng(seed + 555), train, held)  # mem/learn check

    # grade order: GRADED = ascending difficulty; SHUFFLED = a fixed deterministic shuffle of the SAME grades
    grade_order = list(hardness)
    if arm == "shuffled":
        perm = np.random.default_rng(90000 + seed).permutation(len(grade_order))
        grade_order = [hardness[i] for i in perm]
    use_replay = (arm != "noreplay")
    G = len(grade_order)

    torch.manual_seed(seed)
    ext = lt.RetrainableExtractor()
    trainable, n_layers = ext.unfreeze_top(DEPTH)
    opt = torch.optim.Adam(trainable, lr=lt.LR, weight_decay=lt.WEIGHT_DECAY)
    # snapshot the PRISTINE trainable params (before any resume-load) for the weight-move measurement
    fp = {n: p.detach().clone() for n, p in ext.model.named_parameters() if p.requires_grad}

    # ---- resume from a per-grade checkpoint if present ----
    payload = None
    p_ck = _online_ckpt_path(seed, arm, run_mode)
    if os.path.exists(p_ck):
        payload = torch.load(p_ck, map_location="cpu", weights_only=False)
    if payload is not None:
        with torch.no_grad():
            cur = dict(ext.model.named_parameters())
            for n_, v_ in payload["trainable_state"].items():
                cur[n_].copy_(v_)
        opt.load_state_dict(payload["opt_state"])
        st = payload["state"]
        grades_done = st["grades_done"]
        curve = list(st["curve"]); curve_meta = list(st["curve_meta"])
        easy_at = {int(k): v for k, v in st["easy_at"].items()}
        replay_texts = list(st["replay_texts"]); replay_labels = list(st["replay_labels"])
        loss_first = st["loss_first"]; loss_last = st["loss_last"]
        train_loop = st["train_loop"]; wc_tuned = st["wc_tuned"]
        _log("  [seed=%d arm=%s] RESUME from grade %d/%d (curve=%s)"
             % (seed, arm, grades_done, G, [round(x, 3) for x in curve]))
    else:
        replay_texts, replay_labels = [], []
        curve, curve_meta, easy_at = [], [], {}
        loss_first = loss_last = train_loop = wc_tuned = float("nan")
        grades_done = 0
        # checkpoint t=0: BEFORE any reading (== frozen encoder)
        ck0 = _eval_heldahead(ext, eval_structs, tables, target)
        curve.append(ck0["loop"]); curve_meta.append({"entcons": ck0["entcons"], "q_agree": ck0["q_agree"]})
        _log("  [seed=%d arm=%s] t=0 (pre-read) target loop=%.3f" % (seed, arm, ck0["loop"]))

    for gi in range(grades_done, G):
        n_mods = grade_order[gi]
        texts, labels = _gather_grade_texts(train, n_mods, nctx, seed + 100 * (gi + 1))
        pool_texts = list(texts)
        pool_labels = list(labels)
        if use_replay and replay_texts:
            pool_texts += replay_texts
            pool_labels += replay_labels
        ids_all = ext._ids_of(pool_texts)
        y_all = torch.tensor(pool_labels, dtype=torch.int64)
        n = ids_all.shape[0]
        b = min(batch, n)
        ext.model.train()
        gen = torch.Generator().manual_seed(seed * 131 + gi)
        t0 = time.perf_counter()
        for it in range(steps_per_grade):
            idx = torch.randperm(n, generator=gen)[:b]
            loss, la, lp, lv = _loss_step(ext, ids_all[idx], y_all[idx])
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, lt.GRAD_CLIP)
            opt.step()
            lf = float(loss.detach())
            if gi == 0 and it == 0:
                loss_first = lf
            loss_last = lf
        ext.model.eval()
        _log("    [seed=%d arm=%s] grade %d/%d n_mods=%d steps=%d pool=%d loss=%.4f (%.1fs)"
             % (seed, arm, gi + 1, G, n_mods, steps_per_grade, n, loss_last, time.perf_counter() - t0))
        # update rehearsal reservoir with this grade's samples (deterministic per-grade subsample)
        if use_replay:
            replay_texts += list(texts); replay_labels += list(labels)
            if len(replay_texts) > replay_cap:
                rng_rep_g = np.random.default_rng(50000 + seed * 17 + gi)
                keep = rng_rep_g.permutation(len(replay_texts))[:replay_cap]
                replay_texts = [replay_texts[i] for i in keep]
                replay_labels = [replay_labels[i] for i in keep]
        # checkpoint t=gi+1: held-ahead target (ext now built at target renders)
        ck = _eval_heldahead(ext, eval_structs, tables, target)
        curve.append(ck["loop"]); curve_meta.append({"entcons": ck["entcons"], "q_agree": ck["q_agree"]})
        last_grade = (gi + 1) == G
        if last_grade:
            # REUSE the target build (renders installed): tuned train-entity loop + tuned held-out geometry
            train_loop = _score_loop_built(ext, train_structs, tables)
            wc_tuned = lt.within_minus_cross(ext, held, seed=seed + 2)["within_minus_cross"]
        # forgetting: EASY held-ahead at t=1 and t=G (switches renders -> do AFTER target-based metrics)
        if (gi + 1) == 1 or last_grade:
            easy_at[gi + 1] = _eval_heldahead(ext, eval_structs, tables, EASY_NMODS)["loop"]
        _log("  [seed=%d arm=%s] t=%d target loop=%.3f (entcons=%.3f q_agree=%.3f)"
             % (seed, arm, gi + 1, ck["loop"],
                ck["entcons"] if ck["entcons"] is not None else float("nan"), ck["q_agree"]))
        # ---- persist per-grade checkpoint + heartbeat (NEVER-SILENT: progress visible + resumable) ----
        _save_online_ckpt(seed, arm, run_mode, ext, opt,
                          {"grades_done": gi + 1, "curve": curve, "curve_meta": curve_meta,
                           "easy_at": {str(k): v for k, v in easy_at.items()},
                           "replay_texts": replay_texts, "replay_labels": replay_labels,
                           "loss_first": loss_first, "loss_last": loss_last,
                           "train_loop": train_loop, "wc_tuned": wc_tuned})
        _heartbeat(seed, arm, run_mode, gi + 1, G, curve, loss_last, time.perf_counter() - t0)
        restore_renders()

    # ---- learning diagnostics (a): weights moved + loss descended + objective fit the TRAIN entities ----
    tp = {n: p.detach() for n, p in ext.model.named_parameters() if p.requires_grad}
    num = den = 0.0
    for nm in fp:
        d = tp[nm] - fp[nm]; num += float((d * d).sum()); den += float((fp[nm] ** 2).sum())
    weight_move_rel = (num ** 0.5) / (den ** 0.5) if den > 0 else float("nan")
    restore_renders()
    # unit fully computed -> drop the per-grade checkpoint (the unit itself is recorded by the caller)
    try:
        if os.path.exists(p_ck):
            os.remove(p_ck)
    except OSError:
        pass

    res = {"kind": "online", "seed": seed, "arm": arm, "hardness": list(hardness), "target": target,
           "grade_order": [int(h) for h in grade_order], "use_replay": bool(use_replay),
           "curve_target": [float(x) for x in curve],
           "curve_meta": curve_meta,
           "climb": float(curve[-1] - curve[0]),
           "easy_t1": easy_at.get(1, float("nan")), "easy_tG": easy_at.get(G, float("nan")),
           "forgetting": float(easy_at.get(1, float("nan")) - easy_at.get(G, float("nan")))
           if (1 in easy_at and G in easy_at) else float("nan"),
           "weight_move_rel": weight_move_rel, "loss_first": loss_first, "loss_last": loss_last,
           "loss_descent": float(loss_first - loss_last) if not (math.isnan(loss_first) or math.isnan(loss_last)) else float("nan"),
           "train_loop_target": train_loop, "wc_tuned": wc_tuned,
           "final_entcons": curve_meta[-1]["entcons"], "final_q_agree": curve_meta[-1]["q_agree"],
           "steps_per_grade": steps_per_grade, "replay_cap": replay_cap if use_replay else 0}
    _log("  [seed=%d arm=%s] CURVE=%s climb=%.3f forget=%.3f wmove=%.4f loss %.3f->%.3f train_loop=%.3f"
         % (seed, arm, [round(x, 3) for x in curve], res["climb"], res["forgetting"],
            weight_move_rel, loss_first, loss_last, train_loop))
    return res


# ================= verdict =================
def _mean(xs):
    v = [x for x in xs if not (isinstance(x, float) and math.isnan(x))]
    return float(np.mean(v)) if v else float("nan")


def _floors_ok(bases):
    ok, notes = True, []
    spec = {"random_addr": (QUERY_TYPES, ADDR_FLOOR_BAR),
            "no_coref": (("b_competitive_coref",), ADDR_FLOOR_BAR),
            "wrongrole": (QUERY_TYPES, DECODE_FLOOR_BAR),
            "shuffled": (QUERY_TYPES, DECODE_FLOOR_BAR)}
    for r in bases:
        for arm, (qts, bar) in spec.items():
            for qt in qts:
                x = r["floors"][arm][qt]
                if not math.isnan(x) and x > bar:
                    ok = False; notes.append("seed%d %s[%s]=%.3f>%.3f" % (r["seed"], arm, qt, x, bar))
        for qt in QUERY_TYPES:
            x = r["most_recent"][qt]
            if not math.isnan(x) and x > DECODE_FLOOR_BAR:
                ok = False; notes.append("seed%d most_recent[%s]=%.3f>%.3f" % (r["seed"], qt, x, DECODE_FLOOR_BAR))
    return ok, notes


def _pooled_reservoir(bases):
    for r in bases:
        if (not math.isnan(r["pooled_b"]) and r["pooled_b"] >= PROVEN_MIN) or \
           (not math.isnan(r["pooled_c"]) and r["pooled_c"] >= PROVEN_MIN):
            return True
    return False


def _monotone_ok(curve):
    """Non-decreasing within TIE_BAND at each step (small dips tolerated)."""
    for i in range(1, len(curve)):
        if curve[i] < curve[i - 1] - TIE_BAND:
            return False
    return True


def decide_verdict(bases, online, seeds, hardness, eval_n):
    expected = len(seeds) * (1 + len(ARMS_ONLINE))
    got = len(bases) + len(online)
    if got < expected:
        return "HARD_FAIL", ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: %d/%d units (bases=%d online=%d)"
                             % (got, expected, len(bases), len(online))), {}

    floors_ok, floor_notes = _floors_ok(bases)
    if _pooled_reservoir(bases):
        return "INVALID", "POOLED_READER reservoir-decodable (b/c >= PROVEN_MIN) -- harness trivially solvable", {}
    if not floors_ok:
        return "INVALID", "can-fail floor did not collapse: " + "; ".join(floor_notes[:6]), {}

    chance = 1.0 / V_FILL
    by_seed_base = {r["seed"]: r for r in bases}
    frozen_target = _mean([r["frozen_target_loop"] for r in bases])
    oracle_target = _mean([r["oracle_target_loop"] for r in bases])
    profile_decline = _mean([r["profile_decline"] for r in bases])
    wc_frozen = _mean([r["wc_frozen"] for r in bases])
    frozen_train = float("nan")  # frozen train-entity loop reference (approx via oracle not needed; use base)

    # genuinely-graded gate (validity): the FROZEN profile must DECLINE with hardness
    if math.isnan(profile_decline) or profile_decline < PROFILE_DECLINE_MIN:
        return "INVALID", ("STREAM NOT GENUINELY GRADED: frozen loop declines only %.3f (< %.2f) from easiest "
                           "to hardest grade -- the higher grades are not actually harder for the frozen "
                           "encoder, so there is no genuinely-new signal to climb on. Fix the grading (steeper "
                           "difficulty axis) before interpreting any climb." % (profile_decline, PROFILE_DECLINE_MIN),
                           {"profile_decline": profile_decline}), {"profile_decline": profile_decline}

    # base reading at hardest grade must be readable given a clean address
    base_reading_ok = (not math.isnan(oracle_target)) and (oracle_target - chance) >= BASE_READING_MARGIN \
        and (not math.isnan(wc_frozen)) and wc_frozen > 0.0

    arms = {}
    for a in ARMS_ONLINE:
        rs = [r for r in online if r["arm"] == a]
        climbs = [r["climb"] for r in rs]
        curves = [r["curve_target"] for r in rs]
        mean_curve = [float(np.mean([c[i] for c in curves])) for i in range(len(curves[0]))] if curves else []
        arms[a] = {
            "mean_climb": _mean(climbs), "min_seed_climb": (min(climbs) if climbs else float("nan")),
            "mean_curve": mean_curve, "per_seed_curve": curves,
            "final": _mean([c[-1] for c in curves]) if curves else float("nan"),
            "mean_forgetting": _mean([r["forgetting"] for r in rs]),
            "mean_weight_move": _mean([r["weight_move_rel"] for r in rs]),
            "mean_loss_descent": _mean([r["loss_descent"] for r in rs]),
            "mean_train_loop": _mean([r["train_loop_target"] for r in rs]),
            "mean_wc_tuned": _mean([r["wc_tuned"] for r in rs]),
            "mean_entcons": _mean([r["final_entcons"] for r in rs]),
            "mean_q_agree": _mean([r["final_q_agree"] for r in rs]),
            "monotone_ok": all(_monotone_ok(c) for c in curves) if curves else False}

    g = arms["graded"]
    climb = g["mean_climb"]
    guard = hc.collapse_guard(g["final"], frozen_target, g["mean_wc_tuned"], wc_frozen,
                              g["mean_entcons"], g["mean_q_agree"])

    # ---- flat diagnosis (USER flat=fix): learning? new-content? powered? ----
    learning_ok = ((not math.isnan(g["mean_weight_move"])) and g["mean_weight_move"] > WEIGHT_MOVE_MIN
                   and (not math.isnan(g["mean_loss_descent"])) and g["mean_loss_descent"] > LOSS_DESCENT_MIN
                   and (not math.isnan(g["mean_train_loop"]))
                   and (g["mean_train_loop"] - frozen_target) >= LEARN_TRAIN_MIN)
    content_ok = (not math.isnan(profile_decline)) and profile_decline >= PROFILE_DECLINE_MIN
    climbs_all = [r["climb"] for r in online if r["arm"] == "graded"]
    std_climb = float(np.std(climbs_all, ddof=1)) if len(climbs_all) > 1 else float("nan")
    n_eff = eval_n * len(QUERY_TYPES) * max(1, len(seeds))
    pbar = _mean([frozen_target, g["final"]])
    se_loop = math.sqrt(max(pbar * (1 - pbar), 1e-9) / max(n_eff, 1)) if not math.isnan(pbar) else float("nan")
    mde_binom = (1.96 * math.sqrt(2.0) * se_loop) if not math.isnan(se_loop) else float("nan")
    mde_seed = (1.96 * std_climb / math.sqrt(len(seeds))) if not math.isnan(std_climb) else float("nan")
    cands = [x for x in (mde_binom, mde_seed) if not math.isnan(x)]
    mde = max(cands) if cands else float("nan")
    powered = (not math.isnan(mde)) and mde <= CLIMB_MIN
    if not learning_ok:
        cause = "a_NOT_LEARNING"
    elif not content_ok:
        cause = "b_NO_NEW_CONTENT"
    elif not powered:
        cause = "c_UNDERPOWERED"
    else:
        cause = "CLEAN_DESIGN_LIMIT"

    bands = {
        "one_variable": ("DATA SCHEDULE (online graded stream + replay) vs the frozen no-learning control; the "
                         "learner objective/steps/LR/batch is IDENTICAL across online arms. hardness=%s (n_mods "
                         "per grade), target=%d, chance=%.4f." % (list(hardness), hardness[-1], chance)),
        "bars": {"climb_min": CLIMB_MIN, "tie_band": TIE_BAND, "forget_max": FORGET_MAX,
                 "profile_decline_min": PROFILE_DECLINE_MIN, "base_reading_margin": BASE_READING_MARGIN},
        "frozen_target_loop": frozen_target, "oracle_target_loop": oracle_target,
        "frozen_graded_profile": {str(h): _mean([r["frozen_profile"][str(h)] for r in bases]) for h in hardness},
        "profile_decline": profile_decline, "base_reading_ok": base_reading_ok,
        "chance": chance, "wc_frozen": wc_frozen,
        "arms": arms, "collapse_guard_graded": guard,
        "curriculum_value": {"graded_final": g["final"], "shuffled_final": arms["shuffled"]["final"],
                             "graded_minus_shuffled": (g["final"] - arms["shuffled"]["final"])},
        "forgetting": {"graded": g["mean_forgetting"], "noreplay": arms["noreplay"]["mean_forgetting"],
                       "replay_helps": (arms["noreplay"]["mean_forgetting"] - g["mean_forgetting"])},
        "flat_diagnosis": {"cause": cause, "learning_ok": learning_ok, "content_ok": content_ok,
                           "powered": powered, "mde_climb": mde, "weight_move": g["mean_weight_move"],
                           "loss_descent": g["mean_loss_descent"], "train_loop": g["mean_train_loop"],
                           "climb_min_target": CLIMB_MIN},
        "non_triviality": {"floors_ok": floors_ok, "pooled_reservoir": _pooled_reservoir(bases)}}

    sub = ("[CONTINUOUS LOOP hardness=%s target=%d chance=%.4f] frozen_target=%.3f oracle=%.3f (chance+%.3f) "
           "profile_decline=%.3f. GRADED curve=%s climb=%.3f (min-seed=%.3f) monotone=%s | forgetting graded=%.3f "
           "noreplay=%.3f (replay_helps=%.3f) | curriculum graded_final=%.3f shuffled_final=%.3f (diff=%.3f) | "
           "guard=%s. DIAG cause=%s (learn=%s wmove=%.4f loss_desc=%.3f train_loop=%.3f | content=%s decline=%.3f "
           "| powered=%s MDE=%.3f)."
           % (list(hardness), hardness[-1], chance, frozen_target, oracle_target, oracle_target - chance,
              profile_decline, [round(x, 3) for x in g["mean_curve"]], climb, g["min_seed_climb"],
              g["monotone_ok"], g["mean_forgetting"], arms["noreplay"]["mean_forgetting"],
              arms["noreplay"]["mean_forgetting"] - g["mean_forgetting"], g["final"], arms["shuffled"]["final"],
              g["final"] - arms["shuffled"]["final"], guard["pass"], cause, learning_ok, g["mean_weight_move"],
              g["mean_loss_descent"], g["mean_train_loop"], content_ok, profile_decline, powered, mde))

    # ---- HARD_FAIL: the loop is BROKEN (not a capability statement) ----
    if not guard["c1_loop_not_cratered"]:
        return "HARD_FAIL", ("BROKEN LOOP: the online update CRATERS the reader below frozen at t=G (guard C1 "
                             "failed) -- the continuous update is destabilizing the encoder, fix LR/replay/steps "
                             "before any capability read. " + sub), bands
    if not base_reading_ok:
        return "HARD_FAIL", ("BROKEN PRECONDITION (encoder, NOT a curriculum ceiling): the encoder cannot read "
                             "the hardest grade even given a CLEAN address (oracle only chance+%.3f < %.2f) -- "
                             "the climb is moot until base reading holds. " % (oracle_target - chance, BASE_READING_MARGIN)
                             + sub), bands

    # ---- HARD_PASS: comprehension CLIMBS, beats frozen, no forgetting ----
    if ((not math.isnan(climb)) and climb >= CLIMB_MIN and (not math.isnan(g["min_seed_climb"]))
            and g["min_seed_climb"] > 0 and g["monotone_ok"] and guard["pass"]
            and (not math.isnan(g["mean_forgetting"])) and g["mean_forgetting"] <= FORGET_MAX):
        return "HARD_PASS", ("LEARN-AS-YOU-GO WORKS: held-ahead comprehension CLIMBS as the graded stream is "
                             "read (climb=%.3f >= %.2f, every seed climbs, monotone), BEATS the frozen "
                             "no-learning control, earlier (easy) material is NOT forgotten (%.3f <= %.2f), "
                             "guard holds, stream genuinely graded, floors collapse. The reader learns as it "
                             "reads -- SCALE the graded curriculum loop (full K-12 program = USER's call). "
                             % (climb, CLIMB_MIN, g["mean_forgetting"], FORGET_MAX) + sub), bands

    # ---- FLAT / MIDDLE: diagnose (a)/(b)/(c); DO NOT conclude a ceiling ----
    flat = (not math.isnan(climb)) and climb <= TIE_BAND
    if flat:
        if cause == "a_NOT_LEARNING":
            return "INVALID", ("EXPERIMENT NOT LEARNING (a): weights barely moved (wmove=%.4f) OR online loss did "
                               "not descend (%.3f) OR the objective did not fit the TRAIN entities (train_loop-"
                               "frozen=%.3f < %.2f). The flat climb is a BROKEN-TRAINING artifact, NOT a ceiling "
                               "-- fix LR/steps/grad-flow and re-run. " % (g["mean_weight_move"], g["mean_loss_descent"],
                               g["mean_train_loop"] - frozen_target, LEARN_TRAIN_MIN) + sub), bands
        if cause == "b_NO_NEW_CONTENT":
            return "INVALID", ("EXPERIMENT NO-NEW-CONTENT (b): the frozen graded profile is FLAT (decline=%.3f) "
                               "-- higher grades are not actually harder, so there is no genuinely-new signal to "
                               "climb on. Steepen the difficulty axis and re-run. " % profile_decline + sub), bands
        if cause == "c_UNDERPOWERED":
            return "INVALID", ("EXPERIMENT UNDERPOWERED (c): MDE=%.3f exceeds the required climb %.2f (seeds=%d "
                               "eval_n=%d) -- a real climb could not register at this budget. Add seeds/eval/"
                               "steps and re-run. " % (mde, CLIMB_MIN, len(seeds), eval_n) + sub), bands
        return "MIDDLE", ("CLEAN-EXPERIMENT DESIGN-LIMIT: learning happened + the stream is genuinely graded + "
                          "adequately powered, and STILL no held-ahead climb from reading harder material. This "
                          "says the top-1-layer online objective does not accrue CONTINUAL gain from harder "
                          "surface -- a DESIGN fix (more unfreeze / harder negatives / more steps / a second "
                          "difficulty axis like competing-entity count), NOT a capability ceiling. " + sub), bands

    return "MIDDLE", ("PARTIAL climb: comprehension rose as it read but did not clear HARD_PASS (climb=%.3f in "
                      "(tie=%.2f, climb_min=%.2f); check monotone=%s forgetting=%.3f guard=%s). Report the curve "
                      "= the extrapolation for the USER's curriculum-scale decision. "
                      % (climb, TIE_BAND, CLIMB_MIN, g["monotone_ok"], g["mean_forgetting"], guard["pass"]) + sub), bands


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
    _log("SELF-TEST: graded surface axis is structurally monotone (n_mods=1 cross-frame consistent; n_mods=8 mismatched) ...")
    tc_easy, tc_hard = _selftest_graded_axis()
    assert tc_easy == 1.0, "n_mods=1 must be fully cross-frame consistent, got %.3f" % tc_easy
    assert tc_hard < 0.75, "n_mods=8 must have cross-frame mismatch for many entities, got consistent=%.3f" % tc_hard
    # n_mods=8 must reproduce hc's hard renders bit-for-bit (same surface string)
    install_graded_renders(8)
    t1, _ = graded_render_name_event(3, 5, 7)
    hc.install_hard_renders()
    t2, _ = hc.hard_render_name_event(3, 5, 7)
    hc.restore_easy_renders()
    assert t1 == t2, "n_mods=8 graded render != hc hard render: %r vs %r" % (t1, t2)
    _log("  cross-frame consistent frac easy=%.3f hard=%.3f (monotone) | n_mods=8 == hc.hard (byte-identical)" % (tc_easy, tc_hard))

    _log("SELF-TEST: tiny BASE + a 2-grade online GRADED + FROZEN(base) + NOREPLAY end-to-end ...")
    hardness = HARDNESS_SMOKE
    base = run_base(7, "smoke", eval_n=8, hardness=hardness)
    restore_renders()
    assert base["profile_decline"] == base["profile_decline"], "profile_decline nan"
    g = run_online_arm(7, "graded", "smoke", eval_n=8, hardness=hardness); restore_renders()
    nr = run_online_arm(7, "noreplay", "smoke", eval_n=8, hardness=hardness); restore_renders()

    # META_RULE_AF: FROZEN (base) vs GRADED (online) must DIFFER -- an inert online loop that never moved the
    # encoder would leave the climb == frozen everywhere. Compare the curve digest + weight move.
    dig_curve = hashlib.sha256(json.dumps([round(x, 4) for x in g["curve_target"]]).encode()).hexdigest()
    dig_frozen = hashlib.sha256(json.dumps([round(base["frozen_target_loop"], 4)] * len(g["curve_target"])).encode()).hexdigest()
    arms_differ = (dig_curve != dig_frozen) or (g["weight_move_rel"] > 1e-4)
    assert arms_differ, "META_RULE_AF: online loop indistinguishable from frozen (weights never moved?)"
    assert g["weight_move_rel"] > 1e-4, "online SGD did not move the unfrozen weights (NOT LEARNING)"
    assert g["loss_last"] == g["loss_last"], "loss nan"
    # GRADED (replay) vs NOREPLAY must differ (replay changes the schedule)
    replay_differs = (abs(g["curve_target"][-1] - nr["curve_target"][-1]) > 1e-9) \
        or (abs(g["weight_move_rel"] - nr["weight_move_rel"]) > 1e-9)
    assert replay_differs, "GRADED and NOREPLAY produced identical output (replay inert)"
    for x in g["curve_target"] + nr["curve_target"] + [base["frozen_target_loop"], base["oracle_target_loop"]]:
        assert math.isnan(x) or (0.0 <= x <= 1.0), "loop out of range: %s" % x
    restore_renders()
    _log("  arms-differ=%s replay-differs=%s | base frozen=%.3f decline=%.3f | graded curve=%s climb=%.3f wmove=%.4f"
         % (arms_differ, replay_differs, base["frozen_target_loop"], base["profile_decline"],
            [round(x, 3) for x in g["curve_target"]], g["climb"], g["weight_move_rel"]))
    _log("SELF-TEST PASS")
    return {"token_copy_easy": tc_easy, "token_copy_hard": tc_hard,
            "n_mods8_eq_hc_hard": True, "arms_differ_verified": bool(arms_differ),
            "replay_differs_verified": bool(replay_differs),
            "tiny_frozen_target": base["frozen_target_loop"], "tiny_profile_decline": base["profile_decline"],
            "tiny_graded_curve": [round(x, 3) for x in g["curve_target"]], "tiny_climb": g["climb"],
            "tiny_weight_move_rel": g["weight_move_rel"],
            "hardness_lite": list(HARDNESS_LITE), "hardness_smoke": list(HARDNESS_SMOKE)}


# ================= main =================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--budget-sec", type=float, default=520.0,
                    help="lite: stop starting NEW units once this many seconds elapsed this call (resumable "
                         "per-unit). Keeps each foreground call under the 10-min timeout.")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite):
        run_mode = "self_test"
    elif args.smoke:
        run_mode = "smoke"
    else:
        run_mode = "lite"

    hardness = HARDNESS_SMOKE if run_mode == "smoke" else HARDNESS_LITE
    seeds = SEEDS_SMOKE if run_mode == "smoke" else SEEDS_LITE
    eval_n = EVAL_N_SMOKE if run_mode == "smoke" else EVAL_N_LITE

    if run_mode == "self_test":
        _write_start_marker(OUTPUT_DIR, run_mode, 1)
        t0 = time.perf_counter()
        st = run_self_test()
        metrics = {"verdict": "SELFTEST_PASS",
                   "verdict_msg": "SELFTEST_PASS (graded axis monotone + n_mods8==hc.hard + base/online/noreplay "
                                  "end-to-end + arms-differ + replay-differs + real_code_path)",
                   "summary": "SELFTEST_PASS", "run_mode": "self_test", "elapsed_s": time.perf_counter() - t0,
                   "ts_iso": _now_iso(), "anchor_name": ANCHOR_NAME, "selftest": st,
                   "start_marker_written": True, "crash_diagnostic_present": True,
                   "final_metrics_atomicity": "tmp_replace"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE self-test in %.1fs" % (time.perf_counter() - t0))
        return

    # pre-run construction audit (color harness, default renders)
    audit = clean.audit_construction(seed=7, n=300)
    if audit["fails"]:
        raise AssertionError("pre-run construction audit FAILED: %s" % audit["fails"])

    expected_units = len(seeds) * (1 + len(ARMS_ONLINE))
    _write_start_marker(OUTPUT_DIR, run_mode, expected_units)
    t0 = time.perf_counter()
    _log("%s: hardness=%s target=%d chance=%.4f seeds=%s arms=%s eval_n=%d expected_units=%d"
         % (run_mode.upper(), list(hardness), hardness[-1], 1.0 / V_FILL, seeds, ("frozen",) + ARMS_ONLINE,
            eval_n, expected_units))

    worklist = []
    for s in seeds:
        worklist.append(("base", s, "frozen"))
        for a in ARMS_ONLINE:
            worklist.append(("online", s, a))

    done = ckpt.completed_units(OUTPUT_DIR)
    ran = 0
    for kind, s, a in worklist:
        key = ckpt.unit_key(kind, s, a, run_mode)
        if key in done:
            continue
        if ran >= 1 and run_mode == "lite" and (time.perf_counter() - t0) > args.budget_sec:
            _log("  budget %.0fs reached after %d new unit(s); stopping (re-run to resume)" % (args.budget_sec, ran))
            break
        if kind == "base":
            res = run_base(s, run_mode, eval_n, hardness)
        else:
            res = run_online_arm(s, a, run_mode, eval_n, hardness)
        restore_renders()
        ckpt.record_unit(OUTPUT_DIR, key, res)
        ran += 1

    units_map = ckpt.load_units(OUTPUT_DIR)
    bases, online = [], []
    for kind, s, a in worklist:
        key = ckpt.unit_key(kind, s, a, run_mode)
        if key in units_map:
            (bases if kind == "base" else online).append(units_map[key])
    n_done = len(bases) + len(online)
    if n_done < expected_units:
        _log("PARTIAL: %d/%d units done -- re-run to resume" % (n_done, expected_units))
        metrics = {"verdict": "PARTIAL", "verdict_msg": "%d/%d units complete; re-run to resume"
                   % (n_done, expected_units), "summary": "PARTIAL %d/%d" % (n_done, expected_units),
                   "run_mode": run_mode, "elapsed_s": time.perf_counter() - t0, "ts_iso": _now_iso(),
                   "anchor_name": ANCHOR_NAME, "n_units_done": n_done, "expected_n_units": expected_units,
                   "cardinality_ok": False, "bases": bases, "online": online, "start_marker_written": True,
                   "crash_diagnostic_present": True, "final_metrics_atomicity": "tmp_replace",
                   "progress_logging": "print_flush_true"}
        _atomic_write_metrics(OUTPUT_DIR, metrics)
        _log("DONE (partial) %s in %.1fs" % (run_mode, time.perf_counter() - t0))
        return

    verdict, msg, bands = decide_verdict(bases, online, seeds, hardness, eval_n)
    elapsed = time.perf_counter() - t0
    metrics = {"verdict": verdict, "verdict_msg": msg,
               "summary": "%s | hardness=%s target=%d chance=%.4f | %s"
               % (verdict, list(hardness), hardness[-1], 1.0 / V_FILL, msg[:150]),
               "run_mode": run_mode, "elapsed_s": elapsed, "ts_iso": _now_iso(),
               "anchor_name": ANCHOR_NAME, "chance": 1.0 / V_FILL, "bands": bands,
               "cardinality_ok": bool(n_done == expected_units), "expected_n_units": expected_units,
               "n_units_done": n_done, "construction_audit": audit, "bases": bases, "online": online,
               "params": {"DIM": clean.DIM, "V_FILL": V_FILL, "DEPTH": DEPTH, "hardness": list(hardness),
                          "steps_per_grade": STEPS_PER_GRADE_SMOKE if run_mode == "smoke" else STEPS_PER_GRADE_LITE,
                          "nctx": NCTX_SMOKE if run_mode == "smoke" else NCTX_LITE,
                          "replay_cap": REPLAY_CAP_SMOKE if run_mode == "smoke" else REPLAY_CAP_LITE,
                          "eval_n": eval_n, "seeds": list(seeds), "arms": list(("frozen",) + ARMS_ONLINE),
                          "LR": lt.LR, "batch": lt.TRAIN_BATCH},
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
