# check-secrets.ps1, pull-secrets.ps1 공용. 직접 실행하지 말고 dot-source 한다.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

$SecretTargets = @(
    @{ Item = "Devenira backend .env";        Example = "backend\.env.example";        Dest = "backend\.env" },
    @{ Item = "Devenira frontend .env.local"; Example = "frontend\.env.local.example"; Dest = "frontend\.env.local" },
    @{ Item = "Devenira mobile .env";         Example = "mobile\.env.example";         Dest = "mobile\.env"; Optional = $true }
)

$corpCa = Join-Path $env:USERPROFILE ".certs\basf-ca.pem"
if (-not $env:NODE_EXTRA_CA_CERTS -and (Test-Path $corpCa)) { $env:NODE_EXTRA_CA_CERTS = $corpCa }

$Bw = (Get-Command bw -ErrorAction SilentlyContinue).Source
if (-not $Bw) {
    $Bw = Get-ChildItem (Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages") -Recurse -Filter bw.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
}
if (-not $Bw -or -not (Test-Path $Bw)) { throw "bw CLI를 찾을 수 없어요. 'winget install Bitwarden.CLI' 후 다시 실행하세요." }

function Get-EnvKeys([string]$text) {
    $map = [ordered]@{}
    foreach ($line in ($text -split "`r?`n")) {
        if ($line -match '^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$') {
            $map[$Matches[1]] = $Matches[2].Trim().Trim('"').Trim("'")
        }
    }
    $map
}

function Unlock-Bitwarden {
    $status = (& $Bw status | ConvertFrom-Json).status
    if ($status -eq "unauthenticated") {
        Write-Host "Bitwarden 로그인 (이메일, 마스터 비밀번호, 2단계 인증 코드 입력)" -ForegroundColor Cyan
        & $Bw login | Out-Null
        $status = (& $Bw status | ConvertFrom-Json).status
    }
    if ($status -eq "locked") {
        Write-Host "Bitwarden 잠금 해제 (마스터 비밀번호 입력)" -ForegroundColor Cyan
        $env:BW_SESSION = & $Bw unlock --raw
    }
    if ((& $Bw status | ConvertFrom-Json).status -ne "unlocked") { throw "잠금 해제에 실패했어요." }
    & $Bw sync | Out-Null
}

function Lock-Bitwarden {
    & $Bw lock | Out-Null
    Remove-Item Env:BW_SESSION -ErrorAction SilentlyContinue
}

function Get-SecretItems {
    & $Bw list items --search "Devenira" | ConvertFrom-Json
}
