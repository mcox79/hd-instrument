# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): FULL/RANDOM/NO_EFF/NO_VAL/SHUFFLED theta hashes
#   asserted pairwise distinct in self_test.
# - final_metrics_atomicity: tmp_replace.
# - except SystemExit: raised BEFORE except Exception (no BaseException swallow).
# - crlb: n/a -- no swept capacity claim; grounded feature code far below FHRR capacity at N=256.
# - baseline_in_band: RANDOM is the must-FAIL floor (~1/N_CAND); SHUFFLED must fail; mechanism arm=FULL.
# - discriminator survives scale: smoke reduced-episode FULL-vs-{RANDOM,SHUFFLED} gap; FULL run full episodes.
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY if fewer landed.
# - calibration_check: default_ok_for_this_regime (bands from chance 1/N_CAND + structural, set in prereg
#   BEFORE running, not tuned).
# - deterministic_seeding: torch.Generator per seed; sorted(set()) pools; OMP/OPENBLAS/MKL=1; no hash()-seed.
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py); start_marker + crash_diag present.
# - all reported numbers MEASURED@ tagged in the completion report, not this file.
"""Grounded causal-COHERENCE SELECTION, then TEXT TRANSFER.

Re-earns causal-coherence selection (pick the candidate whose grounded EFFECT matches the OUTCOME) over a
GROUNDED representation SHARED with how text events are encoded, fixing the CANNOT_BRIDGE negative of
exp_coherence_selector_text_transfer_v1 (0.4286, selector over an arbitrary sim permutation + char-trigram
text). Grounded code = valence (appraisal dim, resolve_valence_blind) x effect-match (situation-model
relational overlap, normalize_tokens) x outcome-valence, on the FHRR binding organ reused from
exp_grounded_appraisal_sim_earned_v1. Brain: hippocampal relational retrieval / reverse-replay over a
grounded semantic code. The sim is a NAMED SUBSTITUTE for embodied experience; sim->text transfer is TESTED.
Prereg: preregs/2026-08-04_grounded_coherence_selector_v1.md. Local-only: no queue/remote/push."""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "grounded_coherence_selector_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED VERBATIM: FHRR binding organ (project-native, NOT borrowed) ----------------------
from hdlab.binding import bind  # noqa: E402
from hdlab.bundling import bundle  # noqa: E402
# ---- REUSED VERBATIM: grounded appraisal representation building blocks -----------------------
from exp_grounded_appraisal_sim_earned_v1 import rand_fhrr, to_real_feat  # noqa: E402
# ---- REUSED VERBATIM: blind valence lexicon (appraisal dim for text) --------------------------
from exp_grounded_structure_phase0_probe_v1 import resolve_valence_blind  # noqa: E402
# ---- REUSED VERBATIM: situation-model relational tokenizer (effect-match for text) ------------
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
# ---- REUSED VERBATIM: the vetted 7-item loader + contamination guard --------------------------
from exp_coherence_selector_text_transfer_v1 import (  # noqa: E402
    load_items, mech_inputs, TRUE_SLOT,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ----------------------------------------------------------------------------- config
N_DIM = 256
N_CAND = 3          # sim candidates; text uses 2
K_EFF = 4           # quantized effect-match bins {0..3}, shared sim<->text
DTYPE = torch.complex64
SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
LR = 0.10
EPS_START = 0.30
EPS_FLOOR = 0.05
ARMS = ("FULL", "RANDOM", "NO_EFF", "NO_VAL", "SHUFFLED")

FULL_CFG = {"n_train": 8000, "n_eval": 1500}
SMOKE_CFG = {"n_train": 1200, "n_eval": 400}

VAL_KEYS = ("HARM", "NEUTRAL", "HELP")
OVAL_KEYS = ("NEG", "POS")
# valence causally consistent with each outcome sign (the causal law the learner must EARN).
CONSISTENT_VAL = {"NEG": "HARM", "POS": "HELP"}
INCONSISTENT_VAL = {"NEG": "HELP", "POS": "HARM"}


# ----------------------------------------------------------------------------- grounded codebook
class Codebook:
    """Fixed random FHRR atoms for the grounded appraisal/relational code (per-seed generator)."""

    def __init__(self, gen: torch.Generator):
        self.R_VAL = rand_fhrr(gen)
        self.R_EFF = rand_fhrr(gen)
        self.R_OUTVAL = rand_fhrr(gen)
        self.R_REC = rand_fhrr(gen)
        self.R_VXO = rand_fhrr(gen)   # role for the valence x outcome interaction (conjunctive coding)
        self.VAL = {k: rand_fhrr(gen) for k in VAL_KEYS}
        self.EFF = {b: rand_fhrr(gen) for b in range(K_EFF)}
        self.OUTVAL = {k: rand_fhrr(gen) for k in OVAL_KEYS}
        self.REC = {0: rand_fhrr(gen), 1: rand_fhrr(gen)}


# ----------------------------------------------------------------------------- grounded feature encoder
def phi(cb: Codebook, oval: str, val: str, eff_bin: int, rec: int, variant: str) -> torch.Tensor:
    """Encode (outcome, candidate) grounded features -> real feature vector under the arm's info set.
    FULL: valence + effect + outcome-valence + recency + valence x outcome interaction.
    NO_EFF: drops the effect-match dim. NO_VAL: drops valence + the interaction dim."""
    comps = [bind(cb.R_OUTVAL, cb.OUTVAL[oval]), bind(cb.R_REC, cb.REC[rec])]
    if variant != "NO_VAL":
        comps.append(bind(cb.R_VAL, cb.VAL[val]))
        comps.append(bind(cb.R_VXO, bind(cb.VAL[val], cb.OUTVAL[oval])))
    if variant != "NO_EFF":
        comps.append(bind(cb.R_EFF, cb.EFF[eff_bin]))
    v = bundle(torch.stack(comps)) if len(comps) > 1 else comps[0]
    return to_real_feat(v)


# ----------------------------------------------------------------------------- world / episodes
def make_episode(gen: torch.Generator, shuffle_labels: bool = False):
    """One grounded coherence-selection episode. The TRUE cause is valence-consistent with the outcome AND
    highest effect-match. Distractor A shares valence (consistent, low eff). Distractor B shares eff (high
    eff, inconsistent valence). Neither valence-alone nor eff-alone suffices -> conjunction must be learned.
    Recency assigned to a random slot, decorrelated from the true cause.
    shuffle_labels: decouple the true-cause label from the features (SHUFFLED floor)."""
    oval = OVAL_KEYS[int(torch.randint(0, 2, (1,), generator=gen).item())]
    hi = K_EFF - 1
    lo = int(torch.randint(0, 2, (1,), generator=gen).item())  # low eff bin in {0,1}
    # three candidate feature-profiles (before slot assignment)
    true_prof = {"val": CONSISTENT_VAL[oval], "eff": hi}
    dist_val = {"val": CONSISTENT_VAL[oval], "eff": lo}                 # shares valence
    dist_eff = {"val": INCONSISTENT_VAL[oval], "eff": hi}              # shares eff-match
    profiles = [true_prof, dist_val, dist_eff]
    true_local = 0
    # assign the 3 profiles to N_CAND slots (N_CAND==3): random permutation
    perm = torch.randperm(N_CAND, generator=gen).tolist()
    cands = [None] * N_CAND
    for local_i, slot in enumerate(perm):
        cands[slot] = dict(profiles[local_i])
    true_slot = perm[true_local]
    rec_slot = int(torch.randint(0, N_CAND, (1,), generator=gen).item())
    for s in range(N_CAND):
        cands[s]["rec"] = 1 if s == rec_slot else 0
    if shuffle_labels:
        # decouple the label: pick a random slot as the "true cause" independent of features
        true_slot = int(torch.randint(0, N_CAND, (1,), generator=gen).item())
    return {"oval": oval, "cands": cands, "true_slot": true_slot, "rec_slot": rec_slot}


def cand_score(cb, theta, oval, cand, variant):
    return float(phi(cb, oval, cand["val"], cand["eff"], cand["rec"], variant) @ theta)


# ----------------------------------------------------------------------------- bandit training
def train_theta(cb: Codebook, gen: torch.Generator, variant: str, n_train: int):
    """Online reward-modulated delta-rule selection bandit. theta inspectable (glass-box)."""
    theta = torch.zeros(2 * N_DIM, dtype=torch.float32)
    shuffle = variant == "SHUFFLED"
    enc_variant = "FULL" if variant in ("FULL", "RANDOM", "SHUFFLED") else variant
    for i in range(n_train):
        ep = make_episode(gen, shuffle_labels=shuffle)
        feats = [phi(cb, ep["oval"], c["val"], c["eff"], c["rec"], enc_variant) for c in ep["cands"]]
        P = torch.stack(feats)          # [N_CAND, D]
        q = P @ theta                   # [N_CAND]
        eps = max(EPS_FLOOR, EPS_START * (1.0 - i / max(1, n_train)))
        if torch.rand(1, generator=gen).item() < eps:
            a = int(torch.randint(0, N_CAND, (1,), generator=gen).item())
        else:
            a = int(torch.argmax(q).item())
        r = 1.0 if a == ep["true_slot"] else -0.5
        theta = theta + LR * (r - float(q[a])) * P[a]
    return theta


def eval_theta(cb, gen, variant, theta, n_eval):
    """Greedy selection eval on novel episodes. Returns selection acc + recency/random floors."""
    enc_variant = "FULL" if variant in ("FULL", "RANDOM", "SHUFFLED") else variant
    n_correct = n_rec = n_rand = 0
    rg = torch.Generator().manual_seed(999)
    for _ in range(n_eval):
        ep = make_episode(gen, shuffle_labels=False)  # eval always uses the true grounded label
        feats = [phi(cb, ep["oval"], c["val"], c["eff"], c["rec"], enc_variant) for c in ep["cands"]]
        a = int(torch.argmax(torch.stack(feats) @ theta).item())
        if a == ep["true_slot"]:
            n_correct += 1
        if ep["rec_slot"] == ep["true_slot"]:
            n_rec += 1
        if int(torch.randint(0, N_CAND, (1,), generator=rg).item()) == ep["true_slot"]:
            n_rand += 1
    return {"acc": n_correct / max(1, n_eval),
            "recency_acc": n_rec / max(1, n_eval),
            "random_acc": n_rand / max(1, n_eval)}


# ----------------------------------------------------------------------------- TEXT bridge
_STOP_EXTRA = {"who", "what", "the", "a", "an", "to", "of", "in", "on", "for", "is", "was", "he",
               "she", "it", "her", "his", "him", "and", "or", "she", "you", "i", "this", "that"}


def content_tokens(text: str):
    """Grounded content-lemma set (situation-model relational tokens), reusing normalize_tokens."""
    toks = normalize_tokens(text)
    return {t for t in toks if t not in _STOP_EXTRA and len(t) > 2}


def effect_overlap(cand_text: str, outcome_text: str) -> float:
    """Relational effect-match: fraction of the outcome's content tokens the candidate span shares.
    Grounded (patient/effect lexical identity) -- NOT char-trigram surface. In [0,1]."""
    o = content_tokens(outcome_text)
    c = content_tokens(cand_text)
    if not o:
        return 0.0
    return len(o & c) / len(o)


def quantize_eff(overlap: float) -> int:
    """Fixed thresholds -> shared K_EFF bins (set in prereg, not tuned)."""
    if overlap <= 0.0:
        return 0
    if overlap < 0.10:
        return 1
    if overlap < 0.25:
        return 2
    return 3


def text_features(view):
    """Encode a 7-item mech-view into the SAME grounded feature space (valence, eff_bin, oval, rec)."""
    outcome_text = view["goal_desc"] + " " + view["query_text"]
    oval = "NEG"  # all 7 are blocked-goal / harm outcomes (pre-registered)
    _valmap = {"HARM": "HARM", "HELP": "HELP", "NA": "NEUTRAL"}
    cands = []
    for i in range(2):
        val = _valmap[resolve_valence_blind(view["cand_text"][i])]
        eff = quantize_eff(effect_overlap(view["cand_text"][i], outcome_text))
        cands.append({"val": val, "eff": eff})
    # recency: most-recent candidate at/before the query; else nearest overall (mirrors char-trigram v1)
    q = view["query_pos"]
    before = [(view["cand_pos"][i], i) for i in range(2) if view["cand_pos"][i] <= q]
    if before:
        rec_pick = max(before)[1]
    else:
        rec_pick = min(range(2), key=lambda i: abs(view["cand_pos"][i] - q))
    for i in range(2):
        cands[i]["rec"] = 1 if i == rec_pick else 0
    return {"oval": oval, "cands": cands, "rec_pick": rec_pick}


def score_text_item(cb, theta, view, variant):
    tf = text_features(view)
    scores = [cand_score(cb, theta, tf["oval"], c, variant) for c in tf["cands"]]
    pick = int(scores.index(max(scores))) if scores[0] != scores[1] else -1
    return {"id": view["id"], "scores": scores, "pick_slot": pick,
            "correct": pick == TRUE_SLOT, "features": tf["cands"], "rec_pick": tf["rec_pick"]}


# ----------------------------------------------------------------------------- per-seed unit
def hash_variant(variant: str) -> int:
    return int.from_bytes(hashlib.sha256(variant.encode()).digest()[:2], "big") % 1000


def run_seed(seed: int, cfg: dict, views) -> dict:
    gen = torch.Generator().manual_seed(seed)
    cb = Codebook(gen)
    thetas = {}
    for variant in ("FULL", "NO_EFF", "NO_VAL", "SHUFFLED"):
        g = torch.Generator().manual_seed(seed * 100 + hash_variant(variant))
        thetas[variant] = train_theta(cb, g, variant, cfg["n_train"])
    grnd = torch.Generator().manual_seed(seed * 100 + 7)
    thetas["RANDOM"] = torch.randn(2 * N_DIM, generator=grnd, dtype=torch.float32) * 0.01

    out = {"seed": seed}
    for variant in ARMS:
        ge = torch.Generator().manual_seed(seed * 1000 + hash_variant(variant) + 1)
        out[f"{variant}_heldout"] = eval_theta(cb, ge, variant, thetas[variant], cfg["n_eval"])

    # arms-must-differ (META_RULE_AF)
    digs = {v: hashlib.sha256(thetas[v].numpy().tobytes()).hexdigest()[:16] for v in ARMS}
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], f"META_RULE_AF: {names[i]}/{names[j]} identical theta"
    out["arms_theta_digests"] = digs

    # TEXT TRANSFER (load-bearing): FULL selector + VET decompositions (valence-only, eff-only)
    text_full = [score_text_item(cb, thetas["FULL"], v, "FULL") for v in views]
    text_valonly = [score_text_item(cb, thetas["NO_EFF"], v, "NO_EFF") for v in views]   # valence, no eff
    text_effonly = [score_text_item(cb, thetas["NO_VAL"], v, "NO_VAL") for v in views]   # eff, no valence
    n = len(views)
    out["text"] = {
        "full_rows": text_full,
        "full_acc": sum(r["correct"] for r in text_full) / n,
        "valence_only_acc": sum(r["correct"] for r in text_valonly) / n,
        "eff_only_acc": sum(r["correct"] for r in text_effonly) / n,
    }
    return out


