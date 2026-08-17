import json, os, sys, glob

targets = sys.argv[1:]
for t in targets:
    for p in sorted(glob.glob(t)):
        if not p.endswith('metrics.json'):
            p = os.path.join(p, 'metrics.json')
        if not os.path.exists(p):
            print('MISSING', p); continue
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print('BADJSON', p, e); continue
        print('=' * 25, p)
        for k in ('run_mode', 'n_items', 'n_anchors', 'n_seeds', 'chance', 'elapsed_s', 'prereg', 'verdict'):
            if k in d:
                print('  %-12s %s' % (k, str(d[k])[:120]))
        print('  MSG:', str(d.get('verdict_msg', ''))[:1500])
        for k in ('arm_accuracy', 'K_cliff_per_op', 'per_op_summary', 'per_arm', 'arms', 'sweep',
                  'K_star_per_op', 'floors', 'per_dim', 'results', 'by_dim', 'summary_table'):
            if k in d:
                print('  %s = %s' % (k, json.dumps(d[k])[:1400]))
        print('  ALLKEYS:', ','.join(list(d.keys()))[:600])
