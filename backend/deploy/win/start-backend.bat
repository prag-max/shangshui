@echo off
setlocal

REM =====================================================================
REM  尚水数字 - 本机 Windows 后端启动脚本
REM  作用：把 Laravel 后端跑在本机 127.0.0.1:8000，供 frpc 转发到公网。
REM  链路：EdgeOne 官网 -> frps 公网端口 -> 本机 frpc -> 这个后端 -> 本机 MySQL
REM =====================================================================

REM --- PHP 可执行文件路径（按需修改）---
set "PHP_BIN=G:\360Downloads\Software\php\php.exe"
if not exist "%PHP_BIN%" set "PHP_BIN=php"

REM --- 监听地址与端口 ---
REM 只被本机 frpc 访问，绑 127.0.0.1 即可（更安全）。
set "BIND=127.0.0.1:8000"

REM --- 进入 backend 目录（脚本在 backend\deploy\win\ 下）---
cd /d "%~dp0..\.."

echo [1/3] 生成配置/路由缓存 ...
"%PHP_BIN%" artisan config:cache
"%PHP_BIN%" artisan route:cache

echo [2/3] 检查数据库连接 ...
"%PHP_BIN%" artisan migrate --force

echo [3/3] 启动后端： http://%BIND%  (Ctrl+C 停止)
echo     公网访问由 frpc 转发，勿关闭此窗口。
"%PHP_BIN%" -S %BIND% -t public server.php

endlocal
