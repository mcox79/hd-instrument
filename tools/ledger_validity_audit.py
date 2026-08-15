# -*- coding: ascii -*-
"""LEDGER VALIDITY AUDIT -- classify every RECOVERY_PROGRAM.md row against disk.

Answers, per row, the four questions that decide whether a green status row is a
result you can wire or a result that merely looks green:

  1. did it have a floor at all?
  2. was that floor the STRONGEST AVAILABLE non-understanding baseline, or the
     weakest on the shelf?  ladder: ORTHOGRAPHIC > FREQUENCY > SCRAMBLE
  3. was the comparison in the same currency as the criterion it is carried onto?
  4. was there a known-answer / positive arm?  A floor says whether the EFFECT is
     real; a positive arm says whether the INSTRUMENT is. Both, or it is half blind.

Detection is by SHAPE, never by verdict vocabulary -- verdict strings drift from
13 distinct forms in June to 444 in July, and a `scramble` keyword filter finds 11
floored cells in the chain-graded tier while missing 161 that have one.

NOTHING HERE DEMOTES A RESULT. Classifying a floor as weak is a statement about
the FLOOR, not about the result: it makes a win UNPROVEN, never FALSE.

Four traps this hit during development, all now guarded (see GUARD-n comments):
  GUARD-1 a family token that is also in the cell's own anchor_name is the
          TREATMENT, not a floor (compose_FREQ_routing; hoc1_word_BIGRAM)
  GUARD-2 keys stating a REQUIREMENT (HP_lift_over_null=0.3 is the BAR) or a
          DERIVED comparison (ultra_acc_minus_random) are not arm scores, and
          metrics where bigger is worse (auc_std, sparse_rate, falsefriend_sim)
          must not be read with max()
  GUARD-3 a floor 'winning' on one metric while losing by more on another is
          METRIC DISAGREEMENT, not a defeat (MAVEN-ERE majority = 97.78% accuracy
          and 0.00 micro-F1 on the same rows)
  GUARD-4 run_mode self_test is a harness check, not a measurement

Usage:  .venv/Scripts/python.exe tools/ledger_validity_audit.py [--json OUT]
"""
import os, re, json, collections, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, 'notes', 'RECOVERY_PROGRAM.md')
DATA = os.path.join(REPO, 'data')

# =====================================================================
# 1. PARSE -- ledger tables, by header shape
# =====================================================================
def _cells(line):
    s = line.strip()
    if s.startswith('|'): s = s[1:]
    if s.endswith('|'): s = s[:-1]
    return [c.strip() for c in s.split('|')]

STATE_RE = re.compile(r'STATE:([A-Z_]+)')
DUP_RE = re.compile(r'state=([A-Z_]+)\s+DUP-OF\s+([A-Za-z0-9_.-]+)')

def parse_rows():
    lines = open(SRC, encoding='utf-8').read().split('\n')
    raw, cur_sec, i = [], None, 0
    while i < len(lines):
        l = lines[i]
        if l.startswith('#'): cur_sec = l.strip('# ').strip()
        if l.startswith('| # |'):
            hdr = [c.lower() for c in _cells(l)]
            i += 1
            while i < len(lines) and re.match(r'^\|[\s\-:|]+\|\s*$', lines[i]): i += 1
            while i < len(lines) and lines[i].startswith('|'):
                c = _cells(lines[i])
                if len(c) == len(hdr):
                    d = dict(zip(hdr, c)); d['_section'] = cur_sec
                    raw.append(d)
                i += 1
            continue
        i += 1
    out = []
    for d in raw:
        st = d.get('state', '')
        m, m2 = STATE_RE.search(st), DUP_RE.search(st)
        if not (m or m2): continue
        name = (d.get('cell') or d.get('system') or '').strip().strip('`').strip()
        name = re.sub(r'\s*\*\*.*$', '', name).strip().strip('`')
        ev = d.get('evidence') or d.get('evidence (metrics.json)') or ''
        evm = re.search(r'(data/[A-Za-z0-9_./{},-]+metrics[A-Za-z0-9_.-]*\.json)', ev)
        out.append(dict(
            rid=d.get('#', '').strip(), section=d['_section'], name=name,
            evidence_path=evm.group(1) if evm else None,
            run_mode=(d.get('run_mode') or d.get('run mode') or '').strip(),
            floor_col=(d.get('floor') or d.get('floor by shape') or '').strip(),
            module=(d.get('module') or '').strip(), moves=(d.get('moves') or '').strip(),
            state=(m.group(1) if m else m2.group(1)),
            dup_of=(m2.group(2) if m2 else None)))
    return out

