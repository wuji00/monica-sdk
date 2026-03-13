"""
Monica SDK 自动认证示例

演示如何使用自动登录功能获取 session_id
"""

from monica_sdk import MonicaClient, MonicaAuth


def main():
    print("=" * 50)
    print("Monica SDK 自动认证示例")
    print("=" * 50)

    # 方式 1: 自动启动浏览器并等待登录（推荐）
    print("\n方式 1: 自动启动浏览器并等待登录")
    print("-" * 50)

    try:
        client = MonicaClient.auto_login(
            browser="chrome",  # 或 "edge"
            timeout=60,        # 等待登录的超时时间（秒）
            verbose=True
        )

        print(f"\n客户端创建成功!")
        print(f"对话 ID: {client.conversation_id}")

        # 发送测试消息
        print("\n发送测试消息...")
        response = client.chat("你好，请用一句话介绍你自己")
        print(f"\n响应: {response}")

    except ValueError as e:
        print(f"错误: {e}")
    except FileNotFoundError as e:
        print(f"浏览器错误: {e}")
    except ImportError as e:
        print(f"依赖错误: {e}")


def example_from_existing_browser():
    """
    方式 2: 从已登录的浏览器获取 session_id

    使用前需要先手动启动浏览器:
    - Chrome: chrome --remote-debugging-port=9222
    - Edge: msedge --remote-debugging-port=9222

    然后在浏览器中登录 monica.im
    """
    print("\n方式 2: 从已登录的浏览器获取 session_id")
    print("-" * 50)

    try:
        client = MonicaClient.from_logged_in_browser(
            port=9222,
            verbose=True
        )

        print(f"\n客户端创建成功!")
        response = client.chat("你好")
        print(f"响应: {response}")

    except ValueError as e:
        print(f"错误: {e}")


def example_direct_auth():
    """
    方式 3: 直接使用 MonicaAuth 类
    """
    print("\n方式 3: 直接使用 MonicaAuth 类")
    print("-" * 50)

    auth = MonicaAuth(browser="chrome")

    # 获取 session_id
    session_id = auth.get_session_id(timeout=60, auto_start=True)

    if session_id:
        print(f"\n获取到 session_id: {session_id[:20]}...")

        # 手动创建客户端
        client = MonicaClient(session_id=session_id, verbose=True)
        response = client.chat("测试消息")
        print(f"响应: {response}")
    else:
        print("未能获取 session_id")


if __name__ == "__main__":
    main()

    # 如果想测试其他方式，取消下面的注释
    # example_from_existing_browser()
    # example_direct_auth()
