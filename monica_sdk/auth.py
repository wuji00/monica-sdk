"""
Monica SDK 认证模块 - 自动获取 session_id
"""
import subprocess
import time
import platform
import tempfile
import socket
import shutil
from pathlib import Path
from typing import Optional


class MonicaAuth:
    """Monica 认证管理器 - 自动启动浏览器并获取 cookie"""

    CDP_PORT = 9222
    MONICA_DOMAIN = "monica.im"

    # 浏览器路径配置
    BROWSER_PATHS = {
        "chrome": {
            "Windows": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe",
            ],
            "Darwin": [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ],
            "Linux": [
                "/usr/bin/google-chrome",
                "/usr/bin/chrome",
            ]
        },
        "edge": {
            "Windows": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ],
            "Darwin": [
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            ],
        }
    }

    # 用户数据目录配置
    USER_DATA_DIRS = {
        "chrome": {
            "Windows": Path.home() / "AppData/Local/Google/Chrome/User Data",
            "Darwin": Path.home() / "Library/Application Support/Google/Chrome",
            "Linux": Path.home() / ".config/google-chrome",
        },
        "edge": {
            "Windows": Path.home() / "AppData/Local/Microsoft/Edge/User Data",
            "Darwin": Path.home() / "Library/Application Support/Microsoft Edge",
        }
    }

    def __init__(self, port: int = 9222, browser: str = "chrome", use_existing_profile: bool = False, use_default_profile: bool = False):
        self.port = port
        self.browser = browser
        self._browser_process = None
        self._temp_dir = None
        self._original_port = port
        self.use_existing_profile = use_existing_profile  # 是否使用现有配置文件（复制 Cookies）
        self.use_default_profile = use_default_profile    # 是否直接使用 Default profile（需要关闭其他 Chrome）

    def _find_available_port(self, start_port: int = 9222, max_attempts: int = 100) -> int:
        """查找可用端口"""
        for port in range(start_port, start_port + max_attempts):
            if self._is_port_available(port):
                return port
        raise RuntimeError(f"无法找到可用端口 (尝试范围: {start_port}-{start_port + max_attempts})")

    def _find_browser_path(self) -> Optional[str]:
        """查找浏览器可执行文件路径"""
        system = platform.system()
        paths = self.BROWSER_PATHS.get(self.browser, {}).get(system, [])

        for path in paths:
            path = Path(path)
            if path.exists():
                return str(path)
        return None

    def _get_user_data_dir(self) -> Optional[Path]:
        """获取浏览器的用户数据目录"""
        system = platform.system()
        data_dir = self.USER_DATA_DIRS.get(self.browser, {}).get(system)
        if data_dir and data_dir.exists():
            return data_dir
        return None

    def _copy_cookies_to_temp_profile(self, temp_dir: str) -> bool:
        """
        复制 Cookies 和登录相关文件到临时配置目录

        :param temp_dir: 临时目录路径
        :return: 是否成功复制
        """
        user_data_dir = self._get_user_data_dir()
        if not user_data_dir:
            print(f"未找到 {self.browser} 用户数据目录")
            return False

        # 默认配置目录
        default_profile = user_data_dir / "Default"
        if not default_profile.exists():
            print(f"未找到默认配置目录: {default_profile}")
            return False

        # 创建临时配置目录结构
        temp_profile = Path(temp_dir) / "Default"
        temp_profile.mkdir(parents=True, exist_ok=True)

        # 需要复制的文件（Cookies 和登录相关）
        files_to_copy = [
            "Cookies",           # Cookies 数据库
            "Cookies-journal",   # SQLite 日志文件
            "Login Data",        # 登录数据
            "Web Data",          # 表单数据
            "Preferences",       # 偏好设置
            "Secure Preferences", # 安全偏好
        ]

        copied = 0
        for filename in files_to_copy:
            src = default_profile / filename
            dst = temp_profile / filename
            if src.exists():
                try:
                    shutil.copy2(src, dst)
                    copied += 1
                except Exception as e:
                    print(f"复制 {filename} 失败: {e}")

        if copied > 0:
            print(f"已复制 {copied} 个配置文件到临时目录")
            return True
        return False

    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用（未被监听）"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except Exception:
            return True

    def _check_cdp_service(self, port: int) -> bool:
        """检查 CDP 服务是否可用"""
        import urllib.request
        import os

        # 保存当前代理设置
        old_http_proxy = os.environ.get('HTTP_PROXY')
        old_https_proxy = os.environ.get('HTTPS_PROXY')
        old_http_proxy_lower = os.environ.get('http_proxy')
        old_https_proxy_lower = os.environ.get('https_proxy')

        # 临时禁用代理（localhost 不需要代理）
        for proxy_var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
            os.environ.pop(proxy_var, None)

        try:
            url = f"http://localhost:{port}/json/version"
            req = urllib.request.Request(url)
            # 不使用代理处理器
            handler = urllib.request.ProxyHandler({})
            opener = urllib.request.build_opener(handler)
            with opener.open(req, timeout=2) as response:
                content = response.read().decode()
                return "webSocketDebuggerUrl" in content
        except Exception:
            return False
        finally:
            # 恢复代理设置
            if old_http_proxy:
                os.environ['HTTP_PROXY'] = old_http_proxy
            if old_https_proxy:
                os.environ['HTTPS_PROXY'] = old_https_proxy
            if old_http_proxy_lower:
                os.environ['http_proxy'] = old_http_proxy_lower
            if old_https_proxy_lower:
                os.environ['https_proxy'] = old_https_proxy_lower

    def _wait_for_cdp_port(self, port: int, timeout: int = 30) -> bool:
        """等待 CDP 端口和 DevTools 服务就绪"""
        import urllib.request
        import urllib.error

        start_time = time.time()
        while time.time() - start_time < timeout:
            # 首先检查端口是否开放
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result != 0:
                        time.sleep(0.5)
                        continue
            except Exception:
                time.sleep(0.5)
                continue

            # 然后验证 DevTools 服务是否就绪（不使用代理）
            try:
                url = f"http://localhost:{port}/json/version"
                req = urllib.request.Request(url)
                handler = urllib.request.ProxyHandler({})
                opener = urllib.request.build_opener(handler)
                with opener.open(req, timeout=2) as response:
                    if response.status == 200:
                        # DevTools 服务已就绪
                        time.sleep(0.5)
                        return True
            except Exception:
                pass

            time.sleep(0.5)
        return False

    def _start_browser(self) -> subprocess.Popen:
        """启动带调试端口的浏览器"""
        browser_path = self._find_browser_path()
        if not browser_path:
            raise FileNotFoundError(f"未找到 {self.browser} 浏览器")

        # 获取用户数据目录
        user_data_dir = self._get_user_data_dir()

        if self.use_default_profile and user_data_dir:
            # 直接使用 Default profile（需要关闭其他 Chrome 实例）
            # 这样可以保留所有登录状态
            self._temp_dir = None  # 不使用临时目录
            cmd = [
                browser_path,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={user_data_dir}",
                "--profile-directory=Default",
                "--no-first-run",
                "--no-default-browser-check",
                f"https://{self.MONICA_DOMAIN}",
            ]
            print(f"使用 Default Profile（请确保已关闭其他 Chrome 窗口）")

        elif self.use_existing_profile and user_data_dir:
            # 使用现有用户数据目录，但指定不同的 profile
            # 这样可以与正在运行的 Chrome 共存
            self._temp_dir = None  # 不使用临时目录
            profile_dir = "Profile_MonicaSDK"

            cmd = [
                browser_path,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={user_data_dir}",
                f"--profile-directory={profile_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                f"https://{self.MONICA_DOMAIN}",
            ]
            print(f"使用现有用户数据目录，Profile: {profile_dir}")
        else:
            # 创建临时用户数据目录
            self._temp_dir = tempfile.mkdtemp(prefix=f"monica_sdk_{self.browser}_")

            # 如果启用了使用现有配置，复制 Cookies 等文件
            if self.use_existing_profile:
                self._copy_cookies_to_temp_profile(self._temp_dir)

            cmd = [
                browser_path,
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={self._temp_dir}",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-background-networking",
                f"https://{self.MONICA_DOMAIN}",
            ]

        print(f"启动命令: {' '.join(cmd[:4])}...")

        self._browser_process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return self._browser_process

    def _stop_browser(self):
        """关闭浏览器"""
        if self._browser_process:
            try:
                self._browser_process.terminate()
                self._browser_process.wait(timeout=5)
            except Exception:
                self._browser_process.kill()
            finally:
                self._browser_process = None

        # 清理临时目录
        if self._temp_dir and Path(self._temp_dir).exists():
            import shutil
            try:
                shutil.rmtree(self._temp_dir, ignore_errors=True)
            except Exception:
                pass
            self._temp_dir = None

    def get_session_id(self, timeout: int = 60, auto_start: bool = True) -> Optional[str]:
        """
        获取 session_id

        :param timeout: 等待登录的超时时间（秒）
        :param auto_start: 是否自动启动浏览器
        :return: session_id 或 None
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError("请安装: uv add playwright && uv run playwright install chromium")

        browser_started_by_us = False

        if auto_start:
            # 首先检查默认端口是否有可用的 CDP 服务
            if self._check_cdp_service(self._original_port):
                print(f"检测到端口 {self._original_port} 已有可用的浏览器，直接连接...")
                self.port = self._original_port
            elif self._check_cdp_service(self.port):
                # 检查当前配置的端口
                print(f"检测到端口 {self.port} 已有可用的浏览器，直接连接...")
            else:
                # 需要启动新浏览器，先找可用端口
                if not self._is_port_available(self.port):
                    print(f"端口 {self.port} 已被占用，正在查找可用端口...")
                    self.port = self._find_available_port(self.port + 1)
                    print(f"使用端口: {self.port}")

                print(f"正在启动 {self.browser} 浏览器...")
                self._start_browser()
                browser_started_by_us = True

                # 等待 CDP 端口就绪
                print(f"等待浏览器 CDP 端口 {self.port} 就绪...")
                if not self._wait_for_cdp_port(self.port, timeout=30):
                    raise ConnectionError(f"浏览器 CDP 端口 {self.port} 未能在规定时间内就绪")

        # 设置 NO_PROXY 排除 localhost（保留代理设置，因为访问 monica.im 需要代理）
        import os
        old_no_proxy = os.environ.get('NO_PROXY')
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1'

        p = None
        try:
            p = sync_playwright().start()

            browser = None
            last_error = None

            for attempt in range(15):  # 增加尝试次数
                try:
                    browser = p.chromium.connect_over_cdp(
                        f"http://localhost:{self.port}",
                        timeout=10000  # 10秒超时
                    )
                    break
                except Exception as e:
                    last_error = e
                    if attempt < 14:
                        time.sleep(1)

            if not browser:
                raise ConnectionError(f"无法连接到浏览器: {last_error}")

            print("已连接到浏览器，正在检查登录状态...")

            start_time = time.time()
            while time.time() - start_time < timeout:
                # 检查所有上下文的 cookie
                for context in browser.contexts:
                    try:
                        cookies = context.cookies([f"https://{self.MONICA_DOMAIN}"])
                        for cookie in cookies:
                            if cookie["name"] == "session_id" and cookie["value"]:
                                session_id = cookie["value"]
                                print("成功获取 session_id!")
                                return session_id
                    except Exception:
                        pass

                # 等待用户登录
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed
                print(f"请在浏览器中登录 {self.MONICA_DOMAIN}... (剩余 {remaining} 秒)")
                time.sleep(3)

            print("超时：未能在规定时间内获取 session_id")
            return None

        finally:
            # 恢复 NO_PROXY 设置
            if old_no_proxy:
                os.environ['NO_PROXY'] = old_no_proxy
            elif 'NO_PROXY' in os.environ:
                del os.environ['NO_PROXY']

            # 停止 Playwright
            if p:
                try:
                    p.stop()
                except Exception:
                    pass

            # 关闭我们启动的浏览器
            if browser_started_by_us:
                print("正在关闭浏览器...")
                self._stop_browser()

    def get_session_id_from_existing(self, timeout: int = 10) -> Optional[str]:
        """
        从已运行的浏览器获取 session_id（不启动新浏览器）

        :param timeout: 超时时间
        :return: session_id 或 None
        """
        return self.get_session_id(timeout=timeout, auto_start=False)