# =====================================================================
# 2. RESOLVE -- rows to on-disk artifacts, by ENUMERATION not search
# =====================================================================
def build_index():
    dirs = sorted(e.name for e in os.scandir(DATA) if e.is_dir())
    lower = collections.defaultdict(list)
    for d in dirs: lower[d.lower()].append(d)
    art = {}
    for d in dirs:
        p = os.path.join(DATA, d)
        mj = os.path.join(p, 'metrics.json')
        if os.path.isfile(mj):
            art[d] = mj; continue
        try: names = os.listdir(p)
        except OSError: continue
        # 4th invisibility mode: an artifact not named metrics.json
        alt = sorted(n for n in names if n.startswith('metrics') and n.endswith('.json'))
        if alt: art[d] = os.path.join(p, alt[0])
    return dirs, lower, art

BRACE = re.compile(r'\{([^}]*)\}')
def expand(name):
    m = BRACE.search(name)
    if not m: return [name]
    o = []
    for part in m.group(1).split(','):
        o.extend(expand(name[:m.start()] + part.strip() + name[m.end():]))
    return o

GENERIC = set('3seed full chain grade seed v1 v2 v3 gpu cpu exp substrate smoke'.split())

def resolve(row, dirs, lower, art):
    ep = row.get('evidence_path')
    if ep:
        d = ep.split('/')[1]
        for c in expand(d):
            if c in art: return [c], 'explicit-path'
            for r in lower.get(c.lower(), []):
                if r in art: return [r], 'explicit-path-ci'
    nm = row['name']
    if not nm: return [], 'no-name'
    var = expand(nm)
    hits = [v for v in var if v in art]
    if hits: return hits, 'exact'
    hits = [r for v in var for r in lower.get(v.lower(), []) if r in art]
    if hits: return hits, 'case-insensitive'
    m = re.search(r'_seed_(\d+)(?:_AND_(\d+))+', nm)
    if m:
        base, sd = nm[:m.start()], re.findall(r'(\d+)', nm[m.start():])
        hits = [c for s in sd for c in [base + '_seed_' + s] if c in art]
        if hits: return hits, 'seed-AND'
    pref = [d for d in dirs if d.lower().startswith(nm.lower()) and d in art]
    if pref: return sorted(pref, key=len)[:3], 'string-prefix'
    toks = [t for t in nm.split('_') if t]
    best, bs = None, 0
    for d in dirs:
        if d not in art: continue
        dt = [t for t in d.split('_') if t]
        n = 0
        for a, b in zip(toks, dt):
            if a.lower() != b.lower(): break
            n += 1
        if n < 4: continue
        info = sum(1 for t in toks[:n] if t.lower() not in GENERIC)
        if info < 2: continue
        if n * 100 + info > bs: best, bs = d, n * 100 + info
    if best: return [best], 'token-prefix-SIBLING'
    return [], 'DANGLING'

# =====================================================================
# 3. FLOOR LADDER + arm discovery
# =====================================================================
FAM = {
 'ORTHO': ('trigram bigram ngram charngram chargram orthographic orthography chartrigram '
           'spelling spell lexical levenshtein editdistance jaccard prefixonly prefixmatch '
           'stringform surfaceform surface stringmatch stringsim lemmaoverlap tokenoverlap '
           'wordform bagofwords tfidf bm25 substring chartri charngrams').split(),
 'FREQ':  ('frequency freq unigram baserate prior marginal majority mostcommon mostfrequent '
           'popularity zipf empiricalprior classprior freqnull freqoracle basefreq').split(),
 'SCRAM': ('scramble scrambled scram shuffle shuffled shuf permutedlabel labelshuffle random '
           'rand randomised randomized chance null nullarm noise mismatched mismatch '
           'pathology foil uniform untrained randinit randomarm').split(),
}
METHODW = set(('naive plain ablation ablated ablate lesion lesioned without noop nocx flat '
               'additive unwhitened untuned incumbent legacy raw basic standard dense fhrr '
               'hrr hebb knn cosine nogate nobind nostructure disabled single pooled sum '
               'unbound nowhiten nopinv').split())
