import json, os, sys
from collections import Counter, defaultdict
from datetime import datetime

path = r"C:/Users/marsh/.claude/projects/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a.jsonl"
OFFSET = 2829654968  # binary-search-located start of last-2-weeks window (>= 2026-07-29T00:00:00Z)
CUTOFF = "2026-07-29T00:00:00.000Z"

agent_calls = []
main_tool_counts = Counter()
kb_keywords = ["foundation", "fact_store", "gap_detector", "gap_driven_reader",
               "reading_grounding", "director_kb_query.py", "substrate_query.sh"]
kb_command_samples = []
kb_keyword_counts = Counter()
director_kb_query_count = 0
substrate_query_count = 0

prev_ts = None
gaps = []
tool_result_sizes = []

seen_uuids = set()
raw_line_count = 0
deduped_line_count = 0
parse_errors = 0
first_ts_seen = None
last_ts_seen = None

edit_write_experiments = []
real_smoke_runs = []

import re
SMOKE_RE = re.compile(r'experiments/[A-Za-z0-9_]+\.py\s+--(smoke|self-test)')

def ts_to_epoch(ts):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")

with open(path, 'r', encoding='utf-8', errors='replace') as f:
    f.seek(OFFSET)
    f.readline()
    for raw in f:
        raw = raw.strip()
        if not raw:
            continue
        raw_line_count += 1
        try:
            d = json.loads(raw)
        except Exception:
            parse_errors += 1
            continue

        ts = d.get('timestamp')
        if ts and ts < CUTOFF:
            continue

        u = d.get('uuid')
        if u:
            if u in seen_uuids:
                continue
            seen_uuids.add(u)

        deduped_line_count += 1

        if ts:
            if first_ts_seen is None:
                first_ts_seen = ts
            last_ts_seen = ts
            try:
                cur_epoch = ts_to_epoch(ts)
                if prev_ts is not None:
                    delta = (cur_epoch - prev_ts).total_seconds()
                    if delta > 0:
                        gaps.append((delta, ts))
                prev_ts = cur_epoch
            except Exception:
                pass

        dtype = d.get('type')

        if dtype == 'assistant':
            msg = d.get('message', {})
            content = msg.get('content', [])
            if isinstance(content, list):
                for b in content:
                    if not isinstance(b, dict):
                        continue
                    if b.get('type') == 'tool_use':
                        name = b.get('name', 'UNKNOWN')
                        main_tool_counts[name] += 1
                        inp = b.get('input', {}) or {}

                        if name == 'Agent':
                            prompt = inp.get('prompt', '') or ''
                            agent_calls.append({
                                'subagent_type': inp.get('subagent_type', 'UNSPECIFIED'),
                                'model': inp.get('model'),
                                'run_in_background': inp.get('run_in_background'),
                                'prompt_len': len(prompt),
                                'ts': ts,
                            })

                        cmd_text = inp.get('command', '') if name in ('Bash', 'PowerShell') else ''
                        file_path_text = inp.get('file_path', '') or ''
                        combined = (cmd_text or '') + ' ' + file_path_text
                        low = combined.lower()
                        for kw in kb_keywords:
                            if kw.lower() in low:
                                kb_keyword_counts[kw] += 1
                                if cmd_text and len(kb_command_samples) < 60:
                                    kb_command_samples.append((ts, name, cmd_text.strip()[:400]))
                        if 'director_kb_query.py' in low:
                            director_kb_query_count += 1
                        if 'substrate_query.sh' in low:
                            substrate_query_count += 1

                        if name in ('Edit', 'Write'):
                            fp = file_path_text.replace('\\', '/')
                            if '/experiments/' in fp and fp.endswith('.py'):
                                edit_write_experiments.append((ts, name, fp))
                        if name == 'Bash' and cmd_text and SMOKE_RE.search(cmd_text):
                            real_smoke_runs.append((ts, cmd_text.strip()[:200]))

        elif dtype == 'user':
            msg = d.get('message', {})
            content = msg.get('content')
            if isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get('type') == 'tool_result':
                        c = b.get('content')
                        size = 0
                        if isinstance(c, str):
                            size = len(c)
                        elif isinstance(c, list):
                            for cc in c:
                                if isinstance(cc, dict) and cc.get('type') == 'text':
                                    size += len(cc.get('text', '') or '')
                        tool_result_sizes.append((size, ts, b.get('tool_use_id')))

