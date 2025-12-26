import requests
import re
from concurrent.futures import ThreadPoolExecutor

# ================= 配置区域 =================
M3U_SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/display.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/YueChan/live/main/hotel.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tv.m3u",
    "https://raw.githubusercontent.com/Guutong/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/yuanzl77/IPTV/main/living.m3u"
]

TG_CHANNELS = [
    "https://t.me/s/zhiboyuan",
    "https://t.me/s/iptv_list",
    "https://t.me/s/iptv_live_share",
    "https://t.me/s/youshandefeiyang",
    "https://t.me/s/iptv_collect",
    "https://t.me/s/m3u8list"
]

KEYWORDS = ["联通", "酒店", "UNICOM", "CU", "单播"]
MAX_WORKERS = 50
# ===========================================

def fetch_tg_links():
    """从 TG 频道提取潜在的直播链接"""
    links_found = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url in TG_CHANNELS:
        try:
            print(f"[*] 正在爬取 TG 频道: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            # 匹配 http 链接
            found = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
            for link in found:
                clean_link = link.replace('&amp;', '&').strip('.,"\')')
                # 过滤条件
                if any(x in clean_link for x in [".m3u8", ".php", ":81/", ":808/"]):
                    links_found.append(clean_link)
        except Exception as e:
            print(f"[!] TG 抓取异常 {url}: {e}")
    return list(set(links_found))

def check_url(item):
    """验证链接存活率"""
    info, url = item
    headers = {"User-Agent": "Lavf/58.29.100"}
    try:
        # 使用 GET 请求配合 stream=True，超时设为 3 秒
        with requests.get(url, headers=headers, timeout=3, stream=True) as response:
            if response.status_code == 200:
                # 尝试读取一小段数据确认流有效
                next(response.iter_content(512))
                return f"{info}\n{url}"
    except StopIteration:
        # 有些流可能立即结束，但也算 200 OK
        return f"{info}\n{url}"
    except Exception:
        return None
    return None

def main():
    all_to_check = []
    seen_urls = set()

    # 1. 处理 M3U 源
    print("[*] 开始处理
