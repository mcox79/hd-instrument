"""bound_event_backbone.py -- the TIERED bound-event-token backbone (the ASSEMBLY completion).

WHY THIS EXISTS (2026-09-01, landed by the strategy session from the owner-DONE problem
`the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token`, p4). The full-system p4
test proved the assembled reader is N PARALLEL SILOS: each situation dimension keeps its own LIST (the set
of agents / the set of actions / the set of times) and NOTHING stores the JOINT -- which agent did which
action at which time. That is the BINDING PROBLEM. This module is the fix, promoted VERBATIM from the
validated cell `experiments/exp_tiered_bound_event_token_coref_v1.py`: it COMPOSES already-built hdlab
organs (no new mechanism) into a tiered bound-event-token backbone --

    BIND      one FHRR bound token per event over {AGENT, PATIENT, PRED, TENSE}      (hdlab.binding +
              hdlab.situation_model_accumulate.unit_phase_vec -- the PINNED FHRR basis, SEM/Franklin 2020)
    CHUNK     segment the event stream at prediction-error boundaries                (hdlab.n400_coherence_monitor)
    STORE     a DG-sparse + CA3 episodic store                                       (hdlab.hippocampal_encoder)
    QUERY     resolve a partial event-mention against the stored bound tokens        (this module)

-- and proves it stores the JOINT the silos cannot (JOINT coref 1.000 vs late-fusion-of-marginals 0.600
CI-separated on LitBank old fiction AND UD-EWT modern web; binding-shuffle collapses it; the tiered store
holds at passage scale where a single flat superposition collapses ~1/sqrt(M)). See the problem's SOLVED.md.

BRAIN FRAME (PINNED): comprehension builds ONE bound event token per event indexed on all dimensions at once
(Zwaan & Radvansky 1998 event-indexing; Franklin 2020 SEM); recognising two mentions as the SAME event is
CA3 pattern completion from a partial cue (Marr 1971); the decisive control is RECOMBINATION -- same items
rebound differently -- the conjunctive-memory dissociation (Konkel & Cohen 2009). The brain MUST CHUNK
because one passage-scale superposition collapses ~1/sqrt(M) (Plate/Frady HD capacity).

THE READOUT ROUTE (honest fidelity note, from the p4 drill): coreference resolution uses the DIRECT
EC->CA3 similarity route over the raw bound tokens -- which completes at 1.00. The DG-separated CA3
RETRIEVAL path in `hippocampal_encoder` is a KNOWN low-fidelity follow-on (DG separation is an ENCODING
operation; retrieval should bypass DG, EC->CA3-direct), so `resolve()` uses the direct bound-token cleanup.
The DG/CA3 episodic store IS built (the STORE tier, for passage-scale consolidation + inspection); it is not
the coref query path. Making the CA3 net itself faithful is a scoped `hippocampal_encoder` follow-on.

GLASS-BOX, NO external LLM at inference. This module is promoted byte-for-byte from the cell's core codec
(`_seed_of` / `sym` / `event_token` / `cue_token` / `fhrr_score` / the role normalization), so a token built
here is torch-equal to the validated cell's token for the same event (witnessed:
verification/test_bound_event_backbone_landing_organ.py).
"""
from __future__ import annotations

import hashlib
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

from hdlab import binding
from hdlab.situation_model_accumulate import unit_phase_vec
from hdlab.n400_coherence_monitor import N400CoherenceMonitor
from hdlab.hippocampal_encoder import HippocampalEncoder

# --- OUR-INVENTION-UNDER-TEST constants, PROMOTED VERBATIM from the validated cell (do NOT retune here;
#     the witness pins byte-equality to the cell, and the FHRR dim D is what any fitted asset assumes) ---
D = 1024                      # FHRR dim
ROLES = ("AGENT", "PATIENT", "PRED", "TENSE")
JOINT_THRESH = 1.5            # principled midpoint between a 1-of-2 and a 2-of-2 attribute match (NOT tuned)
CONTENT_DIM = 256             # real-valued content space for the N400 segmenter (semantic-similar, not binding)
# DG/CA3 episodic-store construction params, matching the cell's partial_cue_completion tier build.
_DG_DIM = 4096
_DG_SPARSITY = 0.02
_DG_SEED = 7


# ===========================================================================
# Deterministic FHRR symbol space -- same string -> same vector, order-independent.
# (Promoted VERBATIM from experiments/exp_tiered_bound_event_token_coref_v1.py.)
# ===========================================================================
def _seed_of(s: str) -> int:
    return int.from_bytes(hashlib.sha256(s.encode("utf-8")).digest()[:8], "big") % (2 ** 63)


