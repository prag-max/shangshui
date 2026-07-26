<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Inquiry;
use Illuminate\Http\Request;

class InquiryController extends Controller
{
    public function index(Request $request)
    {
        $q = trim((string) $request->input('q', ''));
        $sort = $request->input('sort', 'desc');
        $sort = in_array($sort, ['asc', 'desc']) ? $sort : 'desc';

        $query = Inquiry::query();

        if ($q !== '') {
            $query->where(function ($builder) use ($q) {
                $builder->where('name', 'like', '%'.$q.'%')
                    ->orWhere('company', 'like', '%'.$q.'%')
                    ->orWhere('phone', 'like', '%'.$q.'%')
                    ->orWhere('email', 'like', '%'.$q.'%')
                    ->orWhere('requirement', 'like', '%'.$q.'%');
            });
        }

        $items = $query->orderBy('created_at', $sort)->paginate(15)->withQueryString();

        return view('admin.index', [
            'items' => $items,
            'q' => $q,
            'sort' => $sort,
        ]);
    }

    public function show($id)
    {
        $item = Inquiry::findOrFail($id);

        return view('admin.show', ['item' => $item]);
    }

    public function update(Request $request, $id)
    {
        $item = Inquiry::findOrFail($id);

        $data = $request->validate([
            'status' => ['required', 'in:pending,contacted,won,closed'],
            'admin_note' => ['nullable', 'string', 'max:2000'],
        ]);

        $item->update([
            'status' => $data['status'],
            'admin_note' => ! empty($data['admin_note']) ? strip_tags(trim($data['admin_note'])) : null,
        ]);

        return redirect()->route('admin.show', $item->id)->with('success', '已保存');
    }
}
