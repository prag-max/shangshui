# 尚水数字 — 本机 Windows 后端 + frp 内网穿透 部署指南

## 链路总览

```
访客浏览器
   │  填表提交
   ▼
EdgeOne 静态官网 (https://www.shanwater.com)  —— contact.html 里的 JS
   │  跨域 fetch POST /api/inquiries
   ▼
云服务器公网地址 (frps)   ← 你有公网 IP 的那台机器
   │  frp 隧道
   ▼
本机 Windows (frpc → 127.0.0.1:8000 Laravel 后端)
   │
   ▼
本机 MySQL (127.0.0.1:3306 / 库 shanwater)
```

分两个阶段推进：

| 阶段 | 目标 | 对外地址 | 备案 |
| --- | --- | --- | --- |
| **Phase 1** | 打通隧道，验证能写进本机 MySQL | `http://<云IP>:18000`（curl 测） | 高端口，不涉及 80/443，无需备案 |
| **Phase 2** | 让 EdgeOne 上的线上表单真正联通 | `https://api.shanwater.com:8443` | 子域名 + DNS-01 证书 + 8443 高端口，不用备案 |

> ⚠️ 关键约束：官网是 **HTTPS**。浏览器禁止 HTTPS 页面向 `http://` 后端发请求（Mixed Content）。所以 **Phase 1 的 http 高端口只能用 curl 验证，线上表单必须等 Phase 2 的 https 才会通**。这与"先不启用 api.shanwater.com"的安排一致：先验证链路，再挂域名上线。

---

## 一、本机 Windows：跑起后端

前置：本机已装 PHP 8.2（`G:\360Downloads\Software\php\php.exe`）、MySQL 8（库 `shanwater` 已建、`.env` 已配好本机库）。

```bat
REM 双击或在 cmd 里执行：
website\backend\deploy\win\start-backend.bat
```

脚本会：生成配置缓存 → 跑迁移 → 在 `127.0.0.1:8000` 启动 Laravel。保持窗口开着。

自测（新开一个 cmd）：

```bat
curl http://127.0.0.1:8000/api/inquiries -X POST ^
  -H "Accept: application/json" ^
  -F "name=本机自测" -F "company=测试水司" -F "phone=13800138000" ^
  -F "email=test@example.com" -F "requirement=本机后端验证"
```

返回 `201` 且 Navicat 里 `inquiries` 表新增一行，即本机后端 OK。

---

## 二、云服务器：跑 frps

在有公网 IP 的云服务器（Linux）上：

```bash
# 1. 下载 frp（示例 v0.61.1，按需换版本/架构）
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_amd64.tar.gz
tar -xf frp_0.61.1_linux_amd64.tar.gz && cd frp_0.61.1_linux_amd64

# 2. 用本仓库的 frps.toml（deploy/frp/frps.toml），改好 token
#    把 CHANGE_ME_TO_A_LONG_RANDOM_TOKEN 换成一长串随机字符串

# 3. 前台先跑通看日志
./frps -c frps.toml
```

安全组/防火墙放行：`7000`（frp 控制）、`18000`（隧道对外）、`7500`（面板，可选）。

常驻（systemd）：

```ini
# /etc/systemd/system/frps.service
[Unit]
Description=frp server
After=network.target
[Service]
ExecStart=/opt/frp/frps -c /opt/frp/frps.toml
Restart=always
[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now frps
```

---

## 三、本机 Windows：跑 frpc（连上 frps）

```powershell
# 在 website\backend\deploy\frp 目录下
powershell -ExecutionPolicy Bypass -File get-frpc.ps1   # 下载 bin\frpc.exe
# 编辑 frpc.toml：serverAddr 填云服务器公网IP、auth.token 与 frps 一致
bin\frpc.exe -c frpc.toml
```

看到 `start proxy success` 即隧道建立。

---

## 四、Phase 1 验证（http 高端口，用 curl）

从任意机器（此时 frps.toml 的 `proxyBindAddr` 保持 `0.0.0.0`）：

```bash
curl http://<云服务器公网IP>:18000/api/inquiries -X POST \
  -H "Accept: application/json" \
  -F "name=穿透验证" -F "company=测试水司" -F "phone=13800138000" \
  -F "email=test@example.com" -F "requirement=frp链路验证"
```

返回 `201` → 说明 **公网 → frps → frpc → 本机后端 → 本机 MySQL** 全链路已通。Navicat 里能查到这条记录。

> 此时线上 `www.shanwater.com` 的表单还不会通（HTTPS 页面不能打 http），属预期。继续 Phase 2。

---

## 五、Phase 2 上线（https 子域名，让线上表单联通）

### 1. DNS 解析

在域名服务商给 `api.shanwater.com` 加 **A 记录 → 云服务器公网 IP**。（仅解析，不需要备案；因为我们只用 8443 高端口，不碰 80/443。）

### 2. 收紧隧道

`frps.toml` 里取消注释 `proxyBindAddr = "127.0.0.1"`，重启 frps —— 隧道端口 18000 只对云服务器本机开放，交给 Caddy 反代。

### 3. 用 DNS-01 签发证书（不需要 80 端口/备案）

以 acme.sh 为例（DNS 提供商 API 令牌按你的服务商填）：

```bash
curl https://get.acme.sh | sh
# 例：DNSPod / 阿里云 / Cloudflare，各自导出对应环境变量后：
acme.sh --issue --dns dns_dp -d api.shanwater.com
acme.sh --install-cert -d api.shanwater.com \
  --cert-file  /etc/caddy/certs/api.shanwater.com.cer \
  --key-file   /etc/caddy/certs/api.shanwater.com.key
```

### 4. 用 Caddy 在 8443 终结 HTTPS

用本仓库 `deploy/frp/Caddyfile`（已指向上面证书路径、反代 `127.0.0.1:18000`）：

```bash
caddy run --config /etc/caddy/Caddyfile
```

对外地址即 `https://api.shanwater.com:8443`。安全组放行 `8443`。

### 5. 前端已就绪

`contact.html` 里 API 已设为 `https://api.shanwater.com:8443`（非本机访问时自动用它）。EdgeOne 重新发布官网后，在线上填一次表单，返回成功且本机 MySQL 出现新记录 → 全链路上线完成。

`.env` 的 `CORS_ALLOWED_ORIGINS` 已放行 `https://www.shanwater.com,https://shanwater.com`；改动后执行 `php artisan config:cache`。

---

## 常见问题

- **线上表单报"网络错误"**：多为 Phase 2 未完成（还在 http 阶段）或证书不被信任 / 端口未放行 / CORS 未放行来源。用浏览器 F12 看 Console 的具体报错。
- **curl 通但浏览器不通**：CORS。确认 `.env` 放行了 `https://www.shanwater.com` 并 `config:cache`。
- **隧道断**：本机 frpc 窗口不能关；建议用 nssm 把 frpc.exe 与后端注册成 Windows 服务常驻。
- **端口冲突**：本机 8000 被占用时，改 `start-backend.bat` 的 BIND 与 `frpc.toml` 的 localPort。
- **改证书端口**：若你后续完成备案，可把 Caddy 换到 443、`contact.html` 的 API 去掉 `:8443`。
