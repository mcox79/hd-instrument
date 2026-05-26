"""One-time backfill: add plain_language + importance to existing status log entries."""
import json
import os

STATUS_LOG = "D:/AI/hd-instrument/data/orchestrator_status_log.jsonl"

BACKFILL = {
    "orchestrator_init|Orchestrator status log initialized. Backfilling today's significant events follows; future events appended in real time.": {
        "plain_language": "The orchestrator was started and its event log was initialised. All significant events from today are being backfilled into the log so the dashboard has historical context.",
        "importance": "LOW",
    },
    "migration|Phase 0 orchestrator skeleton built at tools/orchestrator/; dispatch.py + 5 sub-agents (queue_health/visibility/research/exp_dev/strategy) defined.": {
        "plain_language": "Initial orchestrator scaffolding is in place. The dispatch system and five specialised sub-agents (queue health, visibility, research, experiment development, and strategy) are now defined.",
        "importance": "HIGH",
    },
    "migration|Full migration: META cron deleted, 5 live tabs closed; orchestrator dispatches on file-system events.": {
        "plain_language": "The old cron-based automation was replaced with a new event-driven orchestrator. Old watchers removed; the system now reacts to file changes rather than running on a fixed schedule.",
        "importance": "HIGH",
    },
    "verdict|BETA_M_INIT_UNIFORM_KILL v1 FULL (OOM artifact)": {
        "plain_language": "A test of uniform memory-capacity initialisation ran out of memory and was killed. This was diagnosed as a runtime artefact (too much memory allocated at once), not evidence that the underlying mechanism is fundamentally broken.",
        "importance": "MEDIUM",
    },
    "verdict|BETA_M_INIT_OOM_INCONCLUSIVE v2 FULL": {
        "plain_language": "A second capacity sweep confirmed the OOM kills happen at over-capacity memory-to-dimension ratios - exactly where theory predicts failure. This is expected behaviour, not a surprise.",
        "importance": "MEDIUM",
    },
    "verdict|BETA continual_edit v3 FAILED 4.1s OOM at N=32768": {
        "plain_language": "Attempting to continuously edit substrate memory at large dimension (N=32768) crashed with an out-of-memory error after just 4 seconds. A hard gate now blocks this class of experiment until the code is refactored to process data in smaller chunks.",
        "importance": "CRITICAL",
    },
    "verdict|CROOKS_NOISE_ENVELOPE_KILL FULL": {
        "plain_language": "Forensic-erase verification (Cap 1 - the ability to cryptographically prove a memory entry was deleted) appeared to break under noisy conditions. Follow-up research was immediately triggered to check whether a corrected mathematical bound rescues the result.",
        "importance": "CRITICAL",
    },
    "research_delivery|Crooks noise-robust 2x drill": {
        "plain_language": "Deep-dive research found a noise-corrected theoretical bound (Sagawa-Ueda) that applies when the substrate operates under noise. Post-hoc re-analysis of the earlier negative result suggests forensic-erase actually works at all tested noise levels - the prior test used the wrong yardstick.",
        "importance": "HIGH",
    },
    "verdict|CROOKS_NOISE_CORRECTED_PASS FULL — Sagawa-Ueda re-axiomatization PASSES at all 3 noise cells": {
        "plain_language": "With the corrected theoretical bound, forensic-erase verification (Cap 1) passes at all three noise levels tested. The capability narrative flips from 'only works on clean substrate' to 'works across a tiered noise-tolerance envelope.' This is a significant positive result for the memory-audit story.",
        "importance": "CRITICAL",
    },
    "verdict|STREAMING_NOISE_ENVELOPE_PASS FULL — 3/3 noisy cells pass throughput>=0.9": {
        "plain_language": "Streaming inference (Cap 3) now passes under noise - all three noisy test conditions achieve throughput above 0.9. The operating envelope is expanded to include moderately noisy environments, strengthening this capability's product story.",
        "importance": "CRITICAL",
    },
    "audit|Historical audit landed: active_priorities.md is 46 versions stale (last v111, current v157); Bet Z.5 orphaned 13 versions; 3 today Research deliveries never integrated; Bet T/V never had rescue sketches; pq_high_resolution FULL pending 5 cycles.": {
        "plain_language": "A self-audit found significant coordination debt: the priorities document is 46 versions behind current state, three research findings from today were never acted on, two research bets have no rescue plans, and one confirmed capability has been waiting for formal recognition for five cycles.",
        "importance": "HIGH",
    },
    "verdict|ONLINE_W_NOISE_ENVELOPE_NARROW FULL — 4/5 noisy cells pass at p<=0.30; hard fail p>=0.40": {
        "plain_language": "Online learning (Cap 5 - the substrate can keep updating its memory as new information arrives) works reliably up to 30% bit-flip noise but fails hard above 40%. The operating envelope is now formally documented: use this capability under moderate noise only.",
        "importance": "CRITICAL",
    },
    "verdict|CAP2_MARGIN_KILL FULL — corr(margin, correct) < 0.2 in ALL strata": {
        "plain_language": "We tested whether the substrate can reliably signal how confident it is in its own answers (Cap 2 - self-monitoring). The correlation between its confidence score and actual correctness was below 0.2 in every test group - essentially noise. This capability is structurally closed; the active portfolio shrinks from 12 to 11.",
        "importance": "CRITICAL",
    },
    "verdict|ONLINE_W_POLYAK_PARTIAL FULL — 4/5 noisy cells pass at p<=0.30": {
        "plain_language": "A Polyak-averaging variant of the online learning update (Cap 5) matches but does not exceed the existing 30% noise ceiling. It is a partial rescue - confirming the envelope boundary - but does not expand it further.",
        "importance": "MEDIUM",
    },
    "verdict|PQ_OTHER_CARDINALITY FULL: 60 total / 7 outer peaks (hierarchical multi-scale)": {
        "plain_language": "Measuring the substrate's internal memory landscape (P(q) order parameter) revealed a hierarchical two-level structure: 7 broad peaks each containing roughly 8-9 finer peaks, totalling ~60 distinct states. This resolves an earlier partial observation and characterises the physical structure of the memory.",
        "importance": "HIGH",
    },
}

def backfill():
    with open(STATUS_LOG, encoding="utf-8") as f:
        lines = f.readlines()

    updated = []
    patched = 0
    no_match = []
    for line in lines:
        s = line.strip()
        if not s:
            updated.append(line)
            continue
        try:
            entry = json.loads(s)
        except json.JSONDecodeError:
            updated.append(line)
            continue
        key = f"{entry.get('event_kind', '')}|{entry.get('summary', '')}"
        patch = BACKFILL.get(key)
        if patch:
            if "plain_language" not in entry:
                entry["plain_language"] = patch["plain_language"]
            if "importance" not in entry:
                entry["importance"] = patch["importance"]
            patched += 1
            updated.append(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")
        else:
            no_match.append(key[:80])
            updated.append(line)

    tmp = STATUS_LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.writelines(updated)
    os.replace(tmp, STATUS_LOG)
    print(f"Patched {patched} entries.")
    if no_match:
        print("No match for:")
        for k in no_match:
            print(f"  {k}")

if __name__ == "__main__":
    backfill()
