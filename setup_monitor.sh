#!/bin/bash

# 丘成桐奖网站监控脚本 - 设置脚本

echo "======================================"
echo "丘成桐奖网站监控脚本 - 安装向导"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

echo "✓ Python3 已安装"
PYTHON_VERSION=$(python3 --version)
echo "  版本: $PYTHON_VERSION"
echo ""

# 安装基础依赖
echo "正在安装基础依赖..."
pip3 install -q requests beautifulsoup4 lxml
if [ $? -eq 0 ]; then
    echo "✓ 基础依赖安装成功"
else
    echo "✗ 基础依赖安装失败"
    exit 1
fi
echo ""

# 询问是否安装Selenium
echo "是否安装Selenium支持？(推荐，可绕过反爬虫保护)"
echo "需要安装ChromeDriver，可能需要额外配置"
read -p "安装Selenium? (y/n): " install_selenium

if [[ "$install_selenium" == "y" || "$install_selenium" == "Y" ]]; then
    echo "正在安装Selenium..."
    pip3 install -q selenium webdriver-manager
    if [ $? -eq 0 ]; then
        echo "✓ Selenium安装成功"
        echo "  注意: 还需要安装Chrome浏览器和ChromeDriver"
        echo "  或运行: pip3 install webdriver-manager"
    else
        echo "✗ Selenium安装失败"
    fi
fi
echo ""

# 配置邮箱
echo "======================================"
echo "配置邮箱设置"
echo "======================================"
echo ""

if [ -f "monitor_config.json" ]; then
    echo "发现已存在的配置文件: monitor_config.json"
    read -p "是否重新配置? (y/n): " reconfig
    if [[ "$reconfig" != "y" && "$reconfig" != "Y" ]]; then
        echo "保留现有配置"
        CONFIG_EXISTS=1
    fi
fi

if [ -z "$CONFIG_EXISTS" ]; then
    echo "请输入邮箱配置信息:"
    echo ""

    read -p "SMTP服务器 (如 smtp.gmail.com): " smtp_server
    read -p "SMTP端口 (通常是 587): " smtp_port
    read -p "发件人邮箱: " sender_email
    read -sp "发件人密码/应用专用密码: " sender_password
    echo ""
    read -p "收件人邮箱: " receiver_email
    read -p "检查间隔(秒，默认3600=1小时): " check_interval
    check_interval=${check_interval:-3600}

    # 生成配置文件
    cat > monitor_config.json <<EOF
{
  "email": {
    "smtp_server": "$smtp_server",
    "smtp_port": ${smtp_port:-587},
    "sender_email": "$sender_email",
    "sender_password": "$sender_password",
    "receiver_email": "$receiver_email"
  },
  "check_interval": $check_interval
}
EOF

    echo ""
    echo "✓ 配置文件已创建: monitor_config.json"
fi

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "使用方法:"
echo "  1. 单次检查:  python3 yau_awards_monitor.py --once"
echo "  2. 持续监控:  python3 yau_awards_monitor.py"
echo "  3. 后台运行:  nohup python3 yau_awards_monitor.py > monitor.log 2>&1 &"
echo ""
echo "如果遇到403错误，使用Selenium版本:"
echo "  python3 yau_awards_monitor_selenium.py --once"
echo ""
echo "查看详细文档: cat YAU_MONITOR_README.md"
echo ""
