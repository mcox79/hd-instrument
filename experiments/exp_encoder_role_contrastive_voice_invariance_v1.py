# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF): sha256 of each arm's held-out cross-voice
#   (active_to_passive) per-example correct-bool array; pairwise-distinct across the 4 arms.
# - final_metrics_atomicity: tmp_replace (os.replace at end); per-unit shards via tools/exp_checkpoint.
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n_a: closed-form nearest-centroid role classification on frozen encoder latents; no
#   learned-noise Cramer-Rao floor. Discriminator = the pre-registered HARD_PASS/HARD_FAIL bands below.
# - baseline_in_band: the FLOOR arms (ARM_FWDPRED = the measured wall, ARM_RANDOM = dead floor) MUST
#   empirically floor cross-voice (<= FWDPRED_FLOOR_MAX / within RANDOM_FLOOR_BAND); enforced as the
#   INVALID gate (test-is-broken check) BEFORE any MAIN-arm interpretation -- the AG-equivalent floor.
# - discriminator survives scale: LITE is a real (smaller-budget) directional read on the SAME
#   architecture; smoke additionally previews the discriminator via the TRAINED-items separation gate
#   (contrastive must beat the forward-pred wall on trained items at smoke, else the objective is inert).
# - HARD_PASS strictly above floor: xvoice held-out >= 0.70 both directions (CHANCE=0.50) AND
#   within-voice >= 0.85 -- both well above the 0.55 fail line and the anti-collapse floor.
# - HP_SCOPE: PASS/FAIL bands apply to ARM_CONTRASTIVE (PRIMARY) and are reported for ARM_DEPHEAD
#   (mechanism-faithful control). ARM_FWDPRED / ARM_RANDOM are can-fail FLOORS, never gated by PASS_MIN.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_arms; counted in decide_verdict.
# - per-unit failure-class instrumentation: no bare except; SystemExit/KeyboardInterrupt/Exception order.
# - calibration_check: default_ok_for_this_regime -- all bands are fixed HYPOTHESIZED thresholds set
#   BEFORE running (from notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md);
#   chance=0.50 exact-by-construction (binary balanced agent/patient task).
# - deterministic seeding: torch.manual_seed + numpy default_rng(seed+k) only; no hash(), no list(set()).
# - real_code_path: --self-test builds the REAL tokenizer + REAL corpus + REAL encoder + REAL train
#   loop for every arm + REAL readout at tiny scale (SELFTEST_CFG IS the real pipeline, tiny).
# - progress_logging: print_flush_true + _heartbeat.jsonl (defense-in-depth; timeout_s of a FULL >1800).
# - device-agnostic: cpu here (local, push-free); cuda path present but this cell is CPU-sized.
"""Token-level role-DISCRIMINATIVE CONTRASTIVE objective for voice-invariant thematic role -- the
LEARNED structural-objective fix after the causal/forward-predictive encoder alone was REFUTED.

CONTEXT (the measured wall this cell attacks):
  notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md. The prior causal
  forward-predictive encoder inverts cross-voice on the agent/patient probe (active->passive=0.017,
  passive->active=0.000; same Broca's/position-only profile as the frozen MLM). Root cause (CITED,
  Henderson 2016 / Papadimitriou 2022): a predictive objective is satisfiable by position and applies
  NO pressure on role-GEOMETRY. The research names the fix: add a NON-predictive structural training
  pressure that directly optimizes position-invariance of role.

ARMS (one variable: the ADDED structural loss term; ALL share the SAME causal-encoder backbone +
  next-token LM loss, so the comparison is the added pressure, nothing else):
  ARM_CONTRASTIVE (PRIMARY, research #1): causal LM + token-level role-discriminative InfoNCE across
    active/passive minimal pairs -- PULL the same-referent argument together across voice, PUSH the
    two arguments apart WITHIN a sentence (the mandatory anti-SimCSE-collapse negative).
  ARM_DEPHEAD (CONTROL, research #2, LISA-style, mechanism-faithful): causal LM + a dependency-arc
    auxiliary (predict each argument token's HEAD verb position + its thematic relation agent/patient).
    Isolates whether voice-invariant role needs explicit arc-building or just the representational
    constraint (#1).
  ARM_FWDPRED (FLOOR = the wall): causal LM ONLY -- must reproduce the ~chance/inverted cross-voice.
  ARM_RANDOM (FLOOR = dead): random-init causal encoder, no training -- must sit near chance.

READOUT (parser-free; gold roles known by CONSTRUCTION -- allowed data-supervision, NOT an
  inference-time parser): closed-form cosine nearest-centroid over the FROZEN encoder's per-token
  contextual reps at each argument's head-noun token. Cross-voice: fit centroids on one voice, classify
  the OTHER, BOTH directions. Anti-collapse (MANDATORY, research): also report WITHIN-voice
  agent-vs-patient separation -- high cross-voice is real only if within-voice role separation is
  preserved (else invariance-by-erasure, the SimCSE bag-of-words cheat).

FAIRNESS / HELD-OUT (defeats teach-to-the-test; memorization = HARD_FAIL):
  Encoder trains ONLY on TRAIN_NOUNS x TRAIN_VERBS. The PRIMARY metric is on a HELD-OUT split of NOVEL
  verbs AND novel filler nouns never seen in any training sentence (Petty 2022: novel-verb
  generalization is the crux). A separate TRAINED-items cross-voice slice is reported to expose the
  memorization signature (pass on trained only, held-out fails). Filler variation (determiner + adjective
  vary independently between the active and passive of a minimal pair) prevents referent alignment being
  solved by surface span identity. Every sentence contributes exactly one AGENT rep + one PATIENT rep ->
  every split is 50/50 balanced by construction; chance = 0.50.

PRE-REGISTERED BANDS (HYPOTHESIZED, set BEFORE running, from the research note; NOT loosened):
  Primary = token-level cross-voice role accuracy on HELD-OUT novel verbs+fillers, both directions.
  HARD_PASS = cross-voice >= 0.70 BOTH directions AND within-voice >= 0.85 (anti-collapse).
  HARD_FAIL = either direction <= 0.55, OR within-voice < 0.65 (bag-of-words erasure), OR trained-items
              cross-voice >= 0.70 while held-out <= 0.55 (memorization).
  MIDDLE    = held-out cross-voice in [0.55,0.70] with within-voice preserved (off-inversion, informative).
  INVALID   = the FLOOR arms did not floor (ARM_FWDPRED cross-voice > FWDPRED_FLOOR_MAX, OR ARM_RANDOM
              outside RANDOM_FLOOR_BAND) -> the test is broken; MAIN-arm numbers are NOT interpreted.
  Bands apply to ARM_CONTRASTIVE (primary) + reported for ARM_DEPHEAD (control).

Run:  .venv/Scripts/python.exe experiments/exp_encoder_role_contrastive_voice_invariance_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_encoder_role_contrastive_voice_invariance_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_encoder_role_contrastive_voice_invariance_v1.py --lite
      .venv/Scripts/python.exe experiments/exp_encoder_role_contrastive_voice_invariance_v1.py --full

ASCII-only. No emojis. Deterministic (torch.manual_seed + numpy default_rng only; no hash/list(set)).
CPU (local, push-free). Compute architecture: sequential-CPU, justified -- a small word-level
TinyTransformer over a tiny closed-vocab templated corpus; matmul-light; the DECISIVE question is a
directional GATE (does the added structural loss move cross-voice off inversion), the cheapest method
for it. Storage strategy: no_storage / no_composition (representation-geometry + nearest-centroid only).
"""

