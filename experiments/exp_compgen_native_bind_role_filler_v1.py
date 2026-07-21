#!/usr/bin/env python
"""Layer-1 component #1 CAN-FAIL cell: compositional generalization via native role-filler binding.

QUESTION: does a LEARNED text->role encoder that outputs into a FIXED VSA (FHRR) binding
space generalize to HELD-OUT (filler, role) combinations where a FAIR LEARNED-FLAT baseline
(same capacity + training + supervision) FAILS?

The LOCUS of any win must be the LEARNED encoder (the noun->concept embedding learned from
supervision), NOT the free binding algebra. Guards:
  - learning curve: held-out compgen accuracy RISES from ~chance with training (learned, not free)
  - arm D (role-tied emb): binding ON but role-specific embeddings FAILS held-out
    => the free algebra alone does NOT solve compgen; the learned SHARED-embedding factorization is
    load-bearing. This is a live alternative where native-bind ALSO fails (rebuts construction-determinism).
  - arm C (scramble roles): binding scrambled => compgen collapses (binding is load-bearing).

ARMS (one variable across A/B = readout: binding vs flat; identical data + supervision):
  A native_bind_shared : FHRR binding readout, SHARED noun-emb across roles          [MECHANISM]
  B flat               : per-role classifier heads over pooled features, NO binding  [FAIR BASELINE]
  C native_bind_scramble : A but role vectors collapsed (roleP:=roleA)               [MUST-FAIL control]
  D native_bind_tied   : binding readout but role-SPECIFIC emb tables                [LIVE-ALT / construction-check]

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: cleanup among N_FILL=24 near-orthogonal FHRR at N=1024 is not the bottleneck (learning is)
# - baseline_in_band at smoke (flat in-dist high; flat held-out low; native in-dist+heldout high)
# - discriminator survives scale: full-N params in smoke (single seed, fewer epochs) preview arm
# - HARD_PASS strictly above floor
# - deterministic_seeding: fixed int seeds + sorted() splits; NO hash()-seeded RNG
# - all numbers MEASURED@ this cell's metrics.json (no hypothesized numbers in verdict)
# LOCAL-ONLY: no push, no store mutation, no atom bank. Skunkworks VETs after land.

Anchor: compgen_native_bind_role_filler_v1
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

ANCHOR_NAME = "compgen_native_bind_role_filler_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", "exp_" + ANCHOR_NAME)

# ------------------------------ config ------------------------------
N_DIM = 1024            # FHRR dimensionality (phasor / complex64)
N_FILL = 24             # noun concepts
N_VERB = 12             # verbs (train triple-space = 248 role-valid (a,p) pairs x N_VERB)
N_ROLE = 2              # AGENT, PATIENT (VERB slot uses a 3rd fixed role vector)
# concept groups (deterministic, sorted): both-role / agent-only-train / patient-only-train
GROUP_SIZE = 8          # 8 both + 8 agent_only + 8 patient_only = 24
D_FLAT = 256            # flat noun/verb embedding dim
H_FLAT = 256            # flat hidden dim
TEMP = 20.0             # logit temperature for the binding-cleanup readout
DEVICE = "cpu"          # runner does not pass argv; default cpu (this cell is tiny)

FULL = dict(n_train=1800, n_indist=400, n_heldout=300, epochs=80, eval_every=10,
            batch=256, lr=1e-2, seeds=[7, 13, 19])
SMOKE = dict(n_train=800, n_indist=200, n_heldout=100, epochs=30, eval_every=10,
             batch=256, lr=1e-2, seeds=[7])

# Trained arms (one variable across shared vs flat = readout). native_bind_scramble is a
# post-hoc LESION of the trained shared model (decode with random role keys) -> the decisive
# "binding load-bearing" control that collapses to true chance (not the 2-way floor).
ARMS_TRAIN = ["native_bind_shared", "flat", "native_bind_tied"]
ARMS = ["native_bind_shared", "flat", "native_bind_scramble", "native_bind_tied"]


# ------------------------------ dataset ------------------------------
def concept_groups():
    """Deterministic sorted partition of concepts into both / agent_only / patient_only."""
    ids = list(range(N_FILL))
    both = sorted(ids[0:GROUP_SIZE])
    agent_only = sorted(ids[GROUP_SIZE:2 * GROUP_SIZE])       # train: agent; heldout test: as patient
    patient_only = sorted(ids[2 * GROUP_SIZE:3 * GROUP_SIZE])  # train: patient; heldout test: as agent
    return both, agent_only, patient_only


def make_dataset(seed, n_train, n_indist, n_heldout):
    """Build train / in-dist-test / held-out-combination-test.

    Held-out = NOVEL (concept, role): a concept seen only as agent in train, tested as patient
    (and vice versa). Genuinely non-tautological: the ANSWER (concept in that role) never appears
    in training; only the concept-in-the-other-role plus the existence of the role (from other
    concepts) is seen. Split integrity is guaranteed by construction (train sampler never draws
    agent from patient_only nor patient from agent_only) and asserted in self_test.
    """
    rng = np.random.default_rng(seed)
    both, agent_only, patient_only = concept_groups()
    train_agents = sorted(both + agent_only)     # valid agents in train
    train_patients = sorted(both + patient_only)  # valid patients in train

    def sample_triples(n, agent_pool, patient_pool, seen=None, avoid=None):
        out = []
        guard = 0
        seen = set() if seen is None else set(seen)
        while len(out) < n and guard < n * 200:
            guard += 1
            a = int(rng.choice(agent_pool))
            p = int(rng.choice(patient_pool))
            v = int(rng.integers(0, N_VERB))
            if a == p:
                continue
            key = (a, p, v)
            if key in seen:
                continue
            if avoid is not None and key in avoid:
                continue
            seen.add(key)
            out.append(key)
        return out

    train = sample_triples(n_train, train_agents, train_patients)
    train_set = set(train)
    indist = sample_triples(n_indist, train_agents, train_patients, seen=train_set)

    # held-out subsets. novel_role marks WHICH slot is the compgen test.
    # heldout_agent: agent in patient_only (never was agent) ; patient in both (seen as patient)
    # heldout_patient: patient in agent_only (never was patient) ; agent in both (seen as agent)
    n_half = n_heldout // 2
    ho_a = sample_triples(n_half, patient_only, both)       # novel role = AGENT (index 0)
    ho_p = sample_triples(n_heldout - n_half, both, agent_only)  # novel role = PATIENT (index 1)
    heldout = [(a, p, v, 0) for (a, p, v) in ho_a] + [(a, p, v, 1) for (a, p, v) in ho_p]
    # loud guard: exhausted triple-space -> empty split (would surface as a confusing 1-D error later)
    if len(train) < 0.5 * n_train or len(indist) == 0 or len(heldout) == 0:
        raise RuntimeError("DATASET_UNDERFILLED seed=%d train=%d/%d indist=%d/%d heldout=%d/%d "
                           "(triple-space too small; reduce n_train or raise N_VERB)"
                           % (seed, len(train), n_train, len(indist), n_indist, len(heldout), n_heldout))
    return train, indist, heldout, (train_agents, train_patients)


# ------------------------------ FHRR fixed codebook ------------------------------
def fixed_codebook(seed):
    """Fixed (non-trained) phasor codebook + role vectors. exp(i*phase), unit modulus."""
    g = torch.Generator().manual_seed(seed + 100003)
    two_pi = 2.0 * np.pi
    cb_phase = torch.rand(N_FILL, N_DIM, generator=g) * two_pi
    role_phase = torch.rand(3, N_DIM, generator=g) * two_pi   # 0=AGENT 1=PATIENT 2=VERB
    codebook = torch.exp(1j * cb_phase.to(torch.float32)).to(torch.complex64)
    roles = torch.exp(1j * role_phase.to(torch.float32)).to(torch.complex64)
    return codebook, roles


# ------------------------------ models ------------------------------
class NativeBind(torch.nn.Module):
    """FHRR binding readout. shared=True: one noun-emb table; shared=False: role-specific tables.
    scramble=True: role vectors collapsed (roleP := roleA) so binding cannot separate roles."""

    def __init__(self, codebook, roles, seed, shared=True, scramble=False):
        super().__init__()
        self.register_buffer("codebook", codebook)          # (N_FILL, N) complex, fixed
        r = roles.clone()
        if scramble:
            r[1] = r[0]                                       # PATIENT role := AGENT role
        self.register_buffer("roles", r)                     # (3, N) complex, fixed
        self.shared = shared
        g = torch.Generator().manual_seed(seed + 7)
        two_pi = 2.0 * np.pi
        if shared:
            self.theta_emb = torch.nn.Parameter(torch.rand(N_FILL, N_DIM, generator=g) * two_pi)
        else:
            self.theta_emb_a = torch.nn.Parameter(torch.rand(N_FILL, N_DIM, generator=g) * two_pi)
            self.theta_emb_p = torch.nn.Parameter(torch.rand(N_FILL, N_DIM, generator=g) * two_pi)
        self.theta_verb = torch.nn.Parameter(torch.rand(N_VERB, N_DIM, generator=g) * two_pi)

    def _emb(self, theta, idx):
        return torch.exp(1j * theta[idx])                    # (B, N) complex, unit modulus

    def forward(self, a, p, v, decode_roles=None):
        if self.shared:
            ea = self._emb(self.theta_emb, a)
            ep = self._emb(self.theta_emb, p)
        else:
            ea = self._emb(self.theta_emb_a, a)
            ep = self._emb(self.theta_emb_p, p)
        ev = self._emb(self.theta_verb, v)
        prop = ea * self.roles[0] + ep * self.roles[1] + ev * self.roles[2]   # (B, N) complex
        # decode: unbind by role KEY then cleanup against codebook (differentiable cosine logits).
        # decode_roles!=None (lesion) uses WRONG keys -> encode/decode mismatch breaks read-out.
        dr = self.roles if decode_roles is None else decode_roles
        cb_conj = self.codebook.conj()                       # (N_FILL, N)
        qa = prop * dr[0].conj()
        qp = prop * dr[1].conj()
        logits_a = (qa @ cb_conj.T).real / N_DIM * TEMP      # (B, N_FILL)
        logits_p = (qp @ cb_conj.T).real / N_DIM * TEMP
        return logits_a, logits_p


class Flat(torch.nn.Module):
    """FAIR strong baseline: handed the role-sorted structure (agent slot first), MORE params
    than the binding arm, per-role classifier heads. Fails held-out (filler,role) because a
    role head has no training signal for a concept never seen in that role -- transparent (the
    head output-weight rows for held-out concepts get no gradient)."""

    def __init__(self, seed):
        super().__init__()
        torch.manual_seed(seed + 11)
        self.emb_noun = torch.nn.Embedding(N_FILL, D_FLAT)
        self.emb_verb = torch.nn.Embedding(N_VERB, D_FLAT)
        self.mlp = torch.nn.Sequential(torch.nn.Linear(3 * D_FLAT, H_FLAT), torch.nn.ReLU(),
                                       torch.nn.Linear(H_FLAT, H_FLAT), torch.nn.ReLU())
        self.head_agent = torch.nn.Linear(H_FLAT, N_FILL)
        self.head_patient = torch.nn.Linear(H_FLAT, N_FILL)

    def forward(self, a, p, v):
        x = torch.cat([self.emb_noun(a), self.emb_noun(p), self.emb_verb(v)], dim=-1)  # role-sorted
        h = self.mlp(x)
        return self.head_agent(h), self.head_patient(h)


def build_model(arm, codebook, roles, seed):
    if arm == "native_bind_shared":
        return NativeBind(codebook, roles, seed, shared=True, scramble=False)
    if arm == "native_bind_scramble":
        return NativeBind(codebook, roles, seed, shared=True, scramble=True)
    if arm == "native_bind_tied":
        return NativeBind(codebook, roles, seed, shared=False, scramble=False)
    if arm == "flat":
        return Flat(seed)
    raise ValueError("unknown arm: " + arm)


# ------------------------------ eval ------------------------------
def _tensorize(triples):
    arr = np.array([(t[0], t[1], t[2]) for t in triples], dtype=np.int64)
    return (torch.from_numpy(arr[:, 0]), torch.from_numpy(arr[:, 1]), torch.from_numpy(arr[:, 2]))


def eval_indist(model, indist):
    """Accuracy on both role slots for in-dist test."""
    model.eval()
    a, p, v = _tensorize(indist)
    with torch.no_grad():
        la, lp = model(a, p, v)
    acc_a = (la.argmax(-1) == a).float().mean().item()
    acc_p = (lp.argmax(-1) == p).float().mean().item()
    return 0.5 * (acc_a + acc_p), acc_a, acc_p


def eval_heldout(model, heldout):
    """Accuracy on the NOVEL role slot only (the compgen discriminator)."""
    model.eval()
    a, p, v = _tensorize([(t[0], t[1], t[2]) for t in heldout])
    novel = torch.tensor([t[3] for t in heldout], dtype=torch.int64)  # 0=agent novel, 1=patient novel
    with torch.no_grad():
        la, lp = model(a, p, v)
    pred_a = la.argmax(-1)
    pred_p = lp.argmax(-1)
    correct_a = (pred_a == a)
    correct_p = (pred_p == p)
    # pick the novel-slot correctness per sample
    correct = torch.where(novel == 0, correct_a, correct_p)
    return correct.float().mean().item()


def train_arm(arm, cfg, codebook, roles, seed, train, indist, heldout, log):
    model = build_model(arm, codebook, roles, seed).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=cfg["lr"])
    lossfn = torch.nn.CrossEntropyLoss()
    a_all, p_all, v_all = _tensorize(train)
    n = a_all.shape[0]
    curve = []
    # epoch 0 (init, untrained) -- FREE-ALGEBRA check
    ind0, _, _ = eval_indist(model, indist)
    ho0 = eval_heldout(model, heldout)
    curve.append({"epoch": 0, "indist": round(ind0, 4), "heldout": round(ho0, 4)})
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
        if ep <= 10 or ep % cfg["eval_every"] == 0 or ep == cfg["epochs"]:
            ind, _, _ = eval_indist(model, indist)
            ho = eval_heldout(model, heldout)
            curve.append({"epoch": ep, "indist": round(ind, 4), "heldout": round(ho, 4)})
            print("[%s seed=%d] ep=%d indist=%.3f heldout=%.3f" % (arm, seed, ep, ind, ho), flush=True)
    ind_f, acc_a, acc_p = eval_indist(model, indist)
    ho_f = eval_heldout(model, heldout)
    # signature tensor for arms-differ hash: final logits on a fixed probe
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = model(pa, pp, pv)
        sig = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    res = {"arm": arm, "seed": seed, "indist_final": round(ind_f, 4),
           "indist_agent": round(acc_a, 4), "indist_patient": round(acc_p, 4),
           "heldout_final": round(ho_f, 4), "heldout_init": round(curve[0]["heldout"], 4),
           "learning_curve": curve, "_sig": sig}
    return res, model


def eval_scramble(model, seed, indist, heldout):
    """LESION: evaluate the TRAINED shared model encoding with correct roles but DECODING with
    RANDOM role keys (encode/decode key mismatch). If the learned solution relies on the correct
    role-binding, read-out collapses to chance."""
    g = torch.Generator().manual_seed(seed + 424242)
    two_pi = 2.0 * np.pi
    dr = torch.exp(1j * (torch.rand(3, N_DIM, generator=g) * two_pi)).to(torch.complex64)
    model.eval()
    a, p, v = _tensorize(indist)
    with torch.no_grad():
        la, lp = model(a, p, v, decode_roles=dr)
    ind = 0.5 * ((la.argmax(-1) == a).float().mean().item() + (lp.argmax(-1) == p).float().mean().item())
    ha, hp, hv = _tensorize([(t[0], t[1], t[2]) for t in heldout])
    novel = torch.tensor([t[3] for t in heldout], dtype=torch.int64)
    with torch.no_grad():
        hla, hlp = model(ha, hp, hv, decode_roles=dr)
    correct = torch.where(novel == 0, hla.argmax(-1) == ha, hlp.argmax(-1) == hp)
    ho = correct.float().mean().item()
    with torch.no_grad():
        pa, pp, pv = _tensorize(indist[:32])
        sla, slp = model(pa, pp, pv, decode_roles=dr)
        sig = torch.cat([sla.flatten(), slp.flatten()]).cpu().numpy().astype(np.float32)
    return {"arm": "native_bind_scramble", "seed": seed, "indist_final": round(ind, 4),
            "indist_agent": round(ind, 4), "indist_patient": round(ind, 4),
            "heldout_final": round(ho, 4), "heldout_init": round(ho, 4),
            "learning_curve": [], "_sig": sig}


# ------------------------------ verdict ------------------------------
CHANCE = 1.0 / N_FILL


def compute_verdict(agg):
    """agg: {arm: {"indist": mean, "heldout": mean, "heldout_init": mean, "curve_rise": mean}}"""
    nb = agg["native_bind_shared"]
    fl = agg["flat"]
    sc = agg["native_bind_scramble"]
    ti = agg["native_bind_tied"]
    gap = nb["heldout"] - fl["heldout"]
    rise = nb["heldout"] - nb["heldout_init"]

    checks = {
        "native_heldout_ge_0.70": nb["heldout"] >= 0.70,
        "flat_heldout_le_0.40": fl["heldout"] <= 0.40,
        "gap_ge_0.30": gap >= 0.30,
        "both_indist_ge_0.80": nb["indist"] >= 0.80 and fl["indist"] >= 0.80,
        "learning_curve_rises_ge_0.30": rise >= 0.30,
        "native_heldout_init_lt_0.60": nb["heldout_init"] < 0.60,   # not free-algebra
        "scramble_collapses_le_0.10": sc["heldout"] <= 0.10,        # binding load-bearing
        "tied_fails_heldout_le_0.40": ti["heldout"] <= 0.40,        # shared-emb factorization load-bearing
    }
    hard_fail = (nb["heldout"] <= 0.40 or gap <= 0.10 or fl["heldout"] >= 0.70
                 or nb["heldout_init"] >= 0.60 or sc["heldout"] > 0.20)
    hard_pass = all(checks.values())
    if hard_pass:
        verdict = "HARD_PASS"
    elif hard_fail:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"
    msg = ("native_heldout=%.3f flat_heldout=%.3f gap=%.3f rise=%.3f init=%.3f "
           "scramble_ho=%.3f tied_ho=%.3f indist(nb=%.3f,flat=%.3f) chance=%.3f"
           % (nb["heldout"], fl["heldout"], gap, rise, nb["heldout_init"],
              sc["heldout"], ti["heldout"], nb["indist"], fl["indist"], CHANCE))
    return verdict, msg, checks, gap, rise


# ------------------------------ run ------------------------------
def run(cfg, run_mode):
    t0 = time.perf_counter()
    per_unit = []
    sigs = {}   # arm -> {seed: sig} for arms-differ
    for seed in cfg["seeds"]:
        train, indist, heldout, _ = make_dataset(seed, cfg["n_train"], cfg["n_indist"], cfg["n_heldout"])
        for arm in ARMS_TRAIN:
            codebook, roles = fixed_codebook(seed)
            res, model = train_arm(arm, cfg, codebook, roles, seed, train, indist, heldout, None)
            sigs.setdefault(arm, {})[seed] = res.pop("_sig")
            per_unit.append(res)
            if arm == "native_bind_shared":
                sres = eval_scramble(model, seed, indist, heldout)
                sigs.setdefault("native_bind_scramble", {})[seed] = sres.pop("_sig")
                per_unit.append(sres)
                print("[native_bind_scramble seed=%d] indist=%.3f heldout=%.3f (lesion: random role keys)"
                      % (seed, sres["indist_final"], sres["heldout_final"]), flush=True)

    # arms-differ (META_RULE_AF) on the first seed
    s0 = cfg["seeds"][0]
    digests = {arm: hashlib.sha256(sigs[arm][s0].tobytes()).hexdigest() for arm in ARMS}
    for i in range(len(ARMS)):
        for j in range(i + 1, len(ARMS)):
            ai, aj = ARMS[i], ARMS[j]
            assert digests[ai] != digests[aj], (
                "META_RULE_AF VIOLATION: arms %s and %s bit-identical" % (ai, aj))

    # aggregate across seeds
    agg = {}
    for arm in ARMS:
        rows = [r for r in per_unit if r["arm"] == arm]
        agg[arm] = {
            "indist": float(np.mean([r["indist_final"] for r in rows])),
            "heldout": float(np.mean([r["heldout_final"] for r in rows])),
            "heldout_init": float(np.mean([r["heldout_init"] for r in rows])),
        }
    verdict, msg, checks, gap, rise = compute_verdict(agg)
    elapsed = time.perf_counter() - t0

    expected_units = len(cfg["seeds"]) * len(ARMS)
    cardinality_ok = len(per_unit) == expected_units

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": "compgen native-bind vs flat: " + verdict,
        "elapsed_s": round(elapsed, 2),
        "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "chance": round(CHANCE, 4),
        "arms_aggregate": agg,
        "gap_native_minus_flat_heldout": round(gap, 4),
        "native_heldout_learning_rise": round(rise, 4),
        "hard_pass_checks": checks,
        "cardinality_ok": cardinality_ok,
        "expected_n_units": expected_units,
        "n_units": len(per_unit),
        "arms_digests": digests,
        "config": {k: v for k, v in cfg.items()},
        "per_unit": [{k: v for k, v in r.items()} for r in per_unit],
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

    # 1. FHRR bind/unbind involution (algebra sanity)
    codebook, roles = fixed_codebook(7)
    c = codebook[3]
    bound = c * roles[0]
    recovered = bound * roles[0].conj()
    cos = (recovered @ c.conj()).real.item() / N_DIM
    assert cos > 0.99, "involution failed cos=%.4f" % cos
    print("[self-test] involution cos=%.4f OK" % cos, flush=True)

    # 2. SCRAMBLE FIRES: unbind a clean prop with a RANDOM role -> ~chance vs correct role ~1
    prop = codebook[3] * roles[0] + codebook[5] * roles[1]
    g = torch.Generator().manual_seed(123)
    rand_role = torch.exp(1j * (torch.rand(N_DIM, generator=g) * two_pi)).to(torch.complex64)
    cb_conj = codebook.conj()
    correct = ((prop * roles[0].conj()) @ cb_conj.T).real / N_DIM
    scram = ((prop * rand_role.conj()) @ cb_conj.T).real / N_DIM
    assert correct.argmax().item() == 3, "correct-role decode failed"
    assert abs(scram.max().item()) < 0.2, "scramble did not collapse: %.3f" % scram.max().item()
    print("[self-test] scramble collapse OK (correct_max=%.3f scram_max=%.3f)"
          % (correct.max().item(), scram.max().item()), flush=True)

    # 3. SPLIT INTEGRITY: no held-out (concept, novel_role) appears in train in that role
    both, agent_only, patient_only = concept_groups()
    assert len(set(both) & set(agent_only)) == 0 and len(set(both) & set(patient_only)) == 0
    train, indist, heldout, _ = make_dataset(7, 800, 200, 100)
    seen_agent = set(a for (a, p, v) in train)       # concepts ever in AGENT role in train
    seen_patient = set(p for (a, p, v) in train)      # concepts ever in PATIENT role in train
    for (a, p, v, novel) in heldout:
        if novel == 0:   # AGENT slot is the novel test -> a must NOT have been an agent in train
            assert a not in seen_agent, "SPLIT BREACH: heldout agent %d seen as agent in train" % a
            assert a in patient_only, "heldout novel-agent %d not from patient_only" % a
        else:            # PATIENT slot novel -> p must NOT have been a patient in train
            assert p not in seen_patient, "SPLIT BREACH: heldout patient %d seen as patient in train" % p
            assert p in agent_only, "heldout novel-patient %d not from agent_only" % p
    # in-dist test disjoint from train triples
    assert len(set((a, p, v) for (a, p, v) in indist) & set(train)) == 0, "indist leaks train triples"
    print("[self-test] split integrity OK (train=%d indist=%d heldout=%d)"
          % (len(train), len(indist), len(heldout)), flush=True)

    # 4. LEARNING-CURVE RESPONDS + arms differ: a tiny run
    tiny = dict(n_train=400, n_indist=120, n_heldout=80, epochs=25, eval_every=25,
                batch=128, lr=1e-2, seeds=[7])
    m = run(tiny, "self_test")
    nb = m["arms_aggregate"]["native_bind_shared"]
    fl = m["arms_aggregate"]["flat"]
    # native held-out must RISE from init (learned, not free-algebra)
    assert nb["heldout_init"] < 0.30, "native heldout not near-chance at init: %.3f" % nb["heldout_init"]
    assert nb["heldout"] > nb["heldout_init"] + 0.20, "native heldout did not rise: %.3f->%.3f" % (
        nb["heldout_init"], nb["heldout"])
    # flat must be BELOW native on held-out (discriminator lives)
    assert nb["heldout"] > fl["heldout"], "native did not beat flat on heldout (%.3f vs %.3f)" % (
        nb["heldout"], fl["heldout"])
    # arms-differ already asserted inside run(); confirm digests distinct count
    assert len(set(m["arms_digests"].values())) == len(ARMS), "arms not all distinct"
    print("[self-test] learning-curve+discriminator OK (nb init=%.3f final=%.3f flat=%.3f)"
          % (nb["heldout_init"], nb["heldout"], fl["heldout"]), flush=True)
    print("[self-test] PASS", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        sys.exit(0)

    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    cfg = SMOKE if args.smoke else FULL
    run_mode = "smoke" if args.smoke else "full"
    print("[run] mode=%s cfg=%s" % (run_mode, cfg), flush=True)
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
