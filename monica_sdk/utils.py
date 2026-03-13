"""
Monica SDK 工具函数
"""
import uuid
from typing import Optional, Dict, Any


def generate_uuid(prefix: str = "") -> str:
    """
    生成带前缀的 UUID
    :param prefix: 前缀，如 "task", "conv", "msg"
    :return: 格式化的 UUID 字符串，如 "task:xxx", "conv:xxx"
    """
    uid = str(uuid.uuid4())
    if prefix:
        return f"{prefix}:{uid}"
    return uid


def generate_client_id() -> str:
    """生成客户端 ID (不带前缀的 UUID)"""
    return str(uuid.uuid4())


class ConsoleLogger:
    """控制台分层输出器"""

    # ANSI 颜色代码
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "dim": "\033[2m",
    }

    # 边框字符
    BOX = {
        "tl": "╔", "tr": "╗",  # 顶部左右
        "bl": "╚", "br": "╝",  # 底部左右
        "h": "═", "v": "║",    # 横线和竖线
        "lt": "╠", "rt": "╣",  # 左右 T 形
    }

    def __init__(self, enabled: bool = True):
        """
        :param enabled: 是否启用日志输出
        """
        self.enabled = enabled

    def _color(self, text: str, color: str) -> str:
        """添加颜色"""
        if not self.enabled:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def _box_line(self, text: str, width: int = 60) -> str:
        """生成带边框的行"""
        padding = width - len(text) - 2  # 减去两个空格
        return f"{self.BOX['v']} {text}{' ' * max(0, padding)} {self.BOX['v']}"

    def _separator(self, width: int = 60) -> str:
        """生成分隔线"""
        return f"{self.BOX['lt']}{self.BOX['h'] * (width - 2)}{self.BOX['rt']}"

    def _top_border(self, width: int = 60) -> str:
        """生成顶部边框"""
        return f"{self.BOX['tl']}{self.BOX['h'] * (width - 2)}{self.BOX['tr']}"

    def _bottom_border(self, width: int = 60) -> str:
        """生成底部边框"""
        return f"{self.BOX['bl']}{self.BOX['h'] * (width - 2)}{self.BOX['br']}"

    def _title_line(self, title: str, width: int = 60) -> str:
        """生成标题行"""
        padding = width - len(title) - 2
        left_pad = padding // 2
        right_pad = padding - left_pad
        return f"{self.BOX['v']}{' ' * left_pad}{title}{' ' * right_pad}{self.BOX['v']}"

    def log_request(self, url: str, conversation_id: str, model: str, message: str):
        """记录请求信息"""
        if not self.enabled:
            return

        width = 62
        print()
        print(self._color(self._top_border(width), "cyan"))
        print(self._color(self._title_line("[Monica SDK] 请求发送", width), "cyan"))
        print(self._color(self._separator(width), "cyan"))

        # 请求信息
        print(self._color(self._box_line(f"{self._color('[请求信息]', 'bold')}"), "cyan"))
        print(self._color(self._box_line(f"  ├── URL: {url[:45]}..." if len(url) > 45 else f"  ├── URL: {url}"), "cyan"))
        print(self._color(self._box_line(f"  ├── 对话ID: {conversation_id}"), "cyan"))
        print(self._color(self._box_line(f"  ├── 模型: {model}"), "cyan"))

        # 截断过长的消息
        display_msg = message[:50] + "..." if len(message) > 50 else message
        print(self._color(self._box_line(f"  └── 消息: {display_msg}"), "cyan"))

        print(self._color(self._separator(width), "cyan"))
        print(self._color(self._box_line(f"{self._color('[响应流]', 'bold')}"), "cyan"))

    def log_thinking(self, text: str):
        """记录思考过程"""
        if not self.enabled:
            return

        # 提取标题部分
        if text.startswith("**") and "**" in text[2:]:
            title_end = text.index("**", 2)
            title = text[2:title_end]
            content = text[title_end + 2:].strip()
        else:
            title = "思考中..."
            content = text

        # 截断内容
        if len(content) > 80:
            content = content[:80] + "..."

        line = f"  ├── {self._color('[思考]', 'yellow')} {title}"
        if content:
            line += f" - {content}"

        print(self._color(self._box_line(line, 62), "cyan"))

    def log_content(self, text: str, is_chunk: bool = True):
        """记录内容"""
        if not self.enabled:
            return

        if is_chunk:
            # 对于流式内容，直接打印（不带边框）
            print(text, end="", flush=True)
        else:
            # 对于完整内容，带边框显示
            lines = text.split('\n')
            for line in lines[:5]:  # 最多显示 5 行
                if len(line) > 56:
                    line = line[:56] + "..."
                print(self._color(self._box_line(f"  │ {line}", 62), "cyan"))
            if len(lines) > 5:
                print(self._color(self._box_line(f"  │ ... (还有 {len(lines) - 5} 行)", 62), "cyan"))

    def log_response_complete(self):
        """响应完成"""
        if not self.enabled:
            return

        print()  # 换行
        print(self._color(self._box_line("  └── [完成] 响应结束", 62), "cyan"))
        print(self._color(self._bottom_border(62), "cyan"))
        print()

    def log_error(self, error: str):
        """记录错误"""
        if not self.enabled:
            return

        print(self._color(f"[错误] {error}", "magenta"))

    def log_info(self, message: str):
        """记录信息"""
        if not self.enabled:
            return

        print(self._color(f"[信息] {message}", "blue"))


def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """
    解析 SSE 行
    :param line: SSE 格式的行，支持两种格式:
                 - "data: {...}" (标准 SSE 格式)
                 - "message\t{...}" (Monica API 格式)
    :return: 解析后的 JSON 对象，解析失败返回 None
    """
    import json

    line = line.strip()
    if not line:
        return None

    # 标准 SSE 格式: data: {...}
    if line.startswith("data:"):
        json_str = line[5:].strip()
        if json_str:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None

    # Monica API 格式: message\t{...} 或 message {JSON}
    if line.startswith("message"):
        # 去掉 "message" 前缀
        rest = line[7:].strip()
        # 可能是 tab 分隔或空格分隔
        if rest.startswith("\t"):
            rest = rest[1:]
        # 尝试解析 JSON
        if rest:
            try:
                return json.loads(rest)
            except json.JSONDecodeError:
                return None

    return None
