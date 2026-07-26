<?php

namespace Database\Seeders;

use App\Models\Admin;
use Illuminate\Database\Seeder;

class AdminSeeder extends Seeder
{
    public function run(): void
    {
        $email = env('ADMIN_EMAIL', 'admin@example.com');
        $password = env('ADMIN_PASSWORD', 'password');
        $name = env('ADMIN_NAME', '管理员');

        Admin::updateOrCreate(
            ['email' => $email],
            ['name' => $name, 'password' => $password]
        );
    }
}
