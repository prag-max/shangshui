@extends('admin.layout')
@section('title','提交列表')
@section('content')
<div class="card">
  <div class="toolbar">
    <form method="GET" class="toolbar" style="margin:0">
      <input type="text" name="q" value="{{ $q }}" placeholder="搜索 姓名/单位/电话/邮箱/需求" style="width:280px">
      <button class="btn" type="submit">搜索</button>
      @if($q)<a class="btn" href="{{ route('admin.dashboard') }}">清除</a>@endif
      <a class="btn" href="{{ route('admin.dashboard', ['sort' => $sort==='desc'?'asc':'desc', 'q' => $q]) }}">
        提交时间：{{ $sort==='desc' ? '最新优先 ↓' : '最早优先 ↑' }}
      </a>
    </form>
  </div>
  <table>
    <thead><tr><th>#</th><th>姓名</th><th>单位</th><th>电话</th><th>邮箱</th><th>提交时间</th><th>状态</th><th>操作</th></tr></thead>
    <tbody>
    @forelse($items as $it)
      <tr>
        <td>{{ $it->id }}</td>
        <td>{{ $it->name }}</td>
        <td>{{ $it->company }}</td>
        <td>{{ $it->phone }}</td>
        <td>{{ $it->email ?? '-' }}</td>
        <td>{{ $it->created_at->format('Y-m-d H:i') }}</td>
        <td><span class="badge badge-{{ $it->status }}">{{ \App\Models\Inquiry::statusOptions()[$it->status] ?? $it->status }}</span></td>
        <td><a class="btn btn-sm" href="{{ route('admin.show', $it->id) }}">查看</a></td>
      </tr>
    @empty
      <tr><td colspan="8" style="text-align:center;color:var(--muted)">暂无提交记录</td></tr>
    @endforelse
    </tbody>
  </table>
  <div class="pager">{{ $items->links() }}</div>
</div>
@endsection
