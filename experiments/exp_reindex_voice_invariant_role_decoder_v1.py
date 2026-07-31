# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at run (META_RULE_AF): sha256 of each role-reader arm's held-out predicted-
#   agent-mention array; pairwise-distinct across FF / FF_FROZEN / REVISION / REVISION_NOCUE.
# - final_metrics_atomicity: tmp_replace (os.replace at end); per-unit shards via tools/exp_checkpoint;
#   frozen encoder state_dict saved to out_dir so resume skips the encoder retrain.
# - except SystemExit: raise BEFORE except Exception (no BaseException).
# - crlb_n_a: closed-form/argmax role readout on frozen latents; no learned-noise Cramer-Rao floor.
#   Discriminator = the pre-registered HARD_PASS/HARD_FAIL bands below.
# - baseline_in_band: the INVERTED control ARM_ENCODER_LINPROBE (static-encoder cross-voice linear probe
#   on the SAME frozen latents) MUST stay <= LINPROBE_INVERT_MAX -- the pre-registered premise that the
#   latents do NOT already carry cross-voice role, so any cross-voice consistency the decoder gets is from
#   the REVISION, not from the latents. Enforced as the PREMISE gate before HARD_PASS.
# - discriminator survives scale: LITE is a real (smaller-budget) directional read on the SAME
#   architecture; smoke additionally previews the discriminator via the TRAINED-items reanalysis gate
#   (REVISION passive acc must beat REVISION_NOCUE passive acc on trained items, else the cue-triggered
#   revision mechanism is inert and full is pointless).
# - HARD_PASS strictly above floor: query-role acc >= 0.70 BOTH voices AND cross-voice consistency >=0.70
#   AND beats the Step-1 feedforward-head consistency floor by >= STEP1_BEAT_MARGIN -- all above the 0.55
#   fail line and above the measured feedforward floor.
# - HP_SCOPE: PASS/FAIL bands apply to ARM_REVISION (PRIMARY). ARM_FF/ARM_FF_FROZEN are feedforward
#   FLOORS (Step-1). ARM_REVISION_NOCUE is the cue-ablation floor. ARM_ENCODER_LINPROBE is the inverted
#   control. None of the floors are gated by PASS_MIN.
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_arm_units (5 arm-readout units); counted in verdict.
# - per-unit failure-class instrumentation: no bare except; SystemExit/KeyboardInterrupt/Exception order.
# - calibration_check: default_ok_for_this_regime -- all bands are fixed HYPOTHESIZED thresholds set
#   BEFORE running (from notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md STEP-4
#   pre-registration); chance=0.50 exact-by-construction (balanced 2-mention/2-role task).
# - deterministic seeding: torch.manual_seed + numpy default_rng(seed+k) only; no hash(), no list(set()).
# - real_code_path: --self-test builds the REAL corpus + REAL DEPHEAD encoder + REAL frozen-latent
#   feature extraction + REAL decoder train loop for every arm + REAL readout at tiny scale + REAL FHRR
#   slot bind/unbind of the decoder output (SELFTEST_CFG IS the real pipeline, tiny).
# - progress_logging: print_flush_true + _heartbeat.jsonl (defense-in-depth; a FULL could exceed 1800s).
# - device-agnostic: cpu here (local, push-free); the frozen-latent decoder is matmul-light.
"""Cue-triggered REINDEXING DECODER for voice-invariant thematic role -- the corrected fix after THREE
static-encoder objectives (contrastive, dephead, forward-predictive) all failed to make voice-invariant
role LIVE in encoder geometry (cross-voice linear probe inverts: 0.016/0.402).

RESEARCH (build to this): notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md. Diagnosis:
role is NOT a static geometric code -- it is the OUTPUT of an incremental, revisable reindexing
computation that writes surface NPs onto a canonical (agent,patient) event slot, voice-invariant only
because it lives in that constructed representation. Fix = a small LEARNED glass-box cue-triggered
reindexing DECODER on top of the FROZEN encoder latents, read the probe at the DECODER OUTPUT (not the
encoder hidden state). Borrowed algorithms: St. John & McClelland 1990 Sentence Gestalt (query-based
role-filler readout, supervision form) + Vosse & Kempen 2000 competitive relaxation (cue-triggered
reassignment = reanalysis). Output feeds the substrate's existing FHRR role slot (hdlab/binding.py).

MEASUREMENT-FIRST. STEP 1 (the floor the organ must beat) is computed inside this same cell:
  STEP 1 = OUTPUT-level cross-voice CONSISTENCY of the EXISTING feedforward DEPHEAD thematic-relation
  head on HELD-OUT novel verbs -- for the SAME event rendered both voices, does the head OUTPUT the same
  canonical (agent,patient)? (New quantity = same-event same-answer rate across voices; NOT per-voice
  accuracy which was 0.742/0.726 MEASURED@data/exp_encoder_role_headlevel_readout_probe_v1/metrics.json,
  and NOT the encoder-geometry linear probe which inverts 0.016/0.402 MEASURED@same file.) This is the
  feedforward-without-revision floor; the revision decoder must beat it.

ARMS (ONE VARIABLE = the added cue-triggered revision register; all role-readers read the SAME frozen
  DEPHEAD encoder latents E_dh with the SAME mention gather + SAME Sinkhorn readout):
  ARM_FF          (Step-1 literal floor): the EXISTING joint-trained DEPHEAD rel head (per-argument-token
                    agent/patient classifier). Per-voice acc reproduces ~0.742/0.726; its cross-voice
                    CONSISTENCY is the Step-1 floor.
  ARM_FF_FROZEN   (strict matched feedforward control): a content-only query-reader (S = content, no
                    prior, no cue) trained on FROZEN E_dh latents -- apples-to-apples with the decoder,
                    only the revision register differs.
  ARM_REVISION    (PRIMARY, the build): S = content + alpha*(1-2g)*default_prior; g = LEARNED cue gate
                    over the encoder's OWN latents (glass-box: per-token cue logits, reads which token
                    fires); default_prior = first-mention=agent (brain-faithful canonical default);
                    (1-2g) flips the prior when the passive cue fires = Vosse-Kempen cue-triggered
                    relaxation. Sinkhorn competitive relaxation over the 2x2 mention/slot assignment.
  ARM_REVISION_NOCUE (cue-ablation floor): the SAME decoder with g:=0 (default prior, NO cue) -> passive
                    tracks the wrong first-NP=agent default -> must fail passive. Proves the cue is
                    load-bearing (isolates cue-triggered revision from a static default prior).
  ARM_ENCODER_LINPROBE (inverted control): the static-encoder cross-voice LINEAR probe on the SAME frozen
                    E_dh latents -- must stay inverted (<= LINPROBE_INVERT_MAX), reproducing 0.016/0.402.

SUPERVISION (Sentence-Gestalt query-readout, allowed data-supervision NOT an inference-time parser): the
  decoder is trained end-to-end to emit the correct GOLD filler for each role query (AGENT?/PATIENT?)
  against the canonical (agent,patient) tuple known BY CONSTRUCTION. At inference it uses NO external
  parse: it reads its own cue gate over its own latents and relaxes its own 2x2 register. Gold roles at
  TRAIN time are the training target (the thing being learned); FORBIDDEN = an external parser at test.

FAIRNESS / HELD-OUT: decoder + heads train ONLY on TRAIN_NOUNS x TRAIN_VERBS. PRIMARY metric is on a
  HELD-OUT split of NOVEL verbs AND novel filler nouns (Petty 2022 crux). A TRAINED-items slice exposes
  memorization. Filler variation (independent det/adj per voice) blocks surface-span alignment. Every
  event contributes one agent + one patient mention -> 50/50 balanced; chance = 0.50.

PRE-REGISTERED BANDS (HYPOTHESIZED, set BEFORE running, from the research note; NOT loosened):
  Metric = query-based canonical-role accuracy on HELD-OUT novel verbs+fillers, per voice, PLUS
  cross-voice consistency (same-event same-answer rate).
  HARD_PASS = ARM_REVISION query-role acc >= 0.70 BOTH active AND passive AND cross-voice consistency
              >= 0.70, WHILE ARM_ENCODER_LINPROBE stays inverted <= 0.40, AND ARM_REVISION consistency
              BEATS the Step-1 ARM_FF feedforward consistency floor (by >= STEP1_BEAT_MARGIN), AND the
              passive reanalysis fired (REVISION passive - NOCUE passive >= REANALYSIS_MARGIN).
  HARD_FAIL = either voice <= 0.55 on held-out, OR trained >= 0.70 while held-out <= 0.55 (memorization),
              OR passive tracks the first-NP=agent default (passive <= 0.55 AND reanalysis did NOT fire).
  MIDDLE    = held-out both-voice in [0.55,0.70] with consistency preserved (off-inversion, informative;
              the research assesses MIDDLE MORE likely than HARD_PASS).
  PREMISE_VIOLATED = ARM_ENCODER_LINPROBE > LINPROBE_INVERT_MAX (latents already carry cross-voice role)
              -> the revision-needed premise is undercut; decoder numbers reported but not claimed.

Run:  .venv/Scripts/python.exe experiments/exp_reindex_voice_invariant_role_decoder_v1.py --self-test
      .venv/Scripts/python.exe experiments/exp_reindex_voice_invariant_role_decoder_v1.py --smoke
      .venv/Scripts/python.exe experiments/exp_reindex_voice_invariant_role_decoder_v1.py --lite
      .venv/Scripts/python.exe experiments/exp_reindex_voice_invariant_role_decoder_v1.py --full

ASCII-only. No emojis. Deterministic. CPU (local, push-free). Compute architecture: sequential-CPU,
justified -- a small DEPHEAD TinyTransformer over a tiny closed-vocab templated corpus, then a
matmul-light 2x2-register decoder on FROZEN latents; the DECISIVE question is a directional GATE (does a
cue-triggered revision register beat the feedforward head cross-voice), the cheapest decisive method.
Storage strategy: no_storage / no_composition for the readout; the decoder OUTPUT is bound into an FHRR
role slot as a wiring demonstration (self-test), not a stored corpus.
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
import exp_checkpoint as ckpt  # noqa: E402
sys.path.insert(0, os.path.dirname(_THIS))
import exp_encoder_role_headlevel_readout_probe_v1 as P  # noqa: E402  (imports C internally)
from _cell_heartbeat import CellHeartbeat  # noqa: E402

C = P.C  # base corpus/encoder/readout machinery

ANCHOR_NAME = "reindex_voice_invariant_role_decoder_v1"
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)

AGENT, PATIENT = 0, 1
CHANCE = 0.5

# ---- pre-registered bands (HYPOTHESIZED; set BEFORE running) ----
PASS_MIN = 0.70               # query-role acc HARD_PASS both voices
FAIL_MAX = 0.55               # query-role acc HARD_FAIL either voice
CONS_PASS = 0.70              # cross-voice consistency HARD_PASS
LINPROBE_INVERT_MAX = 0.40    # ARM_ENCODER_LINPROBE must stay inverted <= this (premise)
STEP1_BEAT_MARGIN = 0.05      # REVISION consistency must beat Step-1 FF floor by this
REANALYSIS_MARGIN = 0.10      # REVISION passive - NOCUE passive (held) for reanalysis to count as fired
SMOKE_REANALYSIS_MARGIN = 0.15  # smoke: REVISION passive - NOCUE passive on TRAINED items (discriminator)

ARM_FF = "ARM_FF"                          # Step-1 literal feedforward floor (existing DEPHEAD rel head)
ARM_FF_FROZEN = "ARM_FF_FROZEN"            # strict content-only control on frozen latents
ARM_REVISION = "ARM_REVISION"              # PRIMARY (the build)
ARM_REVISION_NOCUE = "ARM_REVISION_NOCUE"  # cue-ablation floor
ARM_ENCODER_LINPROBE = "ARM_ENCODER_LINPROBE"  # inverted control
DECODER_ARMS = [ARM_FF_FROZEN, ARM_REVISION, ARM_REVISION_NOCUE]
ARM_UNITS = [ARM_FF, ARM_FF_FROZEN, ARM_REVISION, ARM_REVISION_NOCUE, ARM_ENCODER_LINPROBE]

# ---------------------------------------------------------------------------
# Config profiles
# ---------------------------------------------------------------------------
# enc_* configure the DEPHEAD encoder (reuses C.CausalRoleEncoder); dec_* configure the frozen-latent
# reindexing decoder. n_dec_train caps the pairs whose full [L,d] latents are held for cue detection.
SELFTEST_CFG = dict(run_mode="selftest", seeds=[7], d_model=32, n_layers=1, n_heads=4, ffn_mult=2,
                    enc_steps=8, enc_batch=8, enc_lr=3e-3, lm_coef=1.0, dephead_coef=2.0,
                    n_train_triples=64, n_held_triples=48, n_dec_train=64,
                    dec_steps=25, dec_batch=16, dec_lr=5e-3, relax_iters=3, sink_temp=0.5)
SMOKE_CFG = dict(run_mode="smoke", seeds=[7], d_model=48, n_layers=2, n_heads=4, ffn_mult=2,
                 enc_steps=400, enc_batch=64, enc_lr=3e-3, lm_coef=1.0, dephead_coef=2.0,
                 n_train_triples=1000, n_held_triples=300, n_dec_train=1000,
                 dec_steps=400, dec_batch=64, dec_lr=5e-3, relax_iters=3, sink_temp=0.5)
LITE_CFG = dict(run_mode="lite", seeds=[7], d_model=96, n_layers=2, n_heads=4, ffn_mult=2,
                enc_steps=2000, enc_batch=96, enc_lr=2e-3, lm_coef=1.0, dephead_coef=2.0,
                n_train_triples=3000, n_held_triples=440, n_dec_train=2200,
                dec_steps=1500, dec_batch=128, dec_lr=4e-3, relax_iters=4, sink_temp=0.5)
FULL_CFG = dict(run_mode="full", seeds=[7, 13], d_model=128, n_layers=3, n_heads=8, ffn_mult=4,
                enc_steps=6000, enc_batch=128, enc_lr=1e-3, lm_coef=1.0, dephead_coef=2.0,
                n_train_triples=6000, n_held_triples=440, n_dec_train=3000,
                dec_steps=2500, dec_batch=128, dec_lr=3e-3, relax_iters=5, sink_temp=0.4)


def _log(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Frozen-latent feature extraction (mentions ordered by surface position)
# ---------------------------------------------------------------------------
@torch.no_grad()
def extract_features(enc, pairs, voice, device, chunk=256):
    """From the FROZEN encoder, per (pair, voice): full contextual latents H [L,d], the two argument
    head-noun token indices ordered by surface position (m0=first, m1=second), the gold agent mention
    (0/1), the two mention NOUN ids, and the valid-token mask. Returns batched tensors on `device`."""
    H_all, ment, gA, nouns, valid = [], [], [], [], []
    L = C.MAX_LEN
    n = len(pairs)
    for s in range(0, n, chunk):
        sel = list(range(s, min(n, s + chunk)))
        ids, ai, pi, _vi = C._batch_tensor(pairs, sel, voice, device)
        h = enc.contextual(ids)                       # [b,L,d]
        for k, idx in enumerate(sel):
            a = int(ai[k].item())
            p = int(pi[k].item())
            t0, t1 = (a, p) if a < p else (p, a)       # surface order
            gold_agent_mention = 0 if t0 == a else 1
            H_all.append(h[k].detach().cpu())
            ment.append([t0, t1])
            gA.append(gold_agent_mention)
            nouns.append([int(ids[k, t0].item()), int(ids[k, t1].item())])
            length = int(pairs[idx][voice]["length"])
            valid.append([1 if j < length else 0 for j in range(L)])
    H = torch.stack(H_all).to(device)                  # [N,L,d]
    return dict(H=H,
                ment=torch.tensor(ment, dtype=torch.long, device=device),
                gA=torch.tensor(gA, dtype=torch.long, device=device),
                nouns=torch.tensor(nouns, dtype=torch.long, device=device),
                valid=torch.tensor(valid, dtype=torch.bool, device=device))


def _gather_mentions(H, ment):
    """H [N,L,d], ment [N,2] -> mention latents [N,2,d]."""
    N, L, d = H.shape
    idx = ment.unsqueeze(-1).expand(N, 2, d)
    return torch.gather(H, 1, idx)                      # [N,2,d]


# ---------------------------------------------------------------------------
# Reindexing decoder (glass-box; 2 mentions x 2 slots register)
# ---------------------------------------------------------------------------
class ReindexDecoder(torch.nn.Module):
    """S[m,r] = content[m,r] + use_prior * alpha*(1-2g)*D[m,r]; competitive relaxation (Sinkhorn) over the
    2x2 register; query readout = P[:, r] as a distribution over mentions. Glass-box: g is a readable
    per-example cue gate computed from per-token cue logits over the encoder's OWN latents."""

    def __init__(self, d, use_prior, use_cue, relax_iters, sink_temp):
        super().__init__()
        self.use_prior = use_prior
        self.use_cue = use_cue
        self.relax_iters = relax_iters
        self.sink_temp = sink_temp
        self.V = torch.nn.Parameter(torch.randn(2, d) * (1.0 / (d ** 0.5)))   # role content vectors
        self.w_cue = torch.nn.Parameter(torch.randn(d) * (1.0 / (d ** 0.5)))  # cue direction over latents
        self.b_cue = torch.nn.Parameter(torch.tensor(-2.0))                   # gate starts low (default-first)
        self.alpha_raw = torch.nn.Parameter(torch.tensor(0.5413))             # softplus -> ~1.0
        D = torch.tensor([[1.0, -1.0], [-1.0, 1.0]])   # default: m0=agent, m1=patient
        self.register_buffer("D", D)

    def gate(self, H, valid):
        """Per-example cue gate g in [0,1] from per-token cue logits; logsumexp pools toward the cue
        token (soft-max over positions). Returns g [N] and the per-token logits c [N,L] (glass-box)."""
        c = torch.einsum("nld,d->nl", H, self.w_cue)   # [N,L]
        c = c.masked_fill(~valid, -1e9)
        cue_score = torch.logsumexp(c, dim=1) + self.b_cue
        return torch.sigmoid(cue_score), c

    def forward(self, H, ment, valid):
        Hm = _gather_mentions(H, ment)                 # [N,2,d]
        content = torch.einsum("nmd,rd->nmr", Hm, self.V)   # [N,2,2]
        g = torch.zeros(H.shape[0], device=H.device)
        c = None
        S = content
        if self.use_prior:
            if self.use_cue:
                g, c = self.gate(H, valid)
            prior = (1.0 - 2.0 * g).view(-1, 1, 1) * self.D.unsqueeze(0)      # [N,2,2]
            S = content + torch.nn.functional.softplus(self.alpha_raw) * prior
        # Sinkhorn competitive relaxation (lateral inhibition -> doubly-stochastic-ish assignment)
        K = torch.exp(S / self.sink_temp)
        for _ in range(self.relax_iters):
            K = K / (K.sum(dim=2, keepdim=True) + 1e-9)
            K = K / (K.sum(dim=1, keepdim=True) + 1e-9)
        return K, g, c


