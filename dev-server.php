<?php
/**
 * 本地单源开发服务器（Windows / 本机演示用）
 *
 * 让“官网静态页”和“Laravel 后端接口”跑在【同一个源/同一个端口】，
 * 表单提交无需跨域、也完全不依赖 admin.shanwater.com。
 *
 * 用法（在 website/ 目录下执行）：
 *   php -S 127.0.0.1:8000 -t website website/dev-server.php
 *
 * 行为：
 *   /api/*   -> Laravel 接口（写库，目标为本机 MySQL）
 *   /admin/* -> Laravel 后台
 *   其余静态文件（contact.html、assets/* 等）-> 直接返回
 *   未匹配路径 -> 回退给 Laravel
 */

$uri = urldecode(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?: '/');

$laravelPrefixes = ['/api', '/admin', '/sanctum'];
foreach ($laravelPrefixes as $prefix) {
    if (strpos($uri, $prefix) === 0) {
        require __DIR__ . '/backend/public/index.php';
        return;
    }
}

// 静态文件存在则交给内置服务器直接返回
$file = __DIR__ . $uri;
if ($uri !== '/' && is_file($file)) {
    return false;
}

// 其余回退给 Laravel（如 /admin/login 深链）
require __DIR__ . '/backend/public/index.php';
