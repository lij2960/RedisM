#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 RedisM 应用图标
生成不同尺寸的 PNG 图标文件
"""

import os
import sys

def create_icons():
    """创建应用图标"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("警告: 未安装 Pillow 库，跳过图标创建")
        print("如需创建图标，请运行: pip install Pillow")
        return False
    
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆角矩形背景
        padding = size // 10
        radius = size // 5
        
        # 背景颜色 - Redis 红色
        bg_color = (220, 53, 69, 255)
        
        # 绘制圆角矩形
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=radius,
            fill=bg_color
        )
        
        # 绘制 "R" 字母
        font_size = int(size * 0.5)
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        text = "R"
        # 获取文本边界框
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 居中绘制文本
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - bbox[1]
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 保存图标
        filename = f"icon_{size}.png"
        img.save(filename, 'PNG')
        print(f"已创建: {filename}")
    
    print("图标创建完成!")
    return True

if __name__ == "__main__":
    create_icons()
