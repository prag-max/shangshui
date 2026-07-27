#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尚水数字 - 一键启动本机环境（Python 版）
作用同 start-all.bat：检查 MySQL -> 起 Laravel 后端 -> 起 frpc 隧道 -> 验证公网链路
用法：python start-all.py
"""

import os
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE, '..')
FRP_DIR = os.path.join(BASE, 'frp')
PHP_CANDIDATES = [
    r'G:\360Downloads\Software\php\php.exe',
    shutil.which('php'),
]
FRPC_EXE = os.path.join(FRP_DIR, 'bin', 'frpc.exe')


def find_php():
    for c in PHP_CANDIDATES:
        if c and os.path.exists(c):
            return c
    return None


def process_running(name):
    try:
        out = subprocess.check_output(['tasklist'], stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        return name.lower().encode() in out.lower()
    except Exception:
        return False


def wait_for_url(url, timeout=20, expected=None, verify_ssl=True):
    start = time.time()
    while time.time() - start < timeout:
        try:
            ctx = None if verify_ssl else urllib.request.SSLContext()
            with urllib.request.urlopen(url, timeout=3, context=ctx) as resp:
                code = resp.getcode()
                if expected is None or code == expected:
                    return True, code
                return False, code
        except urllib.error.HTTPError as e:
            # HTTPError means server responded; if no specific expected, accept it
            if expected is None:
                return True, e.code
            return False, e.code
        except Exception:
            pass
        time.sleep(1)
    return False, None


def main():
    print('=' * 60)
    print('尚水数字 一键启动 (Python 版)')
    print('=' * 60)

    # 0. MySQL
    print('[0/3] 检查 MySQL 服务 ...')
    if process_running('mysqld.exe'):
        print('      MySQL 已在运行，跳过。')
    else:
        print('      MySQL 未运行，尝试启动 (需要管理员权限) ...')
        for svc in ['MySQL80', 'MySQL']:
            try:
                subprocess.check_call(['net', 'start', svc], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                print('      MySQL 启动成功。')
                break
            except Exception:
                pass
        else:
            print('      [警告] 无法自动启动 MySQL，请手动以管理员启动；后端可能连不上库。')

    # 1. Laravel backend
    php = find_php()
    if not php:
        print('[错误] 找不到 php.exe，请确认 PHP 已安装或在 PATH 中。')
        sys.exit(1)

    backend_proc = None
    print('[1/3] 启动 Laravel 后端 (127.0.0.1:8000) ...')
    if process_running('php.exe'):
        # might be an existing backend; probe it
        ok, code = wait_for_url('http://127.0.0.1:8000/api/inquiries', timeout=3, expected=None)
        if ok:
            print('      检测到 :8000 已在监听，跳过重复启动。')
        else:
            print('      [警告] 有 php.exe 在跑，但 :8000 未响应，尝试再启一个 ...')
    else:
        cmd = [php, '-S', '127.0.0.1:8000', '-t', 'public', 'server.php']
        backend_proc = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f'      已启动后端 (PID={backend_proc.pid})，新窗口可见。')

    # 2. Wait for backend
    print('[2/3] 等待后端就绪 (最长 20 秒) ...')
    ok, code = wait_for_url('http://127.0.0.1:8000/api/inquiries', timeout=20, expected=None)
    if ok:
        print(f'      后端已就绪 (HTTP {code})。')
    else:
        print('      [警告] 后端 20 秒内无响应，frpc 可能接不到。')

    # 3. frpc tunnel
    frpc_proc = None
    print('[3/3] 启动 frpc 隧道 (-> 43.139.72.9:7000) ...')
    if process_running('frpc.exe'):
        print('      检测到 frpc 已在运行，跳过重复启动。')
    elif not os.path.exists(FRPC_EXE):
        print(f'      [错误] 找不到 {FRPC_EXE}，请先运行 get-frpc.ps1 下载 frpc。')
    else:
        frpc_proc = subprocess.Popen(
            [FRPC_EXE, '-c', 'frpc.toml'],
            cwd=FRP_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f'      已启动 frpc (PID={frpc_proc.pid})，新窗口可见。')

    # 4. Public verification
    print('等待公网链路建立 (最长 25 秒) ...')
    ok, code = wait_for_url('https://api.shanwater.com:8443/api/inquiries', timeout=25, expected=None, verify_ssl=False)
    print('=' * 60)
    if ok and code == 405:
        print('全部就绪！打开 https://www.shanwater.com/contact.html 提交表单即可。')
        print('查库命令：')
        print(r'  "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -h127.0.0.1 -uroot -p shanwater')
        print('  SELECT * FROM inquiries ORDER BY id DESC LIMIT 5;')
    elif ok:
        print(f'脚本已执行，但外网返回 {code} 而非 405。')
        print('请检查「尚水-后端」和「尚水-frpc」窗口是否有报错。')
    else:
        print('脚本已执行，但外网暂时无响应。')
        print('请检查：1) 两个子窗口是否在运行；2) 云端 frps/Caddy 是否在跑。')
        print('手动自检：curl -k https://api.shanwater.com:8443/api/inquiries  (期望 405)')
    print('=' * 60)

    if '--verify' in sys.argv:
        print('验证模式：已确认链路状态，本脚本退出，子窗口继续运行。')
        return

    # Keep main script alive so subprocesses are easy to track; user Ctrl+C to stop
    print('本窗口保持运行以监控子进程，按 Ctrl+C 可停止（不会停止已弹出的子窗口）。')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('已退出。')


if __name__ == '__main__':
    main()