_SYM: Dict[str, torch.Tensor] = {}


def sym(s: str) -> torch.Tensor:
    """FHRR atomic symbol for a string filler/role (cached, deterministic by content hash)."""
    v = _SYM.get(s)
    if v is None:
        v = unit_phase_vec(D, torch.Generator().manual_seed(_seed_of(s)))
        _SYM[s] = v
    return v


_CONTENT: Dict[str, np.ndarray] = {}


def content_vec(s: str) -> np.ndarray:
    """Real Gaussian embedding of a content word (for the N400 CONTENT-space segmenter, NOT binding space)."""
    v = _CONTENT.get(s)
    if v is None:
        g = np.random.default_rng(_seed_of("content::" + s) % (2 ** 32))
        v = g.standard_normal(CONTENT_DIM).astype(np.float32)
        v /= (np.linalg.norm(v) + 1e-9)
        _CONTENT[s] = v
    return v


def fhrr_score(cue: torch.Tensor, token: torch.Tensor) -> float:
    """FHRR cleanup inner product Re(<conj(cue), token>)/D ~ number of shared bound (role,filler) terms."""
    return float(torch.real(torch.sum(torch.conj(cue) * token))) / D


def event_token(attrs: Dict[str, str]) -> torch.Tensor:
    """ONE bound event token = raw FHRR superposition of bind(ROLE, filler) over present attributes.
    Raw sum (not per-component renorm) so <cue,token>/D reads as an integer match count -- glass-box."""
    terms = [binding.bind(sym(r), sym("%s=%s" % (r, f))) for r, f in attrs.items() if f and f != "?"]
    if not terms:
        return torch.zeros(D, dtype=torch.complex64)
    return torch.stack(terms, dim=0).sum(dim=0)


def cue_token(probe: Dict[str, str]) -> torch.Tensor:
    """Partial-mention cue = superposition of the probed (role,filler) bindings (same codec as the token)."""
    return event_token(probe)


def _norm_event(agent, patient, pred, tense) -> Dict[str, str]:
    """Normalize a reader EventRecord's four positional roles into the {ROLE: filler} the codec binds
    (lowercase/strip, drop the '?' placeholder) -- VERBATIM the cell's Passage._norm mapping."""
    raw = {"AGENT": agent, "PATIENT": patient, "PRED": pred, "TENSE": tense}
    out: Dict[str, str] = {}
    for r in ROLES:
        v = raw.get(r)
        if v is None:
            continue
        v = str(v).strip().lower()
        if v and v != "?":
            out[r] = v
    return out


def _c2r(z: torch.Tensor) -> np.ndarray:
    """Complex FHRR vector -> real 2D vector concat(real, imag); preserves the FHRR inner product exactly."""
    return np.concatenate([z.real.numpy(), z.imag.numpy()]).astype(np.float32)


# ===========================================================================
# The episodic store over one passage's bound event tokens.
# ===========================================================================
class BoundEpisodicStore:
    """The tiered episodic store the reader hangs on `sm.episodic_store` when `bind_event_tokens` is on.

    Holds the passage's bound event tokens (BIND), the N400 segment boundaries (CHUNK), and a DG-sparse +
    CA3 episodic store (STORE). Coreference `resolve`/`corefer` use the DIRECT bound-token cleanup route
    (the validated route that completes at 1.00); the DG/CA3 store is the consolidation tier + inspection
    handle, NOT the coref query path (its DG-at-retrieval CA3 path is a known low-fidelity follow-on).
    """

    def __init__(self, tokens: List[torch.Tensor], attrs: List[Dict[str, str]],
                 segment_sizes: Optional[List[int]] = None,
                 encoder: Optional[HippocampalEncoder] = None,
                 stored_dg_codes: Optional[np.ndarray] = None):
        self.tokens = tokens                 # list[complex64]  one raw FHRR bound token per kept event
        self.attrs = attrs                   # list[dict]       the normalized {ROLE: filler} that built each
        self.segment_sizes = segment_sizes or []   # N400 CHUNK-tier segment lengths (Cowan-small)
        self._encoder = encoder              # hdlab.hippocampal_encoder.HippocampalEncoder (STORE tier)
        self._stored_dg_codes = stored_dg_codes

    def __len__(self) -> int:
        return len(self.tokens)

    def resolve(self, query_attrs: Dict[str, str]) -> Tuple[int, float]:
        """Direct EC->CA3 similarity route: return (best_event_index, best_score) for a partial mention.
        Score = FHRR cleanup inner product ~ number of shared bound (role,filler) terms. Returns (-1, 0.0)
        when the store is empty."""
        cue = cue_token({r: v for r, v in query_attrs.items() if v and v != "?"})
        if not self.tokens:
            return (-1, 0.0)
        scores = [fhrr_score(cue, t) for t in self.tokens]
        bi = int(np.argmax(scores))
        return (bi, float(scores[bi]))

    def corefer(self, query_attrs: Dict[str, str], thresh: float = JOINT_THRESH) -> bool:
        """JOINT coref decision: does SOME stored event token match the probed attributes? (needs the
        JOINT -- BOTH probed attributes bound to ONE event; the validated joint_decide readout)."""
        _, best = self.resolve(query_attrs)
        return bool(best >= thresh)


