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
attention (softmax over slots given [clause_rep, slot_summary] -- the "competitive
attention" that gives slot-attention (Locatello 2020) its name: normalization is ACROSS
slots for a given input, not across inputs for a given slot).

KB-GROUNDING (Arm B, the framing-test variable; notes/drill_language_world_model_framing.md
section 6): a supplied KB PRIOR vector (encoded via the SAME encoder from real CSKG edge
text -- never a borrowed embedding) may seed slot 0 at reset and contributes an optional
`kb_consistency` readout term (agreement between the slot's addressed content and the KB
prior). Arm A leaves kb_prior=None (blank slots) -- see gen_kb_prior() below and the cell
script for how the two arms are wired.
"""
from __future__ import annotations

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
        # learned content-addressed competition over slots: reads [clause_rep, slot_summary]
        self.addr_net = _mlp(2 * d_model, hidden, n_slots, g)
        # learned PE-gated write strength: reads [clause_rep, addressed_readback, surprise_scalar]
        self.gate_net = _mlp(2 * d_model + 1, hidden, 1, g)

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
        """
        key = F.normalize(self.role_key_net(clause_rep), dim=-1)          # [B, d] content key
        slot_summary = slots.mean(dim=1)                                  # [B, d]
        addr_logits = self.addr_net(torch.cat([clause_rep, slot_summary], dim=-1))  # [B, K]
        addr_w = torch.softmax(addr_logits, dim=-1)                       # [B, K] competition-over-slots

        readback = unbind(slots, key.unsqueeze(1))                        # [B, K, d] per-slot unbind
        addr_readback = (addr_w.unsqueeze(-1) * readback).sum(dim=1)      # [B, d]
        surprise = 1.0 - F.cosine_similarity(addr_readback, clause_rep, dim=-1)  # [B]

        gate_in = torch.cat([clause_rep, addr_readback, surprise.unsqueeze(-1)], dim=-1)
        write_strength = torch.sigmoid(self.gate_net(gate_in)).squeeze(-1)  # [B], LEARNED PE-gate

        candidate = bind(key, clause_rep)                                  # [B, d] role-bound content
        w = (addr_w * write_strength.unsqueeze(-1)).unsqueeze(-1)          # [B, K, 1]
        new_slots = (1.0 - w) * slots + w * candidate.unsqueeze(1)

        ent = -(addr_w.clamp_min(1e-8) * addr_w.clamp_min(1e-8).log()).sum(dim=-1)
        addr_entropy = ent / torch.log(torch.tensor(float(self.n_slots)))

        feats = dict(surprise=surprise, write_strength=write_strength, addr_entropy=addr_entropy)
        if kb_prior is not None:
            kb_readback = unbind(new_slots, key.unsqueeze(1))              # [B, K, d]
            kb_pred = (addr_w.unsqueeze(-1) * kb_readback).sum(dim=1)      # [B, d]
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
