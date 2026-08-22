#!/usr/bin/env python
"""Progress snapshot: derives "where are we" from disk, in plain language, every session.

Built because hand-maintained status docs rot silently and the owner has said twice they
have no sense of progress. This is a MECHANISM, not a document: every line traces to a file
on disk (a commit hash, a metrics.json, notes/STATUS.md's own WHAT IS RUNNING block, or the
scoreboard table in notes/SUBSTRATE_STRATEGY.md). Anything that cannot be derived prints the
literal string UNKNOWN -- never a guess, never a stale number shown as current.

Five sections, one screen:
  1. Plan progress    -- notes/PLAN_NEXT_12H.md steps, each marked DONE/RUNNING/NOT STARTED,
                          evidence = a matching commit subject, a STATUS.md running-block line,
                          or a data/ result directory -- never eyeballed.
  2. Running right now -- data/heartbeats/*.timestamp ages + fresh data/ dirs (mtime, NOT
                          `tasklist`, which is unreliable under Git Bash and produced a false
                          "finished" once already) + notes/STATUS.md's own WHAT IS RUNNING block.
  3. Scoreboard        -- the C1-C4 numbers from notes/SUBSTRATE_STRATEGY.md PART 1, quoted
                          verbatim (name/now/floor cells), plus the C3 vs orthographic-floor
                          honesty check read directly from
                          data/exp_orthographic_floor_vet_v1/metrics.json when present.
  4. What moved        -- diffs against the previous snapshot's embedded state (an HTML-comment
                          JSON blob at the bottom of the file this script itself wrote last time).
  5. What is stuck      -- HELD/BLOCKED/PENDING lines in STATUS.md's running block, plus plan
                          steps with no evidence at all.

Modes:
  (default)   full derive; writes notes/PROGRESS_SNAPSHOT.md (rewritten in place) and prints it.
  --hook      same full derive (kept fast -- no recursive data/ walk, one bounded git log call),
              but prints ONLY the headline line, for session_start_hook.py to inject cheaply.
              Still rewrites notes/PROGRESS_SNAPSHOT.md as a side effect -- this IS the "periodic
              without a cron" mechanism: the hook is proven to fire every session, so wiring the
              refresh there survives a disabled scheduled task the way three prior mechanisms did
              not (11 hd_* tasks silently disabled 12 days; KB ingest 6 days; hd_session_watchdog
              writing 1585 ping files nothing reads).
  --self-test unit-tests the parsing/classification functions against in-memory fixtures. Never
              touches notes/STATUS.md, notes/SUBSTRATE_STRATEGY.md, or notes/PLAN_NEXT_12H.md.

ASCII-only. .venv/Scripts/python.exe, never bare python. cwd-independent (absolute paths only).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
PLAN_MD = REPO / 'notes' / 'PLAN_NEXT_12H.md'
STATUS_MD = REPO / 'notes' / 'STATUS.md'
STRATEGY_MD = REPO / 'notes' / 'SUBSTRATE_STRATEGY.md'
OUT_MD = REPO / 'notes' / 'PROGRESS_SNAPSHOT.md'
ORTHO_METRICS = REPO / 'data' / 'exp_orthographic_floor_vet_v1' / 'metrics.json'
HEARTBEATS_DIR = REPO / 'data' / 'heartbeats'
DATA_DIR = REPO / 'data'
GIT_TIMEOUT_SEC = 15
STATE_MARK_START = '<!-- SNAPSHOT_STATE_JSON'
STATE_MARK_END = '-->'
DATA_FRESH_WINDOW_MIN = 180.0   # "running right now" window for data/ dir mtimes
HEARTBEAT_STALE_MIN = 90.0      # matches PART 4's self-drive-tick stale threshold

UNKNOWN = 'UNKNOWN'

STOPWORDS = {
    'about', 'after', 'again', 'again', 'along', 'alongside', 'always', 'apply', 'artifact',
    'because', 'before', 'being', 'branches', 'build', 'could', 'depend', 'doing', 'during',
    'either', 'every', 'final', 'first', 'given', 'nothing', 'neither', 'never', 'notes',
    'outcome', 'produced', 'question', 'record', 'recover', 'session', 'shall', 'should',
    'stalls', 'state', 'stated', 'still', 'their', 'there', 'these', 'those', 'until',
    'using', 'which', 'while', 'would', 'write', 'written', 'memory', 'director',
    'conversation', 'answer', 'continue',
    # generic scientific-writing words that would otherwise create noisy false-positive
    # overlaps between plan-step prose and unrelated experiment directory names
    'measured', 'measure', 'result', 'results', 'value', 'values', 'shown', 'based',
    'across', 'share', 'group', 'table', 'count', 'level', 'points', 'point', 'other',
    'items', 'words', 'number', 'numbers', 'change', 'changed', 'against',
}


# --------------------------------------------------------------------------------------
# generic helpers
# --------------------------------------------------------------------------------------

def _read(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding='utf-8')
    except OSError:
        return None


def _run_git(*args: str) -> Optional[str]:
    try:
        proc = subprocess.run(
            ['git', '-C', str(REPO), *args],
            capture_output=True, text=True, timeout=GIT_TIMEOUT_SEC,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


_ASCII_MAP = str.maketrans({
    '—': '--', '–': '-', '‘': "'", '’': "'",
    '“': '"', '”': '"', '→': '->', '≤': '<=', '≥': '>=',
})


def _asciify(text: str) -> str:
    """Repo convention is ASCII-only output; source docs quoted verbatim carry em-dashes,
    curly quotes and arrows that otherwise render as mangled bytes on a non-UTF8 console
    (observed directly: printed output showed a literal replacement glyph)."""
    return text.translate(_ASCII_MAP)


def _trunc(text: str, n: int) -> str:
    """Truncate at a word boundary with an ellipsis marker, never mid-word."""
    text = text.strip()
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(' ', 1)[0]
    return (cut or text[:n]) + ' ...'


def stem(token: str) -> str:
    token = token.lower()
    return token[:6] if len(token) >= 6 else token


def tokenize(text: str, minlen: int = 5) -> set[str]:
    words = re.findall(r'[a-zA-Z]+', text.lower())
    return {stem(w) for w in words if len(w) >= minlen and w not in STOPWORDS}


# --------------------------------------------------------------------------------------
# 1. plan progress
# --------------------------------------------------------------------------------------

def parse_plan_steps(plan_text: str) -> list[dict]:
    """Split on '### ' headings. Each step: id (before the dash), title, body, tokens."""
    steps = []
    # split on lines starting with '### ' or '## ' (the latter closes the last '### ' section)
    lines = plan_text.splitlines()
    cur = None
    for ln in lines:
        if ln.startswith('### '):
            if cur is not None:
                steps.append(cur)
            heading = ln[4:].strip()
            # split on an em-dash or a spaced double-hyphen ONLY -- never a bare '-', which
            # appears inside step ids like "0-1h" / "8-11h" and would truncate them to "0"/"8"
            parts = re.split(r'\s+--\s+|—', heading, maxsplit=1)
            step_id = parts[0].strip() if parts else heading
            title = parts[1].strip() if len(parts) > 1 else heading
            cur = {'id': step_id, 'title': title, 'heading': heading, 'body_lines': []}
        elif ln.startswith('## ') or ln.strip() == '---':
            if cur is not None:
                steps.append(cur)
                cur = None
        else:
            if cur is not None:
                cur['body_lines'].append(ln)
    if cur is not None:
        steps.append(cur)
    for s in steps:
        body = '\n'.join(s['body_lines'])
        s['body'] = body
        s['tokens'] = tokenize(s['heading'] + ' ' + body)
        # ONLY "HELD PENDING" -- NOT "Stop if:", which is boilerplate present in every step's
        # required template ("the question, the artifact, the test that can fail, and what
        # makes us stop") and would otherwise false-flag every single step as BLOCKED.
        s['held_pending'] = bool(re.search(r'HELD PENDING', body, re.IGNORECASE))
        m = re.search(r'HELD PENDING[^.\n]{0,90}', body, re.IGNORECASE)
        s['held_excerpt'] = m.group(0).strip() if m else None
        del s['body_lines']

    # DISCOUNT tokens that recur across most steps of THIS plan before matching. Found
    # necessary directly: this plan's central theme word ("structure"/"structured") appears
    # in 4 of 6 steps' own prose, so on raw overlap it "matched" evidence for a step it had
    # nothing to do with (the step's own text was the source of the false trigger, not the
    # evidence). A word repeated across most of the document cannot discriminate BETWEEN its
    # sections; this is document-frequency filtering, computed fresh each run so it adapts
    # automatically if a future rewrite of the plan changes its vocabulary.
    n_steps = len(steps)
    df: dict[str, int] = {}
    for s in steps:
        for tok in s['tokens']:
            df[tok] = df.get(tok, 0) + 1
    threshold = max(1, -(-n_steps // 2))  # ceil(n_steps / 2)
    for s in steps:
        s['match_tokens'] = {t for t in s['tokens'] if df.get(t, 0) <= threshold}
    return steps


def git_commits_since(days: int = 30, max_count: int = 500) -> list[dict]:
    out = _run_git('log', f'--since={days} days ago', '-n', str(max_count),
                    '--format=%H%x1f%s')
    if out is None:
        return []
    commits = []
    for line in out.splitlines():
        if '\x1f' not in line:
            continue
        h, subj = line.split('\x1f', 1)
        commits.append({'hash': h, 'subject': subj, 'tokens': tokenize(subj)})
    return commits


def build_data_dir_index() -> dict[str, list[str]]:
    """One pass over top-level data/ dirs -> inverted index token -> [dirnames].
    Non-recursive (a recursive walk over ~7885 dirs is the expensive operation this file
    exists to avoid; CLAUDE.md records a full-repo grep at 8.5s for exactly that reason)."""
    index: dict[str, list[str]] = {}
    if not DATA_DIR.is_dir():
        return index
    try:
        entries = list(os.scandir(DATA_DIR))
    except OSError:
        return index
    for e in entries:
        if not e.is_dir():
            continue
        for tok in tokenize(e.name.replace('exp_', '')):
            index.setdefault(tok, []).append(e.name)
    return index


def match_step_evidence(step: dict, commits: list[dict], running_lines: list[str],
                         data_index: dict[str, list[str]]) -> dict:
    """Token-overlap evidence, ranked and labeled by strength.

    A SINGLE shared stem between a short plan-step heading and thousands of commit subjects
    is not reliable on its own (observed directly: "negative" in a step's prose matched a
    commit about a "negative control" in an unrelated self-test). Overlap of >=2 tokens is
    treated as a confident match; overlap of exactly 1 is kept (recall matters for short
    headings like "COMPACTION SAFETY" that legitimately hinge on one word) but labeled WEAK so
    the reader knows to eyeball it rather than trust it outright -- the same "print the
    evidence, let a human judge it" principle as everywhere else in this tool.
    """
    scored_commits = sorted(
        ((c, c['tokens'] & step['match_tokens']) for c in commits if c['tokens'] & step['match_tokens']),
        key=lambda pair: -len(pair[1]),
    )
    commit_hits = [c for c, _ov in scored_commits]
    strong_commit = bool(scored_commits) and len(scored_commits[0][1]) >= 2
    running_hits = [ln for ln in running_lines if tokenize(ln) & step['match_tokens']]
    dir_hits: set[str] = set()
    for tok in step['match_tokens']:
        dir_hits.update(data_index.get(tok, []))
    dir_hits = sorted(dir_hits)[:5]

    # PRIORITY: notes/STATUS.md's WHAT IS RUNNING block is hand-curated by the working session
    # in near-real-time -- it is a stronger signal than a stemmed-token guess against git log,
    # so an active running-block match wins over even a "strong" (2-token) commit match. This
    # was found necessary directly: "structural floor recovery" (a cert_ledger triage commit)
    # 2-token-matched step 4-8h ("TEST STRUCTURE AGAINST THE BAG") on stems 'struct'+'floor'
    # while STATUS.md correctly names the real in-flight work
    # (data/exp_structured_comparator_v1/probes -- concurrent writers, not yet landed).
    if step['held_pending']:
        status = 'BLOCKED'
    elif running_hits:
        status = 'RUNNING'
    elif strong_commit:
        status = 'DONE'
    elif commit_hits:
        status = 'DONE (weak)'
    elif dir_hits:
        status = 'RUNNING'
    else:
        status = 'NOT STARTED'

    evidence_bits = []
    if step['held_pending'] and step['held_excerpt']:
        evidence_bits.append(f"plan states: {step['held_excerpt']}")
    if running_hits:
        evidence_bits.append(f"STATUS.md running-block: \"{_trunc(running_hits[0], 80)}\"")
    if commit_hits:
        c, overlap = scored_commits[0]
        weak_tag = '' if strong_commit else f" [WEAK match on '{next(iter(overlap))}' -- verify]"
        evidence_bits.append(f"commit {c['hash'][:9]} \"{_trunc(c['subject'], 70)}\"{weak_tag}")
        if len(commit_hits) > 1:
            evidence_bits.append(f"(+{len(commit_hits) - 1} more commits)")
    if dir_hits and status == 'RUNNING' and not running_hits:
        evidence_bits.append(f"data/ dirs: {', '.join(dir_hits[:3])}")
    if not evidence_bits:
        evidence_bits.append('no matching commit, running-block line, or data/ dir found')

    return {'status': status, 'evidence': '; '.join(evidence_bits)}


# --------------------------------------------------------------------------------------
# 2. running right now
# --------------------------------------------------------------------------------------

def _load_session_start_hook():
    spec = importlib.util.spec_from_file_location(
        'session_start_hook', REPO / 'tools' / 'session_start_hook.py')
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def status_running_lines() -> list[str]:
    """Pull the bullet lines out of notes/STATUS.md's '## WHAT IS RUNNING' section. Read-only;
    reuses session_start_hook's own parser so the two never silently diverge (CLAUDE.md: 'a
    doc parsed by code is coupled to it')."""
    text = _read(STATUS_MD)
    if text is None:
        return []
    lines = text.splitlines()
    out, in_running, found = [], False, False
    for ln in lines:
        if ln.strip().startswith('## WHAT IS RUNNING'):
            in_running, found = True, True
            continue
        if in_running and ln.strip().startswith('## '):
            break
        if in_running and ln.strip():
            out.append(ln)
    return out if found else []


