<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@yield('title', '管理后台') - 尚水数字</title>
<style>
:root{--primary:#1f6feb;--primary-d:#0b4fb5;--bg:#f5f7fa;--card:#fff;--border:#e3e8ef;--text:#1f2733;--muted:#6b7785;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--text);font-size:14px;}
a{color:var(--primary);text-decoration:none}
.topbar{background:#0f1729;color:#fff;padding:0 20px;height:52px;display:flex;align-items:center;justify-content:space-between}
.topbar .brand{font-weight:700}
.topbar nav a{color:#cdd6e4;margin-left:16px}
.container{max-width:1080px;margin:24px auto;padding:0 20px}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:18px}
table{width:100%;border-collapse:collapse}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
th{background:#f0f3f8;font-weight:600}
.btn{display:inline-block;padding:8px 14px;border-radius:8px;border:1px solid var(--border);background:#fff;cursor:pointer;font-size:14px}
.btn-primary{background:var(--primary);border-color:var(--primary);color:#fff}
.btn-sm{padding:5px 10px;font-size:13px}
input,select,textarea{width:100%;padding:8px 10px;border:1px solid var(--border);border-radius:8px;font-size:14px;font-family:inherit}
.field{margin-bottom:14px}
.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:14px;flex-wrap:wrap}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px}
.badge-pending{background:#fff4e5;color:#b76e00}
.badge-contacted{background:#e6f0ff;color:#0b4fb5}
.badge-won{background:#e6f9ed;color:#1a7f37}
.badge-closed{background:#eeeff1;color:#6b7785}
.pager{margin-top:14px;display:flex;gap:8px;align-items:center}
.alert{background:#e6f9ed;border:1px solid #b7e4c4;color:#1a7f37;padding:10px 14px;border-radius:8px;margin-bottom:14px}
</style>
</head>
<body>
<div class="topbar">
  <span class="brand">尚水数字 · 管理后台</span>
  <nav>
    <a href="{{ route('admin.dashboard') }}">提交列表</a>
    <a href="{{ route('admin.profile') }}">修改密码</a>
    <a href="#" onclick="event.preventDefault();document.getElementById('logout-form').submit();">退出</a>
    <form id="logout-form" action="{{ route('admin.logout') }}" method="POST" style="display:none">@csrf</form>
  </nav>
</div>
<div class="container">
  @if(session('success'))<div class="alert">{{ session('success') }}</div>@endif
  @yield('content')
</div>
</body>
</html>
