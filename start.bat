@echo off
chcp 65001 >nul
title 息 · 情绪按摩（后端 + 本地预览）
cd /d "%~dp0"
echo [息] 启动后端（调 opencode 网关）…
set OPenCode_BASE_URL=https://opencode.ai/go/v1
start "" python server.py
timeout /t 2 >nul
start "" http://localhost:8088
