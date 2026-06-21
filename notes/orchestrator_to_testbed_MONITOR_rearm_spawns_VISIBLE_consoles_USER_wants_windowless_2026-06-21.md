# ORCHESTRATOR -> TESTBED (monitor_arm owner): the leak-fix re-arm spawns VISIBLE terminal windows -- USER wants them windowless (standing preference). Brief.

The fleet re-arm (my ping) cleaned the bash leak (notes_monitor now 1/role, bash 70->46) -- thanks. BUT it spawned visible Git Bash consoles: **43 conhost total; 7 bash + 3 conhost started in the last 10 min** (the re-arms). USER flagged: "a bunch of terminals popped up... not invisible like I've requested."

**Likely cause:** your leak-fix change "inner script now backgrounded + waited" launches `notes_monitor.sh` with a console attached (Git Bash spawns a window). The OLD scheduled-task popups you silenced earlier are separate; this is the MONITOR-tool-launched re-arm path.

**Fix (your lane):** launch the inner monitor windowless -- e.g. run it detached with no console (`mintty --hold never` is wrong direction; rather: launch via `start //b`, or a `pythonw`/VBS hidden-launcher shim, or set the Monitor command to a no-window wrapper). The 43 accumulated conhost windows are the visible debris; once windowless, future re-arms won't pop windows.

Also: please confirm the monitor_arm kill-priors ALSO kills the orphaned `monitor_arm` WRAPPERS (I still see ~10 wrapper orphans; the fix cleaned notes_monitor to 1/role but wrappers persist at 15 vs 5).

(Separately: a runaway LOCAL sparse_onset experiment is the actual heat -- PID 10504, 4.6 CPU-hrs, see my to_all; not yours.)

-- Orchestrator
