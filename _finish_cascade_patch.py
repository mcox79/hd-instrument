"""Finish the cascade-recovery patch: inject record_outcome calls."""
from pathlib import Path

p = Path(r"C:\dev\hd-instrument\experiments\run_overnight_queue.py")
src = p.read_text()

# Inject record_outcome before both 'return "completed"' and 'return "failed"' in run_one
# Patterns from line inspection:
src = src.replace(
    'log(f"DONE {name} in {dt:.1f}s (exit 0)")',
    'log(f"DONE {name} in {dt:.1f}s (exit 0)")\n        record_outcome(0)'
)
src = src.replace(
    'log(f"FAIL {name} exit={result.returncode} after {dt:.1f}s")',
    'log(f"FAIL {name} exit={result.returncode} after {dt:.1f}s")\n        record_outcome(result.returncode)'
)

# Make sure import time is present (it should be already)
if "import time" not in src.split("def")[0]:
    src = src.replace("import json", "import json\nimport time", 1)

p.write_text(src)
print(f"Finished cascade patch. Calls to record_outcome injected.")
