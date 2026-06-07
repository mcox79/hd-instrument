import subprocess
raw = subprocess.run(
    ["wmic", "process", "where", "name='python.exe'",
     "get", "processid,parentprocessid,executablepath,commandline", "/format:list"],
    capture_output=True, text=True, errors='replace'
).stdout
# Strip CR + split on \n; group records by empty-line delimiter
lines = [l.rstrip() for l in raw.replace('\r','').split('\n')]
records, cur = [], {}
for l in lines:
    if not l.strip():
        if cur:
            records.append(cur); cur = {}
        continue
    if '=' in l:
        k, v = l.split('=', 1)
        cur[k.strip()] = v.strip()
if cur:
    records.append(cur)

print(f"Total records: {len(records)}")
print()
print(f"{'PID':>7}  {'PPID':>7}  {'EXE_TYPE':<8}  CMDLINE")
print('-' * 110)
for r in records:
    pid = r.get('ProcessId','?')
    ppid = r.get('ParentProcessId','?')
    exe = r.get('ExecutablePath','')
    cmd = r.get('CommandLine','')
    exe_type = '.venv' if '.venv' in exe else ('AppData' if 'AppData' in exe else '?')
    cmd_short = cmd[:80] if cmd else ''
    print(f"{pid:>7}  {ppid:>7}  {exe_type:<8}  {cmd_short}")
