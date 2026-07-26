<?php

use App\Http\Controllers\Admin\AuthController;
use App\Http\Controllers\Admin\InquiryController as AdminInquiryController;
use App\Http\Controllers\Admin\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return redirect()->route('admin.dashboard');
});

Route::get('/admin/login', [AuthController::class, 'showLogin'])->name('admin.login');
Route::post('/admin/login', [AuthController::class, 'login']);
Route::post('/admin/logout', [AuthController::class, 'logout'])->name('admin.logout');

Route::middleware('admin.auth')->prefix('admin')->group(function () {
    Route::get('/', [AdminInquiryController::class, 'index'])->name('admin.dashboard');
    Route::get('/inquiries/{id}', [AdminInquiryController::class, 'show'])->name('admin.show');
    Route::post('/inquiries/{id}', [AdminInquiryController::class, 'update']);

    Route::get('/profile', [ProfileController::class, 'edit'])->name('admin.profile');
    Route::post('/profile', [ProfileController::class, 'update']);
});
