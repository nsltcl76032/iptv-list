import requests
import re
import os

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

# 1. 扩充后的源列表（包含酒店、联通、专线）
M3U_URLS = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/display.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/YueChan/live/main/hotel.m3u",
    "https://raw.githubusercontent.com/Guutong/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/yuanzl77/IPTV/main/living.m3u"
]

# 2. TG 频道 Web 预览链接
TG_URLS = [
    "https://t.me/s/zhiboyuan",
    "https://t.me/s/iptv_list",
    "https://t.me/s/iptv_live_share",
    "https://t.me/s/youshandefeiyang",
    "https://t.me/s/iptv_collect",
    "https://t.me/s/m3u8list"
]

# 匹配关键词
KEYWORDS = ["联通", "酒店", "UNICOM", "CU", "单播", "专线"]

def main():
    final_list = []
    seen = set()
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    print("[*] 开始从 M3U 源抓取数据...")
    for url in M3U_URLS:
        try:
            r = requests.get(url, timeout=15, verify=False)
            r.encoding = 'utf-8'
            lines = [l.strip() for l in r.text.split('\n') if l.strip()]
            for i in range(len(lines)):
                if lines[i].startswith("#EXTINF") and i+1 < len(lines):
                    info = lines[i]
                    stream_url = lines[i+1]
                    if stream_url.startswith("http") and stream_url not in seen:
                        # 检查关键词
                        content = (info + stream_url).lower()
                        if any(k.lower() in content for k in KEYWORDS):
                            final_list.append(f"{info}\n{stream_url}")
                            seen.add(stream_url)
        except Exception as e:
            print(f"[!] 跳过源 {url}: {e}")

    print("[*] 开始从 Telegram 频道解析数据...")
    for t_url in TG_URLS:
        try:
            r = requests.get(t_url, headers=ua, timeout=20, verify=False)
            # 改进的正则匹配链接
            found_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', r.text)
            for u in found_urls:
                u = u.replace('&amp;', '&').strip('.,"\')')
                # 联通酒店源常见特征：m3u8, php, 808, 81
                if any(x in u for x in [".m3u8", ".php", ":81/", ":808/"]):
                    if u not in seen:
                        # 手动构造标签，方便搜索
                        info = f'#EXTINF:-1 group-title="TG采集-联通酒店",联通专线-{len(final_list)}'
                        final_list.append(f"{info}\n{u}")
                        seen.add(u)
        except:
            continue

    # 保存文件
    output_file = "unicom_hotel_ultimate.m3u"
    print(f"[*] 抓取完毕，共计 {len(final_list)} 条源。正在写入文件...")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        if final_list:
            f.write("\n".join(final_list))
    
    print(f"[*] 执行成功！文件已生成: {output_file}")

if __name__ == "__main__":
    main()