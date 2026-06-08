import sys
import json
sys.path.insert(0, 'd:/AI/hd-instrument')
from tools.orchestrator.remote_state import get_metrics, is_stale

print('stale:', is_stale())
anchors = [
    'n2_pathA_betterprompt_gpu_v1',
    'substrate_kg_khop_gpu_scale_v1',
    'sharding_scaling_largeS_gpu_v1',
    'kgqa_discrete_vs_fuzzy_gpu_scale_v1',
    'sharding_contrast_demo_data_cpu_v1',
    'n1d_parallel_subq_native_cpu_v1',
]
for a in anchors:
    m = get_metrics(a)
    print(f'=== {a} ===')
    if m is None:
        print('  NONE')
    else:
        print(f'  _source: {m.get("_source")}')
        print(f'  verdict: {m.get("verdict")}')
        print(f'  verdict_msg: {m.get("verdict_msg")}')
        for k in ['cells', 'per_cell', 'cell_results', 'results', 'metrics']:
            if k in m:
                print(f'  [{k}]: {json.dumps(m[k])[:800]}')
        skip = {'_source','verdict','verdict_msg','cells','per_cell','cell_results','results','metrics','summary','elapsed_s'}
        for k, v in m.items():
            if k not in skip and not k.startswith('_'):
                print(f'  {k}: {v}')
