# GitHub Pages push helper
# 从 ~/.git-credentials 读取 PAT token，通过 ghproxy 推送
# 用法: .\push.ps1 [提交信息]

param([string]$msg)

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoDir

# 读取 PAT
$credFile = "$env:USERPROFILE\.git-credentials"
if (!(Test-Path $credFile)) {
    Write-Host "❌ 找不到 $credFile" -ForegroundColor Red
    exit 1
}

$cred = Get-Content $credFile | Select-String "ghproxy.net"
if (!$cred) {
    Write-Host "❌ 未找到 ghproxy.net 的凭据" -ForegroundColor Red
    exit 1
}

# 提取 token (格式: https://uskj:TOKEN@ghproxy.net)
$token = ($cred -split '@')[0] -split ':' | Select-Object -Last 1
Write-Host "🔑 PAT token 已读取" -ForegroundColor Green

# 检查是否有未提交的更改
$status = git status --porcelain
if ($status) {
    if ($msg) {
        git add -A
        git commit -m $msg
        Write-Host "✅ 已提交: $msg" -ForegroundColor Green
    } else {
        Write-Host "⚠️  有未提交的更改，请先提交或传提交信息参数" -ForegroundColor Yellow
        Write-Host "   用法: .\push.ps1 ""提交信息""" -ForegroundColor Yellow
        git status -s
        exit 1
    }
}

# 推送到 ghproxy
$pushUrl = "https://uskj:$token@ghproxy.net/https://github.com/uskj/uskj.github.io.git"
Write-Host "🚀 正在推送到 GitHub Pages..." -ForegroundColor Cyan
git push $pushUrl

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 推送成功！https://uskj.github.io" -ForegroundColor Green
} else {
    Write-Host "❌ 推送失败" -ForegroundColor Red
}
