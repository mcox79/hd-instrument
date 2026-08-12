import json, re

path = r"C:/Users/marsh/.claude/projects/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a.jsonl"
OFFSET = 2829654968
CUTOFF = "2026-07-29T00:00:00.000Z"

edit_write_experiments = []
real_smoke_runs = []
queue_add_direct = []

with open(path, 'r', encoding='utf-8', errors='replace') as f:
    f.seek(OFFSET)
    f.readline()
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        ts = d.get('timestamp')
        if ts and ts < CUTOFF:
            continue
        if d.get('type') != 'assistant':
            continue
        msg = d.get('message', {})
        content = msg.get('content', [])
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict) or b.get('type') != 'tool_use':
                continue
            name = b.get('name')
            inp = b.get('input', {}) or {}
            if name in ('Edit', 'Write'):
                fp = (inp.get('file_path') or '')
                fp = fp.replace('\\', '/')
                if '/experiments/' in fp and fp.endswith('.py'):
                    edit_write_experiments.append((ts, name, fp))
            if name == 'Bash':
                cmd = inp.get('command', '') or ''
                if re.search(r'experiments/[A-Za-z0-9_]+\.py\s+--(smoke|self-test)', cmd):
                    real_smoke_runs.append((ts, cmd.strip()[:200]))
                if 'queue_add.sh' in cmd and ('ssh' in cmd.lower() or 'scp' in cmd.lower() or './tools/orchestrator/queue_add.sh' in cmd):
                    queue_add_direct.append((ts, cmd.strip()[:200]))

print("EDIT/WRITE to experiments/*.py from main thread:", len(edit_write_experiments))
for x in edit_write_experiments[:10]:
    print(x)
print()
print("REAL smoke/self-test executions from main thread:", len(real_smoke_runs))
for x in real_smoke_runs[:15]:
    print(x)
print()
print("direct queue_add.sh invocations from main thread:", len(queue_add_direct))
for x in queue_add_direct[:10]:
    print(x)