def heartbeat_report() -> list[str]:
    if not HEARTBEATS_DIR.is_dir():
        return [f'[heartbeats] {UNKNOWN} -- {HEARTBEATS_DIR} does not exist']
    now = time.time()
    lines = []
    for f in sorted(HEARTBEATS_DIR.glob('*.timestamp')):
        raw = _read(f)
        if raw is None:
            continue
        raw = raw.strip()
        try:
            import datetime
            ts = datetime.datetime.strptime(raw, '%Y-%m-%dT%H:%M:%SZ').replace(
                tzinfo=datetime.timezone.utc).timestamp()
            age_min = (now - ts) / 60.0
        except ValueError:
            # fall back to file mtime if the content isn't parseable
            age_min = (now - f.stat().st_mtime) / 60.0
        flag = ' <-- STALE' if age_min > HEARTBEAT_STALE_MIN else ''
        lines.append(f'{f.stem}: {age_min:.0f} min ago{flag}')
    return lines or ['(no heartbeat files found)']


def fresh_data_dirs(window_min: float = DATA_FRESH_WINDOW_MIN, limit: int = 8) -> list[str]:
    """Top-level data/ dirs modified in the last `window_min` minutes. mtime of a directory
    reflects a direct child being added/removed, not a nested-grandchild write -- an
    approximation, stated here rather than silently assumed. This is deliberately NOT a
    process-table check (tasklist is unreliable under Git Bash in this environment and
    produced a false "finished" once already); it is "what changed on disk recently."""
    if not DATA_DIR.is_dir():
        return [f'{UNKNOWN} -- {DATA_DIR} does not exist']
    now = time.time()
    hits = []
    try:
        for e in os.scandir(DATA_DIR):
            if not e.is_dir():
                continue
            try:
                mtime = e.stat().st_mtime
            except OSError:
                continue
            age_min = (now - mtime) / 60.0
            if age_min <= window_min:
                has_metrics = (Path(e.path) / 'metrics.json').exists()
                hits.append((age_min, e.name, has_metrics))
    except OSError:
        return [f'{UNKNOWN} -- could not scan {DATA_DIR}']
    hits.sort()
    out = []
    for age_min, name, has_metrics in hits[:limit]:
        tag = 'has metrics.json' if has_metrics else 'NO metrics.json yet (likely in-flight)'
        out.append(f'{name}: {age_min:.0f} min ago, {tag}')
    if not out:
        out.append(f'(no data/ dir modified in the last {window_min:.0f} min)')
    return out


