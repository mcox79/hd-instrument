"""One-shot: remove a pending entry from a queue.json by anchor name."""
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("usage: remove_queue_entry.py <queue.json-path> <anchor-name>", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    target = sys.argv[2]
    with open(path) as f:
        d = json.load(f)
    exps = d.get("experiments", [])
    removed = []
    remaining = []
    for x in exps:
        if x.get("name") == target and x.get("status") == "pending":
            removed.append(x.get("name"))
        else:
            remaining.append(x)
    d["experiments"] = remaining
    with open(path, "w") as f:
        json.dump(d, f, indent=2)
    print(f"removed: {removed}")
    print(f"remaining count: {len(remaining)}")
    pending = [x.get("name") for x in remaining if x.get("status") == "pending"]
    print(f"remaining pending: {pending[:5]}")

if __name__ == "__main__":
    main()