# ----------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict, views) -> dict:
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(path):
        vals = []
        for s in seeds:
            d = per_seed[s]
            for k in path.split("."):
                d = d[k]
            vals.append(float(d))
        return sum(vals) / max(1, len(vals))

    FULL = mean("FULL_heldout.acc")
    RANDOM = mean("RANDOM_heldout.acc")
    NO_EFF = mean("NO_EFF_heldout.acc")
    NO_VAL = mean("NO_VAL_heldout.acc")
    SHUF = mean("SHUFFLED_heldout.acc")
    REC = mean("FULL_heldout.recency_acc")
    RANDPICK = mean("FULL_heldout.random_acc")

    text_full = mean("text.full_acc")
    text_valonly = mean("text.valence_only_acc")
    text_effonly = mean("text.eff_only_acc")

    # gold recency floor (read ONLY for reporting; never fed to the mechanism) -- 0/7 by design
    gold_rec = sum(1 for it in views_gold(views) if it.get("recency_baseline_correct") is True) / len(views)
    CHAR_TRIGRAM_BASELINE = 0.4286  # MEASURED@ data/exp_coherence_selector_text_transfer_v1/metrics.json
    CHANCE = 0.5

    chance_sim = 1.0 / N_CAND
    random_failed = RANDOM <= chance_sim + 0.08
    shuffled_failed = SHUF <= 0.45
    full_learns = FULL >= 0.80 and (FULL - max(NO_EFF, NO_VAL, SHUF, REC, RANDOM)) >= 0.10
    ablations_degrade = (NO_EFF < FULL - 0.10) and (NO_VAL < FULL - 0.10)
    sim_mechanism_ok = random_failed and shuffled_failed and full_learns and ablations_degrade

    text_beats_all = (text_full > max(gold_rec, CHANCE, CHAR_TRIGRAM_BASELINE)) and (text_full >= 4.0 / 7.0)
    text_near_chance = text_full <= 0.5
    # VET decomposition (pre-registered): a CLEAN grounded bridge needs the grounded APPRAISAL dim to
    # transfer on its own (valence-only > chance by margin). If valence-only ~ chance and the lift is
    # carried by effect-match (content-lemma overlap = a lexical-similarity proxy), the bridge is a
    # LEXICAL PROXY, not grounded causal selection -> honest deflation (do NOT force a clean pass).
    valence_dim_transfers = text_valonly >= CHANCE + 0.10
    lift_carried_by_eff = (text_effonly > text_valonly + 0.08) and not valence_dim_transfers

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif not sim_mechanism_ok:
        if not (random_failed and shuffled_failed):
            verdict = "SIM_CONSTRUCTION_DETERMINED"
        else:
            verdict = "SIM_MECHANISM_WEAK"
    elif text_beats_all and valence_dim_transfers:
        verdict = "GROUNDED_BRIDGES"
    elif text_beats_all and lift_carried_by_eff:
        verdict = "GROUNDED_PARTIAL_LEXICAL_PROXY"
    elif text_beats_all:
        verdict = "GROUNDED_PARTIAL"
    elif text_near_chance:
        verdict = "STILL_FAILS_TEXT"
    else:
        verdict = "TEXT_MIDDLE_BAND"

    summary = (
        f"SIM: FULL={FULL:.3f} RANDOM={RANDOM:.3f}(chance={chance_sim:.3f}) NO_EFF={NO_EFF:.3f} "
        f"NO_VAL={NO_VAL:.3f} SHUFFLED={SHUF:.3f} recency={REC:.3f} | "
        f"TEXT(n=7): full={text_full:.3f} valence_only={text_valonly:.3f} eff_only={text_effonly:.3f} "
        f"vs gold_recency={gold_rec:.3f} random={CHANCE:.3f} char_trigram={CHAR_TRIGRAM_BASELINE:.3f}")

    # per-item text pick (glass-box)
    per_item = {}
    for it in views:
        iid = it["id"]
        picks = []
        for s in seeds:
            r = next(rr for rr in per_seed[s]["text"]["full_rows"] if rr["id"] == iid)
            picks.append(r["correct"])
        r0 = next(rr for rr in per_seed[seeds[0]]["text"]["full_rows"] if rr["id"] == iid)
        per_item[iid] = {"full_correct_frac_over_seeds": sum(picks) / len(picks),
                         "features_seed0": r0["features"], "scores_seed0": r0["scores"]}

    return {
        "verdict": verdict,
        "verdict_msg": f"{verdict}: {summary}",
        "summary": summary,
        "n_seeds": n,
        "means": {
            "FULL_heldout_acc": FULL, "RANDOM_heldout_acc": RANDOM, "NO_EFF_heldout_acc": NO_EFF,
            "NO_VAL_heldout_acc": NO_VAL, "SHUFFLED_heldout_acc": SHUF, "sim_recency_acc": REC,
            "sim_randompick_acc": RANDPICK, "sim_chance": chance_sim,
            "text_full_acc": text_full, "text_valence_only_acc": text_valonly,
            "text_eff_only_acc": text_effonly, "text_gold_recency_acc": gold_rec,
            "text_random_chance": CHANCE, "text_char_trigram_baseline": CHAR_TRIGRAM_BASELINE,
        },
        "bands": {
            "random_failed": random_failed, "shuffled_failed": shuffled_failed,
            "full_learns": full_learns, "ablations_degrade": ablations_degrade,
            "sim_mechanism_ok": sim_mechanism_ok, "text_beats_all": text_beats_all,
            "text_near_chance": text_near_chance,
            "valence_dim_transfers": valence_dim_transfers, "lift_carried_by_eff": lift_carried_by_eff,
        },
        "per_item_text": per_item,
        "contamination_check": {
            "mechanism_reads_only": ["goal_desc(parenthetical, leak-safe)", "query_span.text",
                                     "candidate span texts", "line positions"],
            "gold_recency_read_for_reporting_only": True,
            "char_trigram_encoder_used": False,
            "borrowed_embedding_or_llm_used": False,
        },
        "baseline_reference": ("char_trigram selector_text_acc=0.4286 MEASURED@ "
                               "data/exp_coherence_selector_text_transfer_v1/metrics.json"),
    }


