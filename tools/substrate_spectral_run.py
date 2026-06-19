"""Run Layer 2 spectral observability on the current substrate codebook."""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.spectral import spectral_observability

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")
log = logging.getLogger("spectral_run")

DATA_ROOT = Path("data/substrate_index")


def main():
    pstore = PartitionedStore(DATA_ROOT)
    encoder = AtomEncoder()
    atoms = pstore.all_atoms()
    log.info("encoding %d atoms...", len(atoms))
    av_dict = encoder.encode_atoms(atoms)

    semantic_mat = np.stack([av_dict[a.id].semantic for a in atoms])

    log.info("computing spectral observability on semantic codebook...")
    sem_obs = spectral_observability(semantic_mat)

    print("\n=== Layer 2 spectral observability: SEMANTIC codebook ===")
    print(json.dumps(sem_obs.to_dict(), indent=2))

    # Algebra HRR codebook (only atoms with algebra_hrr)
    from backend.substrate_index.algebra_index import AlgebraIndex
    aidx = AlgebraIndex(dim=1024)
    aidx.build(pstore)
    algebra_atom_ids = []
    algebra_rows = []
    for aid, av in aidx._atom_vectors.items():
        if av.algebra_hrr is not None:
            algebra_atom_ids.append(aid)
            algebra_rows.append(av.algebra_hrr)
    if algebra_rows:
        algebra_mat = np.stack(algebra_rows)
        alg_obs = spectral_observability(algebra_mat)
        print("\n=== Layer 2 spectral observability: ALGEBRA-HRR codebook ===")
        print(json.dumps(alg_obs.to_dict(), indent=2))

    out = DATA_ROOT / "bench_reports" / f"spectral_observability_{int(time.time())}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "semantic_codebook": sem_obs.to_dict(),
        "algebra_hrr_codebook": alg_obs.to_dict() if algebra_rows else None,
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log.info("wrote spectral report -> %s", out)


if __name__ == "__main__":
    main()
