#!/usr/bin/env python3
import argparse
import subprocess
import shutil
import sys
import time
import os
import signal
import re

PIDFILE = '/tmp/stay-with-me.pid'
SCRIPT = os.path.abspath(__file__)

def is_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False

def start_background():
    if os.path.exists(PIDFILE):
        try:
            pid = int(open(PIDFILE).read().strip())
            if is_running(pid):
                print('Already running (pid %d)' % pid)
                return
        except Exception:
            pass
    args = [sys.executable, SCRIPT, 'run']
    p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, close_fds=True)
    with open(PIDFILE, 'w') as f:
        f.write(str(p.pid))
    print('Started stay-with-me (pid %d)' % p.pid)

def stop_background():
    if not os.path.exists(PIDFILE):
        print('Not running')
        return
    try:
        pid = int(open(PIDFILE).read().strip())
    except Exception:
        try:
            os.remove(PIDFILE)
        except Exception:
            pass
        print('PID file removed')
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        print('Process not found, removing stale pidfile')
    except Exception as e:
        print('Error stopping:', e)
        return
    try:
        os.remove(PIDFILE)
    except Exception:
        pass
    print('Stopped')

def status():
    if os.path.exists(PIDFILE):
        try:
            pid = int(open(PIDFILE).read().strip())
            if is_running(pid):
                print('Running (pid %d)' % pid)
                return
        except Exception:
            pass
    print('Not running')

def run_foreground():
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    gdbus = shutil.which('gdbus')
    xdg = shutil.which('xdg-screensaver')
    xset = shutil.which('xset')
    caffeinate = shutil.which('caffeinate')
    cookie = None
    caffeinate_proc = None
    try:
        if sys.platform == 'darwin':
            if caffeinate:
                caffeinate_proc = subprocess.Popen([caffeinate, '-dims'])
                print('Keeping awake via caffeinate (pid %d)' % caffeinate_proc.pid)
            else:
                print('caffeinate not found on macOS; cannot prevent display sleep')
                return
        elif gdbus:
            cmd = ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.ScreenSaver', '--object-path', '/org/freedesktop/ScreenSaver', '--method', 'org.freedesktop.ScreenSaver.Inhibit', 'stay-with-me', 'Prevent screen from sleeping']
            out = subprocess.check_output(cmd, text=True)
            m = re.search(r'([0-9]+)', out)
            if m:
                cookie = int(m.group(1))
                print('Inhibited via gdbus (cookie %d)' % cookie)
            else:
                print('gdbus returned:', out)
        elif xdg:
            print('gdbus not found; using xdg-screensaver reset loop')
        elif xset:
            print('gdbus/xdg-screensaver not found; using xset reset loop')
        else:
            print('No known method found (gdbus/xdg-screensaver/xset). Exiting.')
            return
        while True:
            time.sleep(30)
            if not cookie:
                if xdg:
                    subprocess.run(['xdg-screensaver', 'reset'])
                elif xset:
                    subprocess.run(['xset', 's', 'reset'])
    finally:
        if cookie:
            try:
                cmd = ['gdbus', 'call', '--session', '--dest', 'org.freedesktop.ScreenSaver', '--object-path', '/org/freedesktop/ScreenSaver', '--method', 'org.freedesktop.ScreenSaver.UnInhibit', str(cookie)]
                subprocess.run(cmd)
                print('Uninhibited gdbus')
            except Exception:
                pass
        if caffeinate_proc:
            try:
                caffeinate_proc.terminate()
            except Exception:
                pass

def main():
    p = argparse.ArgumentParser(prog='stay-with-me')
    p.add_argument('command', nargs='?', choices=['start', 'stop', 'status', 'run'], default='status')
    args = p.parse_args()
    if args.command == 'start':
        start_background()
    elif args.command == 'stop':
        stop_background()
    elif args.command == 'status':
        status()
    elif args.command == 'run':
        run_foreground()

if __name__ == '__main__':
    main()
