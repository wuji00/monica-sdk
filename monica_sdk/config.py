"""
Monica SDK 配置模块
"""

# API 基础配置
API_BASE_URL = "https://api.monica.im"
CHAT_ENDPOINT = "/api/custom_bot/chat"

# 默认请求头
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": "https://monica.im",
    "Referer": "https://monica.im/",
    "x-client-type": "web",
    "x-client-version": "5.4.3",
    "x-product-name": "Monica",
    "x-from-channel": "NA",
}

# 默认时区
DEFAULT_TIMEZONE = "Asia/Shanghai;-480"

# 默认语言
DEFAULT_LOCALE = "en"

# 默认模型
DEFAULT_MODEL = "claude-sonnet-4-6"

# 可用模型列表 (已验证可用)
AVAILABLE_MODELS = [
    # Claude 4.6 系列 (推荐)
    "claude-sonnet-4-6",      # Claude Sonnet 4.6 - 平衡性能与速度
    "claude-opus-4-6",        # Claude Opus 4.6 - 最强能力
    # GPT 5.x 系列
    "gpt-5.3-codex",          # GPT 5.3 Codex - 代码优化
    "gpt-5.4",                # GPT 5.4 - 通用
    "gpt-5.4-pro",            # GPT 5.4 Pro - 增强版
    # GPT 4.x 系列
    "gpt-4o",                 # GPT-4o - 快速多模态
    "gpt-4o-mini",            # GPT-4o Mini - 轻量版
    # Claude 3.x 系列
    "claude-3-5-sonnet",      # Claude 3.5 Sonnet
    "claude-3-opus",          # Claude 3 Opus
    "claude-3-sonnet",        # Claude 3 Sonnet
    "claude-3-haiku",         # Claude 3 Haiku - 快速
    # Gemini 系列
    "gemini-2.5-pro",         # Gemini 2.5 Pro
    "gemini-2.0-flash",       # Gemini 2.0 Flash - 快速
]

# 不可用/不稳定模型列表 (仅供参考)
UNAVAILABLE_MODELS = [
    "gemini-3-pro-preview-thinking",    # 返回服务器错误
    "gemini-3.1-pro-preview-thinking",  # 返回空响应
]

# 默认 bot_uid
DEFAULT_BOT_UID = "monica"

# 默认任务类型
DEFAULT_TASK_TYPE = "chat_with_custom_bot"

# 默认技能列表
DEFAULT_SKILL_LIST = [
    {"uid": "web_access", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "draw_image", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "book_calendar", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "code_interpreter", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "artifacts", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "memory", "allow_user_modify": False, "enable": True, "force_enable": False},
    {"uid": "use_custom_memory", "allow_user_modify": False, "enable": True, "force_enable": False},
]
