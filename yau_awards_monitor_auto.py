#!/usr/bin/env python3
"""
丘成桐奖官网通知公告监控脚本 - 自动化增强版
使用多种技术绕过反爬虫保护
"""

import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib

# 尝试导入多个库
import requests
from bs4 import BeautifulSoup

SCRAPER_TYPE = None

try:
    import cloudscraper
    SCRAPER_TYPE = 'cloudscraper'
    print("使用 cloudscraper (反Cloudflare)")
except ImportError:
    pass

if not SCRAPER_TYPE:
    try:
        from requests_html import HTMLSession
        SCRAPER_TYPE = 'requests_html'
        print("使用 requests_html (JavaScript支持)")
    except ImportError:
        pass

if not SCRAPER_TYPE:
    SCRAPER_TYPE = 'requests'
    print("使用基础 requests")


class YauAwardsMonitorAuto:
    def __init__(self, config_file='monitor_config.json'):
        """初始化监控器"""
        self.url = 'http://www.yau-awards.com/'
        self.config_file = config_file
        self.data_file = 'notifications_data.json'
        self.config = self.load_config()
        self.scraper_type = SCRAPER_TYPE

        # 初始化scraper
        if self.scraper_type == 'cloudscraper':
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
        elif self.scraper_type == 'requests_html':
            self.session = HTMLSession()
        else:
            self.session = requests.Session()

        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }

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
                "check_interval": 3600
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"已创建配置文件: {self.config_file}")
            return default_config

    def fetch_notifications(self):
        """获取通知公告内容"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

                print(f"尝试 {attempt + 1}/{max_retries}: 使用 {self.scraper_type}")

                # 根据不同的scraper类型使用不同的方法
                if self.scraper_type == 'cloudscraper':
                    response = self.scraper.get(self.url, timeout=30)
                    response.raise_for_status()
                    html_content = response.text

                elif self.scraper_type == 'requests_html':
                    response = self.session.get(self.url, headers=self.headers, timeout=30)
                    response.raise_for_status()

                    # 尝试渲染JavaScript (如果页面需要)
                    try:
                        response.html.render(timeout=20, sleep=2)
                        html_content = response.html.html
                    except:
                        html_content = response.text

                else:  # basic requests
                    response = self.session.get(self.url, headers=self.headers, timeout=30)
                    response.raise_for_status()
                    html_content = response.text

                # 检查是否成功
                if len(html_content) < 100:
                    print(f"⚠ 响应内容太短 ({len(html_content)} bytes)，可能被拦截")
                    continue

                if '403' in html_content or 'forbidden' in html_content.lower():
                    print("⚠ 检测到403错误特征")
                    continue

                print(f"✓ 成功获取页面 ({len(html_content)} bytes)")

                # 解析HTML
                soup = BeautifulSoup(html_content, 'html.parser')

                notifications = []

                # 方法1: 查找包含"通知"或"公告"的标题及其内容
                for keyword in ['通知公告', '通知', '公告', 'Notice', 'Announcement', '新闻']:
                    title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span'],
                                                  string=lambda text: text and keyword in text)

                    for title_elem in title_elements:
                        parent = title_elem.find_parent(['div', 'section', 'article'])
                        if parent:
                            items = parent.find_all(['li', 'a', 'div'], class_=lambda x: x and any(
                                k in str(x).lower() for k in ['item', 'list', 'notice', 'news', 'announcement']
                            ))

                            for item in items:
                                text = item.get_text(strip=True)
                                link = item.find('a')
                                href = link.get('href') if link else None

                                if text and len(text) > 5:
                                    notifications.append({
                                        'title': text[:200],
                                        'link': href if href else '',
                                        'html': str(item)[:500]
                                    })

                        if notifications:
                            break

                    if notifications:
                        break

                # 方法2: 查找新闻/列表类元素
                if not notifications:
                    news_containers = soup.find_all(['ul', 'div'], class_=lambda x: x and any(
                        k in str(x).lower() for k in ['news', 'notice', 'list', 'announcement', 'info']
                    ))

                    for container in news_containers:
                        items = container.find_all(['li', 'a'])[:20]
                        for item in items:
                            text = item.get_text(strip=True)
                            link = item.find('a')
                            href = link.get('href') if link else item.get('href')

                            if text and len(text) > 5:
                                notifications.append({
                                    'title': text[:200],
                                    'link': href if href else '',
                                    'html': str(item)[:500]
                                })

                        if notifications:
                            break

                # 方法3: 获取所有有意义的链接
                if not notifications:
                    all_links = soup.find_all('a')
                    for link in all_links[:50]:
                        text = link.get_text(strip=True)
                        href = link.get('href')

                        if text and 10 < len(text) < 200:
                            notifications.append({
                                'title': text,
                                'link': href if href else '',
                                'html': str(link)[:500]
                            })

                if notifications:
                    # 去重
                    seen = set()
                    unique = []
                    for n in notifications:
                        if n['title'] not in seen:
                            seen.add(n['title'])
                            unique.append(n)
                    return unique

                print("⚠ 未找到通知内容")
                return []

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"✗ 访问被拒绝(403) - 尝试 {attempt + 1}/{max_retries}")
                    if attempt == max_retries - 1:
                        print("\n尝试了所有方法仍被拦截")
                        print("建议:")
                        print("  1. 网站可能需要登录或有严格的访问控制")
                        print("  2. 可能需要使用代理或VPN")
                        print("  3. 考虑使用真实浏览器(Selenium/Playwright)")
                        return None
                else:
                    print(f"HTTP错误 {e.response.status_code}: {e}")
                    return None

            except Exception as e:
                print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None

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
        content = notification['title'] + notification.get('html', '')
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
                本邮件由丘成桐奖官网监控脚本自动发送 (Auto版本)<br>
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

    def check_updates(self):
        """检查更新"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查...")
        print(f"使用方法: {self.scraper_type}")

        current_notifications = self.fetch_notifications()

        if current_notifications is None:
            print("✗ 无法获取网页内容")
            return

        if not current_notifications:
            print("⚠ 未找到通知内容")
            return

        print(f"✓ 成功获取 {len(current_notifications)} 条通知")

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

    def run_once(self):
        """运行一次检查"""
        self.check_updates()

    def run_continuous(self):
        """持续监控"""
        interval = self.config.get('check_interval', 3600)
        print(f"开始监控丘成桐奖官网 (自动增强版)...")
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

    print("=" * 60)
    print("丘成桐奖官网监控 - 自动化增强版")
    print("=" * 60)

    monitor = YauAwardsMonitorAuto()

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        monitor.run_once()
    else:
        monitor.run_continuous()


if __name__ == '__main__':
    main()
