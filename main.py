import requests
import re
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
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
    links_found = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url in TG_CHANNELS:
        try:
            print(f"[*] Scanning TG Channel: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            found = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
            for link in found:
                clean_link = link.replace('&amp;', '&').strip('.,"\')')
                if
