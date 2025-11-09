#!/bin/bash

# 丘成桐奖网站监控脚本 - 快速启动

echo "======================================"
echo "丘成桐奖网站监控脚本"
echo "======================================"
echo ""

# 检查配置文件
if [ ! -f "monitor_config.json" ]; then
    echo "错误: 未找到配置文件 monitor_config.json"
    echo "请先运行安装脚本: bash setup_monitor.sh"
    exit 1
fi

# 检查Python和依赖
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "错误: 缺少必要的Python库"
    echo "请运行: pip3 install -r requirements_monitor.txt"
    exit 1
fi

echo "选择运行模式:"
echo "  1) 单次检查 (检查一次后退出)"
echo "  2) 持续监控 (按配置间隔持续检查)"
echo "  3) 后台运行 (持续监控，后台运行)"
echo "  4) Selenium版本 - 单次检查 (可绕过403错误)"
echo "  5) Selenium版本 - 持续监控"
echo ""
read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo "开始单次检查..."
        python3 yau_awards_monitor.py --once
        ;;
    2)
        echo "开始持续监控 (按Ctrl+C停止)..."
        python3 yau_awards_monitor.py
        ;;
    3)
        echo "启动后台监控..."
        nohup python3 yau_awards_monitor.py > monitor.log 2>&1 &
        PID=$!
        echo "✓ 监控已在后台启动 (PID: $PID)"
        echo "  查看日志: tail -f monitor.log"
        echo "  停止监控: kill $PID"
        ;;
    4)
        echo "开始Selenium单次检查..."
        python3 yau_awards_monitor_selenium.py --once
        ;;
    5)
        echo "开始Selenium持续监控 (按Ctrl+C停止)..."
        python3 yau_awards_monitor_selenium.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