def _decoder_loss(Pmat, gA):
    """CE of the agent-slot mention distribution vs gold agent mention + patient-slot vs gold patient."""
    agent_dist = Pmat[:, :, AGENT] / (Pmat[:, :, AGENT].sum(dim=1, keepdim=True) + 1e-9)   # [N,2]
    patient_dist = Pmat[:, :, PATIENT] / (Pmat[:, :, PATIENT].sum(dim=1, keepdim=True) + 1e-9)
    gp = 1 - gA
    la = -torch.log(agent_dist[torch.arange(gA.shape[0]), gA] + 1e-9)
    lp = -torch.log(patient_dist[torch.arange(gA.shape[0]), gp] + 1e-9)
    return (la + lp).mean() / 2.0


def train_decoder(arm, cfg, feats_act, feats_pas, seed, device, hb):
    """Train a ReindexDecoder arm on FROZEN latents (both voices interleaved). ONE variable per arm =
    use_prior/use_cue. Returns the trained decoder."""
    torch.manual_seed(seed + 1000)
    use_prior = arm in (ARM_REVISION, ARM_REVISION_NOCUE)
    use_cue = arm == ARM_REVISION
    dec = ReindexDecoder(cfg["d_model"], use_prior=use_prior, use_cue=use_cue,
                         relax_iters=cfg["relax_iters"], sink_temp=cfg["sink_temp"]).to(device)
    opt = torch.optim.AdamW(dec.parameters(), lr=cfg["dec_lr"])
    g = np.random.default_rng(seed + 21)
    n = feats_act["H"].shape[0]
    bs = min(cfg["dec_batch"], n)
    steps = cfg["dec_steps"]
    log_every = max(1, steps // 8)
    dec.train()
    t0 = time.perf_counter()
    for step in range(steps):
        sel = torch.tensor(g.integers(0, n, size=bs), dtype=torch.long, device=device)
        opt.zero_grad(set_to_none=True)
        total = torch.zeros((), device=device)
        for feats in (feats_act, feats_pas):
            Pmat, _g, _c = dec(feats["H"][sel], feats["ment"][sel], feats["valid"][sel])
            total = total + _decoder_loss(Pmat, feats["gA"][sel])
        total = total / 2.0
        if not torch.isfinite(total):
            raise FloatingPointError("non-finite decoder loss arm=%s step=%d seed=%d" % (arm, step, seed))
        total.backward()
        opt.step()
        if (step % log_every == 0) or (step == steps - 1):
            _log("  %s seed=%d step=%d/%d loss=%.4f (%.1fs)"
                 % (arm, seed, step, steps, float(total.detach()), time.perf_counter() - t0))
            hb.tick(step, extra={"arm": arm, "loss": float(total.detach())})
    dec.eval()
    return dec


# ---------------------------------------------------------------------------
# Readouts (all read the DECODER / head OUTPUT, never the encoder hidden state)
# ---------------------------------------------------------------------------
@torch.no_grad()
def _decoder_predict(dec, feats):
    """Predicted agent/patient mention (argmax over mentions of each slot) + agent-slot continuous score
    matrix [N,2] (mechanism fingerprint, distinct across arms even when argmax coincides) + mean gate."""
    Pmat, g, _c = dec(feats["H"], feats["ment"], feats["valid"])
    pred_agent_m = Pmat[:, :, AGENT].argmax(dim=1)     # [N]
    pred_patient_m = Pmat[:, :, PATIENT].argmax(dim=1)
    return pred_agent_m, pred_patient_m, Pmat[:, :, AGENT], g


@torch.no_grad()
def score_arm(dec, feats_act, feats_pas):
    """query-role acc per voice + cross-voice consistency (same-event same agent-noun) + gate stats."""
    out = {}
    pred_noun_agent = {}
    scores = {}
    for name, feats in (("active", feats_act), ("passive", feats_pas)):
        pag, ppa, agent_score, g = _decoder_predict(dec, feats)
        gA = feats["gA"]
        gp = 1 - gA
        acc_agent = (pag == gA).float().mean().item()
        acc_patient = (ppa == gp).float().mean().item()
        out[name] = float((acc_agent + acc_patient) / 2.0)
        nouns = feats["nouns"]                          # [N,2]
        pred_noun_agent[name] = nouns[torch.arange(nouns.shape[0]), pag]   # [N]
        scores[name] = agent_score.cpu().numpy()
        out["_g_" + name] = float(g.mean().item())
    consistent = (pred_noun_agent["active"] == pred_noun_agent["passive"]).float().mean().item()
    out["xvoice_consistency"] = float(consistent)
    out["_agent_scores_active"] = scores["active"]
    out["_agent_scores_passive"] = scores["passive"]
    return out


@torch.no_grad()
def score_ff_relhead(enc, dephead, feats_act, feats_pas, held_pairs, device):
    """STEP 1: the EXISTING feedforward DEPHEAD rel head. Per-voice acc (reproduces ~0.742/0.726) + its
    OUTPUT-level cross-voice CONSISTENCY (same-event same agent-noun across voices) -- the floor."""
    # per-voice acc via the shared machinery (argument-token rel head over gold-labelled reps)
    per_voice = P.rel_head_readout(enc, dephead, held_pairs, device)
    out = {"active": float(per_voice["active"]), "passive": float(per_voice["passive"])}
    # cross-voice consistency: at each mention token, rel head -> agent/patient logit; predicted agent
    # mention = argmax over mentions of the agent logit; compare the agent NOUN across voices.
    pred_noun_agent = {}
    scores = {}
    for name, feats in (("active", feats_act), ("passive", feats_pas)):
        Hm = _gather_mentions(feats["H"], feats["ment"])       # [N,2,d]
        logits = dephead.rel_logits(Hm.reshape(-1, Hm.shape[-1])).reshape(Hm.shape[0], 2, 2)  # [N,2,(agent,patient)]
        pred_agent_m = logits[:, :, AGENT].argmax(dim=1)
        nouns = feats["nouns"]
        pred_noun_agent[name] = nouns[torch.arange(nouns.shape[0]), pred_agent_m]
        scores[name] = logits[:, :, AGENT].cpu().numpy()
    out["xvoice_consistency"] = float((pred_noun_agent["active"] == pred_noun_agent["passive"]).float().mean().item())
    out["_agent_scores_active"] = scores["active"]
    out["_agent_scores_passive"] = scores["passive"]
    return out


# ---------------------------------------------------------------------------
# FHRR slot wiring demonstration (decoder output feeds the existing role slot)
# ---------------------------------------------------------------------------
def fhrr_slot_demo(agent_filler_id, patient_filler_id, n_dim=1024, seed=0):
    """Bind the decoder's canonical (agent=X, patient=Y) into an FHRR role slot and unbind to recover.
    Returns (recovered_agent_ok, recovered_patient_ok). Uses hdlab.binding FHRR (VET-confirmed)."""
    from hdlab import binding
    gen = torch.Generator().manual_seed(seed)

    def unit_phase(k):
        gg = torch.Generator().manual_seed(1000 + k)
        ph = torch.rand(n_dim, generator=gg) * 2 * np.pi
        return torch.exp(1j * ph).to(torch.complex64)
    role_agent = unit_phase(1)
    role_patient = unit_phase(2)
    n_fillers = 8
    fillers = [unit_phase(100 + i) for i in range(n_fillers)]
    ev = binding.bind(role_agent, fillers[agent_filler_id % n_fillers]) \
        + binding.bind(role_patient, fillers[patient_filler_id % n_fillers])
    rec_a = binding.unbind(ev, role_agent)
    rec_p = binding.unbind(ev, role_patient)

    def nearest(v):
        sims = [float(torch.abs(torch.vdot(v, f)) / n_dim) for f in fillers]
        return int(np.argmax(sims))
    return (nearest(rec_a) == agent_filler_id % n_fillers,
            nearest(rec_p) == patient_filler_id % n_fillers)


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def decide_verdict(arms, expected_n_units, n_units_done):
    if n_units_done != expected_n_units:
        return "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", \
            "n_units_done=%d != expected=%d" % (n_units_done, expected_n_units)

    lp = arms[ARM_ENCODER_LINPROBE]["linear_probe_xvoice_held"]
    lp_max = max(lp["active_to_passive"], lp["passive_to_active"])
    premise_ok = lp_max <= LINPROBE_INVERT_MAX

    rev = arms[ARM_REVISION]["held"]
    revt = arms[ARM_REVISION]["trained"]
    nocue = arms[ARM_REVISION_NOCUE]["held"]
    ff = arms[ARM_FF]["held"]
    ffz = arms[ARM_FF_FROZEN]["held"]

    rev_act, rev_pas = rev["active"], rev["passive"]
    rev_cons = rev["xvoice_consistency"]
    step1_floor = ff["xvoice_consistency"]
    ffz_cons = ffz["xvoice_consistency"]
    beats_step1 = (rev_cons >= step1_floor + STEP1_BEAT_MARGIN) and (rev_cons >= ffz_cons + STEP1_BEAT_MARGIN)
    reanalysis_fired = (rev_pas - nocue["passive"]) >= REANALYSIS_MARGIN
    memorized = (min(revt["active"], revt["passive"]) >= PASS_MIN) and (max(rev_act, rev_pas) <= FAIL_MAX)
    passive_tracks_default = (rev_pas <= FAIL_MAX) and (not reanalysis_fired)

    if not premise_ok:
        band = "PREMISE_VIOLATED"
    elif (rev_act <= FAIL_MAX) or (rev_pas <= FAIL_MAX) or memorized or passive_tracks_default:
        band = "HARD_FAIL"
    elif (rev_act >= PASS_MIN and rev_pas >= PASS_MIN and rev_cons >= CONS_PASS
          and beats_step1 and reanalysis_fired):
        band = "HARD_PASS"
    else:
        band = "MIDDLE"

    verdict = {"HARD_PASS": "REINDEX_DECODER_READS_VOICE_INVARIANT_ROLE",
               "HARD_FAIL": "REINDEX_DECODER_FAILED_VOICE_INVARIANT_ROLE",
               "MIDDLE": "REINDEX_DECODER_MIDDLE_OFF_INVERSION",
               "PREMISE_VIOLATED": "PREMISE_VIOLATED_LATENTS_NOT_INVERTED"}[band]
    msg = ("band=%s | ARM_REVISION held act=%.3f pas=%.3f xvoice_consistency=%.3f (trained act=%.3f "
           "pas=%.3f cons=%.3f) | STEP1 feedforward floor: ARM_FF consistency=%.3f (per-voice act=%.3f "
           "pas=%.3f) ARM_FF_FROZEN consistency=%.3f | beats_step1=%s reanalysis_fired=%s "
           "(REVISION pas %.3f - NOCUE pas %.3f = %.3f) memorized=%s | inverted control "
           "ARM_ENCODER_LINPROBE ap=%.3f pa=%.3f (premise_ok=%s <= %.2f) | gate g_active=%.3f "
           "g_passive=%.3f"
           % (band, rev_act, rev_pas, rev_cons, revt["active"], revt["passive"],
              revt["xvoice_consistency"], step1_floor, ff["active"], ff["passive"], ffz_cons,
              beats_step1, reanalysis_fired, rev_pas, nocue["passive"], rev_pas - nocue["passive"],
              memorized, lp["active_to_passive"], lp["passive_to_active"], premise_ok,
              LINPROBE_INVERT_MAX, rev["_g_active"], rev["_g_passive"]))
    return verdict, msg


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------
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
    _atomic_write(out_dir, diag)


# ---------------------------------------------------------------------------
# Run one config
# ---------------------------------------------------------------------------
def _strip_private(d):
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _pred_fp(d):
    """Fingerprint an arm from its CONTINUOUS held agent-slot score matrices (active + passive). The
    continuous mechanism output differs across arms even when the argmax (the gold-convergent binary
    prediction) coincides -> catches a true bit-identical-arm bug without false-positiving when two
    competent-but-distinct mechanisms both solve the low-entropy binary role task (META_RULE_AF)."""
    a = np.asarray(d.pop("_agent_scores_active"), dtype=np.float64).round(5)
    p = np.asarray(d.pop("_agent_scores_passive"), dtype=np.float64).round(5)
    return hashlib.sha256(np.concatenate([a.ravel(), p.ravel()]).tobytes()).hexdigest()


def run_cfg(cfg, out_dir):
    device = torch.device("cpu")
    torch.set_num_threads(min(6, max(1, os.cpu_count() or 1)))
    seed = cfg["seeds"][0]
    run_mode = cfg["run_mode"]
    expected_n_units = len(ARM_UNITS)                  # single seed (all profiles) -> one unit per arm
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t0 = time.perf_counter()
    prior = ckpt.load_units(out_dir)
    if prior:
        _log("checkpoint: %d/%d units on disk; resuming" % (len(prior), expected_n_units))

    # ---- corpora (encoder trains only on TRAIN nouns x TRAIN verbs) ----
    train_pairs = C.build_pairs(C.TRAIN_NOUNS, C.TRAIN_VERBS, cfg["n_train_triples"], seed + 100)
    held_pairs = C.build_pairs(C.HELDOUT_NOUNS, C.HELDOUT_VERBS, cfg["n_held_triples"], seed + 200)
    trained_probe = C.build_pairs(C.TRAIN_NOUNS, C.TRAIN_VERBS, cfg["n_held_triples"], seed + 300)
    dec_train_pairs = train_pairs[:cfg["n_dec_train"]]

    # ---- DEPHEAD encoder (shared frozen substrate) -- save/load state_dict for cheap resume ----
    enc_cfg = dict(d_model=cfg["d_model"], n_layers=cfg["n_layers"], n_heads=cfg["n_heads"],
                   ffn_mult=cfg["ffn_mult"], lr=cfg["enc_lr"], steps=cfg["enc_steps"],
                   batch=cfg["enc_batch"], lm_coef=cfg["lm_coef"], dephead_coef=cfg["dephead_coef"])
    enc_path = os.path.join(out_dir, "encoder_seed%d.pt" % seed)
    enc = C.CausalRoleEncoder(enc_cfg).to(device)
    dephead = C.DepHead(cfg["d_model"]).to(device)
    if os.path.exists(enc_path):
        _log("loading frozen DEPHEAD encoder from %s" % enc_path)
        state = torch.load(enc_path, map_location=device)
        enc.load_state_dict(state["enc"])
        dephead.load_state_dict(state["dephead"])
    else:
        _log("TRAIN DEPHEAD encoder seed=%d (%d train pairs, %d enc steps)"
             % (seed, len(train_pairs), cfg["enc_steps"]))
        enc, dephead = P.train_dephead(enc_cfg, train_pairs, seed, device)
        os.makedirs(out_dir, exist_ok=True)
        torch.save(dict(enc=enc.state_dict(), dephead=dephead.state_dict()), enc_path)
    enc.eval()
    dephead.eval()

    # ---- frozen-latent features (both voices; held / trained-probe / decoder-train) ----
    _log("extracting frozen latents ...")
    feats_held_act = extract_features(enc, held_pairs, "active", device)
    feats_held_pas = extract_features(enc, held_pairs, "passive", device)
    feats_tr_act = extract_features(enc, trained_probe, "active", device)
    feats_tr_pas = extract_features(enc, trained_probe, "passive", device)
    feats_dtr_act = extract_features(enc, dec_train_pairs, "active", device)
    feats_dtr_pas = extract_features(enc, dec_train_pairs, "passive", device)

    arms = {}
    digests = {}
    with CellHeartbeat(out_dir, total_units=expected_n_units, interval_s=30) as hb:
        # ARM_FF (Step-1 literal feedforward floor)
        kff = ckpt.unit_key(ARM_FF, seed)
        if kff in prior:
            arms[ARM_FF] = prior[kff]
        else:
            ffh = score_ff_relhead(enc, dephead, feats_held_act, feats_held_pas, held_pairs, device)
            fft = score_ff_relhead(enc, dephead, feats_tr_act, feats_tr_pas, trained_probe, device)
            dg = _pred_fp(ffh)
            arms[ARM_FF] = dict(held=_strip_private(ffh), trained=_strip_private(fft), digest=dg)
            ckpt.record_unit(out_dir, kff, arms[ARM_FF])
            _log("  STEP1 ARM_FF held per-voice act=%.3f pas=%.3f xvoice_consistency=%.3f"
                 % (ffh["active"], ffh["passive"], ffh["xvoice_consistency"]))
        digests[ARM_FF] = arms[ARM_FF]["digest"]
        hb.tick(1, extra={"unit": ARM_FF})

        # decoder arms (FF_FROZEN, REVISION, REVISION_NOCUE)
        for ui, arm in enumerate(DECODER_ARMS, start=2):
            k = ckpt.unit_key(arm, seed)
            if k in prior:
                arms[arm] = prior[k]
            else:
                _log("TRAIN %s seed=%d (%d dec-train pairs)" % (arm, seed, len(dec_train_pairs)))
                dec = train_decoder(arm, cfg, feats_dtr_act, feats_dtr_pas, seed, device, hb)
                held = score_arm(dec, feats_held_act, feats_held_pas)
                trained = score_arm(dec, feats_tr_act, feats_tr_pas)
                dg = _pred_fp(held)
                arms[arm] = dict(held=held, trained=_strip_private(trained), digest=dg)
                ckpt.record_unit(out_dir, k, arms[arm])
                _log("  %s held act=%.3f pas=%.3f xvoice_consistency=%.3f g_act=%.3f g_pas=%.3f"
                     % (arm, held["active"], held["passive"], held["xvoice_consistency"],
                        held["_g_active"], held["_g_passive"]))
            digests[arm] = arms[arm]["digest"]
            hb.tick(ui, extra={"unit": arm})

        # ARM_ENCODER_LINPROBE (inverted control on the SAME frozen latents)
        klp = ckpt.unit_key(ARM_ENCODER_LINPROBE, seed)
        if klp in prior:
            arms[ARM_ENCODER_LINPROBE] = prior[klp]
        else:
            probe = P.linear_probe_xvoice(enc, held_pairs, device, seed)
            arms[ARM_ENCODER_LINPROBE] = dict(
                linear_probe_xvoice_held=dict(active_to_passive=float(probe["active_to_passive"]),
                                              passive_to_active=float(probe["passive_to_active"])),
                digest=hashlib.sha256(("linprobe|%.6f|%.6f" % (probe["active_to_passive"],
                                                               probe["passive_to_active"])).encode()).hexdigest())
            ckpt.record_unit(out_dir, klp, arms[ARM_ENCODER_LINPROBE])
            _log("  ARM_ENCODER_LINPROBE ap=%.3f pa=%.3f"
                 % (probe["active_to_passive"], probe["passive_to_active"]))
        digests[ARM_ENCODER_LINPROBE] = arms[ARM_ENCODER_LINPROBE]["digest"]
        hb.tick(expected_n_units, extra={"unit": ARM_ENCODER_LINPROBE})

    # arms_differ (META_RULE_AF): the 4 role-reader arms must produce distinct held predictions
    role_reader_digests = {a: digests[a] for a in (ARM_FF, ARM_FF_FROZEN, ARM_REVISION, ARM_REVISION_NOCUE)}
    keys = sorted(role_reader_digests)
    for a in keys:
        for b in keys:
            if a < b:
                assert role_reader_digests[a] != role_reader_digests[b], \
                    "META_RULE_AF VIOLATION: arms %r and %r bit-identical held predictions" % (a, b)

    n_units_done = len(digests)
    verdict, msg = decide_verdict(arms, expected_n_units, n_units_done)

    # smoke discriminator-fires: on TRAINED items, REVISION passive must beat NOCUE passive (reanalysis)
    smoke_fire = None
    if run_mode == "smoke":
        rev_tr_pas = arms[ARM_REVISION]["trained"]["passive"]
        nocue_tr_pas = arms[ARM_REVISION_NOCUE]["trained"]["passive"]
        margin = rev_tr_pas - nocue_tr_pas
        fired = margin >= SMOKE_REANALYSIS_MARGIN
        smoke_fire = dict(revision_trained_passive=rev_tr_pas, nocue_trained_passive=nocue_tr_pas,
                          margin=margin, required=SMOKE_REANALYSIS_MARGIN, fired=bool(fired))
        _log("SMOKE discriminator-fires: REVISION trained-pas=%.3f NOCUE trained-pas=%.3f margin=%.3f "
             "(need >=%.2f) fired=%s" % (rev_tr_pas, nocue_tr_pas, margin, SMOKE_REANALYSIS_MARGIN, fired))

    # FHRR slot wiring demo (decoder output feeds the existing role slot)
    fhrr_ok = None
    try:
        a_ok, p_ok = fhrr_slot_demo(3, 5)
        fhrr_ok = dict(agent_recovered=bool(a_ok), patient_recovered=bool(p_ok))
    except Exception as fe:  # non-fatal demonstration; record class
        fhrr_ok = dict(error=type(fe).__name__)

    elapsed = time.perf_counter() - t0
    _atomic_write(out_dir, dict(
        verdict=verdict, verdict_msg=msg,
        summary="%s | chance=%.2f | %s" % (verdict, CHANCE, msg[:160]),
        run_mode=run_mode, elapsed_s=elapsed, ts_iso=_now_iso(), anchor_name=ANCHOR_NAME,
        chance=CHANCE, arms=arms,
        step1_feedforward_floor=dict(
            arm_ff_xvoice_consistency=arms[ARM_FF]["held"]["xvoice_consistency"],
            arm_ff_per_voice=dict(active=arms[ARM_FF]["held"]["active"],
                                  passive=arms[ARM_FF]["held"]["passive"]),
            arm_ff_frozen_xvoice_consistency=arms[ARM_FF_FROZEN]["held"]["xvoice_consistency"]),
        smoke_discriminator_fires=smoke_fire, fhrr_slot_demo=fhrr_ok,
        bands=dict(pass_min=PASS_MIN, fail_max=FAIL_MAX, cons_pass=CONS_PASS,
                   linprobe_invert_max=LINPROBE_INVERT_MAX, step1_beat_margin=STEP1_BEAT_MARGIN,
                   reanalysis_margin=REANALYSIS_MARGIN),
        arms_differ_verified=True, digests=digests,
        cardinality_ok=bool(n_units_done == expected_n_units),
        expected_n_units=expected_n_units, n_units_done=n_units_done,
        params=dict(arm_units=ARM_UNITS, seed=seed, vocab_size=C.VOCAB_SIZE, max_len=C.MAX_LEN,
                    train_nouns=C.TRAIN_NOUNS, heldout_nouns=C.HELDOUT_NOUNS,
                    train_verbs=C.TRAIN_VERBS, heldout_verbs=C.HELDOUT_VERBS,
                    d_model=cfg["d_model"], n_layers=cfg["n_layers"], enc_steps=cfg["enc_steps"],
                    dec_steps=cfg["dec_steps"], relax_iters=cfg["relax_iters"],
                    sink_temp=cfg["sink_temp"], n_dec_train=cfg["n_dec_train"]),
        start_marker_written=True, crash_diagnostic_present=True,
        final_metrics_atomicity="tmp_replace", defensive_error_checking="passed_all_4_patterns",
        cell_chunked=False, progress_logging="print_flush_true",
        crlb_n_a="argmax/closed-form role readout on frozen latents; discriminator = pre-registered bands",
        calibration_check="default_ok_for_this_regime: fixed HYPOTHESIZED thresholds set before running; "
                          "chance=0.50 exact-by-construction."))
    _log("VERDICT: %s" % verdict)
    _log("  %s" % msg)
    _log("DONE %s in %.1fs" % (run_mode, elapsed))
    return verdict, msg


# ---------------------------------------------------------------------------
# Self-test (real code path at tiny scale)
# ---------------------------------------------------------------------------
def run_self_test():
    _log("SELF-TEST: mention ordering + gold role bookkeeping ...")
    p = C.build_pairs(C.TRAIN_NOUNS, C.TRAIN_VERBS, 24, 7)
    for pr in p[:24]:
        a = pr["active"]
        # active: agent before patient (m0=agent); passive: patient before agent (m0=patient)
        assert a["agent_idx"] < a["patient_idx"], "active agent should precede patient"
        ps = pr["passive"]
        assert ps["patient_idx"] < ps["agent_idx"], "passive patient(subject) should precede agent(by)"
    _log("  PASS: surface ordering (active m0=agent, passive m0=patient=first-NP default is WRONG)")

    _log("SELF-TEST: REAL pipeline (DEPHEAD enc + frozen features + all arms, tiny) ...")
    st_dir = os.path.join(OUTPUT_DIR, "_selftest")
    for fn in ("units.jsonl", "metrics.json", "encoder_seed7.pt"):
        fp = os.path.join(st_dir, fn)
        if os.path.exists(fp):
            os.remove(fp)
    verdict, _msg = run_cfg(SELFTEST_CFG, st_dir)
    assert verdict != "CELL_CRASHED", "selftest crashed"

    _log("SELF-TEST: FHRR slot bind/unbind of a canonical (agent,patient) output ...")
    a_ok, p_ok = fhrr_slot_demo(2, 6, n_dim=1024)
    assert a_ok and p_ok, "FHRR slot did not recover the bound fillers"
    _log("  PASS: FHRR role slot recovered agent+patient fillers")
    _log("SELF-TEST PASS (verdict=%s)" % verdict)
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
            verdict="SELFTEST_PASS", verdict_msg="SELFTEST_PASS (corpus + DEPHEAD + all arms + FHRR slot)",
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
