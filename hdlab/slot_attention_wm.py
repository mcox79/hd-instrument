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

    def __init__(self, d_model: int, n_slots: int = 6, hidden: int = 64, seed: int = 0,
                 n_roles: int = 1) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_slots = n_slots
        g = torch.Generator().manual_seed(seed)
        # AUDIT GAP B (2026-07-29): ROLE-DIFFERENTIATED, ENTITY-FOCUSED addressing key.
        # A SMALL SET of `n_roles` LEARNED role-query vectors each attend (differentiable, softmax
        # over token positions, position-invariant) over the clause's TOKEN-LEVEL reps [B,L,d] to
        # extract a role-specific filler. Role 0 = the entity/subject role: its filler carries
        # ENTITY IDENTITY (which entity the clause is about), used both to ADDRESS (which slot) and
        # as the binding content KEY -- replacing the old single POOLED-CLAUSE key that blended
        # verb+all-entities and could not disambiguate WHICH tracked entity a clause updates (the
        # MES-specific floor). Parser-free / no bolt-on reader: the queries are learned parameters,
        # the attention is a differentiable softmax (Frankland&Greene2015 role-general, lmSTC).
        # n_roles=1 by default => exactly one entity-role query (no dead params); the [n_roles, d]
        # shape is kept so a future AGENT/PATIENT differentiation can add roles without a rewrite.
        self.n_roles = int(n_roles)
        self.role_query = nn.Parameter(torch.empty(self.n_roles, d_model))
        with torch.no_grad():
            self.role_query.normal_(0.0, 0.02, generator=g)
        # learned content key: NOW derived from the entity-role filler (was: pooled clause_rep).
        # role-general binding key derived from entity content, NOT position, NOT clause gist.
        self.role_key_net = _mlp(d_model, hidden, d_model, g)
        # PER-SLOT content-addressed competition (brain-faithful slot-attention, Locatello 2020):
        # a SHARED small MLP scores EACH slot from [clause_rep, slot_k] -> one logit; softmax
        # normalizes ACROSS slots. NO slots.mean() -- per-slot identity is preserved BEFORE the
        # addressing decision (the audit-C correction to the old mean-pool summary).
        self.addr_net = _mlp(2 * d_model, hidden, 1, g)
        # PER-SLOT PE-gated write (PBWM per-stripe, O'Reilly-Frank 2006): each slot's OWN
        # maintain-or-update decision. gate_net now MODULATES (learned fine control in [0,1]) the
        # PE-threshold boundary signal rather than being the free convex-blend gate it was in
        # ee714c31 -- see step() for the SEM/EST bistable segmentation write (audit gap C).
        self.gate_net = _mlp(2 * d_model + 1, hidden, 1, g)
        # addressing-softmax temperature (<1 => sharper competition => non-addressed slots are
        # truly HELD, approaching PBWM bistable maintain-OR-replace rather than a graded average).
        # Fixed low temp; keeps addr_w peaked while remaining fully differentiable (no hard argmax).
        self.addr_temp = 0.5
        # ----- BISTABLE PE-THRESHOLD EVENT-BOUNDARY WRITE (audit gap C; SEM/EST segmentation) -----
        # Comprehension = maintain event/entity states, HOLD the current model, and REPLACE only at
        # a prediction-error SPIKE (event boundary), NOT continuously average (Franklin/Gershman/
        # Norman/Zacks 2020 SEM; Zacks/Kurby Event Segmentation Theory). The write weight is
        # boundary_k = sigmoid((surprise_k - theta) / tau): a per-slot HOLD-vs-REPLACE decision.
        # theta = LEARNED PE threshold (event-boundary criterion, in surprise = 1-cos space).
        self.write_theta = nn.Parameter(torch.tensor(0.5))
        # tau = write temperature, ANNEALED soft->sharp: high tau early (~continuous, gradients
        # flow, trainable) -> low tau late (~bistable 0/1, brain-faithful discrete segmentation).
        # The fit-probe STUCK_FLAT finding (2026-07-29): a sharp gate from step 0 gives a degenerate
        # loss surface, so bistability MUST be annealed IN, never hard from the start. Default
        # schedule below; the FINAL schedule is set from the fit-probe sweep recipe when it lands.
        self.write_tau_start = 1.0   # soft start (near-continuous)
        self.write_tau_end = 0.1     # sharp end (near-bistable)
        self.write_tau = float(self.write_tau_start)
        # KB-SLOT PROTECTION (audit gap D): slot 0 holds the supplied KB world-model prior (Arm B).
        # Exempt it from ordinary write competition (small base write rate) so the prior PERSISTS
        # and BIASES inference instead of being eroded by ordinary blend writes. Applied ONLY when
        # kb_prior is present (Arm B); Arm A (kb_prior=None) is unaffected. A small nonzero rate
        # (not hard zero) still allows GENTLE assimilation of confirming evidence.
        self.kb_protect = 0.1

    def set_write_tau(self, tau: float) -> None:
        """Set the bistable write temperature directly (soft = high, sharp = low)."""
        self.write_tau = max(float(tau), 1e-4)

    def anneal_write_tau(self, frac: float) -> None:
        """Drive the soft->sharp write-tau anneal from a training-progress fraction in [0,1].
        Geometric interpolation write_tau_start -> write_tau_end (frac=0 soft, frac=1 sharp).
        The training loop calls this per epoch/step so the write gate starts near-continuous
        (trainable) and becomes near-bistable (brain-faithful segmentation) late in training."""
        frac = min(max(float(frac), 0.0), 1.0)
        ratio = self.write_tau_end / self.write_tau_start
        self.write_tau = max(self.write_tau_start * (ratio ** frac), 1e-4)

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

    def entity_filler(self, tok_reps: torch.Tensor,
                       pad_mask: torch.Tensor | None = None) -> torch.Tensor:
        """Entity-focused addressing representation (audit gap B). tok_reps: [B, L, d] token-level
        contextual reps; pad_mask: [B, L] bool (True == padding, excluded from attention). Each
        learned role query attends (softmax over token positions, padding masked to -inf) over the
        token reps to pull a role-specific filler; role 0 (entity/subject) is returned as [B, d].
        Position-invariant, parser-free, differentiable. Falls back to the pooled clause_rep at the
        call site when tok_reps is None (see step)."""
        B, L, d = tok_reps.shape
        scores = torch.einsum("bld,rd->brl", tok_reps, self.role_query) / math.sqrt(d)  # [B, R, L]
        if pad_mask is not None:
            scores = scores.masked_fill(pad_mask.unsqueeze(1), float("-inf"))
        attn = torch.softmax(scores, dim=-1)                              # [B, R, L] per-role weights
        fillers = torch.einsum("brl,bld->brd", attn, tok_reps)           # [B, R, d] role fillers
        return fillers[:, 0, :]                                           # [B, d] entity/subject role

    def step(self, slots: torch.Tensor, clause_rep: torch.Tensor,
              tok_reps: torch.Tensor | None = None, pad_mask: torch.Tensor | None = None,
              kb_prior: torch.Tensor | None = None) -> tuple[torch.Tensor, dict]:
        """One clause update. slots: [B, K, d]; clause_rep: [B, d] (pooled clause, the stored
        CONTENT); tok_reps: [B, L, d] token-level reps + pad_mask [B, L] for the entity-role query.
        Returns (new_slots [B,K,d], features dict with per-batch scalars + optional kb term).

        AUDIT GAP B (2026-07-29): the ADDRESSING KEY is now ENTITY-FOCUSED. `addr_src` = the
        role-query entity filler (from TOKEN-LEVEL reps) when tok_reps is given, ELSE the pooled
        clause_rep (byte-identical ee714c31 fallback, so run_clause_stream / the gen-curve diag are
        unchanged). The entity filler feeds BOTH (a) the binding content key `key` (role_key_net)
        and (b) the per-slot addressing competition (addr_net first half) -- routing clause t to the
        slot for THE ENTITY that clause is about, instead of by blended clause gist. The STORED
        CONTENT (candidate = bind(key, clause_rep)), the per-slot PE surprise_k, the per-slot PBWM
        write gate, and the temp-sharpened competition are UNCHANGED IN FORM from ee714c31 -- only
        the SOURCE of the key/addressing changes (pooled-clause -> entity role-query). Judge feature
        shape UNCHANGED (surprise/write_strength/addr_entropy are addr_w-weighted aggregates).

        PER-SLOT-LOCAL gating (audit-C, retained): addressing, prediction-error, and the write gate
        are ALL computed independently per slot -- NO slots.mean(), no single global write scalar.
        """
        B, K, d = slots.shape
        # ENTITY-FOCUSED addressing source (gap B); fallback to pooled clause_rep for old callers.
        addr_src = self.entity_filler(tok_reps, pad_mask) if tok_reps is not None else clause_rep
        key = F.normalize(self.role_key_net(addr_src), dim=-1)            # [B, d] key from ENTITY id
        clause_b = clause_rep.unsqueeze(1).expand(B, K, d)                # [B, K, d] stored CONTENT
        addr_b = addr_src.unsqueeze(1).expand(B, K, d)                    # [B, K, d] addressing input

        # PER-SLOT addressing: shared MLP scores [entity_filler, slot_k] -> one logit per slot;
        # softmax (temperature-sharpened) normalizes ACROSS slots. No mean-pool.
        addr_logits = self.addr_net(torch.cat([addr_b, slots], dim=-1)).squeeze(-1)  # [B, K]
        addr_w = torch.softmax(addr_logits / self.addr_temp, dim=-1)      # [B, K] sharp competition

        # PER-SLOT prediction error: unbind THAT slot with the content key, cos vs clause_rep.
        readback = unbind(slots, key.unsqueeze(1))                        # [B, K, d] per-slot unbind
        surprise_k = 1.0 - F.cosine_similarity(readback, clause_b, dim=-1)  # [B, K] each slot's own PE

        # PER-SLOT BISTABLE PE-THRESHOLD BOUNDARY (audit gap C; SEM/EST event segmentation):
        # a slot is REPLACED only when its OWN prediction error crosses the learned threshold
        # theta (an event boundary = PE spike); otherwise it HOLDS. boundary_k = sigmoid((PE -
        # theta)/tau) with tau ANNEALED soft->sharp so this is ~continuous (trainable) early and
        # ~bistable 0/1 (discrete segmentation, brain-faithful) late. This REPLACES the old free
        # continuous convex blend (write_k = sigmoid(gate_net)) whose graded per-step averaging was
        # the anti-thesis of discrete segmentation.
        tau = max(float(self.write_tau), 1e-4)
        boundary_k = torch.sigmoid((surprise_k - self.write_theta) / tau)  # [B, K] hold(0)/replace(1)

        # gate_net now MODULATES (learned fine control in [0,1]); it can only ATTENUATE the write,
        # so the PE-threshold boundary is the DOMINANT write signal (not a free gate).
        gate_in = torch.cat([clause_b, slots, surprise_k.unsqueeze(-1)], dim=-1)  # [B, K, 2d+1]
        gate_mod = torch.sigmoid(self.gate_net(gate_in)).squeeze(-1)      # [B, K] learned modulator
        write_k = boundary_k * gate_mod                                   # [B, K] per-slot write propensity

        # PER-SLOT update: w_k = addr_w * write_k = (which entity) x (is-this-a-boundary x learned mod).
        # A slot either HOLDS (w~0) or is REPLACED (w~1) at the bistable end -- not averaged.
        candidate = bind(key, clause_rep).unsqueeze(1)                    # [B, 1, d] role-bound content
        w_k = addr_w * write_k                                            # [B, K] per-slot weight
        # KB-SLOT PROTECTION (audit gap D, Arm B only): shield slot 0 (the supplied KB world-model
        # prior) from ordinary write competition so it PERSISTS and biases inference. Arm A
        # (kb_prior=None) unaffected. Multiplicative + out-of-place => fully differentiable.
        if kb_prior is not None:
            protect = torch.ones(K, device=slots.device, dtype=w_k.dtype)
            protect[0] = self.kb_protect
            w_k = w_k * protect.view(1, K)
        w_k = w_k.unsqueeze(-1)                                           # [B, K, 1] per-slot weight
        new_slots = (1.0 - w_k) * slots + w_k * candidate                # [B, K, d] HOLD-vs-REPLACE

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
                            kb_prior: torch.Tensor | None = None,
                            tok_reps: list[torch.Tensor] | None = None,
                            pad_masks: list[torch.Tensor] | None = None,
                            ) -> tuple[torch.Tensor, list[dict]]:
        """clause_reps: list of [B, d] pooled tensors (one per clause, same B throughout). Optional
        tok_reps/pad_masks: parallel lists of [B, L, d] / [B, L] for the entity-role query (gap B);
        if omitted, addressing falls back to pooled clause_rep (ee714c31 behavior). Returns
        (final_slots [B,K,d], per_step_feats list-of-dict, len == len(clause_reps))."""
        assert len(clause_reps) >= 1, "run_clause_stream needs >=1 clause"
        B = clause_reps[0].shape[0]
        device = clause_reps[0].device
        slots = self.init_slots(B, device, kb_prior=kb_prior)
        per_step = []
        for i, cr in enumerate(clause_reps):
            tr = tok_reps[i] if tok_reps is not None else None
            pm = pad_masks[i] if pad_masks is not None else None
            slots, feats = self.step(slots, cr, tok_reps=tr, pad_mask=pm, kb_prior=kb_prior)
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
