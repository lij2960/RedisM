#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""RedisM 主入口文件"""

from .ui.main_window import MainWindow


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()