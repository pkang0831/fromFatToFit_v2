# 배포된 프론트엔드/백엔드가 정상 동작하는지 빠르게 점검한다. 로그인이나 데이터 변경은 하지 않는다.
#
#   powershell -ExecutionPolicy Bypass -File scripts\smoke-prod.ps1
#   powershell -ExecutionPolicy Bypass -File scripts\smoke-prod.ps1 -SiteBase https://<vercel-preview-url> -SkipBackend

param(
    [string]$SiteBase = "https://www.devenira.com",
    [string]$ApiBase = "https://api.devenira.com",
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$SiteBase = $SiteBase.TrimEnd("/")
$ApiBase = $ApiBase.TrimEnd("/")
$failures = 0

function Get-Url([string]$url) {
    try {
        $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 30 -MaximumRedirection 5
        return @{ Status = [int]$r.StatusCode; Headers = $r.Headers; Body = [string]$r.Content }
    } catch {
        $resp = $_.Exception.Response
        if ($resp) { return @{ Status = [int]$resp.StatusCode; Headers = @{}; Body = "" } }
        return @{ Status = 0; Headers = @{}; Body = $_.Exception.Message }
    }
}

function Check([string]$name, [string]$url, [int[]]$expect, [scriptblock]$extra = $null) {
    $r = Get-Url $url
    $ok = $expect -contains $r.Status
    $note = ""
    if ($ok -and $extra) {
        $note = & $extra $r
        if ($note) { $ok = $false }
    }
    if ($ok) {
        Write-Host ("  [OK]   {0}  ({1})" -f $name, $r.Status) -ForegroundColor Green
    } else {
        Write-Host ("  [FAIL] {0}  {1} -> {2} {3}" -f $name, $url, $r.Status, $note) -ForegroundColor Red
        $script:failures++
    }
}

if (-not $SkipFrontend) {
    Write-Host "== Frontend ($SiteBase)" -ForegroundColor Yellow
    Check "home"              "$SiteBase/"            @(200)
    Check "login"             "$SiteBase/login"       @(200)
    Check "blog"              "$SiteBase/blog"        @(200)
    Check "try"               "$SiteBase/try"         @(200)
    Check "sitemap"           "$SiteBase/sitemap.xml" @(200)
    Check "robots"            "$SiteBase/robots.txt"  @(200)
    Check "3D model (glb)"    "$SiteBase/assets/human-converted.glb" @(200) {
        param($r)
        if ($r.Headers["Access-Control-Allow-Origin"] -ne "*") { "missing Access-Control-Allow-Origin: *" }
    }
    Check "dashboard redirects to login" "$SiteBase/home" @(200)
}

if (-not $SkipBackend) {
    Write-Host ""
    Write-Host "== Backend ($ApiBase)" -ForegroundColor Yellow
    Check "health" "$ApiBase/health" @(200) {
        param($r)
        if ($r.Body -notmatch '"status"\s*:\s*"healthy"') { "body: $($r.Body)" }
    }
    Check "3D preview page" "$ApiBase/api/assets/human-body-preview" @(200) {
        param($r)
        $m = [regex]::Match($r.Body, 'src="([^"]+\.glb)"')
        if (-not $m.Success) { return "no .glb src in page" }
        $model = Get-Url $m.Groups[1].Value
        if ($model.Status -ne 200) { return "model $($m.Groups[1].Value) -> $($model.Status)" }
    }
    Check "auth required (/api/auth/me)" "$ApiBase/api/auth/me" @(401, 403)
    Check "public proof share 404" "$ApiBase/api/proof-shares/public/smoke-test-invalid-token" @(404)
    Check "CORS / CSP headers present" "$ApiBase/health" @(200) {
        param($r)
        if (-not $r.Headers["X-Content-Type-Options"]) { "security headers missing" }
    }
}

Write-Host ""
if ($failures -eq 0) { Write-Host "스모크 테스트 통과" -ForegroundColor Green; exit 0 }
Write-Host "스모크 테스트 실패: $failures 개" -ForegroundColor Red
exit 1
