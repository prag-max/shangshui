<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Inquiry extends Model
{
    protected $table = 'inquiries';

    protected $fillable = [
        'name', 'company', 'phone', 'email', 'user_scale', 'requirement',
        'ip', 'referer', 'status', 'admin_note',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_CONTACTED = 'contacted';
    public const STATUS_WON = 'won';
    public const STATUS_CLOSED = 'closed';

    public static function statusOptions(): array
    {
        return [
            self::STATUS_PENDING => '待跟进',
            self::STATUS_CONTACTED => '已联系',
            self::STATUS_WON => '已成交',
            self::STATUS_CLOSED => '已关闭',
        ];
    }
}