# ===========================================================================
# The assembler.
# ===========================================================================
class BoundEventBackbone:
    """Thin assembler (COMPOSES existing organs only; no new mechanism). Promotion target of
    experiments/exp_tiered_bound_event_token_coref_v1.py. `build(events, locations)` returns
    (event_tokens, BoundEpisodicStore)."""

    def __init__(self, d: int = D, build_episodic: bool = True):
        # d is fixed at the promoted FHRR dim; a different d would break byte-equality with the validated
        # cell (and any fitted asset that assumes D). Guard rather than silently diverge.
        if int(d) != D:
            raise ValueError("BoundEventBackbone d must be %d (the validated FHRR dim); got %d" % (D, int(d)))
        self.build_episodic = bool(build_episodic)

    def _content_stream(self, attrs: List[Dict[str, str]]) -> List[np.ndarray]:
        """Per-event CONTENT vector for the N400 segmenter -- VERBATIM the cell's Passage.content_stream."""
        out = []
        for e in attrs:
            parts = [content_vec("%s:%s" % (r, e[r])) for r in ("PRED", "AGENT", "PATIENT") if e.get(r)]
            v = np.sum(parts, axis=0) if parts else np.zeros(CONTENT_DIM, dtype=np.float32)
            out.append(v / (np.linalg.norm(v) + 1e-9))
        return out

    def _segment(self, attrs: List[Dict[str, str]]) -> List[int]:
        """CHUNK tier: N400 prediction-error segmentation of the event content stream (Cowan-small
        segments) -- VERBATIM the cell's segmentation logic."""
        cs = self._content_stream(attrs)
        if len(cs) < 3:
            return [len(cs)] if cs else []
        mon = N400CoherenceMonitor()
        sizes: List[int] = []
        cur = 0
        for v in cs:
            ev = mon.observe(v)
            if ev.is_boundary:
                sizes.append(cur)
                cur = 1
            else:
                cur += 1
        sizes.append(cur)
        return sizes

    def build(self, events, locations=None) -> Tuple[List[torch.Tensor], BoundEpisodicStore]:
        """Assemble the tiered bound-event-token backbone for one passage.

        events    : an iterable of reader EventRecord (uses .agent/.patient/.predicate/.tense).
        locations : sm.locations (a LocationRegister) -- RESERVED. The VALIDATED backbone binds the four
                    roles {AGENT,PATIENT,PRED,TENSE}; binding PLACE into the token is a mapped follow-on
                    (it would diverge from the validated result), so `locations` is accepted for the
                    documented wire signature but NOT bound in yet. Kept explicit rather than hidden.
        """
        # normalize + keep only events with a bindable conjunction (>=2 filled roles), matching the cell.
        attrs: List[Dict[str, str]] = []
        for e in events:
            a = _norm_event(getattr(e, "agent", None), getattr(e, "patient", None),
                            getattr(e, "predicate", None), getattr(e, "tense", None))
            if sum(1 for r in ROLES if a.get(r)) >= 2:
                attrs.append(a)
        tokens = [event_token(a) for a in attrs]              # BIND: the one bound token per event
        segment_sizes = self._segment(attrs)                  # CHUNK: N400 prediction-error boundaries
        encoder = None
        stored = None
        if self.build_episodic and tokens:                    # STORE: DG-sparse + CA3 episodic consolidation
            encoder = HippocampalEncoder(input_dim=2 * D, dg_dim=_DG_DIM, sparsity=_DG_SPARSITY, seed=_DG_SEED)
            real_toks = np.stack([_c2r(t) for t in tokens], axis=0)
            encoder.encode_and_write(real_toks)
            stored = encoder._stored_dg_codes
        store = BoundEpisodicStore(tokens, attrs, segment_sizes, encoder, stored)
        return tokens, store
