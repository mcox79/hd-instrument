# Director write-permission probe, 2026-08-16.
# Purpose: four agents in a row had Write to experiments/** denied with the ambiguous
# "user doesn't want to take this action" string, while their writes to scratch/, notes/
# and .claude/ landed in the same sessions. That asymmetry is evidence of a rule rather
# than of random ESC teardowns. This file is a one-line probe to settle it.
# If this landed, experiments/** is writable and the denials were interrupts after all.
# Safe to delete in a maintenance pass; it is not imported by anything.
PROBE = "director_write_probe_2026_08_16"
