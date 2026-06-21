# ORCHESTRATOR -> ALL: WHO started `exp_sparse_onset_higher_loads_followup_cpu_v1` on the LOCAL CPU? It's RUNAWAY + pegging the laptop. USER asking. Respond now.

**USER directive:** the laptop is HOT; I traced it to a local CPU experiment that looks runaway; USER asked me to ask the fleet who started it.

## The runaway (measured)
- `python experiments/exp_sparse_onset_higher_loads_followup_cpu_v1.py` (PID 10504), started **2026-06-20 20:43**, has burned **~16,500 CPU-seconds (~4.6 CPU-hours)** and is **actively pegging the cores NOW** (70 CPU-s in a 3s sample).
- Its output (`data/exp_sparse_onset_higher_loads_followup_cpu_v1/metrics.json` + partial_s1) are stamped **20:43 -- the start -- and have NOT updated since.** So: hours of max-CPU, ZERO output progress = stuck in an intractable compute loop (the "numpy + per-element Python-loop at large-N" failure mode the queue gate warns about). A 2nd python (PID 18652) sits on the same cell at 0 CPU (stuck parent/double-launch).
- NOT in any queue.json I can see -> looks DIRECT-launched (not via the checkpointed runner). "Higher loads" sparse-onset is a HEAVY sweep -> per compute-routing it belongs on **remote_cpu (marsh@home)**, NOT the laptop.

## ASK (whoever started it -- exp_dev? this looks like the Phase-0 sparse-onset work)
1. **Did you start it?** Confirm owner.
2. Is it CHECKPOINTED (resumable) or will a kill lose everything?
3. OK to **KILL it** (it's pegging the laptop with no progress for ~4.6h) + re-dispatch to remote_cpu with a wall-time bound + checkpointing if you still want the result?

I'll kill PIDs 10504+18652 on USER's go (process-kill = harness-gated). Owner: reply who/checkpointed/OK-to-kill.

-- Orchestrator
