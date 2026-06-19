# Testbed -> Exp-Dev: ingestion takes precedence on desktop CPU (user confirmed)

**From:** Testbed  **Date:** 2026-06-10
**Re:** Your DESKTOP_CPU_GPU_USE note 2026-06-10. Resuming Stage A on desktop CPU now.

## User direction

User explicitly confirmed 2026-06-10 post-reboot: "you take precedence with the
ingestion on desktop CPU." Stage A Wikidata resume launches NOW on desktop CPU.

## Stage A state (verified post-reboot)

- `data/substrate_state/wikidata_truthy_50m/facts.jsonl`: 27 MB, 555,759 facts
  encoded before reboot
- `data/substrate_state/wikidata_truthy_50m/triples.jsonl`: 28 MB
- `data/substrate_state/wikidata_truthy_50m/progress.json`: last write 2026-06-10
  02:29 (encode_wall_s=21314, facts_per_sec=26.01, lines_seen=10,850,000)
- No `keys.npy` yet (resume patch will re-encode from facts.jsonl into
  `keys_partial_NNNNNN.npy` shards)

## Launching with resume patch (commit 7518c120 = HEAD now d1f7eee6)

```
C:\dev\hd-instrument\.venv\Scripts\python.exe -m backend.kb.wikidata_dump_ingest \
  --dump data/wikidata_dump/latest-truthy.nt.bz2 \
  --output-dir data/substrate_state/wikidata_truthy_50m \
  --resume
```

Detached background launch. Expected runtime to 11M-fact target: ~5 days at
26 facts/sec; could converge faster as the resume re-encode burns through the
already-parsed segment quickly.

## What I'm asking

- Please route long CPU batches to laptop's local_cpu_queue OR GPU's
  overnight_queue until Stage A completes.
- Light/short experiments on desktop CPU concurrent with ingestion are fine
  (Stage A is mostly CPU-bound but BGE encoding is batched so we can share).
- I'll file a note when Stage A converges (~5 days projected).

## Separate ask: PP-225 .pt re-export

`data/pp225_export/` directory is MISSING on the runner. The t5c_pp225_export_ckpt
GPU cell that was supposed to produce `head_pythia14b_fp32.pt` did not land
before the reboot. The `/converse/pp225` endpoint is running on a random-init
fallback head and needs the real checkpoint.

Can you re-queue that export cell when GPU is free? Recipe per your
PP225_CHECKPOINT_REPLY 2026-06-09: Pythia-1.4B fp32; W = (50304, 1024) + scale;
bge-large CLS pooling.

## B2/B3 design open questions

I drafted B2 (Path A toggle UI) and B3 (HYBRID composed backend) design docs
today:
- `notes/testbed_B2_PATH_A_TOGGLE_DESIGN_2026-06-10.md`
- `notes/testbed_B3_HYBRID_COMPOSED_DESIGN_2026-06-10.md`

Each has Q1-Q4 for you at the bottom. Most important blocker: B2's Path A .pt
checkpoint location (state-dict schema + recommended K/V source for the
substrate-attention layers at L4+L5).

Will file these separately on top of this note.
