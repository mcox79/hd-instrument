"""Tighter SHAPE test: an explicit SWEEP LIST field.

A sweep leaves a literal list of >=2 values under a key whose NAME names a parameter.
This is stricter than the prose-token scan and is independent of verdict vocabulary.
"""
import os, json, re, collections

paths = [l.strip() for l in open('data/_phase_diag_metrics_list.txt', encoding='utf-8') if l.strip()]

PARAMKEY = re.compile(r'(?i)(n_?dim|dims?|d_lift|ctx_?d|expand|expansion|sparsit|frac|a_?write|a_?read|density|active|topk|top_?k|kwta|encoder|binding|bind_?op|operator|format|code|bundl|cleanup|superpos)')
SWEEPY = re.compile(r'(?i)(sweep|_list|s$|grid|values|range|fracs|buckets|levels)')

hits = collections.defaultdict(list)
n = 0
for p in paths:
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        continue
    n += 1

    def walk(o, prefix=''):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, list) and len(v) >= 2 and all(isinstance(x, (int, float, str)) for x in v):
                    if PARAMKEY.search(k) and len(set(map(str, v))) >= 2:
                        hits[k].append((p.replace('\\', '/'), [str(x)[:20] for x in v[:10]]))
                elif isinstance(v, (dict, list)) and len(prefix) < 40:
                    walk(v, prefix + '/' + str(k))
        elif isinstance(o, list):
            for x in o[:50]:
                if isinstance(x, (dict, list)):
                    walk(x, prefix)
    walk(d)

print('parsed', n, 'of', len(paths))
print('distinct sweep-list KEY NAMES found:', len(hits))
for k in sorted(hits, key=lambda k: -len(hits[k])):
    ps = sorted(set(x[0] for x in hits[k]))
    vals = sorted(set(tuple(x[1]) for x in hits[k]))
    print('\n%-28s in %4d artifacts' % (k, len(ps)))
    for v in vals[:6]:
        print('     values %s' % (list(v),))
    for pp in ps[:6]:
        print('     %s' % pp)
