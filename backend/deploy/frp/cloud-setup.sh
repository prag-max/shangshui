#!/usr/bin/env bash
# =====================================================================
#  cloud-setup.sh —— 云服务器 frps 一键部署（Ubuntu/Debian 验证通过）
#  用法：
#    1) 把本脚本、frps 二进制、frps.toml 放到同一目录（或已就位在 /opt/frp）
#    2) chmod +x cloud-setup.sh
#    3) sudo bash cloud-setup.sh
#  说明：
#    - 若当前目录有 ./frps 就直接用；否则自动下载 v0.61.1（与 Windows 端 frpc 同版本）
#    - 会自动写 systemd 服务 + 放行 7000/18000/7500 + 启动
#    - Tencent Cloud 等还需在【控制台安全组】手动放行这三个端口（OS 防火墙之外）
# =====================================================================
set -euo pipefail

FRP_DIR=/opt/frp
FRP_VERSION=0.61.1   # 仅当本机无 frps 二进制时才用，需与 Windows 端 frpc 版本一致

# 提权处理：已是 root 就不加 sudo，否则需要 sudo
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then SUDO="sudo"; else echo "ERROR: 需要 root 权限" >&2; exit 1; fi
fi

echo "==> 1. 准备目录 $FRP_DIR"
$SUDO mkdir -p "$FRP_DIR"

# ---- 放置 frps 二进制 ----
if [ -x "./frps" ]; then
  echo "    发现本地 ./frps，复制进 $FRP_DIR"
  $SUDO cp ./frps "$FRP_DIR/frps"
elif [ -x "$FRP_DIR/frps" ]; then
  echo "    已存在 $FRP_DIR/frps，跳过"
else
  echo "    未找到 frps 二进制，开始下载 v$FRP_VERSION ..."
  ARCH=$(uname -m)
  case "$ARCH" in x86_64) A=amd64;; aarch64) A=arm64;; *) A=$ARCH;; esac
  TMP=$(mktemp -d)
  curl -fsSL "https://github.com/fatedier/frp/releases/download/v$FRP_VERSION/frp_${FRP_VERSION}_linux_${A}.tar.gz" -o "$TMP/frp.tgz"
  tar -xzf "$TMP/frp.tgz" -C "$TMP"
  $SUDO cp "$TMP/frp_${FRP_VERSION}_linux_${A}/frps" "$FRP_DIR/frps"
  rm -rf "$TMP"
fi
$SUDO chmod +x "$FRP_DIR/frps"

# ---- 放置 frps.toml ----
if [ -f "./frps.toml" ]; then
  $SUDO cp ./frps.toml "$FRP_DIR/frps.toml"
elif [ ! -f "$FRP_DIR/frps.toml" ]; then
  echo "ERROR: 找不到 frps.toml，请把它放到 $FRP_DIR 或当前目录" >&2
  exit 1
fi

# ---- 写 systemd 服务 ----
echo "==> 2. 写 systemd 服务 /etc/systemd/system/frps.service"
$SUDO tee /etc/systemd/system/frps.service >/dev/null <<EOF
[Unit]
Description=frps (shanwater tunnel server)
After=network.target

[Service]
Type=simple
ExecStart=$FRP_DIR/frps -c $FRP_DIR/frps.toml
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
EOF

# ---- 放行防火墙端口 ----
echo "==> 3. 放行端口（7000 控制 / 18000 隧道 / 7500 面板）"
if command -v ufw >/dev/null 2>&1; then
  $SUDO ufw allow 7000/tcp
  $SUDO ufw allow 18000/tcp
  $SUDO ufw allow 7500/tcp
  $SUDO ufw --force enable
  echo "    ufw 已放行 7000/18000/7500"
elif command -v firewall-cmd >/dev/null 2>&1; then
  $SUDO firewall-cmd --permanent --add-port=7000/tcp
  $SUDO firewall-cmd --permanent --add-port=18000/tcp
  $SUDO firewall-cmd --permanent --add-port=7500/tcp
  $SUDO firewall-cmd --reload
  echo "    firewalld 已放行 7000/18000/7500"
else
  echo "    未检测到 ufw/firewalld，请确认云厂商【安全组】已放行 7000/18000/7500"
fi

# ---- 启动 ----
echo "==> 4. 启动 frps"
$SUDO systemctl daemon-reload
$SUDO systemctl enable --now frps

echo ""
echo "==> 完成。"
echo "    查看状态 : sudo systemctl status frps"
echo "    查看日志 : sudo journalctl -u frps -f"
echo "    管理面板 : http://43.139.72.9:7500  (admin / 你的面板密码)"
echo "    Phase1 验证: curl http://43.139.72.9:18000/api/inquiries -X POST -H \"Origin: https://www.shanwater.com\" -F name=test -F phone=13800138000 -F email=t@e.com -F requirement=hi"
echo "    注意：若云厂商有独立安全组，务必在控制台也放行 7000/18000/7500"
