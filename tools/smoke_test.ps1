$timeout=180
for ($i=0; $i -lt $timeout; $i++) {
  $s = Test-NetConnection -ComputerName 127.0.0.1 -Port 8081
  if ($s.TcpTestSucceeded) { Write-Output 'PORT_OPEN'; break }
  Start-Sleep -s 1
}
if (-not $s.TcpTestSucceeded) { Write-Output 'TIMEOUT'; exit 1 }

$r = Invoke-WebRequest -Uri http://127.0.0.1:8081/echo-chat -UseBasicParsing -TimeoutSec 10
Write-Output ('ECHO-CHAT_STATUS: ' + $r.StatusCode)
$len = $r.Content.Length
$r.Content.Substring(0,[math]::Min(400,$len)) | Write-Output

$s1 = Invoke-WebRequest -Uri http://127.0.0.1:8081/static/echo_chat.js -UseBasicParsing -TimeoutSec 10
Write-Output ('JS_STATUS: ' + $s1.StatusCode)
$s1.Content.Substring(0,[math]::Min(300,$s1.Content.Length)) | Write-Output

$body = @{ message='smoke test'; llm_only=$true } | ConvertTo-Json
try {
  $resp = Invoke-RestMethod -Uri http://127.0.0.1:8081/api/echo/chat -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 30
  Write-Output 'POST_RESPONSE:'
  $resp | ConvertTo-Json -Depth 4 | Write-Output
} catch {
  Write-Output 'POST_FAILED'
  $_ | Write-Output
  exit 1
}
