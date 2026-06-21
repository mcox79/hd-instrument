"""DEPRECATED 2026-06-21 — ABANDONED (segfaults).

Original intent: kill running monitor_arm.sh wrappers without killing inner
notes_monitor.sh. The ctypes ReadProcessMemory path to get a process's
command line is fragile across Windows builds; this script segfaults on
this machine (Windows 11 26200). Don't use as-is.

The bash-monitor crash-loop popup pattern was addressed via:
  - monitor_arm.sh 5s->60s restart sleep cap (commit 61edb5cb)
  - Python ports tools/monitor_arm.py + tools/notes_monitor.py (commit 99f8957c-ish)
  - Sessions migrating to the Python pattern per CLAUDE.md canonical invocation

If you need this in the future, prefer psutil (clean cross-version API)
over the ctypes Toolhelp/NtQueryInformationProcess dance.

DO NOT RUN.
"""
import sys
import ctypes
from ctypes import wintypes

# Use Windows API directly (no subprocess spawn).
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

# Snapshot of running processes via Toolhelp.
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
psapi = ctypes.windll.psapi

CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.restype = wintypes.HANDLE
Process32FirstW = kernel32.Process32FirstW
Process32NextW = kernel32.Process32NextW
CloseHandle = kernel32.CloseHandle


def list_bash_pids():
    snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == INVALID_HANDLE_VALUE:
        return []
    entry = PROCESSENTRY32W()
    entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
    pids = []
    if Process32FirstW(snap, ctypes.byref(entry)):
        while True:
            if entry.szExeFile.lower() == "bash.exe":
                pids.append(entry.th32ProcessID)
            if not Process32NextW(snap, ctypes.byref(entry)):
                break
    CloseHandle(snap)
    return pids


def get_command_line(pid: int) -> str | None:
    """Get full command line for a PID via NtQueryInformationProcess. Returns None if denied."""
    OpenProcess = kernel32.OpenProcess
    OpenProcess.restype = wintypes.HANDLE
    h = OpenProcess(0x0410, False, pid)  # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
    if not h:
        return None
    try:
        ntdll = ctypes.windll.ntdll

        class UNICODE_STRING(ctypes.Structure):
            _fields_ = [
                ("Length", wintypes.USHORT),
                ("MaximumLength", wintypes.USHORT),
                ("Buffer", wintypes.LPWSTR),
            ]

        class PROCESS_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("Reserved1", ctypes.c_void_p),
                ("PebBaseAddress", ctypes.c_void_p),
                ("Reserved2", ctypes.c_void_p * 2),
                ("UniqueProcessId", ctypes.c_void_p),
                ("Reserved3", ctypes.c_void_p),
            ]

        pbi = PROCESS_BASIC_INFORMATION()
        ret_len = wintypes.ULONG(0)
        status = ntdll.NtQueryInformationProcess(
            h, 0, ctypes.byref(pbi), ctypes.sizeof(pbi), ctypes.byref(ret_len)
        )
        if status != 0 or not pbi.PebBaseAddress:
            return None

        # PEB.ProcessParameters offset = 0x20 (x64)
        peb_proc_params_offset = 0x20
        proc_params_addr = ctypes.c_void_p()
        bytes_read = ctypes.c_size_t(0)
        peb_int = int(pbi.PebBaseAddress) if pbi.PebBaseAddress else 0
        if not peb_int or not kernel32.ReadProcessMemory(
            h,
            ctypes.c_void_p(peb_int + peb_proc_params_offset),
            ctypes.byref(proc_params_addr),
            ctypes.sizeof(proc_params_addr),
            ctypes.byref(bytes_read),
        ):
            return None

        # RTL_USER_PROCESS_PARAMETERS.CommandLine offset = 0x70 (x64)
        cmdline_offset = 0x70
        cmdline_unicode = UNICODE_STRING()
        if not kernel32.ReadProcessMemory(
            h,
            ctypes.c_void_p(proc_params_addr.value + cmdline_offset),
            ctypes.byref(cmdline_unicode),
            ctypes.sizeof(cmdline_unicode),
            ctypes.byref(bytes_read),
        ):
            return None

        if cmdline_unicode.Length == 0:
            return ""
        buf = ctypes.create_unicode_buffer(cmdline_unicode.Length // 2)
        if not kernel32.ReadProcessMemory(
            h,
            cmdline_unicode.Buffer,
            buf,
            cmdline_unicode.Length,
            ctypes.byref(bytes_read),
        ):
            return None
        return buf.value
    finally:
        CloseHandle(h)


def main():
    bash_pids = list_bash_pids()
    print(f"Found {len(bash_pids)} bash.exe processes total")

    wrappers = []
    for pid in bash_pids:
        cmd = get_command_line(pid)
        if cmd and "monitor_arm.sh" in cmd:
            wrappers.append((pid, cmd))

    print(f"Found {len(wrappers)} monitor_arm.sh wrappers:")
    for pid, cmd in wrappers:
        print(f"  pid={pid} | {cmd[:120]}")

    if not wrappers:
        print("Nothing to kill.")
        return

    print()
    print("Killing wrappers (leaves inner notes_monitor.sh alive as orphans):")
    OpenProcess = kernel32.OpenProcess
    OpenProcess.restype = wintypes.HANDLE
    TerminateProcess = kernel32.TerminateProcess
    for pid, _ in wrappers:
        h = OpenProcess(PROCESS_TERMINATE, False, pid)
        if not h:
            print(f"  pid={pid} FAILED to open (access denied?)")
            continue
        ok = TerminateProcess(h, 1)
        CloseHandle(h)
        print(f"  pid={pid} {'killed' if ok else 'FAILED to terminate'}")


if __name__ == "__main__":
    main()