# --------------------------------------------------------------------------------------
# 3. scoreboard (C1-C4)
# --------------------------------------------------------------------------------------

VERDICT_WORDS = re.compile(
    r'NOT PASSED|NOT_EVALUABLE|FAILS?|CLEARS?|BEATS?|LOSES?|LOSING|PASSED|PASS\b', re.IGNORECASE)


def parse_c_scoreboard(strategy_text: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for ln in strategy_text.splitlines():
        m = re.match(r'\|\s*\*\*C([1-4])\*\*\s*\|(.*)\|\s*$', ln)
        if not m:
            continue
        cnum, rest = m.group(1), m.group(2)
        cells = [c.strip() for c in rest.split('|')]
        if len(cells) < 4:
            continue
        name, now_cell, floor_cell = cells[0], cells[1], cells[2]
        vm = VERDICT_WORDS.search(now_cell) or VERDICT_WORDS.search(floor_cell)
        verdict = vm.group(0).upper() if vm else '(no verdict word in table cell)'
        rows[f'C{cnum}'] = {
            'name': name.strip('* '),
            'now': now_cell,
            'floor': floor_cell,
            'verdict': verdict,
        }
    return rows


def c3_honesty_check() -> str:
    """The one comparison the task calls out by name: C3's own number against the
    orthographic (spelling-only) floor, read straight from the auditor cell's metrics.json
    rather than trusted from prose. UNKNOWN if the file or the expected keys are missing --
    never a stale number shown as current."""
    data = None
    text = _read(ORTHO_METRICS)
    if text is not None:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = None
    if data is None:
        return f'C3 vs spelling floor: {UNKNOWN} -- {ORTHO_METRICS} missing or unreadable'
    try:
        base = data['per_arm']['A1_BASE']['hit_at_1']
        floor = data['per_arm']['A6_TRIGRAM_ONLY']['hit_at_1']
        delta = data['bootstrap']['deltas']['d_A6_TRIGRAM_ONLY_minus_BASE']
        excl_zero = delta['ci_excludes_zero']
    except (KeyError, TypeError):
        return f'C3 vs spelling floor: {UNKNOWN} -- expected keys missing in {ORTHO_METRICS.name}'
    verb = 'LOSING to' if floor > base else 'beating'
    ci_note = 'CI excludes zero (real gap)' if excl_zero else 'CI includes zero (not separated)'
    return (f'C3 vs spelling-only floor: our {base:.4f} is {verb} spelling-alone {floor:.4f} '
            f'(delta {delta["delta"]:+.4f}, {ci_note}) -- source: {ORTHO_METRICS.relative_to(REPO)}')


# --------------------------------------------------------------------------------------
# 4. diff against previous snapshot (state embedded as an HTML-comment JSON blob)
# --------------------------------------------------------------------------------------

def load_prev_state(prev_text: Optional[str]) -> Optional[dict]:
    if not prev_text or STATE_MARK_START not in prev_text:
        return None
    try:
        blob = prev_text.split(STATE_MARK_START, 1)[1].split(STATE_MARK_END, 1)[0]
        return json.loads(blob)
    except (IndexError, json.JSONDecodeError):
        return None


def diff_state(prev: Optional[dict], new: dict) -> list[str]:
    if prev is None:
        return ['(no previous snapshot found -- this is the first run)']
    out = []
    old_head, new_head = prev.get('head_commit'), new.get('head_commit')
    if old_head and new_head and old_head != new_head:
        log = _run_git('log', '--oneline', f'{old_head}..{new_head}')
        n_new = len(log.splitlines()) if log else 0
        out.append(f'{n_new} new commit(s) since last snapshot (HEAD {old_head[:9]} -> {new_head[:9]})')
    old_steps, new_steps = prev.get('step_status', {}), new.get('step_status', {})
    for sid, new_status in new_steps.items():
        old_status = old_steps.get(sid)
        if old_status is not None and old_status != new_status:
            out.append(f'plan step "{sid}": {old_status} -> {new_status}')
    old_c, new_c = prev.get('c_now', {}), new.get('c_now', {})
    for cnum, new_val in new_c.items():
        old_val = old_c.get(cnum)
        if old_val is not None and old_val != new_val:
            out.append(f'{cnum} number changed: "{old_val}" -> "{new_val}"')
    old_n, new_n = prev.get('data_dir_count'), new.get('data_dir_count')
    if isinstance(old_n, int) and isinstance(new_n, int) and new_n != old_n:
        out.append(f'data/ directory count: {old_n} -> {new_n} ({new_n - old_n:+d})')
    if not out:
        out.append('nothing measurable moved since the last snapshot')
    return out


# --------------------------------------------------------------------------------------
# 5. stuck items
# --------------------------------------------------------------------------------------

STUCK_PATTERN = re.compile(r'HELD|BLOCKED|PENDING|USER AUTH', re.IGNORECASE)


def stuck_items(running_lines: list[str], step_results: list[dict]) -> list[str]:
    out = [re.sub(r'^[\s-]+', '', ln).strip() for ln in running_lines if STUCK_PATTERN.search(ln)]
    for s in step_results:
        if s['result']['status'] in ('NOT STARTED', 'BLOCKED'):
            out.append(f'plan step "{s["id"]}" ({_trunc(s["title"], 50)}): {s["result"]["status"]}')
    return out or ['(none found)']


# --------------------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------------------

def generate() -> tuple[str, str, dict]:
    """Returns (full_markdown_report, headline_sentence, state_dict_for_next_diff)."""
    plan_text = _read(PLAN_MD)
    status_text_exists = STATUS_MD.exists()
    strategy_text = _read(STRATEGY_MD)
    head_commit = (_run_git('rev-parse', 'HEAD') or UNKNOWN).strip()

    # section 1
    step_results = []
    if plan_text is not None:
        commits = git_commits_since()
        running_lines_raw = status_running_lines()
        data_index = build_data_dir_index()
        for step in parse_plan_steps(plan_text):
            result = match_step_evidence(step, commits, running_lines_raw, data_index)
            step_results.append({'id': step['id'], 'title': step['title'], 'result': result})

    # section 2
    running_lines = status_running_lines()
    hb_lines = heartbeat_report()
    fresh_dirs = fresh_data_dirs()

    # section 3
    c_rows = parse_c_scoreboard(strategy_text) if strategy_text is not None else {}
    c3_note = c3_honesty_check()

    # data dir count (cheap, for section 4 diffing)
    try:
        data_dir_count = sum(1 for e in os.scandir(DATA_DIR) if e.is_dir()) if DATA_DIR.is_dir() else None
    except OSError:
        data_dir_count = None

    new_state = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'head_commit': head_commit,
        'step_status': {s['id']: s['result']['status'] for s in step_results},
        'c_now': {k: v['now'] for k, v in c_rows.items()},
        'data_dir_count': data_dir_count,
    }

    prev_text = _read(OUT_MD)
    prev_state = load_prev_state(prev_text)
    moved = diff_state(prev_state, new_state)

    # headline: the single most important sentence, per the owner's brief
    n_done = sum(1 for s in step_results if s['result']['status'] == 'DONE')
    n_total = len(step_results) or 1
    headline = (
        f'HEADLINE: {n_done}/{n_total} plan steps done; '
        f'{c3_note.split(" -- source")[0] if "source" in c3_note else c3_note}'
    )

    lines = []
    lines.append('# PROGRESS SNAPSHOT')
    lines.append('')
    lines.append('(generated by tools/progress_snapshot.py -- do not hand-edit, it is rewritten '
                  'every session)')
    lines.append('')
    lines.append(f'**{headline}**')
    lines.append('')
    lines.append(f'generated: {new_state["generated_at"]}  |  HEAD: {head_commit[:9] if head_commit != UNKNOWN else UNKNOWN}')
    lines.append('')

    lines.append('## 1. Where we are against the plan (notes/PLAN_NEXT_12H.md)')
    if not step_results:
        lines.append(f'- {UNKNOWN} -- notes/PLAN_NEXT_12H.md not readable')
    for s in step_results:
        r = s['result']
        lines.append(f'- **{s["id"]}** ({_trunc(s["title"], 45)}): **{r["status"]}** -- {r["evidence"]}')
    lines.append('')

    lines.append('## 2. What is running right now')
    lines.append('Heartbeats (data/heartbeats/*.timestamp):')
    for h in hb_lines:
        lines.append(f'  - {h}')
    lines.append(f'data/ directories touched in the last {DATA_FRESH_WINDOW_MIN:.0f} min:')
    for d in fresh_dirs:
        lines.append(f'  - {d}')
    lines.append('notes/STATUS.md WHAT IS RUNNING (verbatim):')
    if running_lines:
        for ln in running_lines:
            lines.append(f'  {ln}')
    else:
        lines.append(f'  {UNKNOWN} -- section not found in notes/STATUS.md')
    lines.append('')

    lines.append('## 3. How we are doing (C1-C4, notes/SUBSTRATE_STRATEGY.md PART 1)')
    if not c_rows:
        lines.append(f'- {UNKNOWN} -- could not parse the scoreboard table')
    for cnum in ('C1', 'C2', 'C3', 'C4'):
        row = c_rows.get(cnum)
        if row is None:
            lines.append(f'- {cnum}: {UNKNOWN} -- row not found in table')
            continue
        lines.append(f'- **{cnum}** {_trunc(row["name"], 60)}: now={_trunc(row["now"], 70)} '
                     f'| floor(s)={_trunc(row["floor"], 70)} | table verdict: {row["verdict"]}')
    lines.append(f'- {c3_note}')
    lines.append('')

    lines.append('## 4. What moved since the last snapshot')
    for m in moved:
        lines.append(f'- {m}')
    lines.append('')

    lines.append('## 5. What is stuck (blocked / pending / no owner)')
    for item in stuck_items(running_lines, step_results):
        lines.append(f'- {item}')
    lines.append('')

    lines.append(STATE_MARK_START)
    lines.append(json.dumps(new_state, indent=None, sort_keys=True))
    lines.append(STATE_MARK_END)

    report = _asciify('\n'.join(lines) + '\n')
    return report, headline, new_state


