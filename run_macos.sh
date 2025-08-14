#!/bin/bash

# macOS专用启动脚本
# 支持豆包AI和Gemini AI两个版本

echo "🍎 macOS测试用例生成器启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "检查Python依赖..."
python3 -c "import tkinter" 2>/dev/null || {
    echo "❌ 未找到tkinter，请安装Python的tkinter支持"
    exit 1
}

# 检查豆包模块
if [ -f "doubao.py" ]; then
    echo "✅ 找到豆包AI模块"
    DOUBAO_AVAILABLE=true
else
    echo "⚠️  未找到豆包AI模块"
    DOUBAO_AVAILABLE=false
fi

# 检查Gemini模块
if [ -f "gemini.py" ] && [ -f "gui.py" ]; then
    echo "✅ 找到Gemini AI模块"
    GEMINI_AVAILABLE=true
else
    echo "⚠️  未找到Gemini AI模块"
    GEMINI_AVAILABLE=false
fi

# 选择启动版本
echo ""
echo "请选择要启动的版本:"
if [ "$DOUBAO_AVAILABLE" = true ]; then
    echo "1. 豆包AI版本 (doubao_gui.py)"
fi
if [ "$GEMINI_AVAILABLE" = true ]; then
    echo "2. Gemini AI版本 (gui.py)"
fi
echo "3. 退出"

read -p "请输入选择: " choice

case $choice in
    1)
        if [ "$DOUBAO_AVAILABLE" = true ]; then
            echo "🚀 启动豆包AI版本..."
            python3 doubao_gui.py
        else
            echo "❌ 豆包AI版本不可用"
        fi
        ;;
    2)
        if [ "$GEMINI_AVAILABLE" = true ]; then
            echo "🚀 启动Gemini AI版本..."
            python3 gui.py
        else
            echo "❌ Gemini AI版本不可用"
        fi
        ;;
    3)
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
