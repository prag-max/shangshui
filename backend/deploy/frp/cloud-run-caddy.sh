#!/usr/bin/env bash
# =====================================================================
#  cloud-run-caddy.sh -- 云服务器一键安装并运行 Caddy（Phase 2 HTTPS）
#  作用：在 8443 端口对外提供 https://api.shanwater.com:8443，
#        并反代到 frps 暴露的 127.0.0.1:18000。
#  前置：证书已通过 issue-cert.sh 放到 /etc/caddy/certs/
#  用法：sudo bash cloud-run-caddy.sh
# =====================================================================
set -uo pipefail

CADDYFILE_DIR="/etc/caddy"
CERT_DIR="/etc/caddy/certs"
CADDY_BIN="/usr/bin/caddy"

# ---- 0. 必须用 root ----
if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: 请用 root 运行：sudo bash cloud-run-caddy.sh" >&2
  exit 1
fi

# ---- 1. 检查证书存在 ----
if [ ! -f "$CERT_DIR/api.shanwater.com.cer" ] || [ ! -f "$CERT_DIR/api.shanwater.com.key" ]; then
  echo "ERROR: 证书文件不存在于 $CERT_DIR/" >&2
  echo "       请先成功运行 issue-cert.sh 签发证书。" >&2
  exit 1
fi
echo "==> 证书已就绪：$CERT_DIR/api.shanwater.com.*"

# ---- 2. 安装 Caddy（若无）----
if [ ! -x "$CADDY_BIN" ]; then
  echo "==> 未检测到 Caddy，开始安装"
  # 优先使用官方一键安装脚本；国内服务器若失败会给出手动方案
  if ! curl -fsSL --connect-timeout 15 --max-time 120 https://getcaddy.com | bash -s personal; then
    echo "==> 官方脚本失败，尝试 Cloudflare 镜像 ..."
    if ! curl -fsSL --connect-timeout 15 --max-time 120 "https://mirror.ghproxy.com/https://raw.githubusercontent.com/caddyserver/getcaddy.com/master/index.txt" | bash -s personal; then
      echo "ERROR: Caddy 安装失败。请本机下载 caddy linux_amd64 二进制，" >&2
      echo "       用 WinSCP 传到 /usr/bin/caddy 并 chmod +x。" >&2
      exit 1
    fi
  fi
else
  echo "==> Caddy 已安装：$CADDY_BIN"
fi

# ---- 3. 放行 8443 端口 ----
echo "==> 放行防火墙 8443 端口"
if command -v ufw >/dev/null 2>&1; then
  ufw allow 8443/tcp >/dev/null 2>&1 || true
  echo "    ufw 8443 已放行"
elif command -v firewall-cmd >/dev/null 2>&1; then
  firewall-cmd --permanent --add-port=8443/tcp >/dev/null 2>&1 || true
  firewall-cmd --reload >/dev/null 2>&1 || true
  echo "    firewalld 8443 已放行"
fi

# ---- 4. 把 Caddyfile 放到 /etc/caddy/ ----
# 假设 Caddyfile 与本脚本在同一目录；否则请手动复制
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/Caddyfile" ]; then
  cp "$SCRIPT_DIR/Caddyfile" "$CADDYFILE_DIR/Caddyfile"
  echo "==> 已复制 Caddyfile 到 $CADDYFILE_DIR/Caddyfile"
else
  echo "WARN: 同目录未找到 Caddyfile，请确认 $CADDYFILE_DIR/Caddyfile 已存在且配置正确" >&2
fi

# ---- 5. 启动 Caddy（前台，便于看日志；Ctrl+C 停止）----
echo "==> 启动 Caddy（8443 HTTPS 反代 127.0.0.1:18000）"
echo "    如要后台常驻，请另开窗口执行："
echo "      nohup caddy run --config $CADDYFILE_DIR/Caddyfile > /tmp/caddy.log 2>&1 &"
echo ""
caddy run --config "$CADDYFILE_DIR/Caddyfile"
