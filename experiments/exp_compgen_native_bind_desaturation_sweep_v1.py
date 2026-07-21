#!/usr/bin/env python
"""DE-SATURATION sweep for compgen native role-filler binding (follow-up to
exp_compgen_native_bind_role_filler_v1, commit 34544d2b HARD_PASS).

WHY: the base cell showed native-bind LEARNED encoder generalizes to held-out
(concept, role) combos 1.0 vs fair-flat 0.0 -- but on a CLEAN regime (N=1024, 24
near-orthogonal FHRR codes, no noise). Gap=1.0 is SATURATED (construction-favorable
magnitude). The chain-grade question: does native's edge SURVIVE realistic
ambiguity/noise, or is it a clean-regime artifact? SWEEP difficulty to find out.

DE-SATURATION: two INDEPENDENT single-knob difficulty sweeps, both anchored at the
base regime (positive control that must reproduce native 1.0 / flat 0.0):

  SWEEP A -- CLEANUP NOISE (test-time robustness of the learned solution):
    train each arm CLEAN once (per seed), then EVALUATE in-dist + held-out under
    additive complex Gaussian noise on the composed FHRR vector, sigma swept.
    Noise makes cleanup genuinely hard at eval -> in-dist accuracy DROPS -> the
    held-out gap is no longer saturated. Fine-grained erosion curve.
    (Additive noise at N=1024 needs sigma ~ sqrt(N/ln V) ~ 18 to bite cleanup;
     the grid brackets that transition. THEORETICAL@ sigma_crit ~ sqrt(N/ln V).)

  SWEEP B -- ORTHOGONALITY / VOCAB (genuinely harder LEARNED task):
    train + eval from scratch at progressively harder (N_DIM, N_FILL, N_VERB):
    smaller dimension + larger vocab => codes are NOT near-orthogonal => cleanup
    crosstalk rises => in-dist itself becomes non-trivial. A DIFFERENT erosion
    mechanism (code packing, not additive noise) as an independent cross-check.

THE QUANTITATIVE RESULT = native's held-out accuracy (and native-vs-flat gap,
native-vs-tied gap) AS A FUNCTION OF DIFFICULTY, on both axes. Does native maintain
a ROBUST edge (CG-worthy) or erode to clean-regime-only (honest bound)? BOTH are
reported honestly.

ARMS (reused from base cell; one variable A vs B = readout binding-vs-flat):
  A native_bind_shared   : FHRR binding readout, SHARED noun-emb across roles   [MECHANISM]
  B flat                 : per-role classifier heads over pooled feats, NO bind [FAIR BASELINE]
  C native_bind_scramble : A lesion (decode with random role keys)              [MUST-FAIL]
  D native_bind_tied     : binding readout, role-SPECIFIC emb tables            [LIVE-ALT / free-algebra locus]

FLAT NOISE NOTE (transparency): SWEEP A additive noise lives on the FHRR composed
vector, which the flat arm does NOT consume (flat uses independent MLP heads). So
flat is noise-invariant by architecture. This is HONEST and does not confound the
research question, because flat's held-out is STRUCTURALLY ~0 at EVERY difficulty
level (a role-head gets no gradient for a concept never seen in that role). The gap
native-flat therefore reduces to native's held-out; flat's role at each level is the
structural-0 floor + the "task remains in-dist learnable" control. The de-saturation
witness is NATIVE'S OWN in-dist dropping off 1.0 (cleanup now hard).

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test on base regime)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: THEORETICAL cleanup transition sigma_crit ~ sqrt(N/ln V); sweep brackets it (discriminator reachable)
# - baseline_in_band / DE-SAT gate: native in-dist MUST drop <= 0.90 at some swept level (else regime too easy -> INCONCLUSIVE)
# - discriminator survives scale: SWEEP A runs at FULL N=1024; smoke keeps full N (fewer seeds/epochs/sigmas)
# - HARD sentinels: flat held-out < 0.30 all levels; scramble held-out <= 0.20; base sigma0 native in-dist >= 0.95 (positive control)
# - deterministic_seeding: fixed int seeds + sorted() splits + index-derived noise gen; NO hash()-seeded RNG
# - cardinality_ok: EXPECTED_N_UNITS gate over (sweep, level, seed, arm)
# - progress_logging: line_buffered_stdout (flush prints)
# - all numbers MEASURED@ this cell's metrics.json
# LOCAL-ONLY: no push, no store mutation, no atom bank. Skunkworks VETs after land.

Anchor: compgen_native_bind_desaturation_sweep_v1
"""
import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

