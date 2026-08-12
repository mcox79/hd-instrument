# Quick 90-second popup detector. Same as popup_detector.ps1 but shorter window.
$logFile = 'C:/Users/marsh/AppData/Local/Temp/popup_log_v2.txt'
$endTime = (Get-Date).AddSeconds(90)
$seen = @{}
$targets = 'powershell.exe','cmd.exe','bash.exe','python.exe','ssh.exe','scp.exe','git.exe','tar.exe','conhost.exe','wscript.exe','cscript.exe','curl.exe','find.exe','grep.exe','sort.exe'

foreach ($p in Get-CimInstance Win32_Process | Where-Object { $targets -contains $_.Name }) {
    $seen[$p.ProcessId] = $true
}

"=== popup_detector_quick started $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $logFile
"Seeded $($seen.Count) existing console processes; logging new for 90s." | Out-File $logFile -Append
"" | Out-File $logFile -Append

while ((Get-Date) -lt $endTime) {
    $procs = Get-CimInstance Win32_Process | Where-Object { $targets -contains $_.Name }
    foreach ($p in $procs) {
        if (-not $seen.ContainsKey($p.ProcessId)) {
            $seen[$p.ProcessId] = $true
            $parent = $null
            try { $parent = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue).Name } catch {}
            $cmd = if ($p.CommandLine) { $p.CommandLine.Substring(0, [Math]::Min(140, $p.CommandLine.Length)) } else { '(no cmdline)' }
            "$(Get-Date -Format 'HH:mm:ss.fff') | $($p.Name) | par=$parent | $cmd" | Out-File $logFile -Append
        }
    }
    Start-Sleep -Milliseconds 1000
}
"=== done $(Get-Date -Format 'HH:mm:ss') ===" | Out-File $logFile -Append
