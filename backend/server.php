<?php
/**
 * Laravel 内置服务器路由脚本（Windows 生产/本机后端用）
 *
 * 作用：让 `php -S` 能正确承载 Laravel —— 存在的静态文件直接返回，
 * 其余请求全部交给 public/index.php 处理。
 *
 * 之所以不用 `php artisan serve`：本机 Windows 环境变量块超限
 * （370779 > 32767）会导致 artisan serve 起不来，改用 php 内置服务器绕过。
 *
 * 用法（在 backend/ 目录下执行）：
 *   php -S 0.0.0.0:8000 -t public server.php
 * 仅本机 + frpc 转发时也可绑 127.0.0.1：
 *   php -S 127.0.0.1:8000 -t public server.php
 */

$uri = urldecode(
    parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '/'
);

// public/ 下真实存在的静态文件（如 robots.txt、favicon）直接交给内置服务器
if ($uri !== '/' && file_exists(__DIR__ . '/public' . $uri)) {
    return false;
}

// 其余请求统一进 Laravel 前端控制器
require_once __DIR__ . '/public/index.php';
