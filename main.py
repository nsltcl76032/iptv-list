import requests
import re
from concurrent.futures import ThreadPoolExecutor

# 关闭 SSL 警告
requests.packages.urllib3.disable_warnings()

# 源配置
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
# 缩短 UA 长度防止粘贴截断
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def check_url(item):
    info, url = item
    try:
        # 使用缩短后的 UA
        h = {"User-Agent": UA}
        with requests.get(url, headers=h, timeout=3, stream=True, verify=False) as r:
            if r.status_code == 200:
                return f"{info}\n{url}"
    except:
        pass
    return None

def main():
    all_to_check = []
    seen_urls = set()

    # 1. M3U 抓取
    for s_url in M3U_SOURCES:
        try:
            r = requests.get(s_url, timeout=
