"""hdlab/gather_reason.py -- promoted GATHER + REASON mechanism (state-of-mind-conditioned
CA3 relevance gather + K<=2 fan-out reasoning), 2026-08-11.

Promotion of the decisive minimal prototype validated end-to-end in
experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py (commits 589ee680d /
7a6afdab8; FULL landed verdict HARD_PASS_state_of_mind_gather_load_bearing, N=121 real gap
targets, arm3@5=0.3802 vs arm1@5(blind-union)=0.0413 vs arm2@5(voting)=0.0248, delta=0.339 >=
0.20, scramble-collapse + ablation controls clean -- data/exp_state_of_mind_relevance_gather_
reasoning_union_v1/metrics.json) into a reusable hdlab module (WIRE-don't-island), so the
mechanism composes into the full three-tier knowledge loop (hdlab/three_tier_loop.py) instead
of living only inside that one experiment cell.

WHAT THIS IS (per notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md
"(B) CONCRETE BUILD SPEC", steps [1]-[2]):
  RELEVANCE GATHER (ca3_relevance_gather): a CA3/DG-style peel-loop (matching-pursuit
  deflation) over hdlab.cleanup_family.iterative_attractor against a codebook of candidate
  items, cued by a query vector (typically decoded from a
  hdlab.situation_model_accumulate.RelationRegister / AccumulateRegister "state of mind"
  register) -- pulls the RELEVANT neighborhood instead of a blind full scan.
  REASON (fanout_two_hop): a K<=2 fan-out + max-aggregate composition over
  hdlab.kg_traversal.KGStore.predict_one_hop_topk (the CERT-585 certified single-hop
  primitive), OPTIONALLY restricted at hop-1 to a caller-supplied candidate-index set -- this
  is how the GATHER stage's output narrows the REASON stage's search space. Restriction=None
  reproduces the source cell's arm1 BLIND UNION fan-out; a restriction set reproduces arm3's
  STATE-OF-MIND CUED fan-out.

PROMOTION, not a redesign: ca3_relevance_gather is a direct generalization of the source
cell's ca3_gather (identical peel-loop body; the caller now supplies the query vector
directly instead of this module reaching into a RelationRegister itself, decoupling GATHER
from STATE-OF-MIND per the design audit's own stage boundaries -- state-of-mind maintenance
stays owned by hdlab.situation_model_accumulate, not duplicated here). fanout_two_hop is a
direct generalization of the source cell's TWO separate call sites that both did K=2
fan-out + max-aggregate over predict_one_hop_topk -- fanout_query (arm0/arm1/arm2's shared
helper, unrestricted) AND the hand-inlined arm3 restricted variant (run_pipeline lines
~547-566, which filtered idx1 against gathered_idx inline instead of calling fanout_query) --
into ONE function via an optional restrict_hop1_to set. That inline duplication is now gone;
BEHAVIOR-PRESERVATION below proves both code paths are unaffected.

BEHAVIOR-PRESERVATION: verification/test_gather_reason.py reproduces the source cell's own
run_self_test() fixture byte-for-byte through this module's generalized API and asserts
identical outputs (ca3 gather -> ['material0'], restricted fan-out -> gold at top-1), plus an
additional direct check that restrict_hop1_to is load-bearing (a distractor material that
would otherwise out-rank the gold whole is excluded once restricted). The source cell file
itself is UNTOUCHED (a parallel extraction, not a refactor-in-place) -- its own landed FULL
verdict and metrics.json are unaffected by this promotion.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim):
  hdlab.cleanup_family.iterative_attractor          (CA3/DG peel-loop primitive)
  hdlab.kg_traversal.KGStore.predict_one_hop_topk    (CERT-585 single-hop primitive)

ASCII-only. Deterministic (all randomness lives in caller-supplied torch.Generator / the
codebook the caller builds; this module itself draws no randomness -- no built-in hash(), no
list(set()) ordering -- PROT-023/F.5 compliant).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch

from hdlab import cleanup_family
from hdlab.kg_traversal import KGStore


def real_to_concat(v: torch.Tensor) -> np.ndarray:
    """FHRR complex64 -> real-valued concat(Re,Im); preserves the exact cleanup inner product
    (Re(conj(a).b) == dot(concat(Re(a),Im(a)), concat(Re(b),Im(b)))). Byte-identical to the
    source cell's real_to_concat (see module docstring BEHAVIOR-PRESERVATION)."""
    return torch.cat([v.real, v.imag]).numpy().astype(np.float32)