ANCHOR_NAME = "compgen_native_bind_desaturation_sweep_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ------------------------------ fixed config ------------------------------
N_ROLE = 3              # AGENT, PATIENT, VERB role vectors
D_FLAT = 256            # flat noun/verb embedding dim (capacity fixed across regimes)
H_FLAT = 256            # flat hidden dim
TEMP = 20.0             # logit temperature; /N normalization makes it N-robust
DEVICE = "cpu"          # runner does not pass argv; this cell is tiny (small complex matmuls)

# BASE regime = the saturated base-cell regime (positive control anchor for BOTH sweeps).
BASE_REGIME = (1024, 24, 12)   # (N_DIM, N_FILL, N_VERB)

# SWEEP A: additive-noise sigma grid at the BASE regime (N=1024). Brackets sigma_crit ~ sqrt(N/lnV) ~ 18.
SWEEP_A_SIGMAS_FULL = [0.0, 4.0, 8.0, 12.0, 18.0, 24.0, 32.0, 48.0]
SWEEP_A_SIGMAS_SMOKE = [0.0, 12.0, 32.0, 48.0]

# SWEEP B: orthogonality/vocab ladder (N_DIM, N_FILL, N_VERB). All N_FILL divisible by 3.
SWEEP_B_REGIMES_FULL = [(1024, 24, 12), (256, 48, 16), (128, 96, 24), (64, 96, 24), (48, 96, 24)]
SWEEP_B_REGIMES_SMOKE = [(1024, 24, 12), (128, 96, 24)]

FULL = dict(n_train=1400, n_indist=350, n_heldout=280, epochs=60, eval_every=15,
            batch=256, lr=1e-2, seeds=[7, 13, 19],
            sweep_a_sigmas=SWEEP_A_SIGMAS_FULL, sweep_b_regimes=SWEEP_B_REGIMES_FULL)
SMOKE = dict(n_train=700, n_indist=200, n_heldout=140, epochs=25, eval_every=25,
             batch=256, lr=1e-2, seeds=[7],
             sweep_a_sigmas=SWEEP_A_SIGMAS_SMOKE, sweep_b_regimes=SWEEP_B_REGIMES_SMOKE)

ARMS_TRAIN = ["native_bind_shared", "flat", "native_bind_tied"]
ARMS = ["native_bind_shared", "flat", "native_bind_scramble", "native_bind_tied"]


# ------------------------------ dataset (parameterized by regime) ------------------------------
def concept_groups(n_fill):
    """Deterministic sorted partition into both / agent_only / patient_only. group = n_fill//3."""
    gsz = n_fill // 3
    ids = list(range(3 * gsz))
    both = sorted(ids[0:gsz])
    agent_only = sorted(ids[gsz:2 * gsz])
    patient_only = sorted(ids[2 * gsz:3 * gsz])
    return both, agent_only, patient_only, gsz


def make_dataset(seed, n_fill, n_verb, n_train, n_indist, n_heldout):
    """train / in-dist-test / held-out-combination-test. Held-out = NOVEL (concept, role):
    a concept seen only as agent in train, tested as patient (and vice versa). Non-tautological."""
    rng = np.random.default_rng(seed)
    both, agent_only, patient_only, gsz = concept_groups(n_fill)
    train_agents = sorted(both + agent_only)
    train_patients = sorted(both + patient_only)

    def sample_triples(n, agent_pool, patient_pool, seen=None):
        out = []
        guard = 0
        seen = set() if seen is None else set(seen)
        while len(out) < n and guard < n * 400:
            guard += 1
            a = int(rng.choice(agent_pool))
            p = int(rng.choice(patient_pool))
            v = int(rng.integers(0, n_verb))
            if a == p:
                continue
            key = (a, p, v)
            if key in seen:
                continue
            seen.add(key)
            out.append(key)
        return out

    train = sample_triples(n_train, train_agents, train_patients)
    train_set = set(train)
    indist = sample_triples(n_indist, train_agents, train_patients, seen=train_set)
    n_half = n_heldout // 2
    ho_a = sample_triples(n_half, patient_only, both)              # novel role = AGENT (0)
    ho_p = sample_triples(n_heldout - n_half, both, agent_only)     # novel role = PATIENT (1)
    heldout = [(a, p, v, 0) for (a, p, v) in ho_a] + [(a, p, v, 1) for (a, p, v) in ho_p]
    if len(train) < 0.5 * n_train or len(indist) == 0 or len(heldout) == 0:
        raise RuntimeError("DATASET_UNDERFILLED seed=%d nfill=%d nverb=%d train=%d/%d indist=%d/%d heldout=%d/%d"
                           % (seed, n_fill, n_verb, len(train), n_train, len(indist), n_indist,
                              len(heldout), n_heldout))
    return train, indist, heldout


