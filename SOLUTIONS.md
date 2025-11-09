# 监控解决方案 - 应对反爬虫保护

## 问题说明

经过测试，丘成桐奖官网 (http://www.yau-awards.com/) 目前有较强的反爬虫保护，直接访问返回 403 错误。这在当前环境下无法通过简单的HTTP请求绕过。

## 诊断工具

运行诊断工具检查网站访问状态：

```bash
python test_website_access.py
```

该工具会测试多种访问方法并提供详细的诊断信息。

## 解决方案

我们提供了**三种监控方案**，从简单到复杂：

### 方案 1: 手动辅助模式 ⭐ 推荐

**最实用的解决方案**，适合反爬虫保护严格的网站。

```bash
python yau_awards_monitor_manual.py
```

**工作流程**：
1. 你定期用浏览器访问网站查看通知
2. 发现新通知时，在脚本中手动录入
3. 脚本自动检测是否为新通知
4. 自动发送邮件提醒

**优点**：
- ✓ 不会被反爬虫拦截
- ✓ 100% 准确
- ✓ 可记录详细信息
- ✓ 仍能自动发送邮件

**使用示例**：

```
$ python yau_awards_monitor_manual.py

╔==============================================================================╗
║                    丘成桐奖网站监控 - 手动模式                              ║
╚==============================================================================╝

选项:
  1) 查看已记录的通知
  2) 手动录入新通知
  3) 清除所有记录
  4) 导出记录到文件
  5) 退出

请选择 (1-5): 2

手动录入新通知
================================================================================
提示: 访问 http://www.yau-awards.com/ 查看最新通知
      输入空白标题结束录入

通知标题: 2024年丘成桐奖获奖名单公布
通知链接: http://www.yau-awards.com/news/123
✓ 已添加: 2024年丘成桐奖获奖名单公布

通知标题: [直接回车结束]

检查结果
================================================================================
✓ 发现 1 条新通知:
  1. 2024年丘成桐奖获奖名单公布

是否发送邮件通知? (y/n): y
✓ 邮件发送成功！发送到: your@email.com
✓ 已保存 1 条新通知
```

### 方案 2: Selenium 自动化浏览器

使用真实浏览器绕过反爬虫保护。

**安装要求**：
```bash
pip install selenium webdriver-manager
# 需要安装Chrome浏览器
```

**使用**：
```bash
# 单次检查
python yau_awards_monitor_selenium.py --once

# 持续监控
python yau_awards_monitor_selenium.py
```

**优点**：
- ✓ 可绕过大部分反爬虫
- ✓ 全自动运行
- ✓ 可处理JavaScript渲染

**缺点**：
- ✗ 需要安装Chrome
- ✗ 资源消耗较大
- ✗ 可能仍被高级反爬虫检测

**注意**：当前测试环境没有Chrome浏览器，需要在有GUI的机器上运行。

### 方案 3: 基础 HTTP 请求

使用requests库直接请求（当前被403拦截）。

```bash
python yau_awards_monitor.py --once
```

**适用场景**：
- 网站取消反爬虫保护
- 使用代理/VPN
- 在不同网络环境下

## 推荐工作流程

### 个人使用（最简单）

每天或每周：
1. 浏览器访问 http://www.yau-awards.com/
2. 运行 `python yau_awards_monitor_manual.py`
3. 录入新通知
4. 自动收到邮件

### 自动化部署（需要Chrome）

在有Chrome的服务器上：
1. 安装Chrome和ChromeDriver
2. 配置 `monitor_config.json`
3. 运行 `python yau_awards_monitor_selenium.py`
4. 或使用systemd/cron定时运行

### 使用代理

修改脚本添加代理支持：

```python
# 在 yau_awards_monitor.py 中添加
proxies = {
    'http': 'http://proxy-server:port',
    'https': 'http://proxy-server:port'
}
response = session.get(url, headers=headers, proxies=proxies)
```

## 其他替代方案

### 1. RSS订阅

检查网站是否提供RSS feed：
```bash
curl http://www.yau-awards.com/rss.xml
curl http://www.yau-awards.com/feed.xml
```

如果有RSS，可以直接监控RSS更新（更简单可靠）。

### 2. 浏览器扩展

使用浏览器扩展监控页面变化：
- **Distill Web Monitor** (Chrome/Firefox)
- **Visualping**
- **ChangeTower**

### 3. 第三方服务

使用在线监控服务：
- **Visualping.io** - 网页变化监控
- **Changedetection.io** - 开源自托管方案
- **Distill.io** - 免费/付费监控服务

### 4. 移动应用

如果有官方App，可以：
- 使用App接收通知
- 抓包分析App的API
- 监控API接口（通常没有反爬虫）

## 文件说明

| 文件 | 说明 | 推荐度 |
|------|------|--------|
| `yau_awards_monitor_manual.py` | 手动辅助模式 | ⭐⭐⭐⭐⭐ |
| `yau_awards_monitor_selenium.py` | Selenium自动化 | ⭐⭐⭐⭐ |
| `yau_awards_monitor.py` | 基础HTTP请求 | ⭐⭐ |
| `test_website_access.py` | 访问诊断工具 | ⭐⭐⭐⭐⭐ |

## 当前测试结果

```
DNS检查         : ✗ 失败 (环境限制)
基础请求        : ✓ 连接成功，但返回 403
使用UA          : ✓ 连接成功，但返回 403
使用Session     : ✓ 连接成功，但返回 403
HTTPS           : ✓ 连接成功，但返回 403
带延迟          : ✓ 连接成功，但返回 403

结论: 网站可访问但有严格的反爬虫保护
```

## 长期解决方案

1. **联系网站管理员**
   - 说明监控目的
   - 申请API访问权限
   - 获取官方RSS feed

2. **使用官方渠道**
   - 关注官方社交媒体
   - 订阅邮件列表
   - 使用官方App

3. **社区协作**
   - 加入相关微信群/QQ群
   - 设置群通知提醒

## 常见问题

**Q: 为什么会有403错误？**
A: 网站检测到非浏览器访问，触发了反爬虫保护机制。

**Q: Selenium一定能成功吗？**
A: 不一定。高级反爬虫可以检测Selenium特征。但成功率比requests高很多。

**Q: 手动模式是否太麻烦？**
A: 对于访问受限的网站，这是最稳定的方案。而且录入一次通知只需30秒。

**Q: 能否使用无头浏览器？**
A: 可以，Selenium脚本已支持headless模式（在config中配置）。

**Q: 如何知道网站发布了新通知？**
A:
- 设置日历提醒（如每周一检查）
- 加入相关社群获取消息
- 浏览器书签定期查看

## 总结

**最佳实践**：使用 **手动辅助模式**（方案1）

1. 每周访问网站1-2次
2. 发现新通知时录入脚本
3. 自动发送邮件，保持记录
4. 简单可靠，不会被拦截

当网站取消反爬虫保护或你获得了API访问权限时，再切换到自动模式。
