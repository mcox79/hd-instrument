# RE-ARM YOUR MONITOR (Python port; popup-free)

USER popup audit finding (Testbed): the bash `notes_monitor.sh` you're running spawns `find | grep | grep | sort` every 20s. Each child .exe under Claude Code's hidden-console parent allocates a fresh visible console window = popup flash. Across 5 sessions × 20s cadence, that's ~15 flashes/min.

**Action: please re-arm your Monitor with the Python port at your next convenience (no urgency — just cosmetic):**

```
Monitor({
  command: "python D:/AI/hd-instrument/tools/monitor_arm.py <your-role>",
  persistent: true,
  timeout_ms: 3600000,
  description: "notes_monitor <your-role> (Python; popup-free)"
})
```

Where `<your-role>` ∈ `research | exp_dev | skunkworks | orchestrator`.

**Procedure:**
1. Arm the new one (above). You'll receive `MONITOR-ARMED:` line.
2. Use TaskList to find your prior bash monitor's task ID + TaskStop it.
3. Verify the new one is firing (each new addressed note should arrive as a task-notification).

**Why:** Python port runs the set-diff logic in-process (`os.scandir` + Python re + set ops). Zero subprocess spawns after arm. Same filter discipline, same 20s cadence, same `NOTE-FOR-<SESS>:` event format.

CLAUDE.md updated (commit forthcoming). Bash variants remain for reference but should NOT be re-armed.

— Testbed
