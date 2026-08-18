$ErrorActionPreference = 'SilentlyContinue'

Write-Host "=== Grupo X - Reset de Demo ===" -ForegroundColor Cyan

# Verificar Docker
Write-Host "`n[1/4] Verificando Docker..." -ForegroundColor Yellow
docker ps --format "{{.Names}}" | ForEach-Object { Write-Host "  $_" -ForegroundColor Green }

# Verificar datos existentes
Write-Host "`n[2/4] Verificando datos..." -ForegroundColor Yellow
$count = docker exec grupo-x-postgres psql -U postgres -d grupo_x -t -c "SELECT count(*) FROM vulnerabilities;" 2>&1
$count = $count.Trim()
Write-Host "  Vulnerabilidades actuales: $count" -ForegroundColor Green

# Reiniciar backend
Write-Host "`n[3/4] Reiniciando backend..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

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

# Arrancar frontend
Write-Host "`n[4/4] Arrancando frontend..." -ForegroundColor Yellow
$frontendDir = Join-Path $proj "frontend"
Start-Process powershell -ArgumentList @("-NoProfile", "-Command", "Set-Location '$frontendDir'; node .\node_modules\vite\bin\vite.js --port 5173 --host 127.0.0.1") -WindowStyle Hidden
Start-Sleep -Seconds 6

$feOk = try { Invoke-WebRequest -Uri "http://127.0.0.1:5173" -TimeoutSec 5 -UseBasicParsing; $true } catch { $false }
if ($feOk) { Write-Host "  Frontend OK: http://127.0.0.1:5173" -ForegroundColor Green }

Write-Host "`n=== Listo ===" -ForegroundColor Cyan
Write-Host "  Frontend: http://127.0.0.1:5173"
Write-Host "  Backend:  http://localhost:8000/docs"
Write-Host "  n8n:      http://localhost:5678"
Write-Host ""
Write-Host "Login: admin / Admin123" -ForegroundColor Magenta
