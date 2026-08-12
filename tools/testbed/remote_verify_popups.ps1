$ErrorActionPreference = 'SilentlyContinue'
$cutoff = (Get-Date).AddMinutes(-1.5)
Write-Output "=== window-spawn processes started AFTER $cutoff ==="
Get-Process | Where-Object { $_.Name -in @('ssh','scp','conhost','wmic','tasklist','cmd','powershell') -and $_.StartTime -gt $cutoff } | Select-Object Id,Name,StartTime | Sort-Object StartTime -Descending | Format-Table -AutoSize

Write-Output ""
Write-Output "=== count by name (last 90s) ==="
Get-Process | Where-Object { $_.Name -in @('ssh','scp','conhost','wmic','tasklist','cmd','powershell') -and $_.StartTime -gt $cutoff } | Group-Object Name | Select-Object Name,Count | Format-Table -AutoSize

Write-Output ""
Write-Output "=== hd_* task last run + result ==="
Get-ScheduledTask | Where-Object { $_.TaskName -like 'hd_*' } | Get-ScheduledTaskInfo | Select-Object TaskName,LastRunTime,LastTaskResult | Sort-Object LastRunTime -Descending | Format-Table -AutoSize
