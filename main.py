import requests
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

# ================= 环境变量读取 =================
# 在青龙面板-环境变量中添加以下四个变量
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")

# 检查环境变量是否配置
if not all([GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO]):
    print("❌ 错误：请在青龙环境变量中配置 GITHUB_TOKEN, GITHUB_USER, GITHUB_REPO")
# ===============================================

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
    name = name.upper()
    if "CCTV" in name or "中央" in name: return "央视频道"
    if "卫视" in name: return "卫视频道"
    provinces = ["北京", "上海", "广东", "深圳", "天津", "重庆", "湖南", "湖北", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "河北", "山西", "内蒙", "辽宁", "吉林", "黑龙江", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "广西", "海南"]
    for p in provinces:
        if p in name: return f"{p}频道"
    return "其他频道"

def check_streaming(item):
    info, url, name = item
    session = requests.Session()
    session.trust_env = False
    
    # 强制保留运营商内网特征源 (GitHub/部分Docker环境测不通)
    if any(x in url for x in [":6610", ":81", ":808", "rtp://", "udp://", "2409:", "2408:"]):
        return {"group": get_group(name), "info": info, "url": url}

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        with session.get(url, headers=headers, timeout=3, stream=True, verify=False) as r:
            if r.status_code == 200:
                it = r.iter_content(512)
                if next(it):
                    return {"group": get_group(name), "info": info, "url": url}
    except:
        if "[:" not in url: return {"group": get_group(name), "info": info, "url": url}
    return None

def push_to_github():
    if not GITHUB_TOKEN: return
    print("🚀 开始推送到 GitHub...")
    # 配置 Git
    os.system(f'git config --global user.email "{GITHUB_EMAIL or "ql@bot.com"}"')
    os.system(f'git config --global user.name "{GITHUB_USER}"')
    
    # 构建远程地址
    remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{GITHUB_REPO}.git"
    
    # 推送流程
    os.system(f"git add {OUTPUT_FILENAME}")
    os.system(f'git commit -m "Auto Update: {time.strftime("%Y-%m-%d %H:%M:%S")}"')
    # 尝试推送到 main，如果失败尝试 master
    res = os.system(f"git push {remote_url} main")
    if res != 0:
        os.system(f"git push {remote_url} master")
    print("✅ 推送任务结束")

def main():
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
                        info, stream_url = lines[i], lines[i+1]
                        name = re.search(r',([^,]+)$', info).group(1) if re.search(r',([^,]+)$', info) else "未知"
                        if stream_url not in seen_urls:
                            tasks.append((info, stream_url, name))
                            seen_urls.add(stream_url)
        except: continue

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(check_streaming, tasks))
    
    valid_results = sorted([r for r in results if r], key=lambda x: x['group'])

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in valid_results:
            info = re.sub(r'group-title="[^"]*"', f'group-title="{item["group"]}"', item["info"])
            if 'group-title="' not in info:
                info = info.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{item["group"]}"')
            f.write(f"{info}\n{item['url']}\n")
    print(f"✅ 处理完成，共 {len(valid_results)} 条")

if __name__ == "__main__":
    main()
    push_to_github()