# ------------------------------ FHRR fixed codebook (parameterized) ------------------------------
def fixed_codebook(seed, n_dim, n_fill, n_verb):
    """Fixed (non-trained) phasor codebook + role vectors. exp(i*phase), unit modulus."""
    g = torch.Generator().manual_seed(seed + 100003)
    two_pi = 2.0 * np.pi
    cb_phase = torch.rand(n_fill, n_dim, generator=g) * two_pi
    role_phase = torch.rand(3, n_dim, generator=g) * two_pi        # 0=AGENT 1=PATIENT 2=VERB
    codebook = torch.exp(1j * cb_phase.to(torch.float32)).to(torch.complex64)
    roles = torch.exp(1j * role_phase.to(torch.float32)).to(torch.complex64)
    return codebook, roles


# ------------------------------ models (parameterized) ------------------------------
class NativeBind(torch.nn.Module):
    """FHRR binding readout. shared=True: one noun-emb table; shared=False: role-specific.
    scramble=True: PATIENT role vector := AGENT role vector."""

    def __init__(self, codebook, roles, seed, n_verb, shared=True, scramble=False):
        super().__init__()
        self.register_buffer("codebook", codebook)             # (V, N) complex fixed
        r = roles.clone()
        if scramble:
            r[1] = r[0]
        self.register_buffer("roles", r)                       # (3, N) complex fixed
        self.shared = shared
        self.n_dim = codebook.shape[1]
        self.n_fill = codebook.shape[0]
        self.n_verb = n_verb
        g = torch.Generator().manual_seed(seed + 7)
        two_pi = 2.0 * np.pi
        if shared:
            self.theta_emb = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
        else:
            self.theta_emb_a = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
            self.theta_emb_p = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
        self.theta_verb = torch.nn.Parameter(torch.rand(self.n_verb, self.n_dim, generator=g) * two_pi)

    def _emb(self, theta, idx):
        return torch.exp(1j * theta[idx])

    def forward(self, a, p, v, decode_roles=None, noise_sigma=0.0, noise_gen=None):
        if self.shared:
            ea = self._emb(self.theta_emb, a)
            ep = self._emb(self.theta_emb, p)
        else:
            ea = self._emb(self.theta_emb_a, a)
            ep = self._emb(self.theta_emb_p, p)
        ev = self._emb(self.theta_verb, v)
        prop = ea * self.roles[0] + ep * self.roles[1] + ev * self.roles[2]      # (B, N) complex
        if noise_sigma and noise_sigma > 0.0:
            B, N = prop.shape
            scale = float(noise_sigma) / np.sqrt(2.0)
            nr = torch.randn(B, N, generator=noise_gen) * scale
            ni = torch.randn(B, N, generator=noise_gen) * scale
            prop = prop + (nr + 1j * ni).to(prop.dtype)
        dr = self.roles if decode_roles is None else decode_roles
        cb_conj = self.codebook.conj()
        qa = prop * dr[0].conj()
        qp = prop * dr[1].conj()
        logits_a = (qa @ cb_conj.T).real / self.n_dim * TEMP
        logits_p = (qp @ cb_conj.T).real / self.n_dim * TEMP
        return logits_a, logits_p


class Flat(torch.nn.Module):
    """FAIR strong baseline: role-sorted inputs, per-role classifier heads. Fails held-out
    (concept, role) because a role head gets no gradient for a concept never seen in that role."""

    def __init__(self, seed, n_fill, n_verb):
        super().__init__()
        torch.manual_seed(seed + 11)
        self.emb_noun = torch.nn.Embedding(n_fill, D_FLAT)
        self.emb_verb = torch.nn.Embedding(n_verb, D_FLAT)
        self.mlp = torch.nn.Sequential(torch.nn.Linear(3 * D_FLAT, H_FLAT), torch.nn.ReLU(),
                                       torch.nn.Linear(H_FLAT, H_FLAT), torch.nn.ReLU())
        self.head_agent = torch.nn.Linear(H_FLAT, n_fill)
        self.head_patient = torch.nn.Linear(H_FLAT, n_fill)

    def forward(self, a, p, v, decode_roles=None, noise_sigma=0.0, noise_gen=None):
        x = torch.cat([self.emb_noun(a), self.emb_noun(p), self.emb_verb(v)], dim=-1)
        h = self.mlp(x)
        return self.head_agent(h), self.head_patient(h)