def views_gold(views):
    """Attach gold recency_baseline_correct for reporting the recency floor (NOT fed to mechanism)."""
    gold = {it["id"]: it for it in load_items()}
    return [gold[v["id"]] for v in views]


# ----------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(cfg, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    views = [mech_inputs(it) for it in load_items()]
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, cfg, views)
        record_unit(output_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.1f}s FULL={res['FULL_heldout']['acc']:.3f} "
              f"RANDOM={res['RANDOM_heldout']['acc']:.3f} SHUF={res['SHUFFLED_heldout']['acc']:.3f} "
              f"text_full={res['text']['full_acc']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed, views)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"N_DIM": N_DIM, "N_CAND": N_CAND, "K_EFF": K_EFF, "seeds": SEEDS, **cfg}
    agg["prereg"] = "preregs/2026-08-04_grounded_coherence_selector_v1.md"
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ----------------------------------------------------------------------------- self-test
def self_test():
    """(1) arms produce distinct theta (discriminator can fire); (2) tiny-scale FULL beats RANDOM &
    SHUFFLED; (3) RANDOM near chance; (4) sim true-cause is well-defined (conjunction: valence-only and
    eff-only each < 1.0 by construction); (5) text bridge produces a well-formed pick per item;
    (6) contamination: mech view exposes no forbidden field."""
    views = [mech_inputs(it) for it in load_items()]
    assert len(views) == 7
    res = run_seed(0, {"n_train": 1500, "n_eval": 400}, views)
    F = res["FULL_heldout"]["acc"]; R = res["RANDOM_heldout"]["acc"]
    NE = res["NO_EFF_heldout"]["acc"]; NV = res["NO_VAL_heldout"]["acc"]; SH = res["SHUFFLED_heldout"]["acc"]
    digs = res["arms_theta_digests"]
    assert len(set(digs.values())) == len(digs), "arms not distinct (META_RULE_AF)"
    assert F > R + 0.20, f"discriminator did not fire: FULL={F:.3f} RANDOM={R:.3f}"
    assert F > SH + 0.20, f"FULL must beat SHUFFLED: FULL={F:.3f} SHUF={SH:.3f}"
    assert R < 1.0 / N_CAND + 0.10, f"RANDOM not near chance: R={R:.3f}"
    assert NE < F - 0.05 and NV < F - 0.05, f"ablations must degrade: FULL={F:.3f} NO_EFF={NE:.3f} NO_VAL={NV:.3f}"
    # text bridge well-formed
    for r in res["text"]["full_rows"]:
        assert r["pick_slot"] in (-1, 0, 1)
    print(f"[SELFTEST PASS] FULL={F:.3f} RANDOM={R:.3f} NO_EFF={NE:.3f} NO_VAL={NV:.3f} SHUF={SH:.3f} "
          f"text_full={res['text']['full_acc']:.3f} text_valonly={res['text']['valence_only_acc']:.3f} "
          f"text_effonly={res['text']['eff_only_acc']:.3f}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if args.smoke:
        run(SMOKE_CFG, "smoke")
        raise SystemExit(0)
    run(FULL_CFG, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash(OUTPUT_DIR, e)
        raise
