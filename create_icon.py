#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def create_simple_icon():
    """创建一个简单的文本图标文件"""
    # 创建一个简单的图标占位符
    icon_content = """
    Redis Manager Icon Placeholder
    This file serves as an icon placeholder.
    """
    
    with open('icon_placeholder.txt', 'w') as f:
        f.write(icon_content)
    
    print("简单图标占位符已创建")
    print("注意：如需真正的图标，请安装Pillow库并运行完整版本")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        
        # 创建1024x1024的图标
        size = 1024
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制Redis风格的图标
        # 背景圆形
        margin = 50
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(220, 53, 69), outline=(180, 40, 55), width=8)
        
        # 绘制数据库符号
        center_x, center_y = size // 2, size // 2
        
        # 绘制三个椭圆代表数据层
        for i, y_offset in enumerate([-120, 0, 120]):
            y = center_y + y_offset
            # 椭圆
            draw.ellipse([center_x-200, y-40, center_x+200, y+40], 
                        fill=(255, 255, 255), outline=(200, 200, 200), width=4)
            
            # 连接线
            if i < 2:
                draw.line([center_x-200, y+40, center_x-200, y+80], 
                         fill=(255, 255, 255), width=8)
                draw.line([center_x+200, y+40, center_x+200, y+80], 
                         fill=(255, 255, 255), width=8)
        
        # 保存不同尺寸的图标
        sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        for icon_size in sizes:
            resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            resized.save(f'icon_{icon_size}.png')
        
        print("图标文件已创建完成")
        
    except ImportError:
        print("Pillow库未安装，创建简单占位符")
        create_simple_icon()