def build_model(arm, codebook, roles, seed, n_fill, n_verb):
    if arm == "native_bind_shared":
        return NativeBind(codebook, roles, seed, n_verb, shared=True, scramble=False)
    if arm == "native_bind_scramble":
        return NativeBind(codebook, roles, seed, n_verb, shared=True, scramble=True)
    if arm == "native_bind_tied":
        return NativeBind(codebook, roles, seed, n_verb, shared=False, scramble=False)
    if arm == "flat":
        return Flat(seed, n_fill, n_verb)
    raise ValueError("unknown arm: " + arm)


# ------------------------------ eval ------------------------------
def _tensorize(triples):
    arr = np.array([(t[0], t[1], t[2]) for t in triples], dtype=np.int64)
    return (torch.from_numpy(arr[:, 0]), torch.from_numpy(arr[:, 1]), torch.from_numpy(arr[:, 2]))


def _noise_gen(seed, tag_idx):
    """Deterministic noise generator from a stable enumerated index (NO hash())."""
    return torch.Generator().manual_seed(seed * 100003 + tag_idx * 97 + 41)


def eval_indist(model, indist, sigma=0.0, gen=None, decode_roles=None):
    model.eval()
    a, p, v = _tensorize(indist)
    with torch.no_grad():
        la, lp = model(a, p, v, decode_roles=decode_roles, noise_sigma=sigma, noise_gen=gen)
    acc_a = (la.argmax(-1) == a).float().mean().item()
    acc_p = (lp.argmax(-1) == p).float().mean().item()
    return 0.5 * (acc_a + acc_p)


def eval_heldout(model, heldout, sigma=0.0, gen=None, decode_roles=None):
    model.eval()
    a, p, v = _tensorize([(t[0], t[1], t[2]) for t in heldout])
    novel = torch.tensor([t[3] for t in heldout], dtype=torch.int64)
    with torch.no_grad():
        la, lp = model(a, p, v, decode_roles=decode_roles, noise_sigma=sigma, noise_gen=gen)
    correct = torch.where(novel == 0, la.argmax(-1) == a, lp.argmax(-1) == p)
    return correct.float().mean().item()


