"""Phase-diagram recovery scanner.

SHAPE-based, not keyword-based: for every metrics.json under data/, find files in which
a substrate free parameter takes MORE THAN ONE VALUE inside the SAME artifact.
That is the definition of a sweep, and it is independent of the verdict vocabulary
(which has drifted 13 -> 444 distinct strings).
"""
import os, re, json, sys, io

ROOT = 'data'
LIST = 'data/_phase_diag_metrics_list.txt'
OUT = 'data/_phase_diag_scan_out.jsonl'

# Each rule: (param_name, compiled regex, group index yielding the VALUE)
RULES = [
    # dimensionality: d256 / d_1024 / dim=8192 / D=2048 / "d = 512"
    ('dim', re.compile(r'(?<![a-zA-Z0-9])[dD](?:im|IM|imension)?\s*[_=:]?\s*(256|512|1024|2048|4096|8192|16384|10000|128|64)(?![0-9])'), 1),
    # code format
    ('format', re.compile(r'(?i)(?<![a-z])(bipolar|sign\(\)|signed|graded|quant(?:ised|ized)?|QUANT|GRAD|real[_-]?valued|phasor|complex|fhrr|ternary|int8|binary|float32|fp16|dense_real)(?![a-z])'), 1),
    # binding operator
    ('bind', re.compile(r'(?i)(?<![a-z])(hadamard|elementwise_mult|circ(?:ular)?[_-]?conv\w*|hrr|fhrr|vtb|mbat|cyclic[_-]?shift|permut\w*|phase[_-]?rot\w*|xor|map[_-]?b|bsc|tensor[_-]?prod\w*)(?![a-z])'), 1),
    # write sparsity / read sparsity / generic sparsity as a numeric
    ('a_write', re.compile(r'(?i)a[_-]?write\s*[_=:]?\s*([0-9]*\.?[0-9]+)'), 1),
    ('a_read', re.compile(r'(?i)a[_-]?read\s*[_=:]?\s*([0-9]*\.?[0-9]+)'), 1),
    ('sparsity', re.compile(r'(?i)(?:sparsity|active_frac\w*|density|occupancy|\bf)\s*[_=:]\s*(0?\.[0-9]+|[0-9]+(?:\.[0-9]+)?%)'), 1),
    ('topk', re.compile(r'(?i)(?:top[_-]?k|k_active|n_active|kwta)\s*[_=:]?\s*([0-9]+)'), 1),
    ('expansion', re.compile(r'(?i)(?:expansion|expand)[_-]?(?:factor|ratio)?\s*[_=:]?\s*([0-9]+(?:\.[0-9]+)?)'), 1),
    ('bundle', re.compile(r'(?i)(?<![a-z])(majority[_-]?sum|bundl\w*|superpos\w*|normalized[_-]?sum|cleanup|resonator|iterative[_-]?cleanup)(?![a-z])'), 1),
    ('seeds', re.compile(r'(?i)seed\s*[_=:]?\s*([0-9]+)'), 1),
]

RUNMODE = re.compile(r'"run_mode"\s*:\s*"([^"]*)"')
ANCHOR = re.compile(r'"anchor_name"\s*:\s*"([^"]*)"')
VERDICT = re.compile(r'"verdict"\s*:\s*"([^"]*)"')
PREREG = re.compile(r'"prereg"\s*:\s*"([^"]*)"')
NITEMS = re.compile(r'"n_items"\s*:\s*([0-9]+)')
CI = re.compile(r'(?i)ci_lo|ci_hi|"ci"|CI\[|half[_-]?width|bootstrap')
FLOOR = re.compile(r'(?i)floor|scramble|scrambled|chance|null_p95|baseline')
SMOKE = re.compile(r'(?i)smoke')

paths = [l.strip() for l in open(LIST, encoding='utf-8') if l.strip()]
out = open(OUT, 'w', encoding='utf-8')
n_read = 0
n_err = 0
n_cand = 0
for p in paths:
    try:
        with open(p, 'r', encoding='utf-8', errors='replace') as fh:
            txt = fh.read(2_000_000)
    except Exception:
        n_err += 1
        continue
    n_read += 1
    found = {}
    for name, rx, gi in RULES:
        vals = set()
        for m in rx.finditer(txt):
            vals.add(m.group(gi).lower())
        if len(vals) >= 2:
            found[name] = sorted(vals)
    if not found:
        continue
    # drop files whose ONLY multi-value param is 'seeds' (a replication, not a sweep)
    if set(found) <= {'seeds'}:
        continue
    n_cand += 1
    rec = {
        'path': p.replace('\\', '/'),
        'anchor': (ANCHOR.search(txt).group(1) if ANCHOR.search(txt) else ''),
        'run_mode': (RUNMODE.search(txt).group(1) if RUNMODE.search(txt) else ''),
        'verdict': (VERDICT.search(txt).group(1) if VERDICT.search(txt) else '')[:120],
        'prereg': (PREREG.search(txt).group(1) if PREREG.search(txt) else ''),
        'n_items': (int(NITEMS.search(txt).group(1)) if NITEMS.search(txt) else None),
        'bytes': len(txt),
        'has_ci_tokens': bool(CI.search(txt)),
        'has_floor_tokens': bool(FLOOR.search(txt)),
        'mentions_smoke': bool(SMOKE.search(txt)),
        'swept': found,
    }
    out.write(json.dumps(rec) + '\n')
out.close()
print('read', n_read, 'err', n_err, 'candidates', n_cand)