POSW = set(('oracle ceiling knownanswer positivecontrol sanity upperbound seen gold skyline '
            'topline groundtruth teacher supervised cheat identity clean ceilingcheck '
            'reachability').split())
MFW = set(('mustfail cannotpass gapcontrol controlmax refutation decoy negativecontrol '
           'shouldfail nullcontrol canfail').split())
LADDER = ['ORTHO', 'FREQ', 'SCRAM']

def _t(s): return [x.lower() for x in re.split(r'[^A-Za-z0-9]+', str(s)) if x]

def classify_label(label):
    t = _t(label); j = ''.join(t); fams = set()
    for fam, words in FAM.items():
        for w in words:
            if w in t or (len(w) >= 7 and w in j): fams.add(fam); break
    return (fams, bool(set(t) & METHODW) or (len(t) and t[0] in ('no', 'off')),
            bool(set(t) & POSW) or 'oracle' in j or 'ceiling' in j,
            bool(set(t) & MFW) or 'mustfail' in j)

SEEDLIKE = re.compile(r'^(seed|s|run|iter|trial|rep|fold|step|epoch|n|d|k|m|p|v|t|l)?\d+$')

def _nodes(o, path=(), out=None):
    if out is None: out = []
    if isinstance(o, dict):
        out.append((path, o))
        for k, v in o.items(): _nodes(v, path + (str(k),), out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:60]): _nodes(v, path + ('[%d]' % i,), out)
    return out

def _leaves(o, path=(), out=None):
    if out is None: out = []
    if isinstance(o, dict):
        for k, v in o.items(): _leaves(v, path + (str(k),), out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:60]): _leaves(v, path + ('[%d]' % i,), out)
    else: out.append((path, o))
    return out

def _num(d):
    return {k: v for k, v in d.items()
            if isinstance(v, (int, float)) and not isinstance(v, bool)}

def extract_arms(j):
    """Four shape-based discovery modes; see module docstring."""
    nodes = _nodes(j); arms = collections.defaultdict(dict)
    for path, node in nodes:                                  # D1 dict-sibling
        kids = {k: v for k, v in node.items() if isinstance(v, dict)}
        if len(kids) < 2: continue
        ks = {k: set(_num(v).keys()) for k, v in kids.items()}
        shared = set.intersection(*ks.values()) if ks else set()
        if not shared or all(SEEDLIKE.match(l) for l in kids): continue
        for l in kids:
            for mk in shared:
                arms[l]['%s|%s' % ('.'.join(path[-2:]), mk)] = kids[l][mk]
    for path, node in nodes:                                  # D2/D3 key-sibling
        nl = _num(node)
        if len(nl) < 2: continue
        ks = list(nl.keys())
        tk = {k: [t for t in re.split(r'[_.]+', k) if t] for k in ks}
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)):
                ka, kb = ks[a], ks[b]; ta, tb = tk[ka], tk[kb]
                if len(ta) == len(tb) and len(ta) > 1:
                    diff = [i for i in range(len(ta)) if ta[i].lower() != tb[i].lower()]
                    if len(diff) != 1: continue
                    la, lb = ta[diff[0]], tb[diff[0]]
                    if SEEDLIKE.match(la) and SEEDLIKE.match(lb): continue
                    stem = '.'.join(path[-1:]) + '|' + '_'.join(
                        t if i != diff[0] else '*' for i, t in enumerate(ta))
                    arms[la][stem] = nl[ka]; arms[lb][stem] = nl[kb]
                elif len(ta) != len(tb):
                    sh, lo = (ta, tb) if len(ta) < len(tb) else (tb, ta)
                    kh, kl = (ka, kb) if len(ta) < len(tb) else (kb, ka)
                    low = [x.lower() for x in lo]; shl = [x.lower() for x in sh]
                    if low[:len(shl)] == shl: lab = '_'.join(lo[len(sh):])
                    elif low[-len(shl):] == shl: lab = '_'.join(lo[:len(lo) - len(sh)])
                    else: continue
                    if not lab or SEEDLIKE.match(lab): continue
                    stem = '.'.join(path[-1:]) + '|' + '_'.join(sh) + '/+'
                    arms['__BASE__'][stem] = nl[kh]; arms[lab][stem] = nl[kl]
    for path, val in _leaves(j):                              # D4 explicit ARM_*
        for i, comp in enumerate(path):
            if re.match(r'^[Aa][Rr][Mm][_-]\w', comp):
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    arms[comp]['.'.join(path[i + 1:]) or 'v'] = val
                else: arms[comp].setdefault('_nonnum', 0)
                break
    return arms

