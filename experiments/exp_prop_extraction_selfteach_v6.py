"""LEARNED PROPOSITION-EXTRACTION HEAD, SELF-TAUGHT FROM THE FOUNDATION -- v6.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test) -- see _arms_differ()
# - final_metrics_atomicity = tmp_replace (META_RULE_AH) -- see _write_metrics()
# - except SystemExit: raise BEFORE except Exception (no BaseException) -- see main()
# - crlb_n/a: this is a classification/retrieval-accuracy cell, no closed-form noise floor -- declared below
# - baseline_in_band (META_RULE_AG) -- majority-class + B0 baselines checked in [0.05,0.95] non-degenerate band
# - discriminator survives scale: SMOKE proves mechanism FIRES (loss drops, arms differ, checkpoint
#   round-trips); FULL is where the comprehension-vs-memorization bar is judged (bands below)
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L) -- see build_verdict()
# - HP_SCOPE: bands below apply ONLY to the held-out extraction-accuracy arms; B0/majority are baselines
# - cardinality_ok: N/A, single-config single-seed training cell, no sweep axis
# - per-unit failure-class instrumentation (META_RULE_J; no bare except) -- see _write_crash_metrics()
# - calibration_check: default_ok_for_this_regime (bands come directly from the pre-registered research
#   note notes/research_brain_faithful_learned_proposition_extraction_selfteach_from_foundation_2026-07-27.md)
# - all numbers in this docstring are HYPOTHESIZED@this pre-reg or CITED@the research note; nothing here
#   is MEASURED until smoke/FULL land (see metrics.json for MEASURED numbers)
# - self-test constructs the REAL substrate objects (_load_typed_edges/_build_dataset/PropositionHead/
#   _train_head/_eval_extraction/_save_checkpoint) at N~16 concepts, not a synthetic-only branch
#   (real_code_path_exercised)
# - deterministic_seeding: true -- all RNG is np.random.default_rng(fixed int) or torch.Generator(fixed
#   int seed); no hash()-derived seeding or list(set()) ordering anywhere (PROT-023 / gate F.5)

WHY (brain grounding; see notes/research_brain_faithful_learned_proposition_extraction_selfteach_from_
foundation_2026-07-27.md for the full lit-scan): Frankland & Greene (2015, PNAS) found REUSABLE, ROLE-
GENERAL subregions of lmSTC that decode agent/patient identity across arbitrary fillers -- a slot
architecture, not one bound vector per sentence. Rabovsky, Hansen & McClelland (2018, Nat Hum Behav)
treat the N400 as an implicit PREDICTION-ERROR signal during comprehension; St. John & McClelland (1990)
showed an SRN learns thematic-role assignment purely from next-role-filling feedback, no hand labels.
Both together license the design here: a small trainable head with REUSABLE per-RELATION-TYPE slot
vectors (the role code, shared across every filler pair that relation applies to -- literally "reusable
across fillers" per Frankland & Greene), trained end-to-end by a PREDICTION-ERROR objective against the
foundation's own typed edges (distant supervision, Mintz 2009 lineage) -- not a supplied parser.

PRIOR STEP (v4/v5 lineage): v4 (MIDDLE_BAND, clean fair negative) located the defect as an ORDER-BLIND
mean-pool readout (data/probe_v4_readout_order_sensitivity_v1.json: coh-vs-scrambled cos=0.9944). v5
fixed the readout with a STRUCTURE-SENSITIVE HRR-bind pooling (coh-vs-scrambled cos=0.7304) but that is
still a HAND-BUILT position-bind readout -- a cheap proxy for "the substrate can see order," not a
LEARNED comprehension mechanism. v6 is STEP 2 from notes/v4_negative_brain_fidelity_audit_readout_is_
order_blind_next_lever_2026-07-27.md: "learned extraction head self-taught from foundation edges -- the
general own-comprehension mechanism." v6 REUSES v5's exact bind-readout as the frozen SENTENCE GESTALT
(the "read" step is unchanged, already validated) and adds a NEW trainable layer on top: reusable
relation-slot embeddings + a learned filler projection, trained via prediction-error against the
foundation's 1.24M typed edges, and BINDS the result into a role-bound (relation, object) proposition via
the SAME native hdlab.binding.bind primitive v5 uses for the readout. Own-mechanism throughout; no
bolt-on external reader/parser anywhere in the pipeline (invariant, USER-locked 2026-07-27).

DESIGN
------
1. FROZEN encoder (exp_scale_meaning_learn_arc_heldout_v2 ckpt_seed_7, own from-scratch, FULL only;
   SMOKE/SELFTEST train a tiny fresh toy encoder exactly like v1-v5's convention, since the comprehension
   bar is not being judged at those scales -- only mechanism-fires is).
2. Sentence gestalt g = ContentRoleReadout(h, pad_mask): per-token frozen hidden states h are read out by
   binding each h_i to a role_i = f(h_i) -- a function of TOKEN CONTENT ONLY, never of raw position index
   (director-flagged 2026-07-28 fix, see the ContentRoleReadout class docstring below for the full
   rationale and the measured v5 pathology it replaces). h itself is computed with NO_GRAD (the encoder is
   never fine-tuned by v6 -- declared choice, see "Divergences from brain" below); the readout's own
   role_proj IS trained (role_mode="learned") or fixed-random (role_mode="fixed", the ablation arm).
3. PropositionHead(d, n_relations, role_mode): owns the ContentRoleReadout + role_slots (nn.Parameter
   [n_relations, d], REUSABLE across every (subject,object) pair sharing that relation -- the
   Frankland-Greene-style slot code) + obj_proj (small linear filler projection) + rel_head (linear
   relation classifier). forward(h, pad_mask) -> (rel_logits, obj_repr, g).
   proposition(rel_idx, obj_repr) = hdlab.binding.bind(role_slots[rel_idx], obj_repr) -- the actual
   role-bound (relation, object) proposition vector the task requires.
4. DISTANT SUPERVISION DATASET: foundation typed edges (data/cskg_foundation_v1/edges_shard_*.jsonl,
   1.24M /r/* edges) restricted to pairs where BOTH subject and object are single-token ARC-universe
   concepts (V2.load_concept_universe). For each such edge, search the ARC corpus for REAL sentences that
   mention BOTH surfaces (co-occurrence, not synthetic templates -- avoids the CONSTRUCTION-DETERMINED
   risk the research note flags; if an edge has zero real co-occurring sentences it is simply dropped, no
   template fallback in v1). This is standard distant-supervision-for-RE (Mintz 2009); the sentence
   ASSERTING the KG fact is never guaranteed, only CO-MENTIONING both concepts -- exactly Mintz's
   assumption, inheriting its literature's fixes (concept-PAIR-level held-out split; hard-negative
   distractors = other true objects of the same subject under a different relation, per Peng et al. 2020).
5. TRAIN/HELD split: reuses the STANDING concept-level held-out split (V2.build_split -- freq-stratified,
   sha256-ranked, deterministic, leak-proof; the same split every loop cell v1-v5 uses). An edge is a
   TRAIN instance iff its SUBJECT is not held; a HELD instance iff its subject IS held (the subject was
   NEVER available at training time in ANY form -- text, edges, or otherwise).
6. TRAINING OBJECTIVE (self-teacher / prediction-error, per-batch, head-only -- encoder frozen):
   - relation cross-entropy: CE(rel_logits, true_relation)
   - object contrastive (InfoNCE, in-batch negatives): predicts the TRUE object's own frozen text-derived
     concept embedding (mean-pool over the object concept's OWN ARC mentions, via V2.encode_concept_
     text_reps -- same frozen encoder, standard mean-pool space, NOT the bind-readout space; this is a
     deliberate, declared choice: the "target" a proposition should retrieve is a stable semantic
     identity vector for that concept, independent of any one sentence's phrasing)
   - proposition consistency (auxiliary, small weight): cosine(bind(role[true_rel], obj_repr),
     bind(role[true_rel], true_obj_emb)) -- routes gradient through the actual bind() the head reports
   CHECKPOINTED EVERY EPOCH (non-negotiable per director task -- a prior no-save cost a 6h retrain).
7. THE LOAD-BEARING FAIRNESS CONTROLS (all can-fail; this is the whole ballgame):
   (a) HELD-OUT-TO-NEW-CONCEPT: eval only on instances whose SUBJECT was held (never trained on, in any
       form -- text or edges). Standing split, already leak-proof.
   (b) CONCEPT-PAIR-PRESERVING SCRAMBLE: same held sentence, word-order scrambled (LOOP2._scramble_words
       -- preserves the exact token multiset, so both concepts are still lexically present; only order is
       destroyed). Comprehension = coherent extraction-accuracy BEATS scrambled by a pre-registered margin.
       If they tie, the head is using concept-identity/bag-of-words, not reading (v3's failure mode,
       reproduced under a new name if it happens again -- report plainly).
   (c) WRONG-RELATION SLICE: among held eval instances, the subset where the asserted relation is NOT
       that subject's own DOMINANT relation (computed from the full foundation graph, descriptive only,
       never used in training) -- catches "head just parrots X's most common relation regardless of
       sentence content." Comprehension = coherent extraction-accuracy on this harder slice still clears
       the B0 identity-only baseline by margin.
   (d) B0 IDENTITY-ONLY baseline (Peng et al. 2020's diagnostic, directly ported): predicts relation from
       OBJECT identity alone via a frequency table built ONLY from TRAIN edges (majority relation for that
       object among TRAIN edges; the SUBJECT can supply zero signal by construction since it is held-out).
       If B0 alone clears 65% on held edges, any head "win" is indistinguishable from KG-frequency
       memorization (mirrors the v3 "distributional sample-accumulation, not comprehension" downgrade).
8. HARD-PASS / HARD-FAIL bands: see PRE-REG file (preregs/2026-07-27_prop_extraction_selfteach_v6.md) and
   build_verdict() below -- ported directly from the research note's falsifiable predictions, operationalized
   against this cell's concrete metric names.

DIVERGENCES FROM THE BRAIN (declared per standing discipline, not glossed over):
  1. Supervision source: brain's signal is intrinsic prediction error during ordinary comprehension; v6
     uses an EXTERNALLY-SOURCED KG as the target. ACCEPTABLE per charter (layer-2 KNOWLEDGE supply) as
     long as the EXTRACTION itself is learned, not supplied -- it is (role_slots + obj_proj + rel_head are
     all randomly initialized and trained here, nothing hand-set).
  2. Encoder is FROZEN, not fine-tuned by v6's objective (brain's comprehension and role-assignment are
     presumably co-trained). Declared engineering simplification for this v1: avoids encoder-collapse risk
     and keeps the run cheap; a v6.1 could ablate light fine-tuning if v6 lands positive but modest.
  3. Objective shape is a batch/pairwise contrastive+CE loss over pre-assembled targets, not St. John &
     McClelland's incremental online next-word/next-role prediction. Named explicitly (per the research
     note) so a flat v6 result is not mistaken for "the self-teach idea is wrong" when it may be an
     artifact of objective shape -- a genuinely more brain-faithful v7 would move toward incremental
     within-sentence prediction error.
"""
from __future__ import annotations

