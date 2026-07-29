"""Entity-slot scaffold + learned write-gate on FROZEN encoder hidden states (2026-07-28).

Comprehension-frontier "design A" (see notes/comprehension_situation_model_frontier_scoping.md):
a small addressable entity-slot memory, keyed by a LEARNED role-general identity (content-based
addressing over the clause-1 hidden rep, NOT an entity-name/position rule), with a LEARNED scalar
write-gate deciding how strongly to trust/incorporate a clause-2 continuation into that slot. The
WRITE operation reuses `hdlab.sequence_memory.SequenceMatrix.bind_pair` UNMODIFIED (the substrate's
existing Hebbian ordered-pair primitive) -- one `SequenceMatrix` instance per slot.

THE LINE (supply STRUCTURE, not MECHANISM): slot count / addressing scheme / write primitive are
supplied structure (allowed). WHICH slot to address and WHETHER to write are LEARNED decisions
(addr_net / gate_net are trained by backprop against the downstream task) -- nothing here hand-codes
"which entity is being talked about" or "did the referent change". The encoder itself stays FROZEN;
only this small head (addr_net + gate_net, a few thousand params) is trained.

Two-stage plasticity (brain-plausible, and it sidesteps having to backprop through an in-place
Hebbian accumulator):
  (1) WRITE is a LOCAL, no_grad Hebbian update (`SequenceMatrix.bind_pair`) run over TRAIN
      COHERENT items only (the memory only ever learns what "normal" transitions look like), scaled
      by addr_weight[slot] * gate -- i.e. a neuromodulated-plasticity-style gated Hebbian write, not
      a rule-based one (the SCALE is a differentiable function of the current addr_net/gate_net, even
      though the accumulation step itself does not carry gradient).
  (2) READ is differentiable: for held items (train labelled + eval), `surprise_features` queries
      the (frozen, no_grad) slot content built in stage (1) and reports (a) 1-cosine(predicted,
      actual) "prediction-error/surprise" against the addr-weighted slot readback, (b) the gate's
      OWN opinion evaluated fresh on this item (a live forward pass through gate_net -- this is
      where GateNet gets a real gradient signal even though the memory WRITE itself was no_grad),
      and (c) address entropy (how confidently a single slot was chosen). These 3 scalars are the
      "readout" fed to the standard linear probe (matches every other readout arm in
      diag_order_critical_comprehension_calib_v1.score_readout_arm).
  addr_net + gate_net are trained end-to-end over several outer epochs: each epoch rebuilds the
  slots from empty (no_grad Hebbian pass with the CURRENT addr/gate), then computes the 3 features
  for ALL train items and backprops a small linear head's BCE loss through `surprise_features`
  (which is differentiable w.r.t. addr_net/gate_net) into addr_net + gate_net.

MANDATORY control (per the frontier note): `random_init=True` builds the IDENTICAL structure with
addr_net/gate_net left at their random PyTorch initialization (no optimizer steps at all) -- rules
out "the slot+gate STRUCTURE alone, without any learning, already produces the gain."
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from .sequence_memory import SequenceMatrix


class EntitySlotGate(nn.Module):
    """N_SLOTS content-addressable entity slots, each backed by a `SequenceMatrix`."""

    def __init__(self, d_model: int, n_slots: int = 4, hidden: int = 32, seed: int = 0) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_slots = n_slots
        g = torch.Generator().manual_seed(seed)
        self.addr_net = nn.Sequential(nn.Linear(d_model, hidden), nn.Tanh(), nn.Linear(hidden, n_slots))
        self.gate_net = nn.Sequential(nn.Linear(2 * d_model, hidden), nn.Tanh(), nn.Linear(hidden, 1))
        with torch.no_grad():
            for m in list(self.addr_net.modules()) + list(self.gate_net.modules()):
                if isinstance(m, nn.Linear):
                    m.weight.normal_(0.0, 0.05, generator=g)
                    m.bias.zero_()
        self.slots = [SequenceMatrix(d_model) for _ in range(n_slots)]

    def reset_slots(self) -> None:
        for s in self.slots:
            s.reset()

    def addr_weights(self, h1: torch.Tensor) -> torch.Tensor:
        """h1: [B, d_model] clause-1 rep -> [B, n_slots] softmax content-addressing weights."""
        return torch.softmax(self.addr_net(h1), dim=-1)

    def gate(self, h1: torch.Tensor, h2: torch.Tensor) -> torch.Tensor:
        """[B, d_model] x2 -> [B] write-strength in (0, 1)."""
        return torch.sigmoid(self.gate_net(torch.cat([h1, h2], dim=-1)).squeeze(-1))

    def write_train_batch(self, h1: torch.Tensor, h2: torch.Tensor) -> None:
        """Gated Hebbian write into ALL slots (soft addressing), TRAIN-COHERENT items only.
        NO_GRAD by design -- see module docstring "two-stage plasticity". Reuses
        `SequenceMatrix.bind_pair` UNMODIFIED: outer(k_next, k_prev) is bilinear, so scaling
        k_next by (addr_weight * gate) before calling bind_pair(h1, scaled_h2) is mathematically
        equivalent to scaling the whole gated Hebbian write -- no primitive modification needed.
        """
        with torch.no_grad():
            aw = self.addr_weights(h1)         # [B, n_slots]
            gw = self.gate(h1, h2)              # [B]
            for b in range(h1.shape[0]):
                for i in range(self.n_slots):
                    w = float(aw[b, i] * gw[b])
                    if w > 1e-6:
                        self.slots[i].bind_pair(h1[b], h2[b] * w)

    def surprise_features(self, h1: torch.Tensor, h2: torch.Tensor) -> torch.Tensor:
        """Differentiable READ. Returns [B, 3] = [surprise, gate_opinion, addr_entropy_norm].
        `surprise` = 1 - cosine(addr-weighted slot prediction, actual h2) against the (frozen,
        no_grad) slot content built by the most recent `write_train_batch` call. Gradient flows
        into addr_net via the address-weighted combination; `gate_opinion` is a FRESH forward pass
        through gate_net on THIS item (independent of slot content) so gate_net always has a live
        gradient path regardless of memory staleness.
        """
        aw = self.addr_weights(h1)              # [B, n_slots], grad-tracked
        gw = self.gate(h1, h2)                   # [B], grad-tracked
        preds = torch.stack([(self.slots[i].S.detach() @ h1.T).T for i in range(self.n_slots)], dim=1)  # [B, n_slots, d]
        pred_mix = (aw.unsqueeze(-1) * preds).sum(dim=1)          # [B, d]
        cos = F.cosine_similarity(pred_mix, h2, dim=-1)
        surprise = 1.0 - cos
        ent = -(aw.clamp_min(1e-8) * aw.clamp_min(1e-8).log()).sum(dim=-1)
        ent_norm = ent / torch.log(torch.tensor(float(self.n_slots)))
        return torch.stack([surprise, gw, ent_norm], dim=-1)


def fit_entity_slot_gate(d_model: int, h1_train, h2_train, y_train, *, n_slots: int = 4,
                          epochs: int = 12, lr: float = 0.02, seed: int = 0,
                          random_init: bool = False) -> EntitySlotGate:
    """Build + (optionally) train an EntitySlotGate. h1_train/h2_train: torch.FloatTensor [N, d];
    y_train: torch.LongTensor [N] in {0,1} (1 = CONSISTENT/COHERENT-label, used to select the
    WRITE subset -- the memory only ever learns from label==1 items, matching "the memory only
    learns what normal transitions look like").

    random_init=True: build the identical structure and do exactly ONE no_grad write pass with
    the RANDOM (never-optimized) addr_net/gate_net weights, then return -- the MANDATORY
    structure-without-learning control.
    """
    torch.manual_seed(seed)
    mod = EntitySlotGate(d_model, n_slots=n_slots, seed=seed)
    coh_mask = (y_train == 1)
    h1c, h2c = h1_train[coh_mask], h2_train[coh_mask]
    if coh_mask.sum().item() < 2:
        raise ValueError("fit_entity_slot_gate: fewer than 2 COHERENT (label=1) train items to write")

    if random_init:
        mod.write_train_batch(h1c, h2c)
        return mod

    opt = torch.optim.Adam(list(mod.addr_net.parameters()) + list(mod.gate_net.parameters()), lr=lr)
    clf = nn.Linear(3, 2)
    opt_clf = torch.optim.Adam(clf.parameters(), lr=lr)
    counts = torch.clamp(torch.bincount(y_train, minlength=2).float(), min=1.0)
    class_weight = counts.sum() / (2 * counts)
    last_loss = float("nan")
    for _ in range(epochs):
        mod.reset_slots()
        mod.write_train_batch(h1c, h2c)                 # no_grad, CURRENT addr/gate weights
        feats = mod.surprise_features(h1_train, h2_train)  # [N, 3], grad-tracked
        logits = clf(feats)
        loss = F.cross_entropy(logits, y_train, weight=class_weight)
        opt.zero_grad()
        opt_clf.zero_grad()
        loss.backward()
        opt.step()
        opt_clf.step()
        last_loss = float(loss.detach())
    if not torch.isfinite(torch.tensor(last_loss)):
        raise FloatingPointError("EntitySlotGate training diverged (non-finite loss)")
    # Final slot build with the fully-trained addr/gate weights (used by subsequent eval-time reads).
    mod.reset_slots()
    mod.write_train_batch(h1c, h2c)
    return mod
