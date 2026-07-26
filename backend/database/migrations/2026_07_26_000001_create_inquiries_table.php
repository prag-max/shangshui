<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('inquiries', function (Blueprint $table) {
            $table->id();
            $table->string('name', 50)->comment('姓名');
            $table->string('company', 100)->comment('单位名称');
            $table->string('phone', 20)->comment('联系电话');
            $table->string('email', 100)->nullable()->comment('邮箱');
            $table->string('user_scale', 50)->nullable()->comment('用水用户规模');
            $table->text('requirement')->nullable()->comment('需求描述');
            $table->string('ip', 45)->nullable()->comment('提交IP');
            $table->string('referer', 255)->nullable()->comment('来源页');
            $table->string('status', 20)->default('pending')->comment('pending/contacted/won/closed');
            $table->text('admin_note')->nullable()->comment('管理员备注');
            $table->timestamps();
            $table->index('status');
            $table->index('created_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('inquiries');
    }
};
