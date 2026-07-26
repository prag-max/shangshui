# 尚水数字 · 预约演示 / 咨询表单后端与管理后台

基于 **Laravel 11 (PHP 8.2+)** 的轻量后端，包含：

- 公开 API `POST /api/inquiries`：接收官网联系表单提交，含 CORS、限流、隐藏 honeypot 防机器人、服务端校验与清洗。
- 管理后台（部署在 `admin.shanwater.com`）：Session 登录鉴权，列表分页 / 排序 / 关键字搜索、详情查看、状态流转与备注。

## 目录结构

```
backend/
├── app/
│   ├── Http/Controllers/Api/InquiryController.php   # 公开提交接口
│   ├── Http/Controllers/Admin/                      # 登录 / 列表 / 详情 / 改密
│   ├── Http/Middleware/AdminAuthenticate.php       # admin.auth 中间件
│   └── Models/{Inquiry,Admin}.php
├── config/            # app/database/session/cors/...
├── database/migrations/   # inquiries、admins 建表
├── database/seeders/      # 从 .env 种子化默认管理员
├── resources/views/admin/ # Blade 后台页面
├── routes/{web,api}.php
├── Dockerfile / docker-compose.yml / nginx.conf
└── .env.example
```

## 部署步骤（目标服务器）

1. 安装 PHP 8.2+ 与 Composer，扩展：`pdo_mysql`、`mbstring`、`openssl`、`tokenizer`、`xml`、`ctype`、`json`、`bcmath`、`zip`。
2. 拉取代码：
   ```bash
   cd /path/to/backend
   composer install --no-dev --optimize-autoloader
   cp .env.example .env
   php artisan key:generate
   ```
3. 编辑 `.env`，填入：
   - `DB_*`：你的已有 MySQL 连接信息。
   - `CORS_ALLOWED_ORIGINS`：官网来源，如 `https://www.shanwater.com,https://shanwater.com`。
   - `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `ADMIN_NAME`：首个管理员账号。
   - `API_RATE_LIMIT`：每 IP 每分钟最大提交次数（默认 5）。
4. 建库与建表、写入默认管理员：
   ```bash
   php artisan migrate --seed
   ```
5. 配置 Web 服务器（nginx 示例见 `nginx.conf`）指向 `public/`，并配置 `admin.shanwater.com` 域名与 HTTPS。
6. 访问 `https://admin.shanwater.com/admin/login` 登录；登录后请到「修改密码」改掉默认密码。

## Docker 方式（可选）

```bash
docker compose up -d --build
# 进入容器初始化
docker compose exec app sh -c "cp .env.example .env && php artisan key:generate && php artisan migrate --seed"
# 浏览器访问 http://<服务器IP>:8080
```

> MySQL 使用你已有的实例，docker-compose 仅包含 PHP-FPM 应用与 nginx 反代。

## 前端接线

官网 `website/contact.html` 表单已改为 `fetch` 提交到 `https://admin.shanwater.com/api/inquiries`，
并包含隐藏 honeypot 字段。如后台部署在其他域名，请修改 `contact.html` 中 `API` 常量。

## 常见问题

### `composer install` 被安全公告阻断

当前仓库未提交 `composer.lock`。首次部署时，如果 Laravel 11 的某个版本被 Packagist 安全公告标记，Composer 2.7+ 默认会阻止安装。已在 `composer.json` 中设置：

```json
"config": {
    "policy": {
        "advisories": {
            "block": false
        }
    }
}
```

这允许继续安装，但建议部署后立即执行：

```bash
composer audit
composer update
```

并在测试通过后把生成的 `composer.lock` 提交到仓库，后续生产环境使用 `composer install --no-dev`（不再做依赖解析，也不会被安全公告阻断）。

### 生产环境建议

- 使用 HTTPS。
- 将 `APP_ENV=production`、`APP_DEBUG=false`。
- 数据库连接使用独立账号并限制权限。
- 定期执行 `composer audit` 与框架升级。

### `composer install` 提示 "The zip extension and unzip/7z commands are both missing"

说明当前 PHP 没有启用 `zip` 扩展，且系统找不到 `unzip`/`7z` 命令。Windows 下最快的修复是启用 PHP zip 扩展：

1. 打开命令行输出的 `php.ini`（如 `G:\xxx\php\php.ini`）。
2. 找到 `;extension=zip`，去掉前导分号改为 `extension=zip`。
3. 确认同目录 `ext\php_zip.dll` 存在；若不存在，需下载对应 PHP 版本的 zip DLL 放到 `ext\` 下。
4. 保存配置，**重新打开命令行窗口**。
5. 验证：`php -m | findstr zip`（Windows）或 `php -m | grep zip`（Linux/macOS）。
6. 重新执行 `composer install --no-dev --optimize-autoloader`。

Linux 服务器上也可直接安装系统包解决，例如：
```bash
# Debian/Ubuntu
sudo apt-get install php-zip unzip
# CentOS/RHEL
sudo yum install php-zip unzip
```

## 接口说明

`POST /api/inquiries`（表单 `multipart/form-data` 或 `application/x-www-form-urlencoded`）

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| name | 是 | 称呼，≤50 |
| company | 是 | 单位名称，≤100 |
| phone | 是 | 手机号或固话 |
| email | 否 | 邮箱 |
| user_scale | 否 | 用水用户规模 |
| requirement | 否 | 需求描述 |
| website / company_url | 否 | 隐藏 honeypot，正常用户不会填 |

成功返回 `201 {"message": "...", "id": 1}`；校验失败返回 `422`；限流返回 `429`。
