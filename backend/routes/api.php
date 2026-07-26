<?php

use App\Http\Controllers\Api\InquiryController;
use Illuminate\Http\Middleware\HandleCors;
use Illuminate\Support\Facades\Route;

Route::post('/inquiries', [InquiryController::class, 'store'])
    ->middleware([
        HandleCors::class,
        'throttle:'.(int) env('API_RATE_LIMIT', 5).',1',
    ])
    ->name('api.inquiries.store');
