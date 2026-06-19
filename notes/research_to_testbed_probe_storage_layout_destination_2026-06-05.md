# Research -> Testbed: Probe storage layout on marsh@home + report for user confirmation before Llama-1B extraction

**From:** Research session
**To:** Testbed (primary; runner access)
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-05 ~13:30
**Subject:** Before dispatching Llama-3.2-1B extraction, probe marsh@home storage layout (M.2 vs SSD vs HDD per drive letter). User confirms destination. Then proceed with extraction.

---

## Procedure

### Step 1: Probe storage layout (Testbed action)

Run on marsh@home (via SSH or directly on runner):

```powershell
# Show all physical disks with media type + bus type + size
Write-Host "=== PHYSICAL DISKS ==="
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,1)}}, HealthStatus | Format-Table

# Show drive letter to disk mapping
Write-Host "=== DRIVE LETTER -> DISK MAPPING ==="
Get-Partition | Where-Object DriveLetter -ne $null | ForEach-Object {
    $disk = Get-Disk -Number $_.DiskNumber
    [PSCustomObject]@{
        DriveLetter = $_.DriveLetter
        DiskNumber = $_.DiskNumber
        BusType = $disk.BusType
        MediaType = $disk.PartitionStyle
        DiskFriendlyName = $disk.FriendlyName
        FreeSpaceGB = [math]::Round((Get-Volume -DriveLetter $_.DriveLetter).SizeRemaining / 1GB, 1)
        TotalSizeGB = [math]::Round((Get-Volume -DriveLetter $_.DriveLetter).Size / 1GB, 1)
    }
} | Format-Table

# Identify M.2 NVMe drives specifically (BusType=NVMe + MediaType=SSD)
Write-Host "=== M.2 NVMe CANDIDATES (BusType=NVMe) ==="
Get-PhysicalDisk | Where-Object BusType -eq 'NVMe' | Select-Object FriendlyName, BusType, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,1)}} | Format-Table
```

### Step 2: Report back

Reply to Research with the probe output, formatted as a clear table:

```
Drive D: -- BusType=<NVMe|SATA|...>, MediaType=<SSD|HDD>, Free=<XXX GB>, Total=<XXX GB>
Drive C: -- (same)
Drive E: -- (same)
...
```

Plus call out which drives are M.2 NVMe explicitly.

### Step 3: User confirms destination

Based on probe results, user picks where data lives. Likely options:

**Option A (recommended if M.2 has enough space):** Everything under D:\AI\hd-instrument\data\
- Substrate W + activations + corpora all co-located
- Symlinks between desktop view (D:\AI\hd-instrument) and runner view (C:\dev\hd-instrument) if needed

**Option B (split if M.2 is limited):** 
- M.2: substrate W (small) + activation extracts (moderate, random-access during eval)
- Slower drive: Wikipedia corpus (large, sequential read)

**Option C (custom):** user picks specific drive letters per data category.

### Step 4: Proceed with Llama-1B extraction (Testbed action after user confirms)

Once destination confirmed:
1. Create directory structure at confirmed location
2. Adapt Pythia per-token script for Llama-3.2-1B (model_id swap; tokenizer; hidden_dim=2048; layer ~11-12)
3. Smoke test (~50 docs)
4. Dispatch cloud H100 OR local 4060 Ti extraction (~$3-5 cloud OR ~24-48h local)
5. Output to confirmed destination path

---

## Recommended directory structure (for user confirmation)

```
<chosen_drive>\AI\hd-instrument\data\
├── activations\           # LLM extractions; large; one-time writes
│   ├── pythia_160m\
│   │   └── residuals_per_token.npz (existing)
│   ├── llama_3_2_1b\
│   │   └── residuals_per_token.npz (Phase 2 target)
│   └── llama_3_1_8b\      # Phase 3 (later)
├── corpora\               # Source corpora; sequential read
│   ├── wikipedia_en\      # Phase 2-3
│   ├── kg_qa_datasets\    # already on runner
│   └── pubmed\            # Phase 4
├── substrate\             # Substrate W matrices; small files; speed-sensitive
│   ├── ccc_pythia\
│   ├── ccc_llama1b\
│   └── wikipedia_full\    # Phase 3+
├── extractions\           # Per-doc partials during extraction; temporary
│   └── llama_3_2_1b_partials\
└── eval\                  # Benchmark results, ablation data
```

---

## Storage sizing estimates per phase

| Phase | Component | Size |
|---|---|---|
| Phase 1 (Pythia; partly existing) | activations + substrate | ~5-10 GB |
| Phase 2 (Llama-1B subset) | adds ~10-30 GB | total ~15-40 GB |
| Phase 3a (Llama-1B Wikipedia full) | adds ~50-150 GB | total ~65-200 GB |
| Phase 3b (Llama-8B subset) | adds ~50-150 GB | total ~115-350 GB |
| Phase 3c (Llama-8B Wikipedia full) | adds ~300-700 GB | total ~415-1050 GB |
| Phase 4 (comprehensive KB) | adds ~1-2 TB | total ~1.5-3 TB |

For Phase 2: any drive with ~50 GB free works. For Phase 3+: 200-1000 GB+ on chosen drive.

---

## Speed sensitivity per data category

| Category | M.2 / fast SSD benefit |
|---|---|
| LLM extractions (large npz; one-time writes) | Helpful but not critical |
| Substrate W matrices (small; random access during retrieval) | HIGH benefit if substrate doesn't fit in RAM |
| Wikipedia corpus (sequential read during extraction) | Helpful but not critical |
| Per-doc partials (transient during extraction) | Helpful |
| Eval datasets (small; random read) | Doesn't matter |

If user has limited M.2 capacity: prioritize substrate W + per-doc partials on M.2.
If plenty of M.2: keep everything on M.2 for simplicity.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: this is Testbed (extraction + runner) primary
- Per user 2026-06-05 ~13:15: probe BEFORE extraction; user confirms destination
- Per [[feedback-cloud-only-when-absolutely-necessary]]: cloud Llama-1B is ~$3-5 (cheap; OK if user prefers fast wall-time)
- ASCII-only

---

**END.**

**Testbed:** probe storage layout on marsh@home per Step 1 PowerShell snippet. Report drive letters + bus type + M.2 identification + free/total space. Standing for your output + user confirmation before Llama-1B extraction starts.

**User:** standing for Testbed's storage probe output -- then you confirm destination path -- then extraction proceeds. Cloud H100 dispatch ready (~$3-5; ~1 hour wall) once destination confirmed.
