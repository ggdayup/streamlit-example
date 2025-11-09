#!/usr/bin/env python3
"""
丘成桐奖官网通知公告监控脚本
监控 http://www.yau-awards.com/ 的通知公告部分，发现新通知时发送邮件提醒
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib


class YauAwardsMonitor:
    def __init__(self, config_file='monitor_config.json'):
        """初始化监控器"""
        self.url = 'http://www.yau-awards.com/'
        self.config_file = config_file
        self.data_file = 'notifications_data.json'
        self.config = self.load_config()

        # 创建session以保持连接
        self.session = requests.Session()

        # 请求头，模拟真实浏览器访问
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'http://www.yau-awards.com/'
        }

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "your_email@gmail.com",
                    "sender_password": "your_app_password",
                    "receiver_email": "receiver@example.com"
                },
                "check_interval": 3600  # 检查间隔（秒），默认1小时
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"已创建配置文件: {self.config_file}")
            print("请编辑配置文件设置邮件信息")
            return default_config

    def fetch_notifications(self):
        """获取通知公告内容"""
        # 重试机制
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                # 添加随机延迟，避免被识别为机器人
                if attempt > 0:
                    time.sleep(retry_delay * attempt)

                # 使用session发送请求
                response = self.session.get(
                    self.url,
                    headers=self.headers,
                    timeout=30,
                    allow_redirects=True,
                    verify=True
                )
                response.raise_for_status()
                response.encoding = response.apparent_encoding

                # 成功获取，跳出重试循环
                break

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f"✗ 访问被拒绝(403) - 尝试 {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        print("  提示: 网站可能有反爬虫保护，正在重试...")
                        continue
                    else:
                        print("\n⚠️ 建议解决方案:")
                        print("  1. 使用浏览器手动访问网站，查看通知内容")
                        print("  2. 考虑使用VPN或代理")
                        print("  3. 检查网站是否需要登录")
                        print("  4. 尝试使用selenium浏览器自动化工具")
                        return None
                else:
                    print(f"HTTP错误: {e}")
                    return None

            except requests.exceptions.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                continue

        try:

            soup = BeautifulSoup(response.text, 'html.parser')

            # 尝试多种可能的选择器来找到通知公告部分
            notifications = []

            # 方法1: 查找包含"通知"或"公告"的标题及其内容
            for keyword in ['通知公告', '通知', '公告', 'Notice', 'Announcement']:
                # 查找标题
                title_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div', 'span'],
                                              string=lambda text: text and keyword in text)

                for title_elem in title_elements:
                    # 获取该标题后的内容区域
                    parent = title_elem.find_parent(['div', 'section', 'article'])
                    if parent:
                        # 查找列表项
                        items = parent.find_all(['li', 'a', 'div'], class_=lambda x: x and any(
                            k in str(x).lower() for k in ['item', 'list', 'notice', 'news', 'announcement']
                        ))

                        for item in items:
                            text = item.get_text(strip=True)
                            link = item.find('a')
                            href = link.get('href') if link else None

                            if text and len(text) > 5:  # 过滤太短的文本
                                notifications.append({
                                    'title': text[:200],  # 限制长度
                                    'link': href if href else '',
                                    'html': str(item)[:500]  # 保存HTML片段用于检测变化
                                })

            # 方法2: 如果没找到，查找所有新闻/列表类元素
            if not notifications:
                news_containers = soup.find_all(['ul', 'div'], class_=lambda x: x and any(
                    k in str(x).lower() for k in ['news', 'notice', 'list', 'announcement', 'info']
                ))

                for container in news_containers:
                    items = container.find_all(['li', 'a'])[:10]  # 限制数量
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

            return notifications

        except requests.RequestException as e:
            print(f"获取网页失败: {e}")
            return None
        except Exception as e:
            print(f"解析网页失败: {e}")
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

        # 创建邮件内容
        subject = f"丘成桐奖网站有 {len(new_notifications)} 条新通知"

        # HTML格式的邮件正文
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
                本邮件由丘成桐奖官网监控脚本自动发送<br>
                网站地址: <a href="{self.url}">{self.url}</a>
            </p>
        </body>
        </html>
        """

        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['receiver_email']

        # 添加HTML内容
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        try:
            # 发送邮件
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

        # 获取当前通知
        current_notifications = self.fetch_notifications()

        if current_notifications is None:
            print("✗ 无法获取网页内容")
            return

        if not current_notifications:
            print("⚠ 未找到通知内容（可能需要调整选择器）")
            return

        print(f"✓ 成功获取 {len(current_notifications)} 条通知")

        # 加载之前的数据
        previous_notifications = self.load_previous_data()

        if previous_notifications:
            # 查找新通知
            new_notifications = self.find_new_notifications(current_notifications, previous_notifications)

            if new_notifications:
                print(f"🔔 发现 {len(new_notifications)} 条新通知！")
                for i, notif in enumerate(new_notifications, 1):
                    print(f"  {i}. {notif['title'][:100]}")

                # 发送邮件
                self.send_email(new_notifications)
            else:
                print("○ 没有新通知")
        else:
            print("ℹ 首次运行，保存当前状态")

        # 保存当前数据
        self.save_data(current_notifications)

    def run_once(self):
        """运行一次检查"""
        self.check_updates()

    def run_continuous(self):
        """持续监控"""
        interval = self.config.get('check_interval', 3600)
        print(f"开始监控丘成桐奖官网...")
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

    monitor = YauAwardsMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # 单次检查模式
        monitor.run_once()
    else:
        # 持续监控模式
        monitor.run_continuous()


if __name__ == '__main__':
    main()
