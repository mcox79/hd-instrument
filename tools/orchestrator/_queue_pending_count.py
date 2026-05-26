"""Small helper to print pending+running counts for queue.json files on remote."""
import json
import sys

if len(sys.argv) < 2:
    print("usage: _queue_pending_count.py <queue.json>...", file=sys.stderr)
    sys.exit(2)

for path in sys.argv[1:]:
    with open(path) as f:
        data = json.load(f)
    exps = data.get("experiments", data) if isinstance(data, dict) else data
    pending = [e for e in exps if e.get("status") in ("pending", "running")]
    print(f"=== {path}: pending+running = {len(pending)} ===")
    for e in pending:
        print(f"  {e.get('name', '?')}  status={e.get('status', '?')}  prereg={e.get('prereg', '?')}")
