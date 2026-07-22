#!/usr/bin/env python
"""REAL-TEXT compositional-generalization test for native role-filler binding.

Follow-up to exp_compgen_native_bind_role_filler_v1 (HARD_PASS, synthetic near-orthogonal
codes) and exp_compgen_native_bind_desaturation_sweep_v1 (robust across synthetic difficulty).
Those showed native-bind + learned shared-emb factorization delivers ROBUST systematic compgen
on ABSTRACT random role-filler codes. The ONLY remaining bound: it was not REAL LANGUAGE.

QUESTION: does the LEARNED text->role encoder generalize to HELD-OUT (concept, role)
combinations on REAL FILLERS (real nouns with REAL WordNet lexical geometry) drawn from REAL
McGuffey text, where a FAIR LEARNED-FLAT baseline FAILS? Or does REAL lexical structure
(polysemy / frequency / non-orthogonality) erode native's edge (synthetic-only, honest bound)?

REAL FILLERS (the de-saturation the synthetic task lacked):
  - Real vocabulary + real role structure from McGuffey gold argument-structure annotations
    (data/gold_mcguffey_lccp_argstruct_v1.json + gold_mcguffey_castle_building_svo_v1.json),
    frozen into data/real_fillers_mcguffey_wordnet_v1.json.
  - Real EMBEDDING geometry: each noun's fixed FHRR code is built from its WordNet
    hypernym-closure feature vector (idf-weighted), so semantically similar nouns have
    NON-orthogonal codes (kitten~animals, castle~castles, father~papa). This real taxonomic
    geometry caps clean cleanup at ~0.94 (NOT the synthetic 1.0) = the de-saturation.
  - Real ROLE groups: attested corpus roles => both / agent_only / patient_only. The held-out
    split uses the real agent/patient asymmetry (animate nouns are agents, objects are patients).

GOLD-ROLE CONFOUND CONTROL (load-bearing; the VET hits this hardest): on real text, a held-out
FAILURE could be a bad PARSE (parser missed the patient) not "no compgen". This cell removes the
parse confound BY CONSTRUCTION: it feeds GOLD (agent, verb, patient) role structure to the
encoder (no parser in the loop). A held-out failure therefore means genuinely "no compositional
generalization", not "the parser mislabeled the role". A predicted-role arm (to show erosion
under parse noise) is DEFERRED -- no parser is integrated; the clean test is gold-role.

HELD-OUT COMBINATION (non-tautological): a noun attested only as AGENT in the corpus is tested
as PATIENT (and vice versa). The held-out (noun, novel-role) combination NEVER appears in
training in that role -> the answer is not a lookup. Split integrity asserted in self_test.

ARMS (one variable across A/B = readout binding-vs-flat; identical data + supervision; BOTH arms
consume the SAME real filler geometry):
  A native_bind_shared   : FHRR binding readout, SHARED noun-emb, real WordNet codebook  [MECHANISM]
  B flat                 : per-role classifier heads over a frozen REAL-FEATURE projection [FAIR BASELINE]
  C native_bind_scramble : A lesion (decode with random role keys)                        [MUST-FAIL]
  D native_bind_tied     : binding readout, role-SPECIFIC emb tables                       [FREE-ALGEBRA LOCUS]

DIFFICULTY KNOB: additive complex-Gaussian noise on the composed FHRR vector, sigma swept, to
trace whether native's real-filler edge is ROBUST (CG) or erodes (honest bound). (N is NOT a
de-sat knob here: the WordNet geometry is angle-only, so cleanup is dimension-flat; noise is the
erosion axis.)

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb: THEORETICAL clean cleanup ceiling ~0.94 set by real code degeneracy (castle/castles cos=1.0);
#   native in-dist HARD_PASS floor (0.85) sits BELOW the real ceiling and ABOVE chance (0.013). reachable.
# - baseline_in_band at smoke (flat in-dist high = fair+learnable; flat held-out low = structural)
# - discriminator survives scale: FULL N=1024 in smoke; single seed / fewer epochs / fewer sigmas
# - HARD_PASS strictly above floor
# - deterministic_seeding: fixed int seeds + sorted() splits + index-derived noise gen; NO hash()-seeded RNG
# - progress_logging: line_buffered_stdout (flush prints); wall << 30min (no timeout heartbeat needed)
# - all numbers MEASURED@ this cell's metrics.json (no hypothesized numbers in verdict)
# LOCAL-ONLY: no push, no store mutation, no atom bank. Skunkworks VETs after land.

Anchor: compgen_native_bind_real_text_v1
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

ANCHOR_NAME = "compgen_native_bind_real_text_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)
RF_PATH = os.path.join(REPO_ROOT, "data", "real_fillers_mcguffey_wordnet_v1.json")

# ------------------------------ fixed config ------------------------------
N_DIM = 1024            # FHRR dimensionality (phasor / complex64)
D_FLAT = 256            # flat hidden/proj dim (capacity fixed)
H_FLAT = 256
TEMP = 20.0             # logit temperature; /N normalization keeps it N-robust
DEVICE = "cpu"          # runner does not pass argv; tiny complex matmuls

# additive-noise sigma grid (erosion knob on real fillers). Cleanup transition ~ sqrt(N/lnV).
SWEEP_SIGMAS_FULL = [0.0, 4.0, 8.0, 12.0, 18.0, 24.0, 32.0]
SWEEP_SIGMAS_SMOKE = [0.0, 18.0, 32.0]

FULL = dict(n_train=1400, n_indist=350, n_heldout=280, epochs=60, eval_every=15,
            batch=256, lr=1e-2, seeds=[7, 13, 19], sigmas=SWEEP_SIGMAS_FULL)
SMOKE = dict(n_train=700, n_indist=200, n_heldout=140, epochs=25, eval_every=25,
             batch=256, lr=1e-2, seeds=[7], sigmas=SWEEP_SIGMAS_SMOKE)

ARMS_TRAIN = ["native_bind_shared", "flat", "native_bind_tied"]
ARMS = ["native_bind_shared", "flat", "native_bind_scramble", "native_bind_tied"]


# ------------------------------ real fillers ------------------------------
def load_real_fillers():
    """Load the frozen real-filler artifact (nouns, WordNet features, role groups, verbs, gold)."""
    with open(RF_PATH, "r", encoding="utf-8") as f:
        rf = json.load(f)
    nouns = rf["nouns"]
    n_fill = len(nouns)
    n_verb = len(rf["verbs"])
    n_feat = rf["n_features_total"]
    idx = {n: i for i, n in enumerate(nouns)}
    vidx = {v: i for i, v in enumerate(rf["verbs"])}
    # dense idf feature matrix (n_fill, n_feat)
    feat = np.zeros((n_fill, n_feat), dtype=np.float32)
    for n, i in idx.items():
        for fj, w in rf["noun_feats"][n]:
            feat[i, fj] = w
    role_group = [rf["role_group"][n] for n in nouns]
    both = sorted(i for i in range(n_fill) if role_group[i] == "both")
    agent_only = sorted(i for i in range(n_fill) if role_group[i] == "agent_only")
    patient_only = sorted(i for i in range(n_fill) if role_group[i] == "patient_only")
    # real gold tuples as index triples (real-text in-dist anchor)
    gold = [(idx[a], vidx[v], idx[p]) for (a, v, p) in rf["gold_tuples"]
            if a in idx and p in idx and v in vidx]
    return dict(nouns=nouns, n_fill=n_fill, n_verb=n_verb, n_feat=n_feat, feat=feat,
                both=both, agent_only=agent_only, patient_only=patient_only, gold=gold,
                meta=rf["_meta"])


def real_codebook(rf, seed):
    """Deterministic FHRR phasor codes from real WordNet feature vectors + fixed role vectors.
    code[n] = exp(i * angle(sum_f feat[n,f] * exp(i*phi_f))). Semantically similar nouns share
    features -> correlated (non-orthogonal) codes = the real lexical geometry."""
    g = np.random.default_rng(seed + 100003)
    phi = g.uniform(0.0, 2.0 * np.pi, size=(rf["n_feat"], N_DIM)).astype(np.float32)
    feat = rf["feat"]                                       # (n_fill, n_feat)
    z = feat @ np.exp(1j * phi)                             # (n_fill, N) complex
    ang = np.angle(z).astype(np.float32)
    codebook = torch.from_numpy(np.exp(1j * ang).astype(np.complex64))
    tg = torch.Generator().manual_seed(seed + 100003)
    role_phase = torch.rand(3, N_DIM, generator=tg) * (2.0 * np.pi)   # 0=AGENT 1=PATIENT 2=VERB
    roles = torch.exp(1j * role_phase.to(torch.float32)).to(torch.complex64)
    real_feat = torch.from_numpy(feat)                     # frozen real-feature input for flat
    return codebook, roles, real_feat


# ------------------------------ dataset ------------------------------
def make_dataset(rf, seed, n_train, n_indist, n_heldout):
    """Train / in-dist / held-out-combination over REAL vocab + REAL role groups.
    Held-out = NOVEL (noun, role): a noun attested only as agent tested as patient (and v.v.).
    Non-tautological (the held-out noun-in-that-role never appears in training)."""
    rng = np.random.default_rng(seed)
    both, agent_only, patient_only = rf["both"], rf["agent_only"], rf["patient_only"]
    n_verb = rf["n_verb"]
    train_agents = sorted(both + agent_only)
    train_patients = sorted(both + patient_only)

    def sample_triples(n, agent_pool, patient_pool, seen=None):
        out, guard = [], 0
        seen = set() if seen is None else set(seen)
        while len(out) < n and guard < n * 400:
            guard += 1
            a = int(rng.choice(agent_pool)); p = int(rng.choice(patient_pool))
            v = int(rng.integers(0, n_verb))
            if a == p:
                continue
            key = (a, p, v)
            if key in seen:
                continue
            seen.add(key); out.append(key)
        return out

    train = sample_triples(n_train, train_agents, train_patients)
    train_set = set(train)
    indist = sample_triples(n_indist, train_agents, train_patients, seen=train_set)
    n_half = n_heldout // 2
    ho_a = sample_triples(n_half, patient_only, train_patients)      # novel role = AGENT (0)
    ho_p = sample_triples(n_heldout - n_half, train_agents, agent_only)  # novel role = PATIENT (1)
    heldout = [(a, p, v, 0) for (a, p, v) in ho_a] + [(a, p, v, 1) for (a, p, v) in ho_p]
    if len(train) < 0.5 * n_train or len(indist) == 0 or len(heldout) == 0:
        raise RuntimeError("DATASET_UNDERFILLED seed=%d train=%d/%d indist=%d/%d heldout=%d/%d"
                           % (seed, len(train), n_train, len(indist), n_indist, len(heldout), n_heldout))
    return train, indist, heldout


# ------------------------------ models ------------------------------
class NativeBind(torch.nn.Module):
    """FHRR binding readout on the REAL codebook. shared=True: one learned noun-emb table;
    shared=False (tied): role-specific tables. scramble=True: PATIENT role := AGENT role."""

    def __init__(self, codebook, roles, seed, n_verb, shared=True, scramble=False):
        super().__init__()
        self.register_buffer("codebook", codebook)             # (V, N) complex fixed (REAL geometry)
        r = roles.clone()
        if scramble:
            r[1] = r[0]
        self.register_buffer("roles", r)                       # (3, N) complex fixed
        self.shared = shared
        self.n_dim = codebook.shape[1]
        self.n_fill = codebook.shape[0]
        g = torch.Generator().manual_seed(seed + 7)
        two_pi = 2.0 * np.pi
        if shared:
            self.theta_emb = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
        else:
            self.theta_emb_a = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
            self.theta_emb_p = torch.nn.Parameter(torch.rand(self.n_fill, self.n_dim, generator=g) * two_pi)
        self.theta_verb = torch.nn.Parameter(torch.rand(n_verb, self.n_dim, generator=g) * two_pi)

    def _emb(self, theta, idx):
        return torch.exp(1j * theta[idx])

    def forward(self, a, p, v, decode_roles=None, noise_sigma=0.0, noise_gen=None):
        if self.shared:
            ea = self._emb(self.theta_emb, a); ep = self._emb(self.theta_emb, p)
        else:
            ea = self._emb(self.theta_emb_a, a); ep = self._emb(self.theta_emb_p, p)
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
        qa = prop * dr[0].conj(); qp = prop * dr[1].conj()
        logits_a = (qa @ cb_conj.T).real / self.n_dim * TEMP
        logits_p = (qp @ cb_conj.T).real / self.n_dim * TEMP
        return logits_a, logits_p


class Flat(torch.nn.Module):
    """FAIR strong baseline: consumes the SAME real fillers (frozen real-feature projection),
    role-sorted inputs, per-role classifier heads. Aces in-dist; fails held-out (concept, role)
    because a role head gets no gradient for a concept never seen in that role."""

    def __init__(self, seed, real_feat, n_verb):
        super().__init__()
        torch.manual_seed(seed + 11)
        self.register_buffer("real_feat", real_feat)           # (n_fill, n_feat) frozen REAL fillers
        n_feat = real_feat.shape[1]
        self.proj_noun = torch.nn.Linear(n_feat, D_FLAT)       # learned projection of real features
        self.emb_verb = torch.nn.Embedding(n_verb, D_FLAT)
        self.mlp = torch.nn.Sequential(torch.nn.Linear(3 * D_FLAT, H_FLAT), torch.nn.ReLU(),
                                       torch.nn.Linear(H_FLAT, H_FLAT), torch.nn.ReLU())
        self.head_agent = torch.nn.Linear(H_FLAT, real_feat.shape[0])
        self.head_patient = torch.nn.Linear(H_FLAT, real_feat.shape[0])

    def forward(self, a, p, v, decode_roles=None, noise_sigma=0.0, noise_gen=None):
        na = self.proj_noun(self.real_feat[a]); np_ = self.proj_noun(self.real_feat[p])
        x = torch.cat([na, np_, self.emb_verb(v)], dim=-1)     # role-sorted
        h = self.mlp(x)
        return self.head_agent(h), self.head_patient(h)


def build_model(arm, codebook, roles, real_feat, seed, n_verb):
    if arm == "native_bind_shared":
        return NativeBind(codebook, roles, seed, n_verb, shared=True, scramble=False)
    if arm == "native_bind_scramble":
        return NativeBind(codebook, roles, seed, n_verb, shared=True, scramble=True)
    if arm == "native_bind_tied":
        return NativeBind(codebook, roles, seed, n_verb, shared=False, scramble=False)
    if arm == "flat":
        return Flat(seed, real_feat, n_verb)
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


def eval_gold(model, gold):
    """Real-text anchor: accuracy on ACTUAL attested gold (agent, verb, patient) tuples (in-dist)."""
    if not gold:
        return float("nan")
    return eval_indist(model, [(a, p, v) for (a, v, p) in gold])


def train_arm(arm, cfg, codebook, roles, real_feat, seed, n_verb, train, indist, heldout):
    model = build_model(arm, codebook, roles, real_feat, seed, n_verb).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    lossfn = torch.nn.CrossEntropyLoss()
    a_all, p_all, v_all = _tensorize(train)
    n = a_all.shape[0]
    ind0 = eval_indist(model, indist); ho0 = eval_heldout(model, heldout)
    curve = [{"epoch": 0, "indist": round(ind0, 4), "heldout": round(ho0, 4)}]
    g = torch.Generator().manual_seed(seed + 999)
    for ep in range(1, cfg["epochs"] + 1):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, cfg["batch"]):
            idx = perm[i:i + cfg["batch"]]
            la, lp = model(a_all[idx], p_all[idx], v_all[idx])
            loss = lossfn(la, a_all[idx]) + lossfn(lp, p_all[idx])
            opt.zero_grad(); loss.backward(); opt.step()
        if ep <= 5 or ep % cfg["eval_every"] == 0 or ep == cfg["epochs"]:
            ind = eval_indist(model, indist); ho = eval_heldout(model, heldout)
            curve.append({"epoch": ep, "indist": round(ind, 4), "heldout": round(ho, 4)})
            print("[%s seed=%d] ep=%d indist=%.3f heldout=%.3f" % (arm, seed, ep, ind, ho), flush=True)
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = model(pa, pp, pv)
        sig = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    return model, curve, sig


# ------------------------------ verdict ------------------------------
def _agg(rows, key):
    return float(np.mean([r[key] for r in rows])) if rows else float("nan")


def summarize_sweep(per):
    """per: list of {sigma, seed, arm, indist, heldout}. -> per-sigma aggregate dicts (sorted)."""
    out = []
    for s in sorted(set(r["sigma"] for r in per)):
        row = {"sigma": s}
        for arm in ARMS:
            rr = [r for r in per if r["sigma"] == s and r["arm"] == arm]
            row[arm + "_indist"] = round(_agg(rr, "indist"), 4)
            row[arm + "_heldout"] = round(_agg(rr, "heldout"), 4)
        out.append(row)
    return out


def compute_verdict(sw, gold_agg, curve_agg):
    """sw: per-sigma aggregates (sorted asc). gold_agg: {arm: mean gold in-dist}.
       curve_agg: {arm: (heldout_init, heldout_final)}. Classify real-text CG vs honest bound."""
    base = sw[0]                                   # sigma=0 clean real-filler regime
    nb_ind = base["native_bind_shared_indist"]; nb_ho = base["native_bind_shared_heldout"]
    fl_ind = base["flat_indist"]; fl_ho = base["flat_heldout"]
    sc_ho = base["native_bind_scramble_heldout"]; ti_ho = base["native_bind_tied_heldout"]
    gap = nb_ho - fl_ho
    ho_init, ho_final = curve_agg["native_bind_shared"]
    rise = ho_final - ho_init

    # de-saturation: real geometry must cap native in-dist below saturation (< 0.98)
    desat_valid = nb_ind <= 0.98
    # robustness on the noise sweep: where cleanup still works (in-dist>=0.60), held-out tracks it
    robust = True
    for r in sw:
        ind = r["native_bind_shared_indist"]; ho = r["native_bind_shared_heldout"]
        if ind >= 0.60 and ho < 0.85 * ind - 0.05:
            robust = False
    # noise erodes native in-dist somewhere (erosion knob works)
    erosion_works = min(r["native_bind_shared_indist"] for r in sw) < nb_ind - 0.05

    checks = {
        "native_heldout_ge_0.65": nb_ho >= 0.65,
        "flat_heldout_le_0.40": fl_ho <= 0.40,
        "gap_ge_0.30": gap >= 0.30,
        "native_indist_ge_0.85": nb_ind >= 0.85,
        "flat_indist_ge_0.85": fl_ind >= 0.85,
        "learning_curve_rises_ge_0.30": rise >= 0.30,
        "native_heldout_init_lt_0.55": ho_init < 0.55,          # not free-algebra
        "scramble_collapses_le_0.10": sc_ho <= 0.10,            # binding load-bearing
        "tied_fails_heldout_le_0.45": ti_ho <= 0.45,           # shared-emb factorization load-bearing
        "desaturation_valid_native_indist_le_0.98": desat_valid,
        "native_tracks_indist_on_noise_sweep": robust,
    }
    hard_fail = (nb_ho <= 0.40 or gap <= 0.10 or fl_ho >= 0.60 or sc_ho > 0.20
                 or nb_ind < 0.60 or fl_ind < 0.70)
    hard_pass = all(checks.values())
    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "CG_ROBUST_REAL_TEXT"
    else:
        verdict = "MIDDLE_BAND"
    msg = ("verdict=%s | REAL-FILLER clean: native(ind=%.3f ho=%.3f) flat(ind=%.3f ho=%.3f) "
           "gap=%.3f rise=%.3f init=%.3f scramble_ho=%.3f tied_ho=%.3f | gold_indist(nb=%.3f fl=%.3f) | "
           "desat_valid=%s erosion_works=%s robust=%s"
           % (verdict, nb_ind, nb_ho, fl_ind, fl_ho, gap, rise, ho_init, sc_ho, ti_ho,
              gold_agg.get("native_bind_shared", float("nan")), gold_agg.get("flat", float("nan")),
              desat_valid, erosion_works, robust))
    extra = {"gap_native_minus_flat_heldout": round(gap, 4),
             "native_heldout_learning_rise": round(rise, 4),
             "desaturation_valid": desat_valid, "erosion_works": erosion_works,
             "robust_tracking": robust,
             "native_indist_min_over_sweep": round(min(r["native_bind_shared_indist"] for r in sw), 4)}
    return verdict, msg, checks, extra


# ------------------------------ run ------------------------------
def run(cfg, run_mode):
    t0 = time.perf_counter()
    rf = load_real_fillers()
    seeds = cfg["seeds"]; s0 = seeds[0]
    per = []            # sweep rows: {sigma, seed, arm, indist, heldout}
    gold_rows = {}      # arm -> list of gold in-dist acc per seed
    curve_rows = {}     # arm -> list of (init, final) heldout per seed
    curves = {}
    sigs = {}

    for seed in seeds:
        train, indist, heldout = make_dataset(rf, seed, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
        models = {}
        for arm in ARMS_TRAIN:
            codebook, roles, real_feat = real_codebook(rf, seed)
            model, curve, sig = train_arm(arm, cfg, codebook, roles, real_feat, seed, rf["n_verb"],
                                          train, indist, heldout)
            models[arm] = model
            curve_rows.setdefault(arm, []).append((curve[0]["heldout"], curve[-1]["heldout"]))
            gold_rows.setdefault(arm, []).append(eval_gold(model, rf["gold"]))
            if seed == s0:
                sigs[arm] = sig
                if arm == "native_bind_shared":
                    curves["native_learning_curve"] = curve
            print("[trained seed=%d %s] indist=%.3f heldout=%.3f gold=%.3f"
                  % (seed, arm, eval_indist(model, indist), eval_heldout(model, heldout),
                     eval_gold(model, rf["gold"])), flush=True)

        # noise sweep on trained models (real fillers + additive noise)
        for si, sigma in enumerate(cfg["sigmas"]):
            for arm in ARMS_TRAIN:
                m = models[arm]
                gi = _noise_gen(seed, si) if sigma > 0 else None
                gh = _noise_gen(seed, si + 1000) if sigma > 0 else None
                per.append({"sigma": sigma, "seed": seed, "arm": arm,
                            "indist": eval_indist(m, indist, sigma=sigma, gen=gi),
                            "heldout": eval_heldout(m, heldout, sigma=sigma, gen=gh)})
            # scramble lesion of the trained shared model (random role keys) under same noise
            g = torch.Generator().manual_seed(seed + 424242)
            dr = torch.exp(1j * (torch.rand(3, N_DIM, generator=g) * (2.0 * np.pi))).to(torch.complex64)
            gi = _noise_gen(seed, si + 2000) if sigma > 0 else None
            gh = _noise_gen(seed, si + 3000) if sigma > 0 else None
            m = models["native_bind_shared"]
            per.append({"sigma": sigma, "seed": seed, "arm": "native_bind_scramble",
                        "indist": eval_indist(m, indist, sigma=sigma, gen=gi, decode_roles=dr),
                        "heldout": eval_heldout(m, heldout, sigma=sigma, gen=gh, decode_roles=dr)})
            if seed == s0 and sigma == 0.0:
                gold_rows.setdefault("native_bind_scramble", []).append(
                    eval_gold(m, [(a, v, p) for (a, v, p) in rf["gold"]]))
        print("[sweep done seed=%d]" % seed, flush=True)

    # arms-differ (META_RULE_AF): distinct scramble signature on seed0 clean probe
    codebook, roles, real_feat = real_codebook(rf, s0)
    g = torch.Generator().manual_seed(s0 + 424242)
    dr = torch.exp(1j * (torch.rand(3, N_DIM, generator=g) * (2.0 * np.pi))).to(torch.complex64)
    train, indist, heldout = make_dataset(rf, s0, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
    tmp_native = build_model("native_bind_shared", codebook, roles, real_feat, s0, rf["n_verb"])
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = tmp_native(pa, pp, pv, decode_roles=dr)
        sigs["native_bind_scramble"] = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    digests = {arm: hashlib.sha256(sigs[arm].tobytes()).hexdigest() for arm in ARMS}
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            assert digests[ARMS[i]] != digests[ARMS[j]], (
                "META_RULE_AF VIOLATION: arms %s and %s bit-identical" % (ARMS[i], ARMS[j]))

    sw = summarize_sweep(per)
    gold_agg = {arm: float(np.nanmean(v)) for arm, v in gold_rows.items()}
    curve_agg = {arm: (float(np.mean([x[0] for x in v])), float(np.mean([x[1] for x in v])))
                 for arm, v in curve_rows.items()}
    verdict, msg, checks, extra = compute_verdict(sw, gold_agg, curve_agg)
    elapsed = time.perf_counter() - t0

    expected_units = len(cfg["sigmas"]) * len(seeds) * len(ARMS)
    n_units = len(per)
    cardinality_ok = n_units == expected_units

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": "compgen native-bind REAL-TEXT: " + verdict,
        "elapsed_s": round(elapsed, 2),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "chance": round(1.0 / rf["n_fill"], 4),
        "real_fillers_meta": rf["meta"],
        "n_fill": rf["n_fill"], "n_verb": rf["n_verb"], "n_gold_tuples": len(rf["gold"]),
        "role_group_counts": {"both": len(rf["both"]), "agent_only": len(rf["agent_only"]),
                              "patient_only": len(rf["patient_only"])},
        "sweep_noise": sw,
        "gold_indist_by_arm": {k: round(v, 4) for k, v in gold_agg.items()},
        "heldout_curve_by_arm": {k: [round(x, 4) for x in v] for k, v in curve_agg.items()},
        "verdict_checks": checks,
        "verdict_extra": extra,
        "learning_curves": curves,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": n_units,
        "arms_digests": digests,
        "config": {k: v for k, v in cfg.items()},
        "per_unit": per,
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
        "elapsed_s": 0.0, "run_mode": "crash", "anchor_name": ANCHOR_NAME,
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
    rf = load_real_fillers()
    assert rf["n_fill"] >= 60, "too few real nouns: %d" % rf["n_fill"]
    assert len(rf["agent_only"]) >= 10 and len(rf["patient_only"]) >= 20, "role groups too small"
    print("[self-test] real fillers: n_fill=%d n_verb=%d n_gold=%d groups(both=%d ao=%d po=%d)"
          % (rf["n_fill"], rf["n_verb"], len(rf["gold"]), len(rf["both"]),
             len(rf["agent_only"]), len(rf["patient_only"])), flush=True)

    # 1. REAL codebook is non-orthogonal (de-saturation lever present) + involution holds
    codebook, roles, real_feat = real_codebook(rf, 7)
    c = codebook[3]
    cos = ((c * roles[0]) * roles[0].conj() @ c.conj()).real.item() / N_DIM
    assert cos > 0.99, "involution failed cos=%.4f" % cos
    G = (codebook @ codebook.conj().T).real / N_DIM
    mask = ~torch.eye(rf["n_fill"], dtype=torch.bool)
    off_mean = G[mask].abs().mean().item()
    rand_ref = 1.0 / np.sqrt(N_DIM)
    assert off_mean > 1.3 * rand_ref, "real codebook not non-orthogonal enough: %.4f vs rand %.4f" % (
        off_mean, rand_ref)
    # clean cleanup over real codes must be de-saturated (< 0.99, real geometry bites)
    cbc = codebook.conj()
    rng = np.random.default_rng(1); hit = 0; tot = 0
    for _ in range(600):
        a = rng.integers(0, rf["n_fill"]); p = rng.integers(0, rf["n_fill"])
        prop = codebook[a] * roles[0] + codebook[p] * roles[1]
        la = ((prop * roles[0].conj()) @ cbc.T).real
        hit += int(la.argmax().item() == a); tot += 1
    clean_ceiling = hit / tot
    assert clean_ceiling < 0.99, "real geometry did not de-saturate cleanup: %.3f" % clean_ceiling
    assert clean_ceiling > 0.80, "real geometry too degenerate to learn: %.3f" % clean_ceiling
    print("[self-test] real codebook off|cos|=%.4f (rand=%.4f) clean_cleanup_ceiling=%.3f OK"
          % (off_mean, rand_ref, clean_ceiling), flush=True)

    # 2. SCRAMBLE FIRES: random role key collapses decode
    prop = codebook[3] * roles[0] + codebook[5] * roles[1]
    g = torch.Generator().manual_seed(123)
    rr = torch.exp(1j * (torch.rand(N_DIM, generator=g) * (2.0 * np.pi))).to(torch.complex64)
    scram = ((prop * rr.conj()) @ cbc.T).real / N_DIM
    assert abs(scram.max().item()) < 0.2, "scramble did not collapse: %.3f" % scram.max().item()
    print("[self-test] scramble collapse OK", flush=True)

    # 3. SPLIT INTEGRITY: no held-out (noun, novel_role) appears in train in that role
    train, indist, heldout = make_dataset(rf, 7, 700, 200, 140)
    seen_agent = set(a for (a, p, v) in train)
    seen_patient = set(p for (a, p, v) in train)
    ao, po = set(rf["agent_only"]), set(rf["patient_only"])
    for (a, p, v, novel) in heldout:
        if novel == 0:                                      # AGENT slot is the novel test
            assert a not in seen_agent, "SPLIT BREACH: heldout agent %d seen as agent in train" % a
            assert a in po, "heldout novel-agent %d not from patient_only" % a
        else:                                               # PATIENT slot novel
            assert p not in seen_patient, "SPLIT BREACH: heldout patient %d seen as patient in train" % p
            assert p in ao, "heldout novel-patient %d not from agent_only" % p
    assert len(set(train) & set((a, p, v) for (a, p, v) in indist)) == 0, "indist leaks train"
    print("[self-test] split integrity OK (train=%d indist=%d heldout=%d)"
          % (len(train), len(indist), len(heldout)), flush=True)

    # 4. TINY RUN: learning curve rises, native beats flat held-out, arms differ, noise erodes
    tiny = dict(n_train=400, n_indist=120, n_heldout=80, epochs=25, eval_every=25,
                batch=128, lr=1e-2, seeds=[7], sigmas=[0.0, 32.0])
    m = run(tiny, "self_test")
    sw = m["sweep_noise"]; base = sw[0]; hi = sw[-1]
    nb_ind = base["native_bind_shared_indist"]; nb_ho = base["native_bind_shared_heldout"]
    fl_ho = base["flat_heldout"]
    init, final = m["heldout_curve_by_arm"]["native_bind_shared"]
    assert init < 0.35, "native heldout not near-chance at init: %.3f" % init
    assert final > init + 0.20, "native heldout did not rise: %.3f->%.3f" % (init, final)
    assert nb_ho > fl_ho, "native !> flat held-out (%.3f vs %.3f)" % (nb_ho, fl_ho)
    assert nb_ind <= 0.98, "native in-dist saturated (real geometry should cap it): %.3f" % nb_ind
    assert hi["native_bind_shared_indist"] < nb_ind - 0.03, "noise did not erode native in-dist: %.3f->%.3f" % (
        nb_ind, hi["native_bind_shared_indist"])
    scr_max = max(r["native_bind_scramble_heldout"] for r in sw)
    assert scr_max <= 0.25, "scramble held-out too high: %.3f" % scr_max
    assert len(set(m["arms_digests"].values())) == len(ARMS), "arms not all distinct"
    print("[self-test] run OK (native ind=%.3f ho=%.3f flat_ho=%.3f rise %.3f->%.3f noise->ind=%.3f)"
          % (nb_ind, nb_ho, fl_ho, init, final, hi["native_bind_shared_indist"]), flush=True)
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
    print("[run] mode=%s seeds=%s sigmas=%s" % (run_mode, cfg["seeds"], cfg["sigmas"]), flush=True)
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
