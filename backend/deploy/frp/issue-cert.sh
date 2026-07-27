#!/usr/bin/env bash
# =====================================================================
#  issue-cert.sh -- 云端用 DNS-01 给 api.shanwater.com 签发 HTTPS 证书
#  关键：DNS-01 不需要 80/443 端口，国内未备案也能签。
#  用法（在云服务器 43.139.72.9 上，普通用户运行，不要用 sudo 包整个脚本）：
#    export DP_ID="你的数字ID"
#    export DP_TOKEN="你的Token"
#    bash issue-cert.sh
#  签发后证书在 /etc/caddy/certs/，Caddyfile 直接引用。
# =====================================================================
set -uo pipefail

DOMAIN=api.shanwater.com
CERT_DIR=/etc/caddy/certs
ACME_HOME="${HOME}/.acme.sh"

# ---- 0. 禁止用 sudo 跑整个脚本 ----
if [ "$(id -u)" -eq 0 ]; then
  echo "ERROR: 请不要用 root / sudo 运行整个脚本。" >&2
  echo "       请用普通用户执行：export DP_ID=... DP_TOKEN=... && bash issue-cert.sh" >&2
  exit 1
fi

# ---- 1. 选择 DNS 服务商（默认 DNSPod/腾讯云）----
# acme.sh 的 dns_dp 插件只认 DP_Id / DP_Key，但用户习惯用 DP_ID / DP_TOKEN，
# 这里同时兼容：读取 DP_ID/DP_TOKEN，然后映射成 acme.sh 需要的大小写。
export DP_ID="${DP_ID:-填你的DNSPod_ID}"
export DP_TOKEN="${DP_TOKEN:-填你的DNSPod_TOKEN}"

if [ "${DP_ID}" = "填你的DNSPod_ID" ]; then
  echo "ERROR: 请先 export DP_ID / DP_TOKEN（或改脚本里的 DNS 服务商）" >&2
  exit 1
fi

export DP_Id="${DP_ID}"
export DP_Key="${DP_TOKEN}"

# ---- 2. 清理之前 sudo 造成的权限混乱 ----
# /tmp/acme.sh 若被 root 创建过，普通用户无法覆盖，先用 sudo 清掉
if [ -e /tmp/acme.sh ] && [ ! -w /tmp/acme.sh ]; then
  echo "==> 清理 /tmp/acme.sh 的 root 残留权限"
  sudo rm -rf /tmp/acme.sh
fi
rm -rf /tmp/acme.sh 2>/dev/null || sudo rm -rf /tmp/acme.sh

# ~/.acme.sh 若被 root 创建过，也清掉重来
if [ -e "$ACME_HOME" ] && [ ! -w "$ACME_HOME" ]; then
  echo "==> 清理 $ACME_HOME 的 root 残留权限"
  sudo rm -rf "$ACME_HOME"
fi
sudo rm -rf "$ACME_HOME" 2>/dev/null || rm -rf "$ACME_HOME" 2>/dev/null

# ---- 3. 安装 acme.sh（完全绕过 /tmp，git clone 到 $HOME 后安装）----
# 说明：get.acme.sh 在线安装脚本会在 /tmp 创建 master.tar.gz；这台云服务器 /tmp
#       被之前 sudo 操作污染，普通用户无法写入。故改为 git clone 到 $HOME，
#       完全在 $HOME 内完成安装。
echo "==> 安装 acme.sh 到 $ACME_HOME"
install_acmesh_git() {
  local url=$1 label=$2
  cd "$HOME" || exit 1
  echo "==> 尝试 $label git clone ..."
  rm -rf "$HOME/acme.sh.git"
  if git clone --depth 1 "$url" "$HOME/acme.sh.git" 2>/tmp/git.err; then
    cd "$HOME/acme.sh.git" && ./acme.sh --install --home "$ACME_HOME"
    return $?
  fi
  echo "    git 失败: $(cat /tmp/git.err 2>/dev/null | tail -3)"
  return 1
}

if install_acmesh_git "https://github.com/acmesh-official/acme.sh.git" "GitHub"; then
  echo "==> GitHub git 安装成功"
elif install_acmesh_git "https://gitee.com/neilpang/acme.sh.git" "Gitee"; then
  echo "==> Gitee git 安装成功"
else
  echo "ERROR: acme.sh 安装失败。" >&2
  echo "       建议在本机浏览器打开 https://github.com/acmesh-official/acme.sh 下载源码 zip，" >&2
  echo "       用 WinSCP 传到云服务器 $HOME/acme.sh-source/ 后手动执行 ./acme.sh --install --home $ACME_HOME" >&2
  exit 1
fi

if [ ! -x "$ACME_HOME/acme.sh" ]; then
  echo "ERROR: acme.sh 未安装到 $ACME_HOME/acme.sh" >&2
  exit 1
fi
source "$ACME_HOME/acme.sh.env" 2>/dev/null || true

# ---- 4. 预检：用 DP 账号实际登录 DNSPod（这才是真 API 连通性）----
echo "==> 预检：DNSPod API 账号可用性"
DP_CHECK=$(curl -fsS --connect-timeout 10 --max-time 30 -X POST \
  -d "login_token=${DP_Id},${DP_Key}&format=json" \
  "https://dnsapi.cn/Domain.List" 2>/dev/null | head -c 200)
if echo "$DP_CHECK" | grep -q '"code":"1"'; then
  echo "    DNSPod API 账号验证通过"
elif echo "$DP_CHECK" | grep -q '"code":"-1"'; then
  echo "    ERROR: DNSPod API 返回登录失败，请检查 DP_ID / DP_TOKEN" >&2
  echo "    返回: $DP_CHECK" >&2
  exit 1
else
  echo "    WARN: DNSPod API 探测异常（返回: $DP_CHECK），继续尝试签发..."
fi

# ---- 5. 签发证书（DNS-01），日志落盘 ----
echo "==> 签发 $DOMAIN （DNS-01），日志见 /tmp/acme-issue.log"
if ! "$ACME_HOME/acme.sh" --issue --dns dns_dp -d "$DOMAIN" --server letsencrypt --debug 2 2>&1 | tee /tmp/acme-issue.log; then
  echo "ERROR: 证书签发失败，请查看 /tmp/acme-issue.log" >&2
  exit 1
fi

# ---- 6. 安装到 Caddy 目录（写 /etc 需要 root，这里才用 sudo）----
echo "==> 复制证书到 $CERT_DIR"
sudo mkdir -p "$CERT_DIR"
if ! sudo -E "$ACME_HOME/acme.sh" --install-cert -d "$DOMAIN" \
  --cert-file      "$CERT_DIR/$DOMAIN.cer" \
  --key-file       "$CERT_DIR/$DOMAIN.key" \
  --fullchain-file "$CERT_DIR/$DOMAIN.fullchain.cer" \
  --reloadcmd     "systemctl reload caddy || true" 2>&1 | tee -a /tmp/acme-issue.log; then
  echo "ERROR: 证书安装到 $CERT_DIR 失败" >&2
  exit 1
fi

echo ""
echo "==> 完成。证书位置："
ls -l "$CERT_DIR/$DOMAIN".* 2>/dev/null || echo "    未检测到证书文件"
