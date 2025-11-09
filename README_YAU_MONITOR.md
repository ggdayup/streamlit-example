# 丘成桐奖网站监控系统

自动监控 http://www.yau-awards.com/ 的通知公告，有新通知时发送邮件提醒。

## 🚨 重要说明

网站目前有**反爬虫保护**（返回403错误），推荐使用 **手动辅助模式**。

## 🎯 快速开始（3步）

### 1️⃣ 安装依赖

```bash
pip install requests beautifulsoup4 lxml
```

### 2️⃣ 配置邮箱

复制配置模板并编辑：

```bash
cp monitor_config.example.json monitor_config.json
nano monitor_config.json  # 填入你的邮箱信息
```

关键配置：
- `sender_email`: 发件邮箱
- `sender_password`: **应用专用密码**（不是邮箱密码！）
- `receiver_email`: 接收通知的邮箱

### 3️⃣ 运行监控

```bash
bash start_monitor.sh
```

然后选择 **选项 1（手动辅助模式）**。

## 📊 监控方案对比

| 方案 | 推荐度 | 优点 | 缺点 | 适用场景 |
|------|--------|------|------|----------|
| **手动辅助** | ⭐⭐⭐⭐⭐ | 100%可靠<br>不被拦截<br>仍可自动邮件 | 需手动录入 | **有反爬虫保护** |
| Selenium | ⭐⭐⭐⭐ | 可绕过反爬虫<br>全自动 | 需Chrome<br>资源消耗大 | 有Chrome环境 |
| 基础HTTP | ⭐⭐ | 轻量快速 | 易被拦截 | 无反爬虫网站 |

## 🔧 使用方法

### 方案1: 手动辅助模式（推荐）⭐

```bash
python yau_awards_monitor_manual.py
```

**工作流程**：
1. 每天/每周用浏览器访问网站
2. 发现新通知时，在脚本中录入
3. 脚本自动检测是否为新通知
4. 自动发送邮件提醒

**示例**：
```
$ python yau_awards_monitor_manual.py

选项:
  1) 查看已记录的通知
  2) 手动录入新通知  ← 选这个
  3) 清除所有记录
  4) 导出记录到文件
  5) 退出

请选择: 2

通知标题: 2024年获奖名单公布
通知链接: http://www.yau-awards.com/news/123
✓ 已添加

✓ 发现 1 条新通知
是否发送邮件? (y/n): y
✓ 邮件发送成功！
```

### 方案2: Selenium自动化

需要Chrome浏览器：

```bash
pip install selenium webdriver-manager
python yau_awards_monitor_selenium.py --once
```

### 方案3: 基础HTTP请求

```bash
python yau_awards_monitor.py --once
```

**注意**：当前会遇到403错误。

## 🛠️ 工具脚本

### 诊断工具

测试网站访问状态：

```bash
python test_website_access.py
```

输出示例：
```
测试总结
============================================================
DNS检查       : ✗ 失败
基础请求      : ✓ 通过（但返回403）
使用UA        : ✓ 通过（但返回403）
...

建议: 网站有反爬虫保护，建议使用手动模式
```

### 快速启动菜单

```bash
bash start_monitor.sh
```

提供交互式菜单，选择不同的监控模式。

## 📧 邮箱配置详解

### Gmail 用户

1. **开启两步验证**：https://myaccount.google.com/security
2. **生成应用专用密码**：
   - 安全设置 → 应用专用密码
   - 选择"邮件"和设备
   - 复制生成的16位密码
