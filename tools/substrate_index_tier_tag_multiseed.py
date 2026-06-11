"""Multi-seed validation of tier_tag Q5 win from FINDINGS_05.

Per FINDINGS_05 commitment: 'If Q5 win is random, drop tier_tag too.'
Per Research endorsement: drop corpus_tag; keep tier_tag with multi-seed
re-roll caveat pending.

Tests: re-roll tier_tag generation with 5 different seeds; check whether
Q5 still surfaces circular_convolution as top result with tier_tag at 0.3.

If 5/5 seeds: tier_tag genuinely contributes signal on Q5 (drill?)
If 0-2/5 seeds: tier_tag Q5 win was coincidence; drop tier_tag too
If 3-4/5 seeds: marginal; flag pending bigger corpus
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.schema import Tier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("tier_multiseed")

DATA_ROOT = Path("data/substrate_index")
BATCH02_QUERIES_PATH = DATA_ROOT / "math_corpus_batch02_disclosed_queries.json"


def tier_vector_with_seed(label: str, dim: int, seed_extra: int) -> np.ndarray:
    h = int(hashlib.sha256(f"substrate_index_tag::{label}".encode()).hexdigest(), 16)
    rng = np.random.default_rng((h % (2**63 - 1)) ^ (20260611_001 + seed_extra))
    v = rng.standard_normal(dim).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def main():
    pstore = PartitionedStore(DATA_ROOT)
    log.info("loading encoder...")
    encoder = AtomEncoder()
    atoms = pstore.all_atoms()
    log.info("encoding %d atoms (batched bge)", len(atoms))
    av_dict = encoder.encode_atoms(atoms)

    semantic_mat = np.stack([av_dict[a.id].semantic for a in atoms])
    atom_ids = [a.qualified_id for a in atoms]
    atom_tiers = [a.tier for a in atoms]

    with BATCH02_QUERIES_PATH.open("r", encoding="utf-8") as f:
        queries_raw = json.load(f)
    if isinstance(queries_raw, dict):
        queries_raw = queries_raw.get("queries", []) or queries_raw.get("disclosed_queries", [])

    Q5_TEXT = None
    for q_rec in queries_raw:
        qid = q_rec.get("qid", q_rec.get("id", ""))
        if qid == "Q5":
            Q5_TEXT = q_rec.get("query_text") or q_rec.get("text") or q_rec.get("question")
            break
    if not Q5_TEXT:
        log.error("Q5 not found in disclosed queries")
        return

    log.info("Q5 text: %s", Q5_TEXT[:120])
    q5_vec = encoder.encode_query_text(Q5_TEXT)

    # Baseline: semantic-only
    sims_sem = semantic_mat @ q5_vec
    top_sem = atom_ids[int(np.argmax(sims_sem))]
    log.info("baseline (semantic-only) Q5 top: %s", top_sem.split("::")[-1])

    # Each seed: build tier_tag vectors with a different seed offset
    SEEDS = [0, 1, 2, 3, 4]  # original (0) + 4 alternates
    results = []
    for seed_extra in SEEDS:
        tier_tags = {t: tier_vector_with_seed(f"tier::{t.value}", 1024, seed_extra) for t in Tier}
        # Build composite = semantic + 0.3 * tier_tag, L2-normalized
        composite_mat = np.zeros_like(semantic_mat)
        for i, t in enumerate(atom_tiers):
            v = semantic_mat[i] + 0.3 * tier_tags[t]
            composite_mat[i] = v / (np.linalg.norm(v) + 1e-12)
        sims = composite_mat @ q5_vec
        top_5 = [atom_ids[i] for i in np.argsort(-sims)[:5]]
        top_1 = top_5[0]
        # Is the top result circular_convolution (the expected FFT-dual)?
        is_circ_conv_top = top_1.endswith("circular_convolution")
        results.append({
            "seed_extra": seed_extra,
            "top_1": top_1.split("::")[-1],
            "top_5": [t.split("::")[-1] for t in top_5],
            "circular_conv_top1": is_circ_conv_top,
        })

    # Report
    print(f"\n{'='*80}")
    print("Multi-seed tier_tag Q5 validation")
    print(f"{'='*80}\n")
    print(f"Q5: {Q5_TEXT}\n")
    print(f"Baseline (semantic-only) top: {top_sem.split('::')[-1]}")
    print(f"\nSeed sweep with tier_tag at 0.3 (each row = different seed re-roll):\n")
    print(f"  {'seed':>5s}  {'top-1':<30s}  circular_conv@1?")
    print(f"  {'-'*5}  {'-'*30}  {'-'*20}")
    circular_conv_count = 0
    for r in results:
        flag = "YES" if r["circular_conv_top1"] else "no"
        if r["circular_conv_top1"]:
            circular_conv_count += 1
        print(f"  {r['seed_extra']:5d}  {r['top_1']:<30s}  {flag}")

    print(f"\ncircular_conv top-1 across seeds: {circular_conv_count}/{len(SEEDS)}")
    if circular_conv_count >= 4:
        print(f"\nVERDICT: tier_tag GENUINELY contributes on Q5 ({circular_conv_count}/5 seeds)")
    elif circular_conv_count >= 2:
        print(f"\nVERDICT: tier_tag MARGINAL on Q5 ({circular_conv_count}/5 seeds)")
    else:
        print(f"\nVERDICT: Q5 win was COINCIDENCE ({circular_conv_count}/5 seeds) -- recommend drop tier_tag")

    out = DATA_ROOT / "bench_reports" / f"tier_multiseed_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "baseline_top": top_sem,
        "seed_results": results,
        "circular_conv_top1_count": circular_conv_count,
        "total_seeds": len(SEEDS),
    }, indent=2), encoding="utf-8")
    log.info("wrote report -> %s", out)


if __name__ == "__main__":
    main()
