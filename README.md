# Monica AI Chat SDK

一个用于与 Monica AI 聊天 API 交互的 Python SDK，支持自动获取 Cookie。

## 功能特性

- 自动通过 Chrome DevTools Protocol 获取 `session_id`
- 支持多轮对话
- 支持流式输出
- 支持多种模型选择

## 安装

使用 [uv](https://github.com/astral-sh/uv) 管理依赖：

```bash
# 克隆项目
git clone https://github.com/wuji00/monica-sdk.git
cd monica-sdk

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e .

# 安装 Playwright 浏览器
uv run playwright install chromium
```

或使用 pip：

```bash
pip install -e .
playwright install chromium
```

## 使用方法

### 方式 1：自动启动浏览器获取 Cookie（推荐）

```python
from monica_sdk import MonicaClient

# 自动启动 Chrome，等待登录后获取 session_id
client = MonicaClient.auto_login(verbose=True)

# 发送消息
response = client.chat("你好！")
print(response)

# 流式输出
for chunk in client.chat_stream("写一首诗"):
    print(chunk.text, end="", flush=True)
```

### 方式 2：连接已有浏览器

首先手动启动带调试端口的 Chrome：

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="D:\data\chrome"

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome-debug"
```

然后在浏览器中登录 [monica.im](https://monica.im)，之后运行：

```python
from monica_sdk import MonicaClient

# 连接到已登录的浏览器
client = MonicaClient.from_logged_in_browser(verbose=True)

response = client.chat("你好！")
print(response)
```

### 方式 3：手动提供 session_id

```python
from monica_sdk import MonicaClient

# 从浏览器 Cookie 中手动获取 session_id
client = MonicaClient(
    session_id="your_session_id_here",
    verbose=True
)

response = client.chat("你好！")
print(response)
```

## API 参考

### MonicaClient

主客户端类，用于与 Monica AI API 交互。

#### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `session_id` | str | 必填 | 从 Cookie 获取的认证 token |
| `model` | str | `"claude-sonnet-4-6"` | 使用的模型 |
| `verbose` | bool | `True` | 是否输出详细信息 |
| `ai_resp_language` | str | `"Chinese"` | AI 响应语言 |

#### 类方法

| 方法 | 说明 |
|------|------|
| `auto_login(browser, timeout, use_existing_profile, use_default_profile)` | 自动启动浏览器获取 session_id |
| `from_logged_in_browser(port)` | 连接到已登录的浏览器 |

#### 实例方法

| 方法 | 说明 |
|------|------|
| `chat(message)` | 发送消息并获取响应 |
| `chat_stream(message)` | 流式发送消息，返回生成器 |
| `new_conversation()` | 开始新对话 |

### MonicaAuth

认证管理类，用于自动获取 Cookie。

```python
from monica_sdk import MonicaAuth

auth = MonicaAuth(port=9222, browser="chrome")
session_id = auth.get_session_id(timeout=60, auto_start=True)
```

## 可用模型

- `claude-sonnet-4-6` (默认)
- `claude-opus-4-6`
- `gpt-4o`
- `gpt-4-turbo`
- 更多模型请参考 `monica_sdk/config.py`

## 项目结构

```
monica-sdk/
├── monica_sdk/          # 核心 SDK 代码
│   ├── __init__.py
│   ├── auth.py          # 自动获取 Cookie
│   ├── client.py        # 主客户端
│   ├── config.py        # 配置常量
│   ├── models.py        # 数据模型
│   ├── session.py       # 会话管理
│   └── utils.py         # 工具函数
├── tests/               # 测试文件
├── examples/            # 示例代码
├── pyproject.toml
└── README.md
```

## 运行测试

```bash
# 基础测试
uv run python tests/test_auto_auth.py -b

# 完整流程测试
uv run python tests/test_full_flow.py
```

## 注意事项

1. **代理设置**：如果使用代理访问 monica.im，SDK 会自动处理 localhost 的代理绕过
2. **Chrome 锁定**：使用 `auto_login()` 时会启动新的 Chrome 实例，避免与现有 Chrome 冲突
3. **Cookie 过期**：`session_id` 会过期，需要定期重新获取

## License

MIT
