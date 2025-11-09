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

echo "⚠️  重要: 网站有严格的反爬虫保护，自动监控可能失败"
echo "   详情查看: cat AUTOMATED_MONITORING_STATUS.md"
echo ""
echo "选择运行模式:"
echo ""
echo "诊断工具:"
echo "  1) 网站访问诊断"
echo ""
echo "自动监控模式 (⚠️  当前都遇到403错误):"
echo "  2) 增强自动监控 - 单次 (Cloudscraper)"
echo "  3) 增强自动监控 - 持续 (Cloudscraper)"
echo "  4) 基础HTTP - 单次"
echo "  5) 基础HTTP - 持续"
echo "  6) 基础HTTP - 后台运行"
echo ""
echo "浏览器自动化 (建议在本地机器运行):"
echo "  7) Selenium - 单次检查"
echo "  8) Selenium - 持续监控"
echo "  9) Playwright - 单次检查"
echo ""
read -p "请选择 (1-9): " choice

case $choice in
    1)
        echo "运行网站访问诊断..."
        python3 test_website_access.py
        ;;
    2)
        echo "开始增强自动监控 (单次)..."
        python3 yau_awards_monitor_auto.py --once
        ;;
    3)
        echo "开始增强自动监控 (持续，按Ctrl+C停止)..."
        python3 yau_awards_monitor_auto.py
        ;;
    4)
        echo "开始单次检查 (基础HTTP)..."
        python3 yau_awards_monitor.py --once
        ;;
    5)
        echo "开始持续监控 (基础HTTP，按Ctrl+C停止)..."
        python3 yau_awards_monitor.py
        ;;
    6)
        echo "启动后台监控 (基础HTTP)..."
        nohup python3 yau_awards_monitor.py > monitor.log 2>&1 &
        PID=$!
        echo "✓ 监控已在后台启动 (PID: $PID)"
        echo "  查看日志: tail -f monitor.log"
        echo "  停止监控: kill $PID"
        ;;
    7)
        echo "开始Selenium单次检查..."
        echo "💡 提示: 建议在本地机器(非容器)运行"
        python3 yau_awards_monitor_selenium.py --once
        ;;
    8)
        echo "开始Selenium持续监控 (按Ctrl+C停止)..."
        echo "💡 提示: 建议在本地机器(非容器)运行"
        python3 yau_awards_monitor_selenium.py
        ;;
    9)
        echo "开始Playwright单次检查..."
        echo "💡 提示: 需要playwright浏览器"
        python3 yau_awards_monitor_playwright.py --once
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
