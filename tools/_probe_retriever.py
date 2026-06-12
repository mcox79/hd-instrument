import sys
sys.path.insert(0, '.')
from pathlib import Path
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.encode import AtomEncoder
from backend.substrate_index.retrieve import Retriever
p = PartitionedStore(Path('data/substrate_index'))
e = AtomEncoder()
r = Retriever(p, e)
r.rebuild_index()
for q in ['FHRR binding', 'reinforcement learning', 'theta-gamma binding']:
    cands = r.semantic(q, top_k=5)
    print(f'\nQ: {q}')
    for c in cands:
        print(f'  atom_id={c.atom_id!r}  score={c.score:.3f}')
