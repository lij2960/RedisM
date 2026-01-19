#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""应用配置文件"""

__version__ = "1.1.0"
__app_name__ = "RedisM"

# 应用设置
APP_TITLE = f"{__app_name__} v{__version__}"
WINDOW_SIZE = "1600x1000"
BACKGROUND_COLOR = "#F2F2F7"

# Redis设置
DEFAULT_REDIS_PORT = 6379
DEFAULT_SSH_PORT = 22
DEFAULT_MAX_KEYS = 0
DEFAULT_DB_COUNT = 16
MAX_KEYS_STREAMING = 100000

# UI设置
TREE_ROW_HEIGHT = 28
HOVER_COLOR = "#E8F4FD"
SELECTED_COLOR = "#007AFF"

# 字体设置
FONT_FAMILY = "SF Pro Display"
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADING = 12
FONT_SIZE_NORMAL = 10
FONT_SIZE_SMALL = 9
FONT_FAMILY_CODE = "Menlo"