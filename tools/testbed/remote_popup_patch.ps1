$ErrorActionPreference = 'Stop'
Write-Output "=== PATCH 1: set Hidden=true on all hd_* tasks ==="
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -like 'hd_*' }
foreach ($t in $tasks) {
    try {
        $settings = $t.Settings
        $settings.Hidden = $true
        Set-ScheduledTask -TaskName $t.TaskName -Settings $settings | Out-Null
        Write-Output "  Hidden=true set on: $($t.TaskName)"
    } catch {
        Write-Output "  FAIL Hidden on $($t.TaskName): $_"
    }
}

Write-Output ""
Write-Output "=== PATCH 2: rewrite hd_index_refresh + hd_metrics_atomize to use pythonw.exe ==="
$pyVisible  = 'C:/dev/hd-instrument/.venv/Scripts/python.exe'
$pyHidden   = 'C:/dev/hd-instrument/.venv/Scripts/pythonw.exe'

foreach ($taskName in @('hd_index_refresh','hd_metrics_atomize')) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName
        $oldAction = $task.Actions[0]
        if ($oldAction.Execute -like '*python.exe*' -and $oldAction.Execute -notlike '*pythonw.exe*') {
            $newAction = New-ScheduledTaskAction -Execute $pyHidden -Argument $oldAction.Arguments -WorkingDirectory $oldAction.WorkingDirectory
            Set-ScheduledTask -TaskName $taskName -Action $newAction | Out-Null
            Write-Output "  $taskName : python.exe -> pythonw.exe"
        } else {
            Write-Output "  $taskName : already pythonw.exe ($($oldAction.Execute))"
        }
    } catch {
        Write-Output "  FAIL $taskName : $_"
    }
}

Write-Output ""
Write-Output "=== PATCH 3: verify post-patch state ==="
Get-ScheduledTask | Where-Object { $_.TaskName -like 'hd_*' } | ForEach-Object {
    $info = $_
    $action = $info.Actions[0]
    [PSCustomObject]@{
        Task   = $info.TaskName
        Hidden = $info.Settings.Hidden
        Exe    = $action.Execute
    }
} | Format-Table -AutoSize
