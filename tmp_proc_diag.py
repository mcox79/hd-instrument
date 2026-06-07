import subprocess, json, re, sys
# Use wmic to grab process details for python.exe
raw = subprocess.run(
    ["wmic", "process", "where", "name='python.exe'",
     "get", "processid,parentprocessid,executablepath,commandline", "/format:list"],
    capture_output=True, text=True, errors='replace'
).stdout
# wmic outputs records separated by blank lines; each line is Key=Value
records = []
cur = {}
for line in raw.splitlines():
    line = line.strip()
    if not line:
        if cur:
            records.append(cur); cur = {}
        continue
    if '=' in line:
        k, v = line.split('=', 1)
        cur[k.strip()] = v.strip()
if cur:
    records.append(cur)

print(f"{'PID':>7s}  {'PPID':>7s}  {'EXE':<60s}  CMDLINE")
print('-' * 140)
for r in records:
    pid = r.get('ProcessId', '?')
    ppid = r.get('ParentProcessId', '?')
    exe = r.get('ExecutablePath', '?')
    cmd = r.get('CommandLine', '?')
    # Truncate exe path to its parent dir tail
    exe_tail = '...' + exe[-57:] if len(exe) > 60 else exe
    cmd_tail = cmd if len(cmd) <= 70 else cmd[:67] + '...'
    print(f"{pid:>7s}  {ppid:>7s}  {exe_tail:<60s}  {cmd_tail}")
