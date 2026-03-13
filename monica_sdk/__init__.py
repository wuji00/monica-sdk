"""
Monica AI Chat SDK

一个用于与 Monica AI 聊天 API 交互的 Python SDK

使用示例:
    from monica_sdk import MonicaClient

    # 初始化客户端
    client = MonicaClient(
        session_id="your_session_id_here",
        verbose=True
    )

    # 发送消息
    response = client.chat("你好！")
    print(response)

    # 多轮对话
    response = client.chat("介绍一下你自己")
    print(response)

    # 开始新对话
    client.new_conversation()

    # 流式输出
    for chunk in client.chat_stream("写一首诗"):
        print(chunk.text, end="", flush=True)
"""

from .client import MonicaClient
from .models import ChatItem, ChatResponse, ChatRequest, StreamChunk
from .session import ConversationSession
from .auth import MonicaAuth
from .config import (
    API_BASE_URL,
    CHAT_ENDPOINT,
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
)

__version__ = "1.0.0"
__author__ = "Monica SDK"

__all__ = [
    # 主要客户端
    "MonicaClient",

    # 数据模型
    "ChatItem",
    "ChatResponse",
    "ChatRequest",
    "StreamChunk",

    # 会话管理
    "ConversationSession",

    # 认证管理
    "MonicaAuth",

    # 配置常量
    "API_BASE_URL",
    "CHAT_ENDPOINT",
    "DEFAULT_MODEL",
    "AVAILABLE_MODELS",
]
