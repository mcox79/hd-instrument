import json, re, collections, os, sys

recs = [json.loads(l) for l in open('data/_phase_diag_scan_out.jsonl', encoding='utf-8')]
print('candidates', len(recs))

# how many are terminal/failed artifacts?
bad_verdict = re.compile(r'(?i)IMPORT_CRASH|CRASH|OOM|SELFTEST|UNKNOWN|ERROR|TIMEOUT|KILLED|ABORT')
by_mode = collections.Counter(r['run_mode'] or '(none)' for r in recs)
print('run_mode:', by_mode.most_common())

param_counts = collections.Counter()
param_full_counts = collections.Counter()
for r in recs:
    for k in r['swept']:
        param_counts[k] += 1
        if r['run_mode'] == 'full':
            param_full_counts[k] += 1
print('\nparam appearing multi-valued in N artifacts (any mode):')
for k, v in param_counts.most_common():
    print('  %-12s %5d   full-mode %5d' % (k, v, param_full_counts[k]))

# path dedupe: strip _smoke/_selftest/_seed_N suffix to get a "cell family"
def fam(p):
    b = p.split('/')[-2]
    b = re.sub(r'_(smoke|selftest|memsmoke|smoketest|SMOKE|FULL|local|local_test)$', '', b)
    b = re.sub(r'_seed_\d+.*$', '', b)
    return b

fams = collections.defaultdict(list)
for r in recs:
    fams[fam(r['path'])].append(r)
print('\ndistinct cell families among candidates:', len(fams))

# families with a FULL-mode member and a real (non-terminal) verdict
good = []
for f, rs in sorted(fams.items()):
    fulls = [r for r in rs if r['run_mode'] == 'full' and not bad_verdict.search(r['verdict'] or 'UNKNOWN')]
    if fulls:
        good.append((f, fulls))
print('families with >=1 FULL non-terminal artifact:', len(good))

with open('data/_phase_diag_families.txt', 'w', encoding='utf-8') as fh:
    for f, fulls in good:
        sw = {}
        for r in fulls:
            for k, v in r['swept'].items():
                sw.setdefault(k, set()).update(v)
        fh.write('%s | n_full=%d | %s\n' % (f, len(fulls), json.dumps({k: sorted(v) for k, v in sw.items()})[:400]))
        fh.write('    path=%s verdict=%s ci=%s floor=%s\n' % (fulls[0]['path'], fulls[0]['verdict'][:70], fulls[0]['has_ci_tokens'], fulls[0]['has_floor_tokens']))
print('wrote data/_phase_diag_families.txt')
