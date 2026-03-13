"""
Monica SDK 核心客户端
"""
import json
from typing import Generator, Optional, List, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    API_BASE_URL,
    CHAT_ENDPOINT,
    DEFAULT_HEADERS,
    DEFAULT_TIMEZONE,
    DEFAULT_LOCALE,
    DEFAULT_MODEL,
    DEFAULT_BOT_UID,
    DEFAULT_TASK_TYPE,
    DEFAULT_SKILL_LIST,
)
from .models import ChatItem, StreamChunk, ChatResponse, ChatRequest
from .session import ConversationSession
from .utils import (
    generate_uuid,
    generate_client_id,
    ConsoleLogger,
    parse_sse_line,
)


class MonicaClient:
    """Monica AI 客户端"""

    def __init__(
        self,
        session_id: str,
        model: str = DEFAULT_MODEL,
        verbose: bool = True,
        ai_resp_language: str = "Chinese"
    ):
        """
        初始化客户端
        :param session_id: 从 Cookie 获取的认证 token (JWT)
        :param model: 默认使用的模型
        :param verbose: 是否在控制台分层输出
        :param ai_resp_language: AI 响应语言
        """
        self.session_id = session_id
        self.model = model
        self.verbose = verbose
        self.ai_resp_language = ai_resp_language

        # 初始化会话
        self._session = ConversationSession()

        # 初始化日志器
        self._logger = ConsoleLogger(enabled=verbose)

        # 初始化 HTTP 客户端
        self._http = self._create_http_client()

        # 生成客户端 ID
        self._client_id = generate_client_id()

    def _create_http_client(self) -> requests.Session:
        """创建带重试机制的 HTTP 客户端"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = DEFAULT_HEADERS.copy()
        headers["Cookie"] = f"session_id={self.session_id}"
        headers["x-client-id"] = self._client_id
        headers["x-client-locale"] = DEFAULT_LOCALE
        headers["x-time-zone"] = DEFAULT_TIMEZONE
        return headers

    def _build_request_body(self, message: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        构建请求体
        :param message: 用户消息
        :param model: 使用的模型（可选，使用默认模型）
        :return: 请求体字典
        """
        use_model = model or self.model

        # 添加用户消息到会话
        user_item = self._session.add_user_message(message, use_model)

        # 预生成回复 ID
        pre_reply_id = generate_uuid("msg")

        # 构建请求体
        body = {
            "task_uid": generate_uuid("task"),
            "bot_uid": DEFAULT_BOT_UID,
            "data": {
                "conversation_id": self._session.conversation_id,
                "items": self._session.get_items_for_request(),
                "pre_generated_reply_id": pre_reply_id,
                "pre_parent_item_id": user_item.item_id,
                "origin": "https://monica.im/home/chat/Monica/monica",
                "origin_page_title": "Monica Chat",
                "trigger_by": "auto",
                "use_model": use_model,
                "knowledge_source": "developer",
                "is_incognito": False,
                "use_new_memory": True,
                "use_memory_suggestion": True,
            },
            "language": "auto",
            "locale": DEFAULT_LOCALE,
            "task_type": DEFAULT_TASK_TYPE,
            "tool_data": {
                "sys_skill_list": DEFAULT_SKILL_LIST
            },
            "ai_resp_language": self.ai_resp_language
        }

        return body

    def _send_request(self, body: Dict[str, Any]) -> Generator[StreamChunk, None, None]:
        """
        发送请求并返回流式响应
        :param body: 请求体
        :return: StreamChunk 生成器
        """
        url = f"{API_BASE_URL}{CHAT_ENDPOINT}"
        headers = self._build_headers()

        response = self._http.post(
            url,
            headers=headers,
            json=body,
            stream=True,
            timeout=120
        )

        response.raise_for_status()

        # 解析 SSE 流
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = parse_sse_line(line)
            if data is None:
                continue

            chunk = StreamChunk(
                text=data.get("text", ""),
                agent_status=data.get("agent_status"),
                is_finished=data.get("finished", False)
            )

            yield chunk

    def chat_stream(
        self,
        message: str,
        model: Optional[str] = None
    ) -> Generator[StreamChunk, None, None]:
        """
        流式聊天（生成器）- 实时返回响应块
        :param message: 用户消息
        :param model: 使用的模型（可选）
        :return: StreamChunk 生成器
        """
        use_model = model or self.model

        # 记录请求
        self._logger.log_request(
            url=f"{API_BASE_URL}{CHAT_ENDPOINT}",
            conversation_id=self._session.conversation_id,
            model=use_model,
            message=message
        )

        # 构建请求体
        body = self._build_request_body(message, use_model)

        # 发送请求并处理流式响应
        full_content = ""
        thinking_parts = []

        try:
            for chunk in self._send_request(body):
                # 处理思考过程
                if chunk.is_thinking and chunk.thinking_text:
                    self._logger.log_thinking(chunk.thinking_text)
                    thinking_parts.append(chunk.thinking_text)

                # 处理内容
                if chunk.text:
                    self._logger.log_content(chunk.text)
                    full_content += chunk.text

                # 完成
                if chunk.is_finished:
                    self._logger.log_response_complete()

                yield chunk

            # 添加助手回复到会话历史
            if full_content:
                self._session.add_assistant_message(full_content)

        except requests.RequestException as e:
            self._logger.log_error(str(e))
            raise

    def chat(self, message: str, model: Optional[str] = None) -> str:
        """
        发送消息并返回完整响应（阻塞式）
        :param message: 用户消息
        :param model: 使用的模型（可选）
        :return: 完整的响应文本
        """
        full_content = ""

        for chunk in self.chat_stream(message, model):
            full_content += chunk.text

        return full_content

    def chat_with_details(
        self,
        message: str,
        model: Optional[str] = None
    ) -> ChatResponse:
        """
        发送消息并返回详细响应（包含思考过程）
        :param message: 用户消息
        :param model: 使用的模型（可选）
        :return: ChatResponse 对象
        """
        full_content = ""
        thinking_parts = []

        for chunk in self.chat_stream(message, model):
            full_content += chunk.text
            if chunk.is_thinking and chunk.thinking_text:
                thinking_parts.append(chunk.thinking_text)

        return ChatResponse(
            content=full_content,
            thinking_process=thinking_parts,
            conversation_id=self._session.conversation_id,
            item_id=self._session.last_item_id if self._session.last_item_id else ""
        )

    def new_conversation(self):
        """开始新对话"""
        self._session.new_conversation()
        self._logger.log_info("已开始新对话")

    def clear_history(self):
        """清空对话历史（new_conversation 的别名）"""
        self.new_conversation()

    def get_history(self) -> List[Dict[str, Any]]:
        """
        获取当前会话的对话历史
        :return: 对话历史列表
        """
        return self._session.get_history()

    @property
    def conversation_id(self) -> str:
        """获取当前对话 ID"""
        return self._session.conversation_id

    @property
    def message_count(self) -> int:
        """获取当前会话的消息数量"""
        return self._session.message_count

    def set_model(self, model: str):
        """
        设置默认模型
        :param model: 模型名称
        """
        self.model = model
        self._logger.log_info(f"已切换模型: {model}")

    def __repr__(self) -> str:
        return (
            f"MonicaClient("
            f"model={self.model}, "
            f"conversation_id={self.conversation_id}, "
            f"messages={self.message_count})"
        )

    @classmethod
    def auto_login(cls, browser: str = "chrome", timeout: int = 60, use_existing_profile: bool = True, use_default_profile: bool = False, **kwargs):
        """
        自动启动浏览器，等待用户登录后创建客户端

        :param browser: 浏览器类型 ("chrome" 或 "edge")
        :param timeout: 等待登录的超时时间
        :param use_existing_profile: 是否复制现有浏览器的 Cookies（避免重新登录）
        :param use_default_profile: 是否直接使用 Default profile（需要关闭其他 Chrome，但保留登录状态）
        :return: MonicaClient 实例
        """
        from .auth import MonicaAuth
        auth = MonicaAuth(
            browser=browser,
            use_existing_profile=use_existing_profile,
            use_default_profile=use_default_profile
        )
        session_id = auth.get_session_id(timeout=timeout, auto_start=True)

        if not session_id:
            raise ValueError("无法获取 session_id，请确保已登录")

        return cls(session_id=session_id, **kwargs)

    @classmethod
    def from_logged_in_browser(cls, port: int = 9222, **kwargs):
        """
        从已登录的浏览器获取 session_id（浏览器需已启动并登录）

        :param port: 调试端口
        :return: MonicaClient 实例
        """
        from .auth import MonicaAuth
        auth = MonicaAuth(port=port)
        session_id = auth.get_session_id_from_existing()

        if not session_id:
            raise ValueError("无法从浏览器获取 session_id，请确保已登录 monica.im")

        return cls(session_id=session_id, **kwargs)
