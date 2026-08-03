# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; theta-hash across FULL/RANDOM/MEMORIZED/NO_APPRAISAL)
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: n/a (no swept capacity claim; FHRR decode of ~5 bound pairs at N=256 far below ceiling;
#   self-test asserts bind/unbind decode fidelity as a sanity gate)
# - baseline_in_band: RANDOM is the must-FAIL floor (~chance 0.125); mechanism arm = FULL (0.70-0.98).
#   discriminator-fires at smoke: FULL must exceed RANDOM by margin
# - discriminator survives scale: smoke reduced-episode FULL-vs-RANDOM gap; FULL run full episodes;
#   gap analytically not capacity-limited (separable linear problem)
# - cardinality_ok: EXPECTED_N_SEEDS=5; verdict HARD_FAIL_CARDINALITY if fewer landed
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands from chance 1/8 + structural recency 1/n_cand,
#   set BEFORE running, not tuned)
# - deterministic_seeding: torch.Generator per seed; sorted(set()) id pools; OMP/OPENBLAS=1; no hash()-seed
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py); start_marker + crash_diag + heartbeat present
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""Grounded-appraisal SIMULATION: does the substrate EARN the appraisal -> action-tendency dynamics
from simulated experience (no text, no borrow, glass-box FHRR), such that REVENGE (harm directed at
the true causal blocker) EMERGES from primitive actions {pursue, withdraw, harm(target), help(target)}
and generalizes to HELD-OUT agent identities? Three-floor can-fail (random / memorized / no-appraisal)
plus a recency baseline for causal-coherence attribution. See preregs/2026-08-03_grounded_appraisal_
sim_earned_v1.md. GUARDS: no retaliate label; earn coherence not recency; supply only innate +
appraisal schema; discrete world, no text; the sim is a NAMED SUBSTITUTE for embodied experience;
sim-to-text transfer NOT claimed here."""

import os

# Determinism (set BEFORE torch import).
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

ANCHOR_NAME = "grounded_appraisal_sim_earned_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from hdlab.binding import bind  # noqa: E402  (project-native FHRR; NOT borrowed)
from hdlab.bundling import bundle  # noqa: E402
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ----------------------------------------------------------------------------- config
N_DIM = 256
N_CAND = 3
DTYPE = torch.complex64
SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
N_TRAIN_IDS = 24
N_EVAL_IDS = 24
LR = 0.10
EPS_START = 0.30
EPS_FLOOR = 0.05  # persistent exploration: without it, greedy risk-aversion (harm risks -0.5) traps
                  # the policy on safe no-target actions and targeting is NEVER earned (acc caps ~0.68,
                  # revenge=0). The floor lets the substrate discover harm(coherent) is rewarded.

# episode-type mix (fractions); each has a UNIQUE (congruence, coping) signature
TYPES = ["BLOCK_HIGH", "BLOCK_LOW", "RECIPROCITY", "NEUTRAL"]
TYPE_FRAC = {"BLOCK_HIGH": 0.30, "BLOCK_LOW": 0.25, "RECIPROCITY": 0.25, "NEUTRAL": 0.20}

CONG = {"BLOCK_HIGH": "HURT", "BLOCK_LOW": "HURT", "RECIPROCITY": "HELP", "NEUTRAL": "NEUTRAL"}
COPE = {"BLOCK_HIGH": "HIGH", "BLOCK_LOW": "LOW", "RECIPROCITY": "HIGH", "NEUTRAL": "HIGH"}

# action index layout: 0=pursue, 1=withdraw, 2..2+N_CAND-1 = harm(cj), then help(cj)
A_PURSUE = 0
A_WITHDRAW = 1
A_HARM0 = 2
A_HELP0 = 2 + N_CAND
N_ACTIONS = 2 + 2 * N_CAND  # 8 for N_CAND=3

# scale presets
FULL_CFG = {"n_train": 10000, "n_eval": 1500}
SMOKE_CFG = {"n_train": 1200, "n_eval": 400}


# ----------------------------------------------------------------------------- FHRR helpers
def rand_fhrr(gen: torch.Generator, n: int = N_DIM) -> torch.Tensor:
    """Random unit-modulus FHRR hypervector (complex64), phases uniform[0, 2pi)."""
    ang = torch.rand(n, generator=gen, dtype=torch.float32) * (2.0 * 3.141592653589793)
    return torch.complex(torch.cos(ang), torch.sin(ang)).to(DTYPE)


def to_real_feat(v: torch.Tensor) -> torch.Tensor:
    """FHRR complex vector -> UNIT-NORM real feature [real; imag] (len 2*N_DIM).
    Unit-norm keeps the delta-rule bandit stable: LMS needs LR < 2/||phi||^2, and an
    unnormalized bundle has ||phi||^2 = N_DIM (each complex component has modulus 1), which
    diverges at LR=0.05. Normalizing to ||phi||=1 makes LR<2 stable."""
    r = torch.cat([v.real, v.imag]).to(torch.float32)
    n = r.norm()
    return r / n if float(n) > 0 else r


class Codebook:
    """Fixed random FHRR atoms for roles / values / identities (per-seed generator)."""

    def __init__(self, gen: torch.Generator):
        self.ACT = {k: rand_fhrr(gen) for k in ("pursue", "withdraw", "harm", "help")}
        self.R_TARGET = rand_fhrr(gen)
        self.R_COH = rand_fhrr(gen)
        self.R_REC = rand_fhrr(gen)
        self.R_CONG = rand_fhrr(gen)
        self.R_COP = rand_fhrr(gen)
        self.R_FOCAL = rand_fhrr(gen)
        self.VAL = {0: rand_fhrr(gen), 1: rand_fhrr(gen)}  # binary coh/rec value atoms
        self.CONGV = {k: rand_fhrr(gen) for k in ("HURT", "HELP", "NEUTRAL")}
        self.COPV = {k: rand_fhrr(gen) for k in ("HIGH", "LOW")}
        # identity atoms: train pool + disjoint eval pool
        self.ID_TRAIN = [rand_fhrr(gen) for _ in range(N_TRAIN_IDS)]
        self.ID_EVAL = [rand_fhrr(gen) for _ in range(N_EVAL_IDS)]


# ----------------------------------------------------------------------------- world / episodes
def make_episode(gen: torch.Generator, pool: str):
    """One episode dict. pool in {'train','eval'} selects the disjoint identity pool.
    Candidates carry (id_idx, coh, rec). True causal agent = the coherent candidate (coh=1);
    recency assigned INDEPENDENTLY (true agent is most-recent only ~1/N_CAND of the time)."""
    r = torch.rand(1, generator=gen).item()
    acc = 0.0
    etype = TYPES[-1]
    for t in TYPES:
        acc += TYPE_FRAC[t]
        if r <= acc:
            etype = t
            break

    n_ids = N_TRAIN_IDS if pool == "train" else N_EVAL_IDS
    # sample N_CAND distinct identity indices deterministically from the generator
    perm = torch.randperm(n_ids, generator=gen)[:N_CAND].tolist()
    cand_ids = perm

    # coherent candidate (the causal agent) index among the N_CAND candidates
    coh_slot = int(torch.randint(0, N_CAND, (1,), generator=gen).item())
    # recency: pick the most-recent candidate INDEPENDENTLY of coh_slot
    rec_slot = int(torch.randint(0, N_CAND, (1,), generator=gen).item())

    cands = []
    for s in range(N_CAND):
        cands.append({
            "id_idx": cand_ids[s],
            "coh": 1 if s == coh_slot else 0,
            "rec": 1 if s == rec_slot else 0,
        })
    return {
        "type": etype,
        "cong": CONG[etype],
        "cope": COPE[etype],
        "cands": cands,
        "coh_slot": coh_slot,  # = true blocker/helper slot
        "rec_slot": rec_slot,
        "pool": pool,
    }


def reward(ep, action: int) -> float:
    """World dynamics the substrate must discover from consequence. +1 restorative, -0.5 misdirected."""
    etype = ep["type"]
    coh = ep["coh_slot"]
    is_harm = A_HARM0 <= action < A_HARM0 + N_CAND
    is_help = A_HELP0 <= action < A_HELP0 + N_CAND
    harm_slot = (action - A_HARM0) if is_harm else -1
    help_slot = (action - A_HELP0) if is_help else -1
    if etype == "BLOCK_HIGH":
        if is_harm and harm_slot == coh:
            return 1.0
        if is_harm:
            return -0.5
        return 0.0
    if etype == "BLOCK_LOW":
        if action == A_WITHDRAW:
            return 1.0
        if is_harm:
            return -0.5
        return 0.0
    if etype == "RECIPROCITY":
        if is_help and help_slot == coh:
            return 1.0
        if is_harm:
            return -0.5
        return 0.0
    # NEUTRAL
    if action == A_PURSUE:
        return 1.0
    if is_harm:
        return -0.5
    return 0.0


def correct_action(ep) -> int:
    """The unique reward-maximizing action."""
    etype = ep["type"]
    coh = ep["coh_slot"]
    if etype == "BLOCK_HIGH":
        return A_HARM0 + coh
    if etype == "BLOCK_LOW":
        return A_WITHDRAW
    if etype == "RECIPROCITY":
        return A_HELP0 + coh
    return A_PURSUE


# ----------------------------------------------------------------------------- feature encoder
def action_meta(action: int):
    """(type_key, target_slot or -1)."""
    if action == A_PURSUE:
        return "pursue", -1
    if action == A_WITHDRAW:
        return "withdraw", -1
    if A_HARM0 <= action < A_HARM0 + N_CAND:
        return "harm", action - A_HARM0
    return "help", action - A_HELP0


def phi(cb: Codebook, ep, action: int, variant: str) -> torch.Tensor:
    """Encode (state, action) into a real feature vector under the given arm's information set.
    FULL: action-type + target(coh,rec) + congruence + coping  (IDENTITY-FREE)
    NO_APPRAISAL: action-type + target(coh,rec)                 (drops congruence/coping)
    MEMORIZED: action-type + target(identity) + focal(identity bundle)  (no coherence, no appraisal)
    """
    tkey, tslot = action_meta(action)
    comps = [cb.ACT[tkey]]
    pool_ids = cb.ID_TRAIN if ep["pool"] == "train" else cb.ID_EVAL

    if variant in ("FULL", "RANDOM", "NO_APPRAISAL"):
        if tslot >= 0:
            c = ep["cands"][tslot]
            tdesc = bundle(torch.stack([
                bind(cb.R_COH, cb.VAL[c["coh"]]),
                bind(cb.R_REC, cb.VAL[c["rec"]]),
            ]))
            comps.append(bind(cb.R_TARGET, tdesc))
        if variant in ("FULL", "RANDOM"):
            comps.append(bind(cb.R_CONG, cb.CONGV[ep["cong"]]))
            comps.append(bind(cb.R_COP, cb.COPV[ep["cope"]]))
    elif variant == "MEMORIZED":
        if tslot >= 0:
            c = ep["cands"][tslot]
            comps.append(bind(cb.R_TARGET, pool_ids[c["id_idx"]]))
        # focal context: bundle of all present candidate identities (identity-only)
        comps.append(bind(cb.R_FOCAL, bundle(torch.stack(
            [pool_ids[c["id_idx"]] for c in ep["cands"]]))))
    else:
        raise ValueError(f"unknown variant {variant!r}")

    v = bundle(torch.stack(comps)) if len(comps) > 1 else comps[0]
    return to_real_feat(v)


def phi_matrix(cb: Codebook, ep, variant: str) -> torch.Tensor:
    """[N_ACTIONS, 2*N_DIM] feature matrix for all actions in this state."""
    return torch.stack([phi(cb, ep, a, variant) for a in range(N_ACTIONS)])


# ----------------------------------------------------------------------------- bandit
def train_theta(cb: Codebook, gen: torch.Generator, variant: str, n_train: int):
    """Online reward-modulated delta-rule contextual bandit. theta inspectable (glass-box)."""
    theta = torch.zeros(2 * N_DIM, dtype=torch.float32)
    for i in range(n_train):
        ep = make_episode(gen, "train")
        P = phi_matrix(cb, ep, variant)  # [A, D]
        q = P @ theta                    # [A]
        eps = max(EPS_FLOOR, EPS_START * (1.0 - i / max(1, n_train)))
        if torch.rand(1, generator=gen).item() < eps:
            a = int(torch.randint(0, N_ACTIONS, (1,), generator=gen).item())
        else:
            a = int(torch.argmax(q).item())
        r = reward(ep, a)
        theta = theta + LR * (r - float(q[a])) * P[a]
    return theta


def eval_theta(cb: Codebook, gen: torch.Generator, variant: str, theta: torch.Tensor,
               n_eval: int, pool: str):
    """Greedy eval. Returns aggregate + BLOCK_HIGH targeting diagnostics."""
    n_correct = 0
    n_bh = 0                # BLOCK_HIGH count
    n_rev = 0              # harm(true blocker) on BLOCK_HIGH
    n_harm_bh = 0          # any harm chosen on BLOCK_HIGH
    n_harm_true = 0        # harm targeting true blocker (subset of n_harm_bh)
    n_bystander = 0        # harm(bystander) on BLOCK_HIGH
    n_rec_would_restore = 0  # recency-targeting would have restored (most-recent == true blocker)
    for _ in range(n_eval):
        ep = make_episode(gen, pool)
        P = phi_matrix(cb, ep, variant)
        a = int(torch.argmax(P @ theta).item())
        if a == correct_action(ep):
            n_correct += 1
        if ep["type"] == "BLOCK_HIGH":
            n_bh += 1
            coh = ep["coh_slot"]
            if a == A_HARM0 + coh:
                n_rev += 1
            if A_HARM0 <= a < A_HARM0 + N_CAND:
                n_harm_bh += 1
                if (a - A_HARM0) == coh:
                    n_harm_true += 1
                else:
                    n_bystander += 1
            if ep["rec_slot"] == coh:
                n_rec_would_restore += 1
    return {
        "acc": n_correct / max(1, n_eval),
        "n_bh": n_bh,
        "revenge_emergence_rate": (n_rev / n_bh) if n_bh else 0.0,
        "targeting_specificity": (n_harm_true / n_harm_bh) if n_harm_bh else 0.0,
        "bystander_harm_rate": (n_bystander / n_bh) if n_bh else 0.0,
        "earned_restoration": (n_rev / n_bh) if n_bh else 0.0,
        "recency_restoration": (n_rec_would_restore / n_bh) if n_bh else 0.0,
    }


def coherence_vs_recency_readout(cb: Codebook, theta: torch.Tensor) -> float:
    """Glass-box witness: on a canonical BLOCK_HIGH state, Q(harm coherent-cand) - Q(harm recent-cand).
    Positive => the substrate EARNED coherence-over-recency targeting (not recency)."""
    ep = {
        "type": "BLOCK_HIGH", "cong": "HURT", "cope": "HIGH", "pool": "eval",
        "coh_slot": 0, "rec_slot": 1,
        "cands": [
            {"id_idx": 0, "coh": 1, "rec": 0},  # coherent, not recent -> true blocker
            {"id_idx": 1, "coh": 0, "rec": 1},  # recent, not coherent -> distractor
            {"id_idx": 2, "coh": 0, "rec": 0},
        ],
    }
    q_coh = float(phi(cb, ep, A_HARM0 + 0, "FULL") @ theta)
    q_rec = float(phi(cb, ep, A_HARM0 + 1, "FULL") @ theta)
    return q_coh - q_rec


# ----------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, cfg: dict) -> dict:
    gen = torch.Generator().manual_seed(seed)
    cb = Codebook(gen)

    thetas = {}
    for variant in ("FULL", "MEMORIZED", "NO_APPRAISAL"):
        g = torch.Generator().manual_seed(seed * 100 + hash_variant(variant))
        thetas[variant] = train_theta(cb, g, variant, cfg["n_train"])
    # RANDOM: FULL encoder, untrained theta (small gaussian)
    grnd = torch.Generator().manual_seed(seed * 100 + 7)
    thetas["RANDOM"] = torch.randn(2 * N_DIM, generator=grnd, dtype=torch.float32) * 0.01

    out = {"seed": seed}

    # held-out eval (novel identity pool) for all arms
    for variant in ("FULL", "RANDOM", "MEMORIZED", "NO_APPRAISAL"):
        ge = torch.Generator().manual_seed(seed * 1000 + hash_variant(variant) + 1)
        ev = eval_theta(cb, ge, variant, thetas[variant], cfg["n_eval"], "eval")
        out[f"{variant}_heldout"] = ev

    # FULL train-pool eval (generalization gap)
    gt = torch.Generator().manual_seed(seed * 1000 + 999)
    out["FULL_train"] = eval_theta(cb, gt, "FULL", thetas["FULL"], cfg["n_eval"], "train")

    out["coh_minus_rec_readout"] = coherence_vs_recency_readout(cb, thetas["FULL"])

    # arms-must-differ (META_RULE_AF): theta hashes across arms
    digs = {}
    for variant in ("FULL", "RANDOM", "MEMORIZED", "NO_APPRAISAL"):
        digs[variant] = hashlib.sha256(
            thetas[variant].numpy().tobytes()).hexdigest()[:16]
    names = sorted(digs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert digs[names[i]] != digs[names[j]], (
                f"META_RULE_AF VIOLATION: arms {names[i]} and {names[j]} bit-identical theta")
    out["arms_theta_digests"] = digs
    return out


def hash_variant(variant: str) -> int:
    """Deterministic small int per variant (hashlib, NOT builtin hash() -- PROT-023)."""
    return int.from_bytes(hashlib.sha256(variant.encode()).digest()[:2], "big") % 1000


# ----------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
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

    F = mean("FULL_heldout.acc")
    Ft = mean("FULL_train.acc")
    R = mean("RANDOM_heldout.acc")
    M = mean("MEMORIZED_heldout.acc")
    NA = mean("NO_APPRAISAL_heldout.acc")
    rev = mean("FULL_heldout.revenge_emergence_rate")
    spec = mean("FULL_heldout.targeting_specificity")
    bys = mean("FULL_heldout.bystander_harm_rate")
    er = mean("FULL_heldout.earned_restoration")
    rr = mean("FULL_heldout.recency_restoration")
    readout = mean("coh_minus_rec_readout")

    random_failed = R < 0.25
    memorized_failed = (M < 0.30) and ((F - M) >= 0.20)
    appraisal_nonvacuous = (F - NA) >= 0.05
    beats_recency = (er - rr) >= 0.25
    generalizes = (abs(Ft - F) <= 0.10) and (F >= 0.70)
    revenge_emerged = (rev >= 0.70) and (spec >= 0.80)

    construction_determined = (R >= 0.25) or (NA >= 0.90 and (F - NA) < 0.05)
    cannot_earn = (F < 0.40) or ((not revenge_emerged) and F < 0.55)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    elif construction_determined:
        verdict = "CONSTRUCTION_DETERMINED"
    elif (random_failed and memorized_failed and generalizes and revenge_emerged
          and beats_recency and appraisal_nonvacuous):
        verdict = "MECHANISM_EARNS"
    elif (random_failed and memorized_failed and generalizes and revenge_emerged
          and beats_recency and not appraisal_nonvacuous):
        verdict = "MECHANISM_EARNS_APPRAISAL_VACUOUS"
    elif cannot_earn:
        verdict = "MECHANISM_CANNOT_EARN"
    else:
        verdict = "PARTIAL_MIXED"

    summary = (
        f"FULL_heldout={F:.3f} FULL_train={Ft:.3f} RANDOM={R:.3f} MEMORIZED={M:.3f} "
        f"NO_APPRAISAL={NA:.3f} | revenge={rev:.3f} specificity={spec:.3f} bystander={bys:.3f} "
        f"| earned_restore={er:.3f} recency_restore={rr:.3f} | coh-rec_readout={readout:.3f}")
    return {
        "verdict": verdict,
        "verdict_msg": f"{verdict}: {summary}",
        "summary": summary,
        "n_seeds": n,
        "means": {
            "FULL_heldout_acc": F, "FULL_train_acc": Ft, "RANDOM_acc": R,
            "MEMORIZED_heldout_acc": M, "NO_APPRAISAL_heldout_acc": NA,
            "revenge_emergence_rate": rev, "targeting_specificity": spec,
            "bystander_harm_rate": bys, "earned_restoration": er,
            "recency_restoration": rr, "coh_minus_rec_readout": readout,
        },
        "bands": {
            "random_failed": random_failed, "memorized_failed": memorized_failed,
            "appraisal_nonvacuous": appraisal_nonvacuous, "beats_recency": beats_recency,
            "generalizes": generalizes, "revenge_emerged": revenge_emerged,
            "construction_determined": construction_determined, "cannot_earn": cannot_earn,
        },
    }


# ----------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    """Isolate smoke into its own dir so its reduced-scale checkpoint never resumes into a full run."""
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(cfg, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, cfg)
        record_unit(output_dir, k, res)
        print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
              f"FULL_heldout={res['FULL_heldout']['acc']:.3f} "
              f"RANDOM={res['RANDOM_heldout']['acc']:.3f} "
              f"revenge={res['FULL_heldout']['revenge_emergence_rate']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"N_DIM": N_DIM, "N_CAND": N_CAND, "N_ACTIONS": N_ACTIONS,
                     "seeds": SEEDS, **cfg}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ----------------------------------------------------------------------------- self-test
def self_test():
    """(1) FHRR bind/unbind decode fidelity sanity; (2) arms produce different features;
    (3) tiny-scale FULL beats RANDOM (discriminator fires); (4) reward/correct_action consistent;
    (5) recency decorrelated from coherence."""
    from hdlab.binding import unbind
    gen = torch.Generator().manual_seed(123)
    cb = Codebook(gen)

    # (1) decode fidelity: unbind(bind(role, filler), role) ~ filler (high cosine)
    role, filler = rand_fhrr(gen), rand_fhrr(gen)
    rec = unbind(bind(role, filler), role)
    cos = float(torch.real(torch.vdot(rec, filler)).item()) / (
        float(rec.abs().pow(2).sum().sqrt()) * float(filler.abs().pow(2).sum().sqrt()) + 1e-9)
    assert cos > 0.99, f"FHRR decode fidelity too low: cos={cos:.4f}"

    # (2) arms differ: feature vectors for the same (ep, action) differ across variants
    ep = make_episode(torch.Generator().manual_seed(5), "train")
    fa = phi(cb, ep, A_HARM0, "FULL")
    na = phi(cb, ep, A_HARM0, "NO_APPRAISAL")
    me = phi(cb, ep, A_HARM0, "MEMORIZED")
    assert not torch.equal(fa, na) and not torch.equal(fa, me) and not torch.equal(na, me), \
        "arms produce identical features"

    # (3) discriminator fires at tiny scale
    res = run_seed(0, {"n_train": 1500, "n_eval": 400})
    F = res["FULL_heldout"]["acc"]
    R = res["RANDOM_heldout"]["acc"]
    rev = res["FULL_heldout"]["revenge_emergence_rate"]
    assert F > R + 0.2, f"discriminator did not fire: FULL={F:.3f} RANDOM={R:.3f}"
    assert R < 0.30, f"RANDOM not near chance (construction risk): R={R:.3f}"
    assert res["coh_minus_rec_readout"] > 0, "coherence-over-recency not earned in readout"

    # (4) reward/correct_action consistency: correct action yields the max reward
    for _ in range(50):
        e = make_episode(torch.Generator().manual_seed(_ + 1), "train")
        ca = correct_action(e)
        assert reward(e, ca) == 1.0, "correct_action does not yield reward 1.0"
        for a in range(N_ACTIONS):
            assert reward(e, a) <= reward(e, ca), "a non-correct action out-rewards correct"

    # (5) recency decorrelated from coherence over many episodes (~1/N_CAND overlap)
    same = 0
    NN = 3000
    for i in range(NN):
        e = make_episode(torch.Generator().manual_seed(10000 + i), "eval")
        if e["rec_slot"] == e["coh_slot"]:
            same += 1
    frac = same / NN
    assert abs(frac - 1.0 / N_CAND) < 0.05, f"recency not decorrelated: overlap={frac:.3f}"

    print(f"[SELFTEST PASS] decode_cos={cos:.4f} tiny FULL={F:.3f} RANDOM={R:.3f} "
          f"revenge={rev:.3f} readout={res['coh_minus_rec_readout']:.3f} "
          f"rec/coh_overlap={frac:.3f}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run(SMOKE_CFG, "smoke")
        raise SystemExit(0)
    # default = full
    run(FULL_CFG, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
