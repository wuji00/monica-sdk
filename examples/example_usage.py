"""
Monica SDK 使用示例

使用前请将 YOUR_SESSION_ID 替换为你的实际 session_id
session_id 可以从浏览器 Cookie 中获取
"""

from monica_sdk import MonicaClient, AVAILABLE_MODELS


def main():
    # ============================================
    # 配置
    # ============================================

    # 从 Cookie 中获取的 session_id (JWT token)
    # 请替换为你自己的 session_id
    SESSION_ID = "YOUR_SESSION_ID_HERE"

    if SESSION_ID == "YOUR_SESSION_ID_HERE":
        print("请先设置你的 session_id!")
        print("1. 登录 https://monica.im")
        print("2. 打开浏览器开发者工具 (F12)")
        print("3. 在 Application > Cookies 中找到 session_id")
        print("4. 将其值复制到此文件的 SESSION_ID 变量中")
        return

    # ============================================
    # 初始化客户端
    # ============================================

    print("=" * 50)
    print("Monica SDK 使用示例")
    print("=" * 50)
    print()

    # 创建客户端实例
    # verbose=True 会显示详细的请求/响应日志
    client = MonicaClient(
        session_id=SESSION_ID,
        model="gemini-3-pro-preview-thinking",  # 默认模型
        verbose=True,  # 开启分层输出
        ai_resp_language="Chinese"  # AI 响应语言
    )

    print(f"可用模型: {AVAILABLE_MODELS}")
    print()

    # ============================================
    # 示例 1: 基础对话
    # ============================================

    print("\n" + "=" * 50)
    print("示例 1: 基础对话")
    print("=" * 50 + "\n")

    response = client.chat("你好，请用一句话介绍你自己")
    print(f"\n完整回复:\n{response}")

    # ============================================
    # 示例 2: 多轮对话（上下文保持）
    # ============================================

    print("\n" + "=" * 50)
    print("示例 2: 多轮对话")
    print("=" * 50 + "\n")

    # 第二轮对话会记住第一轮的内容
    response = client.chat("我刚才问了你什么问题？")
    print(f"\n回复:\n{response}")

    # 查看对话历史
    print("\n对话历史:")
    for i, msg in enumerate(client.get_history()):
        role = "用户" if msg["role"] == "user" else "助手"
        content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
        print(f"  {i + 1}. [{role}] {content}")

    # ============================================
    # 示例 3: 流式输出
    # ============================================

    print("\n" + "=" * 50)
    print("示例 3: 流式输出")
    print("=" * 50 + "\n")

    # 使用流式输出可以获得实时响应
    print("流式响应: ", end="", flush=True)
    for chunk in client.chat_stream("用三句话描述春天"):
        print(chunk.text, end="", flush=True)
    print()

    # ============================================
    # 示例 4: 获取详细响应（含思考过程）
    # ============================================

    print("\n" + "=" * 50)
    print("示例 4: 获取详细响应")
    print("=" * 50 + "\n")

    # 开始新对话
    client.new_conversation()

    # 获取包含思考过程的详细响应
    response = client.chat_with_details("1+1等于几？为什么？")

    print(f"回复内容: {response.content}")
    if response.thinking_process:
        print("\n思考过程:")
        for i, thought in enumerate(response.thinking_process[:3]):  # 只显示前3条
            print(f"  {i + 1}. {thought[:100]}...")

    # ============================================
    # 示例 5: 切换模型
    # ============================================

    print("\n" + "=" * 50)
    print("示例 5: 切换模型")
    print("=" * 50 + "\n")

    # 开始新对话
    client.new_conversation()

    # 切换模型
    client.set_model("gpt-4o")

    # 使用新模型发送消息
    response = client.chat("你好")
    print(f"\n使用 gpt-4o 的回复:\n{response}")

    # ============================================
    # 示例 6: 静默模式（无日志输出）
    # ============================================

    print("\n" + "=" * 50)
    print("示例 6: 静默模式")
    print("=" * 50 + "\n")

    # 创建静默客户端
    silent_client = MonicaClient(
        session_id=SESSION_ID,
        verbose=False  # 关闭日志输出
    )

    response = silent_client.chat("说一个笑话")
    print(f"回复: {response}")

    # ============================================
    # 会话信息
    # ============================================

    print("\n" + "=" * 50)
    print("会话信息")
    print("=" * 50)
    print(f"对话 ID: {client.conversation_id}")
    print(f"消息数量: {client.message_count}")


if __name__ == "__main__":
    main()
