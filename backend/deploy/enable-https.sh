#!/usr/bin/env bash
# =============================================================
# 阶段二：备案通过后执行 — 绑定 admin.shanwater.com + 免费 HTTPS
# 前提: DNS 已将 admin.shanwater.com A 记录指向本服务器 IP
# 用法: sudo bash enable-https.sh
# =============================================================
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/shanwater/backend}"
DOMAIN="admin.shanwater.com"
PHP_VER="8.3"

if [ "$(id -u)" -ne 0 ]; then echo "请用 sudo 运行"; exit 1; fi

echo "==> 检查 DNS 解析"
RESOLVED=$(getent hosts "$DOMAIN" | awk '{print $1}' | head -1 || true)
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "   $DOMAIN -> ${RESOLVED:-未解析}   本机 IP: $LOCAL_IP"
if [ -z "$RESOLVED" ]; then
  echo "⚠️  域名尚未解析到本机，请先在 DNS 服务商添加 A 记录后重试。"
  exit 1
fi

echo "==> 切换 nginx 到域名配置"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed "s|__APP_DIR__|${APP_DIR}|g; s|__PHP_VER__|${PHP_VER}|g" \
  "$SCRIPT_DIR/nginx-domain.conf" > /etc/nginx/sites-available/shanwater-admin
nginx -t && systemctl reload nginx

echo "==> 安装 certbot 并签发证书（自动续期）"
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d "$DOMAIN" --redirect --non-interactive --agree-tos \
  -m sumwater888@sum-water.com

echo "==> 更新 .env 的 APP_URL 并刷新缓存"
cd "$APP_DIR"
sed -i "s|^APP_URL=.*|APP_URL=https://${DOMAIN}|" .env
php artisan config:cache

echo
echo "============================================================"
echo "✅ HTTPS 已启用: https://${DOMAIN}/admin/login"
echo "   证书由 Let's Encrypt 签发，certbot 已配置自动续期。"
echo "   请确认前端 contact.html 的 API 常量指向 https://${DOMAIN}"
echo "============================================================"