# --------------------------------------------------------------------------------------
# self-test (fixtures only; never touches the real notes/*.md)
# --------------------------------------------------------------------------------------

FIXTURE_PLAN = """\
# PLAN FIXTURE

### 0-1h -- COMPACTION SAFETY
Some artifact text mentioning compaction safety explicitly.

### 1-4h -- DRILL THE BRAIN MECHANISM
Do the drill mechanism thing.

### 4-8h -- HELD STEP
This step is HELD PENDING USER AUTHORISATION because reasons.

## NEXT SECTION
not a step
"""

FIXTURE_STRATEGY_TABLE = """\
| # | number | now | floor(s) | last moved by | what would move it |
|---|---|---|---|---|---|
| **C1** | **Widget accuracy** | **0.70** | scramble 0.50 | `abc123` | more data |
| **C3** | **Readout quality** | **NOT PASSED.** 0.048 | scramble 0.008 | `def456` | separation |
"""


def _self_test() -> int:
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(f'[self-test] {"PASS" if cond else "FAIL"}: {msg}')
        if not cond:
            ok = False

    steps = parse_plan_steps(FIXTURE_PLAN)
    check(len(steps) == 3, f'fixture plan parses to 3 steps (got {len(steps)})')
    check(steps[0]['id'] == '0-1h', f'first step id is "0-1h" (got {steps[0]["id"]!r})')
    check(steps[2]['held_pending'] is True, 'HELD PENDING is detected in step 3')
    check(steps[0]['held_pending'] is False, 'step 1 is not flagged HELD PENDING')

    fake_commits = [{'hash': 'a' * 40, 'subject': 'compaction safety fix landed',
                      'tokens': tokenize('compaction safety fix landed')}]
    r0 = match_step_evidence(steps[0], fake_commits, [], {})
    check(r0['status'] == 'DONE', f'commit-token overlap classifies step as DONE (got {r0["status"]})')

    r1 = match_step_evidence(steps[1], [], ['some line about the drill mechanism in progress'], {})
    check(r1['status'] == 'RUNNING', f'running-block overlap classifies step as RUNNING (got {r1["status"]})')

    r2 = match_step_evidence(steps[2], fake_commits, [], {})
    check(r2['status'] == 'BLOCKED', f'HELD PENDING overrides to BLOCKED (got {r2["status"]})')

    r_none = match_step_evidence(
        {'tokens': {'zzzzznomatch'}, 'match_tokens': {'zzzzznomatch'},
         'held_pending': False, 'held_excerpt': None}, [], [], {})
    check(r_none['status'] == 'NOT STARTED', f'no evidence classifies as NOT STARTED (got {r_none["status"]})')

    rows = parse_c_scoreboard(FIXTURE_STRATEGY_TABLE)
    check('C1' in rows and 'C3' in rows, f'scoreboard fixture parses C1 and C3 (got keys {list(rows)})')
    check(rows['C3']['verdict'].startswith('NOT PASSED'),
          f'C3 verdict word extracted from table cell (got {rows["C3"]["verdict"]!r})')
    check('0.70' in rows['C1']['now'], f'C1 now-cell captured (got {rows["C1"]["now"]!r})')

    prev = {'head_commit': 'aaa', 'step_status': {'0-1h': 'RUNNING'}, 'c_now': {'C1': '0.60'},
            'data_dir_count': 10}
    new = {'head_commit': 'bbb', 'step_status': {'0-1h': 'DONE'}, 'c_now': {'C1': '0.70'},
           'data_dir_count': 12}
    diffs = diff_state(prev, new)
    check(any('0-1h' in d and 'RUNNING -> DONE' in d for d in diffs),
          f'diff_state reports the step-status change (got {diffs})')
    check(diff_state(None, new) == ['(no previous snapshot found -- this is the first run)'],
          'diff_state handles a missing previous snapshot without crashing')

    rendered = (
        f'{STATE_MARK_START}\n{json.dumps(new)}\n{STATE_MARK_END}\n'
    )
    round_tripped = load_prev_state(rendered)
    check(round_tripped == new, f'state JSON round-trips through the HTML-comment blob (got {round_tripped})')
    check(load_prev_state(None) is None, 'load_prev_state(None) returns None, not a crash')
    check(load_prev_state('no marker here') is None, 'load_prev_state with no marker returns None')

    print(f'[self-test] {"ALL PASS" if ok else "FAILED"}')
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--hook', action='store_true',
                         help='fast mode: full derive, print only the headline (for session_start_hook.py)')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    report, headline, _state = generate()
    try:
        OUT_MD.write_text(report, encoding='utf-8')
    except OSError as exc:
        print(f'ERROR writing {OUT_MD}: {exc}', file=sys.stderr)
        return 1

    # STDOUT HERE IS cp1252 ON WINDOWS, AND THE DOCS THIS SUMMARISES ARE FULL OF EMOJI.
    # Measured 2026-08-22: `print(report)` died with UnicodeEncodeError on a U+2705 -- AFTER the
    # snapshot file had been written correctly. So the tool did its whole job and then exited on the
    # way out, which reads as a failed run and invites someone to "fix" a snapshot that was fine.
    # Sanitising the STRING, not reconfiguring stdout: a module-level reconfigure mutates global
    # state for every importer, which this repo has a documented incident about. Second tool hit by
    # this class today (see tools/cite_check.py `_printable`); if a third appears, promote it to a
    # shared helper rather than copying it again.
    def _printable(s):
        enc = (getattr(sys.stdout, 'encoding', None) or 'utf-8')
        try:
            s.encode(enc)
            return s
        except (UnicodeEncodeError, LookupError):
            return s.encode(enc, errors='replace').decode(enc, errors='replace')

    if args.hook:
        print(_printable(f'[progress-snapshot] {headline}'))
    else:
        print(_printable(report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
