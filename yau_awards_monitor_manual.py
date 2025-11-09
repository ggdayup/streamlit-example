#!/usr/bin/env python3
"""
丘成桐奖官网监控 - 手动辅助模式
当自动抓取失败时，提供手动录入通知的界面
"""

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import hashlib


class ManualMonitor:
    def __init__(self, config_file='monitor_config.json'):
        """初始化"""
        self.config_file = config_file
        self.data_file = 'notifications_data.json'
        self.config = self.load_config()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def load_data(self):
        """加载已保存的通知"""
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
        content = notification['title']
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def display_existing_notifications(self):
        """显示已保存的通知"""
        data = self.load_data()
        if not data:
            print("当前无已保存的通知")
            return

        print("\n当前已记录的通知：")
        print("=" * 80)
        for i, notif in enumerate(data[-10:], 1):  # 只显示最近10条
            print(f"{i}. {notif['title']}")
        print("=" * 80)
        if len(data) > 10:
            print(f"(还有 {len(data) - 10} 条历史通知未显示)")

    def manual_input(self):
        """手动输入通知"""
        print("\n" + "=" * 80)
        print("手动录入新通知")
        print("=" * 80)
        print("提示: 访问 http://www.yau-awards.com/ 查看最新通知")
        print("      输入空白标题结束录入\n")

        notifications = []

        while True:
            title = input("通知标题: ").strip()
            if not title:
                break

            link = input("通知链接 (可选): ").strip()

            notifications.append({
                'title': title,
                'link': link,
                'html': '',
                'source': 'manual',
                'input_time': datetime.now().isoformat()
            })

            print(f"✓ 已添加: {title}\n")

        return notifications

    def check_and_notify(self, new_notifications):
        """检查新通知并发送邮件"""
        if not new_notifications:
            print("没有新通知录入")
            return

        # 加载已有数据
        existing = self.load_data()
        existing_hashes = {self.get_notification_hash(n) for n in existing}

        # 找出真正的新通知
        truly_new = []
        duplicates = []

        for notif in new_notifications:
            if self.get_notification_hash(notif) not in existing_hashes:
                truly_new.append(notif)
            else:
                duplicates.append(notif)

        # 显示结果
        print("\n" + "=" * 80)
        print("检查结果")
        print("=" * 80)

        if truly_new:
            print(f"✓ 发现 {len(truly_new)} 条新通知:")
            for i, notif in enumerate(truly_new, 1):
                print(f"  {i}. {notif['title']}")

            # 询问是否发送邮件
            if self.config:
                send = input("\n是否发送邮件通知? (y/n): ").strip().lower()
                if send == 'y':
                    self.send_email(truly_new)
        else:
            print("○ 所有通知均已存在，无新通知")

        if duplicates:
            print(f"\n⚠ {len(duplicates)} 条通知已存在（未添加）:")
            for i, notif in enumerate(duplicates, 1):
                print(f"  {i}. {notif['title']}")

        # 保存新通知
        if truly_new:
            existing.extend(truly_new)
            self.save_data(existing)
            print(f"\n✓ 已保存 {len(truly_new)} 条新通知")

    def send_email(self, notifications):
        """发送邮件"""
        if not self.config:
            print("✗ 未找到配置文件，无法发送邮件")
            return

        email_config = self.config['email']

        subject = f"丘成桐奖网站有 {len(notifications)} 条新通知 (手动录入)"

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
                .manual-tag {{
                    background-color: #ffeaa7;
                    padding: 2px 8px;
                    border-radius: 3px;
                    font-size: 0.85em;
                }}
            </style>
        </head>
        <body>
            <h2>丘成桐奖官网新通知提醒</h2>
            <p class="timestamp">
                录入时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                <span class="manual-tag">手动录入</span>
            </p>
            <p>发现 <strong>{len(notifications)}</strong> 条新通知：</p>
        """

        for i, notification in enumerate(notifications, 1):
            html_body += f"""
            <div class="notification">
                <h3>通知 {i}</h3>
                <p>{notification['title']}</p>
            """
            if notification.get('link'):
                html_body += f'<p><a href="{notification["link"]}" class="link">查看详情</a></p>'
            html_body += "</div>"

        html_body += """
            <hr>
            <p style="color: #7f8c8d; font-size: 0.9em;">
                本邮件由丘成桐奖官网监控脚本发送（手动模式）<br>
                网站地址: <a href="http://www.yau-awards.com/">http://www.yau-awards.com/</a>
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
        except Exception as e:
            print(f"✗ 邮件发送失败: {e}")

    def interactive_mode(self):
        """交互模式"""
        print("\n╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "丘成桐奖网站监控 - 手动模式" + " " * 28 + "║")
        print("╚" + "=" * 78 + "╝\n")

        print("说明: 由于网站有反爬虫保护，自动抓取可能失败")
        print("      本工具提供手动录入模式，帮助你跟踪通知变化\n")

        while True:
            print("\n选项:")
            print("  1) 查看已记录的通知")
            print("  2) 手动录入新通知")
            print("  3) 清除所有记录")
            print("  4) 导出记录到文件")
            print("  5) 退出")

            choice = input("\n请选择 (1-5): ").strip()

            if choice == '1':
                self.display_existing_notifications()

            elif choice == '2':
                new_notifs = self.manual_input()
                self.check_and_notify(new_notifs)

            elif choice == '3':
                confirm = input("确认清除所有记录? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    self.save_data([])
                    print("✓ 已清除所有记录")
                else:
                    print("已取消")

            elif choice == '4':
                data = self.load_data()
                if data:
                    filename = f"notifications_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"✓ 已导出到: {filename}")
                else:
                    print("没有数据可导出")

            elif choice == '5':
                print("\n再见!")
                break

            else:
                print("无效选择，请重试")


def main():
    """主函数"""
    monitor = ManualMonitor()
    monitor.interactive_mode()


if __name__ == '__main__':
    main()
