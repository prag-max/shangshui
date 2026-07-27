# =====================================================================
#  get-frpc.ps1 —— 在本机 Windows 下载并解压 frp 客户端
#  用法（在 backend\deploy\frp 目录下）：
#    powershell -ExecutionPolicy Bypass -File get-frpc.ps1
#  完成后会得到 bin\frpc.exe，配合本目录 frpc.toml 使用：
#    bin\frpc.exe -c frpc.toml
# =====================================================================

$ErrorActionPreference = "Stop"

$version = "0.61.1"
$arch    = "windows_amd64"
$pkg     = "frp_${version}_${arch}"
$url     = "https://github.com/fatedier/frp/releases/download/v${version}/${pkg}.zip"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$zip  = Join-Path $root "$pkg.zip"
$bin  = Join-Path $root "bin"

Write-Host "下载 frp $version ..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
} catch {
    Write-Host "GitHub 直连失败，尝试加速镜像 ..." -ForegroundColor Yellow
    $mirror = "https://ghfast.top/$url"
    Invoke-WebRequest -Uri $mirror -OutFile $zip -UseBasicParsing
}

Write-Host "解压 ..." -ForegroundColor Cyan
$tmp = Join-Path $root "_tmp_frp"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $tmp -Force

New-Item -ItemType Directory -Force -Path $bin | Out-Null
Copy-Item (Join-Path $tmp "$pkg\frpc.exe") (Join-Path $bin "frpc.exe") -Force

Remove-Item $tmp -Recurse -Force
Remove-Item $zip -Force

Write-Host "完成：$bin\frpc.exe" -ForegroundColor Green
Write-Host "下一步：编辑 frpc.toml 填好云服务器 IP 与 token，然后运行  bin\frpc.exe -c frpc.toml"