# ---- GUARD-2: which metrics may be read with max()
GOOD = ('acc accuracy auc auroc f1 recall precision hit hits top1 top5 topk r5 r10 mrr ndcg '
        'score lift capacity cap purity separation sep correct success coverage fidelity '
        'retention resolution win quality yield reach hitrate exact em').split()
BAD = ('std stdev sd var variance cv sem se err error loss nll dist distance time elapsed '
       'sec ms cost mem bytes false spurious collision interference leak drift confusion '
       'overlap contamination gap_control control_max rank_std entropy bpc perplexity ppl '
       'min max_dim norm count n_ sparse sparsity density falsefriend distractor null_rate '
       'fp fn miss').split()
NOT_A_MEASUREMENT = re.compile(
    r'(^|[._|])(hp|hf|hard_?pass|hard_?fail|min|max|need|req|required|thresh\w*|band|bar|'
    r'gate|target|expected|budget|tol|tolerance|cap_?limit)([._|]|$)', re.I)
DERIVED = re.compile(r'(minus|delta|diff|lift_?over|lift_?vs|gap_?vs|_vs_|improv|ratio|'
                     r'relative|norm_?by|over_?floor|over_?null|over_?base)', re.I)

def higher_is_better(metric):
    m = metric.lower()
    if NOT_A_MEASUREMENT.search(m) or DERIVED.search(m): return False
    parts = set(re.split(r'[^a-z0-9]+', m))
    for b in BAD:
        if b in parts or (len(b) > 3 and b in m): return False
    for g in GOOD:
        if g in parts or (len(g) > 3 and g in m): return True
    return False

def detect_beats(arms, arm_class, min_margin=0.01):
    metrics = collections.Counter()
    for lab, mm in arms.items():
        for k in mm: metrics[k] += 1
    out = []
    for mk, c in metrics.items():
        if c < 2 or not higher_is_better(mk): continue
        vals = [(l, arms[l][mk]) for l in arms
                if isinstance(arms[l].get(mk), (int, float))
                and not isinstance(arms[l].get(mk), bool)]
        if len(vals) < 2: continue
        best = max(vals, key=lambda x: x[1]); cl = arm_class.get(best[0], {})
        if not cl.get('fams') or cl.get('pos'): continue
        treat = [(l, v) for l, v in vals if l != best[0]
                 and not arm_class.get(l, {}).get('fams')
                 and not arm_class.get(l, {}).get('pos')
                 and not arm_class.get(l, {}).get('method') and l != '__BASE__']
        if not treat: continue
        topt = max(treat, key=lambda x: x[1])
        if best[1] - topt[1] < min_margin: continue
        out.append(dict(metric=mk[:70], floor=best[0], floor_fams=sorted(cl['fams']),
                        floor_val=round(best[1], 5), treatment=topt[0],
                        treatment_val=round(topt[1], 5), margin=round(best[1] - topt[1], 5)))
    return out

