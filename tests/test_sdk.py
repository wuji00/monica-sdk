"""
Monica SDK 测试脚本
"""
from monica_sdk import MonicaClient

# 从文档中提取的 session_id
SESSION_ID = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3NjcxNTIyOTYsImlzcyI6Im1vbmljYSIsInVzZXJfaWQiOjIxMDA4ODgsInVzZXJfbmFtZSI6Inh1YW55ZSB3dSIsImp0aSI6IjY2Y2NlN2UzNTVmYjQ2OWRhMjQ1Y2Q1ZTI5ZDdhNDczIiwiY2xpZW50X3R5cGUiOiJleHRlbnNpb24ifQ.Ytbb9wXSdVR7wikvZs4zTUdcelvF3kvhf0uG4rEAbI0"


def test_basic_chat():
    """测试基础对话"""
    print("=" * 60)
    print("测试 1: 基础对话")
    print("=" * 60)

    client = MonicaClient(
        session_id=SESSION_ID,
        verbose=True,
        ai_resp_language="Chinese"
    )

    response = client.chat("你好，请用一句话介绍你自己")
    print(f"\n完整回复:\n{response}")
    return client


def test_multi_turn(client):
    """测试多轮对话"""
    print("\n" + "=" * 60)
    print("测试 2: 多轮对话")
    print("=" * 60)

    response = client.chat("我刚才问了你什么？")
    print(f"\n回复:\n{response}")

    print("\n对话历史:")
    for i, msg in enumerate(client.get_history()):
        role = "用户" if msg["role"] == "user" else "助手"
        content = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
        print(f"  {i + 1}. [{role}] {content}")


def test_stream_chat(client):
    """测试流式输出"""
    print("\n" + "=" * 60)
    print("测试 3: 流式输出")
    print("=" * 60)

    client.new_conversation()

    print("\n流式响应 (verbose 模式会自动打印):\n")
    full_text = ""
    for chunk in client.chat_stream("用三句话描述春天"):
        full_text += chunk.text

    print(f"\n收集到的完整响应: {full_text[:100]}..." if len(full_text) > 100 else f"\n收集到的完整响应: {full_text}")


def main():
    try:
        client = test_basic_chat()
        test_multi_turn(client)
        test_stream_chat(client)

        print("\n" + "=" * 60)
        print("所有测试完成!")
        print("=" * 60)

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