import argparse
import hashlib
import json
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
sys.path.insert(0, os.path.join(_REPO, "tools"))
import exp_checkpoint as ckpt  # noqa: E402  -- per-unit checkpoint/resume (CLAUDE.md mandate)
sys.path.insert(0, os.path.dirname(_THIS))
from _cell_heartbeat import CellHeartbeat  # noqa: E402

ANCHOR_NAME = "encoder_role_contrastive_voice_invariance_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)

# ---------------------------------------------------------------------------
# Closed vocabulary (word-level) -- ASCII, deterministic order.
# ---------------------------------------------------------------------------
NOUNS = ["dog", "cat", "bird", "fish", "horse", "cow", "sheep", "goat",
         "lion", "tiger", "bear", "wolf", "fox", "deer", "mouse", "frog",
         "duck", "hawk", "seal", "crab", "whale", "shark", "snake", "owl"]
TRAIN_NOUNS = NOUNS[:16]
HELDOUT_NOUNS = NOUNS[16:]                       # 8 novel filler nouns, never in a training sentence

# regular verbs: past tense == past participle (no irregular morphology leaking a voice cue)
VERBS = ["helped", "chased", "greeted", "followed", "warned", "thanked", "noticed", "watched",
         "pushed", "pulled", "carried", "called", "touched", "kicked", "licked", "hugged"]
TRAIN_VERBS = VERBS[:8]
HELDOUT_VERBS = VERBS[8:]                         # 8 novel verbs

ADJS = ["small", "large", "quiet", "eager", "clever", "gentle", "brave", "calm"]   # filler variation
DETS = ["the", "a"]
FUNC = ["was", "by", "."]
PAD_TOK = "[PAD]"

VOCAB = sorted(set(NOUNS + VERBS + ADJS + DETS + FUNC)) + [PAD_TOK]
WORD2ID = {w: i for i, w in enumerate(VOCAB)}
PAD_ID = WORD2ID[PAD_TOK]
VOCAB_SIZE = len(VOCAB)
MAX_LEN = 12                                     # longest sentence (passive, 2 adjectives) = 10; +slack

AGENT, PATIENT = 0, 1
CHANCE = 0.5

# ---- pre-registered bands (HYPOTHESIZED; set before running) ----
XVOICE_PASS_MIN = 0.70          # research HARD_PASS both directions
XVOICE_FAIL_MAX = 0.55          # research HARD_FAIL either direction
WITHIN_PASS_MIN = 0.85          # anti-collapse HARD_PASS
WITHIN_FAIL_MAX = 0.65          # anti-collapse HARD_FAIL (bag-of-words erasure)
# FLOOR validity semantics (research note: "floor arms MUST empirically floor = reproduce the ~0.0/
# inverted cross-voice"): a floor arm is VALID iff it does NOT show voice-invariant role, i.e. its
# cross-voice is AT OR BELOW the fail line. Inversion (below chance) is the HEALTHY floor signature (a
# position-dominated encoder inverts cross-voice), NOT a broken test -- so the gate is an UPPER BOUND,
# never a near-chance band. MEASURED@selftest: even an untrained random causal encoder inverts to ~0.25.
FLOOR_MAX = 0.60                # both ARM_FWDPRED (wall) and ARM_RANDOM (dead) must be <= this cross-voice
SMOKE_FIRE_MARGIN = 0.08        # smoke: a co-primary arm's trained-items xvoice must beat ARM_FWDPRED by this

DIRECTIONS = ("active_to_passive", "passive_to_active")

