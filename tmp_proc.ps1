Get-CimInstance Win32_Process -Filter "name='python.exe'" | ForEach-Object {
    $exeType = if ($_.ExecutablePath -match '\.venv') {'VENV'}
               elseif ($_.ExecutablePath -match 'AppData') {'APPDATA'}
               else {'OTHER'}
    $script = if ($_.CommandLine -match '([\w_]+)\.py') { $matches[1] + '.py' } else { '?' }
    [PSCustomObject]@{
        PID = $_.ProcessId
        PPID = $_.ParentProcessId
        Type = $exeType
        Script = $script
        MB = [math]::Round($_.WorkingSetSize/1MB,1)
        CPU_sec = [math]::Round($_.UserModeTime/10000000, 1)
    }
} | Sort-Object PPID, PID | Format-Table -AutoSize
