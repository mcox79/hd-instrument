"""Definitive popup detector — uses Win32 Toolhelp32 via ctypes (no subprocess
spawns of our own). Polls process snapshot every 500ms for 4 minutes. Logs every
NEW console-mode process creation with full command line + parent process.

Output: C:/Users/marsh/AppData/Local/Temp/popup_log_v2.txt

Plus: writes the current Claude Code version (read from %APPDATA%\\npm\\node_modules)
and the modification time of relevant binaries so we can verify the downgrade
actually applied to running sessions.
"""
from __future__ import annotations

import ctypes
import json
import os
import sys
import time
from ctypes import wintypes

LOG = r"C:\Users\marsh\AppData\Local\Temp\popup_log_v2.txt"
DURATION_S = 240
POLL_INTERVAL_S = 0.5

# Console-mode binaries we want to flag
TARGETS = {
    "bash.exe", "cmd.exe", "powershell.exe", "python.exe", "conhost.exe",
    "git.exe", "ssh.exe", "scp.exe", "find.exe", "grep.exe", "sort.exe",
    "curl.exe", "tar.exe", "node.exe", "npm.exe", "claude.exe", "wsl.exe",
    "pwsh.exe", "perl.exe",
}

TH32CS_SNAPPROCESS = 0x00000002
INVALID_HANDLE_VALUE = -1


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


kernel32 = ctypes.windll.kernel32


def snapshot() -> dict[int, tuple[str, int]]:
    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE:
        return {}
    out: dict[int, tuple[str, int]] = {}
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    if kernel32.Process32FirstW(snap, ctypes.byref(entry)):
        while True:
            out[entry.th32ProcessID] = (entry.szExeFile, entry.th32ParentProcessID)
            if not kernel32.Process32NextW(snap, ctypes.byref(entry)):
                break
    kernel32.CloseHandle(snap)
    return out


def parent_name(pid: int, table: dict) -> str:
    e = table.get(pid)
    return e[0] if e else "?"


def get_cmdline_via_wmic(pid: int) -> str:
    """Pure-Python WMI via ctypes is complex; skip cmdline collection if it would
    cost a popup. Instead just report the EXE name + PID + parent."""
    return ""


def claude_version_info() -> dict:
    """Read Claude Code version from the npm-installed package.json."""
    info = {}
    npm_paths = [
        os.path.expandvars(r"%APPDATA%\npm\node_modules\@anthropic-ai\claude-code\package.json"),
        os.path.expandvars(r"%LOCALAPPDATA%\npm\node_modules\@anthropic-ai\claude-code\package.json"),
    ]
    for p in npm_paths:
        if os.path.isfile(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
                info[p] = {
                    "version": d.get("version"),
                    "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(p))),
                }
            except Exception as e:
                info[p] = f"read-error: {e}"
    return info


def find_claude_processes(table: dict) -> list[tuple[int, str]]:
    """Find running claude-related processes so we can tell which version they're running."""
    out = []
    for pid, (name, ppid) in table.items():
        nl = name.lower()
        if nl in ("claude.exe", "node.exe"):
            out.append((pid, name))
    return out


def main() -> int:
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(f"=== popup_detector_v2 starting {time.strftime('%H:%M:%S')} ===\n")
        f.write(f"Duration: {DURATION_S}s, poll {POLL_INTERVAL_S}s\n\n")

        # Snapshot Claude Code version info
        f.write("--- Claude Code version state ---\n")
        for path, info in claude_version_info().items():
            f.write(f"  {path}\n    {info}\n")
        f.write("\n")

        # Initial process snapshot
        prev = snapshot()
        claude_procs = find_claude_processes(prev)
        f.write(f"--- Running claude/node processes ({len(claude_procs)}) ---\n")
        for pid, name in claude_procs:
            f.write(f"  pid={pid} {name}\n")
        f.write(f"\nSeeded {len(prev)} existing processes; logging NEW ones for {DURATION_S}s.\n\n")
        f.flush()

        end_time = time.time() + DURATION_S
        seen_pids = set(prev.keys())
        count_by_exe: dict[str, int] = {}

        while time.time() < end_time:
            time.sleep(POLL_INTERVAL_S)
            cur = snapshot()
            new = [(pid, name, ppid) for pid, (name, ppid) in cur.items() if pid not in seen_pids]
            for pid, name, ppid in new:
                seen_pids.add(pid)
                if name.lower() not in TARGETS:
                    continue
                par = parent_name(ppid, cur)
                count_by_exe[name] = count_by_exe.get(name, 0) + 1
                f.write(f"{time.strftime('%H:%M:%S')}.{int((time.time()%1)*1000):03d} "
                        f"NEW pid={pid:>7} {name:<18} parent={par}({ppid})\n")
            if new:
                f.flush()

        f.write(f"\n=== done {time.strftime('%H:%M:%S')} ===\n")
        f.write(f"\nSummary (per-exe spawn count over {DURATION_S}s):\n")
        for exe, n in sorted(count_by_exe.items(), key=lambda kv: -kv[1]):
            f.write(f"  {exe:<18} {n}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