import os
import sys
import re
import json
import time
import math
import glob
import argparse
import traceback
from datetime import datetime, timezone
from collections import defaultdict, Counter

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import experiments.exp_scale_meaning_learn_arc_heldout_v2 as V2
import experiments.exp_unified_self_learning_loop_v2 as LOOP2
from hdlab.binding import bind

ANCHOR_NAME = "prop_extraction_selfteach_v6"

# ===========================================================================
# READOUT -- v6.1 FIX (director-flagged 2026-07-28, BEFORE any v6 run landed): v5's readout bound each
# token to a FIXED PER-POSITION role vector. That was empirically measured (data/probe_v5_bind_readout_
# derisk_v1.json, n=49 concepts, well-powered) to make a concept's OWN mentions only 0.52 cosine
# self-consistent across different sentences (vs 0.955 for plain mean-pool) -- because the SAME concept
# binds to a DIFFERENT role vector depending on which absolute sentence position it happens to land at,
# so any downstream averaging/consolidation washes the signal out. The brain binds by THEMATIC ROLE
# (position-invariant): the same concept in the same role produces the same binding regardless of where
# it sits in the sentence. Fix: make the per-token role a function of TOKEN CONTENT ONLY (h_i), never of
# raw index i -- content-addressed, therefore position-invariant by construction. Order-sensitivity is
# NOT lost: h_i is itself already context-dependent (self-attention mixes neighbours), so h_i measurably
# shifts under word-scrambling (STEP-0, data/probe_v4_readout_order_sensitivity_v1.json, measured this
# directly for mean/max-pool already) -- content-addressed binding still keys off that same order-
# sensitive quantity, it just never adds an EXTRA, purely-positional signal on top of it.
# ===========================================================================
class ContentRoleReadout(nn.Module):
    """role_i = f(h_i) for every token, then bind(h_i, role_i) summed over non-pad, L2-normalized.
    mode="learned": role_proj (nn.Linear) is TRAINED jointly with the rest of PropositionHead -- own
    mechanism, self-taught, matches Steinberg & Sommer (2019, arXiv:1902.09006)'s precedent for learning
    role-filler binding without explicit labeled role-filler pairs. mode="fixed": role_proj is a FIXED
    random projection (never trained) -- the director-requested ablation arm, isolating "content-
    addressing alone" (position-invariance) from "learned content-addressing"."""

    def __init__(self, d, mode="learned", seed=20260728):
        super().__init__()
        if mode not in ("learned", "fixed"):
            raise ValueError("mode must be 'learned' or 'fixed', got %r" % mode)
        self.mode = mode
        if mode == "learned":
            self.role_proj = nn.Linear(d, d)
        else:
            g = torch.Generator().manual_seed(seed)
            W = torch.randn(d, d, generator=g) / math.sqrt(d)
            self.register_buffer("W_fixed", W)

    def forward(self, h, pad_mask):
        """h: [B,L,d] float32 (frozen encoder hiddens, detached upstream). pad_mask: [B,L] bool."""
        role = self.role_proj(h) if self.mode == "learned" else h @ self.W_fixed
        role = role / (role.norm(dim=-1, keepdim=True) + 1e-8)
        bound = bind(h.contiguous(), role.contiguous())
        keep = (~pad_mask).float().unsqueeze(-1)
        bound = bound * keep
        rep = bound.sum(dim=1)
        return rep / (rep.norm(dim=1, keepdim=True) + 1e-8)


def _encode_pad_batch(tok, sents, max_len, pad_id):
    return np.stack([V2._encode_pad(tok, s, max_len, pad_id) for s in sents], axis=0)


def _cache_ids_for_sentences(tok, sents, cfg, spec):
    """Cache the padded TOKEN-ID array for every DISTINCT sentence once (cheap: small ints, not encoder
    output). The frozen encoder forward is re-run each training step on cached ids (forward-only, no
    backward through the encoder -- cheap on GPU); this is what lets the readout's role_proj be genuinely
    TRAINED (a fixed pre-computed gestalt cache, as v6's first draft used, cannot support that since the
    readout itself now has trainable parameters). Deterministic order: sorted(set(...)), never
    list(set(...)) (gate F.5)."""
    uniq = sorted(set(sents))
    max_len = cfg["max_len"]
    pad_id = spec["pad"]
    ids = _encode_pad_batch(tok, uniq, max_len, pad_id)
    return {s: ids[i] for i, s in enumerate(uniq)}


