#!/usr/bin/env bash
# =============================================================
# 尚水数字后台 — Ubuntu 24.04 一键生产部署脚本
# 用法: sudo bash install.sh
# 前提: 代码已放在 /var/www/shanwater/backend (见 DEPLOY.md 第 1 步)
# =============================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/shanwater/backend}"
DB_NAME="${DB_NAME:-shanwater}"
DB_USER="${DB_USER:-shanwater}"
PHP_VER="8.3"

if [ "$(id -u)" -ne 0 ]; then echo "请用 sudo 运行"; exit 1; fi
if [ ! -f "$APP_DIR/artisan" ]; then echo "未找到 $APP_DIR/artisan，请先上传代码（见 DEPLOY.md）"; exit 1; fi

echo "==> [1/7] 安装系统依赖 (nginx / php${PHP_VER}-fpm / mysql / composer)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y nginx mysql-server composer git unzip \
  php${PHP_VER}-fpm php${PHP_VER}-mysql php${PHP_VER}-xml php${PHP_VER}-mbstring \
  php${PHP_VER}-curl php${PHP_VER}-zip php${PHP_VER}-bcmath php${PHP_VER}-intl

systemctl enable --now nginx mysql php${PHP_VER}-fpm

echo "==> [2/7] 配置 MySQL 数据库与专用账号"
read -rsp "为数据库用户 ${DB_USER} 设置密码: " DB_PASS; echo
mysql <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

echo "==> [3/7] 配置 .env"
cd "$APP_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
  read -rsp "设置后台管理员 (admin@sum-water.com) 登录密码: " ADMIN_PASS; echo
  sed -i "s|^DB_HOST=.*|DB_HOST=127.0.0.1|" .env
  sed -i "s|^DB_DATABASE=.*|DB_DATABASE=${DB_NAME}|" .env
  sed -i "s|^DB_USERNAME=.*|DB_USERNAME=${DB_USER}|" .env
  sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=${DB_PASS}|" .env
  sed -i "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=${ADMIN_PASS}|" .env
else
  echo "  .env 已存在，跳过生成（如需重置请手动编辑）"
fi

echo "==> [4/7] 安装 PHP 依赖 (composer install --no-dev)"
sudo -u www-data composer install --no-dev --optimize-autoloader --no-interaction || \
  composer install --no-dev --optimize-autoloader --no-interaction

echo "==> [5/7] 初始化应用（APP_KEY / 迁移 / 种子）"
php artisan key:generate --force
php artisan migrate --seed --force
php artisan config:cache
php artisan route:cache
php artisan view:cache

echo "==> [6/7] 目录权限"
chown -R www-data:www-data "$APP_DIR"
chmod -R 775 "$APP_DIR/storage" "$APP_DIR/bootstrap/cache"

echo "==> [7/7] 配置 nginx（阶段一：IP 直连，80 端口）"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed "s|__APP_DIR__|${APP_DIR}|g; s|__PHP_VER__|${PHP_VER}|g" \
  "$SCRIPT_DIR/nginx-ip.conf" > /etc/nginx/sites-available/shanwater-admin
ln -sf /etc/nginx/sites-available/shanwater-admin /etc/nginx/sites-enabled/shanwater-admin
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

if command -v ufw >/dev/null 2>&1; then
  ufw allow 'Nginx Full' >/dev/null 2>&1 || true
  ufw allow OpenSSH >/dev/null 2>&1 || true
fi

IP=$(hostname -I | awk '{print $1}')
echo
echo "============================================================"
echo "✅ 部署完成（阶段一：IP 访问）"
echo "   后台登录:  http://${IP}/admin/login"
echo "   API 端点:  http://${IP}/api/inquiries"
echo "   管理员:    admin@sum-water.com（密码为刚才输入的值）"
echo
echo "备案通过后执行:  sudo bash deploy/enable-https.sh"
echo "即可切换到 https://admin.shanwater.com"
echo "============================================================"
