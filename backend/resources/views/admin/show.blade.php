@extends('admin.layout')
@section('title','详情')
@section('content')
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2 style="margin:0">提交详情 #{{ $item->id }}</h2>
    <a class="btn" href="{{ route('admin.dashboard') }}">← 返回列表</a>
  </div>
  <table style="margin-top:14px">
    <tr><th style="width:140px">姓名</th><td>{{ $item->name }}</td></tr>
    <tr><th>单位</th><td>{{ $item->company }}</td></tr>
    <tr><th>电话</th><td>{{ $item->phone }}</td></tr>
    <tr><th>邮箱</th><td>{{ $item->email ?? '-' }}</td></tr>
    <tr><th>用水用户规模</th><td>{{ $item->user_scale ?? '-' }}</td></tr>
    <tr><th>需求描述</th><td>{{ $item->requirement ?? '-' }}</td></tr>
    <tr><th>提交IP</th><td>{{ $item->ip ?? '-' }}</td></tr>
    <tr><th>来源页</th><td>{{ $item->referer ?? '-' }}</td></tr>
    <tr><th>提交时间</th><td>{{ $item->created_at->format('Y-m-d H:i:s') }}</td></tr>
  </table>
</div>
<div class="card">
  <h3 style="margin-top:0">跟进处理</h3>
  <form method="POST" action="{{ route('admin.show', $item->id) }}">
    @csrf
    <div class="field">
      <label>处理状态</label>
      <select name="status">
        @foreach(\App\Models\Inquiry::statusOptions() as $val => $label)
          <option value="{{ $val }}" @if($item->status===$val)selected@endif>{{ $label }}</option>
        @endforeach
      </select>
    </div>
    <div class="field">
      <label>管理员备注</label>
      <textarea name="admin_note" rows="4">{{ old('admin_note', $item->admin_note) }}</textarea>
    </div>
    <button class="btn btn-primary">保存</button>
  </form>
</div>
@endsection