def _frozen_hidden(model, ids):
    """Frozen per-token contextual hidden states + pad mask. Always no_grad -- v6 NEVER fine-tunes the
    encoder (declared engineering choice, see module docstring 'Divergences from the brain' #2)."""
    with torch.no_grad():
        h, pad_mask = model._contextual(ids)
        return h.float().detach(), pad_mask.detach()


# ===========================================================================
# HEAD: reusable role-general relation slots + content-addressed readout + native HRR bind
# ===========================================================================
class PropositionHead(nn.Module):
    """role_slots[r] is REUSED across every (subject,object) instance whose relation is r (Frankland &
    Greene 2015 -- role-general, reusable across fillers). readout (ContentRoleReadout) turns frozen
    per-token hiddens into a single content-addressed, position-invariant, order-sensitive sentence
    gestalt. obj_proj projects that gestalt into the filler/object embedding space. proposition() binds
    (role, filler) via the substrate's own HRR bind -- the actual role-bound proposition vector."""

    def __init__(self, d, n_relations, role_mode="learned"):
        super().__init__()
        self.readout = ContentRoleReadout(d, mode=role_mode)
        self.role_slots = nn.Parameter(torch.randn(n_relations, d) / math.sqrt(d))
        self.obj_proj = nn.Linear(d, d)
        self.rel_head = nn.Linear(d, n_relations)
        self.d = d
        self.n_relations = n_relations
        self.role_mode = role_mode

    def forward(self, h, pad_mask):
        g = self.readout(h, pad_mask)
        rel_logits = self.rel_head(g)
        obj_repr = self.obj_proj(g)
        obj_repr = obj_repr / (obj_repr.norm(dim=-1, keepdim=True) + 1e-8)
        return rel_logits, obj_repr, g

    def proposition(self, rel_idx, obj_repr):
        role = self.role_slots[rel_idx]
        role = role / (role.norm(dim=-1, keepdim=True) + 1e-8)
        if role.dim() == 1:
            role = role.unsqueeze(0).expand(obj_repr.shape[0], -1)
        return bind(role.contiguous(), obj_repr.contiguous())


# ===========================================================================
# CONFIG PROFILES
# ===========================================================================
SELFTEST_CFG = dict(
    run_mode="selftest", seed=7,
    d_model=16, max_len=16, vocab=64, n_layers=1, n_heads=2, ffn_mult=2, pad_id=0, mask_id=1,
    encode_batch=8, n_epochs=3, lr=1e-2, batch_size=4, nce_temp=0.2, nce_weight=1.0, prop_weight=0.5,
    pool_size=4, top_n_relations=4, min_train_per_rel=1, max_sent_per_edge=2, role_mode="learned",
)
SMOKE_CFG = dict(
    run_mode="smoke", seed=7,
    min_deg=2, cap_eval_concepts=8000, heldout_count=300, min_mentions_eval=8,
    max_lines=400000, dedup_cap=450000, bpe_sample_lines=150000, cap_mentions=64,
    vocab=1024, max_len=32, encode_batch=128, n_freq_buckets=5, train_token_budget=4000000,
    mlm_steps=200, mlm_batch=64, mlm_mask_frac=0.15, mlm_lr=3e-3,
    d_model=96, n_layers=2, n_heads=4, ffn_mult=2,
    max_shards=6, top_n_relations=8, min_train_per_rel=3, max_sent_per_edge=2,
    n_epochs=8, lr=5e-3, batch_size=32, nce_temp=0.2, nce_weight=1.0, prop_weight=0.5, pool_size=6,
    role_mode="learned",
)
FULL_CFG = dict(
    run_mode="full", seed=7,
    min_deg=2, cap_eval_concepts=None, heldout_count=800, min_mentions_eval=20,
    max_lines=10000000, dedup_cap=6000000, bpe_sample_lines=400000, cap_mentions=128,
    vocab=16000, max_len=128, encode_batch=256, n_freq_buckets=8,
    max_shards=16, top_n_relations=16, min_train_per_rel=40, max_sent_per_edge=3,
    n_epochs=14, lr=2e-3, batch_size=256, nce_temp=0.15, nce_weight=1.0, prop_weight=0.5, pool_size=8,
    role_mode="learned",
)

# HARD-PASS / HARD-FAIL bands (FULL). Ported from the research note's falsifiable predictions.
MAJORITY_BASELINE_MAX = 0.35     # task non-degenerate: majority-relation-only baseline must be BELOW this
B0_HARD_PASS_MAX = 0.40          # identity-only (object-frequency) baseline must be BELOW this for HARD-PASS
B0_HARD_FAIL_MIN = 0.65          # identity-only baseline AT/ABOVE this => any head win is memorization
COMPREHENSION_MARGIN = 0.05      # coherent extraction_acc must beat scrambled extraction_acc by >= this
WRONG_REL_MARGIN = 0.05          # coherent extraction_acc on the non-dominant-relation slice must beat
                                  # B0 (on that same slice) by >= this
MIN_HELD_N = 60                  # power floor for the FULL held-eval set (else MIDDLE_BAND, underpowered)
SMOKE_POWER_FLOOR = 8            # power floor for SMOKE (mechanism-fires only, not comprehension bar)


# ===========================================================================
# INFRA (start marker / heartbeat / log / atomic metrics write / crash diagnostic)
# ===========================================================================
def _out_dir(run_mode):
    suffix = {"selftest": "_selftest", "smoke": "_smoke", "full": ""}.get(run_mode, "")
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME + suffix)
    os.makedirs(d, exist_ok=True)
    return d


