"""
Monica SDK 数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ChatItem:
    """单条聊天消息"""
    item_id: str
    item_type: str  # "question" 或 "answer"
    content: str
    conversation_id: str = ""
    parent_item_id: str = ""
    summary: str = ""
    data: Dict[str, Any] = field(default_factory=dict)

    def to_api_format(self) -> dict:
        """转换为 API 请求格式"""
        return {
            "conversation_id": self.conversation_id,
            "item_id": self.item_id,
            "item_type": self.item_type,
            "summary": self.summary or self.content[:100],
            "parent_item_id": self.parent_item_id,
            "data": self.data or {
                "type": "text",
                "content": self.content,
                "quote_content": "",
                "chat_model": "",
                "max_token": 0,
                "is_incognito": False
            }
        }


@dataclass
class StreamChunk:
    """流式响应块"""
    text: str
    agent_status: Optional[Dict[str, Any]] = None
    is_finished: bool = False

    @property
    def is_thinking(self) -> bool:
        """是否为思考过程"""
        if self.agent_status:
            return self.agent_status.get("type") in ["thinking", "thinking_detail_stream"]
        return False

    @property
    def thinking_text(self) -> str:
        """获取思考内容"""
        if self.agent_status and self.agent_status.get("type") == "thinking_detail_stream":
            metadata = self.agent_status.get("metadata", {})
            return metadata.get("reasoning_detail", "")
        return ""

    @property
    def thinking_title(self) -> str:
        """获取思考标题"""
        if self.agent_status and self.agent_status.get("type") == "thinking_detail_stream":
            metadata = self.agent_status.get("metadata", {})
            return metadata.get("title", "")
        return ""


@dataclass
class ChatResponse:
    """完整聊天响应"""
    content: str
    thinking_process: List[str] = field(default_factory=list)
    conversation_id: str = ""
    item_id: str = ""


@dataclass
class ChatRequest:
    """请求体结构"""
    task_uid: str
    bot_uid: str
    data: Dict[str, Any]
    language: str = "auto"
    locale: str = "en"
    task_type: str = "chat_with_custom_bot"
    tool_data: Dict[str, Any] = field(default_factory=dict)
    ai_resp_language: str = "English"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "task_uid": self.task_uid,
            "bot_uid": self.bot_uid,
            "data": self.data,
            "language": self.language,
            "locale": self.locale,
            "task_type": self.task_type,
            "tool_data": self.tool_data,
            "ai_resp_language": self.ai_resp_language
        }
