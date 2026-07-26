<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Inquiry;
use Illuminate\Http\Request;

class InquiryController extends Controller
{
    public function store(Request $request)
    {
        // Honeypot: 正常用户看不到该隐藏字段，机器人填写后直接丢弃（假装成功）
        if (!empty($request->input('website')) || !empty($request->input('company_url'))) {
            return response()->json(['message' => 'ok'], 201);
        }

        $data = $request->validate([
            'name' => ['required', 'string', 'max:50'],
            'company' => ['required', 'string', 'max:100'],
            'phone' => ['required', 'string', 'regex:/^(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})$/'],
            'email' => ['nullable', 'email', 'max:100'],
            'user_scale' => ['nullable', 'string', 'max:50'],
            'requirement' => ['nullable', 'string', 'max:1000'],
        ], [
            'name.required' => '请填写您的称呼',
            'company.required' => '请填写单位名称',
            'phone.required' => '请填写联系电话',
            'phone.regex' => '联系电话格式不正确',
            'email.email' => '邮箱格式不正确',
        ]);

        // 服务端清洗：去除首尾空白、剥离 HTML 标签、过滤邮箱
        $clean = [
            'name' => strip_tags(trim($data['name'])),
            'company' => strip_tags(trim($data['company'])),
            'phone' => trim($data['phone']),
            'email' => !empty($data['email']) ? filter_var(trim($data['email']), FILTER_SANITIZE_EMAIL) : null,
            'user_scale' => !empty($data['user_scale']) ? strip_tags(trim($data['user_scale'])) : null,
            'requirement' => !empty($data['requirement']) ? strip_tags(trim($data['requirement'])) : null,
            'ip' => $request->ip(),
            'referer' => $request->headers->get('referer') ? mb_substr($request->headers->get('referer'), 0, 255) : null,
            'status' => Inquiry::STATUS_PENDING,
        ];

        $record = Inquiry::create($clean);

        return response()->json([
            'message' => '提交成功，我们会尽快与您联系。',
            'id' => $record->id,
        ], 201);
    }
}