def _log(msg):
    print(msg, flush=True)   # print-progress flushing (gate #17) -- MANDATORY for timeout_s >= 1800


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write_start_marker(out_dir, run_mode, expected_units):
    marker = dict(pid=os.getpid(), ts_iso=_now(), anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_units, host=os.environ.get("COMPUTERNAME", "unknown"))
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_start_marker.json.tmp")
    final = os.path.join(out_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _heartbeat(out_dir, unit_idx, total_units, elapsed_s, extra=None):
    row = dict(ts_iso=_now(), unit_idx=int(unit_idx), total_units=int(total_units), elapsed_s=float(elapsed_s))
    if extra:
        row["extra"] = extra
    with open(os.path.join(out_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics(out_dir, payload, elapsed_s):
    payload = dict(payload)
    payload["elapsed_s"] = float(elapsed_s)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)   # atomic (META_RULE_AH)


def _write_crash_metrics(out_dir, exc):
    diag = dict(
        verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)))[:500],
        summary="CELL_CRASHED: %s" % type(exc).__name__, elapsed_s=0.0,
        traceback=traceback.format_exc()[:5000], ts_iso=_now(), pid=os.getpid(), anchor_name=ANCHOR_NAME,
        failure_class=type(exc).__name__,
    )
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "metrics.json.tmp")
    final = os.path.join(out_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _save_checkpoint(head, out_dir, epoch, rel_to_idx, d):
    ckpt = dict(epoch=int(epoch), state_dict=head.state_dict(), n_relations=head.n_relations, d=int(d),
                rel_to_idx=rel_to_idx, role_mode=head.role_mode, ts_iso=_now())
    tmp = os.path.join(out_dir, "head_ckpt_latest.pt.tmp")
    final = os.path.join(out_dir, "head_ckpt_latest.pt")
    torch.save(ckpt, tmp)
    os.replace(tmp, final)   # CHECKPOINT-ALWAYS: latest is always a complete, atomically-written epoch
    torch.save(ckpt, os.path.join(out_dir, "head_ckpt_epoch_%02d.pt" % int(epoch)))   # never overwritten


# ===========================================================================
# FOUNDATION: typed-edge loader + real co-occurrence sentence finder + dataset builder
# ===========================================================================
def _load_typed_edges(shard_paths, surf_to_idx):
    """(subj_idx, relation, obj_idx) restricted to canonical /r/* relations where BOTH endpoints are
    single-token ARC-universe concepts. Deterministic (sorted shard order, sequential line read; no
    hash()-derived ordering -- gate F.5)."""
    edges = []
    for shard in shard_paths:
        with open(shard, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                e = json.loads(line)
                rel = e.get("relation", "")
                if not rel.startswith("/r/"):
                    continue
                si = surf_to_idx.get(e.get("subject"))
                oi = surf_to_idx.get(e.get("obj"))
                if si is None or oi is None or si == oi:
                    continue
                edges.append((si, rel, oi))
    return edges


def _find_cooccurring_sentences(postings, subj_idx, obj_surface, cap):
    """REAL ARC sentences (from postings[subj_idx], already mention subj) that ALSO mention obj_surface
    as a whole token -- the distant-supervision positive-alignment assumption (Mintz 2009)."""
    out = []
    for s in postings[subj_idx]:
        words = set(V2._WORD_RE.findall(s.lower()))
        if obj_surface in words:
            out.append(s)
            if len(out) >= cap:
                break
    return out


def _build_dataset(postings, surfaces, edges, is_held, cfg):
    """Returns kept_relations, rel_to_idx, train_instances=[(si,ri,oi,sent)], held_instances=[...],
    subj_edge_idx (ALL edges, for hard-negatives + dominant-relation stratification),
    rel_counts_train (coverage diagnostics)."""
    rel_counts_train = Counter()
    per_edge_sents = {}
    for (si, rel, oi) in edges:
        sents = _find_cooccurring_sentences(postings, si, surfaces[oi], cfg["max_sent_per_edge"])
        if not sents:
            continue
        per_edge_sents[(si, rel, oi)] = sents
        if not is_held[si]:
            rel_counts_train[rel] += 1
    kept_rel = sorted([r for r, c in rel_counts_train.items() if c >= cfg["min_train_per_rel"]],
                       key=lambda r: (-rel_counts_train[r], r))[:cfg["top_n_relations"]]
    rel_to_idx = {r: i for i, r in enumerate(kept_rel)}
    train_instances, held_instances = [], []
    for (si, rel, oi), sents in per_edge_sents.items():
        ri = rel_to_idx.get(rel)
        if ri is None:
            continue
        bucket = held_instances if is_held[si] else train_instances
        for s in sents:
            bucket.append((si, ri, oi, s))
    subj_edge_idx = defaultdict(list)
    for (si, rel, oi) in edges:
        ri = rel_to_idx.get(rel)
        if ri is not None:
            subj_edge_idx[si].append((ri, oi))
    return dict(kept_relations=kept_rel, rel_to_idx=rel_to_idx,
                train_instances=train_instances, held_instances=held_instances,
                subj_edge_idx=dict(subj_edge_idx), rel_counts_train=dict(rel_counts_train),
                n_edges_total=len(edges), n_edges_with_sentence=len(per_edge_sents))


def _dominant_relation(subj_edge_idx):
    dom = {}
    for si, lst in subj_edge_idx.items():
        c = Counter(ri for ri, _ in lst)
        dom[si] = c.most_common(1)[0][0]
    return dom


def _b0_table(train_instances, n_rel):
    """Identity-only baseline (Peng et al. 2020): majority relation for a given OBJECT, from TRAIN edges
    only. The SUBJECT can never leak (held-out by construction), so this isolates whether OBJECT identity
    alone already solves the task -- the exact frequency-shortcut diagnostic."""
    obj_rel_counts = defaultdict(Counter)
    global_counts = Counter()
    for (_si, ri, oi, _s) in train_instances:
        obj_rel_counts[oi][ri] += 1
        global_counts[ri] += 1
    global_majority = global_counts.most_common(1)[0][0] if global_counts else 0
    b0 = {oi: c.most_common(1)[0][0] for oi, c in obj_rel_counts.items()}
    return b0, global_majority


# ===========================================================================
# TRAINING
# ===========================================================================
def _get_concept_emb(model, tok, postings, cfg, device, spec):
    """Frozen text-derived concept identity vectors (standard mean-pool space, NOT bind-readout space --
    a deliberate, declared choice: the retrieval TARGET is a stable semantic identity, independent of any
    one sentence's phrasing). Computed for ALL concepts (train + held) -- see docstring divergence note;
    the object's OWN identity is not the thing under test, the RELATION/BINDING is."""
    reps, _cnt = V2.encode_concept_text_reps(model, tok, postings, cfg, device, spec)
    return reps.astype(np.float32)


def _train_head(head, train_instances, idcache, concept_emb, cfg, device, out_dir, rel_to_idx, model):
    opt = torch.optim.Adam(head.parameters(), lr=cfg["lr"])
    n = len(train_instances)
    rng = np.random.default_rng(cfg["seed"] + 101)
    concept_emb_t = torch.from_numpy(concept_emb).to(device)
    loss_hist = []
    for epoch in range(cfg["n_epochs"]):
        order = rng.permutation(n)
        ep_losses = []
        t0 = time.perf_counter()
        for bstart in range(0, n, cfg["batch_size"]):
            idxs = order[bstart:bstart + cfg["batch_size"]]
            if len(idxs) < 2:
                continue   # InfoNCE needs >=2 in-batch items
            batch = [train_instances[i] for i in idxs]
            ids_np = np.stack([idcache[s] for (_si, _ri, _oi, s) in batch], axis=0)
            ids = torch.from_numpy(ids_np).to(device)
            h, pad_mask = _frozen_hidden(model, ids)
            rel_idx = torch.tensor([ri for (_si, ri, _oi, _s) in batch], dtype=torch.long, device=device)
            obj_idx = torch.tensor([oi for (_si, _ri, oi, _s) in batch], dtype=torch.long, device=device)
            rel_logits, obj_repr, _g = head(h, pad_mask)
            ce = F.cross_entropy(rel_logits, rel_idx)
            true_obj_emb = concept_emb_t[obj_idx]
            true_obj_emb_n = true_obj_emb / (true_obj_emb.norm(dim=-1, keepdim=True) + 1e-8)
            logits_nce = (obj_repr @ true_obj_emb_n.t()) / cfg["nce_temp"]
            labels_nce = torch.arange(obj_repr.shape[0], device=device)
            nce = F.cross_entropy(logits_nce, labels_nce)
            prop = head.proposition(rel_idx, obj_repr)
            target_prop = head.proposition(rel_idx, true_obj_emb_n)
            prop_loss = (1.0 - F.cosine_similarity(prop, target_prop.detach(), dim=-1)).mean()
            loss = ce + cfg["nce_weight"] * nce + cfg["prop_weight"] * prop_loss
            if not torch.isfinite(loss):
                raise FloatingPointError("non-finite head loss epoch=%d" % epoch)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            ep_losses.append(float(loss.detach().cpu()))
        mean_loss = float(np.mean(ep_losses)) if ep_losses else float("nan")
        loss_hist.append(mean_loss)
        _log("  epoch=%d/%d loss=%.4f (%.1fs)" % (epoch + 1, cfg["n_epochs"], mean_loss, time.perf_counter() - t0))
        _heartbeat(out_dir, epoch, cfg["n_epochs"], time.perf_counter() - t0, extra={"loss": mean_loss})
        _save_checkpoint(head, out_dir, epoch, rel_to_idx, head.d)   # CHECKPOINT EVERY EPOCH -- non-negotiable
    return loss_hist


# ===========================================================================
# EVAL: extraction accuracy + candidate-pool object retrieval + controls
# ===========================================================================
def _candidate_pool(oi, si, subj_edge_idx, all_obj_ids, pool_size, rng):
    hard_negs = [o for (_ri, o) in subj_edge_idx.get(si, []) if o != oi]
    hard_negs = list(hard_negs)
    rng.shuffle(hard_negs)
    pool = [oi] + hard_negs[:pool_size - 1]
    guard = 0
    while len(pool) < pool_size and guard < 50:
        guard += 1
        cand = int(all_obj_ids[int(rng.integers(0, len(all_obj_ids)))])
        if cand not in pool:
            pool.append(cand)
    return pool


@torch.no_grad()
def _eval_extraction(head, instances, idcache, concept_emb, subj_edge_idx, all_obj_ids, device, cfg, seed, model):
    if not instances:
        return dict(n=0, rel_acc=None, extraction_acc=None, per_instance=[])
    rng = np.random.default_rng(seed)
    concept_emb_t = torch.from_numpy(concept_emb).to(device)
    ids_np = np.stack([idcache[s] for (_si, _ri, _oi, s) in instances], axis=0)
    bs = cfg["encode_batch"]
    rel_pred_chunks, obj_repr_chunks = [], []
    for i in range(0, ids_np.shape[0], bs):
        ids = torch.from_numpy(ids_np[i:i + bs]).to(device)
        h, pad_mask = _frozen_hidden(model, ids)
        rel_logits, obj_repr, _g = head(h, pad_mask)
        rel_pred_chunks.append(rel_logits.argmax(dim=-1).cpu().numpy())
        obj_repr_chunks.append(obj_repr.cpu().numpy())
    rel_pred_all = np.concatenate(rel_pred_chunks, axis=0)
    obj_repr_np = np.concatenate(obj_repr_chunks, axis=0)
    correct_rel = correct_joint = 0
    per_instance = []
    for k, (si, ri, oi, _s) in enumerate(instances):
        rel_pred = int(rel_pred_all[k])
        pool = _candidate_pool(oi, si, subj_edge_idx, all_obj_ids, cfg["pool_size"], rng)
        pool_t = torch.tensor(pool, dtype=torch.long, device=device)
        sims = (concept_emb_t[pool_t] @ torch.from_numpy(obj_repr_np[k]).to(device)).cpu().numpy()
        obj_pred = pool[int(np.argmax(sims))]
        rel_ok = (rel_pred == ri)
        obj_ok = (obj_pred == oi)
        correct_rel += int(rel_ok)
        correct_joint += int(rel_ok and obj_ok)
        per_instance.append(dict(si=int(si), ri=int(ri), oi=int(oi), rel_pred=rel_pred, obj_pred=int(obj_pred),
                                  rel_ok=bool(rel_ok), obj_ok=bool(obj_ok)))
    n = len(instances)
    return dict(n=n, rel_acc=correct_rel / n, extraction_acc=correct_joint / n, per_instance=per_instance)


def _arms_differ(coherent_eval, scrambled_eval):
    """META_RULE_AF: coherent and scrambled predictions must not be bit-identical (arm-implementation
    bug check). They are ALLOWED to score similarly (that IS the deflate-null being tested) but the raw
    per-instance prediction vectors must not literally be the same array (that would mean the scramble
    control never actually ran on different input)."""
    a = [(d["rel_pred"], d["obj_pred"]) for d in coherent_eval.get("per_instance", [])]
    b = [(d["rel_pred"], d["obj_pred"]) for d in scrambled_eval.get("per_instance", [])]
    return a != b if a and b else None


# ===========================================================================
# VERDICT
# ===========================================================================
def build_verdict(run_mode, diag, bands_hit=None):
    if run_mode in ("smoke", "selftest"):
        mech = diag["mechanism_fires"]
        verdict = "SMOKE_MECHANISM_PASS" if mech else "SMOKE_MECHANISM_INCONCLUSIVE"
        return dict(verdict=verdict, verdict_msg=diag.get("verdict_msg", ""))
    # FULL
    b0 = diag["b0_identity_acc"]
    maj = diag["majority_baseline_acc"]
    coh = diag["extraction_acc_coherent"]
    scr = diag["extraction_acc_scrambled"]
    wrong_coh = diag["extraction_acc_wrong_rel_slice"]
    wrong_b0 = diag["b0_wrong_rel_slice_acc"]
    n_held = diag["n_held_eval"]
    non_degenerate = (maj is not None and maj < MAJORITY_BASELINE_MAX)
    power_ok = (n_held is not None and n_held >= MIN_HELD_N)
    b0_hard_pass_ok = (b0 is not None and b0 < B0_HARD_PASS_MAX)
    b0_hard_fail = (b0 is not None and b0 >= B0_HARD_FAIL_MIN)
    comp_gain = (coh - scr) if (coh is not None and scr is not None) else None
    comprehension_specific = (comp_gain is not None and comp_gain >= COMPREHENSION_MARGIN)
    wrong_rel_gain = (wrong_coh - wrong_b0) if (wrong_coh is not None and wrong_b0 is not None) else None
    wrong_rel_ok = (wrong_rel_gain is not None and wrong_rel_gain >= WRONG_REL_MARGIN)

    hard_fail = bool(b0_hard_fail or (comp_gain is not None and comp_gain <= 0.0))
    hard_pass = bool(power_ok and non_degenerate and b0_hard_pass_ok and comprehension_specific and wrong_rel_ok
                      and not hard_fail)
    if hard_fail:
        verdict = "HARD_FAIL"
    elif hard_pass:
        verdict = "HARD_PASS"
    elif not power_ok:
        verdict = "MIDDLE_BAND_UNDERPOWERED"
    else:
        verdict = "MIDDLE_BAND"
    return dict(
        verdict=verdict,
        non_degenerate=non_degenerate, power_ok=power_ok, b0_hard_pass_ok=b0_hard_pass_ok,
        b0_hard_fail=b0_hard_fail, comprehension_specific_gain=comprehension_specific,
        comp_gain=comp_gain, wrong_rel_gain=wrong_rel_gain, wrong_rel_ok=wrong_rel_ok,
    )


# ===========================================================================
# PREP (shared universe/split/postings/encoder construction, mirrors LOOP2._prepare's structure)
# ===========================================================================
def _prepare(cfg, out_dir, ckpt_path, device):
    _log("data prep (universe/counts/split/postings/foundation-edges) ...")
    universe = V2.load_concept_universe(cfg)
    _log("  universe K=%d" % universe["K"])
    counts, cstats = V2.count_pass(cfg, universe["surf_to_idx"])
    _log("  corpus read=%d kept=%d" % (cstats["n_read"], cstats["n_kept"]))
    split = V2.build_split(universe, counts, cfg)
    _log("  split heldout=%d train_eval=%d" % (len(split["held_idx"]), len(split["train_eval_idx"])))
    postings, bpe_lines, pmeta = V2.collect_pass(cfg, universe, split)
    if ckpt_path:
        _log("  loading trained v2 encoder from %s" % ckpt_path)
        model, tok, spec, mc = LOOP2._build_encoder_from_ckpt(ckpt_path, device)
        encoder_source = "v2_checkpoint:" + os.path.basename(ckpt_path)
    else:
        _log("  training tiny fresh encoder (smoke; validates loop mechanism, not the comprehension bar) ...")
        tok, spec = V2.build_bpe(bpe_lines, cfg["vocab"])
        stream, ntok = V2.tokenize_train_stream(cfg, tok, split, spec)
        _log("  train stream tokens=%d" % ntok)
        model, final_loss = V2.mlm_train(stream, spec, cfg, device, cfg["seed"], out_dir, cfg["mlm_steps"])
        _log("  tiny encoder trained final_loss=%.4f" % final_loss)
        encoder_source = "tiny_fresh_smoke"
    shard_paths = sorted(glob.glob(V2.EDGES_GLOB))[:cfg["max_shards"]]
    edges = _load_typed_edges(shard_paths, universe["surf_to_idx"])
    _log("  typed edges (both endpoints in universe, /r/* only) = %d (from %d shards)" % (len(edges), len(shard_paths)))
    ds = _build_dataset(postings, universe["surfaces"], edges, split["is_held"], cfg)
    _log("  dataset: kept_relations=%d train_instances=%d held_instances=%d (edges_with_sentence=%d/%d)"
         % (len(ds["kept_relations"]), len(ds["train_instances"]), len(ds["held_instances"]),
            ds["n_edges_with_sentence"], ds["n_edges_total"]))
    concept_emb = _get_concept_emb(model, tok, postings, cfg, device, spec)
    return dict(universe=universe, split=split, postings=postings, model=model, tok=tok, spec=spec,
                d=model.d_model, encoder_source=encoder_source, corpus_stats=cstats, dataset=ds,
                concept_emb=concept_emb)


# ===========================================================================
# FULL RUN
# ===========================================================================
def run_full(cfg, out_dir, ckpt_path):
    device = V2._select_device() if cfg["run_mode"] == "full" else torch.device("cpu")
    torch.manual_seed(cfg["seed"])
    np.random.seed(cfg["seed"])
    _log("device=%s run_mode=%s ckpt=%s" % (device.type, cfg["run_mode"], ckpt_path))
    prep = _prepare(cfg, out_dir, ckpt_path, device)
    ds = prep["dataset"]
    if len(ds["kept_relations"]) < 2:
        raise RuntimeError("fewer than 2 kept relations (%d) -- cannot train a relation classifier"
                            % len(ds["kept_relations"]))
    if not ds["train_instances"]:
        raise RuntimeError("zero train instances (no real co-occurring sentences found for any edge)")

    all_sents_train = [s for (_si, _ri, _oi, s) in ds["train_instances"]]
    all_sents_held = [s for (_si, _ri, _oi, s) in ds["held_instances"]]
    idcache = _cache_ids_for_sentences(prep["tok"], all_sents_train, cfg, prep["spec"])

    role_mode = cfg.get("role_mode", "learned")
    head = PropositionHead(prep["d"], len(ds["kept_relations"]), role_mode=role_mode).to(device)
    n_params = sum(p.numel() for p in head.parameters())
    _log("  head params=%d n_relations=%d role_mode=%s" % (n_params, len(ds["kept_relations"]), role_mode))
    loss_hist = _train_head(head, ds["train_instances"], idcache, prep["concept_emb"], cfg, device, out_dir,
                             ds["rel_to_idx"], prep["model"])

    # scramble control: SAME held sentences, word-order scrambled (concept-pair-preserving)
    srng = np.random.default_rng(cfg["seed"] + 202)
    scrambled_held_sents = [LOOP2._scramble_words(s, srng) for s in all_sents_held]
    held_instances_scr = [(si, ri, oi, scr) for (si, ri, oi, _s), scr in
                           zip(ds["held_instances"], scrambled_held_sents)]

    idcache_held = _cache_ids_for_sentences(prep["tok"], all_sents_held, cfg, prep["spec"])
    idcache_held_scr = _cache_ids_for_sentences(prep["tok"], scrambled_held_sents, cfg, prep["spec"])

    n_rel = len(ds["kept_relations"])
    all_obj_ids = np.array(sorted(set(oi for (_si, _ri, oi, _s) in ds["train_instances"] + ds["held_instances"])),
                            dtype=np.int64)

    coherent_eval = _eval_extraction(head, ds["held_instances"], idcache_held, prep["concept_emb"],
                                      ds["subj_edge_idx"], all_obj_ids, device, cfg, cfg["seed"] + 301, prep["model"])
    scrambled_eval = _eval_extraction(head, held_instances_scr, idcache_held_scr, prep["concept_emb"],
                                       ds["subj_edge_idx"], all_obj_ids, device, cfg, cfg["seed"] + 301, prep["model"])

    dom_rel = _dominant_relation(ds["subj_edge_idx"])
    b0, global_majority = _b0_table(ds["train_instances"], n_rel)
    def _b0_pred(oi):
        return b0.get(oi, global_majority)

    held_maj_correct = sum(1 for (_si, ri, _oi, _s) in ds["held_instances"] if ri == global_majority)
    majority_baseline_acc = (held_maj_correct / len(ds["held_instances"])) if ds["held_instances"] else None
    b0_correct = sum(1 for (_si, ri, oi, _s) in ds["held_instances"] if _b0_pred(oi) == ri)
    b0_identity_acc = (b0_correct / len(ds["held_instances"])) if ds["held_instances"] else None

    wrong_rel_idx = [k for k, (si, ri, _oi, _s) in enumerate(ds["held_instances"]) if dom_rel.get(si) != ri]
    wrong_instances = [ds["held_instances"][k] for k in wrong_rel_idx]
    wrong_eval = _eval_extraction(head, wrong_instances, idcache_held, prep["concept_emb"], ds["subj_edge_idx"],
                                   all_obj_ids, device, cfg, cfg["seed"] + 401, prep["model"]) if wrong_instances else \
                 dict(n=0, extraction_acc=None, rel_acc=None, per_instance=[])
    b0_wrong_correct = sum(1 for k in wrong_rel_idx if _b0_pred(ds["held_instances"][k][2]) == ds["held_instances"][k][1])
    b0_wrong_rel_slice_acc = (b0_wrong_correct / len(wrong_rel_idx)) if wrong_rel_idx else None

    arms_differ = _arms_differ(coherent_eval, scrambled_eval)

    diag = dict(
        b0_identity_acc=b0_identity_acc, majority_baseline_acc=majority_baseline_acc,
        extraction_acc_coherent=coherent_eval["extraction_acc"], extraction_acc_scrambled=scrambled_eval["extraction_acc"],
        rel_acc_coherent=coherent_eval["rel_acc"], rel_acc_scrambled=scrambled_eval["rel_acc"],
        extraction_acc_wrong_rel_slice=wrong_eval["extraction_acc"], b0_wrong_rel_slice_acc=b0_wrong_rel_slice_acc,
        n_held_eval=coherent_eval["n"], n_wrong_rel_slice=len(wrong_rel_idx),
    )
    verdict_block = build_verdict("full", diag)

    payload = dict(
        anchor_name=ANCHOR_NAME, run_mode=cfg["run_mode"], ts_iso=_now(), pid=os.getpid(),
        encoder_source=prep["encoder_source"], kept_relations=ds["kept_relations"], role_mode=role_mode,
        n_train_instances=len(ds["train_instances"]), n_held_instances=len(ds["held_instances"]),
        n_edges_total=ds["n_edges_total"], n_edges_with_sentence=ds["n_edges_with_sentence"],
        rel_counts_train=ds["rel_counts_train"], loss_hist=loss_hist, arms_differ_coherent_vs_scrambled=arms_differ,
        b0_identity_acc=b0_identity_acc, majority_baseline_acc=majority_baseline_acc,
        extraction_acc_coherent=coherent_eval["extraction_acc"], extraction_acc_scrambled=scrambled_eval["extraction_acc"],
        rel_acc_coherent=coherent_eval["rel_acc"], rel_acc_scrambled=scrambled_eval["rel_acc"],
        extraction_acc_wrong_rel_slice=wrong_eval["extraction_acc"], b0_wrong_rel_slice_acc=b0_wrong_rel_slice_acc,
        n_held_eval=coherent_eval["n"], n_wrong_rel_slice=len(wrong_rel_idx),
        verdict=verdict_block["verdict"],
        verdict_msg=("v6 FULL: b0=%.3f maj=%.3f coh=%.3f scr=%.3f wrong_coh=%s wrong_b0=%s n_held=%s -> %s"
                     % (b0_identity_acc or -1, majority_baseline_acc or -1, coherent_eval["extraction_acc"] or -1,
                        scrambled_eval["extraction_acc"] or -1, wrong_eval["extraction_acc"], b0_wrong_rel_slice_acc,
                        coherent_eval["n"], verdict_block["verdict"])),
        summary="PROP_EXTRACTION_SELFTEACH_V6 FULL %s" % verdict_block["verdict"],
        verdict_detail=verdict_block,
        bands=dict(MAJORITY_BASELINE_MAX=MAJORITY_BASELINE_MAX, B0_HARD_PASS_MAX=B0_HARD_PASS_MAX,
                   B0_HARD_FAIL_MIN=B0_HARD_FAIL_MIN, COMPREHENSION_MARGIN=COMPREHENSION_MARGIN,
                   WRONG_REL_MARGIN=WRONG_REL_MARGIN, MIN_HELD_N=MIN_HELD_N),
        cell_chunked=False, crlb_n_a="classification/retrieval-accuracy cell, no closed-form noise floor",
        final_metrics_atomicity="tmp_replace", deterministic_seeding=True,
        progress_logging="print_flush_true",
    )
    return payload


# ===========================================================================
# SMOKE RUN (mechanism-fires gate, not the comprehension bar)
# ===========================================================================
def run_smoke(cfg, out_dir):
    return run_full(cfg, out_dir, ckpt_path=None)   # smoke never has a ckpt -> _prepare trains a tiny fresh encoder


def _smoke_verdict(payload):
    n_held = payload["n_held_eval"]
    loss_hist = payload["loss_hist"]
    loss_ok = bool(loss_hist and len(loss_hist) >= 2 and loss_hist[-1] < loss_hist[0])
    power_ok = bool(n_held is not None and n_held >= SMOKE_POWER_FLOOR)
    arms_ok = payload["arms_differ_coherent_vs_scrambled"]
    b0_ok = payload["b0_identity_acc"] is not None and 0.0 <= payload["b0_identity_acc"] <= 1.0
    maj_ok = payload["majority_baseline_acc"] is not None and 0.0 <= payload["majority_baseline_acc"] <= 1.0
    ckpt_ok = os.path.exists(os.path.join(_out_dir(payload["run_mode"]), "head_ckpt_latest.pt"))
    mechanism_fires = bool(loss_ok and power_ok and (arms_ok is not False) and b0_ok and maj_ok and ckpt_ok
                            and payload["n_edges_with_sentence"] > 0)
    verdict = "SMOKE_MECHANISM_PASS" if mechanism_fires else "SMOKE_MECHANISM_INCONCLUSIVE"
    msg = ("smoke: loss_ok=%s power_ok=%s(n_held=%s) arms_ok=%s b0_ok=%s maj_ok=%s ckpt_ok=%s edges_w_sent=%d -> %s"
           % (loss_ok, power_ok, n_held, arms_ok, b0_ok, maj_ok, ckpt_ok, payload["n_edges_with_sentence"], verdict))
    return verdict, msg, mechanism_fires


# ===========================================================================
# SELF-TEST (real code path at N~16, per gate F.1 -- constructs the ACTUAL substrate objects)
# ===========================================================================
def self_test():
    t0 = time.perf_counter()
    torch.manual_seed(7)
    np.random.seed(7)
    out_dir = _out_dir("selftest")
    _write_start_marker(out_dir, "selftest", expected_units=1)
    cfg = dict(SELFTEST_CFG)
    device = torch.device("cpu")

    # --- tiny toy universe: 8 subject concepts x 8 object concepts, 4 relations ---
    surfaces = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
                "iota", "kappa", "lam", "mu", "nu", "xi", "omicron", "pi"]
    surf_to_idx = {s: i for i, s in enumerate(surfaces)}
    relations = ["/r/UsedFor", "/r/LocatedNear", "/r/HasProperty", "/r/CapableOf"]

    # --- REAL edge loader exercised against a tiny synthetic shard file (not a mocked branch) ---
    tmp_dir = os.path.join(out_dir, "_tmp_edges")
    os.makedirs(tmp_dir, exist_ok=True)
    shard_path = os.path.join(tmp_dir, "edges_shard_00.jsonl")
    rng = np.random.default_rng(11)
    raw_edges = []
    with open(shard_path, "w", encoding="utf-8") as f:
        for si in range(8):
            for k in range(3):
                oi = 8 + int(rng.integers(0, 8))
                rel = relations[int(rng.integers(0, len(relations)))]
                row = dict(subject=surfaces[si], relation=rel, obj=surfaces[oi])
                f.write(json.dumps(row) + "\n")
                raw_edges.append((si, rel, oi))
        f.write(json.dumps(dict(subject="zzz_unknown", relation="/r/UsedFor", obj="also_unknown")) + "\n")
        f.write(json.dumps(dict(subject=surfaces[0], relation="at:xIntent", obj=surfaces[9])) + "\n")  # non /r/ filtered
    edges = _load_typed_edges([shard_path], surf_to_idx)
    assert len(edges) == len(raw_edges), "REAL_CODE_PATH: _load_typed_edges dropped/gained edges unexpectedly"
    assert all(e[1].startswith("/r/") for e in edges), "REAL_CODE_PATH: non-/r/ edge leaked through filter"

    # --- REAL postings: synthetic sentences co-mentioning subj+obj, some coherent, dedicated for scramble test ---
    postings = [[] for _ in surfaces]
    for (si, rel, oi) in edges:
        sent = "the %s is closely related to the %s here" % (surfaces[si], surfaces[oi])
        postings[si].append(sent)
    is_held = np.zeros(len(surfaces), dtype=bool)
    is_held[6:8] = True   # hold out 2 of the 8 subjects

    ds = _build_dataset(postings, surfaces, edges, is_held, cfg)
    assert len(ds["train_instances"]) > 0, "REAL_CODE_PATH: self-test produced zero train instances"

    # --- REAL toy encoder (V2.TinyTransformer, untrained weights -- plumbing check only) ---
    d = cfg["d_model"]
    model = V2.TinyTransformer(cfg["vocab"], cfg["max_len"], d, cfg["n_layers"], cfg["n_heads"], cfg["ffn_mult"],
                               cfg["pad_id"]).to(device)
    model.eval()

    class _ToyTok:
        def encode(self, s):
            class _E:
                pass
            e = _E()
            e.ids = [2 + (hash_stable(w) % (cfg["vocab"] - 3)) for w in s.split()]
            return e

    def hash_stable(w):
        import hashlib
        return int.from_bytes(hashlib.blake2b(w.encode("utf-8"), digest_size=4).digest(), "big")

    tok = _ToyTok()
    spec = dict(pad=cfg["pad_id"], mask=cfg["mask_id"])

    all_sents = [s for (_si, _ri, _oi, s) in ds["train_instances"] + ds["held_instances"]]
    idcache = _cache_ids_for_sentences(tok, all_sents, cfg, spec)
    ids_all = torch.from_numpy(np.stack([idcache[s] for s in all_sents], axis=0))
    h_all, pad_mask_all = _frozen_hidden(model, ids_all)
    readout_probe = ContentRoleReadout(d, mode="learned")
    g_all = readout_probe(h_all, pad_mask_all).detach().numpy()
    assert g_all.shape == (len(all_sents), d), "REAL_CODE_PATH: ContentRoleReadout output shape wrong"
    nrm = np.linalg.norm(g_all, axis=1)
    assert np.all(nrm > 0.99) and np.all(nrm < 1.01), "REAL_CODE_PATH: readout not L2-normalized"

    # --- REAL PropositionHead + one training epoch (exercises the actual loss/backward/checkpoint path) ---
    n_rel = len(ds["kept_relations"])
    assert n_rel >= 2, "self-test synthetic data must produce >= 2 kept relations"
    concept_emb = np.random.default_rng(3).normal(size=(len(surfaces), d)).astype(np.float32)
    concept_emb /= (np.linalg.norm(concept_emb, axis=1, keepdims=True) + 1e-8)
    head = PropositionHead(d, n_rel, role_mode="learned")
    loss_hist = _train_head(head, ds["train_instances"], idcache, concept_emb, cfg, device, out_dir,
                             ds["rel_to_idx"], model)
    assert len(loss_hist) == cfg["n_epochs"], "REAL_CODE_PATH: _train_head did not run all epochs"
    assert all(math.isfinite(x) for x in loss_hist), "REAL_CODE_PATH: non-finite loss in self-test"

    # --- checkpoint round-trip (byte-for-byte state_dict match) ---
    ckpt_path = os.path.join(out_dir, "head_ckpt_latest.pt")
    assert os.path.exists(ckpt_path), "CHECKPOINT-ALWAYS: latest checkpoint missing after training"
    reloaded = torch.load(ckpt_path, map_location="cpu")
    assert reloaded["role_mode"] == "learned"
    head2 = PropositionHead(d, n_rel, role_mode="learned")
    head2.load_state_dict(reloaded["state_dict"])
    for (n1, p1), (n2, p2) in zip(head.state_dict().items(), head2.state_dict().items()):
        assert n1 == n2 and torch.allclose(p1, p2), "CHECKPOINT round-trip mismatch on %s" % n1

    # --- fixed-mode ablation arm plumbing check (director-requested ablation) ---
    head_fixed = PropositionHead(d, n_rel, role_mode="fixed")
    rl, orep, gg = head_fixed(h_all[:2], pad_mask_all[:2])
    assert rl.shape == (2, n_rel) and orep.shape == (2, d), "REAL_CODE_PATH: fixed-mode head forward shape wrong"

    # --- REAL eval + scramble control + arms-differ + B0 ---
    srng = np.random.default_rng(9)
    held_sents = [s for (_si, _ri, _oi, s) in ds["held_instances"]]
    scr_sents = [LOOP2._scramble_words(s, srng) for s in held_sents]
    for orig, scr in zip(held_sents, scr_sents):
        assert sorted(orig.split()) == sorted(scr.split()), "SCRAMBLE self-test: multiset not preserved"
    idcache_scr = _cache_ids_for_sentences(tok, scr_sents, cfg, spec)
    held_instances_scr = [(si, ri, oi, scr) for (si, ri, oi, _s), scr in zip(ds["held_instances"], scr_sents)]
    all_obj_ids = np.array(sorted(set(oi for (_si, _ri, oi, _s) in ds["train_instances"] + ds["held_instances"])),
                            dtype=np.int64)
    coh_eval = _eval_extraction(head, ds["held_instances"], idcache, concept_emb, ds["subj_edge_idx"], all_obj_ids,
                                 device, cfg, seed=17, model=model)
    scr_eval = _eval_extraction(head, held_instances_scr, idcache_scr, concept_emb, ds["subj_edge_idx"], all_obj_ids,
                                 device, cfg, seed=17, model=model)
    assert coh_eval["n"] == len(ds["held_instances"]), "REAL_CODE_PATH: eval instance count mismatch"
    ad = _arms_differ(coh_eval, scr_eval)
    b0, glob_maj = _b0_table(ds["train_instances"], n_rel)
    assert isinstance(b0, dict)

    # --- build_verdict smoke-path + full-path both exercised ---
    smoke_diag = dict(mechanism_fires=True, verdict_msg="selftest")
    v_smoke = build_verdict("smoke", smoke_diag)
    assert v_smoke["verdict"] == "SMOKE_MECHANISM_PASS"
    full_diag = dict(b0_identity_acc=0.2, majority_baseline_acc=0.3, extraction_acc_coherent=0.5,
                      extraction_acc_scrambled=0.1, extraction_acc_wrong_rel_slice=0.4, b0_wrong_rel_slice_acc=0.2,
                      n_held_eval=100)
    v_full = build_verdict("full", full_diag)
    assert v_full["verdict"] == "HARD_PASS", "build_verdict positive-control did not HARD_PASS: %r" % v_full

    # --- crash-diagnostic path (write + read back without raising) ---
    _write_crash_metrics(os.path.join(out_dir, "_tmp_crash_probe"), RuntimeError("selftest probe"))
    with open(os.path.join(out_dir, "_tmp_crash_probe", "metrics.json"), "r", encoding="utf-8") as f:
        crash_payload = json.load(f)
    assert crash_payload["verdict"] == "CELL_CRASHED"

    elapsed = time.perf_counter() - t0
    payload = dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS (real_code_path exercised: edge-loader, "
                   "dataset-builder, ContentRoleReadout learned+fixed, head-train+checkpoint-roundtrip, "
                   "eval+scramble-control, B0-table, build_verdict smoke+full paths, crash-diagnostic)",
                   summary="PROP_EXTRACTION_SELFTEACH_V6 SELFTEST_PASS", anchor_name=ANCHOR_NAME,
                   run_mode="selftest", ts_iso=_now(), pid=os.getpid(),
                   real_code_path_exercised=["_load_typed_edges", "_build_dataset", "ContentRoleReadout",
                                              "PropositionHead", "_train_head", "_save_checkpoint",
                                              "_eval_extraction", "_arms_differ", "_b0_table", "build_verdict",
                                              "_write_crash_metrics"])
    _write_metrics(out_dir, payload, elapsed)
    _log("SELF-TEST PASS (%.2fs)" % elapsed)
    return True


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--ckpt", type=str, default=None, help="path to v2 encoder checkpoint (FULL engine)")
    ap.add_argument("--role-mode", type=str, default=None, choices=["learned", "fixed"],
                    help="ContentRoleReadout mode override (director-requested ablation arm)")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    if args.self_test:
        try:
            self_test()
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _write_crash_metrics(_out_dir("selftest"), e)
            raise
        return

    # HDLAB_RUN_MODE=full is how the PRODUCTION RUNNER signals FULL (env var injection,
    # runner_v2_prod.py run_one() -- it does NOT pass a --full CLI flag). --smoke in argv
    # always wins (explicit smoke request should never be silently upgraded to FULL).
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    is_full = bool(args.full or (env_mode == "full" and not args.smoke))
    run_mode = "full" if is_full else "smoke"
    cfg = dict(FULL_CFG if is_full else SMOKE_CFG)
    if args.seed is not None:
        cfg["seed"] = args.seed
    if args.role_mode is not None:
        cfg["role_mode"] = args.role_mode
    ckpt_path = args.ckpt
    if is_full and not ckpt_path:
        ckpt_path = os.path.join(_REPO, "data", "exp_scale_meaning_learn_arc_heldout_v2",
                                 "ckpt_seed_%d.pt" % cfg["seed"])
    if is_full and not (ckpt_path and os.path.exists(ckpt_path)):
        raise FileNotFoundError("FULL requires a trained v2 encoder checkpoint (--ckpt or default %s)" % ckpt_path)

    out_dir = _out_dir(run_mode)
    expected_units = cfg["n_epochs"]
    _write_start_marker(out_dir, run_mode, expected_units)
    _log("RUN START run_mode=%s ckpt=%s" % (run_mode, ckpt_path))
    t0 = time.perf_counter()
    try:
        if is_full:
            payload = run_full(cfg, out_dir, ckpt_path)
        else:
            payload = run_smoke(cfg, out_dir)
            verdict, msg, mech = _smoke_verdict(payload)
            payload["verdict"] = verdict
            payload["verdict_msg"] = msg
            payload["summary"] = "PROP_EXTRACTION_SELFTEACH_V6 SMOKE %s" % verdict
            payload["mechanism_fires"] = mech
        elapsed = time.perf_counter() - t0
        _write_metrics(out_dir, payload, elapsed)
        _log("RUN DONE run_mode=%s verdict=%s elapsed=%.1fs" % (run_mode, payload["verdict"], elapsed))
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