def build_codebook(names_to_vecs: Dict[str, torch.Tensor]) -> Tuple[List[str], np.ndarray]:
    """Deterministic (sorted-name-order) codebook build for ca3_relevance_gather, from a
    {name: FHRR complex64 vector} map. Returns (sorted_names, stacked_real_concat_codebook)
    where codebook[i] corresponds to names[i]."""
    names = sorted(names_to_vecs.keys())
    codebook = np.stack([real_to_concat(names_to_vecs[n]) for n in names], axis=0)
    return names, codebook


def ca3_relevance_gather(query_vec: np.ndarray, item_names: Sequence[str], codebook: np.ndarray,
                         k_peel: int = 25, sim_floor: float = 0.05) -> List[str]:
    """CA3-style relevance gather: peel-loop (matching-pursuit deflation) of
    hdlab.cleanup_family.iterative_attractor against `codebook`, cued by `query_vec`. Returns
    the ordered list of item_names picked before the residual norm collapses or the best
    remaining match's similarity drops below sim_floor.

    Generalizes the source cell's ca3_gather (identical peel-loop body: iterative_attractor
    call, residual deflation, sim-floor break, duplicate-index break) -- the ONLY change is
    that the caller now supplies query_vec directly (e.g. via
    real_to_concat(relation_register.decode_filler(entity, role))) instead of this function
    reaching into a RelationRegister itself, so GATHER stays decoupled from STATE-OF-MIND
    maintenance (that stays hdlab.situation_model_accumulate's job).

    item_names[i] must correspond to codebook[i] (see build_codebook)."""
    resid = query_vec.copy()
    picked: List[str] = []
    picked_idx: Set[int] = set()
    for _ in range(k_peel):
        if float(np.linalg.norm(resid)) < 1e-6:
            break
        _, diag = cleanup_family.iterative_attractor(resid, codebook)
        idx = int(diag["final_argmax_idx"])
        cb_row = codebook[idx]
        denom = float(np.linalg.norm(resid) * np.linalg.norm(cb_row) + 1e-8)
        score = float(np.dot(resid, cb_row) / denom) if denom > 0 else 0.0
        if idx in picked_idx or score < sim_floor:
            break
        picked.append(item_names[idx])
        picked_idx.add(idx)
        resid = resid - cb_row
    return picked


def fanout_two_hop(hop1_kg: KGStore, hop2_kg: KGStore, start_idx: int, hop1_rel_idx: int,
                   hop2_rel_idx: int, k1: int, k2: int, n_ent: int,
                   restrict_hop1_to: Optional[Set[int]] = None) -> List[Tuple[int, float]]:
    """K<=2 fan-out + max-aggregate composition over KGStore.predict_one_hop_topk (the
    CERT-585 certified single-hop primitive naive_chain/predict_two_hop themselves call).

    restrict_hop1_to (optional): if given, hop-1 candidates NOT in this set are discarded
    before the hop-2 lookup -- this is how a GATHER-stage result (ca3_relevance_gather's
    output, mapped to entity indices) narrows REASON's search space. None (default)
    reproduces the source cell's arm1 BLIND UNION fan-out (fanout_query) byte-for-byte; a
    restriction set reproduces arm3's STATE-OF-MIND CUED fan-out inline logic byte-for-byte
    (see module docstring BEHAVIOR-PRESERVATION).

    Returns a ranked (desc score, asc idx tie-break -- deterministic) list of
    (entity_idx, max_score) pairs."""
    k1e = min(k1, n_ent)
    idx1, sc1 = hop1_kg.predict_one_hop_topk(start_idx, hop1_rel_idx, k1e)
    agg: Dict[int, float] = {}
    k2e = min(k2, n_ent)
    for m_idx_t in idx1:
        m_idx = int(m_idx_t)
        if restrict_hop1_to is not None and m_idx not in restrict_hop1_to:
            continue
        idx2, sc2 = hop2_kg.predict_one_hop_topk(m_idx, hop2_rel_idx, k2e)
        for w_idx_t, w_sc_t in zip(idx2, sc2):
            w_idx = int(w_idx_t)
            w_sc = float(w_sc_t)
            if w_idx not in agg or w_sc > agg[w_idx]:
                agg[w_idx] = w_sc
    return sorted(agg.items(), key=lambda kv: (-kv[1], kv[0]))


def top1(ranked: List[Tuple[int, float]]) -> Optional[int]:
    """Convenience: top-ranked entity index, or None if ranked is empty."""
    return ranked[0][0] if ranked else None


