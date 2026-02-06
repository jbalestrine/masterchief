try {
    $u = Get-ChildItem -Path .\data\uploads -Filter *.zip -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if(-not $u) { Write-Output 'No zip uploads found'; exit 0 }
    $name = $u.Name
    Write-Output "Found upload: $name"
    Write-Output "Installing..."
    Invoke-WebRequest -Uri "http://127.0.0.1:8080/addons/install/$name" -UseBasicParsing | Out-Null
    Start-Sleep -Milliseconds 300
    $addonName = $name -replace '\.zip$',''
    Write-Output "Loading $addonName..."
    Invoke-WebRequest -Uri "http://127.0.0.1:8080/addons/load/$addonName" -UseBasicParsing | Out-Null
    Start-Sleep -Milliseconds 300
    Write-Output "Registering features..."
    Invoke-WebRequest -Uri "http://127.0.0.1:8080/addons/register_features/$addonName" -UseBasicParsing | Out-Null
    Start-Sleep -Milliseconds 300
    Write-Output "Features page excerpt:"
    $r = Invoke-WebRequest "http://127.0.0.1:8080/features" -UseBasicParsing
    $c = $r.Content
    if($c.Length -gt 400) { $c = $c.Substring(0,400) }
    Write-Output $c
    Write-Output "Addons public list:"
    Invoke-WebRequest "http://127.0.0.1:8080/api/addons/list_public" -UseBasicParsing | Select-Object -ExpandProperty Content
} catch { Write-Output "ERROR: $_" ; exit 1 }
