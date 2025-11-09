#!/usr/bin/env python3
"""
丘成桐奖官网通知公告监控脚本 - Playwright版本
使用Playwright自动化框架，比Selenium更稳定可靠
"""

import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib
import asyncio

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("错误: 需要安装playwright库")
    print("运行: pip install playwright && playwright install chromium")
    exit(1)


class YauAwardsMonitorPlaywright:
    def __init__(self, config_file='monitor_config.json'):
        """初始化监控器"""
        self.url = 'http://www.yau-awards.com/'
        self.config_file = config_file
        self.data_file = 'notifications_data.json'
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "receiver_email": "receiver@example.com"
                },
                "check_interval": 3600,
                "playwright": {
                    "headless": True,
                    "timeout": 30000
                }
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"已创建配置文件: {self.config_file}")
            return default_config

    async def fetch_notifications(self):
        """使用Playwright获取通知公告内容"""
        try:
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(
                    headless=self.config.get('playwright', {}).get('headless', True)
                )

                # 创建浏览器上下文
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                # 创建新页面
                page = await context.new_page()

                print(f"正在访问网站: {self.url}")

                # 访问网站
                timeout = self.config.get('playwright', {}).get('timeout', 30000)
                await page.goto(self.url, timeout=timeout, wait_until='domcontentloaded')

                # 等待页面加载
                await page.wait_for_timeout(3000)

                # 获取页面内容
                content = await page.content()

                notifications = []

                # 策略1: 查找包含"通知"或"公告"的元素
                keywords = ['通知公告', '通知', '公告', 'Notice', 'Announcement']

                for keyword in keywords:
                    try:
                        # 查找包含关键词的元素
                        elements = await page.query_selector_all(f'text="{keyword}"')

                        if elements:
                            print(f"找到包含'{keyword}'的元素")

                            # 获取该区域的所有链接
                            links = await page.query_selector_all('a')

                            for link in links[:30]:
                                try:
                                    text = await link.inner_text()
                                    href = await link.get_attribute('href')

                                    text = text.strip()
                                    if text and len(text) > 5 and len(text) < 200:
                                        notifications.append({
                                            'title': text,
                                            'link': href if href else '',
                                            'html': await link.inner_html()
                                        })
                                except:
                                    continue

                            if notifications:
                                break
                    except:
                        continue

                # 策略2: 获取所有链接
                if not notifications:
                    print("尝试获取所有链接...")
                    all_links = await page.query_selector_all('a')

                    for link in all_links[:50]:
                        try:
                            text = await link.inner_text()
                            href = await link.get_attribute('href')

                            text = text.strip()
                            if text and 10 < len(text) < 200:
                                notifications.append({
                                    'title': text,
                                    'link': href if href else '',
                                    'html': await link.inner_html()
                                })
                        except:
                            continue

                # 关闭浏览器
                await browser.close()

                # 去重
                seen = set()
                unique_notifications = []
                for notif in notifications:
                    key = notif['title']
                    if key not in seen:
                        seen.add(key)
                        unique_notifications.append(notif)

                return unique_notifications

        except Exception as e:
            print(f"获取通知失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_previous_data(self):
        """加载之前保存的通知数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self, data):
        """保存通知数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_notification_hash(self, notification):
        """生成通知的唯一哈希值"""
        content = notification['title'] + notification.get('html', '')[:200]
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def find_new_notifications(self, current, previous):
        """找出新的通知"""
        previous_hashes = {self.get_notification_hash(n) for n in previous}
        new_notifications = []

        for notification in current:
            if self.get_notification_hash(notification) not in previous_hashes:
                new_notifications.append(notification)

        return new_notifications

    def send_email(self, new_notifications):
        """发送邮件提醒"""
        email_config = self.config['email']

        subject = f"丘成桐奖网站有 {len(new_notifications)} 条新通知"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #2c3e50; }}
                .notification {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #3498db;
                    border-radius: 4px;
                }}
                .notification h3 {{ margin-top: 0; color: #2980b9; }}
                .link {{ color: #3498db; }}
                .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h2>丘成桐奖官网新通知提醒</h2>
            <p class="timestamp">检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>发现 <strong>{len(new_notifications)}</strong> 条新通知：</p>
        """

        for i, notification in enumerate(new_notifications, 1):
            html_body += f"""
            <div class="notification">
                <h3>通知 {i}</h3>
                <p>{notification['title']}</p>
            """
            if notification.get('link'):
                full_link = notification['link']
                if not full_link.startswith('http'):
                    full_link = self.url.rstrip('/') + '/' + full_link.lstrip('/')
                html_body += f'<p><a href="{full_link}" class="link">查看详情</a></p>'
            html_body += "</div>"

        html_body += f"""
            <hr>
            <p style="color: #7f8c8d; font-size: 0.9em;">
                本邮件由丘成桐奖官网监控脚本自动发送 (Playwright版本)<br>
                网站地址: <a href="{self.url}">{self.url}</a>
            </p>
        </body>
        </html>
        """

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['receiver_email']

        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                server.starttls()
                server.login(email_config['sender_email'], email_config['sender_password'])
                server.send_message(msg)

            print(f"✓ 邮件发送成功！发送到: {email_config['receiver_email']}")
            return True
        except Exception as e:
            print(f"✗ 邮件发送失败: {e}")
            return False

    async def check_updates_async(self):
        """异步检查更新"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")

        current_notifications = await self.fetch_notifications()

        if current_notifications is None:
            print("✗ 无法获取网页内容")
            return

        if not current_notifications:
            print("⚠ 未找到通知内容")
            return

        print(f"✓ 成功获取 {len(current_notifications)} 条通知")

        # 显示前几条
        for i, notif in enumerate(current_notifications[:5], 1):
            print(f"  {i}. {notif['title'][:80]}")
        if len(current_notifications) > 5:
            print(f"  ... 还有 {len(current_notifications) - 5} 条")

        previous_notifications = self.load_previous_data()

        if previous_notifications:
            new_notifications = self.find_new_notifications(current_notifications, previous_notifications)

            if new_notifications:
                print(f"🔔 发现 {len(new_notifications)} 条新通知！")
                for i, notif in enumerate(new_notifications, 1):
                    print(f"  {i}. {notif['title'][:100]}")

                self.send_email(new_notifications)
            else:
                print("○ 没有新通知")
        else:
            print("ℹ 首次运行，保存当前状态")

        self.save_data(current_notifications)

    def check_updates(self):
        """同步检查更新接口"""
        asyncio.run(self.check_updates_async())

    def run_once(self):
        """运行一次检查"""
        self.check_updates()

    def run_continuous(self):
        """持续监控"""
        interval = self.config.get('check_interval', 3600)
        print(f"开始监控丘成桐奖官网 (Playwright版本)...")
        print(f"检查间隔: {interval} 秒 ({interval/60:.1f} 分钟)")
        print(f"网站地址: {self.url}")
        print("按 Ctrl+C 停止监控\n")

        try:
            while True:
                self.check_updates()
                print(f"下次检查时间: {datetime.fromtimestamp(time.time() + interval).strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n监控已停止")


def main():
    """主函数"""
    import sys

    monitor = YauAwardsMonitorPlaywright()

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        monitor.run_once()
    else:
        monitor.run_continuous()


if __name__ == '__main__':
    main()