out = {}
out['raw_line_count_in_window'] = raw_line_count
out['deduped_line_count_in_window'] = deduped_line_count
out['parse_errors'] = parse_errors
out['first_ts_seen'] = first_ts_seen
out['last_ts_seen'] = last_ts_seen
out['total_agent_calls'] = len(agent_calls)

by_subtype = Counter(a['subagent_type'] for a in agent_calls)
out['by_subagent_type'] = by_subtype.most_common()

model_specified = sum(1 for a in agent_calls if a.get('model'))
out['model_specified_count'] = model_specified
out['model_unspecified_count'] = len(agent_calls) - model_specified
model_values = Counter(a.get('model') for a in agent_calls if a.get('model'))
out['model_value_counts'] = model_values.most_common()

rib_true = sum(1 for a in agent_calls if a.get('run_in_background') is True)
rib_false = sum(1 for a in agent_calls if a.get('run_in_background') is False)
rib_unset = len(agent_calls) - rib_true - rib_false
out['run_in_background'] = {'true': rib_true, 'false': rib_false, 'unset': rib_unset}

plens = sorted(a['prompt_len'] for a in agent_calls)
if plens:
    n = len(plens)
    out['prompt_len'] = {
        'min': plens[0], 'max': plens[-1],
        'median': plens[n // 2],
        'p25': plens[n // 4], 'p75': plens[(3 * n) // 4],
        'mean': sum(plens) / n,
    }
else:
    out['prompt_len'] = None

# per-subagent-type prompt length median
per_sub_plen = defaultdict(list)
for a in agent_calls:
    per_sub_plen[a['subagent_type']].append(a['prompt_len'])
out['prompt_len_by_subtype'] = {
    k: {'n': len(v), 'median': sorted(v)[len(v)//2], 'min': min(v), 'max': max(v)}
    for k, v in per_sub_plen.items()
}

out['main_tool_counts'] = main_tool_counts.most_common()
total_main_tool_calls = sum(main_tool_counts.values())
out['total_main_tool_calls'] = total_main_tool_calls
out['total_agent_dispatch_calls'] = main_tool_counts.get('Agent', 0)
out['non_agent_main_tool_calls'] = total_main_tool_calls - main_tool_counts.get('Agent', 0)

out['kb_keyword_counts'] = kb_keyword_counts.most_common()
out['director_kb_query_count'] = director_kb_query_count
out['substrate_query_count'] = substrate_query_count
out['kb_command_samples'] = kb_command_samples[:15]

out['edit_write_experiments_from_main'] = edit_write_experiments
out['real_smoke_runs_from_main'] = real_smoke_runs

gaps_sorted = sorted(gaps, key=lambda x: -x[0])[:12]
out['top_gaps'] = gaps_sorted

# dedupe tool_result_sizes by tool_use_id too (avoid double count from dup lines)
seen_tr = set()
tr_dedup = []
for size, ts_, tid in tool_result_sizes:
    key = tid
    if key and key in seen_tr:
        continue
    if key:
        seen_tr.add(key)
    tr_dedup.append((size, ts_, tid))
tr_sorted = sorted(tr_dedup, key=lambda x: -x[0])[:12]
out['top_tool_results'] = tr_sorted
out['tool_result_count_raw'] = len(tool_result_sizes)
out['tool_result_count_dedup'] = len(tr_dedup)

with open(r"D:/AI/hd-instrument/notes/_forensics_raw_output.json", 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, default=str)

print("DONE. raw_lines:", raw_line_count, "deduped:", deduped_line_count, "parse_errors:", parse_errors)
print("first_ts:", first_ts_seen, "last_ts:", last_ts_seen)
print("total agent calls (deduped):", len(agent_calls))
