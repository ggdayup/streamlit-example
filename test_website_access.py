#!/usr/bin/env python3
"""
网站访问测试工具
测试不同方法访问丘成桐奖网站，并提供诊断信息
"""

import requests
import time


def test_basic_request():
    """测试基础请求"""
    print("=" * 60)
    print("测试 1: 基础 HTTP 请求")
    print("=" * 60)

    url = 'http://www.yau-awards.com/'

    try:
        response = requests.get(url, timeout=10)
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 响应大小: {len(response.content)} bytes")
        print(f"✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_with_headers():
    """测试使用浏览器请求头"""
    print("\n" + "=" * 60)
    print("测试 2: 使用浏览器 User-Agent")
    print("=" * 60)

    url = 'http://www.yau-awards.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 响应大小: {len(response.content)} bytes")

        # 检查是否被重定向
        if response.history:
            print(f"⚠ 发生重定向:")
            for i, r in enumerate(response.history):
                print(f"  {i+1}. {r.status_code} -> {r.url}")
            print(f"  最终: {response.url}")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_with_session():
    """测试使用 Session"""
    print("\n" + "=" * 60)
    print("测试 3: 使用 Session (保持 cookies)")
    print("=" * 60)

    url = 'http://www.yau-awards.com/'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })

    try:
        response = session.get(url, timeout=10)
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ 响应大小: {len(response.content)} bytes")

        # 显示cookies
        if session.cookies:
            print(f"✓ Cookies 数量: {len(session.cookies)}")
            for cookie in session.cookies:
                print(f"  - {cookie.name}")
        else:
            print("○ 无 cookies")

        # 显示部分响应内容
        if response.status_code == 200:
            preview = response.text[:500].replace('\n', ' ')
            print(f"\n响应预览 (前500字符):")
            print(f"{preview}...")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_https():
    """测试 HTTPS 版本"""
    print("\n" + "=" * 60)
    print("测试 4: HTTPS 版本")
    print("=" * 60)

    url = 'https://www.yau-awards.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, verify=True)
        print(f"✓ 状态码: {response.status_code}")
        print(f"✓ HTTPS 访问成功")
        return True
    except requests.exceptions.SSLError:
        print("✗ SSL 证书验证失败")
        print("  尝试不验证证书...")
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            print(f"✓ 状态码 (不验证SSL): {response.status_code}")
            return True
        except Exception as e:
            print(f"✗ 仍然失败: {e}")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_with_delay():
    """测试带延迟的请求"""
    print("\n" + "=" * 60)
    print("测试 5: 带延迟的多次请求")
    print("=" * 60)

    url = 'http://www.yau-awards.com/'
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    })

    for i in range(3):
        try:
            print(f"\n请求 {i+1}/3...")
            response = session.get(url, timeout=10)
            print(f"  ✓ 状态码: {response.status_code}")

            if i < 2:
                print(f"  等待 2 秒...")
                time.sleep(2)
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            return False

    return True


def check_dns():
    """检查 DNS 解析"""
    print("\n" + "=" * 60)
    print("DNS 检查")
    print("=" * 60)

    import socket

    domain = 'www.yau-awards.com'
    try:
        ip = socket.gethostbyname(domain)
        print(f"✓ DNS 解析成功")
        print(f"  {domain} -> {ip}")
        return True
    except Exception as e:
        print(f"✗ DNS 解析失败: {e}")
        return False


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "丘成桐奖网站访问诊断工具" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    results = {
        'DNS检查': check_dns(),
        '基础请求': test_basic_request(),
        '使用UA': test_with_headers(),
        '使用Session': test_with_session(),
        'HTTPS': test_https(),
        '带延迟': test_with_delay(),
    }

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:15s} : {status}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n成功率: {success_count}/{total_count} ({success_count*100//total_count}%)")

    # 建议
    print("\n" + "=" * 60)
    print("建议")
    print("=" * 60)

    if results['基础请求']:
        print("✓ 网站可以访问，监控脚本应该可以正常工作")
    elif results['使用UA']:
        print("⚠ 需要使用 User-Agent 才能访问")
        print("  监控脚本已包含此功能，应该可以工作")
    elif results['使用Session']:
        print("⚠ 需要使用 Session 保持 cookies")
        print("  监控脚本已包含此功能")
    else:
        print("✗ 网站访问受限，可能的原因:")
        print("  1. 网站有强反爬虫保护")
        print("  2. IP 被限制")
        print("  3. 需要登录或验证")
        print("\n解决方案:")
        print("  1. 使用代理服务器")
        print("  2. 使用VPN")
        print("  3. 手动浏览器访问并检查是否需要验证")
        print("  4. 联系网站管理员")

    print()


if __name__ == '__main__':
    main()
