@echo off
chcp 65001 >nul
cd /d C:\Users\lenovo\WorkBuddy\2026-07-15-15-40-07\website\backend

echo ============================================
echo  修复 Laravel 依赖（vendor / autoload）
echo  注意：运行前请【完全退出 360 安全卫士】
echo ============================================
echo.
echo [1/3] 删除旧的 vendor 半成品...
rmdir /s /q vendor 2>nul
echo.

echo [2/3] 重新安装依赖（composer install）...
G:\360Downloads\Software\php\php.exe "G:\360Downloads\Software\php\composer.phar" install --no-interaction --prefer-dist
echo.

echo [3/3] 验证 autoload.php 是否生成...
if exist vendor\autoload.php (
    echo [OK] vendor\autoload.php 已生成，Laravel 依赖安装成功！
    echo       如果表单仍报错，请再在本窗口执行下面这行建表：
    echo       G:\360Downloads\Software\php\php.exe artisan migrate --force
    echo       然后回到网站测试表单提交。
) else (
    echo [失败] vendor\autoload.php 仍未生成。
    echo        请确认 360 已【完全退出】，再重跑本脚本。
)
echo.
pause
