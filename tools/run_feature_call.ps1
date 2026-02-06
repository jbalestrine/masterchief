try {
    $r = Invoke-WebRequest 'http://127.0.0.1:8080/feature/run/demo_feature_addon.feature_hello' -UseBasicParsing
    Write-Output 'Feature run response:'
    Write-Output $r.Content
    Write-Output 'Addons public list:'
    $p = Invoke-WebRequest 'http://127.0.0.1:8080/api/addons/list_public' -UseBasicParsing
    Write-Output $p.Content
} catch { Write-Output "ERROR: $_" ; exit 1 }
