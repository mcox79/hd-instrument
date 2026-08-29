"""Per-entity situation-model register: FHRR bind(role, event-slot) accumulated via
bundle, decoded via unbind + cleanup argmax.

Promotion of the VET-CONFIRMED accumulate-vs-overwrite organ (atom 29609,
experiments/exp_situation_model_accumulate_vs_overwrite_v1.py ARM B, capability_registry.jsonl
id situation_model_accumulate_register_organ) into a reusable hdlab/ module. Same algebra,
same decode as the validated cell -- reimplemented on torch complex64 tensors via the
canonical hdlab.binding.bind/unbind + hdlab.bundling.bundle primitives (the experiment cell
used bare numpy at its declared numpy/CPU pre-reg scope; this module follows CLAUDE.md's
torch-tensor-at-API-boundary convention instead, not a mechanism change).

ACCUMULATE (default, validated: accumulate=1.0000 vs overwrite=0.4600 vs floor=0.2100 on
real McGuffey multiclause entity-tracking gold, atom 29609, chain length 2-3): each entity's
register is the FHRR-bundle of ALL its (role, event-slot) bindings -- Kintsch C-I / Zwaan
multi-event indexing. Bounded by bundling capacity beyond the validated chain-length scope.

OVERWRITE (reserved mode, per Finding 3 of notes/wire_extraction_wm_real_text_entity_
tracking_design_2026-08-02.md): each entity's register is REPLACED by only the newest
binding -- genuine state-replacement (e.g. "the cup is now empty"), not multi-event history.
Structurally recovers only the last-written event (the Finding-3 too-simple negative control).
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

import torch

from . import binding, bundling


def unit_phase_vec(d: int, generator: torch.Generator) -> torch.Tensor:
    """Random unit-magnitude complex64 vector of dim d (FHRR atomic symbol)."""
    theta = torch.rand(d, generator=generator) * (2.0 * math.pi)
    return torch.polar(torch.ones(d), theta).to(torch.complex64)


def cleanup_argmax(
    readback: torch.Tensor, vocab: Dict[str, torch.Tensor]
) -> Tuple[str, Dict[str, float]]:
    """FHRR cleanup readout: argmax over vocab of Re(sum(conj(vocab_v) * readback)) / d."""
    d = readback.shape[0]
    scores: Dict[str, float] = {}
    for name, v in vocab.items():
        scores[name] = float(torch.real(torch.sum(torch.conj(v) * readback))) / d
    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return best, scores


def cleanup_set(
    readback: torch.Tensor, vocab: Dict[str, torch.Tensor], rel_margin: float = 0.5
) -> Tuple[List[str], Dict[str, float]]:
    """FHRR SET readout = CA3 context-cued reactivation of the whole event set bound at a context,
    instead of the single argmax. Returns EVERY vocab symbol whose cleanup score clears a margin
    relative to the peak (score >= rel_margin * peak, score > 0), sorted by score descending.

    Landed 2026-08-27 from the integrated `the_entity_store_is_a_dense_bundle_that_fans` (SOLVED/EXCELLENT,
    owner-DONE; witnesses test_entity_store_fan.py 21/21 + test_entity_store_frontier.py 26/26, re-verified
    FIRST-HAND). The measured LitBank "fan" (decode accuracy 0.945@few-events -> 0.657@many, slope 0.288) is
    NOT superposition blur: unique-(entity,slot) addresses decode at 1.0000 at EVERY load level, and the dense
    bundle keeps the information (a top-m read recovers the co-slot set at ~1.0). The fan is an ARGMAX-vs-SET
    readout artifact on a COARSE key where 22.7% of (entity,sentence) addresses hold >1 distinct verb (a busy
    character does several things per context). SET-return alone flattens the slope 0.288 -> 0.0003 (CI-sep),
    with an info-free shuffled-order twin LOSING (1.000 vs 0.502). This is the brain's read: CA3 pattern
    completion reactivates the whole set bound to the reinstated context (Nakazawa 2002; Bramao 2022).

    `rel_margin` is a DEPLOYABLE threshold (OUR-INVENTION, not brain-pinned): the pinned part is set-vs-argmax;
    the maximally faithful stop is the CMR race-to-stop (self-terminating, no oracle set size) validated in the
    frontier (F1 0.928 vs fixed-k 0.781) -- a follow-on. Paired brain-faithful fix (caller-side): a FINER
    conjunctive temporal key (within-sentence order = TCM drift) so co-context actions get distinct addresses;
    it flattens the fan equally and is where the finer index carries the specific-action info (twin loses)."""
    d = readback.shape[0]
    scores: Dict[str, float] = {}
    for name, v in vocab.items():
        scores[name] = float(torch.real(torch.sum(torch.conj(v) * readback))) / d
    peak = max(scores.values()) if scores else 0.0
    thresh = rel_margin * peak
    keep = sorted((r for r, s in scores.items() if s > 0.0 and s >= thresh), key=lambda r: -scores[r])
    return keep, scores


def _serial_scores(readback: torch.Tensor, role_mat: torch.Tensor) -> torch.Tensor:
    """Re(<role_v, readback>) for every filler v; role_mat (V,d) complex, readback (d,) complex -> (V,) real.
    Same cleanup scoring convention as cleanup_argmax (the /d normalization is argmax-invariant, omitted here)."""
    return torch.real(torch.conj(role_mat) @ readback)


def _serial_argmax(readback: torch.Tensor, role_mat: torch.Tensor) -> int:
    return int(torch.argmax(_serial_scores(readback, role_mat)))


def _serial_margin(readback: torch.Tensor, role_mat: torch.Tensor) -> float:
    """Gold-blind decode confidence = (top1 - top2) cleanup score / d (an SNR proxy = cue completeness)."""
    s = _serial_scores(readback, role_mat)
    top2 = torch.topk(s, 2).values
    return float((top2[0] - top2[1]) / readback.shape[0])


def decode_serial_slots(
    trace: torch.Tensor,
    keys: List[torch.Tensor],
    role_mat: torch.Tensor,
    n_iter: int = 6,
    order_by_conf: bool = True,
) -> List[int]:
    """Theta-gamma SERIAL decode-and-suppress readout of a SUPERPOSED multi-slot trace (Lisman & Idiart 1995;
    = successive-interference cancellation / resonator iterate). Verbatim port of the validated readout in
    experiments/exp_register_completion_readout_v1.py.

    Init each slot with an independent argmax, then iterate: reconstruct every slot's estimated binding and,
    for each slot (processed strongest-margin FIRST when order_by_conf), decode the RESIDUAL with the OTHER
    slots' current estimates SUBTRACTED (inhibition-of-return). Confident slots clean up ambiguous ones.
    n_iter = the gamma-cycle budget (a swept PARAMETER, not an adopted number). Same FHRR bind/unbind algebra
    as the organ. Returns the decoded role INDEX (into role_mat's row order) per key. The gain over independent
    per-slot argmax is known-key CROSSTALK CANCELLATION on the RAW LINEAR SUM (a per-slot Hopfield attractor
    ties argmax on i.i.d. separated codes -- no manifold; O'Reilly & McClelland 1994), NOT generic completion.
    """
    m = len(keys)
    est = [_serial_argmax(binding.unbind(trace, keys[s]), role_mat) for s in range(m)]
    for _ in range(n_iter):
        recon = [binding.bind(role_mat[est[s]], keys[s]) for s in range(m)]
        total = recon[0].clone()
        for s in range(1, m):
            total = total + recon[s]
        if order_by_conf:
            order = sorted(
                range(m),
                key=lambda s: -_serial_margin(binding.unbind(trace - (total - recon[s]), keys[s]), role_mat),
            )
        else:
            order = list(range(m))
        changed = False
        for s in order:
            residual = trace - (total - recon[s])          # suppress the OTHER slots' estimated bindings
            new = _serial_argmax(binding.unbind(residual, keys[s]), role_mat)
            if new != est[s]:
                total = total - recon[s]
                recon[s] = binding.bind(role_mat[new], keys[s])
                total = total + recon[s]
                est[s] = new
                changed = True
        if not changed:
            break
    return est


def _pooled_gain(trace: torch.Tensor, total: torch.Tensor) -> torch.Tensor:
    """Least-squares complex scalar g minimizing ||total - g*trace||^2 = <trace,total>/<trace,trace>. Lands g*trace on
    the reconstruction scale so the linear residual subtraction isolates one slot -- itself a POOLED divisive-
    normalization step at readout (one scalar over the whole vector), the same op-class as the store norm by design."""
    num = torch.sum(torch.conj(trace) * total)
    den = torch.sum(torch.conj(trace) * trace)
    if float(den.real) <= 1e-12:
        return torch.ones((), dtype=trace.dtype)
    return num / den


def decode_serial_pooled_slots(
    trace: torch.Tensor,
    keys: List[torch.Tensor],
    role_mat: torch.Tensor,
    n_iter: int = 6,
    order_by_conf: bool = True,
) -> List[int]:
    """Theta-gamma SERIAL decode-and-suppress made SCALE-EQUIVARIANT by pooled gain control -- the store-norm-agnostic
    readout. Verbatim port of the validated readout in experiments/exp_register_divisive_norm_v1.py. Identical to
    decode_serial_slots EXCEPT each iteration re-estimates ONE scalar gain matching the trace to the current
    reconstruction. On the raw sum g~=1 -> reduces to decode_serial_slots exactly; on a POOLED/scalar-normalized store
    (bundle_norm="divnorm") g~=the stored scale -> reads it identically; on the PER-COMPONENT store NO single scalar g
    matches (the distortion is per-component) -> the readout fails (the positive control). Returns the decoded role
    INDEX per key.
    """
    m = len(keys)
    est = [_serial_argmax(binding.unbind(trace, keys[s]), role_mat) for s in range(m)]  # scale-invariant init
    for _ in range(n_iter):
        recon = [binding.bind(role_mat[est[s]], keys[s]) for s in range(m)]
        total = recon[0].clone()
        for s in range(1, m):
            total = total + recon[s]
        g = _pooled_gain(trace, total)
        gtrace = g * trace                                  # trace lifted onto the reconstruction scale
        if order_by_conf:
            order = sorted(
                range(m),
                key=lambda s: -_serial_margin(binding.unbind(gtrace - (total - recon[s]), keys[s]), role_mat),
            )
        else:
            order = list(range(m))
        changed = False
        for s in order:
            residual = gtrace - (total - recon[s])          # suppress the OTHER slots' gain-matched estimates
            new = _serial_argmax(binding.unbind(residual, keys[s]), role_mat)
            if new != est[s]:
                total = total - recon[s]
                recon[s] = binding.bind(role_mat[new], keys[s])
                total = total + recon[s]
                est[s] = new
                changed = True
        if not changed:
            break
    return est


def _decode_argmax_slots(trace: torch.Tensor, keys: List[torch.Tensor], role_mat: torch.Tensor) -> List[int]:
    """Independent per-slot argmax cleanup (the cheap readout): unbind each key, argmax over role_mat."""
    return [_serial_argmax(binding.unbind(trace, keys[s]), role_mat) for s in range(len(keys))]


def _recon_residual(est: List[int], keys: List[torch.Tensor], role_mat: torch.Tensor, trace: torch.Tensor) -> float:
    """CA1-comparator (Vinogradova 2001) match/mismatch: reconstruct the superposition from the decoded estimates and
    measure how much of the stored trace it FAILS to explain. GOLD-BLIND (no truth). residual = ||trace - sum_s
    bind(est_s, key_s)|| / ||trace||. Low = the readout explains the trace (a near-exact match certifies the decode)."""
    recon = binding.bind(role_mat[est[0]], keys[0]).clone()
    for s in range(1, len(keys)):
        recon = recon + binding.bind(role_mat[est[s]], keys[s])
    return float(torch.linalg.vector_norm(trace - recon) / torch.linalg.vector_norm(trace).clamp_min(1e-12))


def decode_gated_slots(
    trace: torch.Tensor,
    keys: List[torch.Tensor],
    role_mat: torch.Tensor,
    n_iter: int = 6,
    clean_eps: float = 0.05,
    accept_eps: float = 0.15,
) -> Tuple[List[int], str]:
    """The readout that KNOWS WHEN to complete -- CA1 comparator (Vinogradova 2001) as an EXACT-MATCH gate. Verbatim
    port of the validated gate in experiments/exp_readout_recall_vs_rank_reconciliation_v1.py (register-readout bar
    item 4). Resolves the completion-helps-decode / hurts-ranking tension WITHOUT an oracle:
      (1) if argmax already reconstructs the trace (residual < clean_eps: full cue / low load) -> keep cheap argmax
          (completion inert; Nakazawa full-cue result);
      (2) else run serial and ACCEPT it ONLY if it (near-)EXACTLY reconstructs the trace (residual < accept_eps). The
          TRUE joint solution reconstructs the stored sum exactly; a SPURIOUS diverged solution at extreme overload
          reconstructs only PARTIALLY (a partial match IS the mismatch/novelty signal) -> REJECTED in favour of argmax.
    So it captures serial's overload gain where serial genuinely wins AND refuses serial's divergence at extreme
    overload -- tracking the better arm at every load. Returns (est_role_indices, which) with which in
    {"argmax_inert", "serial", "argmax_fallback"}.
    """
    est_a = _decode_argmax_slots(trace, keys, role_mat)
    if _recon_residual(est_a, keys, role_mat, trace) < clean_eps:
        return est_a, "argmax_inert"
    est_s = decode_serial_slots(trace, keys, role_mat, n_iter=n_iter)
    return (est_s, "serial") if _recon_residual(est_s, keys, role_mat, trace) < accept_eps else (est_a, "argmax_fallback")


class AccumulateRegister:
    """FHRR situation-model register: bind(role_vec, event_idx_vec) per event, accumulate via bundle.

    overwrite=False (default): register = bundle of ALL bound events for the entity (validated
    ACCUMULATE organ, atom 29609). overwrite=True: register = only the most recently bound
    event (reserved OVERWRITE / state-replacement mode, Finding 3).
    """

    def __init__(
        self,
        role_vocab: List[str],
        d: int,
        generator: torch.Generator,
        max_event_slots: int = 8,
        overwrite: bool = False,
        bundle_norm: str = "percomp",
        leak: float = 0.0,
    ) -> None:
        self.role_vocab = list(role_vocab)
        self.d = int(d)
        self.overwrite = bool(overwrite)
        self.max_event_slots = int(max_event_slots)
        # leak=0.0 (DEFAULT) -> flat running sum, BYTE-IDENTICAL to prior behavior. leak>0 -> the brain's ASYMMETRIC
        # leaky/recency WRITE S_j = (1-leak)*S_{j-1} + new (Warden & Miller 2007; Konecky 2017, PINNED-WEAK): recent
        # events dominate, old are geometrically suppressed, so recent context stays recoverable at ANY load where the
        # flat sum saturates (landed 2026-08-29 from `the_register_write_path_has_a_hard_capacity_wall`, SOLVED/
        # EXCELLENT). A FIXED geometric lambda^age is the faithful per-trace form (a single-store power law is emergent
        # from mixing exponentials). The leaky mode buys RECENT by decaying OLD (a fundamental single-store trade); pair
        # it with a salience-gated commit to HDFactStore for far-old events. Opt-in: nothing changes until leak>0.
        self.leak = float(leak)
        # bundle_norm="percomp" (DEFAULT) -> the incumbent per-component renorm (norm=None), BYTE-IDENTICAL to prior
        # behavior. "divnorm" -> pooled Carandini-Heeger divisive norm (a legit bounded, serially-readable stored
        # state; landed 2026-08-28 from `the_register_bundle_renorm_breaks_the_serial_readout`). A "divnorm" register
        # must be read by the gain-matched decode_serial_pooled (decode()/decode_serial's argmax path is scale-
        # invariant and works either way). Opt-in: nothing changes until a caller passes bundle_norm="divnorm".
        self.bundle_norm = str(bundle_norm)
        self._bundle_norm_arg = None if self.bundle_norm == "percomp" else self.bundle_norm
        self.role_vecs: Dict[str, torch.Tensor] = {
            r: unit_phase_vec(self.d, generator) for r in self.role_vocab
        }
        self.idx_vecs: List[torch.Tensor] = [
            unit_phase_vec(self.d, generator) for _ in range(self.max_event_slots)
        ]
        self._events: Dict[str, List[torch.Tensor]] = {}

    def add_event(self, entity: str, role: str, event_idx: int) -> None:
        """Bind role_vec to idx_vec at event_idx; accumulate (bundle) or overwrite entity's register."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        if not (0 <= event_idx < self.max_event_slots):
            raise ValueError(f"event_idx {event_idx} out of range [0, {self.max_event_slots})")
        bound = binding.bind(self.role_vecs[role], self.idx_vecs[event_idx])
        if self.overwrite:
            self._events[entity] = [bound]
        else:
            self._events.setdefault(entity, []).append(bound)

    def register(self, entity: str) -> torch.Tensor:
        """Entity's current register: bundle of all accumulated events, or the sole event if one.

        With leak>0, returns the ASYMMETRIC leaky/recency-weighted RAW sum S = sum_i (1-leak)^(k-1-i) * event_i
        (event k-1 is newest, weight 1; older events geometrically suppressed). The argmax cleanup (decode()) is
        scale-invariant so it reads this as the RECENT readout; per-component renorm would distort direction (the
        parent's measured rule -- read the raw recency-weighted sum)."""
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        if len(events) == 1:
            return events[0]
        if self.leak > 0.0:
            k = len(events)
            lam = 1.0 - self.leak
            w = torch.tensor([lam ** (k - 1 - i) for i in range(k)], dtype=torch.float32)
            wc = torch.complex(w, torch.zeros_like(w)).to(events[0].dtype)
            return (torch.stack(events, dim=0) * wc.unsqueeze(-1)).sum(dim=0)
        return bundling.bundle(torch.stack(events, dim=0), norm=self._bundle_norm_arg)

    def decode(self, entity: str, event_idx: int) -> Tuple[str, Dict[str, float]]:
        """Unbind entity's register by event_idx's key, then cleanup-argmax over role_vocab."""
        reg = self.register(entity)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_argmax(readback, self.role_vecs)

    def decode_set(self, entity: str, event_idx: int, rel_margin: float = 0.5) -> Tuple[List[str], Dict[str, float]]:
        """SET-return decode (CA3 context-cued reactivation): return ALL roles bound at (entity, event_idx)
        whose cleanup score clears the margin, not just the argmax. Flattens the addressing-collision fan where
        a coarse key holds >1 role (see cleanup_set). Additive / default-safe: decode() is unchanged."""
        reg = self.register(entity)
        readback = binding.unbind(reg, self.idx_vecs[event_idx])
        return cleanup_set(readback, self.role_vecs, rel_margin=rel_margin)

    def decode_serial(self, entity: str, event_idxs: List[int] = None, n_iter: int = 6) -> List[str]:
        """Theta-gamma SERIAL decode-and-suppress readout of ALL of an entity's occupied event slots at once,
        reading the RAW LINEAR SUM of the accumulated bindings (NOT the per-component-renorm register()). Recovers
        overloaded-register capacity that independent per-slot argmax cleanup (decode()) loses to crosstalk.
        ADDITIVE / default-safe: register(), decode() and decode_set() are byte-unchanged.

        Landed 2026-08-28 from the integrated `the_register_reads_by_argmax_not_recurrent_completion`
        (SOLVED/EXCELLENT, owner-DONE; witness test_register_completion_readout.py). The register capacity
        "cliff" is largely an ARGMAX-READOUT artifact: the RAW linear sum stays serially decodable where the
        per-slot argmax collapses (synthetic D=256: argmax 0.509 -> serial 0.983 at M=64 events, +0.454 CI-sep).
        The gain is known-key CROSSTALK CANCELLATION (a per-slot modern-Hopfield attractor ties argmax exactly on
        the register's i.i.d. separated codes -- no manifold to complete), NOT generic pattern completion (theta-
        gamma multiplexing, Lisman & Idiart 1995; successive-interference cancellation).

        Reads the RAW SUM, so it also bypasses the per-component bundle renorm that BREAKS the serial structure
        (renorm 0.119 << rawsum 0.983 at M=64 -- the open p5 bundle-renorm fidelity gap); once that normalization
        is made brain-faithful this reads the live register directly.

        event_idxs: which event-slot keys the stored bindings used, in stored (add_event) order. Defaults to
        range(len(events)) -- the standard sequential-accumulate pattern the readout result validated; pass explicit
        idxs if events were accumulated at non-sequential slots. Returns the decoded role name per stored event
        (same order as the add_event calls / event_idxs).
        """
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        m = len(events)
        if event_idxs is None:
            event_idxs = list(range(m))
        if len(event_idxs) != m:
            raise ValueError(f"event_idxs length {len(event_idxs)} != {m} stored events for {entity!r}")
        rawsum = torch.stack(events, dim=0).sum(dim=0)                       # raw linear superposition (NOT renorm)
        keys = [self.idx_vecs[i] for i in event_idxs]
        role_mat = torch.stack([self.role_vecs[r] for r in self.role_vocab], dim=0)  # (V,d) organ's own codebook
        est = decode_serial_slots(rawsum, keys, role_mat, n_iter=n_iter)
        return [self.role_vocab[i] for i in est]

    def decode_serial_pooled(self, entity: str, event_idxs: List[int] = None, n_iter: int = 6) -> List[str]:
        """Store-norm-AGNOSTIC theta-gamma serial readout: read the entity's NORMALIZED register() (whatever
        bundle_norm it was built with) via the gain-matched serial decode-and-suppress. This is the readout the
        `bundle_norm="divnorm"` store needs -- a pooled/scalar-normalized register is a legit bounded state and this
        reads it to the raw-sum ceiling, while the argmax path (decode()) stays scale-invariant. On a `bundle_norm=
        "percomp"` register it FAILS (no single scalar matches a per-component distortion -- the positive control).
        ADDITIVE / default-safe: register(), decode(), decode_set(), decode_serial() are byte-unchanged.

        Landed 2026-08-28 from the integrated `the_register_bundle_renorm_breaks_the_serial_readout` (SOLVED/EXCELLENT,
        owner-DONE; witness test_register_divisive_norm.py). Pairs with decode_serial (its raw-sum, unit-gain special
        case). event_idxs: which event-slot keys the stored bindings used, in stored order (defaults to sequential).
        Returns the decoded role name per stored event.
        """
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        m = len(events)
        if event_idxs is None:
            event_idxs = list(range(m))
        if len(event_idxs) != m:
            raise ValueError(f"event_idxs length {len(event_idxs)} != {m} stored events for {entity!r}")
        trace = self.register(entity)                                       # the NORMALIZED register (bundle_norm-aware)
        keys = [self.idx_vecs[i] for i in event_idxs]
        role_mat = torch.stack([self.role_vecs[r] for r in self.role_vocab], dim=0)
        est = decode_serial_pooled_slots(trace, keys, role_mat, n_iter=n_iter)
        return [self.role_vocab[i] for i in est]

    def decode_gated(self, entity: str, event_idxs: List[int] = None, n_iter: int = 6,
                     clean_eps: float = 0.05, accept_eps: float = 0.15) -> Tuple[List[str], str]:
        """CA1-comparator GATED readout of an entity's occupied event slots on the RAW LINEAR SUM: cheap per-slot
        argmax when it already reconstructs the trace (low load / full cue), else serial decode ACCEPTED only if it
        near-exactly reconstructs (captures serial's overload recovery) else argmax fallback (refuses serial's
        divergence at extreme overload). Tracks the better readout at EVERY load with NO oracle. ADDITIVE /
        default-safe: register(), decode(), decode_set(), decode_serial(), decode_serial_pooled() are byte-unchanged.

        Landed 2026-08-28 from the integrated `the_register_reads_by_argmax_not_recurrent_completion` (SOLVED/EXCELLENT,
        owner-DONE; bar item 4, witness test_register_completion_readout.py). Returns (roles_per_stored_event, which)
        with which in {"argmax_inert", "serial", "argmax_fallback"}. event_idxs default to sequential (the validated
        accumulate pattern).
        """
        events = self._events.get(entity)
        if not events:
            raise KeyError(f"no events recorded for entity {entity!r}")
        m = len(events)
        if event_idxs is None:
            event_idxs = list(range(m))
        if len(event_idxs) != m:
            raise ValueError(f"event_idxs length {len(event_idxs)} != {m} stored events for {entity!r}")
        rawsum = torch.stack(events, dim=0).sum(dim=0)                      # raw linear superposition (NOT renorm)
        keys = [self.idx_vecs[i] for i in event_idxs]
        role_mat = torch.stack([self.role_vecs[r] for r in self.role_vocab], dim=0)
        est, which = decode_gated_slots(rawsum, keys, role_mat, n_iter=n_iter,
                                        clean_eps=clean_eps, accept_eps=accept_eps)
        return [self.role_vocab[i] for i in est], which

    def entities(self) -> List[str]:
        """Entity ids with at least one recorded event."""
        return list(self._events.keys())


def make_situation_register(
    role_vocab: List[str],
    d: int,
    generator: torch.Generator,
    max_event_slots: int = 8,
    backend: str = "multibank",
    n_banks: int = 8,
    leak: float = 0.0,
):
    """Backend-selectable factory for the situation-model entity-event register.

    WIRE-DON'T-ISLAND wire-point (2026-08-03, closing the WIRED_BUT_NOT_PIPELINE_REACHABLE
    gap on hdlab.situation_model_multibank.MultiBankAccumulateRegister, capability_registry
    id situation_model_multibank / working_memory_multibank_K_capacity): every active-pipeline
    caller that used to construct AccumulateRegister directly (tools/read_anne_glassbox_v2_
    honest_ledger.py, hdlab/self_improving_loop.py) should call this factory instead so the
    memory backend is chosen in ONE place.

    backend="multibank" (DEFAULT): returns MultiBankAccumulateRegister with n_banks=8 -- the
    validated config from experiments/exp_situation_model_multibank_capacity_v1.py
    (data/exp_situation_model_multibank_capacity_v1/metrics.json), which holds decode
    self-consistency >=0.999 at n_events=256/entity (multibank_8=0.9992) where the flat
    register degrades to 0.6547 at the same load. Strictly >= flat at every swept load in that
    cell (n_events in {64,96,128,192,256}: multibank_8 in [1.0000, 0.9992], flat in
    [0.9781, 0.6547]) -- there is no regime in the measured sweep where flat beats multibank_8,
    so multibank is a safe default, not a scale-vs-small-scale tradeoff.

    HONEST SCOPE: at current pilot scale (few events/entity, e.g. the Anne consolidated-only
    situation model, bundle-load ~2) multibank and flat decode IDENTICALLY (both saturate near
    1.0 -- see verification/verify_situation_model_multibank_dropin.py). Switching the default
    here is NOT claimed to lift current comprehension-pipeline accuracy; it is capacity-
    headroom future-proofing (book-scale event counts will hit the flat-bundle wall this fixes)
    PLUS making the validated-but-previously-unreachable multibank module actually pipeline-USED
    per the capability registry's WIRED_AND_PIPELINE_USED gate.

    backend="flat": returns the original AccumulateRegister(overwrite=False) -- kept available
    as an explicit opt-out so no caller is forced onto multibank; pass backend="flat" to
    reproduce prior behavior exactly (bit-identical to constructing AccumulateRegister directly
    with the same args, since this branch does exactly that).
    """
    if backend == "flat":
        return AccumulateRegister(role_vocab, d, generator, max_event_slots=max_event_slots, leak=leak)
    if backend == "multibank":
        # Deferred import: situation_model_multibank imports FROM this module
        # (cleanup_argmax/unit_phase_vec), so a module-level import here would be circular.
        from .situation_model_multibank import MultiBankAccumulateRegister
        return MultiBankAccumulateRegister(
            role_vocab, d, generator, max_event_slots=max_event_slots, n_banks=n_banks, leak=leak
        )
    raise ValueError(f"unknown backend {backend!r}; expected 'multibank' or 'flat'")


class CausalLinkRegister(AccumulateRegister):
    """Passage-level CAUSE/EFFECT link register (2026-08-02 comprehension-arc extension).

    Extends AccumulateRegister VERBATIM (same bind/unbind/bundle/cleanup_argmax chain,
    same ACCUMULATE-via-bundle organ validated at atom 29609) to bind EVENT-to-EVENT
    causal links instead of ENTITY-to-role links. The "entity" key becomes an event-slot
    index (as str); the "role_vocab" becomes the fixed 2-symbol meta-role set
    {CAUSE, EFFECT}; the thing bound as "event_idx" is the OTHER linked event's own
    idx_vec (reusing the existing idx_vecs vocabulary, no new vector class).

    add_causal_link(cause_idx, effect_idx) writes BOTH directions in one call:
      - entity=str(cause_idx) accumulates bind(CAUSE_vec, idx_vecs[effect_idx])
        ("this event's effect is <effect_idx>")
      - entity=str(effect_idx) accumulates bind(EFFECT_vec, idx_vecs[cause_idx])
        ("this event's cause is <cause_idx>")
    Multiple links sharing an entity (an event that causes >1 effect, or is caused by
    >1 event) bundle into that entity's register exactly as multi-event entity chains do
    in the base class -- this is the SAME capacity-bounded accumulate organ, not a new one.

    query_effect_of(cause_idx) / query_cause_of(effect_idx) decode by unbinding the
    entity's register with the ROLE vector (mirror of the base class's decode(), which
    unbinds by the EVENT key and cleanup-argmaxes the role; here we unbind by the ROLE
    key and cleanup-argmax the EVENT vocabulary) -- same primitives, reversed which side
    is treated as "key" vs "vocabulary to search," which is a valid symmetry of FHRR
    bind (elementwise complex multiply is commutative).
    """

    CAUSE_ROLE = "CAUSE"
    EFFECT_ROLE = "EFFECT"

    def __init__(self, d: int, generator: torch.Generator, max_event_slots: int) -> None:
        super().__init__(
            role_vocab=[self.CAUSE_ROLE, self.EFFECT_ROLE],
            d=d,
            generator=generator,
            max_event_slots=max_event_slots,
            overwrite=False,
        )
        # per-entity set of roles actually bound (an entity can be present in self._events
        # with ONLY an EFFECT fact and no CAUSE fact, or vice versa -- decode must not guess
        # against an unbound role; base class has no per-role bookkeeping, so track it here).
        self._roles_present: Dict[str, set] = {}
        # cause_idx,effect_idx -> +1/-1 (2026-08-10 WIQA causal-chain-loop extension, see
        # add_causal_link docstring). Plain Python side-dict, NOT bound into the FHRR algebra --
        # a +-1 scalar has nothing to cleanup; existence + index recovery is still done by the
        # unchanged bind/bundle/cleanup_argmax chain below.
        self._link_polarity: Dict[Tuple[int, int], int] = {}

    def add_causal_link(self, cause_idx: int, effect_idx: int, polarity: int = 1) -> None:
        """Bind event cause_idx -> has-effect -> effect_idx, and the reverse, in one write.

        polarity (2026-08-10 extension, exp_wiqa_causal_chain_loop_v1): +1 (default) or -1 --
        signed CAUSE/EFFECT bit for propagating a perturbation's direction along a multi-hop
        chain (does cause_idx increasing make effect_idx increase [+1] or decrease [-1]?).
        Stored as a plain scalar side-dict, not encoded via bind/bundle (there is nothing to
        "clean up" about a +-1 sign; the existing FHRR CAUSE/EFFECT existence+index-recovery
        chain is UNCHANGED). Additive-only: default polarity=1 reproduces prior unsigned
        call sites exactly (query_effect_of/query_cause_of behavior is bit-for-bit unchanged).
        """
        if polarity not in (1, -1):
            raise ValueError(f"polarity must be +1 or -1; got {polarity!r}")
        self.add_event(str(cause_idx), self.CAUSE_ROLE, effect_idx)
        self._roles_present.setdefault(str(cause_idx), set()).add(self.CAUSE_ROLE)
        self.add_event(str(effect_idx), self.EFFECT_ROLE, cause_idx)
        self._roles_present.setdefault(str(effect_idx), set()).add(self.EFFECT_ROLE)
        self._link_polarity[(int(cause_idx), int(effect_idx))] = int(polarity)

    def query_link_polarity(self, cause_idx: int, effect_idx: int) -> int:
        """Return the signed polarity of the cause_idx->effect_idx link (+1 or -1).

        Raises KeyError if this exact (cause_idx, effect_idx) link was never added via
        add_causal_link -- an honest "no signed fact known" rather than a spurious default.
        """
        return self._link_polarity[(int(cause_idx), int(effect_idx))]

    def _decode_linked_event(self, event_idx: int, role: str) -> Tuple[object, Dict[str, float]]:
        """Unbind event_idx's register by role_vecs[role]; cleanup-argmax over idx_vecs vocab.

        Returns (None, {}) if event_idx has no accumulated fact of this SPECIFIC role
        (honest "no link known" rather than a spurious chance-level guess against a role
        that was never bound at all).
        """
        entity = str(event_idx)
        if role not in self._roles_present.get(entity, set()):
            return None, {}
        reg = self.register(entity)
        readback = binding.unbind(reg, self.role_vecs[role])
        vocab = {str(i): v for i, v in enumerate(self.idx_vecs)}
        best, scores = cleanup_argmax(readback, vocab)
        return int(best), scores

    def query_effect_of(self, cause_idx: int) -> Tuple[object, Dict[str, float]]:
        """Decode the effect event linked to cause_idx (or (None, {}) if none recorded)."""
        return self._decode_linked_event(cause_idx, self.CAUSE_ROLE)

    def query_cause_of(self, effect_idx: int) -> Tuple[object, Dict[str, float]]:
        """Decode the cause event linked to effect_idx (or (None, {}) if none recorded)."""
        return self._decode_linked_event(effect_idx, self.EFFECT_ROLE)


class RelationRegister(AccumulateRegister):
    """Two-role (GOAL_ROLE/OUTCOME_ROLE) register binding a role vector to an ARBITRARY supplied
    content concept-vector (2026-08-09, Direction-B build #2,
    exp_situation_model_relation_ablation_v1 -- see notes/exp_dev_handoff_research_psych_bridging_
    inference_situation_models_2026-08-09.md).

    Mirrors CausalLinkRegister's CAUSE/EFFECT role-extension pattern (same base class, same bind/
    bundle/unbind/cleanup_argmax chain) but generalizes what gets bound: CausalLinkRegister binds a
    role to another event's idx_vec (closed max_event_slots vocabulary, since it links event-slot
    indices to each other); this class binds a role to any externally-supplied concept vector (e.g.
    a word's lexical_similarity.concept_vector, or a quality_relation axis-position vector) via
    `bind_filler`, since the goal_outcome_relation ablation needs to carry an OPEN-vocabulary
    concept representation, not a closed idx_vecs symbol.

    Usage note (honest, not hidden): binding+immediately-unbinding a SINGLE filler on a role is
    mathematically EXACT (bind then unbind by the same unit-magnitude role vector recovers the
    input bit-for-bit -- unbind(bind(v,r),r) = v*r*conj(r) = v, since |r|=1), so `decode_filler`
    after exactly one `bind_filler` call on that role is a lossless passthrough, not noise
    injection. This register is used where GOAL_ROLE/OUTCOME_ROLE are bound on SEPARATE per-call
    ephemeral instances (see hdlab.goal_outcome_relation_grounded), specifically to preserve the
    Stage-1-confound-immunity invariant goal_outcome_relation.py's own docstring documents (goal-
    side and outcome-side features must stay independently computable, never a joint goal-word-vs-
    outcome-word comparison) -- its role here is ARCHITECTURAL CONSISTENCY with the proven organ
    (same primitives, auditable bind/unbind trace) and forward-compatibility with genuinely-
    multi-filler use (where bundling would introduce real interference), not a computational
    change on the single-filler case.
    """

    GOAL_ROLE = "GOAL"
    OUTCOME_ROLE = "OUTCOME"

    def __init__(self, d: int, generator: torch.Generator) -> None:
        super().__init__(
            role_vocab=[self.GOAL_ROLE, self.OUTCOME_ROLE],
            d=d,
            generator=generator,
            max_event_slots=1,
            overwrite=False,
        )

    def bind_filler(self, entity: str, role: str, content_vec: torch.Tensor) -> None:
        """Bind role_vecs[role] to an arbitrary content vector (NOT idx_vecs); accumulate
        (bundle) into entity's register exactly as add_event does internally."""
        if role not in self.role_vecs:
            raise KeyError(f"unknown role {role!r}; known={self.role_vocab}")
        bound = binding.bind(self.role_vecs[role], content_vec)
        self._events.setdefault(entity, []).append(bound)

    def decode_filler(self, entity: str, role: str) -> torch.Tensor:
        """Unbind entity's register by role_vecs[role] -> reconstruction of the bound content
        vector (exact if role was the only filler bound for this entity; see class docstring)."""
        reg = self.register(entity)
        return binding.unbind(reg, self.role_vecs[role])