def recovery_at(ranked: List[Tuple[int, float]], gold_idx: int, k: int) -> int:
    """1 iff gold_idx appears in the top-k of ranked, else 0. Byte-identical to the source
    cell's recovery_at."""
    top = [idx for idx, _ in ranked[:k]]
    return int(gold_idx in top)


def self_test() -> dict:
    """Fast off-disk gate exercising the REAL code path (real KGStore + real
    cleanup_family.iterative_attractor, not a synthetic-only branch), per exp_dev SCHEMA-VET
    F.1. Reproduces experiments/exp_state_of_mind_relevance_gather_reasoning_union_v1.py's own
    run_self_test() fixture (same entities, same planted chain, same distractor) through this
    module's generalized API, plus one additional check proving restrict_hop1_to is
    load-bearing (not decorative)."""
    from hdlab.situation_model_accumulate import RelationRegister, unit_phase_vec

    FHRR_D = 1024
    SEED_KG = 20260811
    SEED_FHRR = 20260812
    FATE_RELS = ["CREATE", "DESTROY", "MOVE"]
    BRIDGE_REL = "BRIDGE"

    processes = ["process0", "process1"]
    materials = ["material0", "material1"]
    wholes = ["whole0", "whole1", "distractor_whole"]
    ents: List[str] = []
    seen: Set[str] = set()
    for group in (sorted(processes), sorted(materials), sorted(wholes)):
        for name in group:
            if name not in seen:
                seen.add(name)
                ents.append(name)
    ent_idx = {name: i for i, name in enumerate(ents)}
    n_ent = len(ents)
    assert n_ent == 7, ents

    reading = {
        "process0": {"material0": {"DESTROY": 1}},
        "process1": {"material1": {"CREATE": 1}},
    }

    def fresh_kg(seed: int) -> KGStore:
        gen = torch.Generator().manual_seed(seed)
        return KGStore(n_ent=n_ent, n_rel=len(FATE_RELS) + 1, n_dim=2048, generator=gen)

    rel_idx = {r: i for i, r in enumerate(FATE_RELS + [BRIDGE_REL])}
    bridge_idx = rel_idx[BRIDGE_REL]

    hop1 = fresh_kg(SEED_KG)
    rows = []
    for proc in sorted(reading.keys()):
        for material, fates in sorted(reading[proc].items()):
            for fate in sorted(fates.keys()):
                rows.append((ent_idx[proc], rel_idx[fate], ent_idx[material]))
    hop1.ingest_triples(torch.tensor(rows, dtype=torch.long))

    # narrow bridge: whole0 MadeOf material0 (real chain).
    hop2_cued = fresh_kg(SEED_KG)
    hop2_cued.ingest_triples(torch.tensor([[ent_idx["material0"], bridge_idx, ent_idx["whole0"]]],
                                          dtype=torch.long))

    # (1) STATE-OF-MIND + GATHER: RelationRegister binds process0's own materials to GOAL;
    # ca3_relevance_gather over the material codebook must recover ONLY material0.
    mat_gen = torch.Generator().manual_seed(SEED_FHRR)
    mat_vecs = {m: unit_phase_vec(FHRR_D, mat_gen) for m in sorted(materials)}
    mat_names, codebook = build_codebook(mat_vecs)
    reg_gen = torch.Generator().manual_seed(SEED_FHRR + 1)
    reg = RelationRegister(d=FHRR_D, generator=reg_gen)
    for proc in processes:
        for material in reading.get(proc, {}):
            reg.bind_filler(proc, "GOAL", mat_vecs[material])
    query = real_to_concat(reg.decode_filler("process0", "GOAL"))
    gathered = ca3_relevance_gather(query, mat_names, codebook, k_peel=5)
    assert gathered == ["material0"], f"SELF_TEST FAIL: expected ['material0'], got {gathered}"

    # (2) REASON: unrestricted fan-out (arm1 BLIND UNION shape) recovers whole0 at top-1.
    ranked_blind = fanout_two_hop(hop1, hop2_cued, ent_idx["process0"], rel_idx["DESTROY"],
                                  bridge_idx, k1=5, k2=5, n_ent=n_ent, restrict_hop1_to=None)
    gold_idx = ent_idx["whole0"]
    assert ranked_blind and ranked_blind[0][0] == gold_idx, (
        f"SELF_TEST FAIL: unrestricted fan-out expected top-1={gold_idx} (whole0), got "
        f"{ranked_blind[:3]}")

    # (3) REASON: restricted fan-out (arm3 STATE-OF-MIND CUED shape) -- gathered material
    # indices narrow hop-1; still recovers whole0 at top-1 (same answer, narrower search).
    gathered_idx = {ent_idx[m] for m in gathered}
    ranked_cued = fanout_two_hop(hop1, hop2_cued, ent_idx["process0"], rel_idx["DESTROY"],
                                 bridge_idx, k1=5, k2=5, n_ent=n_ent,
                                 restrict_hop1_to=gathered_idx)
    assert ranked_cued and ranked_cued[0][0] == gold_idx, (
        f"SELF_TEST FAIL: restricted fan-out expected top-1={gold_idx} (whole0), got "
        f"{ranked_cued[:3]}")

    # (4) restrict_hop1_to is LOAD-BEARING (not decorative): plant a distractor material
    # (process1's own material1, real-bridged to distractor_whole) that is ALSO reachable from
    # process0 at hop-1 (a second, unrelated DESTROY edge process0->material1) -- unrestricted,
    # its bridge is a real (non-noise) Hebbian signal TIED with the gold whole0's own bridge
    # (both are single real triples of identical multiplicity, so both score identically:
    # MEASURED@self-test, both 4193215.5 -- an unrestricted reasoner cannot tell process0's OWN
    # material-bridge apart from process1's). Restricted to the CA3-gathered set (material0
    # only), the distractor's score collapses to the associative-matrix NOISE floor
    # (MEASURED@self-test: 4096.0 vs whole0's unchanged 4193215.5, a >1000x drop) while whole0's
    # real signal is untouched. This directly proves restrict_hop1_to changes the outcome, not
    # just narrows an already-decided ranking.
    hop1_distractor = fresh_kg(SEED_KG)
    rows2 = list(rows) + [(ent_idx["process0"], rel_idx["DESTROY"], ent_idx["material1"])]
    hop1_distractor.ingest_triples(torch.tensor(rows2, dtype=torch.long))
    hop2_distractor = fresh_kg(SEED_KG)
    hop2_distractor.ingest_triples(torch.tensor(
        [[ent_idx["material0"], bridge_idx, ent_idx["whole0"]],
         [ent_idx["material1"], bridge_idx, ent_idx["distractor_whole"]]], dtype=torch.long))
    ranked_unrestricted_with_distractor = fanout_two_hop(
        hop1_distractor, hop2_distractor, ent_idx["process0"], rel_idx["DESTROY"], bridge_idx,
        k1=5, k2=5, n_ent=n_ent, restrict_hop1_to=None)
    ranked_restricted_with_distractor = fanout_two_hop(
        hop1_distractor, hop2_distractor, ent_idx["process0"], rel_idx["DESTROY"], bridge_idx,
        k1=5, k2=5, n_ent=n_ent, restrict_hop1_to={ent_idx["material0"]})
    unrestricted_scores = dict(ranked_unrestricted_with_distractor)
    restricted_scores = dict(ranked_restricted_with_distractor)
    gold_score_unrestricted = unrestricted_scores[gold_idx]
    distractor_score_unrestricted = unrestricted_scores[ent_idx["distractor_whole"]]
    assert distractor_score_unrestricted >= 0.9 * gold_score_unrestricted, (
        "test construction failed: unrestricted, the distractor's bridge must be a comparable "
        f"real signal to the gold's (not already noise), got distractor={distractor_score_unrestricted} "
        f"gold={gold_score_unrestricted}")
    gold_score_restricted = restricted_scores[gold_idx]
    distractor_score_restricted = restricted_scores.get(ent_idx["distractor_whole"], 0.0)
    assert distractor_score_restricted <= 0.01 * gold_score_restricted, (
        "META_RULE_AF-style load-bearing check FAILED: restrict_hop1_to did not suppress the "
        f"distractor's bridge to noise level, got distractor={distractor_score_restricted} "
        f"gold={gold_score_restricted}")
    assert ranked_restricted_with_distractor and ranked_restricted_with_distractor[0][0] == gold_idx, (
        f"restricted fan-out with distractor present must still recover whole0 at top-1, got "
        f"{ranked_restricted_with_distractor[:3]}")

    return {
        "n_ent": n_ent, "ca3_gathered": gathered,
        "blind_top1_idx": ranked_blind[0][0], "cued_top1_idx": ranked_cued[0][0],
        "gold_idx": gold_idx, "restrict_hop1_to_load_bearing": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
    print("ALL SELF-TESTS PASSED")
