#!/bin/bash

# RedisM v1.1.2 快速重新打包脚本

echo "=========================================="
echo "RedisM v1.1.2 快速重新打包"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 步骤1: 清理
echo -e "${YELLOW}步骤 1/5: 清理之前的构建...${NC}"
rm -rf build dist
rm -f RedisM.dmg
echo -e "${GREEN}✓ 清理完成${NC}"
echo ""

# 步骤2: 检查虚拟环境
echo -e "${YELLOW}步骤 2/5: 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 步骤3: 安装依赖
echo -e "${YELLOW}步骤 3/5: 安装依赖...${NC}"
pip install -q -r requirements.txt
pip install -q pyinstaller
echo -e "${GREEN}✓ 依赖安装完成${NC}"
echo ""

# 步骤4: 验证导入
echo -e "${YELLOW}步骤 4/5: 验证模块导入...${NC}"
python3 test_imports.py
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 模块导入验证失败，请检查依赖${NC}"
    exit 1
fi
echo ""

# 步骤5: 打包
echo -e "${YELLOW}步骤 5/5: 开始打包...${NC}"
pyinstaller RedisM.spec

# 检查结果
if [ -d "dist/RedisM.app" ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "✓ 打包成功！"
    echo "==========================================${NC}"
    echo ""
    echo "应用位置: dist/RedisM.app"
    echo "应用大小: $(du -sh dist/RedisM.app | cut -f1)"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo "1. 测试应用: open dist/RedisM.app"
    echo "2. 查看日志: ./dist/RedisM.app/Contents/MacOS/RedisM"
    echo "3. 创建 DMG: hdiutil create -volname RedisM -srcfolder dist/RedisM.app -ov -format UDZO RedisM.dmg"
    echo ""
    
    # 询问是否创建 DMG
    read -p "是否创建 DMG 安装包? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "创建 DMG 安装包..."
        hdiutil create -volname "RedisM" -srcfolder "dist/RedisM.app" -ov -format UDZO "RedisM.dmg"
        if [ -f "RedisM.dmg" ]; then
            echo -e "${GREEN}✓ DMG 安装包已创建: RedisM.dmg${NC}"
            echo "DMG 大小: $(du -sh RedisM.dmg | cut -f1)"
        fi
    fi
else
    echo -e "${RED}✗ 打包失败，请检查错误信息${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}完成！${NC}"
