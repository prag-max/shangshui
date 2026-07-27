#!/usr/bin/env bash
# =====================================================================
#  cloud-enable-caddy.sh -- 把云端 Caddy 从"前台进程"改成 systemd 常驻服务
#  痛点：之前 cloud-run-caddy.sh 用 `caddy run` 前台跑，SSH 关窗/崩溃就挂。
#        本脚本写 /etc/systemd/system/caddy.service，实现：
#          - 开机自启 (WantedBy=multi-user.target + enable)
#          - 崩溃自动重启 (Restart=on-failure, RestartSec=5)
#  前置：已成功运行过 cloud-run-caddy.sh
#        （/usr/bin/caddy 存在、/etc/caddy/Caddyfile 与 /etc/caddy/certs/ 就位）
#  用法：sudo bash cloud-enable-caddy.sh
# =====================================================================
set -uo pipefail

CADDY_BIN="/usr/bin/caddy"
CADDYFILE="/etc/caddy/Caddyfile"

# ---- 0. 必须 root ----
if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: 请用 root 运行：sudo bash cloud-enable-caddy.sh" >&2
  exit 1
fi

# ---- 1. 前置检查 ----
if [ ! -x "$CADDY_BIN" ]; then
  echo "ERROR: 未找到可执行 $CADDY_BIN，请先运行 cloud-run-caddy.sh 安装 Caddy" >&2
  exit 1
fi
if [ ! -f "$CADDYFILE" ]; then
  echo "ERROR: 未找到 $CADDYFILE，请先运行 cloud-run-caddy.sh 部署 Caddyfile" >&2
  exit 1
fi
echo "==> 前置检查通过：Caddy=$CADDY_BIN  Caddyfile=$CADDYFILE"

# ---- 2. 停掉可能正在前台跑的 caddy，避免端口冲突 (8443) ----
echo "==> 检查是否有前台 Caddy 进程"
PIDS=$(pgrep -f "caddy run --config" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  echo "    发现前台 caddy 进程：[$PIDS]，先停止它"
  kill $PIDS 2>/dev/null || true
  sleep 2
  PIDS2=$(pgrep -f "caddy run --config" 2>/dev/null || true)
  if [ -n "$PIDS2" ]; then
    echo "    仍未退出，强制结束 [$PIDS2]"
    kill -9 $PIDS2 2>/dev/null || true
  fi
  echo "    前台 caddy 已停止"
else
  echo "    未发现前台 caddy 进程，无需停止"
fi

# ---- 3. 写 systemd 服务 ----
echo "==> 写 /etc/systemd/system/caddy.service"
tee /etc/systemd/system/caddy.service >/dev/null <<EOF
[Unit]
Description=Caddy reverse proxy for shanwater API (api.shanwater.com:8443)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=$CADDY_BIN run --config $CADDYFILE
ExecReload=$CADDY_BIN reload --config $CADDYFILE
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
User=root
WorkingDirectory=/etc/caddy

[Install]
WantedBy=multi-user.target
EOF

# ---- 4. 重载并启用 ----
echo "==> 重载 systemd 并启动 caddy (enable --now)"
systemctl daemon-reload
systemctl enable --now caddy

echo ""
echo "==> 完成。Caddy 现已由 systemd 托管："
echo "    查看状态 : sudo systemctl status caddy"
echo "    实时日志 : sudo journalctl -u caddy -f"
echo "    手动重启 : sudo systemctl restart caddy"
echo "    验证端点 : curl -k https://api.shanwater.com:8443/api/inquiries   (期望返回 405)"
echo ""
echo "==> 至此云端两条链路均为常驻："
echo "    - frps  : systemctl status frps   (enable 自动重启)"
echo "    - caddy : systemctl status caddy  (enable 自动重启)"
echo "    服务器重启/进程崩溃后都会自动拉起，无需人工干预。"
