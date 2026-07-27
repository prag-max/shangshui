@echo off
setlocal EnableDelayedExpansion
REM ============================================================
REM  尚水数字 - 一键启动本机环境
REM  启动顺序：MySQL 服务 -^> Laravel 后端^(:8000^) -^> frpc 隧道
REM  后端与 frpc 会在两个独立窗口运行，请勿关闭它们。
REM  用法：双击本文件即可（建议右键"以管理员身份"运行，便于启动 MySQL 服务）
REM ============================================================

set "DEPLOY_DIR=%~dp0"
set "WIN_BAT=%DEPLOY_DIR%win\start-backend.bat"
set "FRP_BAT=%DEPLOY_DIR%frp\start-frpc.bat"

echo ============================================================
echo   尚水数字 一键启动 ^(MySQL + 后端 + 隧道^)
echo ============================================================

REM ---------- [0] MySQL 服务 ----------
echo [0/3] 检查 MySQL 服务 ...
tasklist | findstr /i mysqld.exe >nul 2>&1
if not errorlevel 1 (
    echo       MySQL 已在运行，跳过。
) else (
    echo       MySQL 未运行，尝试启动 ^(需要管理员权限^) ...
    net start MySQL80 >nul 2>&1 || net start MySQL >nul 2>&1
    if errorlevel 1 (
        echo       [警告] 无法自动启动 MySQL，请手动以管理员启动；后端可能连不上库。
    ) else (
        echo       MySQL 启动成功。
    )
)

REM ---------- [1] Laravel 后端 ----------
echo [1/3] 启动 Laravel 后端 ^(127.0.0.1:8000^) ...
netstat -ano | findstr ":8000" | findstr "LISTEN" >nul 2>&1
if not errorlevel 1 (
    echo       检测到 :8000 已在监听，跳过重复启动。
) else (
    if exist "%WIN_BAT%" (
        start "尚水-后端" /MIN cmd /k "%WIN_BAT%"
        echo       已在新窗口启动后端。
    ) else (
        echo       [错误] 找不到 %WIN_BAT%
    )
)

REM ---------- [2] 等待后端就绪 ----------
echo [2/3] 等待后端就绪 ^(最长 20 秒^) ...
set "READY=0"
for /L %%i in (1,1,20) do (
    curl -s -o nul --max-time 2 http://127.0.0.1:8000/api/inquiries >nul 2>&1
    if not errorlevel 1 (
        set "READY=1"
        echo       后端已就绪 ^(第 %%i 秒^)。
        goto :be_ok
    )
    timeout /t 1 >nul
)
:be_ok
if "%READY%"=="0" echo       [警告] 后端 20 秒内无响应，frpc 可能接不到。

REM ---------- [3] frpc 隧道 ----------
echo [3/3] 启动 frpc 隧道 ^(-^> 43.139.72.9:7000^) ...
tasklist | findstr /i frpc.exe >nul 2>&1
if not errorlevel 1 (
    echo       检测到 frpc 已在运行，跳过重复启动。
) else (
    if exist "%FRP_BAT%" (
        start "尚水-frpc" /MIN cmd /k "%FRP_BAT%"
        echo       已在新窗口启动 frpc。
    ) else (
        echo       [错误] 找不到 %FRP_BAT%
    )
)

REM ---------- 验证公网链路 ----------
echo 等待公网链路建立 ^(最长 25 秒^) ...
set "PUB=0"
set "CODE=000"
for /L %%i in (1,1,25) do (
    for /f "delims=" %%c in ('curl -s -k -o nul -w "%%{http_code}" --max-time 3 https://api.shanwater.com:8443/api/inquiries 2^>nul') do set "CODE=%%c"
    if "!CODE!"=="405" (
        set "PUB=1"
        echo       外网链路已通 ^(HTTP !CODE!^)。
        goto :pub_ok
    )
    timeout /t 1 >nul
)
:pub_ok
echo ============================================================
if "%PUB%"=="1" (
    echo   全部就绪！打开 https://www.shanwater.com/contact.html 提交表单即可。
    echo   查库命令：
    echo     "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -h127.0.0.1 -uroot -p shanwater
    echo     然后： SELECT * FROM inquiries ORDER BY id DESC LIMIT 5;
) else (
    echo   脚本已执行，但外网暂未返回 405 ^(当前探测码：%CODE%^)。
    echo   请检查：
    echo     1^) "尚水-后端" 和 "尚水-frpc" 两个窗口是否在运行、有无报错
    echo     2^) 云端 frps / Caddy 是否在跑
    echo   手动自检： curl -k https://api.shanwater.com:8443/api/inquiries  ^(期望 405^)
)
echo ============================================================
pause
