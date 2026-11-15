# Bitwarden "Devenira" 폴더의 .env 보안 메모를 .env.example 과 비교한다.
# 값은 절대 출력하지 않고, 키 이름과 채워짐 여부만 보여준다.

. (Join-Path $PSScriptRoot "bitwarden-common.ps1")

Unlock-Bitwarden
try {
    $items = Get-SecretItems
    $problems = 0

    foreach ($t in $SecretTargets) {
        Write-Host ""
        Write-Host "== $($t.Item)" -ForegroundColor Yellow
        $item = $items | Where-Object { $_.name -eq $t.Item } | Select-Object -First 1
        if (-not $item) {
            if ($t.Optional) {
                Write-Host "  항목 없음 (선택 항목이라 건너뜀)" -ForegroundColor DarkGray
            } else {
                Write-Host "  항목을 찾을 수 없음" -ForegroundColor Red
                $problems++
            }
            continue
        }

        $expected = (Get-EnvKeys (Get-Content (Join-Path $RepoRoot $t.Example) -Raw)).Keys
        $actual = Get-EnvKeys ([string]$item.notes)

        foreach ($k in $expected) {
            if (-not $actual.Contains($k)) {
                Write-Host ("  [없음]   {0}" -f $k) -ForegroundColor Red; $problems++
            } elseif ([string]::IsNullOrWhiteSpace($actual[$k])) {
                Write-Host ("  [빈 값]  {0}" -f $k) -ForegroundColor DarkYellow
            } else {
                Write-Host ("  [OK]     {0}  ({1}자)" -f $k, $actual[$k].Length) -ForegroundColor Green
            }
        }
        foreach ($k in $actual.Keys) {
            if ($expected -notcontains $k) { Write-Host ("  [추가]   {0}  (.env.example 에 없는 키)" -f $k) -ForegroundColor Cyan }
        }
    }

    Write-Host ""
    Write-Host "Devenira 관련 항목 이름:" -ForegroundColor Yellow
    $items | ForEach-Object { Write-Host "  - $($_.name)" }
} finally {
    Lock-Bitwarden
}

Write-Host ""
if ($problems -eq 0) { Write-Host "확인 끝. 빠진 항목 없음." -ForegroundColor Green }
else { Write-Host "확인 끝. 문제 $problems 개." -ForegroundColor Red }
