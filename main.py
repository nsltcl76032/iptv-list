import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

SOURCES = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/ipv6.m3u",
    "https://raw.githubusercontent.com/cymz6/AutoIPTV-Hotel/main/display.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/Gather.m3u",
    "https://raw.githubusercontent.com/YueChan/live/main/hotel.m3u",
    "https://raw.githubusercontent.com/Guutong/IPTV/main/live.m3u",
    "https://raw.githubusercontent.com/ssili126/tv/main/itvlist.m3u",
    "https://raw.githubusercontent.com/yuanzl77/IPTV/main/living.m3u"
]

OUTPUT_FILENAME = "iptv_tested_final.m3u"

def get_group(name):
    """根据频道名自动归类"""
    name = name.upper()
    if "CCTV" in name or "中央" in name: return "央视频道"
    if "卫视" in name: return "卫视频道"
    if any(x in name for x in ["CETV", "CHC", "风云", "兵团", "嘉佳"]): return "数字频道"
    # 匹配省份
    provinces = ["北京", "上海", "广东", "深圳", "天津", "重庆", "湖南", "湖北", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "河北", "山西", "内蒙", "辽宁", "吉林", "黑龙江", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "广西", "海南"]
    for p in provinces:
        if p in name: return f"{p}频道"
    return "其他频道"

def check_streaming(item):
    """GitHub Action 专用测速逻辑"""
    info, url, name = item
    
    # 策略 1：内网/特定端口源 (GitHub 无法测试，强制保留)
    internal_features = [":6610", ":81", ":808", "rtp://", "udp://", "2409:", "2408:", "240e:"]
    if any(x in url for x in internal_features):
        return {"group": get_group(name), "info": info, "url": url}

    # 策略 2：公网 HLS 链接测试
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with requests.get(url, headers=headers, timeout=3, stream=True, verify=False) as r:
            if r.status_code == 200:
                # 尝试读取数据块
                it = r.iter_content(512)
                if next(it):
                    return {"group": get_group(name), "info": info, "url": url}
    except:
        # IPv4 酒店源通常没有特殊前缀但 GitHub 也连不通，保守保留
        if "[:" not in url:
            return {"group": get_group(name), "info": info, "url": url}
    return None

def main():
    print("🚀 开始全量抓取与归类整理...")
    tasks = []
    seen_urls = set()
    
    for source_url in SOURCES:
        try:
            r = requests.get(source_url, timeout=20)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                lines = [l.strip() for l in r.text.split('\n') if l.strip()]
                for i in range(len(lines)):
                    if lines[i].startswith("#EXTINF") and i+1 < len(lines):
                        info = lines[i]
                        stream_url = lines[i+1]
                        # 提取频道名
                        name_match = re.search(r',([^,]+)$', info)
                        name = name_match.group(1) if name_match else "未知频道"
                        
                        if stream_url not in seen_urls:
                            tasks.append((info, stream_url, name))
                            seen_urls.add(stream_url)
        except: continue

    print(f"[*] 原始数据 {len(tasks)} 条。开始多线程校验...")

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_streaming, tasks))
    
    # 过滤空值
    valid_results = [r for r in results if r]
    
    # 排序：按分组名排序
    valid_results.sort(key=lambda x: x['group'])

    # 写入文件
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        current_group = ""
        for item in valid_results:
            # 动态更新分组标签
            info = re.sub(r'group-title="[^"]*"', f'group-title="{item["group"]}"', item["info"])
            if 'group-title="' not in info:
                info = info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{item["group"]}"')
            
            f.write(f"{info}\n{item['url']}\n")
    
    print(f"✅ 处理完成！输出 {len(valid_results)} 条优质源。")

if __name__ == "__main__":
    main()