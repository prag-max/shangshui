# 尚水数字后台 — Ubuntu 24.04 生产部署指南

架构：静态官网托管在 EdgeOne Makers（`www.shanwater.com`），后端（表单 API + 管理后台）部署在这台 Ubuntu 服务器，目标域名 `admin.shanwater.com`。

由于域名**备案尚未完成**，部署分两个阶段：

| 阶段 | 访问方式 | 状态 |
|---|---|---|
| 阶段一（现在） | `http://服务器IP/admin/login` | 后台可用；官网表单暂不联通（见下方"混合内容"说明） |
| 阶段二（备案通过后） | `https://admin.shanwater.com` | 全部联通，正式上线 |

---

## 阶段一：立即部署（IP 访问）

### 1. 上传代码到服务器

私有仓库，二选一：

**方式 A — git clone（推荐，便于后续更新）**
```bash
sudo mkdir -p /var/www && cd /var/www
sudo git clone https://<你的GitHub用户名>:<PAT>@github.com/prag-max/shangshui.git shanwater
# clone 后清除 URL 中的 token：
cd shanwater && sudo git remote set-url origin https://github.com/prag-max/shangshui.git
```

**方式 B — 本机 scp 上传**
```powershell
scp -r C:\Users\lenovo\WorkBuddy\2026-07-15-15-40-07\website root@<服务器IP>:/var/www/shanwater
```

### 2. 运行一键部署脚本

```bash
cd /var/www/shanwater/backend/deploy
sudo bash install.sh
```

脚本会自动完成：安装 nginx + PHP 8.3-FPM + MySQL 8 + Composer → 建库建专用账号（`shanwater`，不用 root）→ 生成 `.env` → `composer install` → 迁移 + 管理员种子 → 权限 → nginx 站点 → 防火墙。过程中会提示你输入 **数据库密码** 和 **后台管理员密码**。

### 3. 验证

```bash
# 后台（浏览器）
http://<服务器IP>/admin/login    # admin@sum-water.com + 你设置的密码

# API（命令行模拟一次表单提交）
curl -X POST http://<服务器IP>/api/inquiries \
  -H "Content-Type: application/json" \
  -d '{"name":"测试","company":"测试水司","phone":"13800138000","email":"test@example.com","requirement":"部署验证"}'
```

提交成功后在后台列表（或 Navicat 连服务器库）应能看到该记录，验证后可在后台删除或标记关闭。

### ⚠️ 阶段一的"混合内容"限制

官网托管在 EdgeOne 是 **HTTPS**，浏览器禁止 HTTPS 页面向 `http://IP` 发请求（Mixed Content），所以**官网表单要等阶段二 HTTPS 就绪后才能正式联通**。阶段一期间：

- 后台管理、API 本身均可正常使用（curl / 直接访问）；
- 如急需收单，可临时在 contact.html 展示电话/微信二维码引导联系（目前页面已有）。

---

## 阶段二：备案通过后（正式上线）

### 1. DNS 解析
在域名服务商添加记录：`admin.shanwater.com` → A 记录 → 服务器公网 IP。

### 2. 一键切换域名 + HTTPS

```bash
cd /var/www/shanwater/backend/deploy
sudo bash enable-https.sh
```

自动完成：切换 nginx 到域名配置 → certbot 签发 Let's Encrypt 免费证书（自动续期）→ 强制 HTTPS 跳转 → 更新 APP_URL。

### 3. 确认前端联通
`contact.html` 的 API 常量已是 `https://admin.shanwater.com`，无需修改；`.env` 的 `CORS_ALLOWED_ORIGINS` 已包含 `https://www.shanwater.com,https://shanwater.com`。在官网提交一次表单验证闭环。

---

## 日常运维

### 更新代码
```bash
sudo bash /var/www/shanwater/backend/deploy/update.sh
```

### 用 Navicat 连生产数据库（推荐 SSH 通道，勿开放 3306 公网）
Navicat Premium 12 新建 MySQL 连接：
- 「常规」页：主机 `127.0.0.1`，端口 `3306`，用户 `shanwater`，密码为部署时设置的数据库密码
- 「SSH」页：勾选"使用 SSH 通道"，填服务器 IP / SSH 端口 22 / 服务器登录用户和密码（或私钥）

### 数据备份（建议加 crontab）
```bash
mysqldump -ushanwater -p shanwater > /var/backups/shanwater_$(date +%F).sql
```

### 常见问题
- **502 Bad Gateway**：`systemctl status php8.3-fpm`，多为 fpm 未启动或 sock 路径不符。
- **500 错误**：`tail -50 /var/www/shanwater/backend/storage/logs/laravel.log`。
- **改了 .env 不生效**：执行 `php artisan config:cache`。
- **服务器在境外（香港等）**：无需备案，可直接跳到阶段二。