def train_arm(arm, cfg, codebook, roles, seed, n_fill, n_verb, train, indist, heldout):
    model = build_model(arm, codebook, roles, seed, n_fill, n_verb).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    lossfn = torch.nn.CrossEntropyLoss()
    a_all, p_all, v_all = _tensorize(train)
    n = a_all.shape[0]
    ind0 = eval_indist(model, indist)
    ho0 = eval_heldout(model, heldout)
    curve = [{"epoch": 0, "indist": round(ind0, 4), "heldout": round(ho0, 4)}]
    g = torch.Generator().manual_seed(seed + 999)
    for ep in range(1, cfg["epochs"] + 1):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, cfg["batch"]):
            idx = perm[i:i + cfg["batch"]]
            la, lp = model(a_all[idx], p_all[idx], v_all[idx])
            loss = lossfn(la, a_all[idx]) + lossfn(lp, p_all[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        if ep % cfg["eval_every"] == 0 or ep == cfg["epochs"]:
            curve.append({"epoch": ep, "indist": round(eval_indist(model, indist), 4),
                          "heldout": round(eval_heldout(model, heldout), 4)})
    # signature tensor (clean, no noise) for arms-differ hash
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = model(pa, pp, pv)
        sig = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    return model, curve, sig


# ------------------------------ verdict ------------------------------
def _agg(rows, key):
    return float(np.mean([r[key] for r in rows])) if rows else float("nan")


def summarize_sweep_a(per_a):
    """per_a: list of {sigma, seed, arm, indist, heldout}. Returns list of per-sigma aggregate dicts."""
    out = []
    sigmas = sorted(set(r["sigma"] for r in per_a))
    for s in sigmas:
        row = {"sigma": s}
        for arm in ARMS:
            rr = [r for r in per_a if r["sigma"] == s and r["arm"] == arm]
            row[arm + "_indist"] = round(_agg(rr, "indist"), 4)
            row[arm + "_heldout"] = round(_agg(rr, "heldout"), 4)
        out.append(row)
    return out


def summarize_sweep_b(per_b):
    out = []
    keys = sorted(set((r["n_dim"], r["n_fill"], r["n_verb"]) for r in per_b),
                  key=lambda t: (-t[0], t[1]))
    for (nd, nf, nv) in keys:
        row = {"n_dim": nd, "n_fill": nf, "n_verb": nv, "chance": round(1.0 / nf, 4)}
        for arm in ARMS:
            rr = [r for r in per_b if r["n_dim"] == nd and r["n_fill"] == nf
                  and r["n_verb"] == nv and r["arm"] == arm]
            row[arm + "_indist"] = round(_agg(rr, "indist"), 4)
            row[arm + "_heldout"] = round(_agg(rr, "heldout"), 4)
        out.append(row)
    return out


def compute_verdict(sa, sb):
    """Classify the erosion. sa: sweep-A per-sigma aggregates (sorted by sigma asc).
       sb: sweep-B per-regime aggregates (sorted hardest-last-ish, base first)."""
    checks = {}
    # positive control: base regime (sweep A sigma=0 == sweep B base) reproduces native 1.0 / flat 0.
    base = sa[0]
    checks["positive_control_native_indist_ge_0.95"] = base["native_bind_shared_indist"] >= 0.95
    checks["positive_control_native_heldout_ge_0.90"] = base["native_bind_shared_heldout"] >= 0.90
    checks["positive_control_flat_heldout_le_0.10"] = base["flat_heldout"] <= 0.10

    # HARD sentinels (design integrity across ALL levels)
    flat_ho_max = max(max(r["flat_heldout"] for r in sa), max(r["flat_heldout"] for r in sb))
    scr_ho_max = max(max(r["native_bind_scramble_heldout"] for r in sa),
                     max(r["native_bind_scramble_heldout"] for r in sb))
    checks["flat_heldout_lt_0.30_all_levels"] = flat_ho_max < 0.30
    checks["scramble_heldout_le_0.20_all_levels"] = scr_ho_max <= 0.20

    # DE-SATURATION gate: native in-dist must drop <= 0.90 at SOME swept level (else regime too easy).
    nat_indist_min_a = min(r["native_bind_shared_indist"] for r in sa)
    nat_indist_min_b = min(r["native_bind_shared_indist"] for r in sb)
    desat_valid = (nat_indist_min_a <= 0.90) or (nat_indist_min_b <= 0.90)
    checks["desaturation_valid_native_indist_le_0.90_somewhere"] = desat_valid

    # EROSION read on sweep A (primary): onset sigma where native in-dist first <= 0.95.
    onset = None
    for r in sa:
        if r["native_bind_shared_indist"] <= 0.95:
            onset = r
            break
    nat_ho_at_onset = onset["native_bind_shared_heldout"] if onset else base["native_bind_shared_heldout"]

    # collapse-before-cleanup-hard: held-out < 0.40 while in-dist still >= 0.90 (clean-only fragility)
    collapse_early = any(r["native_bind_shared_heldout"] < 0.40 and r["native_bind_shared_indist"] >= 0.90
                         for r in sa + sb)
    # robust tracking: at every level where in-dist >= 0.60, held-out >= 0.85 * in-dist (held-out
    # erodes no faster than in-dist) AND native beats tied by >= 0.30.
    robust = True
    for r in sa + sb:
        ind = r["native_bind_shared_indist"]
        ho = r["native_bind_shared_heldout"]
        tho = r["native_bind_tied_heldout"]
        if ind >= 0.60:
            if ho < 0.85 * ind - 0.05:
                robust = False
            if ho < tho + 0.30:
                robust = False
    checks["native_beats_tied_where_cleanup_ok"] = robust

    hard_fail = (not checks["positive_control_native_indist_ge_0.95"]
                 or not checks["positive_control_native_heldout_ge_0.90"]
                 or not checks["flat_heldout_lt_0.30_all_levels"]
                 or not checks["scramble_heldout_le_0.20_all_levels"])

    if hard_fail:
        verdict = "HARD_FAIL"
    elif not desat_valid:
        verdict = "INCONCLUSIVE_REGIME_TOO_EASY"
    elif collapse_early:
        verdict = "CLEAN_REGIME_ONLY"
    elif robust and nat_ho_at_onset >= 0.70:
        verdict = "CG_ROBUST"
    else:
        verdict = "GRACEFUL_EROSION"

    msg = ("verdict=%s | base(nat_ind=%.3f nat_ho=%.3f flat_ho=%.3f) | "
           "sweepA nat_indist_min=%.3f nat_ho_at_onset=%.3f | sweepB nat_indist_min=%.3f | "
           "flat_ho_max=%.3f scr_ho_max=%.3f desat_valid=%s collapse_early=%s robust=%s"
           % (verdict, base["native_bind_shared_indist"], base["native_bind_shared_heldout"],
              base["flat_heldout"], nat_indist_min_a, nat_ho_at_onset, nat_indist_min_b,
              flat_ho_max, scr_ho_max, desat_valid, collapse_early, robust))
    extra = {"nat_indist_min_sweepA": round(nat_indist_min_a, 4),
             "nat_indist_min_sweepB": round(nat_indist_min_b, 4),
             "nat_heldout_at_onset_sweepA": round(nat_ho_at_onset, 4),
             "desaturation_valid": desat_valid, "collapse_early": collapse_early,
             "robust_tracking": robust}
    return verdict, msg, checks, extra


# ------------------------------ run ------------------------------
def run(cfg, run_mode):
    t0 = time.perf_counter()
    seeds = cfg["seeds"]
    per_a = []   # sweep A rows: {sigma, seed, arm, indist, heldout}
    per_b = []   # sweep B rows: {n_dim, n_fill, n_verb, seed, arm, indist, heldout}
    curves = {}  # representative learning curves
    sigs_base = {}  # arm -> sig on base regime, seed0, for arms-differ

    s0 = seeds[0]
    # ---- BASE regime trained ONCE per seed (reused for SWEEP A + SWEEP B level 0) ----
    nd0, nf0, nv0 = BASE_REGIME
    for seed in seeds:
        train, indist, heldout = make_dataset(seed, nf0, nv0, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
        base_models = {}
        for arm in ARMS_TRAIN:
            codebook, roles = fixed_codebook(seed, nd0, nf0, nv0)
            model, curve, sig = train_arm(arm, cfg, codebook, roles, seed, nf0, nv0, train, indist, heldout)
            base_models[arm] = model
            if seed == s0:
                sigs_base[arm] = sig
                if arm == "native_bind_shared":
                    curves["sweepA_base_native"] = curve
            print("[base seed=%d %s] trained (indist=%.3f heldout=%.3f)"
                  % (seed, arm, eval_indist(model, indist), eval_heldout(model, heldout)), flush=True)

        # SWEEP A: eval base models under additive noise
        for si, sigma in enumerate(cfg["sweep_a_sigmas"]):
            for arm in ARMS_TRAIN:
                m = base_models[arm]
                gi = _noise_gen(seed, si) if sigma > 0 else None
                gh = _noise_gen(seed, si + 1000) if sigma > 0 else None
                ind = eval_indist(m, indist, sigma=sigma, gen=gi)
                ho = eval_heldout(m, heldout, sigma=sigma, gen=gh)
                per_a.append({"sigma": sigma, "seed": seed, "arm": arm,
                              "indist": ind, "heldout": ho})
            # scramble lesion of the trained shared model under same noise
            g = torch.Generator().manual_seed(seed + 424242)
            two_pi = 2.0 * np.pi
            dr = torch.exp(1j * (torch.rand(3, nd0, generator=g) * two_pi)).to(torch.complex64)
            gi = _noise_gen(seed, si + 2000) if sigma > 0 else None
            gh = _noise_gen(seed, si + 3000) if sigma > 0 else None
            m = base_models["native_bind_shared"]
            ind_s = eval_indist(m, indist, sigma=sigma, gen=gi, decode_roles=dr)
            ho_s = eval_heldout(m, heldout, sigma=sigma, gen=gh, decode_roles=dr)
            per_a.append({"sigma": sigma, "seed": seed, "arm": "native_bind_scramble",
                          "indist": ind_s, "heldout": ho_s})
        # SWEEP B level 0 = base (reuse clean evals)
        for arm in ARMS_TRAIN:
            m = base_models[arm]
            per_b.append({"n_dim": nd0, "n_fill": nf0, "n_verb": nv0, "seed": seed, "arm": arm,
                          "indist": eval_indist(m, indist), "heldout": eval_heldout(m, heldout)})
        g = torch.Generator().manual_seed(seed + 424242)
        two_pi = 2.0 * np.pi
        dr = torch.exp(1j * (torch.rand(3, nd0, generator=g) * two_pi)).to(torch.complex64)
        m = base_models["native_bind_shared"]
        per_b.append({"n_dim": nd0, "n_fill": nf0, "n_verb": nv0, "seed": seed,
                      "arm": "native_bind_scramble", "indist": eval_indist(m, indist, decode_roles=dr),
                      "heldout": eval_heldout(m, heldout, decode_roles=dr)})
        print("[sweepA+base done seed=%d]" % seed, flush=True)

    # ---- SWEEP B: harder regimes (skip base, already done) ----
    hardest = cfg["sweep_b_regimes"][-1]
    for (nd, nf, nv) in cfg["sweep_b_regimes"]:
        if (nd, nf, nv) == BASE_REGIME:
            continue
        for seed in seeds:
            train, indist, heldout = make_dataset(seed, nf, nv, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
            reg_models = {}
            for arm in ARMS_TRAIN:
                codebook, roles = fixed_codebook(seed, nd, nf, nv)
                model, curve, _ = train_arm(arm, cfg, codebook, roles, seed, nf, nv, train, indist, heldout)
                reg_models[arm] = model
                per_b.append({"n_dim": nd, "n_fill": nf, "n_verb": nv, "seed": seed, "arm": arm,
                              "indist": eval_indist(model, indist), "heldout": eval_heldout(model, heldout)})
                if seed == s0 and (nd, nf, nv) == hardest and arm == "native_bind_shared":
                    curves["sweepB_hardest_native"] = curve
            g = torch.Generator().manual_seed(seed + 424242)
            two_pi = 2.0 * np.pi
            dr = torch.exp(1j * (torch.rand(3, nd, generator=g) * two_pi)).to(torch.complex64)
            m = reg_models["native_bind_shared"]
            per_b.append({"n_dim": nd, "n_fill": nf, "n_verb": nv, "seed": seed,
                          "arm": "native_bind_scramble",
                          "indist": eval_indist(m, indist, decode_roles=dr),
                          "heldout": eval_heldout(m, heldout, decode_roles=dr)})
            print("[sweepB N=%d V=%d seed=%d done]" % (nd, nf, seed), flush=True)

    # arms-differ (META_RULE_AF) on base regime seed0 signatures (+ scramble sig)
    g = torch.Generator().manual_seed(s0 + 424242)
    two_pi = 2.0 * np.pi
    train, indist, heldout = make_dataset(s0, nf0, nv0, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
    dr = torch.exp(1j * (torch.rand(3, nd0, generator=g) * two_pi)).to(torch.complex64)
    # rebuild base shared model sig under scramble decode for a distinct hash
    codebook, roles = fixed_codebook(s0, nd0, nf0, nv0)
    tmp_native = build_model("native_bind_shared", codebook, roles, s0, nf0, nv0)
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = tmp_native(pa, pp, pv, decode_roles=dr)
        sigs_base["native_bind_scramble"] = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    digests = {arm: hashlib.sha256(sigs_base[arm].tobytes()).hexdigest() for arm in ARMS}
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            assert digests[ARMS[i]] != digests[ARMS[j]], (
                "META_RULE_AF VIOLATION: arms %s and %s bit-identical" % (ARMS[i], ARMS[j]))

    sa = summarize_sweep_a(per_a)
    sb = summarize_sweep_b(per_b)
    verdict, msg, checks, extra = compute_verdict(sa, sb)
    elapsed = time.perf_counter() - t0

    expected_units = (len(cfg["sweep_a_sigmas"]) * len(seeds) * len(ARMS)
                      + len(cfg["sweep_b_regimes"]) * len(seeds) * len(ARMS))
    n_units = len(per_a) + len(per_b)
    cardinality_ok = n_units == expected_units

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": "compgen de-saturation sweep: " + verdict,
        "elapsed_s": round(elapsed, 2),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "base_regime": {"n_dim": nd0, "n_fill": nf0, "n_verb": nv0, "chance": round(1.0 / nf0, 4)},
        "sweep_A_noise": sa,
        "sweep_B_orthogonality": sb,
        "verdict_checks": checks,
        "verdict_extra": extra,
        "learning_curves": curves,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "arms_digests": digests,
        "config": {k: (v if not isinstance(v, list) or k != "sweep_b_regimes" else [list(t) for t in v])
                   for k, v in cfg.items()},
        "per_a": per_a,
        "per_b": per_b,
    }
    return metrics


def _atomic_write(metrics):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)
    return final


def _write_crash_metrics(exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
        "summary": "CELL_CRASHED: " + type(exc).__name__,
        "elapsed_s": 0.0,
        "run_mode": "crash",
        "anchor_name": ANCHOR_NAME,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tmp = os.path.join(OUTPUT_DIR, "metrics.json.tmp")
    final = os.path.join(OUTPUT_DIR, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ------------------------------ self-test ------------------------------
def self_test():
    print("[self-test] start", flush=True)
    two_pi = 2.0 * np.pi
    nd0, nf0, nv0 = BASE_REGIME

    # 1. FHRR involution
    codebook, roles = fixed_codebook(7, nd0, nf0, nv0)
    c = codebook[3]
    rec = (c * roles[0]) * roles[0].conj()
    cos = (rec @ c.conj()).real.item() / nd0
    assert cos > 0.99, "involution failed cos=%.4f" % cos
    print("[self-test] involution cos=%.4f OK" % cos, flush=True)

    # 2. SCRAMBLE FIRES + NOISE DEGRADES cleanup monotonically (the de-sat knob works)
    prop = codebook[3] * roles[0] + codebook[5] * roles[1]
    cb_conj = codebook.conj()
    correct = ((prop * roles[0].conj()) @ cb_conj.T).real / nd0
    assert correct.argmax().item() == 3, "correct-role decode failed"
    g = torch.Generator().manual_seed(123)
    rr = torch.exp(1j * (torch.rand(nd0, generator=g) * two_pi)).to(torch.complex64)
    scram = ((prop * rr.conj()) @ cb_conj.T).real / nd0
    assert abs(scram.max().item()) < 0.2, "scramble did not collapse: %.3f" % scram.max().item()
    # noise: build a NativeBind, verify in-dist decreases as sigma rises on a tiny probe
    print("[self-test] scramble collapse OK", flush=True)

    # 3. SPLIT INTEGRITY at two regimes (base + a hard one)
    for (nd, nf, nv) in [BASE_REGIME, (128, 96, 24)]:
        both, agent_only, patient_only, gsz = concept_groups(nf)
        assert len(set(both) & set(agent_only)) == 0 and len(set(both) & set(patient_only)) == 0
        train, indist, heldout = make_dataset(7, nf, nv, 500, 150, 120)
        seen_agent = set(a for (a, p, v) in train)
        seen_patient = set(p for (a, p, v) in train)
        for (a, p, v, novel) in heldout:
            if novel == 0:
                assert a not in seen_agent, "SPLIT BREACH agent %d (N=%d V=%d)" % (a, nd, nf)
                assert a in patient_only
            else:
                assert p not in seen_patient, "SPLIT BREACH patient %d (N=%d V=%d)" % (p, nd, nf)
                assert p in agent_only
        assert len(set((a, p, v) for (a, p, v) in indist) & set(train)) == 0, "indist leaks train"
    print("[self-test] split integrity OK (2 regimes)", flush=True)

    # 4. TINY RUN: de-sat gate fires + arms differ + noise actually erodes native in-dist
    tiny = dict(n_train=400, n_indist=120, n_heldout=80, epochs=25, eval_every=25,
                batch=128, lr=1e-2, seeds=[7],
                sweep_a_sigmas=[0.0, 48.0], sweep_b_regimes=[(1024, 24, 12), (64, 96, 24)])
    m = run(tiny, "self_test")
    sa = m["sweep_A_noise"]
    base = sa[0]
    hi = sa[-1]   # sigma=48
    # base sigma=0 reproduces native strong / flat held-out weak
    assert base["native_bind_shared_indist"] > 0.90, "base native indist low: %.3f" % base["native_bind_shared_indist"]
    assert base["native_bind_shared_heldout"] > base["flat_heldout"], "native !> flat held-out at base"
    # noise ERODES native in-dist (de-saturation knob works)
    assert hi["native_bind_shared_indist"] < base["native_bind_shared_indist"] - 0.05, (
        "noise did not erode native in-dist: %.3f -> %.3f"
        % (base["native_bind_shared_indist"], hi["native_bind_shared_indist"]))
    # sweep B hard regime erodes native in-dist below base OR noise did (de-sat valid on some axis)
    sb = m["sweep_B_orthogonality"]
    nat_min_b = min(r["native_bind_shared_indist"] for r in sb)
    assert (nat_min_b <= 0.90) or (hi["native_bind_shared_indist"] <= 0.90), (
        "neither axis de-saturated (native in-dist stayed > 0.90): sweepB_min=%.3f sweepA_hi=%.3f"
        % (nat_min_b, hi["native_bind_shared_indist"]))
    # scramble stays low everywhere
    scr_max = max(max(r["native_bind_scramble_heldout"] for r in sa),
                  max(r["native_bind_scramble_heldout"] for r in sb))
    assert scr_max <= 0.25, "scramble held-out too high: %.3f" % scr_max
    assert len(set(m["arms_digests"].values())) == len(ARMS), "arms not all distinct"
    print("[self-test] de-sat gate OK (base nat_ind=%.3f -> sigma48 nat_ind=%.3f ; sweepB nat_min=%.3f)"
          % (base["native_bind_shared_indist"], hi["native_bind_shared_indist"], nat_min_b), flush=True)
    print("[self-test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    if args.self_test:
        self_test()
        sys.exit(0)

    cfg = SMOKE if args.smoke else FULL
    run_mode = "smoke" if args.smoke else "full"
    print("[run] mode=%s seeds=%s sigmas=%s regimes=%s"
          % (run_mode, cfg["seeds"], cfg["sweep_a_sigmas"], cfg["sweep_b_regimes"]), flush=True)
    metrics = run(cfg, run_mode)
    path = _atomic_write(metrics)
    print("[run] %s verdict=%s" % (path, metrics["verdict"]), flush=True)
    print("[run] " + metrics["verdict_msg"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(e)
        raise
