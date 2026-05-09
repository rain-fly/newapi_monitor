#!/usr/bin/env python
"""
NewAPI Monitor 启动/停止脚本
用法:
  python run.py start    启动服务
  python run.py stop     停止服务
  python run.py restart  重启服务
  python run.py status   查看状态
  python run.py          等同于 start
"""
import os
import sys
import signal
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(BASE_DIR, ".pids")


def start():
    os.chdir(BASE_DIR)
    sys.path.insert(0, BASE_DIR)

    # 安装依赖
    print("[1/3] 检查依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])

    os.makedirs("data", exist_ok=True)

    # 停止旧进程
    _stop_silent()

    # 启动 agent
    print("[2/3] 启动监控 Agent...")
    agent_proc = subprocess.Popen(
        [sys.executable, "-m", "monitor.agent"],
        stdout=open("monitor.log", "w"), stderr=subprocess.STDOUT
    )

    time.sleep(2)

    # 启动 web
    print("[3/3] 启动 Web 看板...")
    web_proc = subprocess.Popen(
        [sys.executable, "-m", "web.app"],
        stdout=open("web.log", "w"), stderr=subprocess.STDOUT
    )

    with open(PID_FILE, "w") as f:
        f.write(f"{agent_proc.pid}\n{web_proc.pid}\n")

    port = _get_port()
    print(f"\n服务已启动！")
    print(f"  监控 Agent: PID {agent_proc.pid}")
    print(f"  Web 看板:   PID {web_proc.pid} -> http://localhost:{port}")
    print(f"  日志文件:   monitor.log, web.log")


def _kill_pid(pid):
    """跨平台杀进程"""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True, timeout=5)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass


def stop():
    pids = _read_pids()
    if not pids:
        _stop_silent()
        print("已停止所有服务进程")
        return

    for pid in pids:
        _kill_pid(pid)

    time.sleep(1)

    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

    print("已停止所有服务进程")


def restart():
    stop()
    time.sleep(1)
    start()


def _is_running(pid):
    """检查进程是否运行中（跨平台）"""
    try:
        if sys.platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x100000, False, pid)
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        else:
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, PermissionError):
        return False


def show_status():
    pids = _read_pids()
    if not pids:
        print("服务未运行")
        return

    names = ["监控 Agent", "Web 看板  "]
    for i, pid in enumerate(pids):
        name = names[i] if i < len(names) else f"进程 {i+1}"
        if _is_running(pid):
            print(f"  {name}: PID {pid} (运行中)")
        else:
            print(f"  {name}: PID {pid} (已停止)")


def _read_pids():
    if not os.path.exists(PID_FILE):
        return []
    with open(PID_FILE) as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]


def _stop_silent():
    """停止已知进程，回退到按命令行查找"""
    for pid in _read_pids():
        _kill_pid(pid)
    time.sleep(1)

    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

    # Windows 回退：按命令行匹配杀进程
    if sys.platform == "win32":
        try:
            output = subprocess.check_output(
                'wmic process where "CommandLine like \'%monitor.agent%\' or CommandLine like \'%web.app%\'" get ProcessId /format:list',
                shell=True, text=True, timeout=5
            )
            for line in output.strip().split("\n"):
                line = line.strip()
                if "=" in line:
                    val = line.split("=", 1)[1].strip()
                    if val.isdigit():
                        subprocess.run(["taskkill", "/F", "/PID", val],
                                       capture_output=True, timeout=5)
        except Exception:
            pass


def _get_port():
    try:
        import yaml
        with open(os.path.join(BASE_DIR, "config.yaml")) as f:
            cfg = yaml.safe_load(f)
        return cfg.get("web", {}).get("port", 5000)
    except Exception:
        return 5000


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"

    if cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "restart":
        restart()
    elif cmd == "status":
        show_status()
    else:
        print(f"用法: python run.py [start|stop|restart|status]")
        sys.exit(1)
