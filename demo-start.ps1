$ErrorActionPreference = 'SilentlyContinue'

Write-Host "=== Grupo X - Arrancando servicios ===" -ForegroundColor Cyan

Write-Host "`n[1/3] Docker / PostgreSQL..." -ForegroundColor Yellow
docker compose up postgres smtp4dev -d | Out-Null
$tries = 0
do {
    Start-Sleep -Seconds 2
    $tries++
    $dbUp = ((docker ps --filter "name=postgres" --filter "health=healthy" --format "{{.Names}}") -ne $null)
} while (-not $dbUp -and $tries -lt 15)
docker ps --format "{{.Names}} ({{.Status}})" | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }

Write-Host "`n[2/3] Backend (puerto 8000)..." -ForegroundColor Yellow
$proj = (Get-Item $PSScriptRoot).FullName
$venv = Join-Path $proj ".venv\Scripts\python.exe"
$backendDir = Join-Path $proj "backend"
Start-Process powershell -ArgumentList @("-NoProfile", "-Command", "Set-Location '$backendDir'; & '$venv' -m uvicorn app.main:app --port 8000") -WindowStyle Hidden
Start-Sleep -Seconds 8

$health = try { Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 } catch { $null }
if ($health.database -eq "ok") {
    Write-Host "  Backend OK" -ForegroundColor Green
} else {
    Write-Host "  Backend ERROR" -ForegroundColor Red
}

Write-Host "`n[3/3] Frontend (puerto 5173)..." -ForegroundColor Yellow
$frontendDir = Join-Path $proj "frontend"
Start-Process powershell -ArgumentList @("-NoProfile", "-Command", "Set-Location '$frontendDir'; node .\node_modules\vite\bin\vite.js --port 5173 --host 127.0.0.1") -WindowStyle Hidden
Start-Sleep -Seconds 6

Write-Host "`n=== Listo ===" -ForegroundColor Cyan
Write-Host "  Landing:  http://127.0.0.1:5173  (abrir aca para arrancar la demo)"
Write-Host "  Backend:  http://localhost:8000/docs"
Write-Host "  n8n:      http://localhost:5678"
Write-Host "  Mail:     http://localhost:5300  (bandeja smtp4dev para notificaciones)"
Write-Host ""
Write-Host "Login: admin / Admin123!" -ForegroundColor Magenta
