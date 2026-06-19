"""DECISION 110a: extract STRICT-eligible audit candidates from FROZEN corpus.

Per DECISION 112a ruling: sample from FROZEN Phase 4e batch 1+2 + 83a + 103c
STRICT corpus ONLY; extend to Phase 4a 100-signature strict-eligible
(relation-direction per 101 ruling) if N<50.

Output: data/audit/110a_audit_candidates.json  (sources only; NO vet labels;
NO authoring rationale)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def extract_batch2_strict():
    """17 STRICT edges from Phase 4e batch 2 grounding (DECISION 103c)."""
    edges = []
    src_file = Path('data/substrate_index/skunkworks_phase4e_batch2_grounding_new_STRICT_edges.jsonl')
    with open(src_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            edges.append({
                'src': e['src'],
                'tgt': e['tgt'],
                'rel': e['rel_type'],
                'source': 'phase4e_batch2_grounding',
            })
    return edges


def extract_83a_strict():
    """8 STRICT W-TYPE-SIG edges from DECISION 83a."""
    edges = []
    src_file = Path('data/substrate_index/skunkworks_wtypesig_new_edges_v1.jsonl')
    with open(src_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            edges.append({
                'src': e['src'],
                'tgt': e['tgt'],
                'rel': e['rel_type'],
                'source': '83a_w_type_sig',
            })
    return edges


def extract_batch1_strict():
    """Strict-eligible from Phase 4e batch 1 signature pointers (DECISION 98a)."""
    edges = []
    src_file = Path('data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_1.jsonl')
    with open(src_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            atom = e['atom']
            # SPECIALIZES per 101 relation-direction ruling
            if 'specializes' in e:
                edges.append({
                    'src': atom, 'rel': 'SPECIALIZES', 'tgt': e['specializes'],
                    'source': 'phase4e_batch1_signature_specializes',
                })
            # Pointer relations from algebraic_properties
            for prop in e.get('algebraic_properties', []):
                if ':' in prop:
                    key, tgt = prop.split(':', 1)
                    k = key.strip().lower()
                    if k == 'uses':
                        edges.append({
                            'src': atom, 'rel': 'USES', 'tgt': tgt.strip(),
                            'source': 'phase4e_batch1_signature_uses',
                        })
                    elif k == 'instance_of':
                        edges.append({
                            'src': atom, 'rel': 'INSTANCE_OF', 'tgt': tgt.strip(),
                            'source': 'phase4e_batch1_signature_instance_of',
                        })
    return edges


def extract_phase4a_strict():
    """Strict-eligible from Phase 4a 100-signature corpus (excludes Phase 4e 1+2 entries)."""
    edges = []
    src_file = Path('data/substrate_index/skunkworks_self_model_of_operators_v1.jsonl')
    if not src_file.exists():
        return edges
    phase4e_atoms = set()
    # Compute phase 4e atoms to exclude
    for f in [
        'data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_1.jsonl',
        'data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_2.jsonl',
    ]:
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                phase4e_atoms.add(json.loads(line)['atom'])

    with open(src_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            atom = e['atom']
            if atom in phase4e_atoms:
                continue
            # SPECIALIZES per 101 ruling
            if 'specializes' in e and isinstance(e['specializes'], str):
                edges.append({
                    'src': atom, 'rel': 'SPECIALIZES', 'tgt': e['specializes'],
                    'source': 'phase4a_signature_specializes',
                })
            for prop in e.get('algebraic_properties', []):
                if isinstance(prop, str) and ':' in prop:
                    key, tgt = prop.split(':', 1)
                    k = key.strip().lower()
                    if k == 'uses':
                        edges.append({
                            'src': atom, 'rel': 'USES', 'tgt': tgt.strip(),
                            'source': 'phase4a_signature_uses',
                        })
                    elif k == 'instance_of':
                        edges.append({
                            'src': atom, 'rel': 'INSTANCE_OF', 'tgt': tgt.strip(),
                            'source': 'phase4a_signature_instance_of',
                        })
    return edges


def main():
    all_edges = []
    sources = [
        ('phase4e_batch2', extract_batch2_strict()),
        ('83a_w_type_sig', extract_83a_strict()),
        ('phase4e_batch1', extract_batch1_strict()),
        ('phase4a', extract_phase4a_strict()),
    ]
    for name, edges in sources:
        print(f'{name}: {len(edges)} strict-eligible edges')
        all_edges.extend(edges)

    print(f'\ntotal: {len(all_edges)}')

    # Dedupe by (src, rel, tgt)
    seen = set()
    deduped = []
    for e in all_edges:
        key = (e['src'], e['rel'], e['tgt'])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(e)
    print(f'deduped: {len(deduped)}')

    # Random sample (deterministic for reproducibility)
    import random
    random.seed(42)
    N = min(50, len(deduped))
    sample = random.sample(deduped, N)
    print(f'sample size: {N}')

    out_dir = Path('data/audit')
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / '110a_audit_candidates.json', 'w') as f:
        json.dump({
            'description': 'DECISION 110a authoring-blind audit candidates per DECISION 112a ruling',
            'frozen_corpus_sources': ['phase4e_batch2', '83a_w_type_sig', 'phase4e_batch1', 'phase4a'],
            'random_seed': 42,
            'N': N,
            'total_pool': len(deduped),
            'sample': sample,
        }, f, indent=2)
    print(f'wrote {out_dir / "110a_audit_candidates.json"}')


if __name__ == '__main__':
    main()
