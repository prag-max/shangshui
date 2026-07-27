@echo off
SETLOCAL

REM ============================================================
REM  start-frpc.bat  -  本机 frp 客户端（自动重连版）
REM  作用：把本机 127.0.0.1:8000 (Laravel 后端) 转发到云端服务器
REM  特性：frpc 退出后自动重连，应对 Windows 掉线 / Defender 拦截
REM  用法：双击本文件（建议由 start-all.bat 拉起）；Ctrl+C 停止
REM  注意：全程用 %~dp0 拼绝对路径，不依赖 cd，避免末尾反斜杠转义引号
REM ============================================================

set "FrpcDir=%~dp0"
set "FrpcExe=%FrpcDir%bin\frpc.exe"
set "FrpcToml=%FrpcDir%frpc.toml"
set "GetFrpc=%FrpcDir%get-frpc.ps1"

REM 若 frpc.exe 缺失则尝试下载
if not exist "%FrpcExe%" (
    echo [info] bin\frpc.exe 缺失，尝试下载 ...
    powershell -ExecutionPolicy Bypass -File "%GetFrpc%"
)

if not exist "%FrpcExe%" (
    echo [error] frpc.exe 仍然缺失，请检查 get-frpc.ps1 输出
    pause
    exit /b 1
)

if not exist "%FrpcToml%" (
    echo [error] frpc.toml 未找到，它应与此 bat 同目录
    pause
    exit /b 1
)

REM 解除 Defender / 下载锁定，避免 WinError 5 拒绝访问
powershell -Command "try { Unblock-File -Path '%FrpcExe%' -ErrorAction SilentlyContinue } catch {}"

REM 本地后端存活检查（非阻断）
curl -s -o nul http://127.0.0.1:8000/api/inquiries --max-time 3 >nul 2>&1
if errorlevel 1 (
    echo [warn] 本地后端 :8000 无响应，请先运行 start-backend.bat
    echo [warn] frpc 仍会启动，但隧道暂时没有转发目标
)

REM 自动重连循环：frpc 退出后等待并重连
:loop
echo [%date% %time%] [info] 启动 frpc -> 43.139.72.9:7000 ...
"%FrpcExe%" -c "%FrpcToml%"
echo [%date% %time%] [warn] frpc 已退出 (代码 %errorlevel%)，5 秒后重连 ...
timeout /t 5 /nobreak >nul
goto :loop

ENDLOCAL