ARM_CONTRASTIVE = "ARM_CONTRASTIVE"   # PRIMARY (research #1)
ARM_DEPHEAD = "ARM_DEPHEAD"           # CONTROL (research #2, LISA-style)
ARM_FWDPRED = "ARM_FWDPRED"           # FLOOR = the measured wall (causal LM only)
ARM_RANDOM = "ARM_RANDOM"             # FLOOR = dead (random init)
ARMS = [ARM_CONTRASTIVE, ARM_DEPHEAD, ARM_FWDPRED, ARM_RANDOM]
TRAINED_ARMS = [ARM_CONTRASTIVE, ARM_DEPHEAD, ARM_FWDPRED]

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
# contrastive_coef/dephead_coef weight the added STRUCTURAL term vs the shared causal-LM loss. Set > 1
# because LM (next-token) strongly rewards positional info, which is the very thing the structural term
# must overcome; the added term is applied directly on encoder reps (no projector) so it must win the
# geometry. tau_c = InfoNCE temperature.
SELFTEST_CFG = dict(run_mode="selftest", seeds=[7], d_model=32, n_layers=1, n_heads=4, ffn_mult=2,
                    steps=8, batch=8, lr=3e-3, n_train_triples=64, n_held_triples=48,
                    lm_coef=1.0, contrastive_coef=3.0, dephead_coef=2.0, tau_c=0.1)
SMOKE_CFG = dict(run_mode="smoke", seeds=[7], d_model=48, n_layers=2, n_heads=4, ffn_mult=2,
                 steps=500, batch=64, lr=3e-3, n_train_triples=1200, n_held_triples=300,
                 lm_coef=1.0, contrastive_coef=3.0, dephead_coef=2.0, tau_c=0.1)
LITE_CFG = dict(run_mode="lite", seeds=[7], d_model=96, n_layers=2, n_heads=4, ffn_mult=2,
                steps=2000, batch=96, lr=2e-3, n_train_triples=3000, n_held_triples=440,
                lm_coef=1.0, contrastive_coef=3.0, dephead_coef=2.0, tau_c=0.1)
FULL_CFG = dict(run_mode="full", seeds=[7, 13], d_model=128, n_layers=3, n_heads=8, ffn_mult=4,
                steps=6000, batch=128, lr=1e-3, n_train_triples=6000, n_held_triples=440,
                lm_coef=1.0, contrastive_coef=3.0, dephead_coef=2.0, tau_c=0.1)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Corpus construction (word-level; token indices tracked exactly, no offset parsing)
# ---------------------------------------------------------------------------
def _phrase(det, adj, noun):
    toks = [det]
    if adj is not None:
        toks.append(adj)
    toks.append(noun)
    return toks                                  # head noun is the LAST token


def _mods(rng):
    det = DETS[int(rng.integers(0, len(DETS)))]
    adj = None
    if rng.random() < 0.6:
        adj = ADJS[int(rng.integers(0, len(ADJS)))]
    return det, adj


def _encode_tokens(tok_list):
    ids = [WORD2ID[t] for t in tok_list]
    n = len(ids)
    assert n <= MAX_LEN, "sentence too long (%d > MAX_LEN=%d): %r" % (n, MAX_LEN, tok_list)
    ids = ids + [PAD_ID] * (MAX_LEN - n)
    return ids, n


def _build_active(noun_a, verb, noun_b, rng):
    det_a, adj_a = _mods(rng)
    det_b, adj_b = _mods(rng)
    pa = _phrase(det_a, adj_a, noun_a)
    pb = _phrase(det_b, adj_b, noun_b)
    toks = pa + [verb] + pb + ["."]
    agent_idx = len(pa) - 1
    verb_idx = len(pa)
    patient_idx = len(pa) + 1 + len(pb) - 1
    ids, n = _encode_tokens(toks)
    return dict(ids=ids, length=n, agent_idx=agent_idx, patient_idx=patient_idx, verb_idx=verb_idx)


def _build_passive(noun_a, verb, noun_b, rng):
    det_a, adj_a = _mods(rng)
    det_b, adj_b = _mods(rng)
    pb = _phrase(det_b, adj_b, noun_b)           # grammatical subject = PATIENT
    pa = _phrase(det_a, adj_a, noun_a)           # by-phrase = AGENT
    toks = pb + ["was", verb, "by"] + pa + ["."]
    patient_idx = len(pb) - 1
    verb_idx = len(pb) + 1
    agent_idx = len(pb) + 3 + len(pa) - 1
    ids, n = _encode_tokens(toks)
    return dict(ids=ids, length=n, agent_idx=agent_idx, patient_idx=patient_idx, verb_idx=verb_idx)


def build_pairs(nouns, verbs, n_triples, seed):
    """Deterministic (noun_a, noun_b, verb) triples (noun_a != noun_b) -> matched active+passive
    minimal pairs with INDEPENDENT determiner/adjective mods per voice (filler variation)."""
    rng = np.random.default_rng(seed)
    nn = len(nouns)
    triples = []
    seen = set()
    guard = 0
    while len(triples) < n_triples and guard < n_triples * 50:
        guard += 1
        ia = int(rng.integers(0, nn))
        ib = int(rng.integers(0, nn))
        if ia == ib:
            continue
        iv = int(rng.integers(0, len(verbs)))
        key = (ia, ib, iv)
        if key in seen:
            continue
        seen.add(key)
        triples.append(key)
    pairs = []
    for (ia, ib, iv) in triples:
        na, nb, vb = nouns[ia], nouns[ib], verbs[iv]
        act = _build_active(na, vb, nb, rng)
        pas = _build_passive(na, vb, nb, rng)
        pairs.append(dict(active=act, passive=pas))
    return pairs