# =====================================================================
# 4. VERDICT SHAPE / REGIME / CURRENCY
# =====================================================================
VERDICT_FIELDS = ('verdict', 'verdict_msg', 'summary', 'headline', 'status', 'result',
                  'outcome', 'honest_scope', 'hp_scope', 'notes', 'note', 'conclusion',
                  'interpretation', 'weakest_interface', 'disposition', 'band')
NEG = ('fail refut negative nullresult notreached notachiev blocked abort error insufficient '
       'breakage broke worse below cannot doesnot killed dead reject exhausted regress degrad '
       'unsupported infeasible nogo notmet unmet').split()
POSV = ('pass win succeed success holds confirm achiev clean beats separat recover solved '
        'works clears exceed above resolves carries survives closed sound scalinghold '
        'eligible met rescue').split()
MIDV = ('middle middleband measured bound provenbound partial mixed inconclusive exploratory '
        'feasibility tentative unpinned headroom limit degenerate undetermined').split()
HEADPOS = ('pass', 'win', 'holds', 'clean', 'beats', 'solved', 'recover', 'confirm',
           'succe', 'scaling', 'sound', 'sys_hard')

def verdict_shape(v):
    if not v: return 'UNCLEAR'
    if '/' in v and ':' in v:
        arms = [a for a in re.split(r'\s*/\s*', v) if a.strip()]
        if len(arms) > 1:
            subs = set(verdict_shape(a) for a in arms)
            if 'POSITIVE' in subs and 'NEGATIVE' in subs: return 'MIXED'
            if 'POSITIVE' in subs: return 'POSITIVE'
            if 'NEGATIVE' in subs: return 'NEGATIVE'
    s = re.sub(r'[^a-z]', '', v.lower()); head = re.sub(r'[^a-z]', '', v.lower()[:26])
    if any(w in head for w in NEG): return 'NEGATIVE'
    if any(w in head for w in HEADPOS):
        if any(w in s for w in ('inconclusive', 'blocked', 'insufficient', 'notmet')):
            return 'MIXED'
        return 'POSITIVE'
    if any(w in head for w in MIDV): return 'MIDDLE'
    neg = [w for w in NEG if w in s]; pos = [w for w in POSV if w in s]
    if neg and not pos: return 'NEGATIVE'
    if pos and not neg: return 'POSITIVE'
    if pos and neg: return 'MIXED'
    if any(w in s for w in MIDV): return 'MIDDLE'
    return 'UNCLEAR'

REALW = ('minilm bge e5 llama pythia gpt2 bert roberta mpnet wordnet cskg conceptnet hotpotqa '
         'mcscript mcguffey verbnet simlex propbank framenet ontonotes squad wikitext wikipedia '
         'corpus glove word2vec fasttext openvocab heldout maven sentencetransformer atomic '
         'swow usf mcrae ppmi').split()

