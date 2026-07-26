FROM php:8.2-fpm-alpine

WORKDIR /var/www/html

# MySQL PDO 扩展（连接你的已有 MySQL 需要）
RUN docker-php-ext-install pdo_mysql

# 安装 Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

COPY . .

RUN composer install --no-dev --optimize-autoloader

RUN chown -R www-data:www-data storage bootstrap/cache

EXPOSE 9000