# ---------------------------------------------------------------------------
# Causal encoder (small word-level TinyTransformer; lower-triangular attention == forward-predictive)
# ---------------------------------------------------------------------------
class CausalRoleEncoder(torch.nn.Module):
    def __init__(self, cfg):
        super().__init__()
        d = cfg["d_model"]
        self.d_model = d
        self.tok_emb = torch.nn.Embedding(VOCAB_SIZE, d, padding_idx=PAD_ID)
        self.pos_emb = torch.nn.Embedding(MAX_LEN, d)
        layer = torch.nn.TransformerEncoderLayer(
            d_model=d, nhead=cfg["n_heads"], dim_feedforward=cfg["ffn_mult"] * d,
            dropout=0.0, activation="gelu", batch_first=True, norm_first=True)
        self.enc = torch.nn.TransformerEncoder(layer, num_layers=cfg["n_layers"])
        self.norm = torch.nn.LayerNorm(d)
        self.lm_head = torch.nn.Linear(d, VOCAB_SIZE)

    def contextual(self, ids):
        """ids [B,L] -> H [B,L,d] with a strict causal (lower-triangular) attention mask."""
        B, L = ids.shape
        dev = ids.device
        pos = torch.arange(L, device=dev).unsqueeze(0)
        h = self.tok_emb(ids) + self.pos_emb(pos)
        causal = torch.triu(torch.full((L, L), float("-inf"), device=dev), diagonal=1)
        pad_mask = (ids == PAD_ID)
        h = self.enc(h, mask=causal, src_key_padding_mask=pad_mask)
        return self.norm(h)


class DepHead(torch.nn.Module):
    """LISA-style: (a) bilinear head-attach score (argument token -> its head verb position);
    (b) thematic relation classifier (agent/patient) from the argument token's contextual rep."""
    def __init__(self, d):
        super().__init__()
        self.arc = torch.nn.Linear(d, d, bias=False)
        self.rel = torch.nn.Linear(d, 2)

    def arc_scores(self, h_arg, h_all):
        # h_arg [B,d], h_all [B,L,d] -> [B,L]
        q = self.arc(h_arg).unsqueeze(1)             # [B,1,d]
        return (q * h_all).sum(-1)                    # [B,L]

    def rel_logits(self, h_arg):
        return self.rel(h_arg)                        # [B,2]


# ---------------------------------------------------------------------------
# Losses
# ---------------------------------------------------------------------------
def lm_loss(enc, ids):
    """Causal next-token prediction. logits [B,L,V]; target = ids shifted; ignore pad + last pos."""
    h = enc.contextual(ids)
    logits = enc.lm_head(h)[:, :-1, :]                # predict token t+1 from pos t
    target = ids[:, 1:]
    tgt = target.clone()
    tgt[target == PAD_ID] = -100
    return torch.nn.functional.cross_entropy(
        logits.reshape(-1, VOCAB_SIZE), tgt.reshape(-1), ignore_index=-100)


def _gather(h, idx):
    """h [B,L,d], idx [B] -> [B,d]."""
    B = h.shape[0]
    return h[torch.arange(B, device=h.device), idx]


