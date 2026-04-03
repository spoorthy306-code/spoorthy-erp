$ErrorActionPreference = 'Stop'

Write-Host "Desktop validation suite" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

Write-Host "1) Tauri environment info" -ForegroundColor Yellow
npm run tauri:info

Write-Host "2) Package version check" -ForegroundColor Yellow
npm outdated | Select-String -Pattern 'tauri' | ForEach-Object { $_.Line }

Write-Host "3) Rust target clean" -ForegroundColor Yellow
Push-Location src-tauri
cargo clean
Pop-Location

Write-Host "4) Tauri build" -ForegroundColor Yellow
npm run tauri:build

Write-Host "5) Hardcoded email scan (src-tauri)" -ForegroundColor Yellow
$matches = Get-ChildItem src-tauri -Recurse -File -Include *.rs |
  Select-String -Pattern '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'

$bad = $matches | Where-Object { $_.Line -notmatch 'spoorthy306@gmail\.com' }
if ($bad) {
  Write-Host "Found non-compliant emails:" -ForegroundColor Red
  $bad | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
} else {
  Write-Host "No non-compliant emails found in src-tauri" -ForegroundColor Green
}

Write-Host "Desktop validation complete" -ForegroundColor Green
