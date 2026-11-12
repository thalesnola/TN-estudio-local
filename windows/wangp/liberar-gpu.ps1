param([switch]$DryRun)
# Para tudo que disputa a GPU antes do WanGP: modelos Ollama, IPED (java), Cellebrite.
$alvos = @()
# 1) Ollama: descarrega os modelos residentes (servidor continua de pe)
$m = (ollama ps 2>$null | Select-Object -Skip 1) | ForEach-Object { ($_ -split '\s+')[0] } | Where-Object { $_ }
foreach ($x in $m) { $alvos += "ollama stop $x"; if (-not $DryRun) { ollama stop $x | Out-Null } }
# 2) IPED (java com 'iped' na linha de comando), Cellebrite/UFED, Whisper
Get-CimInstance Win32_Process | Where-Object {
  ($_.Name -eq 'java.exe' -and $_.CommandLine -match 'iped') -or
  $_.Name -match '^(cellebrite|UFED|CellebriteWarrant)'
} | ForEach-Object {
  $alvos += "kill $($_.Name) [$($_.ProcessId)]"
  if (-not $DryRun) { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}
if ($alvos) { $alvos | ForEach-Object { "[liberar-gpu] $_" } } else { "[liberar-gpu] nada a parar" }
