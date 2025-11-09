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
echo ""
echo "推荐模式 (适合有反爬虫保护的网站):"
echo "  1) 手动辅助模式 ⭐ 推荐"
echo "  2) 网站访问诊断工具"
echo ""
echo "自动监控模式 (可能遇到403错误):"
echo "  3) 单次检查 (基础HTTP)"
echo "  4) 持续监控 (基础HTTP)"
echo "  5) 后台运行 (基础HTTP)"
echo ""
echo "高级模式 (需要Chrome浏览器):"
echo "  6) Selenium版本 - 单次检查"
echo "  7) Selenium版本 - 持续监控"
echo ""
read -p "请选择 (1-7): " choice

case $choice in
    1)
        echo "启动手动辅助模式..."
        echo "说明: 你可以手动录入从网站看到的新通知"
        echo ""
        python3 yau_awards_monitor_manual.py
        ;;
    2)
        echo "运行网站访问诊断..."
        python3 test_website_access.py
        ;;
    3)
        echo "开始单次检查 (基础HTTP)..."
        python3 yau_awards_monitor.py --once
        ;;
    4)
        echo "开始持续监控 (基础HTTP，按Ctrl+C停止)..."
        python3 yau_awards_monitor.py
        ;;
    5)
        echo "启动后台监控 (基础HTTP)..."
        nohup python3 yau_awards_monitor.py > monitor.log 2>&1 &
        PID=$!
        echo "✓ 监控已在后台启动 (PID: $PID)"
        echo "  查看日志: tail -f monitor.log"
        echo "  停止监控: kill $PID"
        ;;
    6)
        echo "开始Selenium单次检查..."
        python3 yau_awards_monitor_selenium.py --once
        ;;
    7)
        echo "开始Selenium持续监控 (按Ctrl+C停止)..."
        python3 yau_awards_monitor_selenium.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
