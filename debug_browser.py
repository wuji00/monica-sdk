"""
调试脚本：检查浏览器启动和 CDP 端口状态
"""
import subprocess
import time
import socket
import tempfile
import urllib.request
from pathlib import Path

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9225  # 使用不同的端口

def check_port(port):
    """检查端口状态"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result == 0
    except Exception as e:
        return str(e)

def check_cdp_service(port):
    """检查 CDP 服务状态"""
    try:
        url = f"http://localhost:{port}/json/version"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode()
    except Exception as e:
        return str(e)

def find_available_port(start_port):
    """查找可用端口"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                if result != 0:
                    return port
        except:
            return port
    return start_port

def main():
    print("=" * 60)
    print("浏览器 CDP 调试脚本")
    print("=" * 60)

    # 查找可用端口
    port = find_available_port(PORT)
    print(f"\n使用端口: {port}")

    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="chrome_debug_")
    print(f"临时用户数据目录: {temp_dir}")

    # 启动浏览器
    print(f"\n启动 Chrome 浏览器...")
    cmd = [
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://monica.im",
    ]
    print(f"命令: {' '.join(cmd[:3])}...")

    process = subprocess.Popen(cmd)
    print(f"浏览器进程 PID: {process.pid}")

    # 等待并检查端口
    print(f"\n等待 CDP 端口就绪 (最多 30 秒)...")
    for i in range(30):
        time.sleep(1)

        port_status = check_port(port)
        cdp_result = check_cdp_service(port) if port_status else "端口未开放"

        # 截断输出
        if isinstance(cdp_result, str) and len(cdp_result) > 60:
            cdp_display = cdp_result[:60] + "..."
        else:
            cdp_display = cdp_result

        print(f"  [{i+1:2d}s] 端口: {'开放' if port_status else '未开放'}, CDP: {cdp_display}")

        if port_status and isinstance(cdp_result, str) and "webSocketDebuggerUrl" in cdp_result:
            print(f"\n✓ CDP 服务已就绪!")
            print(f"\nCDP 响应:\n{cdp_result[:500]}")

            # 保持浏览器打开
            print(f"\n浏览器将在 10 秒后关闭...")
            time.sleep(10)
            break

    else:
        print(f"\n✗ 超时: CDP 服务未就绪")

    # 清理
    print(f"\n关闭浏览器...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except:
        process.kill()

    print("完成!")

if __name__ == "__main__":
    main()
