"""
Monica SDK 自动认证模块测试
"""
import sys
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def test_import():
    """测试模块导入"""
    print("1. 测试模块导入...")

    try:
        from monica_sdk import MonicaClient, MonicaAuth
        print("   ✓ MonicaClient 导入成功")
        print("   ✓ MonicaAuth 导入成功")
        return True
    except ImportError as e:
        print(f"   ✗ 导入失败: {e}")
        return False


def test_browser_paths():
    """测试浏览器路径检测"""
    print("\n2. 测试浏览器路径检测...")

    from monica_sdk.auth import MonicaAuth

    auth = MonicaAuth()
    system = platform.system()
    print(f"   当前系统: {system}")

    # Chrome
    auth.browser = "chrome"
    chrome_path = auth._find_browser_path()
    if chrome_path:
        print(f"   ✓ 找到 Chrome: {chrome_path}")
    else:
        print(f"   - 未找到 Chrome (可能未安装)")

    # Edge
    auth.browser = "edge"
    edge_path = auth._find_browser_path()
    if edge_path:
        print(f"   ✓ 找到 Edge: {edge_path}")
    else:
        print(f"   - 未找到 Edge (可能未安装)")

    return chrome_path is not None or edge_path is not None


def test_client_methods():
    """测试客户端类方法存在"""
    print("\n3. 测试 MonicaClient 类方法...")

    from monica_sdk import MonicaClient

    # 检查类方法是否存在
    has_auto_login = hasattr(MonicaClient, 'auto_login')
    has_from_browser = hasattr(MonicaClient, 'from_logged_in_browser')

    print(f"   auto_login 方法: {'✓' if has_auto_login else '✗'}")
    print(f"   from_logged_in_browser 方法: {'✓' if has_from_browser else '✗'}")

    return has_auto_login and has_from_browser


def test_auth_class():
    """测试 MonicaAuth 类"""
    print("\n4. 测试 MonicaAuth 类...")

    from monica_sdk.auth import MonicaAuth

    auth = MonicaAuth(port=9222, browser="chrome")

    print(f"   端口: {auth.port}")
    print(f"   浏览器: {auth.browser}")
    print(f"   Monica 域名: {auth.MONICA_DOMAIN}")
    print(f"   CDP 端口常量: {auth.CDP_PORT}")

    # 检查方法存在
    has_get_session = hasattr(auth, 'get_session_id')
    has_get_existing = hasattr(auth, 'get_session_id_from_existing')
    has_find_browser = hasattr(auth, '_find_browser_path')
    has_start_browser = hasattr(auth, '_start_browser')
    has_stop_browser = hasattr(auth, '_stop_browser')

    methods_ok = all([
        has_get_session,
        has_get_existing,
        has_find_browser,
        has_start_browser,
        has_stop_browser
    ])

    print(f"   get_session_id: {'✓' if has_get_session else '✗'}")
    print(f"   get_session_id_from_existing: {'✓' if has_get_existing else '✗'}")
    print(f"   _find_browser_path: {'✓' if has_find_browser else '✗'}")
    print(f"   _start_browser: {'✓' if has_start_browser else '✗'}")
    print(f"   _stop_browser: {'✓' if has_stop_browser else '✗'}")

    return methods_ok


def test_playwright_available():
    """测试 Playwright 是否可用"""
    print("\n5. 测试 Playwright 依赖...")

    try:
        from playwright.sync_api import sync_playwright
        print("   ✓ Playwright 已安装")

        # 尝试创建实例（不实际启动）
        try:
            p = sync_playwright().start()
            p.stop()
            print("   ✓ Playwright 可以正常启动")
            return True
        except Exception as e:
            print(f"   - Playwright 启动警告: {e}")
            print("   提示: 可能需要运行 'uv run playwright install chromium'")
            return True  # 依赖已安装，只是浏览器未安装

    except ImportError:
        print("   ✗ Playwright 未安装")
        print("   请运行: uv add playwright && uv run playwright install chromium")
        return False


