# Polls Win32_Process every 1.5s for 4 minutes, logs any console-mode child
# (powershell/cmd/bash/python/ssh/scp/git/tar/conhost) that is newly created.
# Output: C:/Users/marsh/AppData/Local/Temp/popup_log.txt

$logFile = 'C:/Users/marsh/AppData/Local/Temp/popup_log.txt'
$endTime = (Get-Date).AddMinutes(4)
$seen = @{}
$targets = 'powershell.exe','cmd.exe','bash.exe','python.exe','ssh.exe','scp.exe','git.exe','tar.exe','conhost.exe','wscript.exe','cscript.exe','perl.exe'

# Seed with current PIDs so we don't log existing processes
foreach ($p in Get-CimInstance Win32_Process | Where-Object { $targets -contains $_.Name }) {
    $seen[$p.ProcessId] = $true
}

"=== popup_detector started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $logFile
"Seeded $($seen.Count) existing console processes; logging new ones for 4 min." | Out-File $logFile -Append
"" | Out-File $logFile -Append

while ((Get-Date) -lt $endTime) {
    $procs = Get-CimInstance Win32_Process | Where-Object { $targets -contains $_.Name }
    foreach ($p in $procs) {
        if (-not $seen.ContainsKey($p.ProcessId)) {
            $seen[$p.ProcessId] = $true
            $parent = $null
            try { $parent = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue).Name } catch {}
            $cmd = if ($p.CommandLine) { $p.CommandLine.Substring(0, [Math]::Min(200, $p.CommandLine.Length)) } else { '(no cmdline)' }
            "$(Get-Date -Format 'HH:mm:ss.fff') | pid=$($p.ProcessId) parent=$($parent)(pid=$($p.ParentProcessId)) | $($p.Name) | $cmd" | Out-File $logFile -Append
        }
    }
    Start-Sleep -Milliseconds 1500
}
"=== done $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $logFile -Append
