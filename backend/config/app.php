<?php

return [

    'name' => env('APP_NAME', 'Laravel'),

    'env' => env('APP_ENV', 'production'),

    'debug' => (bool) env('APP_DEBUG', false),

    'url' => env('APP_URL', 'http://localhost'),

    'asset_url' => env('ASSET_URL'),

    'timezone' => 'Asia/Shanghai',

    'locale' => 'zh_CN',

    'fallback_locale' => 'en',

    'faker_locale' => 'zh_CN',

    'key' => env('APP_KEY'),

    'cipher' => 'AES-256-CBC',

    'maintenance' => [
        'driver' => 'file',
    ],

    'providers' => [
        //
    ],

    'bootstrap' => bootstrap_providers_path(),

    'aliases' => Illuminate\Support\Fluent::make([]),

];
