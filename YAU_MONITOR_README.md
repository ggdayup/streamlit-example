# 丘成桐奖官网通知监控脚本

自动监控 http://www.yau-awards.com/ 网站的"通知公告"部分，当有新通知发布时自动发送邮件提醒。

## 功能特点

- 🔍 自动抓取网站通知公告
- 📧 新通知邮件提醒（支持HTML格式）
- 💾 智能检测变化（基于内容哈希）
- ⏰ 可配置检查间隔
- 🔄 持续监控或单次检查模式

## 安装依赖

```bash
pip install -r requirements_monitor.txt
```

## 配置邮箱

编辑 `monitor_config.json` 文件，配置邮箱信息：

```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_app_password_here",
    "receiver_email": "receiver@example.com"
  },
  "check_interval": 3600
}
```

### 常用邮箱SMTP配置

| 邮箱服务 | SMTP服务器 | 端口 | 说明 |
|---------|-----------|------|------|
| Gmail | smtp.gmail.com | 587 | 需要开启"两步验证"并生成"应用专用密码" |
| QQ邮箱 | smtp.qq.com | 587 | 需要开启SMTP服务并获取授权码 |
| 163邮箱 | smtp.163.com | 587 | 需要开启SMTP服务并获取授权码 |
| Outlook | smtp-mail.outlook.com | 587 | 使用账号密码 |

### Gmail 应用专用密码获取步骤

1. 登录 Google 账户
2. 访问 https://myaccount.google.com/security
3. 开启"两步验证"
4. 在"两步验证"下方选择"应用专用密码"
5. 选择"邮件"和设备，生成密码
6. 将生成的16位密码填入配置文件

### QQ/163邮箱授权码获取

1. 登录邮箱网页版
2. 进入"设置" -> "账户"
3. 找到"POP3/IMAP/SMTP服务"
4. 开启SMTP服务
5. 按提示获取授权码
6. 将授权码填入配置文件的 `sender_password` 字段

## 使用方法

### 方式1: 持续监控（推荐）

```bash
python yau_awards_monitor.py
```

脚本会按配置的时间间隔（默认1小时）持续检查网站更新。

### 方式2: 单次检查

```bash
python yau_awards_monitor.py --once
```

只执行一次检查，适合通过 cron 定时任务调用。

### 方式3: 后台运行（Linux/Mac）

```bash
nohup python yau_awards_monitor.py > monitor.log 2>&1 &
```

使脚本在后台持续运行，日志输出到 `monitor.log` 文件。

### 方式4: 使用 systemd 服务（Linux推荐）

创建服务文件 `/etc/systemd/system/yau-monitor.service`:

```ini
[Unit]
Description=Yau Awards Website Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/streamlit-example
ExecStart=/usr/bin/python3 /home/user/streamlit-example/yau_awards_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start yau-monitor
sudo systemctl enable yau-monitor  # 开机自启
```

## 文件说明

- `yau_awards_monitor.py` - 主监控脚本
- `monitor_config.json` - 配置文件（邮箱设置、检查间隔）
- `notifications_data.json` - 自动生成，存储已检测到的通知
- `requirements_monitor.txt` - Python依赖包列表

## 工作原理

1. **首次运行**: 抓取当前所有通知并保存到 `notifications_data.json`
2. **后续检查**:
   - 抓取最新通知列表
   - 与之前保存的通知对比（使用MD5哈希）
   - 发现新通知则发送邮件
   - 更新保存的通知列表

## 故障排查

### 问题1: 无法获取网页（403错误）

- 网站可能有反爬虫机制
- 脚本已包含浏览器User-Agent模拟
- 如仍失败，可能需要使用代理或selenium

### 问题2: 邮件发送失败

- 检查邮箱配置是否正确
- 确认使用的是"应用专用密码"或"授权码"，而非账号密码
- 检查网络连接和防火墙设置
- 查看错误信息确定具体问题

### 问题3: 未检测到通知

- 网站结构可能已变化
- 运行 `python yau_awards_monitor.py --once` 查看输出
- 如显示"未找到通知内容"，可能需要调整HTML选择器

### 问题4: 收到太多重复通知

- 删除 `notifications_data.json` 文件会导致所有通知被视为新通知
- 首次运行不会发送邮件，只记录当前状态

## 定制化

### 修改检查间隔

编辑 `monitor_config.json` 中的 `check_interval`（单位：秒）：

- 30分钟: `1800`
- 1小时: `3600`
- 2小时: `7200`
- 12小时: `43200`

### 修改网页选择器

如果网站结构变化导致无法检测通知，需要修改 `yau_awards_monitor.py` 中的 `fetch_notifications()` 方法，调整BeautifulSoup选择器。

## 安全建议

- ⚠️ 不要将 `monitor_config.json` 提交到git仓库（已包含在.gitignore）
- 🔒 使用应用专用密码，不要使用邮箱主密码
- 🛡️ 确保服务器安全，防止配置文件泄露

## 测试

首次使用建议先进行测试：

1. 配置好邮箱信息
2. 运行 `python yau_awards_monitor.py --once`
3. 检查是否正常抓取到通知
4. 删除 `notifications_data.json` 并再次运行，应该会收到邮件

## 许可证

MIT License

## 更新日志

- v1.0 (2025-11-09): 初始版本
  - 网页抓取和监控
  - 邮件通知功能
  - 配置文件支持
  - 单次和持续监控模式