def analyse(path, cellname):
    try: j = json.load(open(path, encoding='utf-8'))
    except Exception as e: return {'err': str(e)[:100]}
    if not isinstance(j, dict): return {'err': 'not-a-dict'}
    arms = extract_arms(j); leaves = _leaves(j)
    prim = ''
    for k in ('verdict', 'verdict_msg', 'headline', 'summary', 'status'):
        if isinstance(j.get(k), str) and j[k].strip(): prim = j[k]; break
    vparts = []
    def _vw(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and k.lower() in VERDICT_FIELDS: vparts.append(v)
                else: _vw(v)
        elif isinstance(o, list):
            for v in o[:20]: _vw(v)
    _vw(j)
    vt = ' || '.join(vparts)
    if not prim: prim = vt[:300]

    rm = str(j.get('run_mode') or j.get('mode') or '').lower()
    is_selftest = ('self' in rm and 'test' in rm) or \
                  'selftest' in re.sub(r'[^a-z]', '', prim.lower())[:40]

    # GUARD-1 anchor-name guard
    anchor_tok = set(_t(str(j.get('anchor_name') or '') + ' ' + cellname))
    mech = set()
    for fam, words in FAM.items():
        for w in words:
            if w in anchor_tok: mech.add(fam); break

    arm_class, fams_arm = {}, set()
    pos = mf = meth = False
    for lab in arms:
        f, m, p, x = classify_label(lab)
        arm_class[lab] = dict(fams=sorted(f), method=m, pos=p, mustfail=x)
        fams_arm |= (f - mech); pos |= p; mf |= x; meth |= m

    ptok = _t(vt); pj = ''.join(ptok); fams_prose = set()
    for fam, words in FAM.items():
        if fam in mech: continue
        for w in words:
            if w in ptok or (len(w) >= 7 and w in pj): fams_prose.add(fam); break
    # comparative constructions, over keys AND prose: <x>_floor / delta_vs_<x> / vs <x>.
    # This is how June wrote floors it never gave a key to (hebb_alpha_c, FREQ_NULL,
    # last_token_raw); dropping it silently moves ~6 rows from SOFT to UNFLOORED.
    blob_txt = ' '.join('.'.join(p) for p, _ in leaves) + ' \n ' + \
               ' '.join(str(v) for _, v in leaves if isinstance(v, str))
    for pat in (r'([A-Za-z0-9_]{3,40})[_ ](?:floor|baseline|reference|control|null)\b',
                r'(?:floor|baseline|reference|control)[_ ]([A-Za-z0-9_]{3,40})',
                r'(?:delta|gap|lift|margin|beats?|above|over|improv\w*)[_ ](?:vs|over|above|than)?[_ ]?([A-Za-z0-9_]{3,40})',
                r'\bvs\.?[_ ]([A-Za-z0-9_]{3,40})'):
        for m in re.finditer(pat, blob_txt, re.I):
            fams_prose |= (classify_label(m.group(1))[0] - mech)

    for pth, val in leaves:
        low = '.'.join(pth).lower()
        if 'positive_control' in low: pos = True
        if 'must_fail' in low or 'negative_control' in low or 'can_fail' in low: mf = True

    # GUARD-3 metric-disagreement
    kept = []
    for b in detect_beats(arms, arm_class):
        if set(b['floor_fams']) <= mech: continue                     # GUARD-1
        fl, tr = b['floor'], b['treatment']
        contra = 0
        for m in arms.get(fl, {}):
            if m not in arms.get(tr, {}) or not higher_is_better(m): continue
            fv, tv = arms[fl][m], arms[tr][m]
            if isinstance(fv, (int, float)) and isinstance(tv, (int, float)) \
               and tv - fv > b['margin']: contra += 1
        if contra: continue
        kept.append(b)

    blob = set()
    for p, s in leaves: blob.update(_t('.'.join(p) + ' ' + str(s)))
    cur = set()
    if blob & {'hit', 'hits', 'top1', 'topk', 'recall', 'acc', 'accuracy', 'precision1',
               'mrr', 'r5', 'r10', 'hitrate', 'retrieval'}: cur.add('RETRIEVAL')
    if blob & {'2afc', 'pairwise', 'twoafc'}: cur.add('2AFC')
    if blob & {'capacity', 'cap', 'nstored', 'kmax', 'mmax', 'mcap'}: cur.add('CAPACITY')
    if blob & {'cosine', 'cossim', 'similarity'}: cur.add('GEOMETRY')
    if blob & {'auroc', 'auc', 'f1'}: cur.add('CLASSIFIER')
    if 'margin' in blob: cur.add('MARGIN')
    if blob & {'bpc', 'perplexity', 'ppl', 'nll'}: cur.add('LM')

    return dict(shape=verdict_shape(prim), verdict=prim[:280], run_mode=rm,
                is_selftest=is_selftest, is_full=rm.startswith('full'),
                fams_arm=sorted(fams_arm), fams_prose=sorted(fams_prose),
                pos_arm=pos, mustfail_arm=mf, method_contrast=meth, n_arms=len(arms),
                beats=kept[:3], currency=sorted(cur),
                real=sorted(w for w in REALW if w in blob),
                seeds=(j.get('n_seeds') if isinstance(j.get('n_seeds'), int)
                       else (len(j['seeds']) if isinstance(j.get('seeds'), list) else 0)),
                hygiene=[k for k in ('arms_differ_verified', 'no_leak_verified',
                                     'cardinality_ok', 'deterministic_seeding', 'prereg_path',
                                     'positive_control', 'discriminator_reachability')
                         if k in j])

# =====================================================================
# 5. CLASSIFY
# =====================================================================
def classify(row, cache):
    az = [cache[d] for d in row.get('dirs', []) if d in cache and 'err' not in cache[d]]
    if not az:
        return dict(validity='NO-ARTIFACT', win_claim='UNKNOWN', floor_tier='UNKNOWN',
                    floor_evid='NONE', why=['no metrics artifact resolves on disk'])
    sh = [a['shape'] for a in az]
    win = ('POSITIVE' if 'POSITIVE' in sh else 'MIXED' if 'MIXED' in sh else
           'MIDDLE' if 'MIDDLE' in sh else 'NEGATIVE' if 'NEGATIVE' in sh else 'UNCLEAR')
    fa = set(); fp = set(); cur = set(); real = set()
    for a in az:
        fa |= set(a['fams_arm']); fp |= set(a['fams_prose'])
        cur |= set(a['currency']); real |= set(a['real'])
    pos = any(a['pos_arm'] for a in az); mf = any(a['mustfail_arm'] for a in az)
    meth = any(a['method_contrast'] for a in az)
    beats = [b for a in az for b in a['beats']]
    full = any(a['is_full'] for a in az)
    selftest = all(a['is_selftest'] for a in az) and not full
    narms = max(a['n_arms'] for a in az)

    tier, evid = 'NONE-VISIBLE', 'NONE'
    for f in LADDER:
        if f in fa: tier, evid = f, 'ARM'; break
    if tier == 'NONE-VISIBLE':
        for f in LADDER:
            if f in fp: tier, evid = f, 'PROSE'; break
    if tier == 'NONE-VISIBLE' and meth and narms >= 2: tier, evid = 'METHOD-ONLY', 'ARM'

    synth = not real
    firm_c3 = bool(re.search(r'\bC3\b(?!\?)', row.get('moves', '')))
    cross, cwhy = False, []
    if firm_c3:
        if 'RETRIEVAL' not in cur:
            cross = True; cwhy.append('claims C3 (open-vocab hit@1, pool 5491) but its own '
                                      'currency is ' + ('/'.join(sorted(cur)) or 'none identifiable'))
        if '2AFC' in cur:
            cross = True; cwhy.append('2AFC (chance 0.50) carried onto open-vocab')
        if synth:
            cross = True; cwhy.append('synthetic regime, claim is on the real task')

    # STRONGEST APPLICABLE floor. Any real-data regime has word/concept items, so a
    # string-form baseline is APPLICABLE -- and on 2026-08-14 spelling-alone beat the
    # read-out 0.0870 to 0.0480. A lexical-regime win floored only to frequency or
    # scramble is therefore NOT floored against the strongest available baseline.
    required = 'ORTHO' if real else 'FREQ'
    meets = (required in fa) if required == 'ORTHO' else bool({'ORTHO', 'FREQ'} & fa)

    construction = 'APPENDIX A' in (row.get('section') or '').upper()
    if construction: v = 'CONSTRUCTION'
    elif win != 'POSITIVE': v = 'NOT-A-WIN-CLAIM'
    elif selftest: v = 'NOT-A-RESULT'
    elif beats: v = 'FLOOR-BEATEN'
    elif cross: v = 'CROSS-SCORER'
    elif tier == 'NONE-VISIBLE': v = 'UNFLOORED'
    elif meets and evid == 'ARM' and (pos or mf) and full and not synth: v = 'HARD'
    else: v = 'SOFT'

    why = []
    if v == 'SOFT':
        if tier == 'SCRAM': why.append('floor is scramble/random tier -- the WEAKEST shelf baseline')
        if tier == 'METHOD-ONLY': why.append('only an internal method/ablation contrast, no non-understanding baseline')
        if evid == 'PROSE': why.append('floor stated in verdict prose, not present as a key')
        if not (pos or mf): why.append('no known-answer / must-fail arm: the INSTRUMENT is unverified')
        if not full: why.append('run_mode not full')
        if synth: why.append('synthetic regime -- no real encoder/corpus marker')
        if real and not meets and tier in ('FREQ', 'SCRAM'):
            why.append('STRONGEST APPLICABLE floor (orthographic/string-form) WAS NOT RUN')
    elif v == 'UNFLOORED':
        why.append('no floor arm visible in metrics.json -- NOT a claim that none was run')
    elif v == 'CROSS-SCORER': why = cwhy
    elif v == 'FLOOR-BEATEN':
        why = ['%s floor %s=%s beats treatment %s=%s on %s' %
               (','.join(b['floor_fams']), b['floor'], b['floor_val'],
                b['treatment'], b['treatment_val'], b['metric']) for b in beats[:2]]
    elif v == 'NOT-A-RESULT': why.append('run_mode self_test -- a harness check, not a measurement')

    return dict(validity=v, win_claim=win, floor_tier=tier, floor_evid=evid,
                fams_arm=sorted(fa), fams_prose=sorted(fp), pos_arm=pos, mustfail_arm=mf,
                method_contrast=meth, n_arms=narms, currency=sorted(cur), real=sorted(real),
                run_mode_full=full, synthetic=synth, seeds=max(a['seeds'] or 0 for a in az),
                hygiene=sorted(set(h for a in az for h in a['hygiene'])),
                beats=beats[:2], why=why, verdict=az[0]['verdict'])

TIERPTS = {'ORTHO': 4, 'FREQ': 3, 'SCRAM': 1, 'METHOD-ONLY': 0, 'NONE-VISIBLE': 0}

def score(row):
    V = row['V']
    if V['validity'] in ('NOT-A-WIN-CLAIM', 'CONSTRUCTION', 'NOT-A-RESULT', 'NO-ARTIFACT'):
        return -99, ['excluded: ' + V['validity']]
    s, why = 0, []
    p = TIERPTS.get(V['floor_tier'], 0) * (1 if V['floor_evid'] == 'ARM' else 0.5)
    s += p
    if p: why.append('%s floor (%s)' % (V['floor_tier'], V['floor_evid']))
    if V['pos_arm'] or V['mustfail_arm']: s += 2; why.append('positive/must-fail arm')
    if V['run_mode_full']: s += 2; why.append('full run')
    if (V['seeds'] or 0) >= 3: s += 1; why.append('%d seeds' % V['seeds'])
    if not V['synthetic']: s += 2; why.append('real regime ' + ','.join(V['real'][:3]))
    if V['hygiene']: s += 1; why.append('hygiene')
    if row.get('module', '').upper().startswith(('HDLAB', 'HD:')): s += 1; why.append('module exists')
    if V['validity'] == 'CROSS-SCORER': s -= 3; why.append('CROSS-SCORER penalty')
    if V['validity'] == 'FLOOR-BEATEN': s -= 5; why.append('FLOOR-BEATEN penalty')
    return s, why

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    rows = parse_rows()
    dirs, lower, art = build_index()
    cache = {}
    for r in rows:
        r['dirs'], r['resolve'] = resolve(r, dirs, lower, art)
        for d in r['dirs']:
            if d not in cache: cache[d] = analyse(art[d], d)
    for r in rows:
        r['V'] = classify(r, cache)
        r['score'], r['score_why'] = score(r)
    cnt = [r for r in rows if not r['dup_of']]
    print('countable rows: %d   artifacts read: %d' % (len(cnt), len(cache)))
    for k, v in collections.Counter(r['V']['validity'] for r in cnt).most_common():
        print('   %-18s %4d' % (k, v))
    if a.json:
        json.dump([dict(rid=r['rid'], section=r['section'], name=r['name'], dirs=r['dirs'],
                        state=r['state'], moves=r['moves'], floor_col=r['floor_col'],
                        score=r['score'], V=r['V']) for r in cnt],
                  open(a.json, 'w', encoding='ascii'), indent=0)
        print('wrote', a.json)
    return rows, cnt

if __name__ == '__main__':
    main()
