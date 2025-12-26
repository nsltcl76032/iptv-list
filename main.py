import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor

# ================= 配置区域 =================
# 传统 M3U 订阅源
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

# TG 频道 Web 预览链接
TG_CHANNELS = [
    "https://t.me/s/zhiboyuan",
    "https://t.me/s/iptv_list",
    "https://t.me/s/iptv_live_share",
    "https://t.me/s/youshandefeiyang",
    "https://t.me/s/iptv_collect",
    "https://t.me/s/m3u8list"
]

# 过滤关键词
KEYWORDS = ["联通", "酒店", "UNICOM", "CU", "单播"]
# 线程数 (GitHub Action 环境建议 30-50)
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
                clean_link