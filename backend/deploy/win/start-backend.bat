@echo off
setlocal

REM =====================================================================
REM  尚水数字 - 本机 Windows 后端启动脚本
REM  作用：把 Laravel 后端跑在本机 127.0.0.1:8000，供 frpc 转发到公网。
REM  链路：EdgeOne 官网 -> frps 公网端口 -> 本机 frpc -> 这个后端 -> 本机 MySQL
REM
REM  注意：当前 php artisan 控制台存在「Call to a member function
REM  make() on null」缺陷（Laravel 11 内置命令经 ContainerCommandLoader
REM  懒加载时未注入容器），故本脚本直接以 php 内置服务器运行，
REM  不再依赖 artisan 的 config:cache / route:cache / migrate 命令。
REM  如需执行迁移等 artisan 命令，请先修复该控制台缺陷后再单独运行。
REM =====================================================================

REM --- PHP 可执行文件路径（按需修改）---
set "PHP_BIN=G:\360Downloads\Software\php\php.exe"
if not exist "%PHP_BIN%" set "PHP_BIN=php"

REM --- 监听地址与端口 ---
REM 只被本机 frpc 访问，绑 127.0.0.1 即可（更安全）。
set "BIND=127.0.0.1:8000"

REM --- 进入 backend 目录（脚本在 backend\deploy\win\ 下）---
cd /d "%~dp0..\.."

echo [1/2] 启动 Laravel 后端： http://%BIND%  (Ctrl+C 停止)
echo       公网访问由 frpc 转发，勿关闭此窗口。
echo.

"%PHP_BIN%" -S %BIND% -t public server.php

endlocal
