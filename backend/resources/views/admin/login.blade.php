@extends('admin.layout')
@section('title','登录')
@section('content')
<div class="container" style="max-width:420px">
  <div class="card">
    <h2 style="margin-top:0">管理员登录</h2>
    @if($errors->any())
      <div class="alert" style="background:#fdecea;border-color:#f5c2c0;color:#b42318">
        {{ $errors->first() }}
      </div>
    @endif
    <form method="POST" action="{{ route('admin.login') }}">
      @csrf
      <div class="field"><label>邮箱</label><input type="email" name="email" value="{{ old('email') }}" required></div>
      <div class="field"><label>密码</label><input type="password" name="password" required></div>
      <button class="btn btn-primary" style="width:100%">登录</button>
    </form>
  </div>
</div>
@endsection
