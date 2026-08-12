$ErrorActionPreference = 'SilentlyContinue'
Write-Output "=== SECTION 1: hd_* scheduled tasks ==="
Get-ScheduledTask | Where-Object { $_.TaskName -like 'hd_*' } | ForEach-Object {
    $info = $_
    $action = $info.Actions[0]
    [PSCustomObject]@{
        Task   = $info.TaskName
        Hidden = $info.Settings.Hidden
        Exe    = $action.Execute
        Args   = if ($action.Arguments) { $action.Arguments.Substring(0,[Math]::Min(100,$action.Arguments.Length)) } else { '' }
    }
} | Format-Table -AutoSize -Wrap

Write-Output ""
Write-Output "=== SECTION 2: alive python processes ==="
Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" | ForEach-Object {
    [PSCustomObject]@{
        PID    = $_.ProcessId
        PPID   = $_.ParentProcessId
        Name   = $_.Name
        Cmd    = if ($_.CommandLine) { $_.CommandLine.Substring(0,[Math]::Min(140,$_.CommandLine.Length)) } else { '' }
    }
} | Format-Table -AutoSize -Wrap

Write-Output ""
Write-Output "=== SECTION 3: ssh/scp/conhost/wmic/cmd processes ==="
Get-Process | Where-Object { $_.Name -in @('ssh','scp','conhost','wmic','tasklist','cmd') } | Select-Object Id,Name,StartTime | Sort-Object StartTime -Descending | Format-Table -AutoSize

Write-Output ""
Write-Output "=== SECTION 4: launcher .bat files in tools/orchestrator/ ==="
Get-ChildItem -Path 'C:\dev\hd-instrument\tools\orchestrator\*launcher*.bat' -ErrorAction SilentlyContinue | Select-Object Name,Length,LastWriteTime | Format-Table -AutoSize
Get-ChildItem -Path 'C:\dev\hd-instrument\tools\orchestrator\*launcher*.cmd' -ErrorAction SilentlyContinue | Select-Object Name,Length,LastWriteTime | Format-Table -AutoSize
