"""Coupled stateful core: brain-faithful slot-attention working memory (2026-07-29).

Basis: notes/stateful_core_situation_model_build_design.md +
notes/brain_foundational_component_analysis.md (component 6, WORKING MEMORY / active
maintenance -- the "likely THE structural block" gap) + component 8 (role-general BINDING).

THE ONE OPERATION: maintain K entity-state slots (full d-dim, NO scalar compression --
design-A's fatal error) over a clause stream; UPDATE a slot when new input is
inconsistent-with/extends it (prediction-error gated, PBWM-analog); bind fillers to slots
by a LEARNED CONTENT KEY (role-general, position-invariant -- Frankland-Greene; reuses
hdlab.binding HRR bind/unbind, NOT absolute-position binding, which is the v5 failure this
corrects).

THE LINE (supply STRUCTURE, not MECHANISM): slot count / competitive-attention addressing
scheme / HRR bind primitive are supplied structure (allowed, matches entity_slot_gate.py's
precedent). WHICH slot to address, HOW MUCH to write, and the content KEY itself are ALL
learned functions (addr_net / gate_net / role_key_net), trained end-to-end with the
encoder -- nothing here hand-codes "which entity is being discussed" or "is this
surprising". This is the correction to entity_slot_gate.py's HARD_FAIL_STRUCTURE_ALONE:
that design (a) bolted onto a FROZEN encoder, (b) compressed state to 3 scalars, (c) used
absolute-position addressing implicitly via train-time indexing. Here the encoder is
UNFROZEN (trained jointly), slots stay FULL d-dim, and addressing is learned content-based
attention scored PER SLOT from [clause_rep, slot_k] (temperature-sharpened softmax across
slots -- the "competitive attention" that gives slot-attention (Locatello 2020) its name:
normalization is ACROSS slots for a given input, not across inputs for a given slot). The
write is a PER-SLOT PBWM-style gate (O'Reilly-Frank 2006): each slot decides its own
maintain-or-update from its OWN prediction error -- NO mean-pool summary, NO single global
write scalar (the 2026-07-29 audit-C correction to the earlier mean-pool + convex-blend).

KB-GROUNDING (Arm B, the framing-test variable; notes/drill_language_world_model_framing.md
section 6): a supplied KB PRIOR vector (encoded via the SAME encoder from real CSKG edge
text -- never a borrowed embedding) may seed slot 0 at reset and contributes an optional
`kb_consistency` readout term (agreement between the slot's addressed content and the KB
prior). Arm A leaves kb_prior=None (blank slots) -- see gen_kb_prior() below and the cell
script for how the two arms are wired.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .binding import bind, unbind


def _mlp(in_dim: int, hidden: int, out_dim: int, seed_gen: torch.Generator) -> nn.Sequential:
    m = nn.Sequential(nn.Linear(in_dim, hidden), nn.Tanh(), nn.Linear(hidden, out_dim))
    with torch.no_grad():
        for layer in m.modules():
            if isinstance(layer, nn.Linear):
                layer.weight.normal_(0.0, 0.05, generator=seed_gen)
                layer.bias.zero_()
    return m


class SlotAttentionWM(nn.Module):
    """K full-d-dim entity slots, recurrently maintained + PE-gated-updated over a clause
    stream, with role-general (learned content-key) HRR binding. See module docstring.
    """

    def __init__(self, d_model: int, n_slots: int = 6, hidden: int = 64, seed: int = 0) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_slots = n_slots
        g = torch.Generator().manual_seed(seed)
        # learned content key (role-general binding key derived from clause content, NOT position)
        self.role_key_net = _mlp(d_model, hidden, d_model, g)
        # PER-SLOT content-addressed competition (brain-faithful slot-attention, Locatello 2020):
        # a SHARED small MLP scores EACH slot from [clause_rep, slot_k] -> one logit; softmax
        # normalizes ACROSS slots. NO slots.mean() -- per-slot identity is preserved BEFORE the
        # addressing decision (the audit-C correction to the old mean-pool summary).
        self.addr_net = _mlp(2 * d_model, hidden, 1, g)
        # PER-SLOT PE-gated write (PBWM per-stripe, O'Reilly-Frank 2006): each slot's OWN
        # maintain-or-update decision from [clause_rep, slot_k, surprise_k]. Shared weights,
        # applied broadcast across the K slot dimension.
        self.gate_net = _mlp(2 * d_model + 1, hidden, 1, g)
        # addressing-softmax temperature (<1 => sharper competition => non-addressed slots are
        # truly HELD, approaching PBWM bistable maintain-OR-replace rather than a graded average).
        # Fixed low temp; keeps addr_w peaked while remaining fully differentiable (no hard argmax).
        self.addr_temp = 0.5

    def init_slots(self, batch_size: int, device, kb_prior: torch.Tensor | None = None) -> torch.Tensor:
        """[B, n_slots, d]. Arm A: all-zero. Arm B: kb_prior (if given) seeds slot 0 -- the
        "world-model framing" target-state upgrade (blank text-situation-model -> foundation-
        grounded prior), matching notes/drill_language_world_model_framing.md section 6.
        """
        slots = torch.zeros(batch_size, self.n_slots, self.d_model, device=device)
        if kb_prior is not None:
            slots = slots.clone()
            slots[:, 0, :] = kb_prior
        return slots

    def step(self, slots: torch.Tensor, clause_rep: torch.Tensor,
              kb_prior: torch.Tensor | None = None) -> tuple[torch.Tensor, dict]:
        """One clause update. slots: [B, K, d]; clause_rep: [B, d].
        Returns (new_slots [B,K,d], features dict with per-batch scalars + optional kb term).

        PER-SLOT-LOCAL gating (audit-C rewrite, 2026-07-29): addressing, prediction-error, and
        the write gate are ALL computed independently per slot -- NO slots.mean(), no single
        global write scalar. Each slot k competes on its OWN content [clause_rep, slot_k] and
        decides its OWN update from its OWN surprise -- brain-faithful PBWM per-stripe gating +
        faithful Locatello per-slot competition. The judge-facing scalars (surprise /
        write_strength / addr_entropy) are addr_w-weighted aggregates of the per-slot quantities,
        so the downstream judge feature shape is UNCHANGED.
        """
        B, K, d = slots.shape
        key = F.normalize(self.role_key_net(clause_rep), dim=-1)          # [B, d] content key
        clause_b = clause_rep.unsqueeze(1).expand(B, K, d)                # [B, K, d] broadcast

        # PER-SLOT addressing: shared MLP scores [clause_rep, slot_k] -> one logit per slot;
        # softmax (temperature-sharpened) normalizes ACROSS slots. No mean-pool.
        addr_logits = self.addr_net(torch.cat([clause_b, slots], dim=-1)).squeeze(-1)  # [B, K]
        addr_w = torch.softmax(addr_logits / self.addr_temp, dim=-1)      # [B, K] sharp competition

        # PER-SLOT prediction error: unbind THAT slot with the content key, cos vs clause_rep.
        readback = unbind(slots, key.unsqueeze(1))                        # [B, K, d] per-slot unbind
        surprise_k = 1.0 - F.cosine_similarity(readback, clause_b, dim=-1)  # [B, K] each slot's own PE

        # PER-SLOT write gate (PBWM per-stripe): each slot's OWN maintain-or-update decision.
        gate_in = torch.cat([clause_b, slots, surprise_k.unsqueeze(-1)], dim=-1)  # [B, K, 2d+1]
        write_k = torch.sigmoid(self.gate_net(gate_in)).squeeze(-1)       # [B, K] LEARNED per-slot gate

        # PER-SLOT update: w_k = addr_w * write_k (sharp addr_w => non-addressed slots ~held).
        candidate = bind(key, clause_rep).unsqueeze(1)                    # [B, 1, d] role-bound content
        w_k = (addr_w * write_k).unsqueeze(-1)                            # [B, K, 1] per-slot weight
        new_slots = (1.0 - w_k) * slots + w_k * candidate                # [B, K, d] hold/replace-approach

        # aggregate per-slot -> the scalars the judge expects (shape UNCHANGED).
        surprise = (addr_w * surprise_k).sum(dim=-1)                     # [B]
        write_strength = (addr_w * write_k).sum(dim=-1)                  # [B]
        ent = -(addr_w.clamp_min(1e-8) * addr_w.clamp_min(1e-8).log()).sum(dim=-1)
        # divide by a PYTHON float (math.log), not a 0-dim CPU tensor: keeps addr_entropy on
        # `ent`'s device with no wrapped-scalar cross-device reliance (cuda-safe).
        addr_entropy = ent / math.log(self.n_slots)

        feats = dict(surprise=surprise, write_strength=write_strength, addr_entropy=addr_entropy)
        if kb_prior is not None:
            kb_readback = unbind(new_slots, key.unsqueeze(1))            # [B, K, d]
            kb_pred = (addr_w.unsqueeze(-1) * kb_readback).sum(dim=1)    # [B, d]
            feats["kb_consistency"] = F.cosine_similarity(kb_pred, kb_prior, dim=-1)
        return new_slots, feats

    def run_clause_stream(self, clause_reps: list[torch.Tensor],
                            kb_prior: torch.Tensor | None = None) -> tuple[torch.Tensor, list[dict]]:
        """clause_reps: list of [B, d] tensors (one per clause, same B throughout). Returns
        (final_slots [B,K,d], per_step_feats list-of-dict, len == len(clause_reps))."""
        assert len(clause_reps) >= 1, "run_clause_stream needs >=1 clause"
        B = clause_reps[0].shape[0]
        device = clause_reps[0].device
        slots = self.init_slots(B, device, kb_prior=kb_prior)
        per_step = []
        for cr in clause_reps:
            slots, feats = self.step(slots, cr, kb_prior=kb_prior)
            per_step.append(feats)
        return slots, per_step


def gen_kb_prior(encoder, tok_encode_fn, subj_kb_id: str, edges: list[tuple[str, str, str]],
                  device, max_edges: int = 6) -> torch.Tensor | None:
    """Build a KB-prior vector by encoding a short real-fact text (drawn from real CSKG
    edges -- see cell script for the edge lookup) through the SAME encoder (never a borrowed
    embedding -- the encoder earns the mapping; only the CONTENT is supplied). Returns a
    [d_model] tensor, or None if no edges found (Arm B degrades to Arm A for that item --
    the intended, honest "no KB content available" case, e.g. MES's generic-object entities).
    tok_encode_fn(text) -> LongTensor[1, L] token ids (padded), matching the encoder's own
    tokenizer/padding convention.
    """
    if not edges:
        return None
    frag = edges[:max_edges]
    text = " . ".join("%s %s %s" % (s, r.replace("/r/", "").lower(), o) for (s, r, o) in frag)
    ids = tok_encode_fn(text).to(device)
    with torch.no_grad():
        rep = encoder.pooled(ids)
    return rep.squeeze(0)
