#!/usr/bin/env bash
# =============================================================
# 日常更新脚本：拉取最新代码 + 依赖 + 迁移 + 刷新缓存
# 用法: sudo bash update.sh
# =============================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/shanwater/backend}"
cd "$APP_DIR"

echo "==> 拉取最新代码"
git -C /var/www/shanwater pull --ff-only

echo "==> 安装依赖"
composer install --no-dev --optimize-autoloader --no-interaction

echo "==> 数据库迁移"
php artisan migrate --force

echo "==> 刷新缓存"
php artisan config:cache
php artisan route:cache
php artisan view:cache

chown -R www-data:www-data "$APP_DIR/storage" "$APP_DIR/bootstrap/cache"
systemctl reload php8.3-fpm

echo "✅ 更新完成"
