# Bitwarden "Devenira" 보안 메모로 로컬 .env 파일들을 만든다.
# 이미 있는 파일은 -Force 를 줄 때만 덮어쓴다. 값은 화면에 출력하지 않는다.
#
#   powershell -ExecutionPolicy Bypass -File scripts\pull-secrets.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\pull-secrets.ps1 -Force

param([switch]$Force)

. (Join-Path $PSScriptRoot "bitwarden-common.ps1")

Unlock-Bitwarden
try {
    $items = Get-SecretItems
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false

    foreach ($t in $SecretTargets) {
        $dest = Join-Path $RepoRoot $t.Dest
        $item = $items | Where-Object { $_.name -eq $t.Item } | Select-Object -First 1
        if (-not $item) {
            $color = if ($t.Optional) { "DarkGray" } else { "Red" }
            Write-Host ("[건너뜀] {0}  (Bitwarden에 '{1}' 없음)" -f $t.Dest, $t.Item) -ForegroundColor $color
            continue
        }

        $content = (([string]$item.notes) -replace "`r`n", "`n").TrimEnd() + "`n"
        $newKeys = Get-EnvKeys $content

        if (Test-Path $dest) {
            $oldKeys = Get-EnvKeys (Get-Content $dest -Raw)
            $changed = @($newKeys.Keys | Where-Object { -not $oldKeys.Contains($_) -or $oldKeys[$_] -ne $newKeys[$_] })
            $removed = @($oldKeys.Keys | Where-Object { -not $newKeys.Contains($_) })
            if ($changed.Count -eq 0 -and $removed.Count -eq 0) {
                Write-Host ("[같음]   {0}" -f $t.Dest) -ForegroundColor DarkGray
                continue
            }
            if (-not $Force) {
                Write-Host ("[다름]   {0}  바뀜: {1} / 없어짐: {2}  (-Force 로 덮어쓰기)" -f $t.Dest, ($changed -join ", "), ($removed -join ", ")) -ForegroundColor DarkYellow
                continue
            }
        }

        [System.IO.File]::WriteAllText($dest, $content, $utf8NoBom)
        Write-Host ("[작성]   {0}  (키 {1}개)" -f $t.Dest, $newKeys.Count) -ForegroundColor Green
    }
} finally {
    Lock-Bitwarden
}
