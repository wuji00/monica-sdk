"""
Monica SDK 完整流程测试
1. 启动带调试端口的 Chrome
2. 等待用户登录
3. 获取 session_id
4. 发送消息并获取回复
"""
import subprocess
import time
import sys

# 添加项目路径
sys.path.insert(0, '.')


def start_chrome_with_debug_port(port=9222, user_data_dir=r"D:\data\chrome"):
    """启动带调试端口的 Chrome"""
    import os

    # 确保目录存在
    os.makedirs(user_data_dir, exist_ok=True)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    url = "https://monica.im"

    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        url
    ]

    print(f"启动 Chrome: {' '.join(cmd[:3])} {url}")

    # 启动 Chrome（后台运行）
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return process


def check_cdp_ready(port=9222, timeout=30):
    """检查 CDP 端口是否就绪"""
    import urllib.request

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            handler = urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(handler)
            req = urllib.request.Request(f"http://localhost:{port}/json/version")
            with opener.open(req, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def get_session_id_with_timeout(port=9222, timeout=120):
    """获取 session_id，带超时"""
    from monica_sdk.auth import MonicaAuth

    auth = MonicaAuth(port=port)
    return auth.get_session_id(timeout=timeout, auto_start=False)


def main():
    print("=" * 60)
    print("Monica SDK 完整流程测试")
    print("=" * 60)

    PORT = 9222
    USER_DATA_DIR = r"D:\data\chrome"

    # Step 1: 检查是否已有 Chrome 在运行
    print("\n[Step 1] 检查 CDP 端口状态...")
    if check_cdp_ready(PORT, timeout=2):
        print(f"   ✓ 端口 {PORT} 已有可用的 Chrome")
        chrome_process = None
    else:
        print(f"   - 端口 {PORT} 不可用，启动新的 Chrome...")
        chrome_process = start_chrome_with_debug_port(PORT, USER_DATA_DIR)

        print(f"\n[Step 2] 等待 Chrome CDP 就绪...")
        if not check_cdp_ready(PORT, timeout=30):
            print("   ✗ Chrome CDP 端口未能在规定时间内就绪")
            if chrome_process:
                chrome_process.terminate()
            return False
        print("   ✓ Chrome CDP 已就绪")

    # Step 2: 获取 session_id
    print(f"\n[Step 3] 获取 session_id...")
    print("   如果浏览器未登录 monica.im，请在浏览器中登录")
    print("   等待登录中...")

    session_id = get_session_id_with_timeout(PORT, timeout=120)

    if not session_id:
        print("   ✗ 未能获取 session_id")
        if chrome_process:
            chrome_process.terminate()
        return False

    print(f"   ✓ 成功获取 session_id: {session_id[:30]}...")

    # Step 3: 创建客户端并发送消息
    print(f"\n[Step 4] 创建客户端并发送测试消息...")

    from monica_sdk import MonicaClient

    client = MonicaClient(session_id=session_id, verbose=True)

    print(f"   对话 ID: {client.conversation_id}")

    # 发送多条测试消息
    test_messages = [
        "你好，请用一句话介绍你自己",
        "1+1等于几？",
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n[消息 {i}] {msg}")
        response = client.chat(msg)
        print(f"[回复 {i}] {response[:200]}{'...' if len(response) > 200 else ''}")

    # 测试流式输出
    print(f"\n[Step 5] 测试流式输出...")
    print("   发送: 写一首关于春天的短诗")

    full_response = ""
    for chunk in client.chat_stream("写一首关于春天的短诗"):
        if chunk.text:
            print(chunk.text, end="", flush=True)
            full_response += chunk.text
    print()  # 换行

    print(f"\n" + "=" * 60)
    print("✓ 完整流程测试成功!")
    print("=" * 60)

    # 不关闭 Chrome，让用户继续使用
    print(f"\nChrome 浏览器保持打开状态，你可以继续使用。")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
