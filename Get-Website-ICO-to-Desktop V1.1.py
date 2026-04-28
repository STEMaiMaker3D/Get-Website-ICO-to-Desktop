import os
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
from PIL import Image


def fetch_and_save_icon(icon_url, save_path, headers, domain_name):
    """专门负责下载并转换图标的函数"""
    print(f"⬇️ 正在获取图标: {icon_url}")
    response = requests.get(icon_url, headers=headers, stream=True, timeout=10)
    response.raise_for_status()

    content_type = response.headers.get('Content-Type', '').lower()
    if 'text/html' in content_type:
        raise ValueError("服务器返回了一个假网页 (通常是人机验证页面)，而不是图片。")

    total_size = int(response.headers.get('content-length', 0))
    buffer = io.BytesIO()

    with tqdm(desc=f"{domain_name}", total=total_size if total_size > 0 else None, unit='B', unit_scale=True,
              unit_divisor=1024) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = buffer.write(data)
            bar.update(size)

    buffer.seek(0)
    try:
        img = Image.open(buffer)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        img.save(save_path, format='ICO')
        print(f"✅ 成功！标准 .ico 图标已保存至:\n   📁 {save_path}")
    except Exception as e:
        raise ValueError(f"下载的文件不是有效的图片格式 ({e})。")


def download_and_convert_favicon(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    save_dir = r"C:\Users\95279\OneDrive\Pictures\ico"
    os.makedirs(save_dir, exist_ok=True)

    domain = urlparse(url).netloc
    if not domain:
        print("❌ 错误：无效的网址格式！")
        return

    save_path = os.path.join(save_dir, f"{domain}.ico")

    # 【核心升级 1】加入 Referer，告诉服务器“我是在你网站内部浏览的”，破解图床防盗链
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': url
    }

    print(f"\n🔍 [阶段1] 尝试直接解析网页: {url} ...")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        # 优先寻找高质量图标 (apple-touch-icon)，找不到再找普通 icon
        icon_link = soup.find("link", rel=lambda x: x and ('icon' in x.lower() or 'apple-touch-icon' in x.lower()))

        if icon_link and icon_link.get('href'):
            favicon_url = urljoin(url, icon_link.get('href'))
        else:
            favicon_url = urljoin(url, '/favicon.ico')

        print(f"🔗 找到目标图标地址: {favicon_url}")
        fetch_and_save_icon(favicon_url, save_path, headers, domain)
        return  # 如果成功，直接结束

    except Exception as e:
        print(f"⚠️ 直接获取失败: {e}")
        print("🔄 [阶段2] 正在启动备用方案一：通过 DuckDuckGo API 获取图标...")

        # 【核心升级 2】DuckDuckGo 备用 API，非常稳定
        ddg_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        try:
            fetch_and_save_icon(ddg_url, save_path, headers, f"{domain} (DuckDuckGo)")
            return  # 如果成功，直接结束
        except Exception as ddg_e:
            print(f"⚠️ 备用方案一失败: {ddg_e}")
            print("🔄 [阶段3] 正在启动备用方案二：通过 Google API 获取图标...")

            google_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
            try:
                fetch_and_save_icon(google_url, save_path, headers, f"{domain} (Google)")
            except Exception as google_e:
                print(f"❌ 所有尝试均失败，未能获取该网站图标。错误详情: {google_e}")


if __name__ == "__main__":
    while True:
        target_url = input("\n🌐 请输入要获取图标的网址 (输入 'q' 退出): ").strip()
        if target_url.lower() == 'q':
            break
        if target_url:
            download_and_convert_favicon(target_url)