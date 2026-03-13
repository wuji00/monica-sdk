"""
Monica SDK 会话管理模块
"""
from typing import List, Dict, Any, Optional
from .models import ChatItem
from .utils import generate_uuid


class ConversationSession:
    """会话管理器 - 支持多轮对话"""

    def __init__(self):
        """初始化会话"""
        self.conversation_id: str = generate_uuid("conv")
        self.items: List[ChatItem] = []
        self.last_item_id: str = ""

    def add_message(
        self,
        content: str,
        item_type: str,
        item_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> ChatItem:
        """
        添加消息到对话历史
        :param content: 消息内容
        :param item_type: 消息类型 ("question" 或 "answer")
        :param item_id: 消息 ID（可选，自动生成）
        :param data: 额外数据
        :return: 创建的 ChatItem
        """
        if item_id is None:
            item_id = generate_uuid("msg")

        item = ChatItem(
            item_id=item_id,
            item_type=item_type,
            content=content,
            conversation_id=self.conversation_id,
            parent_item_id=self.last_item_id,
            data=data or {}
        )

        self.items.append(item)
        self.last_item_id = item_id

        return item

    def add_user_message(self, content: str, model: str = "") -> ChatItem:
        """
        添加用户消息
        :param content: 消息内容
        :param model: 使用的模型名称
        :return: 创建的 ChatItem
        """
        data = {
            "type": "text",
            "content": content,
            "quote_content": "",
            "chat_model": model.replace("-", "_"),
            "max_token": 0,
            "is_incognito": False
        }
        return self.add_message(content, "question", data=data)

    def add_assistant_message(self, content: str) -> ChatItem:
        """
        添加助手消息
        :param content: 消息内容
        :return: 创建的 ChatItem
        """
        return self.add_message(content, "answer")

    def get_items_for_request(self) -> List[Dict[str, Any]]:
        """
        获取用于 API 请求的消息列表
        :return: API 格式的消息列表
        """
        return [item.to_api_format() for item in self.items]

    def get_history(self) -> List[Dict[str, Any]]:
        """
        获取完整对话历史
        :return: 对话历史列表
        """
        return [
            {
                "role": "user" if item.item_type == "question" else "assistant",
                "content": item.content
            }
            for item in self.items
        ]

    def clear(self):
        """清空当前会话，开始新对话"""
        self.conversation_id = generate_uuid("conv")
        self.items = []
        self.last_item_id = ""

    def new_conversation(self):
        """开始新对话（clear 的别名）"""
        self.clear()

    @property
    def message_count(self) -> int:
        """获取消息数量"""
        return len(self.items)

    @property
    def last_message(self) -> Optional[ChatItem]:
        """获取最后一条消息"""
        return self.items[-1] if self.items else None

    def __len__(self) -> int:
        return len(self.items)

    def __repr__(self) -> str:
        return f"ConversationSession(conversation_id={self.conversation_id}, messages={len(self.items)})"
