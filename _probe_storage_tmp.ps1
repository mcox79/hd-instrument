Write-Host "=== PHYSICAL DISKS ==="
Get-PhysicalDisk | Select-Object FriendlyName, MediaType, BusType, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,1)}}, HealthStatus | Format-Table

Write-Host "=== DRIVE LETTER -> DISK MAPPING ==="
Get-Partition | Where-Object DriveLetter -ne $null | ForEach-Object {
    $disk = Get-Disk -Number $_.DiskNumber
    $vol = Get-Volume -DriveLetter $_.DriveLetter
    [PSCustomObject]@{
        DriveLetter = $_.DriveLetter
        DiskNumber = $_.DiskNumber
        BusType = $disk.BusType
        DiskFriendlyName = $disk.FriendlyName
        FreeSpaceGB = [math]::Round($vol.SizeRemaining / 1GB, 1)
        TotalSizeGB = [math]::Round($vol.Size / 1GB, 1)
    }
} | Format-Table

Write-Host "=== M.2 NVMe CANDIDATES (BusType=NVMe) ==="
Get-PhysicalDisk | Where-Object BusType -eq 'NVMe' | Select-Object FriendlyName, BusType, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,1)}} | Format-Table
