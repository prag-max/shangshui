@extends('admin.layout')
@section('title','修改密码')
@section('content')
<div class="card" style="max-width:480px">
  <h2 style="margin-top:0">修改管理员密码</h2>
  @if($errors->any())<div class="alert" style="background:#fdecea;border-color:#f5c2c0;color:#b42318">{{ $errors->first() }}</div>@endif
  <form method="POST" action="{{ route('admin.profile') }}">
    @csrf
    <div class="field"><label>当前密码</label><input type="password" name="current_password" required></div>
    <div class="field"><label>新密码（至少8位）</label><input type="password" name="password" required></div>
    <div class="field"><label>确认新密码</label><input type="password" name="password_confirmation" required></div>
    <button class="btn btn-primary">保存修改</button>
  </form>
</div>
@endsection