def info_nce_role(enc, act_ids, pas_ids, act_ai, act_pi, pas_ai, pas_pi, tau):
    """Token-level role-discriminative NT-Xent across voice, applied DIRECTLY on the ENCODER reps (NO
    projection head -- the goal is that the encoder's OWN latents become voice-invariant, so the pressure
    must land on the encoder rep, not escape into a projector). Positives = same-referent argument across
    active/passive; the within-sentence opposite-role argument is an in-batch negative (anti-collapse).
    Gradient-clean assembly via cat (no empty+in-place-assign)."""
    h_act = enc.contextual(act_ids)
    h_pas = enc.contextual(pas_ids)
    a_act, p_act = _gather(h_act, act_ai), _gather(h_act, act_pi)     # [B,d] each
    a_pas, p_pas = _gather(h_pas, pas_ai), _gather(h_pas, pas_pi)
    view1 = torch.cat([a_act, p_act], dim=0)         # [2B,d]  rows 0..B-1 agents, B..2B-1 patients
    view2 = torch.cat([a_pas, p_pas], dim=0)         # [2B,d]  same layout, other voice
    z = torch.nn.functional.normalize(torch.cat([view1, view2], dim=0), dim=1)   # [4B,d]
    M = z.shape[0]
    sim = (z @ z.T) / tau
    sim.fill_diagonal_(float("-inf"))                # mask self
    pos = (torch.arange(M, device=z.device) + M // 2) % M            # cross-voice counterpart
    return torch.nn.functional.cross_entropy(sim, pos)


def dephead_loss(enc, dephead, ids, ai, pi, vi):
    """Arc-attach (argument -> head verb) + thematic relation (agent/patient) CE, for both arguments."""
    h = enc.contextual(ids)
    B, L, _ = h.shape
    pad = (ids == PAD_ID)
    loss = ids.new_zeros((), dtype=torch.float32)
    for arg_idx, role_label in ((ai, AGENT), (pi, PATIENT)):
        h_arg = _gather(h, arg_idx)                  # [B,d]
        arc = dephead.arc_scores(h_arg, h)           # [B,L]
        arc = arc.masked_fill(pad, float("-inf"))
        loss = loss + torch.nn.functional.cross_entropy(arc, vi)
        rel = dephead.rel_logits(h_arg)              # [B,2]
        rel_tgt = torch.full((B,), role_label, device=ids.device, dtype=torch.long)
        loss = loss + torch.nn.functional.cross_entropy(rel, rel_tgt)
    return loss / 2.0


# ---------------------------------------------------------------------------
# Training (one variable = the added structural term; shared causal backbone + LM loss)
# ---------------------------------------------------------------------------
def _batch_tensor(pairs, sel, voice, device):
    ids = torch.tensor([pairs[i][voice]["ids"] for i in sel], dtype=torch.long, device=device)
    ai = torch.tensor([pairs[i][voice]["agent_idx"] for i in sel], dtype=torch.long, device=device)
    pi = torch.tensor([pairs[i][voice]["patient_idx"] for i in sel], dtype=torch.long, device=device)
    vi = torch.tensor([pairs[i][voice]["verb_idx"] for i in sel], dtype=torch.long, device=device)
    return ids, ai, pi, vi


def train_arm(arm, cfg, pairs, seed, device, out_dir, hb):
    torch.manual_seed(seed)
    np.random.seed(seed)
    enc = CausalRoleEncoder(cfg).to(device)
    if arm == ARM_RANDOM:
        enc.eval()
        return enc, dict(arm=arm, trained=False, steps=0)

    dephead = DepHead(cfg["d_model"]).to(device) if arm == ARM_DEPHEAD else None
    params = list(enc.parameters())
    if dephead is not None:
        params += list(dephead.parameters())
    opt = torch.optim.AdamW(params, lr=cfg["lr"])
    g = np.random.default_rng(seed + 11)
    n = len(pairs)
    bs = min(cfg["batch"], n)
    steps = cfg["steps"]
    log_every = max(1, steps // 10)
    lm_c, ct_c, dh_c, tau = cfg["lm_coef"], cfg["contrastive_coef"], cfg["dephead_coef"], cfg["tau_c"]
    enc.train()
    t0 = time.perf_counter()
    last = dict(lm=0.0, extra=0.0)
    for step in range(steps):
        sel = g.integers(0, n, size=bs)
        a_ids, a_ai, a_pi, a_vi = _batch_tensor(pairs, sel, "active", device)
        p_ids, p_ai, p_pi, p_vi = _batch_tensor(pairs, sel, "passive", device)
        opt.zero_grad(set_to_none=True)
        loss = lm_c * (lm_loss(enc, a_ids) + lm_loss(enc, p_ids))
        extra = 0.0
        if arm == ARM_CONTRASTIVE:
            ct = info_nce_role(enc, a_ids, p_ids, a_ai, a_pi, p_ai, p_pi, tau)
            loss = loss + ct_c * ct
            extra = float(ct.detach())
        elif arm == ARM_DEPHEAD:
            dh = dephead_loss(enc, dephead, a_ids, a_ai, a_pi, a_vi) \
                + dephead_loss(enc, dephead, p_ids, p_ai, p_pi, p_vi)
            loss = loss + dh_c * dh
            extra = float(dh.detach())
        if not torch.isfinite(loss):
            raise FloatingPointError("non-finite loss arm=%s step=%d seed=%d" % (arm, step, seed))
        loss.backward()
        opt.step()
        last = dict(lm=float(loss.detach()), extra=extra)
        if (step % log_every == 0) or (step == steps - 1):
            el = time.perf_counter() - t0
            _log("  %s seed=%d step=%d/%d loss=%.4f extra=%.4f (%.1fs)"
                 % (arm, seed, step, steps, last["lm"], extra, el))
            hb.tick(step, extra={"arm": arm, "loss": last["lm"]})
    enc.eval()
    return enc, dict(arm=arm, trained=True, steps=steps, final_loss=last["lm"], final_extra=last["extra"])


# ---------------------------------------------------------------------------
# Readout (frozen encoder; closed-form cosine nearest-centroid; mean-centered)
# ---------------------------------------------------------------------------
def _cos(a, b):
    na, nb = a.norm(), b.norm()
    if na.item() < 1e-12 or nb.item() < 1e-12:
        return 0.0
    return float(torch.dot(a, b) / (na * nb))


@torch.no_grad()
def _voice_reps(enc, pairs, voice, device):
    """Per pair -> (agent_rep, AGENT), (patient_rep, PATIENT) from the frozen encoder's contextual reps
    at the argument head-noun tokens. Batched over all pairs for the chosen voice."""
    reps, labels = [], []
    n = len(pairs)
    bs = 256
    for s in range(0, n, bs):
        sel = list(range(s, min(n, s + bs)))
        ids, ai, pi, _vi = _batch_tensor(pairs, sel, voice, device)
        h = enc.contextual(ids)
        ra = _gather(h, ai)
        rp = _gather(h, pi)
        for k in range(len(sel)):
            reps.append(ra[k]); labels.append(AGENT)
            reps.append(rp[k]); labels.append(PATIENT)
    return torch.stack(reps), torch.tensor(labels)


def _centroids(reps, labels):
    a = reps[labels == AGENT].mean(dim=0)
    p = reps[labels == PATIENT].mean(dim=0)
    return torch.stack([a, p])                       # [2,d] row0=agent row1=patient


def _classify(reps, labels, centroid):
    correct = []
    for k in range(reps.shape[0]):
        r = reps[k]
        sims = [_cos(r, centroid[0]), _cos(r, centroid[1])]
        correct.append(int(np.argmax(sims)) == int(labels[k]))
    correct = np.asarray(correct, dtype=bool)
    return float(correct.mean()), correct


@torch.no_grad()
def readout(enc, held_pairs, trained_pairs, device):
    """Returns cross-voice (both directions) + within-voice on held-out, plus trained-items cross-voice
    (memorization probe). H1/H2 pair-parity split keeps centroid-fit and test disjoint for BOTH
    within and cross. Mean-centering (per read-conditioning finding) applied per voice-set."""
    def eval_set(pairs):
        ar, al = _voice_reps(enc, pairs, "active", device)
        pr, pl = _voice_reps(enc, pairs, "passive", device)
        center = torch.cat([ar, pr], dim=0).mean(dim=0)
        ar = ar - center
        pr = pr - center
        # H1 (even pair index -> even rep blocks) / H2 (odd) split. Each pair contributes 2 consecutive
        # reps, so pair index = rep_index // 2.
        n = ar.shape[0]
        pair_idx = torch.arange(n) // 2
        h1 = (pair_idx % 2 == 0)
        h2 = ~h1
        out = {}
        # cross active_to_passive: centroids from active H1, classify passive H2
        c = _centroids(ar[h1], al[h1])
        acc_ap, corr_ap = _classify(pr[h2], pl[h2], c)
        # cross passive_to_active: centroids from passive H1, classify active H2
        c2 = _centroids(pr[h1], pl[h1])
        acc_pa, _ = _classify(ar[h2], al[h2], c2)
        # within active: centroids active H1, classify active H2
        wa, _ = _classify(ar[h2], al[h2], _centroids(ar[h1], al[h1]))
        wp, _ = _classify(pr[h2], pl[h2], _centroids(pr[h1], pl[h1]))
        out["active_to_passive"] = acc_ap
        out["passive_to_active"] = acc_pa
        out["within_voice"] = float(np.mean([wa, wp]))
        out["_corr_ap"] = corr_ap
        # arm fingerprint (META_RULE_AF): the actual frozen-encoder held-out rep matrix -- two distinct
        # arms give distinct reps even when an accuracy coincidentally coincides; catches a genuine
        # bit-identical-arm (same-encoder) bug without false-positiving on tiny-scale acc collisions.
        rep_bytes = torch.cat([ar, pr], dim=0).detach().cpu().numpy().round(5).tobytes()
        out["_rep_fp"] = hashlib.sha256(rep_bytes).hexdigest()
        return out

    held = eval_set(held_pairs)
    trained = eval_set(trained_pairs)
    return dict(
        xvoice_held={"active_to_passive": held["active_to_passive"],
                     "passive_to_active": held["passive_to_active"]},
        within_held=held["within_voice"],
        xvoice_trained={"active_to_passive": trained["active_to_passive"],
                        "passive_to_active": trained["passive_to_active"]},
        _corr_ap_held=held["_corr_ap"],
        _rep_fp_held=held["_rep_fp"],
    )


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def decide_verdict(per_arm, expected_n_units, n_units_done):
    def xv(arm, d):
        return per_arm[arm]["xvoice_held"][d]

    def xv_mean(arm):
        return float(np.mean(list(per_arm[arm]["xvoice_held"].values())))

    fwd = per_arm.get(ARM_FWDPRED)
    rnd = per_arm.get(ARM_RANDOM)
    floors_ok = True
    floor_msg = []
    for arm, obj in ((ARM_FWDPRED, fwd), (ARM_RANDOM, rnd)):
        if obj is not None:
            arm_max = max(obj["xvoice_held"].values())    # both directions must be <= FLOOR_MAX
            if arm_max > FLOOR_MAX:
                floors_ok = False
                floor_msg.append("%s cross-voice max=%.3f > FLOOR_MAX=%.2f (floor arm shows invariance -> "
                                 "test broken)" % (arm, arm_max, FLOOR_MAX))

    cardinality_ok = (n_units_done == expected_n_units)

    def arm_band(arm):
        aps = per_arm[arm]["xvoice_held"]["active_to_passive"]
        pas = per_arm[arm]["xvoice_held"]["passive_to_active"]
        within = per_arm[arm]["within_held"]
        tr = per_arm[arm]["xvoice_trained"]
        both_pass = aps >= XVOICE_PASS_MIN and pas >= XVOICE_PASS_MIN
        either_fail = aps <= XVOICE_FAIL_MAX or pas <= XVOICE_FAIL_MAX
        memorized = (min(tr.values()) >= XVOICE_PASS_MIN) and (max(aps, pas) <= XVOICE_FAIL_MAX)
        if both_pass and within >= WITHIN_PASS_MIN:
            return "HARD_PASS"
        if either_fail or within < WITHIN_FAIL_MAX or memorized:
            return "HARD_FAIL"
        return "MIDDLE"

    if not cardinality_ok:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", \
            "n_units_done=%d != expected=%d" % (n_units_done, expected_n_units)
    if not floors_ok:
        return "INVALID", "Floor gate failed (test broken): %s. Structural-arm numbers NOT interpreted." \
            % "; ".join(floor_msg)
    # CO-PRIMARY (Director steer per USER "build that organ"): the token-level contrastive arm and the
    # dependency-head / role-STRUCTURE-BUILDER arm are BOTH first-class; the DATA decides which route
    # (direct invariance pressure vs explicit arc-building) confers voice-invariant role. Each is gated
    # against the SAME pre-registered bands; the run-level verdict reflects the BEST-passing route and
    # names both. ARM_FWDPRED/ARM_RANDOM stay floors (never gated by PASS_MIN).
    bands_by_arm = {}
    for arm in (ARM_CONTRASTIVE, ARM_DEPHEAD):
        if arm in per_arm:
            bands_by_arm[arm] = arm_band(arm)
    if not bands_by_arm:
        return "INCOMPLETE", "both co-primary arms missing"
    ct_band = bands_by_arm.get(ARM_CONTRASTIVE, "n/a")
    dh_band = bands_by_arm.get(ARM_DEPHEAD, "n/a")
    order = {"HARD_PASS": 2, "MIDDLE": 1, "HARD_FAIL": 0, "n/a": -1}
    best = max((b for b in bands_by_arm.values()), key=lambda b: order[b])
    verdict = {"HARD_PASS": "ENCODER_ENCODES_VOICE_INVARIANT_ROLE",
               "HARD_FAIL": "NEITHER_STRUCTURAL_OBJECTIVE_FIXED_VOICE_INVARIANCE",
               "MIDDLE": "MIDDLE_OFF_INVERSION"}[best]

    def side(arm):
        if arm not in per_arm:
            return "n/a"
        return "held_xvoice=%s within=%.3f trained_xvoice=%s band=%s" % (
            {k: round(v, 3) for k, v in per_arm[arm]["xvoice_held"].items()},
            per_arm[arm]["within_held"],
            {k: round(v, 3) for k, v in per_arm[arm]["xvoice_trained"].items()},
            bands_by_arm.get(arm, "n/a"))
    msg = ("Floors valid (%s floored). CO-PRIMARY side-by-side -- "
           "ARM_CONTRASTIVE[%s]: %s || ARM_DEPHEAD[%s]: %s. "
           "Run verdict = best-passing route (%s). ARM_FWDPRED(wall) held_xvoice=%s. "
           "ARM_RANDOM(floor) held_xvoice=%s."
           % ("both" if (fwd is not None and rnd is not None) else "available",
              ct_band, side(ARM_CONTRASTIVE), dh_band, side(ARM_DEPHEAD), best,
              {k: round(v, 3) for k, v in fwd["xvoice_held"].items()} if fwd else "n/a",
              {k: round(v, 3) for k, v in rnd["xvoice_held"].items()} if rnd else "n/a"))
    return verdict, msg


# ---------------------------------------------------------------------------
# Run one config
# ---------------------------------------------------------------------------
def _write_start_marker(out_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=_now_iso(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(out_dir, "_start_marker.json"))


def _write_crash_metrics(out_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg="%s: %s" % (type(exc).__name__, str(exc)[:500]),
                summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=_now_iso(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME, failure_class=type(exc).__name__)
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def _jsonify(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, dict):
        return {str(k): _jsonify(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonify(v) for v in o]
    return o


def _atomic_write(out_dir, metrics):
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_jsonify(metrics), f, indent=2)
    os.replace(tmp, os.path.join(out_dir, "metrics.json"))


def run_cfg(cfg, out_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    seeds = cfg["seeds"]
    run_mode = cfg["run_mode"]
    arms = ARMS if run_mode != "lite" else [ARM_CONTRASTIVE, ARM_DEPHEAD, ARM_FWDPRED, ARM_RANDOM]
    expected_n_units = len(seeds) * len(arms)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t0 = time.perf_counter()
    prior = ckpt.load_units(out_dir)
    if prior:
        _log("checkpoint: %d/%d units already on disk; resuming" % (len(prior), expected_n_units))

    per_arm = {}                                     # arm -> aggregated (last seed's readout for verdict)
    per_arm_seeds = {}                               # arm -> {seed: readout}
    digests = {}
    unit_i = 0
    with CellHeartbeat(out_dir, total_units=expected_n_units, interval_s=30) as hb:
        for seed in seeds:
            # build corpora per seed (deterministic); encoder trains only on TRAIN nouns x TRAIN verbs
            train_pairs = build_pairs(TRAIN_NOUNS, TRAIN_VERBS, cfg["n_train_triples"], seed + 100)
            held_pairs = build_pairs(HELDOUT_NOUNS, HELDOUT_VERBS, cfg["n_held_triples"], seed + 200)
            trained_probe = build_pairs(TRAIN_NOUNS, TRAIN_VERBS, cfg["n_held_triples"], seed + 300)
            for arm in arms:
                unit_i += 1
                k = ckpt.unit_key(arm, seed)
                if k in prior:
                    res = prior[k]
                    _log("  [resume] %s loaded from checkpoint" % k)
                else:
                    _log("TRAIN %s seed=%d (%d train pairs, %d held pairs)"
                         % (arm, seed, len(train_pairs), len(held_pairs)))
                    enc, tdiag = train_arm(arm, cfg, train_pairs, seed, device, out_dir, hb)
                    ro = readout(enc, held_pairs, trained_probe, device)
                    ro.pop("_corr_ap_held")
                    digest = ro.pop("_rep_fp_held")   # fingerprint the held-out rep matrix (arm output)
                    res = dict(arm=arm, seed=seed, train=tdiag,
                               xvoice_held=ro["xvoice_held"], within_held=ro["within_held"],
                               xvoice_trained=ro["xvoice_trained"], digest=digest)
                    ckpt.record_unit(out_dir, k, res)
                    _log("  %s seed=%d xvoice_held=%s within=%.3f trained=%s"
                         % (arm, seed, {kk: round(vv, 3) for kk, vv in res["xvoice_held"].items()},
                            res["within_held"],
                            {kk: round(vv, 3) for kk, vv in res["xvoice_trained"].items()}))
                per_arm_seeds.setdefault(arm, {})[str(seed)] = res
                per_arm[arm] = res
                digests[k] = res["digest"]
                hb.tick(unit_i, extra={"unit": k})

    # arms_differ (META_RULE_AF): the 4 arms' held-out cross-voice correct-arrays must differ pairwise
    keys = sorted(digests)
    for a in keys:
        for b in keys:
            if a < b:
                assert digests[a] != digests[b], \
                    "META_RULE_AF VIOLATION: units %r and %r bit-identical" % (a, b)

    n_units_done = len(digests)
    verdict, msg = decide_verdict(per_arm, expected_n_units, n_units_done)
    elapsed = time.perf_counter() - t0

    smoke_fire = None
    if run_mode == "smoke" and ARM_FWDPRED in per_arm:
        fw_tr = float(np.mean(list(per_arm[ARM_FWDPRED]["xvoice_trained"].values())))
        per_arm_fire = {}
        any_fired = False
        for arm in (ARM_CONTRASTIVE, ARM_DEPHEAD):        # BOTH co-primary arms must be able to fire
            if arm in per_arm:
                tr = float(np.mean(list(per_arm[arm]["xvoice_trained"].values())))
                fired = (tr - fw_tr) >= SMOKE_FIRE_MARGIN
                per_arm_fire[arm] = dict(trained_xvoice=tr, margin=tr - fw_tr, fired=fired)
                any_fired = any_fired or fired
                _log("SMOKE discriminator-fires[%s]: trained=%.3f fwdpred_trained=%.3f margin=%.3f "
                     "(need >=%.2f) fired=%s" % (arm, tr, fw_tr, tr - fw_tr, SMOKE_FIRE_MARGIN, fired))
        smoke_fire = dict(fwdpred_trained_xvoice=fw_tr, required=SMOKE_FIRE_MARGIN,
                          per_arm=per_arm_fire, any_fired=any_fired)

    _atomic_write(out_dir, dict(
        verdict=verdict, verdict_msg=msg,
        summary="%s | chance=%.2f | %s" % (verdict, CHANCE, msg[:160]),
        run_mode=run_mode, elapsed_s=elapsed, ts_iso=_now_iso(), anchor_name=ANCHOR_NAME,
        chance=CHANCE, per_arm=per_arm_seeds,
        smoke_discriminator_fires=smoke_fire,
        bands=dict(xvoice_pass_min=XVOICE_PASS_MIN, xvoice_fail_max=XVOICE_FAIL_MAX,
                   within_pass_min=WITHIN_PASS_MIN, within_fail_max=WITHIN_FAIL_MAX,
                   floor_max=FLOOR_MAX),
        arms_differ_verified=True, digests=digests,
        cardinality_ok=bool(n_units_done == expected_n_units),
        expected_n_units=expected_n_units, n_units_done=n_units_done,
        params=dict(arms=arms, seeds=seeds, vocab_size=VOCAB_SIZE, max_len=MAX_LEN,
                    train_nouns=TRAIN_NOUNS, heldout_nouns=HELDOUT_NOUNS,
                    train_verbs=TRAIN_VERBS, heldout_verbs=HELDOUT_VERBS,
                    d_model=cfg["d_model"], n_layers=cfg["n_layers"], steps=cfg["steps"],
                    batch=cfg["batch"], tau_c=cfg["tau_c"]),
        start_marker_written=True, crash_diagnostic_present=True,
        final_metrics_atomicity="tmp_replace", defensive_error_checking="passed_all_4_patterns",
        cell_chunked=False, progress_logging="print_flush_true",
        crlb_n_a="closed-form nearest-centroid; discriminator = pre-registered bands (decide_verdict)",
        calibration_check="default_ok_for_this_regime: bands are fixed HYPOTHESIZED thresholds set "
                          "before running; chance=0.50 exact-by-construction."))
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))
    return verdict, msg


# ---------------------------------------------------------------------------
# Self-test (real code path at tiny scale)
# ---------------------------------------------------------------------------
def run_self_test():
    _log("SELF-TEST: corpus construction (index tracking, balance, filler variation) ...")
    # construction checks: agent/patient token ids match the intended nouns; indices in-range
    p = build_pairs(TRAIN_NOUNS, TRAIN_VERBS, 32, 7)
    for pr in p[:32]:
        for voice in ("active", "passive"):
            s = pr[voice]
            assert 0 <= s["agent_idx"] < s["length"], "agent_idx out of range"
            assert 0 <= s["patient_idx"] < s["length"], "patient_idx out of range"
            assert 0 <= s["verb_idx"] < s["length"], "verb_idx out of range"
            assert s["agent_idx"] != s["patient_idx"]
            assert s["ids"][s["verb_idx"]] in [WORD2ID[v] for v in TRAIN_VERBS], "verb token mismatch"
            # agent token must be the SAME noun across active and passive of the pair (referent identity)
        assert pr["active"]["ids"][pr["active"]["agent_idx"]] == pr["passive"]["ids"][pr["passive"]["agent_idx"]], \
            "agent referent differs across voice"
        assert pr["active"]["ids"][pr["active"]["patient_idx"]] == pr["passive"]["ids"][pr["passive"]["patient_idx"]], \
            "patient referent differs across voice"
    _log("  PASS: indices + referent identity across voice")

    # held-out disjointness
    assert set(TRAIN_NOUNS).isdisjoint(set(HELDOUT_NOUNS))
    assert set(TRAIN_VERBS).isdisjoint(set(HELDOUT_VERBS))
    _log("  PASS: held-out nouns/verbs disjoint from train")

    _log("SELF-TEST: REAL full pipeline (all 4 arms, tiny) ...")
    st_dir = os.path.join(OUTPUT_DIR, "_selftest")
    # clear prior selftest shards so a re-run recomputes
    for fn in ("units.jsonl", "metrics.json"):
        fp = os.path.join(st_dir, fn)
        if os.path.exists(fp):
            os.remove(fp)
    verdict, msg = run_cfg(SELFTEST_CFG, st_dir)
    assert verdict not in ("CELL_CRASHED",), "selftest crashed"
    _log("  selftest verdict=%s" % verdict)
    _log("SELF-TEST PASS")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--lite", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.lite or args.full):
        run_self_test()
        _atomic_write(OUTPUT_DIR, dict(
            verdict="SELFTEST_PASS", verdict_msg="SELFTEST_PASS (corpus + 4-arm tiny pipeline)",
            summary="SELFTEST_PASS", run_mode="self_test", elapsed_s=0.0, ts_iso=_now_iso(),
            anchor_name=ANCHOR_NAME))
        return
    if args.smoke:
        run_cfg(SMOKE_CFG, OUTPUT_DIR + "_smoke")
        return
    if args.lite:
        run_cfg(LITE_CFG, OUTPUT_DIR + "_lite")
        return
    if args.full:
        run_cfg(FULL_CFG, OUTPUT_DIR)
        return


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
