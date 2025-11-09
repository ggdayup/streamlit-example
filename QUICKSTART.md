# 快速开始 - 丘成桐奖网站监控

## 一分钟快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 lxml
```

### 2. 配置邮箱

编辑 `monitor_config.json` 文件：

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "你的邮箱@gmail.com",
    "sender_password": "你的应用专用密码",
    "receiver_email": "接收通知的邮箱@example.com"
  },
  "check_interval": 3600
}
```

**Gmail用户**：需要开启"两步验证"并生成"应用专用密码"
**QQ/163邮箱**：需要开启SMTP服务并获取授权码

### 3. 运行监控

```bash
# 单次检查
python yau_awards_monitor.py --once

# 持续监控
python yau_awards_monitor.py

# 后台运行
nohup python yau_awards_monitor.py > monitor.log 2>&1 &
```

### 4. 如果遇到403错误

使用Selenium版本（需要Chrome浏览器）：

```bash
# 安装selenium
pip install selenium webdriver-manager

# 运行Selenium版本
python yau_awards_monitor_selenium.py --once
```

## 自动化脚本

我们提供了自动化脚本简化操作：

```bash
# 自动安装和配置
bash setup_monitor.sh

# 快速启动（带菜单）
bash start_monitor.sh
```

## 工作原理

1. **首次运行**: 记录当前网站上的所有通知
2. **后续检查**:
   - 定期访问网站获取最新通知
   - 与之前记录对比，找出新通知
   - 发现新通知时发送邮件提醒
3. **智能检测**: 使用内容哈希值识别变化

## 常见问题

### Q: 收不到邮件？
A: 检查以下几点：
- 邮箱配置是否正确
- 是否使用了"应用专用密码"而非账号密码
- 查看脚本输出的错误信息
- 测试邮箱SMTP连接

### Q: 提示403错误？
A: 网站有反爬虫保护，解决方案：
1. 使用Selenium版本：`python yau_awards_monitor_selenium.py --once`
2. 检查网站是否需要登录
3. 考虑使用代理或VPN

### Q: 如何修改检查频率？
A: 编辑 `monitor_config.json` 中的 `check_interval`（单位：秒）
- 30分钟 = 1800
- 1小时 = 3600
- 6小时 = 21600

### Q: 如何停止后台运行的监控？
A:
```bash
# 查找进程
ps aux | grep yau_awards_monitor

# 停止进程
kill <PID>
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `yau_awards_monitor.py` | 主监控脚本（requests版本） |
| `yau_awards_monitor_selenium.py` | Selenium版本（可绕过反爬虫） |
| `monitor_config.json` | 配置文件（邮箱、间隔等） |
| `notifications_data.json` | 自动生成，存储已检测的通知 |
| `setup_monitor.sh` | 自动安装配置脚本 |
| `start_monitor.sh` | 快速启动脚本 |
| `YAU_MONITOR_README.md` | 完整文档 |

## 获取Gmail应用专用密码

1. 访问 https://myaccount.google.com/security
2. 开启"两步验证"
3. 在"两步验证"下方选择"应用专用密码"
4. 选择"邮件"和你的设备
5. 生成密码并复制到配置文件

## 获取QQ邮箱授权码

1. 登录QQ邮箱网页版
2. 设置 → 账户 → POP3/SMTP服务
3. 开启SMTP服务
4. 按提示发送短信获取授权码
5. 将授权码填入配置文件

## 生产环境部署

### 使用systemd（推荐）

创建服务文件 `/etc/systemd/system/yau-monitor.service`:

```ini
[Unit]
Description=Yau Awards Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/streamlit-example
ExecStart=/usr/bin/python3 yau_awards_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl start yau-monitor
sudo systemctl enable yau-monitor
```

### 使用cron定时任务

```bash
# 编辑crontab
crontab -e

# 每小时执行一次
0 * * * * cd /path/to/streamlit-example && python3 yau_awards_monitor.py --once

# 每30分钟执行一次
*/30 * * * * cd /path/to/streamlit-example && python3 yau_awards_monitor.py --once
```

## 更多帮助

查看完整文档：`YAU_MONITOR_README.md`

## License

MIT