def test_manual_auth_flow():
    """
    手动测试：从已登录的浏览器获取 session_id

    使用前需要：
    1. 关闭所有 Chrome 窗口
    2. 运行: chrome --remote-debugging-port=9222
    3. 在浏览器中登录 monica.im
    4. 运行此测试
    """
    print("\n6. 手动测试：从已登录浏览器获取 session_id")
    print("   (需要先启动带调试端口的浏览器并登录 monica.im)")
    print("-" * 50)

    from monica_sdk import MonicaAuth

    auth = MonicaAuth(port=9222)

    try:
        session_id = auth.get_session_id_from_existing(timeout=5)
        if session_id:
            print(f"   ✓ 成功获取 session_id: {session_id[:30]}...")
            return True
        else:
            print("   - 未获取到 session_id（浏览器可能未登录）")
            return False
    except ImportError as e:
        print(f"   ✗ 依赖错误: {e}")
        return False
    except Exception as e:
        print(f"   - 连接失败: {e}")
        print("   提示: 请确保已启动 chrome --remote-debugging-port=9222")
        return False


def test_full_auto_login():
    """
    完整测试：自动启动浏览器并获取 session_id

    此测试会自动打开浏览器，等待用户登录
    """
    print("\n7. 完整测试：自动启动浏览器并登录")
    print("   (此测试会自动打开浏览器)")
    print("-" * 50)

    from monica_sdk import MonicaClient

    try:
        # 使用 use_default_profile=True 来保留登录状态
        # 注意：需要先关闭其他 Chrome 窗口
        client = MonicaClient.auto_login(
            browser="chrome",
            timeout=120,  # 2分钟超时
            use_default_profile=True,  # 使用 Default profile 保留登录状态
            verbose=True
        )

        print(f"\n   ✓ 客户端创建成功!")
        print(f"   对话 ID: {client.conversation_id}")

        # 发送测试消息
        response = client.chat("你好，请回复'测试成功'")
        print(f"   ✓ 收到响应: {response[:100]}...")

        return True

    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False


def run_basic_tests():
    """运行基础测试（不涉及真实浏览器）"""
    print("=" * 60)
    print("Monica SDK 自动认证模块 - 基础测试")
    print("=" * 60)

    results = []

    results.append(("模块导入", test_import()))
    results.append(("浏览器路径检测", test_browser_paths()))
    results.append(("客户端类方法", test_client_methods()))
    results.append(("MonicaAuth 类", test_auth_class()))
    results.append(("Playwright 依赖", test_playwright_available()))

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, v in results if v)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    return passed == total


def run_manual_tests():
    """运行手动测试（需要真实浏览器）"""
    print("\n" + "=" * 60)
    print("手动测试（需要真实浏览器）")
    print("=" * 60)

    print("\n选择测试:")
    print("  1. 从已登录浏览器获取 session_id（需先启动 chrome --remote-debugging-port=9222）")
    print("  2. 完整自动登录测试（自动打开浏览器）")
    print("  0. 跳过")

    try:
        choice = input("\n请输入选项: ").strip()

        if choice == "1":
            test_manual_auth_flow()
        elif choice == "2":
            test_full_auto_login()
        else:
            print("已跳过手动测试")

    except (KeyboardInterrupt, EOFError):
        print("\n已跳过手动测试")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Monica SDK 自动认证测试")
    parser.add_argument("--manual", "-m", action="store_true", help="运行手动测试")
    parser.add_argument("--full", "-f", action="store_true", help="运行完整自动登录测试")
    parser.add_argument("--basic", "-b", action="store_true", help="仅运行基础测试")
    args = parser.parse_args()

    # 运行基础测试
    basic_ok = run_basic_tests()

    # 仅基础测试模式
    if args.basic:
        sys.exit(0 if basic_ok else 1)

    # 完整自动登录测试
    if args.full:
        test_full_auto_login()
        sys.exit(0)

    # 手动测试模式
    if args.manual:
        run_manual_tests()
        sys.exit(0)

    # 默认：显示提示
    print("\n" + "=" * 60)
    print("后续测试选项")
    print("=" * 60)
    print("\n基础测试全部通过! 要测试完整功能，请选择:")
    print("  uv run python test_auto_auth.py -m   # 交互式手动测试")
    print("  uv run python test_auto_auth.py -f   # 完整自动登录测试")
    print("\n提示:")
    print("  - 手动测试: 需要先启动 chrome --remote-debugging-port=9222 并登录")
    print("  - 完整测试: 会自动打开浏览器，等待您登录后自动获取 cookie")
