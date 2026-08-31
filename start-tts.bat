@echo off
chcp 65001 >nul
echo 启动漫庐 TTS 服务...
echo 语音: zh-CN-XiaoxiaoNeural (温暖女声)
echo 端口: 18090
echo.
python "%~dp0tts_server.py"
pause
