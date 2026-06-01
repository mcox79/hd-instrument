# Remote Bridge Recovery

Last updated: 2026-05-27

## What the bridge is

Four processes must be alive for the pipeline to run end-to-end after a reboot:

| Component | Where | Process / Launcher | Task name | Trigger | Run As |
|---|---|---|---|---|---|
| Remote emitter | marsh@home | `pythonw.exe remote_state_emitter.py` | `hd_remote_state_emitter` | ONLOGON | marsh |
| GPU runner | marsh@home | `gpu_runner_0_launcher.bat` | `hd_gpu_runner_0` | ONLOGON | marsh |
| CPU runner | marsh@home | `cpu_runner_0_launcher.bat` | `hd_cpu_runner_0` | ONLOGON | marsh |
| Local watchdog | local laptop | `pythonw.exe heartbeat_watchdog.py` | `hd_orchestrator_watchdog` | ONLOGON | marsh |

All four are registered as Windows Scheduled Tasks with **ONLOGON** triggers, so they restart automatically after any reboot as soon as the user logs in.  No manual intervention needed in the normal case.

> **Hardened 2026-05-27**: `hd_cpu_runner_0` and `hd_gpu_runner_0` were previously One-Time-Only / SYSTEM. Re-created with ONLOGON + RunLevel=Limited + Run As marsh via:
> `schtasks /Create /TN "hd_cpu_runner_0" /SC ONLOGON /TR "C:\dev\hd-instrument\cpu_runner_0_launcher.bat" /RL LIMITED /RU marsh /F`
> `schtasks /Create /TN "hd_gpu_runner_0" /SC ONLOGON /TR "C:\dev\hd-instrument\gpu_runner_0_launcher.bat" /RL LIMITED /RU marsh /F`

---

## Normal auto-recovery (reboot)

After either machine reboots and the user logs in, the relevant schtask fires automatically.  No action required.

---

## Manual restart (if a process died without rebooting)

### Remote emitter (on marsh@home)

```
ssh marsh@home "schtasks /Run /TN hd_remote_state_emitter"
```

Verify it started:
```
ssh marsh@home "schtasks /Query /TN hd_remote_state_emitter /FO LIST /V"
```
Expected: `Status: Running`

### Remote GPU runner (on marsh@home)

```
ssh marsh@home "schtasks /Run /TN hd_gpu_runner_0"
```

### Remote CPU runner (on marsh@home)

```
ssh marsh@home "schtasks /Run /TN hd_cpu_runner_0"
```

### Local heartbeat watchdog (on this laptop)

```powershell
Start-ScheduledTask -TaskName hd_orchestrator_watchdog
```

Or from a regular shell:
```
schtasks /Run /TN hd_orchestrator_watchdog
```

Verify:
```powershell
Get-ScheduledTask -TaskName hd_orchestrator_watchdog | Select-Object State
```
Expected: `State: Running`

---

## Re-register tasks from scratch (if schtasks are deleted)

### Remote (run on marsh@home or via SSH):

Re-register all three remote tasks:

```
ssh marsh@home "schtasks /Create /TN hd_remote_state_emitter /SC ONLOGON /TR \"C:\dev\hd-instrument\.venv\Scripts\pythonw.exe C:\dev\hd-instrument\tools\orchestrator\remote_state_emitter.py\" /RL LIMITED /RU marsh /F"
ssh marsh@home "schtasks /Create /TN hd_cpu_runner_0 /SC ONLOGON /TR \"C:\dev\hd-instrument\cpu_runner_0_launcher.bat\" /RL LIMITED /RU marsh /F"
ssh marsh@home "schtasks /Create /TN hd_gpu_runner_0 /SC ONLOGON /TR \"C:\dev\hd-instrument\gpu_runner_0_launcher.bat\" /RL LIMITED /RU marsh /F"
```

Or use the install script for the emitter only:
```
ssh marsh@home "powershell -ExecutionPolicy Bypass -File C:\dev\hd-instrument\tools\orchestrator\install_remote_emitter_schtask.ps1"
```

### Local (run in PowerShell on this laptop):

```powershell
# Register hd_orchestrator_watchdog with ONLOGON + pythonw.exe (no console window)
$taskName = "hd_orchestrator_watchdog"
$pythonw  = "D:\AI\hd-instrument\.venv\Scripts\pythonw.exe"
$script   = "D:\AI\hd-instrument\tools\orchestrator\heartbeat_watchdog.py"
$action   = New-ScheduledTaskAction -Execute $pythonw -Argument $script -WorkingDirectory "D:\AI\hd-instrument"
$trigger  = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 2) -StartWhenAvailable -RunOnlyIfNetworkAvailable:$false
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "hd-instrument heartbeat watchdog - ONLOGON, no console window"
Start-ScheduledTask -TaskName $taskName
```

---

## Design notes

- Remote emitter: `pythonw.exe` (no console window, avoids cmd popup on marsh@home).
- Local puller: `pythonw.exe` (no console window, eliminates the periodic cmd flash on the laptop).
- All `subprocess.run` calls inside `heartbeat_watchdog.py` use `creationflags=CREATE_NO_WINDOW` (0x08000000) to prevent ssh/scp child processes from creating console windows.
- Remote emitter schtask previously used a "One Time Only, Minute" trigger (created 2026-05-26 original install); that trigger does NOT survive reboot. Replaced with ONLOGON on 2026-05-26.
- Runner schtasks (`hd_cpu_runner_0`, `hd_gpu_runner_0`) were One-Time-Only / SYSTEM from the runner-cleanup agent (2026-05-27 early morning). Re-hardened to ONLOGON / marsh / Limited on 2026-05-27. The bat launchers internally use `python.exe` (not `pythonw`) because stdout is redirected to log files; no console window appears.
- Verify all four tasks post-reboot: `ssh marsh@home "schtasks /Query /TN hd_cpu_runner_0 /V /FO LIST | findstr Schedule"` should show `At logon time`.