3. **配置**：
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your@gmail.com",
    "sender_password": "生成的16位密码",
    "receiver_email": "receiver@example.com"
  }
}
```

### QQ邮箱 / 163邮箱

1. 登录邮箱网页版
2. 设置 → 账户 → POP3/SMTP服务
3. 开启SMTP服务
4. 获取授权码
5. 配置：

**QQ邮箱**：
```json
{
  "smtp_server": "smtp.qq.com",
  "smtp_port": 587,
  "sender_password": "授权码"
}
```

**163邮箱**：
```json
{
  "smtp_server": "smtp.163.com",
  "smtp_port": 587,
  "sender_password": "授权码"
}
```

## 📁 文件说明

```
.
├── yau_awards_monitor_manual.py    ⭐ 手动辅助模式（推荐）
├── yau_awards_monitor_selenium.py   Selenium自动化版本
├── yau_awards_monitor.py            基础HTTP版本
├── test_website_access.py           网站访问诊断工具
├── start_monitor.sh                 快速启动脚本
├── setup_monitor.sh                 自动安装脚本
├── monitor_config.example.json      配置模板
├── requirements_monitor.txt         Python依赖
├── README_YAU_MONITOR.md           本文档
├── QUICKSTART.md                    快速指南
├── YAU_MONITOR_README.md           详细文档
└── SOLUTIONS.md                     解决方案详解
```

## 🔥 常见问题

### Q1: 为什么返回403错误？

**A**: 网站检测到非浏览器访问，触发了反爬虫保护。

**解决方案**：使用手动辅助模式（推荐）或Selenium版本。

### Q2: 邮件发送失败？

**A**: 检查以下几点：
- ✓ 是否使用了"应用专用密码"或"授权码"？
- ✓ SMTP服务器和端口是否正确？
- ✓ 网络连接是否正常？
- ✓ 防火墙是否允许SMTP连接？

### Q3: 手动模式太麻烦？

**A**: 其实很简单：
- 每周只需访问网站1-2次（5分钟）
- 录入新通知只需30秒
- 是针对受保护网站最稳定的方案

### Q4: Selenium需要什么？

**A**: 需要：
1. Chrome浏览器
2. ChromeDriver（或使用webdriver-manager自动管理）
3. `pip install selenium webdriver-manager`

### Q5: 如何自动运行？

**A**: 手动模式无法全自动。但可以：
- 设置日历提醒（每周一检查）
- 或使用Selenium版本配置定时任务

**使用cron（Selenium版本）**：
```bash
# 每天上午10点检查
0 10 * * * cd /path/to/dir && python yau_awards_monitor_selenium.py --once
```

## 🎯 推荐工作流程

### 个人使用（最简单）

**频率**: 每周1-2次

1. 浏览器打开 http://www.yau-awards.com/
2. 运行 `bash start_monitor.sh` → 选择 1（手动模式）
3. 看到新通知就录入
4. 自动收到邮件 ✉️

**总耗时**: 每次约5分钟

### 自动化部署（高级）

**需要**: 有Chrome的服务器

1. 安装Chrome和依赖
2. 配置邮箱
3. 使用systemd或cron运行Selenium版本
4. 定期检查日志

## 📚 更多文档

- **快速开始**: `QUICKSTART.md`
- **完整文档**: `YAU_MONITOR_README.md`
- **解决方案**: `SOLUTIONS.md`（详细说明反爬虫问题）

## 🔗 相关链接

- 网站地址: http://www.yau-awards.com/
- GitHub: 此项目仓库

## 📝 更新日志

**v1.1** (2025-11-09)
- ✨ 新增手动辅助模式
- 🔧 新增网站访问诊断工具
- 📖 新增详细的解决方案文档
- 🎨 改进启动脚本UI

**v1.0** (2025-11-09)
- 🎉 初始版本
- 📧 基础HTTP监控
- 🤖 Selenium自动化
- 📮 邮件通知功能

## 💡 提示

1. **首次使用先测试**：
   ```bash
   python test_website_access.py  # 诊断
   python yau_awards_monitor_manual.py  # 测试手动模式
   ```

2. **不要将配置文件提交到git**：
   - `monitor_config.json` 已在 `.gitignore` 中
   - 包含敏感信息（邮箱密码）

3. **定期检查**：
   - 设置手机日历提醒
   - 或加入相关社群获取通知

## 📞 获取帮助

遇到问题？

1. 查看 `SOLUTIONS.md` 了解常见问题
2. 运行 `python test_website_access.py` 诊断
3. 检查配置文件是否正确

---

**License**: MIT

**Created**: 2025-11-09
