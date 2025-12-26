import requests, re, os
from concurrent.futures import ThreadPoolExecutor

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

# 订阅源
M3U_URLS = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/display.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/YueChan/live/main/hotel.m3u",
    "https://raw.githubusercontent.com/vbskycn/iptv/master/tv.m3u",
    "https://raw.githubusercontent.com/Guutong/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/yuanzl77/IPTV/main/living.m3u"
]

# TG预览页
TG_URLS = [
    "https://t.me/s/zhiboyuan",
    "https://t.me/s/iptv_list",
    "https://t.me/s/iptv_live_share",
    "https://t.me/s/youshandefeiyang",
    "https://t.me/s/iptv_collect",
    "https://t.me/s/m3u8list"
]

def check(item):
    info, url = item
    try:
        # 极简请求，超时3秒
        with requests.get(url, timeout=3, stream=True, verify=False) as r:
            if r.status_code == 200:
                return f"{info}\n{url}"
    except:
        pass
    return None

def main():
    tasks, seen = [], set()
    kw = ["联通", "酒店", "UNICOM", "CU"]
    ua = {"User-Agent": "Mozilla/5.0"}

    # 1. 抓取M3U
    for s in M3U_URLS:
        try:
            r = requests.get(s, timeout=10)
            lines = [l.strip() for l in r.text.split('\n') if l.strip()]
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF") and i+1 < len(lines):
                    info, url = lines[i], lines[i+1]
                    if url.startswith("http") and url not in seen:
                        if any(k.lower() in (info+url).lower() for k in kw):
                            tasks.append((info, url))
                            seen.add(url)
        except: continue

    # 2. 抓取TG
    for t in TG_URLS:
        try:
            r = requests.get(t, headers=ua, timeout=15)
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
            for u in urls:
                u = u.replace('&amp;', '&').strip('.,"\')')
                if any(x in u for x in [".m3u8", ".php", ":81/", ":808/"]):
                    if u not in seen:
                        info = f'#EXTINF:-1 group-title="TG采集-联通酒店",Channel'
                        tasks.append((info, u))
                        seen.add(u)
        except: continue

    # 3. 测速并保存
    print(f"Total: {len(tasks)}. Testing...")
    with ThreadPoolExecutor(max_workers=50) as p:
        res = list(p.map(check, tasks))
    
    with open("unicom_hotel_exclusive.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join([r for r in res if r]))
    print("Done.")

if __name__ == "__main__":
    main()