import re, json
paths = [l.strip().replace('\\', '/') for l in open('data/_phase_diag_metrics_list.txt', encoding='utf-8') if l.strip()]
n = 0
for p in paths:
    try:
        t = open(p, encoding='utf-8', errors='replace').read(800000)
    except Exception:
        continue
    if 'K_cliff' not in t and 'K_star' not in t:
        continue
    n += 1
    if re.search(r'\b750\b', t):
        try:
            d = json.loads(t)
        except Exception:
            d = {}
        print('HIT', p, '| run_mode', d.get('run_mode'), '|', str(d.get('verdict'))[:40])
        print('   ', str(d.get('verdict_msg'))[:400])
print('scanned K_cliff/K_star artifacts:', n)
