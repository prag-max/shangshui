<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Admin;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;

class ProfileController extends Controller
{
    public function edit()
    {
        return view('admin.profile');
    }

    public function update(Request $request)
    {
        $admin = Admin::findOrFail(session('admin_id'));

        $data = $request->validate([
            'current_password' => ['required', 'string'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ]);

        if (! Hash::check($data['current_password'], $admin->password)) {
            return back()->withErrors(['current_password' => '当前密码不正确']);
        }

        $admin->update(['password' => $data['password']]);

        return redirect()->route('admin.profile')->with('success', '密码已修改');
    }
}
